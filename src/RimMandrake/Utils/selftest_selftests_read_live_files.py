#!/usr/bin/env python3
"""selftest_selftests_read_live_files.py -- no selftest reads a repo file that is gone (NIGHTLY_COP_FIX_RED_CYGHVG_QCWJ).

The class: a commit deletes or retires a file, and a selftest that still reads it crashes the next night with
FileNotFoundError (11-04: selftest_brief.py read pulse/widget/index.html, removed by the RimPulse retirement the day
before). This guard reads every selftest*.py under the sweep's roots with `ast`, finds each path anchored on
`__file__` and built only from string literals (`Path(__file__).resolve().parent / "a" / "b"`, `.parents[n]`,
`os.path.join(os.path.dirname(__file__), "a")`, and names bound once to such a path), and fails on every one that is
READ (`.read_text()`, `.read_bytes()`, `.open()`, `open(p)`) and does not exist. Paths the test writes are not reads, and
a path the file also probes (`p.exists()`, `os.path.isfile(p)`) is an optional read the test already skips.

  python3 selftest_selftests_read_live_files.py                        the whole tree (the nightly reading)
  python3 selftest_selftests_read_live_files.py --blob REV:PATH ...    replay a file as it stood at REV (git), resolved
                                                                       at PATH's place in this tree (the instance)
"""
import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SEARCH_ROOTS = ("src", ".claude/hooks", "skills", "infrastructure/dashboards/hub", "infrastructure/stevedesktop")
READ_METHODS = {"read_text", "read_bytes", "open"}
PROBE_METHODS = {"exists", "is_file", "is_dir"}       # p.exists() anywhere in the file: its reads are guarded
PROBE_FUNCS = {"exists", "isfile", "isdir", "lexists"}   # os.path.exists(p)
SKIP_DIRS = {".git", "__pycache__", "node_modules", "bin", "obj"}

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(name)


class Anchored:
    """Resolve expressions to a concrete path when they are __file__ plus literals; None otherwise."""

    def __init__(self, file_path):
        self.file = Path(file_path).resolve()
        self.names = {}    # name -> Path, for names bound exactly once to an anchored path

    def eval(self, n):
        if isinstance(n, ast.Name):
            if n.id == "__file__":
                return self.file
            return self.names.get(n.id)
        if isinstance(n, ast.Call):
            f = n.func
            # Path(__file__) / pathlib.Path(...)
            if (isinstance(f, ast.Name) and f.id in ("Path", "PurePath")) or (isinstance(f, ast.Attribute) and f.attr == "Path"):
                if len(n.args) == 1 and not n.keywords:
                    return self.eval(n.args[0])
                return None
            if isinstance(f, ast.Attribute) and f.attr in ("resolve", "absolute") and not n.args:
                p = self.eval(f.value)
                return Path(os.path.normpath(p)) if p is not None else None
            # os.path.dirname / abspath / realpath / join
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Attribute) and f.value.attr == "path":
                if f.attr in ("abspath", "realpath", "normpath") and len(n.args) == 1:
                    p = self.eval(n.args[0])
                    return Path(os.path.normpath(p)) if p is not None else None
                if f.attr == "dirname" and len(n.args) == 1:
                    p = self.eval(n.args[0])
                    return p.parent if p is not None else None
                if f.attr == "join" and n.args:
                    p = self.eval(n.args[0])
                    if p is None:
                        return None
                    for a in n.args[1:]:
                        if not (isinstance(a, ast.Constant) and isinstance(a.value, str)):
                            return None
                        p = p / a.value
                    return p
            return None
        if isinstance(n, ast.Attribute) and n.attr == "parent":
            p = self.eval(n.value)
            return p.parent if p is not None else None
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Attribute) and n.value.attr == "parents":
            p = self.eval(n.value.value)
            idx = n.slice
            if p is not None and isinstance(idx, ast.Constant) and isinstance(idx.value, int):
                try:
                    return p.parents[idx.value]
                except IndexError:
                    return None
            return None
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            p = self.eval(n.left)
            if p is not None and isinstance(n.right, ast.Constant) and isinstance(n.right.value, str):
                return p / n.right.value
            return None
        return None


