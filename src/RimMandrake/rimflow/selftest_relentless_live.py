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
                 verify_rc=0, proof_raises=False):
        self.it, self.t, self.plan, self.mt, self.started = (item() if it is None else it), touched, plan, mtime, started
        self.take_rc, self.proof, self.verify_rc, self.proof_raises = take_rc, proof, verify_rc, proof_raises
        self.calls = []

    def item(self, item_id):
        return self.it

    def touched(self, sha):
        self.calls.append(("touched", sha))
        return list(self.t)

    def shippable(self, rel):
        return not (rel.endswith(".py") or rel.endswith(".cs") or "/Source/" in "/" + rel)

    def deploy_plan(self, args, timeout):
        self.calls.append(("plan", args))
        return self.plan

    def mtime(self, mod, rel):
        return self.mt

    def game_started(self):
        return self.started

    def rimflow(self, *args, timeout=120):
        self.calls.append(("rimflow",) + args)
        rc = 0
        if args[:2] == ("bridge", "take"):
            rc = self.take_rc
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
    check("order", fx.verbs() == ["touched", "plan", "take", "proof", "release", "verify"], fx.verbs())
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
    try:
        go(fx)
        check("crash propagates", False)
    except OSError:
        pass
    check("released after crash", fx.verbs()[-1] == "release", fx.verbs())


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
    check("game_files keeps shipping paths", L.game_files(TOUCHED, FakeFx().shippable)
          == [("TheRot", "Defs/Fauna/RM_Chittik.xml")])


def t_flyer_words():
    lr = L.live_rules({})
    for s in ("a flyer lands", "Flight test", "wings fold", "it takes off", "airborne"):
        check("flyer %r" % s, L.refused_proof(lr, s, "", "") is not None)
    for s in ("Flynn's butterfly net", "inflight", "a fireflies glow", "conflict"):
        check("not flyer %r" % s, L.refused_proof(lr, s, "", "") is None, s)


def t_def_check_judge():
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
    for bad in ("RM_Chittik", "ThingDef/", "/RM_Chittik=x", "A/B/C"):
        try:
            C.parse_claims([bad])
            check("malformed %r refused" % bad, False)
        except ValueError:
            pass


def main():
    for t in (t_pass_is_a_verify_on_the_built_sha, t_fail_stands, t_unmeasured_is_a_note_never_a_verify,
              t_release_survives_a_crashing_proof, t_refusals_never_touch_the_bridge,
              t_no_game_files_skips_the_deploy_check, t_plan_reading, t_flyer_words, t_def_check_judge):
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
