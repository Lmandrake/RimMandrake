#!/usr/bin/env python3
r"""arena_lane_probe.py — the in-game half of the arena lane canary. Windows python.exe ONLY (rimdrive's Session).

Kept out of arena_lane.py on purpose: that module (and arena_tasks) import fcntl, which Windows python has not, so a
probe living there could never even import. This file imports nothing from the arena.

Prints ONE JSON line: ingame_canary (modcheck validity.canary, reused), live_colonists, game_info (the raw
rimworld/get_game_info reply, so the live proof can pin its keys), and save_name ONLY when that reply carries a key
naming the loaded save. A missing save_name is a red canary in arena_lane (UNMEASURED is never a pass).

UNPROVEN LIVE (owed): which get_game_info key, if any, names the loaded save.
"""
import json
import sys
from pathlib import Path

UTILS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(UTILS / "modcheck"))
sys.path.insert(0, str(UTILS))

SAVE_KEYS = ("saveName", "save_name")   # unverified spellings; a wrong guess leaves it unmeasured (red)


def main():
    from rimdrive import Session  # noqa: E402
    import validity  # noqa: E402
    import runner  # noqa: E402
    out = {}
    with Session(lock=None) as s:
        out["ingame_canary"] = validity.canary(s, runner._default_anchor(s))
        h, rows = validity._pawns(s)
        out["live_colonists"] = sum(1 for r in rows if h.is_colonist(r) and not r.get("dead"))
        gi = s.call("rimworld/get_game_info") or {}
        out["game_info"] = gi
        for k in SAVE_KEYS:
            if isinstance(gi, dict) and k in gi:
                out["save_name"] = gi[k]
                break
    print(json.dumps(out, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
