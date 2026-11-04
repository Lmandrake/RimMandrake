#!/usr/bin/env python3
"""selftest_relentless_live.py -- the live tier's one run (relentless_live.py) and its def proof (live_def_check.py).

No game, no bridge, no ledger: a fake Fx records every call. What must hold, each red under its mutant:
  the bridge is released whatever the proof did; nothing touches the bridge before the item, flyer, proof and deploy
  checks pass; a flyer or a game-changing proof is refused; PASS/FAIL are a verify on the built sha at the criterion's
  level, UNMEASURED a note and never a verify; drift, a held file, an uncovered mod, an old game all stop the run;
  get_defs tokens match whole values only, and a real FAIL outranks an UNMEASURED.
"""
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live as L      # noqa: E402
import live_def_check as C       # noqa: E402

FAILS = []
SHA = "69905fd7165b"
PLAN = """compose: biomes  (manifest src/RimMandrake/Biomes.compose.json)
  compose  TheRot               mandrake.rm.therot                  406 file(s) -> Biomes/TheRot

def guard: 99 mod(s) in the resulting game copy (mandrake.*), 2 target(s): clean
    . ALIAS-REPO ThingDef a -> b: inert

RimMandrake.Biomes mandrake.rm.biomes         5 file(s) HELD
    H  Biomes/Cauldron/northstar/live_works_20261021c.json   (repo-only; not deployed)
           held: live result JSONs: evidence, not game content (hold DEPLOY_HOLD.txt:451 on x)
    ~  Biomes/Contagion/Defs/Other.xml
SWBestiary       mandrake.rsw.swbestiary    98 file(s) HELD
    ~  Textures/swanimals/Worrt/WorrtA_north.png

Drift found. Re-run with --apply to deploy.
"""
TOUCHED = ["src/RimMandrake/TheRot/Defs/Fauna/RM_Chittik.xml",
           "src/RimMandrake/TheRot/Source/WoundLink.cs",
           "src/RimMandrake/TheRot/validation.py"]


def check(name, cond, detail=""):
    if not cond:
        FAILS.append((name, detail))


def item(**kw):
    it = {"id": "ROT_X", "state": "built", "built_sha": SHA, "title": "Rot wound sharing",
          "criteria": [{"id": "A1", "level": "L0", "text": "static"},
                       {"id": "A2", "level": "L1", "text": "get_defs shows CompProperties_WoundLink"},
                       {"id": "A3", "level": "L3", "text": "an Opus read"}],
          "outstanding": ["A2", "A3"]}
    it.update(kw)
    return it


class FakeFx(object):
    def __init__(self, it=None, touched=TOUCHED, plan=(0, PLAN), mtime=1000.0, started=2000.0, take_rc=0, proof=0,
                 verify_rc=0, proof_raises=False, later=(), deleted=(), release_rc=0, start_after_take=None, gap=None,
                 full_gap=None, health=None):
        self.later, self.gone, self.release_rc, self.start_after_take = list(later), list(deleted), release_rc, start_after_take
        self.it, self.t, self.plan, self.mt, self.started = (item() if it is None else it), touched, plan, mtime, started
        self.take_rc, self.proof, self.verify_rc, self.proof_raises = take_rc, proof, verify_rc, proof_raises
        self.calls, self.gap, self.full_gap, self.health_why = [], gap, full_gap, health

    def item(self, item_id):
        return self.it

    def touched(self, sha):
        self.calls.append(("touched", sha))
        return list(self.t)

    def deleted(self, sha):
        return list(self.gone)

    def changed_since(self, sha, paths):
        self.calls.append(("changed", tuple(paths)))
        return [pc for pc in self.later if pc[0] in paths]

    def shippable(self, rel):
        return not (rel.endswith(".py") or rel.endswith(".cs") or "/Source/" in "/" + rel)

    def deploy_plan(self, args, timeout):
        self.calls.append(("plan", args))
        return self.plan

    def mtime(self, mod, rel):
        return self.mt

    def game_started(self):
        if self.start_after_take is not None and any(c[:3] == ("rimflow", "bridge", "take") for c in self.calls):
            return self.start_after_take
        return self.started

    def rimflow(self, *args, timeout=120):
        self.calls.append(("rimflow",) + args)
        rc = 0
        if args[:2] == ("bridge", "take"):
            rc = self.take_rc
        elif args[:2] == ("bridge", "release"):
            rc = self.release_rc
        elif args[0] == "verify":
            rc = self.verify_rc
        return types.SimpleNamespace(returncode=rc, stdout="", stderr="busy: FOUNDRY holds it" if rc else "")

    def running_load_gap(self, mods):
        self.calls.append(("gap", tuple(mods)))
        return self.gap

    def full_list_gap(self):
        self.calls.append(("full_gap",))
        return self.full_gap

    def health(self, files, sha, timeout):
        self.calls.append(("health",))
        if isinstance(self.health_why, Exception):
            raise self.health_why
        return {"why": self.health_why, "hashed": len(files), "unhashed": 0}

    def run_proof(self, proof, log, timeout):
        self.calls.append(("proof", proof))
        if self.proof_raises:
            raise OSError("proof would not start")
        return self.proof

    def verbs(self):
        return [c[1] if c[0] == "rimflow" and c[1] != "bridge" else
                ("take" if c[:3] == ("rimflow", "bridge", "take") else
                 "release" if c[:3] == ("rimflow", "bridge", "release") else c[0]) for c in self.calls]


def go(fx, crit="A2", proof="python3 live_def_check.py --has ThingDef/RM_Chittik=CompProperties_WoundLink", rules=None):
    root = tempfile.mkdtemp(prefix="rl_live_")
    row = L.run(fx, root, "ROT_X", crit, proof, "--compose biomes", rules or {}, now=1_800_000_000)
    with open(os.path.join(root, "live", "runs.jsonl")) as f:
        rows = [json.loads(x) for x in f]
    check("one row per run", len(rows) == 1 and rows[0]["outcome"] == row["outcome"], rows)
    return row


SITE = "python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand"


class ScriptFx(FakeFx):
    """run_proof answers per command from `codes` {command prefix: (exit, log text)} and writes the log."""
    def __init__(self, codes, **kw):
        FakeFx.__init__(self, **kw)
        self.codes = codes

    def run_proof(self, proof, log, timeout):
        self.calls.append(("proof", proof))
        code, text = next((v for k, v in self.codes.items() if proof.startswith(k)), (0, ""))
        with open(log, "w") as f:
            f.write("$ %s\n%s\n" % (proof, text))
        return code


def t_site_runs_first_and_gates_the_proof():
    """RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED: HORIZON_CARAVAN's Stillsand probe ran on a Leaning Scrub map; the
    item's live-site line now makes the map first, bridge held, and a site not made is UNMEASURED with no proof run."""
    root = tempfile.mkdtemp(prefix="rl_live_")
    fx = ScriptFx({"python.exe src/RimMandrake/Utils/live_site.py": (0, "READY: map RM_Stillsand")})
    row = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_000, site=SITE)
    proofs = [c[1] for c in fx.calls if c[0] == "proof"]
    check("site: runs before the proof, the bridge held", proofs == [SITE, "python3 probe.py"]
          and fx.verbs().index("take") < fx.verbs().index("proof") and row["outcome"] == "PASS"
          and row.get("site_log", "").endswith("-site.log"), (fx.verbs(), proofs, row))
    fx = ScriptFx({"python.exe src/RimMandrake/Utils/live_site.py": (2, "NOT READY: the game is at tick 900000")})
    row = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_001, site=SITE)
    check("site: not made -> UNMEASURED with the site's own last line, no proof, released",
          row["outcome"] == "UNMEASURED" and row["why"] == "site not prepared: NOT READY: the game is at tick 900000"
          and [c[1] for c in fx.calls if c[0] == "proof"] == [SITE] and "release" in fx.verbs(), (row, fx.verbs()))
    for bad in ("python3 src/RimMandrake/Utils/live_site.py --biome X", SITE + "; rm -rf x",
                "python.exe src/RimMandrake/Utils/modlist_swap.py --apply"):
        fx = FakeFx()
        row = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_002, site=bad)
        check("site: %r refused before the bridge" % bad[:40], row["outcome"] == "REFUSED" and "take" not in fx.verbs(),
              (row, fx.verbs()))


def t_wsl_proof_reruns_under_windows_python():
    """WORLD_NULLTEX_FLOOD_HUNT: a python3 proof cannot reach the bridge (Windows loopback); it reruns once as python.exe."""
    root = tempfile.mkdtemp(prefix="rl_live_")
    fx = ScriptFx({"python3 ": (2, "RimBridgeError: cannot reach the bridge from WSL ...\n  Re-run under Windows Python:"),
                   "python.exe ": (1, "FAIL: 3 null textures")})
    row = L.run(fx, root, "ROT_X", "A2", "python3 src/x/nulltex_probe.py --live A1", "--compose biomes", {},
                now=1_800_000_000)
    proofs = [c[1] for c in fx.calls if c[0] == "proof"]
    check("wsl: rerun under python.exe gives the real verdict", row["outcome"] == "FAIL"
          and proofs == ["python3 src/x/nulltex_probe.py --live A1", "python.exe src/x/nulltex_probe.py --live A1"]
          and row.get("rerun") == proofs[1] and os.path.exists(row["log"][:-4] + "-wsl.log"), (row, proofs))
    fx = ScriptFx({"python3 ": (2, "UNMEASURED: no save loaded")})
    L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_001)
    check("wsl: another exit 2 is not rerun", len([c for c in fx.calls if c[0] == "proof"]) == 1, fx.calls)


