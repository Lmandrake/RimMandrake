#!/usr/bin/env python3
"""Selftest for block_agent_coded_name.py."""
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hook", os.path.join(HERE, "block_agent_coded_name.py"))
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

CASES = [
    ("C6", True), ("A5", True), ("Lane A2", True), ("lane b", True), ("Lane A", True),
    ("helper C6 review", True), ("fix A4 bugs", True), ("a5", True),
    ("RM_X", False), ("SUBJECT_INTENT_TWIST", False), ("Review wave for dirty C# files", False),
    ("RM_ROT_FIX_V2 cold storage", False), ("Bug fixes", False), ("", False),
    ("B12 - cold storage chain", False), ("B12: cold storage chain", False),
    ("B12", True), ("B12 -", True),
]
fails = [c for c, e in CASES if bool(hook.coded(c)) != e]
for desc, blocked in (("C6", True), ("Bug fixes", False)):
    out = subprocess.run([sys.executable, os.path.join(HERE, "block_agent_coded_name.py")],
                         input=json.dumps({"tool_input": {"description": desc}}),
                         capture_output=True, text=True).stdout
    if ("deny" in out) != blocked:
        fails.append("e2e " + desc)
if subprocess.run([sys.executable, os.path.join(HERE, "block_agent_coded_name.py")],
                  input="not json", capture_output=True, text=True).stdout:
    fails.append("fail-open")
print("FAIL: %s" % fails if fails else "OK %d cases" % (len(CASES) + 3))
sys.exit(1 if fails else 0)
