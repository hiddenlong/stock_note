import uuid
from datetime import datetime


class Position:
    """持仓模型"""
    
    def __init__(self, stock_code, stock_name, buy_price, quantity, buy_date=None):
        """
        初始化持仓
        
        参数:
        stock_code: 股票代码
        stock_name: 股票名称
        buy_price: 买入价格
        quantity: 持仓数量
        buy_date: 买入日期
        """
        self.id = str(uuid.uuid4())
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.buy_price = buy_price
        self.quantity = quantity
        self.buy_date = buy_date or datetime.now().isoformat()
        self.commission = 0
        self.plans = []  # 止盈止损计划ID列表
        self.status = 'HOLDING'  # HOLDING/SOLD
    
    def add_plan(self, plan_id):
        """添加止盈止损计划ID"""
        if plan_id not in self.plans:
            self.plans.append(plan_id)
    
    def remove_plan(self, plan_id):
        """移除止盈止损计划ID"""
        if plan_id in self.plans:
            self.plans.remove(plan_id)
    
    def update_quantity(self, delta_quantity):
        """更新持仓数量"""
        self.quantity += delta_quantity
        if self.quantity <= 0:
            self.status = 'SOLD'
    
    def calculate_profit(self, current_price):
        """计算当前持仓盈亏"""
        if self.quantity <= 0:
            return 0
        
        # 持仓市值
        market_value = current_price * self.quantity
        
        # 持仓成本（包含手续费）
        cost = self.buy_price * self.quantity + self.commission
        
        # 盈亏金额
        profit = market_value - cost
        
        return profit
    
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'buy_price': self.buy_price,
            'quantity': self.quantity,
            'buy_date': self.buy_date,
            'commission': self.commission,
            'plans': self.plans,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建对象"""
        position = cls(
            data['stock_code'],
            data['stock_name'],
            data['buy_price'],
            data['quantity'],
            data['buy_date']
        )
        position.id = data['id']
        position.commission = data['commission']
        position.plans = data['plans']
        position.status = data['status']
        return position