EXIT1_CASES = [     # (log tail of a real exit-1 row of 2026-11-02..04, outcome, the why's head) LIVE_EXIT1_INABILITY_READ_AS_MOD_FAIL
    ("dump s.json: phaseStack=['update'] silentS=60.5 mainStack=NotImplementedException: x tickList=None\n"
     "FAIL s.json does not flag the main thread among 0 threads\nprove_bridge_stall_dump: FAIL (77 s)", "FAIL", "proof exit 1"),
    ("Traceback (most recent call last):\n  File \"x.py\", line 3\n    raise IndeterminateError(\n"
     "rimbridge_client.IndeterminateError: refusing rimworld/pause_game: 1 earlier mutating call(s) have an UNKNOWN outcome",
     "UNMEASURED", L.HARNESS),
    ("OSError: [Errno 28] No space left on device: '/home/x.png' -> '/tmp/com'\nFAIL GelatinousSlime", "UNMEASURED", L.HARNESS),
    ("Error code: Wsl/Service/0x8007274c\nFAIL RustCathedral", "UNMEASURED", L.HARNESS),
    ("Traceback (most recent call last):\nAttributeError: 'NoneType' object has no attribute 'sendall'", "UNMEASURED",
     L.HARNESS),
    ("WRONG_TIER missing tier mods ['mandrake.rut.patches']; 14 running mods", "UNMEASURED", L.RELOAD),
    ("FAIL: the loaded JawaArmoury MVID ac71 is not the committed build's a016 (stale deploy, or redeployed after launch)\n"
     "FAIL: rock X should have bill Y, it does not resolve\nVERDICT FAIL", "UNMEASURED", L.RELOAD),
    ("picked None MoveSpeed tries [3.496, 3.68]\nRESULT SUMP/A1 UNMEASURED no 13 ticks/cell colonist in 6 spawns",
     "UNMEASURED", "the proof exited 1: it did not measure"),
    ("NOT REPRODUCED: neither animal moved >= 6 cells in 300 ticks; the job is not named", "UNMEASURED",
     "the proof exited 1: it did not measure"),
    # the proof's own FAIL beside a None read elsewhere: the None may be the defect, so the FAIL stands for the worker
    # to classify (LIVE_ROWS_FIX_STOP_GUESSING_LOGS: it was erased as a dud)
    ("context: privateMB=None unityReservedMB=None upS=None\nFAIL: missing ['privateMB', 'upS']", "FAIL", "proof exit 1"),
    ("site None net None handler-gone False", "UNMEASURED", "the proof exited 1: it did not measure"),
    ("Traceback (most recent call last):\n  File \"p.py\", line 9\nKeyError: 'mapSize'", "UNMEASURED",
     "the proof exited 1: it did not measure: the proof crashed: KeyError"),
    ("<3>WSL (1999522 - ) ERROR: UtilAcceptVsock:273: accept4 failed 110", "UNMEASURED", L.HARNESS),
    ("FAIL GimmeSomeSlack is not loaded in the running game (probe type unreadable): No loaded type 'X' found",
     "UNMEASURED", L.RELOAD),
    ("loomma_sunstruck_open_vs_roofed: 0 matching rows (want exactly 1)", "UNMEASURED",
     "the proof exited 1: it did not measure: UNKNOWN: a None or zero-row read"),
    # a FAIL line that reports a None or a missing thing is an observed violation and is never erased (the None may be the
    # defect): it reaches the worker as FAIL, who must classify it first (GPT test-tolerance advice 2026-11-04)
    ("0 nightside land tiles in world_tiles.csv\nFAIL A2: no candidate tile on this world", "FAIL", "proof exit 1"),
    ("  RM_Setti_round_trips: FAIL -- ExpectationFailed: X.crossBiomeBiomeList did not restore to '' (read None)",
     "FAIL", "proof exit 1"),
    ("T1 FAIL: top_tinder.tinder_leaves_fuel -> None (out /mnt/d/x.json)", "FAIL", "proof exit 1"),
    ("FAIL: no component genome.inject_starts_gestation in /mnt/d/x", "FAIL", "proof exit 1"),
    ("FAIL: setting round-trip read None; expected enabled\nVERDICT FAIL", "FAIL", "proof exit 1"),
    # an uncaught AssertionError is the proof's own setup as often as the product: UNKNOWN, no strike (GPT 2026-11-04)
    ("Traceback (most recent call last):\nAssertionError: read None; expected enabled", "UNMEASURED",
     "the proof exited 1: it did not measure: the proof crashed: AssertionError (UNKNOWN"),
    # a marker the line negates is no fault, and a FAIL MOD row stands beside any harness text (GPT review 2026-11-03)
    ("deploy check: stale deploy=False\nA1 FAIL MOD missing required texture\nVERDICT FAIL", "FAIL", "proof exit 1"),
    ("PASS: no ConnectionRefusedError in game log\nVERDICT FAIL", "FAIL", "proof exit 1"),
    ("NOT READY: IndeterminateError: refusing jawa/time_clock: 1 earlier mutating call(s) have an UNKNOWN outcome",
     "UNMEASURED", L.HARNESS),
    # prose naming FAIL MOD is no row; a traceback ending in StopIteration is a crash; an indented verdict still counts
    ("Only FAIL MOD rows count against the mod\nTraceback (most recent call last):\nKeyError: mapSize\nVERDICT UNMEASURED",
     "UNMEASURED", "the proof exited 1: it did not measure"),
    ("Traceback (most recent call last):\n  File \"p.py\", line 8\n    c = next(iter(cs))\nStopIteration", "UNMEASURED",
     "the proof exited 1: it did not measure: the proof crashed: StopIteration"),
    ("  VERDICT UNMEASURED: setup unavailable", "UNMEASURED", "the proof exited 1: it did not measure"),
    # real FAILs stand: a mod verdict the proof reached, a FAIL MOD row beside an UNMEASURED SITE one, an assert
    ("VERDICT PASS\nFAIL line 250 names RUT_Horror: Config error in RUT_HorrorProwler: weaponMoney is set\nVERDICT FAIL",
     "FAIL", "proof exit 1"),
    ("  t3_corpse_becomes_a_harvest_site  FAIL  MOD  sites before=1 after=1\n  large_pawns  UNMEASURED SITE  unreadable "
     "(read None)\nVERDICT: FAIL (6 rows, 6 wanted)", "FAIL", "proof exit 1"),
    ("FAIL stall_01.json does not flag the main thread among 0 threads\nprove_bridge_stall_dump: FAIL (77 s)", "FAIL",
     "proof exit 1"),
    ("Traceback (most recent call last):\n  File \"p.py\", line 9\nAssertionError: 3 null textures", "UNMEASURED",
     "the proof exited 1: it did not measure: the proof crashed: AssertionError"),
    # LIVE_ROWS_FIX_STOP_GUESSING_LOGS: the last verdict line does not adjudicate mixed rows, a crash after an observed
    # FAIL does not erase it, and the decisive row may sit far above the end (an 8 KB tail dropped it)
    ("A1 FAIL: no RM_Chittik spawned\nA2 UNMEASURED: no save\nVERDICT UNMEASURED", "FAIL", "proof exit 1"),
    ("A1 FAIL: no RM_Chittik spawned\nTraceback (most recent call last):\nKeyError: 'mapSize'", "FAIL", "proof exit 1"),
    ("A1 FAIL: no RM_Chittik spawned\n" + "detail line of a long proof\n" * 600 + "VERDICT UNMEASURED", "FAIL",
     "proof exit 1"),
    ("A1 FAIL MOD texture missing\n" + "detail line of a long proof\n" * 600 + "ConnectionResetError: reset",
     "FAIL", "proof exit 1"),
    ("Traceback (most recent call last):\n  File \"p.py\", line 9\nValueError: bad literal", "UNMEASURED",
     "the proof exited 1: it did not measure: the proof crashed: ValueError (UNKNOWN"),
    ("FAIL: bill RM_MineShaft_Vacstone exists, but an earlier rock already covers ChunkVacstone\nVERDICT FAIL", "FAIL",
     "proof exit 1"),
]


def t_exit1_that_could_not_ask_is_no_fail():
    """LIVE_EXIT1_INABILITY_READ_AS_MOD_FAIL (owner 2026-11-03): 14 items went back to workers as game_fail on exit-1 rows
    whose proof never asked: a traceback, a full /tmp, the wrong tier, a stale DLL, its own UNMEASURED, a None read.
    Each is UNMEASURED and never a verify; a box fault is the harness's (no strike), a wrong load a reload, the rest a
    proof that measured nothing (relentless_game.RAN_DUD). A FAIL the proof reached stays a FAIL."""
    import relentless_game as G
    for text, outcome, head in EXIT1_CASES:
        root = tempfile.mkdtemp(prefix="rl_live_")
        fx = ScriptFx({"python.exe ": (1, text)})
        row = L.run(fx, root, "ROT_X", "A2", "python.exe probe.py", "--compose biomes", {}, now=1_800_000_000)
        verified = any(c[:2] == ("rimflow", "verify") for c in fx.calls)
        ok = row["outcome"] == outcome and row["why"].startswith(head) and verified == (outcome == "FAIL")
        if outcome == "UNMEASURED":
            ok = ok and bool(row.get("harness")) == (head == L.HARNESS)
            if head.startswith("the proof exited 1"):
                ok = ok and bool(G.RAN_DUD.search(row["why"]))
            if head == L.RELOAD:
                ok = ok and any(row["why"].startswith(w) for w in G.RESTAGE)
        check("exit 1: %s -> %s" % (text.splitlines()[-1][:50], outcome), ok, row)
    root = tempfile.mkdtemp(prefix="rl_live_")
    fx = ScriptFx({"python3 ": (1, "Traceback (most recent call last):\nrimbridge_client.RimBridgeError: cannot reach the "
                                  "bridge from WSL, and no amount of retrying will fix it."),
                   "python.exe ": (1, "FAIL: 3 null textures")})
    row = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_000)
    check("exit 1: a WSL traceback reruns under python.exe", row["outcome"] == "FAIL" and row.get("rerun")
          == "python.exe probe.py", row)


