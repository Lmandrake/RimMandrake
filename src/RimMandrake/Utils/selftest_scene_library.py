#!/usr/bin/env python3
"""Selftest of the scene library's skeleton against a fake game (scene_fake.py). No game, no bridge.

The first 22 checks are the acceptance test of RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY; the rest are the
other promises of the pages. Pages: scene_contracts/, design/specs/2026-11-23-scene-library/boundary.md (each promise
a-b-c has the test t_a_b_c here). The plants that each must turn red: scene_library_mutants.py."""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene                                        # noqa: E402
import scene_fake as F                              # noqa: E402
import scene_hands                                  # noqa: E402
import scene_world                                  # noqa: E402
c = scene.cond


def must(ok, what):
    if not ok:
        raise AssertionError(what)


def refused(name, fn, *a, **kw):
    try:
        got = fn(*a, **kw)
    except scene.Refused as e:
        must(e.name == name, "refused %s, want %s: %s" % (e.name, name, e))
        must(len(e.repair) > 10, "%s carries no repair" % name)
        return e
    raise AssertionError("%s was not refused: %r" % (name, got))


def faulted(name, fn, *a, **kw):
    try:
        got = fn(*a, **kw)
    except scene.Fault as e:
        must(e.name == name, "fault %s, want %s: %s" % (e.name, name, e))
        return e
    raise AssertionError("no fault %s: %r" % (name, got))


def world(**kw):
    scene.LAUNCH.update(mode="script", commit=None, script=None)
    scene.WORLD = F.FakeWorld(F.FakeGame(**kw))
    scene.WORLD.wanted_rows = {"FlowWorks": ("FlowWorks", "mandrake.rm.flowworks", None, {"rimmandrakeflowworks.dll": ["x"]}),
                               "Absent": ("Absent", "mandrake.rm.absent", None, {"a.dll": ["x"]}),
                               "XmlOnly": ("XmlOnly", "mandrake.rsw.swbestiary", None, {})}
    return scene.WORLD


def opened(W=None, **needs):
    W = W or world()
    return W, scene.open("ArchSmall", needs=needs or None)


def untouched(W):
    """Nothing is left of an open that refused: no lock, no calm, no session record, no load, no game session."""
    st = json.loads(W.game.env.get(scene.GAME_STATE, "{}"))
    must(W.lock is None, "the lock is still held")
    must(not W.game.calm_on, "the calm is still on")
    must(not W.game.loads, "a map was loaded: %s" % W.game.loads)
    must(not W.game.session, "the game's session is still open")
    return st.get("session")


# ------------------------------------------------------------------------------- the 22 checks of the ticket
def test_open_refuses_unknown_game():
    W = world()
    e = refused("UNKNOWN_GAME", scene.open, "ArchHuge")
    must("ArchSmall" in e.repair and "Steve2" in e.repair, "the four names are not in the message")
    must(not W.game.log and untouched(W) is None, "something was asked of a game")


def test_open_refuses_game_held():
    W = world()
    W.lock_code = 75
    e = refused("GAME_HELD", scene.open, "archsmall")
    must("planted" in e.repair, "the holder is not named")
    W.lock_code = 0
    refused("GAME_HELD", scene.open, "Steve1")
    must(not W.game.log and untouched(W) is None, "something was asked of a game")


def test_open_refuses_owner_hold():
    W = world()
    W.lock_code = 3
    refused("OWNER_HOLD", scene.open, "ArchSmall")
    must(not W.game.log and untouched(W) is None, "something was asked of a game")


def test_open_refuses_owner_hold_under_an_inherited_take():
    W = world()
    gl = scene_world._import("game_lock", scene_world.RIMFLOW)
    control = scene_world._import("control", scene_world.RIMFLOW)
    with tempfile.TemporaryDirectory() as d:
        lock = os.path.join(d, "driver.json")
        db = os.path.join(d, "control.db")
        take = json.dumps({"identity": gl.driver_lock.my_identity(), "seat": "BENCH", "generation": 7,
                           "purpose": "window take"})
        with open(lock, "w", encoding="utf-8") as f:
            f.write(take)
        with patch.dict(os.environ, {"RM_CONTROL_DB": db}), patch.object(gl, "lock_path", return_value=lock):
            control.init(db)
            control.switch("game:b", True, "his walk", p=db)
            q = gl.query("b")
            must(q["state"] == "HELD" and q["code"] == 3 and q["mine"], "wrong lock setup: %s" % q)
            W.lock_take = scene_world.RealWorld().lock_take
            with patch.object(W, "connect", side_effect=AssertionError("scene connected during OWNER_HOLD")) as connect:
                refused("OWNER_HOLD", scene.open, "ArchSmall")
                connect.assert_not_called()
        with open(lock, encoding="utf-8") as f:
            must(f.read() == take and W.released == 0, "the inherited take was changed")


def test_open_refuses_session_open():
    W = world()
    held = json.dumps({"pid": W.game.pid, "stamps": [], "session": {"id": "scn_other", "driver": {"pid": 9}, "script": "x", "calm": False}})
    W.game.env[scene.GAME_STATE] = held
    e = refused("SESSION_OPEN", scene.open, "ArchSmall")
    must("scn_other" in e.repair and "attach" in e.repair, "the session and the repair are not named")
    must((untouched(W) or {}).get("id") == "scn_other" and W.game.env[scene.GAME_STATE] == held, "the other session's record was changed")


def test_open_refuses_mod_not_loaded():
    W = world()
    e = refused("MOD_NOT_LOADED", scene.open, "ArchSmall", needs={"mods": ["FlowWorks", "Absent"]})
    must("Absent" in e.repair and "FlowWorks," not in e.repair and "./game" in e.repair, "the mod and the commands: %s" % e.repair)
    must(untouched(W) is None, "a session record was left")


def test_open_refuses_wrong_build():
    W = world()
    W.verdict = {"verdict": "WRONG_BUILD", "why": ["rimmandrakeflowworks.dll: the loaded code is not in the committed file"]}
    e = refused("WRONG_BUILD", scene.open, "ArchSmall", needs={"mods": ["FlowWorks"]})
    must("deploy_custom_mods.py --mod FlowWorks" in e.repair, "the deploy command is missing")
    must(untouched(W) is None, "a session record was left")


def test_open_refuses_canonical_save():
    W = world()
    for name in ("ASHKARR_WORLDMAP_FULL", "ashkarr_worldmap_full", "Canon_x"):
        refused("CANONICAL_SAVE", scene.open, "ArchSmall", needs={"map": name})
    must(not W.game.log and untouched(W) is None, "something was asked of a game")


def test_open_refuses_fixture_missing():
    W = world()
    e = refused("FIXTURE_MISSING", scene.open, "ArchSmall", needs={"map": "RM_TestSite_river"})
    must("cp " in e.repair and "RM_TestSite_river" in e.repair, "the copy command is missing")
    refused("FIXTURE_MISSING", scene.open, "ArchSmall", needs={"map": "fresh:moon"})
    W.game.saves += ["x%d" % i for i in range(60)] + ["RM_TestSite_river"]      # on the last page of the list
    W.game.loads = []
    with scene.open("ArchSmall", needs={"map": "rm_testsite_RIVER"}) as s:
        must(s.opened[2]["did"], "the fixture was not loaded")
    must(W.game.loads == ["rm_testsite_RIVER"] and W.lock is None, "loads %s" % W.game.loads)


