#!/usr/bin/env python3
"""selftest_guard_relation.py - a passed guard chain stands only while nothing its checks read or exercise changed, by the one
change relation (gaps.untouched; page design/specs/2026-11-24-stage-six-checks-to-steve/boundary.md). A real git repository."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="guard_rel_")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "q")
os.makedirs(os.environ["TESTQ_QUEUE"])
sys.path.insert(0, HERE)
import gaps as G  # noqa: E402

FAILS = []
R = os.path.join(TMP, "repo")
M = "src/RimMandrake/M/"
V = "design/concepts/M/version/"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def put(path, text):
    p = os.path.join(R, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


def commit(msg="x"):
    for a in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", msg]):
        subprocess.run(["git", "-C", R] + a, check=True, capture_output=True)
    return subprocess.run(["git", "-C", R, "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def main():
    os.makedirs(R)
    subprocess.run(["git", "init", "-q", "-b", "main", R], check=True)
    G.repo_root = lambda: R

    def spec(c):
        return {"stage": 6, "kind": "live_minimal", "file": M + "validation.py", "entry": c, "reads": [M + "validation.py"],
                "testq": {"chains": [c]}}
    put(V + "test_table.json", json.dumps({"tests": {"k_a": spec("a"), "k_b": spec("b"), "k_bare": spec("bare")}}))
    put(V + "exercises.json", json.dumps({"checks": {"k_a": [M + "Source/A.cs"], "k_b": [M + "Source/B.cs"]}}))
    put(M + "validation.py", "def a():\n    return 1\n\n\ndef b():\n    return 1\n\n\ndef bare():\n    return 1\n")
    put(M + "Source/A.cs", "class A { void Run() { int x = 1; } }\n")
    put(M + "Source/B.cs", "class B { void Run() { int x = 1; } }\n")
    old = commit()

    def ask(chain, new, cold=True):
        if cold:
            G._REL.clear()
        return G.untouched("M", chain, old, new)
    put("notes.md", "words\n")
    doc = commit()
    check([ask(c, doc) for c in ("a", "b", "bare")] == [True, True, True], "a change that nothing reads leaves each chain settled")
    put(M + "Source/A.cs", "class A { void Run() { int x = 2; } }\n")
    cs = commit()
    got = [ask(c, cs) for c in ("a", "b", "bare")]
    check(got[0] is False, "a chain whose check exercises the changed C# runs again (its `reads` name only the script) %s" % got)
    check(got[1] is True, "a chain whose check exercises other C# stays settled %s" % got)
    check(got[2] is None, "a game check that declares no C# has no readable relation to changed C#: it runs again %s" % got)
    real, G._relation = G._relation, lambda *a: (_ for _ in ()).throw(RuntimeError("no"))
    check(ask("b", cs) is None, "a relation that cannot be read is no answer")
    G._relation = real
    check(G.untouched("M", "a", "f" * 40, cs) is None and G.untouched("M", "zz", old, cs) is None, "an unknown commit or chain is no answer")

    class Dead:
        def __init__(self, r):
            self._paths = r._paths

        def touches(self, *a):
            raise RuntimeError("asked again")
    G._REL[("M", cs)] = Dead(real("M", G.stage6_tests("M"), cs))
    check(G.untouched("M", "b", old, cs) is True, "the same bytes are not read twice (the tick asks every minute)")
    put(M + "Source/B.cs", "class B { void Run() { int x = 3; } }\n")
    check(ask("b", commit()) is False, "a kept answer does not outlive its bytes")
    G._REL.clear()
    os.remove(os.path.join(os.environ["TESTQ_QUEUE"], G.RELATION_CACHE))     # no kept answer of the same bytes may hide it
    subprocess.run(["git", "-C", R, "branch", "-f", "moving", doc], check=True)
    before = G.untouched("M", "a", old, "moving")
    subprocess.run(["git", "-C", R, "branch", "-f", "moving", cs], check=True)
    after = G.untouched("M", "a", old, "moving")
    check((before, after) == (True, False), "a ref that moved in one process is read again %s" % ((before, after),))
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
