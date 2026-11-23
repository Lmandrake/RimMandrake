#!/usr/bin/env python3
"""selftest_repair_at_refusal.py — a fault of form is repaired where it is found; the fault loop counts substance only.

    python3 src/RimMandrake/rimflow/selftest_repair_at_refusal.py

Page: design/specs/2026-11-21-repair-at-the-refusal/boundary.md (each promise is a t_<name> below).
Item RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES. The refusal texts below are the night of 2026-11-20's,
as the dispatch state recorded them (mods.<Mod>.system_faults).
Exit 0 when every check passes; 1 otherwise (each failure named).
"""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import form_fault as FF             # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import run_void as RV               # noqa: E402

FAILS = []
NOW = 1795300000.0


def check(ok, line):
    print("%s  %s" % ("PASS" if ok else "FAIL", line))
    if not ok:
        FAILS.append(line)


# ---- the night's refusals (2026-11-20), as recorded ---------------------------------------------------------------
DRAIN = ("refused: the account system is draining (switching plan notice since 2026-11-20T18:00:00-08:00): live runs "
         "finish on it and no new run starts until the switch. Launch again after it (`python3 "
         "src/RimMandrake/Utils/switching_plan.py status` shows it). Why: system at 3.0% is at or under its 3% line")
VISIT_CHECK = ("filed RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO; publish: pushed; REFUSED: Pyrelands's in-game visit 2 "
               "would play a game copy not checked against the repo: the game's copy of Pyrelands differs from the "
               "repo's (1 developer script of another mod, 9 unused textures)")
VISIT_NAME = ("spawn refused: RUNNER spawns only for BENCH or FOUNDRY with needs offline or for OWNER with needs owner "
              "(the steward's escalations), or the maturation dispatch's in-game visit for BENCH with needs game "
              "(RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT is not such a name)")
LOCK_FILE = ("RuntimeError: land.sh exited 1: The following paths are ignored by one of your .gitignore files:\n"
             "design/concepts/FlowWorks/.stage_move.lock\nhint: Use -f if you really want to add them.")
LONG_NAME = ("spawn refused: RIMMANDRAKE_ROUTE_GIMMESOMESLACK_VISIT_ONE_FAILURES_BACK_RUN_THREE is not a new-style item "
             "name:\n  - 66 chars; too long, the cap is 64\n\nNew items are PROJECT_VERB_INTENTION_TWIST (owner")
CARD_PASTE = ("road-back item filed by the steward; refused: RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN was "
              "decided by card, and the brief does not carry the picked option's description verbatim: |   «What")
LAUNCH_REFUSALS = {"1-drain": ("fixers", DRAIN), "2-visit-check": ("ingame_auto", VISIT_CHECK),
                   "3-visit-name": ("ingame_auto", VISIT_NAME), "4-lock-file": ("steward", LOCK_FILE),
                   "5-long-name": ("steward", LONG_NAME), "6-card-paste": ("fixers", CARD_PASTE)}


def never_started(book, text, tries=3):
    x = {"item": "RIMMANDRAKE_SOME_ITEM", "unit": None, "at": NOW - 60, "failed": text, "tries": tries}
    if AUT.wait_refusal(text):
        x["wait"] = True
    return x


def state_with(book, x):
    s = {}
    if book in ("steward", "fixers"):
        s[book] = {"k1": x}
    else:
        s[book] = [x]
    return {"mods": {"FakeFlow": s}}, s


def sync(st):
    cfg = {"launch_tries": 3, "_code": "c1", "seat": "BENCH"}
    RV.sync_system(st, lambda u: None, keep_failed=lambda b, x: MD.still_retried(cfg, b, x, "FakeFlow"), now=NOW)


# ---- the mechanism ------------------------------------------------------------------------------------------------

def t_form_note_repairs_and_continues():
    buf, ev = io.StringIO(), {}
    n = FF.repaired("the item name was 66 chars", "cut to RIMMANDRAKE_X_Y_Z", event=ev, stream=buf)
    line = buf.getvalue()
    check(line.startswith(FF.NOTE_HEAD) and line.count("\n") == 1 and ev.get("form_notes") == [n]
          and n == {"what": "the item name was 66 chars", "how": "cut to RIMMANDRAKE_X_Y_Z"},
          "form-note-repairs-and-continues: one NOTE line (%r), the note on the event (%s)" % (line[:60], ev))


