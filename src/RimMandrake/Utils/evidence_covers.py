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
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACER_DIR = HERE / "suite_trace"
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


# --- csproj evaluation (EVIDENCE_COVERS_HARDEN_REVIEW_AD_SIX_MORE F4) ---------------------------------------------
# A declared cover is a claim that the build COMPILED the file, so this evaluates the subset of MSBuild it can be sure
# of and FAILS CLOSED (csproj only, no source) on everything else: a parse error, a non-SDK project (no default glob
# and usually Imports), any <Import>, a Condition on a Compile item, on its ItemGroup or on a property that switches
# the default glob, DefaultItemExcludes/EnableDefaultItems (other glob knobs), `$(` in a Compile spec, and any
# Directory.Build.props/.targets between the project and the repo root that touches Compile items or those knobs.
# What it does evaluate, in document order: the SDK default `**/*.cs` (minus bin/, obj/ and hidden dirs) unless
# EnableDefaultCompileItems is false, then each <Compile Include=".." Exclude=".."/> and <Compile Remove=".."/>,
# ';'-separated, matched case-insensitively (Windows MSBuild). <Compile Update> changes metadata only: ignored.
_GLOB_KNOBS = ("enabledefaultcompileitems", "enabledefaultitems", "defaultitemexcludes")
_DIR_BUILD_TOUCH = re.compile(r"<Compile[\s/>]|EnableDefault\w*Items|DefaultItemExcludes|<Import[\s/>]", re.I)


class _Closed(Exception):
    """The project uses semantics this evaluator does not model: cover the csproj only."""


