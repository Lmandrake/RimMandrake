#!/usr/bin/env python3
"""selftest_conductor_identity.py — the BENCH tile wakes as the v3 Conductor (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE).

Owner, 2026-10-28 ~17:20 PDT: "Please build all the components of the v3 system at this time. ... I need to know we
can proceed with a real trial tonight." Design of record: design/RimMandrake/rimflow_v3_2026-10-26.md (Conductor row:
absorbs Bench; quick mode / session mode; session-only helpers; the one voice to him) and
src/RimMandrake/rimflow/roles/conductor.md. Tonight's path (delegated, v3 build): the BENCH tile stays seat BENCH
(the ledger has no CONDUCTOR seat) and wakes with the Conductor identity. Since CONDUCTOR_RCNAME_RENAME_DISPATCHER_ALIAS
(owner 2026-10-29: "So it's called bench again instead of conductor.") its session is launched and shown as CONDUCTOR,
and every matcher also accepts the pre-rename "AGENT BENCH" (dispatcher_schedule seats.BENCH.session_aliases).
Covered, all on files and in memory (nothing launched, nothing written):
  identity    infrastructure/agents/CONDUCTOR.md exists and states the v3 role: absorbs Bench, quick vs session
              mode, helpers in session only, the single voice to him, the goals file, numbers never from memory
  pointer     BENCH.md points at CONDUCTOR.md in its first lines (belt and braces: the hook now injects CONDUCTOR.md)
  ready       `rimflow seat ready` as BENCH says "CONDUCTOR is ready [seat BENCH]", --seat CONDUCTOR writes seat BENCH,
              and handoff.py reads the seat KEY back out of either form (CONDUCTOR_NAME_RENAME_BENCH_STEPS_ASIDE)
  injection   the SessionStart hook injects CONDUCTOR.md FIRST for a BENCH role, BENCH.md after; titles say CONDUCTOR
  tile        the WT tile is named CONDUCTOR (profile + tabTitle + launch_fleet.ps1), --name/--remote-control CONDUCTOR
  wake        the BENCH tile's first prompt reads CONDUCTOR.md, still runs handoff --wake + seat ready, is shell-safe
  report      a headless quick check has one place to report: conductor.md names the Conductor log
  window      the Dispatcher's BENCH names are CONDUCTOR + alias AGENT BENCH; the role hold matches neither
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

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
    sys.path.insert(0, HERE)
    import session_match as SM
    bench = sch["seats"]["BENCH"]
    check(W.session_name_for("BENCH") == "CONDUCTOR" == bench["session_name"],
          "the tile's --name and the Dispatcher's BENCH session_name are both CONDUCTOR")
    check(SM.names_of(bench) == ["CONDUCTOR", "AGENT BENCH"] and SM.seat_names("BENCH") == ["CONDUCTOR", "AGENT BENCH"],
          "seat BENCH answers to CONDUCTOR, then the pre-rename alias AGENT BENCH")
    check(SM.seat_names("FOUNDRY") == ["AGENT FOUNDRY"], "FOUNDRY keeps its one name")
    role = [r for r in sch["roles"] if r.get("name") == "Conductor"][0]
    check(role.get("enabled") is True and role.get("seat") == "BENCH", "the Conductor role is enabled, as seat BENCH")
    # the quick-check hold keys on window_name: it must NOT match any name of the BENCH tile, or no scheduled check
    # would ever run while the tile is open (nothing else prompts the window at 08:00/20:00)
    hold = role.get("window_name")
    for seat, cfg in sch["seats"].items():
        for n in SM.names_of(cfg):
            check(not SM.name_matches(n, hold) and not SM.name_matches(n + " \u25b6 ITEM_X", hold)
                  and not SM.name_matches(hold, SM.names_of(cfg)),
                  "the quick-check hold %r does not fire on seat %s's window %r" % (hold, seat, n))
    sys.path.insert(0, HERE)
    import role_launch as RL
    m = RL.prompt(role, "quick", "20:00", "-", None, 0, 0, 1.0, 0, "u")
    check("then stop" in m and role["instructions"] in m, "a headless quick launch runs conductor.md and stops")


CLI = os.path.join(HERE, "cli.py")


def _ready(seat):
    """-> (rc, stdout, [seat of each event written]) for `rimflow seat ready` on a throwaway ledger."""
    d = tempfile.mkdtemp(prefix="rf_conductor_")
    try:
        e = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
        e.update(RIMFLOW_LEDGER=os.path.join(d, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(d, "items"),
                 RIMFLOW_PROBE="no-reading", RIMFLOW_SEAT=seat)
        p = subprocess.run([sys.executable, CLI, "seat", "ready"], env=e, capture_output=True, text=True,
                           timeout=60)
        seats = []
        for dp, _, fs in os.walk(d):
            for f in fs:
                if f.endswith(".jsonl"):
                    for line in open(os.path.join(dp, f), encoding="utf-8"):
                        if line.strip():
                            ev = json.loads(line)
                            if ev.get("event") == "seat":
                                seats.append(ev.get("seat"))
        return p.returncode, p.stdout, seats
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_ready():
    rc, out, seats = _ready("BENCH")
    check(rc == 0 and out.startswith("CONDUCTOR is ready [seat BENCH]"), "seat ready as BENCH says Conductor: %r" % out[:60])
    check(seats == ["BENCH"], "seat ready as BENCH writes seat BENCH (the key), got %r" % seats)
    rc, out, seats = _ready("CONDUCTOR")
    check(rc == 0 and out.startswith("CONDUCTOR is ready [seat BENCH]") and seats == ["BENCH"],
          "CONDUCTOR is accepted as an alias and written as seat BENCH (%r, %r)" % (out[:40], seats))
    rc, out, _ = _ready("FOUNDRY")
    check(rc == 0 and out.startswith("FOUNDRY is ready") and "[seat" not in out, "FOUNDRY's line is unchanged")
    import handoff as H
    for line, want in (("CONDUCTOR is ready [seat BENCH]\n", "BENCH"), ("CONDUCTOR is ready\n", "BENCH"),
                       ("BENCH is ready\n", "BENCH"), ("FOUNDRY is ready (x)\n", "FOUNDRY"), ("nope", None)):
        check(H.seat_from_ready(line) == want, "handoff reads %r as %r" % (line.strip(), want))


def _hook():
    spec = importlib.util.spec_from_file_location(
        "set_session_title", os.path.join(ROOT, ".claude", "hooks", "set_session_title.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_injection():
    old = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = ROOT
    try:
        H = _hook()
        body = H.read_identity("AGENT BENCH", "sid") or ""
        cond, bench = read(CONDUCTOR).strip(), read(BENCH).strip()
        check(body.startswith(cond), "the hook injects CONDUCTOR.md FIRST for a BENCH role")
        check(bench and bench in body and body.index(bench) > len(cond) - 1, "BENCH.md follows as the session rules")
        check(len(body) <= 2 * H.MAX_IDENTITY_BYTES, "the combined identity stays bounded")
        f = H.read_identity("AGENT FOUNDRY", "sid") or ""
        check(f == read(os.path.join(ROOT, "infrastructure", "agents", "FOUNDRY.md")).strip(),
              "FOUNDRY's injection is its own file only")
        check(H.display_title("AGENT BENCH") == "CONDUCTOR", "the BENCH conversation title says CONDUCTOR")
        check(H.display_title("AGENT BENCH — x") == "CONDUCTOR — x", "a detail suffix survives the rename")
        check(H.display_title("AGENT FOUNDRY") == "AGENT FOUNDRY", "FOUNDRY's title is unchanged")
        check(H.seat_of("AGENT BENCH") == "BENCH", "the recorded role still keys seat BENCH")
        sys.path.insert(0, HERE)
        import session_match as SM
        import dispatcher as DP
        check(H.display_title("AGENT BENCH \u25b6 ITEM_X") == "CONDUCTOR \u25b6 ITEM_X", "the item suffix survives too")
        names = SM.seat_names("BENCH")
        for live in ("CONDUCTOR", "CONDUCTOR \u25b6 ITEM_X", "AGENT BENCH", "AGENT BENCH \u25b6 ITEM_X"):
            check(DP.find_session([{"name": live}], {"session_name": names[0], "session_aliases": names[1:]})
                  is not None, "dispatcher.find_session finds BENCH's window named %r" % live)
        for other in ("CONDUCTORX", "AGENT CONDUCTOR", "AGENT CONDUCTOR \u25b6 ITEM_X", "AGENT BENCHX"):
            check(DP.find_session([{"name": other}], {"session_name": names[0], "session_aliases": names[1:]})
                  is None, "dispatcher.find_session does not take %r for BENCH" % other)
        check(SM.name_matches("AGENT BENCH", "AGENT BENCH"), "plain seat name matches")
        check(SM.name_matches("AGENT BENCH \u25b6 ITEM_X", "AGENT BENCH"), "name + title suffix matches")
        check(not SM.name_matches("AGENT BENCHX", "AGENT BENCH"), "AGENT BENCHX does not match")
        check(not SM.name_matches("AGENT BENCH \u25b6", "AGENT BENCH"), "bare separator without item still needs the space")
        check(DP.find_session([{"name": "AGENT BENCH \u25b6 ITEM_X"}], {"session_name": "AGENT BENCH"}) is not None,
              "dispatcher.find_session finds the suffixed window")
        check(DP.find_session([{"name": "AGENT BENCHX"}], {"session_name": "AGENT BENCH"}) is None,
              "dispatcher.find_session rejects AGENT BENCHX")
        # the title the hook EMITS is the live session name: it must keep matching the schedule's names
        with open(SCHED, encoding="utf-8") as f:
            seats = json.load(f)["seats"]
        tmp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmp, ".claude", "session_roles"))
            for seat in ("BENCH", "FOUNDRY"):
                sid = "sid-" + seat.lower()
                with open(os.path.join(tmp, ".claude", "session_roles", sid), "w") as fh:
                    fh.write("AGENT " + seat)
                env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)
                r = subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "hooks", "set_session_title.py")],
                                   input=json.dumps({"hook_event_name": "UserPromptSubmit", "session_id": sid}),
                                   capture_output=True, text=True, env=env, timeout=60)
                st = json.loads(r.stdout)["hookSpecificOutput"]["sessionTitle"] if r.stdout.strip() else ""
                want = seats[seat]["session_name"]
                check(st == want or st.startswith(want + " "),
                      "hook sessionTitle for %s ('%s') is the schedule session_name '%s'" % (seat, st, want))
                check(SM.name_matches(st, SM.names_of(seats[seat])), "the Dispatcher matches the emitted %r" % st)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        if old is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = old


def test_tile():
    prof, _ = W.build("BENCH")
    check(prof["name"] == "CONDUCTOR" and prof["tabTitle"] == "CONDUCTOR", "the WT tile is named CONDUCTOR")
    check("--name 'CONDUCTOR'" in prof["commandline"] and "--remote-control 'CONDUCTOR'" in prof["commandline"],
          "the session --name and --remote-control name are CONDUCTOR (what the phone / claude.ai list shows)")
    check("AGENT BENCH" not in prof["commandline"] and "AGENT CONDUCTOR" not in prof["commandline"],
          "the BENCH launch line names neither AGENT BENCH nor the hold's AGENT CONDUCTOR")
    f, _ = W.build("FOUNDRY")
    check("--name 'AGENT FOUNDRY'" in f["commandline"], "FOUNDRY's --name is unchanged")
    check(prof["guid"] == W.seat_guid("BENCH"), "the profile guid still derives from the seat key (updates in place)")
    ps1 = read(os.path.join(ROOT, "src", "RimMandrake", "Utils", "launch_fleet.ps1"))
    check("BENCH     = 'CONDUCTOR'" in ps1, "launch_fleet.ps1 opens and waits for the CONDUCTOR tile")
    check("CONDUCTOR" in W.WAKE_PROMPT["BENCH"].split(":")[0], "the wake prompt names the window CONDUCTOR")


if __name__ == "__main__":
    for fn in (test_identity, test_pointer, test_wake, test_report, test_window, test_ready, test_injection,
               test_tile):
        fn()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
