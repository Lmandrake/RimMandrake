#!/usr/bin/env python3
"""selftest_tick_names_steve_games.py - an in-game visit that waits for ArchBig or ArchSmall names SteveDesktop's two
games too, and says what they take of the visit (page design/specs/2026-11-23-tick-names-steve-games/boundary.md).

RIMMANDRAKE_SEND_MOD_VISITS_TO_STEVEDESKTOP_TICK_SEES_TWO_OF_FOUR_GAMES. Measured 2026-11-23 6:29 AM PST: the tick read
"ExplosiveKnockback ... no game is free: ArchBig: ...; ArchSmall: ..." and named neither Steve1 nor Steve2, so the
Conductor read it as "the tick sees two of four games". The truth was that SteveDesktop could take none of the visit's
56 checks (none carries a testq block). Each test below has the name of its promise on the page.

  python3 selftest_tick_names_steve_games.py                 every case; exit 1 on any failure
  python3 selftest_tick_names_steve_games.py --mutant NAME   the same cases on a planted fault: must exit 1
  python3 selftest_tick_names_steve_games.py --mutants       every mutant; exit 0 only if each one is caught

The bridge, the detached helper and the companion are stand-ins (as in selftest_dispatch_two_games.py); no game,
queue, ssh or ledger is touched.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import selftest_maturation_dispatch as SD  # noqa: E402
import selftest_maturation as SM  # noqa: E402
import maturation as M  # noqa: E402
import maturation_dispatch as MD  # noqa: E402

FAILS = []
STEVE = "SteveDesktop (Steve1, Steve2)"
MUTANTS = {     # name -> (the real steve_takes -> the planted one)
    # the old line: no clause about SteveDesktop at all
    "no_clause": lambda real: (lambda f, mod: ""),
    # a clause that always says "none", whatever the visit's testq blocks are
    "always_none": lambda real: (lambda f, mod: "%s: takes none of its checks" % STEVE),
    # could-not-look read as an empty set
    "unreadable_as_none": lambda real: (lambda f, mod: real(dict(f, to_run=[]), mod)),
    # the line of 2026-11-25: the feed's stop and the host switch are not read, so it says the feed sends what it never will
    "ignores_feed_off": lambda real: (lambda f, mod: _without_off(real, f, mod)),
}


def _without_off(real, f, mod):
    was = MD.steve_feed_off
    MD.steve_feed_off = lambda: None
    try:
        return real(f, mod)
    finally:
        MD.steve_feed_off = was


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:160])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def set_blocks(root, mod, ids):
    """Give exactly IDS a testq block in the fixture table (every other block is removed)."""
    p = os.path.join(root, "design", "concepts", mod, "version", "test_table.json")
    with open(p, encoding="utf-8") as f:
        tt = json.load(f)
    for k, t in (tt.get("tests") or {}).items():
        if isinstance(t, dict):
            t.pop("testq", None)
            if k in ids:
                t["testq"] = {"chains": ["chain_" + k], "by": "testq_blocks.py"}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(tt, f, indent=1)


W = {}     # the fixture world, set up once by setup(): root, log, held, fx, two, owed


def bridge(p, game="a"):
    why = W["held"].get(game)
    return (False, "NOT TAKEABLE  %s" % why) if why else (True, "TAKEABLE  free")


def launches():
    with open(W["log"]) as f:
        return [x for x in f if x.strip()]


def facts_for(c, extra=None):
    out = {}
    for mod in c["advancing"]:
        f = M.build_facts(W["root"], mod)
        f["live_units"] = []
        f["last_end"], f["stage_runs"], f["run_usd"] = None, {}, {}
        out[mod] = dict(MD.add_ingame(W["root"], mod, MD.add_blind(W["root"], mod, f, []), []), **(extra or {}))
    return out


def tick(cfg=None, extra=None):
    cfg = cfg or W["two"]
    shutil.rmtree(W["sd"], ignore_errors=True)
    open(W["log"], "w").close()
    return MD.tick(W["root"], cfg, True, fx=dict(W["fx"], facts=lambda: facts_for(cfg, extra)), now=SM.INGAME_CLOCK,
                   page=False)


def both_held():
    W["held"].clear()
    W["held"].update(a="driver lock held by BENCH for: a test pilot", b="driver lock held by BENCH for: visit 7")


def why_of(rd):
    r = rd["mods"]["Pyrelands"]
    return r["decision"], r.get("why") or ""


def t_the_wait_names_steve_and_why_it_takes_none():
    both_held()
    set_blocks(W["root"], "Pyrelands", [])
    d, why = why_of(tick())
    ok_held = (d == "bridge_held" and not launches() and "no game is free" in why and STEVE in why
               and "takes none" in why and "testq_blocks.py derive Pyrelands" in why)
    W["held"].clear()        # every Arch game driven by a live run: the driver_busy line says the same
    d2, why2 = why_of(tick(dict(W["two"], game_instances=["a"]), {"ingame_live_other": ["rm-detached-x"]}))
    return ok_held and d2 == "driver_busy" and STEVE in why2 and "takes none" in why2


def t_the_wait_names_what_the_feed_sends():
    both_held()
    owed = W["owed"]
    if not isinstance(owed, list) or len(owed) < 3:
        return False
    set_blocks(W["root"], "Pyrelands", owed[:2])
    d, why = why_of(tick())
    return (d == "bridge_held" and STEVE in why and "the visit feed sends the lane 2 of its %d checks" % len(owed) in why
            and "the other %d need a Claude driver" % (len(owed) - 2) in why and "takes none" not in why)


def t_the_wait_says_why_the_feed_sends_nothing():
    """RIMMANDRAKE_SEND_PIPELINE_TICKETS_TO_STEVEDESKTOP_FIRST_IT_SAT_IDLE: 2026-11-25 10:58 PM PST `./pipe why
    ExplosiveKnockback` said the visit feed sends the lane 53 of 65 checks, while testq/fill.stop stopped the feed and the
    host work switch put SteveDesktop on pipeline work only; all 53 ran on ArchBig."""
    both_held()
    owed = W["owed"]
    if not isinstance(owed, list) or len(owed) < 3:
        return False
    set_blocks(W["root"], "Pyrelands", owed[:2])
    stop = os.path.join(W["tq"], "fill.stop")
    with open(stop, "w") as f:
        f.write("a test stop")
    try:
        d, why = why_of(tick())
    finally:
        os.remove(stop)
    ok_stop = (d == "bridge_held" and STEVE in why and "the visit feed sends the lane" not in why and "takes none" in why
               and stop in why and "all %d need a Claude driver" % len(owed) in why)
    sw = os.path.join(W["root"], "host_work_switch.json")
    with open(sw, "w") as f:
        json.dump({"switches": [{"host": "SteveDesktop", "mode": "pipeline", "date": "2026-11-24", "said": "x"}],
                   "lifted": []}, f)
    os.environ["RM_HOST_SWITCH_FILE"] = sw
    try:
        d2, why2 = why_of(tick())
    finally:
        os.environ.pop("RM_HOST_SWITCH_FILE", None)
    ok_switch = (STEVE in why2 and "the visit feed sends the lane" not in why2 and "pipeline work only" in why2
                 and "takes none" in why2)
    return ok_stop and ok_switch


def t_the_brief_says_why_the_feed_sends_nothing():
    """The Stage 6 driver's brief (maturation.ingame_brief_text) said "SteveDesktop's queue takes any mod's token-free
    checks ... queue those with testq.py submit" on 2026-11-25 while the switch refused every mod job."""
    set_blocks(W["root"], "Pyrelands", W["owed"][:2])
    free = M.ingame_brief_text(W["root"], "Pyrelands")[0]
    stop = os.path.join(W["tq"], "fill.stop")
    with open(stop, "w") as f:
        f.write("a test stop")
    try:
        off = M.ingame_brief_text(W["root"], "Pyrelands")[0]
    finally:
        os.remove(stop)
    return ("queue those with `testq.py submit`" in free and "queue those with `testq.py submit`" not in off
            and stop in off and "takes any mod's token-free checks" not in off)


