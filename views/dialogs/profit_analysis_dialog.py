from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QHBoxLayout, 
                             QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView)
from PyQt6.QtCore import Qt


class ProfitAnalysisDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("盈利分析报告")
        self.setGeometry(150, 150, 600, 500)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("盈利分析报告")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 总体统计
        self.overall_group = QGroupBox("📊 总体统计")
        self.overall_layout = QVBoxLayout(self.overall_group)
        
        self.total_invest_label = QLabel("总投入资金: -")
        self.total_market_value_label = QLabel("当前总市值: -")
        self.total_profit_label = QLabel("总盈利: -")
        
        self.overall_layout.addWidget(self.total_invest_label)
        self.overall_layout.addWidget(self.total_market_value_label)
        self.overall_layout.addWidget(self.total_profit_label)
        
        layout.addWidget(self.overall_group)
        
        # 持仓分析
        self.position_group = QGroupBox("📈 持仓分析")
        position_layout = QVBoxLayout(self.position_group)
        
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(5)
        self.position_table.setHorizontalHeaderLabels(["股票", "持仓", "成本", "市值", "盈亏"])
        self.position_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.position_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.position_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        position_layout.addWidget(self.position_table)
        layout.addWidget(self.position_group)
        
        # 计划分析（占位）
        self.plan_group = QGroupBox("📋 计划分析")
        plan_layout = QVBoxLayout(self.plan_group)
        plan_layout.addWidget(QLabel("尚未接入计划数据"))
        layout.addWidget(self.plan_group)
        
        # 风险评估（简易占位）
        self.risk_group = QGroupBox("📊 风险评估")
        risk_layout = QVBoxLayout(self.risk_group)
        risk_layout.addWidget(QLabel("基于当前持仓简单估算"))
        layout.addWidget(self.risk_group)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
    
    def _build_buy_commission_map(self, history):
        code_to_fee = {}
        for h in history:
            try:
                if str(h.get('type', '')) != "买入":
                    continue
                code = str(h.get('code', ''))
                price = float(h.get('price', 0) or 0)
                quantity = float(h.get('quantity', 0) or 0)
                amount = price * quantity
                fee = amount * 0.00025
                if fee < 5.0:
                    fee = 5.0
                code_to_fee[code] = code_to_fee.get(code, 0.0) + fee
            except Exception:
                continue
        return code_to_fee
    
    def load_from_data_manager(self, data_manager):
        """从 DataManager 载入数据并填充统计与表格（动态市值 + 交易级买入佣金）"""
        positions = data_manager.get_positions()
        history = data_manager.get_history()
        buy_fee_map = self._build_buy_commission_map(history)
        
        total_invest = 0.0
        total_market = 0.0
        total_profit = 0.0
        
        self.position_table.setRowCount(0)
        for p in positions:
            try:
                name = str(p.get('name', ''))
                quantity = float(p.get('quantity', 0) or 0)
                cost_price = float(p.get('cost_price', 0) or 0)
                current_price = float(p.get('current_price', 0) or 0)
                market_value = current_price * quantity
                fee_total = buy_fee_map.get(name, 0.0)
                cost_total = cost_price * quantity + fee_total
                profit = market_value - cost_total
                
                total_invest += cost_total
                total_market += market_value
                total_profit += profit
                
                row = self.position_table.rowCount()
                self.position_table.insertRow(row)
                self.position_table.setItem(row, 0, QTableWidgetItem(name))
                self.position_table.setItem(row, 1, QTableWidgetItem(f"{int(quantity) if quantity.is_integer() else quantity:.0f}"))
                self.position_table.setItem(row, 2, QTableWidgetItem(f"{cost_total:.2f}"))
                self.position_table.setItem(row, 3, QTableWidgetItem(f"{market_value:.2f}"))
                self.position_table.setItem(row, 4, QTableWidgetItem(("+" if profit>0 else ("-" if profit<0 else "")) + f"{abs(profit):.2f}"))
            except Exception:
                continue
        
        self.total_invest_label.setText(f"总投入资金: ¥{total_invest:.2f}")
        self.total_market_value_label.setText(f"当前总市值: ¥{total_market:.2f}")
        ratio = (total_profit / total_invest * 100.0) if total_invest>0 else 0.0
        sign = "+" if total_profit>0 else ("-" if total_profit<0 else "")
        self.total_profit_label.setText(f"总盈利: ¥{sign}{abs(total_profit):.2f} ({sign}{abs(ratio):.2f}%)")