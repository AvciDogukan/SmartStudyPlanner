# -*- coding: utf-8 -*-
"""
Planner Page (Database Entegrasyonu + Auto Refresh)
---------------------------------------------------
Görev planlama sayfası; SQLite veritabanı ile tam entegre.
Kullanıcı görevlerini kalıcı olarak kaydeder, listeler, siler ve günceller.
+ Otomatik yenileme eklendi

📊 Data Flow Overview
=====================
| Veri / Değişken              | Kaynak / Yöntem                        | Açıklama |
|-------------------------------|----------------------------------------|-----------|
| `self.db`                    | `DatabaseManager()`                    | Veritabanı bağlantısı nesnesi |
| `self.username`, `self.email`| Kod içinde sabit (örnek kullanıcı)     | Varsayılan kullanıcı bilgisi |
| `self.user_id`               | `self.db.add_user(username, email)`    | Kullanıcıyı ekler veya mevcut kullanıcı ID’sini döner |
| `self.table`                 | PyQt5 QTableWidget                     | Görevleri gösteren tablo arayüzü |
| `self.title_input`           | Kullanıcı girişi (QLineEdit)           | Görev başlığı metin kutusu |
| `self.priority_combo`        | Kullanıcı girişi (QComboBox)           | Görev önceliği (1–5) |
| `self.deadline_input`        | Kullanıcı girişi (QDateEdit)           | Görev bitiş tarihi |
| `self.duration_input`        | Kullanıcı girişi (QLineEdit)           | Tahmini süre (dakika) |
| `self.strategy_combo`        | Kullanıcı girişi (QComboBox)           | Çalışma stratejisi (Pomodoro, Deep Work, Balanced) |
| `self.db.add_task()`         | Veritabanı yazma işlemi                | Yeni görev ekler |
| `self.db.get_all_tasks()`    | Veritabanı okuma işlemi                | Tüm görevleri çeker (pending + done) |
| `self.db.update_task_status()`| Veritabanı güncelleme işlemi           | Görevi “done” durumuna geçirir |
| `self.db.delete_task()`      | Veritabanı silme işlemi                | Görevi kalıcı olarak siler |
| `task["id"]`, `["title"]`, `["priority"]`, `["deadline"]`, `["duration"]`, `["strategy"]`, `["status"]` | Veritabanı sütunları | Her görev kaydının birebir alanları |
| `add_task()`                 | Frontend fonksiyonu                    | Kullanıcı girdilerini alır, DB’ye kaydeder |
| `load_tasks()`               | Frontend fonksiyonu                    | Veritabanındaki görevleri tabloya yükler |
| `insert_task_row(task)`      | UI fonksiyonu                          | Tek bir görevi tabloya satır olarak ekler |
| `mark_done(task_id)`         | Backend bağlantılı fonksiyon           | Görevi tamamlanmış olarak işaretler |
| `delete_task(task_id)`       | Backend bağlantılı fonksiyon           | Görevi veritabanından siler |
| `"pending"`, `"done"`        | Sabit değer                            | Görev durumları |

💡 Notlar
---------
- Tüm görevler SQLite veritabanında `DatabaseManager` üzerinden saklanır.
- Hiçbir dummy veri kullanılmaz.
- Kullanıcı e-posta ve isim alanı sadece örnek olarak atanır (demo kullanıcı).
- PlannerPage → `CompletedPage` ile tamamen uyumlu çalışır (sütunlar ve statü değerleri birebir aynı).
- Görev ekleme, silme ve tamamlama işlemleri anında tabloyu yeniler (`load_tasks()` çağrısı).
"""


from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame, QDateEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from database import DatabaseManager


