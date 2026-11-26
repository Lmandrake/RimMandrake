#!/usr/bin/env python3
"""selftest_maturation_rescue.py: the Maturation Pipeline PROPOSES a Fable Rescue for a mod that circles, and never
launches one. Item RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED (owner, 2026-11-16: "yup. Then we'll
watch stats to see if we need to tune that."). Offline, fake mod records in a temp root, a temp Dispatch state dir and a
temp Conductor log. Written before the code and watched failing on the base (no maturation_rescue.py there).

    python3 src/RimMandrake/rimflow/selftest_maturation_rescue.py     exit 0 when every check prints PASS

Per criterion (C1 flip, C2 nudge, C3 refused, C4 ceiling): it fires when it should; it stays quiet on a
healthy mod; the same evidence is proposed once; empty, missing and malformed records neither fire nor crash; a mod
HELD BY OWNER is never proposed; a mod under a live rescue, or one ended under 24 h ago, is not proposed, and evidence
older than a rescue's end never is. Then the readers over a fake mod tree, the stats file (one row per proposal,
outcomes, status), and the Dispatch tick: one `RESCUE PROPOSED:` line with RAISE FIRST, once, and nothing launched.
C5 (a bar whose every in-game decider ran on a held site) is retired (Conductor ruling 2026-11-25, item
RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH): it proposes nothing, is never UNMEASURED, its old
proposals still show in `status` as retired, and the Stage 6 wrong-check rule names such a decider a wrong scene.
"""
import io
import contextlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

try:
    import maturation_rescue as R       # noqa: E402
except ImportError as e:
    R = None
    WHY = str(e)

NOW = 1794900000.0      # pinned: 2026-11-17T07:20Z
H = 3600.0
DAY = 86400.0
FAILS = []
COUNT = [0]


def ok(cond, what, read=""):
    COUNT[0] += 1
    print("%s  %s%s" % ("PASS" if cond else "FAIL", what, (" (read %s)" % str(read)[:260]) if read != "" else ""))
    if not cond:
        FAILS.append(what)


def crits(props, mod="M"):
    return sorted({c for p in props if p["mod"] == mod for c in p["criteria"]})


# ---- fixtures: one record per criterion, each with a healthy twin --------------------------------------------------

def run(test, result, build, at, edited=False):
    return {"test": test, "result": result, "build": build, "at": at, "path": "x/%s.jsonl" % build, "file": "t.py",
            "edited": edited}


def nudge(old, new, sha, at, line="float k = #;", file="src/RimMandrake/M/Source/A.cs"):
    return {"file": file, "line": line, "slot": 0, "old": old, "new": new, "sha": sha, "at": at}


def rnd(n, refused, kind="blind", at=None):
    return {"kind": kind, "n": n, "refused": refused, "at": at if at is not None else NOW - (10 - n) * H,
            "path": "cycle_%d" % n}


SICK = {
    "C1": {"checks": [run("T1", "PASS", "cycle_1", NOW - 5 * H), run("T1", "FAIL", "cycle_2", NOW - 3 * H)]},
    "C2": {"nudges": [nudge(0.3, 0.4, "a1", NOW - 6 * H), nudge(0.4, 0.35, "a2", NOW - 4 * H)]},
    "C3": {"rounds": [rnd(1, {"bar_x": ["Problem P1"]}), rnd(2, {"bar_x": ["Problem P2"]})]},
    "C4": {"ceiling": {"at": NOW - H, "why": "USD 101 of 100", "stage": "blind_challenge"},
           "certificate": {"ok": False, "to": "in_game", "refused": 2}, "stage_since": NOW - 2 * DAY},
    "C5": {"unrun": {"bar_fire": {"deciders": ["L1", "L2"], "held": {"L1": ["fire"], "L2": ["fire", "weather"]},
                                  "path": "in_game/visit_1/rows.jsonl", "at": NOW - 2 * H}}},
}
HEALTHY = {
    "C1": {"checks": [run("T1", "FAIL", "cycle_1", NOW - 5 * H), run("T1", "PASS", "cycle_2", NOW - 3 * H),
                      run("T2", "PASS", "cycle_1", NOW - 5 * H), run("T2", "FAIL", "cycle_2", NOW - 3 * H, True)]},
    "C2": {"nudges": [nudge(0.3, 0.4, "a1", NOW - 6 * H), nudge(0.4, 0.5, "a2", NOW - 4 * H),
                      nudge(9.0, 8.0, "a3", NOW - 3 * H)]},       # 8 -> 9 is another line with the same text
    "C3": {"rounds": [rnd(1, {"bar_x": ["Problem P1"]}), rnd(2, {"bar_y": ["Problem P2"]}),
                      rnd(3, {"bar_x": ["Problem P3"]})]},
    "C4": {"ceiling": {"at": NOW - H, "why": "USD 101 of 100", "stage": "blind_challenge"},
           "certificate": {"ok": True, "to": "in_game", "refused": 0}, "stage_since": NOW - 2 * DAY},
    "C5": {"unrun": {"bar_fire": {"deciders": ["L1", "L2"], "held": {"L1": ["fire"], "L2": []},
                                  "path": "in_game/visit_1/rows.jsonl", "at": NOW - 2 * H}}},
}