def test_open_phase_report_names_refusing_phase_and_what_was_put_back():
    W = world()
    W.game.calm["verdict"] = "NOT_CALM"
    W.game.calm["controls"][14] = {"name": "mental_states", "status": "NOT_CALM", "detail": "1 found", "things": ["Human12 Berserk"]}
    e = faulted("NOT_CALM", scene.open, "ArchSmall", needs={"map": "fresh:quicktest", "calm": "standard"})
    by = {p["phase"]: p for p in e.report}
    must([p["phase"] for p in e.report] == ["lock", "identify", "load", "settle", "calm", "arm"], "six phases in order")
    must([p["state"] for p in e.report] == ["done"] * 4 + ["refused", "not reached"], "states %s" % [p["state"] for p in e.report])
    must(any("released the calm" in x for x in by["calm"]["put_back"]) and any("released" in x for x in by["lock"]["put_back"]), "put back: %r" % e.report)
    must(any("NOT PUT BACK" in x for x in by["load"]["put_back"]), "the load that stays is not said")
    must("Human12 Berserk" in str(e) and "calm" in str(e), "the thing is not named in the message")
    must(W.lock is None and not W.game.calm_on, "the lock or the calm was left")


def test_open_receipt_build_comes_from_game():
    W, s = opened(mods=["FlowWorks"])
    b, ld = s.receipt.build, W.game.running_mods["loaded"]
    must(b["list"] == ld["listFingerprint"] and b["version"] == ld["gameVersion"], "the list and the version")
    must(b["dlls"]["RimMandrakeFlowWorks"]["mvid"] == "1c12b538-3bb2-45f5-8b8e-8d09a7ef04b3", "the DLL is not the loaded one: %s" % b["dlls"])
    must(b["companion"]["source_hash"] == ld["companion"]["srcHash"] and "the-hash-that-the-repo-holds" not in json.dumps(b), "a hash of the repo is in the build lines")
    must(b["companion"]["is_source_at_this_commit"] is False, "the difference is not said")
    must(s.run(until=20, limit=200).receipt.build == b, "the run's receipt has other build lines")


def test_run_refuses_no_limit():
    W, s = opened()
    n = len(W.game.log)
    for bad in (None, 0, -5, True, 2.5, "100"):
        refused("NO_LIMIT", s.run, 20, limit=bad)
    must(len(W.game.log) == n, "the game was asked")


def test_run_refuses_game_running():
    W, s = opened()
    W.game.status["paused"] = False
    refused("GAME_RUNNING", s.run, 20, limit=200)
    must(W.game.starts == 0, "a run was started")


def test_run_refuses_run_active():
    W, s = opened()
    s.run(until=20, limit=200)
    W.game.run["polls"] = 99
    e = refused("RUN_ACTIVE", s.run, 20, limit=200)
    must(W.game.run["run"] in e.repair and "cancel_run" in e.repair and W.game.starts == 1, "the live run is not named")
    must(s.cancel_run() is True and s.run(until=20, limit=200).hit, "after the cancel a run starts")


def test_run_refuses_unrecorded_value():
    W, s = opened()
    n = len(W.game.log)
    refused("UNRECORDED_VALUE", s.run, {"cmp": [{"p": "pawn.mood"}, ">", 3]}, limit=9)
    refused("UNRECORDED_VALUE", s.run, c.value("Human1078", "GetLord()") == "x", limit=9)
    refused("UNRECORDED_VALUE", s.run, (c.pawn("Human1078").dead == True).optional(), limit=9)  # noqa: E712
    refused("UNRECORDED_VALUE", s.run, {"all": []}, limit=9)
    must(len(W.game.log) == n, "the game was asked")


def test_run_refuses_bad_path():
    W, s = opened()
    n = len(W.game.log)
    for of, path in (("Human1078", "TakeDamage()"), ("Human1078", ""), ("Human1078", "a..b"), ("Human 1078", "x"), ("Human1078", "x[-1]"), (None, "x")):
        refused("BAD_PATH", s.run, 20, limit=200, record=[c.track(of, path)])
    must(len(W.game.log) == n, "the game was asked")
    refused("BAD_PATH", s.run, 20, limit=200, record=[c.track("static:RimMandrake.X", "on")])   # the slice cannot read it
    must(W.game.starts == 0, "a run was started")
    for path in ("positionInt.x", "health.hediffSet.hediffs[0]._size", "comp<RM_CompX>.held", "grid[3,4]"):
        must(c.bad_path("Human1078", path) is None, "%s is in the grammar" % path)


def test_run_refuses_session_closed():
    W, s = opened()
    s.close()
    n = len(W.game.log)
    refused("SESSION_CLOSED", s.run, 20, limit=200)
    refused("SESSION_CLOSED", s.raw, "jawa/map_info")
    must(len(W.game.log) == n, "the game was asked")


def test_run_unreadable_value_stops_as_unknown():
    for state in ("unknown", "hit", "done"):        # the hand says so itself, or says hit or limit over an unreadable value
        W, s = opened()
        W.game.script = {"state": state, "ticks": 20, "tracks": {"Human1078.positionInt.x": [(0, "ok", 5), (12, "gone", None)]}}
        r = s.run(until=c.value("Human1078", "positionInt.x") > 900, limit=20)
        must(r.why == "unknown" and "Human1078.positionInt.x was gone from tick 13" in r.detail, "%s: why %s, %s" % (state, r.why, r.detail))
        faulted("CONDITION_UNKNOWN", lambda: r.hit)
        v = r.values["Human1078.positionInt.x"]
        must(v.state == "gone", "the value is %r" % v)
        faulted("VALUE_NOT_READ", lambda: v.v)
        for op in (lambda: bool(v), lambda: v == 0, lambda: v < 1, lambda: int(v)):
            try:
                op()
            except TypeError:
                continue
            raise AssertionError("a gone value was used as a number")
        must(any("gone on 9 tick(s), first on 13" in x for x in r.receipt.could_not_look), "could_not_look: %s" % r.receipt.could_not_look)


def test_run_unreadable_thing_target_stops_as_unknown():
    for of in ("Fire1", "thing:Fire1"):
        W, s = opened(world(run_until=True))
        W.game.script = {"state": "done", "ticks": 20, "tracks": {"thing:Fire1.fireSize": [(0, "ok", 1), (12, "gone", None)]}}
        r = s.run(until=(c.value(of, "fireSize") < -1) & (c.game.tick < 0), limit=20)
        must(r.why == "unknown", "%s gave %s for a gone condition value" % (of, r.why))
        faulted("CONDITION_UNKNOWN", lambda: r.hit)
        must(r.values["Fire1.fireSize"].state == "gone", "the trace lost the gone value")


