#!/usr/bin/env python3
"""Selftest for selftest_cache.py: touching ANY declared input invalidates the key, an undeclared test never caches, only a
PASS is stored, and a hit prints the CACHED PASS line. Runs on a fake repo in a temp dir with a private cache store, with a
declaration exercising every input kind (test script, files, trees with extension filters, recursion)."""
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
tmp = Path(tempfile.mkdtemp(prefix="st_selftest_cache_"))
os.environ["RM_SELFTEST_CACHE_STORE"] = str(tmp / "store")
import selftest_cache as SC  # noqa: E402

FAILS = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        FAILS.append(name)


repo = tmp / "repo"
(repo / "t").mkdir(parents=True)
(repo / "lib" / "sub").mkdir(parents=True)
(repo / "t" / "selftest_x.py").write_text("print('x')\n")
(repo / "lib" / "a.cs").write_text("class A{}\n")
(repo / "lib" / "sub" / "b.cs").write_text("class B{}\n")
(repo / "lib" / "notes.txt").write_text("not an input\n")
(repo / "extra.py").write_text("E=1\n")
REL = "t/selftest_x.py"
SC.DECLS[REL] = dict(trees=[("lib", (".cs",), True)], files=["extra.py"])


def key():
    k = SC.compute_key(REL, repo)
    return k and k[0]


base = key()
check("a declared test gets a key", bool(base))
check("same inputs, same key", key() == base)
check("an undeclared test never caches", SC.compute_key("t/selftest_unknown.py", repo) is None)


def touch(path, text, label, expect_change=True):
    p = repo / path
    old = p.read_text() if p.exists() else None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    k = key()
    check(f"{label}: key {'changes' if expect_change else 'is unchanged'}", (k != base) == expect_change)
    if old is None:
        p.unlink()
    else:
        p.write_text(old)
    check(f"{label}: restoring the input restores the key", key() == base)


touch(REL, "print('y')\n", "the test script edited")
touch("extra.py", "E=2\n", "a declared file edited")
touch("lib/a.cs", "class A{int x;}\n", "a tree file edited")
touch("lib/sub/b.cs", "class B{int x;}\n", "a nested tree file edited (recursion)")
touch("lib/new.cs", "class N{}\n", "a file added to a tree")
touch("lib/sub/deep/c.cs", "class C{}\n", "a file added in a new subdirectory")
touch("lib/notes.txt", "changed\n", "an extension-filtered file edited", expect_change=False)
# a same-size, same-second edit must still change the key (content hash, not size/mtime)
p = repo / "lib" / "a.cs"
st = p.stat()
p.write_text("class A{}\n".replace("A", "Z"))
os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
check("same-size edit with a restored mtime changes the key", key() != base)
p.write_text("class A{}\n")
(repo / "lib" / "sub" / "b.cs").unlink()
check("a file deleted from a tree changes the key", key() != base)
(repo / "lib" / "sub" / "b.cs").write_text("class B{}\n")
(repo / "extra.py").unlink()
check("a declared file vanishing changes the key", key() != base)
(repo / "extra.py").write_text("E=1\n")
check("all restored: key back to base", key() == base)

# the runner and the cache module are inputs too: they are hashed from HERE, so assert they are fed
import hashlib  # noqa: E402
fed = []
orig = SC._Hasher.file
SC._Hasher.file = lambda self, p: (fed.append(Path(p).name), orig(self, p))[1]
SC.compute_key(REL, repo)
SC._Hasher.file = orig
check("run_selftests.py and selftest_cache.py are keyed", "run_selftests.py" in fed and "selftest_cache.py" in fed)

# store / lookup / only PASS
check("no entry before a PASS", SC.lookup(REL, base) is None)
SC.store_pass(REL, base, 1.0, repo)
rec = SC.lookup(REL, base)
check("a stored PASS is found at its key", bool(rec) and rec["key"] == base)
check("the hit line names test, key, date and sha", all(s in SC.hit_line(REL, base, rec) for s in
      ("CACHED PASS", REL, "key=" + base, rec["date"], rec["sha"])))
(repo / "lib" / "a.cs").write_text("class A{int q;}\n")
check("after an input change the old entry is not found", SC.lookup(REL, key()) is None)
(repo / "lib" / "a.cs").write_text("class A{}\n")
SC.forget(REL)
check("a non-PASS (forget) removes the entry", SC.lookup(REL, base) is None)

# integration: the real runner, real flags
src = (HERE / "run_selftests.py").read_text()
check("the runner has --no-cache", '"--no-cache"' in src)
unit = (HERE / "systemd" / "rm-selftests-nightly.service").read_text()
check("the nightly sweep runs with --no-cache", "run_selftests.py --no-cache" in unit)
check("every real declaration names an existing test",
      all((HERE.parents[2] / r).is_file() for r in SC.DECLS if r != REL))

# a dotnet SelfTest runs from a stage that carries all of src, so it can READ any sibling mod at runtime; every sibling
# mod folder its .cs sources name in a string literal must sit under a declared tree (FlowWorks once read 9 undeclared)
import re  # noqa: E402
REAL = HERE.parents[2]
SRC_ROOTS = ("RimMandrake", "RimUtinni", "RimStarWars", "Jawa")
mod_dirs = {d.name: r for r in SRC_ROOTS if (REAL / "src" / r).is_dir() for d in (REAL / "src" / r).iterdir()
            if d.is_dir() and d.name not in SC.SKIP_DIRS}
check("the sibling-mod probe can see mod folders", {"FlowWorks", "GimmeSomeSlack"} <= set(mod_dirs))
for rel, decl in SC.DECLS.items():
    if rel == REL or not decl.get("csproj"):
        continue
    test_dir = (REAL / decl["csproj"]).parent
    named = set()
    for cs in test_dir.rglob("*.cs"):
        if SC.SKIP_DIRS & set(cs.relative_to(test_dir).parts):
            continue
        for lit in re.findall(r'"([^"\\]{2,})"', cs.read_text(encoding="utf-8", errors="replace")):
            if lit in mod_dirs and lit not in decl.get("names_only", ()):    # names_only: named, never read
                named.add(f"src/{mod_dirs[lit]}/{lit}")
    trees = [d for d, _e, _r in decl.get("trees", [])]
    missing = sorted(n for n in named if not any(t == n or t.startswith(n + "/") for t in trees))
    check(f"{Path(rel).name}: every sibling mod its SelfTest names is a declared tree" +
          (f" (missing {missing})" if missing else ""), not missing)

shutil.rmtree(tmp, ignore_errors=True)
print("\n%s" % ("FAIL: " + ", ".join(FAILS) if FAILS else "ALL PASS"))
sys.exit(1 if FAILS else 0)
