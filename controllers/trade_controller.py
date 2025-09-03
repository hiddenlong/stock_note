from models.trade import Trade
from models.position import Position
from utils.data_manager import DataManager
import uuid


class CommissionStrategy:
    """手续费计算策略基类"""
    
    def calculate(self, price, quantity):
        raise NotImplementedError


class FixedPlusRatioCommission(CommissionStrategy):
    """固定费用+比例费用策略"""
    
    def __init__(self, fixed=5.0, ratio=0.00023):
        """
        初始化手续费策略
        
        参数:
        fixed: 固定费用
        ratio: 比例费用 (如0.00023表示0.023%)
        """
        self.fixed = fixed
        self.ratio = ratio
    
    def calculate(self, price, quantity):
        """
        计算手续费
        
        参数:
        price: 价格
        quantity: 数量
        
        返回:
        手续费金额
        """
        base_amount = price * quantity
        ratio_fee = base_amount * self.ratio
        total_fee = self.fixed + ratio_fee
        # 根据手续费计算规范，最低收费5元
        return max(total_fee, 5.0)


class TradeController:
    """交易控制器"""
    
    def __init__(self, data_manager):
        """
        初始化交易控制器
        
        参数:
        data_manager: 数据管理器实例
        """
        self.data_manager = data_manager
        self.commission_strategy = FixedPlusRatioCommission()
    
    def _calculate_commission(self, price, quantity):
        """计算手续费"""
        return self.commission_strategy.calculate(price, quantity)
    
    def execute_buy(self, stock_code, stock_name, price, quantity, trade_date=None):
        """
        执行买入操作
        
        参数:
        stock_code: 股票代码
        stock_name: 股票名称
        price: 买入价格
        quantity: 买入数量
        trade_date: 交易日期
        
        返回:
        Trade: 交易记录对象
        """
        # 计算手续费
        commission = self._calculate_commission(price, quantity)
        
        # 创建交易记录
        trade = Trade(stock_code, stock_name, 'BUY', price, quantity, trade_date, commission)
        
        # 保存交易记录
        self.data_manager.add_trade(trade)
        
        # 更新或创建持仓
        self._update_position_from_buy(trade)
        
        return trade
    
    def execute_sell(self, position_id, price, quantity, trade_date=None):
        """
        执行卖出操作
        
        参数:
        position_id: 持仓ID
        price: 卖出价格
        quantity: 卖出数量
        trade_date: 交易日期
        
        返回:
        Trade: 交易记录对象
        """
        # 验证持仓
        position = self.data_manager.get_position_by_id(position_id)
        if not position:
            raise ValueError("持仓不存在")
        
        if position.quantity < quantity:
            raise ValueError("持仓数量不足")
        
        # 计算手续费
        commission = self._calculate_commission(price, quantity)
        
        # 创建交易记录
        trade = Trade(position.stock_code, position.stock_name, 'SELL', 
                     price, quantity, trade_date, commission)
        
        # 保存交易记录
        self.data_manager.add_trade(trade)
        
        # 更新持仓
        self._update_position_from_sell(position_id, quantity)
        
        return trade
    
    def _update_position_from_buy(self, trade):
        """根据买入交易更新持仓"""
        # 查找是否已存在该股票的持仓
        existing_position = None
        for position in self.data_manager.get_positions():
            if (position.stock_code == trade.stock_code and 
                position.status == 'HOLDING'):
                existing_position = position
                break
        
        if existing_position:
            # 更新现有持仓
            # 计算新的平均成本价
            total_cost = (existing_position.buy_price * existing_position.quantity) + \
                        (trade.price * trade.quantity) + trade.commission
            total_quantity = existing_position.quantity + trade.quantity
            new_avg_price = total_cost / total_quantity
            
            existing_position.buy_price = new_avg_price
            existing_position.quantity = total_quantity
            existing_position.commission += trade.commission
            self.data_manager.update_position(existing_position)
        else:
            # 创建新持仓
            position = Position(
                trade.stock_code,
                trade.stock_name,
                trade.price,
                trade.quantity,
                trade.trade_date
            )
            position.commission = trade.commission
            self.data_manager.add_position(position)
    
    def _update_position_from_sell(self, position_id, quantity):
        """根据卖出交易更新持仓"""
        position = self.data_manager.get_position_by_id(position_id)
        if position:
            position.update_quantity(-quantity)
            if position.status == 'SOLD':
                # 如果持仓已清空，移除所有关联的止盈止损计划
                for plan_id in position.plans:
                    self.data_manager.remove_plan(plan_id)
                position.plans = []
            self.data_manager.update_position(position)