def test_run_lost_reply_is_recovered_by_request_id():
    for ru in (True, False):
        W = world(run_until=ru)
        s = scene.open("ArchSmall")
        tool = scene_hands.RUN_UNTIL if ru else scene_hands.SLICE
        W.game.script = {"state": "hit", "ticks": 20, "tracks": {}}
        W.game.lose = {tool + ":start", tool + ":status"} if ru else {tool + ":start"}
        r = s.run(until=c.game.tick >= 21, limit=200)
        must(r.why == "hit" and r.tick == 21 and W.game.starts == 1, "%s: %s, %d starts" % (tool, r, W.game.starts))
        must(any("the reply to the start was lost" in x for x in r.receipt.could_not_look), "the loss is not said")
        if ru:
            sent = [a for t, a in W.game.log if t == tool]
            must(len({a["request"] for a in sent}) == 1 and sent[0]["request"] == r.request, "the id was not given before the call, or it changed")
        else:
            must(any("no request id" in x for x in r.receipt.could_not_look), "the slice's limit is not said")
    W = world(run_until=True)
    s = scene.open("ArchSmall")
    real = W.game._run_until
    W.game._run_until = lambda a: {"success": False, "refused": "UNKNOWN_REQUEST"} if a["action"] == "status" else real(a)
    W.game.lose = {scene_hands.RUN_UNTIL + ":start"}
    e = faulted("REPLY_LOST", s.run, 20, limit=200)
    must(e.request and W.game.starts == 1, "the fault carries no id, or the run was started again")


def test_run_lost_reply_passes_the_pending_guard():
    with patch.dict(os.environ, {"RIMBRIDGE_SESSION_LOG": "", "RIMBRIDGE_EVIDENCE_LOG": ""}):
        import rimbridge_client as rb

    class StubTransport(rb.RimBridge):
        def connect(self):
            self.sock = object()
            for marker in rb.outstanding_indeterminate():
                pending.append(marker["cid"])
                for name, args in ((tool, {"action": "start"}), (tool, {"action": "cancel"}), ("jawa/damage", {})):
                    try:
                        self.call(name, args, check=False)
                    except rb.IndeterminateError:
                        continue
                    raise AssertionError("%s %s bypassed the pending guard" % (name, args))

        def close(self):
            self.sock = None

        def _set_call_timeout(self, seconds):
            self.timeout = seconds

        def _request(self, method, params=None):
            if method == "tools/list":
                return {"tools": W.game.tools}
            must(method == "tools/call", "unexpected request %s" % method)
            if params["name"] == rb.JOURNAL_TOOL:
                return {"operations": []}
            try:
                return W.game.call(params["name"], params["arguments"])
            except scene.ReplyLost as e:
                raise rb.RimBridgeError(str(e))

    def connect(_letter):
        b = scene_world.RealBridge.__new__(scene_world.RealBridge)
        b.rb, b.where, b.S = rb, ("127.0.0.1", 12345, "stub"), None
        b._open()
        return b

    for run_until in (True, False):
        W = world(run_until=run_until)
        W.connect = connect
        pending = []
        tool = scene_hands.RUN_UNTIL if run_until else scene_hands.SLICE
        for desc in W.game.tools:
            if desc["name"] in (scene_hands.SESSION, scene_hands.RUN_UNTIL):
                desc["inputSchema"]["properties"] = dict.fromkeys(("action", "driver", "request", "until", "limit", "speed", "record"))
        with tempfile.TemporaryDirectory() as d, patch.object(rb, "EVIDENCE_LOG", os.path.join(d, "calls.jsonl")), \
                patch.object(rb, "RimBridge", StubTransport), patch.object(rb, "_driver_crossing", return_value=None), \
                patch.object(rb, "_deadline_left", return_value=None), patch.object(rb, "game_starts", return_value=[0]):
            s = scene.open("ArchSmall")
            W.game.lose = {tool + ":start"}
            try:
                r = s.run(until=c.game.tick >= 21, limit=200)
            except scene.Fault as e:
                pending = rb.outstanding_indeterminate()
                if e.name == "REPLY_LOST" and [p["tool"] for p in pending] == [tool] and "IndeterminateError" in e.detail:
                    raise AssertionError("%s status was blocked by the lost start marker" % tool) from e
                raise
            must(r.hit and r.tick == 21 and s._run["run"] == W.game.run["run"], "the original run was not returned")
            sent = [a for t, a in W.game.log if t == tool and a["action"] == "start"]
            must(len(sent) == W.game.starts == 1 and not rb.outstanding_indeterminate(), "the start was repeated or its marker was left")
            with open(rb.EVIDENCE_LOG, encoding="utf-8") as f:
                settled = [row for row in map(json.loads, f) if row["ev"] == "reconciled"]
            must(len(settled) == 1 and [settled[0]["cid"]] == pending and settled[0]["as"] == "applied",
                 "the original start marker was not recorded as applied")
            s.close()


def test_raw_undeclared_tool_marks_the_process_and_a_new_session_carries_it():
    W, s = opened()
    must(s.raw("jawa/map_info").receipt.stamps == [], "a declared read-only tool stamped")
    r = s.raw("jawa/damage", damageDef="Bullet", amount=1, thingId="Human1")
    must(r.receipt.stamps == ["EXPLORED"] and "does not know what it changed" in r.receipt.did[0], "no stamp: %r" % r.receipt.stamps)
    i = [t for t, _a in W.game.log].index("jawa/damage")
    must(any(a.get("method") == "SetEnvironmentVariable" and "EXPLORED" in a["args"] for _t, a in W.game.log[:i]), "the mark was not set before the call")
    must(s.run(until=20, limit=200).receipt.stamps == ["EXPLORED"], "the run carries no stamp")
    s.close()
    s2 = scene.open("ArchSmall")
    must(s2.receipt.stamps == ["EXPLORED"] and s2.run(until=20, limit=200).receipt.stamps == ["EXPLORED"], "a new session in a marked process has no stamp")
    s2.close()
    W.games["b"] = g = F.FakeGame()                     # the game was restarted; its block still holds the old text (a child inherits it)
    g.env, g.pid = dict(W.game.env), 777
    g.env[scene.GAME_STATE] = json.dumps({"pid": 39620, "stamps": ["EXPLORED"], "session": {"id": "scn_old"}})
    g.running_mods["loaded"]["pid"] = 777
    s3 = scene.open("ArchSmall")
    must(s3.receipt.stamps == [], "a new process carries the old process's mark")


def _tree(files):
    d = tempfile.mkdtemp()
    for n, t in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, n)), exist_ok=True)
        with open(os.path.join(d, n), "w", encoding="utf-8") as f:
            f.write(t)

    def git(*a):
        p = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", d] + list(a), capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout if p.returncode == 0 else p.stdout + p.stderr
    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("commit", "-qm", "x")
    return d, git


GOOD = "import scene\nfrom scene import cond as c\nwith scene.open('ArchSmall') as s:\n    print('RAN', s.run(until=20, limit=200).receipt.commit)\n"


