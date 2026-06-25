from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
from PyQt5.QtCore import QSize


def create_tray_icon():
    icon = QIcon()
    pixmap = QIcon().pixmap(QSize(32, 32))
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(255, 159, 67))
    painter.setPen(QColor(230, 130, 40))
    painter.drawEllipse(8, 4, 16, 16)
    painter.setBrush(QColor(255, 243, 224))
    painter.setPen(QColor(0, 0, 0, 0))
    painter.drawEllipse(10, 12, 5, 4)
    painter.drawEllipse(17, 12, 5, 4)
    painter.setBrush(QColor(45, 45, 54))
    painter.drawEllipse(11, 12, 2, 2)
    painter.drawEllipse(18, 12, 2, 2)
    painter.end()
    icon.addPixmap(pixmap)
    return icon


class TrayManager:
    def __init__(self, parent):
        self.parent = parent
        self.tray = QSystemTrayIcon(create_tray_icon(), parent)
        self.tray.setToolTip("AI 桌面宠物")

        self.menu = QMenu()

        self._add_action("打招呼", lambda: parent.on_menu_action("greet"))
        self._add_action("摸摸头", lambda: parent.on_menu_action("pet"))
        self._add_action("称赞", lambda: parent.on_menu_action("praise"))
        self._add_action("喂食", lambda: parent.on_menu_action("feed"))
        self._add_action("送礼物", lambda: parent.on_menu_action("gift"))
        self._add_action("洗澡", lambda: parent.on_menu_action("bathe"))
        self._add_action("治疗", lambda: parent.on_menu_action("heal"))
        self._add_action("玩耍", lambda: parent.on_menu_action("play"))
        self._add_action("跳舞", lambda: parent.on_menu_action("dance"))
        self._add_action("讲故事", lambda: parent.on_menu_action("story"))
        self._add_action("教本领", lambda: parent.on_menu_action("teach"))
        self.menu.addSeparator()
        self._add_action("生气", lambda: parent.on_menu_action("scold"))
        self.menu.addSeparator()
        self._add_action("改名字", lambda: parent.on_menu_action("rename"))
        self._add_action("查看状态", lambda: parent.on_menu_action("status"))
        self.menu.addSeparator()
        self._add_action("退出", parent.quit_application)

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self._on_activated)

    def _add_action(self, label: str, callback):
        action = QAction(label, self.parent)
        action.triggered.connect(callback)
        self.menu.addAction(action)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.parent.on_menu_action("interact")
        elif reason == QSystemTrayIcon.Trigger:
            self.parent.raise_window()

    def show(self):
        self.tray.show()

    def show_notification(self, title: str, message: str):
        self.tray.showMessage(title, message, QIcon(), 3000)
