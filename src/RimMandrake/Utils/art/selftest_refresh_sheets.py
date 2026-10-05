#!/usr/bin/env python3
"""Selftest for refresh_sheets.py (donor-only count, line rewriting, fingerprint)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import refresh_sheets
sys.exit(refresh_sheets.selftest())