def test_accept_refuses_a_dirty_tree_and_an_older_layer():
    d, git = _tree({"s/good.py": GOOD, "s/old.py": "import validation_core\n", "s/old2.py": "import scene\ndef f():\n    from scenes import scenelib as S\n",
                    "s/old3.py": "import importlib\nm = importlib.import_module('rimbridge_client')\n", "s/old4.py": "import scene, mine\n",
                    "s/mine.py": "from modcheck import helpers\n", "s/near.py": "import scene, helpers\n", "s/helpers.py": "X = 1\n"})
    p = lambda n: os.path.join(d, "s", n)  # noqa: E731
    W = world()
    W.repo, W.git = d, git
    head = git("rev-parse", "HEAD")[1].strip()
    for n in ("old.py", "old2.py", "old3.py", "old4.py"):
        refused("IMPORTS_OLD_LAYER", scene.check_accept, p(n), d, git)
    must(scene.check_accept(p("near.py"), d, git) == head, "a scene's own helpers.py is no older layer")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = scene.main(["accept", p("good.py")])
    must(rc == 0 and "RAN " + head in out.getvalue(), "accept: rc %s, %s" % (rc, out.getvalue()))
    with open(p("extra.txt"), "w") as f:
        f.write("x")
    e = refused("TREE_NOT_CLEAN", scene.check_accept, p("good.py"), d, git)
    must("extra.txt" in e.repair, "the path is not named")
    refused("SCRIPT_NOT_IN_REPO", scene.check_accept, __file__, d, git)
    os.remove(p("extra.txt"))
    with open(p("good.py"), "a") as f:
        f.write("# edited\n")
    refused("TREE_NOT_CLEAN", scene.check_accept, p("good.py"), d, git)
    n = len(W.game.log)
    with contextlib.redirect_stdout(io.StringIO()):
        must(scene.main(["accept", p("good.py")]) == 3 and len(W.game.log) == n, "a refused script ran")


GAME_SAYER = "import scene\nwith scene.open('ArchSmall') as s:\n    print('GAME', s.game)\n"


def test_accept_game_names_the_free_game_over_the_script_default():
    """ExplosiveKnockback 0.2.0 visit 2: nine committed scenes name ArchSmall in their source; ArchSmall was held by another
    run while ArchBig sat free under the visit's driver, so no check could run. `accept <script> --game <name>` names the game
    at the command line (a name, never the shell's environment); without it the script's own game stands."""
    d, git = _tree({"s/say.py": GAME_SAYER})
    W = world()
    W.repo, W.git = d, git
    for argv, want in ((["accept", os.path.join(d, "s", "say.py"), "--game", "ArchBig"], "driver lock of ArchBig"),     # the fake answers as ArchSmall only
                       (["accept", os.path.join(d, "s", "say.py")], "GAME ArchSmall")):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = scene.main(argv)
        must(want in out.getvalue() and (rc == 0) == (want == "GAME ArchSmall"), "%s: rc %s, %s" % (argv[2:], rc, out.getvalue()[-300:]))
        must(scene.LAUNCH.get("game") is None, "accept left its --game in LAUNCH")
    with contextlib.redirect_stdout(io.StringIO()):
        must(scene.main(["accept", os.path.join(d, "s", "say.py"), "--game", "Nowhere"]) == 3, "an unknown --game is refused by name")


LEDGER_WRITER = ("import os, scene\nwith scene.open('ArchSmall') as s:\n    print('RAN', s.run(until=20, limit=200).receipt.commit)\n"
                 "v = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'design', 'concepts', 'WMod', 'version')\n"
                 "os.makedirs(v, exist_ok=True)\nopen(os.path.join(v, 'scene_runs.jsonl'), 'a').write('{}\\n')\n")


def test_accept_keeps_its_identity_when_the_judge_appends_the_scene_ledger():
    # the judge appends the mod's scene ledger (scene_runs.jsonl) at the end of an accept run; the run then read
    # "THE TREE CHANGED DURING THE RUN" and the next accept was refused TREE_NOT_CLEAN (2026-11-24, ArchSmall)
    d, git = _tree({"s/good.py": GOOD, "s/ledger.py": LEDGER_WRITER})
    W = world()
    W.repo, W.git = d, git
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = scene.main(["accept", os.path.join(d, "s", "ledger.py")])
    must(rc == 0 and "TREE CHANGED" not in out.getvalue(), "the judge's ledger line cost the run its identity: %s" % out.getvalue()[-300:])
    head = git("rev-parse", "HEAD")[1].strip()
    must(scene.check_accept(os.path.join(d, "s", "good.py"), d, git) == head, "a ledger line left by the last run refused the next accept")
    with open(os.path.join(d, "s", "extra.txt"), "w") as f:
        f.write("x")
    refused("TREE_NOT_CLEAN", scene.check_accept, os.path.join(d, "s", "good.py"), d, git)


def test_explore_run_is_explored():
    W = world()
    old, sys.stdin = sys.stdin, io.StringIO("r = s.run(until=20, limit=200)\nprint('STAMPS', r.receipt.stamps)\n")
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = scene.main(["explore", "ArchSmall"])
    finally:
        sys.stdin = old
        scene.LAUNCH.update(mode="script")
    must(rc == 0 and "STAMPS ['EXPLORED']" in out.getvalue(), "rc %s: %s" % (rc, out.getvalue()[-300:]))
    must(W.lock is None and untouched(W) is None, "the session was not ended")


def test_help_prints_ten_names_and_each_built_page_matches_its_signature():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        must(scene.main(["help"]) == 0, "help")
    rows = re.findall(r"^\| \d+ \| `(?:scene|s)\.(\w+)` \|", out.getvalue(), re.M)
    must(rows == list(scene.NAMES) and len(rows) == 10, "the names: %s" % rows)
    for n in scene.NAMES:
        must(os.path.isfile(os.path.join(scene.PAGES, n + ".md")) and scene.page("s." + n), "no page for %s" % n)
    for n in scene.BUILT:
        for fn, args in scene.page_arguments(n).items():
            must(sorted(args) == sorted(scene.signature(fn)), "page %s says %s takes %s; the function takes %s" % (n, fn, args, scene.signature(fn)))
    planted = scene.page("run").replace("| `speed` |", "| `pace` |")
    must("pace" in scene.page_arguments("run", planted)["run"], "the reader of the page is blind")
    with contextlib.redirect_stdout(io.StringIO()):
        must(scene.main(["help", "nothing"]) == 3 and scene.main(["help", "cond"]) == 0, "help of another name")


# ------------------------------------------------------------------------------- the other promises of the pages
def test_run_true_at_start_plays_no_tick():
    for run_until in (False, True):
        W, s = opened(world(run_until=run_until))
        W.game.script = {"state": "hit", "ticks": 0, "tracks": {}}
        tick = W.game.status["tick"]
        r = s.run(until=c.game.tick >= 1, limit=200)
        tool = scene_hands.RUN_UNTIL if run_until else scene_hands.SLICE
        (sent,) = [json.loads(a["until"]) for t, a in W.game.log if t == tool and a["action"] == "start"]
        must(tick == 1 and sent == {"cmp": [{"p": "game.tick"}, ">=", tick]}, "%s sent until=%s at tick %s" % (tool, sent, tick))
        must(r.hit and r.tick == r.tick_from == 1, "%r from %s" % (r, r.tick_from))


def test_run_limit_is_not_a_hit():
    W, s = opened()
    W.game.script = {"state": "done", "ticks": 0, "tracks": {}}
    r = s.run(until=c.game.tick >= 900, limit=30)
    must(r.why == "limit" and r.hit is False and r.tick == 31, "%r" % r)


