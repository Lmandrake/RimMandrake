#!/usr/bin/env python3
"""Class guard for OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT: a live item's build waiting for the game is never sent back to a
worker as game_stale_build while every later change on its paths is another item's rebuild of the shared assembly,
however many such rebuilds land and whatever other sources they carry; it IS sent back once its own source changes.

The instance (SUMP_TAR_FIRE_NETWORK_1, 2026-11-05): the build 64cfba was carried to 890c85 (GSS_END_HEAPS's rebuild of
RimMandrakeFlowWorks.dll); a later commit changed CordLayer.cs (890c85's source, not the item's) and rebuilt the DLL, and
the next carry was computed from 890c85, so the item went back stale a third time to a worker who could change nothing.

Unlike selftest_relentless_game's carry rows (fake carry answers), this runs the REAL relentless_live.preflight and
relentless_live.carry on a REAL git repo, through the game phase of the supervisor's tick: the chain of commits is the
instance's own shape, then a seeded sweep of other orders. No arguments: every row. Exit 1 on any FAIL.
`--pre-fix` replays the instance as it ran before 6cfce056d6: each carry is computed from the item's CURRENT game sha (the
carried commit), not its origin build. Red there is the guard shown failing on the instance (`rimflow guard --instance`).
`--pre-scope` replays the 5th bounce (18:16Z) as it ran before carry_scope: every src/ path the build touched had to
stand, so the item-citing supervisor fix's rimflow/ file and a SelfTest-only source (no .srchash lists it) refused it."""
import os
import random
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_game as G                 # noqa: E402
import relentless_live as L                 # noqa: E402
import selftest_relentless as S             # noqa: E402
import selftest_relentless_game as SG       # noqa: E402

ok = S.ok
MOD = "src/RimMandrake/FlowWorks/"
DLL = MOD + "Assemblies/RimMandrakeFlowWorks.dll"
OWN = MOD + "Source/TarFire.cs"             # the item's own source
OTHERS = [MOD + "Source/CordLayer.cs", MOD + "Source/HoseNet.cs"]     # other items' sources in the same assembly
ABOUT = MOD + "About/About.xml"             # a mod the game loads
SRCHASH = DLL + ".srchash"                  # what the DLL is compiled from
TESTSRC = MOD + "Source/SelfTest/Program.cs"     # a separate test project: no .srchash lists it
TOOL = "src/RimMandrake/rimflow/relentless_game.py"     # the supervisor's own code: no About.xml, never deployed
SRCHASH_TEXT = "# project: RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj\n# dll: 00\n" + "".join(
    "%02d %s\n" % (i, p[len(MOD + "Source/"):]) for i, p in enumerate([OWN] + OTHERS))


def git(repo, *args):
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr[-300:]))
    return r.stdout.strip()


class Repo(object):
    def __init__(self):
        self.d = tempfile.mkdtemp(prefix="carrychain-")
        self.n = 0
        git(self.d, "init", "-q", "-b", "main")
        git(self.d, "config", "user.email", "t@t")
        git(self.d, "config", "user.name", "t")
        self.commit("base", [OWN, DLL, ABOUT, SRCHASH, TESTSRC, TOOL] + OTHERS)

    def commit(self, subject, paths):
        for p in paths:
            self.n += 1
            full = os.path.join(self.d, p)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(SRCHASH_TEXT + "# n %d\n" % self.n if p == SRCHASH else "%s %d\n" % (p, self.n))
        git(self.d, "add", "--", *paths)
        git(self.d, "commit", "-q", "-m", subject)
        return git(self.d, "rev-parse", "HEAD")


class LFx(L.Fx):
    """The real git half of relentless_live.Fx on the temp repo; the ledger half answered by the rig's world."""

    def __init__(self, books, world):
        L.Fx.__init__(self, books=books)
        self.world = world

    def item(self, item_id):
        led = self.world.game_ledger(item_id)
        return {"id": item_id, "state": led["state"], "built_sha": led["built_sha"], "title": led["title"],
                "criteria": [{"id": "A2", "level": "L1", "text": "a clause"}], "outstanding": []}

    # shippable: the real deploy_custom_mods rule (a .py or a Source/ file never ships), as the supervisor reads it


class RealGW(SG.GW):
    """The game rig's world, with preflight and carry answered by relentless_live on the real repo."""

    def __init__(self, repo):
        SG.GW.__init__(self, 1)
        self.repo = repo

    def game_preflight(self, item, lines, sites=None):
        self.pre_calls.append((item, dict(lines)))
        return L.preflight(LFx(self.repo.d, self), L.live_rules({}), item, lines, sites)

    def game_carry(self, item, sha):
        if PRE_FIX and getattr(self, "cur", None):
            sha = self.cur      # the pre-fix supervisor carried from the sha in the game, not from the origin build
        self.carry_calls.append((item, sha))
        try:
            return L.carry(LFx(self.repo.d, self), sha, item)
        except ValueError:
            return None

    def game_carry_blockers(self, item, sha):
        return L.carry_blockers(LFx(self.repo.d, self), sha, item)


