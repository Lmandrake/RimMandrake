#!/usr/bin/env python3
"""T_WALK_SMALL (RIMMANDRAKE_SPLIT_PYRELANDS_SEASON_WALK_TO_MINIMUM_TESTS), bar walk_season_on_the_pyre: the two small scenes
that replaced sc_walk decide what they claim, offline.

  1. reload_verdict: PASS on an equal reload; FAIL, with the reason named, on each planted fault (the front gone, half gone,
     moved; the fruit gone; the scar reads old; the bonus reset; the burn stamp lost); undecided (None) with no front, no
     fruit, no bonus, an equal control save or a read that is missing.
  2. smoke_verdict and our_errors: PASS on a walking front; FAIL on a front that dies or stands still and on an error that
     names Pyrelands; undecided on a short list, an unread list or a short watch; another mod's error is not ours.
  3. the shipped chains, run against a scripted game: PASS on the real state, and each planted switch (PYRE_PLANT_RELOAD,
     PYRE_PLANT_SMOKE) FAILs.
  4. scenes.json and the table carry the scenes, sc_walk is gone, the three scenes alone decide the bar, and his walk carries no long play.

Run: python3 <this file>   exit 0 = every check PASS
"""
import importlib.util
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONCEPT = os.path.join(ROOT, "design", "concepts", "Pyrelands")
NAME = "selftest_pyrelands_walk_small"
BAR = "walk_season_on_the_pyre"
N = {"run": 0, "bad": 0}


def check(name, ok, detail=""):
    N["run"] += 1
    if not ok:
        N["bad"] += 1
        print("FAIL  %s -- %s" % (name, str(detail)[:300]))


_spec = importlib.util.spec_from_file_location("walk_small_live", os.path.join(HERE, "walk_small_live.py"))
W = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W)

# ---- 1. the reload
PART = {"fertility": 1.2, "bonus": 0.5, "burnTick": "4000", "base": 0.7, "wateredFertility": 1.4, "bonusAgeDays": "0.02",
        "bonusDaysLeft": "5.98"}
OLD = dict(PART, fertility=0.7, bonus=0.0, burnTick="-1", bonusAgeDays="-1", bonusDaysLeft="0.00")
CELLS = [(180, 60), (182, 60), (184, 60)]


def state(fires=12, fruit=3, part=PART, dx=0):
    return {"fires": [(192 + dx, 50 + i) for i in range(fires)], "fruit": [(180 + i, 50) for i in range(fruit)],
            "scar": dict((c, dict(part)) for c in CELLS)}


PRE, MID = state(0, 0, OLD), state()
check("an equal reload passes", W.reload_verdict(PRE, MID, state())[0] is True, W.reload_verdict(PRE, MID, state()))
one_tick = state(11, 3, dict(PART, bonus=0.499, bonusAgeDays="0.03"))
check("one tick of play at the load passes", W.reload_verdict(PRE, MID, one_tick)[0] is True, W.reload_verdict(PRE, MID, one_tick))
for label, again, word in (
        ("the front is gone", state(0), "front"), ("half the front is gone", state(6), "front"),
        ("the front moved", state(dx=3), "front"), ("the fruit is gone", state(fruit=0), "fruit"),
        ("one fruit is gone", state(fruit=2), "fruit"), ("the scar reads old", state(part=OLD), "scar"),
        ("the bonus reset", state(part=dict(PART, bonus=0.0, fertility=0.7)), "scar"),
        ("the burn stamp moved", state(part=dict(PART, burnTick="5250")), "scar"),
        ("a scar field is gone", state(part={"burnTick": "4000"}), "scar")):
    ok, why = W.reload_verdict(PRE, MID, again)
    check("planted: %s FAILs and says so" % label, ok is False and word in why, (ok, why))
for label, args in (("no front at the save", (PRE, state(0), state(0))), ("no fruit at the save", (PRE, state(fruit=0), state())),
                    ("no bonus at the save", (PRE, state(part=OLD), state(part=OLD))), ("the control equals the save", (MID, MID, MID)),
                    ("a read is missing", (PRE, MID, {})), ("no read at all", ({}, {}, {}))):
    check("undecided: %s" % label, W.reload_verdict(*args)[0] is None, W.reload_verdict(*args))

# ---- 2. the smoke
sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "modcheck")]
import validation as V  # noqa: E402


def rows(shift=4.0, dark=None):
    return [{"hour": h, "fires": 0 if h == dark else 8, "cx": 180 + shift * h, "cz": 60.0} for h in (1, 2, 3)]


