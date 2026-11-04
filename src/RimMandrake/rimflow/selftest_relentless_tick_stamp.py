#!/usr/bin/env python3
"""RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS. A supervisor tick stamps its readings with the WRITE time and names its slow
steps; the tick's mod gap reads a --gate plan (headers and DLLs), never the 260 s full plan; one game reading serves
several items; and the tick_age_s rule is back at 10 min with the budgets that keep a tick inside it. The Conductor's two
clauses: a round's end starts the next proof with no tick and no timer, and RUNNING_NOW shows the game's idle share.

    python3 src/RimMandrake/rimflow/selftest_relentless_tick_stamp.py
"""
import contextlib
import fcntl
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time as real_time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import deploy_custom_mods as D  # noqa: E402
import relentless as R  # noqa: E402
import relentless_game as G  # noqa: E402
import relentless_live as L  # noqa: E402
import relentless_live_round as LR  # noqa: E402
import running_now as RN  # noqa: E402
import selftest_relentless as T  # noqa: E402
import selftest_relentless_game as GT  # noqa: E402

FAILS = []
ABOUT = '<?xml version="1.0" encoding="utf-8"?>\n<ModMetaData><packageId>mandrake.test.mod</packageId></ModMetaData>\n'


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class FakeTime:
    """The time module, with a clock the test moves."""

    def __init__(self):
        self.at = 5000000.0

    def time(self):
        return self.at

    def monotonic(self):
        return self.at

    def __getattr__(self, name):
        return getattr(real_time, name)


