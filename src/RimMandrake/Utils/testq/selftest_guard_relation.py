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


def chains_no_check_names():
    """A chain that no stage-6 check names: its own declaration, else its whole mod, else no answer."""
    ex = {"checks": {"k_a": [M + "Source/A.cs"], "k_b": [M + "Source/B.cs"]},
          "chains": {"own": {"file": M + "validation.py", "exercises": [M + "Source/C.cs"], "like": ["k_a"]},
                     "badlike": {"file": M + "validation.py", "exercises": [M + "Source/C.cs"], "like": ["k_gone"]},
                     "a": {"file": M + "validation.py", "exercises": [M + "Source/C.cs"]}}}
    put(V + "exercises.json", json.dumps(ex))
    put(M + "validation.py", "def a():\n    return 1\n\n\ndef b():\n    return 1\n\n\ndef own():\n    return 1\n")
    for n, body in (("A", "class A { int x = 1; }"), ("C", "class C { void Run() { int x = 1; } }"), ("D", "class D { int x = 1; }")):
        put(M + "Source/%s.cs" % n, body + "\n")
    put("src/RimMandrake/Dep/Source/E.cs", "class E { int x = 1; }\n")
    base = commit()
    reads = ["src/RimMandrake/M", "src/RimMandrake/Dep"]

    def ask(chain, new, mod_reads=None, old=base):
        G._REL.clear()
        return G.untouched("M", chain, old, new, mod_reads=mod_reads)
    specs = G.chain_specs("M", G.stage6_tests("M"))
    check(sorted(specs) == ["own"], "a chain that a check names, and a `like` that names no declared check, declare nothing %s" % sorted(specs))
    put(M + "Source/D.cs", "class D { int x = 2; }\n")
    d = commit()
    check(ask("own", d) is True, "a declared chain stands when other C# of the mod changes")
    check(ask("plain", d, reads) is False, "an undeclared chain runs again when anything in its mod changes")
    check(ask("plain", d) is None and ask("plain", d, []) is None, "an undeclared chain with no known reads runs again")
    put(M + "Source/C.cs", "class C { void Run() { int x = 2; } }\n")
    c = commit()
    check(ask("own", c, old=d) is False, "a declared chain runs again when C# it declares changes")
    put(M + "Source/A.cs", "class A { int x = 2; }\n")
    a = commit()
    check(ask("own", a, old=c) is False, "a declared chain runs again when C# of a `like` check changes")
    put(M + "validation.py", "def a():\n    return 1\n\n\ndef b():\n    return 1\n\n\ndef own():\n    return 2\n")
    py = commit()
    check(ask("own", py, old=a) is False, "a declared chain runs again when its own code changes")
    put("src/RimMandrake/Other/Source/F.cs", "class F { }\n")
    other = commit()
    check(ask("plain", other, reads, old=py) is True, "an undeclared chain stands when only another mod changes")
    put("src/RimMandrake/Dep/Source/E.cs", "class E { int x = 2; }\n")
    check(ask("plain", commit(), reads, old=other) is False, "an undeclared chain runs again when a mod it depends on changes")
    check(ask("plain", "f" * 40, reads, old=other) is None, "a change that git cannot list is no answer for the whole mod")
    put(V + "exercises.json", "{ not json")
    check(ask("own", commit(), reads, old=base) is False, "a declaration that cannot be read falls back to the whole mod")
    os.remove(os.path.join(R, V + "test_table.json"))
    os.remove(os.path.join(R, V + "exercises.json"))
    no_table = commit()
    put("src/RimMandrake/Other/Source/F.cs", "class F { int y; }\n")
    check(ask("plain", commit(), reads, old=no_table) is True, "a mod with no test table stands on its whole mod")


def ledger_churn():
    """A file that only ANOTHER chain's check reads (the ledger, written every minute) leaves this chain's kept answer
    standing (RIMMANDRAKE_FIX_STEVEDESKTOP_TOP_WASTE_HE_SAID_END_THIS: the key covered every check's reads, so a live
    rank of Pyrelands re-read 21 of 30 relations on each tick, 76 s, while a Steve game sat free)."""
    tt = json.load(open(os.path.join(R, V + "test_table.json")))
    tt["tests"]["k_led"] = {"stage": 6, "kind": "live_minimal", "file": M + "validation.py", "entry": "led",
                            "reads": ["infra/ledger/events"], "testq": {"chains": ["led"]}}
    put(V + "test_table.json", json.dumps(tt))
    put(M + "validation.py", "def a():\n    return 1\n\n\ndef b():\n    return 1\n\n\ndef bare():\n    return 1\n\n\n"
                             "def led():\n    return 1\n")
    put("infra/ledger/events/A.jsonl", "1\n")
    base = commit()
    put("notes2.md", "words\n")
    n1 = commit()
    G._REL.clear()
    first = G.untouched("M", "a", base, n1)
    put("infra/ledger/events/A.jsonl", "2\n")
    n2 = commit()

    class Dead:
        def __init__(self, r):
            self._paths = r._paths

        def touches(self, *a):
            raise RuntimeError("asked again")
    G._REL.clear()
    G._REL[("M", n2)] = Dead(G._relation("M", G.stage6_tests("M"), n2))
    kept = G.untouched("M", "a", base, n2)
    check((first, kept) == (True, True), "a ledger write that only another chain's check reads keeps this chain's "
                                         "answer (no relation re-read) %s" % ((first, kept),))
    G._REL.clear()
    check(G.untouched("M", "led", base, n2) is False, "the chain whose check reads the ledger still runs again")


def probe_reads():
    """The live probe: a mod's reads hold its folder, its dependency's folder and the shared source its csproj compiles."""
    got = {}
    for mod in ("LanternDeeps", "Atlas"):
        r = subprocess.run([sys.executable, os.path.join(HERE, "gapprobe.py")], capture_output=True, text=True,
                           input=json.dumps({"mod": mod, "only": "reads"}))
        got[mod] = (json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else {}).get("reads") or []
    ld = got["LanternDeeps"]
    check("src/RimMandrake/LanternDeeps" in ld and "src/RimMandrake/CreatureBehaviors" in ld, "reads: the folder and its dependency %s" % ld[:3])
    check(any(p.startswith("src/RimMandrake/_Shared/") for p in ld), "reads: shared source that a csproj compiles")
    check("src/RimUtinni/Atlas" in got["Atlas"] and not any("FlowWorks" in p for p in got["Atlas"]), "reads: no mod it does not use")


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
    ledger_churn()
    chains_no_check_names()
    probe_reads()
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
