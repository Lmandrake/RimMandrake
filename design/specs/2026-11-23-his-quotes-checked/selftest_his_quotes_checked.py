#!/usr/bin/env python3
"""Tests for boundary.md beside this file; each test carries its promise's name."""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_quotes as X  # noqa: E402
PLANT = '''# A heading

The owner, 2026-11-20: *"Put the thing on the shelf,
and "never" move it."* So it stays.

- He answered by card: "Which shelf → the top one".

Owner's ruling, 2026-11-19: "nobody may touch that shelf again". The rest is ours.

The tool prints "exit code of the run" and stops.
'''
EDGE = '''# H
- **"A bold lead" is not a quote.** The tool runs. His card: *"Locked bars are
  the page"*.
- **THE SHIP, owner: *"It's ship or nothing."***
'''


def t_three_shapes_are_found():
    got = {(q["shape"], q["text"].split()[0]) for q in X.quotes(PLANT)}
    assert got == {("ITALIC", "Put"), ("CARD", "Which"), ("PLAIN", "nobody")}, got


def t_a_bold_lead_never_swallows_a_quote():
    got = [q["text"] for q in X.quotes(EDGE) if q["shape"] == "ITALIC"]
    assert got == ["Locked bars are the page", "It's ship or nothing."], got


def t_could_not_look_is_not_zero():
    tool = os.path.join(HERE, "extract_quotes.py")
    with tempfile.NamedTemporaryFile("w", suffix=".md") as f:
        assert subprocess.run([sys.executable, tool, f.name], capture_output=True).returncode == 0
    assert subprocess.run([sys.executable, tool, "/no/such/file.md"], capture_output=True).returncode == 2


def main():
    bad = 0
    for t in (t_three_shapes_are_found, t_a_bold_lead_never_swallows_a_quote, t_could_not_look_is_not_zero):
        try:
            t()
            print("PASS", t.__name__)
        except AssertionError as e:
            bad += 1
            print("FAIL", t.__name__, e)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
