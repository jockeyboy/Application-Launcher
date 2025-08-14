import sys
import subprocess
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QSpinBox, QLabel
)


class EXELauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Falcon Application Launcher")
        self.setGeometry(200, 200, 400, 350)

        layout = QVBoxLayout()

        self.listWidget = QListWidget()
        layout.addWidget(self.listWidget)

        btn_add = QPushButton("Add EXE(s)")
        btn_add.clicked.connect(self.add_exes)
        layout.addWidget(btn_add)

        btn_up = QPushButton("Move Up")
        btn_up.clicked.connect(self.move_up)
        layout.addWidget(btn_up)

        btn_down = QPushButton("Move Down")
        btn_down.clicked.connect(self.move_down)
        layout.addWidget(btn_down)

        # Timer setting
        layout.addWidget(QLabel("Delay between launches (seconds):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 300)  # 0 to 5 minutes
        self.delay_spin.setValue(5)  # default
        layout.addWidget(self.delay_spin)

        btn_run = QPushButton("Run in Order")
        btn_run.clicked.connect(self.run_exes_with_delay)
        layout.addWidget(btn_run)

        self.setLayout(layout)

        # Load saved EXEs if file exists
        self.save_file = "exe_list.txt"
        self.load_exes()

    def add_exes(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select EXE Files", "", "Executable Files (*.exe)"
        )
        for f in files:
            if not self.is_in_list(f):
                self.listWidget.addItem(f)

    def is_in_list(self, filepath):
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).text() == filepath:
                return True
        return False

    def move_up(self):
        current_row = self.listWidget.currentRow()
        if current_row > 0:
            item = self.listWidget.takeItem(current_row)
            self.listWidget.insertItem(current_row - 1, item)
            self.listWidget.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.listWidget.currentRow()
        if current_row < self.listWidget.count() - 1:
            item = self.listWidget.takeItem(current_row)
            self.listWidget.insertItem(current_row + 1, item)
            self.listWidget.setCurrentRow(current_row + 1)

    def run_exes_with_delay(self):
        if self.listWidget.count() == 0:
            QMessageBox.warning(self, "No Files", "Please add EXE files first.")
            return

        delay = self.delay_spin.value()

        for i in range(self.listWidget.count()):
            exe_path = self.listWidget.item(i).text()
            try:
                subprocess.Popen(exe_path)  # Launch app
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start {exe_path}\n{e}")
                continue

            if i < self.listWidget.count() - 1:  # No delay after last
                time.sleep(delay)  # Wait before launching next

    def closeEvent(self, event):
        """Save EXE list to file when closing."""
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                for i in range(self.listWidget.count()):
                    f.write(self.listWidget.item(i).text() + "\n")
        except Exception as e:
            print(f"Error saving EXE list: {e}")
        event.accept()

    def load_exes(self):
        """Load EXE list from file on startup."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    for line in f:
                        path = line.strip()
                        if os.path.isfile(path):
                            self.listWidget.addItem(path)
            except Exception as e:
                print(f"Error loading EXE list: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EXELauncher()
    window.show()
    sys.exit(app.exec_())
