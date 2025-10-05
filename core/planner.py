# -*- coding: utf-8 -*-
"""
Planner Module
==============

This module defines the `Planner` class for the Smart Study Planner project.
The Planner manages the relationship between a User and their Tasks, providing
business logic such as filtering, sorting, and productivity strategy execution.

Author:
    Doğukan Avcı

Created:
    2025-10-04
"""

from datetime import datetime
from core.task import Task
from core.user import User
from strategies.strategy_base import StudyStrategy


class Planner:
    """
    Class representing the central planner of the Smart Study Planner system.

    This class links a User object with their Task list and an injected StudyStrategy
    to manage productivity routines and task operations.

    Attributes
    ----------
    __user : User
        The user associated with this planner.
    __tasks : list[Task]
        List of Task objects managed by the planner.
    __strategy : StudyStrategy
        Injected strategy defining the study behavior (e.g., Pomodoro, DeepWork).

    Methods
    -------
    get_user() -> User
        Returns the associated user.
    set_user(new_user: User) -> None
        Updates the user.
    get_tasks() -> list[Task]
        Returns all tasks.
    add_task(task: Task) -> None
        Adds a task.
    remove_task(task: Task) -> None
        Removes a task.
    show_stats() -> dict[str, int]
        Returns 'done' vs 'pending' statistics.
    filter_tasks(by_status: str) -> list[Task]
        Filters tasks by status.
    sort_tasks(by_deadline: bool = True) -> list[Task]
        Sorts tasks by deadline or priority.
    execute_strategy() -> None
        Executes the injected study strategy.
    """

    def __init__(self, user: User, strategy: StudyStrategy, tasks: list[Task] = None):
        """
        Initialize the Planner instance.

        Parameters
        ----------
        user : User
            The user who owns this planner.
        strategy : StudyStrategy
            The injected productivity strategy (Dependency Injection).
        tasks : list[Task], optional
            Initial list of tasks (default is an empty list).
        """
        self.__user = user
        self.__tasks: list[Task] = [] if tasks is None else tasks
        self.__strategy = strategy

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

    def get_strategy(self) -> StudyStrategy:
        """Return the currently injected study strategy."""
        return self.__strategy

    def set_strategy(self, new_strategy: StudyStrategy) -> None:
        """Update the current study strategy."""
        self.__strategy = new_strategy

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

    # ----- Strategy Execution -----
    def execute_strategy(self) -> None:
        """Execute the injected study strategy using dependency injection."""
        if not self.__strategy:
            raise ValueError("No study strategy has been set for this planner.")

        print(f"\n🎯 Executing study strategy: {type(self.__strategy).__name__}")
        self.__strategy.start_session()
        self.__strategy.take_break()

    # ----- Representation -----
    def __repr__(self) -> str:
        """Return a string representation of the planner (for debugging)."""
        return (
            f"Planner(User={self.__user.get_username()}, "
            f"Tasks={len(self.__tasks)}, "
            f"Strategy={type(self.__strategy).__name__})"
        )
