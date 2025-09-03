def calculate_stock_profit(buy_price, quantity, target_profit_percent):
    """
    计算股票止盈信息
    
    参数:
    buy_price: 购买单价
    quantity: 购买数量
    target_profit_percent: 止盈百分比 (例如: 10 表示 10%)
    
    返回:
    dict: 包含每股止盈价格、最终销售金额、获利金额
    """
    
    # 计算每股止盈价格
    target_price = buy_price * (1 + target_profit_percent / 100)
    
    # 计算买入总金额
    buy_amount = buy_price * quantity
    
    # 计算卖出总金额
    sell_amount = target_price * quantity
    
    # 计算手续费 (0.023%的手续费，不满5块按5块计算)
    buy_fee = max(5, buy_amount * 0.00023)
    sell_fee = max(5, sell_amount * 0.00023)
    total_fee = buy_fee + sell_fee
    
    # 计算获利金额
    profit = sell_amount - buy_amount - total_fee
    
    return {
        "每股止盈价格": round(target_price, 2),
        "最终销售金额": round(sell_amount, 2),
        "总手续费": round(total_fee, 2),
        "获利金额": round(profit, 2)
    }

def main():
    print("=== 股票止盈计算器 ===")
    
    try:
        # 获取用户输入
        buy_price = float(input("请输入购买单价: "))
        quantity = int(input("请输入购买数量: "))
        target_profit_percent = float(input("请输入止盈百分比: "))
        
        # 计算结果
        result = calculate_stock_profit(buy_price, quantity, target_profit_percent)
        
        # 显示结果
        print("\n=== 计算结果 ===")
        print(f"每股止盈价格: {result['每股止盈价格']} 元")
        print(f"最终销售金额: {result['最终销售金额']} 元")
        print(f"总手续费: {result['总手续费']} 元")
        print(f"获利金额: {result['获利金额']} 元")
        
    except ValueError:
        print("输入错误，请确保输入的是有效数字！")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()