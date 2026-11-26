#!/usr/bin/env python3
"""Selftest of RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP: three real scenes on the scene library 0.3.0, against the
fake game (scene_fake.py) and kept traces. No game, no bridge. 17 checks; `--mutants` plants the four wrong codes of the ticket
and shows that each turns a check red.

The replies of the new hands are made from their wire pages, not recorded in a game. The two moat traces are made from the hits
that the test pilot sitting of 2026-11-23 captured live (selftest_flowworks_moat_rim_stabs.py), by the game's own rule: a melee
swing at a pawn sets its mindState.lastMeleeThreatHarmTick (Verb_MeleeAttack.TryCastShot). A fake proves what the Python does,
never what the game does."""
import ast
import contextlib
import io
import json
import os
import re
import runpy
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(RM))
sys.path.insert(0, HERE)
import scene                                        # noqa: E402
import scene_fake as F                              # noqa: E402
import scene_names                                  # noqa: E402
c = scene.cond

SCENES = {"moat": os.path.join(RM, "FlowWorks", "northstar", "scene_moat_rim_wardens.py"),
          "storeroom": os.path.join(RM, "ExplosiveKnockback", "proof", "scene_storeroom_pit.py"),
          "wall_lamps": os.path.join(RM, "GimmeSomeSlack", "northstar", "scene_wall_lamp_looks.py")}
READINGS = os.path.join(REPO, "design", "specs", "2026-11-23-bridge-v2", "12_conversion_readings.md")
TMP = tempfile.mkdtemp(prefix="scene_conversion_")
sys.path.insert(0, os.path.join(RM, "rimflow"))
import scene_verdicts                               # noqa: E402
scene_verdicts.REPO = TMP   # the scenes' own judge lines write the verdict ledger: into this test's folder, never a real mod's file
COMMIT = "a" * 40
# the hits captured live on ArchBig, TP_MOAT_HELD_A (selftest_flowworks_moat_rim_stabs.py): 'tick instigator damageDef'
OFF = {"wardens[0]": ["912 Human24671 Blunt", "1032 Human24671 Blunt"],               # the warden's own punches
       "wardens[1]": ["915 Human24675 Blunt", "1035 Human24675 Blunt", "1096 Human21233 Stab"]}   # and a raider's stab
ON = {"wardens[0]": [], "wardens[1]": []}
RAIDERS = {"Human21181", "Human21233"}
CAPTURE_TICK = 900                                  # the capture orders of that sitting were given on tick 900


def must(ok, what):
    if not ok:
        raise AssertionError(what)


def refused(name, fn, *a, **kw):
    try:
        got = fn(*a, **kw)
    except scene.Refused as e:
        must(e.name == name, "refused %s, want %s: %s" % (e.name, name, e))
        return e
    raise AssertionError("%s was not refused: %r" % (name, got))


class DiskWorld(F.FakeWorld):
    """The fake world, with run folders on disk so that scene.judge can read them. One fake game answers for ArchBig and ArchSmall,
    each by its own key."""

    def connect(self, letter):
        self.games["b"].running_mods["loaded"]["gameKey"] = {"a": "archmagi", "b": "archmagi.b"}[letter]
        return F.FakeBridge(self.games["b"])

    def run_dir(self, label):
        return tempfile.mkdtemp(prefix=re.sub(r"\W", "_", label) + "_", dir=TMP)

    def save(self, path, text, append=False):
        F.FakeWorld.save(self, path, text, append)
        with open(path, "a" if append else "w", encoding="utf-8") as f:
            f.write(text)


def world(**launch):
    scene.LAUNCH.update(mode="script", commit=None, script=None, plant=None)
    scene.LAUNCH.update(launch)
    g = F.FakeGame(run_until=True)
    g.saves += ["TP_MOAT_HELD_A", "EK_SITTING_STATION1_STOREROOM_PIT_20261112"]
    W = DiskWorld(g)
    g.tools.append({"name": "jawa/mod_settings_field", "description": "Read or write ANY public field of a ModSettings class",
                    "parameters": [{"name": n, "required": False} for n in ("typeName", "action", "field", "value")]})
    W.wanted_rows = {m: (m, "mandrake.rm.%s" % m.lower(), None, {"rimmandrake%s.dll" % m.lower(): ["x"]})
                     for m in ("FlowWorks", "ExplosiveKnockback", "GimmeSomeSlack")}
    scene.WORLD = W
    return W