def enter(repo, built):
    """A rig whose one item I0 sits in the game phase on `built`, implemented, no game running."""
    x = S.Rig(1)
    x.w = RealGW(repo)
    x.r = dict(x.r, live=dict(x.r.get("live") or {}, auto=False))
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "python3 selftest_x.py", game=SG.GAME)
    R.finish(x.s, "I0", st["gen"], built, "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    R.verdict(x.s, "I0", st["check"]["nonce"], "PASS", "ran it")
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()
    ok(x.st("I0")["game"]["phase"] == "prove" and x.w.led["I0"]["built_sha"] == built, "entered and implemented on the build")
    x.w.running = False
    return x


def step(x, label):
    x.w.cur = (x.st("I0").get("game") or {}).get("sha")
    x.tick()
    st = x.st("I0")
    return st, (st.get("last_fail") or {}).get("class")


def t_the_instance():
    """The SUMP chain: build, rebuild with another source, rebuild with that SAME other source again, a bare rebuild,
    then the item's own source changes."""
    repo = Repo()
    try:
        built = repo.commit("I0: tar fire network", [OWN, DLL])
        x = enter(repo, built)
        c2 = repo.commit("GSS_END_HEAPS: cord layer", [OTHERS[0], DLL])
        st, klass = step(x, "c2")
        ok(klass is None and st["game"]["sha"] == c2, "another item's rebuild carries the build: %s %s" % (klass, st["game"].get("sha")))
        c3 = repo.commit("OTHER: cord layer again", [OTHERS[0], DLL])
        st, klass = step(x, "c3")
        ok(klass is None and st["game"]["sha"] == c3,
           "THE INSTANCE: the carried commit's own source changing does not send the item back (carried from the origin): "
           "%s %s" % (klass, (st.get("last_fail") or {}).get("detail", "")[:200]))
        c4 = repo.commit("OTHER: bare rebuild", [DLL])
        st, klass = step(x, "c4")
        ok(klass is None and st["game"]["sha"] == c4, "a bare rebuild carries: %s" % klass)
        ok(st["game"]["offline_green"].get("carried_from") == built, "the green still names the origin build")
        own = repo.commit("I0-OTHER: touches the tar fire", [OWN, DLL])
        st, klass = step(x, "own")
        ok(klass == "game_stale_build", "the item's own source changing sends it back stale: %s" % klass)
        detail = (st.get("last_fail") or {}).get("detail", "")
        ok("not carried: since %s" % built[:12] in detail and "%s (%s" % (OWN, own[:7]) in detail and DLL + " (" not in
           detail.split("not carried:")[1],
           "OPS_CHURN_DIAGNOSE_PIT_XGUR_QNTR: the return names the own-source change that stopped the carry, not the DLL: %s"
           % detail[:300])
        x.done()
    finally:
        shutil.rmtree(repo.d, ignore_errors=True)


def t_the_fifth_bounce():
    """SUMP 5th bounce: the build's cited commits include a supervisor fix (rimflow/, its subject cites the item) and a
    SelfTest source; later commits by other items edit both, and rebuild the DLL. Neither reaches the game: carried.
    A DLL source the .srchash lists (another item's) is still carried; the item's own one is not."""
    repo = Repo()
    try:
        repo.commit("I0: tar fire network", [OWN, DLL, SRCHASH, TESTSRC])
        built = repo.commit("I0: a second carry starts from the item's origin build", [TOOL])
        x = enter(repo, built)
        repo.commit("PLANK: its own selftest registers", [TESTSRC])
        repo.commit("PIT: a refused carry names its blockers", [TOOL])
        c = repo.commit("OTHER: rebuild from committed source", [OTHERS[1], DLL, SRCHASH])
        st, klass = step(x, "fifth")
        ok(klass is None and st["game"]["sha"] == c,
           "THE 5TH BOUNCE: a later edit to supervisor code or a SelfTest-only source does not send the item back: %s %s"
           % (klass, (st.get("last_fail") or {}).get("detail", "")[:240]))
        repo.commit("I0-OTHER: touches the tar fire", [OWN, DLL, SRCHASH])
        st, klass = step(x, "own")
        ok(klass == "game_stale_build", "the item's own compiled source changing still sends it back stale: %s" % klass)
        x.done()
    finally:
        shutil.rmtree(repo.d, ignore_errors=True)


def t_sweep(seeds=6, length=5):
    """Seeded orders of other items' commits (another source + rebuild, a bare rebuild, another mod's file): no order
    sends the build back while its own source stands."""
    kinds = ("other+dll", "dll", "elsewhere")
    for seed in range(seeds):
        rnd = random.Random(seed)
        repo = Repo()
        try:
            built = repo.commit("I0: tar fire network", [OWN, DLL])
            x = enter(repo, built)
            seq, bad = [], None
            for i in range(length):
                k = rnd.choice(kinds)
                seq.append(k)
                if k == "other+dll":
                    repo.commit("OTHER%d: source and rebuild" % i, [rnd.choice(OTHERS), DLL])
                elif k == "dll":
                    repo.commit("OTHER%d: rebuild" % i, [DLL])
                else:
                    repo.commit("OTHER%d: elsewhere" % i, ["src/RimMandrake/Elsewhere/Defs/x%d.xml" % i])
                st, klass = step(x, k)
                if klass:
                    bad = (i, klass, (st.get("last_fail") or {}).get("detail", "")[:160])
                    break
            ok(bad is None, "seed %d %s: never back while its own source stands: %s" % (seed, "/".join(seq), bad))
            x.done()
        finally:
            shutil.rmtree(repo.d, ignore_errors=True)


PRE_FIX = False


def main():
    global PRE_FIX
    PRE_FIX = "--pre-fix" in sys.argv[1:]
    L.SCOPE_ALL = "--pre-scope" in sys.argv[1:]
    t_the_instance()
    t_the_fifth_bounce()
    t_sweep()
    if S.FAILS:
        print("%d FAIL" % len(S.FAILS))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
