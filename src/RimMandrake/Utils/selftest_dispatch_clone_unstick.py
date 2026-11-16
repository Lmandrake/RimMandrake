#!/usr/bin/env python3
"""Selftest: an unattended clone (the dispatch clone the timers run from) can always publish and get level again
(RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD, 2026-11-16: /home/mandrake/rm/dispatch sat behind 29,
its tick's ingest publish refusing "ledger_lint refuses HEAD ... over d9d006f762", a commit already on origin).

  1. A clone merely BEHIND, nothing of its own to push: ingest's publish levels it and reports no refusal. It used to
     hand ledger_lint the stale HEAD, whose shards lack origin's newer lines: NOT_APPEND forever.
  2. The tick's own live append to a mod ledger (design/concepts/<Mod>/ledger/<WRITER>.jsonl) while origin appended
     to it too: the move carries it, as it carries the rimflow shards. Without merge=union on those paths the clone's
     branch could never move again (publish.Stranded on every run).
  3. A mod ledger VIEW (a pure function of the ledger) left dirty and different from origin's: never blocks the move.
  4. The repo's real .gitattributes marks mod ledgers union and their views derived (the test above runs on it).

    python3 src/RimMandrake/Utils/selftest_dispatch_clone_unstick.py
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "testq"))
import selftest_publish as SP  # noqa: E402  its throwaway bare repo + two clones, on ext4
import publish as P  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SHARD = "infrastructure/state/ledger/events/RUNNER.jsonl"
MODLEDGER = "design/concepts/Mod/ledger/DISPATCH.jsonl"
VIEW = "design/concepts/Mod/ledger/views/state.md"


def ev(n, seat="RUNNER"):
    return json.dumps({"seat": seat, "event": "note", "id": "X", "text": "line %d" % n,
                       "ts": "2026-11-16T12:%02d:00Z" % n, "tsn": 1794832000000000000 + n}) + "\n"


def seed(a, b):
    """The real .gitattributes, a rimflow shard, a mod ledger and one of its views, on origin and in both clones."""
    shutil.copy(os.path.join(REPO, ".gitattributes"), os.path.join(a, ".gitattributes"))
    SP.write(a, SHARD, ev(1))
    SP.write(a, MODLEDGER, ev(1, "DISPATCH"))
    SP.write(a, VIEW, "# Mod\nstate: one\n")
    SP.sh(a, "add", ".gitattributes", SHARD, MODLEDGER, VIEW)
    SP.sh(a, "commit", "-q", "-m", "seed ledgers")
    SP.sh(a, "push", "-q", "origin", "HEAD:main")
    SP.sh(b, "pull", "-q", "--rebase")


def ingest_at(a):
    import ingest
    ingest.REPO = a
    return ingest


def head(a):
    return SP.sh(a, "rev-parse", "HEAD")


def origin(a):
    SP.sh(a, "fetch", "-q", "origin")
    return SP.sh(a, "rev-parse", "origin/main")


def t_behind_clone_with_nothing_to_push_levels_and_does_not_refuse(a, b):
    seed(a, b)
    SP.peer_push(b, SHARD, ev(1) + ev(2), "peer ledger line")
    SP.peer_push(b, "f.txt", "moved on\n", "peer code")
    ing = ingest_at(a)
    out = ing._publish(0, shard_rel=SHARD, message="ledger: nothing new")
    assert "publish stopped" not in out and "refuses" not in out and out.endswith("; pushed"), out
    assert head(a) == origin(a), "the clone is still behind: %s" % out


def t_live_mod_ledger_append_is_carried_and_the_branch_moves(a, b):
    seed(a, b)
    SP.peer_push(b, MODLEDGER, ev(1, "DISPATCH") + ev(3, "DISPATCH"), "a peer's mod-ledger line")
    SP.append(a, MODLEDGER, ev(2, "DISPATCH"))                    # the tick's own append, not yet landed
    SP.append(a, SHARD, ev(2))
    ing = ingest_at(a)
    out = ing._publish(1, shard_rel=SHARD, message="ledger: RUNNER 1")
    assert out.endswith("pushed") and "did not move" not in out, out
    assert head(a) == origin(a), "the branch did not move: %s" % out
    got = sorted(open(os.path.join(a, MODLEDGER)))
    assert got == sorted([ev(1, "DISPATCH"), ev(2, "DISPATCH"), ev(3, "DISPATCH")]), got


def t_dirty_view_never_blocks_the_move(a, b):
    seed(a, b)
    SP.peer_push(b, VIEW, "# Mod\nstate: two (a peer regenerated it)\n", "peer view")
    SP.write(a, VIEW, "# Mod\nstate: three (this clone regenerated it)\n")
    SP.append(a, SHARD, ev(2))
    ing = ingest_at(a)
    out = ing._publish(1, shard_rel=SHARD, message="ledger: RUNNER 1")
    assert out.endswith("pushed") and "did not move" not in out, out
    assert head(a) == origin(a), "the branch did not move: %s" % out


def t_repo_marks_mod_ledgers_union_and_views_derived(a, b):
    def attr(name, path):
        r = subprocess.run(["git", "-C", REPO, "check-attr", name, "--", path], capture_output=True, text=True)
        return r.stdout.strip().rsplit(": ", 1)[-1]
    assert attr("merge", "design/concepts/FlowWorks/ledger/DISPATCH.jsonl") == "union"
    assert attr("merge", "design/concepts/FlowWorks/ledger/HOLDER.run-1.jsonl") == "union"
    assert attr("rm-derived", "design/concepts/FlowWorks/ledger/views/state.json") == "set"
    assert attr("merge", "design/concepts/FlowWorks/ledger/views/state.json") != "union"
    assert attr("merge", "design/concepts/FlowWorks/plan.md") == "unspecified"


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("t_")]


def main():
    ok = 0
    for t in TESTS:
        d, a, b = SP.world()
        try:
            t(a, b)
            ok += 1
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print("%d/%d passed" % (ok, len(TESTS)))
    return 0 if ok == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
