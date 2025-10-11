# -*- coding: utf-8 -*-
"""
Smart Study Planner - Professional Light UI
------------------------------------------------------
Minimalist modern UI with animated sidebar icons, clean dashboard, 
and expandable structure for task management and focus modes.
"""

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, QTimer as QTimerCore
from PyQt5.QtGui import QFont, QPixmap, QIcon, QMovie
import sys
from PyQt5.QtWidgets import QGridLayout
from completed_page import CompletedPage  # en üste ekle
from focus_page import FocusPage
from statistics_page import StatisticsPage
from settings_page import SettingsPage
from planner_page import PlannerPage
from database import DatabaseManager
from PyQt5.QtCore import Qt, QSize, QTimer, QDate
from database import get_connection
from mentor_page import MentorPage




# ============================================================
# 🔹 Animated Sidebar Button (supports PNG + GIF hover icons)
# ============================================================
class AnimatedButton(QPushButton):
    def __init__(self, text, static_icon, gif_icon, parent=None):
        super().__init__(parent)
        self.text_label = QLabel(text, self)
        self.text_label.setFont(QFont("Segoe UI", 11))
        self.text_label.setStyleSheet("color: #334155; background: transparent;")

        # 🔹 Daha büyük ikon
        self.icon_size = QSize(34, 34)

        # 🔹 PNG ve GIF ikonları
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(self.icon_size)
        self.icon_label.setPixmap(QPixmap(static_icon).scaled(self.icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setStyleSheet("background: transparent;")

        self.gif_label = QLabel(self)
        self.gif_label.setFixedSize(self.icon_size)
        self.gif_label.setStyleSheet("background: transparent;")
        self.movie = QMovie(gif_icon)
        self.movie.setScaledSize(self.icon_size)
        self.gif_label.setMovie(self.movie)
        self.gif_label.hide()

        # 🔹 Layout hizalaması
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 5, 10, 5)
        layout.setSpacing(15)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.gif_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        # 🔹 Stiller (mavi çerçeve, beyaz zemin)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 2px solid transparent;
                border-radius: 8px;
                text-align: left;
                padding: 8px;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                border: 2px solid #2563EB;
            }
            QPushButton:hover QLabel {
                color: #2563EB;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #FFFFFF;
                border: 2px solid #2563EB;
            }
            QPushButton:checked QLabel {
                color: #2563EB;
                font-weight: bold;
            }
        """)

    def enterEvent(self, event):
        """Hover olunca GIF başlat, PNG gizle"""
        self.icon_label.hide()
        self.gif_label.show()
        self.movie.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover bitince GIF durur, PNG geri gelir"""
        self.movie.stop()
        self.gif_label.hide()
        self.icon_label.show()
        super().leaveEvent(event)



