"""bars1.py ox oz [--pawns] : the depth bars on ordinary ground, game A.

Row A (z = oz .. oz+1): 2x2 holes side by side, one undug gap between, depths 0 (undug), 0.5, 1, 1.5, 2, 4, 8 m
  (D 0, 1, 2, 3, 4, 8, 16), x = ox + 3k.
Row B (z = oz+5 .. oz+9): one empty 6 x 5 pit dug 2 m (D4), x = ox .. ox+5; beside it (x = ox+9 ..) a 3 x 3 pit 2 m with a
  colonist in it, for occupied vs empty.
--pawns: a drafted colonist stands in the south-west cell of each row-A hole (and on the undug square).
Shots (play zoom, ~64 px a cell): s1_bars_ladder, s1_bars_pit (and _wide at root 11).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb  # noqa: E402
from story1 import shot, log  # noqa: E402

DEPTHS = (0, 1, 2, 3, 4, 8, 16)


def dig(B, cells, d):
    for c in cells:
        B.call("jawa/clear_area", rect="%d,%d,1,1" % c, dryRun=False)
        if d:
            B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=d, setFill=-1)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ox, oz = int(sys.argv[1]), int(sys.argv[2])
    pawns = "--pawns" in sys.argv
    B = fwb.FW()
    holes = []
    for k, d in enumerate(DEPTHS):
        cells = [(ox + 3 * k + i, oz + j) for i in range(2) for j in range(2)]
        dig(B, cells, d)
        holes.append((d, cells))
    big = [(ox + i, oz + 5 + j) for i in range(6) for j in range(5)]
    dig(B, big, 4)
    occ = [(ox + 9 + i, oz + 5 + j) for i in range(3) for j in range(3)]
    dig(B, occ, 4)
    ids = []
    if pawns:
        for d, cells in holes:
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=cells[0][0], z=cells[0][1], faction="player", count=1) or {}
            ids += [p.get("id") for p in r.get("pawns") or [] if p.get("id")]
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=occ[4][0], z=occ[4][1], faction="player", count=1) or {}
        ids += [p.get("id") for p in r.get("pawns") or [] if p.get("id")]
        for pid in ids:
            B.call("rimworld/set_draft", pawnId=pid, drafted=True)
    B.call("rimworld/play_for", durationMs=700, speed="Normal")
    ex = B.call("jawa/flowworks_excavation_rect", x=ox, z=oz, w=21, h=2, onlyNonZero=True, includeTerrain=False) or {}
    log("ladder depths", sorted({(c.get("x") - ox) // 3: c.get("d") for c in ex.get("cells") or ex.get("rows") or []}.items()))
    cen = B.call("jawa/pawn_census", ids=",".join(ids)) if ids else {}
    log("pawns", [(p.get("name"), p.get("x"), p.get("z")) for p in (cen or {}).get("pawns") or []])
    shot(B, "bars_ladder_a", rect=(ox - 1, oz - 2, 12, 6))
    shot(B, "bars_ladder_b", rect=(ox + 11, oz - 2, 11, 6))
    shot(B, "bars_pit", rect=(ox - 1, oz + 3, 14, 9))
    shot(B, "bars_wide", rect=(ox - 2, oz - 3, 24, 16), root=11)


if __name__ == "__main__":
    main()
