#!/usr/bin/env python3
"""selftest_icon_outline_census.py — the outline metric, the dark-material rule, row and texPath matching."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icon_outline_census  # noqa: E402

icon_outline_census.selftest()
