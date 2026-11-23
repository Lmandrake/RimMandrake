#!/usr/bin/env python3
"""rot_giants_clickable_live.py -- LIVE test for RIMMANDRAKE_MAKE_GRATH_ELDER_CLICKABLE_ROOT_CELL_BELOW_ITS_PICTURE:
a click on a Rot giant's body selects it, on a list that loads the Rot (mandrake.rm.biomes) by its own dependency
closure. Offline twin: selftest_rot_giants_clickable.py.

  ROT_hugethings_loaded   the running list holds mandrake.rm.biomes AND mandrake.rm.hugethings (the dependency
                          pulled it in), and the loaded RM_HugeThings.dll is this clone's build.
  ROT_click_<defName>     each Rot giant, staged full-grown (jawa/artboard_stage) on the registered calm site, is
                          clicked on every cell of its visible picture through
                          RimMandrake.HugeThings.HugePlantSelectionProbe.ClickPicture (GenUI.ThingsUnderMouse with
                          the Selector's parameters). PASS when every picture cell selects it and no cell of the ring
                          outside the drawn quad does.

Run on a tier list that loads mandrake.rm.biomes WITHOUT naming mandrake.rm.hugethings by hand (modset_builder's
<modDependencies> closure must bring it), with the bridge held:

    python3 src/RimMandrake/TheRot/rot_giants_clickable_live.py [--only RM_AgariluxPrime] [--cell 60,60]

Exit 0 all PASS, 1 a FAIL, 2 could not look (no bridge, site missing, a row UNMEASURED). Writes one JSON record.
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NS = os.path.join(REPO, "src", "RimMandrake", "HugeThings", "northstar")
sys.path.insert(0, NS)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "HugeThings"))
import showcase_common as SC  # noqa: E402
from showcase_plants_live import parse_probe, PROBE  # noqa: E402
import measure_huge_plant_masks as MHPM  # noqa: E402

ITEM = "RIMMANDRAKE_MAKE_GRATH_ELDER_CLICKABLE_ROOT_CELL_BELOW_ITS_PICTURE"
SITE_KEY = "calm"
SNAP_PREFIX = "CODEX_RotGiantClick_"
DEFAULT_CELL = (60, 60)          # the grath elder's picture reaches ~10 cells each side and ~20 north of its root
WAIT = 120


def giants():
    return sorted(p["def"] for p in MHPM.giants())


class RotClick(object):
    def __init__(self, sc, cell, defs):
        self.sc, (self.x, self.z), self.defs = sc, cell, defs

    def loaded(self, sc):
        ok, why = SC.preflight(sc, ("mandrake.rm.biomes", "mandrake.rm.hugethings"))
        return sc.row("ROT_hugethings_loaded", "a list that loads the Rot also loads Huge Things",
                      "PASS" if ok else "UNMEASURED", "MOD" if ok else "HARNESS", why)

    def clear(self, sc):
        x, z = self.x, self.z
        rect = "%d,%d,30,30" % (x - 15, z - 5)
        sc.call("jawa/set_roof_batch", ops="None:%s" % rect)
        sc.call("jawa/destroy_batch", rects=rect, categories="All")
        sc.call("jawa/set_terrain_batch", ops="Soil:%s" % rect)
        return rect

    def click(self, defname):
        def phase(sc):
            rid = "ROT_click_%s" % defname
            crit = "a click on any cell of %s's visible picture selects it" % defname
            rect = self.clear(sc)
            if sc.call("jawa/list_pawns", rect=rect, limit=50).get("pawns"):
                return sc.row(rid, crit, "UNMEASURED", "SITE", "pawns stand in the plot %s" % rect)
            st = sc.call("jawa/artboard_stage", phase="subjects", pause=False, killHostiles=True,
                         ops="id=g|kind=plant|x=%d|z=%d|def=%s|growth=1" % (self.x, self.z, defname))
            ops = st.get("ops") or []
            if not ops or not ops[0].get("ok"):
                return sc.row(rid, crit, "UNMEASURED", "HARNESS", "could not stage: %s" % str(st)[:300])
            sc.ticks(WAIT)
            ok, txt = sc.hook(PROBE, "ClickPicture", "current|%d,%d" % (self.x, self.z))
            p = parse_probe(txt) if ok else {}
            if "pictureCells" not in p:
                return sc.row(rid, crit, "UNMEASURED", "HARNESS", "probe gave no reading: %s" % txt[:400])
            if p.get("selectionOn") != "True":
                return sc.row(rid, crit, "UNMEASURED", "SITE", "plant selection is off in Mod Settings: %s" % txt[:300])
            cells, hits, ring = int(p["pictureCells"]), int(p["hits"]), int(p.get("ringHits", -1))
            status = "UNMEASURED" if cells == 0 or ring < 0 else ("PASS" if hits == cells and ring == 0 else "FAIL")
            return sc.row(rid, crit, status, "MOD" if cells else "HARNESS",
                          "%d/%d picture cells select it (%s first); ring overreach %s/%s; %s"
                          % (hits, cells, p.get("first"), p.get("ringHits"), p.get("ringCells"), txt[:400]))
        return phase


def run(args, bridge, site, ticker=None):
    defs = [d for d in giants() if not args.only or d in args.only]
    rows = ["ROT_hugethings_loaded"] + ["ROT_click_%s" % d for d in defs]
    sc = SC.Showcase(bridge, args.out, "rot_giants_clickable_live.py", ITEM, rows, ticker=ticker)
    cell = tuple(int(v) for v in args.cell.split(",")) if args.cell else DEFAULT_CELL
    sc.rec.update(promise="Rot giants clickable on their body", site_key=SITE_KEY, cell=cell, giants=defs)
    show = RotClick(sc, cell, defs)
    try:
        try:
            sc.rec["site"] = site.begin()
            sc.run_phases([("LOADED", show.loaded, ["ROT_hugethings_loaded"])]
                          + [("CLICK_%s" % d, show.click(d), ["ROT_click_%s" % d]) for d in defs])
        finally:
            sc.rec["site_restore_errors"] = site.restore()
    except Exception as ex:  # noqa: BLE001
        sc.rec["error"] = repr(ex)
    finally:
        sc.rec["finished"] = SC.utc()
        sc.save()
    return sc


def main(argv=None):
    ap = argparse.ArgumentParser(description="The Rot's giants select on a click on their body (live).")
    ap.add_argument("--only", nargs="*", default=None, help="giant defNames to test (default: every Rot giant)")
    ap.add_argument("--cell", default="", help="X,Z of the root cell (default %d,%d)" % DEFAULT_CELL)
    ap.add_argument("--out", default=os.path.join("/mnt/d/ClaudeWork/rimmandrake/showcases",
                                                  "rot_giants_clickable_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args(argv)
    try:
        b, ticker = SC.live_bridge()
    except Exception as ex:  # noqa: BLE001 -- no bridge is "could not look", never a mod FAIL
        print("UNMEASURED HARNESS: no live bridge: %r" % ex)
        return 2
    sc = run(a, b, SC.LiveSite(b.call, SITE_KEY, SNAP_PREFIX), ticker)
    print("wrote %s  summary %s" % (a.out, sc.summary()))
    return sc.exit_code()


if __name__ == "__main__":
    sys.exit(main())
