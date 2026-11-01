#!/usr/bin/env python3
"""Selftest for the RW1 time ledger (WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT), L0, offline, by planted faults on the
real path (the CLI the mission page's file comes from, then mission_page.time_view reading that file).

S1  a fixture transcript of a known split (133 min: selftest 39, live 20, build 12, reading 11, editing 5, waiting 35,
    model 11, a 30 min idle gap, two parallel calls) must read within 5% per category; then each planted fault (a blind
    classifier, lost tool results, no idle gap) must take it out of 5%, so the check can fail.
S2  the frozen hand-labelled real runs (time_ledger_replay/) must report the missed waste and wrongful stops pinned by
    the labels; a planted lax threshold must turn into wrongful stops, a run labelled both ways or with no transcript
    must read UNMEASURED, never clean.
S3  accounting edges: parent/subagent overlap charged once, gaps between transcripts kept as waiting, gen windows
    (a transcript crossing a restart is split, none goes to a later gen), --days clips, duplicate records, a shared
    transcript folder; and the waste verdict's boundaries plus a replay truth table under the default rules, with
    planted "never flag" / "always flag" faults that must read as missed waste and wrongful stops.
The fixture trees are hashed around each read: the ledger writes its output file and nothing else.
"""
import atexit
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
BASE = Path(tempfile.mkdtemp(prefix="st_time_ledger_"))
atexit.register(shutil.rmtree, BASE, True)
MOD, ITEM = "Fixtmod", "FIXTMOD_TIME_SPLIT_1"
CLONE = "/fixture/relentless/clones/" + ITEM
ENV = {"RELENTLESS_ROOT": str(BASE / "rel"), "RM_TIME_PROJECTS": str(BASE / "projects"),
       "RM_TIME_LEDGER": str(BASE / "out" / "time_ledger.json"), "RM_MISSION_ROOT": str(BASE / "root"),
       "RM_MISSION_LEDGER": str(BASE / "ledger.jsonl"), "RM_PULSE_STATE": str(BASE / "pulse")}
os.environ.update(ENV)
sys.path.insert(0, str(HERE))
import time_ledger as tl   # noqa: E402

FAILS = []
EXPECT = {"selftest": 39, "live": 20, "build": 12, "reading": 11, "editing": 5, "waiting": 35, "model": 11, "other": 0}


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(t))


def tree(p: Path) -> dict:
    return {str(f.relative_to(p)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob("*")) if f.is_file()}


