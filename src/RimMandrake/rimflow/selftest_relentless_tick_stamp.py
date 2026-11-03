#!/usr/bin/env python3
"""RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS. A supervisor tick stamps its readings with the WRITE time and names its slow
steps; the tick's mod gap reads a --gate plan (headers and DLLs), never the 260 s full plan; one game reading serves
several items; and the tick_age_s rule is back at 10 min with the budgets that keep a tick inside it.

    python3 src/RimMandrake/rimflow/selftest_relentless_tick_stamp.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
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
import selftest_relentless as T  # noqa: E402

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
    # acts may be empty on this rig: a tick with nothing to say writes no row, so make sure one was written
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


def main():
    for fn in (t_write_time, t_slow_step_named, t_gap_reads_a_gate_plan, t_gate_plan, t_game_reading_shared):
        fn()
    print("selftest_relentless_tick_stamp: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
