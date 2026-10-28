"""Evaluate supplied test evidence against explicit release policies."""

from .engine import evaluate, evaluate_files
from .models import VERSION, Check, Report, Status

__version__ = VERSION
__all__ = ["Check", "Report", "Status", "__version__", "evaluate", "evaluate_files"]
