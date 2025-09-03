import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QTableWidget, QTableWidgetItem, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QDateEdit, QMessageBox, 
                             QGroupBox, QFormLayout, QTextEdit, QStatusBar, QHeaderView,
                             QAbstractItemView, QMenu, QFileDialog, QSplitter, QFrame,
                             QDialog)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont, QColor, QAction, QIcon


class StockTradingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票交易记录系统 v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        
        # 创建搜索和工具栏
        self.create_search_toolbar()
        
        # 创建持仓和交易历史区域
        self.create_main_content()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 初始化数据
        self.init_data()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        new_buy_action = QAction('新增买入', self)
        new_buy_action.setShortcut('Ctrl+N')
        new_buy_action.triggered.connect(self.on_new_buy)
        file_menu.addAction(new_buy_action)
        
        new_sell_action = QAction('新增卖出', self)
        new_sell_action.setShortcut('Ctrl+S')
        new_sell_action.triggered.connect(self.on_new_sell)
        file_menu.addAction(new_sell_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        plan_action = QAction('设置计划', self)
        plan_action.setShortcut('Ctrl+P')
        plan_action.triggered.connect(self.on_set_plan)
        edit_menu.addAction(plan_action)
        
        # 查看菜单
        view_menu = menubar.addMenu('查看(&V)')
        analysis_action = QAction('盈利分析', self)
        analysis_action.setShortcut('Ctrl+A')
        analysis_action.triggered.connect(self.on_profit_analysis)
        view_menu.addAction(analysis_action)
        
        refresh_action = QAction('刷新', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_search_toolbar(self):
        """创建搜索工具栏"""
        # 搜索区域
        search_layout = QHBoxLayout()
        
        search_label = QLabel("股票搜索:")
        self.stock_search_input = QLineEdit()
        self.stock_search_input.setPlaceholderText("输入股票代码")
        self.stock_search_input.setFixedWidth(120)
        
        search_button = QPushButton("🔍")
        search_button.setFixedWidth(30)
        
        add_button = QPushButton("+")
        add_button.setFixedWidth(30)
        add_button.clicked.connect(self.on_new_buy)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.stock_search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(add_button)
        search_layout.addStretch()
        
        self.main_layout.addLayout(search_layout)
    
    def create_main_content(self):
        """创建主内容区域"""
        # 使用分割器来分割持仓和交易历史
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 持仓区域
        positions_group = QGroupBox("持仓列表")
        positions_layout = QVBoxLayout(positions_group)
        
        # 持仓表格
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)
        self.positions_table.setHorizontalHeaderLabels([
            "股票代码", "股票名称", "持仓", "成本价", "当前价", "盈亏", "计划"
        ])
        
        # 设置表格属性
        self.positions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.positions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.positions_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.positions_table.setAlternatingRowColors(True)
        
        header = self.positions_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # 连接双击事件
        self.positions_table.cellDoubleClicked.connect(self.on_position_double_clicked)
        
        # 右键菜单
        self.positions_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.positions_table.customContextMenuRequested.connect(self.show_positions_context_menu)
        
        positions_layout.addWidget(self.positions_table)
        
        # 持仓操作按钮
        positions_button_layout = QHBoxLayout()
        self.new_buy_button = QPushButton("新增买入")
        self.new_buy_button.clicked.connect(self.on_new_buy)
        
        self.new_sell_button = QPushButton("新增卖出")
        self.new_sell_button.clicked.connect(self.on_new_sell)
        
        self.set_plan_button = QPushButton("设置计划")
        self.set_plan_button.clicked.connect(self.on_set_plan)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_data)
        
        self.profit_analysis_button = QPushButton("盈利分析")
        self.profit_analysis_button.clicked.connect(self.on_profit_analysis)
        
        positions_button_layout.addWidget(self.new_buy_button)
        positions_button_layout.addWidget(self.new_sell_button)
        positions_button_layout.addWidget(self.set_plan_button)
        positions_button_layout.addWidget(self.refresh_button)
        positions_button_layout.addWidget(self.profit_analysis_button)
        positions_button_layout.addStretch()
        
        positions_layout.addLayout(positions_button_layout)
        
        # 交易历史区域
        history_group = QGroupBox("交易记录历史")
        history_layout = QVBoxLayout(history_group)
        
        # 交易历史表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "日期", "类型", "股票代码", "股票名称", "价格", "数量", "金额"
        ])
        
        # 设置表格属性
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        
        header = self.history_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # 右键菜单
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_history_context_menu)
        
        history_layout.addWidget(self.history_table)
        
        # 交易历史操作按钮
        history_button_layout = QHBoxLayout()
        self.export_button = QPushButton("导出Excel")
        self.delete_record_button = QPushButton("删除记录")
        
        history_button_layout.addWidget(self.export_button)
        history_button_layout.addWidget(self.delete_record_button)
        history_button_layout.addStretch()
        
        history_layout.addLayout(history_button_layout)
        
        # 添加到分割器
        splitter.addWidget(positions_group)
        splitter.addWidget(history_group)
        splitter.setSizes([400, 400])  # 设置初始大小
        
        self.main_layout.addWidget(splitter)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def init_data(self):
        """初始化示例数据"""
        # 添加示例持仓数据
        self.add_position_row("600000", "浦发银行", "1000", "10.00", "10.50", "+500", "⚠️")
        self.add_position_row("000001", "平安银行", "500", "12.00", "11.80", "-100", "❌")
        
        # 添加示例交易历史数据
        self.add_history_row("2023-10-01", "买入", "600000", "浦发银行", "10.00", "1000", "10000")
        self.add_history_row("2023-09-15", "买入", "000001", "平安银行", "12.00", "500", "6000")
        
        # 更新状态栏
        self.update_status_bar()
    
    def add_position_row(self, code, name, quantity, cost, current, profit, plan):
        """添加持仓行"""
        row = self.positions_table.rowCount()
        self.positions_table.insertRow(row)
        
        # 创建表格项
        items = [
            QTableWidgetItem(code),
            QTableWidgetItem(name),
            QTableWidgetItem(quantity),
            QTableWidgetItem(cost),
            QTableWidgetItem(current),
            QTableWidgetItem(profit),
            QTableWidgetItem(plan)
        ]
        
        # 设置文本对齐
        items[0].setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        items[1].setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        for i in range(2, 7):
            items[i].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # 设置盈利颜色
        if profit.startswith('+'):
            items[5].setForeground(QColor("#FF0000"))  # 红色
        elif profit.startswith('-'):
            items[5].setForeground(QColor("#008000"))  # 绿色
        
        # 添加到表格
        for i, item in enumerate(items):
            self.positions_table.setItem(row, i, item)
    
    def add_history_row(self, date, type_, code, name, price, quantity, amount):
        """添加交易历史行"""
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        # 创建表格项
        items = [
            QTableWidgetItem(date),
            QTableWidgetItem(type_),
            QTableWidgetItem(code),
            QTableWidgetItem(name),
            QTableWidgetItem(price),
            QTableWidgetItem(quantity),
            QTableWidgetItem(amount)
        ]
        
        # 设置文本对齐
        items[0].setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        items[1].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        items[2].setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        items[3].setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        for i in range(4, 7):
            items[i].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # 设置交易类型颜色
        if type_ == "买入":
            items[1].setForeground(QColor("#0000FF"))  # 蓝色
        else:
            items[1].setForeground(QColor("#FF0000"))  # 红色
        
        # 添加到表格
        for i, item in enumerate(items):
            self.history_table.setItem(row, i, item)
    
    def update_status_bar(self):
        """更新状态栏"""
        current_time = QDate.currentDate().toString("yyyy-MM-dd")
        position_count = self.positions_table.rowCount()
        # 这里应该计算实际的总盈利
        total_profit = "+400"
        plan_count = 2  # 示例值
        
        status_text = f"就绪 | 当前时间: {current_time} | 持仓: {position_count}只 | 总盈利: {total_profit}元 | 计划: {plan_count}个"
        self.status_bar.showMessage(status_text)
    
    def on_new_buy(self):
        """新增买入"""
        dialog = BuyDialog(self)
        if dialog.exec() == BuyDialog.DialogCode.Accepted:
            # 这里应该处理买入逻辑
            QMessageBox.information(self, "买入成功", "买入交易已记录")
            self.refresh_data()
    
    def on_new_sell(self):
        """新增卖出"""
        dialog = SellDialog(self)
        if dialog.exec() == SellDialog.DialogCode.Accepted:
            # 这里应该处理卖出逻辑
            QMessageBox.information(self, "卖出成功", "卖出交易已记录")
            self.refresh_data()
    
    def on_set_plan(self):
        """设置计划"""
        dialog = PlanDialog(self)
        if dialog.exec() == PlanDialog.DialogCode.Accepted:
            # 这里应该处理计划设置逻辑
            QMessageBox.information(self, "设置成功", "止盈止损计划已保存")
            self.refresh_data()
    
    def on_profit_analysis(self):
        """盈利分析"""
        dialog = ProfitAnalysisDialog(self)
        dialog.exec()
    
    def on_position_double_clicked(self, row, column):
        """持仓双击事件"""
        self.show_plan_detail(row)
    
    def show_plan_detail(self, row):
        """显示计划详情"""
        dialog = PlanDetailDialog(self)
        dialog.exec()
    
    def show_positions_context_menu(self, position):
        """显示持仓右键菜单"""
        menu = QMenu()
        
        new_buy_action = menu.addAction("新增买入")
        new_buy_action.triggered.connect(self.on_new_buy)
        
        new_sell_action = menu.addAction("新增卖出")
        new_sell_action.triggered.connect(self.on_new_sell)
        
        menu.addSeparator()
        
        set_plan_action = menu.addAction("设置计划")
        set_plan_action.triggered.connect(self.on_set_plan)
        
        view_plan_action = menu.addAction("查看计划详情")
        view_plan_action.triggered.connect(lambda: self.show_plan_detail(self.positions_table.currentRow()))
        
        delete_action = menu.addAction("删除持仓")
        delete_action.triggered.connect(self.delete_position)
        
        menu.addSeparator()
        
        refresh_action = menu.addAction("刷新")
        refresh_action.triggered.connect(self.refresh_data)
        
        menu.exec(self.positions_table.viewport().mapToGlobal(position))
    
    def show_history_context_menu(self, position):
        """显示交易历史右键菜单"""
        menu = QMenu()
        
        delete_action = menu.addAction("删除记录")
        delete_action.triggered.connect(self.delete_history_record)
        
        view_detail_action = menu.addAction("查看详情")
        view_detail_action.triggered.connect(self.view_history_detail)
        
        copy_action = menu.addAction("复制交易信息")
        copy_action.triggered.connect(self.copy_history_info)
        
        menu.exec(self.history_table.viewport().mapToGlobal(position))
    
    def delete_position(self):
        """删除持仓"""
        current_row = self.positions_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, "确认删除", "确定要删除选中的持仓吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.positions_table.removeRow(current_row)
                self.update_status_bar()
    
    def delete_history_record(self):
        """删除交易记录"""
        current_row = self.history_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, "确认删除", "确定要删除选中的交易记录吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.history_table.removeRow(current_row)
    
    def view_history_detail(self):
        """查看交易详情"""
        QMessageBox.information(self, "交易详情", "这里是交易详情信息")
    
    def copy_history_info(self):
        """复制交易信息"""
        QMessageBox.information(self, "复制成功", "交易信息已复制到剪贴板")
    
    def refresh_data(self):
        """刷新数据"""
        self.status_bar.showMessage("正在刷新数据...")
        # 模拟刷新过程
        QTimer.singleShot(1000, lambda: self.status_bar.showMessage("数据刷新完成"))
        self.update_status_bar()
    
    def show_about(self):
        """显示关于信息"""
        QMessageBox.about(self, "关于", "股票交易记录系统 v1.0\n\n为个人投资者提供直观、易用的股票交易记录管理工具")


