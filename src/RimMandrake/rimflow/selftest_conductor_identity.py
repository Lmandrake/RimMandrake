#!/usr/bin/env python3
"""selftest_conductor_identity.py — the BENCH tile wakes as the v3 Conductor (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE).

Owner, 2026-10-28 ~17:20 PDT: "Please build all the components of the v3 system at this time. ... I need to know we
can proceed with a real trial tonight." Design of record: design/RimMandrake/rimflow_v3_2026-10-26.md (Conductor row:
absorbs Bench; quick mode / session mode; session-only helpers; the one voice to him) and
src/RimMandrake/rimflow/roles/conductor.md. Tonight's path (delegated, v3 build): the BENCH tile stays seat BENCH
(the ledger has no CONDUCTOR seat, the Dispatcher watches `AGENT BENCH`) and wakes with the Conductor identity.
Covered, all on files and in memory (nothing launched, nothing written):
  identity    infrastructure/agents/CONDUCTOR.md exists and states the v3 role: absorbs Bench, quick vs session
              mode, helpers in session only, the single voice to him, the goals file, numbers never from memory
  pointer     BENCH.md points at CONDUCTOR.md in its first lines (the SessionStart hook injects BENCH.md)
  wake        the BENCH tile's first prompt reads CONDUCTOR.md, still runs handoff --wake + seat ready, is shell-safe
  report      a headless quick check has one place to report: conductor.md names the Conductor log
  window      the Dispatcher's BENCH session name is still the tile's label (renaming it would blind seat detection)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import install_wt_seat_profiles as W  # noqa: E402

FAILS = []
CONDUCTOR = os.path.join(ROOT, "infrastructure", "agents", "CONDUCTOR.md")
BENCH = os.path.join(ROOT, "infrastructure", "agents", "BENCH.md")
ROLE = os.path.join(ROOT, "src", "RimMandrake", "rimflow", "roles", "conductor.md")
SCHED = os.path.join(ROOT, "src", "RimMandrake", "rimflow", "dispatcher_schedule.json")
SAFE = re.compile(r"[A-Za-z0-9 .,:/_\-]+")
LOG = r"D:\ClaudeWork\rimmandrake\conductor\log.md"


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def read(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def test_identity():
    t = read(CONDUCTOR)
    check(bool(t), "CONDUCTOR.md exists")
    low = " ".join(t.lower().split())             # prose wraps: match across line breaks
    for needle, what in (("you absorb bench", "absorbs Bench"),
                         ("quick mode", "quick mode"),
                         ("session mode", "session mode"),
                         ("helpers run in session mode only", "helpers in session mode only"),
                         ("the only voice to him", "the single voice to him"),
                         ("infrastructure/state/conductor_goals.md", "the goals file"),
                         ("never answer from memory", "numbers never from memory"),
                         ("src/rimmandrake/rimflow/roles/conductor.md", "the role file"),
                         (LOG.lower(), "the Conductor log")):
        check(needle in low, "CONDUCTOR.md states %s" % what)


def test_pointer():
    head = "\n".join(read(BENCH).splitlines()[:6])
    check("infrastructure/agents/CONDUCTOR.md" in head, "BENCH.md points at CONDUCTOR.md in its first lines")


def test_wake():
    p = W.WAKE_PROMPT.get("BENCH", "")
    check(p.lower().startswith("wake"), "BENCH wake prompt opens with wake")
    check("infrastructure/agents/CONDUCTOR.md" in p, "BENCH wake prompt reads CONDUCTOR.md")
    check("handoff.py --wake" in p and "seat ready" in p, "BENCH wake prompt keeps handoff --wake + seat ready")
    check("next --seat" not in p, "BENCH wake prompt does not pull the queue")
    check(SAFE.fullmatch(p) is not None, "BENCH wake prompt is shell/JSON-safe")


def test_report():
    check(LOG in read(ROLE), "conductor.md names the Conductor log as the quick check's report")


def test_window():
    with open(SCHED, encoding="utf-8") as f:
        sch = json.load(f)
    check(W.label_for("BENCH") == "AGENT BENCH" and sch["seats"]["BENCH"]["session_name"] == "AGENT BENCH",
          "the tile and the Dispatcher's BENCH session_name are both literally AGENT BENCH")
    role = [r for r in sch["roles"] if r.get("name") == "Conductor"][0]
    check(role.get("enabled") is True and role.get("seat") == "BENCH", "the Conductor role is enabled, as seat BENCH")
    # the quick-check hold keys on window_name: it must NOT be the BENCH tile's label tonight, or no scheduled check
    # would ever run while the tile is open (nothing else prompts the window at 08:00/20:00)
    check(role.get("window_name") != "AGENT BENCH", "the quick-check hold does not fire on the BENCH tile")
    sys.path.insert(0, HERE)
    import role_launch as RL
    m = RL.prompt(role, "quick", "20:00", "-", None, 0, 0, 1.0, 0, "u")
    check("then stop" in m and role["instructions"] in m, "a headless quick launch runs conductor.md and stops")


if __name__ == "__main__":
    for fn in (test_identity, test_pointer, test_wake, test_report, test_window):
        fn()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
