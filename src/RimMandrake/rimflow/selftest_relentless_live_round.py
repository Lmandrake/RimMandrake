#!/usr/bin/env python3
"""selftest_relentless_live_round.py -- RA_S09_LIVE_WIRE_ONE_REAL_LEAF: the supervisor's live round and its pacing.

Covers relentless_live_round.py (proof lines, candidates, history, deploy args, the round's batching and early stops),
relentless.live_tick (the tick starts at most one round, paced) and live_log_check.judge. No game, no bridge, no ledger:
the run itself (relentless_live.run) has its own selftest and is swapped here.

    python3 src/RimMandrake/rimflow/selftest_relentless_live_round.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live_round as R      # noqa: E402
import live_log_check as G             # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def item(iid="EG_X", state="built", sha="abc123", owed=("A1", "A2"), levels=None):
    levels = levels or {"A1": "L1", "A2": "L1", "A3": "L3"}
    return {"id": iid, "state": state, "built_sha": sha, "title": "t",
            "criteria": [{"id": c, "level": lv, "text": "x"} for c, lv in sorted(levels.items())],
            "outstanding": list(owed)}


PROSE = "# EG_X\n\n- live-proof A1: python3 live_log_check.py --absent RUT_A\nlive-proof A3: echo judge\n"


def t_proof_lines():
    got = R.proof_lines(PROSE + "live-proof A1: second wins nothing\n`live-proof B12: echo b`\n")
    check("proof lines: bullet and bare lines read, first line per criterion wins",
          got == {"A1": "python3 live_log_check.py --absent RUT_A", "A3": "echo judge", "B12": "echo b"}, got)
    check("proof lines: prose that only mentions live-proof is not a line",
          R.proof_lines("we owe a live-proof for A1 someday") == {})


def t_candidates():
    now = 1_800_000_000
    its = [item(), item("FLOWWORKS_Y"), item("EG_Z", state="claimed"), item("EG_W", sha=None)]
    todo, counts = R.candidates(its, lambda i: PROSE, {}, now, 3600)
    check("candidates: only a live-level owed criterion with a proof runs (A3 is L3, A2 has no proof); FlowWorks too",
          todo == [("EG_X", "A1", "python3 live_log_check.py --absent RUT_A", "abc123"),
                   ("FLOWWORKS_Y", "A1", "python3 live_log_check.py --absent RUT_A", "abc123")], todo)
    check("candidates: missing proofs are counted, not run", counts == {"no proof": 2}, counts)
    at = lambda t: R.L.iso(t)    # noqa: E731
    for outcome, when, sha, runs in (("FAIL", now - 10 ** 6, "abc123", False), ("PASS", now, "abc123", False),
                                      ("REFUSED", now, "abc123", False), ("FAIL", now, "def456", True),
                                      ("UNMEASURED", now - 60, "abc123", False),
                                      ("UNMEASURED", now - 7200, "abc123", True)):
        hist = R.history([{"item": "EG_X", "criterion": "A1", "sha": sha, "outcome": outcome, "at": at(when)}])
        todo, _ = R.candidates([item()], lambda i: PROSE, hist, now, 3600)
        check("history: %s on %s %ds ago -> %s" % (outcome, sha, now - when, "runs" if runs else "waits"),
              bool(todo) == runs, todo)

    # RELENTLESS_FIX_GAME_LANE_OWNER_LOOK_FAILS: his look is never run on the game, whatever its proof line says
    look = item(owed=("A1", "L4"), levels={"A1": "L1", "L4": "L2"})
    look["criteria"][1]["text"] = "the owner has looked at the one review and kept it"
    prose = PROSE + "live-proof L4: grep -q keep infrastructure/state/ledger/events/OWNER.jsonl\n"
    todo, counts = R.candidates([look], lambda i: prose, {}, now, 3600)
    check("candidates: an owner look is skipped, the game's own clause still runs",
          [t[1] for t in todo] == ["A1"] and counts.get("owner look") == 1, (todo, counts))


def t_history_review():
    """GPT review 2026-11-01 counterexamples: per-sha terminal judgments, UTC parsing, bare backticks."""
    now = 1_800_000_000
    rows = [{"item": "EG_X", "criterion": "A1", "sha": "abc123", "outcome": "FAIL", "at": R.L.iso(now - 10 ** 6)},
            {"item": "EG_X", "criterion": "A1", "sha": "def456", "outcome": "PASS", "at": R.L.iso(now - 10 ** 5)},
            {"item": "EG_X", "criterion": "A1", "sha": "abc123", "outcome": "UNMEASURED", "at": R.L.iso(now - 10 ** 5)}]
    todo, _ = R.candidates([item()], lambda i: PROSE, R.history(rows), now, 3600)
    check("history: a FAIL on this build stands after a later build's PASS and a later UNMEASURED", todo == [], todo)
    old = os.environ.get("TZ")
    try:
        os.environ["TZ"] = "America/Los_Angeles"
        time.tzset()
        summer = 1_782_932_400      # 2026-07-01T19:00:00Z, daylight time
        why = R.due({"sha": "s", "outcome": "UNMEASURED", "at": "2026-07-01T19:00:00Z"}, "s", summer + 60, 3600)
    finally:
        if old is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old
        time.tzset()
    check("history: an UNMEASURED a minute old in daylight time still waits (UTC parse)", why == "unmeasured lately", why)
    check("proof lines: a bare command keeps its own backticks",
          R.proof_lines("live-proof A1: echo `date`") == {"A1": "echo `date`"}, R.proof_lines("live-proof A1: echo `date`"))
    check("proof lines: a wrapped line loses only the wrapping pair",
          R.proof_lines("- `live-proof A1: echo x`") == {"A1": "echo x"}, R.proof_lines("- `live-proof A1: echo x`"))


def t_deploy_args():
    check("deploy args: plain mods", R.deploy_args(["B", "A", "A"], {}) == "--mod A --mod B")
    check("deploy args: a folded mod plans through the composed mod, the rest beside it",
          R.deploy_args(["TerminalBiomes", "UtinniPatches"], {"TerminalBiomes": ("x", "y")})
          == "--compose biomes --with UtinniPatches")


class FakeFx(object):
    def __init__(self, game=True, mods=None):
        self.game, self.mods = game, mods or {}
        self.its = [item("EG_A"), item("EG_B"), item("EG_C"), item("EG_D")]

    def game_started(self):
        return 1.0 if self.game else None

    def items(self):
        return self.its

    def proofs(self, i):
        return PROSE

    def folded(self):
        return {}

    def mods_of(self, sha):
        return self.mods.get(sha, ["UtinniPatches"])


def fake_run(outcomes):
    calls = []

    def run(fx, root, item_id, cid, proof, deploy, r, now=None, needs=(), site=None, trees=()):
        calls.append((item_id, cid, deploy))
        NEEDS.append((item_id, tuple(needs)))
        SITES.append((item_id, cid, site))
        o, why = outcomes.get(item_id, ("PASS", "proof exit 0"))
        return {"item": item_id, "criterion": cid, "outcome": o, "why": why, "sha": "abc123"}
    return run, calls


def t_round():
    with tempfile.TemporaryDirectory() as root:
        run, calls = fake_run({})
        s = R.run_round(FakeFx(game=False), root, {}, now=1_800_000_000, run=run)
        check("round: no running game -> no run at all", calls == [] and s["why"] == "no running game", s)
        run, calls = fake_run({"EG_B": ("FAIL", "proof exit 1")})
        s = R.run_round(FakeFx(), root, {"live": {"round_max": 3}}, now=1_800_000_000, run=run)
        check("round: batches up to round_max in one sitting, a FAIL does not stop it",
              [c[0] for c in calls] == ["EG_A", "EG_B", "EG_C"] and s["eligible"] == 4, (calls, s))
        check("round: deploy args come from the item's own mods", calls[0][2] == "--mod UtinniPatches", calls)
        run, calls = fake_run({"EG_A": ("UNMEASURED", "bridge not taken: held by FOUNDRY")})
        s = R.run_round(FakeFx(), root, {}, now=1_800_000_000, run=run)
        check("round: a busy bridge ends the sitting at once", len(calls) == 1 and s["why"].startswith("stopped"), s)
        run, calls = fake_run({})
        s = R.run_round(FakeFx(mods={"abc123": ["FlowWorks"]}), root, {"live": {"round_max": 1}}, now=1_800_000_000, run=run)
        check("round: a FlowWorks game file runs here too (FOUNDRY retired 2026-11-02)",
              len(calls) == 1 and not any(x["outcome"] == "SKIPPED" for x in s["runs"]), s)
        rows = R.read_rows(os.path.join(root, "live", "rounds.jsonl"))
        check("round: every sitting is a rounds.jsonl row", len(rows) == 4, len(rows))
        check("round: a sitting stamps its end beside its start (bottleneck_measure reads both)",
              all(r.get("ended") and r["ended"] >= r["at"] for r in rows), rows)
    # LIVEROUND_SHRINK_PROOFS_ARE_THE_SHORT_PART: a cause that is the bridge's, not the clause's, ends the sitting at once
    # (2026-11-06 LONGSHADE A8..A11 each refused by one IndeterminateError; five waits on an unreadable running list)
    for why in ("the proof exited 2: it did not measure: UNMEASURED: IndeterminateError('refusing jawa/static_call: 1 "
                "earlier mutating call(s) have an UNKNOWN outcome",
                "site not prepared: python rimbridge_client.py --reconcile [--resolve CID --as applied|not-applied|partial",
                "harness fault: INFRA on 3 games for this build, so no game can judge it until the harness is fixed: site "
                "not prepared: python rimbridge_client.py --reconcile [--resolve CID",
                "the proof exited 2: it did not measure: UNMEASURED: bridge unreachable (RimBridgeError)",
                "the running load's mod list could not be read (jawa/running_mods)",
                "health check failed: the bridge does not answer rimbridge/ping from python.exe (exit 1)"):
        with tempfile.TemporaryDirectory() as root:
            run, calls = fake_run({"EG_A": ("UNMEASURED", why)})
            s = R.run_round(FakeFx(), root, {}, now=1_800_000_000, run=run)
            check("round: a bridge-wide dud ends the sitting at the first clause: %s" % why[:50],
                  len(calls) == 1 and s["why"].startswith("stopped") and s.get("left") == 3, (calls, s))
    for why in ("the proof exited 2: it did not measure: UNMEASURED: no generated RM_LongShade map had three wild cells",
                "not in the running load: Graffiti (mandrake.rm.graffiti)",
                "changed since the built commit, so the game cannot run abc123: src/x.xml"):
        with tempfile.TemporaryDirectory() as root:
            run, calls = fake_run({"EG_A": ("UNMEASURED", why)})
            s = R.run_round(FakeFx(), root, {}, now=1_800_000_000, run=run)
            check("round: a clause's own dud does not stop the others: %s" % why[:40],
                  len(calls) == 4 and s["why"] == "done" and "left" not in s, (calls, s))


class TickFx(object):
    def __init__(self, alive=False):
        self.launched, self._alive = 0, alive

    def live_round_alive(self, pid):
        return self._alive

    def live_round_launch(self):
        self.launched += 1
        return 4242


class TickStore(object):
    def __init__(self, d):
        self.dir = d

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def _write(self, path, text):
        with open(path, "w") as f:
            f.write(text)


def t_live_tick():
    import relentless as RL
    with tempfile.TemporaryDirectory() as d:
        st, fx, acts = TickStore(d), TickFx(), []
        RL.live_tick(st, fx, {"live": {}}, 1000.0, acts)
        check("tick: live.auto off starts nothing", fx.launched == 0 and acts == [])
        r = {"live": {"auto": True, "round_every_s": 600}}
        RL.live_tick(st, fx, r, 1000.0, acts)
        check("tick: auto on starts one round and records it", fx.launched == 1 and acts[-1]["do"] == "live_round")
        RL.live_tick(st, fx, r, 1100.0, acts)
        check("tick: paced, no second round inside round_every_s", fx.launched == 1)
        fx._alive = True
        RL.live_tick(st, fx, r, 5000.0, acts)
        check("tick: a round still running is never doubled", fx.launched == 1)
        fx._alive = False
        RL.live_tick(st, fx, r, 5000.0, acts)
        check("tick: after the pace and the round's end, the next one starts", fx.launched == 2)


def t_tick_env():
    import relentless as RL
    fx = RL.Effects.__new__(RL.Effects)
    with tempfile.TemporaryDirectory() as d:
        procs = []
        for root in ("ours", "other"):
            sp = os.path.join(d, root, "src/RimMandrake/rimflow/relentless_live_round.py")
            os.makedirs(os.path.dirname(sp))
            with open(sp, "w") as f:
                f.write("import time\ntime.sleep(30)\n")
            procs.append(subprocess.Popen([sys.executable, sp, "round"]))
        try:
            fx.books = os.path.join(d, "ours")
            check("tick: our checkout's round is alive", fx.live_round_alive(procs[0].pid))
            check("tick: another checkout's round (pid reuse) is not ours", not fx.live_round_alive(procs[1].pid))
        finally:
            for pr in procs:
                pr.kill()
                pr.wait()
    check("tick: our own pid's argv is not a round", not fx.live_round_alive(os.getpid()))
    check("tick: a dead pid is not a round", not fx.live_round_alive(2 ** 22 + 7))
    got = RL.windows_path("/usr/bin:/bin")
    want = [d for d in RL.WINDOWS_DIRS if os.path.isdir(d)]
    check("tick: the round's PATH gains the Windows dirs the systemd unit lacks (powershell.exe finds the game)",
          got.startswith("/usr/bin:/bin") and all(d in got.split(os.pathsep) for d in want), got)
    check("tick: a PATH that already has them is not doubled", RL.windows_path(got) == got)


def t_log_judge():
    log = "Mono path\nConfig error in RUT_A: bad\nRUT_B loaded fine\nwarning: RUT_C odd\n[RimBridge] Bridge token: x\n"
    code, lines = G.judge(log, ["RUT_A"])
    check("log: an error line naming the token is a FAIL", code == G.FAIL and "line 2" in lines[0], lines)
    check("log: a token only on a plain line passes", G.judge(log, ["RUT_B"])[0] == G.PASS)
    check("log: a warning line passes unless --warnings", G.judge(log, ["RUT_C"])[0] == G.PASS
          and G.judge(log, ["RUT_C"], warnings=True)[0] == G.FAIL)
    check("log: no anchor (load not finished) is UNMEASURED, never a pass",
          G.judge("Config error in nothing\n", ["RUT_Z"])[0] == G.UNMEASURED)
    a = "\n[RimBridge] Bridge token: x\n"
    check("log: an exception whose stack trace names the token on a later line is a FAIL",
          G.judge("Exception loading def:\n  defName: RUT_PaleMoss\n  at Verse.X()\n" + a, ["RUT_PaleMoss"])[0] == G.FAIL)
    check("log: a token that contains 'Error' is not itself an error line",
          G.judge("Loaded RUT_ErrorPlant successfully" + a, ["RUT_ErrorPlant"])[0] == G.PASS)
    check("log: '2 errors' and 'Exceptions' naming a token fail (GPT r2)",
          G.judge("2 errors while loading RUT_A" + a, ["RUT_A"])[0] == G.FAIL
          and G.judge("Exceptions encountered while loading RUT_A" + a, ["RUT_A"])[0] == G.FAIL)
    check("log: a blank line or a [Ref] stub does not split an error from its token (GPT r2)",
          G.judge("Exception loading def:\n\n  defName: RUT_A" + a, ["RUT_A"])[0] == G.FAIL
          and G.judge("Exception loading def:\n[Ref C0FFEE]\n  defName: RUT_A" + a, ["RUT_A"])[0] == G.FAIL)
    check("log: another identifier ending in Error is not an error word (GPT r2)",
          G.judge("Loaded RUT_A; fallback=RUT_NoError" + a, ["RUT_A"])[0] == G.PASS
          and G.judge("Loaded RUT_AError" + a, ["RUT_A", "RUT_AError"])[0] == G.PASS)
    check("log: '0 errors' is not an error line", G.judge("RUT_PaleMoss: 0 errors" + a, ["RUT_PaleMoss"])[0] == G.PASS)
    check("log: NullReferenceException naming the token is a FAIL",
          G.judge("NullReferenceException in RUT_PaleMoss tick" + a, ["RUT_PaleMoss"])[0] == G.FAIL)
    check("log: the next message after an error is its own record",
          G.judge("Config error in RUT_A: bad\nRUT_PaleMoss loaded" + a, ["RUT_PaleMoss"])[0] == G.PASS)
    check("log: a failed patch's unindented `file:` line belongs to its record (Player.log, 2026-11-01)",
          G.judge("[M] Patch operation Verse.PatchOperationAdd(Defs/X) failed\nfile: C:\\M\\Patches\\RUT_Loot.xml" + a,
                  ["RUT_Loot"])[0] == G.FAIL)


def t_log_never():
    """LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST: a Log.Warning reaches Player.log as bare text, so --never names it."""
    a = "\n[RimBridge] Bridge token: x\n"
    warn = "[RM Minerals] quarry: no OreDictionary; quarries keep the Quarry mod's own draw" + a
    check("never: bare warning text is invisible to --warnings", G.judge(warn, ["[RM Minerals] quarry"], True)[0] == G.PASS)
    check("never: --never sees it", G.judge(warn, [], never=["[RM Minerals] quarry"])[0] == G.FAIL)
    check("never: absent text passes", G.judge("RUT_A loaded" + a, [], never=["[RM Minerals] quarry"])[0] == G.PASS)
    check("never: no anchor is UNMEASURED", G.judge(warn.split("\n")[0], [], never=["x"])[0] == G.UNMEASURED)
    check("never: a stack-trace line naming it fails", G.judge("Exception x\n  at RM_MineralQuarry.PlanFor()" + a, [],
                                                            never=["RM_MineralQuarry.PlanFor"])[0] == G.FAIL)
    import io, contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = G.safe_main(["--never", "x", "--log", "/nonexistent/dir/Player.log"])
    check("never: an unreadable log is UNMEASURED", code == G.UNMEASURED, out.getvalue())
    real_main = G.main
    G.main = lambda argv=None: (_ for _ in ()).throw(UnicodeEncodeError("ascii", "é", 0, 1, "x"))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            check("log: a crash inside main is UNMEASURED, never exit 1 (GPT r1)", G.safe_main([]) == G.UNMEASURED)
    finally:
        G.main = real_main
    check("never and absent combine", G.judge("Config error in RUT_A" + a, ["RUT_A"], never=["zzz"])[0] == G.FAIL)


def t_proofs_file():
    """LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST: proofs live in live_proofs/<ID>.txt, never the item's prose (the
    Marker's box drops infrastructure/state/items, so a proof there could never be checked blind)."""
    fx = R.RoundFx.__new__(R.RoundFx)
    with tempfile.TemporaryDirectory() as d:
        fx.books = d
        os.makedirs(os.path.join(d, R.PROOFS_DIR))
        os.makedirs(os.path.join(d, "infrastructure/state/items"))
        with open(os.path.join(d, R.PROOFS_DIR, "EG_A.txt"), "w") as f:
            f.write("live-proof A1: echo a\n")
        with open(os.path.join(d, "infrastructure/state/items/EG_B.md"), "w") as f:
            f.write("live-proof A1: echo b\n")
        check("proofs: read from live_proofs/<ID>.txt", R.proof_lines(fx.proofs("EG_A")) == {"A1": "echo a"})
        check("proofs: an item's prose is not a source", fx.proofs("EG_B") == "")
    real = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), R.PROOFS_DIR)
    names = sorted(os.listdir(real)) if os.path.isdir(real) else []
    bad = []
    crit_line = re.compile(r"^[A-Z]+\d+ [A-Z0-9-]+: \S")     # <ID>.criteria: `A2 L1: what is observed` (worker brief)
    for n in names:
        if n.endswith((".py", ".json")) or n.count(".") > 1 and n.endswith(".txt"):   # <ID>.<kind>.txt is data
            continue        # a proof's own script/fixture (`live-proof A1: python3 <ID>_live.py`), not a proof file
        with open(os.path.join(real, n), encoding="utf-8") as f:
            for line in f:
                ok = crit_line.match(line) if n.endswith(".criteria") else (R.PROOF_LINE.match(line.rstrip("\n"))
                                                                             or R.LIVE_MODS.match(line.rstrip("\n"))
                                                                             or R.SITE_LINE.match(line.rstrip("\n"))
                                                                             or R.LIVE_TIER.match(line.rstrip("\n"))
                                                                             or R.LIVE_WITHOUT.match(line.rstrip("\n"))
                                                                             or R.LIVE_COMPANION.match(line.rstrip("\n"))
                                                                             or R.LIVE_MENU.match(line.rstrip("\n"))
                                                                             or R.LIVE_TOGGLE.match(line.rstrip("\n")))
                if line.strip() and not line.startswith("#") and not ok:
                    bad.append("%s: %s" % (n, line[:60]))
    check("proofs: every real live_proofs file is .txt/.criteria (or a proof's .py/.json) and every line parses", names and all(
        n.endswith((".txt", ".criteria", ".py", ".json")) for n in names) and not bad, "%s %s" % (names[:3], bad[:3]))
    # LIVE_PROOFS_STRAY_PRUNE_RED_SELFTEST: a proof's own .py/.json/.<kind>.txt may sit here, but every file is
    # <ID>[_suffix].<ext> for an item the ledger knows; an orphan (typo'd id, item deleted) is a stray to prune.
    ids = set()
    books = os.path.dirname(real)
    for sub in ("items", "items/closed"):
        p = os.path.join(books, sub)
        ids.update(f[:-3] for f in (os.listdir(p) if os.path.isdir(p) else []) if f.endswith(".md"))
    ev = os.path.join(books, "ledger", "events")
    for shard in (os.listdir(ev) if os.path.isdir(ev) else []):
        with open(os.path.join(ev, shard), encoding="utf-8") as f:
            ids.update(m.group(1) for m in re.finditer(r'"id": ?"([^"]+)"', f.read()))
    stems = {n.split(".")[0] for n in names}
    orphans = sorted(s for s in stems if not any(s == i or s.startswith(i + "_") for i in ids if s.startswith(i)))
    check("proofs: every real live_proofs file names a ledger item (no orphan strays)",
          len(ids) > 100 and stems and not orphans, "%d ids, orphans %s" % (len(ids), orphans[:5]))


