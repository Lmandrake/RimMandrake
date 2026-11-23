#!/usr/bin/env python3
"""The CHANGE RELATION: after a change, only the checks that the change touches run again. A program, no AI.

Owner, 2026-11-21 (item RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203; root CLAUDE.md §After a change,
only the checks that the change touches run again; page design/specs/2026-11-21-rerun-only-related/boundary.md).

One question, asked by every stage (the in-game build match, the Stage 6 exit, the visit brief, `./pipe why`, the walk
build): a check's last row was made on commit OLD; the commit now is NEW; does the change OLD..NEW touch what the check
reads or exercises?

  python3 src/RimMandrake/rimflow/rerun_relation.py --mod M [--old SHA] [--new SHA] [--tests ingame|all]
      one line per check that the change touches, then the checks with no readable relation, then the changed files
      that no check declares; --old defaults to each check's last in-game row's mod_sha

What a check declares: its `exercises` (paths, or "*" for the whole mod; in the table, or beside it in
version/exercises.json, which a declaration edits instead of the locked table), its `reads` and its `file`. A full-list
check (kind live_full) declares the whole mod. How a changed file relates, by kind:
  .py    by top-level name: the names that differ between OLD and NEW touch the check only when the names its id and
         entry reach (across every Python file it declares, by name, attribute and string) include one; a dict
         literal relates key by key. A file that does not parse relates whole.
  .json  by object: when the file holds an object whose id (or key) is the check's id or entry, only that object.
  .cs    by source file. The DLL and its .srchash are derived: they relate to nothing by themselves.
  other  by file.
A check whose own test-table entry changed in what it runs (RUN_KEYS) is touched. A check with no declared path, or a
row whose commit git cannot resolve, has no readable relation: it alone runs again, and it is listed.
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

RUN_KEYS = ("kind", "file", "entry", "reads", "exercises", "command", "tier", "why_full_list")
DERIVED_EXT = (".dll", ".pdb", ".srchash")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ROW_ID = re.compile(r"^[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]{4,}$")   # a row or check id: two parts or more, not PASS
WHOLE = "*"


# ---- git, cached ----------------------------------------------------------------------------------------------------

class Git:
    """Reads one repository at given commits. Every read is cached; a read that fails is None (never empty text)."""

    def __init__(self, root, runner=subprocess.run):
        self.root, self.run, self._show, self._rev, self._diff = root, runner, {}, {}, {}

    def _git(self, *args):
        try:
            r = self.run(["git", "-C", self.root] + list(args), capture_output=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout if r.returncode == 0 else None

    def rev(self, sha):
        """The full commit id, or None when git cannot resolve it."""
        if not sha:
            return None
        if sha not in self._rev:
            out = self._git("rev-parse", "--verify", "--quiet", "%s^{commit}" % sha)
            self._rev[sha] = out.decode().strip() if out else None
        return self._rev[sha]

    def show(self, sha, path):
        """The file's text at the commit, or None when the commit lacks it."""
        k = (sha, path)
        if k not in self._show:
            out = self._git("show", "%s:%s" % (sha, path))
            self._show[k] = out.decode("utf-8", "replace") if out is not None else None
        return self._show[k]

    def changed(self, old, new, paths):
        """Repo-relative paths that differ between the commits under `paths`, or None when git cannot say."""
        k = (old, new, tuple(paths))
        if k not in self._diff:
            out = self._git("diff", "--name-only", "--no-renames", old, new, "--", *paths)
            self._diff[k] = sorted(x for x in out.decode().splitlines() if x) if out is not None else None
        return self._diff[k]


def head_sha(root, runner=subprocess.run):
    return Git(root, runner).rev("HEAD")


# ---- what a check declares ------------------------------------------------------------------------------------------

