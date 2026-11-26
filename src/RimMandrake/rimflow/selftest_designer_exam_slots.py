#!/usr/bin/env python3
"""selftest_designer_exam_slots.py: item RIMMANDRAKE_BUDGET_DESIGNER_EXAM_HELPERS_FIVE_READERS_ZERO_SLOTS.

Measured 2026-11-15: Contagion's Designer stage 4 (the exam: an Examiner, a Challenger, two Readers and a Control reader)
ran headless as seat BENCH, and block_agent_over_slots.py counted its Agent spawns against the Conductor window's helper
budget (CONDUCTOR N=0 once the owner left the window, and the window's own helpers filled it before that), so the exam
could never start; the run ended blocked on this item and the mod sat PAUSED 138 min with its fix item open and nobody
launching it.

Checks:
  hook   a Designer role run (RM_ROLE_UNIT rm-role-designer-*) spawns under its own bounded allowance
         (slot_rules.json role_runs), counted on ITS OWN session's helpers: CONDUCTOR N=0 and the window's helpers
         running -> its readers launch; its allowance full -> refused with reason slots_full, never "paused";
         any other role run is still gated by the Conductor budget, as before
  tick   a mod whose Designer is blocked on an open fix item (a pipeline defect with a filed fix) launches that item's
         fixer itself, once: a live run on it is waited on, a spent run leaves it PAUSED (no second launch); full
         pipeline slots -> wait slots_full, not paused; a block naming no open item is PAUSED as before

    python3 src/RimMandrake/rimflow/selftest_designer_exam_slots.py     exit 0 when every check prints PASS
    HOOK=<path> ... runs the hook checks against another hook file; MAT_AUT_BASE_DIR=<dir> the tick checks against
    another maturation_autonomy.py (the base: watched failing)
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HOOK = Path(os.environ.get("HOOK") or ROOT / ".claude" / "hooks" / "block_agent_over_slots.py")
if os.environ.get("MAT_AUT_BASE_DIR"):
    sys.path.insert(0, os.environ["MAT_AUT_BASE_DIR"])
sys.path.insert(1, str(HERE))
sys.path.insert(1, str(ROOT / "src" / "RimMandrake" / "Utils"))
import slot_allocator as SA     # noqa: E402

FAILS = []
NOW = time.time()
ITEM = "RIMMANDRAKE_BUDGET_DESIGNER_EXAM_HELPERS_FIVE_READERS_ZERO_SLOTS"


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


# ---------------------------------------------------------------------------------------------------------- hook
tmp = Path(tempfile.mkdtemp(prefix="dexam_slots_"))
projects = tmp / "projects"
proj = projects / "-home-mandrake-rm-bench"
streams, disp, au = tmp / "streams", tmp / "dispatcher", tmp / "au"
for d in (streams, disp, au):
    d.mkdir(parents=True)
(au / "latest.json").write_text(json.dumps({"schema": 1, "accounts": {}}))
(au / "series.jsonl").write_text("")
U = {"type": "user", "timestamp": SA.iso_z(NOW - 700), "message": {"role": "user", "content": "go"}}
A = {"type": "assistant", "timestamp": SA.iso_z(NOW - 600),
     "message": {"role": "assistant", "stop_reason": "tool_use", "content": [{"type": "text", "text": "x"}]}}


def helpers(session, n):
    """n running helpers (a tool_use in flight, written 20 s ago) in this session's subagents folder."""
    sub = proj / session / "subagents"
    sub.mkdir(parents=True, exist_ok=True)
    for p in sub.glob("agent-*.jsonl"):
        p.unlink()
    for i in range(n):
        p = sub / ("agent-%s%d.jsonl" % (session, i))
        p.write_text(json.dumps(U) + "\n" + json.dumps(A) + "\n")
        os.utime(p, (NOW - 20, NOW - 20))


def budget(conductor):
    (disp / "helper_budget.json").write_text(json.dumps({"t": NOW - 30, "at": SA.iso_local(NOW - 30), "by": "dispatcher",
                                                         "seats": {"CONDUCTOR": conductor, "RELENTLESS": 10},
                                                         "mode": "CRUISE", "why": "fixture: owner out of window"}))