NEEDS = []
SITES = []


def t_live_site():
    """RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED: `live-site <CID>:` lines are read like proof lines, never as proofs,
    and the round hands each criterion its own; a reload request stands on its game, not on the next one."""
    text = "live-site A1: python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand\n" + PROSE
    check("live-site: read per criterion", R.proof_lines(text, R.SITE_LINE)
          == {"A1": "python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand"}, R.proof_lines(text, R.SITE_LINE))
    check("live-site: a site line is not a proof line", "python.exe" not in R.proof_lines(text).get("A1", ""))
    del SITES[:]
    fx = FakeFx()
    fx.proofs = lambda i: text
    with tempfile.TemporaryDirectory() as root:
        R.run_round(fx, root, {"live": {"round_max": 1}}, now=1_800_000_000, run=fake_run({})[0])
        fx.proofs = lambda i: PROSE
        R.run_round(fx, root, {"live": {"round_max": 1}}, now=1_800_000_001, run=fake_run({})[0])
    check("live-site: the round passes A1 its site, and none when the file has no site line",
          SITES[:2] == [("EG_A", "A1", "python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand"),
                        ("EG_A", "A1", None)], SITES)
    last = {"sha": "s", "outcome": "UNMEASURED", "why": "reload needed: the same cause 3 times", "game": "G1",
            "at": "2026-11-02T00:00:00Z"}
    check("live-site: a reload request skips the criterion on the game it was made on, even with no retry wait",
          R.due(last, "s", 1e12, 0, "G1") == "reload needed", R.due(last, "s", 1e12, 0, "G1"))
    check("live-site: another game runs it again", R.due(last, "s", 1e12, 0, "G2") is None)