def t_could_not_read_the_checks_is_unmeasured():
    got = [MD.steve_takes(f, "Pyrelands") for f in ({"stage": "in_game"}, {"to_run": None, "checks": None, "testq": []},
                                                    {"to_run": ["sc_a"], "checks": ["sc_a"]})]
    return all("UNMEASURED" in g and STEVE in g and "takes none" not in g for g in got)


def setup():
    root = tempfile.mkdtemp(prefix="tick_steve_games_")
    SM.copy_ingame(root)
    fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
    idle, ilog = os.path.join(root, "fake_idle.py"), os.path.join(root, "fake_idle.log")
    with open(fake, "w") as f:
        f.write(SD.FAKE_DH)
    with open(idle, "w") as f:
        f.write(SM.FAKE_IDLE)
    for p in (log, ilog):
        open(p, "w").close()
    sd = os.path.join(root, "state")
    tq = os.path.join(root, "testq")
    os.makedirs(tq)
    os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(SM.INGAME_CLOCK),
                      MATURATION_BRIEF_DIR=os.path.join(root, "briefs"), RM_MATURATION_DISPATCH_DIR=sd,
                      MATURATION_BRIDGE_IDLE=idle, FAKE_IDLE="NOT", FAKE_IDLE_LOG=ilog, TESTQ_QUEUE=tq,
                      **{M.COMPANION_ENV: os.path.join(root, "no_companion_here.dll")})
    os.environ.pop("FAKE_DH_FAIL", None)
    MD.DH.read_record = lambda unit, root=None: None
    W.update(root=root, log=log, sd=sd, held={}, tq=tq,
             two=dict(SD.load_cfg(), advancing=["Pyrelands"], ingame_enabled=True, max_live=5, game_instances=["a", "b"]),
             fx={"autonomy": False, "convergence": SD.no_convergence, "account": lambda: (True, "test account KEEP"),
                 "known": lambda: set(), "bridge": bridge, "file": lambda item, title, why, **kw: (True, "filed"),
                 "launch": lambda mod, cap, item, **kw: (2, "the test never launches", None)})
    W["owed"] = facts_for(W["two"])["Pyrelands"].get("to_run")


