#!/usr/bin/env python3
"""selftest_maturation_autonomy_review_findings.py - one case per finding of the 2026-11-17 Codex review of
maturation_autonomy.py (parent RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS; raw
/mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_ma_0.txt, r_ma_1.txt), each named after the child that fixes it. Every
case failed on the base it was written against. Hermetic: temp dirs only; every land, launch and ledger call is a
fake, so no git, systemd or Dispatcher state is touched."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402
import maturation_autonomy as MA  # noqa: E402
import maturation_dispatch as MD  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


class patched:
    """Set attributes for the length of a with-block, then put the originals back."""
    def __init__(self, *triples):
        self.triples, self.was = triples, []

    def __enter__(self):
        for obj, name, val in self.triples:
            self.was.append((obj, name, getattr(obj, name)))
            setattr(obj, name, val)

    def __exit__(self, *a):
        for obj, name, val in reversed(self.was):
            setattr(obj, name, val)


def seed_timeout_leaves_no_record(tmp):
    """RIMMANDRAKE_CLEAN_SEED_RECORD_WHEN_LANDING_TIMES_OUT (finding 1)."""
    root = os.path.join(tmp, "seed")
    rec = os.path.join(M.mod_dir(root, "A"), M.RECORD)

    def seed(root_, mod, **k):
        os.makedirs(os.path.dirname(rec), exist_ok=True)
        with open(rec, "w") as f:
            f.write("{}\n")
        return {}, True
    real_run = subprocess.run

    def run(argv, *a, **k):
        if argv and str(argv[0]).endswith("land.sh"):
            raise subprocess.TimeoutExpired(argv, k.get("timeout"))
        return real_run(argv, *a, **k)
    with patched((M, "seed_mod", seed), (MA.subprocess, "run", run)):
        try:
            MA.seed_and_land(root, "A")
            raised = None
        except Exception as e:  # noqa: BLE001
            raised = e
    check("seed: a landing that times out raises (the tick books it as refused)", raised is not None, raised)
    check("seed: a landing that times out leaves no local record, so the next tick seeds again",
          not os.path.exists(rec), os.path.exists(rec))


def autolock_failure_before_landing_rolls_back(tmp):
    """RIMMANDRAKE_ROLL_BACK_AUTOLOCK_WHEN_RECORD_DIR_FAILS (finding 2)."""
    root = os.path.join(tmp, "lock")
    os.makedirs(M.mod_dir(root, "B"))
    os.makedirs(os.path.join(root, "infrastructure", "state"))
    with open(os.path.join(root, "infrastructure", "state", "delegated"), "w") as f:
        f.write("a file where the delegated folder should be\n")      # makedirs of the record's folder fails
    landed = []
    try:
        MA.autolock_and_land(root, "B", now=1.8e9, land=lambda subj, paths: landed.append(paths) or "PUBLISHED x")
        raised = None
    except Exception as e:  # noqa: BLE001
        raised = e
    vpath = os.path.join(M.mod_dir(root, "B"), "version", "VERSION.json")
    check("autolock: a failure writing the delegated record raises", raised is not None and not landed, (raised, landed))
    check("autolock: a failure writing the delegated record leaves no VERSION.json locked behind",
          not os.path.exists(vpath) and not MA.version_locked(root, "B"),
          (os.path.exists(vpath), MA.version_locked(root, "B")))


def road_back_retries_transient_fixer(tmp):
    """RIMMANDRAKE_RETRY_ROAD_BACK_FIXER_AFTER_TRANSIENT_LAUNCH_FAIL (finding 3)."""
    s = {"road_back": {"caused_by": "STEW_ITEM", "at": 1}, "steward": {},
         "fixers": {"FIX_ITEM": {"item": "FIX_ITEM", "unit": None, "failed": "fatal: index.lock exists", "tries": 1}}}
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s, row, lambda ids: [{"id": "FIX_ITEM", "needs": "offline"}])
    check("road back: a fixer whose launch failed on a transient fault is routed to the gate again, not spent",
          row.get("decision") == "fixer" and row.get("fix_item") == "FIX_ITEM", row)
    # Codex review of the fix: an exhausted failure first in line must not starve an untried item behind it
    s2 = {"road_back": {"caused_by": "STEW_ITEM", "at": 1}, "steward": {},
          "fixers": {"A_ITEM": {"item": "A_ITEM", "unit": None, "failed": "fatal: index.lock exists", "tries": 3}}}
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s2, row, lambda ids: [{"id": "A_ITEM", "needs": "offline"}, {"id": "B_ITEM", "needs": "offline"}])
    check("road back: an untried item goes before one whose failed launches may be spent",
          row.get("decision") == "fixer" and row.get("fix_item") == "B_ITEM", row)
    go, why = MA._gate({"fix_cap_tokens": 1_250_000, "max_live": 2, "launch_tries": 3}, s2,
                       {"mod": "C", "aut": "fixer", "fix_item": "A_ITEM"}, 0, "0.1.0")
    check("road back: the gate calls a three-times-failed transient launch spent", go is False and why[0] == "fixer_spent",
          (go, why))
    s["fixers"]["FIX_ITEM"].update(failed="fatal: index.lock exists")
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s, row, lambda ids: [{"id": "FIX_ITEM", "needs": "offline"}])
    go, why = MA._gate({"fix_cap_tokens": 1_250_000, "max_live": 2, "launch_tries": 3}, s, dict(row, aut="fixer"), 0, "0.1.0")
    check("road back: a once-failed transient fixer launch is let through the gate again", go is True, (go, why))
    s["fixers"]["FIX_ITEM"].update(unit="rm-unit-1", failed=None)
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s, row, lambda ids: [{"id": "FIX_ITEM", "needs": "offline"}])
    check("road back: a fixer that ran is still spent", row.get("decision") == "fixer_spent", row)


def _fixer_row():
    return {"mod": "D", "aut": "fixer", "fix_item": "FIX_D", "stage": "blind_challenge", "cap": 5}


def ledger_after_failure_keeps_the_run(tmp):
    """RIMMANDRAKE_KEEP_LAUNCHED_UNIT_WHEN_LEDGER_AFTER_FAILS (finding 4)."""
    st = {"mods": {"D": {}}}

    def after(*a, **k):
        raise RuntimeError("land_ledger refused")
    fx = {"launch_brief": lambda item, brief, model, cap, seat, env=None: (0, "started", "rm-unit-d"),
          "known": lambda: set(), "file": None, "publish": None}
    with patched((MD, "pilot_ledger", lambda root, mod: True),
                 (MD, "ledger_open", lambda root, mod, role, brief, stage=None, now=None: {"brief": brief, "env": {}}),
                 (MD, "ledger_after", after), (M, "game_takeable", lambda stage: False)):
        row = _fixer_row()
        MA.execute(tmp, {}, st, [row], {"D"}, 1.8e9, fx=fx)
    e = st["mods"]["D"].get("fixers", {}).get("FIX_D") or {}
    check("ledger_after: a run that started keeps its unit when the ledger step after it fails",
          e.get("unit") == "rm-unit-d" and not e.get("failed") and row.get("decision") == "launched", (e, row))


def launch_exception_books_code(tmp):
    """RIMMANDRAKE_BOOK_CODE_ON_LAUNCH_EXCEPTION_FRESH_FIX_SEEN (finding 5)."""
    st = {"mods": {"D": {}}}

    def boom(*a, **k):
        raise ValueError("brief template broken")
    fx = {"launch_brief": boom, "known": lambda: set(), "file": None, "publish": None}
    with patched((MD, "pilot_ledger", lambda root, mod: False), (M, "game_takeable", lambda stage: False)):
        MA.execute(tmp, {"_code": "code-v1"}, st, [_fixer_row()], {"D"}, 1.8e9, fx=fx)
    e = st["mods"]["D"].get("fixers", {}).get("FIX_D") or {}
    check("launch exception: the book entry carries the code it failed on", e.get("code") == "code-v1", e)
    row = dict(_fixer_row())
    go, why = MA._gate({"_code": "code-v2", "fix_cap_tokens": 1_250_000, "max_live": 2}, st["mods"]["D"], row, 0, "0.1.0")
    check("launch exception: once the code changed, the gate tries it again", go is True, (go, why))


# ---- the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt),
# its pre-existing findings 2-8, each watched failing on 36915f0974 first

def _blocked_dst():
    return {"status": "blocked", "history": [{"what": "coverage_stop", "at": "2026-11-18T00:00:00Z", "why": "stop"}]}


def hold_beats_coverage_stop(tmp):
    """RIMMANDRAKE_KEEP_CONDUCTOR_HOLD_ABOVE_COVERAGE_STOP_FIXERS (review item 2)."""
    st = {"mods": {}}
    rows = [{"mod": "H", "decision": "held", "stage": "blind_challenge", "why": "Conductor hold"}]
    fx = {"designer_state": lambda m: _blocked_dst(), "stop_tickets": lambda m, dst, s: [{"id": "T_H"}],
          "ticket_runs": lambda i: [], "ledger_items": lambda: [], "open_items": lambda ids: [],
          "version_locked": lambda m: True, "version_evidence": lambda m: {}}
    rows, launches = MA.resolve(tmp, {"fix_cap_tokens": 1_250_000, "max_live": 2}, st, {"H": {"live_units": []}}, rows, [], 1.8e9,
                                fx=fx)
    check("hold: a Conductor hold is never routed to a fix-ticket fixer by a coverage stop",
          rows[0].get("decision") == "held" and "H" not in launches, (rows[0].get("decision"), launches))


def stop_tickets_retry_failed_launch(tmp):
    """RIMMANDRAKE_RETRY_FAILED_FIX_TICKET_LAUNCH_WHILE_PAUSED (review item 3)."""
    for tickets, want in (([{"id": "T1"}], "T1"), ([{"id": "T1"}, {"id": "T2"}], "T2")):
        s = {"fixers": {"T1": {"item": "T1", "unit": None, "failed": "fatal: index.lock exists", "tries": 1}}}
        row = {"mod": "P", "stage": "blind_challenge"}
        MA._stop_tickets({"stop_tickets": lambda m, dst, s_, t=tickets: t, "ticket_runs": lambda i: []}, row, s,
                         _blocked_dst(), 1.8e9)
        check("paused fixers: with tickets %s the next run is %s (untried first, a failed launch is not spent)" % (
            [t["id"] for t in tickets], want), row.get("decision") == "fixer" and row.get("fix_item") == want, row)


def _steward_row():
    return {"mod": "S", "aut": "steward", "steward_key": "S|k", "steward_kind": "exit_not_met", "stage": "blind_challenge",
            "cap": 5, "why": "w"}


def filed_item_kept_on_failure(tmp):
    """RIMMANDRAKE_KEEP_FILED_STEWARD_ITEM_ACROSS_LAUNCH_FAILURES (review item 4)."""
    st = {"mods": {"S": {}}}

    def boom(*a, **k):
        raise ValueError("brief template broken")
    fx = {"launch_brief": boom, "known": lambda: set(), "file": lambda item, title, why, **k: (True, "filed %s" % item),
          "publish": None}
    with patched((MD, "pilot_ledger", lambda root, mod: False), (MA, "steward_brief", lambda root, mod, row: "brief")):
        MA.execute(tmp, {"_code": "c1"}, st, [_steward_row()], {"S"}, 1.8e9, fx=fx)
    e = st["mods"]["S"]["steward"].get("S|k") or {}
    check("filed: a launch that raises after filing keeps the filed item and filed=True",
          e.get("item") and e.get("filed") is True, e)
    st2 = {"mods": {"S": {"steward": {"S|k": {"item": "S_ITEM_A", "unit": None, "failed": "filed S_ITEM_A; boom",
                                             "tries": 1, "filed": True}}}}}
    row = dict(_steward_row(), retry_of={"item": "S_ITEM_A", "unit": None, "tries": 1, "filed": True,
                                         "failed": "filed S_ITEM_A; boom"})
    fx2 = {"launch_brief": lambda *a, **k: (1, "never", None), "known": lambda: set(),
           "file": lambda *a, **k: (True, "filed again"), "publish": lambda item: (False, "fatal: index.lock exists")}
    with patched((MD, "pilot_ledger", lambda root, mod: False), (MA, "steward_brief", lambda root, mod, row: "brief")):
        MA.execute(tmp, {}, st2, [row], {"S"}, 1.8e9, fx=fx2)
    e2 = st2["mods"]["S"]["steward"]["S|k"]
    check("filed: a republish that fails keeps filed=True, so the next retry launches the same item",
          e2.get("item") == "S_ITEM_A" and e2.get("filed") is True, e2)


def full_launch_output_seen(tmp):
    """RIMMANDRAKE_READ_WHOLE_LAUNCH_OUTPUT_FOR_TRANSIENT_FAULTS (review item 5)."""
    st = {"mods": {"D": {}}}
    fx = {"launch_brief": lambda *a, **k: (1, "launch refused\nfatal: index.lock exists", None), "known": lambda: set(),
          "file": None, "publish": None}
    with patched((MD, "pilot_ledger", lambda root, mod: False), (M, "game_takeable", lambda stage: False)):
        row = _fixer_row()
        MA.execute(tmp, {"launch_tries": 3}, st, [row], {"D"}, 1.8e9, fx=fx)
    check("output: a transient fault on the launch's second line is seen (launch_retry, not launch_failed)",
          row.get("decision") == "launch_retry", (row.get("decision"), st["mods"]["D"].get("fixers")))


def seed_any_exec_failure_cleans(tmp):
    """RIMMANDRAKE_CLEAN_SEED_RECORD_WHEN_LAND_CANNOT_START (review item 6)."""
    root = os.path.join(tmp, "seed2")
    rec = os.path.join(M.mod_dir(root, "A"), M.RECORD)

    def seed(root_, mod, **k):
        os.makedirs(os.path.dirname(rec), exist_ok=True)
        open(rec, "w").close()
        return {}, True
    real_run = subprocess.run

    def run(argv, *a, **k):
        if argv and str(argv[0]).endswith("land.sh"):
            raise PermissionError(13, "Permission denied", argv[0])
        return real_run(argv, *a, **k)
    with patched((M, "seed_mod", seed), (MA.subprocess, "run", run)):
        try:
            MA.seed_and_land(root, "A")
        except Exception:  # noqa: BLE001
            pass
    check("seed: a land.sh that cannot even start leaves no local record", not os.path.exists(rec))


def autolock_keeps_unreadable_record(tmp):
    """RIMMANDRAKE_ABORT_AUTOLOCK_WHEN_BACKUP_UNREADABLE (review item 7)."""
    import time as _t
    if os.geteuid() == 0:
        check("autolock: unreadable-backup case UNMEASURED (running as root reads every file)", True)
        return
    root = os.path.join(tmp, "lock2")
    os.makedirs(M.mod_dir(root, "E"))
    now = 1.8e9
    day = _t.strftime("%Y-%m-%d", _t.localtime(now))
    dp = os.path.join(root, "infrastructure/state/delegated", day, "E-design-version-0.1.0.json")
    os.makedirs(os.path.dirname(dp))
    with open(dp, "w") as f:
        f.write('{"kept": true}\n')
    os.chmod(dp, 0o200)        # writable, unreadable

    def land(subj, paths):
        raise RuntimeError("land.sh refused")
    try:
        MA.autolock_and_land(root, "E", now=now, land=land)
    except Exception:  # noqa: BLE001
        pass
    if os.path.exists(dp):
        os.chmod(dp, 0o600)
    body = open(dp).read() if os.path.exists(dp) else None
    check("autolock: an existing record it cannot back up is never overwritten or deleted", body == '{"kept": true}\n',
          body)


def acts_take_no_slot(tmp):
    """RIMMANDRAKE_COUNT_NO_SLOT_FOR_AUTOLOCK_OR_REPIN_ACTS (review item 8)."""
    st = {"mods": {}}
    rows = [{"mod": "A", "decision": "launch", "aut": "autolock", "steward_key": "A|lock", "stage": "blind_challenge"},
            {"mod": "B", "decision": "launch", "aut": "steward", "steward_key": "0.1.0|B|k", "steward_kind": "x",
             "stage": "blind_challenge"}]
    fx = {"designer_state": lambda m: {}, "open_items": lambda ids: [], "version_locked": lambda m: True,
          "version_evidence": lambda m: {}}
    rows, launches = MA.resolve(tmp, {"steward_cap_tokens": 1_250_000, "max_live": 1}, st,
                                {"A": {"live_units": [], "version": "0.1.0"}, "B": {"live_units": [], "version": "0.1.0"}},
                                rows, [], 1.8e9, fx=fx)
    check("slots: an autolock act takes no slot from a steward run behind it (max_live 1, nothing live)",
          "B" in launches and rows[1].get("decision") != "slots_full", (launches, rows[1].get("decision")))


def spent_failure_never_starves_retry(tmp):
    """The Codex check of the repairs (RIMMANDRAKE_SHARE_GATE_RETRY_RULE_WITH_FIXER_SELECTORS): two failed items, A
    spent (3 tries), B retriable (1 try): both selectors pick B, in the road back and in a paused mod's tickets."""
    cfg = {"launch_tries": 3}
    book = lambda: {"A_ITEM": {"item": "A_ITEM", "unit": None, "failed": "fatal: index.lock exists", "tries": 3},  # noqa: E731
                    "B_ITEM": {"item": "B_ITEM", "unit": None, "failed": "fatal: index.lock exists", "tries": 1}}
    s = {"road_back": {"caused_by": "STEW_ITEM", "at": 1}, "steward": {}, "fixers": book()}
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s, row, lambda ids: [{"id": "A_ITEM", "needs": "offline"}, {"id": "B_ITEM", "needs": "offline"}],
                  cfg=cfg)
    check("retry rule: the road back skips a spent failure for a retriable one", row.get("fix_item") == "B_ITEM", row)
    s = {"fixers": book()}
    row = {"mod": "P", "stage": "blind_challenge"}
    MA._stop_tickets({"stop_tickets": lambda m, dst, s_: [{"id": "A_ITEM"}, {"id": "B_ITEM"}],
                      "ticket_runs": lambda i: []}, row, s, _blocked_dst(), 1.8e9, cfg=cfg)
    check("retry rule: a paused mod's tickets skip a spent failure for a retriable one", row.get("fix_item") == "B_ITEM",
          row)
    s = {"road_back": {"caused_by": "STEW_ITEM", "at": 1}, "steward": {},
         "fixers": {"A_ITEM": dict(book()["A_ITEM"])}}
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s, row, lambda ids: [{"id": "A_ITEM", "needs": "offline"}], cfg=cfg)
    check("retry rule: with only spent failures left, the road back reads fixer_spent",
          row.get("decision") == "fixer_spent", row)


