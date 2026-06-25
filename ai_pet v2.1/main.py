import sys
import os
import pygame

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from config import DATA_DIR, bundled_path
from pet.brain import Brain
from pet.personality import Personality
from pet.memory import Memory
from pet.behavior import BehaviorEngine
from brain_models.char_rnn import CharRNN
from brain_models.train import train
from desktop.pet_window import PetWindow
from desktop.tray import TrayManager


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    brain = Brain()
    brain.load_state()

    weights_path = bundled_path("weights.npz")
    if not weights_path.exists():
        corpus_path = bundled_path("corpus.txt")
        if corpus_path.exists():
            print("[main] 首次启动，正在训练 Char-RNN 模型……")
            try:
                rnn = train(epochs=200)
                brain.rnn = rnn
                brain.dialogue.rnn = rnn
                print("[main] 训练完成！")
            except Exception as e:
                print(f"[main] 训练失败: {e}")

    window = PetWindow(brain, app)
    window.show()

    tray = TrayManager(window)
    tray.show()
    tray.show_notification("AI 桌面宠物", f"{brain.name} 来找你玩啦！右键点击宠物可以互动哦~")

    exit_code = app.exec_()
    pygame.quit()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
