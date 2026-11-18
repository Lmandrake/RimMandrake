#!/usr/bin/env python3
"""RIMMANDRAKE_DECODE_LANDING_PATCHES_AS_BYTES_STRAY_BYTE_CRASHED: a landing must survive a patch that is not UTF-8.

./publish crashed with UnicodeDecodeError (byte 0xb7 at position 166,718,710) replaying a commit that deleted 15,365
files, one of them a text file holding a Latin-1 byte: seat_sync.landed_twin reads `git diff-tree -p` through
Git.run(text=True), which decodes strictly. Git calls a file text unless it holds a NUL, so any stray non-UTF-8 byte in
a tracked text file can do this. Here, in throwaway repos: a commit adding, editing and deleting such a file, landed
upstream under another sha, is found as a twin (not a crash), and an unlanded one reads None.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seat_sync as S  # noqa: E402

fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def git(repo, *a):
    subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True)


def head(repo):
    return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()


def write(repo, rel, data: bytes):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


def main():
    with tempfile.TemporaryDirectory() as td:
        o, seat, peer = f"{td}/o.git", f"{td}/seat", f"{td}/peer"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", o], check=True)
        subprocess.run(["git", "clone", "-q", o, seat], check=True, capture_output=True)
        for r in (seat,):
            git(r, "config", "user.email", "t@t"); git(r, "config", "user.name", "t")
        write(seat, "keep.txt", b"k\n")
        git(seat, "add", "keep.txt"); git(seat, "commit", "-qm", "init"); git(seat, "push", "-q", "origin", "HEAD:main")
        subprocess.run(["git", "clone", "-q", o, peer], check=True, capture_output=True)
        git(peer, "config", "user.email", "p@p"); git(peer, "config", "user.name", "p")
        steps = (("add", {"old/notes.txt": b"caf\xe9 \xb7 dot\n"}),
                 ("edit", {"old/notes.txt": b"caf\xe9 \xb7 dot\nmore \xff\n"}),
                 ("delete", {"old/notes.txt": None}))
        for name, files in steps:
            shas = []
            for repo in (seat, peer):
                for rel, data in files.items():
                    if data is None:
                        git(repo, "rm", "-q", rel)
                    else:
                        write(repo, rel, data); git(repo, "add", rel)
                git(repo, "commit", "-qm", f"{name} non-utf8 file ({os.path.basename(repo)})")
                shas.append(head(repo))
            git(peer, "push", "-q", "origin", "HEAD:main")
            git(seat, "fetch", "-q", "origin")
            g = S.Git(seat)
            try:
                twin = S.landed_twin(g, "origin/main", shas[0])
                err = ""
            except UnicodeError as e:
                twin, err = None, f"{type(e).__name__}: {e}"
            check(not err, f"{name}: landed_twin reads a non-UTF-8 patch without crashing {err}".rstrip())
            check(twin == shas[1], f"{name}: the same change landed under another sha is its twin (got {twin})")
            git(seat, "reset", "-q", "--hard", "origin/main")
        # an unlanded commit touching such a file is no twin
        write(seat, "old/other.txt", b"\xb7 only here\n"); git(seat, "add", "old/other.txt")
        git(seat, "commit", "-qm", "unlanded")
        try:
            twin = S.landed_twin(S.Git(seat), "origin/main", head(seat))
            err = ""
        except UnicodeError as e:
            twin, err = "crash", f"{type(e).__name__}"
        check(twin is None and not err, f"an unlanded non-UTF-8 commit reads None (got {twin} {err})")
    print(f"{'FAIL' if fails else 'PASS'}: {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
