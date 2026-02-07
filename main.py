from gui_moltbook import MoldBookGUI
from PyQt6.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    win = MoldBookGUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
