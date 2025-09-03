# 股票交易记录系统设计说明书

## 1. 系统概述

### 1.1 项目目标
开发一个基于Python的桌面股票交易记录管理系统，为个人投资者提供完整的交易记录管理、止盈止损计划设置、手续费计算和盈利分析功能。

### 1.2 技术栈
- **核心框架**: Python 3.8+
- **GUI框架**: PyQt6
- **数据存储**: JSON文件
- **架构模式**: MVC (Model-View-Controller)

## 2. 系统架构设计

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层 (View)                     │
├─────────────────────────────────────────────────────────┤
│                    业务逻辑层 (Controller)                │
├─────────────────────────────────────────────────────────┤
│                    数据访问层 (Model)                     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 项目目录结构
```
stock_trader/
├── main.py                 # 程序入口点
├── config.py              # 系统配置
├── models/                # 数据模型
│   ├── trade.py           # 交易记录模型
│   ├── position.py        # 持仓模型
│   └── plan.py            # 止盈止损计划模型
├── controllers/           # 控制器
│   ├── main_controller.py # 主控制器
│   ├── trade_controller.py # 交易控制器
│   └── plan_controller.py # 计划控制器
├── views/                 # 视图界面
│   ├── main_window.py     # 主窗口
│   ├── dialogs/           # 各类对话框
│   └── widgets/           # 自定义控件
├── utils/                 # 工具类
│   ├── data_manager.py    # 数据管理器
│   ├── calculator.py      # 计算工具
│   └── validators.py      # 数据验证器
└── data/                  # 数据文件
    └── trading_data.json
```

## 3. 核心数据模型设计

### 3.1 交易记录模型 (Trade)
```python
class Trade:
    def __init__(self, stock_code, stock_name, trade_type, price, quantity, 
                 trade_date=None, commission=0):
        self.id = self._generate_id()
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.trade_type = trade_type  # BUY/SELL
        self.price = price
        self.quantity = quantity
        self.trade_date = trade_date or datetime.now()
        self.commission = commission
        self.total_amount = self._calculate_total()
    
    def _calculate_total(self):
        """计算交易总金额"""
        base_amount = self.price * self.quantity
        if self.trade_type == 'BUY':
            return base_amount + self.commission
        else:
            return base_amount - self.commission
```

### 3.2 持仓模型 (Position)
```python
class Position:
    def __init__(self, stock_code, stock_name, buy_price, quantity, buy_date):
        self.id = self._generate_id()
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.buy_price = buy_price
        self.quantity = quantity
        self.buy_date = buy_date
        self.commission = 0
        self.plans = []  # 止盈止损计划列表
        self.status = 'HOLDING'
    
    def add_plan(self, plan):
        """添加止盈止损计划"""
        self.plans.append(plan)
    
    def update_quantity(self, delta_quantity):
        """更新持仓数量"""
        self.quantity += delta_quantity
        if self.quantity <= 0:
            self.status = 'SOLD'
```

### 3.3 止盈止损计划模型 (ProfitLossPlan)
```python
class ProfitLossPlan:
    def __init__(self, position_id, trigger_type='price'):
        self.id = self._generate_id()
        self.position_id = position_id
        self.trigger_type = trigger_type  # 'price' or 'percentage'
        self.take_profit_price = None
        self.stop_loss_price = None
        self.take_profit_ratio = None
        self.stop_loss_ratio = None
        self.status = 'ACTIVE'  # ACTIVE/EXECUTED/CANCELLED
        self.auto_execute = False  # 是否自动执行
```

## 4. 核心功能实现方式

### 4.1 数据管理框架

#### 4.1.1 数据管理器 (DataManager)
```python
class DataManager:
    def __init__(self, data_file='data/trading_data.json'):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self):
        """从JSON文件加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_data()
    
    def save_data(self):
        """保存数据到JSON文件"""
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
    
    def get_positions(self):
        """获取所有持仓"""
        return [Position(**pos_data) for pos_data in self.data.get('positions', [])]
    
    def add_trade(self, trade):
        """添加交易记录"""
        self.data['trades'].append(trade.__dict__)
        self._update_position_from_trade(trade)
        self.save_data()
```

### 4.2 交易处理框架

