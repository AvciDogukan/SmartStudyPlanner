# -*- coding: utf-8 -*-
"""
Strategy Factory Module
=======================

This module defines the `StrategyFactory` class which creates and returns
study strategy instances dynamically based on input strings.
"""

from strategies import PomodoroStrategy, DeepWorkStrategy, BalancedStrategy
from strategies.strategy_base import StudyStrategy


class StrategyFactory:
    """Factory class to create study strategies dynamically."""

    @staticmethod
    def create(strategy_name: str) -> StudyStrategy:
        """Return an instance of a strategy based on its name."""
        strategies = {
            "pomodoro": PomodoroStrategy,
            "deepwork": DeepWorkStrategy,
            "balanced": BalancedStrategy,
        }

        key = strategy_name.lower().strip()
        if key not in strategies:
            raise ValueError(
                f"❌ Unknown strategy '{strategy_name}'. Valid options: {list(strategies.keys())}"
            )

        # ✅ Bu satır nesne oluşturma (object instantiation)
        return strategies[key]()