S = lambda r=None, e=(), share=1.0: W.smoke_verdict(rows() if r is None else r, list(e), V.front_walks, share)  # noqa: E731
check("a walking front with a clean log passes", S()[0] is True, S())
check("planted: a front that dies FAILs", S(rows(dark=2))[0] is False, S(rows(dark=2)))
check("planted: a fire that stands still FAILs", S(rows(shift=0.5))[0] is False, S(rows(shift=0.5)))
check("planted: an error of ours FAILs", S(e=["[RimMandrake.Pyrelands] x"])[0] is False)
check("an error of ours FAILs even on a short list", S(e=["x"], share=0.1)[0] is False)
check("undecided: not his full list", S(share=0.5)[0] is None)
check("undecided: the list was not read", S(share=None)[0] is None)
check("undecided: a short watch", S(rows()[:2])[0] is None)
check("ours: an error that names our def", W.our_errors([{"type": "Error", "text": "could not load RM_FE_Ash"}]) != [])
check("ours: an exception from our frames",
      W.our_errors([{"level": "Exception", "text": "NullReference", "stackTrace": "at RimMandrake.Pyrelands.X"}]) != [])
check("not ours: another mod's error", W.our_errors([{"type": "Error", "text": "Dubs pipe net failed"}]) == [])
check("not ours: our warning", W.our_errors([{"type": "Warning", "text": "Pyrelands"}]) == [])
check("the full list is read", len(W.full_list_ids()) > 100, len(W.full_list_ids()))
check("a missing list is unread, never complete", W.full_list_missing(None, ["a"])[0] is None and W.full_list_missing(["a"], [])[0] is None)
check("the missing mods are named", W.full_list_missing(["A"], ["a", "b"]) == (0.5, ["b"]), W.full_list_missing(["A"], ["a", "b"]))


# ---- 3. the shipped chains on a scripted game
class Game(object):
    """A pad with a front and a scar; saves keep all of it. `broken` drops a part at a load (a mod that loses it)."""

    def __init__(self, broken=None):
        self.broken, self.now, self.saves, self.log, self.hour = broken, 0, {}, [], 0
        self.st = {"fires": [], "fruit": [], "burn": -1}

    def load(self, name):
        self.st = json.loads(json.dumps(self.saves[name]))
        if name.endswith("_mid"):
            if self.broken == "front":
                self.st["fires"] = []
            if self.broken == "scar":
                self.st["burn"] = -1
            if self.broken == "fruit":
                self.st["fruit"] = []


def run(chain, game, env=None, still=False):
    out = {"notes": [], "verdict": None, "why": ""}

    class Stop(Exception):
        pass

    class Comp(object):
        def __enter__(self):
            return self

        def __exit__(self, et, ev, tb):
            if et is None:
                out["verdict"] = "PASS"
            elif et is Stop:
                out["verdict"], out["why"] = ev.args
                return True
            return False

    class T(object):
        session, upstream_failed, anchor = object(), False, (0, 0)

        def clear_area(self, size=0):
            pass

        def screenshot(self, rect=None):
            check("%s: a capture names its rect" % chain, rect is not None)

        def bridge_call(self, tool, **p):
            if tool == "rimworld/save_game":
                game.saves[p["saveName"]] = json.loads(json.dumps(game.st))
            if tool == "jawa/map_info":
                return {"mapBiome": "RM_Pyrelands"}
            if tool == "jawa/set_terrain":
                out.setdefault("terrain", []).append(p["terrainDef"])
            if tool == "jawa/running_mods":
                return {"success": True, "packageIds": W.full_list_ids()}
            if tool == "jawa/static_call":
                game.log.append({"type": "Error", "text": p["args"]})
            return {"success": True}

    def fire(t, rect, size=1.2):
        if rect[2] > 4:                                     # the scar strip
            game.st["burn"] = game.now
        else:
            game.st["fires"] = [[rect[0] + i, rect[1]] for i in range(8)]

    def wait(t, n):
        game.now += n
        if not still:
            game.st["fires"] = [[x + (4 if n >= W.HOUR else 0), z] for x, z in game.st["fires"]]

    def plants(t, what, rect):
        if what == V.FRUIT_PLANT:
            game.st["fruit"] = [[rect[0] + i, rect[1]] for i in range(rect[2])]

    def probe(t, x, z):
        b = game.st["burn"] >= 0
        return {"fertility": 1.2 if b else 0.7, "bonus": 0.5 if b else 0.0, "burnTick": str(game.st["burn"]), "base": 0.7,
                "wateredFertility": 1.4, "bonusAgeDays": "0.02" if b else "-1", "bonusDaysLeft": "5.98" if b else "0.00"}

    def things(t, d, rect=None, limit=0):
        return [{"x": c[0], "z": c[1]} for c in game.st["fires" if d == "Fire" else "fruit"]]

    def stop(v):
        def f(*a):
            raise Stop(v, a[-1])
        return f
    import contextlib
    chains = {}
    ns = types.SimpleNamespace(
        _teardown=lambda **k: (lambda fn: fn), _comp=lambda t, n, **k: Comp(), _live=lambda t: True, _pad=lambda t, xz: setattr(t, "anchor", xz),
        _wildlife_shield=lambda t: contextlib.nullcontext(), _walk_shield=lambda t: contextlib.nullcontext(),
        _rect=V._rect, _rs=V._rs, _note=lambda t, n, v: out["notes"].append((n, v)), _wait=wait, _fire=fire, _plants=plants,
        _extinguish=lambda t: game.st.update(fires=[]), _walk_steady_colonists=lambda t: None, _clear_scorchfruit=lambda t: game.st.update(fruit=[]),
        _firebreak=lambda *a: None, _soil=lambda *a: None, _things=things, fire_cells=V.fire_cells, _probe=probe,
        _load_site_save=lambda t, n: game.load(n), _unmeasured=stop("UNMEASURED"), _fail=stop("FAIL"), _r6_fires=lambda t: things(t, "Fire") and
        [tuple(c) for c in game.st["fires"]], _log_mark=lambda t: "m", _log_since=lambda t, m: game.log, front_walks=V.front_walks,
        FRUIT_PLANT=V.FRUIT_PLANT, PAD_FIRE_BORN=V.PAD_FIRE_BORN, TEST_SIZE=V.TEST_SIZE, FIREBREAK=V.FIREBREAK)
    W.register(types.SimpleNamespace(chain=lambda n: (lambda fn: chains.setdefault(n, fn))), ns)
    keep = dict((k, os.environ.get(k)) for k in (W.PLANT_RELOAD_ENV, W.PLANT_SMOKE_ENV))
    for k in keep:
        os.environ.pop(k, None)
    os.environ.update(env or {})
    try:
        chains[chain](T())
    finally:
        for k in keep:
            os.environ.pop(k, None)
            if keep[k] is not None:
                os.environ[k] = keep[k]
    return out