class ProtoFx(ScriptFx):
    """ScriptFx whose log text may name {run}: the run id the supervisor gives the proof (live_observe.run_id_of)."""
    def run_proof(self, proof, log, timeout):
        self.calls.append(("proof", proof))
        code, text = next((v for k, v in self.codes.items() if proof.startswith(k)), (0, ""))
        with open(log, "w") as f:
            f.write("$ %s\n%s\n" % (proof, text.replace("{run}", L.live_observe.run_id_of(log))))
        return code


def obs(result, stage="result", run="{run}", clause="A2", **kw):
    row = dict(kw, run=run, clause=clause, result=result, stage=stage)
    row.setdefault("expected", ">= 1")
    row.setdefault("observed", 1)
    return "RMOBS " + json.dumps(row)


def t_rmobs_rows_decide_the_run():
    """LIVE_ROWS_FIX_STOP_GUESSING_LOGS: a proof that writes RMOBS rows is judged by them, not by its exit code or a
    verdict-shaped line: a valid VIOLATED is a FAIL even under exit 0 and a later PASS line; a stale run id, a malformed
    row, an observed None without absence, a stop before stage result are UNMEASURED (no verify, no strike); an
    UNREACHED at transport is the harness's; SATISFIED and exit 0 is a PASS; no rows at all falls back to the regexes."""
    cases = [   # (exit, log, outcome, why head, verified, harness)
        (0, obs("VIOLATED", "evaluation", expected=">= 1 RM_Chittik", observed=0, absence=True) + "\nVERDICT PASS",
         "FAIL", "A2 VIOLATED at evaluation", True, False),
        (1, obs("SATISFIED", "observation") + "\nRMOBS {not json\n" + obs("VIOLATED", "evaluation", observed=0,
                                                                          absence=True), "FAIL", "A2 VIOLATED", True,
         False),
        (0, obs("SATISFIED"), "PASS", "A2 SATISFIED", True, False),
        (1, obs("SATISFIED"), "UNMEASURED", "the proof exited 1: it did not measure: INVALID", False, False),
        (0, obs("SATISFIED", run="ROT_X-A2-20270114T080000Z"), "UNMEASURED",
         "the proof exited 0: it did not measure: INVALID", False, False),
        (0, obs("SATISFIED") + "\nRMOBS [1, 2", "UNMEASURED", "the proof exited 0: it did not measure: INVALID", False,
         False),
        (1, obs("VIOLATED", "evaluation", observed=None), "UNMEASURED",
         "the proof exited 1: it did not measure: UNKNOWN", False, False),
        (0, obs("SATISFIED", "observation"), "UNMEASURED", "the proof exited 0: it did not measure: UNKNOWN", False,
         False),
        (2, obs("UNREACHED", "transport", note="bridge refused the connection"), "UNMEASURED", L.HARNESS, False, True),
        (2, obs("UNREACHED", "setup", note="no map"), "UNMEASURED", "the proof exited 2: it did not measure: UNREACHED",
         False, False),
        (0, obs("SATISFIED", clause="A3"), "UNMEASURED", "the proof exited 0: it did not measure: UNKNOWN", False, False),
        (1, "A1 FAIL: no RM_Chittik spawned", "FAIL", "proof exit 1", True, False),
    ]
    import relentless_game as G
    for code, text, outcome, head, verified, harness in cases:
        root = tempfile.mkdtemp(prefix="rl_live_")
        fx = ProtoFx({"python.exe ": (code, text)})
        row = L.run(fx, root, "ROT_X", "A2", "python.exe probe.py", "--compose biomes", {}, now=1_800_000_000)
        v = any(c[:2] == ("rimflow", "verify") for c in fx.calls)
        ok = (row["outcome"] == outcome and row["why"].startswith(head) and v == verified
              and bool(row.get("harness")) == harness
              and (outcome == "UNMEASURED" or row["verdict"] == outcome))
        if outcome == "UNMEASURED" and not harness:
            ok = ok and bool(G.RAN_DUD.search(row["why"]))
        if "RMOBS" in text:
            ok = ok and "observe" in row
        check("rmobs: exit %d %s -> %s" % (code, text.splitlines()[0][:60], outcome), ok, row)
    seen = {}

    class EnvFx(ProtoFx):
        pass
    fx = L.Fx.__new__(L.Fx)
    fx.books = tempfile.mkdtemp(prefix="rl_env_")
    log = os.path.join(fx.books, "ROT_X-A2-20270115T080000Z.log")
    fx.run_proof("echo \"$%s\"" % L.live_observe.RUN_ENV, log, 30)
    seen["env"] = open(log).read()
    check("rmobs: the real run_proof hands the proof its run id", "ROT_X-A2-20270115T080000Z" in seen["env"].split(
        "\n", 1)[1], seen)


def t_same_cause_becomes_one_reload_request():
    """TIDAL_LOCK and HORIZON were noted UNMEASURED every 17 minutes on one game: the third same-cause row is a reload
    request said once, the second and the later ones are rows without a ledger note, and another game starts over."""
    root = tempfile.mkdtemp(prefix="rl_live_")
    notes, whys = [], []
    for i in range(5):
        fx = ScriptFx({"python3 ": (2, "UNMEASURED: map is RM_LeaningScrub at tick %d, not RM_Stillsand" % (600 + i))},
                      started=2000.0 if i < 4 else 3000.0, mtime=1000.0)
        row = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_000 + i)
        notes.append("note" in fx.verbs())
        whys.append(row["why"])
    check("repeat: noted on the 1st, silent on the 2nd, the reload request on the 3rd, silent after, anew on a new game",
          notes == [True, False, True, False, True], (notes, whys))
    check("repeat: the 3rd says reload needed, which relentless_game restages on",
          whys[2].startswith(L.RELOAD) and not whys[3].startswith(L.RELOAD) and not whys[4].startswith(L.RELOAD), whys)
    rows = [json.loads(x) for x in open(os.path.join(root, "live", "runs.jsonl"))]
    check("repeat: the same cause on a second game is a defect, terminal, said once (LIVE_EXIT2_FIX_DEFECT_"
          "AFTER_TWO_GAMES)", whys[4].startswith(L.DEFECT) and rows[4].get("defect") is True
          and not any(r.get("defect") for r in rows[:4]), (whys[4], rows[4]))
    import relentless_live_round as RR
    check("repeat: the defect row decides its build; a reload request does not", RR.decides(rows[4])
          and not RR.decides(rows[2]), rows[2])
    check("repeat: the cause drops numbers and log paths", L.cause("the proof exited 2: x at 601 (/a/b-20261102T1.log)")
          == L.cause("the proof exited 2: x at 7 (/a/c.log)"), L.cause("the proof exited 2: x at 601"))


def t_cap_on_a_proof_that_cannot_measure():
    """PROOF_RERUNS_TAME_UNMEASURED_REPEATS: 53% of runs were UNMEASURED and repeating. The texts below are real rows."""
    def one(root, text, code=2, proof="python.exe probe.py", started=2000.0, now=1_800_000_000):
        fx = ScriptFx({"python": (code, text)}, started=started, mtime=1000.0)
        return L.run(fx, root, "ROT_X", "A2", proof, "--compose biomes", {}, now=now), fx
    for text in ('A6 UNMEASURED: no CLEAN line: {"success": false, "message": "No public static CleanRead with 0 params."}',
                 'A2 UNMEASURED: no droid line: {"success": false, "message": "Type not found: RimMandrake.Property.RM_Droid"}',
                 "UNMEASURED  bridge: bridge call exit 3: REFUSING 'jawa/static_call'\nPass --yes-i-know-this-is-live if you "
                 "really mean it.",
                 "python3: can't open file 'probe.py': [Errno 2]",
                 "probe.py: error: unrecognized arguments: --live",
                 "ModuleNotFoundError: No module named 'numpy'"):
        row, fx = one(tempfile.mkdtemp(prefix="rl_live_"), text)
        check("cap: a broken call is a defect on its FIRST run: %s" % text[:40],
              row.get("defect") is True and row["why"].startswith(L.DEFECT) and "note" in fx.verbs(), row)
    import relentless_live_round as RR
    check("cap: that first row decides its build, so the round never reruns it", RR.decides(row)
          and RR.due(row, row["sha"], 1_800_000_001, 0, row["game"], per_game=False) is not None, row)
    check("cap: the reason it returns with names the call", "numpy" in row["why"], row["why"])
    row, _ = one(tempfile.mkdtemp(prefix="rl_live_"), "UNMEASURED: current map biome ['RM_TheRot'] is not RM_Slime")
    check("cap: a game-state reason is no broken call: it keeps its reload", not row.get("defect"), row)
    row, _ = one(tempfile.mkdtemp(prefix="rl_live_"), "Type not found: X\nreload needed: this list lacks mod Y")
    check("cap: a proof asking for a load is that, whatever else it printed", row["why"].startswith(L.RELOAD)
          and not row.get("defect"), row)
    row, fx = one(tempfile.mkdtemp(prefix="rl_live_"), "No public static X with 0 params", code=0)
    check("cap: exit 0 is a verdict, whatever the log says", row["outcome"] == "PASS" and not row.get("defect"), row)

    # the same proof line on a new build earns one run; the same cause again stops there, on the same game too
    root = tempfile.mkdtemp(prefix="rl_live_")
    os.makedirs(os.path.join(root, "live"))
    old = {"item": "ROT_X", "criterion": "A2", "sha": "0ldbuild0000", "proof": "python.exe probe.py", "outcome": "UNMEASURED",
           "why": "the proof exited 2: it did not measure: A2: UNMEASURED (rides a later load)", "game": "G0"}
    with open(os.path.join(root, "live", "runs.jsonl"), "w") as f:
        f.write(json.dumps(old) + "\n")
    row, _ = one(root, "A2: UNMEASURED (rides a later load)")
    check("cap: same proof, same cause, another build: a defect", row.get("defect") is True and "0ldbuild0000" in row["why"], row)
    root = tempfile.mkdtemp(prefix="rl_live_")
    os.makedirs(os.path.join(root, "live"))
    with open(os.path.join(root, "live", "runs.jsonl"), "w") as f:
        f.write(json.dumps(dict(old, proof="python.exe other.py")) + "\n" + json.dumps(dict(old, criterion="A9")) + "\n"
                + json.dumps(dict(old, why="the proof exited 2: it did not measure: another cause")) + "\n")
    row, _ = one(root, "A2: UNMEASURED (rides a later load)")
    check("cap: another proof line, clause or cause is not the same again", not row.get("defect"), row)

    # the exit reason
    root = tempfile.mkdtemp(prefix="rl_live_")
    row, _ = one(root, "UNMEASURED GeneDef/RSW_TunnelBorn: does not resolve\n\nVERDICT UNMEASURED")
    check("reason: a generic last line gives way to the line that says why", "RSW_TunnelBorn" in row["why"], row["why"])
    row, _ = one(tempfile.mkdtemp(prefix="rl_live_"), "")
    check("reason: nothing printed but the command line is still a row", row["why"].startswith("the proof exited 2"), row["why"])

    # the cause survives the defect's head, or a fixed proof hitting a NEW cause reads as unchanged and is held
    a = "%s: the proof's own call is broken, so a rerun or a reload cannot help: the proof exited 2: it did not measure: %s"
    x, y = a % (L.DEFECT, "No public static CleanRead"), a % (L.DEFECT, "Type not found: Foo")
    check("fingerprint: two defects on one proof line differ", L.fingerprint("A2", x, "p") != L.fingerprint("A2", y, "p"),
          L.cause(x))
    check("fingerprint: one defect is one key however it is headed", L.cause(x) == L.cause(
        "the proof exited 2: it did not measure: No public static CleanRead"), L.cause(x))
    check("cause: a number glued to its unit is still a number", L.cause("REFUSED calls=18 mean=50.176ms")
          == L.cause("REFUSED calls=18 mean=78.934ms"), L.cause("mean=50.176ms"))
    check("cause: a clause id stays", L.cause("A1 x") != L.cause("A2 x"), L.cause("A1 x"))


