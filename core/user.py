# -*- coding: utf-8 -*-
"""
User Module
===========

This module defines the `User` class for the Smart Study Planner project.
The User class encapsulates user-related information (username, email)
and manages aggregation of tasks.

Features:
---------
- Private attributes with getters and setters for encapsulation
- Task management functions (add_task, remove_task, view_tasks)
- Aggregation relationship with Task class

Author:
    Doğukan Avcı

Created:
    2025-10-04

Last Modified:
    2025-10-04

Notes:
------
This file is part of the `core` package. It is designed with OOP principles
and UML specifications defined for the project.
"""

from core.task import Task   # doğru import

class User:
    def __init__(self, username: str, email: str):
        self.__username = username
        self.__email = email
        self.__tasks: list[Task] = []   # aggregation: User sahip ama Task bağımsız yaşayabilir

    # ----- Getters & Setters -----
    def get_username(self) -> str:
        """Return the username of the user."""
        return self.__username

    def set_username(self, new_username: str) -> None:
        """Update the username of the user."""
        self.__username = new_username

    def get_email(self) -> str:
        """Return the email of the user."""
        return self.__email

    def set_email(self, new_email: str) -> None:
        """Update the email of the user."""
        self.__email = new_email

    def get_tasks(self) -> list[Task]:
        """Return the list of tasks owned by the user."""
        return self.__tasks

    # ----- Task Management -----
    def add_task(self, new_task: Task) -> None:
        """Add a new task to the user's task list."""
        self.__tasks.append(new_task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the user's task list."""
        if task in self.__tasks:
            self.__tasks.remove(task)

    def view_tasks(self) -> list[Task]:
        """Return a copy of the user's tasks."""
        return list(self.__tasks)   # encapsulation: dışarıya kopya veriyoruz