def t_live_mods():
    """PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS: a proof file names the mods its proofs need (`live-mods:`), and the
    round hands them to the gate, so a small list that holds them is enough and a list that lacks them is UNMEASURED."""
    text = "live-mods: Graffiti, SacredGraffiti\n- `live-mods: Graffiti EGrowth`\nlive-proof A1: echo a\n"
    check("live-mods: every line, in order, no repeats", R.live_mods(text) == ["Graffiti", "SacredGraffiti", "EGrowth"],
          R.live_mods(text))
    check("live-mods: none named -> none", R.live_mods("live-proof A1: echo a\n") == [])
    check("live-mods: a live-mods line is not a proof line", R.proof_lines(text) == {"A1": "echo a"})
    del NEEDS[:]
    fx = FakeFx()
    fx.proofs = lambda i: "live-mods: Graffiti\n" + PROSE
    with tempfile.TemporaryDirectory() as root:
        R.run_round(fx, root, {"live": {"round_max": 1}}, now=1_800_000_000, run=fake_run({})[0])
    check("live-mods: the round passes them to the gate", NEEDS[:1] == [("EG_A", ("Graffiti",))], NEEDS)


def t_cut_refusal_is_terminal():
    """LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING: 95 of 263 live runs re-refused one cut criterion every round, because the
    refusal row had no sha and so never stood for its build. A row with the sha stands; a cut refusal stands only while
    the criterion is still cut, and yields once its prose holds it whole."""
    now = 1_800_000_000
    rows = [{"item": "EG_X", "criterion": "A1", "sha": "abc123", "outcome": "REFUSED", "cut": True, "at": R.L.iso(now)}]
    cut = item()
    cut["criteria"] = [dict(c, cut=True) if c["id"] == "A1" else c for c in cut["criteria"]]
    todo, counts = R.candidates([cut], lambda i: PROSE, R.history(rows), now, 3600)
    check("cut refusal: stands while the criterion is still cut", todo == [] and counts.get("judged on this build") == 1,
          (todo, counts))
    todo, _ = R.candidates([item()], lambda i: PROSE, R.history(rows), now, 3600)
    check("cut refusal: runs once the prose holds the criterion whole", len(todo) == 1, todo)
    later = rows + [{"item": "EG_X", "criterion": "A1", "sha": "abc123", "outcome": "PASS", "at": R.L.iso(now + 60)}]
    check("cut refusal: a later PASS decides", R.history(later)[("EG_X", "A1", "abc123")]["outcome"] == "PASS")
    sha_less = [dict(rows[0], sha=None)]
    todo, _ = R.candidates([cut], lambda i: PROSE, R.history(sha_less), now, 3600)
    check("cut refusal: (the old bug) a sha-less row stood for nothing", len(todo) == 1, todo)


