"""showcase_plants_live.py -- the GIANT PLANT promise of HugeThings, its own demonstration on its own restored site
(ANSWERS_OWNER.md answers 1-2, 2026-11-11): what you SEE of a giant plant is what is solid (trunk/root) and what is
open (cap space you walk under), the selection covers the picture, and growth may seal a door until the plant is cut.

  GROWN      stage RM_Nogtyl at growth 1 (jawa/artboard_stage, STAGED), 120 ticks; MapComponent_HugeFootprints
             .DebugPlantState reads it realized; trunk_live.judge on the RM_HugeTrunkBlocker counts (the measured
             contact counts of TheRot/Patches/RotGiants_HugeFootprint.xml, never a hand number).
  BODY       trunk/root cells SOLID: a colonist cannot path onto sampled blocker cells; cap cells OPEN: cells under the
             plant's drawRect (artboard_stage readBack, world units) that hold no blocker are reachable. Paused path
             reads (jawa/order_pawn waitTicks=0, then stop_job), nothing walks.
  SELECTION  CompHugeFootprint.SelectRect() has no bridge/static instrument: written UNMEASURED/HARNESS honestly, with
             the drawRect recorded as the picture to compare against when one exists.
  DOOR       orchestrates trunk_doors_live.py (its own registered-site load, scene-begin snapshot and restore) AFTER this
             showcase's site is restored: growth seals a door until RM_CutHugePlantFromTrunk cuts it.

Gated like the titan showcase (a failed phase leaves the later ones UNMEASURED). LIVE: needs the game and the bridge;
offline proof is selftest_showcases.py.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import showcase_common as SC  # noqa: E402
import trunk_live as TL  # noqa: E402

ITEM = "RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES"
SNAP_PREFIX = "CODEX_ShowcasePlant_"
SITE_KEY = "calm"
DEFAULT_CELL = (40, 200)             # away from trunk_doors_live's workshop rect 90,90,96,30 and the titan lane
FIELDS = tuple(TL.NEED)
ROWS = dict(GROWN=["PLANT_grown"], BODY=["PLANT_trunk_solid", "PLANT_cap_open"], SELECTION=["PLANT_selection"],
            DOOR=["PLANT_door_seal"])
REQUIRED = [r for k in ("GROWN", "BODY", "SELECTION", "DOOR") for r in ROWS[k]]
SAMPLES = 6


def door_subprocess(out):
    """Run trunk_doors_live.py --out <out> and return its record (it loads/restores its own site)."""
    p = subprocess.run([sys.executable, os.path.join(HERE, "trunk_doors_live.py"), "--out", out],
                       capture_output=True, text=True, timeout=530)
    try:
        with open(out, encoding="utf-8") as f:
            rec = json.load(f)
    except (OSError, ValueError):
        rec = {}
    rec["_exit"], rec["_tail"] = p.returncode, (p.stdout + p.stderr)[-600:]
    return rec


class PlantShowcase(object):
    def __init__(self, sc, cell, door_runner):
        self.sc, (self.x, self.z), self.door_runner = sc, cell, door_runner
        self.draw, self.blockers, self.colonist = None, [], None

    def grown(self, sc):
        bad = TL.settings_ok(dict((f, sc.call("jawa/mod_settings_field", typeName=SC.SETTINGS, action="get", field=f)
                                   .get("value")) for f in FIELDS))
        if bad:
            return sc.row("PLANT_grown", "a full-grown RM_Nogtyl with its measured footprint", "UNMEASURED", "SITE",
                          "settings not at the shipped trunk defaults: %s" % bad)
        x, z = self.x, self.z
        clear = "%d,%d,30,30" % (x - 15, z - 15)
        if (sc.call("jawa/list_pawns", rect=clear, limit=50).get("pawns") or []):
            return sc.row("PLANT_grown", "a full-grown RM_Nogtyl", "UNMEASURED", "SITE", "pawns stand in the plot %s" % clear)
        sc.call("jawa/set_roof_batch", ops="None:%s" % clear)
        sc.call("jawa/destroy_batch", rects=clear, categories="All")
        sc.call("jawa/set_terrain_batch", ops="Soil:%s" % clear)
        st = sc.call("jawa/artboard_stage", phase="subjects", pause=False, killHostiles=True,
                     ops="id=g|kind=plant|x=%d|z=%d|def=%s|growth=1" % (x, z, TL.GIANT))
        ops = st.get("ops") or []
        sc.rec.setdefault("staged", []).append("RM_Nogtyl growth=1 at %d,%d (artboard_stage)" % (x, z))
        if not ops or not ops[0].get("ok"):
            return sc.row("PLANT_grown", "a full-grown RM_Nogtyl", "UNMEASURED", "HARNESS", "could not stage: %s" % str(st)[:300])
        self.draw = ops[0].get("drawRect")
        sc.ticks(TL.WAIT)
        around_r, south_r = TL.rects(x, z)
        rows = sc.things(around_r, TL.BLOCKER)
        south = sc.things(south_r, TL.BLOCKER)
        self.blockers = [(t.get("x"), t.get("z")) for t in rows or []]
        _, probe = sc.hook(TL.MC, "DebugPlantState", "current|%d,%d" % (x, z))
        status, d = TL.judge(None if rows is None else len(rows), None if south is None else len(south),
                             TL.allowed_counts(), probe[:500])
        return sc.row("PLANT_grown", "a full-grown RM_Nogtyl with its measured trunk footprint", status,
                      "MOD" if status != "UNMEASURED" else "HARNESS", d)

    def pick_colonist(self, sc):
        for p in sc.call("jawa/list_pawns", rect=SC.MAP_RECT, limit=1000).get("pawns") or []:
            if p.get("isPlayer") and p.get("spawned") and not p.get("dead") and not p.get("downed") \
                    and p.get("intelligence") == "Humanlike":
                return p.get("id")
        return None

    def body(self, sc):
        self.colonist = self.pick_colonist(sc)
        if not self.colonist:
            sc.row("PLANT_trunk_solid", "trunk/root cells are solid", "UNMEASURED", "SITE", "no free colonist to path with")
            return sc.row("PLANT_cap_open", "cap cells are open", "UNMEASURED", "SITE", "no free colonist")
        solid = [(c, sc.reach(self.colonist, c[0], c[1])) for c in self.blockers[:SAMPLES]]
        bad = [c for c, r in solid if r is not False]
        st = "UNMEASURED" if not solid or any(r is None for _, r in solid) else ("FAIL" if bad else "PASS")
        sc.row("PLANT_trunk_solid", "a colonist cannot path onto the trunk/root (blocker) cells", st,
               "MOD" if st != "UNMEASURED" else "HARNESS", "colonist %s; %s" % (self.colonist, solid))
        d = self.draw or {}
        try:
            x0, z0, w, h = int(d["x"] + 0.999), int(d["z"] + 0.999), int(d["w"]), int(d["h"])
        except (KeyError, TypeError, ValueError):
            return sc.row("PLANT_cap_open", "cap cells under the picture are open", "UNMEASURED", "HARNESS",
                          "no drawRect from artboard_stage: %s" % d)
        solidset = set(self.blockers)
        cap = [(cx, cz) for cz in range(z0 + h - 2, z0 - 1, -1) for cx in range(x0, x0 + w - 1)
               if (cx, cz) not in solidset and (cx, cz) != (self.x, self.z)]
        cap = cap[::max(1, len(cap) // SAMPLES)][:SAMPLES]
        opened = [(c, sc.reach(self.colonist, c[0], c[1])) for c in cap]
        closed = [c for c, r in opened if r is not True]
        st = "UNMEASURED" if not opened or any(r is None for _, r in opened) else ("FAIL" if closed else "PASS")
        return sc.row("PLANT_cap_open", "cells under the picture that are not trunk are open to walking pawns", st,
                      "MOD" if st != "UNMEASURED" else "HARNESS", "drawRect %s; %s" % (d, opened))

    def selection(self, sc):
        return sc.row("PLANT_selection", "the selection rect covers the picture", "UNMEASURED", "HARNESS",
                      "no instrument: CompHugeFootprint.SelectRect() is an instance method with no bridge or static hook; "
                      "picture drawRect for the comparison: %s" % (self.draw,))

    def door(self, sc):
        rec = self.door_runner()
        restored = (rec.get("restoration") or {}).get("ok") is True
        err = str(rec.get("error") or "")
        d = "ok=%s error=%s restoration=%s exit=%s" % (rec.get("ok"), err[:200], str(rec.get("restoration"))[:200], rec.get("_exit"))
        if rec.get("ok") is True and restored:
            return sc.row("PLANT_door_seal", "growth seals a door until the plant is cut (trunk_doors_live.py)", "PASS", "MOD", d)
        cls = next((c for c in ("SITE", "HARNESS") if err.startswith(c)), None)
        if rec.get("ok") is None or cls or not restored:
            return sc.row("PLANT_door_seal", "growth seals a door until the plant is cut", "UNMEASURED", cls or "HARNESS",
                          "trunk_doors_live gave no MOD verdict: %s tail %s" % (d, rec.get("_tail", "")[-300:]))
        return sc.row("PLANT_door_seal", "growth seals a door until the plant is cut (trunk_doors_live.py)", "FAIL", "MOD", d)

def run(args, bridge, site, ticker=None, door_runner=None):
    """bridge: .call(tool, **kw) -> dict; site: .begin()/.restore(); door_runner() -> trunk_doors_live record."""
    sc = SC.Showcase(bridge, args.out, "showcase_plants_live.py", ITEM, REQUIRED, ticker=ticker)
    cell = tuple(int(v) for v in args.cell.split(",")) if args.cell else DEFAULT_CELL
    sc.rec.update(promise="giant plants", site_key=SITE_KEY, snapshot_prefix=SNAP_PREFIX, cell=cell)
    door_out = os.path.splitext(args.out)[0] + "_doors.json"
    show = PlantShowcase(sc, cell, door_runner or (lambda: door_subprocess(door_out)))
    try:
        try:
            sc.rec["site"] = site.begin()
            sc.run_phases([("GROWN", show.grown, ROWS["GROWN"]), ("BODY", show.body, ROWS["BODY"])])
        finally:
            sc.rec["site_restore_errors"] = site.restore()
        # SELECTION has no instrument (always UNMEASURED); it is recorded, not a gate on DOOR, which needs no state of ours.
        show.selection(sc)
        if sc.rec["site_restore_errors"] and sc.stopped_by is None:
            sc.stopped_by = "SITE_RESTORE"   # never stage a second scene on an unrestored site
        sc.run_phases([("DOOR", show.door, ROWS["DOOR"])])
    except Exception as ex:  # noqa: BLE001
        sc.rec["error"] = repr(ex)
    finally:
        sc.rec["finished"] = SC.utc()
        sc.save()
    return sc


def main(argv=None):
    ap = argparse.ArgumentParser(description="HugeThings GIANT PLANT promise: grown, solid trunk, open cap, selection, door seal.")
    ap.add_argument("--cell", default="", help="X,Z of the giant (default %d,%d)" % DEFAULT_CELL)
    ap.add_argument("--out", default=os.path.join("/mnt/d/ClaudeWork/rimmandrake/showcases",
                                                  "showcase_plants_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args(argv)
    b, ticker = SC.live_bridge()
    sc = run(a, b, SC.LiveSite(b.call, SITE_KEY, SNAP_PREFIX), ticker)
    print("wrote %s  summary %s" % (a.out, sc.summary()))
    return 0 if sc.summary().get("gameplay_pass") else 1


if __name__ == "__main__":
    sys.exit(main())
