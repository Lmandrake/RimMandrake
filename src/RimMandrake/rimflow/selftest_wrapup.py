#!/usr/bin/env python3
"""selftest_wrapup.py — AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED: the wrap-up that runs after every agent.

  W1  every launch path carries it: role_launch.launch_argv (Relentless + roles) and detached_helper.launch_argv put
      ExecStopPost=wrapup.py unit on the unit; a Relentless run is --carried, a role run is not
  W2  every window path carries it: .claude/settings.json runs wrapup_hook.py on SessionEnd and SubagentStop
  W3  clone census on a real git clone: clean+pushed ok; untracked, modified and unpushed are filed; carried when told
  W4  bridge: this agent's hold from its clone is released (cleaned); a failed release, a helper's or a /clear hold is
      filed, not released; OWNER, another holder or another clone is left alone
  W5  debts (forced settings, staged scenes): what the agent still owes is filed with its undo and leaves the register;
      paid() clears one; another agent's debt is untouched
  W6  claims (session): a claim still doing is filed; an unreadable ledger is UNMEASURED, never ok
  W7  filing: an open file per agent; standing() re-measures; sweep() resolves once the debris is gone
  W8  the hook builds the right context: nothing inside a launched unit; session clones + since from the transcript
  W9  ops_watch's wrapup family: standing count and record count MEASURED; no state dir UNMEASURED, never 0
  W10 the `unit` CLI end to end: exit 0 on any clone (it must never fail the unit) and one runs.jsonl line
  W11 a debt nobody's wrap-up names (a python.exe harness) stands once it is DEBT_AGE_S old
  W12 the producer: validation_v2's sset owes a forced setting, and restore_settings pays it once read back
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, ".claude", "hooks"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

TMP = tempfile.mkdtemp(prefix="selftest_wrapup_")
os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "state")
os.environ["RIMFLOW_SHARED_BRIDGE"] = ""            # the real lock is never read or written here

import wrapup  # noqa: E402
import role_launch  # noqa: E402
import detached_helper  # noqa: E402
import wrapup_hook  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def git(cwd, *a):
    return subprocess.run(["git", "-C", cwd] + list(a), capture_output=True, text=True, check=True).stdout


def make_clone(name):
    bare = os.path.join(TMP, name + ".git")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
    c = os.path.join(TMP, name)
    subprocess.run(["git", "clone", "-q", bare, c], check=True, capture_output=True)
    git(c, "config", "user.email", "t@example.invalid")
    git(c, "config", "user.name", "t")
    with open(os.path.join(c, "a.txt"), "w") as f:
        f.write("a\n")
    git(c, "add", "a.txt")
    git(c, "commit", "-q", "-m", "one")
    git(c, "push", "-q", "-u", "origin", "main")
    return c


class Fake(wrapup.World):
    def __init__(self, sh=None, release_ok=True, claims=(), claims_raise=False):
        self.sh, self.release_ok, self.claims, self.claims_raise = sh, release_ok, list(claims), claims_raise
        self.released = []

    def shared_bridge(self):
        return self.sh

    def release_bridge(self, clone, holder):
        self.released.append((clone, holder))
        if self.release_ok:
            self.sh = None
        return self.release_ok, "fake"

    def doing_claims(self, seat, since):
        if self.claims_raise:
            raise ValueError("torn ledger")
        return list(self.claims)


def ctx(kind="unit", clones=(), **kw):
    c = {"kind": kind, "key": "K-" + kind, "seat": "BENCH", "owner": "unit:K", "holder": "RELENTLESS",
         "clones": list(clones), "since": 0, "carried": False}
    c.update(kw)
    return c


def kinds(rows, kind):
    return [r for r in rows if r["kind"] == kind]


try:
    # W1 ---------------------------------------------------------------------------------------------------------
    role = {"name": "relentless", "seat": "BENCH", "clone": "/x/clone", "model": "opus", "run_max_s": 600}
    argv = role_launch.launch_argv(role, "rm-relentless-work-abc-g1", "m", "/o", "/e", "/usr/bin/claude")
    post = [argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "-p" and argv[i + 1].startswith("ExecStopPost=")]
    check(len(post) == 1 and "wrapup.py unit --unit rm-relentless-work-abc-g1 --seat BENCH --clone /x/clone --carried"
          in post[0] and argv.index("-p") < argv.index("--"), "W1 role_launch: ExecStopPost=wrapup unit, carried for relentless")
    check(post and post[0].startswith("ExecStopPost=-+/usr/bin/python3 ") and os.path.isfile(post[0].split()[1]),
          "W1 the ExecStopPost runs outside the sandbox, never fails the unit, and its tool exists")
    role2 = dict(role, name="Operations", seat="OPERATIONS")
    argv2 = role_launch.launch_argv(role2, "rm-role-ops-1", "m", "/o", "/e", "/usr/bin/claude")
    post2 = [a for a in argv2 if a.startswith("ExecStopPost=")]
    check(len(post2) == 1 and "--carried" not in post2[0] and "--seat OPERATIONS" in post2[0],
          "W1 a role run's wrap-up is not carried")
    rec = {"clone": "/y/c", "unit": "rm-detached-1", "seat": "BENCH", "max_s": 60, "budget_usd": 1, "model": "opus",
           "out": "/o", "err": "/e", "state": "/s", "item": "I", "tmp": None}
    argv3 = detached_helper.launch_argv(rec, "m", "/usr/bin/claude")
    post3 = [a for a in argv3 if a.startswith("ExecStopPost=")]
    check(len(post3) == 2 and any("wrapup.py unit --unit rm-detached-1 --seat BENCH --clone /y/c" in a for a in post3),
          "W1 detached_helper: finish and the wrap-up both run at stop")
    check(any(a.startswith("ExecStopPost=-+/usr/bin/python3 ") and "wrapup.py" in a for a in post3),
          "W1 detached_helper's wrap-up runs outside the sandbox and never fails the unit")

    # W2 ---------------------------------------------------------------------------------------------------------
    st = json.load(open(os.path.join(REPO, ".claude", "settings.json")))
    for ev in ("SessionEnd", "SubagentStop"):
        cmds = [h.get("command", "") for blk in st["hooks"].get(ev, []) for h in blk.get("hooks", [])]
        check(any("wrapup_hook.py" in c for c in cmds), "W2 settings.json runs wrapup_hook.py on %s" % ev)

    # W3 ---------------------------------------------------------------------------------------------------------
    c = make_clone("w3")
    w = wrapup.World()
    check(wrapup.check_clone(w, c, False)["act"] == "ok", "W3 clean and pushed clone is ok")
    with open(os.path.join(c, "new.txt"), "w") as f:
        f.write("x")
    r = wrapup.check_clone(w, c, False)
    check(r["act"] == "filed" and "new.txt" in r["why"], "W3 an untracked file is filed: %s" % r["why"])
    check(wrapup.check_clone(w, c, True)["act"] == "carried", "W3 a carried clone is carried, not filed")
    os.remove(os.path.join(c, "new.txt"))
    with open(os.path.join(c, "a.txt"), "a") as f:
        f.write("b\n")
    git(c, "commit", "-q", "-am", "two")
    r = wrapup.check_clone(w, c, False)
    check(r["act"] == "filed" and "1 unpushed" in r["why"], "W3 an unpushed commit is filed: %s" % r["why"])
    check(wrapup.check_clone(w, os.path.join(TMP, "nope"), False)["act"] == "ok", "W3 a removed clone is ok")
    unborn = os.path.join(TMP, "unborn")
    subprocess.run(["git", "init", "-q", "-b", "main", unborn], check=True)
    check(wrapup.check_clone(w, unborn, False)["act"] == "filed", "W3 a clone whose push state cannot be read is filed")

    # W4 ---------------------------------------------------------------------------------------------------------
    mine = {"holder": "RELENTLESS", "clone": "/k/c", "purpose": "a proof"}
    f = Fake(sh=dict(mine))
    r = wrapup.check_bridge(f, ctx(clones=["/k/c"]))
    check(r["act"] == "cleaned" and f.released == [("/k/c", "RELENTLESS")], "W4 this unit's hold is released")
    f = Fake(sh=dict(mine), release_ok=False)
    check(wrapup.check_bridge(f, ctx(clones=["/k/c"]))["act"] == "filed", "W4 a failed release is filed")
    for name, sh, cx in (("OWNER", dict(mine, holder="OWNER"), ctx(clones=["/k/c"], holder="OWNER")),
                         ("another holder", dict(mine, holder="BENCH"), ctx(clones=["/k/c"])),
                         ("another clone", dict(mine, clone="/books"), ctx(clones=["/k/c"]))):
        f = Fake(sh=sh)
        check(wrapup.check_bridge(f, cx)["act"] == "ok" and not f.released, "W4 %s's hold is left alone" % name)
    for name, cx in (("helper", ctx("subagent", clones=["/k/c"])), ("/clear", ctx("session", clones=["/k/c"], report_only=True))):
        f = Fake(sh=dict(mine))
        check(wrapup.check_bridge(f, cx)["act"] == "filed" and not f.released, "W4 a %s's hold is filed, not released" % name)

    # W5 ---------------------------------------------------------------------------------------------------------
    t1 = wrapup.owe("setting", "FlowWorks clamp OFF", undo="sset clamp true", owner="unit:K")
    t2 = wrapup.owe("scene", "staged review pens", owner="unit:K")
    t3 = wrapup.owe("setting", "someone else's", owner="unit:OTHER")
    check(wrapup.paid(t2) and not wrapup.paid(t2), "W5 paid() clears a debt once")
    rec = wrapup.run(Fake(), ctx(clones=[]))
    d = kinds(rec["rows"], "debt")
    check(len(d) == 1 and "clamp" in d[0]["what"] and "sset clamp true" in d[0]["why"], "W5 the owed setting is filed with its undo")
    check([x["token"] for x in wrapup.debts_of("unit:K")] == [] and [x["token"] for x in wrapup.debts_of("unit:OTHER")] == [t3],
          "W5 the filed debt left the register; another agent's stays")
    check(t1 is not None and os.path.isfile(os.path.join(os.environ["RM_WRAPUP_DIR"], "open", "unit-K-unit.json")),
          "W5 an open file is written for the agent")

    # W6 ---------------------------------------------------------------------------------------------------------
    rows = wrapup.census(Fake(claims=[("ITEM_A", "2026-11-04T00:00:00Z")]), ctx("session"))
    check([r["act"] for r in kinds(rows, "claims")] == ["filed"], "W6 a claim still doing is filed")
    rows = wrapup.census(Fake(claims_raise=True), ctx("session"))
    check([r["act"] for r in kinds(rows, "claims")] == ["unmeasured"], "W6 an unreadable ledger is unmeasured")
    rows = wrapup.census(Fake(), ctx("session", since=None))
    check([r["act"] for r in kinds(rows, "claims")] == ["unmeasured"], "W6 an unknown session start is unmeasured")
    check(not kinds(wrapup.census(Fake(claims=[("X", "t")]), ctx("unit")), "claims"), "W6 a unit's claims are the supervisor's")

    # W7 ---------------------------------------------------------------------------------------------------------
    c7 = make_clone("w7")
    with open(os.path.join(c7, "left.txt"), "w") as f:
        f.write("x")
    rec = wrapup.run(wrapup.World(), dict(ctx(clones=[c7]), key="w7", owner="unit:w7"))
    check(rec["filed"] == 1, "W7 the dirty clone is filed (%d)" % rec["filed"])
    standing = {os.path.basename(p): rows for p, _, rows in wrapup.standing()}
    check(len(standing.get("unit-w7.json", [])) == 1, "W7 standing() re-measures it as standing")
    os.remove(os.path.join(c7, "left.txt"))
    standing = {os.path.basename(p): rows for p, _, rows in wrapup.standing()}
    check(standing.get("unit-w7.json") == [], "W7 a cleaned clone stops standing")
    cleared, left = wrapup.sweep()
    check(cleared == 1 and left == 1 and os.path.isfile(os.path.join(os.environ["RM_WRAPUP_DIR"], "resolved", "unit-w7.json")),
          "W7 sweep resolves the cleared file and keeps the debt one (%d, %d)" % (cleared, left))
    check(wrapup.main(["resolve", "unit-K-unit", "--why", "selftest"]) == 0 and not wrapup.standing(),
          "W7 resolve closes the rest")

    # W8 ---------------------------------------------------------------------------------------------------------
    check(wrapup_hook.build_ctx({"hook_event_name": "SessionEnd"}, env={"RM_ROLE_UNIT": "u"}) is None,
          "W8 inside a launched unit the hook does nothing")
    tr = os.path.join(TMP, "t.jsonl")
    with open(tr, "w") as f:
        f.write(json.dumps({"timestamp": "2026-11-04T01:02:03.000Z", "cwd": c}) + "\n")
        f.write(json.dumps({"timestamp": "2026-11-04T02:00:00.000Z", "cwd": os.path.join(c7)}) + "\n")
    cx = wrapup_hook.build_ctx({"hook_event_name": "SessionEnd", "session_id": "S1", "cwd": c, "transcript_path": tr,
                                "reason": "logout"}, env={"AGENT_SEAT": "BENCH"})
    check(cx and cx["kind"] == "session" and cx["clones"] == [c, c7] and cx["since"] == 1793754123
          and cx["owner"] == "session:S1" and cx["holder"] == "BENCH" and not cx["report_only"],
          "W8 SessionEnd: clones and since from the transcript (%r)" % ((cx and (cx["clones"], cx["since"])),))
    cx = wrapup_hook.build_ctx({"hook_event_name": "SessionEnd", "session_id": "S1", "cwd": c, "transcript_path": tr,
                                "reason": "clear"}, env={"AGENT_SEAT": "BENCH"})
    check(cx["report_only"], "W8 /clear is report-only")
    cx = wrapup_hook.build_ctx({"hook_event_name": "SubagentStop", "session_id": "S1", "agent_id": "A9", "cwd": c,
                                "agent_transcript_path": tr}, env={"AGENT_SEAT": "BENCH"})
    check(cx["kind"] == "subagent" and cx["clones"] == [c7], "W8 SubagentStop: only the helper's other clones")
    check(wrapup_hook.build_ctx({"hook_event_name": "Stop"}, env={}) is None, "W8 a turn end is not an agent end")

    # W9 ---------------------------------------------------------------------------------------------------------
    import ops_watch
    with open(os.path.join(c7, "left.txt"), "w") as f:
        f.write("x")
    wrapup.run(wrapup.World(), dict(ctx(clones=[c7]), key="w9", owner="unit:w9"))
    o = ops_watch.c_wrapup(__import__("time").time(), {}, {})
    check(o["wrapup.debris_standing"]["m"] == "MEASURED" and o["wrapup.debris_standing"]["v"] == 1,
          "W9 standing debris MEASURED 1 (%r)" % o["wrapup.debris_standing"])
    check(o["wrapup.records_24h"]["m"] == "MEASURED" and o["wrapup.records_24h"]["v"] >= 3,
          "W9 the wrap-up records are counted (%r)" % o["wrapup.records_24h"].get("v"))
    rules = json.load(open(os.path.join(REPO, "src", "RimMandrake", "Utils", "ops_watch_rules.json")))
    check(any(t.get("key") == "wrapup.debris_standing" and t.get("alarm") and t.get("name") == "OPS_WRAPUP_DRAIN_DEBRIS_PILES_UP"
              for t in rules["targets"]), "W9 the standing count files one fixed alarm")
    check("wrapup" in ops_watch.FAMILIES and "wrapup" in ops_watch.ORDER, "W9 the family is gathered")
    saved = os.environ["RM_WRAPUP_DIR"]
    os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "absent")
    o = ops_watch.c_wrapup(0, {}, {})
    check(o["wrapup.debris_standing"]["m"] == "UNMEASURED", "W9 no state dir is UNMEASURED, never 0")
    os.environ["RM_WRAPUP_DIR"] = saved

    # W10 --------------------------------------------------------------------------------------------------------
    before = sum(1 for _ in open(os.path.join(saved, "runs.jsonl")))
    p = subprocess.run([sys.executable, os.path.join(HERE, "wrapup.py"), "unit", "--unit", "rm-x", "--seat", "BENCH",
                        "--clone", os.path.join(TMP, "never-was")], capture_output=True, text=True,
                       env=dict(os.environ, RM_WRAPUP_DIR=saved, RIMFLOW_SHARED_BRIDGE=""))
    after = sum(1 for _ in open(os.path.join(saved, "runs.jsonl")))
    check(p.returncode == 0 and after == before + 1, "W10 the unit CLI exits 0 and records one line (%s)" % p.stdout.strip())

    # W11 --------------------------------------------------------------------------------------------------------
    import time as _t
    t11 = wrapup.owe("setting", "a harness's clamp", owner="pid:1")
    now = _t.time()
    check(not any(r.get("token") == t11 for _, _, rs in wrapup.standing(now=now) for r in rs),
          "W11 a fresh orphan debt does not stand yet")
    aged = [r for _, _, rs in wrapup.standing(now=now + wrapup.DEBT_AGE_S + 60) for r in rs if r.get("token") == t11]
    check(len(aged) == 1 and "pid:1" in aged[0]["why"], "W11 an aged orphan debt stands")
    wrapup.paid(t11)
    wrapup.paid(t3)

    # W12 --------------------------------------------------------------------------------------------------------
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar"))
    import validation_v2 as V

    class B12(object):
        def __init__(self):
            self.v = {}

        def call(self, tool, typeName=None, action=None, field=None, value=None):
            if action == "set":
                self.v[field] = value
                return {"success": True}
            return {"success": True, "value": self.v.get(field)}

    typ = sorted(V._SETTINGS)[0]
    fld = sorted(V._SETTINGS[typ])[0]
    L = V.Live(B12())
    dflt = V._SETTINGS[typ][fld]
    other = (not dflt) if isinstance(dflt, bool) else (dflt + 1 if isinstance(dflt, (int, float)) else str(dflt) + "x")
    L.sset(typ, fld, other)
    L.sset(typ, fld, other)
    owed = [d for d in wrapup.debts_of(wrapup.owner_key()) if fld in d.get("what", "")]
    check(len(owed) == 1, "W12 sset owes the forced setting once (%d)" % len(owed))
    bad = L.restore_settings()
    owed = [d for d in wrapup.debts_of(wrapup.owner_key()) if fld in d.get("what", "")]
    check(bad == [] and owed == [], "W12 restore_settings pays it (bad=%r, owed=%d)" % (bad, len(owed)))

    # W13-W15: every live stager owes before it changes the game and pays only after its undo reads back. A stager
    # killed before its teardown (simulated: entered, never exited) leaves the debt, and the wrap-up files it.
    os.environ["RM_ROLE_UNIT"] = "stager-w13"

    def end_agent():
        """The agent ends: the unit wrap-up's census -> its debt rows."""
        return kinds(wrapup.run(Fake(), ctx(owner=wrapup.owner_key(), key="stager"))["rows"], "debt")

    # W13 scenes/scenelib: Scene and setting()
    from scenes import scenelib as SL

    class B13(object):
        def __init__(self):
            self.things, self.settings, self.fail_set = [], {"f": "1"}, False

        def __call__(self, tool, **q):
            if tool == "jawa/mod_settings_field":
                if q["action"] == "get":
                    return {"success": True, "value": self.settings.get(q["field"])}
                if self.fail_set:
                    return {"success": False}
                self.settings[q["field"]] = q["value"]
                return {"success": True}
            if tool == "jawa/clear_area":
                self.things = []
                return {"success": True}
            if tool == "jawa/list_things":
                return {"success": True, "things": list(self.things)}
            return {"success": True}

    b13 = B13()
    SL.call = b13
    with SL.Scene("w13_clean", x=5, z=5, w=3, h=3):
        b13.things = [{"id": "Thing_1", "kind": "Building"}]
    check(end_agent() == [], "W13 a Scene torn down (read back empty) owes nothing")
    sc = SL.Scene("w13_killed", x=5, z=5, w=3, h=3).__enter__()
    b13.things = [{"id": "Thing_2", "kind": "Building"}]          # staged, then the agent dies: no __exit__
    d = end_agent()
    check(len(d) == 1 and "w13_killed" in d[0]["what"] and "clear_area rect=5,5,3,3" in d[0]["why"],
          "W13 a Scene left without teardown is filed with its undo: %r" % [x["what"] for x in d])
    sc2 = SL.Scene("w13_left", x=1, z=1, w=1, h=1).__enter__()
    b13.things = [{"id": "Thing_4"}]
    real_clear = SL.Scene.clear
    SL.Scene.clear = lambda self: {"success": True}                 # success:true, but the rect is not empty
    sc2.teardown()
    SL.Scene.clear = real_clear
    d = end_agent()
    check(len(d) == 1 and "w13_left" in d[0]["what"], "W13 success:true with things still standing stays owed")
    cm = SL.setting("RimMandrake.X", f="0")
    cm.__enter__()                                                  # forced, then killed before the finally
    check(b13.settings["f"] == "0", "W13 setting() forced the field")
    d = end_agent()
    check(len(d) == 1 and "RimMandrake.X f=0" in d[0]["what"] and "f=1" in d[0]["why"],
          "W13 a forced setting never restored is filed with its old value: %r" % [x["what"] for x in d])
    b13.settings["f"] = "1"                                         # what the killed run left, put back by hand
    with SL.setting("RimMandrake.X", f="0"):
        pass
    check(end_agent() == [] and b13.settings["f"] == "1", "W13 a setting() restored owes nothing")
    try:
        with SL.setting("RimMandrake.X", f="0"):
            b13.fail_set = True                                     # the restore call fails
    finally:
        b13.fail_set = False
    check(len(end_agent()) == 1, "W13 a setting() whose restore failed stays owed")
    del sc

    # W14 stage_review: a stage that dies half-way is owed; a finished one is the deliverable and owes nothing
    import stage_review as SR
    SR.connect = lambda: object()
    SR.ensure_map = lambda rb, m: {"mapId": m}
    SR.pause = lambda rb: True
    SR.clear = lambda rb, kinds_, rect: {"cleared": 0}

    def die(*a, **k):
        raise RuntimeError("bridge dropped mid-spawn")
    SR.spawn_roster = die
    argv = sys.argv
    sys.argv = ["stage_review.py", "--map", "7", "--clear", "chunks", "--spawn", "Gizka:2"]
    try:
        SR.main()
        check(False, "W14 the crash propagated")
    except RuntimeError:
        pass
    d = end_agent()
    check(len(d) == 1 and "stage_review map 7" in d[0]["what"] and "spawn Gizka:2" in d[0]["what"],
          "W14 a stage that crashed half-way is filed: %r" % [x["what"] for x in d])
    SR.spawn_roster = lambda rb, roster, at, spread, terr, layout: [("Gizka", 1, 1, True)]
    rc = SR.main()
    check(rc == 0 and end_agent() == [], "W14 a stage that finished owes nothing (rc=%r)" % rc)
    sys.argv = ["stage_review.py", "--map", "7", "--frame", "1,1,2,2"]
    check(SR.stage_debt(SR.argparse.Namespace(kill_hostiles=False, clear="", spawn="", face=None, daylight=False,
                                              weather=None, two_pass=None, map=7)) is None,
          "W14 a reframe-and-shoot run changes nothing and owes nothing")
    sys.argv = argv

    # W15 modcheck/helpers.SettingsTransaction (site_calm and every quiet_world profile)
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))
    import helpers as HL

    class S15(object):
        def __init__(self):
            self.debug, self.diff = {"godMode": False}, {"threatScale": 1.0, "allowBigThreats": True}

        def call(self, tool, **q):
            if tool == "jawa/debug_settings":
                if q.get("action") == "set":
                    self.debug[q["field"]] = q["value"]
                    return {"success": True}
                return {"success": True, "fields": [{"name": k, "value": v} for k, v in self.debug.items()]}
            if tool == "jawa/difficulty_tune":
                before = dict(self.diff)
                for k, v in q.items():
                    self.diff[k] = v
                return {"success": True, "before": before, "after": dict(self.diff)}
            return {"success": True}

    s15 = S15()
    tx = HL.SettingsTransaction(s15).__enter__()
    check(end_agent() == [], "W15 an entered transaction that changed nothing owes nothing")
    tx.set_debug("godMode", True)
    tx.set_difficulty(threatScale=0.0)
    d = end_agent()                                                  # killed before restore()
    check(len(d) == 1 and "godMode=True" in d[0]["what"], "W15 a transaction killed before restore is filed: %r"
          % [x["what"] for x in d])
    s15 = S15()                                                      # a fresh game: the killed run's values gone
    with HL.SettingsTransaction(s15) as tx2:
        tx2.set_debug("godMode", True)
        tx2.set_difficulty(threatScale=0.0)
    check(end_agent() == [] and s15.debug["godMode"] is False and s15.diff["threatScale"] == 1.0,
          "W15 a transaction restored owes nothing")
    tx3 = HL.SettingsTransaction(s15).__enter__()
    tx3.on_restore("wild spawner", lambda: False)                  # a cleanup that is not undone
    try:
        tx3.restore()
    except HL.HelperUnverified:
        pass
    check(len(end_agent()) == 1, "W15 a restore with problems stays owed")
    os.environ.pop("RM_ROLE_UNIT", None)
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print("selftest_wrapup: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
