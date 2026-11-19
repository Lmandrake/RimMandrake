#!/usr/bin/env python3
"""Selftest for RIMMANDRAKE_REAP_CLONES_WHOSE_LENDER_IS_GONE: a clone whose objects/info/alternates names a lender that was
deleted can no longer read its own refs ("cannot list refs (missing object ...)", or "HEAD is unreadable"), and was
refused every hour, forever: 2026-11-19 13:01Z, 70 refusals, 61 GB, 0 B freed, ~15 of them such clones in /tmp and
.seat-tmp (4.5 GB each, .git ~9 MB, borrowed everything). Their tip commits are on no store at all (measured: not in
bench, not in mirror.git), so pointing the alternates elsewhere cannot make them readable.

Proves, with throwaway fixtures (a lender cloned with --shared, then deleted): such a clone goes, and first its .git
(every object it holds of its own) and every file whose bytes the mirror lacks are archived and restore; a commit made in
the borrower itself is in that archive; a detached HEAD at a lost commit (the tunable_sweep shape) goes the same way;
the row and the manifest say the lender was gone, which a clean clone's row never says; and over the preserve cap it
stays refused. The live-process gate is stubbed, as in selftest_scratch_reap_archive_tags.py.
"""
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selftest_scratch_reap as T  # noqa: E402
from selftest_own_dirs import own_dir  # noqa: E402
from selftest_scratch_reap import R, age, check, clone, commit, git, acts, run_reaper  # noqa: E402


def borrower(lender: Path, dest: Path) -> Path:
    subprocess.run(["git", "clone", "-q", "--shared", str(lender), str(dest)], check=True, capture_output=True)
    return dest


def extracted(kept: Path, td: Path, name: str) -> Path:
    out = td / ("restored_" + name)
    out.mkdir()
    for t in ("dirty.tar.gz",):
        with tarfile.open(kept / t) as tf:
            tf.extractall(out, filter="tar")
    return out