def t_dead_rows_and_undeployed():
    """LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT, LIVE_EXIT2_FIX_DEFECT_AFTER_TWO_GAMES: a build no game can run and a cause
    that outlived a reload stand for their build like a verdict; an undeployed build waits for another game, but the game
    phase's own round (retry 0) is the staging that deploys it, so it runs."""
    now = 1_800_000_000
    at = R.L.iso(now - 30 * 86400)
    stale = {"sha": "s", "outcome": "UNMEASURED", "at": at, "why": R.L.STALE + ", so the game cannot run s: a (b)"}
    defect = {"sha": "s", "outcome": "UNMEASURED", "at": at, "why": R.L.DEFECT + ": ...", "defect": True}
    plain = {"sha": "s", "outcome": "UNMEASURED", "at": at, "why": "the proof exited 2: x"}
    check("dead: a stale build decides its sha", R.decides(stale) and R.due(stale, "s", now, 3600, "G1") is not None)
    check("dead: a defect decides its sha", R.decides(defect) and R.due(defect, "s", now, 0, "G2") is not None)
    check("dead: an ordinary UNMEASURED does not", not R.decides(plain) and R.due(plain, "s", now, 3600, "G1") is None)
    check("dead: a new sha runs again", R.due(stale, "s2", now, 3600, "G1") is None)
    rows = [dict(stale, item="I", criterion="A2"), dict(plain, item="I", criterion="A2", at=R.L.iso(now))]
    check("dead: history keeps the stale row over a later rerun on the same sha",
          R.history(rows)[("I", "A2", "s")]["why"].startswith(R.L.STALE))
    und = {"sha": "s", "outcome": "UNMEASURED", "at": at, "why": "not deployed: RM_X", "game": "G1"}
    check("undeployed: waits on the same game", R.due(und, "s", now, 3600, "G1") == "not deployed on this game")
    check("undeployed: runs on another game", R.due(und, "s", now, 3600, "G2") is None)
    check("undeployed: the game phase's own round runs it", R.due(und, "s", now, 3600, "G1", per_game=False) is None)