def reads_in(source, file_path):
    """-> [(line, resolved path)] for every anchored literal path the source reads."""
    tree = ast.parse(source, filename=str(file_path))
    a = Anchored(file_path)
    # names bound exactly once anywhere in the file: a rebound name is not a constant
    counts, binds = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    counts[t.id] = counts.get(t.id, 0) + 1
                    binds[t.id] = node.value
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign, ast.For, ast.With, ast.NamedExpr)):
            for t in ast.walk(node.target if hasattr(node, "target") else node):
                if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                    counts[t.id] = counts.get(t.id, 0) + 2
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in node.args.args + node.args.kwonlyargs + node.args.posonlyargs:
                counts[arg.arg] = counts.get(arg.arg, 0) + 2
    for _ in range(4):    # names built from names: a few passes settle it
        for name, value in binds.items():
            if counts.get(name) == 1 and name not in a.names:
                p = a.eval(value)
                if p is not None:
                    a.names[name] = p
    guarded = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr in PROBE_FUNCS and node.args and \
                    isinstance(f.value, ast.Attribute) and f.value.attr == "path":
                p = a.eval(node.args[0])
            elif isinstance(f, ast.Attribute) and f.attr in PROBE_METHODS:
                p = a.eval(f.value)
            else:
                continue
            if p is not None:
                guarded.add(os.path.normpath(p))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        target = None
        if isinstance(f, ast.Attribute) and f.attr in READ_METHODS:
            target = f.value
            if f.attr == "open" and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str) \
                    and any(c in node.args[0].value for c in "wax"):
                continue
        elif isinstance(f, ast.Name) and f.id == "open" and node.args:
            mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "mode"), None)
            if isinstance(mode, ast.Constant) and isinstance(mode.value, str) and any(c in mode.value for c in "wax"):
                continue
            target = node.args[0]
        if target is None:
            continue
        p = a.eval(target)
        if p is not None and os.path.normpath(p) not in guarded:
            found.append((node.lineno, p))
    return found


def selftests():
    for r in SEARCH_ROOTS:
        base = ROOT / r
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.startswith("selftest") and fn.endswith(".py"):
                    yield Path(dirpath) / fn


def _parses(src):
    try:
        ast.parse(src)
        return True
    except SyntaxError:
        return False


def missing_reads(files):
    """files: [(source, path-it-stands-at)] -> [(path, line, missing)]"""
    out = []
    for src, at in files:
        try:
            hits = reads_in(src, at)
        except SyntaxError:
            continue    # a test that cannot parse is the sweep's crash, not this guard's
        for line, p in hits:
            if not p.exists():
                out.append((at, line, p))
    return out


def fixtures():
    """The instrument can see: a planted read of an absent file is caught, a present one and a write are not."""
    d = Path(tempfile.mkdtemp(prefix="rlf_"))
    (d / "widget").mkdir()
    (d / "widget" / "here.html").write_text("x")
    src = '\n'.join([
        "from pathlib import Path",
        "import os",
        "HERE = Path(__file__).resolve().parent",
        "a = (Path(__file__).resolve().parent / 'widget' / 'index.html').read_text()",
        "b = (HERE / 'widget' / 'here.html').read_text()",
        "(HERE / 'out.txt').write_text('w')",
        "open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gone.json'))",
        "open(HERE / 'made.txt', 'w')",
        "c = Path(__file__).parents[0] / 'widget' / 'gone2.css'",
        "c.read_bytes()",
        "g = HERE / 'optional.json'",
        "if g.exists():",
        "    g.read_text()",
        "OPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'opt2.md')",
        "def rd():",
        "    return open(OPT).read()",
        "if os.path.exists(OPT):",
        "    rd()",
    ])
    miss = missing_reads([(src, d / "selftest_fx.py")])
    names = sorted(p.name for _, _, p in miss)
    check("fixture: the three absent reads are caught (index.html, gone.json, gone2.css)",
          names == ["gone.json", "gone2.css", "index.html"], names)
    check("fixture: a present read, a write_text, an open(..., 'w') and an exists()-guarded read are not flagged",
          not any(n in ("here.html", "out.txt", "made.txt", "optional.json", "opt2.md") for n in names), names)


def main(argv):
    blobs = []
    i = 0
    while i < len(argv):
        if argv[i] == "--blob" and i + 1 < len(argv):
            blobs.append(argv[i + 1])
            i += 2
        else:
            print("usage: %s [--blob REV:PATH ...]" % sys.argv[0])
            return 2
    fixtures()
    if blobs:
        files = []
        for b in blobs:
            rev, _, rel = b.partition(":")
            r = subprocess.run(["git", "show", b], cwd=ROOT, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            if r.returncode != 0:
                print("cannot read %s: %s" % (b, r.stderr.strip()))
                return 2
            files.append((r.stdout, ROOT / rel))
        label = "the replayed blob(s)"
    else:
        files = []
        for p in selftests():
            try:
                files.append((p.read_text(encoding="utf-8", errors="replace"), p))
            except OSError:
                continue
        check("sanity: the sweep sees the suite (over 200 selftests)", len(files) > 200, len(files))
        label = "every selftest under the sweep's roots"
        seen = sum(len(reads_in(src, at)) for src, at in files if _parses(src))
        check("sanity: the scanner resolves anchored reads in the suite (over 50)", seen > 50, seen)
    miss = missing_reads(files)
    for at, line, p in miss:
        print("  %s:%d reads %s, which does not exist" % (at.relative_to(ROOT) if at.is_relative_to(ROOT) else at, line,
                                                          p.relative_to(ROOT) if p.is_relative_to(ROOT) else p))
    check("%s read(s) only repo files that exist" % label, not miss, "%d absent read(s)" % len(miss))
    print("\n" + ("ALL PASS" if not FAILS else "FAILED: %d" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
