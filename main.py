import json
from datetime import datetime
from utils.data_manager import DataManager
from controllers.trade_controller import TradeController
from controllers.plan_controller import PlanController
from utils.calculator import calculate_position_profit, calculate_total_profit


def main():
    """主程序入口"""
    print("=== 股票交易记录系统 ===")
    
    # 初始化数据管理器
    data_manager = DataManager()
    
    # 初始化控制器
    trade_controller = TradeController(data_manager)
    plan_controller = PlanController(data_manager)
    
    while True:
        print("\n请选择操作:")
        print("1. 买入股票")
        print("2. 卖出股票")
        print("3. 设置止盈止损计划")
        print("4. 查看持仓")
        print("5. 查看交易记录")
        print("6. 查看止盈止损计划")
        print("7. 检查止盈止损条件")
        print("8. 计算总盈亏")
        print("9. 退出")
        
        choice = input("请输入选项 (1-9): ").strip()
        
        if choice == '1':
            # 买入股票
            try:
                stock_code = input("请输入股票代码: ").strip()
                stock_name = input("请输入股票名称: ").strip()
                price = float(input("请输入买入价格: "))
                quantity = int(input("请输入买入数量: "))
                
                trade = trade_controller.execute_buy(stock_code, stock_name, price, quantity)
                print(f"买入成功! 交易ID: {trade.id}")
            except ValueError as e:
                print(f"输入错误: {e}")
            except Exception as e:
                print(f"买入失败: {e}")
        
        elif choice == '2':
            # 卖出股票
            try:
                positions = data_manager.get_positions()
                if not positions:
                    print("当前没有持仓")
                    continue
                
                print("当前持仓:")
                for i, pos in enumerate(positions):
                    if pos.status == 'HOLDING':
                        print(f"{i+1}. {pos.stock_name}({pos.stock_code}) - 数量: {pos.quantity}, 成本价: {pos.buy_price}")
                
                try:
                    pos_index = int(input("请选择要卖出的持仓序号: ")) - 1
                    if pos_index < 0 or pos_index >= len([p for p in positions if p.status == 'HOLDING']):
                        print("序号无效")
                        continue
                except ValueError:
                    print("请输入有效的数字")
                    continue
                
                position = positions[pos_index]
                price = float(input("请输入卖出价格: "))
                quantity = int(input(f"请输入卖出数量 (最多{position.quantity}): "))
                
                if quantity > position.quantity:
                    print("卖出数量超过持仓数量")
                    continue
                
                trade = trade_controller.execute_sell(position.id, price, quantity)
                print(f"卖出成功! 交易ID: {trade.id}")
            except ValueError as e:
                print(f"输入错误: {e}")
            except Exception as e:
                print(f"卖出失败: {e}")
        
        elif choice == '3':
            # 设置止盈止损计划
            try:
                positions = data_manager.get_positions()
                if not positions:
                    print("当前没有持仓")
                    continue
                
                print("当前持仓:")
                for i, pos in enumerate(positions):
                    if pos.status == 'HOLDING':
                        print(f"{i+1}. {pos.stock_name}({pos.stock_code}) - 数量: {pos.quantity}, 成本价: {pos.buy_price}")
                
                try:
                    pos_index = int(input("请选择持仓序号: ")) - 1
                    holding_positions = [p for p in positions if p.status == 'HOLDING']
                    if pos_index < 0 or pos_index >= len(holding_positions):
                        print("序号无效")
                        continue
                    position = holding_positions[pos_index]
                except ValueError:
                    print("请输入有效的数字")
                    continue
                
                position = positions[pos_index]
                
                print("请选择计划类型:")
                print("1. 价格触发")
                print("2. 百分比触发")
                
                plan_type = input("请输入选项 (1-2): ").strip()
                
                auto_execute = input("是否自动执行? (y/n): ").strip().lower() == 'y'
                
                if plan_type == '1':
                    take_profit_price = input("请输入止盈价格 (直接回车跳过): ").strip()
                    take_profit_price = float(take_profit_price) if take_profit_price else None
                    
                    stop_loss_price = input("请输入止损价格 (直接回车跳过): ").strip()
                    stop_loss_price = float(stop_loss_price) if stop_loss_price else None
                    
                    if take_profit_price is None and stop_loss_price is None:
                        print("至少需要设置一个价格")
                        continue
                    
                    plan = plan_controller.create_price_plan(
                        position.id, take_profit_price, stop_loss_price, auto_execute)
                    print(f"价格触发计划创建成功! 计划ID: {plan.id}")
                
                elif plan_type == '2':
                    take_profit_ratio = input("请输入止盈百分比 (如10表示10%, 直接回车跳过): ").strip()
                    take_profit_ratio = float(take_profit_ratio) / 100 if take_profit_ratio else None
                    
                    stop_loss_ratio = input("请输入止损百分比 (如5表示5%, 直接回车跳过): ").strip()
                    stop_loss_ratio = float(stop_loss_ratio) / 100 if stop_loss_ratio else None
                    
                    if take_profit_ratio is None and stop_loss_ratio is None:
                        print("至少需要设置一个百分比")
                        continue
                    
                    plan = plan_controller.create_percentage_plan(
                        position.id, take_profit_ratio, stop_loss_ratio, auto_execute)
                    print(f"百分比触发计划创建成功! 计划ID: {plan.id}")
                
                else:
                    print("无效选项")
            
            except ValueError as e:
                print(f"输入错误: {e}")
            except Exception as e:
                print(f"创建计划失败: {e}")
        
        elif choice == '4':
            # 查看持仓
            positions = data_manager.get_positions()
            if not positions:
                print("当前没有持仓")
                continue
            
            print("当前持仓:")
            for pos in positions:
                if pos.status == 'HOLDING':
                    print(f"- {pos.stock_name}({pos.stock_code})")
                    print(f"  数量: {pos.quantity}")
                    print(f"  成本价: {pos.buy_price}")
                    print(f"  买入日期: {pos.buy_date}")
                    print(f"  手续费: {pos.commission}")
                    print(f"  关联计划数: {len(pos.plans)}")
                    print()
        
        elif choice == '5':
            # 查看交易记录
            trades = data_manager.get_trades()
            if not trades:
                print("当前没有交易记录")
                continue
            
            print("交易记录:")
            for trade in trades:
                print(f"- {trade.stock_name}({trade.stock_code})")
                print(f"  类型: {'买入' if trade.trade_type == 'BUY' else '卖出'}")
                print(f"  价格: {trade.price}")
                print(f"  数量: {trade.quantity}")
                print(f"  日期: {trade.trade_date}")
                print(f"  手续费: {trade.commission}")
                print(f"  总金额: {trade.total_amount}")
                print()
        
        elif choice == '6':
            # 查看止盈止损计划
            plans = data_manager.get_plans()
            if not plans:
                print("当前没有止盈止损计划")
                continue
            
            print("止盈止损计划:")
            for plan in plans:
                position = data_manager.get_position_by_id(plan.position_id)
                if position:
                    print(f"- {position.stock_name}({position.stock_code})")
                    print(f"  计划ID: {plan.id}")
                    print(f"  类型: {'价格触发' if plan.trigger_type == 'price' else '百分比触发'}")
                    if plan.trigger_type == 'price':
                        print(f"  止盈价格: {plan.take_profit_price or '未设置'}")
                        print(f"  止损价格: {plan.stop_loss_price or '未设置'}")
                    else:
                        print(f"  止盈百分比: {plan.take_profit_ratio*100 if plan.take_profit_ratio else '未设置'}%")
                        print(f"  止损百分比: {plan.stop_loss_ratio*100 if plan.stop_loss_ratio else '未设置'}%")
                    print(f"  状态: {plan.status}")
                    print(f"  自动执行: {'是' if plan.auto_execute else '否'}")
                    print()
        
        elif choice == '7':
            # 检查止盈止损条件
            try:
                positions = data_manager.get_positions()
                holding_positions = [p for p in positions if p.status == 'HOLDING']
                if not holding_positions:
                    print("当前没有持仓")
                    continue
                
                current_prices = {}
                print("请输入各股票的当前价格:")
                for pos in holding_positions:
                    while True:
                        price_input = input(f"{pos.stock_name}({pos.stock_code}): ").strip()
                        if price_input:
                            try:
                                current_prices[pos.stock_code] = float(price_input)
                                break
                            except ValueError:
                                print("请输入有效的数字")
                        else:
                            print("价格不能为空，请重新输入")
                
                # 检查计划但不自动执行
                plan_controller.check_and_execute_plans(current_prices)
                print("止盈止损检查完成")
            except Exception as e:
                print(f"检查计划失败: {e}")
        
        elif choice == '8':
            # 计算总盈亏
            trades = data_manager.get_trades()
            if not trades:
                print("当前没有交易记录")
                continue
            
            total_profit = calculate_total_profit(trades)
            print(f"历史交易总盈亏: {total_profit:.2f} 元")
            
            # 显示各持仓盈亏
            positions = data_manager.get_positions()
            holding_positions = [p for p in positions if p.status == 'HOLDING']
            if holding_positions:
                print("\n当前持仓详情:")
                for pos in holding_positions:
                    try:
                        current_price = float(input(f"请输入{pos.stock_name}({pos.stock_code})的当前价格: "))
                        profit = calculate_position_profit(pos, current_price)
                        print(f"{pos.stock_name}({pos.stock_code}):")
                        print(f"  持仓数量: {pos.quantity}")
                        print(f"  成本价: {pos.buy_price:.2f}元")
                        print(f"  当前价格: {current_price:.2f}元")
                        print(f"  浮动盈亏: {profit:.2f}元")
                        print(f"  收益率: {(profit / (pos.buy_price * pos.quantity) * 100):.2f}%")
                        
                        # 检查是否有止盈止损计划
                        plans = [data_manager.get_plan_by_id(plan_id) for plan_id in pos.plans]
                        active_plans = [plan for plan in plans if plan and plan.status == 'ACTIVE']
                        if active_plans:
                            print("  止盈止损计划:")
                            for plan in active_plans:
                                if plan.trigger_type == 'price':
                                    if plan.take_profit_price:
                                        take_profit_value = (plan.take_profit_price - pos.buy_price) * pos.quantity
                                        print(f"    止盈价格: {plan.take_profit_price:.2f}元, 预期盈利: {take_profit_value:.2f}元")
                                    if plan.stop_loss_price:
                                        stop_loss_value = (plan.stop_loss_price - pos.buy_price) * pos.quantity
                                        print(f"    止损价格: {plan.stop_loss_price:.2f}元, 预期亏损: {stop_loss_value:.2f}元")
                                else:  # percentage
                                    if plan.take_profit_ratio:
                                        take_profit_price = pos.buy_price * (1 + plan.take_profit_ratio)
                                        take_profit_value = (take_profit_price - pos.buy_price) * pos.quantity
                                        print(f"    止盈比例: {plan.take_profit_ratio*100:.2f}%, 预期盈利: {take_profit_value:.2f}元")
                                    if plan.stop_loss_ratio:
                                        stop_loss_price = pos.buy_price * (1 - plan.stop_loss_ratio)
                                        stop_loss_value = (stop_loss_price - pos.buy_price) * pos.quantity
                                        print(f"    止损比例: {plan.stop_loss_ratio*100:.2f}%, 预期亏损: {stop_loss_value:.2f}元")
                        print()
                    except ValueError:
                        print(f"未输入有效价格，跳过{pos.stock_name}的浮动盈亏计算")
            else:
                print("当前没有持仓")
        
        elif choice == '9':
            # 退出
            print("感谢使用股票交易记录系统!")
            break
        
        else:
            print("无效选项，请重新输入")


if __name__ == "__main__":
    main()