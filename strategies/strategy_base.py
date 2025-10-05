# -*- coding: utf-8 -*-
"""
Strategy Base Module
====================

This module defines the abstract base class `StudyStrategy` used in the
Smart Study Planner system. It follows the **Strategy Design Pattern**,
defining a common interface for all study modes (e.g., Pomodoro, Deep Work,
Balanced). Each strategy defines its own study and break behavior.

Classes:
--------
- StudyStrategy (abstract): Defines the interface for all strategy implementations.

Usage Example:
--------------
>>> from strategies.strategy_base import StudyStrategy
>>> class CustomStrategy(StudyStrategy):
...     def start_session(self):
...         print("Custom session started")
...     def take_break(self):
...         print("Custom break")
"""

from abc import ABC, abstractmethod


class StudyStrategy(ABC):
    """
    Abstract base class for study strategies.

    This class defines the interface (contract) for all study strategies.
    Subclasses such as `PomodoroStrategy`, `DeepWorkStrategy`, and `BalancedStrategy`
    must implement the `start_session()` and `take_break()` methods.

    Notes
    -----
    - Implements the **Strategy Pattern** (Behavioral Design Pattern).
    - Enables runtime selection of study strategy via Dependency Injection.
    - Promotes extensibility without modifying the core Planner logic.

    Example
    -------
    >>> class PomodoroStrategy(StudyStrategy):
    ...     def start_session(self):
    ...         print("Pomodoro session started.")
    ...     def take_break(self):
    ...         print("Short break.")
    """

    @abstractmethod
    def start_session(self) -> None:
        """
        Abstract method to start a focused work session.

        This method defines the behavior for initiating a study session.
        Each concrete strategy must override this method.

        Raises
        ------
        NotImplementedError
            If not implemented by subclass.
        """
        raise NotImplementedError("Subclasses must implement start_session().")

    @abstractmethod
    def take_break(self) -> None:
        """
        Abstract method to define the break period.

        This method defines how a break period should behave after a work session.
        Each concrete strategy must override this method.

        Raises
        ------
        NotImplementedError
            If not implemented by subclass.
        """
        raise NotImplementedError("Subclasses must implement take_break().")
