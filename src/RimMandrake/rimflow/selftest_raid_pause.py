#!/usr/bin/env python3
"""selftest_raid_pause: the promises of design/specs/2026-11-23-raid-tests-paused/boundary.md, one test per promise, each
named as the promise is; then planted faults, each of which must turn a test red. No game, no network; temp files only."""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TMP = tempfile.mkdtemp(prefix="raid_pause_")
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(TMP, "ev.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = os.path.join(TMP, "sess.jsonl")
for k in ("RM_RAID_FOR", "RM_ROLE_UNIT"):
    os.environ.pop(k, None)
for p in (os.path.join(REPO, "src", "RimMandrake", "Utils", "testq"), os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"),
          os.path.join(REPO, "src", "RimMandrake", "Utils"), HERE):
    sys.path.insert(0, p)
import selftest_live_kinds as K  # noqa: E402  its temp roots, rows, table and stubbed change relation
import raid_pause as RP  # noqa: E402
import rimbridge_client as RC  # noqa: E402

M, MOD = K.M, K.MOD
REAL_SWITCH = RP.SWITCH
RAIDS = [("jawa/fire_raid", {"dryRun": False}), ("jawa/raid_shape_fire", {"dryRun": "false"}),
         ("jawa/fire_incident", {"incidentDef": "RaidEnemy"}), ("jawa/storyteller_fire", {"incidentDef": "RaidEnemy", "dryRun": False}),
         ("jawa/incident_schedule", {"incidentDef": "RaidEnemy"}), ("jawa/spawn_mech_cluster", {}),
         ("jawa/lord_assault_spawn", {"pawns": "Human1"}), ("jawa/lord_set_job", {"lordJob": "LordJob_Siege"}),
         ("rimworld/execute_debug_action", {"path": "Incidents\\Execute raid..."})]
OTHERS = [("jawa/fire_raid", {}), ("jawa/fire_raid", {"dryRun": True}), ("jawa/spawn_pawn", {"faction": "Pirate"}),
          ("jawa/fire_incident", {"incidentDef": "TraderCaravanArrival"}), ("jawa/fire_incident", {"incidentDef": "RaidEnemy", "dryRun": True}),
          ("jawa/lord_set_job", {"lordJob": "LordJob_DefendPoint"}), ("jawa/ordered_job", {"jobDef": "Goto"}), ("jawa/kill_hostiles", {})]


def switch(**kw):
    p = os.path.join(TMP, "switch_%d.json" % switch.n)
    switch.n += 1
    with open(p, "w", encoding="utf-8") as f:
        json.dump(dict({"paused": True, "why": "w", "allow": [], "chains": {}}, **kw), f)
    RP.SWITCH = p
    return p


switch.n = 0


class Sent(Exception):
    """The call passed the raid refusal and went on towards the game."""


def client(tool, params):
    """-> "refused" | "sent": what the production client does with one call, no byte leaving this process."""
    rb = RC.RimBridge.__new__(RC.RimBridge)
    rb.host, rb.port, rb.timeout, rb.connect_timeout, rb.client_name, rb._session_calls = "127.0.0.1", 1, 5, 5, "t", 0
    rb.check_params = lambda *a: None

    def stop(*a, **k):
        raise Sent()
    old, RC._driver_crossing, rb._request = RC._driver_crossing, stop, stop
    try:
        RC.RimBridge._call_one(rb, tool, params)
    except Sent:
        return "sent"
    except RC.RimBridgeError as e:
        return "refused" if RP.WORD in str(e) else "error %s" % e
    finally:
        RC._driver_crossing = old
    return "?"


def table(**c1):
    return K.table(**dict({"stages_raid": "a raid of 6 at the map edge"}, **c1))


def t_raid_call_refused():
    switch()
    assert all(client(t, p) == "refused" for t, p in RAIDS), [(t, client(t, p)) for t, p in RAIDS]
    switch(paused=False)
    assert all(client(t, p) == "sent" for t, p in RAIDS), [(t, client(t, p)) for t, p in RAIDS]


def t_other_calls_pass():
    switch()
    assert all(client(t, p) == "sent" for t, p in OTHERS), [(t, client(t, p)) for t, p in OTHERS]


def t_allowed_item_may_stage():
    switch(allow=["RIMMANDRAKE_BUILD_RAID_TOOL"])
    for item, want in (("RIMMANDRAKE_BUILD_RAID_TOOL", "sent"), ("RIMMANDRAKE_OTHER", "refused"), ("", "refused")):
        os.environ[RP.FOR_ENV] = item
        try:
            assert client("jawa/fire_raid", {"dryRun": False}) == want, (item, want)
        finally:
            os.environ.pop(RP.FOR_ENV, None)


def t_tagged_scene_does_not_start():
    switch()
    tt = table()
    ids = [t for t, _ in M.ingame_tests(tt)]
    assert "c1" not in ids and "c2" in ids, ids
    root = K.S.visit("rp_run%d" % switch.n, list(K.OTHERS), tt=tt)
    run, _ = M.ingame_to_run(root, MOD, 1, tt)
    assert "c1" not in run, run
    assert "c1" not in "".join(M.unrun_lines_of([{"check": "c1", "item": "I", "command": "x"}], tt)), "an UNRUN line of a paused scene"
    gone = {"tests": {"new": {"replaces": ["old"]}}}
    assert "old" not in "".join(M.unrun_lines_of([{"check": "old", "item": "I", "command": "x"}], gone)), "a replaced check"
    ex = M.read_ingame_exit(root, MOD, 1, tt)
    assert ex["state"] == "met", ex["why"]
    import control
    assert RP.WORD in control.to_run_text(MOD, root) if hasattr(K.S, "in_game_record") else "RP.said(" in open(
        os.path.join(HERE, "control.py"), encoding="utf-8").read()
    assert any(RP.WORD in w for w in M.paused_lines(root, MOD, 1, tt)), M.paused_lines(root, MOD, 1, tt)
    switch(paused=False)
    assert "c1" in [t for t, _ in M.ingame_tests(tt)]
    assert M.read_ingame_exit(root, MOD, 1, tt)["state"] == "not_met"


def t_paused_is_its_own_word():
    switch()
    for rows in ([], [K.o("SUCCESS", "FAIL")], [K.row("c1", "FAIL", **{"class": "MOD"})], [K.o("UNRESOLVED")],
                 [K.row("c1", "UNMEASURED", **{"class": "HARNESS"})]):
        tt = table()
        root = K.S.visit("rp_word%d" % switch.n, list(K.OTHERS) + rows, tt=tt)
        switch.n += 1
        ex = M.read_ingame_exit(root, MOD, 1, tt)
        p = ex["paused_raids"]["c1"]
        assert p["read"] == RP.WORD and p["open"], (rows, p)
        assert "c1" not in ex["lines"] and not ex["undecided_bars"] and not ex["shortfalls"] and ex["state"] == "met", (rows, ex)


def t_a_standing_pass_stands():
    switch()
    tt = table()

    def read(rows, state="untouched"):
        root = K.S.visit("rp_st%d" % switch.n, list(K.OTHERS) + rows, tt=tt)
        switch.n += 1
        old = M.BM.RR.relate
        M.BM.RR.relate = (lambda *a, **k: 1 / 0) if state is None else (
            lambda r, m, tests, last, **k: {"rows": {t: {"state": state} for t in tests}})
        try:
            return RP.read_scenes(root, MOD, 1, tt)["c1"]
        finally:
            M.BM.RR.relate = old
    good = K.row("c1", "PASS")
    x = read([good])
    assert x["read"] == RP.STANDS and not x["open"], x
    assert read([good], "touched")["open"] and read([good], None)["read"] == RP.WORD
    assert read([K.o("MOD FAILURE", "FAIL"), K.good()])["open"], "a MOD FAILURE on that build is not hidden by a later PASS"
    assert read([K.o("UNRESOLVED"), K.good()])["open"]


def t_open_raid_bar_holds_the_pass():
    switch()
    tt = table()
    root = K.S.visit("rp_pass%d" % switch.n, list(K.OTHERS), tt=tt)
    bars = RP.open_bars(RP.read_scenes(root, MOD, 1, tt))
    assert bars and all(v == ["c1"] for v in bars.values()), bars
    for on in (True, False):
        switch(paused=on)
        ok, why = M.raid_bars_decided(root, MOD, 1, tt, None)
        assert not ok and all(b in why for b in bars), (on, why)
        assert not M.raid_bars_decided(root, MOD, 1, tt, "go on")[0]
        assert M.raid_bars_decided(root, MOD, 1, tt, "defer " + ", ".join(bars))[0]
    assert M.raid_bars_decided(root, MOD, 1, K.table(), None)[0]


def t_walk_brief_names_it():
    switch()
    tt = table()
    root = K.S.visit("rp_wb%d" % switch.n, list(K.OTHERS), tt=tt)
    bars = sorted(RP.open_bars(RP.read_scenes(root, MOD, 1, tt)))
    text = "# b\nwritten_by: u1\n" + "".join("## %s\nx\n" % h for h in M.WALK_BRIEF_HEADINGS)
    why = M.walk_brief_raid_why(root, MOD, 1, tt, text)
    assert why and all(b in " ".join(why) for b in bars), why
    assert not M.walk_brief_raid_why(root, MOD, 1, tt, text + "open: %s\n" % ", ".join(bars))
    src = open(os.path.join(HERE, "maturation.py"), encoding="utf-8").read()
    body = src[src.index("def read_walk_brief("):]
    assert "walk_brief_raid_why(" in body[:body.index("\ndef ", 5)], "read_walk_brief does not ask"
    assert "clause(\"raid_bars_decided\"" in src, "the pass does not ask"


def t_chain_is_not_run():
    import suite as SU
    switch(chains={"Visibility": {"c_raid": "a raid"}})
    assert RP.chain_paused("Visibility", "c_raid") and not RP.chain_paused("Visibility", "c_other")
    t = SU.TestContext(types.SimpleNamespace(call=lambda *a, **k: None), anchor=(0, 0))
    with contextlib.suppress(Exception):
        with t.component("raid row"):
            raise RC.RaidPausedError(RP.WORD + ". Refused: jawa/fire_raid: a raid")
    c = t.components[-1]
    assert c.verdict == SU.NOT_RUN and RP.WORD in (c.detail or ""), (c.verdict, c.detail)
    assert SU.RAID_PAUSED == RP.WORD, SU.RAID_PAUSED
    import runner as RU
    assert RU.chain_paused("Visibility", "c_raid") and RU.raid_component("a raid").verdict == SU.NOT_RUN
    src = open(os.path.join(REPO, "src/RimMandrake/Utils/modcheck/runner.py"), encoding="utf-8").read()
    assert "chain_paused(" in src and "raid_component(" in src
    import pipeline_admit as PA
    r = PA.refusal("Visibility", {"chains": ["c_raid"]}, "BENCH")
    assert r and RP.WORD in r["text"], r
    assert PA.refusal("Visibility", {"chains": ["c_raid", "c_other"]}, "BENCH") is None
    assert PA.refusal("Visibility", {}, "BENCH") is None and PA.refusal("Pyrelands", {"chains": ["c_raid"]}, "BENCH") is None
    switch(paused=False, chains={"Visibility": {"c_raid": "a raid"}})
    assert PA.refusal("Visibility", {"chains": ["c_raid"]}, "BENCH") is None


def t_switch_unreadable_is_paused():
    for body in (None, "{", "[]", '{"paused": "no"}'):
        p = os.path.join(TMP, "bad_%d.json" % switch.n)
        switch.n += 1
        if body is not None:
            with open(p, "w") as f:
                f.write(body)
        RP.SWITCH = p
        s = RP.switch()
        assert s["paused"] and s["unreadable"] and p in s["unreadable"], (body, s)
        assert client("jawa/fire_raid", {"dryRun": False}) == "refused"
    assert json.load(open(REAL_SWITCH))["paused"] in (True, False)


def t_one_command_lifts():
    calls = []
    run = lambda argv, **k: calls.append(argv) or types.SimpleNamespace(returncode=run.rc, stdout="PUBLISHED abc", stderr="")  # noqa: E731
    run.rc = 0

    def cli(*argv, **env):
        with contextlib.redirect_stdout(io.StringIO()):
            return RP.main(list(argv), runner=run, env=env, path=RP.SWITCH)
    switch(chains={"X": {"c": "r"}})
    assert cli("lift", "--why", "the scene library holds a raid still") == 0 and not RP.paused()
    assert calls and "publish" in calls[-1][0] and json.load(open(RP.SWITCH))["chains"] == {"X": {"c": "r"}}
    assert cli("pause", "--why", "again") == 0 and RP.paused()
    assert cli("allow", "ITEM_A", "--why", "w") == 0 and RP.switch()["allow"] == ["ITEM_A"]
    assert cli("disallow", "ITEM_A", "--why", "w") == 0 and RP.switch()["allow"] == []
    assert cli("lift", "--why", "x", RM_ROLE_UNIT="u") == 2 and RP.paused()
    assert cli("lift", "--why", " ") == 2 and RP.paused()
    run.rc = 1
    assert cli("lift", "--why", "x") == 4


def t_briefs_carry_the_rule():
    assert RP.RULE in M.HOW_A_BAR_HOLDS and "cheaper_why" in M.LIVE_KINDS_RULE and "PAUSED" in M.LK.STEWARD_RULE
    for f in ("src/RimMandrake/rimflow/roles/designer_scene_contract.md", "src/RimMandrake/rimflow/roles/fable_rescue.md",
              ".claude/agents/rm-testpilot.md", ".claude/agents/rm-bridge.md", "infrastructure/agents/CHARTER.md", "CLAUDE.md",
              "design/RimMandrake/debug_process.md"):
        assert "cheapest test that decides" in " ".join(open(os.path.join(REPO, f), encoding="utf-8").read().split()), f


def t_census_lists_every_call():
    root = os.path.join(TMP, "cen")
    shutil.rmtree(root, ignore_errors=True)
    vd = os.path.join(root, "design", "concepts", "Mx", "version")
    os.makedirs(os.path.join(vd, "in_game", "visit_2"))
    os.makedirs(os.path.join(root, "src", "a"))
    tt = {"tests": {"s": {"kind": "live_minimal", "stage": "6", "stages_raid": "a raid"}}, "bars": [{"id": "b", "decides": ["s"]}]}
    json.dump(tt, open(os.path.join(vd, "test_table.json"), "w"))
    open(os.path.join(vd, "in_game", "visit_2", "rows.jsonl"), "w").write(json.dumps({"test": "s", "verdict": "PASS"}) + "\n")
    open(os.path.join(root, "src", "a", "live.py"), "w").write("x\nB.call('jawa/fire_raid', dryRun=False)\n")
    open(os.path.join(root, "src", "a", "calm.py"), "w").write("B.call('jawa/spawn_pawn')\n")
    tagged, scripts, unread = RP.census(root)
    assert tagged == [("Mx", "s", "a raid", ["b"], "PASS (visit 2)")] and list(scripts.values()) == [[2]] and not unread, (tagged, scripts)
    open(os.path.join(vd, "test_table.json"), "w").write("{")
    assert RP.census(root)[2]


def run_all(tests):
    red = []
    for t in tests:
        keep = dict(RP.__dict__)
        try:
            t()
        except Exception as e:  # noqa: BLE001
            red.append((t.__name__, "%s: %s" % (type(e).__name__, e)))
        RP.SWITCH = keep["SWITCH"]
    return red


PLANTS = [      # (what, module attribute, the broken stand-in): each must turn a test red
    ("a raid call is never seen", "raid_call", lambda tool, params=None: None),
    ("the switch never reads paused", "switch", lambda path=None: {"paused": False, "why": "", "allow": [], "chains": {}, "unreadable": None}),
    ("the tag is not read", "stages", lambda spec: None),
    ("a paused scene opens no bar", "open_bars", lambda readings: {}),
    ("no chain is paused", "chain_paused", lambda mod, chain, path=None: None)]


def missed_plants(tests):
    missed = []
    for what, name, bad in PLANTS:
        old = getattr(RP, name)
        setattr(RP, name, bad)
        got = run_all(tests)
        setattr(RP, name, old)
        print("plant %-34s %s" % (what, "red: " + ", ".join(x for x, _ in got) if got else "NOT SEEN"))
        if not got:
            missed.append(what)
    return missed


def main():
    tests = [t_raid_call_refused,
             t_other_calls_pass,
             t_allowed_item_may_stage,
             t_tagged_scene_does_not_start,
             t_paused_is_its_own_word,
             t_a_standing_pass_stands,
             t_open_raid_bar_holds_the_pass,
             t_walk_brief_names_it,
             t_chain_is_not_run,
             t_switch_unreadable_is_paused,
             t_one_command_lifts,
             t_briefs_carry_the_rule,
             t_census_lists_every_call]
    red = run_all(tests)
    for n, why in red:
        print("FAIL %s: %s" % (n, why[:400]))
    missed = []
    if not red:
        missed = missed_plants(tests)
    RP.SWITCH = REAL_SWITCH
    shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_raid_pause: %d of %d tests pass%s" % (len(tests) - len(red), len(tests), "" if not missed else
                                                        "; planted faults not seen: %s" % ", ".join(missed)))
    return 1 if red or missed else 0


if __name__ == "__main__":
    sys.exit(main())
