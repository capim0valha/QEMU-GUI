from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QLineEdit, QPushButton,
    QSpinBox, QCheckBox, QTextEdit,
    QFileDialog, QComboBox
)
from PySide6.QtCore import QRect, Qt
import platform
from PySide6.QtWidgets import QMainWindow
import subprocess
import threading

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.qemu_process = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(650, 350)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Title
        self.Title = QLabel(self.centralwidget)
        self.Title.setGeometry(QRect(20, 10, 400, 40))
        self.Title.setText("QEMU Manager")
        self.Title.setStyleSheet("font-size: 24px; font-weight: bold;")

        # RAM selector
        self.RamLabel = QLabel(self.centralwidget)
        self.RamLabel.setGeometry(QRect(20, 70, 120, 25))
        self.RamLabel.setText("RAM (MB):")

        self.RamSpin = QSpinBox(self.centralwidget)
        self.RamSpin.setGeometry(QRect(150, 70, 100, 25))
        self.RamSpin.setMinimum(256)
        self.RamSpin.setMaximum(32768)
        self.RamSpin.setValue(2048)

        # GPU Cores
        self.CpuLabel = QLabel(self.centralwidget)
        self.CpuLabel.setGeometry(QRect(20, 105, 120, 25))
        self.CpuLabel.setText("CPU Cores:")

        self.CpuSpin = QSpinBox(self.centralwidget)
        self.CpuSpin.setGeometry(QRect(150, 105, 100, 25))
        self.CpuSpin.setMinimum(1)
        self.CpuSpin.setMaximum(16)
        self.CpuSpin.setValue(2)


        # Arch selection
        self.ArchLabel = QLabel(self.centralwidget)
        self.ArchLabel.setGeometry(QRect(20, 145, 150, 25))
        self.ArchLabel.setText("Architecture:")

        self.ArchCombo = QComboBox(self.centralwidget)
        self.ArchCombo.setGeometry(QRect(150, 145, 150, 25))
        self.ArchCombo.addItems(["x86_64", "aarch64", "i386", "riscv64"])

        # HDA Path
        self.HdaLabel = QLabel(self.centralwidget)
        self.HdaLabel.setGeometry(QRect(20, 190, 150, 25))
        self.HdaLabel.setText("Disk (HDA):")

        self.HdaPath = QLineEdit(self.centralwidget)
        self.HdaPath.setGeometry(QRect(150, 190, 300, 25))

        self.HdaBtn = QPushButton(self.centralwidget)
        self.HdaBtn.setGeometry(QRect(460, 190, 30, 25))
        self.HdaBtn.setText("...")

        # CD Path
        self.CdLabel = QLabel(self.centralwidget)
        self.CdLabel.setGeometry(QRect(20, 225, 150, 25))
        self.CdLabel.setText("CD-ROM:")

        self.CdPath = QLineEdit(self.centralwidget)
        self.CdPath.setGeometry(QRect(150, 225, 300, 25))

        self.CdBtn = QPushButton(self.centralwidget)
        self.CdBtn.setGeometry(QRect(460, 225, 30, 25))
        self.CdBtn.setText("...")

        # KVM
        self.KvmCheck = QCheckBox(self.centralwidget)
        self.KvmCheck.setGeometry(QRect(20, 260, 200, 25))
        self.KvmCheck.setText("Enable KVM (Linux only)")

        # Disable KVM on non-Linux
        if platform.system().lower() != "linux":
            self.KvmCheck.setEnabled(False)

        # Boot button
        self.BootBtn = QPushButton(self.centralwidget)
        self.BootBtn.setGeometry(QRect(20, 330, 150, 35))  # prima era 295
        self.BootBtn.setText("Boot")

        # LOGS
        self.Logs = QTextEdit(self.centralwidget)
        self.Logs.setGeometry(QRect(500, 70, 130, 260))
        self.Logs.setReadOnly(True)
        self.Logs.setStyleSheet("background: #1e1e1e; color: white;")

        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setWindowTitle("QEMU Manager")

        # Connect file pickers
        self.HdaBtn.clicked.connect(self.pick_hda)
        self.CdBtn.clicked.connect(self.pick_cd)
        self.BootBtn.clicked.connect(self.boot)

        # Boot picker
        self.BootLabel = QLabel(self.centralwidget)
        self.BootLabel.setGeometry(QRect(20, 290, 120, 25))
        self.BootLabel.setText("Boot from:")

        self.BootCombo = QComboBox(self.centralwidget)
        self.BootCombo.setGeometry(QRect(150, 290, 100, 25))
        self.BootCombo.addItems(["Hard Disk (C)", "CD-ROM (D)"])

        # Kill button
        self.KillBtn = QPushButton(self.centralwidget)
        self.KillBtn.setGeometry(QRect(180, 330, 150, 35))
        self.KillBtn.setText("Kill")
        self.KillBtn.clicked.connect(self.kill_qemu)




    def pick_hda(self):
        path, _ = QFileDialog.getOpenFileName(
            None, "Select HDA Disk", "", "Disk Images (*.img *.qcow2 *.bin *.raw)"
        )
        if path:
            self.HdaPath.setText(path)

    def pick_cd(self):
        path, _ = QFileDialog.getOpenFileName(
            None, "Select CD-ROM ISO", "", "ISO Files (*.iso)"
        )
        if path:
            self.CdPath.setText(path)
    def boot(self):
        ram = self.RamSpin.value()
        cpu = self.CpuSpin.value()
        arch = self.ArchCombo.currentText()
        hda = self.HdaPath.text()
        cd = self.CdPath.text()
        kvm = self.KvmCheck.isChecked()

        boot_choice = self.BootCombo.currentText()
        boot_flag = "d" if "CD-ROM" in boot_choice else "c"

        cmd = ["qemu-system-" + arch, "-m", str(ram), "-smp", str(cpu), "-boot", boot_flag]
        if hda:
            cmd += ["-drive", f"file={hda}"]
        if cd:
            cmd += ["-cdrom", cd]
        if kvm:
            cmd += ["-enable-kvm"]

        # Lancia QEMU in un thread separato
        def run_qemu():
            try:
                self.qemu_process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in self.qemu_process.stdout:
                    self.Logs.append(line.strip())
            except Exception as e:
                self.Logs.append(f"Error running QEMU: {e}")

        thread = threading.Thread(target=run_qemu)
        thread.start()

    def kill_qemu(self):
        if self.qemu_process and self.qemu_process.poll() is None:
            self.qemu_process.terminate()
            self.Logs.append("QEMU process terminated.")

