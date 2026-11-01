#!/usr/bin/env python3
"""selftest_flyer_gate.py - the flyer gate can fail where it must (FLYER_STABLE_BODY_GATE_1).

Planted, in memory and in a temp dir, offline:
  STATIC   a body with narrow wings passes; a sliver N/S (G2), a canvas-filling body (G4), a wing-only speck field (G1)
           and a missing facing (UNMEASURED) are each refuted by name
  CELL     a locked def is ✓, a refuted one ✗, a clean static with no book partial; a non-flyer has no cell
  BOOK     flyer_gate.flipbook_rc returns the gate's exit code, and a set with no config is 2, not a pass; the
           Uvak config passes and a planted body shift on a scratch copy of its frames does not
  SHEET    art_sheet carries the cell on both row builders
  ENACT    enact leaves a todo on a keep of a ✗ row
  QUEUE    fill_queue refuses a per-frame whole-creature row, passes a wing layer, passes a named override
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "artpipe"))
import flyer_gate as G  # noqa: E402

fails = []


def ok(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name, extra)
    if not cond:
        fails.append(name)


def ellipse(w, h, cx, cy, rx, ry):
    y, x = np.mgrid[0:h, 0:w]
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1


def save(mask, p):
    a = np.zeros((*mask.shape, 4), np.uint8)
    a[mask] = (120, 90, 60, 255)
    Image.fromarray(a).save(p)
    return p


def static_cases(d: Path):
    S = 256
    body = ellipse(S, S, 128, 128, 45, 70)
    side = ellipse(S, S, 128, 128, 70, 45)
    good = {"east": save(side, d / "e.png"), "south": save(body, d / "s.png"), "north": save(body, d / "n.png")}
    g = G.static_metrics(good)
    ok("static good not refuted", not G.refuted(g), g)
    sl = save(ellipse(S, S, 128, 128, 12, 70), d / "sl.png")
    ok("G2 sliver refuted", any(x.startswith("G2") for x in G.refuted(G.static_metrics({**good, "south": sl}))))
    fat = save(ellipse(S, S, 128, 128, 126, 110), d / "fat.png")
    ok("G4 canvas-filling body refuted", any(x.startswith("G4") for x in G.refuted(G.static_metrics({**good, "south": fat}))))
    wing = np.zeros((S, S), bool)
    wing |= ellipse(S, S, 128, 128, 20, 30)
    wing[120:136, 2:254] = True
    wing[60:68, 2:254] = True
    wing[190:198, 2:254] = True
    thin = save(wing, d / "w.png")
    ok("G1 thin strokes round a small body refuted", any(x.startswith("G1") for x in G.refuted(G.static_metrics({**good, "south": thin}))),
       G.static_metrics({**good, "south": thin}))
    ok("missing facing UNMEASURED", G.static_metrics({"east": good["east"]}) is None and G.refuted(None))


def cell_cases():
    row = {"flipbook": "locked", "static_fails": []}
    ok("cell locked", G.cell_text(row).startswith("flyer: convertible ✓"))
    ok("cell ✗", G.cell_text({"flipbook": "none", "static_fails": ["G2 x"]}).startswith("flyer: ✗ G2 x"))
    ok("cell partial", G.cell_text({"flipbook": "unannotated", "static_fails": []}).startswith("flyer: partial"))
    G._cache = {"RM_X": {"flipbook": "none", "static_fails": ["G3 no wings drawn"]}}
    ok("cell_for finds any name", G.cell_for([None, "nope", "RM_X"]).startswith("flyer: ✗"))
    ok("non-flyer has no cell", G.cell_for(["RM_Muffalo"]) == "")
    G._cache = None
    tex = next(r["tex"] for r in G.plan_rows().values() if r.get("tex"))
    ok("a texPath finds its flyer", G.cell_for([tex]).startswith("flyer:"))
    G._cache = None
    keep, G.PLAN = G.PLAN, G.PLAN.with_name("no_such_plan.json")
    try:
        G.cell_for(["RM_X"])
        ok("a missing plan raises", False)
    except FileNotFoundError:
        ok("a missing plan raises", True)
    G.PLAN, G._cache = keep, None


def book_cases(d: Path):
    ok("no config is UNMEASURED", G.flipbook_rc("NoSuchSet") == 2)
    st = str(HERE / "flier_body_stabilize.py")
    ok("Uvak passes the gate", G.flipbook_rc("Uvak") == 0)
    import json
    cfg = json.loads((G.SETS / "Uvak.json").read_text())
    src = G.REPO / cfg["folder"]
    bad = d / "uvak"
    bad.mkdir()
    for p in src.glob(cfg["prefix"] + "*.png"):
        shutil.copy(p, bad / p.name)
    master = cfg["facings"]["south"].get("master", 1)
    victim = bad / f"{cfg['prefix']}{master % 4 + 1}_south.png"
    a = np.array(Image.open(victim).convert("RGBA"))
    Image.fromarray(np.roll(a, (3, -2), (0, 1))).save(victim)
    rc = subprocess.run([sys.executable, st, "--set", "Uvak", "--src", str(bad), "--facing", "south"],
                        capture_output=True, cwd=G.REPO).returncode
    ok("planted body shift fails the gate", rc != 0, rc)


def wiring():
    t = (HERE / "art_sheet.py").read_text()
    ok("both sheet builders carry the cell", t.count("FG.cell_for(") == 2)
    e = (HERE / "enact.py").read_text()
    ok("enact leaves a todo on a keep of ✗", 'FG.cell_for([row, *names])' in e and 'kept the look, body pass owed' in e)


def queue_cases():
    import fill_queue as F
    base = {"id": "regen_x_flying_1", "rimflow_item_id": "X", "prompt": "p", "canvas_w": 256, "canvas_h": 256}
    try:
        F._refuse_unlocked_frames(base)
        ok("per-frame whole creature refused", False)
    except ValueError as ex:
        ok("per-frame whole creature refused", "wing layer" in str(ex))
    try:
        F._refuse_unlocked_frames({**base, "id": "x", "target_texpath": "a/X_Flying_2"})
        ok("target_texpath seen", False)
    except ValueError:
        ok("target_texpath seen", True)
    F._refuse_unlocked_frames({**base, "plan": "bat", "derive_from": "m"})
    F._refuse_unlocked_frames({**base, "flipbook_override": "ported donor"})
    F._refuse_unlocked_frames({**base, "id": "regen_x_body_v1"})
    ok("wing layer, override and a body row pass", True)
    ok("plan fields carried", {"plan", "flipbook_override"} <= F.KNOWN_ROW_FIELDS and set(F.FLYER_PLANS) == set(G.PLANS))


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        static_cases(d)
        cell_cases()
        book_cases(d)
    wiring()
    queue_cases()
    print("FAILED" if fails else "ALL PASS", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
