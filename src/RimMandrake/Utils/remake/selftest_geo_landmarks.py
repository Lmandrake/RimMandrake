#!/usr/bin/env python3
"""Selftest for geo_landmarks.py: the checker's rules on a toy graph, resolver sanity probes, and the frozen
landmark files themselves (offline check, no save)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_landmarks as g

rc = g.main(["selftest"])
rc |= g.main(["check"])
sys.exit(1 if rc else 0)
