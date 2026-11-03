#!/usr/bin/env python3
"""Nightly hook for art_fold_live.py's own selftest (ART_OVERRIDE_FAMILY_SCRIPT_1): binding, every status, exit codes."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art_fold_live  # noqa: E402

if __name__ == "__main__":
    sys.exit(art_fold_live.selftest())
