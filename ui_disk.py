# ui_disk.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QSpinBox, QComboBox, QFileDialog, QTextEdit
)
from PySide6.QtCore import QRect
import subprocess


class DiskView(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1024, 360)
        self.setWindowTitle("QEMU Disk Creator")

        # ------------------------------
        # TITLE
        # ------------------------------
        self.Title = QLabel("QEMU DISK CREATOR", self)
        self.Title.setGeometry(20, 10, 400, 40)
        self.Title.setStyleSheet("font-size:22px;font-weight:bold;")

        # ------------------------------
        # PATH
        # ------------------------------
        QLabel("HDA Path:", self).setGeometry(20, 70, 100, 20)

        self.path_edit = QLineEdit(self)
        self.path_edit.setGeometry(130, 70, 420, 22)

        self.browse_btn = QPushButton("...", self)
        self.browse_btn.setGeometry(560, 65, 40, 30)

        # ------------------------------
        # SIZE
        # ------------------------------
        QLabel("Size (MB):", self).setGeometry(20, 110, 100, 20)

        self.size_spin = QSpinBox(self)
        self.size_spin.setGeometry(130, 110, 120, 22)
        self.size_spin.setMinimum(1)
        self.size_spin.setMaximum(999999)

        # ------------------------------
        # FORMAT
        # ------------------------------
        QLabel("Format:", self).setGeometry(20,150,100,20)

        self.format_box = QComboBox(self)
        self.format_box.setGeometry(130,150,140,26)
        self.format_box.addItems(["qcow2","raw"])

        # ------------------------------
        # CREATE
        # ------------------------------
        self.create_btn = QPushButton("Create", self)
        self.create_btn.setGeometry(130,200,120,32)

        # ------------------------------
        # LOG
        # ------------------------------
        self.log = QTextEdit(self)
        self.log.setGeometry(600,50,130,260)
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#1e1e1e;color:white;")


        # ------------------------------
        # CONNECTIONS
        # ------------------------------
        self.browse_btn.clicked.connect(self.pick_path)
        self.create_btn.clicked.connect(self.create_disk)

        print("DiskView loaded, connections ready ✅")


    # ------------------------------
    def log_msg(self, msg):
        print(msg)
        self.log.append(msg)

    # ------------------------------
    def pick_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save disk",
            "",
            "Disk Images (*.qcow2 *.img *.raw)"
        )
        if path:
            self.path_edit.setText(path)
            self.log_msg("Selected: " + path)

    # ------------------------------
    def create_disk(self):
        path = self.path_edit.text().strip()
        size = f"{self.size_spin.value()}M"
        fmt = self.format_box.currentText()

        self.log_msg("▶ create_disk triggered")

        if not path:
            self.log_msg("❌ Missing path!")
            return

        cmd = ["qemu-img","create","-f",fmt,path,size]
        self.log_msg("CMD: "+" ".join(cmd))

        try:
            r = subprocess.run(cmd, capture_output=True, text=True)

            self.log_msg("stdout: "+r.stdout)
            self.log_msg("stderr: "+r.stderr)

            if r.returncode == 0:
                self.log_msg("✅ Disk created!")
            else:
                self.log_msg("❌ Error code "+str(r.returncode))

        except Exception as e:
            self.log_msg("❌ Exception: "+str(e))