def build_fixture(t0: float) -> None:
    m = lambda x: t0 + x * 60   # noqa: E731 - minutes into the run
    recs, n = [{"type": "user", "timestamp": iso(m(0)), "message": {"role": "user", "content": "do the item"}}], [0]

    def call(start, end, name, inp, result=True):
        n[0] += 1
        tid = "toolu_%d" % n[0]
        recs.append({"type": "assistant", "timestamp": iso(m(start)), "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": tid, "name": name, "input": inp}]}})
        if result:
            recs.append({"type": "user", "timestamp": iso(m(end)), "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tid, "content": "x"}]}})
    call(1, 7, "Read", {"file_path": "/x/a.py"})
    call(8, 38, "Bash", {"command": "python3 src/RimMandrake/Utils/run_selftests.py --only selftest_x > o.txt 2>&1"})
    call(39, 40, "Edit", {"file_path": "/x/a.py", "old_string": "a", "new_string": "b"})
    call(41, 45, "Write", {"file_path": "/x/b.py", "content": "c"})
    call(46, 58, "Bash", {"command": "python3 src/RimMandrake/Utils/winbuild.py"})
    call(59, 79, "Bash", {"command": "./bridge call jawa/status"})
    call(80, 85, "Bash", {"command": "sleep 300"})
    recs.append({"type": "user", "timestamp": iso(m(115)), "message": {"role": "user", "content": "back from a 30 min idle"}})
    call(116, 118, "Grep", {"pattern": "foo"})
    # two parallel calls: the result order differs from the call order
    for name, inp in (("Bash", {"command": "grep -n foo /x/a.py"}), ("Read", {"file_path": "/x/c.py"})):
        n[0] += 1
        recs.append({"type": "assistant", "timestamp": iso(m(119)), "message": {"content": [
            {"type": "tool_use", "id": "toolu_%d" % n[0], "name": name, "input": inp}]}})
    for k in (n[0], n[0] - 1):
        recs.append({"type": "user", "timestamp": iso(m(121)), "message": {"content": [{"type": "tool_result", "tool_use_id": "toolu_%d" % k}]}})
    n[0] += 1
    a, b = "toolu_%d" % n[0], "toolu_%d" % (n[0] + 1)
    n[0] += 1
    recs.append({"type": "assistant", "timestamp": iso(m(122)), "message": {"content": [
        {"type": "tool_use", "id": a, "name": "Bash", "input": {"command": "python3 src/x/selftest_y.py"}},
        {"type": "tool_use", "id": b, "name": "Read", "input": {"file_path": "/x/d.py"}}]}})
    recs.append({"type": "user", "timestamp": iso(m(124)), "message": {"content": [{"type": "tool_result", "tool_use_id": b}]}})
    recs.append({"type": "user", "timestamp": iso(m(132)), "message": {"content": [{"type": "tool_result", "tool_use_id": a}]}})
    recs.append({"type": "assistant", "timestamp": iso(m(133)), "message": {"content": [{"type": "text", "text": "done"}]},
                 "stop_reason": "end_turn"})
    pd = BASE / "projects" / tl.mangle(CLONE)
    pd.mkdir(parents=True)
    (pd / "sess-1.jsonl").write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    item = BASE / "rel" / "store" / "items" / ITEM
    item.mkdir(parents=True)
    (item / "state.json").write_text(json.dumps({"item": ITEM, "clone": CLONE}), encoding="utf-8")
    (item / "attempts.jsonl").write_text(json.dumps({"at": iso(t0 - 5), "gen": 1, "start": "unit-g1"}) + "\n", encoding="utf-8")
    about = BASE / "root" / "src" / "RimMandrake" / MOD / "About"
    about.mkdir(parents=True)
    (about / "About.xml").write_text("<ModMetaData><packageId>mandrake.x.fixtmod</packageId></ModMetaData>", encoding="utf-8")
    (BASE / "ledger.jsonl").write_text("", encoding="utf-8")
    (BASE / "pulse").mkdir()


def within(hours: dict) -> list:
    """Categories off the known split by more than 5% (of the category; `other` must stay under 5% of a minute)."""
    got = {k: hours.get(k, 0) * 60 for k in EXPECT}
    return [f"{k}: {got[k]:.2f} of {v}" for k, v in EXPECT.items() if abs(got[k] - v) > 0.05 * max(v, 1)]


def run_cli(*args, env=None):
    return subprocess.run([sys.executable, "-B", str(HERE / "time_ledger.py"), *args], capture_output=True, text=True,
                          timeout=300, env=dict(os.environ, **(env or {})))


def in_process_hours(patch) -> dict:
    """The CLI's own main(), with one piece of the real path broken by `patch`; the ledger read back from its file."""
    import agents_timeline as at
    import circling
    saved = (circling.classify, tl.tools_of, at.BUSY_GAP)
    at._SCAN.clear()
    try:
        patch(circling, tl, at)
        rc = tl.main(["write"])
    finally:
        circling.classify, tl.tools_of, at.BUSY_GAP = saved
        at._SCAN.clear()
    assert rc == 0
    return json.loads(Path(ENV["RM_TIME_LEDGER"]).read_text(encoding="utf-8"))["mods"][MOD]["hours"]


def t_s1():
    build_fixture(time.time() - 86400)
    before = {k: tree(BASE / k) for k in ("projects", "rel", "root")}
    p = run_cli("write")
    ok(p.returncode == 0 and "WROTE" in p.stdout, "S1 write exits clean: " + (p.stdout + p.stderr)[-200:].strip())
    d = json.loads(Path(ENV["RM_TIME_LEDGER"]).read_text(encoding="utf-8"))
    rec = d["mods"].get(MOD) or {}
    off = within(rec.get("hours", {}))
    ok(rec and not off, "S1 known split read within 5%%: %s" % (off or {k: round(v * 60, 2) for k, v in rec["hours"].items()}))
    ok(set(tl.CATEGORIES) <= set(rec.get("hours", {})) and isinstance(rec.get("at"), (int, float)),
       "S1 record has the mission page's shape {at, hours:{six}}")
    ok(list(d["runs"]) == [ITEM + "#g1"] and d["runs"][ITEM + "#g1"]["mods"] == [MOD], "S1 one run, charged to the mod")
    ok({k: tree(BASE / k) for k in before} == before, "S1 read-only: transcripts, store and repo untouched")
    import mission_page
    v = mission_page.time_view(MOD, time.time())
    ok(v.get("status") == "READ" and v["hours"]["selftest"] == round(39 / 60, 1), "S1 mission page reads it: %s" % v)

    def blind(c, t, a):
        real = c.classify
        c.classify = lambda name, inp: ("other", None) if "selftest" in str((inp or {}).get("command", "")) else real(name, inp)

    def no_results(c, t, a):
        real = t.tools_of
        t.tools_of = lambda path: [dict(x, t1=None) for x in real(path)]

    def no_gap(c, t, a):
        a.BUSY_GAP = 10 ** 6
    for name, patch in (("blind classifier", blind), ("tool results lost", no_results), ("idle gap not seen", no_gap)):
        off = within(in_process_hours(patch))
        ok(bool(off), "S1 planted fault '%s' leaves 5%%: %s" % (name, off))
    off = within(in_process_hours(lambda c, t, a: None))
    ok(not off, "S1 healthy again in process (the faults were the only change): %s" % off)


def t_s2():
    fx = tl.FIXTURE
    labels = json.loads((fx / "labels.json").read_text(encoding="utf-8"))
    before = tree(fx)
    p = run_cli("replay")
    v = json.loads(p.stdout) if p.returncode == 0 else {}
    waste = sorted(r["run"] for r in labels if r["label"] == "waste")
    missed = sorted(r["run"] for r in v.get("runs", []) if r["label"] == "waste" and not r["waste"])
    ok(v.get("measured") == len(labels) == 22 and not v.get("unmeasured") and not v.get("ledger_unmeasured"),
       "S2 every labelled real run measured: %s of %s" % (v.get("measured"), len(labels)))
    ok(v.get("missed") == 2 and missed == waste, "S2 reports missed waste: %s %s" % (v.get("missed"), missed))
    ok(v.get("wrongful") == 0 and v.get("wrongful_rate") == 0.0, "S2 reports wrongful stops: %s" % v.get("wrongful"))
    ok(v.get("may_stop") is False, "S2 missed waste keeps the flag from stopping runs")

    rules = json.loads(tl.RULES.read_text(encoding="utf-8"))
    rules["circling"].update(test_share_limit=0.3, test_share_min=8)
    lax = BASE / "lax_rules.json"
    lax.write_text(json.dumps(rules), encoding="utf-8")
    p = run_cli("replay", env={"RELENTLESS_RULES": str(lax)})
    w = json.loads(p.stdout) if p.returncode == 0 else {}
    flagged_fine = sorted(r["run"] for r in w.get("runs", []) if r["label"] == "fine" and r["waste"])
    ok(w.get("wrongful", 0) >= 3 and w["wrongful"] == len(flagged_fine)
       and "IDLE_SEAT_RESTART_BUILD_BRINGS_QUIET_BACK#g1" in flagged_fine and w.get("missed") == 0,
       "S2 planted lax threshold turns into wrongful stops: %s wrongful, %s missed" % (w.get("wrongful"), w.get("missed")))

    bad = labels + [dict(labels[0], label="fine" if labels[0]["label"] == "waste" else "waste"),
                    {"run": "NO_SUCH_ITEM#g1", "label": "fine"}]
    bf = BASE / "bad_labels.json"
    bf.write_text(json.dumps(bad), encoding="utf-8")
    p = run_cli("replay", "--labels", str(bf))
    b = json.loads(p.stdout) if p.returncode == 0 else {}
    ok(b.get("measured") == len(labels) - 1 and len(b.get("unmeasured", [])) == 2,
       "S2 planted bad labels read UNMEASURED, never clean: %s" % b.get("unmeasured"))
    ok(tree(fx) == before, "S2 read-only: the frozen fixture is untouched")


def mini(name: str, stores: dict, t0: float):
    """A one-off store + projects tree: {item: (clone, [start offsets s -> gen], {file: [(s, rec kind, *args)]})}.
    -> (relentless root, projects dir). Record kinds: use(id, name, input), res(id), text."""
    top = Path(tempfile.mkdtemp(prefix=name + "_", dir=BASE))
    root, proj = top / "rel", top / "projects"
    for item, (clone, starts, files) in stores.items():
        d = root / "store" / "items" / item
        d.mkdir(parents=True)
        (d / "state.json").write_text(json.dumps({"item": item, "clone": clone}), encoding="utf-8")
        (d / "attempts.jsonl").write_text("".join(json.dumps({"at": iso(t0 + s), "gen": g, "start": "u"}) + "\n"
                                                  for s, g in starts), encoding="utf-8")
        for fname, rows in files.items():
            recs = []
            for s, kind, *a in rows:
                c = ([{"type": "tool_use", "id": a[0], "name": a[1], "input": a[2]}] if kind == "use" else
                     [{"type": "tool_result", "tool_use_id": a[0]}] if kind == "res" else [{"type": "text", "text": "."}])
                recs.append({"type": "assistant" if kind != "res" else "user", "timestamp": iso(t0 + s),
                             "message": {"content": c}})
            p = proj / tl.mangle(clone) / fname
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return root, proj


def runs_of(name, stores, t0, since=0.0, until=float("inf")):
    root, proj = mini(name, stores, t0)
    os.environ["RM_TIME_PROJECTS"] = str(proj)
    try:
        return tl.collect_runs(since, root, until)
    finally:
        os.environ["RM_TIME_PROJECTS"] = ENV["RM_TIME_PROJECTS"]


def t_s3():
    """Accounting edges a per-file sum gets wrong (GPT review 2026-11-01): wall time is charged once per run."""
    t0 = time.time() - 86400
    ST, RD = {"command": "python3 src/x/selftest_z.py"}, {"file_path": "/x/a.py"}
    near = lambda a, b: abs(a - b) < 1.0   # noqa: E731 - iso stamps carry whole seconds
    r, _ = runs_of("overlap", {"OVL": ("/c/ovl", [(-5, 1)], {
        "s.jsonl": [(0, "use", "a", "Read", RD), (600, "res", "a")],
        "s/subagents/agent-1.jsonl": [(0, "use", "b", "Bash", ST), (600, "res", "b")]})}, t0)
    s = r.get("OVL#g1", {}).get("secs", {})
    ok(near(s.get("reading", 0), 300) and near(s.get("selftest", 0), 300) and near(sum(s.values()), 600),
       "S3 parent + subagent overlap charged once (300/300 of 600 s): %s" % {k: round(v) for k, v in s.items() if v})
    r, _ = runs_of("gap", {"GAP": ("/c/gap", [(-5, 1)], {
        "a.jsonl": [(0, "use", "a", "Read", RD), (60, "res", "a")],
        "b.jsonl": [(120, "use", "b", "Read", RD), (180, "res", "b")]})}, t0)
    s = r.get("GAP#g1", {}).get("secs", {})
    ok(near(sum(s.values()), 180) and near(s.get("waiting", 0), 60),
       "S3 gap between transcripts is waiting, not lost (180 s wall): %s" % {k: round(v) for k, v in s.items() if v})
    r, _ = runs_of("early", {"ERL": ("/c/erl", [(0, 1), (100, 2)], {
        "a.jsonl": [(5, "use", "a", "Read", RD), (80, "res", "a")]})}, t0)
    ok(sorted(r) == ["ERL#g1"], "S3 a transcript ending before g2's start row stays g1: %s" % sorted(r))
    r, _ = runs_of("span", {"SPN": ("/c/spn", [(0, 1), (600, 2)], {
        "a.jsonl": [(10, "use", "a", "Read", RD), (20, "res", "a"), (660, "use", "b", "Bash", ST), (900, "res", "b")]})}, t0)
    g1, g2 = (r.get("SPN#g%d" % g, {}).get("secs", {}) for g in (1, 2))
    ok(near(g2.get("selftest", 0), 240) and g1.get("selftest", 0) == 0 and near(sum(g1.values()), 590)
       and near(sum(g2.values()), 300),
       "S3 a transcript crossing a restart is split at it: g1 %s of 590 s, g2 %s of 300 s"
       % (round(sum(g1.values())), round(sum(g2.values()))))
    r, _ = runs_of("since", {"SNC": ("/c/snc", [(-5, 1)], {
        "a.jsonl": [(0, "use", "a", "Bash", ST), (7200, "res", "a")]})}, t0, since=t0 + 3600)
    s = r.get("SNC#g1", {}).get("secs", {})
    ok(near(s.get("selftest", 0), 3600), "S3 hours before --days are not charged: selftest %s of 3600 s" % round(s.get("selftest", 0)))
    r, _ = runs_of("since2", {"SN2": ("/c/sn2", [(-5, 1)], {
        "a.jsonl": [(0, "use", "a", "Read", RD), (60, "res", "a")],
        "b.jsonl": [(7200, "use", "b", "Read", RD), (7260, "res", "b")]})}, t0, since=t0 + 3600)
    s = r.get("SN2#g1", {}).get("secs", {})
    ok(near(s.get("waiting", 0), 3600) and near(sum(s.values()), 3660),
       "S3 a --days cutoff between transcripts keeps the waiting after it: %s" % {k: round(v) for k, v in s.items() if v})
    dup = [(0, "use", "u", "Bash", ST), (0, "use", "u", "Bash", ST), (60, "res", "u"), (300, "text")]
    r, _ = runs_of("dup", {"DUP": ("/c/dup", [(-5, 1)], {"a.jsonl": dup})}, t0)
    s = r.get("DUP#g1", {}).get("secs", {})
    ok(near(s.get("selftest", 0), 60) and near(s.get("model", 0), 240),
       "S3 a repeated tool_use record is one 60 s call: %s" % {k: round(v) for k, v in s.items() if v})
    one = tl.charge(next((BASE).glob("dup_*/projects/*/a.jsonl")))["secs"]
    ok(near(one["selftest"], 60) and near(one["model"], 240), "S3 charge() alone dedupes too: %s" % round(one["selftest"]))
    r, _ = runs_of("par", {"PAR": ("/c/par", [(-5, 1)], {"a.jsonl": [
        (0, "use", "a", "Bash", ST), (0, "use", "b", "Bash", ST), (0, "use", "c", "Read", RD),
        (600, "res", "a"), (600, "res", "b"), (600, "res", "c")]})}, t0)
    s = r.get("PAR#g1", {}).get("secs", {})
    ok(near(s.get("selftest", 0), 400) and near(s.get("reading", 0), 200),
       "S3 two identical parallel calls stay two (400/200 s): %s" % {k: round(v) for k, v in s.items() if v})
    copy = [(0, "use", "a", "Bash", ST), (300, "res", "a"), (300, "use", "b", "Read", RD), (600, "res", "b")]
    sub = [(0, "use", "s", "Read", {"file_path": "/x/sub.py"}), (300, "res", "s")]   # a subagent's own read beside it
    r, _ = runs_of("copy", {"CPY": ("/c/cpy", [(-5, 1)], {"a.jsonl": copy[:2], "b.jsonl": copy,
                                                         "a/subagents/agent-1.jsonl": sub})}, t0)
    s = r.get("CPY#g1", {}).get("secs", {})
    ok(near(s.get("selftest", 0), 150) and near(s.get("reading", 0), 450),
       "S3 a resumed session's copied history counts once (150/450 s): %s" % {k: round(v) for k, v in s.items() if v})
    r, _ = runs_of("xfile", {"XFL": ("/c/xfl", [(-5, 1)], {
        "s.jsonl": [(0, "use", "a", "Bash", ST), (0, "use", "c", "Read", RD), (600, "res", "a"), (600, "res", "c")],
        "s/subagents/agent-1.jsonl": [(0, "use", "b", "Bash", ST), (600, "res", "b")]})}, t0)
    s = r.get("XFL#g1", {}).get("secs", {})
    ok(near(s.get("selftest", 0), 400) and near(s.get("reading", 0), 200),
       "S3 identical calls in parent and subagent stay two (400/200 s): %s" % {k: round(v) for k, v in s.items() if v})
    r, _ = runs_of("opn", {"OPN": ("/c/opn", [(-5, 1)], {"a.jsonl": [
        (0, "use", "a", "Bash", ST), (0, "use", "b", "Bash", ST), (60, "res", "a"), (300, "text")]})}, t0)
    s = r.get("OPN#g1", {}).get("secs", {})
    ok(near(s.get("selftest", 0), 300) and near(s.get("model", 0), 0),
       "S3 a distinct unfinished call beside a finished twin still runs (300 s): %s" % {k: round(v) for k, v in s.items() if v})
    r, _ = runs_of("until", {"UNT": ("/c/unt", [(-5, 1)], {"a.jsonl": [(0, "use", "a", "Bash", ST), (120, "res", "a")]})},
                   t0, until=t0 + 60)
    s = r.get("UNT#g1", {})
    ok(near(s.get("secs", {}).get("selftest", 0), 60) and near(s.get("last", 0), t0 + 60),
       "S3 nothing after `now` is charged: selftest %s of 60 s" % round(s.get("secs", {}).get("selftest", 0)))
    r, _ = runs_of("twice", {"TWC": ("/c/twc", [(0, 1), (200, 1)], {
        "a.jsonl": [(10, "use", "a", "Read", RD), (60, "res", "a")],
        "b.jsonl": [(250, "use", "b", "Read", RD), (300, "res", "b")]})}, t0)
    s = r.get("TWC#g1", {}).get("secs", {})
    ok(near(s.get("reading", 0), 100) and near(s.get("waiting", 0), 190) and near(sum(s.values()), 290),
       "S3 a gen started twice keeps the gap between its starts (100/190 s): %s" % {k: round(v) for k, v in s.items() if v})
    r, _ = runs_of("back", {"BAK": ("/c/bak", [(0, 1), (100, 2), (200, 1)], {
        "a.jsonl": [(10, "use", "a", "Read", RD), (300, "res", "a")]})}, t0, until=t0 + 300)
    g1, g2 = (sum(r.get("BAK#g%d" % g, {}).get("secs", {}).values()) for g in (1, 2))
    ok(near(g1, 190) and near(g2, 100), "S3 a gen resumed after another owns only its own windows: g1 %s of 190, g2 %s of 100"
       % (round(g1), round(g2)))
    tie = Path(tempfile.mkdtemp(prefix="tie_", dir=BASE))
    (tie / "attempts.jsonl").write_text("".join(json.dumps({"at": iso(t0), "gen": g, "start": "u"}) + "\n" for g in (2, 1)),
                                        encoding="utf-8")
    ok([g for _, g in tl.starts_of(tie)] == [2, 1], "S3 tied start rows keep file order: %s" % tl.starts_of(tie))
    ok(tl.hours_of({"reading": 1.0})["reading"] > 0, "S3 a one-second slice survives export rounding")
    froot, fproj = mini("frz", {"FRZ": ("/c/frz", [(-5, 1)], {"a.jsonl": [(0, "use", "a", "Read", RD), (60, "res", "a")]})}, t0)
    with open(froot / "store" / "items" / "FRZ" / "attempts.jsonl", "ab") as f:   # a start row with no gen, then a
        f.write(b'{"at": "%s", "start": "u"}\n{"note":"\xe2\x82' % iso(t0 + 10).encode())   # tail torn mid-UTF-8
    before = {q: q.read_bytes() for q in froot.rglob("*") if q.is_file()}
    fx = Path(tempfile.mkdtemp(prefix="frzout_", dir=BASE))
    old = {k: os.environ.get(k) for k in ("RELENTLESS_ROOT", "RM_TIME_PROJECTS")}
    os.environ.update(RELENTLESS_ROOT=str(froot), RM_TIME_PROJECTS=str(fproj))
    try:
        n = tl.freeze([{"run": "FRZ#g1", "label": "fine"}], fx, 0)
        try:
            tl.freeze([{"run": str(froot / "store" / "items" / "FRZ") + "#g1", "label": "fine"}],
                      Path(tempfile.mkdtemp(prefix="frzout_", dir=BASE)), 0)
            refused = False
        except ValueError:
            refused = True
    finally:
        for k, v in old.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    after = {q: q.read_bytes() for q in froot.rglob("*") if q.is_file()}
    ok(n == 1 and refused and before == after,
       "S3 freeze copies past a torn row, refuses a path as an item id, leaves the live store untouched: %s %s %s"
       % (n, refused, before == after))
    r, _ = runs_of("atstart", {"ATS": ("/c/ats", [(0, 1), (100, 2)], {
        "a.jsonl": [(100, "text")], "b.jsonl": [(200, "use", "r", "Read", RD), (300, "res", "r")]})}, t0, until=t0 + 400)
    s = r.get("ATS#g2", {}).get("secs", {})
    ok(near(s.get("reading", 0), 100) and near(s.get("waiting", 0) + s.get("model", 0), 100),
       "S3 a record exactly at a gen's start opens that gen (200 s): %s" % {k: round(v) for k, v in s.items() if v})
    nul = Path(tempfile.mkdtemp(prefix="nul_", dir=BASE)) / "n.jsonl"
    nul.write_text("\n".join([json.dumps({"timestamp": iso(t0), "message": {"content": [
        {"type": "tool_use", "id": "r", "name": "Read", "input": RD}]}}), "null", json.dumps({"timestamp": iso(t0 + 60),
        "message": {"content": [{"type": "tool_result", "tool_use_id": "r"}]}})]) + "\n", encoding="utf-8")
    rows = tl.tools_of(nul)
    ok(len(rows) == 1 and rows[0]["t1"] is not None and near(rows[0]["t1"] - rows[0]["t0"], 60),
       "S3 a null row in a transcript is skipped, the call still closes: %s" % rows)
    r, _ = runs_of("br[1]", {"BRK": ("/c/brk", [(-5, 1)], {"s.jsonl": [(0, "use", "a", "Read", RD), (60, "res", "a")]})}, t0)
    ok(near(r.get("BRK#g1", {}).get("secs", {}).get("reading", 0), 60), "S3 a [ in the projects path is literal: %s" % sorted(r))
    r, unm = runs_of("shared", {"SHA": ("/c/A_B", [(-5, 1)], {"a.jsonl": [(0, "use", "a", "Read", RD), (60, "res", "a")]}),
                                "SHB": ("/c/A-B", [(-5, 1)], {})}, t0)
    ok(not r and sum("shared with" in u for u in unm) == 2, "S3 a transcript folder two clones map to is UNMEASURED: %s" % unm)
    froot, fproj = mini("frz2", {
        "CPX": ("/c/cpx", [(0, 1), (100, 2)], {"a.jsonl": [(0, "use", "x", "Bash", ST), (60, "res", "x")],
                                               "b.jsonl": [(0, "use", "x", "Bash", ST), (100, "use", "y", "Read", RD),
                                                           (300, "res", "y")]}),
        "SHA": ("/c/A_B", [(-5, 1)], {"a.jsonl": [(0, "use", "a", "Read", RD), (60, "res", "a")]}),
        "SHB": ("/c/A-B", [(-5, 1)], {})}, t0)
    fx = Path(tempfile.mkdtemp(prefix="frzout_", dir=BASE))
    old = {k: os.environ.get(k) for k in ("RELENTLESS_ROOT", "RM_TIME_PROJECTS")}
    os.environ.update(RELENTLESS_ROOT=str(froot), RM_TIME_PROJECTS=str(fproj))
    try:
        tl.freeze([{"run": "CPX#g2", "label": "fine"}], fx, 0)

        def refuses(labels, where):
            try:
                tl.freeze(labels, where, 0)
            except ValueError:
                return True
            return False
        refused = refuses([{"run": "SHA#g1", "label": "fine"}], Path(tempfile.mkdtemp(prefix="frzout_", dir=BASE)))
        before = {q: q.read_bytes() for q in froot.rglob("*") if q.is_file()}
        refrozen = (refuses([{"run": "CPX#g2", "label": "fine"}], fx)                 # already frozen: no stale merge
                    and refuses([{"run": "CPX#g2", "label": "fine"}], froot.parent)   # overlaps the live trees
                    and before == {q: q.read_bytes() for q in froot.rglob("*") if q.is_file()})
        os.environ.update(RELENTLESS_ROOT=str(fx / "relentless"), RM_TIME_PROJECTS=str(fx / "projects"))
        fr, _ = tl.collect_runs(0, fx / "relentless")
    finally:
        for k, v in old.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    s = fr.get("CPX#g2", {}).get("secs", {})
    ok(near(s.get("reading", 0), 200) and near(s.get("selftest", 0), 0) and refused and refrozen,
       "S3 a frozen gen keeps the closed copy from an earlier file (200/0 s) and a shared folder is not frozen: %s %s"
       % ({k: round(v) for k, v in s.items() if v}, refused))

    c = tl.circling_rules()
    L, M = c["test_share_limit"], c["test_share_min"] * 60

    def secs(st, work):
        return dict(dict.fromkeys(tl.KINDS, 0.0), selftest=st, model=work - st, waiting=10 ** 5)
    ok(tl.verdict(secs(2 * M, 2 * M / (L + 0.01)), c)["waste"], "S3 default rules flag a run just over the share limit")
    ok(not tl.verdict(secs(2 * M, 2 * M / (L - 0.01)), c)["waste"], "S3 default rules pass a run just under the share limit")
    ok(tl.verdict(secs(M, M), c)["waste"] and not tl.verdict(secs(M - 1, M - 1), c)["waste"],
       "S3 the test_share_min floor is inclusive: %d s flags, %d s does not" % (M, M - 1))
    runs = {"W#g1": {"secs": secs(2 * M, 2 * M)}, "F#g1": {"secs": secs(1, 2 * M)}}
    lab = [{"run": "W#g1", "label": "waste"}, {"run": "F#g1", "label": "fine"}]
    good = tl.replay(lab, runs, c)
    ok(good["missed"] == 0 and good["wrongful"] == 0, "S3 truth table: caught waste and passed fine read clean: %s/%s"
       % (good["missed"], good["wrongful"]))
    blind = tl.replay(lab, runs, dict(c, test_share_limit=1.0))
    ok(blind["missed"] == 1, "S3 planted fault: flags disabled (limit 1.0) reads as missed waste: %s" % blind["missed"])
    eager = tl.replay(lab, runs, dict(c, test_share_limit=0.0, test_share_min=0))
    ok(eager["wrongful"] == 1, "S3 planted fault: flag everything reads as a wrongful stop: %s" % eager["wrongful"])


if __name__ == "__main__":
    t_s1()
    t_s2()
    t_s3()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
