# -*- coding: utf-8 -*-
"""
Main Module
===========

Entry point for the Smart Study Planner application.

This script demonstrates the full OOP + Design Pattern architecture:
- Uses Strategy Pattern to dynamically switch study behaviors.
- Uses Factory Pattern to create strategy objects at runtime.
- Demonstrates encapsulation, abstraction, and dependency injection
  through the Planner, User, and Strategy relationships.

Author:
    Doğukan Avcı

Created:
    2025-10-06
"""

# ----- Imports -----
from core import User, Task, Planner
from datetime import datetime
from strategies.factory import StrategyFactory


def main():
    """Main entry point for the Smart Study Planner simulation."""

    print("📘 SMART STUDY PLANNER INITIALIZING...\n")

    # ----- Create a user -----
    user = User("dogukanavci", "dogukan@example.com")
    print(f"👤 User created: {user.get_username()} ({user.get_email()})\n")

    # ----- Define initial tasks -----
    tasks = [
        Task(1, 1, "Finish AI homework", datetime(2025, 10, 10), 120, "pending"),
        Task(2, 2, "Prepare TEKNOFEST presentation", datetime(2025, 10, 12), 90, "pending"),
        Task(3, 3, "Update portfolio website", datetime(2025, 10, 15), 60, "done"),
    ]

    print(f"🧩 Planner initialized with {len(tasks)} tasks.\n")

    # ----- Choose strategy via Factory Pattern -----
    strategy_name = input("🎓 Choose study strategy (pomodoro / deepwork / balanced): ").strip()
    try:
        strategy = StrategyFactory.create(strategy_name)
    except ValueError as e:
        print(e)
        return

    # ----- Initialize Planner with selected strategy -----
    planner = Planner(user, strategy, tasks)

    print("\n📋 TASK OVERVIEW")
    for task in planner.get_tasks():
        print(f"- {task.get_title()} (Status: {task.get_status()}, Priority: {task.get_priority()})")

    stats = planner.show_stats()
    print(f"\n📊 Task Stats → Done: {stats['done']} | Pending: {stats['pending']}\n")

    # ----- Execute selected strategy -----
    print("🚀 Starting Study Session:\n")
    planner.execute_strategy()

    # ----- Task Management Demonstration -----
    pending_tasks = [t.get_title() for t in planner.filter_tasks("pending")]
    print(f"\n🕒 Pending Tasks: {pending_tasks}")

    sorted_tasks = [t.get_title() for t in planner.sort_tasks(by_deadline=False)]
    print(f"\n⭐ Tasks Sorted by Priority: {sorted_tasks}")

    print("\n✅ Simulation Complete!")


# ----- Entry Point -----
if __name__ == "__main__":
    main()
