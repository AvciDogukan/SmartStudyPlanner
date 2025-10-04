# -*- coding: utf-8 -*-
"""
Planner Module
==============

This module defines the `Planner` class for the Smart Study Planner project.
The Planner manages the relationship between a User and their Tasks, providing
business logic such as filtering, sorting, and statistics.

Author:
    Doğukan Avcı
Created:
    2025-10-04
"""

from core.task import Task
from core.user import User
from datetime import datetime


class Planner:
    def __init__(self, user: User, tasks: list[Task] = None):
        self.__user = user
        self.__tasks: list[Task] = [] if tasks is None else tasks

    # ----- Getters & Setters -----
    def get_user(self) -> User:
        """Return the user associated with this planner."""
        return self.__user

    def set_user(self, new_user: User) -> None:
        """Update the user associated with this planner."""
        self.__user = new_user

    def get_tasks(self) -> list[Task]:
        """Return the list of tasks managed by this planner."""
        return self.__tasks

    # ----- Task Management -----
    def add_task(self, task: Task) -> None:
        """Add a task to the planner."""
        self.__tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the planner."""
        if task in self.__tasks:
            self.__tasks.remove(task)

    # ----- Business Logic -----
    def show_stats(self) -> dict[str, int]:
        """Return statistics about tasks (done vs pending)."""
        done = sum(1 for t in self.__tasks if t.get_status() == "done")
        pending = sum(1 for t in self.__tasks if t.get_status() == "pending")
        return {"done": done, "pending": pending}

    def filter_tasks(self, by_status: str) -> list[Task]:
        """Filter tasks by a given status."""
        return [t for t in self.__tasks if t.get_status() == by_status]

    def sort_tasks(self, by_deadline: bool = True) -> list[Task]:
        """Sort tasks by deadline (default) or priority."""
        if by_deadline:
            return sorted(self.__tasks, key=lambda t: t.get_deadline())
        else:
            return sorted(self.__tasks, key=lambda t: t.get_priority())
