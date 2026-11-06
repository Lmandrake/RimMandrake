#!/usr/bin/env python3
"""STAGE_WAKE_TUNE_NAPS_AFTER_LOAD. A staging worker's `game-ready` takes the round's own wake path (wake_supervisor): it
leaves store/game_wake and starts `relentless.py game-next`, and that pass follows the staging until its unit is down and
the bridge released, so the first proof after a load starts then and not at the next tick. A wake that lands while a
tick's lease is still making clones is served between lease items, not after the lease.

    python3 src/RimMandrake/rimflow/selftest_relentless_stage_wake.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402
import relentless_live_round as LR  # noqa: E402
import selftest_relentless_game as GT  # noqa: E402
import selftest_relentless_tick_stamp as TS  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def staged(follow_s=None):
    """I0 staging, its unit up: the state the python stager is in when it says game-ready. -> (rig, gen, unit)."""
    x = GT.rig(1)
    if follow_s is not None:
        x.r = dict(x.r, game_next_follow_s=follow_s)
    GT.to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging", "the item is staging: %s" % st["game"]["phase"])
    unit = st["run"]["unit"]
    R.beat(x.s, "I0", st["gen"])
    x.w.running = True                  # the stager loaded the game
    x.w.unkillable = set(x.w.unkillable or ()) | {unit}     # the unit outlives its own game-ready by a few seconds
    polls = []

    def sleep(s):
        polls.append(s)
        x.w.up[unit] = False            # ...then the stager exits
    x.w.sleep = sleep
    return x, st["gen"], unit, polls


def ready_by_cli(x, gen):
    """`relentless.py game-ready` as the stager runs it, with the wake's process start recorded instead of run."""
    spawned, real = [], LR.wake_supervisor
    LR.wake_supervisor = lambda root, spawn=None: real(root, spawn=lambda argv, **kw: spawned.append((argv, kw)))
    keep = os.environ.get("RELENTLESS_ROOT")
    os.environ["RELENTLESS_ROOT"] = x.s.root
    try:
        rc = R.main(["game-ready", "--item", "I0", "--gen", str(gen), "deployed, minimal list"])
    finally:
        LR.wake_supervisor = real
        if keep is None:
            os.environ.pop("RELENTLESS_ROOT", None)
        else:
            os.environ["RELENTLESS_ROOT"] = keep
    return rc, spawned


def t_ready_wakes_the_pass():
    x, gen, unit, polls = staged()
    rc, spawned = ready_by_cli(x, gen)
    ok(rc in (0, None) and x.st("I0")["game"].get("ready"), "game-ready records the staging's ready (rc %s)" % rc)
    ok(os.path.exists(x.s.p(R.GAME_WAKE)), "game-ready leaves the wake where the store looks for it")
    ok(spawned and spawned[0][0][-1] == "game-next" and spawned[0][0][1].endswith("relentless.py")
       and spawned[0][1]["start_new_session"] and spawned[0][1]["env"]["RELENTLESS_ROOT"] == x.s.root,
       "and starts relentless.py game-next, detached, on this store: %s" % (spawned and spawned[0][0]))
    acts = R.game_next(x.s, x.w, x.r, x.now + 5)
    st = x.st("I0")
    ok(polls, "the pass waited for the unit that called it to go down: %d polls" % len(polls))
    ok("release" in x.w.events and x.w.proves == ["I0"] and st["game"]["phase"] == "proving",
       "no tick ran and the proof started: proves %s phase %s" % (x.w.proves, st["game"]["phase"]))
    ok(any(a.get("do") == "game_follow" for a in acts), "the pass says it followed the staging")
    ok(not os.path.exists(x.s.p(R.GAME_WAKE)), "the wake is taken once")
    x.done()


def t_without_follow_it_waits():
    """Sanity: the same wake with the follow off reaches only the unit's stop: the instrument can see the old nap."""
    x, gen, unit, polls = staged(follow_s=0)
    ready_by_cli(x, gen)
    R.game_next(x.s, x.w, x.r, x.now + 5)
    ok(x.w.proves == [] and x.st("I0")["game"]["phase"] == "staging" and not polls,
       "follow off: still staging, no proof until a tick: %s %s" % (x.w.proves, x.st("I0")["game"]["phase"]))
    x.done()


def t_follow_is_bounded():
    """A unit that will not go down holds the pass no longer than game_next_follow_s; the tick's settle takes over."""
    x, gen, unit, polls = staged(follow_s=30)
    clock = [0.0]
    x.w.wall = lambda: clock[0]

    def sleep(s):
        polls.append(s)
        clock[0] += s
    x.w.sleep = sleep
    ready_by_cli(x, gen)
    R.game_next(x.s, x.w, x.r, x.now + 5)
    ok(polls and sum(polls) <= 30 + max(polls) and x.w.proves == [], "bounded: %d polls, %s s" % (len(polls), sum(polls)))
    x.done()


def t_tick_took_the_wake():
    """A running tick took game-ready's wake (it could only stop the unit): the game-next it started still follows."""
    x, gen, unit, polls = staged()
    ready_by_cli(x, gen)
    os.remove(x.s.p(R.GAME_WAKE))       # the tick's serve_wake took it
    R.game_next(x.s, x.w, x.r, x.now + 5)
    ok(x.w.proves == ["I0"] and x.st("I0")["game"]["phase"] == "proving", "the proof started: %s" % x.w.proves)
    ok(R.game_next(x.s, x.w, x.r, x.now + 6)[0]["why"] == "no wake", "nothing staged and no wake: nothing moves")
    x.done()


def t_wake_inside_lease():
    """A round ends while the lease is making clones: its proof starts before the lease ends."""
    x, first, other = TS.two_on_game()
    real_order, real_alarm = R.queue_order, R.pause_alarm
    seen = {}

    def order(states, plan, first_):
        yield dict(x.st(other), status="queued")    # the lease's first item, read before the round ended
        TS.round_over(x, first)
        seen["woke"] = True
        for s in real_order(states, plan, first_):
            yield s

    def alarm(*a, **k):
        seen.setdefault("at_lease_end", list(x.w.proves))
        return real_alarm(*a, **k)

    R.queue_order = order
    R.pause_alarm = alarm
    try:
        acts = x.tick()
    finally:
        R.queue_order, R.pause_alarm = real_order, real_alarm
    ok(seen.get("woke"), "the round ended inside the lease loop")
    ok(seen.get("at_lease_end") == [first, other], "the next proof started inside the lease: %s" % seen.get("at_lease_end"))
    ok("game_wake" in [a.get("do") for a in acts] and not os.path.exists(x.s.p(R.GAME_WAKE)), "the wake was taken once")
    x.done()


def main():
    for fn in (t_ready_wakes_the_pass, t_without_follow_it_waits, t_follow_is_bounded, t_tick_took_the_wake,
               t_wake_inside_lease):
        fn()
    print("selftest_relentless_stage_wake: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