#### 4.2.1 交易控制器 (TradeController)
```python
class TradeController:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def execute_buy(self, stock_code, stock_name, price, quantity, 
                    trade_date=None, commission_strategy=None):
        """执行买入操作"""
        # 计算手续费
        commission = self._calculate_commission(price, quantity, commission_strategy)
        
        # 创建交易记录
        trade = Trade(stock_code, stock_name, 'BUY', price, quantity, 
                     trade_date, commission)
        
        # 保存交易记录
        self.data_manager.add_trade(trade)
        
        return trade
    
    def execute_sell(self, position_id, price, quantity, 
                     trade_date=None, commission_strategy=None):
        """执行卖出操作"""
        # 验证持仓
        position = self.data_manager.get_position_by_id(position_id)
        if not position or position.quantity < quantity:
            raise ValueError("持仓数量不足")
        
        # 计算手续费
        commission = self._calculate_commission(price, quantity, commission_strategy)
        
        # 创建交易记录
        trade = Trade(position.stock_code, position.stock_name, 'SELL', 
                     price, quantity, trade_date, commission)
        
        # 更新持仓
        self.data_manager.update_position_after_sell(position_id, -quantity)
        self.data_manager.add_trade(trade)
        
        return trade
    
    def _calculate_commission(self, price, quantity, strategy):
        """计算手续费"""
        if strategy is None:
            return 0
        return strategy.calculate(price, quantity)
```

### 4.3 止盈止损监控框架

#### 4.3.1 计划控制器 (PlanController)
```python
class PlanController:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.trade_controller = TradeController(data_manager)
    
    def create_plan(self, position_id, trigger_type='price', **kwargs):
        """创建止盈止损计划"""
        plan = ProfitLossPlan(position_id, trigger_type)
        
        if trigger_type == 'price':
            plan.take_profit_price = kwargs.get('take_profit_price')
            plan.stop_loss_price = kwargs.get('stop_loss_price')
        elif trigger_type == 'percentage':
            plan.take_profit_ratio = kwargs.get('take_profit_ratio')
            plan.stop_loss_ratio = kwargs.get('stop_loss_ratio')
        
        plan.auto_execute = kwargs.get('auto_execute', False)
        
        # 保存计划
        self.data_manager.add_plan(plan)
        return plan
    
    def check_and_execute_plans(self, current_prices):
        """检查并执行止盈止损计划"""
        active_plans = self.data_manager.get_active_plans()
        
        for plan in active_plans:
            position = self.data_manager.get_position_by_id(plan.position_id)
            if not position:
                continue
            
            current_price = current_prices.get(position.stock_code)
            if not current_price:
                continue
            
            # 检查是否触发止盈止损
            if self._should_execute_plan(plan, position, current_price):
                if plan.auto_execute:
                    self._execute_plan(plan, position, current_price)
                else:
                    # 发出提醒信号
                    self._emit_plan_trigger_signal(plan, position, current_price)
    
    def _should_execute_plan(self, plan, position, current_price):
        """判断是否应该执行计划"""
        if plan.trigger_type == 'price':
            if (plan.take_profit_price and current_price >= plan.take_profit_price) or \
               (plan.stop_loss_price and current_price <= plan.stop_loss_price):
                return True
        elif plan.trigger_type == 'percentage':
            change_ratio = (current_price - position.buy_price) / position.buy_price
            if (plan.take_profit_ratio and change_ratio >= plan.take_profit_ratio) or \
               (plan.stop_loss_ratio and change_ratio <= -plan.stop_loss_ratio):
                return True
        return False
```

## 5. GUI框架搭建

