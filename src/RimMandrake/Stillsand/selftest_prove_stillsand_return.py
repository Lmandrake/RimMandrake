#!/usr/bin/env python3
"""Offline selftest of prove_stillsand_return.py (STILLSAND_RETURN_REMAINDER_1): its clause judge against
selftest_stillsand's fake game on both tiers, healthy and with each Return live arm broken.

    python3 src/RimMandrake/Stillsand/selftest_prove_stillsand_return.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prove_stillsand_return  # noqa: E402

if __name__ == "__main__":
    sys.exit(prove_stillsand_return.main(["--selftest"]))
