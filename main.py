# -*- coding: utf-8 -*-
"""
Main Entry Point
================

This script serves as the entry point for the Smart Study Planner system.

It demonstrates:
- Creation of a User and Task objects
- Dynamic injection of different Study Strategies (Pomodoro, DeepWork, Balanced)
- Planner operations (add, filter, sort, execute)

Author:
    Doğukan Avcı

Created:
    2025-10-06
"""

from core.user import User
from core.task import Task
from strategies.pomodoro_strategy import PomodoroStrategy
from strategies.deepwork_strategy import DeepWorkStrategy
from strategies.balanced_strategy import BalancedStrategy
from core.planner import Planner
from datetime import datetime


def main():
    """Simulate usage of the Smart Study Planner system."""

    print("📘 SMART STUDY PLANNER INITIALIZING...\n")

    # ----- 1️⃣ Create User -----
    user = User(username="dogukanavci", email="dogukan@example.com")
    print(f"👤 User created: {user.get_username()} ({user.get_email()})")

    # ----- 2️⃣ Create Tasks -----
    task1 = Task(taskid=1, priority=1, title="Finish AI homework",
                 deadline=datetime(2025, 10, 10), duration=120, status="pending")
    task2 = Task(taskid=2, priority=2, title="Prepare TEKNOFEST presentation",
                 deadline=datetime(2025, 10, 12), duration=180, status="pending")
    task3 = Task(taskid=3, priority=3, title="Update portfolio website",
                 deadline=datetime(2025, 10, 14), duration=90, status="done")

    # ----- 3️⃣ Choose Strategy (Dependency Injection) -----
    # Try different options here 👇
    strategy = PomodoroStrategy()
    # strategy = DeepWorkStrategy()
    # strategy = BalancedStrategy()

    # ----- 4️⃣ Create Planner -----
    planner = Planner(user=user, strategy=strategy, tasks=[task1, task2, task3])
    print(f"\n🧩 Planner initialized with {len(planner.get_tasks())} tasks.")

    # ----- 5️⃣ Task Operations -----
    print("\n📋 TASK OVERVIEW")
    for t in planner.get_tasks():
        print(f"- {t.get_title()} (Status: {t.get_status()}, Priority: {t.get_priority()})")

    stats = planner.show_stats()
    print(f"\n📊 Task Stats → Done: {stats['done']} | Pending: {stats['pending']}")

    # ----- 6️⃣ Apply Strategy -----
    print("\n🚀 Starting Study Session:")
    planner.execute_strategy()

    # ----- 7️⃣ Filter Example -----
    pending_tasks = planner.filter_tasks("pending")
    print(f"\n🕒 Pending Tasks: {[t.get_title() for t in pending_tasks]}")

    # ----- 8️⃣ Sort Example -----
    sorted_by_priority = planner.sort_tasks(by_deadline=False)
    print(f"\n⭐ Tasks Sorted by Priority: {[t.get_title() for t in sorted_by_priority]}")

    print("\n✅ Simulation Complete!")


if __name__ == "__main__":
    main()
