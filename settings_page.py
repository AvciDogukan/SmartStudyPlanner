# -*- coding: utf-8 -*-
"""
Settings Page (Database Entegrasyonu)
-------------------------------------
Kullanıcının uygulama tercihlerini kalıcı olarak SQLite veritabanına kaydeder.
- Kullanıcı bilgileri (isim, hedef)
- Tema, animasyon, ses, hatırlatıcı tercihleri
- Tam sıfırlama ve hakkında bölümü
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QComboBox,
    QCheckBox, QSlider, QMessageBox, QFrame, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import DatabaseManager


class SettingsPage(QWidget):
    def __init__(self, username="dogukanavci", email="dogukan@example.com"):
        super().__init__()

        # 🔹 Database bağlantısı
        self.db = DatabaseManager()

        # 🔹 Kullanıcı bilgilerini yükle
        self.user = self.db.get_user_by_email(email)
        if not self.user:
            self.user_id = self.db.add_user(username, email)
            self.user = self.db.get_user_by_email(email)
        else:
            self.user_id = self.user["id"]

        # 🔹 Tercihlerin varsayılan değerleri
        self.preferences = {
            "theme": "Light",
            "animations": True,
            "sound": True,
            "reminder": True,
            "volume": 70,
            "goal": "",
        }

        # 🔹 Veritabanından mevcut tercihler varsa yükle
        self.load_user_preferences()

        # 🔹 UI başlat
        self.init_ui()

    # ============================================================
    # 🔹 Kullanıcı Arayüzü
    # ============================================================
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(25)

        title = QLabel("⚙️ Uygulama Ayarları")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E3A8A;")
        layout.addWidget(title)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #CBD5E1; margin: 10px 0;")
        layout.addWidget(divider)

        # ============================================================
        # 🧑‍💻 Kullanıcı Ayarları
        # ============================================================
        user_label = QLabel("👤 Kullanıcı Ayarları")
        user_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(user_label)

        # Ad
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Adınızı girin")
        self.name_edit.setText(self.user["username"])
        layout.addWidget(self.name_edit)

        # Hedef
        self.goal_edit = QLineEdit()
        self.goal_edit.setPlaceholderText("Haftalık hedef (ör. 20 saat odaklanma)")
        self.goal_edit.setText(self.preferences["goal"])
        layout.addWidget(self.goal_edit)

        save_btn = QPushButton("💾 Kaydet")
        save_btn.clicked.connect(self.save_user_settings)
        save_btn.setStyleSheet(self.button_style("#2563EB"))
        layout.addWidget(save_btn)

        # ============================================================
        # 🎨 Tema & Görünüm
        # ============================================================
        theme_label = QLabel("🎨 Tema ve Görünüm")
        theme_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(theme_label)

        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Aurora", "Ocean Blue", "Sunset"])
        self.theme_combo.setCurrentText(self.preferences["theme"])
        theme_layout.addWidget(self.theme_combo)

        self.animations_cb = QCheckBox("Animasyonları etkinleştir")
        self.animations_cb.setChecked(self.preferences["animations"])
        theme_layout.addWidget(self.animations_cb)

        layout.addLayout(theme_layout)

        apply_theme_btn = QPushButton("Temayı Uygula")
        apply_theme_btn.clicked.connect(self.apply_theme)
        apply_theme_btn.setStyleSheet(self.button_style("#10B981"))
        layout.addWidget(apply_theme_btn)

        # ============================================================
        # 🔔 Bildirim & Odak Ayarları
        # ============================================================
        focus_label = QLabel("🔔 Odak ve Bildirim Ayarları")
        focus_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(focus_label)

        self.sound_cb = QCheckBox("Seans başında sesli bildirim")
        self.sound_cb.setChecked(self.preferences["sound"])
        layout.addWidget(self.sound_cb)

        self.reminder_cb = QCheckBox("Ara zamanı geldiğinde hatırlat")
        self.reminder_cb.setChecked(self.preferences["reminder"])
        layout.addWidget(self.reminder_cb)

        volume_label = QLabel("🔊 Bildirim Sesi Seviyesi")
        layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.preferences["volume"])
        layout.addWidget(self.volume_slider)

        # ============================================================
        # 🧹 Reset & About
        # ============================================================
        reset_label = QLabel("🧹 Veri ve Hakkında")
        reset_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(reset_label)

        reset_btn = QPushButton("Tüm Verileri Sıfırla")
        reset_btn.clicked.connect(self.reset_data)
        reset_btn.setStyleSheet(self.button_style("#EF4444"))
        layout.addWidget(reset_btn)

        about_btn = QPushButton("📘 Hakkında")
        about_btn.clicked.connect(self.show_about)
        about_btn.setStyleSheet(self.button_style("#6366F1"))
        layout.addWidget(about_btn)

        layout.addStretch()

    # ============================================================
    # 🔹 Yardımcı Fonksiyonlar
    # ============================================================
    def button_style(self, color):
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            font-weight: bold;
            padding: 8px;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: #1E40AF;
        }}
        """

    # ============================================================
    # 🔹 Veritabanı Entegrasyonu
    # ============================================================
    def load_user_preferences(self):
        """Kullanıcının veritabanında kayıtlı tercihler varsa yükler."""
        with open("user_prefs.txt", "a+") as f:
            f.seek(0)
            data = f.read().strip().split(",")
            if len(data) >= 6:
                self.preferences = {
                    "theme": data[0],
                    "animations": data[1] == "True",
                    "sound": data[2] == "True",
                    "reminder": data[3] == "True",
                    "volume": int(data[4]),
                    "goal": data[5],
                }

    def save_user_preferences(self):
        """Tercihleri dosyaya veya veritabanına kaydeder."""
        self.preferences = {
            "theme": self.theme_combo.currentText(),
            "animations": self.animations_cb.isChecked(),
            "sound": self.sound_cb.isChecked(),
            "reminder": self.reminder_cb.isChecked(),
            "volume": self.volume_slider.value(),
            "goal": self.goal_edit.text().strip(),
        }
        with open("user_prefs.txt", "w") as f:
            f.write(",".join(map(str, self.preferences.values())))

    # ============================================================
    # 🔹 Event Handlers
    # ============================================================
    def save_user_settings(self):
        """Kullanıcı bilgilerini ve hedefini kaydeder."""
        name = self.name_edit.text().strip()
        goal = self.goal_edit.text().strip()
        if name:
            self.db.add_user(name, self.user["email"])
        self.save_user_preferences()
        QMessageBox.information(self, "Kaydedildi", "Kullanıcı ayarları başarıyla kaydedildi ✅")

    def apply_theme(self):
        selected = self.theme_combo.currentText()
        self.save_user_preferences()
        QMessageBox.information(self, "Tema Uygulandı", f"Yeni tema: {selected} 🎨")

    def reset_data(self):
        confirm = QMessageBox.question(
            self, "Veri Sıfırlama",
            "Tüm çalışma geçmişi, görevler ve tercihler silinecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            from os import remove
            try:
                remove("study_planner.db")
                remove("user_prefs.txt")
                QMessageBox.information(self, "Sıfırlandı", "Tüm veriler başarıyla temizlendi 🧹")
            except FileNotFoundError:
                QMessageBox.information(self, "Temiz", "Silinecek veri bulunamadı 🧹")

    def show_about(self):
        QMessageBox.information(
            self, "Smart Study Planner",
            "Smart Study Planner v1.0\n\nDeveloped by Doğukan Avcı\nModern Productivity System 💡"
        )
