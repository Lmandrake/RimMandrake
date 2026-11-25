#!/usr/bin/env python3
"""selftest_idle_stop.py - a SteveDesktop game that no job uses is stopped after the idle time, and a game in use never is
(page design/specs/2026-11-25-steve-idle-game-stop/boundary.md; one t_ test per promise). A throwaway queue for each test;
the ssh call is a stub."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["TESTQ_QUEUE"] = tempfile.mkdtemp(prefix="idle_stop_")
sys.path.insert(0, HERE)
import schema as S  # noqa: E402
import testq as T  # noqa: E402

FAILS = []
T0 = 1_800_000_000.0


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def fresh():
    """-> (idle_stop, the list of sent commands, run): a new empty queue, and a stub ssh that records each command."""
    T.QHOME = tempfile.mkdtemp(prefix="idle_stop_")
    T.ensure_dirs()
    import idle_stop as I
    sent = []

    def run(_T, cmd):
        sent.append(cmd)
        return (2, "REFUSED: BENCH holds the bridge") if os.environ.get("IDLE_MOCK") == "REFUSE" else (0, "stopped (graceful)")
    os.environ.pop("IDLE_MOCK", None)
    return I, sent, run


def put(state, rec, name):
    with open(T.q(state, name + ".json"), "w") as f:
        json.dump(rec, f)


def t_a_game_in_use_is_never_stopped():
    I, sent, run = fresh()
    job = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", "a" * 40)
    put("running", {"job": job, "host": T.STEVE, "attempt": job["id"] + ".a1"}, job["id"])
    for dt in (0, I.IDLE_STOP_S + 60, 3 * I.IDLE_STOP_S):
        I.step(T, now=T0 + dt, run=run)
    check(not any(T.REMOTE_RUNNER + " &&" in c for c in sent),
          "a-game-in-use-is-never-stopped: Steve1 runs a job, no down to Steve1 %s" % sent)
    os.remove(T.q("running", job["id"] + ".json"))
    pend = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", "a" * 40)
    put("pending", pend, pend["id"])
    del sent[:]
    for dt in (4 * I.IDLE_STOP_S, 6 * I.IDLE_STOP_S):
        I.step(T, now=T0 + dt, run=run)
    check(sent == [], "a-game-in-use-is-never-stopped: a ready pending job keeps both games up %s" % sent)


def t_an_idle_game_is_stopped_after_the_idle_time():
    I, sent, run = fresh()
    I.step(T, now=T0, run=run)
    I.step(T, now=T0 + I.IDLE_STOP_S - 60, run=run)
    check(sent == [], "an-idle-game-is-stopped-after-the-idle-time: nothing before the idle time %s" % sent)
    I.step(T, now=T0 + I.IDLE_STOP_S + 1, run=run)
    s1 = [c for c in sent if c.startswith("cd %s &&" % T.REMOTE_RUNNER)]
    s2 = [c for c in sent if c.startswith("cd %s &&" % T.REMOTE_RUNNER_B)]
    check(len(s1) == 1 and len(s2) == 1 and all(c.endswith("infrastructure/stevedesktop/rw_game.sh down") for c in sent)
          and T.STEVE2_PREFIX in s2[0] and T.STEVE2_PREFIX not in s1[0],
          "an-idle-game-is-stopped-after-the-idle-time: one down per game, Steve2 through its own clone and instance %s"
          % sent)
    I.step(T, now=T0 + I.IDLE_STOP_S + 120, run=run)
    check(len(sent) == 2, "an-idle-game-is-stopped-after-the-idle-time: once, then a new idle clock %s" % len(sent))


def t_a_refused_stop_waits_and_is_named():
    I, sent, run = fresh()
    os.environ["IDLE_MOCK"] = "REFUSE"
    I.step(T, now=T0, run=run)
    t2 = T0 + I.IDLE_STOP_S + 1
    I.step(T, now=t2, run=run)
    n = len(sent)
    I.step(T, now=t2 + 60, run=run)
    I.step(T, now=t2 + I.RETRY_S - 60, run=run)
    check(n == 2 and len(sent) == 2, "a-refused-stop-waits-and-is-named: no second ask before RETRY_S %s %s" % (n, len(sent)))
    I.step(T, now=t2 + I.RETRY_S + 1, run=run)
    check(len(sent) == 4, "a-refused-stop-waits-and-is-named: asked again after RETRY_S %s" % len(sent))
    log = open(T.q("tick.log")).read() if os.path.exists(T.q("tick.log")) else ""
    check("BENCH holds the bridge" in log, "a-refused-stop-waits-and-is-named: the refusal's words are in the tick log")
    os.environ.pop("IDLE_MOCK", None)


def t_the_next_job_starts_the_game():
    """No code of idle_stop's: the worker's load starts a game that is down, and the tick runs the stop after admission."""
    worker = open(os.path.join(HERE, "..", "..", "..", "..", "infrastructure", "stevedesktop", "worker.py")).read()
    check('"%s init && %s up --wait" % (GAME, GAME)' in worker,
          "the-next-job-starts-the-game: the worker's load is `rw_game.sh init && up --wait`")
    src = open(os.path.join(HERE, "testq.py")).read()
    tick = src[src.index("def cmd_tick("):src.index("GAME_NAMES = {")]
    check("admit(" in tick and "idle_stop" in tick and tick.index("idle_stop") > tick.rindex("admit("),
          "the-next-job-starts-the-game: the tick runs the idle stop after this tick's admission")


def main():
    for t in (t_a_game_in_use_is_never_stopped, t_an_idle_game_is_stopped_after_the_idle_time,
              t_a_refused_stop_waits_and_is_named, t_the_next_job_starts_the_game):
        t()
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
