from models.trade import Trade
from models.position import Position


def calculate_position_profit(position, current_price):
    """
    计算持仓盈亏
    
    参数:
    position: Position对象
    current_price: 当前价格
    
    返回:
    盈亏金额
    """
    return position.calculate_profit(current_price)


def calculate_trade_profit(buy_trade, sell_trade):
    """
    计算单笔交易盈亏
    
    参数:
    buy_trade: 买入交易Trade对象
    sell_trade: 卖出交易Trade对象
    
    返回:
    盈亏金额
    """
    if buy_trade.trade_type != 'BUY' or sell_trade.trade_type != 'SELL':
        raise ValueError("交易类型错误")
    
    buy_cost = buy_trade.price * buy_trade.quantity + buy_trade.commission
    sell_income = sell_trade.price * sell_trade.quantity - sell_trade.commission
    profit = sell_income - buy_cost
    return profit


def calculate_total_profit(trades):
    """
    计算总盈亏
    
    参数:
    trades: 交易记录列表
    
    返回:
    总盈亏金额
    """
    total_profit = 0
    # 按股票代码分组交易
    stock_trades = {}
    for trade in trades:
        if trade.stock_code not in stock_trades:
            stock_trades[trade.stock_code] = []
        stock_trades[trade.stock_code].append(trade)
    
    # 计算每只股票的盈亏
    for stock_code, trades_list in stock_trades.items():
        # 按时间排序
        trades_list.sort(key=lambda x: x.trade_date)
        
        # 匹配买入和卖出交易
        buy_trades = [t for t in trades_list if t.trade_type == 'BUY']
        sell_trades = [t for t in trades_list if t.trade_type == 'SELL']
        
        # 简单匹配（先进先出）
        i, j = 0, 0
        while i < len(buy_trades) and j < len(sell_trades):
            buy_trade = buy_trades[i]
            sell_trade = sell_trades[j]
            
            # 计算可匹配的数量
            match_quantity = min(buy_trade.quantity, sell_trade.quantity)
            
            # 创建匹配的交易对象（用于计算）
            match_buy = Trade(
                buy_trade.stock_code,
                buy_trade.stock_name,
                'BUY',
                buy_trade.price,
                match_quantity,
                buy_trade.trade_date,
                buy_trade.commission * match_quantity / buy_trade.quantity if buy_trade.quantity > 0 else 0
            )
            
            match_sell = Trade(
                sell_trade.stock_code,
                sell_trade.stock_name,
                'SELL',
                sell_trade.price,
                match_quantity,
                sell_trade.trade_date,
                sell_trade.commission * match_quantity / sell_trade.quantity if sell_trade.quantity > 0 else 0
            )
            
            # 计算盈亏
            profit = calculate_trade_profit(match_buy, match_sell)
            total_profit += profit
            
            # 更新剩余数量
            buy_trade.quantity -= match_quantity
            sell_trade.quantity -= match_quantity
            
            # 移动到下一个交易
            if buy_trade.quantity == 0:
                i += 1
            if sell_trade.quantity == 0:
                j += 1
    
    return total_profit


def calculate_return_rate(buy_trade, sell_trade):
    """
    计算收益率
    
    参数:
    buy_trade: 买入交易Trade对象
    sell_trade: 卖出交易Trade对象
    
    返回:
    收益率 (如0.1表示10%)
    """
    profit = calculate_trade_profit(buy_trade, sell_trade)
    buy_cost = buy_trade.price * buy_trade.quantity + buy_trade.commission
    if buy_cost == 0:
        return 0
    return profit / buy_cost


def calculate_risk_reward_ratio(take_profit_price, stop_loss_price, buy_price):
    """
    计算风险收益比
    
    参数:
    take_profit_price: 止盈价格
    stop_loss_price: 止损价格
    buy_price: 买入价格
    
    返回:
    风险收益比
    """
    if buy_price <= 0:
        raise ValueError("买入价格必须大于0")
    
    profit = take_profit_price - buy_price
    loss = buy_price - stop_loss_price
    
    if loss == 0:
        return float('inf') if profit > 0 else 0
    
    return profit / loss