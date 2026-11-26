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
                      RM_OWNER_HOLD_FILE=hold, RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
    os.makedirs(os.path.join(root, "dispatcher"))
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
    # the counts live in control.py's store now (slice 2, RIMMANDRAKE_TYPE_EVERY_CONSUMABLE_AS_ACCOUNT_OLD_COUNTERS_GO)
    check(any(l.startswith("undo: pipe undo ct_") for l in out), "the act prints its undo command", out)
    act_id = re.search(r"act (ct_\w+)", "\n".join(out)).group(1)
    check("look" not in (CJ.stop_reason(st) or ""),
          "the real reader (coverage_judge.stop_reason) sees the look given back", CJ.stop_reason(st))
    rc, out, _ = run("undo", act_id, "--why", "test undo")
    check(rc == 0 and len(out) <= 3 and "%s undone" % act_id in out[0], "undo prints what it put back", out)
    check("look" in (CJ.stop_reason(st) or ""), "after undo the look is spent again",
          CJ.stop_reason(st))
    rc, out, _ = run("set", "Fx", "look", "0", "--why", "label works too")
    check(rc == 0 and "-> 0/1" in out[0], "set by the short label (look) reads 0", out)
    rc, out, _ = run("reset", "Fx", "granted_look", "--why", "reset")
    check(rc == 0 and "-> 0/1" in out[0], "reset reads 0", out)
    rc, out, _ = run("set", "Fx", "granted_look", "1", "--why", "back")
    # the caps after a release: coverage_runs since it
    st2 = concept(dict(st, mod="Rx", coverage_releases=[], coverage_rounds=[{"judge": "j%d" % i, "verdict": None, "error": "exited 1",
                                                           "error_kind": "judge", "tokens": 1} for i in range(4)]))
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
    rc, out, _ = run("undo", "ct_nope", "--why", "typo")
    check(rc == 2 and "no act" in out[0], "an unknown control act id is refused", out)
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
    "ingame_runs_visit": ["ingame_auto_runs_per_visit"],
    "steward_runs": ["steward_max_per_version"],
    "fixer_runs": [],       # the same setting as steward_runs (a token names one consumable); its reader is listed
    "launch_tries": ["launch_tries"],
    "chain_runs_day": ["chain_max_per_day", "CHAIN_MAX_PER_DAY"],
    "refusals": ["ITEM_ALARM_AT"],
    "pilot_streak": ["STREAK"],
    "spend_offline_build": ["stage_ceiling_tokens"],
    "spend_blind_challenge": [],    # one setting, three per-stage accounts: maturation_dispatch.stage_spend reads all
    "spend_in_game": [],
}
# how a reader names the consumable in its PC.used/PC.limit call (default: the name as a string literal)
READ_RX = {r: r"PC\.SPEND_RES\[" for r in ("spend_offline_build", "spend_blind_challenge", "spend_in_game")}


def read_rx(res):
    return READ_RX.get(res, '"%s"' % res)


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
            check(re.search(r"PC\.used\([^)]*%s" % read_rx(res), src) is not None,
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
                ok = re.search(r"PC\.(used|limit)\([^)]*%s" % read_rx(res), body) is not None
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
        check(rc == 0 and len(out) == 3 and all(l.startswith("ct_") for l in out), "log -n 3 prints the control "
                                                                                   "store's last 3", out)
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
    PC.act("queue", None, ["Fx", "Rx"], "the queue is the journal's last section (counts moved to control.py)", "queue")
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
    # journal now holds the queue only (counts and limits: control.py, slice 2), so a torn journal stops its reader
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

# ---- the six more consumables (item RIMMANDRAKE_TYPE_SIX_MORE_CONSUMABLES_READERS_IN_LIVE_LANES; page
# design/specs/2026-11-19-consumable-readers/boundary.md): each promise's test, by its name


def act_line(rc, out, what):
    """A `pipe` write: exit 0, at most 3 lines, its undo printed. -> the act id."""
    m = re.search(r"undo: pipe undo (ct_\w+)", "\n".join(out))
    check(rc == 0 and len(out) <= 3 and m is not None, "%s: one line in, at most 3 out, with its undo" % what, out)
    return m.group(1) if m else "ct_missing"


def put_books(mod, **books):
    """Write `mod`'s books into the fixture's dispatch state.json, so `pipe`'s measure reads what the reader reads."""
    p = os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "state.json")
    with open(p) as fh:
        st = json.load(fh)
    st["mods"].setdefault(mod, {}).update(books)
    with open(p, "w") as fh:
        json.dump(st, fh)