def hook(unit, session):
    env = dict(os.environ, RM_SPAWN_RESERVE_S="0", RM_SLOT_PROJECTS=str(projects), RM_STREAMS_DIR=str(streams),
               RM_ACCOUNT_USAGE_DIR=str(au), RM_SLOT_MACHINE="testhost", RM_SLOT_OWNER_LEDGER=str(tmp / "none.jsonl"),
               AGENT_SEAT="BENCH", RM_DISPATCHER_STATE=str(disp), CLAUDE_PROJECT_DIR=str(ROOT), RM_ROLE_UNIT=unit)
    body = json.dumps({"tool_name": "Agent", "cwd": "/x", "session_id": session,
                       "transcript_path": str(proj / (session + ".jsonl")),
                       "tool_input": {"prompt": "be the Reader", "model": "opus"}})
    p = subprocess.run([sys.executable, str(HOOK)], input=body, env=env, capture_output=True, text=True, timeout=60)
    out = json.loads(p.stdout) if p.stdout.strip() else {}
    h = out.get("hookSpecificOutput") or {}
    return h.get("permissionDecision"), h.get("permissionDecisionReason") or ""


def hook_checks():
    rules = SA.load_rules(ROOT / "src" / "RimMandrake" / "Utils" / "slot_rules.json")
    rr = rules.get("role_runs") or {}
    n = rr.get("rm-role-designer-")
    ok(isinstance(n, int) and n >= 5, "rules: slot_rules.json role_runs gives the Designer run its own allowance of at "
       "least five (Examiner, Challenger, two Readers, Control) (read %r)" % (n,))
    n = n if isinstance(n, int) else 5
    budget(0)
    helpers("conductor1", 3)            # the Conductor window's own helpers, in the same project folder
    helpers("designer1", 0)
    dec, why = hook("rm-role-designer-1794775427", "designer1")
    ok(dec is None, "hook: CONDUCTOR N=0, three window helpers running, a Designer exam asks for its first reader -> "
       "allowed under its own allowance (read %s: %s)" % (dec, why[:160]))
    helpers("designer1", 3)
    dec, why = hook("rm-role-designer-1794775427", "designer1")
    ok(dec is None, "hook: the Designer's own three readers running, under its allowance -> the next is allowed "
       "(read %s: %s)" % (dec, why[:160]))
    helpers("designer1", n)
    dec, why = hook("rm-role-designer-1794775427", "designer1")
    ok(dec == "deny" and why.startswith("slots_full") and "paused" not in why.lower() and "CONDUCTOR" not in why,
       "hook: the Designer's allowance full -> it waits, the reason slots_full, never paused nor the Conductor's "
       "budget (read %s: %s)" % (dec, why[:200]))
    helpers("designer1", 0)
    # RIMMANDRAKE_ALLOW_STEWARD_EXAM_RETAKE_ITS_OWN_FIVE_READERS: the steward's detached exam retake (its unit named for
    # RIMMANDRAKE_RETAKE_<MOD>_EXAM_*, maturation_autonomy) runs the same five-agent exam, so it gets the same allowance
    budget(0)
    dec, why = hook("rm-detached-bench-rimmandrake-retake-contagion-exam-failin-1794848893", "steward1")
    ok(dec is None, "hook: CONDUCTOR N=0, three window helpers running, a steward's exam retake asks for its control "
       "reader -> allowed under its own allowance (read %s: %s)" % (dec, why[:160]))
    # RIMMANDRAKE_COUNT_DETACHED_SUBRUNS_APART_FROM_CONDUCTOR_SLOTS: a detached run's own sub-runs are counted on its
    # own session, never against the Conductor window's slots (2026-11-20 11:05 PM PST: a FlowWorks holder's sub-run
    # was refused at CONDUCTOR 0 free, and the holder stopped with 6 of 10 game items open)
    holder = "rm-detached-bench-rimmandrake-drive-flowworks-in-game-visit-1795240000"
    n_det = rr.get("rm-detached-")
    helpers("holder1", 0)
    dec, why = hook(holder, "holder1")
    ok(dec is None, "hook: CONDUCTOR N=0, three window helpers running, a detached holder asks for its sub-run -> "
       "allowed under its own allowance (read %s: %s)" % (dec, why[:160]))
    helpers("holder1", n_det if isinstance(n_det, int) else 99)
    dec, why = hook(holder, "holder1")
    ok(isinstance(n_det, int) and dec == "deny" and why.startswith("slots_full") and "CONDUCTOR" not in why,
       "hook: a detached run's own allowance full -> it waits, slots_full, never the Conductor's budget (N %r; read "
       "%s: %s)" % (n_det, dec, why[:160]))
    helpers("holder1", 0)
    # RIMMANDRAKE_ALLOW_REWRITE_BATCH_ITS_ONE_MEANING_READER: a plain-English rewrite batch (unit named for
    # RIMMANDRAKE_REWRITE_*) must start one fresh Opus meaning reader per file (batch_plan.md step 6), one at a time
    rw = "rm-detached-bench-rimmandrake-rewrite-subagent-files-share-1795131536"
    n_rw = rr.get("rm-detached-bench-rimmandrake-rewrite-")
    ok(n_rw == 1, "rules: slot_rules.json role_runs gives a rewrite batch exactly one reader at a time (read %r)" % (n_rw,))
    budget(0)
    helpers("rewrite1", 0)
    dec, why = hook(rw, "rewrite1")
    ok(dec is None, "hook: CONDUCTOR N=0, three window helpers running, a rewrite batch asks for its meaning reader -> "
       "allowed under its own allowance (read %s: %s)" % (dec, why[:160]))
    helpers("rewrite1", 1)
    dec, why = hook(rw, "rewrite1")
    ok(dec == "deny" and why.startswith("slots_full"), "hook: a rewrite batch with its one reader running -> the next "
       "waits, slots_full (read %s: %s)" % (dec, why[:160]))
    helpers("rewrite1", 0)
    budget(0)
    dec, why = hook("rm-role-operations-1794775000", "ops1")
    ok(dec == "deny" and "N=0" in why, "hook: any other role run is still gated by the Conductor budget (N=0 -> deny; "
       "read %s: %s)" % (dec, why[:160]))
    (streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "none at all", "until": SA.iso_local(NOW + 3600),
                                                            "n": 0}))
    dec, why = hook("rm-role-designer-1794775427", "designer1")
    ok(dec == "deny" and "none at all" in why, "hook: his word (slot_override.json N=0) still caps the Designer run "
       "(read %s: %s)" % (dec, why[:160]))
    (streams / "slot_override.json").unlink()