def test_run_dead_member_stays_in_group_as_gone():
    """The Python half: a group member that is gone keeps its name in the values; gone_ok makes it readable."""
    W = world(run_until=True)
    s = scene.open("ArchSmall")
    W.game.script = {"state": "hit", "ticks": 20, "tracks": {"raiders[0].positionInt.x": [(0, "ok", 1)], "raiders[1].positionInt.x": [(0, "ok", 2), (5, "gone", None)]}}
    r = s.run(until=c.gone_ok("raiders[1]", "positionInt.x", c.value("raiders[1]", "positionInt.x") > 9), limit=200)
    must(r.hit and r.values["raiders[1].positionInt.x"].state == "gone" and r.values["raiders[0].positionInt.x"].v == 1, "%r %r" % (r, r.values))
    W.game.script = {"state": "hit", "ticks": 5, "tracks": {"thing:Human1078.positionInt.x": [(0, "ok", 1), (2, "gone", None)],
                                                            '{"f":"dead","p":"pawn.state","pawn":"Human1078"}': [(0, "unbound", None)]}}
    r = s.run(until=c.value("Human1078", "positionInt.x") > 3, limit=200)
    must(r.why == "unknown" and "Human1078.positionInt.x" in r.values, "the game's name of a track is not the script's: %r %r" % (r, r.values))
    r = s.run(until=c.pawn("Human1078").dead == True, limit=200)  # noqa: E712
    must(r.why == "unknown" and "pawn.state(f=dead,pawn=Human1078)" in r.detail, "%r" % r)


def test_run_stalled_clock_is_cancelled():
    W, s = opened()
    W.game.script = {"state": "hit", "ticks": 20, "tracks": {}, "polls": 10 ** 6}
    r = s.run(until=20, limit=200)
    must(r.why == "fault" and "stood still" in r.detail, "%r" % r)


def test_run_bind_refusal_is_by_name():
    W, s = opened()
    W.game.script = {"state": "hit", "ticks": 1, "tracks": {}, "bind": "$.until.cmp[0]"}
    refused("UNRECORDED_VALUE", s.run, c.value("Human1078", "noSuchField") == 3, limit=9)
    W.game.script["bind"] = "$.sample.probes.x"
    refused("BAD_PATH", s.run, 20, limit=9, record=[c.track("Human1078", "noSuchField")])


def test_raw_refuses_unknown_tool():
    W, s = opened()
    e = refused("UNKNOWN_TOOL", s.raw, "jawa/map_inf")
    must("jawa/map_info" in e.repair, "the near name is missing")


def test_raw_refuses_bad_args():
    W, s = opened()
    e = refused("BAD_ARGS", s.raw, "jawa/static_call", kind="X")
    must("kind" in e.repair and "type" in e.repair, "the argument and the schema: %s" % e.repair)


def test_raw_refuses_session_closed():
    W, s = opened()
    s.close()
    refused("SESSION_CLOSED", s.raw, "jawa/map_info")


def test_raw_refuses_life_cycle_tool():
    W, s = opened()
    n = len(W.game.log)
    for t in ("rimworld/load_game", "rimworld/load_game_ready", "rimworld/start_debug_game_ready", "rimworld/go_to_main_menu", "jawa/session"):
        refused("LIFE_CYCLE_TOOL", s.raw, t)
    must(len(W.game.log) == n, "the game was asked")


def test_raw_changing_call_stamps_explored():
    W, s = opened()
    r = s.raw("jawa/static_call", type="X", method="Y", args="")
    must(r.receipt.stamps == ["EXPLORED"] and r["success"] is True, "jawa/static_call left no stamp")


def test_raw_undeclared_tool_is_treated_as_changing():
    must(scene._read_only({"name": "jawa/a", "description": "READ ONLY. x"}), "declared")
    must(not scene._read_only({"name": "jawa/a", "description": "Read a thing"}) and not scene._read_only({"name": "jawa/a"}), "undeclared")
    must(not scene._read_only({"name": "jawa/static_call", "description": "READ ONLY."}), "jawa/static_call is never read-only")


def test_raw_call_is_in_the_trace():
    W, s = opened()
    s.raw("jawa/damage", damageDef="Bullet", amount=1, thingId="H")
    must(any("scene raw jawa/damage" in m and '"amount": 1' in m for m in W.game.marks), "the game's record: %s" % W.game.marks)


def test_raw_batch_arguments_are_in_the_trace():
    W = world()
    tool = "jawa/set_terrain_batch"
    W.game.tools.append({"name": tool, "parameters": [{"name": "ops", "required": True}]})
    s = scene.open("ArchSmall")
    args = {"ops": ";".join("PavedTile:%d,20,1,1" % x for x in range(20, 50))}
    prefix = "scene raw %s " % tool
    s.raw(tool, **args)
    (mark_at, payload), = [(i, a["why"][len(prefix):]) for i, (t, a) in enumerate(W.game.log)
                           if t == "jawa/telemetry_mark" and a["why"].startswith(prefix)]
    (call_at, sent), = [(i, a) for i, (t, a) in enumerate(W.game.log) if t == tool]
    must(mark_at < call_at and sent == args, "the marker was late or the call was changed")
    must(prefix + payload in W.game.marks, "the game's record does not hold the marker")
    try:
        marked = json.loads(payload)
    except ValueError as e:
        raise AssertionError("batch marker holds incomplete argument JSON (%d characters)" % len(payload)) from e
    must(marked == sent, "the marker arguments differ from the call")
    W.game.fail["jawa/telemetry_mark"] = "writer dropped the marker row"
    r = s.raw(tool, **args)
    must(any(tool in line and "writer dropped the marker row" in line for line in r.receipt.could_not_look),
         "the missing batch marker was not reported")


def test_raw_call_without_a_mark_is_not_made():
    W, s = opened()
    real = W.game._do
    W.game._do = lambda t, a: F.rec("env_set") if a.get("method") == "SetEnvironmentVariable" else real(t, a)      # the game drops the write
    faulted("MARK_NOT_HELD", s.raw, "jawa/damage", damageDef="B", amount=1, thingId="H")
    must(not any(t == "jawa/damage" for t, _a in W.game.log), "the call was made with no mark")


def test_lock_that_could_not_be_read_is_a_fault():
    W = world()
    W.lock_code = 2
    faulted("COULD_NOT_LOOK", scene.open, "ArchSmall")
    must(untouched(W) is None, "left")
    W = world()
    W.game.tools = []
    faulted("COULD_NOT_LOOK", scene.open, "ArchSmall")
    W = world()
    W.game.running_mods.pop("loaded")
    faulted("COULD_NOT_LOOK", scene.open, "ArchSmall", needs={"mods": ["Absent"]})
    W = world()
    W.game.deny_static = True
    faulted("COULD_NOT_LOOK", scene.open, "ArchSmall")
    W = world()
    W.game.fail = {"rimworld/list_saves": "broken"}
    faulted("COULD_NOT_LOOK", scene.open, "ArchSmall", needs={"map": "RM_TestSite_river"})
    must(W.lock is None, "left")
    W = world()
    W.game.running_mods["loaded"]["gameKey"] = "archmagi"
    faulted("WRONG_GAME", scene.open, "ArchSmall")
    W, s = opened(mods=["XmlOnly"])
    must(any("XmlOnly ships no DLL" in x for x in s.receipt.could_not_look), "a mod with no DLL reads as checked")
    W = world()
    W.repo = HERE
    W.git = lambda *a: (128, "fatal: not a git repository")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = scene.main(["accept", os.path.join(HERE, "scene.py")])
    must(rc == 2 and "COULD NOT LOOK" in out.getvalue(), "a tree that could not be read: rc %s %s" % (rc, out.getvalue()))