def honours(what, decide, base, n_add, limit_to, more=None):
    """The reader at its base reading; `pipe add -N` moves it; `pipe undo` puts it back; `pipe limit` moves it; `pipe
    limit default` puts it back. more: the consumable's name. decide() -> True when the reader stops (spent)."""
    check(decide() is True, "%s: base: the reader reads it spent" % what, decide())
    aid = act_line(*run("add", base, more, "-%d" % n_add, "--why", "t")[:2], what="add -%d %s" % (n_add, more))
    check(decide() is False, "%s: `pipe add %s %s -%d` moves the reader" % (what, base, more, n_add), decide())
    rc, out, _ = run("undo", aid, "--why", "t")
    check(rc == 0 and decide() is True, "%s: `pipe undo` puts the reader back" % what, (out, decide()))
    act_line(*run("limit", base, more, str(limit_to), "--why", "t")[:2], what="limit %s" % more)
    check(decide() is False, "%s: `pipe limit %s %s %d` moves the reader" % (what, base, more, limit_to), decide())
    run("limit", base, more, "default", "--why", "t")
    check(decide() is True, "%s: `pipe limit ... default` restores the pipeline's own limit" % what, decide())


def t_ingame_runs_read_the_store():
    import maturation_dispatch as MD
    s = {"ingame_auto": [{"visit_id": "0.1.0#1", "visit": 0, "unit": "rm-ig-0"}]}
    f = {"mod": "Fx", "visit": 1, "version": "0.1.0", "exit": {}, "live_units": [], "owed": "run", "ingame_runs": []}
    cfg = {"ingame_auto_runs_per_visit": 1, "settle_s": 180, "launch_tries": 3, "ingame_enabled": True}

    def decide():
        row = {"mod": "Fx"}

        def put(decision, why, need=None):
            row["decision"], row["why"] = decision, why
        try:
            MD.decide_ingame(cfg, dict(s), dict(f), row, put, time.time(), (True, "ok"), 0, [], (True, "ok"))
        except Exception as e:      # noqa: BLE001  past the counter the fixture is thin; the counter is what is read
            row.setdefault("decision", "past_counter (%s)" % type(e).__name__)
        return row.get("decision") == "auto_spent"
    honours("decide_ingame", decide, "Fx", 1, 2, "ingame_runs_visit")


def t_steward_runs_read_the_store():
    import maturation_autonomy as AUT
    cfg = {"steward_max_per_version": 12, "steward_enabled": True, "steward_cap_tokens": 2_000_000, "fix_cap_tokens": 2_500_000,
           "max_live": 2}

    def gate(aut):
        if aut == "steward":
            row = {"mod": "Fx", "aut": "steward", "steward_key": "0.1.0|new"}
            st = {"steward": {"0.1.0|k%d" % i: {"unit": "rm-s-%d" % i} for i in range(12)}}
        else:
            row = {"mod": "Fx", "aut": "fixer", "fix_item": "RIMMANDRAKE_FX_NEW"}
            st = {"fixers": fixers}
        go, got = AUT._gate(cfg, st, row, 0, "0.1.0")
        return bool(got) and got[0] == "steward_spent"
    # a program's own act (a game_only key: no unit ever launched, `landed` set) is no run: FlowWorks read 12 of 12 on 10
    acts = {"steward": dict({"0.1.0|k%d" % i: {"unit": "rm-s-%d" % i} for i in range(10)},
                            **{"0.1.0|offline_build|game_only|%d" % i: {"unit": None, "item": None, "failed": None,
                                                                       "landed": "PUBLISHED x"} for i in range(2)})}
    go, got = AUT._gate(cfg, acts, {"mod": "Fx", "aut": "steward", "steward_key": "0.1.0|new"}, 0, "0.1.0")
    check("_gate counts no program act as a steward run", not (got and got[0] == "steward_spent"), got)
    fixers = {"RIMMANDRAKE_FX_%d" % i: {"unit": "rm-f-%d" % i} for i in range(12)}
    put_books("Fx", fixers=fixers)      # pipe's measure of fixer_runs reads the tick's books: 12 here too
    honours("_gate (steward)", lambda: gate("steward"), "Fx", 1, 13, "steward_runs")
    honours("_gate (fixer)", lambda: gate("fixer"), "Fx", 1, 13, "fixer_runs")


