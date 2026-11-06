#!/usr/bin/env python3
"""selftest_proof_sha_cited_mods.py -- a built commit that touched no shippable mod file still deploys and gap-checks
its item's mods (PROOF_SHA_FIX_DEPLOYS_NOTHING_TWICE).

The instance: GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS was built on 8f6c177, then 2e9ce47, commits that touched only proofs
and lessons. relentless_live_round.mods_of read no mod, runs.jsonl wrote deploy='', relentless_live.run checked no
running-load gap, and A1 FAILED twice on a game without GimmeSomeSlack. Now relentless_live.build_shas stands such a
commit for every ancestor whose SUBJECT cites the item. What must hold, each red under its mutant:
  Fx.cited reads a real git history: subject citations only, ancestors of the built sha only, whole-token ids only;
  stale_build without the item is the old empty answer (the instance), with it the cited commits' game files;
  a built commit with game files of its own is not widened; item_mods / mod_gap / batch_gap / run_round name the mod;
  relentless_live.run on such a build checks the mod in the RUNNING load and takes no bridge when it is absent.
"""
import json
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live as L          # noqa: E402
import relentless_live_round as R    # noqa: E402

FAILS = []
ID = "GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS"
MOD_FILE = "src/RimMandrake/GimmeSomeSlack/Defs/Slack.xml"
PROOF_FILE = "infrastructure/state/live_proofs/%s.txt" % ID
GSS_PLAN = """GimmeSomeSlack   mandrake.rm.gimmesomeslack   12 file(s)

Nothing to deploy.
"""


def check(name, cond, detail=""):
    if not cond:
        FAILS.append((name, detail))


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL,
                       env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                GIT_COMMITTER_EMAIL="t@t"))
    if r.returncode:
        raise RuntimeError("git %s: %s" % (args, r.stderr))
    return r.stdout.strip()


