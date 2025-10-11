# -*- coding: utf-8 -*-
"""
🎯 FocusPage - Modern Clean White Theme (Full Backend Integration)
==================================================================
Light UI version of Focus Mode with identical backend logic:
- Integrated with DatabaseManager, User, Task, Planner, and StrategyFactory
- Real-time statistics update (streak, total focus, completed/pending tasks)
- Visual redesign using white glass cards and minimalist progress visuals
- Includes all session controls (Start / Pause / Continue / Reset / Complete)

🧠 Data Flow Overview
---------------------
| Variable / Attribute                   | Source / Method / Description                                   | Type / Category              | Function |
|---------------------------------------|------------------------------------------------------------------|------------------------------|-----------|
| `self.db`                             | `DatabaseManager()` instance                                     | 🔹 Database Connection        | Provides CRUD operations for users, tasks, sessions, and statistics. |
| `self.user_email`                     | `"dogukan@example.com"` (hardcoded for active session)           | 🔸 Local Constant             | Used for retrieving or creating user data in the database. |
| `user_data`                           | `self.db.get_user_by_email(self.user_email)`                     | 🔹 Database Query             | Returns current user record (id, streak_days, total_focus_minutes). |
| `self.user_id`                        | From `user_data["id"]` or created by `self.db.add_user()`        | 🔹 Database Derived           | Primary key of current user. |
| `self.user`                           | `User("dogukanavci", self.user_email)`                           | 🔸 Local Object               | High-level wrapper around user-related logic. |
| `self.strategy_name`                  | Default `"pomodoro"` / updated via `change_strategy()`           | 🔸 Local State Variable       | Determines focus logic type: pomodoro / deepwork / balanced. |
| `self.strategy`                       | `StrategyFactory.create(self.strategy_name)`                     | 🔸 Local Object (Strategy)    | Strategy instance controlling timing behavior. |
| `self.planner`                        | `Planner(self.user, self.strategy)`                              | 🔸 Local Object (Composition) | Manages the task list and executes strategy logic. |
| `self.timer`                          | `QTimer()` (interval = 1 s)                                      | 🔸 UI Timer                   | Countdown timer triggering `update_timer()` every second. |
| `self.remaining_time`                 | Integer (seconds)                                                | 🔸 Runtime Variable           | Remaining seconds for the active focus session. |
| `self.total_duration`                 | `duration * 60`                                                  | 🔸 Runtime Variable           | Total focus time for selected strategy in seconds. |
| `self.is_running`, `self.is_paused`   | Boolean flags                                                    | 🔸 State Variables            | Indicate current session activity. |
| `self.session_start_time`             | `datetime.datetime.now()`                                        | 🔸 Runtime Variable           | Timestamp of when session started. |
| `self.current_task_id`                | Task ID or `None`                                                | 🔸 Local Variable (Nullable)  | Associates session with a specific task (if applicable). |
| `self.circular_progress`              | `ModernCircularProgress()`                                       | 🔸 UI Widget                  | Custom widget rendering gradient circular progress. |
| `self.time_label`                     | `QLabel("25:00")`                                                | 🔸 UI Element                 | Displays countdown (MM:SS). Updated every second. |
| `self.strategy_combo`                 | `QComboBox()`                                                    | 🔸 UI Element                 | Dropdown for strategy selection (Pomodoro, DeepWork, Balanced). |
| `self.task_list_layout`               | `QVBoxLayout()`                                                  | 🔸 UI Container               | Holds `ModernTaskCard` widgets for pending tasks. |
| `self.stats_value_labels`             | `list[QLabel]`                                                   | 🔸 UI References              | References to value labels in stat cards for live refresh. |
| `self.start_btn`, `pause_btn`, etc.   | `QPushButton()` controls                                          | 🔸 UI Controls                | Buttons for session management (Start, Pause, Continue, Complete, Reset). |
| `self.status_label`                   | `QLabel()`                                                       | 🔸 UI Feedback Element        | Displays textual state of current session. |
| `completed_count`                     | `sum(1 for t in all_tasks if t["status"] == "done")`             | 🔹 Database Derived           | Total number of completed tasks. |
| `pending_count`                       | `sum(1 for t in all_tasks if t["status"] == "pending")`          | 🔹 Database Derived           | Total number of pending tasks. |
| `stats_data`                          | Local list of (icon, title, value, color)                        | 🔸 Local Data Structure       | Populates StatCard widgets. |
| `elapsed_seconds`                     | `self.total_duration - self.remaining_time`                      | 🔸 Calculated Local           | Total seconds elapsed in current session. |
| `duration_minutes`                    | `max(1, elapsed_seconds / 60)`                                   | 🔸 Calculated Local           | Converted minutes (minimum 1 min for DB logging). |
| `self.db.add_focus_minutes()`         | Database write                                                   | 🔹 Database Update            | Increases user’s total focus time. |
| `self.db.update_streak()`             | Database write                                                   | 🔹 Database Update            | Updates streak based on session completion date. |
| `self.db.update_average_session()`    | Database write                                                   | 🔹 Database Update            | Recalculates average session duration. |
| `self.db.log_session()`               | Database insert                                                  | 🔹 Database Insert            | Records session metadata (strategy, start/end time, duration). |

⚙️ Functional Event Flow
------------------------
1. **change_strategy(index)** → Updates `self.strategy_name`, sets new duration, updates combo box display.  
2. **start_focus()** → Initializes session timers, sets total duration, and starts countdown (`QTimer.start(1000)`).  
3. **update_timer()** → Decrements remaining time, updates circular progress, refreshes label each second.  
4. **pause_focus() / continue_focus()** → Toggle `self.is_running` and `self.is_paused`, controlling timer state.  
5. **complete_session()** →  
   - Stops timer  
   - Calculates elapsed minutes  
   - Updates database (`add_focus_minutes`, `update_streak`, `update_average_session`, `log_session`)  
   - Refreshes UI (stats, task list) and shows confirmation dialog.  
6. **refresh_stats()** → Reloads database metrics and updates stat cards dynamically.  
7. **reset_focus()** → Restores default UI and clears runtime variables.

💡 Data Category Legend
-----------------------
🔹 **Database Query/Update:** Data persisted in SQLite through `DatabaseManager`.  
🔸 **Local / Runtime / UI Variable:** In-memory state controlling session behavior and display.  

💬 Notes
--------
- The UI runs on a pure white gradient background for minimal eye strain.  
- `ModernCircularProgress` provides smooth progress drawing using gradient pens (blue → purple).  
- Database synchronization occurs **only** after `complete_session()`.  
- `refresh_stats()` ensures user metrics (focus time, streak, tasks) are instantly updated after each session.  
- The class maintains **full backend parity** with the dark “Premium Focus Mode” version for seamless theme switching.

"""


