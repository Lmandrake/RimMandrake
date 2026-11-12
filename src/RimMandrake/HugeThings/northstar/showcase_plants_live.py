"""showcase_plants_live.py -- the GIANT PLANT promise of HugeThings, its own demonstration on its own restored site
(ANSWERS_OWNER.md answers 1-2, 2026-11-11): what you SEE of a giant plant is what is solid (trunk/root) and what is
open (cap space you walk under), the selection covers the picture, and growth may seal a door until the plant is cut.

  GROWN      stage RM_Nogtyl at growth 1 (jawa/artboard_stage, STAGED), 120 ticks; MapComponent_HugeFootprints
             .DebugPlantState reads it realized; trunk_live.judge on the RM_HugeTrunkBlocker counts (the measured
             contact counts of TheRot/Patches/RotGiants_HugeFootprint.xml, never a hand number).
  BODY       trunk/root cells SOLID: a colonist cannot path onto sampled blocker cells; cap cells OPEN: cells on the
             drawn picture that hold no blocker are reachable. Paused path reads (jawa/order_pawn waitTicks=0, then
             stop_job), nothing walks. The picture comes from HugePlantSelectionProbe (vanilla Plant.Print replayed:
             growth-scaled quad, flip, variant, the variant's art-measured opaque box), NOT artboard_stage's drawRect,
             which is Graphic.drawSize (1x1 for a giant: plants scale by plant.visualSizeRange).
  SELECTION  HugePlantSelectionProbe.ClickPicture clicks every cell of the visible picture through GenUI.ThingsUnderMouse
             with the Selector's parameters: PASS when every picture cell selects the plant, FAIL on any miss.
  DOOR       orchestrates trunk_doors_live.py (its own registered-site load, scene-begin snapshot and restore) AFTER this
             showcase's site is restored: growth seals a door until RM_CutHugePlantFromTrunk cuts it.

Gated like the titan showcase (a failed phase leaves the later ones UNMEASURED). LIVE: needs the game and the bridge;
offline proof is selftest_showcases.py.
"""
import argparse
import json
import os
import re
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
PROBE = "RimMandrake.HugeThings.HugePlantSelectionProbe"


def parse_probe(txt):
    """key=value tokens of HugePlantSelectionProbe.ClickPicture; picture/quad as float tuples."""
    d = dict(tok.split("=", 1) for tok in txt.split() if "=" in tok)
    try:
        a, b = d["picture"].split("..")
        d["picture"] = tuple(float(v) for v in a.split(",") + b.split(","))
    except (KeyError, ValueError):
        d.pop("picture", None)
    return d


def picture_cells(p):
    """Cells whose centre lies on the visible picture box (x0,z0,x1,z1), south to north."""
    try:
        x0, z0, x1, z1 = p["picture"]
    except (KeyError, TypeError, ValueError):
        return []
    import math
    xs = range(int(math.ceil(x0 - 0.5)), int(math.floor(x1 - 0.5)) + 1)
    zs = range(int(math.ceil(z0 - 0.5)), int(math.floor(z1 - 0.5)) + 1)
    return [(x, z) for z in zs for x in xs]