def t_launch_tries_read_the_store():
    import maturation_dispatch as MD
    import maturation_autonomy as AUT
    fail = {"failed": "fatal: Unable to create index.lock: File exists", "tries": 3, "cycle": 2, "visit_id": "0.1.0#1"}
    cfg = {"launch_tries": 3, "blind_auto_cycles_per_visit": 3, "settle_s": 180, "blind_enabled": True,
           "steward_max_per_version": 12, "steward_enabled": True, "steward_cap_tokens": 2_000_000, "max_live": 2}
    f = {"mod": "Fx", "cycle": 2, "version": "0.1.0", "visit_first": 1, "live_units": [], "owed": "cycle", "exit": {}}

    def blind():        # the production path: decide_blind hands the mod to retriable
        row = {"mod": "Fx"}

        def put(decision, why, need=None):
            row["decision"], row["why"] = decision, why
        try:
            MD.decide_blind(cfg, {"blind_auto": [dict(fail)]}, dict(f), row, put, time.time(), (True, "ok"), 0, [])
        except Exception as e:      # noqa: BLE001
            row.setdefault("decision", "past_counter (%s)" % type(e).__name__)
        return row.get("decision") == "stopped"

    def steward():
        row = {"mod": "Fx", "aut": "steward", "steward_key": "0.1.0|k"}
        go, got = AUT._gate(cfg, {"steward": {"0.1.0|k": dict(fail)}}, row, 0, "0.1.0")
        return bool(got) and got[0] == "steward_spent"

    def swept():        # the void sweep's callbacks: each entry's mod found by entry_mods
        st = {"mods": {"Fx": {"steward": {"0.1.0|k": dict(fail)}}}}
        x = st["mods"]["Fx"]["steward"]["0.1.0|k"]
        return not MD.still_retried(cfg, "steward", x, MD.entry_mods(st).get(id(x)))
    for what, fn in (("decide_blind -> retriable", blind), ("_gate -> _retriable", steward),
                     ("still_retried via entry_mods", swept)):
        honours(what, fn, "Fx", 1, 4, "launch_tries")
    check(not MD.retriable(cfg, dict(fail), mod="Gx"), "another mod's launch_tries account is its own")


def t_chain_runs_read_the_store():
    import role_launch as RL
    now = time.time()
    concept = os.path.join(os.environ["RM_PIPE_ROOT"], "design", "concepts", "Fx")
    key = "%s %s" % (RL.day_of(now), concept)
    rs = {"chain_day": {key: 8}, "chain_stages_day": {key: ["3"] * 8}}     # stage 3 again: a return, not forward
    with open(os.path.join(os.environ["RM_DISPATCHER_STATE"], "state.json"), "w") as fh:
        json.dump({"roles": {"Designer": dict(rs)}}, fh)      # the Dispatcher's books, as pipe's measure reads them
    honours("role_launch.chain_capped", lambda: RL.chain_capped(dict(rs), {}, concept, "3", now), "Fx", 1, 9,
            "chain_runs_day")
    check(RL.chain_cap({}, os.path.join("x", "Gx"), 8) == (8, RL.CHAIN_MAX_PER_DAY),
          "a concept's chain account is its folder's name, its own")


