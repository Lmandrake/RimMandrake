#!/usr/bin/env python3
"""Selftest for ledger_sync.py — temp git repos (bare origin + seat clone), no network."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_sync as ls  # noqa: E402

REL = "infrastructure/state/ledger/events/FOUNDRY.jsonl"


def sh(cwd, *args):
    subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True)


def ev(verb, id_, ts):
    return json.dumps({"seat": "FOUNDRY", "event": verb, "id": id_, "ts": ts})


def main():
    fails = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    a, b, c, d = ev("note", "A", "t1"), ev("note", "B", "t2"), ev("lease", "C", "t3"), ev("x", "D", "t4")
    # pure: key order does not matter, duplicates collapse, edits are conflicts
    a_reordered = json.dumps(dict(reversed(list(json.loads(a).items()))))
    edited_b = json.dumps({"seat": "FOUNDRY", "event": "note", "id": "B", "ts": "t2", "x": 1})
    m, conf, bad = ls.missing_lines("\n".join([a_reordered, c, c, edited_b, "{torn", d]) + "\n",
                                    a + "\n" + b + "\n")
    check("pure: missing = C, D in order", m == [c, d])
    check("pure: edited B is a conflict", conf == [edited_b])
    check("pure: torn line reported", bad == ["{torn"])

    with tempfile.TemporaryDirectory() as tmp:
        origin = os.path.join(tmp, "origin.git")
        seed = os.path.join(tmp, "seed")
        seat = os.path.join(tmp, "seat")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
        subprocess.run(["git", "clone", "-q", origin, seed], check=True, capture_output=True)
        for r in (seed,):
            sh(r, "config", "user.email", "t@t"); sh(r, "config", "user.name", "t")
        os.makedirs(os.path.join(seed, os.path.dirname(REL)))
        with open(os.path.join(seed, REL), "w") as fh:
            fh.write(a + "\n")
        sh(seed, "add", REL); sh(seed, "commit", "-qm", "seed"); sh(seed, "push", "-q", "origin", "HEAD:main")
        subprocess.run(["git", "clone", "-q", origin, seat], check=True, capture_output=True)
        # origin moves on (another seat appends b); seat clone appends c, d locally only
        with open(os.path.join(seed, REL), "a") as fh:
            fh.write(b + "\n")
        sh(seed, "commit", "-qam", "b"); sh(seed, "push", "-q", "origin", "HEAD:main")
        with open(os.path.join(seat, REL), "a") as fh:
            fh.write(c + "\n" + d + "\n")
        before = open(os.path.join(seat, REL)).read()

        os.environ.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                          GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        fresh = os.path.join(tmp, "fresh")
        quiet = lambda *_: None  # noqa: E731
        r = ls.run("FOUNDRY", seat, fresh, apply=False, out=quiet)
        check("dry run counts 2", r["missing"] == 2 and r["pushed"] is None)
        r = ls.run("FOUNDRY", seat, fresh, apply=True, out=quiet)
        check("apply pushes 2", r["missing"] == 2 and r["pushed"])
        shown = subprocess.run(["git", "-C", origin, "show", "main:" + REL],
                               capture_output=True, text=True).stdout
        check("origin shard = a, b, c, d (append-only)", shown == "\n".join([a, b, c, d]) + "\n")
        r = ls.run("FOUNDRY", seat, fresh, apply=True, out=quiet)
        check("re-run is idempotent", r["missing"] == 0 and r["pushed"] is None)
        check("seat clone untouched", open(os.path.join(seat, REL)).read() == before)
        try:
            ls.run("FOUNDRY", seat, seat, out=quiet)
            check("refuses seat clone as --clone", False)
        except RuntimeError:
            check("refuses seat clone as --clone", True)
        # no --clone: the temp clone lives under SCRATCH_ROOT/<SEAT> and is deleted when the run ends
        ls.SCRATCH_ROOT = os.path.join(tmp, "scratch")
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            rc = ls.main(["--seat", "FOUNDRY", "--seat-clone", seat])
        left = os.listdir(os.path.join(tmp, "scratch", "FOUNDRY"))
        check("temp clone removed after the run (rc %s, left %s)" % (rc, left), rc == 0 and left == [])

    print("selftest_ledger_sync: %d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