def main(mutant=None):
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
            "RM_MATURATION_DISPATCH_DIR", "FAKE_DH_FAIL", "MATURATION_BRIDGE_IDLE", "FAKE_IDLE", "FAKE_IDLE_LOG",
            "TESTQ_QUEUE", "RM_HOST_SWITCH_FILE",
            M.COMPANION_ENV)
    env_was = {k: os.environ.get(k) for k in keys}
    rec_was = MD.DH.read_record
    real = MD.__dict__.get("steve_takes")
    if mutant:
        if real is None:
            print("FAIL mutant %s: maturation_dispatch has no steve_takes to replace" % mutant)
            return 1
        MD.steve_takes = MUTANTS[mutant](real)
    try:
        setup()
        chk(t_the_wait_names_steve_and_why_it_takes_none,
            "the-wait-names-steve-and-why-it-takes-none: no owed check has a testq block and both Arch games are held "
            "(bridge_held) or every Arch game is driven (driver_busy): the line names SteveDesktop's two games, says "
            "they take none, and names the command that says why")
        chk(t_the_wait_names_what_the_feed_sends,
            "the-wait-names-what-the-feed-sends: two owed checks carry a testq block: the line says the visit feed "
            "sends those 2 to SteveDesktop and the rest need a Claude driver on ArchBig or ArchSmall")
        chk(t_the_wait_says_why_the_feed_sends_nothing,
            "the-wait-says-why-the-feed-sends-nothing: two owed checks carry a testq block, but testq's fill.stop "
            "stops the visit feed, or the host work switch puts SteveDesktop on pipeline work only: the line says "
            "SteveDesktop takes none, names the stop or the switch, and never says the feed sends them")
        chk(t_the_brief_says_why_the_feed_sends_nothing,
            "the-brief-says-why-the-feed-sends-nothing: the Stage 6 driver's brief tells it to queue the testq checks "
            "on SteveDesktop only while the feed may send them; under fill.stop or the host switch it names the cause "
            "and runs them all on Archmagi")
        chk(t_could_not_read_the_checks_is_unmeasured,
            "could-not-read-the-checks-is-unmeasured: a visit whose owed checks or testq blocks could not be read "
            "says UNMEASURED about SteveDesktop, never 'takes none'")
    finally:
        MD.DH.read_record = rec_was
        if mutant:
            MD.steve_takes = real
        for k, v in env_was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        if W.get("root"):
            shutil.rmtree(W["root"], ignore_errors=True)
    print("%s selftest_tick_names_steve_games%s: %d failed" % ("FAIL" if FAILS else "PASS",
                                                               " (mutant %s)" % mutant if mutant else "", len(FAILS)))
    return 1 if FAILS else 0


def run_mutants():
    bad = []
    for m in MUTANTS:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mutant", m], capture_output=True, text=True)
        caught = r.returncode != 0
        print("%s mutant %s" % ("CAUGHT    " if caught else "NOT CAUGHT", m))
        if not caught:
            bad.append(m)
    print("%s: %d of %d mutants caught" % ("PASS" if not bad else "FAIL", len(MUTANTS) - len(bad), len(MUTANTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutant", choices=sorted(MUTANTS))
    ap.add_argument("--mutants", action="store_true")
    a = ap.parse_args()
    sys.exit(run_mutants() if a.mutants else main(a.mutant))
