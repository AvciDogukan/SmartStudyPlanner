# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Premium Completed Tasks Page
----------------------------
Modern, beautiful design with:
- Achievement cards
- Animated task cards
- Confetti celebration
- Stats overview
- Smooth animations

📊 Data Flow Overview
=====================
| Variable / Data             | Source / Origin                | Description |
|-----------------------------|--------------------------------|--------------|
| `user_email`                | Default parameter (manual)     | Current user email, used to fetch user ID |
| `user_id`                   | Database (`get_user_by_email`) | Unique user identifier |
| `completed_tasks`           | Database (`get_completed_tasks`) | All completed tasks for this user |
| `all_tasks`                 | Database (`get_all_tasks`)     | All tasks (pending + completed) for this user |
| `task["id"]`, `["title"]`, `["deadline"]`, `["duration"]`, `["strategy"]`, `["priority"]`, `["status"]` | Database fields | Real values stored per task |
| `total_completed`           | Calculated (len of completed)  | Count of completed tasks |
| `total_tasks`               | Calculated (len of all)        | Total number of tasks |
| `total_time`                | Calculated (sum of durations)  | Sum of durations of completed tasks |
| `success_rate`              | Calculated                     | (completed / total) × 100 |
| `avg_duration`              | Calculated                     | Average duration per completed task |
| `"No deadline"`             | UI placeholder                 | Displayed if no deadline exists |
| `"No strategy"`             | UI placeholder                 | Displayed if no strategy set |
| `"dogukan@example.com"`     | Default demo value             | Used if no login system present |

💡 Notes
--------
- All actual data (tasks, durations, strategies) are fetched from `DatabaseManager`.
- Only success rate, averages, and fallback labels are calculated locally.
- No dummy or randomly generated data is used.
- UI animations (confetti, cards, badges) are visual only; they do not hold data.
"""


from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QMessageBox, QFrame,
    QScrollArea, QGraphicsDropShadowEffect, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QLinearGradient, QBrush
from database import DatabaseManager
import random


# ============================================================
# 🎨 Completed Task Card Widget
# ============================================================
class CompletedTaskCard(QFrame):
    def __init__(self, task_id, title, deadline, duration, strategy, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.setMinimumHeight(140)
        self.setMaximumHeight(180)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFFFFF,
                    stop:1 #F8FAFC
                );
                border: 2px solid #E2E8F0;
                border-left: 1px solid #10B981;
                border-radius: 12px;
                padding: 10px;
            }
            QFrame:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F0FDF4,
                    stop:1 #ECFDF5
                );
                border: 2px solid #10B981;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 18, 25, 18)
        main_layout.setSpacing(20)
        
        # Left: Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(0, 5, 0, 5)
        
        # Checkmark + Title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        check_label = QLabel("✅")
        check_label.setFont(QFont("Segoe UI", 22))
        check_label.setFixedWidth(35)
        check_label.setStyleSheet("background: transparent; border: none;")
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #1E293B; background: transparent; border: none; line-height: 1.4;")
        
        title_layout.addWidget(check_label)
        title_layout.addWidget(title_label, stretch=1)
        title_layout.addStretch()
        
        # Details
        details_label = QLabel(f"📅 {deadline or 'No deadline'} • ⏱️ {duration} min • 🎯 {strategy or 'No strategy'}")
        details_label.setFont(QFont("Segoe UI", 11))
        details_label.setWordWrap(True)
        details_label.setStyleSheet("color: #64748B; background: transparent; border: none; line-height: 1.5;")
        
        info_layout.addLayout(title_layout)
        info_layout.addWidget(details_label)
        
        main_layout.addLayout(info_layout, stretch=3)
        
        # Right: Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignVCenter)
        
        view_btn = QPushButton("👁️ View")
        restore_btn = QPushButton("↩️ Restore")
        delete_btn = QPushButton("🗑️ Delete")
        
        for btn in [view_btn, restore_btn, delete_btn]:
            btn.setMinimumSize(100, 42)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    border: 2px solid #E2E8F0;
                    border-radius: 8px;
                    font-size: 11pt;
                    color: #1E293B;
                    padding: 8px 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #3B82F6;
                    border-color: #2563EB;
                    color: white;
                }
            """)
        
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                border: 2px solid #FECACA;
                border-radius: 8px;
                font-size: 11pt;
                color: #DC2626;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #EF4444;
                border-color: #DC2626;
                color: white;
            }
        """)
        
        self.view_btn = view_btn
        self.restore_btn = restore_btn
        self.delete_btn = delete_btn
        
        btn_layout.addWidget(view_btn)
        btn_layout.addWidget(restore_btn)
        btn_layout.addWidget(delete_btn)
        
        main_layout.addLayout(btn_layout)


# ============================================================
# 🎨 Achievement Badge Widget
# ============================================================
class AchievementBadge(QFrame):
    def __init__(self, icon, title, value, color, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 130)
        self.setMaximumHeight(140)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color},
                    stop:1 {self.darken_color(color)}
                );
                border-radius: 16px;
                padding: 18px;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 28))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none; color: white;")
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setStyleSheet("background: transparent; border: none; color: white;")
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("background: transparent; border: none; color: rgba(255,255,255,0.95);")
        
        layout.addWidget(icon_label)
        layout.addWidget(value_label)
        layout.addWidget(title_label)
    
    def darken_color(self, color):
        """Darken a hex color by 10%"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-25), max(0, g-25), max(0, b-25)
        return f'#{r:02x}{g:02x}{b:02x}'


