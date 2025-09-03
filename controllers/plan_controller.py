from models.plan import ProfitLossPlan
from controllers.trade_controller import TradeController


class PlanController:
    """止盈止损计划控制器"""
    
    def __init__(self, data_manager):
        """
        初始化计划控制器
        
        参数:
        data_manager: 数据管理器实例
        """
        self.data_manager = data_manager
        self.trade_controller = TradeController(data_manager)
    
    def create_price_plan(self, position_id, take_profit_price=None, stop_loss_price=None, auto_execute=False):
        """
        创建价格触发的止盈止损计划
        
        参数:
        position_id: 持仓ID
        take_profit_price: 止盈价格
        stop_loss_price: 止损价格
        auto_execute: 是否自动执行
        
        返回:
        ProfitLossPlan: 止盈止损计划对象
        """
        # 验证持仓是否存在
        position = self.data_manager.get_position_by_id(position_id)
        if not position:
            raise ValueError("持仓不存在")
        
        # 创建计划
        plan = ProfitLossPlan(position_id, 'price')
        plan.set_price_trigger(take_profit_price, stop_loss_price)
        plan.auto_execute = auto_execute
        
        # 保存计划
        self.data_manager.add_plan(plan)
        
        # 将计划ID添加到持仓中
        position.add_plan(plan.id)
        self.data_manager.update_position(position)
        
        return plan
    
    def create_percentage_plan(self, position_id, take_profit_ratio=None, stop_loss_ratio=None, auto_execute=False):
        """
        创建百分比触发的止盈止损计划
        
        参数:
        position_id: 持仓ID
        take_profit_ratio: 止盈百分比 (如0.1表示10%)
        stop_loss_ratio: 止损百分比 (如0.05表示5%)
        auto_execute: 是否自动执行
        
        返回:
        ProfitLossPlan: 止盈止损计划对象
        """
        # 验证持仓是否存在
        position = self.data_manager.get_position_by_id(position_id)
        if not position:
            raise ValueError("持仓不存在")
        
        # 创建计划
        plan = ProfitLossPlan(position_id, 'percentage')
        plan.set_percentage_trigger(take_profit_ratio, stop_loss_ratio)
        plan.auto_execute = auto_execute
        
        # 保存计划
        self.data_manager.add_plan(plan)
        
        # 将计划ID添加到持仓中
        position.add_plan(plan.id)
        self.data_manager.update_position(position)
        
        return plan
    
    def check_and_execute_plans(self, current_prices):
        """
        检查并执行止盈止损计划
        
        参数:
        current_prices: 当前价格字典 {stock_code: price}
        """
        plans = self.data_manager.get_plans()
        active_plans = [plan for plan in plans if plan.status == 'ACTIVE']
        
        for plan in active_plans:
            position = self.data_manager.get_position_by_id(plan.position_id)
            if not position or position.status != 'HOLDING':
                continue
            
            current_price = current_prices.get(position.stock_code)
            if not current_price:
                continue
            
            # 检查是否触发止盈止损
            triggered, trigger_type = plan.check_trigger(current_price, position.buy_price)
            if triggered:
                if plan.auto_execute:
                    self._execute_plan(plan, position, current_price, trigger_type)
                else:
                    # 这里可以发出提醒信号，但不自动执行
                    print(f"股票 {position.stock_code} 触发{'止盈' if trigger_type == 'TAKE_PROFIT' else '止损'}条件，当前价格: {current_price}")
    
    def _execute_plan(self, plan, position, current_price, trigger_type):
        """
        执行止盈止损计划（仅作为示例，实际应用中可能不会自动执行）
        
        参数:
        plan: 止盈止损计划
        position: 持仓
        current_price: 当前价格
        trigger_type: 触发类型 ('TAKE_PROFIT' 或 'STOP_LOSS')
        """
        # 标记计划为已执行
        plan.execute()
        self.data_manager.update_plan(plan)
        
        print(f"{'止盈' if trigger_type == 'TAKE_PROFIT' else '止损'}计划已触发，"
              f"股票: {position.stock_code}, 当前价格: {current_price}, "
              f"建议卖出数量: {position.quantity}")
    
    def cancel_plan(self, plan_id):
        """
        取消止盈止损计划
        
        参数:
        plan_id: 计划ID
        """
        plan = self.data_manager.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError("计划不存在")
        
        plan.cancel()
        self.data_manager.update_plan(plan)
        
        # 从持仓中移除计划ID
        position = self.data_manager.get_position_by_id(plan.position_id)
        if position:
            position.remove_plan(plan_id)
            self.data_manager.update_position(position)