def door_error_class(err):
    """trunk_doors_live stores repr(exc): AssertionError('SITE: ...') for a tagged require, KeyError(...) for a crash.
    A SITE/HARNESS tag anywhere, or any exception that is not an AssertionError, is no verdict on the mod."""
    m = re.search(r"['\"](SITE|HARNESS|MOD)\b", err)
    if m:
        return None if m.group(1) == "MOD" else m.group(1)
    return "HARNESS" if err and not err.startswith("AssertionError") else None


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
        self.pic, self.pic_txt = None, ""

    def grown(self, sc):
        okp, why = SC.preflight(sc, ("mandrake.rm.hugethings",))
        if not okp:
            return sc.row("PLANT_grown", "the loaded build is this clone's", "UNMEASURED", "HARNESS", why)
        sc.rec["preflight"] = why
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
        self.read_picture(sc)
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
        if not self.pic:
            return sc.row("PLANT_cap_open", "cap cells under the picture are open", "UNMEASURED", "HARNESS",
                          "no picture from HugePlantSelectionProbe: %s" % self.pic_txt[:300])
        solidset = set(self.blockers)
        cap = [c for c in picture_cells(self.pic)[::-1] if c not in solidset and c != (self.x, self.z)]
        cap = cap[::max(1, len(cap) // SAMPLES)][:SAMPLES]
        opened = [(c, sc.reach(self.colonist, c[0], c[1])) for c in cap]
        closed = [c for c, r in opened if r is not True]
        st = "UNMEASURED" if not opened or any(r is None for _, r in opened) else ("FAIL" if closed else "PASS")
        return sc.row("PLANT_cap_open", "cells under the picture that are not trunk are open to walking pawns", st,
                      "MOD" if st != "UNMEASURED" else "HARNESS", "picture %s; %s" % (self.pic.get("picture"), opened))

    def read_picture(self, sc):
        ok, self.pic_txt = sc.hook(PROBE, "ClickPicture", "current|%d,%d" % (self.x, self.z))
        self.pic = parse_probe(self.pic_txt) if ok else None

    def selection(self, sc):
        crit = "a click on any cell of the visible picture selects the plant (GenUI.ThingsUnderMouse, Selector parameters)"
        self.read_picture(sc)   # fresh: BODY's path reads must not have changed anything, and this shows it
        p = self.pic
        if not p or "pictureCells" not in p:
            return sc.row("PLANT_selection", crit, "UNMEASURED", "HARNESS", "probe gave no reading: %s" % self.pic_txt[:400])
        if p.get("selectionOn") != "True":
            return sc.row("PLANT_selection", crit, "UNMEASURED", "SITE", "plant selection is off in Mod Settings: %s" % self.pic_txt)
        cells, hits, ring_hits = int(p["pictureCells"]), int(p["hits"]), int(p.get("ringHits", -1))
        # ring = cells wholly outside the drawn quad: a click there selecting the plant is a selection box bigger than the art
        st = "UNMEASURED" if cells == 0 or ring_hits < 0 else ("PASS" if hits == cells and ring_hits == 0 else "FAIL")
        return sc.row("PLANT_selection", crit, st, "MOD" if cells else "HARNESS",
                      "%d/%d picture cells select it (%s first); ring overreach %s/%s; %s"
                      % (hits, cells, p.get("first"), p.get("ringHits"), p.get("ringCells"), self.pic_txt[:600]))

    def door(self, sc):
        rec = self.door_runner()
        restored = (rec.get("restoration") or {}).get("ok") is True
        err = str(rec.get("error") or "")
        d = "ok=%s error=%s restoration=%s exit=%s" % (rec.get("ok"), err[:200], str(rec.get("restoration"))[:200], rec.get("_exit"))
        if rec.get("ok") is True and restored:
            return sc.row("PLANT_door_seal", "growth seals a door until the plant is cut (trunk_doors_live.py)", "PASS", "MOD", d)
        cls = door_error_class(err)
        if rec.get("ok") is None or cls or not restored:
            return sc.row("PLANT_door_seal", "growth seals a door until the plant is cut", "UNMEASURED", cls or "HARNESS",
                          "trunk_doors_live gave no MOD verdict: %s tail %s" % (d, rec.get("_tail", "")[-300:]))
        return sc.row("PLANT_door_seal", "growth seals a door until the plant is cut (trunk_doors_live.py)", "FAIL", "MOD", d)

def run(args, bridge, site, ticker=None, door_runner=None):
    """bridge: .call(tool, **kw) -> dict; site: .begin()/.restore(); door_runner() -> trunk_doors_live record."""
    no_door = bool(getattr(args, "no_door", False))
    required = [r for r in REQUIRED if not (no_door and r in ROWS["DOOR"])]
    sc = SC.Showcase(bridge, args.out, "showcase_plants_live.py", ITEM, required, ticker=ticker)
    cell = tuple(int(v) for v in args.cell.split(",")) if args.cell else DEFAULT_CELL
    sc.rec.update(promise="giant plants", site_key=SITE_KEY, snapshot_prefix=SNAP_PREFIX, cell=cell,
                  door="skipped (--no-door: BLOCKED, proven separately or not at all)" if no_door else "run")
    door_out = os.path.splitext(args.out)[0] + "_doors.json"
    show = PlantShowcase(sc, cell, door_runner or (lambda: door_subprocess(door_out)))
    try:
        try:
            sc.rec["site"] = site.begin()
            sc.run_phases([("GROWN", show.grown, ROWS["GROWN"]), ("BODY", show.body, ROWS["BODY"]),
                           ("SELECTION", show.selection, ROWS["SELECTION"])])
        finally:
            sc.rec["site_restore_errors"] = site.restore()
        sc.stopped_by = None if sc.stopped_by in (None, "SELECTION") else sc.stopped_by  # DOOR needs no state of ours
        if sc.rec["site_restore_errors"] and sc.stopped_by is None:
            sc.stopped_by = "SITE_RESTORE"   # never stage a second scene on an unrestored site
        if not no_door:
            sc.scene += 1                # trunk_doors_live loads its own registered site: a new scene, a new clock
            sc.run_phases([("DOOR", show.door, ROWS["DOOR"])])
            sc.phases[-1]["foreignClock"] = "trunk_doors_live.py loads and restores its own registered site"
    except Exception as ex:  # noqa: BLE001
        sc.rec["error"] = repr(ex)
    finally:
        sc.rec["finished"] = SC.utc()
        sc.save()
    return sc


def main(argv=None):
    ap = argparse.ArgumentParser(description="HugeThings GIANT PLANT promise: grown, solid trunk, open cap, selection, door seal.")
    ap.add_argument("--cell", default="", help="X,Z of the giant (default %d,%d)" % DEFAULT_CELL)
    ap.add_argument("--no-door", action="store_true",
                    help="skip the DOOR phase (trunk_doors_live.py) and drop PLANT_door_seal from the required rows")
    ap.add_argument("--out", default=os.path.join("/mnt/d/ClaudeWork/rimmandrake/showcases",
                                                  "showcase_plants_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args(argv)
    try:
        b, ticker = SC.live_bridge()
    except Exception as ex:  # noqa: BLE001 -- no bridge is "could not ask", never a mod FAIL
        print("UNMEASURED HARNESS: no live bridge: %r" % ex)
        return 2
    sc = run(a, b, SC.LiveSite(b.call, SITE_KEY, SNAP_PREFIX), ticker)
    print("wrote %s  summary %s" % (a.out, sc.summary()))
    return sc.exit_code()


if __name__ == "__main__":
    sys.exit(main())
