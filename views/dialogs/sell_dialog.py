from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
                             QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtCore import QDate


class SellDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增卖出交易")
        self.setGeometry(200, 200, 400, 350)
        
        # 创建布局
        layout = QFormLayout(self)
        
        # 创建输入控件
        self.position_combo = QComboBox()
        self.position_combo.addItems(["请选择持仓..."])
        self.sell_price_input = QLineEdit("")
        self.sell_quantity_input = QLineEdit("")
        self.all_button = QPushButton("全部")
        self.trade_date_input = QDateEdit()
        self.trade_date_input.setDate(QDate.currentDate())
        self.trade_date_input.setDisplayFormat("yyyy-MM-dd")
        self.fee_input = QLineEdit("5.00")
        self.total_amount_label = QLabel("0.00")
        self.expected_profit_label = QLabel("0.00")
        
        # 添加到布局
        layout.addRow("持仓股票:", self.position_combo)
        layout.addRow("卖出价格:", self.sell_price_input)
        layout.addRow("卖出数量:", self.sell_quantity_input)
        layout.addWidget(self.all_button)
        layout.addRow("交易日期:", self.trade_date_input)
        layout.addRow("手续费:", self.fee_input)
        layout.addRow("总金额:", self.total_amount_label)
        layout.addRow("预计盈利:", self.expected_profit_label)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确认卖出")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow(button_layout)
    
    def prefill_from_position(self, name: str, quantity: str, current_price: str):
        """根据选中持仓预填字段"""
        self.position_combo.clear()
        self.position_combo.addItem(f"{name}")
        self.position_combo.setCurrentIndex(0)
        if current_price:
            self.sell_price_input.setText(str(current_price))
        if quantity:
            self.sell_quantity_input.setText(str(quantity))
    
    def accept(self):
        """确认卖出"""
        # 这里应该添加数据验证逻辑
        super().accept()