#!/usr/bin/env python3
"""MIASMA_WARDEN_MOTHER_ART_1 contract proof: runs ../selftest_warden_mother_art.py (the check lives there so the
nightly selftest sweep, which discovers selftest*.py, runs it too). Exit code passes through."""
import runpy
import sys
from pathlib import Path

sys.exit(runpy.run_path(str(Path(__file__).resolve().parents[1] / "selftest_warden_mother_art.py"))["main"]())
