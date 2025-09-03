import json
from datetime import datetime
import uuid


class Trade:
    """交易记录模型"""
    
    def __init__(self, stock_code, stock_name, trade_type, price, quantity, 
                 trade_date=None, commission=0):
        """
        初始化交易记录
        
        参数:
        stock_code: 股票代码
        stock_name: 股票名称
        trade_type: 交易类型 ('BUY' 或 'SELL')
        price: 交易价格
        quantity: 交易数量
        trade_date: 交易日期时间
        commission: 手续费
        """
        self.id = str(uuid.uuid4())
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.trade_type = trade_type  # BUY/SELL
        self.price = price
        self.quantity = quantity
        self.trade_date = trade_date or datetime.now().isoformat()
        self.commission = commission
        self.total_amount = self._calculate_total()
    
    def _calculate_total(self):
        """计算交易总金额"""
        base_amount = self.price * self.quantity
        if self.trade_type == 'BUY':
            return base_amount + self.commission
        else:
            return base_amount - self.commission
    
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'trade_type': self.trade_type,
            'price': self.price,
            'quantity': self.quantity,
            'trade_date': self.trade_date,
            'commission': self.commission,
            'total_amount': self.total_amount
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建对象"""
        trade = cls(
            data['stock_code'],
            data['stock_name'],
            data['trade_type'],
            data['price'],
            data['quantity'],
            data['trade_date'],
            data['commission']
        )
        trade.id = data['id']
        trade.total_amount = data['total_amount']
        return trade