def cases(td: Path, origin: Path):
    root = td / "r_lender"
    s = root / "S"
    s.mkdir(parents=True)
    (td / "archive").mkdir()
    os.environ.update(SCRATCH_REAP_ROOTS=str(root), SCRATCH_REAP_SCAN=str(root), LEFTOVERS_ARCHIVE_ROOT=str(td / "archive"))
    lenders = td / "lenders"            # outside the roots: the reaper never judges them, only their loss

    # 1. a review copy of an unlanded commit; its lender is deleted, its worktree is clean
    l1 = clone(origin, lenders / "l1")
    commit(l1, "w.txt", "work only the lender held")
    b1 = borrower(l1, s / "review_clone")
    tip1 = git(b1, "rev-parse", "HEAD")
    # 2. the borrower made a commit of its own on top, then the lender went
    l2 = clone(origin, lenders / "l2")
    commit(l2, "x.txt", "lender work")
    b2 = borrower(l2, s / "own_commit_clone")
    commit(b2, "y.txt", "a commit made in the borrower")
    own = git(b2, "rev-parse", "HEAD")
    # 3. the tunable_sweep shape: a detached HEAD at a commit only the lender had
    l3 = clone(origin, lenders / "l3")
    commit(l3, "z.txt", "detached work")
    b3 = borrower(l3, s / "detached_clone")
    git(b3, "checkout", "-q", "--detach", git(l3, "rev-parse", "HEAD"))
    # 4. a clean clone with a live lender: the ordinary outcome, for contrast
    b4 = clone(origin, s / "plain_clean_clone")
    for lender in (l1, l2, l3):
        shutil.rmtree(lender)
    for c in (b1, b2, b3, b4):
        age(c)
    st = R.clone_state(b1)
    check(not st["hard"] and any("lender" in x for x in st["soft"]),
          f"a gone lender is a reason to archive, not to refuse (hard={st['hard'][:2]})")

    rc, rows = run_reaper("--apply")
    v = {k: r["verdict"] for k, r in rows.items()}
    print(f"verdicts: {v}")
    check(rc == 0, f"the run succeeds (rc={rc})")
    for name, c in (("review_clone", b1), ("own_commit_clone", b2), ("detached_clone", b3)):
        row = rows.get(name, {})
        check(row.get("verdict") == "DELETED" and not c.exists(), f"{name}: archived, then deleted ({row.get('verdict')})")
        check(any("lender" in w for w in row.get("why", [])), f"{name}: the row says its lender was gone")
    check(v.get("plain_clean_clone") == "DELETED" and not any("lender" in w for w in rows["plain_clean_clone"]["why"])
          and not rows["plain_clean_clone"].get("archive"), "a clean clone is deleted with no archive and no lender note")

    kept = Path(rows.get("review_clone", {}).get("archive", td / "none"))
    m = json.loads((kept / "manifest.json").read_text()) if (kept / "manifest.json").exists() else {}
    check("lender" in (m.get("broken") or ""), f"the manifest records the history as unreadable: {m.get('broken')!r}")
    if (kept / "dirty.tar.gz").exists():
        out = extracted(kept, td, "b1")
        check((out / "w.txt").read_text() == "work only the lender held\n", "a file whose bytes the mirror lacks restores")
        check(not (out / "a.txt").exists(), "a file the mirror holds is not copied")
        check((out / ".git/HEAD").exists() and (out / ".git/index").exists(), "the .git (refs, index) restores")
        check(tip1 in (out / ".git/packed-refs").read_text() + "".join(
            p.read_text() for p in (out / ".git/refs/heads").glob("*")), "the lost tip's id is in the archive")
    else:
        check(False, "the review clone's archive holds a tar")

    kept2 = Path(rows.get("own_commit_clone", {}).get("archive", td / "none"))
    if (kept2 / "dirty.tar.gz").exists():
        out = extracted(kept2, td, "b2")
        r = subprocess.run(["git", "--git-dir", str(out / ".git"), "cat-file", "-p", own], capture_output=True, text=True)
        check(r.returncode == 0 and "a commit made in the borrower" in r.stdout, "the borrower's own commit is in the archive")
        y = subprocess.run(["git", "--git-dir", str(out / ".git"), "cat-file", "-p", own + ":y.txt"], capture_output=True, text=True)
        check((out / "x.txt").exists() and y.returncode == 0 and "borrower" in y.stdout,
              "both files the mirror lacks restore (x.txt from the tar, y.txt from the borrower's own objects)")
    else:
        check(False, "the own-commit clone's archive holds a tar")
    logged = [Path(a.get("path", "")).name for a in acts(td / "archive") if "lender" in a.get("evidence", "")]
    check({"detached_clone", "own_commit_clone", "review_clone"} <= set(logged), f"acts.jsonl records all three ({logged})")

    # 6. a chain (real: /tmp/rim-judge-review.nUCjic/sparse -> its sibling full -> a deleted codex lane clone): the
    #    direct lender lives, the one behind it is gone. Both go, the borrower first (its lender waits for it).
    l6 = clone(origin, lenders / "l6")
    commit(l6, "c.txt", "chained work")
    mid = borrower(l6, s / "chain_mid")
    leaf = borrower(mid, s / "chain_leaf")
    shutil.rmtree(l6)
    for c in (mid, leaf):
        age(c)
    seen = {}
    for _ in range(2):
        rc, rows = run_reaper("--apply")
        seen.update({k: rows[k]["verdict"] for k in ("chain_mid", "chain_leaf") if k in rows})
    check(not leaf.exists() and not mid.exists() and seen.get("chain_leaf") == "DELETED",
          f"a borrower whose lender's lender is gone goes, then that lender ({seen})")

    # 5. over the preserve cap: stays refused, deletes nothing
    l5 = clone(origin, lenders / "l5")
    commit(l5, "big.txt", "x" * 5000)
    b5 = borrower(l5, s / "over_cap_clone")
    shutil.rmtree(l5)
    age(b5)
    cap = R.DIRTY_CAP
    R.DIRTY_CAP = 1000
    try:
        rc, rows = run_reaper("--apply")
    finally:
        R.DIRTY_CAP = cap
    row = rows.get("over_cap_clone", {})
    check(row.get("verdict") == "REFUSE" and b5.exists() and any("cap" in w for w in row.get("why", [])),
          f"over the cap it stays ({row.get('verdict')}: {row.get('why', [''])[:1]})")


def main() -> int:
    lock = None if os.environ.get("SCRATCH_REAP_SELFTEST_ONCE") else T.serial_lock()   # noqa: F841 (held for the run)
    with own_dir("scratch_reap_gone_lender", dir="/tmp") as tds:
        td = Path(tds)
        os.environ.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
                          GIT_CONFIG_GLOBAL="/dev/null")
        origin = td / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
        seed = clone(origin, td / "seed")
        commit(seed, "a.txt", "a")
        git(seed, "push", "-q", "origin", "HEAD:main")
        st = td / "corpus/infrastructure/state"
        for x in ("handoffs", "ledger/events", "items/closed"):
            (st / x).mkdir(parents=True)
        (st / "canon.yml").write_text("start_savegame: x.rws\n")
        (td / "tr/-proj").mkdir(parents=True)
        os.environ.update(SCRATCH_REAP_CORPUS=str(td / "corpus"), SCRATCH_REAP_STATE=str(td / "state"), SCRATCH_REAP_TTL_HOURS="24",
                          SCRATCH_REAP_MIRRORS=str(origin), SCRATCH_REAP_TRANSCRIPTS=str(td / "tr"),
                          SCRATCH_REAP_PROTECTED=str(td / "protected"))
        R.Ctx.global_holds = lambda self: []
        cases(td, origin)
    print(f"{len(T.FAILS)} failed" + (": " + "; ".join(T.FAILS) if T.FAILS else " (ALL PASS)"))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
