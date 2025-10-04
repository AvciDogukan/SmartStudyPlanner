# -*- coding: utf-8 -*-
"""
Task Module
===========

This module defines the `Task` class for the Smart Study Planner project.
The Task class encapsulates all information related to a study task such as
title, deadline, duration, status, priority, and task ID.

Features:
---------
- Encapsulated private attributes with getters/setters
- Mark tasks as completed
- Reschedule tasks with a new deadline

Author:
    Doğukan Avcı
Created:
    2025-10-04
"""

from datetime import datetime

class Task:
    def __init__(self, taskid: int, priority: int, title: str, deadline: datetime, duration: int, status: str = "pending"):
        self.__taskid = taskid
        self.__priority = priority
        self.__title = title
        self.__deadline = deadline
        self.__duration = duration
        self.__status = status

    # ----- Getters & Setters -----
    def get_taskid(self) -> int:
        """Return the unique ID of the task."""
        return self.__taskid

    def set_taskid(self, new_taskid: int) -> None:
        """Update the task ID."""
        self.__taskid = new_taskid

    def get_priority(self) -> int:
        """Return the priority of the task."""
        return self.__priority

    def set_priority(self, new_priority: int) -> None:
        """Update the priority of the task."""
        self.__priority = new_priority

    def get_title(self) -> str:
        """Return the title of the task."""
        return self.__title

    def set_title(self, new_title: str) -> None:
        """Update the task title."""
        self.__title = new_title

    def get_deadline(self) -> datetime:
        """Return the deadline of the task."""
        return self.__deadline

    def set_deadline(self, new_deadline: datetime) -> None:
        """Update the task deadline."""
        self.__deadline = new_deadline

    def get_duration(self) -> int:
        """Return the duration of the task in minutes."""
        return self.__duration

    def set_duration(self, new_duration: int) -> None:
        """Update the task duration in minutes."""
        self.__duration = new_duration

    def get_status(self) -> str:
        """Return the current status of the task."""
        return self.__status

    def set_status(self, new_status: str) -> None:
        """Update the status of the task (pending/done)."""
        if new_status in ["pending", "done"]:
            self.__status = new_status
        else:
            raise ValueError("Status must be either 'pending' or 'done'")

    # ----- Business Logic -----
    def mark_done(self) -> None:
        """Mark the task as completed."""
        self.set_status("done")

    def reschedule(self, new_deadline: datetime) -> None:
        """Reschedule the task with a new deadline."""
        self.set_deadline(new_deadline)