# ============================================================
# 🔹 Main Application Window
# ============================================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Study Planner")
        self.resize(1200, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #F9FAFB;
                color: #334155;
                font-family: 'Segoe UI';
                font-size: 11pt;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E3A8A;
            }
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
            }
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                background-color: #FFFFFF;
                gridline-color: #E2E8F0;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                font-weight: 600;
                border: none;
                padding: 6px;
            }
        """)

        # Layout
        main_layout = QHBoxLayout(self)

        # Sidebar
        sidebar = self.create_sidebar()

        # Pages
        self.stack = QStackedWidget()
        self.dashboard_page = self.create_dashboard_page()
        self.completed_page = CompletedPage()
        self.planner_page = PlannerPage()
        self.focus_page = FocusPage()
        self.stats_page = StatisticsPage()
        self.settings_page = SettingsPage()
        self.mentor_page = MentorPage()


        # Add pages to stacked widget
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.completed_page)
        self.stack.addWidget(self.planner_page)
        self.stack.addWidget(self.focus_page)
        self.stack.addWidget(self.stats_page)
        self.stack.addWidget(self.mentor_page)
        self.stack.addWidget(self.settings_page)
        
        # Add sidebar + stack to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

    # ============================================================
    # 🔸 Sidebar with Animated Buttons
    # ============================================================
    def create_sidebar(self):
        frame = QFrame()
        frame.setFixedWidth(300)
        frame.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-right: 1px solid #E2E8F0;
            }
            QPushButton {
                background-color: transparent;
                color: #334155;
                text-align: left;
                padding: 10px 24px;
                border: none;
                font-weight: 500;
                border-radius: 6px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
            QPushButton:checked {
                background-color: #2563EB;
                color: white;
            }
        """)

        main_layout = QVBoxLayout(frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----- Header -----
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 40, 0, 30)
        header_layout.setSpacing(8)

        logo_label = QLabel()
        pixmap = QPixmap("icon_transparent.png")
        pixmap = pixmap.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")

        title_label = QLabel("Smart Study Planner")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2563EB; background: transparent; border: none;")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)

        header_widget = QWidget()
        header_widget.setLayout(header_layout)

        # ----- Menu Buttons -----
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(0, 10, 0, 20)
        menu_layout.setSpacing(6)

        buttons_info = [
            ("Dashboard", "icons/dashboard.png", "icons/dashboard.gif"),
            ("Completed Tasks", "icons/completed.png", "icons/completed.gif"),
            ("Planner", "icons/calendar.png", "icons/calendar.gif"),
            ("Focus Mode", "icons/focus.png", "icons/focus.gif"),
            ("Statistics", "icons/stats.png", "icons/stats.gif"),
            ("AI Mentor", "icons/mentor.png", "icons/mentor.gif"),
            ("Settings", "icons/settings.png", "icons/settings.gif"),
        ]

        self.buttons = []
        for i, (text, icon_png, icon_gif) in enumerate(buttons_info):
            btn = AnimatedButton(text, icon_png, icon_gif)
            btn.clicked.connect(lambda _, idx=i: self.switch_page(idx))
            menu_layout.addWidget(btn)
            self.buttons.append(btn)

        self.buttons[0].setChecked(True)

        # ----- Footer -----
        footer_layout = QVBoxLayout()
        footer_layout.setContentsMargins(20, 10, 20, 20)
        footer_layout.setSpacing(4)

        user_label = QLabel("👤 dogukanavci")
        version_label = QLabel("v1.0.0")
        copyright_label = QLabel("© 2025 Smart Study Planner")

        for lbl in [user_label, version_label, copyright_label]:
            lbl.setAlignment(Qt.AlignLeft)
            lbl.setStyleSheet("color: #94A3B8; background: transparent;")

        footer_layout.addWidget(user_label)
        footer_layout.addWidget(version_label)
        footer_layout.addWidget(copyright_label)

        footer_widget = QWidget()
        footer_widget.setLayout(footer_layout)

        # ----- Combine -----
        main_layout.addWidget(header_widget)
        main_layout.addLayout(menu_layout)
        main_layout.addStretch()
        main_layout.addWidget(footer_widget)

        return frame

    # ============================================================
    # 🔸 Page Switching
    # ============================================================
    def switch_page(self, index):
        """Switch between pages and update button states + AUTO REFRESH"""
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        
        # 🔹 Her sayfa değişiminde o sayfayı yenile
        if index == 0:  # Dashboard
            self.refresh_dashboard()
        elif index == 1:  # Completed Tasks
            self.completed_page.refresh_page()  # ✅ Kartları güncelle
        elif index == 2:  # Planner
            self.planner_page.load_tasks()
        elif index == 3:  # Focus Mode
            self.focus_page.load_pending_tasks()
        elif index == 4:  # Statistics
            self.stats_page.refresh_stats()  # ✅ Her açılışta yenile
            
    def refresh_dashboard(self):
        """Dashboard'u tamamen yeniden oluştur"""
        # Eski dashboard'u kaldır
        old_dashboard = self.stack.widget(0)
        self.stack.removeWidget(old_dashboard)
        old_dashboard.deleteLater()
        
        # Yeni dashboard oluştur
        self.dashboard_page = self.create_dashboard_page()
        self.stack.insertWidget(0, self.dashboard_page)
        self.stack.setCurrentIndex(0)

    # ============================================================
    # 🔸 Dashboard Page (with Chart, Focus Ratio, Pomodoro Stats)
    # ============================================================
    def create_dashboard_page(self):
        import datetime
        from PyQt5.QtWidgets import QGridLayout
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # ----- Başlık -----
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1E3A8A;")
        layout.addWidget(title)

        # ============================================================
        # 🔹 Üst bölüm: Grafik (sol) + Kartlar (sağ)
        # ============================================================
        top_section = QHBoxLayout()
        top_section.setSpacing(25)

        # --- Veritabanı bağlantısı ---
        self.db = DatabaseManager()
        user = self.db.get_user_by_email("dogukan@example.com")
        user_id = user["id"] if user else None

        # --- Görev verileri ---
        all_tasks = self.db.get_all_tasks(user_id) if user_id else []
        completed_tasks = self.db.get_completed_tasks(user_id) if user_id else []

        total_focus_time = user["total_focus_minutes"] if user else 0
        planned_tasks_count = len(all_tasks)
        completed_tasks_count = len(completed_tasks)
        streak_days = user["streak_days"] if user else 0

        # 🔹 Basit hesaplamalar
        planned_time = sum([t["duration"] for t in all_tasks]) if all_tasks else 1
        focus_ratio = int((total_focus_time / planned_time) * 100) if planned_time > 0 else 0
        task_efficiency = int((completed_tasks_count / planned_tasks_count) * 100) if planned_tasks_count > 0 else 0

        # ============================================================
        # 🔸 Grafik (Son 7 Günlük Gerçek Focus Süresi)
        # ============================================================
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
            }
        """)
        chart_frame.setFixedSize(560, 400)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)
        
        fig = Figure(figsize=(5, 2))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 🔹 Gerçek veriyi daily_focus tablosundan çekelim
        from datetime import date, timedelta
        
        today = date.today()
        last_7_days = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
        daily_data = {day: 0 for day in last_7_days}
        
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT date, focus_minutes
                FROM daily_focus
                WHERE user_id = ?
                  AND date BETWEEN ? AND ?
                ORDER BY date ASC
            """, (user_id, last_7_days[0], last_7_days[-1]))
            rows = c.fetchall()
            for row in rows:
                daily_data[row["date"]] = row["focus_minutes"]
        
        # 🔹 Tarihleri kullanıcı dostu biçimde göster (örneğin 'Mon', 'Tue')
        import datetime
        days_labels = [datetime.datetime.fromisoformat(d).strftime("%a") for d in last_7_days]
        focus_minutes = list(daily_data.values())
        
        # 🔹 Grafik çizimi
        bars = ax.bar(days_labels, focus_minutes, color="#3B82F6", edgecolor="#1E3A8A", width=0.55)
        ax.set_title("Last 7 Days Focus Time (minutes)", fontsize=10, color="#1E3A8A")
        ax.set_ylabel("Minutes", fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        
        # 🔹 Ortalama çizgisi
        if focus_minutes:
            avg = sum(focus_minutes) / len(focus_minutes)
            ax.axhline(avg, color="#F97316", linestyle="--", linewidth=1.5, label=f"Avg: {int(avg)}m")
            ax.legend(fontsize=8, loc="upper right")
        
        # 🔹 Bar üstü değer etiketleri
        for bar in bars:
            yval = bar.get_height()
            if yval > 0:
                ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{int(yval)}",
                        ha='center', va='bottom', fontsize=8, color="#1E3A8A")
        
        chart_layout.addWidget(canvas)
        top_section.addWidget(chart_frame)


        # ============================================================
        # 🔸 Sağ Taraf: 6 Kart (Veritabanı verileriyle)
        # ============================================================
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        def create_stat_card(title_text, value_text, color):
            frame = QFrame()
            frame.setFixedSize(200, 120)
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 10px;
                }}
                QLabel {{
                    color: white;
                    background: transparent;
                }}
            """)
            card_layout = QVBoxLayout(frame)
            card_layout.setContentsMargins(6, 4, 6, 4)
            label_title = QLabel(title_text)
            label_title.setFont(QFont("Segoe UI", 9))
            label_title.setWordWrap(True)
            label_value = QLabel(str(value_text))
            label_value.setFont(QFont("Segoe UI", 12, QFont.Bold))
            card_layout.addWidget(label_title)
            card_layout.addWidget(label_value)
            return frame

        cards = [
            ("✅ Completed Tasks", str(completed_tasks_count), "#10B981"),
            ("🗓️ Planned Tasks", str(planned_tasks_count), "#F59E0B"),
            ("🎯 Focus Ratio", f"{focus_ratio}%", "#6366F1"),
            ("⚡ Task Efficiency", f"{task_efficiency}%", "#14B8A6"),
            ("🧠 Total Focus Time", f"{total_focus_time//60}h {total_focus_time%60}m", "#F97316"),
            ("🔥 Streak Days", str(streak_days), "#3B82F6"),
        ]

        row, col = 0, 0
        for title, value, color in cards:
            card = create_stat_card(title, value, color)
            grid_layout.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        right_widget = QWidget()
        right_widget.setLayout(grid_layout)
        top_section.addWidget(right_widget)
        layout.addLayout(top_section)

        # ============================================================
        # 🔹 Görev Tablosu (Veritabanından)
        # ============================================================
        task_table = QTableWidget(0, 5)
        task_table.setHorizontalHeaderLabels(["Task", "Deadline", "Duration", "Status", "Actions"])
        task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        task_table.setColumnWidth(4, 150)
        layout.addWidget(task_table)

        task_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                font-size: 10.5pt;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                font-weight: bold;
            }
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)

        # --- Veritabanından satırları ekle ---
        for row, task in enumerate(all_tasks):
            task_table.insertRow(row)
            task_table.setItem(row, 0, QTableWidgetItem(task["title"]))
            task_table.setItem(row, 1, QTableWidgetItem(task["deadline"]))
            task_table.setItem(row, 2, QTableWidgetItem(f"{task['duration']} min"))
            status_icon = "✅ Done" if task["status"] == "done" else "🕒 Pending"
            task_table.setItem(row, 3, QTableWidgetItem(status_icon))

            # --- Actions sütunu ---
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)

            # Durum Değiştir Butonu
            toggle_btn = QPushButton("↩ Toggle")
            toggle_btn.setStyleSheet("background-color: #3B82F6;")
            toggle_btn.clicked.connect(lambda _, t=task["id"], r=row: self.toggle_task_status(t, r, task_table))

            # Sil Butonu
            del_btn = QPushButton("✖ Delete")
            del_btn.setStyleSheet("background-color: #EF4444;")
            del_btn.clicked.connect(lambda _, t=task["id"], r=row: self.delete_task(t, r, task_table))

            action_layout.addWidget(toggle_btn)
            action_layout.addWidget(del_btn)
            action_widget.setLayout(action_layout)
            task_table.setCellWidget(row, 4, action_widget)

        # ============================================================
        # 🔹 Günlük Motivasyon Cümlesi
        # ============================================================
        quotes = [
            "Discipline beats motivation every time.",
            "You don’t need more time, you need more focus.",
            "Small progress is still progress.",
            "The secret to getting ahead is getting started.",
            "Success doesn’t come from what you do occasionally, but what you do consistently."
        ]
        day_index = datetime.datetime.now().weekday() % len(quotes)
        daily_quote = quotes[day_index]

        quote_label = QLabel(f"💬 {daily_quote}")
        quote_label.setWordWrap(True)
        quote_label.setAlignment(Qt.AlignCenter)
        quote_label.setStyleSheet("""
            QLabel {
                background-color: #EFF6FF;
                border-radius: 8px;
                border: 1px solid #BFDBFE;
                color: #1E3A8A;
                padding: 12px;
                font-style: italic;
            }
        """)
        layout.addWidget(quote_label)

        return page


    # ============================================================
    # 🔸 Yardımcı Fonksiyonlar (Dashboard içinde)
    # ============================================================
    def toggle_task_status(self, task_id, row, table):
        """Görev durumunu değiştirir (done/pending)."""
        task_item = table.item(row, 3)
        current = task_item.text()
        new_status = "done" if "Pending" in current else "pending"
        self.db.update_task_status(task_id, new_status)
        task_item.setText("✅ Done" if new_status == "done" else "🕒 Pending")
        
        QTimer.singleShot(500, self.refresh_dashboard)

    def delete_task(self, task_id, row, table):
        """Görevi siler (veritabanı + tablo)."""
        self.db.delete_task(task_id)
        table.removeRow(row)
        
        QTimer.singleShot(500, self.refresh_dashboard)
    
    # ============================================================
    # 🔸 Placeholder Pages
    # ============================================================
    def placeholder_page(self, title_text):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)
        return page


# ============================================================
# 🔹 Main Execution
# ============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
