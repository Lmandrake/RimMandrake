#!/usr/bin/env python3
"""selftest_test_site_saves -- offline checks of modcheck/test_site_saves.py against a small fake map (no game)."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_site_saves as T  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("PASS" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


class Fake(object):
    """A map with a shrine (casket holding a sleeper, crate, trigger pair), a hive, a ruin wall, a warhead, fog, a
    hostile pawn the fog hides until the unfog, 3 colonists, rain off."""

    def __init__(self):
        self.things = [
            {"id": "AncientCryptosleepCasket1", "def": "AncientCryptosleepCasket", "x": 10, "z": 10, "faction": None},
            {"id": "AncientHermeticCrate2", "def": "AncientHermeticCrate", "x": 12, "z": 10, "faction": None},
            {"id": "Hive3", "def": "Hive", "x": 50, "z": 50, "faction": "Insect"},
            {"id": "Wall4", "def": "Wall", "x": 11, "z": 12, "faction": None},
            {"id": "Geyser5", "def": "SteamGeyser", "x": 90, "z": 90, "faction": None},
            {"id": "Shell6", "def": "Shell_AntigrainWarhead", "x": 13, "z": 11, "faction": None, "item": True},
            {"id": "RectTrigger7", "def": "RectTrigger", "x": 10, "z": 9, "faction": None, "ethereal": True},
            {"id": "SignalAction_Letter8", "def": "SignalAction_Letter", "x": 10, "z": 9, "faction": None, "ethereal": True},
            {"id": "Bed9", "def": "Bed", "x": 100, "z": 100, "faction": "PlayerColony"},
            {"id": "Turret10", "def": "Turret_MiniTurret", "x": 102, "z": 100, "faction": "PlayerColony",
             "factionName": "New Arrivals"},
        ]
        self.pawns = [{"id": "C%d" % i, "isPlayer": True, "intelligence": "Humanlike", "dead": False, "downed": False,
                       "hostile": False, "spawned": True} for i in range(3)]
        self.hidden = [{"id": "Fleshbeast1", "isPlayer": False, "intelligence": "Animal", "dead": False, "hostile": True}]
        self.fogged = 500
        self.log = []
        self.state = "Playing"

    def _rect_hit(self, rects, t):
        for r in rects.split(";"):
            x, z = [int(v) for v in r.split(",")[:2]]
            if (t["x"], t["z"]) == (x, z):
                return True
        return False

    def __call__(self, tool, **kw):
        self.log.append(tool)
        if tool == "jawa/list_things":
            rows = [t for t in self.things]
            if kw.get("defName"):
                want = set(kw["defName"].split(","))
                rows = [t for t in rows if t["def"] in want]
            if kw.get("group") == "BuildingArtificial":
                rows = [t for t in rows if not t.get("item") and not t.get("ethereal")]
            return {"success": True, "things": rows, "countMatched": len(rows), "isCompleteList": True}
        if tool == "jawa/destroy_batch":
            cats = set(kw.get("categories", "Plant").split(","))

            def kind(t):
                return "Ethereal" if t.get("ethereal") else ("Item" if t.get("item") else "Building")
            self.things = [t for t in self.things if not (self._rect_hit(kw["rects"], t) and (kind(t) in cats or "All" in cats))]
            return {"success": True}
        if tool == "jawa/destroy_bulk":
            n = len([p for p in self.pawns if not p["isPlayer"]])
            self.pawns = [p for p in self.pawns if p["isPlayer"]]
            return {"success": True, "matchedCount": n}
        if tool == "jawa/list_pawns":
            rows = self.pawns
            if kw.get("faction") == "hostile":
                rows = [p for p in rows if p.get("hostile")]
            return {"success": True, "pawns": rows}
        if tool == "jawa/set_fog":
            if kw.get("action") == "unfogAll":
                before, self.fogged = self.fogged, 0
                self.pawns.extend(self.hidden)          # the unfog releases what the fog held (r7/r8)
                self.hidden = []
                return {"success": True, "foggedCellsBefore": before, "foggedCellsNow": 0}
            return {"success": True, "foggedCellsNow": self.fogged}
        if tool == "jawa/map_info":
            return {"success": True, "tile": 77, "mapId": 0, "sizeX": 250, "sizeZ": 250, "mapBiome": "TemperateForest",
                    "outdoorTempNow": 18.0}
        if tool == "jawa/weather_get":
            return {"success": True, "weather": {"current": "Clear", "rainRate": 0.0}, "conditions": []}
        if tool == "jawa/weather_set":
            return {"success": True, "after": "Clear"}
        if tool == "jawa/map_fire":
            return {"success": True, "firesExtinguished": 0}
        if tool == "jawa/quiet_site":
            hives = [t for t in self.things if t["def"] == "Hive"]
            return {"success": True, "threats": [{"def": t["def"], "id": t["id"]} for t in hives]}
        if tool == "rimworld/get_ui_state":
            return {"programState": self.state}
        if tool == "rimworld/go_to_main_menu":
            self.state = "Entry"
            return {"success": True}
        if tool == "rimworld/load_game":
            self.load_args = dict(kw)
            self.state = "Playing"
            return {"success": True}
        return {"success": True}


# 1. the danger classifier
for d in ("AncientCryptosleepCasket", "AncientHermeticCrate", "Sarcophagus", "Hive", "EggSac", "GlowPod",
          "Shell_AntigrainWarhead", "PsychicAnimalPulser"):
    check("1 danger: %s" % d, T.is_danger_def(d))
for d in ("Wall", "Column", "Urn", "Slate", "SteamGeyser", "Bed", "AncientBarrel"):
    check("1 not danger: %s" % d, not T.is_danger_def(d))

# 2. a calm clean leaves nothing and releases the fog-held pawn into the sweep
f = Fake()
rec = T.clean_map(f, "calm", quiet=False)
check("2 calm clean reads back clean", not rec["problems"], rec["problems"])
check("2 casket + crate + warhead + hive vanished before the unfog",
      {"AncientCryptosleepCasket", "AncientHermeticCrate", "Shell_AntigrainWarhead", "Hive"} <= set(rec["dangerFound"]))
check("2 the casket went BEFORE the unfog",
      f.log.index("jawa/destroy_batch") < f.log.index("jawa/set_fog"))
check("2 the released fleshbeast was swept", rec["fog"].get("releasedByUnfog") == ["Fleshbeast1"], rec["fog"])
check("2 ruins gone; geyser, the player's bed and the player's turret (factionName is the colony's name) kept",
      sorted(t["def"] for t in f.things) == ["Bed", "SteamGeyser", "Turret_MiniTurret"], [t["def"] for t in f.things])
chk = T.check_map(f, "calm")
check("2 check_map verified on the cleaned map", chk["verified"], chk["problems"])

# 3. the danger profile keeps the ruins (Pyrelands reads them)
f = Fake()
rec = T.clean_map(f, "danger", quiet=False)
check("3 danger clean reads back clean", not rec["problems"], rec["problems"])
check("3 ruin wall kept", any(t["def"] == "Wall" for t in f.things))
check("3 casket gone", not any(t["def"] == "AncientCryptosleepCasket" for t in f.things))

# 4. check_map catches each dirt kind
f = Fake()
chk = T.check_map(f, "calm")
p = " | ".join(chk["problems"])
for word in ("fogged", "triggers", "danger", "ruins", "threat structures"):
    check("4 dirty map: %s named" % word, word in p, p)
check("4 dirty map not verified", not chk["verified"])
f = Fake()
T.clean_map(f, "calm", quiet=False)
f.pawns[0]["downed"] = True
f.pawns[1]["downed"] = True
chk = T.check_map(f, "calm")
check("4 two downed colonists fail the standing-colonist bar", any("standing colonist" in x for x in chk["problems"]))

# 5. a save is never overwritten
d = tempfile.mkdtemp()
open(os.path.join(d, "RM_TestSite_calm_v1.rws"), "w").close()
try:
    T.save_site(lambda *a, **k: {}, "RM_TestSite_calm_v1", d, sleep=lambda s: None)
    check("5 save refuses an existing name", False)
except RuntimeError as ex:
    check("5 save refuses an existing name", "never overwritten" in str(ex))
try:
    T.build(Fake(), "calm", d, d)
    check("5 build refuses before touching the game", False)
except RuntimeError as ex:
    check("5 build refuses before touching the game", "exists" in str(ex))

# 6. load goes through the main menu, then reads back
f = Fake()
T.clean_map(f, "calm", quiet=False)
f.log = []
T.read_registry = lambda path=None: {}
import quiet_site as QS  # noqa: E402
QS.site_profile_receipt = lambda *a, **k: {"problems": [], "error": None}
r = T.load_site(f, "calm", sleep=lambda s: None)
check("6 load via main menu before load_game", f.log.index("rimworld/go_to_main_menu") < f.log.index("rimworld/load_game"))
check("6 loaded clean map verified", r["verified"], r["problems"])
check("6 load ignores the save's mod header (fixture save, tier list differs)",
      getattr(f, "load_args", {}).get("ignoreModCompatibility") is True, getattr(f, "load_args", None))
try:
    T.load_site(f, "pyrelands")
    check("6 pyrelands has no save of its own here", False)
except ValueError:
    check("6 pyrelands has no save of its own here", True)

print("selftest_test_site_saves: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
