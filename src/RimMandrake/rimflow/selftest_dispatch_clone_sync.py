#!/usr/bin/env python3
"""selftest_dispatch_clone_sync.py: the tick's clone keeps its ledger lines and stays level with origin/main
(RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL).

The instance, 2026-11-26: at 4:11 AM PST the tick wrote a run.end and a session.id into ExplosiveKnockback's
ledger/DISPATCH.jsonl in /home/mandrake/rm/dispatch. A steward in another clone had appended a stage line to the same
shard on origin at 4:08 AM PST, so origin_views refused the landing ("not a prefix ... pull before landing"), and no
tick tried again. The two lines stayed uncommitted. Each later origin commit that also appended to that shard (the
pass commit 902fc06e35, 9:41 AM PST) made the clone's `git pull --ff-only` refuse, and the clone sat 68 behind.

Each case is real git against a local bare origin, with the real land.sh and seat_sync.py:
  land-ledger-lands-beside-a-peer-append   a peer appended to the same DISPATCH shard on origin; the tick's
                                            land_ledger still lands its own line, both lines are on origin, and the
                                            clone is level and clean after.
  sync-clone-lands-unlanded-lines-and-moves an unlanded line sits in the clone and origin appended to the same file
                                            (the fixture shows `git pull --ff-only` refusing it); sync_clone keeps
                                            both lines, lands the local one and moves the clone level.
  sync-clone-moves-past-a-dirty-view        nothing is unlanded but a derived view is dirty and origin rewrites it
                                            (the ff-only pull refuses); sync_clone still moves the clone level.

Page: design/specs/2026-11-26-tick-clone-sync/boundary.md

    python3 src/RimMandrake/rimflow/selftest_dispatch_clone_sync.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation_dispatch as MD     # noqa: E402
import modledger as ML               # noqa: E402

FAILS = []


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


class Fixture:
    """A bare origin, a peer clone and the tick's clone, with the repo's .gitattributes (merge=union on the shards)."""

    def __init__(self, mod):
        self.tmp = tempfile.mkdtemp(prefix="dispatch_clone_sync_")
        self.mod = mod
        self.rel = "design/concepts/%s/ledger" % mod
        self.origin = os.path.join(self.tmp, "origin.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", self.origin], check=True, timeout=120)
        self.peer = self.clone("peer")
        attrs = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), ".gitattributes")
        shutil.copy(attrs, os.path.join(self.peer, ".gitattributes"))
        ML.grant(self.peer, mod, "L1", version="1")
        self.git(self.peer, "add", ".gitattributes", self.rel)
        self.git(self.peer, "commit", "-q", "-m", "fixture: lease granted")
        self.git(self.peer, "push", "-q", "origin", "HEAD:main")
        self.root = self.clone("dispatch")

    def git(self, repo, *a):
        r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, timeout=120)
        return r.stdout.strip() if r.returncode == 0 else None

    def clone(self, name):
        d = os.path.join(self.tmp, name)
        subprocess.run(["git", "clone", "-q", self.origin, d], check=True, capture_output=True, timeout=120)
        for k, v in (("user.name", "selftest"), ("user.email", "selftest@example.invalid"), ("commit.gpgsign", "false")):
            self.git(d, "config", k, v)
        return d

    def peer_appends(self, move):
        """A steward's maturation.py in another clone: one DISPATCH stage line on the same shard, pushed."""
        self.git(self.peer, "pull", "-q", "--rebase", "origin", "main")
        eid, _ = ML.append(self.peer, self.mod, "DISPATCH", "stage.accepted", "stage", env_writer=None,
                           body={"from": "in_game", "to": "pre_human", "by": "BENCH", "move": move,
                                 "at": "2026-11-26T04:08:48-08:00"})
        self.git(self.peer, "add", self.rel)
        self.git(self.peer, "commit", "-q", "-m", "fixture: a steward appends to the same DISPATCH shard")
        ok(self.git(self.peer, "push", "-q", "origin", "HEAD:main") is not None, "fixture: the peer line is on origin")
        return eid

    def origin_shard(self):
        self.git(self.root, "fetch", "-q", "origin", "main")
        return self.git(self.root, "show", "origin/main:%s/DISPATCH.jsonl" % self.rel) or ""

    def level_and_clean(self):
        self.git(self.root, "fetch", "-q", "origin", "main")
        counts = self.git(self.root, "rev-list", "--left-right", "--count", "HEAD...origin/main")
        dirty = self.git(self.root, "status", "--porcelain", "--", self.rel + "/DISPATCH.jsonl")
        return counts, dirty

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def t_land_ledger_lands_beside_a_peer_append():
    """land_ledger refused on 2026-11-26 4:11 AM PST: origin's DISPATCH.jsonl held a peer's line the clone lacked."""
    fx = Fixture("CloneSyncLandFixture")
    try:
        peer_id = fx.peer_appends(1)
        ML.grant(fx.root, fx.mod, "L2")                 # the tick's own line, blind to the peer's
        mine = [e["id"] for e in ML.read(fx.root, fx.mod) if e.get("_shard") == "DISPATCH"][-1]
        got = MD.land_ledger(fx.root, [fx.mod], "run L2 on %s granted" % fx.mod)
        print("     land_ledger -> %s" % got)
        shard = fx.origin_shard()
        ok(str(got).startswith("PUBLISHED"), "land_ledger_lands_beside_a_peer_append: it lands (read %s)" % got)
        ok(peer_id in shard and mine in shard,
           "land_ledger_lands_beside_a_peer_append: origin holds the peer's line and the tick's line")
        counts, dirty = fx.level_and_clean()
        ok(counts == "0\t0" and not dirty,
           "land_ledger_lands_beside_a_peer_append: the clone is level and its shard clean (counts %r, dirty %r)"
           % (counts, dirty))
    finally:
        fx.close()