def _clean(p):
    """A declared path, without prose in brackets and without a leading ./ ; '' when nothing is left."""
    p = str(p or "").strip()
    p = re.split(r"\s+\(", p, maxsplit=1)[0].strip()
    p = p.replace("\\", "/")
    return p[2:] if p.startswith("./") else p


def run_key(spec, k):
    """A test-table field as it bears on what the check runs: a command's trailing note in brackets (`(minimal list;
    entry exists)`) is the table maker's prose, not part of what runs; lists compare as sets of cleaned paths."""
    v = (spec or {}).get(k)
    if k == "command" and isinstance(v, str):
        return re.sub(r"\s+\([^()]*\)\s*$", "", v).strip()
    if k in ("reads", "exercises") and isinstance(v, list):
        return sorted({_clean(x) for x in v if x})
    return v


DECLARATIONS = "design/concepts/%s/version/exercises.json"


def _aslist(v):
    return [v] if isinstance(v, str) else list(v or [])


def declarations(root, mod):
    """{check id: [paths or "*"]}: what a check exercises, declared beside the test table (`exercises.json`, field
    `checks`) so that a declaration never edits the locked table. Absent: {}. A file that does not parse raises: a
    declaration that cannot be read is never read as none."""
    p = os.path.join(root, DECLARATIONS % mod)
    if not os.path.isfile(p):
        return {}
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return {k: _aslist(v) for k, v in (d.get("checks") or {}).items()}


def mod_root(mod):
    return "src/RimMandrake/%s" % mod


def in_repo(p):
    """A declared path git can diff: repo-relative, not absolute (`/mnt/c/...`), not a drive path (`C:\\...`), no `..`.
    A path outside the repository never changes in a commit, and git refuses a pathspec holding one (exit 128), which
    made a whole table's change unreadable (RIMMANDRAKE_KEEP_RERUN_RELATION_READABLE_PAST_THE_STEAM_FOLDER)."""
    p = str(p or "")
    return bool(p) and not p.startswith("/") and not re.match(r"^[A-Za-z]:", p) and ".." not in p.split("/")


def declared(spec, mod):
    """-> (paths, whole): the paths a check declares (exercises + reads + file), and whether it declares the whole mod
    (exercises "*", the mod folder itself or a parent of it, or a full-list check)."""
    spec = spec or {}
    raw = []
    for k in ("exercises", "reads"):
        v = spec.get(k)
        raw.extend([v] if isinstance(v, str) else list(v or []))
    if spec.get("file"):
        raw.append(spec["file"])
    paths, whole = [], spec.get("kind") == "live_full"
    root = mod_root(mod)
    for r in raw:
        if str(r).strip() == WHOLE:
            whole = True
            continue
        p = _clean(r)
        if not p:
            continue
        if (root + "/").startswith(p.rstrip("/") + "/"):        # the mod folder or a parent of it
            whole = True
            continue
        paths.append(p)
    return sorted(set(paths)), whole


def covers(decl, path):
    d = decl.rstrip("/")
    return path == d or path.startswith(d + "/")


def derived(path):
    return path.lower().endswith(DERIVED_EXT)


# ---- Python, by top-level name --------------------------------------------------------------------------------------