def _local(tag) -> str:
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _glob_re(pat: str):
    """MSBuild wildcard (relative to the project dir, '/' separated) -> case-insensitive regex over rel paths."""
    pat = os.path.normpath(pat.replace("\\", "/")).replace(os.sep, "/")
    out, i = "", 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out, i = out + "(?:[^/]+/)*", i + 3
        elif pat.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pat[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pat[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pat[i]), i + 1
    return re.compile(out + r"\Z", re.I)


def _match(specs: str, items: set) -> set:
    """The members of `items` (paths relative to the project dir) any ';'-separated spec matches."""
    hit = set()
    for sp in (x.strip() for x in specs.split(";")):
        if sp:
            rx = _glob_re(sp)
            hit |= {f for f in items if rx.match(f)}
    return hit


def _walk(top: str, base: str) -> set:
    out = set()
    for dp, dns, fns in os.walk(top):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__")]
        out |= {os.path.relpath(os.path.join(dp, f), base).replace(os.sep, "/") for f in fns}
    return out


def _expand(specs: str, base: str) -> set:
    """Files an Include spec names, relative to the project dir: a literal path if the file exists, a wildcard
    matched over a walk of its static (wildcard-free) leading directory."""
    out = set()
    for sp in (x.strip() for x in specs.split(";")):
        if not sp:
            continue
        norm = os.path.normpath(sp.replace("\\", "/")).replace(os.sep, "/")
        if not any(c in norm for c in "*?"):
            if os.path.isfile(os.path.join(base, norm)):
                out.add(norm)
            continue
        parts = norm.split("/")
        k = next(i for i, x in enumerate(parts) if any(c in x for c in "*?"))
        top = os.path.normpath(os.path.join(base, *parts[:k])) if k else base
        rx = _glob_re(norm)
        out |= {f for f in _walk(top, base) if rx.match(f)}
    return out


def _default_glob(base: str) -> set:
    def ok(f):
        parts = f.split("/")
        return f.lower().endswith(".cs") and not any(
            p.lower() in ("bin", "obj") or p.startswith(".") for p in parts[:-1])
    return {f for f in _walk(base, base) if ok(f)}


def _evaluate(root, base: str) -> set:
    if root is None or _local(root.tag) != "project":
        raise _Closed("not a Project")
    if not root.get("Sdk") and not any(_local(e.tag) == "sdk" for e in root):
        raise _Closed("non-SDK project")
    default_on = True
    for el in root.iter():
        t = _local(el.tag)
        if t in ("import", "choose", "importgroup"):
            raise _Closed(t)
        if t in _GLOB_KNOBS:
            if t != "enabledefaultcompileitems" or el.get("Condition"):
                raise _Closed(t)
            default_on = (el.text or "").strip().lower() != "false"
    for pg in (e for e in root if _local(e.tag) == "propertygroup" and e.get("Condition")):
        if any(_local(c.tag) in _GLOB_KNOBS for c in pg):
            raise _Closed("conditioned glob knob")
    items = _default_glob(base) if default_on else set()
    for ig in (e for e in root if _local(e.tag) == "itemgroup"):
        comps = [c for c in ig if _local(c.tag) == "compile"]
        if comps and ig.get("Condition"):
            raise _Closed("conditioned ItemGroup with Compile")
        for c in comps:
            if c.get("Condition"):
                raise _Closed("conditioned Compile")
            inc, exc, rem = c.get("Include"), c.get("Exclude"), c.get("Remove")
            if any(v and "$(" in v or v and "@(" in v or v and "%(" in v for v in (inc, exc, rem)):
                raise _Closed("property in Compile spec")
            if inc:
                new = _expand(inc, base)
                items |= new - (_match(exc, new) if exc else set())
            if rem:
                items -= _match(rem, items)
    return items


def _csproj_sources(repo: Path, csproj: str) -> set:
    """The csproj plus the .cs files its build compiles, when that is decidable from the file (see above); otherwise
    the csproj alone. Never a file outside the repo."""
    import xml.etree.ElementTree as ET
    repo = Path(repo)
    cs = repo / csproj
    out = {csproj}
    root_real = os.path.realpath(str(repo))
    base = Path(os.path.realpath(str(cs.parent)))
    try:
        tree = ET.fromstring(cs.read_bytes())
    except (OSError, ET.ParseError):
        return out
    d = base
    while _inside(str(d), root_real) is not None or os.path.realpath(str(d)) == root_real:
        for n in ("Directory.Build.props", "Directory.Build.targets"):
            try:
                if _DIR_BUILD_TOUCH.search((d / n).read_text(encoding="utf-8-sig", errors="replace")):
                    return out
            except OSError:
                pass
        if os.path.realpath(str(d)) == root_real:
            break
        d = d.parent
    try:
        items = _evaluate(tree, str(base))
    except _Closed:
        return out
    for f in items:
        if not f.lower().endswith(".cs"):
            continue
        r = _inside(os.path.realpath(os.path.join(str(base), f)), root_real)
        if r and os.path.isfile(os.path.join(root_real, r)):
            out.add(r)
    return out


def stamped_sources(repo, csproj: str, stamps) -> set:
    """What a winbuild of `csproj` provably compiled (F3): the csproj plus every .cs its own `.srchash` stamp lists
    (Directory.Build.targets writes one line per evaluated @(Compile) item: '<sha256> <path rel to the project dir>'),
    kept only when the stamp's '# project:' names THIS csproj (relative to src/), the path lies inside the repo and its
    sha256 equals the repo file's now. No stamp -> the csproj alone (a staged folder is not a list of inputs)."""
    import hashlib
    repo = Path(repo)
    root_real = os.path.realpath(str(repo))
    out = {csproj}
    want = os.path.relpath(str(repo / csproj), str(repo / "src")).replace(os.sep, "/")
    base = (repo / csproj).parent
    for st in stamps or []:
        try:
            lines = (repo / st).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        proj = next((ln.split(":", 1)[1].strip() for ln in lines if ln.lower().startswith("# project:")), None)
        if proj is None or proj.lower() != want.lower():
            continue
        for ln in lines:
            if ln.startswith("#") or " " not in ln.strip():
                continue
            h, p = ln.strip().split(" ", 1)
            if not p.lower().endswith(".cs") or not re.fullmatch(r"[0-9a-fA-F]{64}", h):
                continue
            r = _inside(os.path.realpath(os.path.join(str(base), p)), root_real)
            if not r:
                continue
            try:
                if hashlib.sha256((repo / r).read_bytes()).hexdigest() == h.lower():
                    out.add(r)
            except OSError:
                pass
    return out


# --- header declarations -------------------------------------------------------------------------------------------
# A selftest may declare, in its own source, a file it exercises that the trace cannot see -- a child started as
# `python -E`/`-I` never loads the tracer (contracts/replay.py runs replay_worker.py that way):
#     # selftest-covers: src/RimMandrake/contracts/replay_worker.py
# Comma-separated, repo-relative. Not a DECLS key on purpose: a DECLS entry makes the test CACHEABLE, and a
# covers-only entry would cache it on an incomplete input key. A header entry counts ONLY when it is an exact,
# existing in-clone file (no folder, glob, '..', absolute path) AND the code that ran NAMES it (its basename appears
# in the test source outside header lines, or in a module the run loaded): a declaration of a file nothing in the run
# refers to is an unbacked claim and is dropped.
HEADER = "# selftest-covers:"


def _read(p: Path):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def header_entries(src: str):
    """(declared paths, test source with every header line removed)."""
    decl, rest = [], []
    for line in (src or "").splitlines():
        s = line.strip()
        if s.startswith(HEADER):
            decl += [x.strip() for x in s[len(HEADER):].split(",") if x.strip()]
        else:
            rest.append(line)
    return decl, "\n".join(rest)


def _exact(repo: Path, c: str) -> bool:
    if not c or c.startswith(("/", "\\")) or "\\" in c or any(ch in c for ch in "*?[]") or ":" in c:
        return False
    parts = c.split("/")
    if any(p in ("", ".", "..") for p in parts):
        return False
    try:
        root = repo.resolve()
        f = (repo / c).resolve()
    except OSError:
        return False
    return f.is_file() and root in f.parents and f.relative_to(root).as_posix() == c


def header_declared(rel: str, repo, loaded=()) -> set:
    """Header-declared files of the test at `rel` that are exact, existing and named by the test code or by one of
    `loaded` (repo-relative sources the run loaded). Unreadable test -> empty."""
    repo = Path(repo)
    src = _read(repo / rel)
    if src is None:
        return set()
    decl, code = header_entries(src)
    out = set()
    texts = None
    for c in decl:
        if c == rel or not _exact(repo, c):
            continue
        base = c.rsplit("/", 1)[-1]
        if base in code:
            out.add(c)
            continue
        if texts is None:
            texts = [t for t in (_read(repo / s) for s in sorted(loaded) if s != rel) if t]
        if any(base in t for t in texts):
            out.add(c)
    return out


def declared(rel: str, repo, loaded=()) -> set:
    """Sources the test at `rel` (relative to its clone `repo`) declares: in selftest_cache.DECLS its csproj and the
    csproj's compile items plus an explicit `covers` list; and its `# selftest-covers:` header entries that the code
    that ran names (header_declared; `loaded` = what the run's trace showed loading). Unknown test -> header only."""
    repo = Path(repo)
    out = header_declared(rel, repo, loaded)
    try:
        import selftest_cache as SC
    except Exception:  # noqa: BLE001 -- coverage is optional; never break the run
        return out
    decl = SC.DECLS.get(rel)
    if not decl:
        return out
    out |= set(_csproj_sources(repo, decl["csproj"])) if decl.get("csproj") else set()
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
