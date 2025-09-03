from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, 
                             QHBoxLayout, QPushButton, QGroupBox)


class PlanDetailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("止盈止损计划详情")
        self.setGeometry(200, 200, 400, 460)
        
        # 创建布局
        self.layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel("止盈止损计划详情")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(self.title_label)
        
        # 容器占位，内容在 load_for_name 中填充
        self.content_group = QGroupBox("详情")
        self.content_form = QFormLayout(self.content_group)
        self.layout.addWidget(self.content_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        self.layout.addLayout(button_layout)
    
    def _format_price(self, p: float) -> str:
        return f"{p:.4f}" if p < 10 else f"{p:.2f}"
    
    def _calc_sell_fee(self, target_price: float, quantity: float) -> float:
        amount = target_price * quantity
        fee = amount * 0.00025
        return 5.0 if fee < 5.0 and quantity > 0 else fee
    
    def load_for_name(self, name: str):
        dm = getattr(self.parent(), 'data_manager', None) if self.parent() else None
        plan = dm.find_latest_plan_by_name(name) if dm else None
        # 清空
        while self.content_form.rowCount() > 0:
            self.content_form.removeRow(0)
        if not plan:
            self.content_form.addRow("提示:", QLabel("未找到该股票的计划"))
            return
        # 渲染真实计划
        quantity = float(plan.get('quantity', 0) or 0)
        cost_price = float(plan.get('cost_price', 0) or 0)
        tp_price = float(plan.get('take_profit_price', 0) or 0)
        tp_ratio = float(plan.get('take_profit_ratio', 0) or 0)
        sl_price = float(plan.get('stop_loss_price', 0) or 0)
        sl_ratio = float(plan.get('stop_loss_ratio', 0) or 0)
        buy_fee_total = float(plan.get('buy_fee_total', 0) or 0)
        
        self.content_form.addRow("股票:", QLabel(str(plan.get('name', ''))))
        self.content_form.addRow("持仓:", QLabel(f"{int(quantity)}股"))
        self.content_form.addRow("成本价:", QLabel(self._format_price(cost_price)))
        self.content_form.addRow("止盈价:", QLabel(self._format_price(tp_price)))
        self.content_form.addRow("止盈幅:", QLabel(f"{tp_ratio*100:.2f}%"))
        self.content_form.addRow("止损价:", QLabel(self._format_price(sl_price)))
        self.content_form.addRow("止损幅:", QLabel(f"{sl_ratio*100:.2f}%"))
        self.content_form.addRow("买入手续费:", QLabel(f"{buy_fee_total:.2f}"))
       
        
        # 预计盈亏（含费用）
        cost_total = cost_price * quantity + buy_fee_total
        tp_sell_fee = self._calc_sell_fee(tp_price, quantity)
        sl_sell_fee = self._calc_sell_fee(sl_price, quantity)
        tp_income = tp_price * quantity - tp_sell_fee
        sl_income = sl_price * quantity - sl_sell_fee
        tp_profit = tp_income - cost_total
        sl_profit = sl_income - cost_total
        
        self.content_form.addRow("止盈预计盈亏:", QLabel(f"{tp_profit:+.2f} 元 (含卖费{tp_sell_fee:.2f})"))
        self.content_form.addRow("止损预计盈亏:", QLabel(f"{sl_profit:+.2f} 元 (含卖费{sl_sell_fee:.2f})"))
        self.content_form.addRow("创建时间:", QLabel(str(plan.get('created_at', ''))))