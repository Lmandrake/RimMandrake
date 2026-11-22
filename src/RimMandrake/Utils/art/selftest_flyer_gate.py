#!/usr/bin/env python3
"""selftest_flyer_gate.py - the flyer gate can fail where it must (FLYER_STABLE_BODY_GATE_1).

Planted, in memory and in a temp dir, offline:
  STATIC   a body with narrow wings passes; a sliver N/S (G2), a canvas-filling body (G4), a wing-only speck field (G1)
           and a missing facing (UNMEASURED) are each refuted by name
  CELL     a locked def is ✓, a refuted one ✗, a clean static with no book partial; a non-flyer has no cell
  BOOK     flyer_gate.flipbook_rc returns the gate's exit code, and a set with no config is 2, not a pass; the
           Uvak config passes and a planted body shift on a scratch copy of its frames does not
  SHEET    a real art_sheet build shows the cell, drops a failing set's frames, and serve_gated refuses a planted lane
  ENACT    a real enact dry run: a keep of a ✗ flyer installs nothing and is a conflict
  FLIGHT   phase_flight makes no bridge call unattended; present, one read-only pawn_flight report
  QUEUE    fill_queue refuses a per-frame whole-creature row, passes a wing layer, passes a named override
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

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


def withhold_cases():
    live, render = {"kind": "live"}, {"kind": "artpipe"}
    keep = dict(G._rc)
    G._rc.update({"Sketto": 1, "Uvak": 0})
    ok("a failing set shows no frames", G.withhold_books(["RSW_Sketto"], [live, render])[0] == [])
    ok("and says so", "Sketto (exit 1)" in G.withhold_books(["RSW_Sketto"], [live])[1])
    ok("a passing set shows its frames", G.withhold_books(["RSW_Uvak"], [live, render]) == ([live, render], ""))
    plan = G.plan_rows()
    free = next(k for k in plan if k not in G.DEF_SETS)
    ok("a flyer with no set keeps old frames, loses a new render", G.withhold_books([free], [live, render])[0] == [live])
    ok("a non-flyer is untouched", G.withhold_books(["RM_Muffalo"], [render]) == ([render], ""))
    G._rc.clear()
    G._rc.update(keep)


def sheet_cases(d: Path):
    """A real sheet build (--allow-failing: a probe has no decisions file), then the serve door on it."""
    import serve_gated as SG
    out, snap = d / "flyer_gate_selftest.html", G.REPO / "infrastructure/state/art/sheets/flyer_gate_selftest.snapshot.json"
    try:
        rc = subprocess.run([sys.executable, str(HERE / "art_sheet.py"), "--subjects", "RSW_Uvak", "RSW_Sketto", "--name",
                             "flyer_gate_selftest", "--label", "selftest", "--allow-failing", "selftest", "--sheet-only",
                             "--out", str(out)], capture_output=True, cwd=G.REPO, timeout=500).returncode
    finally:
        snap.unlink(missing_ok=True)
    ok("a real sheet builds", rc == 0 and out.exists(), rc)
    t = out.read_text(errors="replace")
    fails_now = G.book_rc("Sketto") != 0
    ok("the built sheet shows both flyers' cells", t.count("flyer: ") >= 2)
    ok("a passing set's lane is on the built sheet", '"res": "_flip:swanimals/Uvak/Uvak_Flying_"' in t)
    ok("a failing set's frames are not", ('_flip:swanimals/Sketto/Sketto_Flying_"' not in t) == fails_now)
    ok("and the row says why", ("flip-book withheld: Sketto" in t) == fails_now)
    ok("the serve door passes the real sheet", G.sheet_refusal(t) == "" or not fails_now)
    planted = d / "planted.html"
    planted.write_text(t + '"res": "_flip:swanimals/Sketto/Sketto_Flying_"')
    keep = dict(G._rc)
    G._rc["Sketto"] = 1
    err = StringIO()
    with redirect_stderr(err):
        rc = SG.prereview_gate(planted)
    G._rc.clear()
    G._rc.update(keep)
    ok("serve refuses a sheet with a failing lane", rc == 4 and "Sketto (exit 1)" in err.getvalue(), rc)


def enact_cases():
    """A real enact dry run on selftest_enact's fixture: RM_Foo's keep installs until the gate refutes the flyer."""
    import artledger as L
    import enact as E
    import selftest_enact as T
    F = T.build(T.SCRATCH / f"flyer_gate_selftest_{os.getpid()}")
    L.MARK_ROOT = F["root"]
    try:
        P = E.enact(F["decisions"], apply=False, holds=["vine"], no_deploy=True)["plan"]
        ok("control: the keep installs", any(i["row"] == "RM_Foo" for i in P["install"]))
        G._cache = {"RM_Foo": {"flipbook": "none", "static_fails": ["G2 x"]}}
        P = E.enact(F["decisions"], apply=False, holds=["vine"], no_deploy=True)["plan"]
        ok("a keep of a ✗ flyer installs nothing", not any(i["row"] == "RM_Foo" for i in P["install"]))
        ok("and is a conflict, not a todo", any(c.startswith("RM_Foo: keep refused") for c in P["conflicts"])
           and not any(c.startswith("RM_Foo: keep") for c in P["todo"]))
    finally:
        G._cache = None
        shutil.rmtree(F["root"], ignore_errors=True)


def flight_cases():
    """Criterion 4: the only flight check is a read-only Pawn_FlightTracker report, and it needs him present."""
    sys.path.insert(0, str(HERE.parent / "modcheck"))
    import l1_donor_off_round as M

    def run(present):
        R = M.Round.__new__(M.Round)
        calls, rows = [], []
        R.man, R.args = {"flyers": ["RSW_Sketto"]}, SimpleNamespace(owner_present=present)
        R.site = lambda *a: (0, 0, 8, 8)
        R.row = lambda rid, st, cls, det: rows.append((rid, st, cls))
        R.call = lambda tool, **kw: calls.append((tool, kw)) or {
            "pawns": [{"canEverFly": True, "maxFlightTimeStat": 5.0, "flightState": "Grounded"}]}
        R.phase_flight()
        return calls, rows
    calls, rows = run(None)
    ok("unattended: no bridge call, UNMEASURED", not calls and rows == [("FLIGHT_RSW_Sketto", "UNMEASURED", "OWNER")])
    calls, rows = run("his words")
    fl = [kw for tool, kw in calls if tool == "jawa/pawn_flight"]
    ok("present: a read only", rows[0][1] == "PASS" and len(fl) == 1 and fl[0]["action"] == "report"
       and fl[0]["maintainTicks"] == 0 and fl[0]["unpause"] is False, fl)
    src = (G.REPO / "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlightTools.cs").read_text()
    ok("the tool reads the tracker", "flight" in src.lower() and "'report' (read-only, default)" in src)


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
        sheet_cases(d)
    withhold_cases()
    enact_cases()
    flight_cases()
    queue_cases()
    print("FAILED" if fails else "ALL PASS", fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