def t_same_game_same_build_waits():
    """LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: 2026-11-03 17:47-18:16Z, GRAFFITI A2/F1/F2 and GENERATOR A2 re-ran every 15
    min on one game and one build, six UNMEASURED runs that could not differ. A dud or a FINAL_WAIT on (game, build) is
    not run again there, the game phase's round (retry 0) included; another game or another build runs it."""
    now = 1_800_000_000
    g1, g2 = R.L.iso(now - 3600), R.L.iso(now - 60)
    dud = {"sha": "s", "outcome": "UNMEASURED", "at": R.L.iso(now - 900), "game": g1,
           "why": "the proof exited 2: it did not measure: Graffiti: REFUSED  PASS=0"}
    fin = {"sha": "s", "outcome": "UNMEASURED", "at": R.L.iso(now - 900), "game": g1,
           "why": R.L.FINAL_WAIT + ": the running game has 48 mods, 40 of FULL.LATEST's 316"}
    old_fin = dict(fin, game=None)
    for name, row, want in (("dud", dud, R.DUD_HERE), ("final", fin, R.WAITS_TIER)):
        check("same game: %s waits, game phase too" % name, R.due(row, "s", now, 0, g1, per_game=False) == want,
              R.due(row, "s", now, 0, g1, per_game=False))
        check("same game: %s runs on another game" % name, R.due(row, "s", now, 0, g2, per_game=False) is None)
        check("same game: %s runs on a new build" % name, R.due(row, "s2", now, 0, g1, per_game=False) is None)
    check("same game: a gameless FINAL_WAIT row written on this game waits",
          R.due(old_fin, "s", now, 0, g1, per_game=False) == R.WAITS_TIER)
    check("same game: a gameless FINAL_WAIT row from before this game runs",
          R.due(old_fin, "s", now, 0, g2, per_game=False) is None)
    busy = dict(dud, why="bridge not taken: busy")
    check("same game: a transient cause is no wait", R.due(busy, "s", now, 0, g1, per_game=False) is None)
    site = dict(dud, why="site not prepared: exit 2")
    check("same game: a site that would not prepare waits", R.due(site, "s", now, 0, g1, per_game=False) == R.DUD_HERE)
    it = item(sha="s", owed=("A2", "F1"), levels={"A2": "L2", "F1": R.L.FINAL})
    hist = {("EG_X", "A2", "s"): dict(dud, item="EG_X", criterion="A2"),
            ("EG_X", "F1", "s"): dict(fin, item="EG_X", criterion="F1")}
    todo, counts = R.candidates([it], lambda i: "live-proof A2: python3 a.py\nlive-proof F1: python3 f.py\n", hist,
                                now, 0, g1)
    check("same game: the game phase's round runs neither", todo == [] and counts.get(R.DUD_HERE) == 1
          and counts.get(R.WAITS_TIER) == 1, (todo, counts))


