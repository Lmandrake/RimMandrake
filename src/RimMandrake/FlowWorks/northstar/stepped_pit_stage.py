"""RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM, the live stage: the offline sweep's 12 stepped-pit cases dug in
the running game (the engine's own Deepen, RM_NorthstarProofs.ProofStageBasin), each captured close, the grid captured whole,
and the map saved for his look.

Why a live stage: the C# selftest (PitSteppedReliefChecks, the golden twin of design/specs/2026-11-22-stepped-pit-inner-cliff/
pitrule.py) proves the numbers; only the game shows the picture (his words, 2026-11-22: "This might work better in the game
than in the mock-up"). This script decides no bar: it stages and captures, and a person or a judge LOOKS.

Layout: 4 columns x 3 rows of 8-square slots from --origin x,z (the south-west corner of the grid); each case's north row is
the slot's top. The labels are the capture file names (case_<nn>_<slug>.png) and the README's table.
LIES: a refused call is HARNESS; a square that did not dig to its depth is SITE. Exit 0 when every case staged and captured,
2 otherwise (never PASS/FAIL: nothing here is a verdict).

    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python.exe src/RimMandrake/FlowWorks/northstar/stepped_pit_stage.py <out_dir> [--origin 40,40] [--save NAME]
"""
import argparse
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))):
    if p not in sys.path:
        sys.path.insert(0, p)

NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
SLOT, NCOL = 8, 4
# the offline sweep's cases (render.py CASES), metres, rows north first
CASES = [
    ("his L: 4 m L in 8 m", [[4, 4, 8], [4, 8, 8], [8, 8, 8]]),
    ("step 2 m / 6 m", [[2] * 4, [2] * 4, [6] * 4, [6] * 4]),
    ("step 6 m / 2 m (deep north)", [[6] * 4, [6] * 4, [2] * 4, [2] * 4]),
    ("step N-S: 2 m west, 6 m east", [[2, 2, 6, 6]] * 4),
    ("three levels: 1, 3, 6 m", [[1] * 3, [3] * 3, [6] * 3]),
    ("deep corner 6 m in 2 m", [[2, 2, 2], [2, 2, 2], [2, 2, 6]]),
    ("6 m hole in 1 m pit", [[1, 1, 1], [1, 6, 1], [1, 1, 1]]),
    ("1 m island in 6 m pit", [[6, 6, 6], [6, 1, 6], [6, 6, 6]]),
    ("trench 1 wide, 3 m", [[3], [3], [3], [3]]),
    ("trench 1 wide, 8 m", [[8], [8], [8]]),
    ("1-square pit, 4 m", [[4]]),
    ("single depth 2 m", [[2] * 3] * 3),
]
# --set water: the three things the dry sweep never drew (README "Not done"): side walls in water, an inner cliff part way under
# water, and a ladder hung on that cliff. Each: (name, grid, water surface in metres below the ground, ladders as (row, col) of
# the deep square the ladder stands in, hung north onto the cliff above it).
WATER_CASES = [
    ("step 2/6, water at 3 m, ladder on cliff", [[2] * 4, [2] * 4, [6] * 4, [6] * 4], 3.0, [(2, 1)]),
    ("step 2/6, water at 1 m, cliff drowned", [[2] * 4, [2] * 4, [6] * 4, [6] * 4], 1.0, [(2, 1)]),
    ("his L, water at 6 m, ladder on L", [[4, 4, 8], [4, 8, 8], [8, 8, 8]], 6.0, [(1, 1)]),
    ("step N-S 2 W / 6 E, water at 3 m", [[2, 2, 6, 6]] * 4, 3.0, []),
]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]


def slot_origin(k, ox, oz, nrows=3):
    col, row = k % NCOL, k // NCOL
    return ox + col * SLOT, oz + (nrows - 1 - row) * SLOT   # row 0 of the grid is its north row


def cells_of(k, grid, ox, oz, nrows=3):
    """(x, z, notches) of every dug square of case k: its north row at the slot's top, one square in from the slot's west edge."""
    sx, sz = slot_origin(k, ox, oz, nrows)
    top = sz + SLOT - 2
    out = []
    for r, row in enumerate(grid):
        for c, m in enumerate(row):
            out.append((sx + 1 + c, top - r, int(round(m * 2))))
    return out


