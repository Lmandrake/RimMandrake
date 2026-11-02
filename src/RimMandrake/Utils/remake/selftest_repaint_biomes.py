#!/usr/bin/env python3
"""Selftest for repaint_biomes.py: rename/edit logic, the by-name decode (base hashes, bumped and clashing hashes), the
stamp check's bars on a toy stamp, and the committed big-repaint stamp itself (offline, no save)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repaint_biomes as r

rc = r.main(["selftest"])
rc |= r.main(["check", os.path.join(r.REPO, "world", "repaint_2026-10-21", "tiles_biome.csv")])
sys.exit(1 if rc else 0)