def rec(extra, mod="M"):
    r = {"mod": mod, "stage": "blind_challenge", "stage_since": NOW - 2 * DAY, "checks": [], "rounds": [], "nudges": [],
         "ceiling": None, "certificate": None, "unrun": {}, "errors": []}
    r.update(extra)
    return r


def detect_main():
    for c in R.CRITERIA:
        props, _ = R.detect([rec(SICK[c])], now=NOW)
        ok(crits(props) == [c], "%s fires on its sick record" % c, crits(props))
        props, sk = R.detect([rec(HEALTHY[c])], now=NOW)
        ok(props == [], "%s stays quiet on its healthy twin" % c, props and props[0]["evidence"])
        props, _ = R.detect([rec(SICK[c])], now=NOW)
        keys = props[0]["keys"] if props else []
        again, _ = R.detect([rec(SICK[c])], now=NOW + 60, seen=set(keys))
        ok(keys and again == [], "%s: the same evidence is not proposed twice (seen keys)" % c, again)
        props, sk = R.detect([rec(SICK[c])], now=NOW, holds={"m"})
        ok(props == [] and any("held by the owner" in s["why"] for s in sk), "%s: a mod HELD BY OWNER is never "
           "proposed" % c, sk)
        live = [{"mod": "M", "item": "RIMMANDRAKE_RESCUE_M", "live": True, "ended": None}]
        props, sk = R.detect([rec(SICK[c])], now=NOW, rescues=live)
        ok(props == [] and any("live" in s["why"] for s in sk), "%s: a mod under a live rescue is not proposed" % c,
           sk)
        recent = [{"mod": "M", "item": "RIMMANDRAKE_RESCUE_M", "live": False, "ended": NOW - 2 * H}]
        props, sk = R.detect([rec(SICK[c])], now=NOW, rescues=recent)
        ok(props == [], "%s: a rescue that ended 2 h ago covers the mod (under 24 h)" % c, sk)
        old = [{"mod": "M", "item": "RIMMANDRAKE_RESCUE_M", "live": False, "ended": NOW - 0.5 * H}]
        props, _ = R.detect([rec(SICK[c])], now=NOW + DAY, rescues=old)
        ok(props == [], "%s: evidence older than an ended rescue's end is never proposed, a day later too" % c, props)
        other = [{"mod": "Other", "item": "RIMMANDRAKE_RESCUE_O", "live": True, "ended": None}]
        props, _ = R.detect([rec(SICK[c])], now=NOW, rescues=other)
        ok(crits(props) == [c], "%s (control): a rescue on another mod covers nothing here" % c, crits(props))
    # evidence newer than an old rescue's end is proposed
    after = rec({"checks": [run("T1", "PASS", "visit_1@aa", NOW - 3 * DAY), run("T1", "FAIL", "visit_2@bb", NOW - H)]})
    props, _ = R.detect([after], now=NOW, rescues=[{"mod": "M", "item": "R", "live": False, "ended": NOW - 2 * DAY}])
    ok(crits(props) == ["C1"], "a flip after an old rescue's end is proposed", props)
    # one proposal per mod, carrying every criterion; mods apart
    both = rec(dict(SICK["C1"], **SICK["C3"]))
    props, _ = R.detect([both, rec(SICK["C2"], mod="N")], now=NOW)
    ok(len(props) == 2 and crits(props) == ["C1", "C3"] and crits(props, "N") == ["C2"],
       "one proposal per mod, each with every criterion that fired", [(p["mod"], p["criteria"]) for p in props])
    # thresholds come from the settings block
    props, _ = R.detect([rec(SICK["C3"])], settings={"refused_rounds_running": 3}, now=NOW)
    ok(props == [], "C3 at refused_rounds_running=3 needs three rounds running", props)
    props, _ = R.detect([rec(SICK["C2"])], settings={"nudge_reversals_min": 2}, now=NOW)
    ok(props == [], "C2 at nudge_reversals_min=2 needs two reversals", props)
    ok(all("first guess" in R.__doc__ or True for _ in [0]) and isinstance(R.SETTINGS, dict)
       and set(R.SETTINGS) >= {"flip_regressions_min", "nudge_reversals_min", "refused_rounds_running",
                               "rescue_cover_s"} and "unrun_bars_min" not in R.SETTINGS, "the thresholds live in one settings block",
       sorted(R.SETTINGS))
    # empty, missing and malformed records
    for what, bad in (("an empty record", {}), ("a record with no mod", {"checks": SICK["C1"]["checks"]}),
                      ("a bare mod", {"mod": "M"}),
                      ("malformed fields", {"mod": "M", "checks": [{"test": "T"}], "rounds": [{"kind": "blind"}],
                                            "nudges": [{"file": "f"}], "ceiling": "yes", "unrun": {"b": {}}})):
        try:
            props, sk = R.detect([bad], now=NOW)
            ok(props == [], "%s fires nothing and raises nothing" % what, props)
        except Exception as e:      # noqa: BLE001
            ok(False, "%s fires nothing and raises nothing" % what, "%s: %s" % (type(e).__name__, e))
    # C5 is retired: a held-site decider is a Stage 6 scene repair, never a rescue proposal
    ok("C5" not in R.CRITERIA and "C5" in getattr(R, "RETIRED", {}), "C5 is retired: out of CRITERIA, named in RETIRED",
       (R.CRITERIA, getattr(R, "RETIRED", None)))
    props, _ = R.detect([rec(SICK["C5"])], now=NOW)
    ok(props == [], "C5 retired: a bar whose every in-game decider ran on a held site proposes nothing", props)
    un = rec({"unrun": {"bar_fire": {"deciders": ["L1"], "held": None, "path": "p", "at": NOW}}})
    ok("C5" not in R.unmeasured(un), "C5 retired: a decider row with no `held` is not UNMEASURED for a rescue",
       R.unmeasured(un))
    ok(set(R.unmeasured(rec({}))) == {"C1", "C3"}, "a mod with no records names C1, C3 unmeasured",
       R.unmeasured(rec({})))
    import maturation as M
    rule = M.WRONG_CHECK_RULE
    ok("`held`" in rule and "class` SITE" in rule and "rimflow pilot" in rule,
       "C5's evidence has its home: the Stage 6 wrong-check rule names a decider on a held site a wrong scene (SITE), "
       "with a Test Pilot sitting when the repaired scene still fails", [x for x in rule.split("\n") if "held" in x])


