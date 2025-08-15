import sys
import subprocess
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QSpinBox, QLabel, QComboBox, QInputDialog
)


class MultiProfileLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Application Launcher")
        self.setGeometry(200, 200, 450, 400)

        self.profiles_dir = "profiles"
        os.makedirs(self.profiles_dir, exist_ok=True)

        layout = QVBoxLayout()

        # Profile selection
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Select Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.load_profile)
        profile_layout.addWidget(self.profile_combo)
        btn_new_profile = QPushButton("New Profile")
        btn_new_profile.clicked.connect(self.create_profile)
        profile_layout.addWidget(btn_new_profile)
        btn_delete_profile = QPushButton("Delete Profile")
        btn_delete_profile.clicked.connect(self.delete_profile)
        profile_layout.addWidget(btn_delete_profile)
        layout.addLayout(profile_layout)

        self.listWidget = QListWidget()
        layout.addWidget(self.listWidget)

        btn_add = QPushButton("Add EXE(s)")
        btn_add.clicked.connect(self.add_exes)
        layout.addWidget(btn_add)

        btn_remove = QPushButton("Remove Selected EXE")
        btn_remove.clicked.connect(self.remove_selected_exe)
        layout.addWidget(btn_remove)

        btn_up = QPushButton("Move Up")
        btn_up.clicked.connect(self.move_up)
        layout.addWidget(btn_up)

        btn_down = QPushButton("Move Down")
        btn_down.clicked.connect(self.move_down)
        layout.addWidget(btn_down)

        # Delay
        layout.addWidget(QLabel("Delay between launches (seconds):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 300)
        self.delay_spin.setValue(5)
        layout.addWidget(self.delay_spin)

        btn_run = QPushButton("Run EXEs with Delay")
        btn_run.clicked.connect(self.run_exes_with_delay)
        layout.addWidget(btn_run)

        self.setLayout(layout)

        self.load_profiles()

    # Profile management
    def load_profiles(self):
        self.profile_combo.clear()
        profiles = [f[:-4] for f in os.listdir(self.profiles_dir) if f.endswith(".txt")]
        self.profile_combo.addItems(profiles)
        if profiles:
            self.profile_combo.setCurrentIndex(0)

    def create_profile(self):
        text, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and text.strip():
            profile_file = os.path.join(self.profiles_dir, text.strip() + ".txt")
            if not os.path.exists(profile_file):
                open(profile_file, "w").close()
                self.load_profiles()
                self.profile_combo.setCurrentText(text.strip())
            else:
                QMessageBox.warning(self, "Exists", "Profile already exists.")

    def delete_profile(self):
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Are you sure you want to delete profile '{profile_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            file_path = self.profile_file_path(profile_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            self.load_profiles()

    def profile_file_path(self, profile_name):
        return os.path.join(self.profiles_dir, profile_name + ".txt")

    def load_profile(self):
        self.listWidget.clear()
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return
        file_path = self.profile_file_path(profile_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    path = line.strip()
                    if os.path.isfile(path):
                        self.listWidget.addItem(path)

    def save_profile(self):
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return
        file_path = self.profile_file_path(profile_name)
        with open(file_path, "w", encoding="utf-8") as f:
            for i in range(self.listWidget.count()):
                f.write(self.listWidget.item(i).text() + "\n")

    # EXE management
    def add_exes(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select EXE Files", "", "Executable Files (*.exe)"
        )
        for f in files:
            if not self.is_in_list(f):
                self.listWidget.addItem(f)
        self.save_profile()

    def remove_selected_exe(self):
        row = self.listWidget.currentRow()
        if row >= 0:
            self.listWidget.takeItem(row)
            self.save_profile()

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
        self.save_profile()

    def move_down(self):
        current_row = self.listWidget.currentRow()
        if current_row < self.listWidget.count() - 1:
            item = self.listWidget.takeItem(current_row)
            self.listWidget.insertItem(current_row + 1, item)
            self.listWidget.setCurrentRow(current_row + 1)
        self.save_profile()

    def run_exes_with_delay(self):
        if self.listWidget.count() == 0:
            QMessageBox.warning(self, "No Files", "Please add EXE files first.")
            return
        delay = self.delay_spin.value()
        for i in range(self.listWidget.count()):
            exe_path = self.listWidget.item(i).text()
            try:
                subprocess.Popen(exe_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start {exe_path}\n{e}")
            if i < self.listWidget.count() - 1:
                time.sleep(delay)

    def closeEvent(self, event):
        self.save_profile()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiProfileLauncher()
    window.show()
    sys.exit(app.exec_())