def raising_republish_keeps_filing(tmp):
    """RIMMANDRAKE_SHARE_GATE_RETRY_RULE_WITH_FIXER_SELECTORS, its second half: a republish that RAISES keeps the
    established filing."""
    st = {"mods": {"S": {"steward": {"S|k": {"item": "S_ITEM_A", "unit": None, "failed": "filed S_ITEM_A; boom",
                                            "tries": 1, "filed": True}}}}}
    row = dict(_steward_row(), retry_of={"item": "S_ITEM_A", "unit": None, "tries": 1, "filed": True,
                                         "failed": "filed S_ITEM_A; boom"})

    def pub(item):
        raise OSError("fatal: index.lock exists")
    fx = {"launch_brief": lambda *a, **k: (1, "never", None), "known": lambda: set(),
          "file": lambda *a, **k: (True, "filed again"), "publish": pub}
    with patched((MD, "pilot_ledger", lambda root, mod: False), (MA, "steward_brief", lambda root, mod, row: "brief")):
        MA.execute(tmp, {}, st, [row], {"S"}, 1.8e9, fx=fx)
    e = st["mods"]["S"]["steward"]["S|k"]
    check("filed: a republish that raises keeps the item and filed=True", e.get("item") == "S_ITEM_A"
          and e.get("filed") is True, e)