def t_pass_is_a_verify_on_the_built_sha():
    fx = FakeFx()
    row = go(fx)
    check("pass outcome", row["outcome"] == "PASS", row)
    check("order", fx.verbs() == ["touched", "changed", "plan", "gap", "take", "health", "proof", "release",
                                       "verify"], fx.verbs())
    v = [c for c in fx.calls if c[:2] == ("rimflow", "verify")][0]
    for flag, want in (("--sha", SHA), ("--level", "L1"), ("--criterion", "A2"), ("--result", "pass")):
        check("verify %s" % flag, v[v.index(flag) + 1] == want, v)
    check("released recorded", row.get("released") is True, row)


def t_fail_stands():
    fx = FakeFx(proof=1)
    row = go(fx)
    v = [c for c in fx.calls if c[:2] == ("rimflow", "verify")]
    check("fail outcome", row["outcome"] == "FAIL" and v and v[0][v[0].index("--result") + 1] == "fail", (row, v))


def t_unmeasured_is_a_note_never_a_verify():
    for code in (2, None, 7):
        fx = FakeFx(proof=code)
        row = go(fx)
        check("unmeasured %s" % code, row["outcome"] == "UNMEASURED", row)
        check("no verify %s" % code, "verify" not in fx.verbs() and "note" in fx.verbs(), fx.verbs())
        check("released %s" % code, "release" in fx.verbs(), fx.verbs())


def t_release_survives_a_crashing_proof():
    fx = FakeFx(proof_raises=True)
    row = go(fx)           # go() also asserts exactly one audit row was written
    check("crash is an UNMEASURED row, not an escape", row["outcome"] == "UNMEASURED" and "could not run" in row["why"], row)
    check("released after crash, no verify", "release" in fx.verbs() and "verify" not in fx.verbs(), fx.verbs())


def t_review_round_one():
    # GPT round 1 (2026-11-01): each row red under the mutant that removes its guard
    fx = FakeFx(deleted=["src/RimMandrake/TheRot/Defs/Fauna/Old.xml"])
    row = go(fx)
    check("deleted shipping file is unmeasured", row["outcome"] == "UNMEASURED" and "deleted" in row["why"]
          and not any(v in ("plan", "take", "verify") for v in fx.verbs()), (row, fx.verbs()))
    check("deleted tooling file is fine", go(FakeFx(deleted=["src/RimMandrake/TheRot/validation.py"]))["outcome"] == "PASS")
    fx = FakeFx(release_rc=1)
    row = go(fx)
    check("failed release writes no verdict", row["outcome"] == "UNMEASURED" and "verify" not in fx.verbs(), (row, fx.verbs()))
    fx = FakeFx(start_after_take=3000.0)
    row = go(fx)
    check("game changed while taking the bridge", row["outcome"] == "UNMEASURED" and "verify" not in fx.verbs()
          and "proof" not in fx.verbs(), (row, fx.verbs()))
    for dep in ("--compose biomes --apply", "--apply", "--compose x --ap''ply", "--pull"):
        fx = FakeFx()
        L_row = L.run(fx, tempfile.mkdtemp(prefix="rl_live_"), "ROT_X", "A2", "python3 live_def_check.py", dep, {}, now=1_800_000_000)
        check("deploy %r refused" % dep, L_row["outcome"] == "REFUSED" and "plan" not in fx.verbs(), (L_row, fx.verbs()))
    lr = L.live_rules({})
    for proof in ("python3 modlist_''swap.py --to x", "python3 deploy_custom_mods.py --compose b --ap\\ply",
                  'python3 deploy_custom_mods.py --"apply"'):
        check("quoted evasion refused %r" % proof, L.refused_proof(lr, "t", "c", proof) is not None, proof)
    # a drift in an XML of the same mod the commit did not touch
    plan = PLAN.replace("SWBestiary       mandrake.rsw.swbestiary    98 file(s) HELD\n",
                        "SWBestiary       mandrake.rsw.swbestiary    98 file(s) HELD\n    ~  Defs/Other.xml\n")
    check("untouched xml drift in a shipped mod stops", L.deploy_gap([("SWBestiary", "Defs/A.xml")], 0, plan) is not None)
    held = plan.replace("    ~  Defs/Other.xml\n", "    H  Defs/Other.xml   (repo-only; not deployed)\n")
    check("an untouched held xml does not stop (held out on purpose)",
          L.deploy_gap([("SWBestiary", "Defs/A.xml")], 0, held) is None)
    check("a touched held xml still stops", L.deploy_gap([("SWBestiary", "Defs/Other.xml")], 0, held) is not None)
    check("untouched png drift does not", L.deploy_gap([("SWBestiary", "Defs/A.xml")], 0, PLAN) is None)
    # a timed-out proof's children die with it
    d = tempfile.mkdtemp(prefix="rl_live_")
    pidf = os.path.join(d, "pid")
    code = L.Fx().run_proof("sleep 60 & echo $! > %s; wait" % pidf, os.path.join(d, "log"), 1)
    pid = int(open(pidf).read())
    import time as _t
    _t.sleep(0.3)
    alive = os.path.exists("/proc/%d" % pid) and open("/proc/%d/stat" % pid).read().split()[2] != "Z"
    check("timeout kills the whole group", code is None and not alive, (code, alive))
    # two runs in the same second keep both logs
    r1 = go(FakeFx(proof=1))
    root = tempfile.mkdtemp(prefix="rl_live_")
    logs = set()
    class Writes(FakeFx):
        def run_proof(self, proof, log, timeout):
            open(log, "w").write("x")
            return 0
    for _ in range(2):
        logs.add(L.run(Writes(), root, "ROT_X", "A2", "python3 live_def_check.py", "", {}, now=1_800_000_000)["log"])
    check("same-second logs are distinct", len(logs) == 2 and all(os.path.exists(x) for x in logs), logs)