import random
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox, QGraphicsDropShadowEffect,
    QFrame, QScrollArea, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QPen, QColor, QBrush, QLinearGradient, QPainterPath

# Backend Integration
from database import DatabaseManager
from core.user import User
from core.task import Task
from core.planner import Planner
from strategies.factory import StrategyFactory


# ============================================================
# 🎨 Modern Circular Progress (White Theme)
# ============================================================
class ModernCircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 280)
        self._progress = 0
        self._max_value = 100
        
    @pyqtProperty(int)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()
    
    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background circle (light gray)
        pen = QPen()
        pen.setWidth(18)
        pen.setColor(QColor("#E8EEF5"))
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(20, 20, width-40, height-40, 0, 360 * 16)
        
        # Progress arc (gradient blue to purple)
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor("#667EEA"))
        gradient.setColorAt(1, QColor("#764BA2"))
        
        pen.setBrush(QBrush(gradient))
        pen.setColor(QColor("#667EEA"))
        painter.setPen(pen)
        
        angle = int(self._progress * 360 / self._max_value * 16)
        painter.drawArc(20, 20, width-40, height-40, 90 * 16, -angle)


# ============================================================
# 🎨 Clean White Card
# ============================================================
class CleanCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(100, 116, 139, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


# ============================================================
# 🎨 Stat Card (White Theme)
# ============================================================
class StatCard(QFrame):
    def __init__(self, icon, title, value, color, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setMinimumWidth(150)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 2px solid {color}30;
                border-radius: 14px;
                padding: 9px;
            }}
            QFrame:hover {{
                border: 2px solid {color}60;
                background: {color}08;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 14, 16, 14)
        
        # Icon + Title
        header = QHBoxLayout()
        header.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setStyleSheet("border: none; background: transparent;")
        icon_label.setFixedSize(0, 0)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet(f"color: #64748B; border: none; background: transparent;")
        title_label.setWordWrap(False)
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color}; border: none; background: transparent;")
        self.value_label.setWordWrap(False)
        
        layout.addLayout(header)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