class PlannerPage(QWidget):
    """Görev planlama sayfası (SQLite veritabanı bağlantılı)."""

    def __init__(self):
        super().__init__()

        # 🔹 Veritabanı bağlantısı
        self.db = DatabaseManager()

        # 🔹 Varsayılan kullanıcı (örnek)
        self.username = "dogukanavci"
        self.email = "dogukan@example.com"
        self.user_id = self.db.add_user(self.username, self.email)

        # 🔹 UI başlat
        self.init_ui()
        self.load_tasks()  # veritabanındaki görevleri yükle

    # ============================================================
    # 🔹 UI Setup
    # ============================================================
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(25)

        # Başlık
        title = QLabel("🗓️ Görev Planlayıcısı")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0F172A; letter-spacing: 0.5px;")
        layout.addWidget(title)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: rgba(148,163,184,0.3); margin: 10px 0;")
        layout.addWidget(divider)

        # ============================================================
        # 🔹 Görev Ekleme Alanı
        # ============================================================
        form_layout = QHBoxLayout()
        form_layout.setSpacing(20)

        label_style = """
            QLabel {
                font-weight: 600;
                color: #1E3A8A;
                font-size: 10pt;
                margin-bottom: 4px;
            }
        """

        input_style = """
            QLineEdit, QDateEdit, QComboBox {
                background: rgba(255,255,255,0.85);
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                padding: 6px 10px;
                font-size: 10.5pt;
                color: #0F172A;
                min-width: 130px;
            }
            QLineEdit:hover, QDateEdit:hover, QComboBox:hover {
                border: 1px solid #3B82F6;
                background: rgba(255,255,255,1);
            }
        """

        # --- Görev Başlığı ---
        title_box = QVBoxLayout()
        label_title = QLabel("Görev Başlığı:")
        label_title.setStyleSheet(label_style)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Örn: Rapor Yazımı")
        self.title_input.setStyleSheet(input_style)
        title_box.addWidget(label_title)
        title_box.addWidget(self.title_input)
        form_layout.addLayout(title_box)

        # --- Öncelik ---
        priority_box = QVBoxLayout()
        label_priority = QLabel("Öncelik:")
        label_priority.setStyleSheet(label_style)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["1", "2", "3", "4", "5"])
        self.priority_combo.setStyleSheet(input_style)
        priority_box.addWidget(label_priority)
        priority_box.addWidget(self.priority_combo)
        form_layout.addLayout(priority_box)

        # --- Deadline ---
        deadline_box = QVBoxLayout()
        label_deadline = QLabel("Bitiş Tarihi:")
        label_deadline.setStyleSheet(label_style)
        self.deadline_input = QDateEdit()
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setStyleSheet(input_style)
        deadline_box.addWidget(label_deadline)
        deadline_box.addWidget(self.deadline_input)
        form_layout.addLayout(deadline_box)

        # --- Süre ---
        duration_box = QVBoxLayout()
        label_duration = QLabel("Tahmini Süre (dk):")
        label_duration.setStyleSheet(label_style)
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Örn: 90")
        self.duration_input.setStyleSheet(input_style)
        duration_box.addWidget(label_duration)
        duration_box.addWidget(self.duration_input)
        form_layout.addLayout(duration_box)

        # --- Strateji ---
        strategy_box = QVBoxLayout()
        label_strategy = QLabel("Strateji:")
        label_strategy.setStyleSheet(label_style)
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Pomodoro", "Deep Work", "Balanced"])
        self.strategy_combo.setStyleSheet(input_style)
        strategy_box.addWidget(label_strategy)
        strategy_box.addWidget(self.strategy_combo)
        form_layout.addLayout(strategy_box)

        # --- Ekle Butonu ---
        add_btn = QPushButton("➕ Ekle")
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border-radius: 10px;
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563EB, stop:1 #1E40AF);
            }
        """)
        add_btn.clicked.connect(self.add_task)
        form_layout.addWidget(add_btn)

        layout.addLayout(form_layout)

        # ============================================================
        # 🔸 Görev Tablosu
        # ============================================================
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Başlık", "Öncelik", "Deadline", "Süre", "Durum", "İşlemler"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(226,232,240,0.9);
                border-radius: 12px;
                font-size: 10.5pt;
            }
            QHeaderView::section {
                background-color: #EFF6FF;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #DBEAFE;
                padding: 8px;
                color: #1E3A8A;
            }
        """)

        layout.addStretch()

    # ============================================================
    # 🔹 Veritabanından Görevleri Yükle
    # ============================================================
    def load_tasks(self):
        """Tüm görevleri veritabanından çeker ve tabloya ekler."""
        self.table.setRowCount(0)  # ✅ Önce tabloyu temizle
        tasks = self.db.get_all_tasks(self.user_id)
        for task in tasks:
            self.insert_task_row(task)

    # ============================================================
    # 🔹 Görev Ekleme
    # ============================================================
    def add_task(self):
        """Yeni görev ekler (veritabanına kaydeder)."""
        title = self.title_input.text().strip()
        duration_text = self.duration_input.text().strip()
        priority = int(self.priority_combo.currentText())
        deadline_qdate = self.deadline_input.date()
        deadline = datetime(deadline_qdate.year(), deadline_qdate.month(), deadline_qdate.day())
        strategy = self.strategy_combo.currentText()

        if not title or not duration_text.isdigit():
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen görev başlığı ve geçerli süre giriniz.")
            return

        duration = int(duration_text)

        # ✅ Veritabanına kaydet
        task_id = self.db.add_task(
            user_id=self.user_id,
            title=title,
            priority=priority,
            deadline=deadline.strftime("%Y-%m-%d"),
            duration=duration,
            strategy=strategy,
            status="pending"
        )

        # ✅ Alanları temizle
        self.title_input.clear()
        self.duration_input.clear()
        
        # ✅ Tabloyu yeniden yükle (otomatik güncelleme)
        self.load_tasks()
        
        QMessageBox.information(self, "Başarılı", f"Görev '{title}' başarıyla eklendi!")

    # ============================================================
    # 🔹 Tabloya Satır Ekle
    # ============================================================
    def insert_task_row(self, task):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(task["id"])))
        self.table.setItem(row, 1, QTableWidgetItem(task["title"]))
        self.table.setItem(row, 2, QTableWidgetItem(str(task["priority"])))
        self.table.setItem(row, 3, QTableWidgetItem(task["deadline"]))
        self.table.setItem(row, 4, QTableWidgetItem(str(task["duration"])))
        
        # Status renkli göster
        status_item = QTableWidgetItem(task["status"])
        if task["status"] == "done":
            status_item.setForeground(Qt.green)
        else:
            status_item.setForeground(Qt.blue)
        self.table.setItem(row, 5, status_item)

        # --- İşlem Butonları ---
        cell_layout = QHBoxLayout()
        btn_done = QPushButton("✅ Tamamla")
        btn_done.setStyleSheet("background-color: #10B981; color: white; border-radius: 6px; padding: 5px 10px;")
        btn_done.clicked.connect(lambda _, t=task["id"]: self.mark_done(t))

        btn_delete = QPushButton("🗑️ Sil")
        btn_delete.setStyleSheet("background-color: #EF4444; color: white; border-radius: 6px; padding: 5px 10px;")
        btn_delete.clicked.connect(lambda _, t=task["id"]: self.delete_task(t))

        container = QWidget()
        hbox = QHBoxLayout(container)
        hbox.addWidget(btn_done)
        hbox.addWidget(btn_delete)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(5)
        self.table.setCellWidget(row, 6, container)

    # ============================================================
    # 🔹 Görev Tamamlama
    # ============================================================
    def mark_done(self, task_id: int):
        """Görevi tamamlandı olarak işaretler."""
        self.db.update_task_status(task_id, "done")
        self.load_tasks()  # ✅ Tabloyu yenile
        QMessageBox.information(self, "Tamamlandı", f"Görev #{task_id} başarıyla tamamlandı!")

    # ============================================================
    # 🔹 Görev Silme
    # ============================================================
    def delete_task(self, task_id: int):
        """Görevi veritabanından siler."""
        reply = QMessageBox.question(self, "Silme Onayı", 
            f"Görev #{task_id} silinecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.db.delete_task(task_id)
            self.load_tasks()  # ✅ Tabloyu yenile
            QMessageBox.information(self, "Silindi", f"Görev #{task_id} kaldırıldı.")