def t_census():
    """PROOF_RERUNS_TAME_UNMEASURED_REPEATS: the numbers the item was filed on come from this, not a one-off script."""
    row = {"item": "I", "criterion": "A1", "sha": "s", "outcome": "UNMEASURED", "at": "2026-11-03T00:00:00Z", "log": "/l.log",
           "why": "the proof exited 2: it did not measure: x at 601"}
    rows = [row, dict(row, why="the proof exited 2: it did not measure: x at 77"), dict(row, sha="s2"),
            dict(row, why="not in the running load: M", log=None), dict(row, outcome="PASS", why="proof exit 0"),
            dict(row, item="J", outcome="REFUSED", why="cut", log=None)]
    c = R.census(rows)
    check("census: the outcomes count every row", c["outcomes"] == {"UNMEASURED": 4, "PASS": 1, "REFUSED": 1}, c)
    check("census: a repeat is the same clause, build and cause; another build is not", c["repeats"] == 1
          and c["repeating_items"] == [[1, "I"]], c)
    check("census: causes sort by count, numbers gone", c["causes"][0][0] == 3 and "601" not in c["causes"][0][1], c)
    check("census: what held the game, and what that bought", (c["took_bridge"], c["took_bridge_verdict"]) == (4, 1), c)
    check("census: no rows is no crash", R.census([])["rows"] == 0)
    # the biggest cause arrives after smaller ones, so first-seen order and a sorted list differ; a tie reads by name
    order = ["zz small"] + ["cc tied"] * 2 + ["aa tied"] * 2 + ["bb biggest"] * 3
    c = R.census([dict(row, why=w, cause=None) for w in order])
    check("census: causes are sorted by count whatever order they arrived, a tie by name",
          [(n, k) for n, k in c["causes"]] == [(3, "bb biggest"), (2, "aa tied"), (2, "cc tied"), (1, "zz small")], c["causes"])
    many = [dict(row, item=i, why="w") for i in ["one"] * 2 + ["two"] * 4 + ["three"] * 3]
    check("census: repeating items sorted by count whatever order they arrived",
          R.census(many)["repeating_items"] == [[3, "two"], [2, "three"], [1, "one"]], R.census(many)["repeating_items"])