R, F = "reload_keeps_the_burn", "full_list_smoke"
x = run(R, Game())
check("chain %s PASSes on a game that keeps its state" % R, x["verdict"] == "PASS", x)
for b in ("front", "scar", "fruit"):
    x = run(R, Game(b))
    check("chain %s FAILs on a game that loses the %s" % (R, b), x["verdict"] == "FAIL", (x["verdict"], x["why"]))
for p in ("front_lost", "old_save"):
    x = run(R, Game(), {W.PLANT_RELOAD_ENV: p})
    check("chain %s: the planted %s FAILs" % (R, p), x["verdict"] == "FAIL", (x["verdict"], x["why"]))
x = run(F, Game())
check("chain %s PASSes on a walking front" % F, x["verdict"] == "PASS", x)
check("chain %s burns the biome's own ground, deep ash (visit 8: on never-burned soil a fire outlives its grass for 3 h, so the centre "
      "of all that burns moved half the front's way: 3.0 and 2.7 cells, one PASS and one FAIL)" % F,
      x.get("terrain") == ["RM_FE_Ash_Deep"], x.get("terrain"))
x = run(F, Game(), still=True)
check("chain %s FAILs on a fire that stands still" % F, x["verdict"] == "FAIL", (x["verdict"], x["why"]))
for p in ("no_front", "log_error"):
    x = run(F, Game(), {W.PLANT_SMOKE_ENV: p})
    check("chain %s: the planted %s FAILs" % (F, p), x["verdict"] == "FAIL", (x["verdict"], x["why"]))

# ---- 4. the record
for c in (R, F):
    check("validation.py registers %s" % c, any(getattr(k, "name", None) == c or k == c or (isinstance(k, tuple) and k[0] == c)
                                               for k in V.suite.chains), [str(k)[:40] for k in list(V.suite.chains)[-3:]])
sc = dict((s["id"], s) for s in json.load(open(os.path.join(CONCEPT, "scenes.json"), encoding="utf-8"))["scenes"])
tt = json.load(open(os.path.join(CONCEPT, "version", "test_table.json"), encoding="utf-8"))
bar = [b for b in tt["bars"] if b["id"] == BAR][0]
NEW = ("sc_reload_keeps_the_burn", "sc_fire_sense")
check("sc_walk is gone from the scenes and the table", "sc_walk" not in sc and "sc_walk" not in tt["tests"])
for s in NEW:
    check("%s is a scene of the bar and a kind A test" % s, BAR in (sc.get(s) or {}).get("requirement", []) and
          (tt["tests"].get(s) or {}).get("test_kind", "A") == "A" and s in tt["tests"], s)
check("the two scenes, and not his walk, decide the bar", sorted(bar["decides"]) == sorted(NEW), bar["decides"])
check("no check uses the full list (retired until the integration phase)", [k for k, t in tt["tests"].items() if t.get("kind") == "live_full"] == [])
check("his walk names no season and no weeks (season-long play is play testing)",
      not any(w in tt["tests"]["LOOK_STAGE8"]["observes"] for w in ("week", "season")), tt["tests"]["LOOK_STAGE8"]["observes"])

print("%s: %d of %d checks failed" % (NAME, N["bad"], N["run"]))
sys.exit(1 if N["bad"] else 0)
