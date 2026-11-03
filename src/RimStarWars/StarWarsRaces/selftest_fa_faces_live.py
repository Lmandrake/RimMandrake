#!/usr/bin/env python3
"""Offline half of fa_faces_live.py (RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM): the subject plan and the verdict rules,
on synthetic rows. The live half needs the running game (infrastructure/state/live_proofs/RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM.txt)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa_faces_live  # noqa: E402

if __name__ == "__main__":
    sys.exit(fa_faces_live.selftest())
