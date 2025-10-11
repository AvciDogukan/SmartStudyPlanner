from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QFrame, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QPainter, QColor, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import sys, random


# 🔹 Yağmur Efektli Arka Plan Widget'ı
class RainBackground(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.background = QPixmap(image_path)
        self.rain_drops = [self.create_drop() for _ in range(50)]  # yağmur damlası sayısı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rain)
        self.timer.start(40)  # 25 FPS

    def create_drop(self):
        """Yeni bir yağmur damlası oluşturur."""
        return {
            "x": random.randint(0, 600),
            "y": random.randint(-400, 0),
            "speed": random.uniform(5, 10),
            "length": random.randint(10, 20),
            "opacity": random.randint(80, 180)
        }

    def update_rain(self):
        """Her karede damlaların pozisyonunu günceller."""
        for drop in self.rain_drops:
            drop["y"] += drop["speed"]
            if drop["y"] > self.height():
                drop["y"] = random.randint(-100, 0)
                drop["x"] = random.randint(0, self.width())
        self.update()

    def paintEvent(self, event):
        """Görseli ve damlaları çizer."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Arka plan resmi
        scaled_bg = self.background.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_bg)

        # Yağmur damlaları
        for drop in self.rain_drops:
            color = QColor(255, 255, 255, drop["opacity"])
            painter.setPen(color)
            painter.drawLine(drop["x"], drop["y"], drop["x"], drop["y"] + drop["length"])


# 🔹 Login Arayüzü
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Study Planner - Login")
        self.setGeometry(200, 100, 1150, 700)
        self.setStyleSheet("background-color: white;")

        # Ana layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sol panel (yağmur efektiyle)
        self.left_frame = RainBackground("assets/morning_productivity.png")
        self.main_layout.addWidget(self.left_frame, 1)

        # Sağ panel (login)
        self.right_frame = QFrame()
        self.right_frame.setStyleSheet("background-color: white;")
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(100, 100, 100, 100)
        self.right_layout.setSpacing(20)

        # Başlıklar
        welcome_label = QLabel("👋 Welcome Back")
        welcome_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        welcome_label.setStyleSheet("color:#1e3a8a;")

        subtitle = QLabel("Please sign in to continue")
        subtitle.setStyleSheet("color:#64748b; font-size:12pt; margin-bottom:10px;")

        # Giriş alanları
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email address")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding:12px; border:1px solid #cbd5e1; border-radius:8px;
                background-color:#f8fafc; font-size:11pt;
            }
            QLineEdit:focus { border:1.5px solid #2563eb; background-color:white; }
        """)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding:12px; border:1px solid #cbd5e1; border-radius:8px;
                background-color:#f8fafc; font-size:11pt;
            }
            QLineEdit:focus { border:1.5px solid #2563eb; background-color:white; }
        """)

        # Parola gösterme kutusu
        self.show_pass = QCheckBox("Show Password")
        self.show_pass.stateChanged.connect(self.toggle_password_visibility)

        # Giriş butonu
        self.login_button = QPushButton("Sign In")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color:#2563eb; color:white; font-weight:bold;
                border-radius:8px; padding:12px; font-size:12pt;
            }
            QPushButton:hover { background-color:#1d4ed8; }
        """)
        self.login_button.clicked.connect(self.handle_login)

        # Alt metin
        footer = QLabel("By signing in, you agree to our <a href='#'>Terms of Service</a>")
        footer.setOpenExternalLinks(True)
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color:#64748b; font-size:10pt;")

        # Sağ paneli oluştur
        self.right_layout.addWidget(welcome_label)
        self.right_layout.addWidget(subtitle)
        self.right_layout.addSpacing(10)
        self.right_layout.addWidget(self.email_input)
        self.right_layout.addWidget(self.password_input)
        self.right_layout.addWidget(self.show_pass)
        self.right_layout.addSpacing(10)
        self.right_layout.addWidget(self.login_button)
        self.right_layout.addStretch()
        self.right_layout.addWidget(footer)
        self.main_layout.addWidget(self.right_frame, 1)

    # Parola görünürlüğü
    def toggle_password_visibility(self, state):
        self.password_input.setEchoMode(QLineEdit.Normal if state else QLineEdit.Password)

    # Basit giriş kontrolü
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")
            return
        if email == "dogukan@example.com" and password == "1234":
            QMessageBox.information(self, "Success", "Login successful! 🚀")
        else:
            QMessageBox.critical(self, "Error", "Invalid email or password.")


# 🔹 Ana Çalıştırma
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
