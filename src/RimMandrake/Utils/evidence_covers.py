"""Which SOURCE files a selftest run covers, for close_evidence `covers` (item SELFTEST_EVIDENCE_FIX_COVERS_TESTS_ONLY).

Before this, run_selftests recorded `covers` = the selftest files it ran, so arbiter G6 stayed OPEN for every claim
that touched a source file, even when an isolated, independent run of that file's selftest passed.

A source counts as covered by a test ONLY when the test that ran
  * provably LOADED it: the run's trace (suite_trace/sitecustomize.py, the tracer suite_evidence already uses) lists
    it as an imported module file of the test process or of any python process it spawned (a script a test runs with
    `subprocess.run([sys.executable, X.py])` is that child's __main__ module), inside the test's own clone; or
  * DECLARES it: the test has a selftest_cache.DECLS entry with a `csproj`, and the file is that csproj or one of its
    <Compile Include> items (the dotnet build compiles exactly those; a csproj that leaves EnableDefaultCompileItems on
    compiles every .cs under its folder), or is listed in the entry's explicit `covers` key.
Never by name similarity (selftest_foo.py beside foo.py proves nothing until foo.py is in its trace), never from
DECLS `trees`/`files` (cache INPUTS: declared broadly on purpose, so a stale PASS is impossible -- the opposite of a
coverage claim), never from files a test merely opened (a lint that reads every def is not a test of every def).

predict() is the static, one-hop version for planning (isolated_evidence's dry run): the imports and `*.py` string
literals of the test source, resolved against the files of the tree. It is a PREDICTION and is never recorded.
"""
from __future__ import annotations

import ast
import glob
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACER_DIR = HERE / "suite_trace"
_INCLUDE = re.compile(r"<Compile\s+Include\s*=\s*\"([^\"]+)\"", re.I)
_DEFAULT_OFF = re.compile(r"<EnableDefaultCompileItems>\s*false\s*</EnableDefaultCompileItems>", re.I)
_SKIP = {"bin", "obj", "__pycache__", ".git"}


def _inside(p: str, root: str) -> str | None:
    """`p` relative to `root` (posix) when it lies inside it, else None."""
    try:
        r = os.path.relpath(os.path.normpath(p), root)
    except ValueError:
        return None
    if r == "." or r.startswith(".."):
        return None
    return r.replace(os.sep, "/")


def traced(trace_dir, clone) -> set:
    """In-clone .py files any traced process of one test run imported (or ran as __main__). Unreadable trace files
    contribute nothing: a coverage claim needs the trace, its absence only makes the run cover less."""
    root = os.path.realpath(str(clone))
    tracer = os.path.join(str(TRACER_DIR), "")
    out = set()
    for f in sorted(Path(trace_dir).glob("*.json")):
        try:
            mods = json.loads(f.read_text(encoding="utf-8")).get("modules") or []
        except (OSError, ValueError, AttributeError):
            continue
        for m in mods:
            if not isinstance(m, str) or not m.endswith(".py") or "/__pycache__/" in m or m.startswith(tracer):
                continue
            r = _inside(os.path.realpath(m), root)
            if r:
                out.add(r)
    return out


def _csproj_sources(repo: Path, csproj: str) -> set:
    cs = repo / csproj
    try:
        text = cs.read_text(encoding="utf-8-sig")
    except OSError:
        return set()
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    base = cs.parent
    root = os.path.realpath(str(repo))
    out = {csproj}
    pats = [i.replace("\\", "/") for i in _INCLUDE.findall(text)]
    if not _DEFAULT_OFF.search(text):
        pats.append("**/*.cs")
    for pat in pats:
        full = os.path.normpath(os.path.join(str(base), pat))
        hits = glob.glob(full, recursive=True) if any(c in pat for c in "*?[") else [full]
        for h in hits:
            if not os.path.isfile(h) or set(Path(h).parts) & _SKIP:
                continue
            r = _inside(os.path.realpath(h), root)
            if r:
                out.add(r)
    return out


def declared(rel: str, repo) -> set:
    """Sources the test at `rel` (relative to its clone `repo`) declares in selftest_cache.DECLS: its csproj and the
    csproj's compile items, plus an explicit `covers` list. Unknown test -> empty."""
    try:
        import selftest_cache as SC
    except Exception:  # noqa: BLE001 -- coverage is optional; never break the run
        return set()
    decl = SC.DECLS.get(rel)
    if not decl:
        return set()
    repo = Path(repo)
    out = set(_csproj_sources(repo, decl["csproj"])) if decl.get("csproj") else set()
    out |= {c for c in decl.get("covers", []) if (repo / c).is_file()}
    return out


def merge(per_test: dict) -> tuple:
    """{test rel: set(source rels)} -> (covers: sorted tests + sources, covers_by: {source: sorted tests}).
    A test's own file is never a 'source' of itself (it is already in paths)."""
    tests = set(per_test)
    by: dict = {}
    for t, srcs in per_test.items():
        for s in srcs:
            if s not in tests:
                by.setdefault(s, set()).add(t)
    covers_by = {s: sorted(v) for s, v in sorted(by.items())}
    return sorted(tests | set(covers_by)), covers_by


# ------------------------------------------------------------------ static prediction (plans only)

def _imports(src: str):
    """(module dotted names, '*.py' string literals) the source names. A syntax error yields nothing."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return [], []
    mods, lits = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            mods.append(n.module)
            mods += ["%s.%s" % (n.module, a.name) for a in n.names if a.name != "*"]
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.endswith(".py") \
                and len(n.value) < 200 and "\n" not in n.value:
            lits.append(n.value)
    return mods, lits


def predict(rel: str, read, tree) -> set:
    """Static one-hop guess of what the test at `rel` loads: each import / `*.py` literal resolved against the test's
    directory, its ancestors and src/RimMandrake/Utils, kept only when that file exists in `tree` (a set of repo
    paths). `read(rel)` -> source text or None. Planning only: evidence comes from traced()."""
    src = read(rel)
    if src is None:
        return set()
    tree = set(tree)
    d = os.path.dirname(rel)
    bases = []
    while True:
        bases.append(d)
        if not d:
            break
        d = os.path.dirname(d)
    bases.append("src/RimMandrake/Utils")
    mods, lits = _imports(src)
    out = set()
    for m in mods:
        p = m.replace(".", "/")
        for b in bases:
            for c in (p + ".py", p + "/__init__.py"):
                f = (b + "/" + c) if b else c
                if f in tree:
                    out.add(f)
    for lit in lits:
        lit = lit.replace("\\", "/").lstrip("./")
        for b in bases:
            f = os.path.normpath((b + "/" + lit) if b else lit).replace(os.sep, "/")
            if f in tree:
                out.add(f)
    out.discard(rel)
    return out
