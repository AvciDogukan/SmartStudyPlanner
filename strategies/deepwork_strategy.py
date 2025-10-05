# -*- coding: utf-8 -*-
"""
Deep Work Strategy Module
=========================

This module implements the `DeepWorkStrategy` class — a concrete implementation
of the `StudyStrategy` interface. It is inspired by Cal Newport’s *Deep Work*
principles: long, uninterrupted sessions of focused work followed by longer breaks.

Author:
    Doğukan Avcı

Created:
    2025-10-06

Notes:
------
- Inherits from `StudyStrategy` (defined in `strategy_base.py`)
- Designed for tasks requiring high concentration and cognitive depth
- Can be dynamically injected into the Planner class
"""

import time
from strategies.strategy_base import StudyStrategy


class DeepWorkStrategy(StudyStrategy):
    """
    Concrete implementation of the Deep Work study technique.

    Encourages long, distraction-free focus periods for intense mental work.

    Attributes
    ----------
    work_duration : int
        Duration of deep focus session in minutes (default = 90)
    break_duration : int
        Duration of recovery break in minutes (default = 15)

    Methods
    -------
    start_session():
        Starts a long, uninterrupted Deep Work session.
    take_break():
        Starts a longer restorative break.
    """

    def __init__(self, work_duration: int = 90, break_duration: int = 15):
        self.work_duration = work_duration
        self.break_duration = break_duration

    # ------------------------------------------------------------------
    def start_session(self) -> None:
        """
        Begin a Deep Work focus session.

        Prints motivational messages and simulates the session duration.

        Notes
        -----
        - In practice, this could trigger a focus mode or timer.
        """
        print(f"🧠 Starting Deep Work session: {self.work_duration} minutes of total focus.")
        time.sleep(0.1)
        print("✅ Deep Work session complete. Time for a longer break!")

    # ------------------------------------------------------------------
    def take_break(self) -> None:
        """
        Begin a recovery break after an intense Deep Work session.

        Provides extended rest time to reset mental energy.
        """
        print(f"🌿 Taking a {self.break_duration}-minute restorative break.")
        time.sleep(0.1)
        print("⚡ Break complete. Ready to dive deep again!")
