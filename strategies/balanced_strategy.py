# -*- coding: utf-8 -*-
"""
Balanced Strategy Module
========================

This module defines the `BalancedStrategy` class — a concrete implementation
of the `StudyStrategy` interface that combines the flexibility of Pomodoro
and the depth of Deep Work for balanced productivity.

Author:
    Doğukan Avcı

Created:
    2025-10-06

Notes:
------
- Inherits from `StudyStrategy` (defined in `strategy_base.py`)
- Balances between short sprints and long focus blocks
- Ideal for users who want steady productivity without burnout
"""

import time
from strategies.strategy_base import StudyStrategy


class BalancedStrategy(StudyStrategy):
    """
    Concrete implementation of a balanced study technique.

    Mixes Pomodoro and Deep Work principles:
    - Short sessions for quick tasks.
    - Long sessions for complex work.
    - Smart breaks to sustain energy.

    Attributes
    ----------
    short_session : int
        Duration (in minutes) for light or creative tasks.
    long_session : int
        Duration (in minutes) for demanding or analytical work.
    break_duration : int
        Duration (in minutes) for rest periods between sessions.

    Methods
    -------
    start_session():
        Starts either a short or long focus session depending on context.
    take_break():
        Initiates a standard relaxation break.
    """

    def __init__(self, short_session: int = 30, long_session: int = 60, break_duration: int = 10):
        self.short_session = short_session
        self.long_session = long_session
        self.break_duration = break_duration

    # ------------------------------------------------------------------
    def start_session(self, task_complexity: str = "medium") -> None:
        """
        Start a balanced study session.

        Parameters
        ----------
        task_complexity : str
            Indicates the difficulty of the task ("light", "medium", "deep").

        Notes
        -----
        - Light tasks → short 30 min sessions
        - Deep tasks → long 60 min sessions
        """
        if task_complexity == "light":
            duration = self.short_session
            mode = "short"
        elif task_complexity == "deep":
            duration = self.long_session
            mode = "long"
        else:
            duration = self.short_session + 15
            mode = "medium"

        print(f"⚖️ Starting {mode} balanced session: {duration} minutes.")
        time.sleep(0.1)
        print("✅ Balanced study session completed successfully!")

    # ------------------------------------------------------------------
    def take_break(self) -> None:
        """Start a relaxing break between balanced sessions."""
        print(f"☕ Taking a balanced {self.break_duration}-minute break.")
        time.sleep(0.1)
        print("💡 Break complete. Time to get back to work!")
