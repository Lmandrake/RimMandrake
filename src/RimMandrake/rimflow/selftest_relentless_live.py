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
                 verify_rc=0, proof_raises=False, later=(), deleted=(), release_rc=0, start_after_take=None):
        self.later, self.gone, self.release_rc, self.start_after_take = list(later), list(deleted), release_rc, start_after_take
        self.it, self.t, self.plan, self.mt, self.started = (item() if it is None else it), touched, plan, mtime, started
        self.take_rc, self.proof, self.verify_rc, self.proof_raises = take_rc, proof, verify_rc, proof_raises
        self.calls = []

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


def t_pass_is_a_verify_on_the_built_sha():
    fx = FakeFx()
    row = go(fx)
    check("pass outcome", row["outcome"] == "PASS", row)
    check("order", fx.verbs() == ["touched", "changed", "plan", "take", "proof", "release", "verify"], fx.verbs())
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
    it = item()
    it["criteria"] = [dict(cr, cut=True) if cr["id"] == "A2" else cr for cr in it["criteria"]]
    fx = FakeFx(it=it)
    row = go(fx)
    check("cut criterion refused, nothing touched", row["outcome"] == "REFUSED" and "cut" in row["why"]
          and fx.verbs() == [], (row, fx.verbs()))
    it = item()
    it["criteria"] = [dict(cr, text=whole["text"]) if cr["id"] == "A2" else cr for cr in it["criteria"]]
    check("flyer word past the cap is seen", go(FakeFx(it=it))["outcome"] == "REFUSED")


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


def main():
    for t in (t_pass_is_a_verify_on_the_built_sha, t_fail_stands, t_later_commit_is_unmeasured, t_cut_criterion, t_prose_holds_the_criteria_file, t_unmeasured_is_a_note_never_a_verify,
              t_release_survives_a_crashing_proof, t_review_round_one, t_review_round_two, t_review_round_three, t_refusals_never_touch_the_bridge,
              t_no_game_files_skips_the_deploy_check, t_plan_reading, t_flyer_words, t_def_check_judge, t_unloaded_mod,
              t_load_condition):
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
