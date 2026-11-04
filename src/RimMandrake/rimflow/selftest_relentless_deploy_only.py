#!/usr/bin/env python3
"""selftest_relentless_deploy_only.py -- RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY: a deploy item reaches the game folder.

A worker may not --apply; only a staging worker may, and it deployed what a commit changed. WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT
changes nothing, so it was taken and blocked with nobody to act. This walks that shape end to end with no game, no bridge
and no ledger: a build that touches no mod file names `live-deploy:` trees; a drifting tree reads UNMEASURED "not deployed"
(no bridge, no proof, no FAIL); the game phase stages; the staging prompt names those mods to apply; in sync, the proof runs.

    python3 src/RimMandrake/rimflow/selftest_relentless_deploy_only.py
"""
import contextlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_game as G                 # noqa: E402
import relentless_live as L                 # noqa: E402
import relentless_live_round as RR          # noqa: E402
import selftest_relentless as S             # noqa: E402
import selftest_relentless_game as SG       # noqa: E402
import selftest_relentless_live as SL       # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import deploy_custom_mods as D              # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
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


def t_production_game_trees():
    """selftest_relentless_game's GW replaces game_trees with a fake, so the walk there cannot see the real one: this reads
    it with git and the deploy tool's own manifest, the proof file committed to a real repo."""
    ok(R.Effects.game_trees is G.GameFx.game_trees, "the supervisor runs GameFx.game_trees, no override")
    real = RR.RoundFx(books=REPO, seat="BENCH").folded()
    ok(bool(real) and "Armoury" not in real, "the instrument sees the real compose manifest", sorted(real)[:3])
    fold = sorted(real)[0]
    with tempfile.TemporaryDirectory() as repo:
        def git(*a):
            return subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
                                  + list(a), check=True, capture_output=True, text=True).stdout.strip()
        git("init", "-q", "-b", "main")
        os.makedirs(os.path.join(repo, G.PROOFS_DIR))

        def put(name, text):
            with open(os.path.join(repo, G.PROOFS_DIR, name + ".txt"), "w", encoding="utf-8") as f:
                f.write(text)
            git("add", ".")
            git("commit", "-qm", name)
            return git("rev-parse", "HEAD")
        plain = put("P", "live-deploy: Doctrine, Armoury\n")
        mixed = put("M", "live-deploy: Armoury, %s\n" % fold)
        other = put("O", "live-deploy: Greentide, Armoury\n")
        none = put("N", "live-mods: Armoury\nlive-proof A2: true\n")
        fx = G.GameFx()
        fx.books, fx.r = repo, {"seat": "BENCH"}
        got = fx.game_trees([("P", plain)])
        ok(got == (["Armoury", "Doctrine"], "--mod Armoury --mod Doctrine"), "real game_trees: the trees and their plan args", got)
        got = fx.game_trees([("M", mixed)])
        ok(got == (sorted(["Armoury", fold]), "--compose biomes --with Armoury"),
           "real game_trees: a folded mod is planned through the composed mod, never --mod %s" % fold, got)
        got = fx.game_trees([("P", plain), ("O", other)])
        ok(got and got[0] == ["Armoury", "Doctrine", "Greentide"], "every build riding the load, once each", got)
        ok(fx.game_trees([("N", none)]) is None, "a live-mods line owes no tree: no DEPLOY ITEM", none)


def deploy_line(prompt):
    """The DEPLOY ITEM line alone: step 1 of the prompt says `then --apply` for any staging, so `"--apply" in prompt` is blind."""
    lines = [x for x in prompt.split("\n") if "DEPLOY ITEM" in x]
    ok(len(lines) == 1, "one DEPLOY ITEM line", lines)
    return lines[0] if lines else ""


def plan_args(line):
    m = re.search(r"`python3 src/RimMandrake/Utils/deploy_custom_mods\.py ([^`]*)`", line)
    return m.group(1) if m else ""


def t_deploy_line_itself():
    p = G.stage_prompt({"item": ITEM, "gen": 1, "game": {}, "_proofs_text": ""}, {"seat": "BENCH"}, "abc",
                       trees=(["Armoury", "Greentide"], "--compose biomes --with Armoury"))
    line = deploy_line(p)
    ok("Armoury, Greentide" in line, "the line names the trees", line)
    ok(plan_args(line) == "--compose biomes --with Armoury", "the line carries the plan command game_trees made", line)
    ok("then the same with --apply" in line, "the line itself says to apply that same command", line)