def t_census_command():
    """PROOF_RERUNS_TAME_UNMEASURED_REPEATS: the contract's own command, as a process, on a runs.jsonl fixture: it prints
    the sorted causes from that file, honours --last, and a missing file is UNMEASURED, never "no rows"."""
    def run(root, *args):
        env = dict(os.environ, RELENTLESS_ROOT=root)
        return subprocess.run([sys.executable, os.path.join(HERE, "relentless_live_round.py"), "census"] + list(args),
                              env=env, capture_output=True, text=True, timeout=60)
    base = {"item": "I", "criterion": "A1", "sha": "s", "outcome": "UNMEASURED"}
    whys = ["not in the running load: M", "Type not found", "aaa first alpha", "Type not found", "aaa first alpha", "Type not found"]
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "live"))
        with open(os.path.join(root, "live", "runs.jsonl"), "w", encoding="utf-8") as f:
            for i, w in enumerate(whys):
                f.write(json.dumps(dict(base, why=w, at="2026-11-03T00:00:0%dZ" % i)) + "\n")
        p = run(root)
        check("census command: exit 0 on a fixture", p.returncode == 0, p.stderr[-300:])
        try:
            got = json.loads(p.stdout)
        except ValueError:
            got = {}
        check("census command: prints the sorted causes read from runs.jsonl", got.get("rows") == 6 and got.get("causes") ==
              [[3, "Type not found"], [2, "aaa first alpha"], [1, "not in the running load: M"]], p.stdout[-400:])
        p = run(root, "--last", "2")
        try:
            got = json.loads(p.stdout)
        except ValueError:
            got = {}
        check("census command: --last takes the newest rows", p.returncode == 0 and got.get("rows") == 2
              and got.get("from") == "2026-11-03T00:00:04Z" and got.get("to") == "2026-11-03T00:00:05Z", p.stdout[-400:])
    with tempfile.TemporaryDirectory() as root:
        p = run(root)
        check("census command: no file is UNMEASURED with exit 2, and no numbers", p.returncode == 2
              and "UNMEASURED" in p.stderr and not p.stdout.strip(), (p.returncode, p.stdout[-200:], p.stderr[-200:]))


def main():
    for t in (t_live_site, t_proof_lines, t_proofs_file, t_candidates, t_deploy_args, t_round, t_live_mods, t_live_tick, t_log_judge, t_log_never,
              t_history_review, t_tick_env, t_cut_refusal_is_terminal, t_dead_rows_and_undeployed,
              t_same_game_same_build_waits, t_census, t_census_command):
        t()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
