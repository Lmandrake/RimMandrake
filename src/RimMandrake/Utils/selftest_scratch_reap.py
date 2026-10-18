#!/usr/bin/env python3
"""Selftest for scratch_reap.py's safety rules: only an old, clean, fully pushed, unmentioned clone or
session dir is deleted; an unpushed commit, a dirty tracked file, an untracked file, a stash, a ledger
mention, a borrower, or youth each REFUSES (or skips) it — and --apply deletes nothing else."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FAILS = []
OLD = 3 * 86400


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout.strip()


def age(d: Path, secs=OLD):
    stamp = __import__("time").time() - secs
    for dp, dns, fns in os.walk(d):
        for n in dns + fns:
            os.utime(os.path.join(dp, n), (stamp, stamp), follow_symlinks=False)
    os.utime(d, (stamp, stamp))


def clone(origin, dest):
    subprocess.run(["git", "clone", "-q", str(origin), str(dest)], check=True, capture_output=True)
    return Path(dest)


def run_reaper(*args):
    import importlib
    import scratch_reap as R
    importlib.reload(R)
    from io import StringIO
    import contextlib
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        R.main(["--json", *args])
    return {Path(r["path"]).name: r for r in json.loads(buf.getvalue())}


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                     "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}.items():
            os.environ[k] = v
        origin = td / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
        seed = clone(origin, td / "seed")
        (seed / "a.txt").write_text("a\n")
        git(seed, "add", "--", "a.txt"); git(seed, "commit", "-q", "-m", "a"); git(seed, "push", "-q", "origin", "HEAD:main")

        root = td / "scratch"
        seat = root / "FOUNDRY"
        seat.mkdir(parents=True)
        corpus = td / "seatclone"
        (corpus / "infrastructure/state/ledger/events").mkdir(parents=True)
        (corpus / "infrastructure/state/items").mkdir(parents=True)
        os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_CORPUS=str(corpus),
                          SCRATCH_REAP_STATE=str(td / "state"), SCRATCH_REAP_TTL_HOURS="24",
                          SCRATCH_REAP_MIRRORS=str(origin))

        clean = clone(origin, seat / "clean_pushed_clone")
        unpushed = clone(origin, seat / "unpushed_clone")
        (unpushed / "b.txt").write_text("b\n"); git(unpushed, "add", "--", "b.txt"); git(unpushed, "commit", "-q", "-m", "only here")
        dirty = clone(origin, seat / "dirty_tracked_clone")
        (dirty / "a.txt").write_text("edited\n")
        untracked = clone(origin, seat / "untracked_file_clone")
        (untracked / "ITEM_PROSE.md").write_text("only copy\n")
        stashed = clone(origin, seat / "stashed_clone")
        (stashed / "a.txt").write_text("stash me\n"); git(stashed, "stash", "-q")
        mentioned = clone(origin, seat / "crackedlands_rename_clone")
        (corpus / "infrastructure/state/ledger/events/FOUNDRY.jsonl").write_text(json.dumps(
            {"event": "note", "id": "CRACKEDLANDS_FULL_RENAME_1",
             "text": "3 commits committed LOCALLY, not pushed, in %s" % (seat / "crackedlands_rename_clone")}) + "\n")
        noremote = seat / "no_remote_clone"
        noremote.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(noremote)], check=True)
        lender = clone(origin, seat / "lender_clone")
        borrower = seat / "borrower_clone"
        subprocess.run(["git", "clone", "-q", "--shared", str(lender), str(borrower)], check=True, capture_output=True)
        young = clone(origin, seat / "young_clone")
        # a commit made here, then pushed by ANOTHER clone: this clone's origin/main ref is stale, but the
        # mirror proves the exact commit is on origin -> deletable
        stale = clone(origin, seat / "stale_ref_clone")
        (stale / "s.txt").write_text("s\n"); git(stale, "add", "--", "s.txt"); git(stale, "commit", "-q", "-m", "pushed elsewhere")
        relay = clone(origin, td / "relay")
        git(relay, "fetch", "-q", str(stale), "main"); git(relay, "merge", "-q", "--ff-only", "FETCH_HEAD")
        git(relay, "push", "-q", "origin", "HEAD:main")
        sess_ok = root / "FOUNDRY" / "claude-1000" / "-proj" / "11111111-2222-3333-4444-555555555555"
        (sess_ok / "scratchpad").mkdir(parents=True)
        (sess_ok / "scratchpad" / "notes.txt").write_text("tmp\n")
        clone(origin, sess_ok / "scratchpad" / "pushclone")
        sess_bad = root / "FOUNDRY" / "claude-1000" / "-proj" / "99999999-8888-7777-6666-555555555555"
        (sess_bad / "scratchpad").mkdir(parents=True)
        inner = clone(origin, sess_bad / "scratchpad" / "rename_work")
        (inner / "c.txt").write_text("c\n"); git(inner, "add", "--", "c.txt"); git(inner, "commit", "-q", "-m", "local only")
        loose = seat / "loose_file.txt"
        loose.write_text("not a clone\n")

        for d in [stale, clean, unpushed, dirty, untracked, stashed, mentioned, noremote, lender, borrower, sess_ok, sess_bad]:
            age(d)

        rows = run_reaper()
        v = {k: r["verdict"] for k, r in rows.items()}
        why = {k: " | ".join(r["why"]) for k, r in rows.items()}
        check(v.get("clean_pushed_clone") == "DELETE", "an old, clean, pushed clone is a DELETE")
        check(v.get("unpushed_clone") == "REFUSE" and "on no remote" in why["unpushed_clone"],
              "a clone with an unpushed commit is REFUSED")
        check(v.get("dirty_tracked_clone") == "REFUSE" and "tracked file(s) changed" in why["dirty_tracked_clone"],
              "a clone with a dirty tracked file is REFUSED")
        check(v.get("untracked_file_clone") == "REFUSE" and "untracked" in why["untracked_file_clone"],
              "a clone with an untracked file (item prose) is REFUSED")
        check(v.get("stashed_clone") == "REFUSE" and "stash" in why["stashed_clone"], "a clone with a stash is REFUSED")
        check(v.get("crackedlands_rename_clone") == "REFUSE" and "names" in why["crackedlands_rename_clone"],
              "a clean, pushed clone the ledger names is REFUSED")
        check(v.get("no_remote_clone") == "REFUSE" and "no remote" in why["no_remote_clone"], "a clone with no remote is REFUSED")
        check(v.get("lender_clone") == "REFUSE" and "borrows" in why["lender_clone"],
              "a clone another clone borrows objects from is REFUSED")
        check(v.get("stale_ref_clone") == "DELETE", "a commit on origin per the mirror counts as pushed despite a stale ref")
        check(v.get("young_clone") == "YOUNG", "a clone touched within the TTL is left alone (YOUNG)")
        check(v.get(sess_ok.name) == "DELETE", "an old session dir whose clones are all pushed is a DELETE")
        check(v.get(sess_bad.name) == "REFUSE" and "on no remote" in why[sess_bad.name],
              "a session dir holding an unpushed clone is REFUSED")
        check("pushclone" not in rows and "rename_work" not in rows, "clones inside a session are judged with it")
        check("loose_file.txt" not in rows, "loose files are never candidates")

        # the dry run deleted nothing
        check(all(p.exists() for p in [clean, sess_ok, unpushed]), "the dry run deletes nothing")

        rows = run_reaper("--apply")
        v = {k: r["verdict"] for k, r in rows.items()}
        check(not clean.exists() and not sess_ok.exists(), "--apply deletes exactly the DELETE rows")
        check(not borrower.exists(), "a clean, pushed BORROWER is deletable (only its lender must stay)")
        check(all(p.exists() for p in [unpushed, dirty, untracked, stashed, mentioned, noremote, lender,
                                         young, sess_bad, loose]),
              "--apply leaves every refused, young or non-candidate path in place")
        check(git(unpushed, "log", "-1", "--format=%s") == "only here", "the unpushed commit survives")
        alarms = (td / "state" / "alarms.log").read_text()
        check("unpushed_clone" in alarms and "crackedlands_rename_clone" in alarms, "refusals are written as alarm lines")
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