def track_rows(rows, ticks):
    """{name: [(offset, state, value)]} for the fake run, from {name: [(offset, value)]}."""
    return {n: [(off, "ok", v) for off, v in series] for n, series in rows.items()}


def moat_world(hits):
    W = world()
    g = W.game
    for rid, cell in (("Human21181", "61,0,66"), ("Human21233", "74,0,69")):
        g.values[("thing:" + rid, "def.defName")] = ("ok", "Human")
        g.values[("thing:" + rid, "positionInt")] = ("ok", cell)
    series = {}
    for i, (rid, (x, z)) in enumerate((("Human21181", (61, 66)), ("Human21233", (74, 69)))):
        series["raiders[%d].positionInt.x" % i] = [(0, x)]
        series["raiders[%d].positionInt.z" % i] = [(0, z)]
    for w, hs in hits.items():
        series["%s.health.healthState" % w] = [(0, "Mobile")]
        swings = [int(h.split()[0]) for h in hs if h.split()[1] in RAIDERS]
        series["%s.mindState.lastMeleeThreatHarmTick" % w] = [(0, -99999)] + [(t - CAPTURE_TICK, t) for t in swings]
    g.script = {"state": "hit", "ticks": 900, "tracks": track_rows(series, 900)}
    return W


def storeroom_world(thrown=True):
    W = world()
    g = W.game
    things = [("Shell_HighExplosive20001", "Item", "Shell_HighExplosive", (120, 124))]
    things += [("Human%d" % (30001 + i), "Pawn", "Human", (119 + i, 123)) for i in range(5)]
    things += [("Steel%d" % (40001 + i), "Item", "Steel", (118 + i % 6, 125 + i // 6)) for i in range(12)]
    things += [("Wall50001", "Building", "Wall", (114, 117))]
    g.rect_values = []
    for tid, cat, d, (x, z) in things:
        for path, v in (("def.category", cat), ("def.defName", d), ("positionInt", "%d,0,%d" % (x, z))):
            g.rect_values.append({"of": "thing:" + tid, "path": path, "state": "ok", "v": v})
            g.values[("thing:" + tid, path)] = ("ok", v)
    g.values[("thing:Shell_HighExplosive20001", "hitPointsInt")] = ("ok", 60)
    series = {"bomb.positionInt": [(0, "120,124")]}
    for i in range(5):
        series["people[%d].positionInt" % i] = [(0, "%d,%d" % (119 + i, 123))]
        series["people[%d].positionInt.x" % i] = [(0, 119 + i)] + ([(40, 129)] if thrown and i == 2 else [])
        series["people[%d].positionInt.z" % i] = [(0, 123)]
    for i in range(6):
        series["goods[%d].positionInt" % i] = [(0, "x")]
        series["goods[%d].positionInt.x" % i] = [(0, 118 + i % 6)] + ([(30, 130)] if thrown and i < 4 else [])
        series["goods[%d].positionInt.z" % i] = [(0, 125 + i // 6)]
    tracks = track_rows(series, 300)
    tracks["bomb.positionInt"] = [(0, "gone", None)]
    g.script = {"state": "hit", "ticks": 300, "tracks": tracks}
    return W


def lamp_world(styled=True):
    W = world()
    g = W.game
    x0, z0, looks = 60, 60, ["Scrapper", "Industrial", "Modern", "Futuristic"]
    g.values[("static:RimMandrake.GimmeSomeSlack.Aerial.AerialProbe", "result")] = ("ok", "PLACED WallLamp")
    g.rect_values = []
    series = {}
    for i, look in enumerate(looks):
        tid, x, z = "WallLamp%d" % (31001 + i), x0 + 3 + 4 * i, z0 + 7
        g.rect_values += [{"of": "thing:" + tid, "path": "def.defName", "state": "ok", "v": "WallLamp"},
                          {"of": "thing:" + tid, "path": "positionInt", "state": "ok", "v": "%d,0,%d" % (x, z)}]
        g.values[("thing:" + tid, "def.defName")] = ("ok", "WallLamp")
        g.values[("thing:" + tid, "positionInt")] = ("ok", "%d,%d" % (x, z))
        series["lamps[%d].positionInt" % i] = [(0, "ok")]
        series["lamps[%d].comp<CompStyleable>.styleDef" % i] = [(0, "WallLamp_" + look if styled else None)]
    g.script = {"state": "hit", "ticks": 1, "tracks": {}}
    W.lamp_tracks = track_rows(series, 60)
    return W


def play(path, W):
    """Run a converted scene on the fake world. -> (its run folder, its printed text)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        g = runpy.run_path(path, run_name="__main__")
    return g.get("folder"), out.getvalue()


def judged(folder):
    return scene.judge(folder)


# ------------------------------------------------------------------------------- the 17 checks
def imports_only_scene(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            mods.add(n.module)
    must(mods == {"scene"}, "%s imports %s" % (os.path.basename(path), sorted(mods)))


def t_moat_imports_only_scene():
    imports_only_scene(SCENES["moat"])


def t_storeroom_imports_only_scene():
    imports_only_scene(SCENES["storeroom"])


def t_wall_lamps_imports_only_scene():
    imports_only_scene(SCENES["wall_lamps"])


def t_moat_plays_to_its_end():
    W = moat_world(ON)
    folder, text = play(SCENES["moat"], W)
    must(folder and os.path.isfile(os.path.join(folder, "contract.json")), "no contract.json beside the trace")
    must("SUCCESS" in text, "the moat scene's own judge line: %s" % text[-300:])
    acts = [a for t, a in W.game.log if t == "jawa/act_batch"]
    must(len(acts) == 1 and len(json.loads(acts[0]["acts"])) == 2, "the two capture orders were not one batch: %s" % acts)
    must(W.lock is None and not W.game.session, "the session was not closed")


def t_storeroom_plays_to_its_end():
    W = storeroom_world()
    folder, text = play(SCENES["storeroom"], W)
    v = judged(folder)
    must(v.outcome == "SUCCESS", "storeroom: %s %s" % (v.outcome, v.first_failed))
    must(any(t == "jawa/act_batch" and "jawa/damage" in a["acts"] for t, a in W.game.log), "the bomb was not set off by s.act.damage")
    W = storeroom_world(thrown=False)               # the bomb never went off: no exposure, so never a SUCCESS
    W.game.script["tracks"]["bomb.positionInt"] = [(0, "ok", "120,124")]
    folder, _text = play(SCENES["storeroom"], W)
    v = judged(folder)
    must(v.outcome != "SUCCESS" and v.evidence.get("exposure") is False, "no exposure judged %s" % v.outcome)


def t_wall_lamps_plays_to_its_end():
    W = lamp_world()
    real = W.game._run_until

    def run_until(a):                       # the probe's one-tick runs, then the judged run of 60 ticks with the lamps' tracks
        if a["action"] == "start" and a["limit"] > 10:
            W.game.script = {"state": "hit", "ticks": 60, "tracks": W.lamp_tracks}
        return real(a)
    W.game._run_until = run_until
    folder, text = play(SCENES["wall_lamps"], W)
    v = judged(folder)
    must(v.outcome == "SUCCESS", "wall lamps: %s %s" % (v.outcome, v.first_failed))
    must(any(t == "jawa/artboard_capture" for t, _a in W.game.log), "no picture was taken for the judge")


def _a_contract(**kw):
    base = dict(claim="raiders held in the drained moat do not stab the rim wardens", kind="A",
                exposure=c.value("raiders[0]", "positionInt.x") > 0, success=[c.played(10)],
                forbidden=c.value("wardens[0]", "mindState.lastMeleeThreatHarmTick") >= 0, end=10, limit=20)
    base.update(kw)
    return scene.contract(**base)


def t_contract_refuses_success_with_no_exposure():
    refused("NO_EXPOSURE", _a_contract, exposure=None)


def t_contract_refuses_kind_b_with_no_budget():
    refused("KIND_B_NO_BUDGET", _a_contract, kind="B")
    must(_a_contract(kind="B", budget=(1, 3)).plan(None, 5)["allowed_miss"] is True, "an X of Y budget allows a miss")


def t_contract_refuses_a_tap_that_is_not_built():
    refused("UNRECORDED_VALUE", _a_contract, success=[c.count("damage", victim="wardens") == 0])
    refused("NO_END", _a_contract, end=None)


def t_contract_makes_no_bridge_call_and_is_checked_before_the_load():
    W = world()
    k = _a_contract()
    must(k.receipt.hands == {} and k.receipt.game == "not applicable", "the contract touched a game: %s" % k.receipt.as_dict())
    must(W.game.log == [], "a bridge call was made: %s" % W.game.log)
    try:
        with open(SCENES["moat"], encoding="utf-8") as f:
            src = f.read()
        bad = src.replace('claim="raiders held', 'kind="B", budget=None, claim="raiders held').replace(', kind="A",', ',', 1)
        exec(compile(bad, "moat_planted", "exec"), {"__name__": "__main__"})
    except scene.Refused as e:
        must(e.name == "KIND_B_NO_BUDGET", "refused %s" % e.name)
    else:
        raise AssertionError("a bad contract in the scene was not refused")
    must(not W.game.loads and W.lock is None, "the game was touched before the bad contract was refused: %s" % W.game.loads)


def t_stage_reply_is_built_from_the_read_back_and_a_replaced_kind_is_a_staging_fault():
    W = world()
    s = scene.open("ArchSmall")
    W.game.kind_made = {"Colonist": "Human21301"}
    try:
        s.stage(cast={"digger": dict(kind="Colonist", at=(4, 4))})
    except scene.Fault as e:
        must(e.name == "STAGING_FAULT" and "Human21301" in e.detail, "%s" % e)
    else:
        raise AssertionError("a replaced pawn kind was not a staging fault")
    W.game.kind_made = {}
    cast = s.stage(cast={"pair": dict(kind="Colonist", at=[(5, 5), (6, 5)])})
    must([m.cell for m in cast.pair] == [(5, 5), (6, 5)] and all(m.id.startswith("Human") for m in cast.pair), "%s" % cast)
    W.game.echo = True
    try:
        s.stage(cast={"echoed": dict(kind="Colonist", at=(7, 7))})
    except scene.Fault as e:
        must(e.name == "COULD_NOT_LOOK", "an echo was %s" % e.name)
    else:
        raise AssertionError("a staging reply with no read-back was taken as made")
    s.close()


def t_read_gives_gone_for_a_gone_thing_never_zero():
    W = world()
    s = scene.open("ArchSmall")
    W.game.values[("thing:Human9", "def.defName")] = ("ok", "Human")
    W.game.values[("thing:Human9", "positionInt")] = ("ok", "3,4")
    s.stage(cast={"raider": dict(take="Human9")})
    W.game.values[("thing:Human9", "positionInt")] = ("gone", None)
    v = s.read("raider", "positionInt")
    must(v.state == "gone" and v.receipt.could_not_look, "%r" % v)
    try:
        v.v
    except scene.Fault:
        pass
    else:
        raise AssertionError("a gone value gave a number")
    refused("UNKNOWN_ALIAS", s.read, "nobody", "positionInt")
    refused("PATH_CALLS_METHOD", s.read, "raider", "GetStatValue(x)")
    s.close()


def t_moat_judge_is_mod_failure_on_the_hits_with_the_melee_rule_off():
    folder, _text = play(SCENES["moat"], moat_world(OFF))
    v = judged(folder)
    must(v.outcome == "MOD FAILURE" and v.row == 1, "rule off: %s row %s %s" % (v.outcome, v.row, v.first_failed))


def t_moat_judge_is_success_on_the_hits_with_the_melee_rule_on():
    folder, _text = play(SCENES["moat"], moat_world(ON))
    v = judged(folder)
    must(v.outcome == "SUCCESS" and v.evidence.get("exposure") is True, "rule on: %s %s" % (v.outcome, v.first_failed))


def t_a_run_after_a_changing_raw_call_does_not_count_for_a_bar():
    W = moat_world(ON)
    scene.LAUNCH.update(mode="accept", commit=COMMIT, script="src/RimMandrake/FlowWorks/northstar/scene_moat_rim_wardens.py")
    clean, _t = play(SCENES["moat"], W)
    W = moat_world(ON)
    scene.LAUNCH.update(mode="accept", commit=COMMIT, plant="melee_rule_off", script="src/RimMandrake/FlowWorks/northstar/scene_moat_rim_wardens.py")
    raw, _t = play(SCENES["moat"], W)
    a, b = judged(clean), judged(raw)
    must(a.outcome == "SUCCESS" and a.counts_for_bar is True, "a clean accepted run: %s counts=%s" % (a.outcome, a.counts_for_bar))
    must(b.counts_for_bar is False and "EXPLORED" in b.receipt["stamps"], "a raw run counts=%s stamps=%s" % (b.counts_for_bar, b.receipt["stamps"]))
    must(any(x.startswith("PLANTED") for x in b.receipt["stamps"]), "a planted run is not stamped PLANTED")
    world()
    s = scene.open("ArchSmall")
    refused("NOT_BUILT", getattr, s.act, "tune")
    s.close()


def t_a_trace_with_no_closing_record_is_could_not_look():
    W = moat_world(ON)
    W.game.script["no_close"] = True
    try:
        play(SCENES["moat"], W)
    except scene.Fault as e:
        must(e.name == "TRACE_INCOMPLETE", "%s" % e.name)
        folder = os.path.dirname(e.trace)
    else:
        raise AssertionError("a trace with no close was taken")
    with open(os.path.join(folder, "contract.json"), "w", encoding="utf-8") as f:
        json.dump(scene.contract(claim="raiders held in the drained moat do not stab the rim wardens", kind="A",
                                 exposure=c.value("raiders[0]", "positionInt.x") > 0, success=[c.played(900)],
                                 forbidden=None, end=900, limit=1000).plan(None, 1), f)
    v = judged(folder)
    must(v.outcome == "COULD NOT LOOK" and v.counts_for_bar is False, "%s" % v.outcome)


def t_readings_have_a_measured_row_for_each_scene_old_and_new():
    must(os.path.isfile(READINGS), "no %s" % READINGS)
    text = open(READINGS, encoding="utf-8").read()
    for name in ("sc_moat_raid", "storeroom bomb pit", "sc_wall_lamp_looks"):
        rows = [ln for ln in text.splitlines() if ln.startswith("|") and name in ln]
        old = [r for r in rows if "| old |" in r]
        new = [r for r in rows if "| new |" in r]
        must(old and new, "%s has no old and new row" % name)
        for r in old + new:
            cells = [x.strip() for x in r.strip("|").split("|")]
            must(all(x and x not in ("?", "TBD", "unknown") for x in cells[2:6]), "%s: a row is not measured: %s" % (name, r))
    must("## Did the ten names help" in text and "## What could not be measured" in text, "the verdict or its limits are missing")


def t_a_job_to_a_cell_alone_reaches_the_game_as_its_first_target():
    """s.act.job(pawn, "Goto", cell=...) with no target: the game refuses a second target with no first one (live ArchBig
    2026-11-25: every walker of scene_walk_under_cover stood still, the order refused). The cell alone is target A."""
    import scene_names as N
    got = {}

    class S(object):
        pass
    act = N.Act(S())
    act._thing = lambda p: "Thing_" + p
    act._do = lambda verb, name, tool, args, subject, **kw: got.update(args)
    act.job("Human1", "Goto", cell=(15, 107))
    must(got.get("targetAX") == 15 and got.get("targetAZ") == 107 and "targetBX" not in got, "a lone cell was sent as %s" % got)
    got.clear()
    act.job("Human1", "RM_CaptureDown", target="Human2", cell=(3, 4))
    must(got.get("targetAId") == "Human2" and (got.get("targetBX"), got.get("targetBZ")) == (3, 4), "target and cell were sent as %s" % got)
    fake = __import__("scene_fake").FakeGame() if hasattr(__import__("scene_fake"), "FakeGame") else None
    if fake is not None and hasattr(fake, "_do"):
        r = fake._do("jawa/ordered_job", {"pawnId": "1", "jobDef": "Goto", "targetBX": 1, "targetBZ": 2, "waitTicks": 0})
        must(r.get("success") is False, "the fake game took a second target with no first: %s" % r)


CHECKS = [t_a_job_to_a_cell_alone_reaches_the_game_as_its_first_target, t_moat_imports_only_scene, t_storeroom_imports_only_scene, t_wall_lamps_imports_only_scene,
          t_moat_plays_to_its_end, t_storeroom_plays_to_its_end, t_wall_lamps_plays_to_its_end,
          t_contract_refuses_success_with_no_exposure, t_contract_refuses_kind_b_with_no_budget,
          t_contract_refuses_a_tap_that_is_not_built, t_contract_makes_no_bridge_call_and_is_checked_before_the_load,
          t_stage_reply_is_built_from_the_read_back_and_a_replaced_kind_is_a_staging_fault,
          t_read_gives_gone_for_a_gone_thing_never_zero,
          t_moat_judge_is_mod_failure_on_the_hits_with_the_melee_rule_off, t_moat_judge_is_success_on_the_hits_with_the_melee_rule_on,
          t_a_run_after_a_changing_raw_call_does_not_count_for_a_bar, t_a_trace_with_no_closing_record_is_could_not_look,
          t_readings_have_a_measured_row_for_each_scene_old_and_new]


def run(checks):
    good = 0
    for t in checks:
        try:
            t()
            good += 1
            print("ok    " + t.__name__)
        except Exception as e:  # noqa: BLE001 - a check that dies is a failure with its cause, never a skip
            print("FAIL  %s: %s: %s" % (t.__name__, type(e).__name__, str(e)[:400]))
        finally:
            scene.LAUNCH.update(mode="script", commit=None, script=None, plant=None)
    return good


# ------------------------------------------------------------------------------- the four wrong codes of the ticket
@contextlib.contextmanager
def patched(obj, name, new):
    old = getattr(obj, name)
    setattr(obj, name, new)
    try:
        yield
    finally:
        setattr(obj, name, old)


def m_stage_echoes_the_request():
    def echo(s, tool, reply, rec, done):           # the reply built from the request: every row as asked
        a = [x for t_, x in s.bridge.game.log if t_ == tool][-1]
        row = {"op": "pawn", "id": "Human1", "x": a.get("x"), "z": a.get("z"),
               "got": {"kind": a.get("kindDef"), "spawned": "True", "cell": "%s,%s" % (a.get("x"), a.get("z"))}}
        return {"ok": True, "made": [row], "wrong": [], "sameFrame": True}
    return patched(scene_names, "_block", echo), t_stage_reply_is_built_from_the_read_back_and_a_replaced_kind_is_a_staging_fault


def m_read_gives_zero_for_a_gone_thing():
    real = scene_names._values

    def zero(s, rec, pairs, rect=None, path=None):
        out = real(s, rec, pairs, rect, path)
        return [scene.Value(v.name, "ok", 0, v.tick) if v.state == "gone" else v for v in out]
    return patched(scene_names, "_values", zero), t_read_gives_gone_for_a_gone_thing_never_zero


def m_contract_checked_after_the_load():
    real_contract, real_open, held = scene.contract, scene.open, []

    def later(**kw):
        try:
            return real_contract(**kw)
        except scene.Refused as e:
            held.append(e)
            return None

    def open_then_check(game, contract=None, needs=None):
        s = real_open(game, needs=needs)
        if held:
            raise held.pop()
        return s
    stack = contextlib.ExitStack()
    stack.enter_context(patched(scene, "contract", later))
    stack.enter_context(patched(scene, "open", open_then_check))
    return stack, t_contract_makes_no_bridge_call_and_is_checked_before_the_load


def m_judge_success_with_no_exposure():
    J = scene._judge_module()
    real = J.readings

    def exposed(plan, trace):
        first, hits, misses, final = real(plan, trace)
        hits.setdefault("exposure", final.get("exposure"))
        return first, hits, misses, final
    return patched(J, "readings", exposed), t_storeroom_plays_to_its_end


MUTANTS = [m_stage_echoes_the_request, m_read_gives_zero_for_a_gone_thing, m_contract_checked_after_the_load,
           m_judge_success_with_no_exposure]


def mutants():
    caught = 0
    for m in MUTANTS:
        ctx, check = m()
        out = io.StringIO()
        with ctx, contextlib.redirect_stdout(out):
            red = run([check]) == 0
        caught += red
        why = [ln for ln in out.getvalue().splitlines() if ln.startswith("FAIL")]
        print("    " + (why[0][:230] if why else "(no FAIL line)"))
        print("%s  %s turns %s red" % ("CAUGHT" if red else "NOT CAUGHT", m.__name__[2:], check.__name__))
    print("planted wrong code: %d of %d caught" % (caught, len(MUTANTS)))
    return 0 if caught == len(MUTANTS) else 1


def main(argv):
    if "--mutants" in argv:
        try:
            return mutants()
        finally:
            shutil.rmtree(TMP, ignore_errors=True)
    try:
        good = run(CHECKS)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("scene conversion: %d of %d checks passed" % (good, len(CHECKS)))
    return 0 if good == len(CHECKS) == 18 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