def test_trace_that_is_not_whole():
    for plant in ({"no_close": True}, {"gap": True}, {"dropped": 2}, {"drained": False}):
        W, s = opened()
        W.game.script = dict({"state": "hit", "ticks": 20, "tracks": {}}, **plant)
        e = faulted("TRACE_INCOMPLETE", s.run, 20, limit=200)
        must(e.request and e.receipt.did, "%s: the fault carries no id or no receipt" % plant)
    for name in ("trace_hit", "trace_limit"):
        must(scene_hands.trace_fault(F.rec(name)) is None and scene_hands.ran_on(F.rec(name)) is None, "a real trace reads as faulty")
    gap = F.rec("trace_hit")
    gap.pop(5)
    gap[-1]["rows"] -= 1
    must("gap" in (scene_hands.trace_fault(gap) or ""), "a gap that the count of rows does not show")
    lost = F.rec("trace_hit")
    lost[-1]["rows"] += 1
    must("counts" in scene_hands.trace_fault(lost), "a lost row")


def test_game_that_ran_on():
    for plant, want in (({"ran_on": 2}, "RAN_PAST_END"), ({"paused": False}, "PAUSE_REFUSED"), ({"fault": "ran_past_end"}, "RAN_PAST_END")):
        W, s = opened()
        W.game.script = dict({"state": "hit", "ticks": 20, "tracks": {}}, **plant)
        faulted(want, s.run, 20, limit=200)
    for after, want in (({"paused": False}, "PAUSE_REFUSED"), ({"tick": 40}, "RAN_PAST_END")):     # only the second reading shows it
        W, s = opened()
        real = W.game._play

        def play(*a, **k):
            W.game.after_run = after
            return real(*a, **k)
        W.game._play = play
        faulted(want, s.run, 20, limit=200)


def test_close_puts_back_also_after_an_error():
    W = world()
    try:
        with scene.open("ArchSmall", needs={"map": "fresh:quicktest", "calm": "standard"}) as s:
            must(W.game.calm_on and W.lock == "b", "open")
            raise ValueError("the script's own error")
    except ValueError:
        pass
    must(not W.game.calm_on and W.lock is None and json.loads(W.game.env[scene.GAME_STATE])["session"] is None, "left after an error")
    must(W.game.status["paused"] is True and s.closed, "paused")
    W = world()
    s = scene.open("ArchSmall", needs={"map": "fresh:quicktest", "calm": "standard"})
    W.game.fail = {"jawa/quiet_site": "broken"}
    e = faulted("CLOSE_INCOMPLETE", s.close)
    must("jawa/quiet_site" in str(e) and W.lock is None, "what was not put back is not named, or the lock was kept")
    W = world(run_until=True)
    with scene.open("ArchSmall"):
        must(W.game.session, "the game's session")
    must(W.game.session is None, "the game's session was left open")


def test_close_waits_for_the_session_writer():
    for finishes in (True, False):
        W, s = opened(world(run_until=True))
        s.run(until=20, limit=200)
        polls = []
        session = W.game._session

        def draining(a):
            if a["action"] == "close":
                W.game.session["stage"] = "closing"
                return session({"action": "state"})
            if W.game.session and W.game.session["stage"] == "closing":
                must(W.lock == "b" and W.released == 0, "the lock was released while the writer drained")
                polls.append(W.clock())
                if finishes and len(polls) == 3:
                    W.game.session["stage"] = "closed"
            return session(a)

        W.game._session = draining
        if finishes:
            s.close()
            must(W.game.session["stage"] == "closed", "close returned with the companion still closing")
            must(len(polls) == 3 and W.released == 1, "the lock was not released after the writer drained")
            W.game._session = session
            with scene.open("ArchSmall"):
                pass
        else:
            started = W.clock()
            e = faulted("CLOSE_INCOMPLETE", s.close)
            must("SESSION_NOT_CLOSED" in str(e) and "closing" in str(e), "the unfinished session is not named")
            must(polls and W.released == 1, "the close did not wait or did not release after the fault")
            must(60 <= W.clock() - started < 61, "the close did not use the companion's drain limit")


def test_session_of_another_is_lost_not_used():
    W, s = opened()
    W.game.env.clear()
    faulted("SESSION_LOST", s.run, 20, limit=200)
    must(W.game.starts == 0, "a run was started")


def test_end_session_ends_a_dead_driver_only():
    W = world()
    s = scene.open("ArchSmall", needs={"map": "fresh:quicktest", "calm": "standard"})
    W.lock = None                                       # the driver died: its lock is free at once
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        must(scene.main(["end-session", "ArchSmall"]) == 3 and W.game.calm_on, "a live driver's session was ended")
        W.dead = True
        must(scene.main(["end-session", "ArchSmall"]) == 0, out.getvalue())
    must(s.id in out.getvalue() and not W.game.calm_on and W.lock is None, out.getvalue())
    scene.open("ArchSmall").close()


def dead_driver(**game):
    """A session whose driver died with its run live. -> (world, the dead session)."""
    W, s = opened(world(run_until=True), calm="standard")
    s.run(until=20, limit=200)
    W.game.run.update(polls=5)                          # the run is live, and the clock runs
    W.game.status["paused"] = False
    for k, v in game.items():
        setattr(W.game, k, v)
    W.lock, W.dead = None, True                         # a dead process holds no lock
    return W, s


def test_attach_refuses_no_session():
    for W in (world(), world(run_until=True)):
        refused("NO_SESSION", scene.attach, "ArchSmall")
        must(W.lock is None, "the lock is still held")


def test_attach_refuses_driver_alive():
    W, s = dead_driver()
    W.dead = False
    e = refused("DRIVER_ALIVE", scene.attach, "ArchSmall")
    must(s.id in e.repair and "4242" in e.repair, "the driver is not named: %s" % e.repair)
    must(W.lock is None and W.game.calm_on and W.game.run["polls"] == 5 and W.game.session["driver"] == s.id, "something was changed")
    W.alive = lambda ident: None                        # could not look is not dead
    refused("DRIVER_ALIVE", scene.attach, "ArchSmall")
    W.game.env.clear()                                  # the game's session has no record of a process: only its lease can say
    refused("DRIVER_ALIVE", scene.attach, "ArchSmall")
    W.game.session["leaseEnded"] = True
    scene.attach("ArchSmall").close()


def test_attach_refuses_owner_hold():
    W, _s = dead_driver()
    W.lock_code = 3
    refused("OWNER_HOLD", scene.attach, "ArchSmall")
    W.lock_code = 75
    refused("GAME_HELD", scene.attach, "ArchSmall")


