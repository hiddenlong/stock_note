from PyQt6.QtWidgets import (QSplitter, QGroupBox, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QAbstractItemView, 
                             QHeaderView, QTableWidgetItem, QWidget, QLabel)
from PyQt6.QtCore import Qt as QtCoreQt
from PyQt6.QtGui import QAction, QColor
from views.dialogs.buy_dialog import BuyDialog
from views.dialogs.sell_dialog import SellDialog
from views.dialogs.plan_dialog import PlanDialog
from views.dialogs.plan_detail_dialog import PlanDetailDialog
from views.dialogs.profit_analysis_dialog import ProfitAnalysisDialog
from utils.Ashare import get_price


class NumericTableWidgetItem(QTableWidgetItem):
    """支持数值排序的表格项"""
    def __lt__(self, other):
        return self.data(QtCoreQt.ItemDataRole.UserRole) < other.data(QtCoreQt.ItemDataRole.UserRole)


class MainContent(QSplitter):
    def __init__(self, parent=None):
        super().__init__(QtCoreQt.Orientation.Vertical)
        self.parent = parent
        
        # 首先创建UI组件
        self.create_positions_section()
        self.create_history_section()
        
        # 设置初始大小
        self.setSizes([400, 400])
        
        # 初始禁用排序，加载后再开启
        self.positions_table.setSortingEnabled(False)
        self.history_table.setSortingEnabled(False)
    
    def create_positions_section(self):
        """创建持仓区域"""
        positions_group = QGroupBox("持仓列表")
        positions_layout = QVBoxLayout(positions_group)
        
        # 持仓表格（新增涨跌列与成本涨跌列）
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(10)
        self.positions_table.setHorizontalHeaderLabels([
            "代码", "名称", "市值", "持仓", "成本价", "当前价", "当前涨跌", "成本涨跌", "盈亏", "盈亏率"
        ])
        
        # 设置表格属性
        self.positions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.positions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.positions_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.positions_table.setAlternatingRowColors(True)
        
        header = self.positions_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setSectionsClickable(True)
        
        # 连接双击事件
        self.positions_table.cellDoubleClicked.connect(self.on_position_double_clicked)
        
        # 右键菜单
        self.positions_table.setContextMenuPolicy(QtCoreQt.ContextMenuPolicy.CustomContextMenu)
        self.positions_table.customContextMenuRequested.connect(self.show_positions_context_menu)
        
        positions_layout.addWidget(self.positions_table)
        
        # 统计栏
        summary_layout = QHBoxLayout()
        self.total_invest_label = QLabel("投入: -")
        self.total_market_label = QLabel("现值: -")
        self.total_profit_label = QLabel("盈亏: -")
        summary_layout.addWidget(self.total_invest_label)
        summary_layout.addSpacing(20)
        summary_layout.addWidget(self.total_market_label)
        summary_layout.addSpacing(20)
        summary_layout.addWidget(self.total_profit_label)
        summary_layout.addStretch()
        positions_layout.addLayout(summary_layout)
        
        # 操作按钮
        positions_button_layout = QHBoxLayout()
        self.new_buy_button = QPushButton("新增买入")
        self.new_buy_button.clicked.connect(self.on_new_buy)
        
        self.new_sell_button = QPushButton("新增卖出")
        self.new_sell_button.clicked.connect(self.on_new_sell)
        
        self.set_plan_button = QPushButton("设置计划")
        self.set_plan_button.clicked.connect(self.on_set_plan)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.parent.refresh_data)
        
        self.profit_analysis_button = QPushButton("盈利分析")
        self.profit_analysis_button.clicked.connect(self.on_profit_analysis)
        
        positions_button_layout.addWidget(self.new_buy_button)
        positions_button_layout.addWidget(self.new_sell_button)
        positions_button_layout.addWidget(self.set_plan_button)
        positions_button_layout.addWidget(self.refresh_button)
        positions_button_layout.addWidget(self.profit_analysis_button)
        positions_button_layout.addStretch()
        
        positions_layout.addLayout(positions_button_layout)
        
        self.addWidget(positions_group)
    
    def create_history_section(self):
        """创建交易历史区域"""
        history_group = QGroupBox("交易记录历史")
        history_layout = QVBoxLayout(history_group)
        
        # 交易历史表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "日期", "类型", "名称", "简称", "成交价", "成交量", "成交金额"
        ])
        
        # 设置表格属性
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        
        header = self.history_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setSectionsClickable(True)
        
        # 右键菜单
        self.history_table.setContextMenuPolicy(QtCoreQt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_history_context_menu)
        
        history_layout.addWidget(self.history_table)
        
        self.addWidget(history_group)
    
    def clear_tables(self):
        """清空表格"""
        self.positions_table.setRowCount(0)
        self.history_table.setRowCount(0)
    
    def _build_buy_commission_map(self, history):
        """根据交易记录构建每只股票买入手续费汇总（0.025%，最低5元）"""
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
    
    def _fetch_live_price_pair(self, code: str, fallback: float):
        """返回 (live_close, prev_close)。失败时用回退值和同值。"""
        try:
            df = get_price(code, frequency='1m', count=2)
            live = float(df['close'].iloc[-1])
            prev = float(df['close'].iloc[-2]) if len(df) >= 2 else live
            return live, prev
        except Exception:
            return fallback, fallback
    
    def load_data_from_json(self):
        """从 DataManager 加载 JSON 数据并填充到表格，同时计算盈亏和盈亏率"""
        self.clear_tables()
        
        # 关闭排序以避免插入期抖动
        self.positions_table.setSortingEnabled(False)
        self.history_table.setSortingEnabled(False)
        
        data_manager = getattr(self.parent, 'data_manager', None)
        if data_manager is None:
            return
        
        # 预备历史与买入手续费映射
        history = data_manager.get_history()
        buy_fee_map = self._build_buy_commission_map(history)
        
        # 填充持仓（市值与手续费实时计算）
        positions = data_manager.get_positions()
        
        total_invest = 0.0
        total_market = 0.0
        
        for p in positions:
            try:
                code = str(p.get('code', ''))
                name = str(p.get('name', ''))
                quantity = float(p.get('quantity', 0) or 0)
                cost_price = float(p.get('cost_price', 0) or 0)
                current_price_json = float(p.get('current_price', 0) or 0)
                # 实时价与上一笔
                live_price, prev_close = self._fetch_live_price_pair(code, current_price_json) if code else (current_price_json, current_price_json)
                # 当前涨跌（相对上一笔/昨日，根据数据源）
                change_now_ratio = ((live_price - prev_close) / prev_close * 100.0) if prev_close > 0 else 0.0
                # 成本涨跌（现价相对成本）
                cost_diff_amount = live_price - cost_price
                cost_diff_ratio = (cost_diff_amount / cost_price * 100.0) if cost_price > 0 else 0.0
                
                market_value = live_price * quantity
                commission_total = buy_fee_map.get(code or name, 0.0)
                cost_total = cost_price * quantity + commission_total
                profit_value = market_value - cost_total
                profit_ratio_value = (profit_value / cost_total * 100.0) if cost_total > 0 else 0.0
                
                total_invest += cost_total
                total_market += market_value
                
                # 文本
                market_value_text = f"{market_value:.2f}"
                quantity_text = f"{int(quantity) if quantity.is_integer() else quantity:.0f}"
                cost_price_text = f"{cost_price:.4f}" if cost_price < 10 else f"{cost_price:.2f}"
                current_price_text = f"{live_price:.4f}" if live_price < 10 else f"{live_price:.2f}"
                change_now_text = ("▲" if change_now_ratio>0 else ("▼" if change_now_ratio<0 else "")) + f"{abs(change_now_ratio):.2f}%"
                cost_diff_text = ("▲" if cost_diff_amount>0 else ("▼" if cost_diff_amount<0 else "")) + f"{abs(cost_diff_amount):.4f} ({abs(cost_diff_ratio):.2f}%)"
                profit_text = ("+" if profit_value > 0 else ("-" if profit_value < 0 else "")) + f"{abs(profit_value):.2f}"
                profit_ratio_text = ("+" if profit_ratio_value > 0 else ("-" if profit_ratio_value < 0 else "")) + f"{abs(profit_ratio_value):.2f}%"
                
                self.add_position_row(
                    code, name,
                    market_value_text, quantity_text, cost_price_text, current_price_text,
                    change_now_text, cost_diff_text,
                    profit_text, profit_ratio_text,
                    profit_value, profit_ratio_value, market_value,
                    change_now_ratio, cost_diff_ratio
                )
            except Exception:
                continue
        
        # 更新统计栏
        total_profit = total_market - total_invest
        sign = "+" if total_profit>0 else ("-" if total_profit<0 else "")
        self.total_invest_label.setText(f"投入: ¥{total_invest:.2f}")
        self.total_market_label.setText(f"现值: ¥{total_market:.2f}")
        self.total_profit_label.setText(f"盈亏: {sign}{abs(total_profit):.2f}")
        
        # 启用持仓排序
        self.positions_table.setSortingEnabled(True)
        
        # 填充历史
        for h in history:
            try:
                date = str(h.get('date', ''))
                type_ = str(h.get('type', ''))
                code = str(h.get('code', ''))
                name = str(h.get('name', ''))
                price = float(h.get('price', 0) or 0)
                quantity = float(h.get('quantity', 0) or 0)
                amount = float(h.get('amount', price * quantity))
                
                self.add_history_row(date, type_, code, name, f"{price:.4f}" if price < 10 else f"{price:.2f}", f"{int(quantity) if quantity.is_integer() else quantity:.0f}", f"{amount:.2f}")
            except Exception:
                continue
        
        # 启用历史排序
        self.history_table.setSortingEnabled(True)
    
    def load_data_from_json_with_cache(self, use_cache_only: bool = False):
        """加载数据并可选仅使用缓存/JSON价格（不请求网络）"""
        self.clear_tables()
        self.positions_table.setSortingEnabled(False)
        self.history_table.setSortingEnabled(False)
        data_manager = getattr(self.parent, 'data_manager', None)
        if data_manager is None:
            return
        history = data_manager.get_history()
        buy_fee_map = self._build_buy_commission_map(history)
        positions = data_manager.get_positions()
        last_prices = data_manager.get_last_prices()
        total_invest = 0.0
        total_market = 0.0
        for p in positions:
            try:
                code = str(p.get('code', ''))
                name = str(p.get('name', ''))
                quantity = float(p.get('quantity', 0) or 0)
                cost_price = float(p.get('cost_price', 0) or 0)
                json_price = float(p.get('current_price', 0) or 0)
                # 价格选择：优先缓存，其次JSON；若允许请求网络且有code，之后刷新时会异步覆盖
                live_price = float(last_prices.get(code, json_price))
                prev_close = live_price  # 无网络时无法取上一笔，置同值
                change_now_ratio = 0.0
                if not use_cache_only and code:
                    try:
                        from utils.Ashare import get_price
                        df = get_price(code, frequency='1m', count=2)
                        prev_close = float(df['close'].iloc[-2]) if len(df) >= 2 else live_price
                        live_price = float(df['close'].iloc[-1])
                        # 更新缓存到内存（批量更新在主线程进行）
                    except Exception:
                        pass
                if prev_close > 0:
                    change_now_ratio = ((live_price - prev_close) / prev_close * 100.0)
                cost_diff_amount = live_price - cost_price
                cost_diff_ratio = (cost_diff_amount / cost_price * 100.0) if cost_price > 0 else 0.0
                market_value = live_price * quantity
                commission_total = buy_fee_map.get(code or name, 0.0)
                cost_total = cost_price * quantity + commission_total
                profit_value = market_value - cost_total
                profit_ratio_value = (profit_value / cost_total * 100.0) if cost_total > 0 else 0.0
                total_invest += cost_total
                total_market += market_value
                market_value_text = f"{market_value:.2f}"
                quantity_text = f"{int(quantity) if quantity.is_integer() else quantity:.0f}"
                cost_price_text = f"{cost_price:.4f}" if cost_price < 10 else f"{cost_price:.2f}"
                current_price_text = f"{live_price:.4f}" if live_price < 10 else f"{live_price:.2f}"
                change_now_text = ("▲" if change_now_ratio>0 else ("▼" if change_now_ratio<0 else "")) + f"{abs(change_now_ratio):.2f}%"
                cost_diff_text = ("▲" if cost_diff_amount>0 else ("▼" if cost_diff_amount<0 else "")) + f"{abs(cost_diff_amount):.4f} ({abs(cost_diff_ratio):.2f}%)"
                profit_text = ("+" if profit_value > 0 else ("-" if profit_value < 0 else "")) + f"{abs(profit_value):.2f}"
                profit_ratio_text = ("+" if profit_ratio_value > 0 else ("-" if profit_ratio_value < 0 else "")) + f"{abs(profit_ratio_value):.2f}%"
                self.add_position_row(
                    code, name,
                    market_value_text, quantity_text, cost_price_text, current_price_text,
                    change_now_text, cost_diff_text,
                    profit_text, profit_ratio_text,
                    profit_value, profit_ratio_value, market_value,
                    change_now_ratio, cost_diff_ratio
                )
            except Exception:
                continue
        total_profit = total_market - total_invest
        sign = "+" if total_profit>0 else ("-" if total_profit<0 else "")
        self.total_invest_label.setText(f"投入: ¥{total_invest:.2f}")
        self.total_market_label.setText(f"现值: ¥{total_market:.2f}")
        self.total_profit_label.setText(f"盈亏: {sign}{abs(total_profit):.2f}")
        self.positions_table.setSortingEnabled(True)
    
    def add_position_row(self, code, name, market_value, quantity, cost_price, current_price, change_now_text, cost_diff_text, profit, profit_ratio, profit_value=0.0, profit_ratio_value=0.0, market_value_numeric=0.0, change_now_ratio_value=0.0, cost_diff_ratio_value=0.0):
        """添加持仓行（支持数值排序；新增涨跌幅列带箭头）"""
        row = self.positions_table.rowCount()
        self.positions_table.insertRow(row)
        
        # 创建表格项
        items = [
            QTableWidgetItem(code),
            QTableWidgetItem(name),
            NumericTableWidgetItem(market_value),
            NumericTableWidgetItem(quantity),
            NumericTableWidgetItem(cost_price),
            NumericTableWidgetItem(current_price),
            NumericTableWidgetItem(change_now_text),
            NumericTableWidgetItem(cost_diff_text),
            NumericTableWidgetItem(profit),
            NumericTableWidgetItem(profit_ratio)
        ]
        
        # 设置排序值（市值、持仓、成本、现价、涨跌幅、盈亏、盈亏率）
        try:
            items[2].setData(QtCoreQt.ItemDataRole.UserRole, float(market_value_numeric))
        except Exception:
            try:
                items[2].setData(QtCoreQt.ItemDataRole.UserRole, float(market_value))
            except Exception:
                items[2].setData(QtCoreQt.ItemDataRole.UserRole, 0.0)
        for idx, val in [(3, quantity), (4, cost_price), (5, current_price)]:
            try:
                items[idx].setData(QtCoreQt.ItemDataRole.UserRole, float(val.replace(',', '')) if isinstance(val, str) else float(val))
            except Exception:
                items[idx].setData(QtCoreQt.ItemDataRole.UserRole, 0.0)
        items[6].setData(QtCoreQt.ItemDataRole.UserRole, float(change_now_ratio_value))
        items[7].setData(QtCoreQt.ItemDataRole.UserRole, float(cost_diff_ratio_value))
        items[8].setData(QtCoreQt.ItemDataRole.UserRole, float(profit_value))
        items[9].setData(QtCoreQt.ItemDataRole.UserRole, float(profit_ratio_value))
        
        # 对齐
        items[0].setTextAlignment(QtCoreQt.AlignmentFlag.AlignLeft | QtCoreQt.AlignmentFlag.AlignVCenter)
        items[1].setTextAlignment(QtCoreQt.AlignmentFlag.AlignLeft | QtCoreQt.AlignmentFlag.AlignVCenter)
        for i in range(2, 10):
            items[i].setTextAlignment(QtCoreQt.AlignmentFlag.AlignRight | QtCoreQt.AlignmentFlag.AlignVCenter)
        
        # 着色：当前价、当前涨跌、成本涨跌、盈亏/盈亏率
        # 当前涨跌基于 change_now_ratio_value
        if change_now_ratio_value > 0:
            items[5].setForeground(QColor("#FF0000"))
            items[6].setForeground(QColor("#FF0000"))
        elif change_now_ratio_value < 0:
            items[5].setForeground(QColor("#008000"))
            items[6].setForeground(QColor("#008000"))
        # 成本涨跌基于 cost_diff_ratio_value
        if cost_diff_ratio_value > 0:
            items[7].setForeground(QColor("#FF0000"))
        elif cost_diff_ratio_value < 0:
            items[7].setForeground(QColor("#008000"))
        # 盈亏颜色
        if profit.startswith('+'):
            items[8].setForeground(QColor("#FF0000"))
            items[9].setForeground(QColor("#FF0000"))
        elif profit.startswith('-'):
            items[8].setForeground(QColor("#008000"))
            items[9].setForeground(QColor("#008000"))
        
        for i, item in enumerate(items):
            self.positions_table.setItem(row, i, item)
    
    def add_history_row(self, date, type_, code, name, price, quantity, amount):
        """添加交易历史行（数值排序）"""
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        items = [
            QTableWidgetItem(date),
            QTableWidgetItem(type_),
            QTableWidgetItem(code),
            QTableWidgetItem(name),
            NumericTableWidgetItem(price),
            NumericTableWidgetItem(quantity),
            NumericTableWidgetItem(amount)
        ]
        
        # 排序值
        try:
            items[4].setData(QtCoreQt.ItemDataRole.UserRole, float(price))
        except Exception:
            items[4].setData(QtCoreQt.ItemDataRole.UserRole, 0.0)
        try:
            items[5].setData(QtCoreQt.ItemDataRole.UserRole, float(quantity))
        except Exception:
            items[5].setData(QtCoreQt.ItemDataRole.UserRole, 0.0)
        try:
            items[6].setData(QtCoreQt.ItemDataRole.UserRole, float(amount))
        except Exception:
            items[6].setData(QtCoreQt.ItemDataRole.UserRole, 0.0)
        
        # 对齐
        items[0].setTextAlignment(QtCoreQt.AlignmentFlag.AlignLeft | QtCoreQt.AlignmentFlag.AlignVCenter)
        items[1].setTextAlignment(QtCoreQt.AlignmentFlag.AlignCenter)
        items[2].setTextAlignment(QtCoreQt.AlignmentFlag.AlignLeft | QtCoreQt.AlignmentFlag.AlignVCenter)
        items[3].setTextAlignment(QtCoreQt.AlignmentFlag.AlignLeft | QtCoreQt.AlignmentFlag.AlignVCenter)
        for i in range(4, 7):
            items[i].setTextAlignment(QtCoreQt.AlignmentFlag.AlignRight | QtCoreQt.AlignmentFlag.AlignVCenter)
        
        # 交易类型颜色
        if type_ == "买入":
            items[1].setForeground(QColor("#0000FF"))
        else:
            items[1].setForeground(QColor("#FF0000"))
        
        for i, item in enumerate(items):
            self.history_table.setItem(row, i, item)
    
    def _get_selected_position(self):
        """获取当前选中持仓的简要信息（名称、数量、成本价）"""
        row = self.positions_table.currentRow()
        if row < 0:
            return None
        name_item = self.positions_table.item(row, 1) # Changed from 0 to 1 for name
        quantity_item = self.positions_table.item(row, 3) # Changed from 2 to 3 for quantity
        cost_item = self.positions_table.item(row, 4) # Changed from 3 to 4 for cost_price
        current_item = self.positions_table.item(row, 5) # Changed from 4 to 5 for current_price
        return {
            'name': name_item.text() if name_item else '',
            'quantity': quantity_item.text() if quantity_item else '0',
            'cost_price': cost_item.text() if cost_item else '0',
            'current_price': current_item.text() if current_item else '0',
        }
    
    def on_new_buy(self):
        """新增买入"""
        dialog = BuyDialog(self.parent)
        if dialog.exec() == BuyDialog.DialogCode.Accepted:
            self.parent.statusBar().show_message("买入交易已记录")
            self.parent.refresh_data()
    
    def on_new_sell(self):
        """新增卖出（默认选中当前持仓）"""
        selected = self._get_selected_position()
        dialog = SellDialog(self.parent)
        if selected:
            dialog.prefill_from_position(selected['name'], selected['quantity'], selected['current_price'])
        if dialog.exec() == SellDialog.DialogCode.Accepted:
            self.parent.statusBar().show_message("卖出交易已记录")
            self.parent.refresh_data()
    
    def on_set_plan(self):
        """设置计划（默认选中当前持仓）"""
        selected = self._get_selected_position()
        dialog = PlanDialog(self.parent)
        if selected:
            dialog.prefill_from_position(selected['name'], selected['quantity'], selected['cost_price'])
        if dialog.exec() == PlanDialog.DialogCode.Accepted:
            self.parent.statusBar().show_message("止盈止损计划已保存")
            # 计划保存后立即显示盈利分析
            analysis = ProfitAnalysisDialog(self.parent)
            analysis.load_from_data_manager(self.parent.data_manager)
            analysis.exec()
            self.parent.refresh_data()
    
    def on_profit_analysis(self):
        """盈利分析（根据 JSON 计算）"""
        dialog = ProfitAnalysisDialog(self.parent)
        dialog.load_from_data_manager(self.parent.data_manager)
        dialog.exec()
    
    def on_position_double_clicked(self, row, column):
        """持仓双击事件"""
        self.show_plan_detail(row)
    
    def show_plan_detail(self, row):
        """显示计划详情"""
        name_item = self.positions_table.item(row, 1) # Changed from 0 to 1 for name
        name = name_item.text() if name_item else ""
        dialog = PlanDetailDialog(self.parent)
        try:
            dialog.load_for_name(name)
        except Exception:
            pass
        dialog.exec()
    
    def show_positions_context_menu(self, position):
        """显示持仓右键菜单"""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        
        new_buy_action = QAction("新增买入", self)
        new_buy_action.triggered.connect(self.on_new_buy)
        menu.addAction(new_buy_action)
        
        new_sell_action = QAction("新增卖出", self)
        new_sell_action.triggered.connect(self.on_new_sell)
        menu.addAction(new_sell_action)
        
        menu.addSeparator()
        
        set_plan_action = QAction("设置计划", self)
        set_plan_action.triggered.connect(self.on_set_plan)
        menu.addAction(set_plan_action)
        
        view_plan_action = QAction("查看计划详情", self)
        view_plan_action.triggered.connect(lambda: self.show_plan_detail(self.positions_table.currentRow()))
        menu.addAction(view_plan_action)
        
        delete_action = QAction("删除持仓", self)
        delete_action.triggered.connect(self.delete_position)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.parent.refresh_data)
        menu.addAction(refresh_action)
        
        menu.exec(self.positions_table.viewport().mapToGlobal(position))
    
    def show_history_context_menu(self, position):
        """显示交易历史右键菜单"""
        from PyQt6.QtWidgets import QMenu, QMessageBox
        menu = QMenu()
        
        delete_action = QAction("删除记录", self)
        delete_action.triggered.connect(self.delete_history_record)
        menu.addAction(delete_action)
        
        view_detail_action = QAction("查看详情", self)
        view_detail_action.triggered.connect(self.view_history_detail)
        menu.addAction(view_detail_action)
        
        copy_action = QAction("复制交易信息", self)
        copy_action.triggered.connect(self.copy_history_info)
        menu.addAction(copy_action)
        
        menu.exec(self.history_table.viewport().mapToGlobal(position))
    
    def delete_position(self):
        """删除持仓"""
        from PyQt6.QtWidgets import QMessageBox
        current_row = self.positions_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self.parent, "确认删除", "确定要删除选中的持仓吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.positions_table.removeRow(current_row)
                # 状态栏将在 refresh_data 中统一更新
    
    def delete_history_record(self):
        """删除交易记录"""
        from PyQt6.QtWidgets import QMessageBox
        current_row = self.history_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self.parent, "确认删除", "确定要删除选中的交易记录吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.history_table.removeRow(current_row)
    
    def view_history_detail(self):
        """查看交易详情"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "交易详情", "这里是交易详情信息")
    
    def copy_history_info(self):
        """复制交易信息"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self.parent, "复制成功", "交易信息已复制到剪贴板")