def t_review_round_two():
    import subprocess

    def git(d, *a):
        return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=d, capture_output=True,
                              text=True, check=True).stdout.strip()
    d = tempfile.mkdtemp(prefix="rl_git_")
    git(d, "init", "-q", "-b", "main")
    mod = os.path.join(d, "src/RimMandrake/TheRot/Defs")
    os.makedirs(mod)
    open(os.path.join(d, "README"), "w").write("a")
    git(d, "add", "."); git(d, "commit", "-qm", "root")
    git(d, "checkout", "-qb", "side")
    open(os.path.join(mod, "\u00c9.xml"), "w").write("<Defs/>")
    git(d, "add", "."); git(d, "commit", "-qm", "adds a non-ascii def")
    built = git(d, "rev-parse", "HEAD")
    fx = L.Fx(books=d)
    check("non-ascii path is the real path", fx.touched(built) == ["src/RimMandrake/TheRot/Defs/\u00c9.xml"], fx.touched(built))
    os.remove(os.path.join(mod, "\u00c9.xml"))
    git(d, "add", "-A"); git(d, "commit", "-qm", "later deletes it")
    check("a path deleted LATER still lists and shows as changed",
          fx.touched(built) == ["src/RimMandrake/TheRot/Defs/\u00c9.xml"]
          and [p for p, _ in fx.changed_since(built, fx.touched(built))] == fx.touched(built), fx.changed_since(built, fx.touched(built)))
    git(d, "checkout", "-q", "main")
    open(os.path.join(d, "README"), "w").write("b")
    git(d, "add", "."); git(d, "commit", "-qm", "readme")
    git(d, "merge", "-q", "--no-ff", "-m", "merge", "side")
    try:
        fx.touched(git(d, "rev-parse", "HEAD"))
        check("merge commit refused", False)
    except ValueError as e:
        check("merge commit refused", "merge" in str(e), str(e))
    lr = L.live_rules({})
    for proof in ("python3 deploy_custom_mods.py --ap$()ply", "python3 modlist_$()swap.py", "x `echo y`", "eval 'a'",
                  "python3 deploy_custom_mods.py \\\n --apply"):
        check("run-time-built proof refused %r" % proof, L.refused_proof(lr, "t", "c", proof) is not None, proof)

    class ReleaseBoom(FakeFx):
        def rimflow(self, *args, timeout=120):
            if args[:2] == ("bridge", "release"):
                raise OSError("release would not run")
            return FakeFx.rimflow(self, *args, timeout=timeout)
    fx = ReleaseBoom()
    row = go(fx)
    check("release exception is an UNMEASURED row", row["outcome"] == "UNMEASURED" and "verify" not in fx.verbs(), row)
    real = C.subprocess.run
    C.subprocess.run = lambda *x, **k: types.SimpleNamespace(returncode=0, stderr="", stdout='{"defs":' + "[" * 300000 + "0" + "]" * 300000 + "}")
    try:
        got = C.call_get_defs(["ThingDef/X"], 5)
    finally:
        C.subprocess.run = real
    check("a reply too deep to decode is no reply, not a crash", got[0] is None, got)
    one = [("ThingDef/X", "1")]
    a = {"requested": "ThingDef/X", "found": True, "fields": {"v": True}}
    b = {"requested": "ThingDef/X", "found": True, "fields": {"v": 1}}
    check("True vs 1 duplicates are UNMEASURED both orders", C.judge(one, {"defs": [a, b]})[0] == C.UNMEASURED
          and C.judge(one, {"defs": [b, a]})[0] == C.UNMEASURED)


def t_review_round_three():
    lr = L.live_rules({})
    for proof in ('arg=--ap; python3 deploy_custom_mods.py --compose b "$arg"ply', "python3 deploy_custom_mods.py --app{ly,}"):
        check("expansion refused %r" % proof, L.refused_proof(lr, "t", "c", proof) is not None, proof)
    class Swap(FakeFx):                     # the owner redeploys and restarts the game DURING the proof
        def run_proof(self, proof, log, timeout):
            self.mt, self.started = 2500.0, 3000.0
            return 0
    for cls in (Swap,):
        fx = cls()
        row = go(fx)
        check("game replaced mid-proof is UNMEASURED", row["outcome"] == "UNMEASURED" and "verify" not in fx.verbs()
              and "while the proof ran" in row["why"], (row, fx.verbs()))
    fx = FakeFx(touched=["src/RimMandrake/TheRot/Defs/A\nB.xml"], started=None)
    row = go(fx)
    check("newline in a shipping path is still a game file", row["outcome"] == "UNMEASURED", row)
    d = tempfile.mkdtemp(prefix="rl_glob_")
    os.makedirs(os.path.join(d, "Bundle/Biomes/TheRot/Defs"))
    open(os.path.join(d, "Bundle/Biomes/TheRot/Defs/A[1].xml"), "w").write("x")
    check("bracket filename is found", len(L.deployed_paths(d, "TheRot", "Defs/A[1].xml")) == 1)
    e = tempfile.mkdtemp(prefix="rl_pg_")
    pidf = os.path.join(e, "pid")
    code = L.Fx().run_proof("sleep 60 & echo $! > %s" % pidf, os.path.join(e, "log"), 20)
    pid = int(open(pidf).read())
    import time as _t
    _t.sleep(0.3)
    alive = os.path.exists("/proc/%d" % pid) and open("/proc/%d/stat" % pid).read().split()[2] != "Z"
    check("a proof that exits leaves no child behind", code == 0 and not alive, (code, alive))
    real = C.subprocess.run
    C.subprocess.run = lambda *x, **k: types.SimpleNamespace(returncode=0, stderr="", stdout='{"defs":[{"requested":"ThingDef/X",'
                                                             '"found":false,"found":true,"fields":{}}]}')
    try:
        got = C.call_get_defs(["ThingDef/X"], 5)
    finally:
        C.subprocess.run = real
    check("repeated JSON key is no reply", got[0] is None, got)
    def boom(*x, **k):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid")
    C.subprocess.run = boom
    try:
        got = C.call_get_defs(["ThingDef/X"], 5)
    finally:
        C.subprocess.run = real
    check("undecodable reply bytes are no reply", got[0] is None, got)
    real_main = C.main
    C.main = lambda argv=None: (_ for _ in ()).throw(UnicodeEncodeError("utf-8", "\ud800", 0, 1, "surrogates"))
    try:
        check("a crash in main exits UNMEASURED, never 1", C.safe_main([]) == C.UNMEASURED)
    finally:
        C.main = real_main


def t_refusals_never_touch_the_bridge():
    cases = {
        "state": FakeFx(it=item(state="ready")),
        "not owed": FakeFx(it=item(outstanding=["A3"])),
        "no such crit": None,
        "flyer title": FakeFx(it=item(title="Skyray flight path holds")),
        "flyer crit": None,
        "forbid": None,
        "bridge busy": FakeFx(take_rc=1),
        "drift": FakeFx(touched=["src/RimMandrake/Contagion/Defs/Other.xml"]),
        "drift plain mod": FakeFx(touched=["src/RimStarWars/SWBestiary/Textures/swanimals/Worrt/WorrtA_north.png"]),
        "held": FakeFx(touched=["src/RimMandrake/Cauldron/northstar/live_works_20261021c.json"]),
        "uncovered": FakeFx(touched=["src/RimMandrake/Pyrelands/Defs/A.xml"]),
        "plan failed": FakeFx(plan=(1, "Traceback")),
        "plan timeout": FakeFx(plan=(None, "the deploy plan took over 500s")),
        "not deployed": FakeFx(plan=(0, PLAN + "Pyrelands        mandrake.rm.pyrelands          NOT DEPLOYED\n"),
                               touched=["src/RimMandrake/Pyrelands/Defs/A.xml"]),
        "no copy": FakeFx(mtime=None),
        "old game": FakeFx(started=999.0),
        "no game": FakeFx(started=None),
    }
    for name, fx in cases.items():
        crit, proof = "A2", "python3 live_def_check.py --has ThingDef/RM_Chittik"
        if name == "no such crit":
            fx, crit = FakeFx(), "A9"
        elif name == "flyer crit":
            fx = FakeFx(it=item(criteria=[{"id": "A2", "level": "L2", "text": "the drone takes off and lands"}]))
        elif name == "forbid":
            fx, proof = FakeFx(), "python3 modlist_swap.py --to minimal && python3 live_def_check.py"
        if name == "L3":
            continue
        row = go(fx, crit=crit, proof=proof)
        check("%s stops" % name, row["outcome"] in ("REFUSED", "UNMEASURED"), row)
        check("%s: no proof" % name, "proof" not in fx.verbs(), fx.verbs())
        check("%s: no ledger verdict" % name, "verify" not in fx.verbs(), fx.verbs())
        if name != "bridge busy":
            check("%s: no bridge" % name, "take" not in fx.verbs() and "release" not in fx.verbs(), fx.verbs())
    fx = FakeFx()
    row = go(fx, crit="A3")
    check("L3 is not live", row["outcome"] == "REFUSED" and "not a live level" in row["why"], row)
    fx = FakeFx(take_rc=1)
    check("busy: no release of another's hold", "release" not in (go(fx), fx.verbs())[1], fx.verbs())


def t_later_commit_is_unmeasured():
    fx = FakeFx(later=[("src/RimMandrake/TheRot/Defs/Fauna/RM_Chittik.xml", "ef081426f0")])
    row = go(fx)
    check("later change: unmeasured", row["outcome"] == "UNMEASURED" and "ef081426f0" in row["why"], row)
    check("later change: no bridge, no verify", not any(v in ("take", "verify", "plan") for v in fx.verbs()),
          fx.verbs())
    fx = FakeFx(later=[("src/RimMandrake/TheRot/validation.py", "ef081426f0")])
    check("tooling change after is fine", go(fx)["outcome"] == "PASS", fx.verbs())


def t_cut_criterion():
    head = "x" * (L.CUT_AT - 11) + " sits still"          # exactly CUT_AT chars, like a ledger copy at the cap
    assert len(head) == L.CUT_AT
    c = {"id": "A2", "level": "L1", "text": head}
    check("short text untouched", L.whole_criterion({"id": "A2", "level": "L1", "text": "short"}, "") ==
          {"id": "A2", "level": "L1", "text": "short"})
    check("cut, no prose -> cut", L.whole_criterion(c, "")["cut"] is True)
    whole = L.whole_criterion(c, "## Criteria\n- A1 L0: other\n- A2 L1: %s and lands, a flyer\n" % head)
    check("cut, prose holds it -> whole", whole["text"].endswith("a flyer") and "cut" not in whole, whole)
    check("other id's line not taken", L.whole_criterion(c, "- A3 L1: %s more\n" % head).get("cut") is True)
    # RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED: GRAFFITI's ledger kept pre-retier text; the refusal must say so
    re_c = L.whole_criterion(c, "A2 L2: on a fresh map, something new\n")
    check("same id, other text -> retiered", re_c.get("cut") is True and re_c.get("retiered") is True, re_c)
    check("no same-id line -> not retiered", "retiered" not in L.whole_criterion(c, "- A3 L1: x\n"))
    it = item()
    it["criteria"] = [dict(cr, cut=True, retiered=True) if cr["id"] == "A2" else cr for cr in it["criteria"]]
    row = go(FakeFx(it=it))
    check("retiered refusal names the re-record", row["outcome"] == "REFUSED" and "re-tiered" in row["why"]
          and "implemented --criteria-file" in row["why"], row)
    it = item()
    it["criteria"] = [dict(cr, cut=True) if cr["id"] == "A2" else cr for cr in it["criteria"]]
    fx = FakeFx(it=it)
    row = go(fx)
    check("cut criterion refused, nothing touched", row["outcome"] == "REFUSED" and "cut" in row["why"]
          and fx.verbs() == [], (row, fx.verbs()))
    it = item()
    it["criteria"] = [dict(cr, text=whole["text"]) if cr["id"] == "A2" else cr for cr in it["criteria"]]
    check("flyer word past the cap is seen", go(FakeFx(it=it))["outcome"] == "REFUSED")


