"""Offline selftest of showcase_titan_live.py / showcase_plants_live.py on a fake bridge (no game):
the titan phases run CROSSING -> DEATH -> CROWD with ordered tick stamps; a failed crossing leaves DEATH and CROWD
UNMEASURED (never run); the plant and titan showcases are separate entrypoints with separate site snapshots; --help works.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import showcase_common as SC  # noqa: E402
import showcase_titan_live as TT  # noqa: E402
import showcase_plants_live as PP  # noqa: E402


class FakeSite(object):
    def __init__(self, prefix):
        self.prefix, self.began, self.restored = prefix, 0, 0

    def begin(self):
        self.began += 1
        return dict(snapshot=self.prefix + "fake")

    def restore(self):
        self.restored += 1
        return []


class Fake(object):
    """A tiny world: a clock, settings, things in the lane, one walking titan, a SiteReport."""

    def __init__(self, stuck=False, misses=0, selection_on=True, ring_hits=0):
        self.tick, self.stuck, self.settings, self.calls = 1000, stuck, {}, []
        self.misses, self.selection_on, self.ring_hits = misses, selection_on, ring_hits
        self.things = [dict(def_="Wall", x=TT.WALL_X, z=z) for z in TT.STAGED_Z] + \
                      [dict(def_="Wall", x=x, z=z) for x, z in TT.RING] + \
                      [dict(def_="Plant_TreeOak", x=TT.TREE_X, z=z) for z in TT.STAGED_Z[::3]] + \
                      [dict(def_="RM_Nogtyl", x=TT.GIANT[0], z=TT.GIANT[1])]
        self.titan, self.sites, self.blockers = None, [], [(40 + dx, 200 + dz) for dx in (-2, -1, 0, 1, 2) for dz in (0, 1)]

    def advance(self, n):
        self.tick += n
        t = self.titan
        if t and not t["dead"] and not self.stuck:
            for _ in range(n // 40):
                t["x"] += 1
                self.things = [th for th in self.things if not (th["x"] == t["x"] and abs(th["z"] - t["z"]) <= 6)
                               or th["def_"] == "Filth_RubbleRock"]
                if t["x"] % 5 == 0:
                    self.things.append(dict(def_="Filth_RubbleRock", x=t["x"], z=t["z"]))
        for s in self.sites:
            if s["scav"]:
                s["atSite"] = True

    def report(self):
        return "sites=%d" % len(self.sites) + "".join(
            " | %s at %d,%d meat=100 eaten=0 scav=%d camp=%d%s" % (
                s["id"], s["x"], s["z"], s["scav"], s["camp"],
                "".join(" S[RM_Scav tier=T1 homedHere=True pred=True spawned=True atSite=%s]" % s["atSite"]
                        for _ in range(s["scav"]))) for s in self.sites)

    def call(self, tool, **kw):
        self.calls.append(tool)
        if tool == "jawa/site_state":
            return dict(success=True, ticksGame=self.tick)
        if tool == "rimworld/step_game_ticks":
            self.advance(kw["ticks"])
            return dict(success=True)
        if tool == "jawa/mod_settings_field":
            if kw["action"] == "set":
                self.settings[kw["field"]] = kw["value"]
            return dict(success=True, value=self.settings.get(kw["field"], {"plantTrunkScale": "1"}.get(kw["field"], "True")))
        if tool == "jawa/list_things":
            x, z, w, h = (int(v) for v in kw["rect"].split(","))
            if kw.get("defName") == "RM_HugeTrunkBlocker":
                rows = [dict(def_="RM_HugeTrunkBlocker", x=a, z=b) for a, b in self.blockers
                        if x <= a < x + w and z <= b < z + h]
            else:
                rows = [t for t in self.things if x <= t["x"] < x + w and z <= t["z"] < z + h]
            rows = [dict(t, def_=None, **{"def": t["def_"]}) for t in rows]
            return dict(success=True, isCompleteList=True, countMatched=len(rows), things=rows)
        if tool == "jawa/list_pawns":
            ps = [dict(id="Col1", x=10, z=10, spawned=True, dead=False, downed=False, isPlayer=True, intelligence="Humanlike")]
            if self.titan and not self.titan["dead"]:
                ps.append(dict(self.titan, spawned=True, downed=False, isPlayer=False))
            if kw["rect"] != SC.MAP_RECT:
                ps = []
            return dict(success=True, pawns=ps)
        if tool == "jawa/spawn_pawn":
            self.titan = dict(id="Titan1", x=kw["x"], z=kw["z"], dead=False, hp=1000)
            return dict(success=True, pawns=[dict(id="Titan1")])
        if tool == "jawa/damage":
            self.titan["hp"] -= kw["amount"]
            if self.titan["hp"] <= 0:
                self.titan["dead"] = True
                self.sites.append(dict(id="RM_TitanicCorpseSite1", x=self.titan["x"], z=self.titan["z"], scav=0, camp=0,
                                       atSite=False))
            return dict(success=True)
        if tool == "jawa/static_call":
            m = kw["method"]
            if m == "SiteReport":
                return dict(success=True, result=self.report())
            if m == "SiteDailyStep":
                for s in self.sites:
                    s["scav"], s["camp"] = 2, 1
                return dict(success=True, result="stepped %d" % len(self.sites))
            if m == "DebugPlantState":
                return dict(success=True, result="registered=True realized=True")
            if m == "ClickPicture":   # a 12-cell Nogtyl quad; visible box 37.4..44.6 x 200.2..211.8 = 8 x 12 = 96 cells
                return dict(success=True, result=(
                    "plant=Plant_RM_Nogtyl1 growth=1 selectionOn=%s variant=Nogtyl_A flip=False quad=34.5,200 side=12 "
                    "picture=37.4,200.2..44.6,211.8 selectRect=(37,200)-(44,211) pictureCells=96 hits=%d first=90 "
                    "missed=%s ringCells=60 ringHits=%d aheadOfPlant=none"
                    % (self.selection_on, 96 - self.misses, "none" if not self.misses else "44,211", self.ring_hits)))
            return dict(success=True, result="FAIL unknown %s" % m)
        if tool == "jawa/artboard_stage":
            return dict(success=True, ops=[dict(ok=True, drawRect=dict(x=36.0, z=199.0, w=9.0, h=9.0))])
        if tool == "jawa/order_pawn":
            return dict(success=True, pawns=[dict(canReach=(kw["x"], kw["z"]) not in self.blockers)])
        return dict(success=True)


class Args(object):
    def __init__(self, out, cell=""):
        self.out, self.cell = out, cell


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="showcases_")
        self._pf = SC.preflight
        SC.preflight = lambda sc, pk: (True, "fake preflight")

    def tearDown(self):
        SC.preflight = self._pf

    def titan(self, stuck):
        f = Fake(stuck=stuck)
        out = os.path.join(self.tmp, "titan_%s.json" % stuck)
        site = FakeSite(TT.SNAP_PREFIX)
        TT.run(Args(out), f, site, ticker=f.advance)
        with open(out) as fh:
            return json.load(fh), site, f

    def test_titan_phases_run_in_order_with_stamps(self):
        rec, site, f = self.titan(False)
        st = dict((r["id"], r["status"]) for r in rec["rows"])
        self.assertEqual([p["phase"] for p in rec["phases"]], ["PRE", "CROSSING", "DEATH", "CROWD"], rec["phases"])
        self.assertTrue(all(v == "PASS" for v in st.values()), [(r["id"], r["status"], r["detail"]) for r in rec["rows"]])
        ticks = [(p["startTick"], p["endTick"]) for p in rec["phases"]]
        self.assertTrue(all(type(a) is int and type(b) is int and a <= b for a, b in ticks), ticks)
        self.assertTrue(all(ticks[i][1] <= ticks[i + 1][0] for i in range(len(ticks) - 1)), ticks)
        self.assertLess(ticks[1][0], ticks[1][1])            # the crossing took game time
        self.assertTrue(rec["summary"]["phases_in_order"] and rec["summary"]["gameplay_pass"], rec["summary"])
        self.assertEqual((site.began, site.restored), (1, 1))
        # the crossing call came before the death call, and the death before the crowd's daily step
        self.assertLess(f.calls.index("jawa/spawn_pawn"), f.calls.index("jawa/damage"))

    def test_failed_crossing_gates_death_and_crowd(self):
        rec, site, f = self.titan(True)
        st = dict((r["id"], r["status"]) for r in rec["rows"])
        self.assertEqual(st["CROSSING_walked"], "FAIL")
        for rid in ("DEATH_titan_dies", "DEATH_corpse_site", "CROWD_arrives", "CROWD_targets_site"):
            self.assertEqual(st[rid], "UNMEASURED", rid)
        by = dict((p["phase"], p) for p in rec["phases"])
        self.assertEqual((by["DEATH"]["status"], by["CROWD"]["status"]), ("UNMEASURED", "UNMEASURED"))
        self.assertIsNone(by["DEATH"]["startTick"])
        self.assertEqual(by["DEATH"]["gatedBy"], "CROSSING")
        self.assertNotIn("jawa/damage", f.calls)              # death was never driven
        self.assertNotIn("SiteDailyStep", str(rec["calls"]))
        self.assertFalse(rec["summary"]["gameplay_pass"])
        self.assertEqual(site.restored, 1)                    # restore still ran

    def test_plants_rows_and_door_orchestration(self):
        f = Fake()
        out = os.path.join(self.tmp, "plants.json")
        site, door = FakeSite(PP.SNAP_PREFIX), []

        def door_runner():
            door.append(site.restored)                       # the plant site is already restored when the door scene runs
            return dict(ok=True, restoration=dict(ok=True))
        PP.run(Args(out, "40,200"), f, site, ticker=f.advance, door_runner=door_runner)
        with open(out) as fh:
            rec = json.load(fh)
        st = dict((r["id"], (r["status"], r["cls"])) for r in rec["rows"])
        self.assertEqual(st["PLANT_selection"], ("PASS", "MOD"))
        cap = next(r["detail"] for r in rec["rows"] if r["id"] == "PLANT_cap_open")
        self.assertIn("(37.4, 200.2, 44.6, 211.8)", cap)              # cap samples come from the probe's picture
        self.assertNotIn("(40, 200)", cap.split(";", 1)[1])           # never the root, never a blocker
        for rid in ("PLANT_trunk_solid", "PLANT_cap_open", "PLANT_door_seal"):
            self.assertEqual(st[rid][0], "PASS", (rid, [r["detail"] for r in rec["rows"] if r["id"] == rid]))
        self.assertEqual(st["PLANT_grown"][0], "PASS")  # 10 blockers: a count trunk_live.allowed_counts reads from the patch
        self.assertEqual(door, [1])

    def plants(self, **kw):
        f = Fake(**kw)
        out = os.path.join(self.tmp, "plants_%d.json" % len(os.listdir(self.tmp)))
        PP.run(Args(out, "40,200"), f, FakeSite(PP.SNAP_PREFIX), ticker=f.advance,
               door_runner=lambda: dict(ok=True, restoration=dict(ok=True)))
        with open(out) as fh:
            rec = json.load(fh)
        return dict((r["id"], (r["status"], r["cls"])) for r in rec["rows"])

    def test_selection_miss_fails_and_off_is_site(self):
        st = self.plants(misses=1)
        self.assertEqual(st["PLANT_selection"], ("FAIL", "MOD"))
        self.assertEqual(st["PLANT_door_seal"][0], "PASS")             # a selection failure does not gate the door scene
        self.assertEqual(self.plants(selection_on=False)["PLANT_selection"], ("UNMEASURED", "SITE"))
        self.assertEqual(self.plants(ring_hits=3)["PLANT_selection"], ("FAIL", "MOD"))   # a box bigger than the art
        self.assertEqual(PP.picture_cells(PP.parse_probe("picture=37.4,200.2..44.6,211.8")).__len__(), 96)

    def test_door_errors_are_classed_not_blamed_on_the_mod(self):
        self.assertEqual(PP.door_error_class("AssertionError('SITE: no registered site')"), "SITE")
        self.assertEqual(PP.door_error_class("AssertionError('HARNESS: bridge')"), "HARNESS")
        self.assertEqual(PP.door_error_class("KeyError('pawns')"), "HARNESS")
        self.assertIsNone(PP.door_error_class("AssertionError('MOD: door still open')"))
        self.assertIsNone(PP.door_error_class("AssertionError('cut_recovered')"))

    def test_door_scene_has_its_own_clock(self):
        f = Fake()
        out = os.path.join(self.tmp, "plants_clock.json")
        site = FakeSite(PP.SNAP_PREFIX)

        def door_runner():
            f.tick = 10                                      # the door scene reloads its own save: the clock goes back
            return dict(ok=True, restoration=dict(ok=True))
        PP.run(Args(out, "40,200"), f, site, ticker=f.advance, door_runner=door_runner)
        with open(out) as fh:
            rec = json.load(fh)
        self.assertTrue(rec["summary"]["phases_in_order"], rec["phases"])
        self.assertEqual([p["scene"] for p in rec["phases"]], [1, 1, 1, 2])
        self.assertIn("foreignClock", rec["phases"][-1])

    def test_separate_entrypoints_and_sites(self):
        self.assertNotEqual(TT.SNAP_PREFIX, PP.SNAP_PREFIX)
        self.assertNotEqual(os.path.abspath(TT.__file__), os.path.abspath(PP.__file__))
        self.assertFalse(set(TT.REQUIRED) & set(PP.REQUIRED))
        self.assertTrue(callable(TT.main) and callable(PP.main) and TT.main is not PP.main)

    def test_help(self):
        for script in ("showcase_titan_live.py", "showcase_plants_live.py"):
            p = subprocess.run([sys.executable, os.path.join(HERE, script), "--help"], capture_output=True, text=True,
                               timeout=60)
            self.assertEqual(p.returncode, 0, p.stderr[-400:])
            self.assertIn("--out", p.stdout)


if __name__ == "__main__":
    unittest.main()