def wait_file(path, timeout=10.0):
    """Wait until the capture at <path> exists and its size holds for one poll (it is written after the bridge call returns)."""
    if not path:
        return False
    if os.name != "nt":
        from game_paths import win_to_wsl
        path = win_to_wsl(path)
    end, last = time.time() + timeout, -1
    while time.time() < end:
        n = os.path.getsize(path) if os.path.exists(path) else -1
        if n > 0 and n == last:
            return True
        last = n
        time.sleep(0.25)
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir")
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--save", default="RM_STEPPED_PIT_12_CASES")
    ap.add_argument("--set", choices=("dry", "water"), default="dry", help="dry: the sweep's 12 cases; water: WATER_CASES")
    ap.add_argument("--root-size", type=float, default=7.0, help="camera zoom of each case's capture (smaller is closer)")
    a = ap.parse_args(argv)
    ox, oz = (int(v) for v in a.origin.split(","))
    os.makedirs(a.out_dir, exist_ok=True)
    import validation_core as V      # noqa: E402  (bridge-side imports only on a live run)
    import proof_hose as PH          # noqa: E402
    from game_paths import win_to_wsl  # noqa: E402
    B = V.guard(PH.PB())
    res = {"script": "stepped_pit_stage.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "origin": [ox, oz], "cases": []}
    out_json = os.path.join(a.out_dir, "stage.json" if a.set == "dry" else "stage_%s.json" % a.set)

    def save():
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def call(method, arg):
        r = B.call("jawa/static_call", type=NPROOF, method=method, args=arg, _answer=True) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (r.get("success") is True and not txt.startswith("REFUSED")), txt

    nrows = 3 if a.set == "dry" else 1
    w, h = NCOL * SLOT, nrows * SLOT
    # the scene: plants and rock chunks on a quicktest map stood over the pits and hid the faces (first stage, 2026-11-22)
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (ox - 3, oz - 3, w + 6, h + 6), categories="All")
    # and one ground: MarshyTerrain patches darkened half a case (first look, 2026-11-22)
    B.call("jawa/set_terrain", x=ox - 3, z=oz - 3, terrainDef="Soil", width=w + 6, height=h + 6)
    ok, txt = call("ProofResetRect", "%d;%d;%d;%d" % (ox - 1, oz - 1, w + 2, h + 2))
    res["reset"] = txt[:200]
    if not ok:
        res["verdict"] = "HARNESS: ProofResetRect refused: " + txt[:200]
        save()
        print(res["verdict"])
        return 2
    B.call("jawa/mod_settings_field", typeName="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings", field="pitSteppedReliefEnabled",
           action="set", value="True")
    bad = 0
    cases = CASES if a.set == "dry" else WATER_CASES
    prefix = "case" if a.set == "dry" else "water"
    for k, case in enumerate(cases):
        name, grid = case[0], case[1]
        surface = case[2] if len(case) > 2 else None
        rec = {"k": k + 1, "name": name, "cells": [], "short": [], "surface_m": surface, "ladders": []}
        for x, z, n in cells_of(k, grid, ox, oz, nrows):
            water = max(0.0, n * 0.5 - surface) if surface is not None else 0.0
            ok, txt = call("ProofStageBasin", "%d;%d;1;1;%d;%s;RM_Fluid_Water" % (x, z, n, repr(water)))
            got = re.search(r"maxDepth=(\d+)", txt)
            rec["cells"].append([x, z, n, int(got.group(1)) if got else None])
            if not ok or not got or int(got.group(1)) != n:
                rec["short"].append([x, z, n, txt[:120]])
        for rr, cc in (case[3] if len(case) > 3 else ()):
            sx, sz = slot_origin(k, ox, oz, nrows)
            lx, lz = sx + 1 + cc, sz + SLOT - 2 - rr
            lr = B.call("jawa/spawn_batch", ops="RM_LadderPortable:%d,%d" % (lx, lz)) or {}
            rec["ladders"].append([lx, lz, str(lr.get("message") or lr)[:120]])
        bad += 1 if rec["short"] else 0
        res["cases"].append(rec)
        save()
    B.call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
    B.call("jawa/clear_ui", all=True)
    for k, rec in enumerate(res["cases"]):
        sx, sz = slot_origin(k, ox, oz, nrows)
        # a name of its own and a wait for the file: the default name has one-second resolution and the PNG is written after
        # the call returns, so the first stage's case 3 copied case 2's picture (and 7 copied 6, 10 copied 9).
        name = "stp_%s_%02d" % (time.strftime("%H%M%S"), k + 1)
        r = B.call("rimworld/screenshot_cell_rect", x=sx, z=sz, width=SLOT, height=SLOT, paddingCells=0, fileName=name,
                   rootSize=a.root_size) or {}
        src = r.get("path")
        wait_file(src)
        rec["capture"] = src
        if src:
            dst = os.path.join(a.out_dir, "%s_%02d_%s.png" % (prefix, k + 1, slug(rec["name"])))
            try:
                # copied at once: the capture name has one-second resolution, so the next case's capture overwrites it. Under
                # python.exe (the bridge's side) the game's Windows path opens as is; win_to_wsl's /mnt path does not.
                shutil.copyfile(src if os.name == "nt" else win_to_wsl(src), dst)
                rec["capture"] = dst
            except OSError as e:
                rec["capture_error"] = str(e)
        save()
    r = B.call("rimworld/screenshot_cell_rect", x=ox, z=oz, width=w, height=h, paddingCells=1,
               fileName="stp_%s_grid" % time.strftime("%H%M%S")) or {}
    res["grid_capture"] = r.get("path")
    wait_file(res["grid_capture"])
    sv = B.call("rimworld/save_game", saveName=a.save) or {}
    res["save"] = {"name": a.save, "ok": sv.get("success"), "reply": str(sv)[:200]}
    res["verdict"] = "STAGED" if bad == 0 else "SITE: %d case(s) did not dig to depth" % bad
    save()
    print("%s; save %s; %s" % (res["verdict"], a.save, out_json))
    return 0 if bad == 0 and sv.get("success") else 2


if __name__ == "__main__":
    sys.exit(main())