def t_form_refusal_names_its_repair():
    t = FF.refusal("the brief does not carry the card text", "add the card's words: card_capture.py show X")
    try:
        FF.refusal("no repair given", "  ")
        raised = False
    except ValueError:
        raised = True
    check(FF.FORM_HEAD + "the brief" in t and FF.repair_of(t) == "add the card's words: card_capture.py show X"
          and raised and FF.fault_class(t) == "form",
          "form-refusal-names-its-repair: head, REPAIR line read back, an empty repair raises (%s)" % raised)


def t_every_brief_carries_the_repair_line():
    import detached_helper as DH
    import role_launch as RL
    foot = DH.FOOTER.format(clone="/c", item="SOME_ITEM_X", seat="BENCH", bound_text="no wall-time bound")
    role = {"clone": "/nonexistent/clone", "model": "opus", "name": "designer", "seat": "BENCH"}
    try:
        argv = RL.launch_argv(role, "rm-role-x", "do the work", "/tmp/o", "/tmp/e", "/usr/bin/claude")
        msg = argv[argv.index("-p", argv.index("--")) + 1] if "-p" in argv[argv.index("--"):] else ""
    except Exception as e:      # noqa: BLE001
        msg = "launch_argv raised %s" % e
    check(FF.BRIEF_LINE in foot and FF.BRIEF_LINE.strip() in msg,
          "every-brief-carries-the-repair-line: the detached footer %s, a role run's message %s" % (
              FF.BRIEF_LINE in foot, FF.BRIEF_LINE.strip() in msg))


def t_a_launch_that_never_started_is_form():
    texts = {"machine": "LAUNCH FAILED rm-detached-x: pool full",
             "lock-outlasted": "refused: X is not on origin/main; publish infrastructure/state/ledger/events/RUNNER.jsonl",
             "anything": "REFUSED: a rule said no", "no-text-holder": None}
    out = {}
    for k, text in texts.items():
        book = "holder_road_back" if text is None else "steward"
        st, s = state_with(book, never_started(book, text))
        sync(st)
        out[k] = (RV.faults(s), len([r for r in s.get("form_repairs") or [] if r.get("state") == "owed"]))
    ctl = FF.fault_class("REFUSED rm-detached-x by control: pipe off FlowWorks")
    check(out == {k: (0, 1) for k in texts} and ctl == "wait" and FF.fault_class(DRAIN) == "wait",
          "a-launch-that-never-started-is-form: (faults, repairs owed) %s; a control stop %s" % (out, ctl))


def t_a_repair_launch_refused_names_the_conductor():
    st, s = state_with("steward", never_started("steward", LOCK_FILE))
    sync(st)
    fx = {"repair_launch": lambda *a, **k: (False, "LAUNCH FAILED rm-x: pool full", None),
          "record": lambda u: None, "live": lambda r: "running"}
    rows = None
    for _ in range(MD.REPAIR_LAUNCH_MOST + 1):
        rows = [{"mod": "FakeFlow", "decision": "launch", "why": "owed"}]
        MD.form_repair_step("/nonexistent", {}, st, rows, ["FakeFlow"], NOW, True, fx)
    check(rows[0]["decision"] == "repairing" and "Conductor" in (rows[0].get("need") or "") and RV.faults(s) == 0,
          "a-repair-launch-refused-names-the-conductor: after %d refused repair launches: %s / %s" % (
              MD.REPAIR_LAUNCH_MOST, rows[0]["decision"], (rows[0].get("need") or "-")[:90]))


def t_the_launch_refusals_count_no_fault():
    out = {}
    for case, (book, text) in sorted(LAUNCH_REFUSALS.items()):
        st, s = state_with(book, never_started(book, text))
        sync(st)
        st2 = json.loads(json.dumps(st))
        rows = [{"mod": "FakeFlow", "decision": "launch", "why": "owed"}]
        la = MD.system_fault_stop({}, st2, rows, ["FakeFlow"])
        owed = [r for r in s.get("form_repairs") or [] if r.get("state") == "owed"]
        out[case] = (RV.faults(s), rows[0]["decision"], len(owed))
    # the drain is a wait; the tick's own bad name is re-made by the tick's namer on the next tick (a wait), so neither
    # owes a repair run
    want = {c: (0, "launch", 0 if c in ("1-drain", "5-long-name") else 1) for c in LAUNCH_REFUSALS}
    check(out == want, "the-launch-refusals-count-no-fault: (faults, decision, repairs owed) per case: %s" % out)