# ---------------------------------------------------------------------------------------------------------- tick
CFG = {"enabled": True, "advancing": [], "cap_tokens": 3_750_000, "max_live": 2, "settle_s": 180, "blind_enabled": True,
       "blind_cap_tokens": 5_000_000, "blind_auto_cycles_per_visit": 3, "ingame_enabled": True, "ingame_cap_tokens": 7_500_000,
       "ingame_auto_runs_per_visit": 1, "steward_cap_tokens": 1_250_000, "fix_cap_tokens": 2_500_000, "steward_model": "opus",
       "stalled_min": 10, "seat": "BENCH"}
BLOCKED = {"status": "blocked", "stage": 4, "item": "CONCEPT_C", "blocked_on": ITEM,
           "history": [{"at": "2026-11-15T21:25:54Z", "stage": 4, "what": "close",
                        "why": "run rm-role-designer-1794775427: stage 4 blocked"}]}


def res(root, st, dst, tickets, runs=None, live=()):
    import maturation_autonomy as MA
    facts = {"C": {"version": None, "live_units": []}}
    for i, u in enumerate(live):
        facts["L%d" % i] = {"version": "0.1.0", "live_units": [u]}
    fx = {"designer_state": lambda m: dst, "version_locked": lambda m: False, "open_items": lambda ids: [],
          "version_evidence": lambda m: [], "designer_unit": lambda m: None, "designer_chain": lambda m: None,
          "blocked_tickets": lambda m, d: None if tickets is None else [{"id": t} for t in tickets],
          # no closed item to lift: the fixture's ledger holds only the open ticket (a lift has its own test,
          # selftest_tick_pauses.py, RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS)
          "blocked_closed": lambda m, d: [],
          "ticket_runs": lambda i: (runs or {}).get(i, [])}
    rows = [{"mod": "C", "stage": "designer", "decision": "not_offline", "why": "decide's reading", "need": "C: design"}]
    rows, launches = MA.resolve(root, dict(CFG), st, facts, rows, [], NOW, fx)
    MA.classify(dict(CFG), st, rows, NOW)
    return rows[0], launches