def t_preflight_before_a_slot():
    """LIVE_CUT_CRITERION_ENFORCE_AT_IMPLEMENT, LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT: what a run would refuse whatever the game
    does is known before a game slot is spent, with a fingerprint that moves only when the worker changes something."""
    lr = L.live_rules({})
    ok_line = "python3 live_def_check.py --has ThingDef/RM_Chittik=CompProperties_WoundLink"
    fx = FakeFx()
    check("preflight: a clean build and line has nothing to say", L.preflight(fx, lr, "ROT_X", {"A2": ok_line}) == [],
          L.preflight(fx, lr, "ROT_X", {"A2": ok_line}))
    check("preflight: no bridge, no deploy plan", not any(v in ("take", "plan", "proof") for v in fx.verbs()), fx.verbs())
    it = item()
    it["criteria"] = [dict(cr, cut=True) if cr["id"] == "A2" else cr for cr in it["criteria"]]
    bad = L.preflight(FakeFx(it=it), lr, "ROT_X", {"A2": ok_line, "A3": ok_line})
    check("preflight: a cut criterion is refused, a clause no longer owed is skipped... (A3 is L3: refused as not live)",
          [b["cid"] for b in bad] == ["A2", "A3"] and "cut at" in bad[0]["why"] and bad[0]["kind"] == "refused", bad)
    it2 = item(outstanding=["A3"])
    check("preflight: a criterion not owed is skipped", [b["cid"] for b in
                                                        L.preflight(FakeFx(it=it2), lr, "ROT_X", {"A2": ok_line})] == [])
    bad = L.preflight(FakeFx(), lr, "ROT_X", {"A2": "python3 x.py --tick $N"})
    check("preflight: a $-built line is refused", len(bad) == 1 and "run time" in bad[0]["why"], bad)
    bad = L.preflight(FakeFx(), lr, "ROT_X", {"A2": ok_line}, {"A2": "python3 make_map.py"})
    check("preflight: a live-site command other than live_site.py is refused", len(bad) == 1
          and "live-site" in bad[0]["why"], bad)
    bad = L.preflight(FakeFx(), lr, "ROT_X", {"A2": ok_line + " --flying"})
    check("preflight: a flyer is the game phase's put-down, not a refusal", bad == [], bad)
    fx = FakeFx(later=[("src/RimMandrake/TheRot/Defs/Fauna/RM_Chittik.xml", "ef081426f0")])
    bad = L.preflight(fx, lr, "ROT_X", {"A2": ok_line})
    check("preflight: a stale build is caught once, for the build", [(b["kind"], b["cid"]) for b in bad] ==
          [("stale", None)] and bad[0]["why"].startswith(L.STALE) and "ef081426f0" in bad[0]["why"], bad)
    fx2 = FakeFx(it=item(built_sha="other"), later=fx.later)
    check("preflight: the stale fingerprint moves with the sha",
          L.preflight(fx2, lr, "ROT_X", {"A2": ok_line})[0]["fp"] != bad[0]["fp"])
    f1 = L.fingerprint("A2", "cut at 160 (/a/b.log) 12", ok_line, "text")
    check("fingerprint: paths and numbers in the why do not move it", f1 == L.fingerprint("A2", "cut at 7 (/c.log) 3",
                                                                                          ok_line, "text"))
    check("fingerprint: the text, the proof or the criterion moves it", len({f1, L.fingerprint("A2", "cut", ok_line, "text2"),
          L.fingerprint("A2", "cut", ok_line + " x", "text"), L.fingerprint("A1", "cut", ok_line, "text")}) == 4)


def t_undeployed_row_carries_its_game():
    """relentless_live_round.due retries an undeployed build on another game only, so the row names its game."""
    row = go(FakeFx(gap="not in the running load: RM_Biomes (mandrake.rm.biomes)"))
    check("undeployed: the row has its game", row.get("game"), row)
    row = go(FakeFx(plan=(0, PLAN + "Pyrelands        mandrake.rm.pyrelands          NOT DEPLOYED\n"),
                    touched=["src/RimMandrake/Pyrelands/Defs/A.xml"]))
    check("undeployed (plan): the row has its game", row["why"].startswith(L.UNDEPLOYED) and row.get("game"), row)
    row = go(FakeFx(plan=(1, "Traceback")))
    check("a failed deploy plan is the harness's: no game stamp", not row.get("game"), row)


def t_no_game_files_skips_the_deploy_check():
    fx = FakeFx(touched=["src/RimMandrake/TheRot/validation.py"])
    row = go(fx)
    check("tooling-only commit runs", row["outcome"] == "PASS" and "plan" not in fx.verbs(), (row, fx.verbs()))


def t_plan_reading():
    covered, drift, off = L.plan_sections(PLAN)
    check("covers compose + headers", {"TheRot", "RimMandrake.Biomes", "SWBestiary"} <= covered, covered)
    check("drift rows", ("SWBestiary", "~", "Textures/swanimals/Worrt/WorrtA_north.png") in drift, drift)
    check("held row strips the note", ("RimMandrake.Biomes", "H", "Biomes/Cauldron/northstar/live_works_20261021c.json")
          in drift, drift)
    check("held explanation is not a row", not any("held:" in e for _, _, e in drift), drift)
    check("alias line is not a row", not any("ALIAS" in e for _, _, e in drift), drift)
    check("clean plan, rot file", L.deploy_gap([("TheRot", "Defs/Fauna/RM_Chittik.xml")], 0, PLAN) is None)
    check("same name other mod is not drift",
          L.deploy_gap([("TheRot", "Defs/Other.xml")], 0, PLAN) is None)
    drifted = PLAN                              # the fixture is a real drift plan: it ends in the drift line
    cut = PLAN.replace("Drift found. Re-run with --apply to deploy.", "Traceback (most recent call last):")
    check("exit 1 for other mods' drift is read", L.deploy_gap([("TheRot", "Defs/Fauna/RM_Chittik.xml")], 1, drifted)
          is None)
    check("exit 1 still catches this commit's drift",
          L.deploy_gap([("SWBestiary", "Textures/swanimals/Worrt/WorrtA_north.png")], 1, drifted) is not None)
    check("exit 1 without the drift line fails", L.deploy_gap([("TheRot", "Defs/Fauna/RM_Chittik.xml")], 1, cut)
          is not None)
    check("game_files keeps shipping paths", L.game_files(TOUCHED, FakeFx().shippable)
          == [("TheRot", "Defs/Fauna/RM_Chittik.xml")])


def t_flyer_words():
    lr = L.live_rules({})
    for s in ("a flyer lands", "Flight test", "wings fold", "it takes off", "airborne"):
        check("flyer %r" % s, L.refused_proof(lr, s, "", "") is not None)
    for s in ("Flynn's butterfly net", "inflight", "a fireflies glow", "conflict"):
        check("not flyer %r" % s, L.refused_proof(lr, s, "", "") is None, s)
    # a vehicle's flight is no flyer's (SEABED_DESCENT_ASCENT_1), and every doubt stays refused
    title = "Gravship flies from a sea tile down to its RM_SeabedLayer floor and back up (seabed Phase 2)"
    for s, text, proof in ((title, "after that flight lands", "python3 x.py"), ("The shuttle takes off", "", ""),
                           ("Shuttle test", "it takes off and lands", "")):
        check("vehicle %r" % s, L.refused_proof(lr, s, text, proof) is None, s)
    for s, text, proof in (("Mynock flies around the gravship", "", ""),        # the creature is the subject
                           ("Bird flies past a ship", "", ""),
                           ("Gravship carries a flyer", "", ""),                # a creature word in the title
                           (title, "the flyer lands", ""),                      # ... in a criterion
                           (title, "", "read Pawn_FlightTracker"),              # ... in the proof
                           (title, "its wings fold", ""),
                           ("Relationship flight test", "", ""),                # "ship" as a word, not inside one
                           ("Flight test", "the ship lands", "")):              # a vehicle only outside the title
        check("still a flyer %r %r" % (s, text), L.refused_proof(lr, s, text, proof) is not None, s)


