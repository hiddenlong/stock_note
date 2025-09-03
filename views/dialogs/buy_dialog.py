from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QDateEdit, 
                             QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtCore import QDate


class BuyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增买入交易")
        self.setGeometry(200, 200, 400, 300)
        
        # 创建布局
        layout = QFormLayout(self)
        
        # 创建输入控件
        self.stock_code_input = QLineEdit()
        self.stock_name_input = QLineEdit("")
        self.buy_price_input = QLineEdit("0")
        self.buy_quantity_input = QLineEdit("0")
        self.trade_date_input = QDateEdit()
        self.trade_date_input.setDate(QDate.currentDate())
        self.trade_date_input.setDisplayFormat("yyyy-MM-dd")
        self.fee_input = QLineEdit("5.00")
        self.total_amount_label = QLabel("0.00")
        
        # 添加到布局
        layout.addRow("股票代码:", self.stock_code_input)
        layout.addRow("股票名称:", self.stock_name_input)
        layout.addRow("买入价格:", self.buy_price_input)
        layout.addRow("买入数量:", self.buy_quantity_input)
        layout.addRow("交易日期:", self.trade_date_input)
        layout.addRow("手续费:", self.fee_input)
        layout.addRow("总金额:", self.total_amount_label)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确认买入")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow(button_layout)
    
    def accept(self):
        """确认买入"""
        # 这里应该添加数据验证逻辑
        super().accept()