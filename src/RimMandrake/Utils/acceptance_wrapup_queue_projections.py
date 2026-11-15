#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_EXEMPT_QUEUE_PROJECTIONS_FROM_DEBRIS_EVERY_HELPER.

wrapup.check_clone must treat an untracked rimflow queue projection (infrastructure/state/queue/<SEAT>.md,
regenerated on every rimflow call) like an untracked conversations/ export: not debris. Real work in the
same clone must still be filed. Prints PASS n/6; exit 0 only on 6/6.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rimflow"))
import wrapup  # noqa: E402


def repo(tmp, name, files):
    up = os.path.join(tmp, name + ".up")
    work = os.path.join(tmp, name)
    g = lambda c, *a: subprocess.run(["git", "-C", c] + list(a), capture_output=True, check=True, timeout=30)
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", up], check=True, timeout=30)
    subprocess.run(["git", "clone", "-q", up, work], check=True, capture_output=True, timeout=30)
    for rel in ("infrastructure/state/queue/HUMAN.md", "conversations/old.md"):   # tracked, as on main
        os.makedirs(os.path.dirname(os.path.join(work, rel)), exist_ok=True)
        open(os.path.join(work, rel), "w").close()
        g(work, "add", rel)
    g(work, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
    g(work, "push", "-q", "origin", "HEAD:main")
    g(work, "branch", "-q", "--set-upstream-to=origin/main")
    for rel, body in files.items():
        p = os.path.join(work, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)
    return work


def main():
    os.environ["RM_WRAPUP_SEAT_CLONES"] = "/nonexistent-seat-clone"
    w = wrapup.World()
    q = "infrastructure/state/queue/"
    cases = [  # (name, untracked files, expected act)
        ("empty", {}, "ok"),
        ("one_projection", {q + "CLAUDE_ARCHMAGI_FWLIVE.md": "x"}, "ok"),
        ("many_projections", {q + "CLAUDE_STEVEDESKTOP_OFFLINE%d.md" % i: "x" for i in range(1, 9)}, "ok"),
        ("projections_and_conversation", {q + "CODEX_ARCHMAGI_FWDRAIN.md": "x", "conversations/c.md": "x"}, "ok"),
        ("projection_plus_real_work", {q + "CONDUCTOR.md": "x", "src/RimMandrake/new_tool.py": "x"}, "filed"),
        ("nested_under_queue_is_work", {q + "sub/notes.txt": "x"}, "filed"),
    ]
    passed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, files, want in cases:
            got = wrapup.check_clone(w, repo(tmp, name, files), carried=False)
            ok = got["act"] == want
            passed += ok
            print("%s %s: want %s got %s (%s)" % ("PASS" if ok else "FAIL", name, want, got["act"], got["why"]))
    print("PASS %d/%d" % (passed, len(cases)))
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
