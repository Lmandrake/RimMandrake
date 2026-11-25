#!/usr/bin/env python3
"""Selftest for land.sh: LAND_REPO defaults to the cwd's clone, and a landing realigns the clone (seat_sync)."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LAND = Path(__file__).resolve().parent / "land.sh"
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(cwd, *a):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def land(cwd, *a, env=None):
    e = dict(os.environ)
    e.pop("LAND_REPO", None)
    e.update(env or {})
    return subprocess.run(["sh", str(LAND), *a], cwd=cwd, capture_output=True, text=True, env=e)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        os.environ.update({"HOME": td, "TMPDIR": td, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null",
                           # the "outside a clone" case must never find a real clone above td and land into it
                           "GIT_CEILING_DIRECTORIES": os.path.dirname(td)})
        o, seat, peer = f"{td}/o.git", f"{td}/seat", f"{td}/peer"
        git(td, "init", "-q", "--bare", "-b", "main", o)
        git(td, "clone", "-q", o, seat)
        Path(seat, "a.txt").write_text("a1\n")
        git(seat, "add", "--", "a.txt"); git(seat, "commit", "-q", "-m", "init"); git(seat, "push", "-q", "origin", "HEAD:main")
        git(td, "clone", "-q", o, peer)

        r = land(td, "-m", "x", "a.txt")
        check(r.returncode == 2 and "LAND_REPO is unset" in r.stderr, "outside a clone with no LAND_REPO: refused")

        # sha mode while upstream moved on: lands, then the clone realigns onto the new origin/main
        Path(peer, "p.txt").write_text("p\n")
        git(peer, "add", "--", "p.txt"); git(peer, "commit", "-q", "-m", "peer"); git(peer, "push", "-q", "origin", "HEAD:main")
        Path(seat, "b.txt").write_text("b\n")
        git(seat, "add", "--", "b.txt"); git(seat, "commit", "-q", "-m", "b", "--", "b.txt")
        Path(seat, "dirty.txt").write_text("unrelated\n")
        r = land(seat, git(seat, "rev-parse", "HEAD"), "b.txt")
        out = r.stdout.strip().splitlines()
        check(r.returncode == 0 and len(out) == 1 and out[0].startswith("PUBLISHED "), "sha mode: stdout is one PUBLISHED line")
        new = out[0].split()[1] if out else ""
        check(git(o, "rev-parse", "main") == new, "origin/main is the published sha")
        check(git(seat, "rev-parse", "HEAD") == new and "SYNCED" in r.stderr, "clone defaulted from cwd and realigned to it")
        check(Path(seat, "p.txt").is_file() and Path(seat, "dirty.txt").is_file(), "peer file arrived; unrelated untracked kept")

        # -m mode: the dirty path is published and the clone reads clean afterwards
        Path(seat, "a.txt").write_text("a2\n")
        r = land(seat, "-m", "a2", "a.txt")
        check(r.returncode == 0 and r.stdout.startswith("PUBLISHED"), "-m mode publishes")
        check(git(seat, "rev-parse", "HEAD") == git(o, "rev-parse", "main"), "-m mode: clone realigned")
        check("a.txt" not in git(seat, "status", "--porcelain"), "-m mode: landed path reads clean")

        # an unlanded local commit stays: PUBLISHED still printed, HEAD untouched, reason on stderr
        Path(seat, "c.txt").write_text("c\n")
        git(seat, "add", "--", "c.txt"); git(seat, "commit", "-q", "-m", "c not landed", "--", "c.txt")
        head = git(seat, "rev-parse", "HEAD")
        Path(seat, "a.txt").write_text("a3\n")
        r = land(seat, "-m", "a3", "a.txt")
        check(r.returncode == 0 and r.stdout.startswith("PUBLISHED"), "landing still succeeds with an unlanded local commit")
        check(git(seat, "rev-parse", "HEAD") == head and "NOT on origin/main" in r.stderr, "clone left as is, and says why")

        # losing a push race: a pre-push hook advances origin from the peer once; land.sh rebuilds and retries
        hook = Path(seat, ".git", "hooks", "pre-push")
        hook.write_text(f"#!/bin/sh\n[ -e {td}/raced ] && exit 0\ntouch {td}/raced\n"
                        f"cd {peer} && git pull -q --ff-only origin main && echo r > r.txt && git add r.txt && "
                        f"git commit -qm race && git push -q --no-verify origin HEAD:main\nexit 0\n")
        hook.chmod(0o755)
        Path(seat, "d.txt").write_text("d\n")
        r = land(seat, "-m", "d", "d.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 0 and "rebuilding on the new tip" in r.stderr, "a lost push race is retried on the new tip")
        check("r.txt" in git(o, "ls-tree", "--name-only", "main"), "the racing commit is kept under ours")
        hook.unlink()

        # OPS_TIMER_REPAIR_PRXC_XKGA: the race in the pre-push lint's words. Origin moves after the build, and the
        # ledger lint refuses the stale commit against the newer tip (NOT_APPEND), not git's "rejected": rm-seat-tidy
        # died "push failed" on it six times on Archmagi on 2026-11-23/24. A refusal while origin moved is the race.
        hook.write_text(f"#!/bin/sh\n[ -e {td}/raced2 ] && exit 0\ntouch {td}/raced2\n"
                        f"(cd {peer} && git pull -q --ff-only origin main && echo r2 > r2.txt && git add r2.txt && "
                        f"git commit -qm race2 && git push -q --no-verify origin HEAD:main) >/dev/null 2>&1\n"
                        f"echo 'pre-push REFUSED (ledger_lint) on refs/heads/main:' >&2\n"
                        f"echo '  NOT_APPEND x.jsonl:0 line on the base is gone' >&2\nexit 1\n")
        hook.chmod(0o755)
        Path(seat, "g.txt").write_text("g\n")
        r = land(seat, "-m", "g", "g.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 0 and "rebuilding on the new tip" in r.stderr,
              "a hook refusal while origin moved is the race: rebuilt and retried (rc=%d)" % r.returncode)
        check("r2.txt" in git(o, "ls-tree", "--name-only", "main") and "g.txt" in git(o, "ls-tree", "--name-only", "main"),
              "the hook-race landing keeps the racing commit under ours")
        # a refusal with origin standing still is a verdict on the commit: refused once, never retried
        hook.write_text("#!/bin/sh\necho 'pre-push REFUSED (ledger_lint): a real finding' >&2\nexit 1\n")
        tip = git(o, "rev-parse", "main")
        Path(seat, "h.txt").write_text("h\n")
        r = land(seat, "-m", "h", "h.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "push failed" in r.stderr and "rebuilding" not in r.stderr
              and git(o, "rev-parse", "main") == tip, "a hook refusal with origin unmoved: refused, not retried")
        hook.unlink()
        # a fetch that loses a ref-update race in the clone ("incorrect old value provided") is tried again
        shim = Path(td, "bin")
        shim.mkdir(exist_ok=True)
        real_git = subprocess.run(["sh", "-c", "command -v git"], capture_output=True, text=True).stdout.strip()
        Path(shim, "git").write_text(
            f"#!/bin/sh\nif [ \"$1\" = fetch ] && [ ! -e {td}/fetched ]; then touch {td}/fetched; "
            f"echo 'error: fetching ref refs/remotes/origin/main failed: incorrect old value provided' >&2; exit 1; fi\n"
            f"exec {real_git} \"$@\"\n")
        Path(shim, "git").chmod(0o755)
        Path(seat, "i.txt").write_text("i\n")
        r = land(seat, "-m", "i", "i.txt", env={"LAND_SYNC": "0", "PATH": f"{shim}:{os.environ['PATH']}"})
        check(r.returncode == 0 and r.stdout.startswith("PUBLISHED"),
              "a fetch that collides with a peer's fetch is tried again (rc=%d: %s)" % (r.returncode, r.stderr.strip()[-160:]))

        r = land(seat, "-m", "a3", "a.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "nothing to land" in r.stderr, "re-landing identical content is refused")

        # review wave 87: the guards that keep a landing to the listed paths, each refused with origin untouched
        tip = git(o, "rev-parse", "main")
        Path(seat, "e.txt").write_text("e\n")
        Path(seat, "f.txt").write_text("not listed\n")
        git(seat, "add", "--", "e.txt", "f.txt"); git(seat, "commit", "-q", "-m", "e+f", "--", "e.txt", "f.txt")
        r = land(seat, git(seat, "rev-parse", "HEAD"), "e.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "outside the listed paths" in r.stderr and git(o, "rev-parse", "main") == tip,
              "sha mode: a commit touching an unlisted path is refused, origin unchanged")
        r = land(seat, new, "b.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "already" in r.stderr and git(o, "rev-parse", "main") == tip,
              "sha mode: a commit already on origin is refused")
        r = land(seat, "-m", "typo", "no_such_file.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "not in worktree or origin" in r.stderr and git(o, "rev-parse", "main") == tip,
              "-m mode: a path in neither the worktree nor origin is refused")

        # sha-mode replay onto a moved origin, in a fresh world: the merged tree and the author must be the commit's
        o2, s2, p2 = f"{td}/o2.git", f"{td}/s2", f"{td}/p2"
        git(td, "init", "-q", "--bare", "-b", "main", o2)
        git(td, "clone", "-q", o2, s2)
        body = "".join(f"line {i} of a file long enough for rename detection\n" for i in range(40))
        Path(s2, "ren_a.txt").write_text(body)
        git(s2, "add", "--", "ren_a.txt"); git(s2, "commit", "-q", "-m", "init"); git(s2, "push", "-q", "origin", "HEAD:main")
        git(td, "clone", "-q", o2, p2)

        # RIMMANDRAKE_KEEP_AUTHOR_ON_LAND_REPLAY_COMMIT_TREE: the replayed commit keeps its author and author date
        Path(p2, "q.txt").write_text("q\n")
        git(p2, "add", "--", "q.txt"); git(p2, "commit", "-q", "-m", "peer q"); git(p2, "push", "-q", "origin", "HEAD:main")
        Path(s2, "auth.txt").write_text("authored elsewhere\n")
        git(s2, "add", "--", "auth.txt")
        git(s2, "commit", "-q", "-m", "auth", "--author", "Xavier Q <xq@example.org>",
            "--date", "2001-02-03T04:05:06+00:00", "--", "auth.txt")
        r = land(s2, git(s2, "rev-parse", "HEAD"), "auth.txt", env={"LAND_SYNC": "0"})
        got = git(o2, "log", "-1", "--format=%an|%ae|%at", "main")
        check(r.returncode == 0 and got == "Xavier Q|xq@example.org|981173106",
              f"sha mode: the replayed commit keeps its author and date (got {got!r})")

        # RIMMANDRAKE_SCOPE_LAND_REPLAY_TREE_AFTER_RENAME_MERGE: upstream renamed the listed path; the merge carries
        # our edit to the unlisted new name, so the landing must refuse (it would publish an unchecked path)
        git(p2, "pull", "-q", "--ff-only", "origin", "main")
        git(p2, "mv", "ren_a.txt", "ren_b.txt"); git(p2, "commit", "-q", "-m", "rename"); git(p2, "push", "-q", "origin", "HEAD:main")
        tip2 = git(o2, "rev-parse", "main")
        Path(s2, "ren_a.txt").write_text(body.replace("line 7 of", "LINE SEVEN of"))
        git(s2, "add", "--", "ren_a.txt"); git(s2, "commit", "-q", "-m", "edit a", "--", "ren_a.txt")
        r = land(s2, git(s2, "rev-parse", "HEAD"), "ren_a.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "ren_b.txt" in r.stderr and git(o2, "rev-parse", "main") == tip2,
              f"sha mode: a merge that moves the change onto an unlisted path is refused, origin unchanged "
              f"(rc {r.returncode}: {r.stderr.strip()[-160:]})")

        # Codex review of the fix (RIMMANDRAKE_LITERAL_LAND_PATHSPECS_AND_FETCH_TIP_CODEX_SAW): a newline in a renamed
        # path split into two listed-looking names and passed the scope check
        git(s2, "fetch", "-q", "origin"); git(s2, "reset", "-q", "--hard", "origin/main")
        Path(s2, "nl.txt").write_text(body)
        git(s2, "add", "--", "nl.txt"); git(s2, "commit", "-q", "-m", "nl"); git(s2, "push", "-q", "origin", "HEAD:main")
        git(p2, "pull", "-q", "--ff-only", "origin", "main")
        git(p2, "mv", "nl.txt", "nl.txt\nnl.txt"); git(p2, "commit", "-q", "-m", "nl rename"); git(p2, "push", "-q", "origin", "HEAD:main")
        tip2 = git(o2, "rev-parse", "main")
        Path(s2, "nl.txt").write_text(body.replace("line 9 of", "LINE NINE of"))
        git(s2, "add", "--", "nl.txt"); git(s2, "commit", "-q", "-m", "edit nl", "--", "nl.txt")
        r = land(s2, git(s2, "rev-parse", "HEAD"), "nl.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and git(o2, "rev-parse", "main") == tip2,
              f"sha mode: a renamed path holding a newline is not read as two listed paths (rc {r.returncode})")
        r = land(s2, git(s2, "rev-parse", "HEAD"), "nl.txt", '"nl.txt\\nnl.txt"', env={"LAND_SYNC": "0"})
        check(r.returncode == 2 and "git quotes" in r.stderr and git(o2, "rev-parse", "main") == tip2,
              f"sha mode: listing git's quoted spelling of that path does not let it through (rc {r.returncode})")

        # ... -m mode read a listed path as a glob: 'a[1].txt' also staged a1.txt
        git(s2, "fetch", "-q", "origin"); git(s2, "reset", "-q", "--hard", "origin/main")
        Path(s2, "a[1].txt").write_text("x\n"); Path(s2, "a1.txt").write_text("x\n")
        git(s2, "add", "--", "a[1].txt", "a1.txt"); git(s2, "commit", "-q", "-m", "globs")
        git(s2, "push", "-q", "origin", "HEAD:main")
        Path(s2, "a[1].txt").write_text("y\n"); Path(s2, "a1.txt").write_text("NOT LISTED\n")
        r = land(s2, "-m", "only the bracket file", "a[1].txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 0 and git(o2, "show", "main:a1.txt") == "x" and git(o2, "show", "main:a[1].txt") == "y",
              f"-m mode: a listed path is literal, never a glob (rc {r.returncode})")

        # ... a clone whose fetch refspec has no origin/main: the failed rev-parse printed its argument into UP
        s3 = f"{td}/s3"
        git(td, "clone", "-q", o2, s3)
        git(s3, "config", "remote.origin.fetch", "+refs/heads/topic:refs/remotes/origin/topic")
        git(s3, "update-ref", "-d", "refs/remotes/origin/main")
        tip2 = git(o2, "rev-parse", "main")
        Path(s3, "t.txt").write_text("t\n")
        r = land(s3, "-m", "from a topic-only clone", "t.txt", env={"LAND_SYNC": "0"})
        check(r.returncode == 0 and git(o2, "rev-parse", "main^") == tip2,
              f"-m mode: a clone with no origin/main lands on the fetched tip (rc {r.returncode}: {r.stderr.strip()[-120:]})")
        # RIMMANDRAKE_TRACE_DESIGNER_ROLE_CLONE_VANISHED_OPERATIONS_FAILS: origin changed the commit's file after it was
        # made; land.sh replayed it (PUBLISHED), but seat_sync could not prove the twin (its bytes differ from the
        # commit's), so the clone stayed "ahead 1" and role_clones.level refused every Operations launch STRANDED
        o5, s5, p5 = f"{td}/o5.git", f"{td}/s5", f"{td}/p5"
        git(td, "init", "-q", "--bare", "-b", "main", o5)
        git(td, "clone", "-q", o5, s5)
        # the commit also appends to a merge=union ledger shard, as a role run's fix commit does: the shard's context
        # differs between clone and origin, so `git cherry` reads it '+' and only landed_twin could prove it landed
        Path(s5, ".gitattributes").write_text("*.jsonl merge=union\n")
        Path(s5, "m.py").write_text("".join(f"line {i}\n" for i in range(30)))
        Path(s5, "S.jsonl").write_text('{"e": 0}\n')
        git(s5, "add", "--", ".gitattributes", "m.py", "S.jsonl"); git(s5, "commit", "-q", "-m", "init")
        git(s5, "push", "-q", "origin", "HEAD:main")
        git(td, "clone", "-q", o5, p5)
        Path(s5, "m.py").write_text(Path(s5, "m.py").read_text().replace("line 25\n", "line 25 MINE\n"))
        Path(s5, "S.jsonl").write_text(Path(s5, "S.jsonl").read_text() + '{"e": "mine"}\n')
        git(s5, "commit", "-q", "-m", "mine", "--", "m.py", "S.jsonl")
        Path(p5, "m.py").write_text(Path(p5, "m.py").read_text().replace("line 2\n", "line 2 THEIRS\n"))
        Path(p5, "S.jsonl").write_text(Path(p5, "S.jsonl").read_text() + '{"e": "theirs"}\n')
        git(p5, "commit", "-q", "-m", "theirs", "--", "m.py", "S.jsonl"); git(p5, "push", "-q", "origin", "HEAD:main")
        r = land(s5, git(s5, "rev-parse", "HEAD"), "m.py", "S.jsonl")
        new5 = r.stdout.strip().split()[-1] if r.stdout.strip() else ""
        check(r.returncode == 0 and git(o5, "rev-parse", "main") == new5, "sha mode onto an origin that changed the same file lands")
        check(git(s5, "rev-parse", "HEAD") == new5 and "SYNCED" in r.stderr,
              f"... and the clone realigns: land.sh tells seat_sync the commit it just landed "
              f"(HEAD {git(s5, 'rev-parse', '--short', 'HEAD')}, stderr {r.stderr.strip()[-160:]!r})")
    print(f"{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
