from PyQt6.QtWidgets import QStatusBar
from PyQt6.QtCore import QDate


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.show_message("就绪")
    
    def show_message(self, message):
        """显示消息"""
        super().showMessage(message)
    
    def update_status(self, position_count: int, total_profit: float, plan_count: int):
        """更新状态（动态统计）"""
        current_time = QDate.currentDate().toString("yyyy-MM-dd")
        status_text = (
            f"就绪 | 当前时间: {current_time} | 持仓: {position_count}只 | 总盈利: {total_profit:.2f}元 | 计划: {plan_count}个"
        )
        self.show_message(status_text)