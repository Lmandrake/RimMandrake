#!/usr/bin/env python3
"""Class guard for OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT: a live item's build waiting for the game is never sent back to a
worker as game_stale_build while every later change on its paths is another item's rebuild of the shared assembly,
however many such rebuilds land and whatever other sources they carry; it IS sent back once its own source changes.

The instance (SUMP_TAR_FIRE_NETWORK_1, 2026-11-05): the build 64cfba was carried to 890c85 (GSS_END_HEAPS's rebuild of
RimMandrakeFlowWorks.dll); a later commit changed CordLayer.cs (890c85's source, not the item's) and rebuilt the DLL, and
the next carry was computed from 890c85, so the item went back stale a third time to a worker who could change nothing.

Unlike selftest_relentless_game's carry rows (fake carry answers), this runs the REAL relentless_live.preflight and
relentless_live.carry on a REAL git repo, through the game phase of the supervisor's tick: the chain of commits is the
instance's own shape, then a seeded sweep of other orders. No arguments: every row. Exit 1 on any FAIL."""
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
        self.commit("base", [OWN, DLL] + OTHERS)

    def commit(self, subject, paths):
        for p in paths:
            self.n += 1
            full = os.path.join(self.d, p)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write("%s %d\n" % (p, self.n))
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

    def shippable(self, rel):
        return True


class RealGW(SG.GW):
    """The game rig's world, with preflight and carry answered by relentless_live on the real repo."""

    def __init__(self, repo):
        SG.GW.__init__(self, 1)
        self.repo = repo

    def game_preflight(self, item, lines, sites=None):
        self.pre_calls.append((item, dict(lines)))
        return L.preflight(LFx(self.repo.d, self), L.live_rules({}), item, lines, sites)

    def game_carry(self, item, sha):
        self.carry_calls.append((item, sha))
        try:
            return L.carry(LFx(self.repo.d, self), sha, item)
        except ValueError:
            return None


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
        repo.commit("I0-OTHER: touches the tar fire", [OWN, DLL])
        st, klass = step(x, "own")
        ok(klass == "game_stale_build", "the item's own source changing sends it back stale: %s" % klass)
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


def main():
    t_the_instance()
    t_sweep()
    if S.FAILS:
        print("%d FAIL" % len(S.FAILS))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
