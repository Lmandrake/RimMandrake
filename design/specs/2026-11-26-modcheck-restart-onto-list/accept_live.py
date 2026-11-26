#!/usr/bin/env python3
"""Outcome check of RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS: a LIVE
`game_lock.py run <game> -- modcheck run <Mod>` on an Archmagi game that was up on ANOTHER mod list restarted the game
onto the list modcheck composed by itself, and the run ended with measured rows and no 'mod_not_installed'.

The proof is the run's own modcheck JSON, committed in this folder as live_<stamp>.json by live_accept.sh (Transient/ is
untracked). The JSON says the restart itself: runner.restart_onto_list writes `restarted_onto_list` into each mod's
summary, with the gap it read before the restart. A recorded `verify --result pass` alone is paper and does not count.

    python3 design/specs/2026-11-26-modcheck-restart-onto-list/accept_live.py

Exit 0: such a run is here. 1: none yet (the need is unmet, or not yet shown). 2: could not look (a JSON that does not
parse). How to satisfy it: on a free Archmagi game that runs another list,
`bash design/specs/2026-11-26-modcheck-restart-onto-list/live_accept.sh ArchSmall`.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEASURED = ("PASS", "FAIL")


def judge(path):
    """-> (ok, why) for one modcheck JSON."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    d = json.loads(text)
    s = d.get("summary") or {}
    rec = s.get("restarted_onto_list") or {}
    if not rec.get("restarted"):
        return False, "no restart by modcheck recorded (restarted_onto_list: %s)" % (rec or "absent")
    if not rec.get("why"):
        return False, "the restart names no gap: the game was not shown to be on another list"
    if "mod_not_installed" in text:
        return False, "the run reads mod_not_installed"
    if s.get("unmeasured") or s.get("refused"):
        return False, "the run was refused: %s" % (s.get("refused") or s.get("unmeasured"))
    rows = [c.get("verdict") for ch in s.get("chains") or [] for c in ch.get("components") or []]
    if not any(v in MEASURED for v in rows):
        return False, "no measured row (verdicts %s)" % rows
    return True, "%s: restarted %s onto its list (gap: %s); rows %s" % (
        os.path.basename(path), rec.get("game"), "; ".join(rec["why"])[:200], rows)


def main():
    paths = sorted(glob.glob(os.path.join(HERE, "live_*.json")))
    if not paths:
        print("NOT YET: no live_*.json here; run live_accept.sh on a free Archmagi game")
        return 1
    blind = False
    for p in reversed(paths):
        try:
            ok, why = judge(p)
        except (OSError, ValueError) as e:
            print("COULD NOT LOOK: %s: %s" % (os.path.basename(p), e))
            blind = True
            continue
        print(("HOLDS: " if ok else "NOT: ") + why)
        if ok:
            return 0
    return 2 if blind else 1


if __name__ == "__main__":
    sys.exit(main())
