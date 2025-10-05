# -*- coding: utf-8 -*-
"""
Strategies Package Initialization
=================================

This file makes the `strategies` directory a Python package.
It exposes all available study strategies following the Strategy Pattern.
"""

from .strategy_base import StudyStrategy
from .pomodoro_strategy import PomodoroStrategy
from .deepwork_strategy import DeepWorkStrategy
from .balanced_strategy import BalancedStrategy

__all__ = [
    "StudyStrategy",
    "PomodoroStrategy",
    "DeepWorkStrategy",
    "BalancedStrategy",
]
