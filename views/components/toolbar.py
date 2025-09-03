from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton


class Toolbar(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.create_toolbar()
    
    def create_toolbar(self):
        """创建工具栏"""
        search_label = QLabel("股票搜索:")
        self.stock_search_input = QLineEdit()
        self.stock_search_input.setPlaceholderText("输入股票代码")
        self.stock_search_input.setFixedWidth(120)
        
        search_button = QPushButton("🔍")
        search_button.setFixedWidth(30)
        
        add_button = QPushButton("+")
        add_button.setFixedWidth(30)
        # 修复引用问题
        add_button.clicked.connect(self.on_add_button_clicked)
        
        self.addWidget(search_label)
        self.addWidget(self.stock_search_input)
        self.addWidget(search_button)
        self.addWidget(add_button)
        self.addStretch()
    
    def on_add_button_clicked(self):
        """处理添加按钮点击事件"""
        # 这里应该打开买入对话框
        from views.dialogs.buy_dialog import BuyDialog
        dialog = BuyDialog(self.parent)
        if dialog.exec() == BuyDialog.DialogCode.Accepted:
            # 这里应该处理买入逻辑
            self.parent.statusBar().show_message("买入交易已记录")
            self.parent.refresh_data()