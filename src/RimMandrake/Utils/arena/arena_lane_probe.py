#!/usr/bin/env python3
r"""arena_lane_probe.py — the in-game half of the arena lane canary. Windows python.exe ONLY (rimdrive's Session).

Kept out of arena_lane.py on purpose: that module (and arena_tasks) import fcntl, which Windows python has not, so a
probe living there could never even import. This file imports nothing from the arena.

Prints ONE JSON line: ingame_canary (modcheck validity.canary, reused), live_colonists, game_info (the raw
rimworld/get_game_info reply), and world {name, seed} from jawa/world_info_get. A missing world is a red canary in
arena_lane (UNMEASURED is never a pass), which compares it to the canonical save's world.

Measured live 2026-10-30: get_game_info has NO key naming the loaded save (keys: status, ticksGame, mapCount,
selectedPawns, operation, state), so the map is identified by its world instead. Stdout is one clean JSON line.
"""
import json
import sys
from pathlib import Path

UTILS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(UTILS / "modcheck"))
sys.path.insert(0, str(UTILS))


def main():
    from rimdrive import Session  # noqa: E402
    import validity  # noqa: E402
    import runner  # noqa: E402
    out = {}
    with Session(lock=None) as s:
        out["ingame_canary"] = validity.canary(s, runner._default_anchor(s))
        h, rows = validity._pawns(s)
        cols = [r for r in rows if h.is_colonist(r)]
        if all(isinstance(r.get("dead"), bool) for r in cols):   # a row with no death flag leaves it unmeasured
            out["live_colonists"] = sum(1 for r in cols if r["dead"] is False)
        out["game_info"] = s.call("rimworld/get_game_info") or {}
        wi = s.call("jawa/world_info_get") or {}
        info = wi.get("info") if isinstance(wi, dict) else None
        if isinstance(info, dict) and info.get("name") and info.get("seedString"):
            out["world"] = {"name": info["name"], "seed": info["seedString"]}
    print(json.dumps(out, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
