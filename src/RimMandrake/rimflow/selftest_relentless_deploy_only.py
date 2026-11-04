#!/usr/bin/env python3
"""selftest_relentless_deploy_only.py -- RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY: a deploy item reaches the game folder.

A worker may not --apply; only a staging worker may, and it deployed what a commit changed. WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT
changes nothing, so it was taken and blocked with nobody to act. This walks that shape end to end with no game, no bridge
and no ledger: a build that touches no mod file names `live-deploy:` trees; a drifting tree reads UNMEASURED "not deployed"
(no bridge, no proof, no FAIL); the game phase stages; the staging prompt names those mods to apply; in sync, the proof runs.

    python3 src/RimMandrake/rimflow/selftest_relentless_deploy_only.py
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_game as G                 # noqa: E402
import relentless_live as L                 # noqa: E402
import relentless_live_round as RR          # noqa: E402
import selftest_relentless as S             # noqa: E402
import selftest_relentless_game as SG       # noqa: E402
import selftest_relentless_live as SL       # noqa: E402

FAILS = S.FAILS
ITEM = "I0"
PROOF = "python3 src/RimMandrake/rimflow/relentless_live_round.py deployed --item %s" % ITEM
TEXT = "live-deploy: Armoury, Doctrine\nlive-proof A2: %s\n" % PROOF
HEAD = "Armoury  mandrake.rimstarwars.armoury  (in Mods)\nDoctrine  mandrake.rimstarwars.doctrine  (in Mods)\n"
SYNCED = (0, HEAD + "Everything in sync.\n")
TEXTURE_DRIFT = (1, HEAD.replace("Doctrine ", "  ~ Textures/a.png\nDoctrine ", 1) + "Drift found. Re-run with --apply to deploy.\n")
ONLY_GARBAGE = (1, HEAD.replace("Doctrine ", "  - Patches/old.xml\nDoctrine ", 1)
                + "Drift found. Re-run with --apply to deploy.\n")


def ok(cond, what, detail=""):
    S.ok(cond, what + (": %s" % (detail,) if detail and not cond else ""))


def t_lines():
    ok(RR.live_deploy(TEXT) == ["Armoury", "Doctrine"], "live-deploy names the trees")
    ok(RR.live_mods(TEXT) == ["Armoury", "Doctrine"], "a live-deploy mod must also be in the load, as a live-mods one")
    ok(RR.live_deploy("live-mods: Armoury\n") == [], "a live-mods line owes no tree: foreign drift there stays no reason to stage")
    ok(RR.live_mods("live-mods: Armoury\nlive-deploy: Armoury, Doctrine\n") == ["Armoury", "Doctrine"], "no repeats")


def t_gap():
    ok("Armoury" in (L.deploy_gap([], *TEXTURE_DRIFT, trees=["Armoury"]) or ""), "any drifting file of a tree is a gap, a texture too")
    ok(L.deploy_gap([], *TEXTURE_DRIFT, trees=["Doctrine"]) is None, "another mod's drift is not this tree's")
    ok(L.deploy_gap([], *TEXTURE_DRIFT) is None, "with no tree nothing changes for a build's own files")
    ok(L.deploy_gap([], *ONLY_GARBAGE, trees=["Armoury"]) is None, "a - line: --apply would not clear it, so it stages nothing")
    ok("does not cover" in (L.deploy_gap([], 0, "Everything in sync.\n", trees=["Armoury"]) or ""), "a plan missing the mod is a gap")
    held = (1, HEAD.replace("Doctrine ", "  H Patches/held.xml\nDoctrine ", 1) + "Drift found. Re-run with --apply to deploy.\n")
    ok(L.deploy_gap([], *held, trees=["Armoury"]) is None, "a file held on purpose is not drift")


def t_run():
    def go(plan):
        fx = SL.FakeFx(touched=["infrastructure/state/live_proofs/%s.txt" % ITEM], plan=plan)
        root = tempfile.mkdtemp(prefix="rl_deploy_")
        row = L.run(fx, root, "ROT_X", "A2", PROOF, "--mod Armoury --mod Doctrine", {}, now=1_800_000_000,
                    needs=["Armoury", "Doctrine"], trees=["Armoury", "Doctrine"])
        return row, fx.verbs()
    row, verbs = go(TEXTURE_DRIFT)
    ok(row["outcome"] == "UNMEASURED" and row["why"].startswith("not deployed"), "a drifting tree is UNMEASURED not deployed", row)
    ok(any(row["why"].startswith(w) for w in G.RESTAGE), "and that is a word the game phase restages on", row)
    ok("take" not in verbs and "proof" not in verbs, "no bridge and no proof spent on it", verbs)
    row, verbs = go(SYNCED)
    ok(row["outcome"] == "PASS" and "proof" in verbs, "in sync: the proof runs, on a build that changed no mod file", (row, verbs))
    fx = SL.FakeFx(touched=[], plan=TEXTURE_DRIFT)
    row = L.run(fx, tempfile.mkdtemp(prefix="rl_deploy_"), "ROT_X", "A2", PROOF, "", {}, now=1_800_000_000)
    ok(row["outcome"] == "PASS" and ("plan", "") not in fx.calls, "no live-deploy line: no plan, as before", fx.calls)


def t_round_covers_the_trees():
    class Fx(SL.FakeFx):
        def game_started(self): return 2000.0
        def items(self): return [SL.item(id=ITEM, built_sha="sha1", outstanding=["A2"])]
        def proofs(self, i): return TEXT
        def folded(self): return {}
        def mods_of(self, sha): return []
    fx = Fx(touched=[], plan=TEXTURE_DRIFT)
    with tempfile.TemporaryDirectory() as root:
        s = RR.run_round(fx, root, {}, now=1_800_000_000)
    ok(("plan", "--mod Armoury --mod Doctrine") in fx.calls, "the round's plan covers the trees though the build has no mod", fx.calls)
    ok([x["outcome"] for x in s["runs"]] == ["UNMEASURED"] and s["runs"][0]["why"].startswith("not deployed"),
       "and the row says not deployed", s)


def t_proof_tool():
    class Fx(object):
        plan = SYNCED
        def has_mod(self, m): return m != "Lost"
        def folded(self): return {}
        def deploy_plan(self, args, timeout):
            self.args = args
            return self.plan
    fx = Fx()
    ok(RR.deployed(fx, ITEM, TEXT)[0] == 0 and fx.args == "--mod Armoury --mod Doctrine", "in sync exits 0")
    fx.plan = TEXTURE_DRIFT
    ok(RR.deployed(fx, ITEM, TEXT)[0] == 1, "drift exits 1")
    fx.plan = (2, "Traceback")
    ok(RR.deployed(fx, ITEM, TEXT)[0] == 2, "a plan that did not read did not measure: exit 2, never a verdict")
    ok(RR.deployed(fx, ITEM, "nothing\n")[0] == 2, "no live-deploy line did not measure")
    fx.deploy_plan = None
    ok(RR.deployed(fx, ITEM, TEXT, lint=True)[0] == 0, "--lint reads no game folder (no plan)")
    ok(RR.deployed(fx, ITEM, "live-deploy: Lost\nlive-proof A2: %s\n" % PROOF, lint=True)[0] == 1, "--lint: a mod the repo lacks")
    ok(RR.deployed(fx, ITEM, "live-deploy: Armoury\nlive-proof A2: true\n", lint=True)[0] == 1, "--lint: a proof that measures nothing")
    ok(L.refused_proof(L.live_rules({}), "t", "", PROOF) is None, "the live lane accepts the proof line")
    ok(L.refused_proof(L.live_rules({}), "t", "", "python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Armoury --apply"),
       "and still refuses a worker's --apply")


def t_game_stages_and_names_them():
    x = SG.rig(1)
    x.w.proofs[(ITEM, ".txt")] = TEXT
    SG.to_game(x, ITEM)
    x.tick()
    st = x.st(ITEM)
    ok(st["game"]["phase"] == "prove", "the worker's commit changed no mod and still enters the game phase", st["game"])
    now = time.time()
    x.w.started = now - 600
    x.w.rows.append({"item": ITEM, "criterion": "A2", "sha": SG.SHA, "outcome": "UNMEASURED", "at": L.iso(now + 5),
                     "why": "not deployed: Armoury has drift in the game folder (Armoury Textures/a.png)"})
    for _ in range(3):
        x.tick()
        if x.st(ITEM)["game"]["phase"] == "staging":
            break
    st = x.st(ITEM)
    ok(st["game"]["phase"] == "staging" and "take" in x.w.events, "the undeployed row stages, the bridge held", st["game"])
    prompt = x.w.launches[-1][2]
    ok("STAGING" in prompt and "DEPLOY ITEM" in prompt and "Armoury, Doctrine" in prompt
       and "deploy_custom_mods.py --mod Armoury --mod Doctrine" in prompt and "--apply" in prompt,
       "and the staging worker is told to apply exactly those trees", prompt[:600])
    x.done()
    plain = {"item": ITEM, "gen": 1, "game": {}, "_proofs_text": ""}
    p = G.stage_prompt(plain, {"seat": "BENCH"}, "abc")
    ok("DEPLOY ITEM: none" in p, "an ordinary build's staging is told there is none")


def t_brief():
    text = " ".join(G.BRIEF)
    ok("live-deploy:" in text and "--lint" in text and "you never --apply" in text, "the worker brief teaches the deploy item")
    on = dict(S.RULES, game=dict(G.DEFAULTS, enabled=True))
    ok("live-deploy:" in R.worker_prompt(R.new_state(ITEM, 0, "t"), "x", "", on), "and reaches the worker")


def main():
    for t in (t_lines, t_gap, t_run, t_round_covers_the_trees, t_proof_tool, t_game_stages_and_names_them, t_brief):
        t()
    print(json.dumps({"fails": len(FAILS) + len(SL.FAILS)}))
    for f in FAILS + SL.FAILS:
        print("FAIL", f)
    return 1 if FAILS or SL.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