### 5.1 主窗口框架 (MainWindow)
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.trade_controller = TradeController(self.data_manager)
        self.plan_controller = PlanController(self.data_manager)
        
        self._setup_ui()
        self._setup_signals()
        self._load_data()
    
    def _setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("股票交易管理系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建持仓显示区域
        self._create_position_view()
        
        # 创建交易记录区域
        self._create_trade_history_view()
        
        # 创建状态栏
        self._create_status_bar()
    
    def _setup_signals(self):
        """连接信号槽"""
        # 绑定按钮点击事件
        self.buy_button.clicked.connect(self._show_buy_dialog)
        self.sell_button.clicked.connect(self._show_sell_dialog)
        self.plan_button.clicked.connect(self._show_plan_dialog)
```

### 5.2 数据绑定机制
```python
class PositionTableModel(QAbstractTableModel):
    def __init__(self, positions):
        super().__init__()
        self.positions = positions
        self.headers = ['股票代码', '股票名称', '持仓数量', '成本价', '当前价', '盈亏', '状态']
    
    def rowCount(self, parent=None):
        return len(self.positions)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        position = self.positions[index.row()]
        
        if role == Qt.DisplayRole:
            column = index.column()
            if column == 0:
                return position.stock_code
            elif column == 1:
                return position.stock_name
            elif column == 2:
                return position.quantity
            elif column == 3:
                return f"{position.buy_price:.2f}"
            # ... 其他列数据
        
        elif role == Qt.ForegroundRole:
            # 盈亏颜色显示
            if index.column() == 5:  # 盈亏列
                profit = self._calculate_position_profit(position)
                if profit > 0:
                    return QColor('red')  # 盈利用红色
                elif profit < 0:
                    return QColor('green')  # 亏损用绿色
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
```

## 6. 核心算法实现

### 6.1 盈利计算算法
```python
def calculate_position_profit(position, current_price):
    """计算持仓盈亏"""
    if position.quantity <= 0:
        return 0
    
    # 持仓市值
    market_value = current_price * position.quantity
    
    # 持仓成本（包含手续费）
    cost = position.buy_price * position.quantity + position.commission
    
    # 盈亏金额
    profit = market_value - cost
    
    return profit

def calculate_trade_profit(buy_trade, sell_trade):
    """计算单笔交易盈亏"""
    buy_cost = buy_trade.price * buy_trade.quantity + buy_trade.commission
    sell_income = sell_trade.price * sell_trade.quantity - sell_trade.commission
    profit = sell_income - buy_cost
    return profit
```

### 6.2 手续费计算策略
```python
class CommissionStrategy:
    """手续费计算策略基类"""
    def calculate(self, price, quantity):
        raise NotImplementedError

class FixedPlusRatioCommission(CommissionStrategy):
    """固定费用+比例费用策略"""
    def __init__(self, fixed=0, ratio=0.00025):
        self.fixed = fixed
        self.ratio = ratio
    
    def calculate(self, price, quantity):
        base_amount = price * quantity
        ratio_fee = base_amount * self.ratio
        total_fee = self.fixed + ratio_fee
        # 最低收费限制（如5元）
        return max(total_fee, 5.0)
```

## 7. 系统集成与启动

### 7.1 程序入口点
```python
# main.py
import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("股票交易管理系统")
    app.setApplicationVersion("1.0.0")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 启动定时任务（如行情刷新、计划检查）
    setup_timers(window)
    
    # 运行应用程序
    sys.exit(app.exec())

def setup_timers(window):
    """设置定时任务"""
    # 每30秒刷新一次行情
    market_timer = QTimer()
    market_timer.timeout.connect(window.refresh_market_data)
    market_timer.start(30000)
    
    # 每分钟检查一次止盈止损计划
    plan_timer = QTimer()
    plan_timer.timeout.connect(window.check_profit_loss_plans)
    plan_timer.start(60000)

if __name__ == '__main__':
    main()
```

## 8. 数据持久化机制

### 8.1 事务处理
```python
class DataManager:
    def __init__(self):
        self.temp_file = 'data/trading_data_temp.json'
        self.backup_file = 'data/trading_data_backup.json'
    
    def _safe_save(self, data):
        """安全保存数据"""
        try:
            # 1. 保存到临时文件
            with open(self.temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # 2. 备份原文件
            if os.path.exists(self.data_file):
                shutil.copy2(self.data_file, self.backup_file)
            
            # 3. 替换原文件
            shutil.move(self.temp_file, self.data_file)
            
        except Exception as e:
            # 恢复备份文件
            if os.path.exists(self.backup_file):
                shutil.copy2(self.backup_file, self.data_file)
            raise e
```

## 9. 扩展性设计

### 9.1 插件化架构
```python
class StrategyManager:
    """策略管理器"""
    def __init__(self):
        self.strategies = {}
    
    def register_strategy(self, name, strategy_class):
        """注册策略"""
        self.strategies[name] = strategy_class
    
    def get_strategy(self, name, **kwargs):
        """获取策略实例"""
        if name in self.strategies:
            return self.strategies[name](**kwargs)
        return None

# 使用示例
strategy_manager = StrategyManager()
strategy_manager.register_strategy('fixed_ratio', FixedPlusRatioCommission)
```

### 9.2 配置管理
```python
# config.py
CONFIG = {
    'commission': {
        'default_strategy': 'fixed_ratio',
        'strategies': {
            'fixed_ratio': {
                'fixed': 5.0,
                'ratio': 0.00025
            }
        }
    },
    'ui': {
        'refresh_interval': 30,  # 行情刷新间隔(秒)
        'check_plan_interval': 60  # 计划检查间隔(秒)
    }
}
```

## 10. 总结

本设计采用分层架构，通过MVC模式将界面、业务逻辑和数据访问分离，确保系统具有良好的可维护性和扩展性。核心功能通过控制器模式实现，数据持久化采用JSON文件存储，GUI界面基于PyQt6构建，为个人用户提供完整的股票交易管理解决方案。