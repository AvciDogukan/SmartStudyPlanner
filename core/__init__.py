# -*- coding: utf-8 -*-
"""
Core Package Initialization
===========================

This file makes the `core` directory a Python package.
It contains the fundamental classes used throughout the Smart Study Planner:
- Task
- User
- Planner
"""

from .task import Task
from .user import User
from .planner import Planner

__all__ = ["Task", "User", "Planner"]
