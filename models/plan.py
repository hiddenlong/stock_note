import uuid
from datetime import datetime


class ProfitLossPlan:
    """止盈止损计划模型"""
    
    def __init__(self, position_id, trigger_type='price'):
        """
        初始化止盈止损计划
        
        参数:
        position_id: 关联的持仓ID
        trigger_type: 触发类型 ('price' 或 'percentage')
        """
        self.id = str(uuid.uuid4())
        self.position_id = position_id
        self.trigger_type = trigger_type  # 'price' or 'percentage'
        self.take_profit_price = None
        self.stop_loss_price = None
        self.take_profit_ratio = None
        self.stop_loss_ratio = None
        self.status = 'ACTIVE'  # ACTIVE/EXECUTED/CANCELLED
        self.auto_execute = False  # 是否自动执行
        self.created_date = datetime.now().isoformat()
    
    def set_price_trigger(self, take_profit_price=None, stop_loss_price=None):
        """设置价格触发条件"""
        if self.trigger_type != 'price':
            raise ValueError("触发类型不是price")
        self.take_profit_price = take_profit_price
        self.stop_loss_price = stop_loss_price
    
    def set_percentage_trigger(self, take_profit_ratio=None, stop_loss_ratio=None):
        """设置百分比触发条件"""
        if self.trigger_type != 'percentage':
            raise ValueError("触发类型不是percentage")
        self.take_profit_ratio = take_profit_ratio
        self.stop_loss_ratio = stop_loss_ratio
    
    def check_trigger(self, current_price, buy_price):
        """检查是否触发止盈止损"""
        if self.status != 'ACTIVE':
            return False, None
        
        if self.trigger_type == 'price':
            if self.take_profit_price and current_price >= self.take_profit_price:
                return True, 'TAKE_PROFIT'
            elif self.stop_loss_price and current_price <= self.stop_loss_price:
                return True, 'STOP_LOSS'
        elif self.trigger_type == 'percentage':
            change_ratio = (current_price - buy_price) / buy_price
            if self.take_profit_ratio and change_ratio >= self.take_profit_ratio:
                return True, 'TAKE_PROFIT'
            elif self.stop_loss_ratio and change_ratio <= -self.stop_loss_ratio:
                return True, 'STOP_LOSS'
        
        return False, None
    
    def execute(self):
        """执行计划"""
        self.status = 'EXECUTED'
    
    def cancel(self):
        """取消计划"""
        self.status = 'CANCELLED'
    
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'position_id': self.position_id,
            'trigger_type': self.trigger_type,
            'take_profit_price': self.take_profit_price,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_ratio': self.take_profit_ratio,
            'stop_loss_ratio': self.stop_loss_ratio,
            'status': self.status,
            'auto_execute': self.auto_execute,
            'created_date': self.created_date
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建对象"""
        plan = cls(data['position_id'], data['trigger_type'])
        plan.id = data['id']
        plan.take_profit_price = data['take_profit_price']
        plan.stop_loss_price = data['stop_loss_price']
        plan.take_profit_ratio = data['take_profit_ratio']
        plan.stop_loss_ratio = data['stop_loss_ratio']
        plan.status = data['status']
        plan.auto_execute = data['auto_execute']
        plan.created_date = data['created_date']
        return plan