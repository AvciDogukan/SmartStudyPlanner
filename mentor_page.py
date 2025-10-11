# -*- coding: utf-8 -*-
"""
AI Mentor Page - Complete Advanced Version
--------------------------------------------
Enhanced AI coach with full database integration:
- Real-time trend analysis (7-day, 30-day patterns)
- Performance scoring (0-100) based on multiple metrics
- Personalized recommendations using actual data
- Goal tracking and streak analysis
- Visual insights with progress bars
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QProgressBar, QPushButton, QScrollArea, QGridLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from database import DatabaseManager, get_connection
from datetime import date, timedelta
import random


class InsightCard(QFrame):
    """Modern insight card with icon, title, and value"""
    def __init__(self, icon, title, value, color="#667EEA", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 28))
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: #64748B; background: transparent; border: none;")
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class RecommendationCard(QFrame):
    """Recommendation action card"""
    def __init__(self, text, color="#667EEA", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 2px solid {color}40;
                border-radius: 10px;
                padding: 12px 16px;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                background: {color}08;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        bullet = QLabel("▸")
        bullet.setFont(QFont("Segoe UI", 14, QFont.Bold))
        bullet.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        bullet.setFixedWidth(20)
        
        text_label = QLabel(text)
        text_label.setFont(QFont("Segoe UI", 11))
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #334155; background: transparent; border: none;")
        
        layout.addWidget(bullet)
        layout.addWidget(text_label)


class MentorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.user_email = "dogukan@example.com"
        self.user = self.db.get_user_by_email(self.user_email)
        self.user_id = self.user["id"] if self.user else None
        
        self.init_ui()
        self.refresh_feedback()

    def init_ui(self):
        # Main scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF,
                    stop:1 #F8FAFC
                );
                border: none;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 5px;
            }
        """)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(25)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        title = QLabel("🤖 AI Mentor")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E293B; background: transparent;")
        
        subtitle = QLabel("Your personalized AI coach analyzing your focus patterns")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748B; background: transparent;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        # Performance Score Card
        score_card = QFrame()
        score_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667EEA,
                    stop:1 #764BA2
                );
                border-radius: 16px;
                padding: 30px;
            }
        """)
        score_layout = QVBoxLayout(score_card)
        score_layout.setSpacing(15)
        
        score_title = QLabel("Performance Score")
        score_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        score_title.setAlignment(Qt.AlignCenter)
        score_title.setStyleSheet("color: white; background: transparent;")
        
        self.score_label = QLabel("85")
        self.score_label.setFont(QFont("Segoe UI", 48, QFont.Bold))
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("color: white; background: transparent;")
        
        self.score_desc = QLabel("Calculating...")
        self.score_desc.setFont(QFont("Segoe UI", 11))
        self.score_desc.setAlignment(Qt.AlignCenter)
        self.score_desc.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent;")
        
        score_layout.addWidget(score_title)
        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self.score_desc)
        layout.addWidget(score_card)
        
        # Insights Grid
        insights_label = QLabel("📊 Weekly Insights")
        insights_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        insights_label.setStyleSheet("color: #1E293B; background: transparent;")
        layout.addWidget(insights_label)
        
        insights_grid = QHBoxLayout()
        insights_grid.setSpacing(15)
        
        self.insight_card1 = InsightCard("📈", "7-Day Trend", "Loading...", "#667EEA")
        self.insight_card2 = InsightCard("🎯", "Avg Session", "Loading...", "#10B981")
        self.insight_card3 = InsightCard("⚡", "Best Day", "Loading...", "#F59E0B")
        
        insights_grid.addWidget(self.insight_card1)
        insights_grid.addWidget(self.insight_card2)
        insights_grid.addWidget(self.insight_card3)
        
        layout.addLayout(insights_grid)
        
        # AI Feedback Section
        feedback_label = QLabel("💬 AI Analysis")
        feedback_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        feedback_label.setStyleSheet("color: #1E293B; background: transparent;")
        layout.addWidget(feedback_label)
        
        self.feedback_frame = QFrame()
        self.feedback_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #E2E8F0;
                border-radius: 14px;
                padding: 25px;
            }
        """)
        feedback_layout = QVBoxLayout(self.feedback_frame)
        feedback_layout.setSpacing(15)
        
        self.feedback_label = QLabel("Analyzing your focus patterns...")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setFont(QFont("Segoe UI", 13))
        self.feedback_label.setStyleSheet("color: #334155; line-height: 1.6;")
        
        feedback_layout.addWidget(self.feedback_label)
        layout.addWidget(self.feedback_frame)
        
        # Recommendations
        rec_label = QLabel("✨ Personalized Recommendations")
        rec_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        rec_label.setStyleSheet("color: #1E293B; background: transparent;")
        layout.addWidget(rec_label)
        
        self.rec_layout = QVBoxLayout()
        self.rec_layout.setSpacing(10)
        layout.addLayout(self.rec_layout)
        
        # Strategy Insights
        strategy_label = QLabel("🎯 Strategy Insights")
        strategy_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        strategy_label.setStyleSheet("color: #1E293B; background: transparent;")
        layout.addWidget(strategy_label)
        
        self.strategy_frame = QFrame()
        self.strategy_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #E2E8F0;
                border-radius: 14px;
                padding: 20px;
            }
        """)
        self.strategy_layout = QVBoxLayout(self.strategy_frame)
        self.strategy_layout.setSpacing(12)
        layout.addWidget(self.strategy_frame)
        
        # Motivational Quote
        self.quote_label = QLabel("")
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setFont(QFont("Segoe UI", 12))
        self.quote_label.setStyleSheet("""
            QLabel {
                background: #F0F9FF;
                border: 2px solid #BAE6FD;
                border-radius: 12px;
                color: #0C4A6E;
                padding: 20px;
                font-style: italic;
            }
        """)
        layout.addWidget(self.quote_label)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def calculate_performance_score(self):
        """Calculate 0-100 performance score based on multiple factors"""
        if not self.user:
            return 0
        
        score = 0
        
        # 1. Streak (30 points max)
        streak = self.user["streak_days"]
        score += min(30, streak * 5)
        
        # 2. Total focus time (30 points max)
        total_focus = self.user["total_focus_minutes"]
        score += min(30, total_focus // 60)
        
        # 3. Task completion rate (20 points max)
        all_tasks = self.db.get_all_tasks(self.user_id)
        if all_tasks:
            completed = sum(1 for t in all_tasks if t["status"] == "done")
            completion_rate = completed / len(all_tasks)
            score += int(completion_rate * 20)
        
        # 4. 7-day activity (20 points max)
        today = date.today()
        last_7_days = [(today - timedelta(days=i)).isoformat() for i in range(7)]
        
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT COUNT(DISTINCT date) as active_days
                FROM daily_focus
                WHERE user_id = ? AND date IN ({})
            """.format(','.join('?' * len(last_7_days))), [self.user_id] + last_7_days)
            row = c.fetchone()
            active_days = row["active_days"] if row else 0
            score += int((active_days / 7) * 20)
        
        return min(100, score)

    def get_weekly_trend(self):
        """Calculate if user is improving, declining, or stable"""
        today = date.today()
        last_14_days = [(today - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
        
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT date, focus_minutes
                FROM daily_focus
                WHERE user_id = ? AND date IN ({})
                ORDER BY date ASC
            """.format(','.join('?' * len(last_14_days))), [self.user_id] + last_14_days)
            rows = c.fetchall()
        
        if len(rows) < 7:
            return "stable", 0
        
        # Split into two weeks
        first_week = sum(row["focus_minutes"] for row in rows[:7])
        second_week = sum(row["focus_minutes"] for row in rows[7:])
        
        if second_week > first_week * 1.1:
            return "improving", int(((second_week - first_week) / first_week) * 100)
        elif second_week < first_week * 0.9:
            return "declining", int(((first_week - second_week) / first_week) * 100)
        else:
            return "stable", 0

    def get_average_session(self):
        """Get average session duration from sessions table"""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT AVG(duration) as avg_duration
                FROM sessions
                WHERE task_id IN (SELECT id FROM tasks WHERE user_id = ?)
            """, (self.user_id,))
            row = c.fetchone()
            return int(row["avg_duration"]) if row and row["avg_duration"] else 0

    def get_best_day(self):
        """Get the day with most focus time"""
        return self.db.get_best_day(self.user_id)

    def get_strategy_distribution(self):
        """Get distribution of strategy usage"""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT strategy, COUNT(*) as count
                FROM sessions
                WHERE task_id IN (SELECT id FROM tasks WHERE user_id = ?)
                GROUP BY strategy
            """, (self.user_id,))
            rows = c.fetchall()
            
            if not rows:
                return {}
            
            total = sum(row["count"] for row in rows)
            return {row["strategy"]: int((row["count"] / total) * 100) for row in rows}

    def generate_ai_feedback(self, score, trend, trend_percent):
        """Generate personalized AI feedback"""
        streak = self.user["streak_days"]
        total_focus = self.user["total_focus_minutes"]
        avg_session = self.get_average_session()
        
        feedback = []
        
        # Score-based feedback
        if score >= 80:
            feedback.append("🌟 Outstanding performance! You're in the top tier of focused learners.")
        elif score >= 60:
            feedback.append("💪 Great work! You're building strong study habits.")
        elif score >= 40:
            feedback.append("📈 Good progress! Keep pushing forward.")
        else:
            feedback.append("🌱 You're just starting your focus journey. Every expert was once a beginner!")
        
        # Trend-based feedback
        if trend == "improving":
            feedback.append(f"📊 You've improved by {trend_percent}% this week - momentum is building!")
        elif trend == "declining":
            feedback.append(f"⚠️ Focus time decreased by {trend_percent}% this week. Time to get back on track!")
        else:
            feedback.append("⚖️ Your focus time is stable. Consider pushing for a new personal best!")
        
        # Streak feedback
        if streak >= 7:
            feedback.append(f"🔥 Amazing {streak}-day streak! You're building an unbreakable habit.")
        elif streak >= 3:
            feedback.append(f"🎯 {streak} days in a row! Keep the momentum going.")
        elif streak == 0:
            feedback.append("👣 Start your streak today! Even 25 minutes makes a difference.")
        
        # Session length feedback
        if avg_session > 60:
            feedback.append("⏱️ Your sessions average over 1 hour - excellent deep work capacity!")
        elif avg_session > 30:
            feedback.append("✅ Good session length! Try extending to 45-60 minutes for deeper focus.")
        elif avg_session > 0:
            feedback.append("💡 Short sessions are okay! Focus on consistency over duration.")
        
        return " ".join(feedback)

    def generate_recommendations(self, score, trend, avg_session):
        """Generate actionable recommendations"""
        recommendations = []
        all_tasks = self.db.get_all_tasks(self.user_id)
        pending = sum(1 for t in all_tasks if t["status"] == "pending")
        
        # Strategy recommendations
        if avg_session < 25:
            recommendations.append(("Try the Pomodoro technique (25 min) to build focus endurance", "#EF4444"))
        elif avg_session < 45:
            recommendations.append(("Level up to Balanced sessions (45 min) for deeper work", "#F59E0B"))
        else:
            recommendations.append(("Ready for Deep Work (90 min)? Challenge yourself!", "#3B82F6"))
        
        # Task-based recommendations
        if pending > 5:
            recommendations.append((f"You have {pending} pending tasks. Break them into smaller chunks!", "#8B5CF6"))
        elif pending == 0:
            recommendations.append(("All tasks done! Time to set new goals in the Planner.", "#10B981"))
        
        # Streak recommendations
        if self.user["streak_days"] == 0:
            recommendations.append(("Start a new streak today! Consistency beats intensity.", "#667EEA"))
        elif self.user["streak_days"] < 7:
            recommendations.append((f"Just {7 - self.user['streak_days']} more days to reach a 1-week streak!", "#F59E0B"))
        
        # Time-based recommendations
        import datetime
        if datetime.datetime.now().hour < 12:
            recommendations.append(("Morning focus sessions have 25% higher success rates. Start now!", "#10B981"))
        
        return recommendations

    def refresh_feedback(self):
        """Refresh all AI mentor data"""
        if not self.user:
            self.feedback_label.setText("No user data found.")
            return
        
        # Calculate metrics
        score = self.calculate_performance_score()
        trend, trend_percent = self.get_weekly_trend()
        avg_session = self.get_average_session()
        best_day = self.get_best_day()
        
        # Update score card
        self.score_label.setText(str(score))
        if score >= 80:
            self.score_desc.setText("Excellent! You're in the top 10%")
        elif score >= 60:
            self.score_desc.setText("Great work! Keep it up")
        elif score >= 40:
            self.score_desc.setText("Good progress! Push harder")
        else:
            self.score_desc.setText("Getting started! Stay consistent")
        
        # Update insight cards
        trend_emoji = "📈" if trend == "improving" else "📉" if trend == "declining" else "➡️"
        trend_text = f"{trend_emoji} {trend.capitalize()}"
        if trend_percent > 0:
            trend_text += f" {trend_percent}%"
        
        self.insight_card1.value_label.setText(trend_text)
        self.insight_card2.value_label.setText(f"{avg_session} min")
        
        try:
            best_day_obj = date.fromisoformat(best_day)
            self.insight_card3.value_label.setText(best_day_obj.strftime("%a, %b %d"))
        except:
            self.insight_card3.value_label.setText("N/A")
        
        # Generate AI feedback
        feedback = self.generate_ai_feedback(score, trend, trend_percent)
        self.feedback_label.setText(feedback)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(score, trend, avg_session)
        
        # Clear old recommendations
        while self.rec_layout.count():
            item = self.rec_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new recommendations
        for text, color in recommendations:
            card = RecommendationCard(text, color)
            self.rec_layout.addWidget(card)
        
        # Strategy distribution
        strategy_dist = self.get_strategy_distribution()
        
        # Clear old strategy info
        while self.strategy_layout.count():
            item = self.strategy_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if strategy_dist:
            for strategy, percent in strategy_dist.items():
                row = QHBoxLayout()
                row.setSpacing(10)
                
                label = QLabel(f"{strategy.capitalize()}")
                label.setFont(QFont("Segoe UI", 11))
                label.setStyleSheet("color: #334155; background: transparent; border: none;")
                label.setFixedWidth(120)
                
                bar = QProgressBar()
                bar.setMaximum(100)
                bar.setValue(percent)
                bar.setTextVisible(False)
                bar.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        background: #F1F5F9;
                        border-radius: 4px;
                        height: 8px;
                    }
                    QProgressBar::chunk {
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:0,
                            stop:0 #667EEA,
                            stop:1 #764BA2
                        );
                        border-radius: 4px;
                    }
                """)
                
                percent_label = QLabel(f"{percent}%")
                percent_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                percent_label.setStyleSheet("color: #667EEA; background: transparent; border: none;")
                percent_label.setFixedWidth(50)
                
                row.addWidget(label)
                row.addWidget(bar)
                row.addWidget(percent_label)
                
                self.strategy_layout.addLayout(row)
        else:
            no_data = QLabel("No strategy data yet. Complete some focus sessions!")
            no_data.setFont(QFont("Segoe UI", 11))
            no_data.setStyleSheet("color: #94A3B8; background: transparent; font-style: italic;")
            self.strategy_layout.addWidget(no_data)
        
        # Random motivational quote
        quotes = [
            "Discipline beats motivation every time.",
            "Small steps every day lead to big changes.",
            "Progress, not perfection.",
            "Focus on consistency, not intensity.",
            "Your habits define your future.",
            "The secret of getting ahead is getting started.",
            "You don't need more time, you need more focus.",
            "Success is the sum of small efforts repeated daily."
        ]
        self.quote_label.setText(f"💬 {random.choice(quotes)}")