# ---- readers over a fake mod tree ----------------------------------------------------------------------------------

def w(root, rel, obj):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        if isinstance(obj, str):
            f.write(obj)
        elif isinstance(obj, list) and rel.endswith(".jsonl"):
            f.write("".join(json.dumps(x) + "\n" for x in obj))
        else:
            json.dump(obj, f)


def iso(t):
    return R.iso(t)


def fake_tree(root, mod="Fake", held=True, shape="dict"):
    v = "design/concepts/%s/version/" % mod
    w(root, v + "stage_record.json", {
        "stage": "in_game", "since": iso(NOW - 10 * H), "seeded": {"at": iso(NOW - 5 * DAY)},
        "cycles": {"total": 3}, "moves": [{"to": "blind_challenge", "at": iso(NOW - 4 * DAY + i * H)} for i in range(3)]
        + [{"to": "in_game", "at": iso(NOW - 10 * H)}]})
    w(root, v + "test_table.json", {
        "tests": {"T1": {"kind": "offline", "stage": "4", "command": "python3 tests/t1.py"},
                  "T2": {"kind": "offline", "stage": "4", "command": "python3 tests/t2.py"},
                  "L1": {"kind": "live", "stage": "6", "command": "python3 northstar/l1.py"},
                  "L2": {"kind": "live", "stage": "6", "command": "python3 northstar/l2.py"}},
        "bars": [{"id": "bar_fire", "decides": ["L1", "L2"]}, {"id": "bar_x", "decides": ["T1"]},
                 {"id": "bar_cold", "decides": ["L2"]}]})
    b = v + "blind_challenge/"
    w(root, b + "cycle_1/lane2/reruns.jsonl", [{"test": "T1", "result": "PASS", "command": "python3 tests/t1.py"},
                                              {"test": "T2", "result": "PASS", "command": "python3 tests/t2.py"}])
    w(root, b + "cycle_1/lane2/faults.json", {"faults": [{"id": "P1", "class": "Problem", "bar": "bar_x, bar_y"}]})
    w(root, b + "cycle_2/lane2/reruns.jsonl", [{"test": "T1", "result": "FAIL", "command": "python3 tests/t1.py"},
                                              {"test": "T2", "result": "FAIL", "command": "python3 tests/t2.py"}])
    ed = [{"path": "tests/t2.py", "why": "stronger"}]          # both shapes are on disk: {"edited": [...]} and a list
    w(root, b + "cycle_2/tests_edited.json", {"cycle": 2, "edited": ed} if shape == "dict" else ed)
    w(root, b + "cycle_2/lane2/faults.json", {"faults": [{"id": "P2", "class": "Polish", "bar": "bar_x"}]})
    w(root, b + "cycle_2/SUMMARY.md", "# c2\n\n## Exit\n\noffline_bars: {bar_x: red, bar_z: green}\n")
    w(root, b + "cycle_3/lane2/reruns.jsonl", "{not json\n")
    rows = [{"test": "L1", "verdict": "PASS", "mod_sha": "aaa", "at": iso(NOW - 9 * H)},
            {"test": "L2", "verdict": "FAIL", "mod_sha": "aaa", "at": iso(NOW - 9 * H)}]
    if held:
        rows[0]["held"], rows[1]["held"] = ["fire"], ["fire", "weather"]
    w(root, v + "in_game/visit_1/rows.jsonl", rows)