def test_attach_refuses_unknown_game():
    world()
    e = refused("UNKNOWN_GAME", scene.attach, "ArchHuge")
    must("ArchSmall" in e.repair and "Steve2" in e.repair, "the four names are not in the message")


def test_attach_pauses_a_running_game():
    W, old = dead_driver(open_act="act_7")
    s = scene.attach("ArchSmall")
    must(W.game.status["paused"] is True and W.game.session["driver"] == s.id, "%s" % W.game.session)
    st = s.state
    must(st.paused is True and st.open_act == "act_7" and st.last_run["why"] == "cancelled" and st.last_run["stage"] == "closed", "%r" % st)
    must(st.last_run["trace"] == "whole", "%r" % st.last_run)
    must(any("took the session %s" % old.id in x and "dead" in x for x in s.receipt.did), "%s" % s.receipt.did)
    s.close()
    must(not W.game.calm_on and W.lock is None and W.game.session is None, "what the dead driver left was not put back")
    W, _old = dead_driver()                             # a run with no closing record
    W.game.rows = [r for r in W.game.rows if r["rec"] != "close"]
    s = scene.attach("ArchSmall")
    must("not whole" in s.state.last_run["trace"] and any("not whole" in x for x in s.receipt.could_not_look), "%r" % s.state.last_run)
    W, s = opened()                                     # the older hand, with no session of its own
    s.run(until=20, limit=200)
    W.game.run.update(polls=500)
    W.lock, W.dead = None, True
    s2 = scene.attach("ArchSmall")
    must(W.game.run["state"] == "cancelled" and s2.state.last_run["run"] == W.game.run["run"], "the run of the older hand plays on")
    s2.close()


def test_attach_then_run_is_refused():
    W, _old = dead_driver()
    s = scene.attach("ArchSmall")
    n = W.game.starts
    refused("TAKEN_OVER", s.run, until=20, limit=200)
    refused("TAKEN_OVER", s.raw, "jawa/static_call", type="T", method="M", args="")
    must(W.game.starts == n and scene.EXPLORED not in s.state.stamps, "the new driver went on with the scene")
    s.raw("jawa/map_info")                              # a read is allowed
    s.close()
    W.dead = False
    with scene.open("ArchSmall") as t:
        t.run(until=20, limit=200)                      # the next session is its own


def test_abort_writes_closing_record():
    W, _old = dead_driver()
    s = scene.attach("ArchSmall")
    s.abort()
    must([a["action"] for t, a in W.game.log if t == "jawa/session"][-1] == "abort" and W.game.session is None, "the game's session was not aborted")
    must(W.lock is None and json.loads(W.game.env[scene.GAME_STATE])["session"] is None, "the lock or the record is left")
    must(W.game.calm_on and any("calm" in x for x in s.closed_report.could_not_look), "abort changes nothing else, and says what it leaves")
    refused("SESSION_CLOSED", s.run, until=20, limit=200)
    W, _old = dead_driver()                             # a driver that dies while it attaches leaves the session for the next one
    W.game.fail = {"rimbridge/get_bridge_status": "broken"}
    faulted("COULD_NOT_LOOK", scene.attach, "ArchSmall")
    must(W.lock is None and W.game.session, "a half attach closed the session, or kept the lock")
    W.game.fail = {}
    scene.attach("ArchSmall").abort()


def test_names_not_built_say_so():
    """0.3.0: all ten names are built; a verb or a piece that is not built refuses NOT_BUILT and names the ticket that builds it."""
    W, s = opened()
    must(sorted(scene.BUILT) == sorted(scene.NAMES) and callable(scene.contract), "the ten names")
    for verb in ("tune", "reload", "order"):
        e = refused("NOT_BUILT", getattr, s.act, verb)
        must("RIMMANDRAKE_" in e.repair, "no ticket for %s" % verb)
    must(not hasattr(s.act, "tune") and not hasattr(s, "nothing"), "hasattr")


def test_tools_and_raw_census():
    got = scene.tools("power net")
    must(0 < len(got) <= 10 and any(t.name == "jawa/get_power_nets_batch" for t in got), "%s" % got)
    must(scene.tools("zzqqxx") == [], "looked and found none is []")
    must([t for t in scene.tools("map_info") if t.name == "jawa/map_info"][0].read_only is True, "declared")
    with tempfile.TemporaryDirectory() as d:
        for n, t in (("a.py", "import scene\ns.raw('jawa/static_call', type='T', method='A')\ns.raw('jawa/x')\n"),
                     ("b.py", "from scene import cond\ns.raw('jawa/static_call', type='T', method='B')\ns.raw('jawa/x')\n"), ("c.py", "import other\ns.raw('jawa/x')\n"),
                     ("d.py", "import scene\ndef(\n")):
            with open(os.path.join(d, n), "w") as f:
                f.write(t)
        ops, looked, blind = scene.raw_census([os.path.join(d, n) for n in ("a.py", "b.py", "c.py", "d.py")])
    must({k: len(v) for k, v in ops.items()} == {"jawa/static_call T.A": 1, "jawa/static_call T.B": 1, "jawa/x": 2}, "%s" % ops)
    must(looked == 2 and len(blind) == 1, "%s looked, %s blind" % (looked, blind))


def t_a_refusal_changes_nothing():
    """The eight refusals above each end in untouched(); here the order: no changing call was made before the refusal."""
    for needs, name in (({"mods": ["Absent"]}, "MOD_NOT_LOADED"), ({"map": "RM_none"}, "FIXTURE_MISSING")):
        W = world()
        refused(name, scene.open, "ArchSmall", needs=needs)
        changed = [t for t, a in W.game.log if t in ("jawa/quiet_site", "rimworld/load_game_ready", "rimworld/pause_game", "jawa/telemetry_mark") or a.get("method") == "SetEnvironmentVariable"]
        must(not changed, "changed before the refusal: %s" % changed)
    refused("BAD_ARGS", scene.open, "ArchSmall", needs={"moods": 1})
    refused("BAD_ARGS", scene.open, "ArchSmall", needs={"mods": ["NoSuchMod"]})
    refused("BAD_ARGS", scene.open, "ArchSmall", needs={"calm": "loud"})


t_build_lines_come_from_the_game = test_open_receipt_build_comes_from_game
t_owner_hold_refuses_a_new_scene = test_open_refuses_owner_hold_under_an_inherited_take
t_could_not_look_is_not_a_refusal_and_not_clean = test_lock_that_could_not_be_read_is_a_fault
t_unreadable_is_never_false = test_run_unreadable_value_stops_as_unknown
t_a_lost_reply_is_found_by_its_id = test_run_lost_reply_is_recovered_by_request_id
t_true_at_start_plays_no_tick = test_run_true_at_start_plays_no_tick
t_a_trace_that_is_not_whole_is_a_fault = test_trace_that_is_not_whole
t_a_game_that_ran_on_is_a_fault = test_game_that_ran_on
t_the_game_holds_the_mark = test_raw_undeclared_tool_marks_the_process_and_a_new_session_carries_it
t_raw_arguments_are_recorded_before_the_call = test_raw_batch_arguments_are_in_the_trace
t_an_undeclared_tool_is_changing = test_raw_undeclared_tool_is_treated_as_changing
t_accept_needs_one_identity = test_accept_refuses_a_dirty_tree_and_an_older_layer
t_explore_is_stamped = test_explore_run_is_explored
t_close_puts_back = test_close_puts_back_also_after_an_error
t_a_name_not_built_says_so = test_names_not_built_say_so
t_help_equals_the_code = test_help_prints_ten_names_and_each_built_page_matches_its_signature
t_accept_game_names_the_free_game = test_accept_game_names_the_free_game_over_the_script_default