def t_a_dead_run_still_counts_one():
    st = {"mods": {"FakeFlow": {"ingame_auto": [{"item": "I", "unit": "rm-detached-x", "at": NOW - 600}]}}}
    s = st["mods"]["FakeFlow"]
    rec = {"status": "finished", "result": "killed", "exit_status": "KILL", "rc": None}
    RV.sync_system(st, lambda u: rec if u == "rm-detached-x" else None, now=NOW)
    check(RV.faults(s) == 1 and not s.get("form_repairs"),
          "a-dead-run-still-counts-one: a killed run counts %d fault(s), owes %d repair(s)" % (
              RV.faults(s), len(s.get("form_repairs") or [])))


def _tick_repair(st, rows, launches, apply=True, record=None, launched=None):
    calls = launched if launched is not None else []

    def rl(root, cfg, mod, recs, kind="form"):
        calls.append((mod, kind, [r.get("what") for r in recs]))
        return True, "DETACHED rm-detached-repair-%d" % len(calls), "rm-detached-repair-%d" % len(calls)
    fx = {"repair_launch": rl, "record": record or (lambda u: {"status": "running"}), "live": lambda rec: "running"}
    MD.repair_sync(st, NOW, fx)
    la = MD.form_repair_step("/nonexistent", {}, st, rows, launches, NOW, apply, fx)
    return la, calls


def t_form_refusal_is_repaired_not_resent():
    st, s = state_with("steward", never_started("steward", LOCK_FILE))
    sync(st)
    rows = [{"mod": "FakeFlow", "decision": "launch", "why": "steward owed"}]
    la, calls = _tick_repair(st, rows, ["FakeFlow"])
    first = (la, rows[0]["decision"], rows[0].get("why", "")[:40], len(calls))
    rows = [{"mod": "FakeFlow", "decision": "launch", "why": "steward owed"}]
    la2, _ = _tick_repair(st, rows, ["FakeFlow"], launched=calls)
    second = (la2, rows[0]["decision"], len(calls))
    rows = [{"mod": "FakeFlow", "decision": "launch", "why": "steward owed"}]
    la3, _ = _tick_repair(st, rows, ["FakeFlow"], record=lambda u: {"status": "finished"}, launched=calls)
    third = (la3, rows[0]["decision"], len(calls))
    check(first[0] == [] and first[1] == "repairing" and first[2].startswith("repairing: ") and first[3] == 1
          and second == ([], "repairing", 1) and third == (["FakeFlow"], "launch", 1),
          "form-refusal-is-repaired-not-resent: tick 1 %s; tick 2 (repair live) %s; tick 3 (repair ended) %s" % (
              first, second, third))


def t_a_repair_that_did_not_hold_counts_once():
    st, s = state_with("steward", never_started("steward", LOCK_FILE))
    sync(st)
    _tick_repair(st, [{"mod": "FakeFlow", "decision": "launch"}], ["FakeFlow"])
    _tick_repair(st, [{"mod": "FakeFlow", "decision": "launch"}], ["FakeFlow"], record=lambda u: {"status": "finished"})
    s["steward"] = {"k1": never_started("steward", LOCK_FILE.replace("stage_move", "stage_move"))}
    sync(st)
    causes = [f.get("cause") for f in s.get("system_faults") or []]
    check(RV.faults(s) == 1 and causes and "did not hold" in causes[-1],
          "a-repair-that-did-not-hold-counts-once: faults %d, cause %s" % (RV.faults(s), (causes or ["-"])[-1][:80]))


def t_the_trip_starts_a_repair():
    s = {"system_faults": [{"at": NOW - 30 * i, "book": "launches", "unit": "rm-u%d" % i, "cause": "it timed out",
                            "n": 1} for i in range(3)]}
    st = {"mods": {"FakeFlow": s}}
    calls = []

    def rl(root, cfg, mod, recs, kind="form"):
        calls.append(kind)
        return True, "DETACHED rm-fix-%d" % len(calls), "rm-fix-%d" % len(calls)

    def tick(rec):
        fx = {"repair_launch": rl, "record": rec, "live": lambda r: "running"}
        MD.repair_sync(st, NOW, fx)
        rows = [{"mod": "FakeFlow", "decision": "launch", "why": "owed"}]
        la = MD.system_fault_stop({}, st, rows, ["FakeFlow"])
        MD.fault_repair_step("/nonexistent", {}, st, rows, NOW, True, fx)
        return la, rows[0]
    la1, r1 = tick(lambda u: {"status": "running"})
    la2, r2 = tick(lambda u: {"status": "finished"})     # the repair run ended: the count resets by itself
    a = (la1, r1["decision"], "repairing" in r1.get("why", ""), calls[:], RV.faults(s))
    s["system_faults"] += [{"at": NOW + 10 + i, "book": "launches", "unit": "rm-v%d" % i, "cause": "it timed out",
                            "n": 1} for i in range(3)]
    la3, r3 = tick(lambda u: {"status": "finished"})
    la4, r4 = tick(lambda u: {"status": "finished"})
    b = (la3, r3["decision"], calls[:], "Conductor" in (r4.get("need") or ""), len(calls))
    check(a == ([], "system_fault", True, ["fault"], 0) and b[0] == [] and b[1] == "system_fault"
          and b[2] == ["fault", "fault"] and b[3] and b[4] == 2,
          "the-trip-starts-a-repair: first trip %s; second trip %s" % (a, b))


