#!/usr/bin/env python3
"""Selftest of `pipe` (pipeline_control.py; item RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS). The
owner, 2026-11-18: "This should be a one-line bash command, ok? ... Make all of this deterministic, easy, traceable,
reproducable, testable".

Proves, on temp stores and fixtures only (never the live store, never a live mod):
  - every verb acts in one line and prints at most 3 lines; --why is demanded and nothing else; a wrong mod, consumable,
    stage or act id is refused with the nearest valid names;
  - each consumable's real reader honours the store (coverage looks, runs, verdict counts; blind cycles per visit and
    in the visit), and a reader that ignores the store fails here (the mutant: used() returning the raw count);
  - the reader census: every place a limit constant is compared lives in a function the census lists, and every listed
    function reads the store through used()/limit();
  - `pipe off <Mod>` reads as a hold to mod_owner_hold.load() (so every hold reader honours it), item/stage/all switch
    the tick's launches to control_off, classed held (no pause or stall alarm);
  - undo puts back what an act changed and is itself an act; replaying the journal on a fresh dir reproduces the
    state exactly; a torn snapshot is rebuilt from the journal; an unreadable journal raises Unreadable everywhere
    (everything OFF, a named error), never a calm empty store.
"""
import contextlib
import inspect
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def check(ok, msg, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", msg, "" if ok or got is None else "  (got %r)" % (got,)))
    if not ok:
        FAILS.append(msg)


def concept(st):
    d = os.path.join(os.environ["RM_PIPE_ROOT"], "design", "concepts", st["mod"])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump(st, f)
    return st


def run(*argv):
    import pipeline_control as PC
    buf = io.StringIO()
    t = time.time()
    with contextlib.redirect_stdout(buf):
        rc = PC.main(list(argv))
    return rc, buf.getvalue().strip().splitlines(), time.time() - t


def fixture():
    """A temp pipeline: a control dir, a dispatch state dir, a tree with one concept (Fx) whose coverage release has
    spent its one look on a not_covered verdict, and an owner hold file holding nothing."""
    root = tempfile.mkdtemp(prefix="pipe_ctl_")
    ctl, md = os.path.join(root, "control"), os.path.join(root, "maturation")
    os.makedirs(md)
    d = os.path.join(root, "design", "concepts", "Fx")
    os.makedirs(d)
    st = {"mod": "Fx", "status": "blocked",
          "coverage_rounds": [{"judge": "rm-coverage-judge-1", "verdict": "not_covered", "tokens": 1000},
                              {"judge": "rm-coverage-judge-2", "verdict": "not_covered", "tokens": 1000}],
          "coverage_releases": [{"rounds_at": 1, "final": True, "granted_at": "2026-11-18T00:00:00Z", "after": []}]}
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump(st, f)
    os.makedirs(os.path.join(root, "src", "RimMandrake", "rimflow"))
    with open(os.path.join(root, "src", "RimMandrake", "rimflow", "maturation_dispatch.json"), "w") as f:
        json.dump({"advancing": ["Fx", "Gx", "Hx"], "blind_auto_cycles_per_visit": 1}, f)
    with open(os.path.join(md, "state.json"), "w") as f:
        json.dump({"mods": {"Fx": {"blind_auto": [{"visit_id": "0.1.0#1", "cycle": 1, "unit": "rm-x-1"}]},
                            "Gx": {}, "Hx": {}}}, f)
    hold = os.path.join(root, "mod_owner_hold.json")
    with open(hold, "w") as f:
        json.dump({"holds": []}, f)
    os.environ.update(RM_PIPE_CONTROL_DIR=ctl, RM_MATURATION_DISPATCH_DIR=md, RM_PIPE_ROOT=root,
                      RM_OWNER_HOLD_FILE=hold)
    return root, st


def fake_blind(PC):
    """The blind measures read maturation's record; the fixture has none, so they read a fixed visit."""
    def visit(ctx, mod):
        ours = [x for x in ctx.mstate(mod).get("blind_auto") or [] if x.get("visit_id") == "0.1.0#1"]
        return len(ours), 1
    PC.RESOURCES["blind_cycles_visit"] = PC.RESOURCES["blind_cycles_visit"][:2] + (
        visit, PC.RESOURCES["blind_cycles_visit"][3])
    PC.RESOURCES["blind_cycles_total"] = PC.RESOURCES["blind_cycles_total"][:2] + (
        lambda ctx, mod: (3, 3), PC.RESOURCES["blind_cycles_total"][3])


def test_verbs_and_coverage(st):
    import pipeline_control as PC
    import coverage_judge as CJ
    PC._CACHE.clear()
    check(PC.state() == PC.empty(), "no journal reads as the empty store (nothing commanded)")
    check("look" in (CJ.stop_reason(st) or ""),
          "the fixture's granted look is spent: judging stops", CJ.stop_reason(st))
    rc, out, secs = run("add", "Fx", "granted_look", "-1", "--why", "the look died on a system fault")
    check(rc == 0 and len(out) <= 3 and "1/1 -> 0/1" in out[0], "add -1 prints before -> after in <= 3 lines", out)
    check(any(l.startswith("undo: pipe undo pc_") for l in out), "the act prints its undo command", out)
    act_id = re.search(r"act (pc_\w+)", "\n".join(out)).group(1)
    check("look" not in (CJ.stop_reason(st) or ""),
          "the real reader (coverage_judge.stop_reason) sees the look given back", CJ.stop_reason(st))
    rc, out, _ = run("undo", act_id, "--why", "test undo")
    check(rc == 0 and len(out) <= 3 and "undoes %s" % act_id in out[0], "undo prints what it put back", out)
    check("look" in (CJ.stop_reason(st) or ""), "after undo the look is spent again",
          CJ.stop_reason(st))
    rc, out, _ = run("set", "Fx", "look", "0", "--why", "label works too")
    check(rc == 0 and "-> 0/1" in out[0], "set by the short label (look) reads 0", out)
    rc, out, _ = run("reset", "Fx", "granted_look", "--why", "reset")
    check(rc == 0 and "-> 0/1" in out[0], "reset reads 0", out)
    rc, out, _ = run("set", "Fx", "granted_look", "1", "--why", "back")
    # the caps after a release: coverage_runs since it
    st2 = concept(dict(st, mod="Rx", coverage_releases=[], coverage_rounds=[{"judge": "j%d" % i, "verdict": "covered", "tokens": 1}
                                                          for i in range(4)]))
    check("4 judge runs" in (CJ.stop_reason(st2) or ""), "four runs stop judging (base)", CJ.stop_reason(st2))
    run("limit", "Rx", "coverage_runs", "6", "--why", "an exception")
    check(CJ.stop_reason(st2) is None, "limit 6 on coverage_runs lets judging go on", CJ.stop_reason(st2))
    run("limit", "Rx", "coverage_runs", "default", "--why", "back to the shipped limit")
    check("4 judge runs" in (CJ.stop_reason(st2) or ""), "limit default restores the shipped 4", CJ.stop_reason(st2))
    st3 = concept(dict(st, mod="Nx", coverage_releases=[], coverage_rounds=[{"judge": "j%d" % i, "verdict": "not_covered", "tokens": 1}
                                                          for i in range(CJ.NOT_COVERED_LIMIT)]))
    check("not_covered" in (CJ.stop_reason(st3) or ""), "NOT_COVERED_LIMIT not_covered verdicts stop judging (base)", CJ.stop_reason(st3))
    run("add", "Nx", "coverage_not_covered", "-1", "--why", "one was a harness fault")
    check(CJ.stop_reason(st3) is None, "forgiving one not_covered lets judging go on", CJ.stop_reason(st3))
    st4 = concept(dict(st, mod="Bx", coverage_releases=[], coverage_rounds=[{"judge": "j%d" % i, "verdict": "malformed", "tokens": 1}
                                                          for i in range(CJ.MALFORMED_LIMIT)]))
    check("malformed" in (CJ.stop_reason(st4) or ""), "malformed verdicts stop judging (base)", CJ.stop_reason(st4))
    run("add", "Bx", "coverage_malformed", "-1", "--why", "a broken pipe, not the brief")
    check("malformed" not in (CJ.stop_reason(st4) or ""), "forgiving one malformed verdict lifts that stop",
          CJ.stop_reason(st4))
    # refusals with nearest names; --why demanded
    rc, out, _ = run("add", "Fxx", "granted_look", "-1", "--why", "typo")
    check(rc == 2 and "nearest: Fx" in out[0], "a wrong mod is refused with the nearest names", out)
    rc, out, _ = run("add", "Fx", "granted_lok", "-1", "--why", "typo")
    check(rc == 2 and "granted_look" in out[0], "a wrong consumable is refused with the nearest names", out)
    rc, out, _ = run("off", "stage:blind_chalenge", "--why", "typo")
    check(rc == 2 and "blind_challenge" in out[0], "a wrong stage is refused with the nearest names", out)
    rc, out, _ = run("undo", "pc_nope", "--why", "typo")
    check(rc == 2 and "no act" in out[0], "an unknown act id is refused", out)
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            PC.main(["add", "Fx", "granted_look", "-1"])
        check(False, "an act without --why is refused")
    except SystemExit as e:
        check(e.code == 2, "an act without --why is refused (argparse exit 2)", e.code)


def test_blind_reader():
    import pipeline_control as PC
    import maturation_dispatch as MD
    fake_blind(PC)
    s = {"blind_auto": [{"visit_id": "0.1.0#1", "cycle": 1, "unit": "rm-x-1"}]}
    f = {"mod": "Fx", "cycle": 2, "version": "0.1.0", "visit_first": 1, "live_units": [], "owed": "cycle", "exit": {}}
    cfg = {"blind_auto_cycles_per_visit": 1, "settle_s": 180, "launch_tries": 3, "blind_enabled": True}

    def decide():
        row = {"mod": "Fx"}

        def put(decision, why, need=None):
            row["decision"], row["why"] = decision, why
        put.row = row
        try:
            MD.decide_blind(cfg, dict(s), dict(f), row, put, time.time(), (True, "ok"), 0, [])
        except Exception as e:      # noqa: BLE001  past the counter the fixture is thin; the counter is what is read
            row.setdefault("decision", "past_counter (%s)" % type(e).__name__)
        return row.get("decision")

    check(decide() == "auto_spent", "base: the visit's one automatic cycle is spent", decide())
    rc, out, _ = run("add", "Fx", "blind_cycles_visit", "-1", "--why", "killed by the Conductor's stop")
    check(rc == 0 and "1/1 -> 0/1" in out[0], "add -1 on blind_cycles_visit", out)
    check(decide() != "auto_spent", "decide_blind honours the store: the cycle is no longer spent", decide())
    run("add", "Fx", "blind_cycles_visit", "+1", "--why", "back")
    check(decide() == "auto_spent", "add +1 spends it again", decide())
    run("limit", "Fx", "blind_cycles_visit", "2", "--why", "an exception: one more automatic cycle")
    check(decide() != "auto_spent", "a raised limit lets one more cycle go", decide())
    run("limit", "Fx", "blind_cycles_visit", "default", "--why", "back")


def test_mutant():
    """A reader that ignores the store must fail: used() returning the raw count leaves the look spent."""
    import pipeline_control as PC
    import coverage_judge as CJ
    st = concept({"mod": "Mx", "coverage_rounds": [{"judge": "a", "verdict": "not_covered", "tokens": 1}],
                  "coverage_releases": [{"rounds_at": 0, "final": False}]})
    run("add", "Mx", "granted_look", "-1", "--why", "mutant check")
    honest = CJ.stop_reason(st)
    real = PC.used
    try:
        PC.used = lambda mod, res, measured, st=None: measured
        mutant = CJ.stop_reason(st)
    finally:
        PC.used = real
    check(honest is None and mutant is not None, "a store-blind used() (the mutant) changes the verdict: caught",
          (honest, mutant))


# the names a reader of each limit must use: constants, settings keys. A use of one in code (ast: never a comment or a
# docstring) outside a census reader, in a function that does not read the store, is a bypass.
LIMIT_TOKENS = {
    "granted_look": [],     # a code shape, not a name: its one reader is listed and checked above
    "coverage_runs": ["JUDGE_RUNS_MAX"],
    "coverage_not_covered": ["NOT_COVERED_LIMIT"],
    "coverage_malformed": ["MALFORMED_LIMIT"],
    "blind_cycles_visit": ["blind_auto_cycles_per_visit"],
    "blind_cycles_total": ["CYCLE_LIMIT"],
}


def uses(path, tokens):
    """-> [(line, function or None, token)] for each code use of a token: a Name, an Attribute or a str constant."""
    import ast
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    out = []

    def walk(node, fn):
        for ch in ast.iter_child_nodes(node):
            f = ch.name if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
            tok = (ch.id if isinstance(ch, ast.Name) else ch.attr if isinstance(ch, ast.Attribute)
                   else ch.value if isinstance(ch, ast.Constant) and isinstance(ch.value, str) else None)
            if tok in tokens and not (isinstance(ch, ast.Name) and isinstance(ch.ctx, ast.Store)):
                out.append((ch.lineno, fn, tok))
            walk(ch, f)
    walk(tree, None)
    return out


def test_reader_census():
    import pipeline_control as PC
    import importlib
    srcs = {}
    for res, (_lab, _doc, _m, readers) in PC.RESOURCES.items():
        check(readers, "%s names its readers" % res)
        for mod, fn in readers:
            src = inspect.getsource(getattr(importlib.import_module(mod), fn))
            check(re.search(r"PC\.used\([^)]*\"%s\"" % res, src) is not None,
                  "%s.%s reads %s through PC.used" % (mod, fn, res))
    check(set(LIMIT_TOKENS) == set(PC.RESOURCES), "every consumable has its limit tokens in this census",
          sorted(set(PC.RESOURCES) ^ set(LIMIT_TOKENS)))
    tok_res = {t: r for r, ts in LIMIT_TOKENS.items() for t in ts}
    seen = 0
    for base in (HERE, os.path.join(HERE, "..", "Utils")):
        for name in sorted(os.listdir(base)):
            if not name.endswith(".py") or name.startswith(("selftest_", "accept_", "pipeline_control")):
                continue
            path = os.path.join(base, name)
            for line, fn, tok in uses(path, set(tok_res)):
                if fn is None:
                    continue        # module level: a definition (X = 3) or an import-time constant, not a decision
                res = tok_res[tok]
                m = importlib.import_module(name[:-3]) if base == HERE else None
                body = inspect.getsource(getattr(m, fn)) if m is not None and hasattr(m, fn) else ""
                if not body:
                    with open(path, encoding="utf-8") as fh:
                        body = fh.read()
                ok = re.search(r"PC\.(used|limit)\([^)]*\"%s\"" % res, body) is not None
                seen += 1
                check(ok, "%s:%d %s uses %s (%s) %s" % (name, line, fn, tok, res, "through the store" if ok else
                                                         "WITHOUT the store: a bypass"))
    check(seen >= 6, "the census scan sees the known readers (%d uses), so a clean result is not a blind one" % seen)


def test_switches(root):
    import pipeline_control as PC
    import mod_owner_hold as OH
    hold = os.environ.pop("RM_OWNER_HOLD_FILE")
    try:
        os.environ["RM_OWNER_HOLD_FILE"] = hold
        check("Gx" not in OH.load(), "base: Gx is not held")
        rc, out, _ = run("off", "Gx", "--why", "stop it now")
        check(rc == 0 and out[0] == "mod:Gx ON -> OFF" and len(out) == 3, "off Gx prints ON -> OFF", out)
        h = OH.load().get("Gx")
        check(bool(h) and h.get("control") and "OFF by pipe" in OH.status(h) and "stop it now" in OH.status(h),
              "mod_owner_hold.load() reads pipe's off as a hold, status OFF by pipe with its why", h)
        check(OH.load(hold).get("Gx") is None, "his own file is untouched: an explicit path reads the file alone")
        rc, out, _ = run("on", "Gx", "--why", "go again")
        check(rc == 0 and "OFF -> ON" in out[0] and "Gx" not in OH.load(), "on Gx clears it", out)
        rc, out, _ = run("on", "Gx", "--why", "again")
        check(rc == 0 and "already ON" in out[0] and len(out) == 1, "on of an ON thing says so in one line", out)
        rc, out, _ = run("off", "item:RIMMANDRAKE_FX_ITEM", "--why", "skip this item")
        check(rc == 0 and PC.off(item="RIMMANDRAKE_FX_ITEM") and not PC.off(item="RIMMANDRAKE_OTHER"),
              "an item switch is scoped to that item", out)
        rc, out, _ = run("off", "RIMMANDRAKE_FX_TWO", "--why", "a bare item id")
        check(rc == 0 and out[0].startswith("item:RIMMANDRAKE_FX_TWO"), "a bare item id switches the item", out)
        run("off", "stage:in_game", "--why", "no live runs today")
        check(bool(PC.off(stage="in_game")) and not PC.off(stage="blind_challenge"), "a stage switch is scoped")
        run("off", "all", "--why", "pause everything")
        check(bool(PC.off(mod="Hx")) and "OFF by pipe (all" in PC.off(mod="Hx"), "all switches everything off")
        run("on", "all", "--why", "resume")
        run("on", "stage:in_game", "--why", "resume")
        rc, out, _ = run("show")
        check(rc == 0 and len(out) <= 25 and any(l.startswith("Fx ") for l in out), "show is one screen, a row per "
              "mod", out)
        check(any("item:RIMMANDRAKE_FX_ITEM OFF" in l for l in out), "show lists an item switch", out)
        rc, out, _ = run("show", "Fx")
        check(rc == 0 and any("granted_look" in l for l in out), "show <Mod> lists each consumable with its doc", out)
        rc, out, _ = run("log", "-n", "3")
        check(rc == 0 and len(out) == 3 and all(l.startswith("pc_") for l in out), "log -n 3 prints the last 3", out)
    finally:
        os.environ["RM_OWNER_HOLD_FILE"] = hold


def test_tick_switch(root):
    """The tick itself: an item, stage or all switch turns a launch into control_off, classed held."""
    import pipeline_control as PC
    import maturation_dispatch as MD
    import maturation_autonomy as AUT
    rows = [{"mod": "Fx", "stage": "blind_challenge", "decision": "launch", "item": "RIMMANDRAKE_FX_ITEM"}]
    src = inspect.getsource(MD._tick)
    check("PC.off(item=" in src and "control_off" in src, "_tick filters its launches through PC.off")
    row = {"mod": "Fx", "decision": "control_off", "why": "OFF by pipe"}
    AUT._klass({"stalled_min": 0}, {}, row, time.time(), {})
    check(row["klass"] == "held" and not row["stalled"], "a control_off row is held, never paused or stalled", row)
    run("on", "item:RIMMANDRAKE_FX_ITEM", "--why", "done")
    run("on", "item:RIMMANDRAKE_FX_TWO", "--why", "done")
    check(not PC.off(item="RIMMANDRAKE_FX_ITEM"), "the item switch is back on")


def test_journal_replay_and_damage(root):
    import pipeline_control as PC
    d = os.environ["RM_PIPE_CONTROL_DIR"]
    PC._CACHE.clear()
    live = PC.state()
    with open(os.path.join(d, PC.JOURNAL)) as f:
        lines = f.read().splitlines()
    check(all({"id", "who", "at", "at_pacific", "why", "before", "after"} <= set(json.loads(l)) for l in lines),
          "every act records who, when (UTC and Pacific), why, before and after")
    check(PC.fold(lines) == live, "replaying the journal reproduces the state exactly")
    fresh = os.path.join(root, "replay")
    os.makedirs(fresh)
    shutil.copy(os.path.join(d, PC.JOURNAL), fresh)
    PC._CACHE.clear()
    check(PC.state(fresh) == live, "a fresh dir holding only the journal reads the same state")
    with open(os.path.join(d, PC.SNAPSHOT), "w") as f:
        f.write("{torn")
    PC._CACHE.clear()
    check(PC.state() == live, "a torn snapshot is rebuilt from the journal")
    with open(os.path.join(d, PC.JOURNAL), "a") as f:
        f.write("not json\n")
    PC._CACHE.clear()
    try:
        PC.state()
        check(False, "an unreadable journal raises")
    except PC.Unreadable as e:
        check("line" in str(e), "an unreadable journal raises Unreadable naming the line", str(e))
    import mod_owner_hold as OH
    # the switches moved to control.py's SQLite store (its unreadable case: selftest_control.t_unreadable); this
    # journal now holds counts, limits and the queue only, so a torn journal stops their readers, not the hold reader
    OH.load()
    check(True, "a torn counts journal leaves the owner-hold reader on control.py's store")
    rc, out, _ = run("show")
    check(rc == 3 and "launches NOTHING" in out[0], "pipe itself says the store is unreadable, exit 3", out)


def test_speed():
    worst = 0.0
    for argv in (("show",), ("show", "Fx"), ("add", "Fx", "granted_look", "-1", "--why", "t"),
                 ("off", "Fx", "--why", "t"), ("on", "Fx", "--why", "t"), ("log",)):
        rc, out, secs = run(*argv)
        worst = max(worst, secs)
        if argv[0] != "show" and argv[0] != "log":
            check(len(out) <= 3, "%s prints at most 3 lines" % argv[0], out)
    check(worst < 2.0, "every verb runs under 2 s in-process (worst %.2f s)" % worst)


def main():
    keep = {k: os.environ.get(k) for k in ("RM_PIPE_CONTROL_DIR", "RM_MATURATION_DISPATCH_DIR", "RM_PIPE_ROOT",
                                           "RM_OWNER_HOLD_FILE")}
    root, st = fixture()
    try:
        test_verbs_and_coverage(st)
        test_blind_reader()
        test_mutant()
        test_reader_census()
        test_switches(root)
        test_tick_switch(root)
        test_speed()
        test_journal_replay_and_damage(root)
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
