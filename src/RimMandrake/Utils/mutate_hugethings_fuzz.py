#!/usr/bin/env python3
"""Planted-bug check for the HugeThings fuzz: runs the shared mutation runner over mutations_hugethings_fuzz.json.

    python3 src/RimMandrake/Utils/mutate_hugethings_fuzz_fuzz.py [--only N]      # N = 0-based mutation index
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mutate_kernel_fuzz  # noqa: E402

if __name__ == "__main__":
    sys.exit(mutate_kernel_fuzz.main(["selftest_hugethings_fuzz.py", os.path.join(HERE, "mutations_hugethings_fuzz.json")] + sys.argv[1:]))