def t_batch_names_every_tree():
    x = SG.rig(2, share=1.0, max_workers=2)
    x.w.proofs[("I0", ".txt")] = "live-deploy: Armoury\nlive-proof A2: %s\n" % PROOF
    x.w.proofs[("I1", ".txt")] = "live-deploy: Doctrine\nlive-proof A2: %s\n" % PROOF.replace(ITEM, "I1")
    x.w.game_trees = types.MethodType(G.GameFx.game_trees, x.w)
    x.w._round_fx = lambda: types.SimpleNamespace(folded=dict)
    SG.two_in_prove(x)
    x.w.gap = {"I0": SG.GAPS["running"], "I1": SG.GAPS["modsconfig"]}
    with x.s.lock():
        st = x.s.load("I1")
        st["game"].update(phase="stage")
        x.s.save(st)
    x.w.running = False
    G.step(x.s, x.w, x.r, "I0", x.now, [], R)
    G.step(x.s, x.w, x.r, "I0", x.now + 1, [], R)
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging" and st["game"].get("batch") == ["I1"], "two deploy items ride one staging", st["game"])
    line = deploy_line(x.w.launches[-1][2])
    ok(plan_args(line) == "--mod Armoury --mod Doctrine" and "Armoury, Doctrine" in line, "and its one line covers both", line)
    x.done()


ABOUT = "<ModMetaData><name>%s</name><packageId>mandrake.test.%s</packageId></ModMetaData>\n"