class BuyDialog(QDialog):
    """买入对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增买入交易")
        self.setGeometry(200, 200, 400, 300)
        
        # 创建布局
        layout = QFormLayout(self)
        
        # 创建输入控件
        self.stock_code_input = QLineEdit()
        self.stock_name_input = QLineEdit("浦发银行")
        self.buy_price_input = QLineEdit("10.00")
        self.buy_quantity_input = QLineEdit("1000")
        self.trade_date_input = QDateEdit()
        self.trade_date_input.setDate(QDate.currentDate())
        self.trade_date_input.setDisplayFormat("yyyy-MM-dd")
        self.fee_input = QLineEdit("5.00")
        self.total_amount_label = QLabel("10005.00")
        
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


class SellDialog(QDialog):
    """卖出对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增卖出交易")
        self.setGeometry(200, 200, 400, 350)
        
        # 创建布局
        layout = QFormLayout(self)
        
        # 创建输入控件
        self.position_combo = QComboBox()
        self.position_combo.addItems(["浦发银行 (1000股 @ 10.00)", "平安银行 (500股 @ 12.00)"])
        self.sell_price_input = QLineEdit("10.50")
        self.sell_quantity_input = QLineEdit("1000")
        self.all_button = QPushButton("全部")
        self.trade_date_input = QDateEdit()
        self.trade_date_input.setDate(QDate.currentDate())
        self.trade_date_input.setDisplayFormat("yyyy-MM-dd")
        self.fee_input = QLineEdit("5.00")
        self.total_amount_label = QLabel("10495.00")
        self.expected_profit_label = QLabel("+490.00")
        
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
    
    def accept(self):
        """确认卖出"""
        # 这里应该添加数据验证逻辑
        super().accept()