def t_a_tick_with_stand_ins_launches_nothing_real():
    st, s = state_with("steward", never_started("steward", LOCK_FILE))
    sync(st)
    rows = [{"mod": "FakeFlow", "decision": "launch", "why": "owed"}]
    fx = {"record": lambda u: None, "live": lambda r: "running", "file": lambda *a, **k: (False, "stand-in")}
    la = MD.form_repair_step("/nonexistent", {}, st, rows, ["FakeFlow"], NOW, True, fx)
    check(MD.repair_launcher(fx) is None and MD.repair_launcher({}) is MD.repair_launch and la == []
          and rows[0]["decision"] == "repairing" and FF.open_repair(s).get("state") == "owed",
          "a-tick-with-stand-ins-launches-nothing-real: no repair launcher in the fixtures means none is run (%s)" % (
              rows[0].get("why", "")[:80]))


def t_a_refused_repair_launch_reuses_its_filed_item():
    st, s = state_with("steward", never_started("steward", LOCK_FILE))
    sync(st)
    calls = []

    def rl(root, cfg, mod, recs, kind="form", item=None):
        calls.append(item)
        if len(calls) == 1:
            return False, ("filed RIMMANDRAKE_REPAIR_FAKEFLOW_FORM_REFUSAL_AT_THE_GATE; publish: publish stopped: fetch "
                           "failed"), None
        return True, "DETACHED rm-detached-repair-x", "rm-detached-repair-x"
    fx = {"repair_launch": rl, "record": lambda u: {"status": "running"}, "live": lambda r: "running"}
    for _ in range(2):
        MD.form_repair_step("/nonexistent", {}, st, [{"mod": "FakeFlow", "decision": "launch"}], ["FakeFlow"], NOW,
                            True, fx)
    check(calls == [None, "RIMMANDRAKE_REPAIR_FAKEFLOW_FORM_REFUSAL_AT_THE_GATE"],
          "a-refused-repair-launch-reuses-its-filed-item: the retry launches the item the first try filed (%s)" % calls)


def t_repairing_is_a_named_wait_never_paused():
    # measured live 2026-11-21 02:28-02:38 PST: GimmeSomeSlack read `repairing` with class `paused` (a pause alarm's
    # class) while the tick's own repair run worked on it
    st = {"mods": {"FakeFlow": {}}}
    row = {"mod": "FakeFlow", "decision": "repairing", "why": "repairing: x (repair run rm-detached-repair-x)",
           "repairing": "repairing: x (repair run rm-detached-repair-x)"}
    AUT.classify({}, st, [row], NOW)
    check(row.get("klass") == "wait" and "repairing" in str(row.get("waits_on")),
          "repairing-is-a-named-wait-never-paused: class %s, waits_on %s" % (row.get("klass"), row.get("waits_on")))


# scratch_clone.pool_admit's two refusals, as a launch or a rerun's result carries them (Pyrelands, 2026-11-22 3:34 PM PST)
POOL_FULL = ("RuntimeError: scratch_clone failed (exit 1): scratch_clone: FAILED: POOL REFUSED: pool full: 16 clones, "
             "cap 16 (no idle clone to reuse); finish or push one, then retry")
POOL_GB = "RuntimeError: scratch_clone failed (exit 1): scratch_clone: FAILED: POOL REFUSED: pool at 106.88 GB, cap 80 GB"
CERT = {"rows": [{"test": "T_A", "status": "REFUSED", "clause": "ran_on_this_build", "would_pass": "build b"}]}


def t_a_pool_refusal_is_a_wait():
    got = (FF.fault_class(POOL_FULL), FF.fault_class(POOL_GB), FF.fault_class(LOCK_FILE))
    check(got == ("wait", "wait", "form"), "a-pool-refusal-is-a-wait: full, over its GB line, a lock file: %s" % (got,))