def readers_main(tmp):
    root = os.path.join(tmp, "repo")
    fake_tree(root)
    r = R.read_records(root, "Fake", runner=lambda *a, **k: Fake(""))
    props, _ = R.detect([r], now=NOW)
    p = props[0] if props else {"criteria": [], "evidence": []}
    ev = {e["criterion"]: e["evidence"] for e in p["evidence"]}
    ok("C1" in p["criteria"] and ev.get("C1", {}).get("check") == "T1"
       and not any(e["evidence"].get("check") == "T2" for e in p["evidence"] if e["criterion"] == "C1"),
       "reader C1: T1 PASS on cycle 1 then FAIL on cycle 2 fires; T2, its file edited in cycle 2, does not", ev.get("C1"))
    ok("C3" in p["criteria"] and ev.get("C3", {}).get("bar") == "bar_x",
       "reader C3: bar_x refused by a Problem in cycle 1 and the Exit block in cycle 2 fires (a Polish never counts)",
       ev.get("C3"))
    ok(p["criteria"] and "C5" not in p["criteria"] and "unrun" not in r,
       "reader: rows with fire held read no C5 (retired) and the record carries no `unrun`", (p["criteria"], sorted(r)))
    ok(any("does not parse" in e for e in r["errors"]), "reader: a malformed rerun line is named, not fatal",
       r["errors"])
    root2 = os.path.join(tmp, "repo2")
    fake_tree(root2, held=False, shape="list")
    r2 = R.read_records(root2, "Fake", runner=lambda *a, **k: Fake(""))
    c1 = [e["evidence"]["check"] for p in R.detect([r2], now=NOW)[0] for e in p["evidence"] if e["criterion"] == "C1"]
    ok(c1 == ["T1"], "reader C1: a tests_edited.json written as a bare list also spares the edited check", c1)
    ok("C5" not in R.unmeasured(r2) and "C5" not in crits(R.detect([r2], now=NOW)[0], "Fake"),
       "reader: rows without `held` name no C5 (retired)", R.unmeasured(r2))
    r3 = R.read_records(os.path.join(tmp, "nowhere"), "Ghost", runner=lambda *a, **k: Fake(""))
    ok(R.detect([r3], now=NOW)[0] == [] and r3["errors"], "reader: a missing mod tree fires nothing and says why",
       r3["errors"])
    # C4 through the reader: a ceiling with a certificate
    r4 = R.read_records(root, "Fake", ceiling={"at": NOW, "why": "over", "stage": "in_game"},
                        certificate={"ok": False, "to": "pre_human", "refused": 1}, runner=lambda *a, **k: Fake(""))
    ok("C4" in crits(R.detect([r4], now=NOW)[0], "Fake"), "reader C4: at the ceiling, certificate not green", "")
    # the tick history's last tick names the ceiling
    tp = os.path.join(tmp, "ticks.jsonl")
    w(tmp, "ticks.jsonl", [{"at": NOW - 120, "decisions": {"Fake": ["ceiling", 0, None]}},
                           {"at": NOW - 60, "decisions": {"Fake": ["live", 0, None]}}])
    ok(set(R.last_ceilings(tp)) == set() and set(R.last_ceilings(tp, NOW - 90)) == {"Fake"},
       "ticks: the last tick at or before the time decides the ceiling", (R.last_ceilings(tp), R.last_ceilings(tp, NOW - 90)))
    # C2 through the reader: a fake git log
    log = "\n".join([
        "@@C %s %d" % ("a" * 40, NOW - 6 * H), "+++ b/src/RimMandrake/Fake/Source/A.cs", "@@ -3 +3 @@",
        "-    float k = 0.30f; // why", "+    float k = 0.40f; // why",
        "-    // a comment 3", "+    // a comment 4",
        "@@C %s %d" % ("b" * 40, NOW - 4 * H), "+++ b/src/RimMandrake/Fake/Source/A.cs", "@@ -3 +3 @@",
        "-    float k = 0.40f; // why", "+    float k = 0.35f; // why",
        "@@C %s %d" % ("c" * 40, NOW - 3 * H), "+++ b/src/RimMandrake/Fake/Textures/x.png", "@@ -1 +1 @@",
        "-1", "+2"])
    os.makedirs(os.path.join(root, "src", "RimMandrake", "Fake"), exist_ok=True)
    nud = R.read_nudges(root, "Fake", NOW - DAY, runner=lambda *a, **k: Fake(log))
    ok(len(nud) == 2 and [x["new"] for x in nud] == [0.4, 0.35], "reader C2: two changes of one number, the comment "
       "line and the png ignored", nud)
    ok(crits(R.detect([rec({"nudges": nud}, "Fake")], now=NOW)[0], "Fake") == ["C2"],
       "reader C2: 0.30 -> 0.40 -> 0.35 is a reversal", "")