def run(tests):
    good = 0
    for t in tests:
        try:
            t()
            good += 1
            print("ok    " + t.__name__)
        except Exception as e:  # noqa: BLE001 - a test that dies is a failure with its cause, never a skip
            print("FAIL  %s: %s: %s" % (t.__name__, type(e).__name__, e))
    return good


FACTION_DIALOG = {"type": "VEF.Factions.Dialog_NewFactionSpawning", "forcePause": True, "buttons": ["Spawn", "Do nothing"]}


def test_load_answers_the_known_load_windows_only():
    """A save made before a mod's factions existed opens VEF's Dialog_NewFactionSpawning once per missing faction (live on ArchBig
    2026-11-25: the storeroom-pit fixture under the Knockback small list; the calm then refused NOT_CALM force_pause_windows). The load
    gives each one its approved answer, 'Do nothing', and says so; a window with no approved answer stays open for the calm to refuse.
    The windows open a few frames after the load returns (live: the first answer, made at the load's return, found none)."""
    W = world()
    W.game.saves.append("RM_TestSite_river")
    W.game.load_windows = [dict(FACTION_DIALOG, ID=7), dict(FACTION_DIALOG, ID=8)]
    with scene.open("ArchSmall", needs={"map": "RM_TestSite_river"}) as s:
        did = s.opened[3]["did"]
    must(W.game.windows == [] and getattr(W.game, "clicked", []) == ["Do nothing", "Do nothing"], "windows %s clicked %s" % (
        W.game.windows, getattr(W.game, "clicked", None)))
    must(any("answered 2 load window" in x and "Do nothing" in x for x in did), "the settle does not say what it answered: %s" % did)
    W = world()
    W.game.saves.append("RM_TestSite_river")
    W.game.load_windows = [{"ID": 9, "type": "Dialog_MessageBox", "forcePause": True, "buttons": ["OK"]}]
    with scene.open("ArchSmall", needs={"map": "RM_TestSite_river"}) as s:
        pass
    must([w["ID"] for w in W.game.windows] == [9] and not getattr(W.game, "clicked", None), "an unknown window was touched")


def test_lock_child_env_names_no_dropped_variable():
    """A Windows driver takes the lock through a WSL child. A variable it drops must leave WSLENV too: WSL passes a name that WSLENV
    lists and the parent lacks as an EMPTY value, and an empty RIMFLOW_DRIVER_LOCK reads as "no lock path" for ArchBig (seen live
    2026-11-24: scene.open on ArchBig refused COULD_NOT_LOOK while ArchSmall took its lock)."""
    env = {"WSLENV": "RM_GAME_INSTANCE:RM_GAME_USERDATA/p:GABP_TOKEN:RIMFLOW_DRIVER_LOCK/p:RM_INSTANCES_ROOT/p", "RIMFLOW_DRIVER_LOCK": "x",
           "RM_GAME_INSTANCE": "b", "RM_INSTANCES_ROOT": "D:\\i", "RM_SCENE_GEN": "4", "PATH": "p"}
    out = scene_world.lock_child_env(env, "RM_SCENE_GEN")
    assert "RIMFLOW_DRIVER_LOCK" not in out and "RM_GAME_INSTANCE" not in out and "RM_SCENE_GEN" not in out, out
    names = [w.split("/")[0] for w in out["WSLENV"].split(":") if w]
    assert "RIMFLOW_DRIVER_LOCK" not in names and "RM_GAME_INSTANCE" not in names, names
    assert "RM_INSTANCES_ROOT" in names and "GABP_TOKEN" in names and out["PATH"] == "p", out


def main():
    ticket = [test_open_refuses_unknown_game, test_open_refuses_game_held, test_open_refuses_owner_hold, test_open_refuses_session_open,
              test_open_refuses_mod_not_loaded, test_open_refuses_wrong_build, test_open_refuses_canonical_save, test_open_refuses_fixture_missing,
              test_open_phase_report_names_refusing_phase_and_what_was_put_back, test_open_receipt_build_comes_from_game,
              test_run_refuses_no_limit, test_run_refuses_game_running, test_run_refuses_run_active, test_run_refuses_unrecorded_value,
              test_run_refuses_bad_path, test_run_refuses_session_closed, test_run_unreadable_value_stops_as_unknown,
              test_run_lost_reply_is_recovered_by_request_id, test_raw_undeclared_tool_marks_the_process_and_a_new_session_carries_it,
              test_accept_refuses_a_dirty_tree_and_an_older_layer, test_explore_run_is_explored,
              test_help_prints_ten_names_and_each_built_page_matches_its_signature]
    more = [t_a_refusal_changes_nothing, t_accept_game_names_the_free_game, test_open_refuses_owner_hold_under_an_inherited_take,
            test_run_unreadable_thing_target_stops_as_unknown, test_run_lost_reply_passes_the_pending_guard,
            test_run_true_at_start_plays_no_tick, test_run_limit_is_not_a_hit, test_run_dead_member_stays_in_group_as_gone,
            test_run_stalled_clock_is_cancelled, test_run_bind_refusal_is_by_name, test_raw_refuses_unknown_tool, test_raw_refuses_bad_args,
            test_raw_refuses_session_closed, test_raw_refuses_life_cycle_tool, test_raw_changing_call_stamps_explored,
            test_raw_undeclared_tool_is_treated_as_changing, test_raw_call_is_in_the_trace, test_raw_batch_arguments_are_in_the_trace,
            test_raw_call_without_a_mark_is_not_made,
            test_lock_that_could_not_be_read_is_a_fault, test_trace_that_is_not_whole, test_game_that_ran_on, test_close_puts_back_also_after_an_error,
            test_close_waits_for_the_session_writer, test_session_of_another_is_lost_not_used, test_end_session_ends_a_dead_driver_only,
            test_attach_refuses_no_session, test_attach_refuses_driver_alive, test_attach_refuses_owner_hold, test_attach_refuses_unknown_game,
            test_attach_pauses_a_running_game, test_attach_then_run_is_refused, test_abort_writes_closing_record,
            test_names_not_built_say_so, test_tools_and_raw_census, test_lock_child_env_names_no_dropped_variable,
            test_load_answers_the_known_load_windows_only,
            test_accept_keeps_its_identity_when_the_judge_appends_the_scene_ledger]
    a = run(ticket)
    print("scene library: %d of %d checks passed" % (a, len(ticket)))
    b = run(more)
    print("other promises of the pages: %d of %d passed" % (b, len(more)))
    return 0 if a == len(ticket) == 22 and b == len(more) else 1


if __name__ == "__main__":
    sys.exit(main())