def t_a_pool_refused_repair_launch_spends_no_try():
    st, s = state_with("steward", never_started("steward", LOCK_FILE))
    sync(st)
    fx = {"repair_launch": lambda *a, **k: (False, "retry of X, filed earlier; publish: pushed; clone failed: " + POOL_FULL,
                                            None), "record": lambda u: None, "live": lambda r: "running"}
    rows = None
    for _ in range(MD.REPAIR_LAUNCH_MOST + 1):
        rows = [{"mod": "FakeFlow", "decision": "launch", "why": "owed"}]
        MD.form_repair_step("/nonexistent", {}, st, rows, ["FakeFlow"], NOW, True, fx)
    rep = FF.open_repair(s) or {}
    check(rows[0]["decision"] == "repairing" and not rows[0].get("need") and not rep.get("repair_tries"),
          "a-pool-refused-repair-launch-spends-no-try: after %d pool refusals: %s, need %s, tries %s" % (
              MD.REPAIR_LAUNCH_MOST + 1, rows[0]["decision"], rows[0].get("need"), rep.get("repair_tries")))


def t_an_owed_pool_refusal_owes_no_repair():
    text = ("Pyrelands: in-game visit 6: waiting on its certificate; the zero-token certificate rerun rm-cert-rerun-x on "
            "this build ended (ok None, published nothing, error: %s); the step never reruns the same build" % POOL_FULL)
    st = {"mods": {"FakeFlow": {}}}
    FF.owe_repair(st["mods"]["FakeFlow"], text, "FakeFlow certificate", NOW, book="cert_rerun", key="k")
    calls = []
    fx = {"repair_launch": lambda *a, **k: (calls.append(a), (True, "DETACHED rm-r", "rm-r"))[1],
          "record": lambda u: None, "live": lambda r: "running"}
    rows = [{"mod": "FakeFlow", "decision": "launch", "why": "owed"}]
    la = MD.form_repair_step("/nonexistent", {}, st, rows, ["FakeFlow"], NOW, True, fx)
    check(la == ["FakeFlow"] and not calls and FF.open_repair(st["mods"]["FakeFlow"]) is None,
          "an-owed-pool-refusal-owes-no-repair: launches %s, repair launches %d, open %s" % (
              la, len(calls), FF.open_repair(st["mods"]["FakeFlow"])))


def t_a_pool_refused_cert_rerun_starts_again():
    key = MD.stale_key(CERT)
    for err in (POOL_FULL, POOL_GB):
        s = {"cert_rerun": {"key": key, "unit": "rm-cert-rerun-x", "at": NOW - 60, "failed": None, "tries": 1}}
        f = {"certificate": CERT, "cert_rerun_result": {"unit": "rm-cert-rerun-x", "ok": None, "published": None,
                                                         "key_after": None, "error": err}}
        row, put = {"mod": "FakeFlow"}, []
        got = MD.cert_rerun_decide({}, s, f, row, lambda d, w, need=None: put.append(d), NOW)
        st = {"mods": {"FakeFlow": s}}
        up = MD.cert_rerun_launch({}, st, row, NOW, {"cert_rerun": lambda m, k: (0, "STARTED rm-cert-rerun-y",
                                                                                "rm-cert-rerun-y")}) if got == "launch" else None
        check(got == "launch" and row.get("cert_rerun_key") == key and not s.get("form_repairs") and up
              and s["cert_rerun"].get("tries") == 1,
              "a-pool-refused-cert-rerun-starts-again: %s -> %s, owed %d, tries %s" % (
                  err[-40:], got, len(s.get("form_repairs") or []), s["cert_rerun"].get("tries")))