# ============================================================
# 🎨 Confetti Animation Widget
# ============================================================
class ConfettiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.confetti = []
        self.colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899']
        
        for _ in range(50):
            self.confetti.append({
                'x': random.randint(0, 1000),
                'y': random.randint(-500, 0),
                'size': random.randint(6, 12),
                'speed': random.uniform(2, 5),
                'color': random.choice(self.colors),
                'rotation': random.randint(0, 360)
            })
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_confetti)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")
    
    def start(self):
        self.show()
        self.timer.start(30)
        QTimer.singleShot(3000, self.stop)
    
    def stop(self):
        self.timer.stop()
        self.hide()
    
    def update_confetti(self):
        for c in self.confetti:
            c['y'] += c['speed']
            c['rotation'] += 5
            if c['y'] > self.height():
                c['y'] = -20
                c['x'] = random.randint(0, self.width())
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for c in self.confetti:
            painter.save()
            painter.translate(c['x'], c['y'])
            painter.rotate(c['rotation'])
            
            color = QColor(c['color'])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(-c['size']//2, -c['size']//2, c['size'], c['size'])
            
            painter.restore()


# ============================================================
# 🎯 Premium Completed Page
# ============================================================
class CompletedPage(QWidget):
    def __init__(self, user_email="dogukan@example.com", parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.user_email = user_email

        user = self.db.get_user_by_email(self.user_email)
        self.user_id = user["id"] if user else None

        self.init_ui()
        self.load_completed_tasks()

    def init_ui(self):
        # Main layout with gradient background
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Background gradient
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F0FDF4,
                    stop:0.5 #ECFDF5,
                    stop:1 #D1FAE5
                );
            }
        """)
        
        # Confetti overlay
        self.confetti = ConfettiWidget(self)
        self.confetti.setGeometry(0, 0, 1200, 700)
        self.confetti.hide()
        
        # Content wrapper
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Title with icon
        title_section = QVBoxLayout()
        title = QLabel("🏆 Completed Tasks")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #047857; background: transparent;")
        
        subtitle = QLabel("Your achievements and completed work")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #059669; background: transparent;")
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        header_layout.addLayout(title_section)
        header_layout.addStretch()
        
        # Celebration button
        celebrate_btn = QPushButton("🎉 Celebrate!")
        celebrate_btn.setMinimumSize(180, 55)
        celebrate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10B981,
                    stop:1 #059669
                );
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 13pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669,
                    stop:1 #047857
                );
            }
        """)
        celebrate_btn.clicked.connect(self.celebrate)
        
        header_layout.addWidget(celebrate_btn)
        content_layout.addLayout(header_layout)
        
        # Stats badges
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Get real stats with calculations
        completed_tasks = self.db.get_completed_tasks(self.user_id) if self.user_id else []
        all_tasks = self.db.get_all_tasks(self.user_id) if self.user_id else []
        
        total_completed = len(completed_tasks)
        total_tasks = len(all_tasks)
        total_time = sum(t["duration"] for t in completed_tasks) if completed_tasks else 0
        
        # Calculate success rate (completed / total tasks)
        success_rate = int((total_completed / total_tasks * 100)) if total_tasks > 0 else 0
        
        # Calculate average task duration
        avg_duration = int(total_time / total_completed) if total_completed > 0 else 0
        
        badges_data = [
            ("✅", "Tasks Done", total_completed, "#10B981"),
            ("⏱️", "Total Time", f"{total_time//60}h {total_time%60}m", "#3B82F6"),
            ("📊", "Average Duration", f"{avg_duration} min", "#F59E0B"),
            ("🎯", "Success Rate", f"{success_rate}%", "#8B5CF6")
        ]
        
        for icon, title, value, color in badges_data:
            badge = AchievementBadge(icon, title, value, color)
            stats_layout.addWidget(badge)
        
        stats_layout.addStretch()
        content_layout.addLayout(stats_layout)
        
        # Tasks section header
        tasks_header = QLabel("📋 Completed Tasks List")
        tasks_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        tasks_header.setStyleSheet("color: #1E293B; background: transparent; margin-top: 10px;")
        content_layout.addWidget(tasks_header)
        
        # Scrollable task list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(226, 232, 240, 0.5);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #10B981;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #059669;
            }
        """)
        
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setSpacing(15)
        self.task_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.task_container)
        content_layout.addWidget(scroll)
        
        main_layout.addWidget(content)

    def load_completed_tasks(self):
        """Load and display completed tasks as beautiful cards"""
        if not self.user_id:
            return
        
        # Clear existing tasks
        while self.task_layout.count():
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        tasks = self.db.get_completed_tasks(self.user_id)
        
        if not tasks:
            # Empty state
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignCenter)
            
            empty_icon = QLabel("📭")
            empty_icon.setFont(QFont("Segoe UI", 64))
            empty_icon.setAlignment(Qt.AlignCenter)
            empty_icon.setStyleSheet("background: transparent;")
            
            empty_text = QLabel("No completed tasks yet")
            empty_text.setFont(QFont("Segoe UI", 14))
            empty_text.setAlignment(Qt.AlignCenter)
            empty_text.setStyleSheet("color: #64748B; background: transparent;")
            
            empty_subtext = QLabel("Complete tasks from the Planner to see them here!")
            empty_subtext.setAlignment(Qt.AlignCenter)
            empty_subtext.setStyleSheet("color: #94A3B8; background: transparent;")
            
            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_text)
            empty_layout.addWidget(empty_subtext)
            
            self.task_layout.addWidget(empty_widget)
            return
        
        # Add task cards
        for task in tasks:
            card = CompletedTaskCard(
                task["id"],
                task["title"],
                task["deadline"],
                task["duration"],
                task["strategy"]
            )
            
            # Connect buttons
            card.view_btn.clicked.connect(lambda _, t=task: self.view_details(t))
            card.restore_btn.clicked.connect(lambda _, tid=task["id"], title=task["title"]: self.restore_task(tid, title))
            card.delete_btn.clicked.connect(lambda _, tid=task["id"], title=task["title"]: self.delete_task(tid, title))
            
            self.task_layout.addWidget(card)
            
            # Animate card appearance
            animation = QPropertyAnimation(card, b"geometry")
            animation.setDuration(300)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.setStartValue(QRect(0, -100, card.width(), card.height()))
            animation.setEndValue(card.geometry())
            animation.start()
        
        self.task_layout.addStretch()

    def view_details(self, task):
        """Show task details in a beautiful dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Task Details")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"<h2>✅ {task['title']}</h2>")
        msg.setInformativeText(
            f"<p><b>📅 Deadline:</b> {task['deadline'] or 'No deadline'}</p>"
            f"<p><b>⏱️ Duration:</b> {task['duration']} minutes</p>"
            f"<p><b>🎯 Strategy:</b> {task['strategy'] or 'No strategy'}</p>"
            f"<p><b>🏆 Priority:</b> P{task['priority']}</p>"
            f"<p><b>📊 Status:</b> {task['status'].upper()}</p>"
        )
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #1E293B;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 11pt;
                font-weight: 600;
                min-width: 80px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        msg.exec_()

    def restore_task(self, task_id, task_title):
        """Restore task to pending"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Restore Task")
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"Move '{task_title}' back to Planner?")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #1E293B;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 11pt;
                font-weight: 600;
                min-width: 80px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        
        yes_btn = msg.addButton("Yes", QMessageBox.YesRole)
        no_btn = msg.addButton("No", QMessageBox.NoRole)
        msg.exec_()
        
        if msg.clickedButton() == yes_btn:
            self.db.update_task_status(task_id, "pending")
            QMessageBox.information(self, "✅ Restored", 
                f"'{task_title}' has been moved back to Planner!")
            self.refresh_page()

    def delete_task(self, task_id, task_title):
        """Permanently delete task"""
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ Delete Task")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Permanently delete '{task_title}'?")
        msg.setInformativeText("This action cannot be undone!")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #1E293B;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #64748B;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 11pt;
                font-weight: 600;
                min-width: 80px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        
        yes_btn = msg.addButton("Delete", QMessageBox.YesRole)
        yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 11pt;
                font-weight: 600;
                min-width: 80px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        no_btn = msg.addButton("Cancel", QMessageBox.NoRole)
        msg.exec_()
        
        if msg.clickedButton() == yes_btn:
            self.db.delete_task(task_id)
            QMessageBox.information(self, "🗑️ Deleted", 
                f"'{task_title}' has been permanently deleted.")
            self.refresh_page()
    
    def refresh_stats(self):
        """Refresh only the stats cards without recreating entire UI"""
        # Find and update stats badges
        # Get real stats with calculations
        completed_tasks = self.db.get_completed_tasks(self.user_id) if self.user_id else []
        all_tasks = self.db.get_all_tasks(self.user_id) if self.user_id else []
        
        total_completed = len(completed_tasks)
        total_tasks = len(all_tasks)
        total_time = sum(t["duration"] for t in completed_tasks) if completed_tasks else 0
        
        # Calculate success rate (completed / total tasks)
        success_rate = int((total_completed / total_tasks * 100)) if total_tasks > 0 else 0
        
        # Calculate average task duration
        avg_duration = int(total_time / total_completed) if total_completed > 0 else 0
        
        # Update would require recreating badges, so let's just reload tasks
        self.load_completed_tasks()
    
    def refresh_page(self):
        """Refresh entire page with updated stats"""
        # Clear and reload everything
        self.load_completed_tasks()
        # Recreate the whole UI to update stats cards
        # Clear current layout
        QWidget().setLayout(self.layout())
        self.init_ui()
        self.load_completed_tasks()

    def celebrate(self):
        """Trigger celebration animation"""
        self.confetti.start()
        QMessageBox.information(self, "🎉 Awesome!", 
            "You're doing great! Keep up the excellent work! 🌟")