# -*- coding: utf-8 -*-
"""
database.py
====================
SQLite tabanlı veritabanı yöneticisi.

Bu modül, Smart Study Planner uygulamasındaki tüm verilerin kalıcı olarak 
saklanmasını sağlar. Aşağıdaki ana tabloları içerir:

- users: Kullanıcı bilgileri, streak, toplam odak süresi, başarımlar
- tasks: Kullanıcının görevleri
- sessions: Odak oturum geçmişleri
- user_stats: Kullanıcıya özel istatistik kayıtları (haftalık skor, streak, vb.)
- strategy_usage: Strateji kullanım yüzdeleri

Tüm fonksiyonlar context manager yapısı (with get_connection()) ile güvenli çalışır.
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager

# ============================================================
# 🔹 Database Path
# ============================================================
DB_NAME = "study_planner.db"


# ============================================================
# 🔹 Safe Connection Manager
# ============================================================
@contextmanager
def get_connection():
    """Veritabanına güvenli bağlantı (otomatik commit/rollback)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()


# ============================================================
# 🔹 DatabaseManager Class
# ============================================================
class DatabaseManager:
    """Smart Study Planner için tüm CRUD işlemlerini yöneten ana sınıf."""

    def __init__(self):
        self.initialize_database()

    # ------------------------------------------------------------
    # 🧱 TABLE CREATION
    # ------------------------------------------------------------
    def initialize_database(self):
        """Tüm tabloları oluşturur (varsa atlar)."""
        with get_connection() as conn:
            c = conn.cursor()

            # 🔸 USERS TABLOSU
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    streak_days INTEGER DEFAULT 0,
                    total_focus_minutes INTEGER DEFAULT 0,
                    tasks_completed INTEGER DEFAULT 0,
                    weekly_productivity_score REAL DEFAULT 0.0,
                    last_active_date TEXT,
                    achievements TEXT DEFAULT ''
                )
            """)

            # 🔸 TASKS TABLOSU
            c.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    priority INTEGER,
                    deadline TEXT,
                    duration INTEGER,
                    status TEXT DEFAULT 'pending',
                    strategy TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 🔸 SESSIONS TABLOSU
            c.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    strategy TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)

            # 🔸 USER_STATS TABLOSU
            c.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    total_focus_hours REAL DEFAULT 0,
                    average_session REAL DEFAULT 0,
                    best_day TEXT DEFAULT 'N/A',
                    streak INTEGER DEFAULT 0,
                    weekly_score INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 🔸 WEEKLY_FOCUS TABLOSU
            c.execute("""
                CREATE TABLE IF NOT EXISTS weekly_focus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    day TEXT,
                    focus_minutes INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 🔸 STRATEGY_USAGE TABLOSU
            c.execute("""
                CREATE TABLE IF NOT EXISTS strategy_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    strategy TEXT,
                    usage_percent REAL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 🔸 DAILY_FOCUS TABLOSU
            c.execute("""
                CREATE TABLE IF NOT EXISTS daily_focus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date TEXT,
                    focus_minutes INTEGER DEFAULT 0,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            print("✅ Database initialized successfully.")

    # ------------------------------------------------------------
    # 👤 USER OPERATIONS
    # ------------------------------------------------------------
    def add_user(self, username: str, email: str):
        """Yeni kullanıcı ekler (email varsa var olanı döner)."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = c.fetchone()
            if user:
                return user["id"]
            c.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
            user_id = c.lastrowid
            c.execute("INSERT INTO user_stats (user_id) VALUES (?)", (user_id,))
            return user_id

    def get_user_by_email(self, email: str):
        """Email'e göre kullanıcıyı döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            return c.fetchone()

    # ------------------------------------------------------------
    # 🔹 USER STATISTICS & STREAKS
    # ------------------------------------------------------------
    def update_streak(self, user_id: int, new_date: str):
        """Kullanıcının günlük streak'ini kontrol eder ve günceller."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT last_active_date, streak_days FROM users WHERE id = ?", (user_id,))
            row = c.fetchone()
            if not row:
                return
            last_date = row["last_active_date"]
            streak = row["streak_days"]
            if last_date:
                try:
                    diff = (datetime.fromisoformat(new_date) - datetime.fromisoformat(last_date)).days
                    if diff == 1:
                        streak += 1
                    elif diff > 1:
                        streak = 1
                except ValueError:
                    streak = 1
            else:
                streak = 1
            c.execute("""
                UPDATE users
                SET streak_days = ?, last_active_date = ?
                WHERE id = ?
            """, (streak, new_date, user_id))
            c.execute("UPDATE user_stats SET streak=? WHERE user_id=?", (streak, user_id))

    

    def update_weekly_score(self, user_id: int, score: float):
        """Kullanıcının haftalık üretkenlik skorunu günceller."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE users
                SET weekly_productivity_score = ?
                WHERE id = ?
            """, (score, user_id))
            c.execute("""
                UPDATE user_stats
                SET weekly_score = ?
                WHERE user_id = ?
            """, (score, user_id))

    def add_achievement(self, user_id: int, achievement: str):
        """Yeni bir başarıyı kullanıcıya ekler."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT achievements FROM users WHERE id = ?", (user_id,))
            row = c.fetchone()
            if not row:
                return
            achievements = row["achievements"].split(",") if row["achievements"] else []
            if achievement not in achievements:
                achievements.append(achievement)
                c.execute("UPDATE users SET achievements = ? WHERE id = ?",
                          (",".join(achievements), user_id))

    # ------------------------------------------------------------
    # ✅ TASK OPERATIONS
    # ------------------------------------------------------------
    def add_task(self, user_id: int, title: str, priority: int, deadline: str,
                 duration: int, strategy: str, status: str = "pending"):
        """Yeni görev ekler."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO tasks (user_id, title, priority, deadline, duration, status, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, title, priority, deadline, duration, status, strategy))
            return c.lastrowid

    def get_all_tasks(self, user_id: int):
        """Kullanıcının tüm görevlerini döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
            return c.fetchall()

    def update_task_status(self, task_id: int, new_status: str):
        """Görev durumunu günceller."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
            return c.rowcount

    def delete_task(self, task_id: int):
        """Görevi siler."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return c.rowcount

    # ------------------------------------------------------------
    # ⏱️ SESSION OPERATIONS
    # ------------------------------------------------------------
    def log_session(self, task_id: int, strategy: str, start_time: datetime,
                    end_time: datetime, duration: int):
        """Odak oturumunu kaydeder."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO sessions (task_id, strategy, start_time, end_time, duration)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, strategy, start_time.isoformat(), end_time.isoformat(), duration))
            return c.lastrowid

    def get_sessions_for_task(self, task_id: int):
        """Belirli bir görevin tüm oturumlarını döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM sessions WHERE task_id = ?", (task_id,))
            return c.fetchall()

    # ------------------------------------------------------------
    # 📊 STATISTICS OPERATIONS (for StatisticsPage)
    # ------------------------------------------------------------
    def add_focus_minutes(self, user_id: int, minutes: int):
        """Toplam odak süresine dakika ekler ve daily_focus tablosuna işler."""
        from datetime import date
        today = date.today().isoformat()
    
        with get_connection() as conn:
            c = conn.cursor()
    
            # 🔹 USERS tablosundaki toplam süreyi güncelle
            c.execute("""
                UPDATE users
                SET total_focus_minutes = total_focus_minutes + ?
                WHERE id = ?
            """, (minutes, user_id))
    
            # 🔹 USER_STATS tablosundaki toplam saati güncelle
            c.execute("""
                UPDATE user_stats
                SET total_focus_hours = total_focus_hours + (? / 60.0)
                WHERE user_id = ?
            """, (minutes, user_id))
    
            # 🔹 DAILY_FOCUS tablosuna bugünün kaydını ekle/güncelle
            c.execute("""
                INSERT INTO daily_focus (user_id, date, focus_minutes)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, date)
                DO UPDATE SET
                    focus_minutes = focus_minutes + excluded.focus_minutes
            """, (user_id, today, minutes))
    
            conn.commit()

    
    def get_user_stats(self, user_id: int):
        """Kullanıcının user_stats kaydını döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM user_stats WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if not row:
                return {"total_focus_minutes": 0, "average_session": 0, "best_day": "N/A", "streak": 0, "weekly_score": 0}
            return dict(row)

    def add_daily_focus(self, user_id: int, minutes: int):
        """Günlük odak süresine dakika ekler."""
        from datetime import date
        today = date.today().isoformat()
        with get_connection() as conn:
            c = conn.cursor()
            # Eğer kayıt varsa ekle, yoksa oluştur
            c.execute("""
                INSERT INTO daily_focus (user_id, date, focus_minutes)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET
                focus_minutes = focus_minutes + excluded.focus_minutes
            """, (user_id, today, minutes))
            conn.commit()
    
    def get_best_day(self, user_id: int):
        """En çok odaklanılan günü döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT date, focus_minutes
                FROM daily_focus
                WHERE user_id = ?
                ORDER BY focus_minutes DESC
                LIMIT 1
            """, (user_id,))
            row = c.fetchone()
            if row:
                return row["date"]
            return "N/A"


    def update_user_stats(self, user_id: int, data: dict):
        """Belirli alanları günceller."""
        with get_connection() as conn:
            c = conn.cursor()
            for key, value in data.items():
                c.execute(f"UPDATE user_stats SET {key}=? WHERE user_id=?", (value, user_id))
    
    def update_average_session(self, user_id: int):
        """Kullanıcının ortalama oturum süresini (dakika cinsinden) günceller."""
        with get_connection() as conn:
            c = conn.cursor()
            # Kullanıcının session kayıtlarından ortalama süreyi hesapla
            c.execute("""
                SELECT AVG(duration) AS avg_duration
                FROM sessions
                WHERE task_id IN (
                    SELECT id FROM tasks WHERE user_id = ?
                )
            """, (user_id,))
            row = c.fetchone()
            avg_duration = row["avg_duration"] if row and row["avg_duration"] else 0
    
            # user_stats tablosunu güncelle
            c.execute("""
                UPDATE user_stats
                SET average_session = ?
                WHERE user_id = ?
            """, (avg_duration, user_id))
            conn.commit()
    
            print(f"✅ Updated average session for user {user_id}: {avg_duration:.2f} minutes")

            
    
    def get_weekly_focus_data(self, user_id: int):
        """Haftalık odak verilerini döndürür (gün, dakika)."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT day, focus_minutes FROM weekly_focus
                WHERE user_id=? ORDER BY id ASC
            """, (user_id,))
            return c.fetchall()

    def get_strategy_usage(self, user_id: int):
        """Strateji kullanım oranlarını döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT strategy, usage_percent FROM strategy_usage WHERE user_id=?", (user_id,))
            data = c.fetchall()
            return {k["strategy"]: k["usage_percent"] for k in data} if data else {}
        
    def get_completed_tasks(self, user_id: int):
        """Tamamlanan (status='done') görevleri döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM tasks
                WHERE user_id = ? AND status = 'done'
                ORDER BY deadline DESC
            """, (user_id,))
            return c.fetchall()

    def get_task_by_id(self, task_id: int):
        """Tek bir görevi ID'ye göre döndürür."""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            return c.fetchone()
