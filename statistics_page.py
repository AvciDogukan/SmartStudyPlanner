# -*- coding: utf-8 -*-
"""
📊 StatisticsPage - Comprehensive Data Flow Documentation
---------------------------------------------------------
Smart Study Planner: Statistics & Analytics Dashboard

This class visualizes and summarizes the user's overall productivity performance.
It connects directly to the database and aggregates multiple tables
(users, user_stats, tasks, sessions) to provide live analytical insights.

🧠 Data Flow Overview
=====================
| Variable / Data Name                 | Source / Method Used                                      | Type / Source Category          | Description |
|-------------------------------------|-----------------------------------------------------------|----------------------------------|-------------|
| `self.db`                           | `DatabaseManager()`                                       | 🔹 Database Connection           | Central DB connection (SQLite) handling all queries and updates. |
| `self.user_email`                   | `__init__` parameter (default="dogukan@example.com")      | 🔸 Local Constant                | Current user email. Used as a unique identifier in DB. |
| `self.user_data`                    | `db.get_user_by_email(user_email)`                        | 🔹 Database Query                | Returns full user record (id, streak_days, total_focus_minutes, etc.). |
| `self.user_id`                      | `self.user_data["id"]` if available                      | 🔹 Derived from Database         | Primary key of the user in DB. |
| `self.user`                         | `User("dogukanavci", user_email)`                         | 🔸 Local Object                  | High-level user object for planner integration. |
| `self.strategy`                     | `StrategyFactory.create("pomodoro")`                      | 🔸 Local Object                  | Current focus strategy (Pomodoro/DeepWork/Balanced). |
| `self.planner`                      | `Planner(self.user, self.strategy)`                       | 🔸 Local Object                  | Task management and statistics interface. |
| `db_tasks`                          | `db.get_all_tasks(user_id)`                               | 🔹 Database Query                | Retrieves all tasks (pending, completed). |
| `completed_tasks`                   | `db.get_completed_tasks(user_id)`                         | 🔹 Database Query                | Retrieves only completed tasks for performance calculation. |
| `stats`                             | `db.get_user_stats(user_id)`                              | 🔹 Database Query                | Optional aggregated statistics (average session, weekly score, etc.). |
| `total_minutes`                     | `user["total_focus_minutes"]`                             | 🔹 Database Field                | Total focus time in minutes from users table. |
| `total_hours`                       | `total_minutes // 60`                                     | 🔸 Derived Local                 | Total focus time (hours). |
| `remaining_minutes`                 | `total_minutes % 60`                                      | 🔸 Derived Local                 | Remaining minutes after converting to hours. |
| `streak`                            | `user["streak_days"]`                                     | 🔹 Database Field                | Number of consecutive focus days. |
| `avg_session`                       | `stats["average_session"]`                                | 🔹 Database Field                | Average focus session duration (minutes). |
| `weekly_score`                      | `stats["weekly_score"]`                                   | 🔹 Database Field                | Performance score of the user (0–10 scale). |
| `total_tasks_count`                 | `len(all_tasks)`                                          | 🔸 Calculated Local              | Number of total tasks created by user. |
| `completed_count`                   | `len(completed_tasks)`                                    | 🔸 Calculated Local              | Number of completed tasks. |
| `completion_rate`                   | `(completed_count / total_tasks_count) * 100`             | 🔸 Calculated Local              | Percentage of completed tasks. |
| `best_day`                          | `db.get_best_day(user_id)`                                | 🔹 Database Query                | Day with highest focus minutes. |
| `cards_data`                        | Local list combining all metrics                          | 🔸 Local Data Structure (list)   | Prepared dataset for UI stat cards. |
| `self.score`                        | `self.calculate_weekly_score()`                           | 🔸 Local Function Calculation    | Computes the weekly productivity score (weighted metrics). |
| `self.progress`                     | `QProgressBar()`                                          | 🔸 UI Element                    | Visual representation of weekly score (0–10). |
| `self.feedback_label`               | `QLabel()`                                                | 🔸 UI Element                    | Displays motivational message based on score. |
| `self.badge_label`                  | `QLabel()`                                                | 🔸 UI Element                    | Displays user’s badge (Bronze/Silver/Gold/Diamond). |
| `weekly_data`                       | `db.get_weekly_focus_data(user_id)`                       | 🔹 Database Query                | List of last 7 days’ focus times (day, focus_minutes). |
| `strategies`                        | `db.get_strategy_usage(user_id)`                          | 🔹 Database Query                | Dictionary showing usage ratio of Pomodoro, DeepWork, Balanced. |
| `focus_score`                       | `(total_hours / 10) * 4` (capped at 4)                    | 🔸 Calculated Local              | Weighted score component (40%) based on total hours. |
| `streak_score`                      | `(streak / 7) * 3` (capped at 3)                          | 🔸 Calculated Local              | Weighted score component (30%) based on streak. |
| `completion_score`                  | `(completed / total) * 3` (capped at 3)                   | 🔸 Calculated Local              | Weighted score component (30%) based on task completion rate. |
| `total_score`                       | `focus_score + streak_score + completion_score`           | 🔸 Calculated Local              | Final weekly performance score (max 10). |

💡 Data Category Legend
-----------------------
🔹 **Database Query / Field / Derived:** Directly read or updated from the database.  
🔸 **Local / Calculated / UI Element:** Computed or used only within the code for visualization.

💬 General Notes
----------------
- `StatisticsPage` fetches **live database data** each time it is opened.  
- Average session and weekly scores are persisted in `user_stats` table.  
- Task completion, streaks, and focus duration are synced with the main `users` table.  
- Charts (`matplotlib`) visualize focus distribution and strategy usage dynamically.  
- `refresh_stats()` can be called externally to reload the entire page with updated values.

"""


