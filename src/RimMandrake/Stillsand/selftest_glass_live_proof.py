#!/usr/bin/env python3
"""Offline selftest of prove_glass_chain.py (STILLSAND_GLASS_CHAIN_REMAINDER_1): its clause judge against
selftest_stillsand's fake game, healthy and with each glass live arm broken.

    python3 src/RimMandrake/Stillsand/selftest_glass_live_proof.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prove_glass_chain  # noqa: E402

if __name__ == "__main__":
    sys.exit(prove_glass_chain.main(["--selftest"]))