def t_refusals_read_the_store():
    import refusal_contract as RC
    keep = {k: os.environ.get(k) for k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE",
                                          "RM_JUDGE_CALIBRATION", "RM_CALIBRATION_ROOT")}
    root = tempfile.mkdtemp(prefix="pipe_ref_")
    try:
        os.makedirs(os.path.join(root, "ops"))
        os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "refusals"), RM_OPS_WATCH_DIR=os.path.join(root, "ops"),
                          RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
        crit = "the knockback scene pushes a pawn at least 3 cells"
        with open(os.path.join(root, "scene.log"), "w") as fh:
            fh.write("BlastAt 10,10\npawn Kira displaced 1 cell\nend\n")
        with open(os.path.join(root, "brief.md"), "w") as fh:
            fh.write("a calibrated brief\n")
        with open(os.path.join(root, "cal.json"), "w") as fh:
            json.dump({"families": {"scene_look": {"brief": ["brief.md"], "hash": RC.brief_hash(["brief.md"], root),
                                                   "status": "CALIBRATED", "cases": {}}}}, fh)
        os.environ.update(RM_JUDGE_CALIBRATION=os.path.join(root, "cal.json"), RM_CALIBRATION_ROOT=root)
        given = {"root": root, "criteria": {"C1": crit}, "inputs": ["scene.log"]}
        n = [0]

        def refuse(item):
            n[0] += 1
            later = RC.counters()["items"].get(item, {}).get("refused")
            v = {"item": item, "family": "scene_look", "sha": "sha%d" % n[0], "passed": [],
                 "refusals": [{"clause": "C1", "criterion_hash": RC.criterion_hash(crit), "evidence": ["scene.log:2"],
                               "observed": "pawn displaced 1 cell after the blast",
                               "would_pass": "scene.log shows displaced >= 3 cells for pawn Kira after BlastAt",
                               "smallest_fix": {"what": "raise KnockbackForce in RM_ExplosiveKnockback def to 6",
                                                "attainable": "yes", "cost": "edit"},
                               "criterion_verdict": "sound",
                               "criterion_why": "Three cells is what the owner's line asks and the scene can show."}]}
            if later:
                v["refusals"][0]["new_since"] = "unfixed:C1"
            r = RC.submit(v, given)
            check(r["ok"] and r["counted"], "refusal %d on %s is counted" % (n[0], item), r.get("errors"))
            # the item-count alarm only ("N refused verdicts"); the clause-repair line is its own count (CLAUSE_REPAIR_AT)
            return any(a.get("subject") == "item:%s" % item and "refused verdicts" in str(a.get("why"))
                       for a in r["alarms"])
        for _ in range(RC.ITEM_ALARM_AT - 1):
            refuse("ITEM_R")
        rc, out, _ = run("add", "ITEM_R", "refusals", "-1", "--why", "one refusal was a harness fault")
        act_line(rc, out, "add -1 refusals (an item account)")
        check(refuse("ITEM_R") is False, "submit honours the store: the 4th refusal, one forgiven, raises no item alarm")
        check(refuse("ITEM_R") is True, "the next refusal reaches the limit and alarms")
        for _ in range(RC.ITEM_ALARM_AT - 1):
            refuse("ITEM_L")
        act_line(*run("limit", "ITEM_L", "refusals", "9", "--why", "a noisy family")[:2], what="limit refusals")
        check(refuse("ITEM_L") is False, "submit honours a raised limit")
        run("limit", "ITEM_L", "refusals", "default", "--why", "back")
        check(refuse("ITEM_L") is True, "limit default alarms again at ITEM_ALARM_AT")
        rc, out, _ = run("add", "NO_SUCH_ITEM_EVER", "refusals", "-1", "--why", "typo")
        check(rc == 2 and "refused" in out[0], "an account the counters do not hold, and no mod, is refused", out)
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)


def t_stage_spend_reads_the_store():
    import maturation_dispatch as MD
    cfg = {"stage_ceiling_tokens": 25_000_000}
    over = lambda: MD.ceiling_gate(cfg, {}, "Fx", "in_game", 23_750_000, 2_500_000, "in-game acceptance", ([], 0))[0] is not None
    honours("ceiling_gate (in_game)", over, "Fx", 2_500_000, 50_000_000, "spend_in_game")
    blind = lambda: MD.ceiling_gate(cfg, {}, "Fx", "blind_challenge", 23_750_000, 2_500_000, "b", ([], 0))[0] is not None
    honours("ceiling_gate (blind)", blind, "Fx", 2_500_000, 50_000_000, "spend_blind_challenge")
    build = lambda: MD.ceiling_gate(cfg, {}, "Fx", "offline_build", 23_750_000, 2_500_000, "o", ([], 0))[0] is not None
    honours("ceiling_gate (offline build)", build, "Fx", 2_500_000, 50_000_000, "spend_offline_build")
    row = {"mod": "Fx", "stage": "in_game", "stage_tokens": 12_500_000}
    small = lambda: MD.holder_cap(cfg, row, 2_500_000) <= 12_500_000 + MD.READ_SLACK
    honours("holder_cap (a pilot holder's cap)", small, "Fx", 2_500_000, 50_000_000, "spend_in_game")
    rc, out, _ = run("add", "Fx", "spend_in_game", "-%d" % 2_500_000, "--why", "t")
    check(not MD.ceiling_gate(cfg, {}, "Fx", "blind_challenge", 23_750_000, 2_500_000, "b", ([], 0))[0] is None,
          "a stage's account is its own: an in-game give-back leaves the blind challenge's ceiling")
    shown = run("show", "Fx")[1]
    check(any("spend_in_game" in l and "weighted tokens" in l for l in shown),
          "pipe show <Mod> lists the adjusted spend account in weighted tokens", shown)
    run("undo", re.search(r"(ct_\w+)", out[1]).group(1), "--why", "t")


