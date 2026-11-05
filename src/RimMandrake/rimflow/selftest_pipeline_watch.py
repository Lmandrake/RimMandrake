#!/usr/bin/env python3
"""selftest_pipeline_watch.py -- the Pipeline window (PIPELINE_WINDOW_BUILD_TABS_NOT_TERMINALS), offline.

  scopes      a relentless unit's claude-seat scope parses to unit/kind/item; any other scope is ignored
  stations    a run keeps its station until it ends; a new run takes the lowest free one of ITS kind; overflow none;
              every tab (its own process) reads the same map; a systemctl outage changes nothing and ends no run
  render      prose, tool calls and results render one line each; bookkeeping and sidechain records render nothing
  tail        only whole lines are read; the run's transcript is its clone's newest session since launch, the walled
              judge's box included
  follow      a station tab shows its run's past, then what is appended, then that the run ended
  read-only   following and the overview write nothing under the relentless root and run only `systemctl`
              (never claude: zero tokens)
  tile        launch_fleet.ps1 opens PIPELINE at FOUNDRY's rect by default, one tab per station of pipeline_watch,
              hands the focus back, finds the window by its tab-following title; the tab wrapper loops
"""
import ast
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import pipeline_watch as PW  # noqa: E402

FAILS = []


def check(cond, what):
    print(("PASS  " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


def scope(kind, item, gen=1, tail=""):
    return "claude-seat-BENCH-rm-relentless-%s-%s-g%d%s.scope" % (kind, PW.short(item), gen, tail)


def test_scopes():
    u = PW.parse_scope(scope("check", "X_Y_Z", 2, "-c3"))
    check(u and u["kind"] == "check" and u["gen"] == 2 and u["unit"].endswith("-g2-c3"), "a judge scope parses (%s)" % u)
    check(PW.parse_scope("claude-seat-BENCH-228517.scope") is None, "the Conductor's own scope is not a station")
    check(PW.parse_scope("claude-seat-unknown-2101486.scope") is None, "an unknown seat scope is not a station")


def test_stations():
    runs = [{"unit": "w%d" % i, "kind": "work", "start": i} for i in range(10)]
    got = PW.assign({}, runs)
    check([got.get("w%d" % i) for i in range(8)] == ["B%d" % i for i in range(1, 9)], "oldest builder first, B1..B8")
    check("w8" not in got and "w9" not in got, "builders past B8 get no station (the overview lists them)")
    later = PW.assign(got, [r for r in runs if r["unit"] not in ("w0", "w3")] + [{"unit": "n", "kind": "work", "start": 99}])
    check(all(later[u] == got[u] for u in later if u in got), "a running builder keeps its station when others end")
    check(later.get("w8") == "B1", "the oldest waiting builder takes the LOWEST free station (B1, freed by w0)")
    check(later.get("w9") == "B4" and "n" not in later, "the next oldest takes B4 (freed by w3); the newest waits")
    j = PW.assign({"c": "B2"}, [{"unit": "c", "kind": "check", "start": 1}, {"unit": "h", "kind": "help", "start": 2}])
    check(j == {"c": "J1", "h": "C1"}, "kinds never share stations; a stale wrong-kind entry is dropped (%s)" % j)
    d = tempfile.mkdtemp()
    try:
        base = os.path.join(d, "rl")
        os.makedirs(os.path.join(base, "store", "items"))
        sc = [scope("work", "I%d" % i) for i in range(3)]
        _, _, a = PW.poll(base, lambda: sc, d)
        _, _, b = PW.poll(base, lambda: sc, d)
        check(a == b and len(a) == 3 and json.load(open(os.path.join(d, "stations.json"))) == a,
              "every tab reads the same station map")
        scopes, runs_, c = PW.poll(base, lambda: None, d)
        check(scopes is None and runs_ == [] and c == a and json.load(open(os.path.join(d, "stations.json"))) == a,
              "an unreadable unit list changes no station")
    finally:
        shutil.rmtree(d)


def ev(t, blocks, **kw):
    d = {"type": t, "timestamp": "2026-11-05T01:00:00Z", "message": {"content": blocks}}
    d.update(kw)
    return d


def test_render():
    a = PW.render_event(ev("assistant", [{"type": "text", "text": "Hello there"}]))
    check(len(a) == 1 and "Hello there" in a[0], "assistant prose renders")
    b = PW.render_event(ev("assistant", [{"type": "tool_use", "name": "Bash",
                                          "input": {"command": "ls -la", "description": "List files"}}]))
    check(len(b) == 1 and "Bash: List files" in b[0], "a tool call renders as its description")
    c = PW.render_event(ev("user", [{"type": "tool_result", "is_error": True, "content": "boom\nline2\nline3"}]))
    check(len(c) == 1 and "boom" in c[0] and "+2 lines" in c[0] and "✗" in c[0], "an error result: first line + count")
    check(PW.render_event({"type": "attachment"}) == [] and PW.render_event({"type": "api-request"}) == [],
          "bookkeeping records render nothing")
    check(PW.render_event(ev("assistant", [{"type": "text", "text": "x"}], isSidechain=True)) == [],
          "a sub-agent's record does not interleave into the station")
    check(PW.render_event(ev("assistant", [{"type": "thinking", "thinking": ""}])) == [], "empty thinking renders nothing")
    e = PW.render_event(ev("assistant", [{"type": "text", "text": "a\x1b[2Jb\x07c"}]))
    r = PW.render_event(ev("user", [{"type": "tool_result", "content": "x\x1b]0;evil\x07y"}]))
    check("\x1b[2J" not in e[0] and "\x07" not in e[0] and "\x1b]0;" not in r[0] and "\x07" not in r[0],
          "a worker's control characters never reach the terminal (no clear, no retitle)")


def test_tail_and_transcript():
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "t.jsonl")
        with open(p, "w") as f:
            f.write(json.dumps({"a": 1}) + "\n" + '{"b": ')
        recs, off = PW.read_from(p, 0)
        check(recs == [{"a": 1}] and off == len(json.dumps({"a": 1})) + 1, "a half-written line waits")
        with open(p, "a") as f:
            f.write('2}\n')
        recs, off2 = PW.read_from(p, off)
        check(recs == [{"b": 2}], "and is read once whole")
        home = os.path.join(d, "home")
        clone = "/home/x/rm/relentless/clones/IT"
        pd = os.path.join(home, ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", clone))
        os.makedirs(pd)
        old, new = os.path.join(pd, "old.jsonl"), os.path.join(pd, "new.jsonl")
        for q in (old, new):
            open(q, "w").close()
        now = time.time()
        os.utime(old, (now - 3600, now - 3600))
        os.utime(new, (now, now))
        saved = os.environ.get("HOME")
        os.environ["HOME"] = home
        try:
            check(PW.transcript_for({"clone": clone, "start": now - 60}) == new, "the newest session since launch")
            check(PW.transcript_for({"clone": clone, "start": now + 3600}) is None, "nothing older than the run")
            box = os.path.join(d, "walled", "abc")
            tree = os.path.join(box, "tree")
            wd = os.path.join(box, "projects", re.sub(r"[^A-Za-z0-9]", "-", tree))
            os.makedirs(wd)
            open(os.path.join(wd, "s.jsonl"), "w").close()
            check(PW.transcript_for({"clone": tree, "start": now - 60}) == os.path.join(wd, "s.jsonl"),
                  "a walled judge's transcript is read from its box")
        finally:
            os.environ["HOME"] = saved
    finally:
        shutil.rmtree(d)


def snapshot(top):
    got = {}
    for dp, dn, fn in os.walk(top):
        for n in dn + fn:
            p = os.path.join(dp, n)
            st = os.lstat(p)
            got[p] = (st.st_size, st.st_mtime_ns)
    return got


def test_follow_and_readonly():
    d = tempfile.mkdtemp()
    saved = os.environ.get("HOME")
    real_run, real_popen = subprocess.run, subprocess.Popen
    calls = []
    try:
        base = os.path.join(d, "relentless")
        clone = os.path.join(base, "clones", "ITEM_A")
        os.makedirs(clone)
        os.makedirs(os.path.join(base, "store", "items", "ITEM_A"))
        roles = os.path.join(base, "store", "runs", "roles")
        os.makedirs(roles)
        sc = scope("work", "ITEM_A")
        unit = PW.parse_scope(sc)["unit"]
        with open(os.path.join(roles, unit + ".json.clone"), "w") as f:
            f.write(clone)
        home = os.path.join(d, "home")
        os.environ["HOME"] = home
        pd = os.path.join(home, ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", clone))
        os.makedirs(pd)
        tp = os.path.join(pd, "sess.jsonl")
        with open(tp, "w") as f:
            f.write(json.dumps(ev("assistant", [{"type": "text", "text": "first words"}])) + "\n")
        state = os.path.join(d, "state")
        os.makedirs(state)
        before = snapshot(base)
        live = [[sc]]
        PW.POLL_S = 0
        out = io.StringIO()

        def scopes():
            calls.append("scopes")
            return live[0]
        PW.follow_station("B1", base, rounds=1, out=out, state_dir=state, scopes_fn=scopes)
        s = out.getvalue()
        check("Builder 1 · ITEM_A · gen 1 · work" in s and "first words" in s, "the tab shows its run and its past")
        # one follower across rounds: append, then end the unit
        out = io.StringIO()
        steps = iter([[sc], [sc], []])

        def scripted():
            v = next(steps, [])
            if v == [sc] and calls.count("appended") == 0:
                with open(tp, "a") as f:
                    f.write(json.dumps(ev("assistant", [{"type": "tool_use", "name": "Read",
                                                         "input": {"file_path": "/x/y.py"}}])) + "\n")
                calls.append("appended")
            return v
        PW.follow_station("B1", base, rounds=3, out=out, state_dir=state, scopes_fn=scripted)
        s = out.getvalue()
        check("Read: /x/y.py" in s, "what the worker does next reaches the tab")
        check("ended; station idle" in s, "the tab says when its run ended")
        out = io.StringIO()
        PW.follow_station("B2", base, rounds=1, out=out, state_dir=state, scopes_fn=lambda: [sc])
        check("no run here yet" in out.getvalue(), "an empty station says so once")
        out = io.StringIO()
        blind = iter([[sc], None, None, [sc]])
        PW.follow_station("B1", base, rounds=4, out=out, state_dir=state, scopes_fn=lambda: next(blind))
        s = out.getvalue()
        check("cannot read the unit list" in s and "ended" not in s and s.count("Builder 1 ·") == 1,
              "a systemctl outage is not an ended run: the tab keeps its worker (%r)" % s[-200:])
        PW.overview(base, rounds=1, out=io.StringIO(), state_dir=state, scopes_fn=lambda: [sc])
        check(snapshot(base) == before, "following and the overview write NOTHING under the relentless root")

        def spy_run(argv, *a, **k):
            calls.append(list(argv))
            return subprocess.CompletedProcess(argv, 0, stdout=sc + " loaded active running x\n", stderr="")

        def spy_popen(argv, *a, **k):
            calls.append(list(argv))
            raise AssertionError("Popen")
        subprocess.run, subprocess.Popen = spy_run, spy_popen
        got = PW.list_scopes()
        PW.follow_station("B1", base, rounds=2, out=io.StringIO(), state_dir=state)
        PW.overview(base, rounds=1, out=io.StringIO(), state_dir=state)
    finally:
        subprocess.run, subprocess.Popen = real_run, real_popen
        os.environ["HOME"] = saved
        shutil.rmtree(d)
    argvs = [c for c in calls if isinstance(c, list)]
    check(got == [sc], "the unit list is read from systemctl's active claude-seat scopes")
    check(argvs and all(c[0] == "systemctl" and "--user" in c for c in argvs),
          "the only command it runs is `systemctl --user` (%d calls)" % len(argvs))
    tree = ast.parse(open(os.path.join(HERE, "pipeline_watch.py"), encoding="utf-8").read())
    consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    imports = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
               for a in (n.names if isinstance(n, ast.Import) else [type("m", (), {"name": n.module or ""})])}
    check("claude" not in consts and not any(c.startswith("claude ") for c in consts)
          and not imports & {"anthropic", "relentless", "requests", "urllib"},
          "it can never start claude or call an API: zero tokens")


def ps1():
    with open(os.path.join(ROOT, "src", "RimMandrake", "Utils", "launch_fleet.ps1"), encoding="utf-8") as f:
        return f.read()


def test_tile():
    s = ps1()
    seats = re.search(r"\[string\[\]\]\$Seats = @\(([^)]*)\)", s).group(1)
    check("'PIPELINE'" in seats and seats.index("'PIPELINE'") < seats.index("'BENCH'"),
          "PIPELINE opens by default, before BENCH (which takes the focus last)")
    rect = dict(re.findall(r"^\s+(FOUNDRY|PIPELINE)\s+= (@\(.*?\))\s*(?:#.*)?$", s, re.M))
    check(rect.get("PIPELINE") and rect.get("PIPELINE") == rect.get("FOUNDRY"), "PIPELINE sits at FOUNDRY's rect")
    check("if ($seat -eq 'FOUNDRY') { Write-Warning \"FOUNDRY is retired; not launched\"; continue }" in s,
          "FOUNDRY itself is still never launched")
    tabs = re.search(r"\$pipelineTabs = (.*)", s).group(1)
    want = ["overview"] + PW.STATIONS
    built = ["overview"]
    for p, n in re.findall(r"\(1\.\.(\d+) \| ForEach-Object \{ \"([A-Z])\$_\" \}\)", tabs):
        built += [n + str(i) for i in range(1, int(p) + 1)]
    built += re.findall(r"@\('([A-Z]\d)'\)", tabs)
    check(built == want, "one tab per pipeline_watch station, in order (%s)" % built)
    check("'/home/mandrake/rm/bench/src/RimMandrake/rimflow/pipeline_watch.sh'" in s,
          "the tabs run the wrapper from BENCH's clone")
    check("$prevFg = if ($seat -eq 'PIPELINE') { [Fleet]::GetForegroundWindow() }" in s
          and "if ($prevFg -ne [IntPtr]::Zero) { Restore-Focus $prevFg }" in s
          and s.index("function Restore-Focus") < s.index("Restore-Focus $prevFg"),
          "the Pipeline hands the focus back to whoever had it (defined before use)")
    check("$titleFor.Contains($_) -and $_ -ne 'PIPELINE'" in s and "(-not $Fresh -or $seat -eq 'PIPELINE')" in s,
          "-Fresh neither closes nor duplicates the Pipeline (no WT close-all-tabs prompt, no second window)")
    pat = re.search(r"WindowsMatching\('([^']+)'\)", s).group(1)
    check(all(re.match(pat, t) for t in ["Pipeline", "Pipeline B3", "Pipeline J4", "Pipeline C1"])
          and not any(re.match(pat, t) for t in ["Pipeline [test]", "CONDUCTOR", "Pipelines", "Pipeline B3 x"]),
          "the window is found whichever tab is active, and nothing else matches")
    check(s.count("[Fleet]::WindowsTitled(") == 2, "every sweep/keep/wait lookup goes through Find-Fleet")
    sh = os.path.join(HERE, "pipeline_watch.sh")
    check(os.access(sh, os.X_OK) and "while true" in open(sh).read()
          and subprocess.run(["bash", "-n", sh]).returncode == 0,
          "the tab wrapper is executable, parses, and restarts the renderer (a tab never drops to a prompt)")


if __name__ == "__main__":
    for fn in (test_scopes, test_stations, test_render, test_tail_and_transcript, test_follow_and_readonly, test_tile):
        fn()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