class PlanDialog(QDialog):
    """设置计划对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置止盈止损计划")
        self.setGeometry(200, 200, 500, 500)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 持仓信息
        info_label = QLabel("持仓股票: 浦发银行 (1000股 @ 10.00元)")
        info_label.setStyleSheet("font-weight: bold; margin: 10px;")
        layout.addWidget(info_label)
        
        # 成本价信息
        cost_label = QLabel("当前成本价: 10.00")
        cost_label.setStyleSheet("margin: 0 10px 10px 10px;")
        layout.addWidget(cost_label)
        
        # 止盈计划组
        take_profit_group = QGroupBox("止盈计划")
        take_profit_layout = QFormLayout(take_profit_group)
        
        self.take_profit_type_combo = QComboBox()
        self.take_profit_type_combo.addItems(["价格", "百分比"])
        self.take_profit_price_input = QLineEdit("12.00")
        self.take_profit_ratio_input = QLineEdit("20%")
        
        take_profit_layout.addRow("触发方式:", self.take_profit_type_combo)
        take_profit_layout.addRow("目标价格:", self.take_profit_price_input)
        take_profit_layout.addRow("或 目标涨幅:", self.take_profit_ratio_input)
        
        layout.addWidget(take_profit_group)
        
        # 止损计划组
        stop_loss_group = QGroupBox("止损计划")
        stop_loss_layout = QFormLayout(stop_loss_group)
        
        self.stop_loss_type_combo = QComboBox()
        self.stop_loss_type_combo.addItems(["价格", "百分比"])
        self.stop_loss_price_input = QLineEdit("9.00")
        self.stop_loss_ratio_input = QLineEdit("10%")
        
        stop_loss_layout.addRow("触发方式:", self.stop_loss_type_combo)
        stop_loss_layout.addRow("目标价格:", self.stop_loss_price_input)
        stop_loss_layout.addRow("或 目标跌幅:", self.stop_loss_ratio_input)
        
        layout.addWidget(stop_loss_group)
        
        # 计划分析组
        analysis_group = QGroupBox("计划分析")
        analysis_layout = QVBoxLayout(analysis_group)
        
        analysis_label = QLabel("若达到止盈价: 预计盈利 +2000元\n若达到止损价: 预计亏损 -1000元")
        analysis_layout.addWidget(analysis_label)
        
        layout.addWidget(analysis_group)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("保存计划")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def accept(self):
        """保存计划"""
        super().accept()


class PlanDetailDialog(QDialog):
    """计划详情对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("止盈止损计划详情")
        self.setGeometry(200, 200, 400, 400)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("止盈止损计划详情")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 股票信息
        stock_label = QLabel("股票: 浦发银行 (600000)")
        stock_label.setStyleSheet("margin: 0 10px;")
        layout.addWidget(stock_label)
        
        position_label = QLabel("持仓: 1000股 @ 10.00元")
        position_label.setStyleSheet("margin: 0 10px 10px 10px;")
        layout.addWidget(position_label)
        
        # 止盈计划组
        take_profit_group = QGroupBox("止盈计划")
        take_profit_layout = QFormLayout(take_profit_group)
        
        take_profit_layout.addRow("触发方式:", QLabel("价格"))
        take_profit_layout.addRow("目标价格:", QLabel("12.00元"))
        take_profit_layout.addRow("当前价差:", QLabel("+0.50元"))
        take_profit_layout.addRow("距离目标:", QLabel("+1.50元"))
        take_profit_layout.addRow("预计盈利:", QLabel("+2000元"))
        
        layout.addWidget(take_profit_group)
        
        # 止损计划组
        stop_loss_group = QGroupBox("止损计划")
        stop_loss_layout = QFormLayout(stop_loss_group)
        
        stop_loss_layout.addRow("触发方式:", QLabel("价格"))
        stop_loss_layout.addRow("目标价格:", QLabel("9.00元"))
        stop_loss_layout.addRow("当前价差:", QLabel("+0.50元"))
        stop_loss_layout.addRow("距离目标:", QLabel("-1.50元"))
        stop_loss_layout.addRow("预计亏损:", QLabel("-1000元"))
        
        layout.addWidget(stop_loss_group)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.modify_button = QPushButton("修改计划")
        self.delete_button = QPushButton("删除计划")
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.modify_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)