# ============================================================
# 🎨 Task Card (White Theme)
# ============================================================
class ModernTaskCard(QFrame):
    def __init__(self, task_title, priority, duration, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(85)
        
        colors = {
            1: "#EF4444",  # Red
            2: "#F59E0B",  # Orange
            3: "#3B82F6",  # Blue
            4: "#10B981"   # Green
        }
        color = colors.get(priority, "#64748B")
        
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 4px solid {color};
                border-radius: 10px;
                padding: 14px;
            }}
            QFrame:hover {{
                background: #F8FAFC;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        
        # Title
        title = QLabel(task_title)
        title.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        title.setWordWrap(True)
        title.setStyleSheet(f"color: #1E293B; background: transparent; border: none;")
        
        # Info
        info = QLabel(f"P{priority} • {duration} min")
        info.setFont(QFont("Segoe UI", 10))
        info.setStyleSheet(f"color: {color}; background: transparent; border: none; font-weight: 600;")
        
        layout.addWidget(title)
        layout.addWidget(info)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


# ============================================================
# 🎯 Focus Page - Modern White Theme
# ============================================================
class FocusPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Database setup
        self.db = DatabaseManager()
        self.user_email = "dogukan@example.com"
        user_data = self.db.get_user_by_email(self.user_email)
        
        if not user_data:
            self.user_id = self.db.add_user("dogukanavci", self.user_email)
        else:
            self.user_id = user_data["id"]
        
        # Core backend integration
        self.user = User("dogukanavci", self.user_email)
        self.strategy_name = "pomodoro"
        self.strategy = StrategyFactory.create(self.strategy_name)
        self.planner = Planner(self.user, self.strategy)
        
        self.load_tasks_to_planner()
        
        # Timer variables
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        self.total_duration = 0
        self.is_running = False
        self.is_paused = False
        self.session_start_time = None
        self.current_task_id = None
        
        self.init_ui()
    
    def load_tasks_to_planner(self):
        """Load pending tasks from database"""
        db_tasks = self.db.get_all_tasks(self.user_id)
        for db_task in db_tasks:
            if db_task["status"] == "pending":
                deadline = datetime.datetime.fromisoformat(db_task["deadline"]) if db_task["deadline"] else None
                task = Task(
                    db_task["id"],
                    db_task["priority"],
                    db_task["title"],
                    deadline,
                    db_task["duration"],
                    db_task["status"]
                )
                self.planner.add_task(task)
    
    def load_pending_tasks(self):
        """Reload pending tasks"""
        self.planner = Planner(self.user, self.strategy)
        self.load_tasks_to_planner()
        self.refresh_task_list()
    
    def refresh_task_list(self):
        """Refresh task list UI"""
        if hasattr(self, 'task_list_layout'):
            while self.task_list_layout.count():
                item = self.task_list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            pending_tasks = self.planner.filter_tasks("pending")
            
            if pending_tasks:
                for task in pending_tasks[:5]:
                    card = ModernTaskCard(task.get_title(), task.get_priority(), task.get_duration())
                    self.task_list_layout.addWidget(card)
            else:
                no_tasks = QLabel("No pending tasks ✨")
                no_tasks.setFont(QFont("Segoe UI", 11))
                no_tasks.setAlignment(Qt.AlignCenter)
                no_tasks.setStyleSheet("color: #94A3B8; background: transparent; padding: 30px;")
                self.task_list_layout.addWidget(no_tasks)
            
            self.task_list_layout.addStretch()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Clean white background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF,
                    stop:1 #F8FAFC
                );
            }
        """)
        
        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(50, 40, 50, 40)
        content_layout.setSpacing(30)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Focus Mode")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #1E293B; background: transparent;")
        
        subtitle = QLabel("Deep work sessions")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #64748B; background: transparent;")
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        header.addLayout(header_layout)
        header.addStretch()
        content_layout.addLayout(header)
        
        # Stats Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        user_data = self.db.get_user_by_email(self.user_email)
        all_tasks = self.db.get_all_tasks(self.user_id)
        completed_count = sum(1 for task in all_tasks if task["status"] == "done")
        pending_count = sum(1 for task in all_tasks if task["status"] == "pending")
        
        stats_data = [
            ("","🔥 Streak", f"{user_data['streak_days'] if user_data else 0} days", "#F59E0B"),
            ("", "⏱️ Focus Time", f"{(user_data['total_focus_minutes']//60) if user_data else 0}h {(user_data['total_focus_minutes']%60) if user_data else 0}m", "#667EEA"),
            ("", "✅ Completed", f"{completed_count}", "#10B981"),
            ("", "📋 Pending", f"{pending_count}", "#3B82F6")
        ]
        
        self.stats_value_labels = []
        
        for icon, title, value, color in stats_data:
            card = StatCard(icon, title, value, color)
            self.stats_value_labels.append(card.value_label)
            stats_layout.addWidget(card)
        
        content_layout.addLayout(stats_layout)
        
        # Main Timer Section
        timer_section = QHBoxLayout()
        timer_section.setSpacing(40)
        
        # Left: Timer
        timer_container = QWidget()
        timer_container.setStyleSheet("background: transparent;")  # ✅ Şeffaf
        timer_layout = QVBoxLayout(timer_container)
        timer_layout.setAlignment(Qt.AlignCenter)
        timer_layout.setSpacing(20)
        
        # Circular progress with time label inside
        progress_wrapper = QWidget()
        progress_wrapper.setFixedSize(280, 280)
        
        self.circular_progress = ModernCircularProgress(progress_wrapper)
        
        # Time label INSIDE the wrapper
        self.time_label = QLabel("25:00", progress_wrapper)
        self.time_label.setFont(QFont("Segoe UI", 70, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #1E293B; background: transparent;")
        self.time_label.setGeometry(0, 100, 280, 80)
        
        timer_layout.addWidget(progress_wrapper, alignment=Qt.AlignCenter)
        
        # Strategy selector
        strategy_label = QLabel("Focus Strategy")
        strategy_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        strategy_label.setStyleSheet("color: #64748B; background: transparent;")
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["🍅 Pomodoro (25 min)", "🧠 Deep Work (90 min)", "⚖️ Balanced (45 min)"])
        self.strategy_combo.setStyleSheet("""
            QComboBox {
                background: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px 16px;
                color: #1E293B;
                font-size: 11pt;
                font-weight: 600;
            }
            QComboBox:hover {
                border: 2px solid #667EEA;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #1E293B;
                selection-background-color: #667EEA;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        self.strategy_combo.currentIndexChanged.connect(self.change_strategy)
        
        timer_layout.addWidget(strategy_label, alignment=Qt.AlignCenter)
        timer_layout.addWidget(self.strategy_combo)
        timer_section.addWidget(timer_container)
        
        # Right: Tasks
        task_container = CleanCard()
        task_layout = QVBoxLayout(task_container)
        task_layout.setSpacing(16)
        
        task_header = QLabel("📋 Active Tasks")
        task_header.setFont(QFont("Segoe UI", 15, QFont.Bold))
        task_header.setStyleSheet("color: #1E293B; background: transparent; border: none;")
        task_layout.addWidget(task_header)
        
        # Scrollable task list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
            }
        """)
        
        task_list_widget = QWidget()
        self.task_list_layout = QVBoxLayout(task_list_widget)
        self.task_list_layout.setSpacing(12)
        
        pending_tasks = self.planner.filter_tasks("pending")
        if pending_tasks:
            for task in pending_tasks[:5]:
                card = ModernTaskCard(task.get_title(), task.get_priority(), task.get_duration())
                self.task_list_layout.addWidget(card)
        else:
            no_tasks = QLabel("No pending tasks ✨")
            no_tasks.setFont(QFont("Segoe UI", 11))
            no_tasks.setAlignment(Qt.AlignCenter)
            no_tasks.setStyleSheet("color: #94A3B8; background: transparent; padding: 30px;")
            self.task_list_layout.addWidget(no_tasks)
        
        self.task_list_layout.addStretch()
        scroll.setWidget(task_list_widget)
        task_layout.addWidget(scroll)
        timer_section.addWidget(task_container)
        
        content_layout.addLayout(timer_section)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.start_btn = QPushButton("▶ Start")
        self.pause_btn = QPushButton("⏸ Pause")
        self.continue_btn = QPushButton("▶ Continue")
        self.complete_btn = QPushButton("✅ Complete")
        self.reset_btn = QPushButton("⟲ Reset")
        
        self.continue_btn.hide()
        self.complete_btn.hide()
        
        # Button styles
        default_style = """
            QPushButton {
                background: #667EEA;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 24px;
                font-size: 12pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #5568D3;
            }
            QPushButton:pressed {
                background: #4C51BF;
            }
        """
        
        complete_style = """
            QPushButton {
                background: #10B981;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 24px;
                font-size: 12pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #059669;
            }
            QPushButton:pressed {
                background: #047857;
            }
        """
        
        for btn in [self.start_btn, self.pause_btn, self.continue_btn, self.reset_btn]:
            btn.setStyleSheet(default_style)
            btn.setMinimumHeight(50)
            
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(102, 126, 234, 60))
            shadow.setOffset(0, 4)
            btn.setGraphicsEffect(shadow)
        
        self.complete_btn.setStyleSheet(complete_style)
        self.complete_btn.setMinimumHeight(50)
        
        self.start_btn.clicked.connect(self.start_focus)
        self.pause_btn.clicked.connect(self.pause_focus)
        self.continue_btn.clicked.connect(self.continue_focus)
        self.complete_btn.clicked.connect(self.complete_session)
        self.reset_btn.clicked.connect(self.reset_focus)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.continue_btn)
        btn_layout.addWidget(self.complete_btn)
        btn_layout.addWidget(self.reset_btn)
        content_layout.addLayout(btn_layout)
        
        # Status
        self.status_label = QLabel("Ready to focus 💪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setStyleSheet("color: #64748B; background: transparent; padding: 10px;")
        content_layout.addWidget(self.status_label)
        
        main_layout.addWidget(content)
        
        # Time label is now inside progress_wrapper, no need for positioning
    
    def change_strategy(self, index):
        """Change focus strategy"""
        strategy_map = {0: "pomodoro", 1: "deepwork", 2: "balanced"}
        durations = {0: 25, 1: 90, 2: 45}
        
        self.strategy_name = strategy_map[index]
        self.strategy = StrategyFactory.create(self.strategy_name)
        self.planner.set_strategy(self.strategy)
        
        duration = durations[index]
        self.time_label.setText(f"{duration}:00")
        self.status_label.setText(f"✅ Strategy: {self.strategy_name.capitalize()} ({duration} min)")
    
    def start_focus(self):
        """Start focus session"""
        if self.is_running:
            return
        
        durations = [25, 90, 45]
        duration = durations[self.strategy_combo.currentIndex()]
        
        self.total_duration = duration * 60
        self.remaining_time = self.total_duration
        self.session_start_time = datetime.datetime.now()
        
        self.planner.execute_strategy()
        
        self.timer.start(1000)
        self.is_running = True
        self.is_paused = False
        
        self.status_label.setText(f"🔥 Focus session in progress...")
        self.start_btn.hide()
        self.pause_btn.show()
        self.complete_btn.show()
    
    def pause_focus(self):
        """Pause session"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.is_paused = True
            self.status_label.setText("⏸ Paused")
            self.pause_btn.hide()
            self.continue_btn.show()
    
    def continue_focus(self):
        """Continue session"""
        if self.is_paused:
            self.timer.start(1000)
            self.is_running = True
            self.is_paused = False
            self.status_label.setText("🔥 Resumed!")
            self.continue_btn.hide()
            self.pause_btn.show()
    
    def reset_focus(self):
        """Reset session"""
        self.timer.stop()
        self.remaining_time = 0
        self.circular_progress.progress = 0
        self.time_label.setText("25:00")
        self.is_running = False
        self.is_paused = False
        self.status_label.setText("Ready to focus 💪")
        self.start_btn.show()
        self.pause_btn.show()
        self.continue_btn.hide()
        self.complete_btn.hide()
    
    def update_timer(self):
        """Update timer"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            elapsed = self.total_duration - self.remaining_time
            progress = int((elapsed / self.total_duration) * 100)
            self.circular_progress.progress = progress
            
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.time_label.setText(f"{minutes:02}:{seconds:02}")
        else:
            self.complete_session()
    
    def complete_session(self):
        """Complete and save session"""
        if not self.is_running and not self.is_paused:
            QMessageBox.warning(self, "⚠️ No Active Session", 
                "Please start a focus session first!")
            return
        
        if self.session_start_time is None:
            QMessageBox.warning(self, "⚠️ No Active Session", 
                "Please start a focus session first!")
            return
        
        self.timer.stop()
        self.is_running = False
        
        elapsed_seconds = self.total_duration - self.remaining_time
        duration_minutes = max(1, int(elapsed_seconds / 60))
        
        if duration_minutes < 1:
            QMessageBox.warning(self, "⚠️ Too Short", 
                "Session must be at least 1 minute!")
            self.reset_focus()
            return
        
        # Save to database
        self.db.add_focus_minutes(self.user_id, duration_minutes)
        self.db.update_streak(self.user_id, datetime.datetime.now().isoformat())
        self.db.update_average_session(self.user_id)
        
        if self.session_start_time:
            self.db.log_session(
                task_id=self.current_task_id,
                strategy=self.strategy_name,
                start_time=self.session_start_time,
                end_time=datetime.datetime.now(),
                duration=duration_minutes
            )
        
        user_updated = self.db.get_user_by_email(self.user_email)
        
        self.status_label.setText("✅ Session completed!")
        
        QMessageBox.information(self, "🎉 Session Complete!", 
            f"Great work! You completed {duration_minutes} minutes of focused work!\n\n"
            f"🔥 Streak: {user_updated['streak_days']} days\n"
            f"⏱️ Total Focus: {user_updated['total_focus_minutes']//60}h {user_updated['total_focus_minutes']%60}m")
        
        self.reset_focus()
        self.load_pending_tasks()
        self.refresh_stats()
    
    def refresh_stats(self):
        """Refresh statistics"""
        user_data = self.db.get_user_by_email(self.user_email)
        all_tasks = self.db.get_all_tasks(self.user_id)
        completed_count = sum(1 for task in all_tasks if task["status"] == "done")
        pending_count = sum(1 for task in all_tasks if task["status"] == "pending")
        
        total_hours = (user_data['total_focus_minutes']//60) if user_data else 0
        total_mins = (user_data['total_focus_minutes']%60) if user_data else 0
        
        stats_values = [
            f"{user_data['streak_days'] if user_data else 0} days",
            f"{total_hours}h {total_mins}m",
            f"{completed_count} tasks",
            f"{pending_count} tasks"
        ]
        
        if hasattr(self, 'stats_value_labels'):
            for i, label in enumerate(self.stats_value_labels):
                label.setText(stats_values[i])