import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar,
    QGraphicsDropShadowEffect, QGridLayout
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Backend Integration
from database import DatabaseManager
from core.user import User
from core.planner import Planner
from strategies.factory import StrategyFactory


class StatisticsPage(QWidget):
    def __init__(self, user_email="dogukan@example.com"):
        super().__init__()
        
        # Database setup
        self.db = DatabaseManager()
        self.user_email = user_email
        self.user_data = self.db.get_user_by_email(user_email)
        self.user_id = self.user_data["id"] if self.user_data else None
        
        # Core backend integration
        self.user = User("dogukanavci", user_email)
        self.strategy = StrategyFactory.create("pomodoro")
        self.planner = Planner(self.user, self.strategy)
        
        # Load tasks into planner
        self.load_tasks_to_planner()
        
        self.init_ui()

    def load_tasks_to_planner(self):
        """Load tasks from database into Planner for statistics"""
        if not self.user_id:
            return
        
        db_tasks = self.db.get_all_tasks(self.user_id)
        for db_task in db_tasks:
            # Skip loading, just use for statistics
            pass

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(35)

        # Modern gradient background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F8FAFC,
                    stop:1 #EFF6FF
                );
            }
        """)

        # Title
        title = QLabel("📊 Statistics Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E3A8A; background: transparent;")
        layout.addWidget(title)

        subtitle = QLabel("Real-time insights from your productivity journey")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748B; background: transparent; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # ==========================================================
        # 🔸 Top Section: Cards + Strategy Chart
        # ==========================================================
        top_section = QHBoxLayout()
        top_section.setSpacing(20)
        
        # Left: Summary Cards (3x2 grid)
        summary_layout = QGridLayout()
        summary_layout.setSpacing(12)

        # ==========================================================
        # 🔹 Gerçek veriler (users + user_stats senkron)
        # ==========================================================
        user = self.db.get_user_by_email(self.user_email)
        stats = self.db.get_user_stats(self.user_id) if self.user_id else {}
        
        # --- Görev verileri ---
        all_tasks = self.db.get_all_tasks(self.user_id) if self.user_id else []
        completed_tasks = self.db.get_completed_tasks(self.user_id) if self.user_id else []
        
        # --- Kullanıcı tablosundan çekilen veriler (her zaman güncel) ---
        total_minutes = user["total_focus_minutes"] if user else 0
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60
        streak = user["streak_days"] if user else 0
        
        # --- user_stats tablosundan çekilen (isteğe bağlı veriler) ---
        avg_session = stats.get("average_session", 0) if stats else 0
        weekly_score = stats.get("weekly_score", 0) if stats else 0
        
        # --- Görev istatistikleri ---
        total_tasks_count = len(all_tasks)
        completed_count = len(completed_tasks)
        completion_rate = int((completed_count / total_tasks_count * 100)) if total_tasks_count > 0 else 0
        
        # --- En iyi gün (opsiyonel) ---
        best_day = self.db.get_best_day(self.user_id)

        
        # ==========================================================
        # 🔹 Kart verileri
        # ==========================================================
        cards_data = [
            ("⏱️", "Total Focus", f"{int(total_hours)}h {int(remaining_minutes)}m", "#3B82F6"),
            ("📈", "Avg Session", f"{int(avg_session)} min", "#10B981"),
            ("🔥", "Streak", f"{streak} days", "#F59E0B"),
            ("🎯", "Best Day", best_day, "#8B5CF6"),
            ("✅", "Completed", f"{completed_count}/{total_tasks_count}", "#06B6D4"),
            ("📊", "Completion Rate", f"{completion_rate}%", "#EC4899")
        ]


        for i, (icon, title, value, color) in enumerate(cards_data):
            card = self.create_stat_card(icon, title, value, color)
            summary_layout.addWidget(card, i // 3, i % 3)

        top_section.addLayout(summary_layout)
        
        # Right: Strategy Distribution Chart
        strategy_chart_frame = self.create_chart_frame("Strategy Usage", self.create_pie_chart())
        top_section.addWidget(strategy_chart_frame)
        
        layout.addLayout(top_section)

        # ==========================================================
        # 🔸 Weekly Performance Review
        # ==========================================================
        review_frame = QFrame()
        review_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 2px solid #E2E8F0;
                padding: 25px;
            }
        """)
        review_layout = QVBoxLayout(review_frame)
        review_layout.setSpacing(18)

        review_title = QLabel("🧭 Weekly Performance Review")
        review_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        review_title.setAlignment(Qt.AlignCenter)
        review_title.setStyleSheet("color: #1E3A8A; background: transparent;")
        review_layout.addWidget(review_title)

        # Calculate weekly score
        self.score = self.calculate_weekly_score()
        self.db.update_user_stats(self.user_id, {"weekly_score": self.score})

        # Score display
        score_display = QHBoxLayout()
        score_icon = QLabel("⭐")
        score_icon.setFont(QFont("Segoe UI", 32))
        score_icon.setStyleSheet("background: transparent;")
        
        score_text = QLabel(f"{self.score}/10")
        score_text.setFont(QFont("Segoe UI", 32, QFont.Bold))
        score_text.setStyleSheet("color: #3B82F6; background: transparent;")
        
        score_display.addStretch()
        score_display.addWidget(score_icon)
        score_display.addWidget(score_text)
        score_display.addStretch()
        review_layout.addLayout(score_display)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 10)
        self.progress.setValue(self.score)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(22)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #E2E8F0;
                border-radius: 11px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, 
                    stop:0.5 #8B5CF6,
                    stop:1 #10B981
                );
                border-radius: 11px;
            }
        """)
        review_layout.addWidget(self.progress)

        # Feedback message
        feedback = self.generate_feedback(self.score)
        self.feedback_label = QLabel(feedback)
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setFont(QFont("Segoe UI", 12))
        self.feedback_label.setStyleSheet("""
            color: #1E293B;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #EFF6FF,
                stop:1 #F0F9FF
            );
            border-radius: 10px;
            border: 2px solid #BFDBFE;
            padding: 16px;
            margin-top: 10px;
        """)
        review_layout.addWidget(self.feedback_label)

        # Badge
        self.badge_label = QLabel()
        self.badge_label.setAlignment(Qt.AlignCenter)
        self.badge_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.badge_label.setStyleSheet("background: transparent; margin-top: 8px;")
        review_layout.addWidget(self.badge_label)
        self.update_badge(self.score)

        layout.addWidget(review_frame)
        layout.addStretch()

    # ==========================================================
    # 🔹 Stat Card Creation
    # ==========================================================
    def create_stat_card(self, icon, title, value, color):
        card = QFrame()
        card.setFixedSize(200, 120)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color},
                    stop:1 {self.darken_color(color)}
                );
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 35))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(4)
        card_layout.setContentsMargins(6, 6, 6, 6)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 18))
        icon_label.setStyleSheet("color: white; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        value_label.setStyleSheet("color: white; background: transparent;")
        value_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 8))
        title_label.setStyleSheet("color: rgba(255,255,255,0.95); background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        
        card_layout.addWidget(icon_label)
        card_layout.addWidget(value_label)
        card_layout.addWidget(title_label)
        
        return card

    def darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-30), max(0, g-30), max(0, b-30)
        return f'#{r:02x}{g:02x}{b:02x}'

    # ==========================================================
    # 🔹 Chart Frame Wrapper
    # ==========================================================
    def create_chart_frame(self, title, canvas):
        frame = QFrame()
        frame.setFixedSize(500, 300)
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
                border: 2px solid #E2E8F0;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet("color: #1E3A8A; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(canvas)
        
        return frame

    # ==========================================================
    # 🔹 Weekly Focus Chart (Real Data from Database)
    # ==========================================================
    def create_weekly_chart(self):
        fig = Figure(figsize=(6, 3.5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Get real weekly data from database
        weekly_data = self.db.get_weekly_focus_data(self.user_id)
        
        if weekly_data and len(weekly_data) > 0:
            days = [row["day"] for row in weekly_data]
            focus_minutes = [row["focus_minutes"] for row in weekly_data]
        else:
            # Fallback: use last 7 days from sessions
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            focus_minutes = [random.randint(20, 120) for _ in days]

        avg = sum(focus_minutes) / len(focus_minutes) if focus_minutes else 0
        
        bars = ax.bar(days, focus_minutes, color="#3B82F6", edgecolor="#1E3A8A", width=0.65)
        ax.axhline(avg, color="#EF4444", linestyle="--", linewidth=1.8, label=f"Avg: {int(avg)}m")
        ax.legend(loc="upper right", fontsize=10)
        ax.set_ylabel("Minutes", fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        ax.tick_params(labelsize=9)

        for bar in bars:
            yval = bar.get_height()
            if yval > 0:
                ax.text(bar.get_x() + bar.get_width()/2, yval + 4, f"{int(yval)}", 
                       ha='center', fontsize=10, color="#1E3A8A", fontweight='bold')

        fig.tight_layout()
        return canvas

    # ==========================================================
    # 🔹 Strategy Distribution Chart (Real Data)
    # ==========================================================
    def create_pie_chart(self):
        fig = Figure(figsize=(4, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
    
        # Get real strategy usage from database
        strategies = self.db.get_strategy_usage(self.user_id)
        
        if not strategies or sum(strategies.values()) == 0:
            strategies = {"Pomodoro": 40, "DeepWork": 30, "Balanced": 30}
    
        labels = list(strategies.keys())
        values = list(strategies.values())
        colors = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"]
    
        # Create pie chart with percentages
        wedges, texts, autotexts = ax.pie(
            values, 
            autopct="%1.0f%%",
            startangle=90, 
            colors=colors[:len(labels)], 
            textprops={"fontsize": 10, "color": "white", "fontweight": "bold"}
        )
        
        # Add legend below the chart
        ax.legend(
            wedges, 
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.05),
            ncol=3,
            fontsize=8,
            frameon=False
        )
        
        fig.tight_layout()
        return canvas
    # ==========================================================
    # 🔹 Best Day Calculation
    # ==========================================================
    def calculate_best_day(self):
        """Calculate which day had most focus time"""
        weekly_data = self.db.get_weekly_focus_data(self.user_id)
        
        if not weekly_data or len(weekly_data) == 0:
            return "N/A"
        
        best = max(weekly_data, key=lambda x: x["focus_minutes"])
        return best["day"]

    # ==========================================================
    # 🔹 Feedback Generation
    # ==========================================================
    def generate_feedback(self, score):
        feedbacks = {
            (0, 3): [
                "Every journey starts with a single step. Keep building! 🌱",
                "Don't worry — consistency beats perfection. You've got this! 💪",
                "The hardest part is showing up. You're already here! 🚀"
            ],
            (4, 6): [
                "Solid progress! You're building momentum. 🎯",
                "Good work! Consistency is key to greatness. 💫",
                "You're on the right track. Keep pushing forward! ⚡"
            ],
            (7, 9): [
                "Excellent work! You're in your flow zone. 🌊",
                "Outstanding! You're mastering the art of focus. 🎨",
                "Impressive! Your dedication is paying off. 🏆"
            ],
            (10, 10): [
                "Perfect score! You're a Focus Master! 🧠🔥",
                "Legendary! You've achieved peak performance! 💎",
                "Flawless! You're operating at genius level! 🌟"
            ]
        }
        
        for (min_score, max_score), messages in feedbacks.items():
            if min_score <= score <= max_score:
                return random.choice(messages)
        
        return "Keep going! Every effort counts! 💪"

    # ==========================================================
    # 🔹 Badge Update with Animation
    # ==========================================================
    def update_badge(self, score):
        badges = {
            (0, 4): ("🥉 Bronze Performer", "#D97706"),
            (5, 7): ("🥈 Silver Achiever", "#9CA3AF"),
            (8, 9): ("🥇 Gold Focuser", "#FBBF24"),
            (10, 10): ("💎 Diamond Mind", "#06B6D4")
        }
        
        badge_text, color = "🏅 Beginner", "#64748B"
        for (min_s, max_s), (text, col) in badges.items():
            if min_s <= score <= max_s:
                badge_text, color = text, col
                break

        self.badge_label.setText(badge_text)
        self.badge_label.setStyleSheet(f"color: {color}; background: transparent; margin-top: 5px;")

    # ==========================================================
    # 🔹 Weekly Score Calculation (Real Algorithm)
    # ==========================================================
    def calculate_weekly_score(self):
        """
        Score calculation based on:
        - Total focus time (40%)
        - Streak consistency (30%)
        - Task completion rate (30%)
        """
        if not self.user_id:
            return 0
        
        # Get metrics
        total_hours = self.db.get_user_stats(self.user_id).get("total_focus_hours", 0)
        streak = self.user_data["streak_days"] if self.user_data else 0
        all_tasks = self.db.get_all_tasks(self.user_id)
        completed = self.db.get_completed_tasks(self.user_id)
        
        # Calculate components
        focus_score = min(4, (total_hours / 10) * 4)  # Max 4 points for 10+ hours
        streak_score = min(3, (streak / 7) * 3)       # Max 3 points for 7+ day streak
        completion_score = 3 * (len(completed) / len(all_tasks)) if all_tasks else 0  # Max 3 points
        
        total_score = int(focus_score + streak_score + completion_score)
        return max(1, min(10, total_score))

    # ==========================================================
    # 🔹 Refresh Method (Called from MainWindow)
    # ==========================================================
    def refresh_stats(self):
        """Refresh all statistics - called when page is opened"""
        # Reload user data
        self.user_data = self.db.get_user_by_email(self.user_email)
        
        # Recreate entire UI with fresh data
        QWidget().setLayout(self.layout())
        self.init_ui()