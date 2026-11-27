#!/usr/bin/env python3
"""live_flyer_flight_sizes.py - in the running game, does each flyer fly at its own life stage's size?

The live half of flyer_size_census.py (item RIMMANDRAKE_RESIZE_FLYERS_ADULTS_FLY_AT_BABY_SIZE_TWENTY_OF_THEM). With
flyingAnimationInheritColors true, RimWorld 1.6 (AnimationDefGenerator_Flying) makes one flight GraphicStateDef per
life stage colour, named <PawnKind>FlyEast_<aarrggbb>_0. This reads, through jawa/get_defs (read-only, no tick), the
drawSize the engine gave each stage's first east frame, and compares it with the stage's own size from the def in src/
(bodyGraphicData drawSize x flyingAnimationDrawSize). A stage whose GraphicStateDef is absent is a FAIL: the engine
did not key that stage's flight by its colour.

Only flyers with InheritColors true and the size as a multiplier are read (the census judges the others offline).
The game must have loaded the defs of this tree (deploy first; defs are parsed at startup).

Exit 0 = every read stage flies at its own size, 1 = a stage does not (listed), 2 = could not look (no bridge or
no reply), UNMEASURED.

    python.exe src/RimMandrake/Utils/art/live_flyer_flight_sizes.py [PawnKind ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import flyer_size_census as C  # noqa: E402
import selftest_skinflap_flutter as T  # noqa: E402

TOL = 0.01


def color_hex(text: str | None) -> str:
    """The engine's name key for a stage colour: Color32 as aarrggbb (CreateAnimFromFrames)."""
    r, g, b, a = (round(x * 255) for x in T.parse_color(text))
    return f"{(a << 24) | (r << 16) | (g << 8) | b:08x}"


def wanted(only: set[str]) -> list[tuple[str, int, str, float]]:
    """(pawnkind, stage, GraphicStateDef name, own flight size) for each inherit+multiplier flyer stage."""
    rows = []
    for d, _f, pk in C.kinds():
        if only and d not in only:
            continue
        flag = lambda tag: (pk.findtext(tag) or "false").strip().lower() == "true"  # noqa: E731
        if not (flag("flyingAnimationInheritColors") and flag("flyingAnimationDrawSizeIsMultiplier")):
            continue
        base = float(pk.findtext("flyingAnimationDrawSize") or "1")
        for i, st in enumerate(pk.findall("lifeStages/li")):
            own = T.parse_size(st.findtext("bodyGraphicData/drawSize")) * base
            rows.append((d, i, f"{d}FlyEast_{color_hex(st.findtext('bodyGraphicData/color'))}_0", own))
    return rows


def main(argv: list[str]) -> int:
    rows = wanted(set(argv))
    if not rows:
        print("UNMEASURED: no flyer with InheritColors true and a multiplier size matched")
        return 2
    try:
        from rimbridge_client import RimBridge, resolve_endpoint
        host, port, token = resolve_endpoint()
        with RimBridge(host, port, token) as rb:
            reply = rb.call("jawa/get_defs", {"defs": ";".join(f"GraphicStateDef/{n}" for _, _, n, _ in rows),
                                              "fields": "defaultGraphicData", "limit": len(rows) + 10})
    except Exception as e:  # noqa: BLE001 - any bridge fault is a could-not-look, named
        print(f"UNMEASURED: bridge call failed: {type(e).__name__}: {e}")
        return 2
    got = {x.get("defName") or x.get("requested", "").split("/")[-1]: x for x in reply.get("defs") or []}
    if not got:
        print(f"UNMEASURED: jawa/get_defs returned no rows ({str(reply)[:200]})")
        return 2
    bad = 0
    for d, i, name, own in rows:
        row = got.get(name)
        size = (((row or {}).get("fields") or {}).get("defaultGraphicData") or {}).get("drawSize") or {}
        if not row or not row.get("found") or "x" not in size:
            print(f"FAIL {d} stage {i}: {name} not in the game (the engine did not key this stage by its colour)")
            bad += 1
            continue
        ok = abs(size["x"] - own) <= TOL * own
        print(f"{'ok  ' if ok else 'FAIL'} {d} stage {i}: engine flight size {size['x']}, own size {round(own, 4)}")
        bad += 0 if ok else 1
    print(f"{len(rows)} flyer stages read, {bad} not at their own size")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