def t_def_check_judge():
    check("defs joined by semicolon", C.defs_param(["ThingDef/A", "ThingDef/B"]) == "ThingDef/A;ThingDef/B")
    claims = C.parse_claims(["ThingDef/RM_Chittik=CompProperties_WoundLink", "ThingDef/RM_Durrok"])
    ok = {"defs": [{"requested": "ThingDef/RM_Chittik", "found": True,
                    "fields": {"comps": [{"compClass": "CompProperties_WoundLink"}]}},
                   {"requested": "ThingDef/RM_Durrok", "found": True, "fields": {}}]}
    check("judge pass", C.judge(claims, ok)[0] == C.PASS, C.judge(claims, ok))
    sub = {"defs": [dict(ok["defs"][0], fields={"comps": ["CompProperties_WoundLinkOld"]}), ok["defs"][1]]}
    check("substring is not a match", C.judge(claims, sub)[0] == C.FAIL, C.judge(claims, sub))
    gone = {"defs": [dict(ok["defs"][0], found=False)]}
    check("FAIL outranks UNMEASURED", C.judge(claims, gone)[0] == C.FAIL, C.judge(claims, gone))
    check("silent def is UNMEASURED", C.judge(claims, {"defs": [ok["defs"][0]]})[0] == C.UNMEASURED)
    check("not an answer", C.judge(claims, {"error": "x"})[0] == C.UNMEASURED)
    one = [("ThingDef/X", "T")]
    for name, rep_ in (("no found", {"requested": "ThingDef/X", "fields": {"a": "T"}}),
                       ("string found", {"requested": "ThingDef/X", "found": "false", "fields": {}}),
                       ("found, no fields", {"requested": "ThingDef/X", "found": True}),
                       ("list requested", {"requested": ["ThingDef/X"], "found": True, "fields": {}}),
                       ("non-dict record", "ThingDef/X")):
        try:
            got = C.judge(one, {"defs": [rep_]})[0]
        except Exception as e:
            got = "crash %r" % e
        check("malformed record %s is UNMEASURED" % name, got == C.UNMEASURED, got)
    two = {"defs": [{"requested": "ThingDef/X", "found": True, "fields": {"a": "T"}},
                    {"requested": "ThingDef/X", "found": False}]}
    check("contradicting duplicates are UNMEASURED", C.judge(one, two)[0] == C.UNMEASURED, C.judge(one, two))
    try:
        C.parse_claims(["ThingDef/X=", "ThingDef/Y= "])
        check("empty token refused", False)
    except ValueError:
        pass
    for bad in ("RM_Chittik", "ThingDef/", "/RM_Chittik=x", "A/B/C"):
        try:
            C.parse_claims([bad])
            check("malformed %r refused" % bad, False)
        except ValueError:
            pass


def t_reload_line_is_the_why():
    """GENERATOR_MODS_PROVE_INERT_AFTER_CREATION: a proof whose list must LACK two mods ran twice on a game holding them,
    exited 2 with 'the proof exited 2: it did not measure', and went back to a worker; no restage was ever asked. A
    proof's or site's own last line `reload needed: ...` is now the row's why (relentless_game RESTAGE)."""
    root = tempfile.mkdtemp(prefix="rl_live_")
    fx = ScriptFx({"python3 probe.py": (2, "UNMEASURED: holds x\nreload needed: restart on a list that lacks x")})
    row = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_000)
    check("reload: a proof's `reload needed:` line is the why", row["outcome"] == "UNMEASURED"
          and row["why"].startswith("reload needed: restart on a list that lacks x"), row)
    fx = ScriptFx({"python.exe src/RimMandrake/Utils/live_site.py": (2, "reload needed: restart on a list that lacks x")})
    row = L.run(fx, root, "ROT_Y", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_001, site=SITE)
    check("reload: a site's `reload needed:` line is the why, no proof run", row["why"].startswith("reload needed: ")
          and [c[1] for c in fx.calls if c[0] == "proof"] == [SITE], row)
    fx = ScriptFx({"python3 probe.py": (2, "reload needed later, maybe")})
    row = L.run(fx, root, "ROT_Z", "A2", "python3 probe.py", "--compose biomes", {}, now=1_800_000_002)
    check("reload: only the exact `reload needed:` prefix counts", row["why"].startswith("the proof exited 2"), row)


def t_unloaded_mod():
    """LIVEDEF_UNLOADED_MOD_FIX_READS_AS_FAIL: an unresolved def is a FAIL only when its mod is in the RUNNING load."""
    import tempfile
    one = [("QuestScriptDef/RUT_Reckoning_Rumor", None)]
    gone = {"defs": [{"requested": "QuestScriptDef/RUT_Reckoning_Rumor", "found": False}]}
    own = {"QuestScriptDef/RUT_Reckoning_Rumor": {"mandrake.utinni.eggreckoning"}}
    check("mod not in the running load is UNMEASURED", C.judge(one, gone, own, {"ludeon.rimworld"})[0] == C.UNMEASURED,
          C.judge(one, gone, own, {"ludeon.rimworld"}))
    check("mod loaded and def missing is FAIL", C.judge(one, gone, own, {"mandrake.utinni.eggreckoning"})[0] == C.FAIL)
    check("running list unread is UNMEASURED", C.judge(one, gone, own, None)[0] == C.UNMEASURED)
    check("owner search failed is UNMEASURED", C.judge(one, gone, {one[0][0]: None}, {"ludeon.rimworld"})[0] == C.UNMEASURED)
    check("a def no repo mod owns stays FAIL", C.judge(one, gone, {}, {"ludeon.rimworld"})[0] == C.FAIL)
    check("FAIL from another claim still stands", C.judge(one + [("ThingDef/X", None)], {"defs": gone["defs"] + [
        {"requested": "ThingDef/X", "found": False}]}, own, {"ludeon.rimworld"})[0] == C.FAIL)
    check("running_ids reads packageIds", C.running_ids({"success": True, "packageIds": ["A.B", "c.d"]}) == {"a.b", "c.d"})
    check("running_ids reads a result wrapper", C.running_ids({"result": {"packageIds": ["A.B"]}}) == {"a.b"})
    for bad in (None, {}, {"packageIds": []}, {"packageIds": "a.b"}, {"packageIds": ["a", 1]}, {"error": "x"}):
        check("running_ids %r is None" % (bad,), C.running_ids(bad) is None)
    with tempfile.TemporaryDirectory() as d:
        for mod, pid, defs in (("ModA", "Mandrake.Utinni.ModA", "RUT_X"), ("ModB", "mandrake.utinni.modb", "RUT_X"),
                               ("Loose", None, "RUT_Y")):
            os.makedirs(os.path.join(d, mod, "1.6", "Defs"))
            if pid:
                os.makedirs(os.path.join(d, mod, "About"))
                with open(os.path.join(d, mod, "About", "About.xml"), "w") as f:
                    f.write("<ModMetaData><packageId>%s</packageId></ModMetaData>" % pid)
            with open(os.path.join(d, mod, "1.6", "Defs", "a.xml"), "w") as f:
                f.write("<Defs><ThingDef><defName>%s</defName></ThingDef></Defs>" % defs)
        got = C.def_owners(["ThingDef/RUT_X", "ThingDef/RUT_Y", "ThingDef/RUT_Z"], d)
        bad = C.def_owners(["ThingDef/RUT_X"], os.path.join(d, "nowhere"))
        check("a failed search owns None", bad == {"ThingDef/RUT_X": None}, bad)
        check("owners from the repo's About.xml", got == {"ThingDef/RUT_X": {"mandrake.utinni.moda", "mandrake.utinni.modb"}},
              got)
    real = C.def_owners(["QuestScriptDef/RUT_Reckoning_Rumor"])
    check("the measured case: RUT_Reckoning_Rumor is EggReckoning's",
          len(real.get("QuestScriptDef/RUT_Reckoning_Rumor", ())) == 1, real)
    calls = []
    real_run = C.subprocess.run

    def fake(cmd, *x, **k):
        if cmd[0] in ("wslpath", "grep"):
            return real_run(cmd, *x, **k) if cmd[0] == "grep" else types.SimpleNamespace(returncode=0, stdout="c", stderr="")
        tool = cmd[cmd.index("--call") + 1]
        calls.append(tool)
        out = gone if tool == "jawa/get_defs" else {"success": True, "packageIds": ["ludeon.rimworld"]}
        return types.SimpleNamespace(returncode=0, stderr="", stdout=json.dumps(out))
    C.subprocess.run = fake
    try:
        code = C.main(["--has", "QuestScriptDef/RUT_Reckoning_Rumor"])
    finally:
        C.subprocess.run = real_run
    check("main asks running_mods and reads UNMEASURED", code == C.UNMEASURED and calls == ["jawa/get_defs", "jawa/running_mods"],
          (code, calls))


def t_load_condition():
    """LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST: --needs/--without guard a criterion's load; a folded member counts as
    loaded when the composed mod runs, for owners and conditions alike."""
    alias = {"mandrake.rm.therot": "mandrake.rm.biomes"}
    run = {"ludeon.rimworld", "mandrake.rm.biomes", "ogliss.thewhitecrayon.quarry"}
    check("no condition: nothing to say", C.condition([], [], None, alias) == (None, []))
    check("needs met", C.condition(["ogliss.thewhitecrayon.quarry"], [], run, alias)[0] is None)
    check("needs met through the composed mod", C.condition(["mandrake.rm.therot"], [], run, alias)[0] is None)
    check("needs missing is UNMEASURED", C.condition(["mandrake.rm.warcasket"], [], run, alias)[0] == C.UNMEASURED)
    check("without present is UNMEASURED", C.condition([], ["ogliss.thewhitecrayon.quarry"], run, alias)[0] == C.UNMEASURED)
    check("without absent is met", C.condition([], ["sarg.alphabiomes"], run, alias)[0] is None)
    check("running unread is UNMEASURED", C.condition(["x.y"], [], None, alias)[0] == C.UNMEASURED)
    check("packageIds compare lower-case", C.condition(["Ogliss.TheWhiteCrayon.Quarry"], [], run, alias)[0] is None)
    own = C.with_aliases({"ThingDef/RM_Chittik": {"mandrake.rm.therot"}, "ThingDef/X": None}, alias)
    check("owners gain the composed id", own == {"ThingDef/RM_Chittik": {"mandrake.rm.therot", "mandrake.rm.biomes"},
                                                 "ThingDef/X": None}, own)
    one = [("ThingDef/RM_Chittik", None)]
    gone = {"defs": [{"requested": "ThingDef/RM_Chittik", "found": False}]}
    check("a composed def missing while the composed mod runs is a FAIL, not UNMEASURED",
          C.judge(one, gone, own, {"mandrake.rm.biomes"})[0] == C.FAIL)
    check("an empty --without is UNMEASURED", C.condition([], [" "], run, alias)[0] == C.UNMEASURED)
    check("--without with a padded id still sees the mod", C.condition([], ["ogliss.thewhitecrayon.quarry "], run,
                                                                      alias)[0] == C.UNMEASURED)
    check("--without with the manifest unread is UNMEASURED (GPT r1)", C.condition([], ["mandrake.rm.therot"], run,
                                                                                    None)[0] == C.UNMEASURED)
    check("--needs with the manifest unread still reads direct ids", C.condition(["ogliss.thewhitecrayon.quarry"], [],
                                                                               run, None)[0] is None)
    check("owners with the manifest unread stay as they are", C.with_aliases({"K": {"a.b"}}, None) == {"K": {"a.b"}})
    real = C.aliases()
    check("the real compose manifest folds TheRot into the composed mod", real.get("mandrake.rm.therot"), real)


