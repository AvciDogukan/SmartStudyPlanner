# -*- coding: utf-8 -*-
"""
Pomodoro Strategy Module
========================

This module implements the `PomodoroStrategy` class — a concrete implementation
of the `StudyStrategy` interface. It follows the Pomodoro time management method:
25 minutes of focused work followed by a 5-minute break.

Author:
    Doğukan Avcı

Created:
    2025-10-06

Notes:
------
- Inherits from `StudyStrategy` (defined in `strategy_base.py`)
- Designed to be injected into the `Planner` class dynamically
- Follows the **Strategy Design Pattern**
"""

import time
from strategies.strategy_base import StudyStrategy


class PomodoroStrategy(StudyStrategy):
    """
    Concrete implementation of the Pomodoro study technique.

    The Pomodoro method divides work into short intervals
    (called "pomodoros") of 25 minutes, separated by short breaks.

    Attributes
    ----------
    work_duration : int
        Duration of focused work in minutes (default = 25)
    break_duration : int
        Duration of break in minutes (default = 5)

    Methods
    -------
    start_session():
        Starts a focused Pomodoro work session.
    take_break():
        Starts a short 5-minute break.
    """

    def __init__(self, work_duration: int = 25, break_duration: int = 5):
        self.work_duration = work_duration
        self.break_duration = break_duration

    # ------------------------------------------------------------------
    def start_session(self) -> None:
        """
        Begin a focused Pomodoro work session.

        Prints motivational messages and simulates the work duration
        (optionally could be replaced by a GUI timer in future).

        Notes
        -----
        - Uses time.sleep() for simulation purposes only.
        """
        print(f"🍅 Starting Pomodoro session: {self.work_duration} minutes of deep focus!")
        # Simülasyon: gerçek projede zamanlayıcı veya GUI timer ile değiştirilebilir
        time.sleep(0.1)
        print("✅ Pomodoro session completed! Time for a break.")

    # ------------------------------------------------------------------
    def take_break(self) -> None:
        """
        Begin a short break after a Pomodoro session.

        Provides rest time for the user before the next work cycle.

        Notes
        -----
        - Uses time.sleep() for simulation purposes only.
        """
        print(f"☕ Taking a {self.break_duration}-minute break. Relax and recharge!")
        time.sleep(0.1)
        print("💪 Break over! Ready for the next Pomodoro.")
