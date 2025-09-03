import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from views.components.menu_bar import MenuBar
from views.components.toolbar import Toolbar
from views.components.main_content import MainContent
from views.components.status_bar import StatusBar
from utils.data_manager import DataManager
from utils.Ashare import get_price
import datetime


class PriceLoaderThread(QThread):
    loaded = pyqtSignal(dict)   # code -> live_price
    failed = pyqtSignal(str)

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager

    def run(self):
        try:
            positions = self.data_manager.get_positions()
            result = {}
            for p in positions:
                code = str(p.get('code', ''))
                fallback = float(p.get('current_price', 0) or 0)
                if not code:
                    continue
                try:
                    df = get_price(code, frequency='1m', count=2)
                    live = float(df['close'].iloc[-1])
                    result[code] = live
                except Exception:
                    # 留空，稍后由主线程用缓存兜底
                    pass
            self.loaded.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class StockTradingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票交易记录系统 v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 数据管理器
        self.data_manager = DataManager()
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        
        # 创建界面组件
        self.create_components()
        
        # 初始化数据（异步加载）
        self.init_data()
    
    def create_components(self):
        """创建界面组件"""
        # 创建菜单栏
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # 创建工具栏
        self.toolbar = Toolbar(self)
        self.main_layout.addLayout(self.toolbar)
        
        # 创建主内容区域
        self.main_content = MainContent(self)
        self.main_layout.addWidget(self.main_content)
        
        # 创建状态栏
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
    
    def _in_trading_time(self) -> bool:
        """交易时段 09:15~15:00 内返回 True"""
        now = datetime.datetime.now().time()
        start = datetime.time(9, 15)
        end = datetime.time(15, 0)
        return start <= now <= end
    
    def init_data(self):
        """初始化数据：先显示loading，然后异步拉取实时价格，失败则使用缓存"""
        self.status_bar.show_message("正在加载数据...")
        # 先用现有JSON同步渲染一版（用fallback和缓存）
        self.refresh_data(use_cache_only=True)
        # 异步拉实时价
        self.loader = PriceLoaderThread(self.data_manager)
        self.loader.loaded.connect(self.on_prices_loaded)
        self.loader.failed.connect(self.on_prices_failed)
        self.loader.start()
        # 定时刷新：仅交易时段内，每59秒触发
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(59 * 1000)
        self.refresh_timer.timeout.connect(self.on_refresh_timer)
        self.refresh_timer.start()
    
    def on_refresh_timer(self):
        if not self._in_trading_time():
            return
        # 避免与正在运行的加载线程重叠
        if hasattr(self, 'loader') and self.loader.isRunning():
            return
        self.status_bar.show_message("自动刷新实时价格...")
        self.loader = PriceLoaderThread(self.data_manager)
        self.loader.loaded.connect(self.on_prices_loaded)
        self.loader.failed.connect(self.on_prices_failed)
        self.loader.start()
    
    def on_prices_loaded(self, price_map: dict):
        # 合并并缓存成功的价格
        if price_map:
            self.data_manager.update_last_prices(price_map)
        self.status_bar.show_message("实时价格已更新，正在刷新界面...")
        self.refresh_data()
    
    def on_prices_failed(self, err: str):
        self.status_bar.show_message("实时价格获取失败，使用缓存数据")
        self.refresh_data(use_cache_only=True)
    
    def refresh_data(self, use_cache_only: bool = False):
        """刷新数据。use_cache_only=True 时仅使用缓存/JSON价，不请求网络。"""
        # 将缓存传递给主内容用于兜底
        self.main_content.load_data_from_json_with_cache(use_cache_only)

        # 汇总状态数据（保持不变）
        positions = self.data_manager.get_positions()
        position_count = len(positions)
        
        history = self.data_manager.get_history()
        buy_fee_map = self.main_content._build_buy_commission_map(history)
        
        total_profit = 0.0
        for p in positions:
            try:
                name = str(p.get('name', ''))
                code = str(p.get('code', ''))
                quantity = float(p.get('quantity', 0) or 0)
                cost_price = float(p.get('cost_price', 0) or 0)
                # 使用缓存/JSON价作为刷新后的计算价
                last_prices = self.data_manager.get_last_prices()
                current_price = float(last_prices.get(code, p.get('current_price', 0) or 0))
                market_value = current_price * quantity
                commission_total = buy_fee_map.get(code or name, 0.0)
                cost_total = cost_price * quantity + commission_total
                profit = market_value - cost_total
                total_profit += profit
            except Exception:
                continue
        plan_count = 0
        self.status_bar.update_status(position_count, total_profit, plan_count)



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