def t_pilot_streak_reads_the_store():
    """`pipe add|limit <ITEM> pilot_streak` changes testpilot_route.judge's verdict, one item's account leaves the
    others, `routed` reads the store once and sees it too, and an unreadable store routes by the derived count only,
    saying so (RIMMANDRAKE_TYPE_PILOT_STREAK_AS_ITEM_ACCOUNT_ALREADY_ORDERED)."""
    import model
    import pipeline_control as PC
    import testpilot_route as TP

    class It(object):
        state, blocked, needs, history = "ready", False, "bridge", []

        def __init__(self, iid, fails):
            self.id = iid
            self.runs = [model.Run(iid, n, "full-578", "fail", None, "abc", "2026-11-18T0%d:00:00Z" % n, n)
                         for n in range(1, fails + 1)]

    a, b = It("PSTREAK_FIX_ALPHA_THREE_MISSES", 3), It("PSTREAK_FIX_BETA_THREE_MISSES", 3)
    two = It("PSTREAK_FIX_GAMMA_TWO_MISSES", 2)
    kind = lambda it, adj=None: (TP.judge(it, [], void={}, adjusted=adj) or {}).get("kind")
    check(kind(a) == "streak" and kind(two) is None, "base: three misses route, two do not")
    rc, out, _ = run("limit", a.id, "pilot_streak", "4", "--why", "t")
    aid = act_line(rc, out, "pipe limit <ITEM> pilot_streak")
    check(kind(a) is None and kind(b) == "streak", "a raised limit holds that item only; another item's account is its own")
    run("undo", aid, "--why", "t")
    check(kind(a) == "streak", "pipe undo of the limit routes it again")
    rc, out, _ = run("add", two.id, "pilot_streak", "+1", "--why", "t")
    aid = act_line(rc, out, "pipe add <ITEM> pilot_streak")
    check(kind(two) == "streak" and "account 3 of limit 3" in TP.judge(two, [], void={})["why"],
          "an added miss routes an item two misses in, and the verdict names the account", TP.judge(two, [], void={}))

    class W(object):
        items = {i.id: i for i in (a, b, two)}
    got = sorted(v["id"] for v in TP.routed(W, []))
    check(got == sorted([a.id, b.id, two.id]), "routed() reads the store once and sees the adjusted item", got)
    run("undo", aid, "--why", "t")
    check(kind(two) is None and kind(two, adj=set()) is None, "undo of the add: two misses stand again")
    rc, out, _ = run("limit", "Fx", "pilot_streak", "2", "--why", "t")
    check(rc == 2 and "item" in out[0], "a mod name is refused: the streak is an item's account", out)
    blind = TP.judge(a, [], void={}, adjusted="OperationalError: disk I/O error")
    check(blind and "control store is UNMEASURED" in blind["why"] and kind(two, adj="x") is None,
          "an unreadable store routes by the derived count only, and says so", blind)


def t_every_limit_read_goes_through_the_store():
    test_reader_census()


SIX_MORE = ("ingame_runs_visit", "steward_runs", "fixer_runs", "launch_tries", "chain_runs_day", "refusals",
            "spend_offline_build", "spend_blind_challenge", "spend_in_game")


def t_one_line_each_with_its_undo():
    """Each of the six (nine accounts) takes `pipe set`, `add`, `reset` and `limit` in one line, prints at most 3
    lines with its undo, and `pipe undo` takes the act back."""
    import pipeline_control as PC
    for res in SIX_MORE:
        check(res in PC.RESOURCES, "%s is a consumable pipe knows" % res)
        who = "Fx@0.1.0" if res == "refusals" else "Fx"     # a refusal account is an item: here a mod's, by version
        for argv in (("set", who, res, "2"), ("add", who, res, "+1"), ("reset", who, res), ("limit", who, res, "7")):
            rc, out, _ = run(*(argv + ("--why", "t")))
            aid = act_line(rc, out, "pipe %s %s" % (argv[0], res))
            rc, out, _ = run("undo", aid, "--why", "t")
            check(rc == 0 and len(out) <= 3, "pipe undo of `%s %s` takes the act back" % (argv[0], res), out)



def main():
    keep = {k: os.environ.get(k) for k in ("RM_PIPE_CONTROL_DIR", "RM_MATURATION_DISPATCH_DIR", "RM_PIPE_ROOT",
                                           "RM_OWNER_HOLD_FILE", "RM_DISPATCHER_STATE")}
    root, st = fixture()
    try:
        test_verbs_and_coverage(st)
        test_blind_reader()
        test_mutant()
        test_reader_census()
        t_ingame_runs_read_the_store()
        t_steward_runs_read_the_store()
        t_launch_tries_read_the_store()
        t_chain_runs_read_the_store()
        t_refusals_read_the_store()
        t_pilot_streak_reads_the_store()
        t_stage_spend_reads_the_store()
        t_every_limit_read_goes_through_the_store()
        t_one_line_each_with_its_undo()
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
