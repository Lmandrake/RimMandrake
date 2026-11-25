#!/usr/bin/env python3
"""selftest_bridge_take_pipe_hold.py - `bridge take` honours his `./pipe off game:<g>` (RIMMANDRAKE_HONOUR_PIPE_OFF_IN_BRIDGE_TAKE_IT_WALKED_PAST).

game_lock.claim refuses a game under his hold (EX_HIS 3; an unreadable store is COULD NOT LOOK 2); the bridge take used to walk past it.
Everything runs on a throwaway ledger, throwaway driver locks and a throwaway control store (RM_CONTROL_DB); the live games are never touched.
Prints cases read, worst, limit."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
CLI = os.path.join(HERE, "cli.py")
FAILS = []
CASES = [0]


def check(ok, msg):
    CASES[0] += 1
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_pipehold_")
    try:
        os.makedirs(os.path.join(tmp, "items"))
        ledger = os.path.join(tmp, "events.jsonl")
        a_lock, root = os.path.join(tmp, "a_lock.json"), os.path.join(tmp, "instances")
        db = os.path.join(tmp, "control.db")
        env = {k: v for k, v in os.environ.items()
               if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RM_HOST_GUARD_GEN", "RM_GAME_INSTANCE",
                            "GABP_SERVER_PORT", "GABP_TOKEN", "RM_HOST")}
        env.update(RM_HOST="archmagi")     # games a and b are Archmagi's: on SteveDesktop a host-less take means Steve1
        env.update(RIMFLOW_LEDGER=ledger, RIMFLOW_ITEMS=os.path.join(tmp, "items"), RIMFLOW_PROBE="no-reading",
                   RIMFLOW_DRIVER_LOCK=a_lock, RM_INSTANCES_ROOT=root, RM_CONTROL_DB=db, PYTHONDONTWRITEBYTECODE="1")
        saved = dict(os.environ)
        os.environ.clear()
        os.environ.update(env)
        try:
            import game_lock
            import control as C
            # isolation proof before any take: every path the verbs can reach is under tmp
            for g in ("a", "b"):
                p = game_lock.lock_path(g)
                check(p is None or os.path.abspath(p).startswith(tmp), "isolation: game %s lock path %s is under the temp dir" % (g, p))
            check(C.db_path() == db, "isolation: control store is the temp one")

            def bridge(*argv, seat="BENCH"):
                r = subprocess.run([sys.executable, CLI, "bridge", *argv, "--seat", seat], env=env, capture_output=True, text=True, timeout=120)
                return r.returncode, r.stdout + r.stderr

            def bridge_events():
                if not os.path.exists(ledger):
                    return 0
                return sum(1 for ln in open(ledger) if '"event": "bridge"' in ln or '"event":"bridge"' in ln)

            def locks_written():
                return [p for p in (a_lock, os.path.join(root, "b", "DRIVER_LOCK.json")) if os.path.exists(p)]

            def refused(code, out, want, g):
                return code == want and (want == 2 or ("./pipe on game:" in out and "his test hold" in out))

            # no store at all: a take is not refused by this rule
            check(not os.path.exists(db), "setup: no store file yet")
            code, out = bridge("take", "--for", "x")
            check("HIS HOLD" not in out and code != 3, "no store: take of a is not refused by a hold (exit %s)" % code)
            bridge("release")
            for f in locks_written():
                os.remove(f)

            C.init(db)
            C.switch("game:a", True, "his test hold", p=db)
            n0 = bridge_events()
            for label, argv in (("take", ["take", "--for", "x"]), ("--idle-ok", ["take", "--idle-ok", "--for", "x"]),
                                ("--force", ["take", "--force", "--for", "x"]), ("--host ArchBig", ["take", "--host", "ArchBig", "--for", "x"])):
                code, out = bridge(*argv)
                check(refused(code, out, 3, "a"), "hold on a: bridge %s refused exit 3 naming hold and pass (exit %s: %s)" % (label, code, out.strip()[:90]))
            check(bridge_events() == n0 and not locks_written(), "hold on a: no bridge event, no lock written")
            # --despite-hold (the Conductor staging his walk on purpose, as game_lock.claim --despite-hold): the hold is
            # named and passed, for idle and take alike; game_instance stop/launch --despite-hold reach it through idle
            for label, argv in (("idle", ["idle", "--for", "x"]), ("take", ["take", "--for", "x"])):
                code, out = bridge(*(argv + ["--despite-hold", "staging his walk"]))
                check(code != 3 and "acting anyway: staging his walk" in out,
                      "hold on a: bridge %s --despite-hold passes the hold, naming it (exit %s: %s)" % (label, code, out.strip()[:90]))
            bridge("release")
            for f in locks_written():
                os.remove(f)
            n0 = bridge_events()
            code, out = bridge("release")
            check("HIS HOLD" not in out and code != 3, "hold on a: release is not refused (exit %s)" % code)
            code, out = bridge("who")
            check(code != 3, "hold on a: who is not refused (exit %s)" % code)
            C.switch("game:a", False, "lift", p=db)

            C.switch("game:b", True, "his test hold", p=db)
            code, out = bridge("take", "--host", "ArchSmall", "--for", "x")
            check(refused(code, out, 3, "b"), "hold on b: --host ArchSmall refused exit 3 (exit %s: %s)" % (code, out.strip()[:90]))
            check(bridge_events() == 0 and not locks_written(), "hold on b: no bridge event, no lock written")
            code, out = bridge("take", "--for", "x")
            check("HIS HOLD" not in out and code != 3, "hold on b only: take of a is not refused (exit %s)" % code)
            bridge("release")
            C.switch("game:b", False, "lift", p=db)

            # an unreadable store is COULD NOT LOOK, exit 2
            for f in locks_written():
                os.remove(f)
            open(db, "wb").write(b"this is not a database" * 100)
            n0 = bridge_events()
            code, out = bridge("take", "--for", "x")
            check(code == 2 and "COULD NOT LOOK" in out and bridge_events() == n0, "unreadable store: take refused exit 2 COULD NOT LOOK (exit %s: %s)" % (code, out.strip()[:90]))
            code, out = bridge("release")
            check("COULD NOT LOOK" not in out, "unreadable store: release not refused by it")
        finally:
            os.environ.clear()
            os.environ.update(saved)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("cases read %d, failing %d (worst: %s), limit 0" % (CASES[0], len(FAILS), FAILS[0][:80] if FAILS else "none"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