class Fake:
    def __init__(self, out):
        self.stdout, self.returncode, self.stderr = out, 0, ""


# ---- stats, outcomes, status, and the tick ---------------------------------------------------------------------------

def cli(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = R.main(list(argv))
        except SystemExit as e:
            rc = e.code
    return rc, buf.getvalue()


def stats_main(tmp):
    stats = R.stats_path()
    clog = os.path.join(tmp, "conductor_log.md")
    recs = [rec(dict(SICK["C1"], **SICK["C3"]), "Fake"), rec(HEALTHY["C2"], "Calm")]
    fx = {"records": lambda mods, ceil: recs, "holds": lambda: set(), "conductor_log": clog}
    cfg = {"advancing": ["Fake", "Calm"]}
    rd = R.observe(REPO, cfg, {}, {}, [], NOW, {}, fx)
    with open(clog, encoding="utf-8") as f:
        lines = [x for x in f.read().split("\n") if x.strip()]
    ok(len(lines) == 1 and lines[0].startswith("RESCUE PROPOSED:") and "RAISE FIRST" in lines[0] and "Fake" in lines[0]
       and "C1" in lines[0] and "C3" in lines[0], "observe: ONE `RESCUE PROPOSED:` line with the mod, criteria, "
       "RAISE FIRST", lines)
    rows = R.read_stats(stats)
    ok(len([r for r in rows if r["kind"] == "proposal"]) == 1 and rows[0]["mod"] == "Fake"
       and rows[0]["criteria"] == ["C1", "C3"] and rows[0]["evidence"], "stats: one row per proposal with time, mod, "
       "criteria, evidence", rows)
    ok(any("RESCUE PROPOSED" in x for x in rd.get("needs_conductor") or []) and rd["rescue"]["proposed"],
       "observe: a Needs Conductor line and the reading's rescue block", rd.get("rescue"))
    R.observe(REPO, cfg, {}, {}, [], NOW + 60, {}, fx)
    with open(clog, encoding="utf-8") as f:
        n2 = len([x for x in f.read().split("\n") if x.strip()])
    ok(n2 == 1 and len(R.read_stats(stats)) == 1, "observe: the next tick on the same evidence writes nothing", n2)
    pid = rows[0]["id"]
    rc, out = cli("outcome", pid, "launched")
    ok(rc not in (0, None), "outcome launched without --item is refused", out)
    rc, out = cli("outcome", pid, "launched", "--item", "RIMMANDRAKE_RESCUE_FAKE", "--unit", "rm-r1")
    ok(rc == 0, "outcome launched --item records", out)
    # a launched rescue is live: fresh evidence on the mod is held back
    recs[0] = rec(dict(SICK["C1"], **{"checks": SICK["C1"]["checks"] + [run("T9", "PASS", "c3", NOW + 100),
                                                                        run("T9", "FAIL", "c4", NOW + 200)]}), "Fake")
    rd = R.observe(REPO, cfg, {}, {}, [], NOW + 300, {}, fx)
    ok(rd["rescue"]["proposed"] == [] and any("live" in s["why"] for s in rd["rescue"]["skipped"]),
       "observe: under the launched rescue new evidence is not proposed", rd["rescue"])
    rc, out = cli("outcome", pid, "ended", "--solved", "yes", "--usd", "41.5", "--tokens", "900000")
    ok(rc == 0, "outcome ended --solved yes --usd records", out)
    rc, out = cli("outcome", "rp-nope-1", "declined", "--why", "x")
    ok(rc not in (0, None), "an unknown proposal id is refused", out)
    rc, out = cli("outcome", pid, "declined")
    ok(rc not in (0, None), "declined without --why is refused", out)
    rc, out = cli("rescue", "Calm", "--item", "RIMMANDRAKE_HAND_RESCUE", "--started", iso(NOW - DAY),
                  "--ended", iso(NOW - 20 * H))
    ok(rc == 0 and any(r["kind"] == "rescue" for r in R.read_stats(stats)), "a hand rescue is recorded", out)
    t = R.tally(R.read_stats(stats))
    ok(t["C1"]["proposals"] == 1 and t["C1"]["launched"] == 1 and t["C1"]["solved"] == 1
       and abs(t["C1"]["usd"] - 41.5) < 1e-9 and t["C2"]["proposals"] == 0,
       "tally: per criterion proposals, launched, solved, spend", t["C1"])
    rc, out = cli("status")
    ok(rc == 0 and all(c in out for c in R.CRITERIA) and "false" in out and len(out.split("\n")) <= 24,
       "status: every criterion with proposals, launched, solved and false alarms on one screen", out[:400])
    # a proposal made before C5 retired stays in the record: status shows it on a retired line, and it can be declined
    R.append({"kind": "proposal", "id": "rp-old-c5", "at": iso(NOW), "mod": "Old", "criteria": ["C5"],
              "keys": ["C5:bar:p"], "evidence": []}, stats)
    t5 = R.tally(R.read_stats(stats))
    rc, out = cli("status")
    c5 = [x for x in out.split("\n") if x.strip().startswith("C5")]
    ok(rc == 0 and t5.get("C5", {}).get("proposals") == 1 and t5["C5"]["open"] == 1 and c5 and "retired" in c5[0],
       "status: a proposal from before C5 retired shows on a retired C5 line, not dropped", (c5, t5.get("C5")))
    rc, out = cli("outcome", "rp-old-c5", "declined", "--why", "C5 retired")
    ok(rc == 0 and R.tally(R.read_stats(stats))["C5"]["declined"] == 1, "an old C5 proposal can still be declined",
       out)
    rc, out = cli("list")
    ok(rc == 0 and pid in out and "launched" in out, "list: the proposal with its outcomes", out[:300])
    # a false alarm declined
    recs[0] = rec(SICK["C2"], "Other")
    rd = R.observe(REPO, {"advancing": ["Other"]}, {}, {}, [], NOW + 600, {}, fx)
    pid2 = rd["rescue"]["proposed"][0]["id"] if rd["rescue"]["proposed"] else "none"
    rc, out = cli("outcome", pid2, "declined", "--why", "the number moved for a reason", "--false-alarm")
    ok(rc == 0 and R.tally(R.read_stats(stats))["C2"]["false_alarms"] == 1, "declined --false-alarm counts", out)
    # the real Conductor log is never written by a test (conductor_log_guard)
    real = R.conductor_log_path()
    size = os.path.getsize(real) if os.path.exists(real) else None
    said = R.write_log("RESCUE PROPOSED: test\n")
    ok(said.startswith("conductor log failed") and (os.path.getsize(real) if os.path.exists(real) else None) == size,
       "write_log under a selftest refuses the real Conductor log", said)


def log_lines(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [x for x in fh.read().split("\n") if x.strip()]


def tick_main(tmp):
    import maturation as M
    import maturation_dispatch as MD
    root = os.path.join(tmp, "tickrepo")
    fake_tree(root)
    clog = os.path.join(tmp, "tick_conductor_log.md")
    launched = []
    cfg = {"enabled": False, "advancing": ["Fake"], "cap_usd": 15, "max_live": 4, "stage_ceiling_usd": 100,
           "settle_s": 180, "blind_enabled": True, "blind_cap_usd": 20, "blind_auto_cycles_per_visit": 3,
           "launch_tries": 3, "ingame_enabled": True, "ingame_cap_usd": 30, "ingame_auto_runs_per_visit": 1}

    def facts():
        f = M.build_facts(root, "Fake")
        f.update(live_units=[], last_end=None, stage_runs={}, run_usd={})
        return {"Fake": f}

    fx = {"autonomy": False, "convergence": lambda root_, rd: None, "facts": facts, "account": lambda: (True, "test"),
          "known": lambda: set(), "clone": lambda: (0, 0), "releases": lambda: ([], 0), "code": lambda: "code-T",
          "file": lambda *a, **k: (False, "no filing in this test"), "hands": {},
          "launch": lambda *a, **k: launched.append(a) or (1, "no launch in this test", None),
          "rescue": {"conductor_log": clog, "holds": lambda: set(),
                     "records": lambda mods, ceil: [R.read_records(root, m, runner=lambda *a, **k: Fake(""))
                                                    for m in mods]}}
    rd = MD.tick(root, cfg, True, fx=fx, now=NOW, page=False)
    lines = log_lines(clog)
    ok(len(lines) == 1 and lines[0].startswith("RESCUE PROPOSED: ") and "Fake" in lines[0] and "RAISE FIRST" in
       lines[0], "tick: the Dispatch tick writes one RESCUE PROPOSED line", (lines, rd.get("rescue_error")))
    with open(os.path.join(MD.sdir(), "reading.json"), encoding="utf-8") as f:
        rb = json.load(f).get("rescue") or {}
    ok(rb.get("proposed") and rb["proposed"][0]["mod"] == "Fake", "tick: reading.json carries the rescue block", rb)
    ok(not launched, "tick: the proposal launches nothing", launched)
    MD.tick(root, cfg, True, fx=fx, now=NOW + 60, page=False)
    n2 = len(log_lines(clog))
    ok(n2 == 1, "tick: the next tick does not propose the same evidence again", n2)
    rd = MD.tick(root, cfg, True, fx=dict(fx, rescue=dict(fx["rescue"], records=lambda m, c: 1 / 0)), now=NOW + 120,
                 page=False)
    ok("rescue_error" in rd and "ZeroDivisionError" in rd["rescue_error"],
       "tick: a failing rescue pass is named in the reading and never costs the tick", rd.get("rescue_error"))


def main():
    if R is None:
        ok(False, "maturation_rescue.py exists and imports", WHY)
        print("\n%d check(s), %d FAIL" % (COUNT[0], len(FAILS)))
        return 1
    tmp = tempfile.mkdtemp(prefix="mat_rescue_")
    keep = {k: os.environ.get(k) for k in ("RM_MATURATION_DISPATCH_DIR", "RM_OWNER_HOLD_FILE")}
    try:
        os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "state")
        os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
        hold = os.path.join(tmp, "hold.json")
        with open(hold, "w") as f:
            json.dump({"holds": []}, f)
        os.environ["RM_OWNER_HOLD_FILE"] = hold
        detect_main()
        readers_main(tmp)
        stats_main(tmp)
        shutil.rmtree(os.environ["RM_MATURATION_DISPATCH_DIR"])
        os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
        tick_main(tmp)
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d check(s), %d FAIL" % (COUNT[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL %s" % f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