def rows_of(store):
    with open(store.p("journal.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def t_write_time():
    """A 300 s tick: the stamps say the write, the staffing arithmetic stays on the tick's start."""
    x = T.Rig(n=2, share=1.0, max_workers=10, staffing=dict(T.STAFF))
    fake, keep = FakeTime(), R.time
    R.time = fake
    real_sync = x.w.sync

    def slow_sync():
        fake.at += 300
        return real_sync()
    x.w.sync = slow_sync
    x.w.wall = fake.monotonic
    try:
        x.tick()
    finally:
        R.time = keep
    start = x.now
    with open(x.s.p("staffing.json"), encoding="utf-8") as f:
        staff = json.load(f)
    with open(x.s.p("reading.json"), encoding="utf-8") as f:
        read = json.load(f)
    with open(x.s.p("staffing_state.json"), encoding="utf-8") as f:
        state = json.load(f)
    ok(staff["t"] == start + 300, "staffing.json t is the write time, 300 s past the tick's start: %s" % (staff["t"] - start))
    ok(staff["at"] == R.iso(start + 300), "staffing.json at agrees with its t: %s" % staff["at"])
    ok(read["at"] == R.iso(start + 300), "reading.json at is the write time: %s" % read["at"])
    ok(state["at"] == start, "minutes-under arithmetic still counts from the tick's start")
    tick = [r for r in rows_of(x.s) if r.get("do") == "tick"][-1]
    ok(tick["at"] == R.iso(start), "the journal row keeps the tick's start")
    ok(tick["wall_s"] == 300, "wall_s covers the whole tick, the prelude included: %s" % tick["wall_s"])
    ok(tick["phases"]["prelude"] == 300.0, "the phases name where the 300 s went: %s" % tick["phases"])
    ok(set(tick["phases"]) >= {"prelude", "steps", "after_steps", "enrol_lease", "staffing_live", "flush"},
       "every phase is on the row: %s" % sorted(tick["phases"]))
    x.done()


def t_slow_step_named():
    x = T.Rig(n=2, share=1.0)
    fake, keep = FakeTime(), R.step
    x.w.wall = fake.monotonic
    T.parked(x, "G0", "game", "/c/G0", game={"phase": "prove", "sha": "s"})
    T.parked(x, "G1", "game", "/c/G1", game={"phase": "prove", "sha": "s"})

    def step(store, fx, r, item, now, acts):
        fake.at += 260 if item == "G1" else 1
    R.step = step
    try:
        x.tick()
    finally:
        R.step = keep
    tick = [r for r in rows_of(x.s) if r.get("do") == "tick"]
    ok(tick and tick[-1]["slow_steps"][0] == {"item": "G1", "s": 260.0} and len(tick[-1]["slow_steps"]) == 1,
       "the 260 s step is named and the 1 s one is not: %s" % (tick and tick[-1]["slow_steps"]))
    x.done()


def t_gap_reads_a_gate_plan():
    seen = []

    class Fx:
        def folded(self):
            return ["Fold"]

        def deploy_plan(self, args, timeout):
            seen.append((args, timeout))
            return 0, ""
    out = {"off": {}, "dll": [], "error": None}
    LR._plan_into(Fx(), ["Fold", "Other"], out)
    ok(seen == [("--compose biomes --with Other --gate", L.live_rules({})["gate_plan_max_s"])],
       "the gap plan asks for --gate, on its own timeout: %s" % seen)
    # the run's real gate stays the full plan: nothing but _plan_into may add the flag
    with open(os.path.join(HERE, "relentless_live.py"), encoding="utf-8") as f:
        ok('fx.deploy_plan(deploy or "", lr["plan_max_s"])' in f.read(), "relentless_live.run gates on the full plan")


def plan(argv, repo, game, cfg, hold):
    """deploy_custom_mods main() against a planted repo and game -> (rc, stdout)."""
    D.SRC_ROOT, D.HOLD_FILE = repo, hold
    D._MODS, D._CONFIG = [game], [cfg]
    sys.argv = ["x"] + argv
    D._INV.clear()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = D.main()
    return rc, out.getvalue()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def t_gate_plan():
    keep = D.SRC_ROOT, D.HOLD_FILE, D._MODS, D._CONFIG, sys.argv, D._def_guard
    tmp = tempfile.mkdtemp(prefix="tickgate-")
    guard = []
    try:
        repo, game = os.path.join(tmp, "repo"), os.path.join(tmp, "game")
        tier = D.SRC_TIERS[0]
        src, dst = os.path.join(repo, tier, "ModA"), os.path.join(game, "ModA")
        for root in (src, dst):
            write(os.path.join(root, "About", "About.xml"), ABOUT)
            write(os.path.join(root, "Assemblies", "Same.dll"), "same\n")
        write(os.path.join(src, "Defs", "changed.xml"), "<Defs>A</Defs>\n")
        write(os.path.join(dst, "Defs", "changed.xml"), "<Defs>B</Defs>\n")
        write(os.path.join(src, "Assemblies", "Stale.dll"), "repo\n")
        write(os.path.join(dst, "Assemblies", "Stale.dll"), "game\n")
        write(os.path.join(dst, "Assemblies", "Gone.dll"), "old\n")
        write(os.path.join(src, "Assemblies", "New.dll"), "new\n")
        cfg, hold = os.path.join(tmp, "ModsConfig.xml"), os.path.join(repo, "DEPLOY_HOLD.txt")
        write(cfg, "<ModsConfigData><activeMods><li>other.mod</li></activeMods></ModsConfigData>\n")
        write(hold, "")
        D._def_guard = lambda *a: (guard.append(1), [])[1]

        rc, text = plan(["--mod", "ModA", "--gate"], repo, game, cfg, hold)
        _cov, drift, off = L.plan_sections(text)
        files = sorted((flag, e.replace(os.sep, "/")) for _s, flag, e in drift)
        ok(guard == [], "a gate never walks the def guard")
        ok(not any(e.endswith(".xml") for _f, e in files), "a gate does not compare non-DLL files: %s" % files)
        ok(files == [("+", "Assemblies/New.dll"), ("-", "Assemblies/Gone.dll"), ("~", "Assemblies/Stale.dll")],
           "a gate reports every stale, missing and leftover DLL: %s" % files)
        ok(off == {"ModA": "not enabled in ModsConfig"}, "a gate keeps the header flags: %s" % off)
        ok(rc == 1, "DLL drift exits 1 as a plan does: %s" % rc)
        ok("other files NOT compared" in text, "the output says what it did not compare")
        ok("in sync" not in text.replace("DLLs in sync", ""), "a gate never prints a plain 'in sync'")

        rc, text = plan(["--mod", "ModA"], repo, game, cfg, hold)
        _cov, drift, _off = L.plan_sections(text)
        ok(guard == [1] and any(e.endswith("changed.xml") for _s, _f, e in drift),
           "the full plan keeps its guard and compares every file")

        for bad in (["--gate", "--apply"], ["--gate", "--pull", "ModA"]):
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    plan(bad, repo, game, cfg, hold)
                ok(False, "%s is refused" % bad)
            except SystemExit as e:
                ok(e.code == 2, "%s is refused" % bad)
        ok(open(os.path.join(dst, "Assemblies", "Stale.dll"), encoding="utf-8").read() == "game\n", "nothing was written")
    finally:
        D.SRC_ROOT, D.HOLD_FILE, D._MODS, D._CONFIG, sys.argv, D._def_guard = keep
        D._INV.clear()
        shutil.rmtree(tmp, ignore_errors=True)


def t_game_reading_shared():
    calls = []
    probe = types.ModuleType("probe")
    probe.measure = lambda use_cache=False: (calls.append(1), {"running": False, "implies": "DOWN", "evidence": "x"})[1]
    fake, keep_t, keep_p, keep_m = FakeTime(), G.time, sys.modules.get("probe"), G.live_mod_count
    G.time, sys.modules["probe"], G.live_mod_count = fake, probe, lambda: 9
    try:
        fx = G.GameFx.__new__(G.GameFx)
        fx.r = {"seat": "BENCH"}
        a = fx.game_reading()
        a["state"] = "scribbled"
        b = fx.game_reading()
        ok(len(calls) == 1 and b["state"] == "DOWN", "a second item shares the reading, and cannot scribble on it")
        fake.at += G.READING_TTL_S
        fx.game_reading()
        ok(len(calls) == 2, "a reading older than READING_TTL_S is taken again")
        fx._game_read = None
        fx.game_reading()
        ok(len(calls) == 3, "a forgotten reading is taken again")
    finally:
        G.time, G.live_mod_count = keep_t, keep_m
        if keep_p is None:
            sys.modules.pop("probe", None)
        else:
            sys.modules["probe"] = keep_p
    with open(os.path.join(HERE, "relentless_game.py"), encoding="utf-8") as f:
        ok("self._round = self._game_read = None" in f.read(), "modlist_enable forgets the shared reading")


def t_rule_back_at_ten():
    repo_utils = os.path.join(os.path.dirname(HERE), "Utils")
    with open(os.path.join(repo_utils, "ops_watch_rules.json"), encoding="utf-8") as f:
        rule = json.load(f)["ranges"]["relentless.tick_age_s"]
    ok(rule["max_age_min"] == 10, "relentless.tick_age_s max_age_min is 10: %s" % rule["max_age_min"])
    live = R.rules(os.path.join(HERE, "relentless_rules.json"))
    worst = live["tick_game_budget_s"] + live["live"]["gate_plan_max_s"]
    ok(worst <= 480, "game budget plus the one plan that may start under it leave room in 10 min with the 2 min pause: %s s" % worst)


def two_on_game():
    """I0 has just had a round, I1 waits its turn: the state a round's end leaves. -> the rig."""
    x = GT.rig(2, share=1.0, max_workers=2)
    x.w.palive = set(range(4001, 4010))     # a launched round runs until the test ends it
    GT.to_game(x, "I0")
    GT.to_game(x, "I1")
    for _ in range(6):
        if "I0" in x.w.proves or "I1" in x.w.proves:
            break
        x.tick()
    first = x.w.proves[0]
    x.tick()
    ok(x.w.proves == [first], "one live user: the other item waits while the round runs")
    return x, first, "I1" if first == "I0" else "I0"


def wake(x):
    with open(x.s.p(R.GAME_WAKE), "w", encoding="utf-8") as f:
        f.write("now")


def t_round_end_starts_next():
    """The Conductor's clause: the game gets its next proof as soon as a round ends, not at the next tick."""
    x, first, other = two_on_game()
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": first, "criterion": "A2", "sha": GT.SHA, "outcome": "PASS"}]
    x.w.palive = set()          # the round is over; no tick runs below
    spawned = []
    LR.wake_supervisor(x.s.root, spawn=lambda argv, **kw: spawned.append((argv, kw)))
    ok(os.path.exists(x.s.p(R.GAME_WAKE)), "a round's end leaves the wake where the store looks for it")
    ok(spawned and spawned[0][0][-1] == "game-next" and spawned[0][0][1].endswith("relentless.py"),
       "a round's end starts relentless.py game-next: %s" % (spawned and spawned[0][0]))
    ok(spawned[0][1]["start_new_session"] and spawned[0][1]["env"]["RELENTLESS_ROOT"] == x.s.root, "detached, on the round's store")
    acts = R.game_next(x.s, x.w, x.r, x.now + 5)
    ok(x.w.proves == [first, other], "no tick ran and the next item has its proof: %s" % x.w.proves)
    ok(x.st(other)["game"]["phase"] == "proving", "the next item holds the game")
    ok(any(a.get("do") == "game_prove" and a["item"] == other for a in acts), "the pass says so in its acts")
    ok(not os.path.exists(x.s.p(R.GAME_WAKE)), "the wake is taken once")
    row = rows_of(x.s)[-1]
    ok(row["do"] == "game_next" and "wall_s" in row, "the pass has its journal row")
    ok(not os.path.exists(x.s.p(R.GAME_NEXT_ON)), "the pass clears its mark")
    before = list(x.w.proves)
    ok(R.game_next(x.s, x.w, x.r, x.now + 6)[0]["why"] == "no wake" and x.w.proves == before, "no wake: nothing moves")
    x.done()


def t_round_end_inside_a_tick():
    """A tick is running when the round ends: the proof starts between the tick's steps, not at its end or the next one."""
    x, first, other = two_on_game()
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": first, "criterion": "A2", "sha": GT.SHA, "outcome": "PASS"}]
    real_sync, steps = x.w.sync, []

    def round_ends_during_prelude():
        x.w.palive = set()
        wake(x)
        return real_sync()
    x.w.sync = round_ends_during_prelude
    keep = R.step

    def spy(store, fx, r, item, now, acts):
        steps.append((item, list(fx.proves)))
        return keep(store, fx, r, item, now, acts)
    R.step = spy
    try:
        acts = x.tick()
    finally:
        R.step = keep
    dos = [a.get("do") for a in acts]
    ok("game_wake" in dos and x.w.proves == [first, other], "the running tick took the wake: %s %s" % (dos, x.w.proves))
    ok(not os.path.exists(x.s.p(R.GAME_WAKE)), "and the wake is gone")
    served = [s for s in steps if other in s[1]]
    ok(len(served) < len(steps), "the proof started inside the tick, before its ordinary steps ended: %s" % steps)
    x.done()


def t_pass_stops_at_the_holder():
    """The round still runs (a second wake, a general round's end): the pass starts nobody."""
    x, first, _other = two_on_game()
    wake(x)
    R.game_next(x.s, x.w, x.r, x.now + 5)
    ok(x.w.proves == [first], "the game is held: no second proof: %s" % x.w.proves)
    x.done()


def t_lock_is_shared_with_the_tick():
    x = T.Rig(n=1, share=1.0)
    lk = open(x.s.p("tick.lock"), "w")
    fcntl.flock(lk, fcntl.LOCK_EX)
    ok(R.game_next(x.s, x.w, x.r, x.now)[0]["why"] == "the running tick took the wake", "under a tick, no wake left: the pass leaves")
    ok(R.tick(x.s, x.w, x.r, x.now + 120) == [{"do": "skip", "why": "a tick is running"}], "a tick still refuses a second tick")
    with open(x.s.p(R.GAME_NEXT_ON), "w"):
        pass
    threading.Timer(0.3, lambda: fcntl.flock(lk, fcntl.LOCK_UN)).start()
    acts = R.tick(x.s, x.w, x.r, x.now + 120)
    ok(acts != [{"do": "skip", "why": "a tick is running"}], "a tick behind a game pass waits its turn instead of losing it")
    lk.close()
    x.done()


def t_unclean_gate_stays_the_ticks():
    x, _first, _other = two_on_game()
    x.w.palive = set()
    wake(x)
    before = list(x.w.proves)
    os.remove(R.relentless_integrity.record_path(x.s))
    acts = R.game_next(x.s, x.w, x.r, x.now + 5)
    ok("integrity gate due" in acts[0]["why"] and x.w.proves == before, "only the tick runs the integrity gate: %s" % acts)
    x.done()


def t_round_wires_the_wake():
    """relentless_live_round.main: the wake comes after round.lock is let go, and a refused round wakes nobody."""
    tmp = tempfile.mkdtemp(prefix="roundwake-")
    rules = os.path.join(tmp, "rules.json")
    with open(rules, "w", encoding="utf-8") as f:
        json.dump({"seat": "BENCH"}, f)
    keep = LR.RoundFx, LR.run_round, LR.wake_supervisor, dict(os.environ)
    woke = []

    def spy(root):
        with open(os.path.join(root, "live", "round.lock"), "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)      # raises if the round still held it
        woke.append(root)
    LR.RoundFx, LR.run_round, LR.wake_supervisor = (lambda seat=None: None), (lambda *a, **k: {"why": "done"}), spy
    os.environ.update(RELENTLESS_ROOT=tmp, RELENTLESS_RULES=rules)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            LR.main(["round", "--item", "I0"])
        ok(woke == [tmp], "a round's end wakes the supervisor, round.lock already free: %s" % woke)
        with open(os.path.join(tmp, "live", "round.lock"), "w") as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            with contextlib.redirect_stdout(out):
                LR.main(["round"])
        ok(woke == [tmp], "a refused round (another is running) wakes nobody: that one will")
    finally:
        LR.RoundFx, LR.run_round, LR.wake_supervisor = keep[:3]
        os.environ.clear()
        os.environ.update(keep[3])
        shutil.rmtree(tmp, ignore_errors=True)


def t_game_next_is_a_command():
    """The real CLI, on an empty store: it parses, builds its Effects, and stays out of a store with no clean tick."""
    tmp = tempfile.mkdtemp(prefix="gamenext-")
    os.makedirs(os.path.join(tmp, "store"))
    with open(os.path.join(tmp, "store", R.GAME_WAKE), "w", encoding="utf-8") as f:
        f.write("now")
    got = subprocess.run([sys.executable, os.path.join(HERE, "relentless.py"), "game-next"], capture_output=True, text=True,
                         timeout=60, env=dict(os.environ, RELENTLESS_ROOT=tmp), stdin=subprocess.DEVNULL)
    ok(got.returncode == 0 and "integrity gate due" in got.stdout, "relentless.py game-next runs: %s %s" % (got.returncode, (got.stdout + got.stderr)[-200:]))
    shutil.rmtree(tmp, ignore_errors=True)


class IdleEnv:
    def __init__(self, text, cut_off=False):
        self.text, self.cut_off = text, cut_off

    def read_tail(self, path, n):
        return self.text, self.cut_off


def t_idle_share():
    """The Conductor's reading: the share of the last 180 minutes with no proof holding the game."""
    now = 1793750000
    row = lambda ago_min, log="x.log": json.dumps({"at": RN_iso(now - ago_min * 60), "log": log})
    rows = [row(1), row(1), row(30), row(179), row(181), row(40, None)]
    g = RN.collect_game_idle(IdleEnv("\n".join(rows) + "\n"), now, 35)
    ok(g["used_min"] == 3 and g["window_min"] == 180, "one minute counts once, a row outside the window or with no log not at all: %s" % g)
    ok(g["idle_pct"] == 98 and g["waiting"] == 35, "idle share %s" % g)
    text = RN.game_idle_text(g)
    ok("idle 98%" in text and "180 min" in text and "35 items wait" in text and "ceiling" in text, text)
    g = RN.collect_game_idle(IdleEnv("{broken\n" + row(10) + "\n", True), now, 0)
    ok(g["window_min"] == 10, "a tail short of the window measures only what it holds: %s" % g)
    try:
        RN.collect_game_idle(IdleEnv(""), now, 0)
        ok(False, "no rows must not read as idle 100%")
    except RN.Unmeasured:
        ok(True, "no rows is UNMEASURED, never idle 100%")
    page = subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), "Utils", "selftest_running_now.py")],
                          capture_output=True, text=True, timeout=200, stdin=subprocess.DEVNULL)
    ok(page.returncode == 0 and "PASS the page shows the game's idle share" in page.stdout,
       "RUNNING_NOW's page carries it: selftest_running_now exit %d %s" % (page.returncode, page.stdout[-300:]))


def RN_iso(t):
    return real_time.strftime("%Y-%m-%dT%H:%M:%SZ", real_time.gmtime(t))


def main():
    for fn in (t_write_time, t_slow_step_named, t_gap_reads_a_gate_plan, t_gate_plan, t_game_reading_shared, t_rule_back_at_ten,
               t_round_end_starts_next, t_round_end_inside_a_tick, t_pass_stops_at_the_holder, t_lock_is_shared_with_the_tick,
               t_unclean_gate_stays_the_ticks, t_round_wires_the_wake, t_game_next_is_a_command, t_idle_share):
        fn()
    print("selftest_relentless_tick_stamp: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
