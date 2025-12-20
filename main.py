import sys
import argparse
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon

# UI della GUI principale
from ui_mainwindow import Ui_MainWindow

# View già completa per la creazione dei dischi
from ui_disk import DiskView


class MainWindow(QMainWindow):
    def __init__(self, mode):
        super().__init__()

        if mode == "disk":
            # DiskView è già un QWidget completo
            self.setWindowTitle("QEMU Disk Creator")
            self.resize(1024, 360)

            self.disk_view = DiskView()
            self.setCentralWidget(self.disk_view)

        else:
            # GUI principale usa Ui_MainWindow con setupUi
            self.setWindowTitle("QEMU Manager")
            self.resize(650, 350)

            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

        self.show()


def parse_args():
    parser = argparse.ArgumentParser(description="QEMU GUI Launcher")

    parser.add_argument("-d", "--disk",
                        action="store_true",
                        help="Apri la GUI per creare dischi")

    parser.add_argument("-q", "--qemu",
                        action="store_true",
                        help="Apri la GUI principale")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.disk:
        mode = "disk"
    else:
        mode = "qemu"

    sys.argv[0] = "qemu-gui"
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    window = MainWindow(mode)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