def commit(root, path, body, msg):
    p = os.path.join(root, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(body + "\n")
    git(root, "add", path)
    git(root, "commit", "-q", "-m", msg)
    return git(root, "rev-parse", "HEAD")


def history():
    """A temp repo shaped like the instance -> (root, {name: sha})."""
    root = tempfile.mkdtemp(prefix="cited_mods_")
    git(root, "init", "-q", "-b", "main")
    s = {}
    # every fixture folder is a mod the game loads (About/About.xml): stale_build counts only those (fx.deployable)
    for mod in ("Other", "GimmeSomeSlack", "Bystander", "Longer", "Later"):
        commit(root, "src/RimMandrake/%s/About/About.xml" % mod, "<ModMetaData/>", "FIXTURE: %s is a mod" % mod)
    s["other"] = commit(root, "src/RimMandrake/Other/Defs/O.xml", "<o/>", "OTHER_ITEM: unrelated mod work")
    s["mod"] = commit(root, MOD_FILE, "<slack/>", "%s: slice grows with cords" % ID)
    s["body"] = commit(root, "src/RimMandrake/Bystander/Defs/B.xml", "<b/>",
                       "BYSTANDER_X: tidy\n\ncaused_by=%s, only a body mention" % ID)
    s["longer"] = commit(root, "src/RimMandrake/Longer/Defs/L.xml", "<l/>", "%s_2: a longer id is another item" % ID)
    s["proof"] = commit(root, PROOF_FILE, "live-proof A1: true", "%s: A1 names its proof (no mod file)" % ID)
    s["after"] = commit(root, "src/RimMandrake/Later/Defs/L.xml", "<l/>", "%s: a later commit is not the build" % ID)
    return root, s


class GitFx(L.Fx):
    """The real Fx (git reads) with the plan, game and bridge faked; the shippable test is the deploy tool's shape."""

    def __init__(self, root, built, gap=None):
        L.Fx.__init__(self, books=root)
        self.built, self.gap, self.calls = built, gap, []

    def shippable(self, rel):
        return not (rel.endswith(".py") or rel.endswith(".cs"))

    def item(self, item_id):
        return {"id": item_id, "state": "built", "built_sha": self.built, "title": "GSS slice", "outstanding": ["A1"],
                "criteria": [{"id": "A1", "level": "L2", "text": "the slack slice grows with cords on a quicktest map"}]}

    def deploy_plan(self, args, timeout):
        self.calls.append(("plan", args))
        return 0, GSS_PLAN

    def mtime(self, mod, rel):
        return 1000.0

    def game_started(self):
        return 2000.0

    def running_load_gap(self, mods):
        self.calls.append(("gap", tuple(mods)))
        return self.gap

    def full_list_gap(self):
        return None

    def rimflow(self, *args, timeout=120):
        self.calls.append(("rimflow",) + args)
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    def health(self, files, sha, timeout):
        return {"why": None}

    def run_proof(self, proof, log, timeout):
        self.calls.append(("proof", proof))
        return 0

    # RoundFx's surface, for the round helpers
    def mods_of(self, sha):
        return sorted({m for m, _ in L.game_files(self.touched(sha), self.shippable)})

    def folded(self):
        return {}

    def items(self):
        return [self.item(ID)]

    def proofs(self, item_id):
        return "live-proof A1: true\n"


def t_cited_reads_subjects_of_ancestors():
    root, s = history()
    fx = GitFx(root, s["proof"])
    got = fx.cited(ID, s["proof"])
    check("cited: the item's subjects up to the build, newest first", got == [s["proof"], s["mod"]], (got, s))
    check("cited: a body mention, a longer id and a later commit are not the build",
          not {s["body"], s["longer"], s["after"], s["other"]} & set(got), got)
    check("cites: whole token", L.cites("%s: x" % ID, ID) and not L.cites("%s_2: x" % ID, ID)
          and not L.cites("X%s: x" % ID, ID), "")
    return root, s


def t_stale_build_widens_only_a_modless_build(root, s):
    fx = GitFx(root, s["proof"])
    why, files = L.stale_build(fx, s["proof"])
    check("the instance: the proof-only build alone has no game file", why is None and files == [], (why, files))
    short = s["proof"][:10]
    for sha in (s["proof"], short):
        why, files = L.stale_build(fx, sha, ID)
        check("with the item, the cited commit's mod file is the build's (%s)" % len(sha),
              why is None and files == [("GimmeSomeSlack", "Defs/Slack.xml")], (why, files))
    check("build_shas keeps the built commit first, once", L.build_shas(fx, short, ID) == [short, s["mod"]],
          L.build_shas(fx, short, ID))
    check("a build with its own game files is not widened", L.build_shas(fx, s["mod"], ID) == [s["mod"]],
          L.build_shas(fx, s["mod"], ID))


def t_round_helpers_name_the_mod(root, s):
    fx = GitFx(root, s["proof"])
    check("item_mods: the cited mod", R.item_mods(fx, ID, s["proof"]) == ["GimmeSomeSlack"],
          R.item_mods(fx, ID, s["proof"]))
    check("item_mods without the item: the old answer", R.item_mods(fx, None, s["proof"]) == [],
          R.item_mods(fx, None, s["proof"]))
    gap = R.mod_gap(fx, s["proof"], "", running=True, item=ID)
    check("mod_gap plans and gap-checks the cited mod", gap["mods"] == ["GimmeSomeSlack"]
          and ("gap", ("GimmeSomeSlack",)) in fx.calls and any(c[0] == "plan" and "GimmeSomeSlack" in c[1]
                                                               for c in fx.calls), (gap, fx.calls))
    bg = R.batch_gap(fx, [(s["proof"], "", ID), (s["other"], "")])
    check("batch_gap: an item rider adds its cited mod, a two-tuple rider keeps its own",
          bg["mods"] == ["GimmeSomeSlack", "Other"], bg)


def t_run_checks_the_running_load(root, s):
    fx = GitFx(root, s["proof"], gap="not in the running load: GimmeSomeSlack")
    out = tempfile.mkdtemp(prefix="cited_run_")
    row = L.run(fx, out, ID, "A1", "true", "--mod GimmeSomeSlack", {}, now=1_800_000_000)
    check("a GSS-less game: UNMEASURED before any slot", row["outcome"] == "UNMEASURED" and row.get("slot") is False
          and "running load" in (row.get("why") or ""), row)
    check("no bridge taken, no proof run", not any(c[0] == "proof" or c[:2] == ("rimflow", "bridge") for c in fx.calls),
          fx.calls)
    check("the cited file is the run's", row.get("files") == 1, row)
    fx = GitFx(root, s["proof"])
    seen = []

    def fake_run(fx_, root_, item_id, cid, proof, deploy, r, **kw):
        seen.append(deploy)
        return {"item": item_id, "criterion": cid, "outcome": "PASS", "why": "", "sha": s["proof"]}
    R.run_round(fx, out, {}, now=1_800_000_000, run=fake_run, only=ID)
    check("run_round deploys the cited mod", seen == ["--mod GimmeSomeSlack"], seen)


def main():
    root, s = t_cited_reads_subjects_of_ancestors()
    t_stale_build_widens_only_a_modless_build(root, s)
    t_round_helpers_name_the_mod(root, s)
    t_run_checks_the_running_load(root, s)
    for name, detail in FAILS:
        print("FAIL %s: %s" % (name, json.dumps(detail, default=str)[:400]))
    print("selftest_proof_sha_cited_mods: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