# each child's section joins once its fix lands (every one was watched failing on base first)
SECTIONS = [
    seed_timeout_leaves_no_record,
    autolock_failure_before_landing_rolls_back,
    road_back_retries_transient_fixer,
    ledger_after_failure_keeps_the_run,
    launch_exception_books_code,
    hold_beats_coverage_stop,
    stop_tickets_retry_failed_launch,
    filed_item_kept_on_failure,
    full_launch_output_seen,
    seed_any_exec_failure_cleans,
    autolock_keeps_unreadable_record,
    acts_take_no_slot,
    spent_failure_never_starves_retry,
    raising_republish_keeps_filing,
]


def main():
    tmp = tempfile.mkdtemp(prefix="mat_aut_findings_")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "state")
    os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
    try:
        for run in SECTIONS:
            run(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    if "--all" in sys.argv:      # every case, landed or not: the red-on-base run
        SECTIONS[:] = [seed_timeout_leaves_no_record, autolock_failure_before_landing_rolls_back,
                       road_back_retries_transient_fixer, ledger_after_failure_keeps_the_run,
                       launch_exception_books_code, hold_beats_coverage_stop, stop_tickets_retry_failed_launch,
                       filed_item_kept_on_failure, full_launch_output_seen, seed_any_exec_failure_cleans,
                       autolock_keeps_unreadable_record, acts_take_no_slot,
                       spent_failure_never_starves_retry, raising_republish_keeps_filing]
    sys.exit(main())
