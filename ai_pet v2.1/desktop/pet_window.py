import pygame

from PyQt5.QtWidgets import (QWidget, QApplication, QMenu, QAction,
                              QInputDialog, QMessageBox, QDialog, QVBoxLayout,
                              QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QImage, QColor, QFont

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, ANIMAL_CONFIGS, GIFT_COST
from renderer.renderer import PetRenderer
from pet.brain import Brain


class PetWindow(QWidget):
    def __init__(self, brain: Brain, app: QApplication):
        super().__init__()
        self.brain = brain
        self.app = app
        self.renderer = PetRenderer()
        self.dragging = False
        self.drag_offset = None
        self.last_dialogue = ""
        self.dialogue_timer = 0

        self._setup_pygame()
        self._setup_window()
        self._setup_timer()

    def _setup_window(self):
        self.setWindowTitle("AI 桌面宠物")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setStyleSheet("background: transparent;")

    def _setup_pygame(self):
        pygame.font.init()
        self.pygame_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.pygame_surf.fill((0, 0, 0, 0))

    def _setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(1000 // FPS)

    def _update(self):
        self.brain.tick()
        dialogue = None
        if self.dialogue_timer > 0:
            dialogue = self.last_dialogue
            self.dialogue_timer -= 1

        overlay = None
        if self.brain.visual_overlay and self.brain.overlay_max_duration > 0:
            progress = 1.0 - (self.brain.overlay_duration / self.brain.overlay_max_duration)
            overlay = (self.brain.visual_overlay, progress)

        self.renderer.render(
            self.pygame_surf,
            self.brain.current_emotion,
            dialogue,
            overlay,
            self.brain.animal_type,
        )
        self.update()

    def _get_pet_rect(self) -> QRect:
        r = self.renderer.get_pet_rect()
        return QRect(r.x, r.y, r.width, r.height)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixels = pygame.image.tobytes(self.pygame_surf, "RGBA")
        w, h = self.pygame_surf.get_size()
        image = QImage(pixels, w, h, QImage.Format_RGBA8888)
        painter.drawImage(0, 0, image)
        painter.end()

    def _is_on_pet(self, pos) -> bool:
        return self._get_pet_rect().contains(pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._is_on_pet(event.pos()):
                self.dragging = True
                self.drag_offset = event.pos()
            else:
                self.dragging = False

        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            if self._is_on_pet(event.pos()):
                self._on_click()

    def _on_click(self):
        text = self.brain.random_interact()
        self._show_dialogue(text)

    def _show_context_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D36;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #FF9F43;
            }
            QMenu::separator {
                height: 1px;
                background: #555;
                margin: 4px 8px;
            }
        """)

        actions = [
            ("打招呼", "greet"),
            ("摸摸头", "pet"),
            ("称赞", "praise"),
            ("喂食", "feed"),
            ("送礼物", "gift"),
            ("洗澡", "bathe"),
            ("治疗", "heal"),
            ("玩耍", "play"),
            ("跳舞", "dance"),
            ("讲故事", "story"),
            ("教本领", "teach"),
        ]
        for label, action_type in actions:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, t=action_type: self.on_menu_action(t))
            menu.addAction(action)

        menu.addSeparator()
        scold_action = QAction("生气", self)
        scold_action.triggered.connect(lambda: self.on_menu_action("scold"))
        menu.addAction(scold_action)

        menu.addSeparator()
        rename_action = QAction("改名字", self)
        rename_action.triggered.connect(lambda: self.on_menu_action("rename"))
        menu.addAction(rename_action)
        status_action = QAction("查看状态", self)
        status_action.triggered.connect(lambda: self.on_menu_action("status"))
        menu.addAction(status_action)

        menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.quit_application)
        menu.addAction(exit_action)

        menu.exec_(global_pos)

    def on_menu_action(self, action_type: str):
        if action_type == "rename":
            name, ok = QInputDialog.getText(self, "改名字", "给宠物取个新名字吧：")
            if ok and name.strip():
                self.brain.set_name(name.strip())
                self._show_dialogue(f"以后我就叫{name}啦！")
            return
        elif action_type == "status":
            dialog = StatusDialog(self.brain, self)
            dialog.exec_()
            return
        elif action_type == "interact":
            text = self.brain.random_interact()
            self._show_dialogue(text)
            return

        text = self.brain.interact(action_type)
        self._show_dialogue(text)

    def _show_dialogue(self, text: str, duration: int = None):
        self.last_dialogue = text
        self.dialogue_timer = duration or FPS * 4

    def raise_window(self):
        self.show()
        self.raise_()

    def quit_application(self):
        self.brain.save_all()
        self.app.quit()

    def closeEvent(self, event):
        self.brain.save_all()
        event.accept()


class StatusDialog(QDialog):
    def __init__(self, brain, parent=None):
        super().__init__(parent)
        self.brain = brain
        self.setWindowTitle("宠物状态")
        self.setFixedSize(280, 320)
        self.setStyleSheet("""
            QDialog { background-color: #2D2D36; color: white; }
            QLabel { color: white; font-size: 13px; }
            QProgressBar {
                border: none; border-radius: 6px;
                background-color: #3D3D46; height: 16px;
                text-align: center; font-size: 11px; color: white;
            }
            QProgressBar::chunk { border-radius: 6px; }
        """)

        s = self.brain.get_status()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 16, 20, 16)

        name_label = QLabel(f"🐱  {s['name']}")
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; padding-bottom: 4px;")
        layout.addWidget(name_label)

        stats = [
            ("🍖  饱腹度", 100 - s["hunger"], "#FF9F43"),
            ("⚡  精力值", s["energy"], "#4FC3F7"),
            ("❤️  心情值", s["mood"], "#FF6B9D"),
            ("💚  健康值", s["health"], "#66BB6A"),
        ]
        for label, value, color in stats:
            frame = QFrame()
            frame.setStyleSheet("QFrame { background: transparent; }")
            row = QVBoxLayout()
            row.setSpacing(4)
            row.addWidget(QLabel(label))
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(value))
            bar.setFormat(f"{int(value)}/100")
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none; border-radius: 6px;
                    background-color: #3D3D46; height: 18px;
                    text-align: center; font-size: 11px; color: white;
                }}
                QProgressBar::chunk {{
                    border-radius: 6px;
                    background-color: {color};
                }}
            """)
            row.addWidget(bar)
            frame.setLayout(row)
            layout.addWidget(frame)

        layout.addStretch()
        self.setLayout(layout)
