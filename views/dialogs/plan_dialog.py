from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
                             QHBoxLayout, QPushButton, QLabel, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator


class PlanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置止盈止损计划")
        self.setGeometry(200, 200, 500, 500)
        
        self._updating = False
        self._cost_price = 0.0
        self._quantity = 0.0
        self._code_name = ""
        self._buy_fee_total = 0.0
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 持仓信息（动态）
        self.info_label = QLabel("请选择持仓")
        self.info_label.setStyleSheet("font-weight: bold; margin: 10px;")
        layout.addWidget(self.info_label)
        
        # 成本价信息
        self.cost_label = QLabel("当前成本价: -")
        self.cost_label.setStyleSheet("margin: 0 10px 10px 10px;")
        layout.addWidget(self.cost_label)
        
        # 止盈计划组（去掉触发方式，仅保留价格与百分比）
        take_profit_group = QGroupBox("止盈计划")
        take_profit_layout = QFormLayout(take_profit_group)
        
        self.take_profit_price_input = QLineEdit("")
        self.take_profit_ratio_input = QLineEdit("")
        self._apply_numeric_validator(self.take_profit_ratio_input)
        
        take_profit_layout.addRow("目标价格:", self.take_profit_price_input)
        take_profit_layout.addRow("目标涨幅(%):", self.take_profit_ratio_input)
        
        layout.addWidget(take_profit_group)
        
        # 止损计划组（去掉触发方式，仅保留价格与百分比）
        stop_loss_group = QGroupBox("止损计划")
        stop_loss_layout = QFormLayout(stop_loss_group)
        
        self.stop_loss_price_input = QLineEdit("")
        self.stop_loss_ratio_input = QLineEdit("")
        self._apply_numeric_validator(self.stop_loss_ratio_input)
        
        stop_loss_layout.addRow("目标价格:", self.stop_loss_price_input)
        stop_loss_layout.addRow("目标跌幅(%):", self.stop_loss_ratio_input)
        
        layout.addWidget(stop_loss_group)
        
        # 计划分析组
        analysis_group = QGroupBox("计划分析")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analysis_label = QLabel("请完善参数后显示预计盈亏")
        analysis_layout.addWidget(self.analysis_label)
        
        layout.addWidget(analysis_group)
        
        # 事件连接：双向联动（价格 ↔ 百分比）
        self.take_profit_ratio_input.textChanged.connect(self._on_take_profit_ratio_changed)
        self.take_profit_price_input.textChanged.connect(self._on_take_profit_price_changed)
        self.stop_loss_ratio_input.textChanged.connect(self._on_stop_loss_ratio_changed)
        self.stop_loss_price_input.textChanged.connect(self._on_stop_loss_price_changed)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("保存计划")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _apply_numeric_validator(self, line_edit: QLineEdit):
        validator = QDoubleValidator(0.0, 1000.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        line_edit.setValidator(validator)
        line_edit.setPlaceholderText("单位 %，如 6 表示 6%")
    
    def _get_data_manager(self):
        try:
            return getattr(self.parent(), 'data_manager', None)
        except Exception:
            return None
    
    def _calc_buy_fee_total(self, code_name: str) -> float:
        dm = self._get_data_manager()
        if not dm:
            # 兜底：按聚合估算
            est = self._cost_price * self._quantity * 0.00025
            return 5.0 if est < 5.0 and self._quantity > 0 else est
        fee_total = 0.0
        try:
            for h in dm.get_history():
                if str(h.get('type', '')) != "买入":
                    continue
                if str(h.get('code', '')) != code_name:
                    continue
                price = float(h.get('price', 0) or 0)
                qty = float(h.get('quantity', 0) or 0)
                amount = price * qty
                fee = amount * 0.00025
                if fee < 5.0:
                    fee = 5.0
                fee_total += fee
        except Exception:
            pass
        if fee_total == 0.0:
            # 没有历史，退回估算
            est = self._cost_price * self._quantity * 0.00025
            if est < 5.0 and self._quantity > 0:
                est = 5.0
            return est
        return fee_total
    
    def prefill_from_position(self, name: str, quantity: str, cost_price: str):
        """根据选中持仓预填显示，并设置默认止盈6%/止损3%及对应价格；并载入买入手续费总额"""
        self._code_name = name or ""
        self.info_label.setText(f"持仓股票: {name} ({quantity}股)")
        # 解析数据
        try:
            self._quantity = float(str(quantity).replace(',', '') or 0)
        except Exception:
            self._quantity = 0.0
        try:
            self._cost_price = float(cost_price or 0)
        except Exception:
            self._cost_price = 0.0
        self.cost_label.setText(f"当前成本价: {self._format_price(self._cost_price)}")
        
        # 计算买入手续费总额
        self._buy_fee_total = self._calc_buy_fee_total(self._code_name)
        
        # 默认 6% / 3%
        self._updating = True
        try:
            self.take_profit_ratio_input.setText("6")
            tp_price = self._cost_price * (1.0 + 0.06)
            self.take_profit_price_input.setText(self._format_price(tp_price))
            
            self.stop_loss_ratio_input.setText("3")
            sl_price = self._cost_price * (1.0 - 0.03)
            self.stop_loss_price_input.setText(self._format_price(sl_price))
        finally:
            self._updating = False
        
        self._update_analysis()
    
    def _parse_ratio_percent(self, text: str) -> float:
        """解析百分比数字（如 '6' -> 0.06, '1' -> 0.01）"""
        try:
            val = float(text) if text not in (None, "") else 0.0
        except Exception:
            val = 0.0
        return val / 100.0
    
    def _format_ratio_number(self, r: float) -> str:
        """将比例转为数字百分比（如 0.06 -> '6.00'）"""
        return f"{r*100:.2f}"
    
    def _parse_price(self, text: str) -> float:
        try:
            return float(text)
        except Exception:
            return 0.0
    
    def _format_price(self, p: float) -> str:
        return f"{p:.4f}" if p < 10 else f"{p:.2f}"
    
    def _on_take_profit_ratio_changed(self, _):
        if self._updating:
            return
        self._updating = True
        try:
            r = self._parse_ratio_percent(self.take_profit_ratio_input.text())
            price = self._cost_price * (1.0 + r)
            self.take_profit_price_input.setText(self._format_price(price))
        finally:
            self._updating = False
        self._update_analysis()
    
    def _on_take_profit_price_changed(self, _):
        if self._updating:
            return
        self._updating = True
        try:
            p = self._parse_price(self.take_profit_price_input.text())
            if self._cost_price > 0:
                r = (p - self._cost_price) / self._cost_price
            else:
                r = 0.0
            self.take_profit_ratio_input.setText(self._format_ratio_number(r))
        finally:
            self._updating = False
        self._update_analysis()
    
    def _on_stop_loss_ratio_changed(self, _):
        if self._updating:
            return
        self._updating = True
        try:
            r = self._parse_ratio_percent(self.stop_loss_ratio_input.text())
            price = self._cost_price * (1.0 - r)
            self.stop_loss_price_input.setText(self._format_price(price))
        finally:
            self._updating = False
        self._update_analysis()
    
    def _on_stop_loss_price_changed(self, _):
        if self._updating:
            return
        self._updating = True
        try:
            p = self._parse_price(self.stop_loss_price_input.text())
            if self._cost_price > 0:
                r = max(0.0, (self._cost_price - p) / self._cost_price)
            else:
                r = 0.0
            self.stop_loss_ratio_input.setText(self._format_ratio_number(r))
        finally:
            self._updating = False
        self._update_analysis()
    
    def _calc_sell_fee(self, target_price: float) -> float:
        amount = target_price * self._quantity
        fee = amount * 0.00025
        return 5.0 if fee < 5.0 and self._quantity > 0 else fee
    
    def _update_analysis(self):
        """根据当前参数预估盈亏（含手续费）"""
        if self._quantity <= 0 or self._cost_price <= 0:
            self.analysis_label.setText("请完善持仓数量与成本价")
            return
        # 止盈预估
        tp = self._parse_price(self.take_profit_price_input.text())
        tp_sell_fee = self._calc_sell_fee(tp)
        tp_cost = self._cost_price * self._quantity + self._buy_fee_total
        tp_income = tp * self._quantity - tp_sell_fee
        tp_profit = tp_income - tp_cost
        # 止损预估
        sl = self._parse_price(self.stop_loss_price_input.text())
        sl_sell_fee = self._calc_sell_fee(sl)
        sl_cost = tp_cost
        sl_income = sl * self._quantity - sl_sell_fee
        sl_profit = sl_income - sl_cost
        self.analysis_label.setText(
            f"若达到止盈价: 预计盈亏 {tp_profit:+.2f}元 (含买费{self._buy_fee_total:.2f}、卖费{tp_sell_fee:.2f})\n"
            f"若达到止损价: 预计盈亏 {sl_profit:+.2f}元 (含买费{self._buy_fee_total:.2f}、卖费{sl_sell_fee:.2f})"
        )
    
    def accept(self):
        """保存计划：写入 DataManager plans 简化版（按名称聚合）"""
        dm = self._get_data_manager()
        if dm:
            plan = {
                'id': f'plan-{self._code_name}',
                'name': self._code_name,
                'quantity': self._quantity,
                'cost_price': self._cost_price,
                'take_profit_price': self._parse_price(self.take_profit_price_input.text()),
                'take_profit_ratio': self._parse_ratio_percent(self.take_profit_ratio_input.text()),
                'stop_loss_price': self._parse_price(self.stop_loss_price_input.text()),
                'stop_loss_ratio': self._parse_ratio_percent(self.stop_loss_ratio_input.text()),
                'buy_fee_total': self._buy_fee_total,
                'created_at': __import__('datetime').datetime.now().isoformat()
            }
            try:
                # 先删除同名旧计划，再添加
                existing = dm.find_latest_plan_by_name(self._code_name)
                if existing:
                    dm.delete_plan(existing.get('id'))
            except Exception:
                pass
            dm.add_plan(plan)
        super().accept()