class ProfitAnalysisDialog(QDialog):
    """盈利分析对话框"""
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
        overall_group = QGroupBox("📊 总体统计")
        overall_layout = QVBoxLayout(overall_group)
        
        overall_layout.addWidget(QLabel("总投入资金: ¥16,000.00"))
        overall_layout.addWidget(QLabel("当前总市值: ¥16,400.00"))
        overall_layout.addWidget(QLabel("总盈利: ¥400.00 (+2.50%)"))
        
        layout.addWidget(overall_group)
        
        # 持仓分析
        position_group = QGroupBox("📈 持仓分析")
        position_layout = QVBoxLayout(position_group)
        
        position_table = QTableWidget()
        position_table.setColumnCount(5)
        position_table.setHorizontalHeaderLabels(["股票", "持仓", "成本", "市值", "盈亏"])
        position_table.setRowCount(2)
        
        # 添加数据
        position_table.setItem(0, 0, QTableWidgetItem("浦发银行"))
        position_table.setItem(0, 1, QTableWidgetItem("1000"))
        position_table.setItem(0, 2, QTableWidgetItem("10000"))
        position_table.setItem(0, 3, QTableWidgetItem("10500"))
        position_table.setItem(0, 4, QTableWidgetItem("+500"))
        
        position_table.setItem(1, 0, QTableWidgetItem("平安银行"))
        position_table.setItem(1, 1, QTableWidgetItem("500"))
        position_table.setItem(1, 2, QTableWidgetItem("6000"))
        position_table.setItem(1, 3, QTableWidgetItem("5900"))
        position_table.setItem(1, 4, QTableWidgetItem("-100"))
        
        # 设置表格属性
        position_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        position_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = position_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        position_layout.addWidget(position_table)
        layout.addWidget(position_group)
        
        # 计划分析
        plan_group = QGroupBox("📋 计划分析")
        plan_layout = QVBoxLayout(plan_group)
        
        plan_table = QTableWidget()
        plan_table.setColumnCount(5)
        plan_table.setHorizontalHeaderLabels(["股票", "止盈价", "止损价", "预期盈亏", "状态"])
        plan_table.setRowCount(2)
        
        # 添加数据
        plan_table.setItem(0, 0, QTableWidgetItem("浦发银行"))
        plan_table.setItem(0, 1, QTableWidgetItem("12.00"))
        plan_table.setItem(0, 2, QTableWidgetItem("9.00"))
        plan_table.setItem(0, 3, QTableWidgetItem("+2000/-1000"))
        plan_table.setItem(0, 4, QTableWidgetItem("⚠️"))
        
        plan_table.setItem(1, 0, QTableWidgetItem("平安银行"))
        plan_table.setItem(1, 1, QTableWidgetItem("13.00"))
        plan_table.setItem(1, 2, QTableWidgetItem("11.00"))
        plan_table.setItem(1, 3, QTableWidgetItem("+500/-500"))
        plan_table.setItem(1, 4, QTableWidgetItem("⚠️"))
        
        # 设置表格属性
        plan_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        plan_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = plan_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        plan_layout.addWidget(plan_table)
        layout.addWidget(plan_group)
        
        # 风险评估
        risk_group = QGroupBox("📊 风险评估")
        risk_layout = QVBoxLayout(risk_group)
        
        risk_layout.addWidget(QLabel("胜率预测: 66.7% (基于计划)"))
        risk_layout.addWidget(QLabel("最大潜在盈利: ¥2500"))
        risk_layout.addWidget(QLabel("最大潜在亏损: ¥1500"))
        risk_layout.addWidget(QLabel("风险收益比: 1:1.67"))
        
        layout.addWidget(risk_group)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        self.export_button = QPushButton("导出报告")
        self.print_button = QPushButton("打印")
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.print_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("股票交易记录系统")
    app.setApplicationVersion("1.0.0")
    
    # 创建并显示主窗口
    window = StockTradingUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()