def t_a_raced_cert_rerun_publish_starts_again():
    """Pyrelands, 2026-11-22 4:19 PM PST: the rerun ran 17 deciders green, then its publish met a newer test_table.json
    on origin (a testq-blocks commit landed during its 449 s) and stopped on a conflict. The worker drops its own stamp
    commit (the clone has one owner and the table is derived) and the tick starts the rerun again, no try, no repair."""
    import types
    mod = "FakeFlow"
    rel = "design/concepts/%s/version/test_table.json" % mod
    conflict = ("REFUSED: replaying 45656f037753 onto origin/main stopped on a conflict in: %s. Your commit is intact "
                "on HEAD; this clone has one owner, so merge it by hand, then re-run ./publish" % rel)
    calls = []

    def runner(argv, cwd=None, **kw):
        calls.append(list(argv))
        if "certificate" in argv:
            return types.SimpleNamespace(returncode=0, stdout=json.dumps({"ok": True, "rows": [], "run": {}}), stderr="")
        if argv[:2] == ["git", "status"]:
            return types.SimpleNamespace(returncode=0, stdout=" M %s\n" % rel, stderr="")
        if argv[0] == "./publish":
            return types.SimpleNamespace(returncode=2, stdout="tree checks: 19 green\n" + conflict, stderr="")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    d = tempfile.mkdtemp(prefix="rerunrace_")
    old = MD.rerun_dir
    MD.rerun_dir = lambda: d
    try:
        res = MD.cert_rerun_worker(mod, "k", "rm-cert-rerun-x", runner=runner, take=lambda item: (d, "made"),
                                   now=lambda: NOW)
    finally:
        MD.rerun_dir = old
    dropped = ["git", "reset", "--hard", "origin/main"] in calls
    check(res.get("race") and dropped and not res.get("published"),
          "a-raced-cert-rerun-publish-starts-again: the worker reads a race %s and drops its commit %s" % (
              res.get("race"), dropped))
    # must stay a hand merge: a conflict in any other file drops nothing
    conflict = conflict.replace(rel, "src/RimMandrake/rimflow/cli.py")
    calls.clear()
    MD.rerun_dir = lambda: d
    try:
        other = MD.cert_rerun_worker(mod, "k", "rm-cert-rerun-x", runner=runner, take=lambda item: (d, "made"),
                                     now=lambda: NOW)
    finally:
        MD.rerun_dir = old
    check(not other.get("race") and ["git", "reset", "--hard", "origin/main"] not in calls
          and "publish exit" in str(other.get("error")),
          "a-raced-cert-rerun-publish-starts-again: a conflict in another file is no race and drops nothing (%s)" %
          str(other.get("error"))[:60])
    key = MD.stale_key(CERT)
    s = {"cert_rerun": {"key": key, "unit": "rm-cert-rerun-x", "at": NOW - 600, "failed": None, "tries": 1}}
    f = {"certificate": CERT, "cert_rerun_result": dict(res, key=key, unit="rm-cert-rerun-x")}
    row = {"mod": mod}
    got = MD.cert_rerun_decide({}, s, f, row, lambda dd, w, need=None: None, NOW)
    check(got == "launch" and not s.get("form_repairs") and row.get("cert_rerun_wait"),
          "a-raced-cert-rerun-publish-starts-again: the tick starts it again (%s), owes %d repair(s)" % (
              got, len(s.get("form_repairs") or [])))
    # a result written before the worker read races (no `race` field) is read by its conflict text on the table
    s = {"cert_rerun": {"key": key, "unit": "rm-cert-rerun-x", "at": NOW - 600, "failed": None, "tries": 1}}
    f = {"certificate": CERT, "cert_rerun_result": {"unit": "rm-cert-rerun-x", "ok": False, "published": None,
                                                     "error": "publish exit 2: tree checks green\n" + conflict.replace(
                                                         "src/RimMandrake/rimflow/cli.py", rel)}}
    row = {"mod": mod}
    got = MD.cert_rerun_decide({}, s, f, row, lambda dd, w, need=None: None, NOW)
    check(got == "launch" and not s.get("form_repairs"),
          "a-raced-cert-rerun-publish-starts-again: an older result's conflict text starts it again (%s)" % got)


def main():
    for t in (t_form_note_repairs_and_continues, t_form_refusal_names_its_repair, t_every_brief_carries_the_repair_line,
              t_a_launch_that_never_started_is_form, t_a_repair_launch_refused_names_the_conductor,
              t_the_launch_refusals_count_no_fault, t_a_dead_run_still_counts_one,
              t_form_refusal_is_repaired_not_resent, t_a_repair_that_did_not_hold_counts_once,
              t_the_trip_starts_a_repair, t_a_tick_with_stand_ins_launches_nothing_real,
              t_a_refused_repair_launch_reuses_its_filed_item, t_repairing_is_a_named_wait_never_paused,
              t_a_pool_refusal_is_a_wait, t_a_pool_refused_repair_launch_spends_no_try,
              t_an_owed_pool_refusal_owes_no_repair, t_a_pool_refused_cert_rerun_starts_again,
              t_a_raced_cert_rerun_publish_starts_again):
        try:
            t()
        except Exception as e:      # noqa: BLE001  one test's crash is that test's FAIL
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
