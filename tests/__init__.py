"""
Tests for the Supply Chain Analytics system
"""
import os
import sys
import pytest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