def t_prose_holds_the_criteria_file():
    """RELENTLESS_LIVE_REPAIR_QUITS_BEFORE_THE_LOAD: every game clause comes from live_proofs/<ID>.criteria and is cut on
    the ledger; the file holds the whole line, so it is prose, and the round is not REFUSED before the bridge."""
    import tempfile
    b = tempfile.mkdtemp(prefix="rl-prose-")
    os.makedirs(os.path.join(b, "infrastructure/state/items"))
    os.makedirs(os.path.join(b, "infrastructure/state/live_proofs"))
    head = "x" * L.CUT_AT
    with open(os.path.join(b, "infrastructure/state/items/I0.md"), "w") as f:
        f.write("# I0\n- A1 L0: offline\n")
    with open(os.path.join(b, "infrastructure/state/live_proofs/I0.criteria"), "w") as f:
        f.write("A2 L2: %s and the rest\n" % head)
    fx = L.Fx(seat="BENCH")
    fx.books = b
    whole = L.whole_criterion({"id": "A2", "level": "L2", "text": head}, fx.prose("I0"))
    check("the criteria file extends a cut clause", whole["text"].endswith("and the rest") and "cut" not in whole, whole)
    check("the item prose is still read", "A1 L0: offline" in fx.prose("I0"))


def t_running_load_gap_is_unmeasured():
    """owner 2026-11-02: an item fits the game by its RUNNING mods; a build the running list does not load is not run."""
    fx = FakeFx(gap="not in the running load: RM_Biomes (mandrake.rm.biomes)")
    row = go(fx)
    check("gap row unmeasured, restageable", row["outcome"] == "UNMEASURED" and
          row["why"].startswith("not in the running load"), row)
    check("gap: no proof, no verify", "proof" not in fx.verbs() and "verify" not in fx.verbs(), fx.verbs())
    # LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: read before the slot, so a game that cannot serve the run gives it none
    check("gap asked before the bridge, which is never taken", "gap" in fx.verbs() and "take" not in fx.verbs()
          and "release" not in fx.verbs() and row.get("slot") is False, (fx.verbs(), row))
    import relentless_game
    check("the game phase restages on it", any(row["why"].startswith(w) for w in relentless_game.RESTAGE), row["why"])


def t_tiers_small_first_final_last():
    """PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS (owner 2026-11-02: "small mod lists should always be the way to test
    until a final verification pass on the whole huge mod list"): a proof's declared live-mods are gated on the RUNNING
    load even when its commit touched no game file (GRAFFITI A1 failed on a 23-mod game: it was never gated); a GREEN-FULL
    clause is the final verification, and a small game is no FAIL for it: a row, no proof, no ledger note, no restage."""
    import relentless_game
    fx = FakeFx(touched=[], gap="not in the running load: Graffiti (mandrake.rm.graffiti)")
    root = tempfile.mkdtemp(prefix="rl_live_")
    row = L.run(fx, root, "ROT_X", "A2", "python3 x.py", "", {}, now=1_800_000_000, needs=["Graffiti"])
    check("tiers: declared live-mods are gated with no game file touched",
          ("gap", ("Graffiti",)) in fx.calls and row["outcome"] == "UNMEASURED" and "proof" not in fx.verbs(), fx.calls)
    fx = FakeFx(touched=[])
    row = L.run(fx, root, "ROT_X", "A2", "python3 x.py", "", {}, now=1_800_000_000, needs=["Graffiti"])
    check("tiers: a small game holding the mods runs the L1 proof, never asks for the full list",
          row["outcome"] == "PASS" and ("full_gap",) not in fx.calls, fx.calls)
    final = item(criteria=[{"id": "F1", "level": L.FINAL, "text": "the running list equals FULL.LATEST"}],
                 outstanding=["F1"])
    fx = FakeFx(it=final, touched=[], full_gap="%s: the running game has 23 mods, 21 of FULL.LATEST's 316" % L.FINAL_WAIT)
    row = L.run(fx, root, "ROT_X", "F1", "python3 x.py", "", {}, now=1_800_000_000, needs=["Graffiti"])
    check("tiers: a final clause on a small game is UNMEASURED FINAL_WAIT, the proof never runs",
          row["outcome"] == "UNMEASURED" and row["why"].startswith(L.FINAL_WAIT) and "proof" not in fx.verbs()
          and "take" not in fx.verbs() and row.get("slot") is False, (row, fx.verbs()))
    check("tiers: the FINAL_WAIT row carries its game (one row per game, relentless_live_round.due)",
          row.get("game") == L.iso(2000.0), row)
    check("tiers: and no ledger note, no verify", "note" not in fx.verbs() and "verify" not in fx.verbs(), fx.verbs())
    check("tiers: FINAL_WAIT is no restage reason (the batched final load is)",
          not any(row["why"].startswith(w) for w in relentless_game.RESTAGE)
          and relentless_game.FINAL_WAIT == L.FINAL_WAIT and relentless_game.FINAL_LEVEL == L.FINAL, row["why"])
    fx = FakeFx(it=final, touched=[])
    row = L.run(fx, root, "ROT_X", "F1", "python3 x.py", "", {}, now=1_800_000_000)
    check("tiers: on the full list the final proof runs", row["outcome"] == "PASS" and ("full_gap",) in fx.calls, fx.calls)


def t_refusal_row_has_its_sha():
    """LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING: a refusal before the build is read (owed() raising) still names the built
    sha, so relentless_live_round.history counts it as judged on that build; a cut criterion's row says cut."""
    it = item()
    it["criteria"] = [dict(cr, cut=True) if cr["id"] == "A2" else cr for cr in it["criteria"]]
    row = go(FakeFx(it=it))
    check("cut refusal row carries the built sha and cut", row["outcome"] == "REFUSED" and row.get("sha") == SHA
          and row.get("cut") is True, row)
    row = go(FakeFx(it=item(outstanding=["A3"])))
    check("not-owed refusal row carries the built sha, not cut", row["outcome"] == "REFUSED" and row.get("sha") == SHA
          and "cut" not in row, row)


def t_composed_mod_reads_its_parent_about():
    """A folder folded into a composed mod (Stillsand in RimMandrake.Biomes) has no Mods/Stillsand: its packageId is the
    composed mod's (HORIZON_CARAVAN_VANILLA_REFUSES_1 UNMEASURED 'Stillsand has no readable packageId')."""
    import live_def_check
    mods = tempfile.mkdtemp(prefix="rl_mods_")
    os.makedirs(os.path.join(mods, "RimMandrake.Biomes", "About"))
    os.makedirs(os.path.join(mods, "RimMandrake.Biomes", "Biomes", "Stillsand", "Defs"))
    with open(os.path.join(mods, "RimMandrake.Biomes", "About", "About.xml"), "w") as f:
        f.write("<ModMetaData><packageId>mandrake.rm.biomes</packageId><modDependencies><li>"
                "<packageId>brrainz.harmony</packageId></li></modDependencies></ModMetaData>")
    fx = L.Fx(mods_dir=mods)
    old = live_def_check.call_running_mods
    try:
        live_def_check.call_running_mods = lambda t: {"mandrake.rm.biomes", "brrainz.harmony"}
        check("composed: loaded under the composed mod", fx.running_load_gap(["Stillsand"]) is None,
              fx.running_load_gap(["Stillsand"]))
        live_def_check.call_running_mods = lambda t: {"brrainz.harmony"}
        gap = fx.running_load_gap(["Stillsand"]) or ""
        check("composed: the composed mod missing names its packageId", "mandrake.rm.biomes" in gap, gap)
        check("absent mod still has no packageId", "no readable packageId" in (fx.running_load_gap(["Nope"]) or ""))
    finally:
        live_def_check.call_running_mods = old


def main():
    for t in (t_exit1_that_could_not_ask_is_no_fail, t_rmobs_rows_decide_the_run, t_reload_line_is_the_why, t_site_runs_first_and_gates_the_proof, t_wsl_proof_reruns_under_windows_python,
              t_same_cause_becomes_one_reload_request, t_cap_on_a_proof_that_cannot_measure, t_pass_is_a_verify_on_the_built_sha, t_fail_stands, t_later_commit_is_unmeasured, t_cut_criterion, t_prose_holds_the_criteria_file, t_unmeasured_is_a_note_never_a_verify,
              t_release_survives_a_crashing_proof, t_review_round_one, t_review_round_two, t_review_round_three, t_refusals_never_touch_the_bridge,
              t_no_game_files_skips_the_deploy_check, t_plan_reading, t_flyer_words, t_def_check_judge, t_unloaded_mod,
              t_load_condition, t_running_load_gap_is_unmeasured, t_tiers_small_first_final_last,
              t_refusal_row_has_its_sha, t_composed_mod_reads_its_parent_about,
              t_preflight_before_a_slot, t_undeployed_row_carries_its_game):
        try:
            t()
        except Exception as e:     # a crash is a red, named
            FAILS.append((t.__name__, "crashed: %r" % e))
    if FAILS:
        print(json.dumps(FAILS, default=str)[:2000])
    print("selftest_relentless_live:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
