#!/usr/bin/env python3
"""Offline guard for stage_pole_sway_matrix.py (RIMMANDRAKE_SHOW_SLACK_FIXES_LIVE_WHEN_BUILDERS_END, measured 2026-11-16).

Its first live run (python.exe, as its docstring says) staged and saved the matrix, then died writing the key sheet:
PermissionError on '/mnt/d/ClaudeWork' -- the showings folder was a hard-wired WSL path. It must come from rmpaths (the one
storage helper), which spells it for whichever Python runs it. Also checks the 27-station layout never overlaps.

    python3 src/RimMandrake/GimmeSomeSlack/tools/selftest_stage_pole_sway_matrix.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))
import rmpaths  # noqa: E402


def main():
    fails = []

    def check(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    src = open(os.path.join(HERE, "stage_pole_sway_matrix.py"), encoding="utf-8").read()
    check("/mnt/" not in src and "D:\\\\" not in src and "D:/" not in src, "no hard-wired storage path in the stager's source")
    try:
        import stage_pole_sway_matrix as M
    except ImportError as ex:          # its live imports are numpy-free; a missing one is a real failure here
        check(False, "imports offline (%s)" % ex)
        M = None
    if M is not None:
        want = rmpaths.rm_str("showings", "RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT")
        check(str(M.SHOW) == want, "SHOW comes from rmpaths for this Python (%s)" % M.SHOW)
        st = M.layout(20, 20)
        cells = [(x, s["a"][1]) for s in st for x in range(s["a"][0], s["b"][0] + 1)]
        check(len(st) == 27 and len(cells) == len(set(cells)), "27 stations, no two spans share a cell")
        # a mast draws ~3 cells tall above its base cell; a sign book there hid the mast art (live capture 2026-11-16)
        drawn = {(m[0], m[1] + dz) for s in st for m in (s["a"], s["b"]) for dz in range(0, 4)} | set(cells)
        signs = [M.sign_cell(s) for s in st] if hasattr(M, "sign_cell") else []
        check(len(signs) == 27 and not drawn & set(signs) and len(set(signs)) == 27,
              "every sign book sits clear of the masts and spans (%s)" % sorted(drawn & set(signs))[:3])
        # north (higher z) is UP on screen; the first sheet said "top to bottom: Pendulum" with Pendulum the bottom row
        order = [s["look"] + " " + s["span"] for s in sorted(st, key=lambda s: -s["a"][1]) if s["wind"] == "calm"]
        txt = M.row_order_text(st) if hasattr(M, "row_order_text") else ""
        check(txt.startswith("Rows top to bottom") and txt.find(order[0]) < txt.find(order[-1]) and order[0] in txt,
              "the key sheet's row order reads top (north) to bottom: %s ... %s" % (order[0], order[-1]))
    print("%d/%d" % (6 - len(fails), 6))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