def t_sync_clone_lands_unlanded_lines_and_moves():
    """The tick's clone held two unlanded lines; origin appended to the same file; the ff-only pull refused for 30 min."""
    fx = Fixture("CloneSyncPullFixture")
    try:
        ML.grant(fx.root, fx.mod, "L2")                 # a line a refused landing left in the worktree
        mine = [e["id"] for e in ML.read(fx.root, fx.mod) if e.get("_shard") == "DISPATCH"][-1]
        peer_id = fx.peer_appends(1)
        r = subprocess.run(["git", "-C", fx.root, "pull", "-q", "--ff-only", "origin", "main"], capture_output=True,
                           text=True, timeout=120)
        ok(r.returncode != 0, "fixture: `git pull --ff-only` refuses this clone, as on 2026-11-26 (rc %d)" % r.returncode)
        sync = getattr(MD, "sync_clone", None)
        got = sync(fx.root) if sync else "no sync_clone in maturation_dispatch"
        print("     sync_clone -> %s" % got)
        shard = fx.origin_shard()
        ok(peer_id in shard and mine in shard,
           "sync_clone_lands_unlanded_lines_and_moves: origin holds the peer's line and the clone's unlanded line")
        here = open(os.path.join(fx.root, fx.rel, "DISPATCH.jsonl"), encoding="utf-8").read()
        ok(peer_id in here and mine in here, "sync_clone_lands_unlanded_lines_and_moves: the clone keeps both lines")
        counts, dirty = fx.level_and_clean()
        ok(counts == "0\t0" and not dirty,
           "sync_clone_lands_unlanded_lines_and_moves: the clone moved level and its shard is clean (counts %r, "
           "dirty %r)" % (counts, dirty))
    finally:
        fx.close()


def t_sync_clone_moves_past_a_dirty_view():
    """Nothing unlanded, but a derived view in the clone is dirty and origin's next commit rewrites it: the ff-only pull
    refuses, and sync_clone must still move the clone (the view takes origin's bytes; the next append prints it)."""
    fx = Fixture("CloneSyncViewFixture")
    try:
        view = os.path.join(fx.root, fx.rel, "views", "state.md")
        with open(view, "a", encoding="utf-8") as fh:
            fh.write("a half-written view line\n")
        fx.peer_appends(1)
        r = subprocess.run(["git", "-C", fx.root, "pull", "-q", "--ff-only", "origin", "main"], capture_output=True,
                           text=True, timeout=120)
        ok(r.returncode != 0, "fixture: `git pull --ff-only` refuses the dirty view (rc %d)" % r.returncode)
        sync = getattr(MD, "sync_clone", None)
        got = sync(fx.root) if sync else "no sync_clone in maturation_dispatch"
        print("     sync_clone -> %s" % got)
        fx.git(fx.root, "fetch", "-q", "origin", "main")
        counts = fx.git(fx.root, "rev-list", "--left-right", "--count", "HEAD...origin/main")
        ok(counts == "0\t0", "sync_clone_moves_past_a_dirty_view: the clone moved level (counts %r)" % counts)
    finally:
        fx.close()


def main():
    saved = {k: os.environ.pop(k, None) for k in ("RM_STAGE_LAND", "LAND_SYNC", "RM_MODLEDGER_WRITER")}
    try:
        t_land_ledger_lands_beside_a_peer_append()
        t_sync_clone_lands_unlanded_lines_and_moves()
        t_sync_clone_moves_past_a_dirty_view()
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
