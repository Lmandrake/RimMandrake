#!/usr/bin/env python3
"""Offline selftest of prove_sandswim.py (STILLSAND_SAND_SWIM_REMAINDER_1): its clause judge against
selftest_stillsand's fake game, healthy and with each sand-swim arm broken.

    python3 src/RimMandrake/Stillsand/selftest_prove_sandswim.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prove_sandswim  # noqa: E402

if __name__ == "__main__":
    sys.exit(prove_sandswim.main(["--selftest"]))
