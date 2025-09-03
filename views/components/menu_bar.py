from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction
from views.dialogs.buy_dialog import BuyDialog
from views.dialogs.sell_dialog import SellDialog
from views.dialogs.plan_dialog import PlanDialog
from views.dialogs.profit_analysis_dialog import ProfitAnalysisDialog


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.create_menus()
    
    def create_menus(self):
        """创建菜单"""
        # 文件菜单
        file_menu = self.addMenu('文件(&F)')
        
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
        exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.addMenu('编辑(&E)')
        
        plan_action = QAction('设置计划', self)
        plan_action.setShortcut('Ctrl+P')
        plan_action.triggered.connect(self.on_set_plan)
        edit_menu.addAction(plan_action)
        
        # 查看菜单
        view_menu = self.addMenu('查看(&V)')
        
        analysis_action = QAction('盈利分析', self)
        analysis_action.setShortcut('Ctrl+A')
        analysis_action.triggered.connect(self.on_profit_analysis)
        view_menu.addAction(analysis_action)
        
        refresh_action = QAction('刷新', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.parent.refresh_data)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = self.addMenu('帮助(&H)')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def on_new_buy(self):
        """新增买入"""
        dialog = BuyDialog(self.parent)
        if dialog.exec() == BuyDialog.DialogCode.Accepted:
            # 这里应该处理买入逻辑
            self.parent.statusBar().show_message("买入交易已记录")
            self.parent.refresh_data()
    
    def on_new_sell(self):
        """新增卖出"""
        dialog = SellDialog(self.parent)
        if dialog.exec() == SellDialog.DialogCode.Accepted:
            # 这里应该处理卖出逻辑
            self.parent.statusBar().show_message("卖出交易已记录")
            self.parent.refresh_data()
    
    def on_set_plan(self):
        """设置计划"""
        dialog = PlanDialog(self.parent)
        if dialog.exec() == PlanDialog.DialogCode.Accepted:
            # 这里应该处理计划设置逻辑
            self.parent.statusBar().show_message("止盈止损计划已保存")
            self.parent.refresh_data()
    
    def on_profit_analysis(self):
        """盈利分析"""
        dialog = ProfitAnalysisDialog(self.parent)
        dialog.exec()
    
    def show_about(self):
        """显示关于信息"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self.parent, "关于", "股票交易记录系统 v1.0\n\n为个人投资者提供直观、易用的股票交易记录管理工具")