def tick_checks():
    import maturation_autonomy as MA
    root = tempfile.mkdtemp(prefix="dexam_root_")
    os.makedirs(os.path.join(root, "design", "concepts"))
    st = {"mods": {}}
    r, la = res(root, st, BLOCKED, [ITEM])
    ok(r.get("aut") == "fixer" and r.get("fix_item") == ITEM and la == ["C"] and r.get("klass") == "launch",
       "tick: a Designer blocked on an open fix item launches that item's fixer itself (read %s / %s, launches %s)" % (
           r.get("decision"), r.get("klass"), la))
    ok(not r.get("need"), "tick: that launch owes no Needs Conductor line (read %s)" % r.get("need"))
    st = {"mods": {}}
    r, la = res(root, st, BLOCKED, [ITEM], live=["rm-u1", "rm-u2"])
    ok(r.get("decision") == "slots_full" and r.get("klass") == "wait" and la == [] and ITEM in str(r.get("status")),
       "tick: the pipeline's slots full -> it waits with reason slots_full, not paused (read %s / %s)" % (
           r.get("decision"), r.get("klass")))
    st = {"mods": {}}
    unit = "rm-detached-bench-rimmandrake-budget-designer-exam-helpers-1794786386"
    r, la = res(root, st, BLOCKED, [ITEM], runs={ITEM: [(unit, "running")]})
    ok(la == [] and r.get("klass") == "wait" and unit in str(r.get("status")),
       "tick: a live run on the fix item (a hand launch) is waited on, never doubled (read %s / %s)" % (
           r.get("decision"), r.get("status")))
    ok((st["mods"]["C"].get("fixers") or {}).get(ITEM, {}).get("unit") == unit,
       "tick: that live run is booked as the item's one fixer run")
    # the next tick: the run ended, the item is still open, the Designer still blocked: PAUSED, no second launch
    r, la = res(root, st, BLOCKED, [ITEM], runs={ITEM: [(unit, "finished")]})
    ok(la == [] and r.get("klass") == "paused" and ITEM in str(r.get("status")),
       "tick: its one fixer run spent and the item still open -> PAUSED naming it, launched once, not twice (read %s "
       "/ %s, launches %s)" % (r.get("decision"), r.get("klass"), la))
    st = {"mods": {"C": {"fixers": {ITEM: {"item": ITEM, "unit": "rm-u9", "at": NOW - 900}}}}}
    r, la = res(root, st, BLOCKED, [ITEM])
    ok(la == [] and r.get("klass") == "paused", "tick: a fixer run the tick booked earlier counts as the one run (read "
       "%s, launches %s)" % (r.get("klass"), la))
    for tk, what in (([], "a block naming no open item"), (None, "an unreadable ledger")):
        st = {"mods": {}}
        r, la = res(root, st, BLOCKED, tk)
        ok(la == [] and not r.get("aut") and r.get("decision") == "designer_blocked" and r.get("klass") == "paused",
           "tick: %s -> PAUSED as before, nothing launched (read %s / %s)" % (what, r.get("decision"), r.get("klass")))
    held = dict(BLOCKED, blocked_on="OWNER HOLD: %s" % ITEM)
    r, la = res(root, {"mods": {}}, held, [ITEM])
    ok(la == [] and r.get("decision") == "owner", "tick: an OWNER HOLD stays his even when it names an item (read %s)"
       % r.get("decision"))
    # the default reader: the open ledger items blocked_on names, in the order named
    it = lambda s: types.SimpleNamespace(state=s, kind="bug", caused_by=None)       # noqa: E731
    items = {ITEM: it("doing"), "RIMMANDRAKE_OTHER_DONE_ITEM_LONG_AGO": it("done"), "RIMMANDRAKE_SECOND_OPEN_FIX": it("ready")}
    dst = dict(BLOCKED, blocked_on="%s; also RIMMANDRAKE_OTHER_DONE_ITEM_LONG_AGO and RIMMANDRAKE_SECOND_OPEN_FIX, "
               "NOT_AN_ITEM_NAME" % ITEM)
    got = MA.blocked_tickets(dst, items) if hasattr(MA, "blocked_tickets") else None
    ok([x["id"] for x in got or []] == [ITEM, "RIMMANDRAKE_SECOND_OPEN_FIX"],
       "tick: the default reader finds the open items the block names, in order, closed and unknown ones dropped "
       "(read %s)" % [x["id"] for x in got or []])


def main():
    hook_checks()
    tick_checks()
    print("\n%s: %d failed" % ("GREEN" if not FAILS else "RED", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
