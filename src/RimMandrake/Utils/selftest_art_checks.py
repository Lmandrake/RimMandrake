#!/usr/bin/env python3
"""Puts art_checks.py's own selftest into the run_selftests.py sweep.

`run_selftests.py` discovers by the `selftest*.py` filename glob, so
`art_checks.py --selftest` was invisible to it — a suite nobody runs is a suite
nobody trusts. This wrapper also covers artpiped.run_facts_gate's four verdict
paths, because the gate's job is to REFUSE and a gate that silently passes
everything looks identical to a gate that works.

    python3 selftest_art_checks.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

# Clipped on the right edge — boundaries_respected must call this out.
# ⚠️ Was `Gizka_south.png` until 2026-09-18. That file was REPLACED by the
# owner-locked dino_v5 set (bd9a1b8ee, 2026-09-17) and is no longer clipped, so
# the gate's reject path silently stopped being exercised and the gate read as
# working while nothing proved it refuses anything. `GizkaW_south.png` is the
# stable stand-in: same folder, untouched since 2026-09-14, right margin 0 px in
# both the current file and the pre-dino_v5 blob. A fixture must be a file
# nobody is trying to fix.
KNOWN_BAD = REPO / "src/RimStarWars/GizkaArtOverride/Textures/swanimals/Gizka/GizkaW_south.png"
KNOWN_OK = (REPO / "src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal"
                   "/Pyrelands/Sytheclaw/Sytheclaw_east.png")


def main() -> int:
    fails = []

    proc = subprocess.run([sys.executable, str(HERE / "art_checks.py"), "--selftest"],
                          capture_output=True, text=True, timeout=300)
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        fails.append("art_checks.py --selftest returned %d" % proc.returncode)
    else:
        print("PASS  art_checks.py --selftest")

    sys.path.insert(0, str(HERE / "artpipe"))
    try:
        import artpiped
    except Exception as exc:                                      # noqa: BLE001
        print("FAIL  could not import artpiped: %s" % exc)
        return 1

    # The gate defaults OFF until bounded-retry + PARKED exist, so arm it to test
    # its behaviour, and check the default separately below.
    os.environ["ARTPIPE_FACTS_GATE"] = "1"
    for label, path, want in (("reject on a clipped sprite", KNOWN_BAD, "reject"),
                              ("pass on a clean sprite", KNOWN_OK, "pass"),
                              ("gate_error on a missing file", Path("/nonexistent.png"),
                               "gate_error")):
        if path.name != "nonexistent.png" and not path.is_file():
            fails.append("fixture missing: %s" % path)
            continue
        got = artpiped.run_facts_gate(path)[0]
        if got == want:
            print("PASS  facts gate %s -> %s" % (label, got))
        else:
            fails.append("facts gate %s: wanted %s, got %s" % (label, want, got))

    # Unarmed is the SHIPPED state: arming a refusing gate without a retry cap loops
    # and burns render quota. If this ever returns anything but "skipped", the gate
    # went live without the handling art_review_facts_spec.md requires alongside it.
    del os.environ["ARTPIPE_FACTS_GATE"]
    got = artpiped.run_facts_gate(KNOWN_BAD)[0]
    if got == "skipped":
        print("PASS  facts gate is UNARMED by default -> skipped")
    else:
        fails.append("the facts gate is armed by default (got %s) — it must stay off "
                     "until bounded retry and PARKED exist" % got)

    for f in fails:
        print("FAIL  %s" % f)
    print("\n%d check(s) failed" % len(fails) if fails else "\nall checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