@contextlib.contextmanager
def throwaway_world():
    """The real deploy tool over a throwaway repo and game folder (the way selftest_deploy_prune.py drives it): never the
    real Mods folder. Armoury's texture is stale, Doctrine was never deployed, Decoy is stale and no line names it."""
    saved = D.SRC_ROOT, D.HOLD_FILE, D._MODS, D._CONFIG, sys.argv
    tmp = tempfile.mkdtemp(prefix="rl_deploy_world_")

    def write(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    repo, game = os.path.join(tmp, "repo"), os.path.join(tmp, "game")
    for mod in ("Armoury", "Doctrine", "Decoy"):
        write(os.path.join(repo, "RimMandrake", mod, "About", "About.xml"), ABOUT % (mod, mod.lower()))
        write(os.path.join(repo, "RimMandrake", mod, "Textures", "a.png"), "repo %s\n" % mod)
    for mod in ("Armoury", "Decoy"):
        write(os.path.join(game, mod, "About", "About.xml"), ABOUT % (mod, mod.lower()))
        write(os.path.join(game, mod, "Textures", "a.png"), "stale %s\n" % mod)
    cfg = os.path.join(tmp, "ModsConfig.xml")
    write(cfg, "<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>\n"
          % "".join("<li>mandrake.test.%s</li>" % m for m in ("armoury", "doctrine", "decoy")))
    write(os.path.join(tmp, "HOLD.txt"), "")
    D.SRC_ROOT, D.HOLD_FILE = repo, os.path.join(tmp, "HOLD.txt")
    D._MODS, D._CONFIG = [game], [cfg]
    try:
        yield game
    finally:
        D.SRC_ROOT, D.HOLD_FILE, D._MODS, D._CONFIG, sys.argv = saved
        shutil.rmtree(tmp, ignore_errors=True)


def real_tool(args):
    """deploy_custom_mods.py <args> -> (exit, its text), exactly what Fx.deploy_plan reads from the subprocess."""
    sys.argv = ["deploy_custom_mods.py"] + shlex.split(args)
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            rc = D.main() or 0
        except SystemExit as e:
            rc, _ = (e.code, out.write(str(e.code))) if isinstance(e.code, str) else (e.code or 0, None)
    return (rc if isinstance(rc, int) else 1), out.getvalue()


def t_staged_rig_walks_to_a_pass():
    """One continuous walk, supervisor and real deploy tool together: the only hands that apply are the staging worker's, and
    they run the command read off the prompt. If the prompt named the wrong mods the PASS below could not be reached."""
    class Fx(SL.FakeFx):
        def game_started(self): return self.started
        def items(self): return [SL.item(id=ITEM, built_sha=SG.SHA, outstanding=["A2"])]
        def proofs(self, i): return TEXT
        def folded(self): return {}
        def mods_of(self, sha): return []
        def has_mod(self, m): return True
        def deploy_plan(self, args, timeout):
            self.calls.append(("plan", args))
            return real_tool(args)
        def run_proof(self, proof, log, timeout):      # the item's own proof line, on what the throwaway folder holds now
            self.calls.append(("proof", proof))
            ok(proof == PROOF, "the round runs the item's own proof line", proof)
            code, text = RR.deployed(self, ITEM, TEXT)
            with open(log, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            return code

    def round_rows(fx, root, at):   # only=: what the game phase's prove_launch runs, retrying as soon as staging ended
        s = RR.run_round(fx, root, {}, now=at, only=ITEM, run=lambda *a, **k: L.run(*a, **dict(k, now=at)))
        with open(os.path.join(root, "live", "runs.jsonl"), encoding="utf-8") as f:
            return s, [json.loads(z) for z in f]

    def read(game, mod):
        with open(os.path.join(game, mod, "Textures", "a.png"), encoding="utf-8") as f:
            return f.read()

    with throwaway_world() as game, tempfile.TemporaryDirectory() as root:
        x = SG.rig(1)
        x.w.proofs[(ITEM, ".txt")] = TEXT
        x.w.game_trees = types.MethodType(G.GameFx.game_trees, x.w)     # production's, not the rig's fake
        x.w._round_fx = lambda: types.SimpleNamespace(folded=dict)
        SG.to_game(x, ITEM)
        x.tick()
        now = time.time()
        x.w.started = now - 600
        fx = Fx(touched=["infrastructure/state/live_proofs/%s.txt" % ITEM], started=now - 600)
        fx.it = SL.item(id=ITEM, built_sha=SG.SHA, outstanding=["A2"])
        s, x.w.rows = round_rows(fx, root, now + 5)
        ok([r["outcome"] for r in x.w.rows] == ["UNMEASURED"] and x.w.rows[0]["why"].startswith("not deployed"),
           "before staging the real plan reads not deployed, never FAIL", x.w.rows)
        ok("take" not in fx.verbs() and "proof" not in fx.verbs(), "no bridge and no proof spent on it", fx.verbs())
        ok(RR.deployed(fx, ITEM, TEXT)[0] == 1, "the item's proof is red before the deploy")
        for _ in range(3):
            x.tick()
            if x.st(ITEM)["game"]["phase"] == "staging":
                break
        st = x.st(ITEM)
        ok(st["game"]["phase"] == "staging", "the undeployed row stages", st["game"])
        ok(read(game, "Armoury") == "stale Armoury\n", "the supervisor itself wrote nothing to the game folder")

        line = deploy_line(x.w.launches[-1][2])     # from here the test is the staging worker, reading only its prompt
        args = plan_args(line)
        ok(args == "--mod Armoury --mod Doctrine" and "Decoy" not in line, "the line names exactly those mods", line)
        ok("then the same with --apply" in line, "and says to apply that same command", line)
        rc, text = real_tool(args)
        ok(rc == 1 and "Drift found" in text and read(game, "Armoury") == "stale Armoury\n", "the plan writes nothing", (rc, text))
        rc, text = real_tool(args + " --apply")
        ok(rc == 0, "the apply worked", (rc, text[-300:]))
        ok(read(game, "Armoury") == "repo Armoury\n" and read(game, "Doctrine") == "repo Doctrine\n", "both trees are in the folder")
        ok(read(game, "Decoy") == "stale Decoy\n", "and a mod no line names was left alone")

        G.ready(x.s, ITEM, st["gen"], "applied the DEPLOY ITEM line, restarted")
        restarted = time.time() + 30   # after every row so far: a row from the old game says nothing of this one
        x.w.started = fx.started = restarted
        x.tick()        # stopped: the bridge stays held until the unit is down
        x.tick()
        ok(x.w.events[-1] == "release" and x.st(ITEM)["game"]["phase"] == "prove", "ready and down: bridge released, prove", x.w.events[-3:])
        before = len(x.w.proves)
        x.tick()
        ok(len(x.w.proves) == before + 1, "the blind round runs again on the staged rig", x.w.proves)

        fx.calls[:] = []
        s, x.w.rows = round_rows(fx, root, restarted + 5)
        ok([r["outcome"] for r in x.w.rows] == ["UNMEASURED", "PASS"], "the same round tool, the same folder: now the proof PASSes", x.w.rows)
        ok(("proof", PROOF) in fx.calls and "take" in fx.verbs(), "the proof ran, the bridge held", fx.calls)
        x.w.palive = set()
        x.tick()
        ok(x.st(ITEM)["status"] == "game", "the PASS row waits for the ledger's own done", x.st(ITEM)["status"])
        x.w.led[ITEM]["state"] = "done"
        x.tick()
        ok(x.st(ITEM)["status"] == "done", "and the deploy item is done", x.st(ITEM)["status"])
        x.done()


def t_brief():
    text = " ".join(G.BRIEF)
    ok("live-deploy:" in text and "--lint" in text and "you never --apply" in text, "the worker brief teaches the deploy item")
    on = dict(S.RULES, game=dict(G.DEFAULTS, enabled=True))
    ok("live-deploy:" in R.worker_prompt(R.new_state(ITEM, 0, "t"), "x", "", on), "and reaches the worker")


def main():
    for t in (t_lines, t_gap, t_run, t_round_covers_the_trees, t_proof_tool, t_game_stages_and_names_them, t_brief,
              t_production_game_trees, t_deploy_line_itself, t_batch_names_every_tree, t_staged_rig_walks_to_a_pass):
        t()
    print(json.dumps({"fails": len(FAILS) + len(SL.FAILS)}))
    for f in FAILS + SL.FAILS:
        print("FAIL", f)
    return 1 if FAILS or SL.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
