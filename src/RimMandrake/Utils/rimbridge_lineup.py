"""Spawn one of every pawn kind in a grid, for visual review.

The point is the census: with the full mod list this places every alien race,
xenotype and droid chassis side by side so they can be compared at a glance --
the "spawn them all in a nice grid for me to evaluate" job that has been parked
since the droid roster review.

    python src/RimMandrake/Utils/rimbridge_lineup.py --list
    python src/RimMandrake/Utils/rimbridge_lineup.py --dry-run
    python src/RimMandrake/Utils/rimbridge_lineup.py --apply --skip-humanlike
    python src/RimMandrake/Utils/rimbridge_lineup.py --apply --filter droid

Requires a RUNNING game with RimBridgeServer active. Port and token are scraped
from Player.log by rimbridge_client.

WHY A GRID AND NOT A LINE. 68 races at 3-cell spacing is 204 cells, wider than
most maps and far wider than one legible screenshot. Rows wrap at --per-row.

NOTE ON "RACES". RimWorld has no single race list. This walks the debug tree's
`Actions\\Spawn Pawn...` children, which are PawnKindDefs -- so vanilla shows 39
humanlike KINDS (Colonist, Pirate, Mercenary_Sniper...) that are all the same
race. --skip-humanlike drops them by detecting the run before the first animal.
With alien-race mods loaded the humanlike kinds ARE the interesting ones, so the
flag is off by default.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint

BS = chr(92)
ROOT = "Actions" + BS + "Spawn Pawn..."


def kinds(rb):
    d = rb.call("rimworld/list_debug_action_children", {"path": ROOT})
    return [c.get("label") for c in (d.get("children") or []) if c.get("label")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x", type=int, default=40)
    ap.add_argument("--z", type=int, default=100)
    ap.add_argument("--step", type=int, default=3)
    ap.add_argument("--row-gap", type=int, default=6)
    ap.add_argument("--per-row", type=int, default=40)
    ap.add_argument("--filter", help="substring match on the kind label")
    ap.add_argument("--skip-humanlike", action="store_true",
                    help="drop the leading run of humanlike pawn kinds")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    host, port, token = resolve_endpoint()
    if not token:
        print("No bridge token in Player.log. Is the game running?")
        return 1

    with RimBridge(host, port, token) as rb:
        ks = kinds(rb)
        if a.skip_humanlike:
            # The tree lists humanlike kinds first, then animals. Cut at the
            # first entry that is not obviously a humanlike faction kind.
            for marker in ("Alpaca", "Alphabeaver"):
                if marker in ks:
                    ks = ks[ks.index(marker):]
                    break
        if a.filter:
            ks = [k for k in ks if a.filter.lower() in k.lower()]

        print("%d pawn kinds selected" % len(ks))
        if a.list:
            for k in ks:
                print("   ", k)
            return 0

        rb.call("rimworld/set_god_mode", {"enabled": True})
        ok = fail = 0
        first = last = None
        for i, k in enumerate(ks):
            x = a.x + (i % a.per_row) * a.step
            z = a.z + (i // a.per_row) * a.row_gap
            if a.dry_run:
                print("   would place %-28s at (%d,%d)" % (k, x, z))
                continue
            if not a.apply:
                continue
            try:
                r = rb.call("rimworld/execute_debug_action",
                            {"path": ROOT + BS + k, "x": x, "z": z})
                if r.get("success"):
                    ok += 1
                    first = first or (k, x, z)
                    last = (k, x, z)
                else:
                    fail += 1
            except Exception as e:
                fail += 1
                print("   !! %s -> %s" % (k, str(e)[:110]))
        if a.apply:
            print("placed ok=%d fail=%d" % (ok, fail))
            print("first %s  last %s" % (first, last))
            w = min(len(ks), a.per_row) * a.step
            h = ((len(ks) - 1) // a.per_row + 1) * a.row_gap
            try:
                rb.call("rimworld/frame_cell_rect",
                        {"x": a.x, "z": a.z - 2, "width": w, "height": h + 4})
            except Exception:
                pass
            rb.call("rimworld/take_screenshot",
                    {"fileName": "lineup", "suppressMessage": True})
            print("screenshot -> Screenshots/lineup.png")
        elif not a.dry_run:
            print("plan only. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
