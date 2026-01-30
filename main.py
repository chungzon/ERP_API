import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app_gui import AppGUI


def main():
    app = AppGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