def _strip_doc(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        return body[1:]
    return body


def _refs(node):
    """Names a node reaches: Name ids, attribute names, and dict reads as 'N[k]' (a constant
    key) or 'N[?]' (a computed key); a Name used any other way reaches the whole N."""
    out = set()
    keyed = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name):
            s = n.slice
            s = getattr(s, "value", s) if type(s).__name__ == "Index" else s
            out.add("%s[%s]" % (n.value.id, s.value) if isinstance(s, ast.Constant) and isinstance(s.value, str)
                    else "%s[?]" % n.value.id)
            keyed.add(id(n.value))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" \
                and isinstance(n.func.value, ast.Name) and n.args:
            a = n.args[0]
            out.add("%s[%s]" % (n.func.value.id, a.value) if isinstance(a, ast.Constant) and isinstance(a.value, str)
                    else "%s[?]" % n.func.value.id)
            keyed.add(id(n.func.value))
        elif isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], (ast.In, ast.NotIn)) \
                and isinstance(n.comparators[0], ast.Name):
            a, nm = n.left, n.comparators[0].id                 # `k in N`: a membership read keyed by k
            out.add("%s[%s]" % (nm, a.value) if isinstance(a, ast.Constant) and isinstance(a.value, str)
                    else "%s[?]" % nm)
            keyed.add(id(n.comparators[0]))
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and id(n) not in keyed:
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def _strings(node):
    return {n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def py_symbols(text):
    """-> {symbol: (dump, refs, strings)} or None when the text does not parse. Symbols: each top-level def or class by
    name; each assignment to one name by that name, a dict literal of constant keys also key by key ('N[k]') and a
    tuple, list or set literal of strings element by element; each
    imported name; '<module>' for every other top-level statement together."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    out, other = {}, []
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = _strip_doc(list(st.body))
            dump = ast.dump(st.__class__(**dict(ast.iter_fields(st), body=body)))
            out[st.name] = (dump, _refs(st), _strings(st))
        elif isinstance(st, (ast.Assign, ast.AnnAssign)) and len(getattr(st, "targets", [st.target if
                                                                                         hasattr(st, "target") else None])) == 1:
            tgt = st.targets[0] if isinstance(st, ast.Assign) else st.target
            if not isinstance(tgt, ast.Name) or st.value is None:
                other.append(st)
                continue
            v = st.value
            if isinstance(v, ast.Dict) and v.keys and all(isinstance(k, ast.Constant) and isinstance(k.value, str)
                                                          for k in v.keys):
                out[tgt.id] = ("dict", set(), set())
                for k, val in zip(v.keys, v.values):
                    out["%s[%s]" % (tgt.id, k.value)] = (ast.dump(val), _refs(val), _strings(val) | {k.value})
            elif isinstance(v, (ast.Tuple, ast.List, ast.Set)) and v.elts and all(
                    isinstance(e, ast.Constant) and isinstance(e.value, str) for e in v.elts):
                out[tgt.id] = ("dict", set(), set())         # a literal of names relates element by element
                for e in v.elts:
                    out["%s[%s]" % (tgt.id, e.value)] = ("in", {e.value} if IDENT.match(e.value) else set(), {e.value})
            else:
                out[tgt.id] = (ast.dump(v), _refs(v), _strings(v))
        elif isinstance(st, (ast.Import, ast.ImportFrom)):
            for a in st.names:
                nm = (a.asname or a.name).split(".")[0]
                out[nm] = (ast.dump(st), set(), set())
        else:
            other.append(st)
    out["<module>"] = ("\n".join(ast.dump(s) for s in other), set(), set())
    return out


def py_changed(old, new):
    """Symbols that differ between two symbol tables (added, removed, or a different dump)."""
    return {k for k in set(old) | set(new) if (old.get(k) or (None,))[0] != (new.get(k) or (None,))[0]}


def py_reach(tables, seeds, added=frozenset()):
    """-> {path: reached symbols}: from the seeds (the check's id and entry), every top-level symbol of the declared
    Python files that a reached symbol names, to a fixed point. Anchors: a symbol named by a seed, a dict key equal to
    a seed, or a def, class or dict entry holding a seed as a string. Only an anchor's own strings count as names (the
    dispatch it makes by string: a getattr, a key); a string deeper down names nothing, or one big table would reach
    every scene in the mod. `added`: (path, 'N[k]') entries absent at the old commit; a whole-table use does not
    reach them."""
    seeds = {s for s in seeds if s}
    names = set(seeds)
    strings = set(seeds)
    ids = {x for x in seeds if ROW_ID.match(x)}
    reached = {p: set() for p in tables}
    grew = True
    while grew:
        grew = False
        for p, tab in tables.items():
            for sym, (dump, refs, strs) in tab.items():
                if sym in reached[p] or sym == "<module>":
                    continue
                m = re.match(r"^(.*)\[(.*)\]$", sym)
                anchor = sym in seeds or (dump != "dict" and bool(strs & seeds)) or bool(m and m.group(2) in seeds)
                if m:
                    n, k = m.groups()
                    keyed = sym in names or ("%s[?]" % n in names and k in strings)
                    # an entry added to a table is reached by its key only: a loop over the whole table meets one
                    # more entry, the new feature's, and that feature's own checks look it up by key
                    hit = anchor or keyed or (n in names and (p, sym) not in added)
                else:
                    # a def that writes a row id an anchor names (row(rows, "M8_...")) makes that row: reached, though
                    # its own strings name nothing further
                    hit = anchor or sym in names or (dump != "dict" and bool(strs & ids))
                if hit:
                    reached[p].add(sym)
                    names |= refs
                    if anchor:          # an anchor's own strings name what it dispatches to (getattr, a key)
                        add = {x for x in strs if IDENT.match(x)}
                        names |= add
                        strings |= add
                        ids |= {x for x in add if ROW_ID.match(x)}
                    grew = True
    return reached


# ---- JSON, by object ------------------------------------------------------------------------------------------------

def _find(obj, seeds, path=()):
    """Every (path, object) in a JSON tree whose "id" is a seed or whose dict key is a seed."""
    out = []
    if isinstance(obj, dict):
        if obj.get("id") in seeds:
            out.append((path, obj))
        for k, v in obj.items():
            if k in seeds:
                out.append((path + (k,), v))
            else:
                out.extend(_find(v, seeds, path + (k,)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(_find(v, seeds, path + (i,)))
    return out


def json_touches(old_text, new_text, seeds):
    """-> True/False when the file holds the check's object at either commit (its change decides), None when it does
    not (the file relates whole)."""
    try:
        old = json.loads(old_text) if old_text is not None else None
        new = json.loads(new_text) if new_text is not None else None
    except ValueError:
        return None
    a = [json.dumps(o, sort_keys=True) for _, o in _find(old, seeds)] if old is not None else []
    b = [json.dumps(o, sort_keys=True) for _, o in _find(new, seeds)] if new is not None else []
    if not a and not b:
        return None
    return a != b


# ---- the relation ---------------------------------------------------------------------------------------------------

def _srchash_sources(text, mod):
    """The C# files a DLL is compiled from, repo-relative, from its .srchash (paths relative to Source/)."""
    out = []
    base = mod_root(mod) + "/Source"
    for ln in (text or "").splitlines():
        if ln.startswith("#") or " " not in ln:
            continue
        rel = ln.split(" ", 1)[1].strip()
        out.append(os.path.normpath(os.path.join(base, rel)).replace("\\", "/"))
    return out


def scope(git, mod, sha, specs):
    """The paths a change is read under: the mod's source, its design folder, every path a check declares, and every
    C# file the mod's DLLs are compiled from."""
    paths = {mod_root(mod), "design/concepts/%s" % mod}
    for s in specs.values():
        paths.update(declared(s, mod)[0])
    for p in (git.show(sha, mod_root(mod) + "/Assemblies") or "").splitlines():
        if p.endswith(".srchash"):
            paths.update(_srchash_sources(git.show(sha, "%s/Assemblies/%s" % (mod_root(mod), p)), mod))
    return sorted(p for p in paths if in_repo(p))


class Relation:
    """The change relation of one mod's test table, read at commit NEW. `touches(id, old)` answers one check."""

    def __init__(self, root, mod, tests, new=None, runner=subprocess.run, old_tests=None):
        self.root, self.mod, self.tests = root, mod, dict(tests)
        self.git = Git(root, runner)
        self.new = self.git.rev(new or "HEAD")
        self._scope = {}
        self._py = {}
        self.old_tests = old_tests          # {old sha: {id: spec}} for a test; else read from git
        self.extra = declarations(root, mod)

    def _scope_for(self, old):
        if old not in self._scope:
            self._scope[old] = sorted(set(scope(self.git, self.mod, self.new, self.tests)) |
                                      set(scope(self.git, self.mod, old, self.tests)))
        return self._scope[old]

    def change(self, old):
        """Files changed between OLD and NEW in the mod's scope, or None when git cannot say."""
        o = self.git.rev(old)
        if not o or not self.new:
            return None
        return self.git.changed(o, self.new, self._scope_for(o))

    def unshipped(self, path):
        """True when the mod's .hashignore at NEW lists the path: a file that never ships and never changes what the mod
        does, so the mod hash (modcheck/status.py mod_hash, same grammar) leaves it out. A mod without the file: False."""
        if not hasattr(self, "_ignore"):
            txt = self.git.show(self.new, mod_root(self.mod) + "/.hashignore") if self.new else None
            self._ignore = [l.split("#")[0].strip() for l in (txt or "").splitlines() if l.split("#")[0].strip()]
        root = mod_root(self.mod) + "/"
        if not path.startswith(root):
            return False
        rel = path[len(root):]
        return any(rel == g or rel.startswith(g.rstrip("/") + "/") or (g.endswith("*") and rel.startswith(g[:-1]))
                   for g in self._ignore)

    def _table_at(self, old):
        if self.old_tests is not None:
            return self.old_tests.get(old)
        txt = self.git.show(old, "design/concepts/%s/version/test_table.json" % self.mod)
        try:
            t = json.loads(txt) if txt else None
        except ValueError:
            return None
        t = (t or {}).get("tests")
        if isinstance(t, list):
            t = {x.get("id"): x for x in t if isinstance(x, dict)}
        return t

    def _syms(self, sha, path):
        k = (sha, path)
        if k not in self._py:
            txt = self.git.show(sha, path)
            self._py[k] = py_symbols(txt) if txt is not None else {}
        return self._py[k]

    def _mod_py(self, sha):
        """{module stem: [repo paths]} of the mod's Python files at the commit."""
        k = ("ls", sha)
        if k not in self._py:
            out = self.git._git("ls-tree", "-r", "--name-only", sha, "--", mod_root(self.mod) + "/")
            m = {}
            for f in (out.decode().splitlines() if out else []):
                if f.endswith(".py"):
                    m.setdefault(os.path.basename(f)[:-3], []).append(f)
            self._py[k] = m
        return self._py[k]

    def py_closure(self, files, old):
        """The mod's own Python files that the declared ones import, to a fixed point, at either commit (a cheap
        static read that fills a declaration: a scene script's own modules)."""
        seen = set()
        todo = list(files)
        while todo:
            f = todo.pop()
            if f in seen:
                continue
            seen.add(f)
            for sha in (self.new, old):
                stems = self._mod_py(sha)
                for nm in self._imports(sha, f):
                    todo.extend(stems.get(nm, []))
        return seen - set(files)

    def _imports(self, sha, f):
        """The names a Python file imports at a commit, parsed once per relation (python-imports-read-once-per-commit:
        every check of a table declares the same scene files, and a blob at a commit never changes)."""
        k = ("imports", sha, f)
        if k not in self._py:
            names = set()
            txt = self.git.show(sha, f)
            try:
                tree = ast.parse(txt) if txt else None
            except (SyntaxError, ValueError):
                tree = None
            for n in ast.walk(tree) if tree is not None else ():
                if isinstance(n, ast.Import):
                    names.update(part for a in n.names for part in a.name.split("."))
                elif isinstance(n, ast.ImportFrom):
                    names.update((n.module or "").split("."))
                    names.update(a.name for a in n.names)
            self._py[k] = names
        return self._py[k]

    def touches(self, tid, old):
        """-> (state, why, files): state 'untouched' | 'touched' | 'unreadable'. files: the changed files that touch."""
        spec = self.tests.get(tid) or {}
        paths, whole = declared(dict(spec, exercises=_aslist(spec.get("exercises")) + self.extra.get(tid, [])),
                                self.mod)
        if not paths and not whole:
            return "unreadable", "the check declares nothing it reads or exercises (no exercises, reads or file)", []
        if not whole and not any(in_repo(p) for p in paths):
            return "unreadable", "the check declares only paths outside the repository (%s), which no commit shows" % paths[0], []
        o = self.git.rev(old)
        if not o:
            return "unreadable", "its row names no commit git can resolve (%s)" % (old or "no mod_sha"), []
        if o == self.new:
            return "untouched", "made on the commit now", []
        ch = self.change(o)
        if ch is None:
            return "unreadable", "git cannot list the change %s..%s" % (o[:10], self.new[:10]), []
        ot = self._table_at(o)
        if ot is None:
            return "unreadable", "the test table at %s cannot be read, so whether its entry changed is unknown" % (
                o[:10]), []
        if tid in ot and any(run_key(ot[tid], k) != run_key(spec, k) for k in RUN_KEYS):
            keys = [k for k in RUN_KEYS if run_key(ot[tid], k) != run_key(spec, k)]
            return "touched", "its test-table entry changed (%s)" % ", ".join(keys), ["test_table.json"]
        if whole:
            under = [f for f in ch if covers(mod_root(self.mod), f)]
            hit = [f for f in under if not self.unshipped(f)]
            if hit:
                return "touched", "a whole-mod check: %d changed file(s) under the mod" % len(hit), hit
            if under:
                return ("untouched", "a whole-mod check, and each of the %d changed file(s) under the mod is one its "
                        ".hashignore lists (never ships; the mod hash does not move)" % len(under), [])
            return "untouched", "a whole-mod check, and nothing under the mod changed", []
        imported = self.py_closure([p for p in paths if p.endswith(".py")], o)
        mine = [f for f in ch if not derived(f) and (any(covers(p, f) for p in paths) or f in imported)]
        if not mine:
            return "untouched", "no changed file is one it declares or its Python imports", []
        seeds = {tid, spec.get("entry")}
        hits, why = [], []
        pys = [f for f in mine if f.endswith(".py")]
        if pys:
            decl_py = sorted({p for p in paths if p.endswith(".py")} | set(pys) | imported)
            tables_new = {p: self._syms(self.new, p) for p in decl_py}
            tables_old = {p: self._syms(o, p) for p in decl_py}
            added = {(p, k) for p in decl_py for k in (tables_new.get(p) or {})
                     if "[" in k and k not in (tables_old.get(p) or {})}
            reach = py_reach({p: (tables_new[p] or {}) for p in decl_py if tables_new[p] is not None}, seeds, added)
            reach_old = py_reach({p: (tables_old[p] or {}) for p in decl_py if tables_old[p] is not None}, seeds)
            for f in pys:
                a, b = tables_old.get(f), tables_new.get(f)
                if a is None or b is None:
                    hits.append(f)
                    why.append("%s does not parse at one commit (related whole)" % f)
                    continue
                r = reach.get(f, set()) | reach_old.get(f, set())
                chg = py_changed(a, b)
                got = sorted(chg & r)
                if "<module>" in chg and r:
                    got.append("<module>")
                if not r and f == _clean(spec.get("file")):
                    hits.append(f)
                    why.append("%s: no top-level name reached from %s (related whole)" % (
                        f, " or ".join(sorted(s for s in seeds if s))))
                elif got:
                    hits.append(f)
                    why.append("%s: %s" % (f, ", ".join(got[:6]) + (" ..." if len(got) > 6 else "")))
        for f in mine:
            if f.endswith(".py"):
                continue
            if f.endswith(".json"):
                t = json_touches(self.git.show(o, f), self.git.show(self.new, f), {s for s in seeds if s})
                if t is False:
                    continue
                hits.append(f)
                why.append("%s: %s" % (f, "its own entry changed" if t else "changed (related whole)"))
                continue
            hits.append(f)
            why.append(f)
        if hits:
            return "touched", "; ".join(why), hits
        return "untouched", "declared file(s) changed only in parts it does not reach (%s)" % ", ".join(mine), []

    def undeclared(self, old):
        """Changed files under the mod's source that no check declares (derived files left out), for declaring."""
        ch = self.change(old) or []
        decl = set()
        for t, s in self.tests.items():
            decl.update(declared(dict(s, exercises=_aslist(s.get("exercises")) + self.extra.get(t, [])), self.mod)[0])
        return [f for f in ch if covers(mod_root(self.mod), f) and not derived(f)
                and not any(covers(p, f) for p in decl)]


def relate(root, mod, tests, last_rows, new=None, runner=subprocess.run, old_tests=None):
    """tests: {id: spec}; last_rows: {id: row or None}. -> {rows: {id: {state, why, files, old}}, touched, unreadable,
    untouched, norow, undeclared, new}."""
    rel = Relation(root, mod, tests, new=new, runner=runner, old_tests=old_tests)
    out = {"rows": {}, "touched": [], "unreadable": [], "untouched": [], "norow": [], "undeclared": [],
           "new": rel.new}
    olds = set()
    for t in tests:
        r = last_rows.get(t)
        if not r:
            out["norow"].append(t)
            continue
        old = r.get("mod_sha")
        st, why, files = rel.touches(t, old)
        out["rows"][t] = {"state": st, "why": why, "files": files, "old": old}
        out[st].append(t)
        if st != "unreadable" and rel.git.rev(old):
            olds.add(rel.git.rev(old))
    und = set()
    for o in olds:
        und.update(rel.undeclared(o))
    out["undeclared"] = sorted(und)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", required=True)
    ap.add_argument("--old", help="one commit for every check (default: each check's last in-game row's mod_sha)")
    ap.add_argument("--new", default="HEAD")
    ap.add_argument("--tests", choices=("ingame", "all"), default="ingame",
                    help="which checks: the stage-6 in-game ones (default) or every test of the table, offline included")
    ap.add_argument("--root", default=REPO)
    a = ap.parse_args(argv)
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import maturation as M
    tt, err = M.read_json(a.root, a.mod, "version/test_table.json")
    if tt is None:
        print("UNREADABLE: test_table.json: %s" % err)
        return 3
    tests = dict(M.ingame_tests(tt)) if a.tests == "ingame" else {
        k: v for k, v in ((tt.get("tests") or {}).items() if isinstance(tt.get("tests"), dict) else
                          ((x.get("id"), x) for x in tt.get("tests") or [])) if isinstance(v, dict)}
    if a.old:
        last = {t: {"mod_sha": a.old} for t in tests}
    else:
        import build_match as BM
        last = BM.carried_rows(a.root, a.mod)
    res = relate(a.root, a.mod, tests, last, new=a.new)
    for t in res["touched"]:
        print("RERUN  %s: %s" % (t, res["rows"][t]["why"]))
    for t in res["unreadable"]:
        print("RERUN  %s (no readable relation, declare it): %s" % (t, res["rows"][t]["why"]))
    for t in res["norow"]:
        print("RUN    %s: no row yet" % t)
    for f in res["undeclared"]:
        print("UNDECLARED  %s: changed, and no check declares it" % f)
    print("relation: %d check(s), %d touched, %d with no readable relation, %d with no row, %d untouched; "
          "%d changed file(s) under the mod no check declares" % (
              len(tests), len(res["touched"]), len(res["unreadable"]), len(res["norow"]), len(res["untouched"]),
              len(res["undeclared"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
