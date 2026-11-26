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
  .cs    by member and by switch section (cs_units, a lexical read): a changed member or `case "x":` section touches
         the check only when the members and sections its id and entry reach include it (a section by its label, a
         helper by its name, `goto case` by its string; a section no check's entry labels runs with its method). It
         relates whole when the file does not read at either commit, the check anchors in no member or section of it,
         a using or namespace line changed, the changed member carries an attribute, is called by the engine (override,
         Unity message), is named in another .cs or .py file of the mod, or is reached by no check. A changed section
         that uses a shared static the check reaches touches it too. A declared C# file reads the mod's C# files that
         define a type it names (a partial class's other parts among them; to a fixed point; of the project a
         .srchash names): there a member touches the check only when the check reaches its name and its type's name,
         by name alone (no string, label or list value), and an engine-called member when the check names its type. A
         check that anchors in no C# and lists C# in its `exercises` is related by that list alone.
         A path may name parts: `F.cs::Type,member` (those types and members, and what they name in F.cs) and `F.cs::~`
         (the members of F.cs that the check's other declared C# names: a settings or tuning file). "none" in exercises
         says that the check was read and exercises no C#.
         A file whose .srchash line differs between OLD and NEW changed in the DLL, whatever its text: it relates whole.
         A check that runs in the game and declares no C# that ships has no readable relation to a change of shipped C#.
         The DLL's bytes relate to nothing by themselves.
  other  by file.
An entry is read against its check's scene (declaration_check.py): one that leaves out C# the scene names is touched by a
change there, and one that says none while its scene names C# has no readable relation.
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
# a row or check id: two parts or more, not PASS; a shipped def name (RM_, RSW_, RUT_) is none (Pyrelands visit 8: "RM_FurnaceBeast"
# made every def that names the creature part of the check)
ROW_ID = re.compile(r"^(?!(?:RM|RSW|RUT)_)[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]{4,}$")
WHOLE = "*"
NONE = "none"       # in `exercises`: the check was read, and it exercises no C# of the mod
PART = "::"         # F.cs::Type,member
REACHED = "~"       # F.cs::~ : the members of F.cs that the check's other declared C# names


# ---- git, cached ----------------------------------------------------------------------------------------------------

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
# A blob at a full commit id never changes, so reads at one are shared by every Git and Relation of one process that
# uses the same root and runner (item RIMMANDRAKE_FIND_SLOW_PIPELINE_COMMANDS_HE_ASKED_FOR_INSTANT_ONES: the forecast
# rebuilt the relations on each of 31 simulated ticks, 62 s of git reads each). Keyed by runner, so a test's fake runner
# never sees another's reads; the runner object is kept in the key, so its id cannot be reused.
# budget: danger=memory of a long-lived importer that reads many commits; evidence=one forecast tick reads about 1,700
# budget: blobs (profile 2026-11-25); the shared store is emptied when it passes 10x a 10-tick forecast's reads
SHARED_MAX = 20000
_SHARED = {}


def _shared(kind, root, runner, sha, key):
    """-> (store, k) when this read may be shared (a full commit id), else (None, None)."""
    if not (isinstance(sha, str) and FULL_SHA.match(sha)):
        return None, None
    if len(_SHARED) > SHARED_MAX:
        _SHARED.clear()
    return _SHARED, (kind, root, runner, sha, key)


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
            store, sk = _shared("show", self.root, self.run, sha, path)
            if store is not None and sk in store:
                self._show[k] = store[sk]
                return self._show[k]
            out = self._git("show", "%s:%s" % (sha, path))
            self._show[k] = out.decode("utf-8", "replace") if out is not None else None
            if store is not None and out is not None:       # a failed read is not shared: it may be a passing fault
                store[sk] = self._show[k]
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

def part_names(p):
    """The types and members that a declared path names (`F.cs::Type,member`, `F.cs::~`); None for a whole path."""
    raw = re.split(r"\s+\(", str(p or "").strip(), maxsplit=1)[0]
    if PART not in raw:
        return None
    return {x.strip() for x in raw.split(PART, 1)[1].split(",") if x.strip()}


def _clean(p):
    """A declared path, without its parts, prose in brackets and a leading ./ ; '' when nothing is left."""
    p = str(p or "").strip()
    p = re.split(r"\s+\(", p, maxsplit=1)[0].strip()
    p = p.split(PART, 1)[0].strip()
    p = p.replace("\\", "/")
    return p[2:] if p.startswith("./") else p


def run_key(spec, k):
    """A test-table field as it bears on what the check runs: a command's trailing note in brackets (`(minimal list;
    entry exists)`) is the table maker's prose, not part of what runs; lists compare as sets of cleaned paths."""
    v = (spec or {}).get(k)
    if k == "command" and isinstance(v, str):
        return re.sub(r"\s+\([^()]*\)\s*$", "", v).strip()
    if k in ("reads", "exercises") and isinstance(v, list):
        return sorted({_clean(x) if part_names(x) is None else _clean(x) + PART + ",".join(sorted(part_names(x))) for x in v if x})
    return v


DECLARATIONS = "design/concepts/%s/version/exercises.json"


def _aslist(v):
    return [v] if isinstance(v, str) else list(v or [])


def declarations(root, mod):
    """{check id: [paths or "*"]}: what a check exercises, declared beside the test table (`exercises.json`, field
    `checks`) so that a declaration never edits the locked table. Absent: {}. A file that does not parse raises: a
    declaration that cannot be read is never read as none."""
    return read_declarations(os.path.join(root, DECLARATIONS % mod))[0]


def read_declarations(p):
    """-> ({check id: [paths]}, {check id: {path: why}}, why off): the `checks`, the `left_out` (what an entry leaves out on
    purpose, declaration_check.py) and the `scene_check` ("off: <why>": a left-out name reruns nothing) of an
    exercises.json. Absent: empty."""
    if not os.path.isfile(p):
        return {}, {}, ""
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return {k: _aslist(v) for k, v in (d.get("checks") or {}).items()}, dict(d.get("left_out") or {}), str(
        d.get("scene_check") or "")


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
        if not p or p == NONE:
            continue
        if (root + "/").startswith(p.rstrip("/") + "/"):        # the mod folder or a parent of it
            whole = True
            continue
        paths.append(p)
    return sorted(set(paths)), whole


def declared_cs(paths):
    """True when a declared list names a C# file."""
    return any(_clean(p).endswith(".cs") for p in paths)


def declared_parts(spec):
    """{C# file: the types and members declared of it}, for a file that the check declares by its parts only: a path that
    covers the file whole (itself or a folder) is the whole file."""
    raw = [x for k in ("exercises", "reads") for x in _aslist((spec or {}).get(k))] + _aslist((spec or {}).get("file"))
    parts = {}
    for r in raw:
        if part_names(r) is not None:
            parts.setdefault(_clean(r), set()).update(part_names(r))
    wholes = [_clean(r) for r in raw if part_names(r) is None and str(r).strip() not in (WHOLE, NONE)]
    return {f: n for f, n in parts.items() if not any(w and covers(w, f) for w in wholes)}


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


def _call_name(v):
    """'a.b.c' of a call's function, or ''."""
    f, parts = getattr(v, "func", None), []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    return ".".join(reversed(parts + [f.id])) if isinstance(f, ast.Name) else ""


def _registers_a_file(st, defs):
    """-> name f when `st` is a bare `f()` and f's body only loads another file and calls its `register(suite, ...)` (the
    chains of that file, which the checks of that file declare); else None. A body that does anything else relates whole."""
    v = st.value if isinstance(st, ast.Expr) else None
    if not (isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and not v.args and not v.keywords):
        return None
    d = defs.get(v.func.id)
    if d is None:
        return None
    registered = False
    todo = _strip_doc(list(d.body))
    while todo:
        b = todo.pop(0)
        if isinstance(b, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(b, ast.For) and isinstance(b.target, ast.Name) and not b.orelse and isinstance(b.iter, (ast.Tuple, ast.List)) \
                and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in b.iter.elts):
            todo = list(b.body) + todo    # the same few statements for each named file
            continue
        if isinstance(b, ast.Assign) and len(b.targets) == 1 and isinstance(b.targets[0], ast.Name) \
                and _call_name(b.value) in ("importlib.util.spec_from_file_location", "importlib.util.module_from_spec"):
            continue
        c = b.value if isinstance(b, ast.Expr) and isinstance(b.value, ast.Call) else None
        nm = _call_name(c) if c is not None else ""
        if nm.endswith(".loader.exec_module"):
            continue
        if nm.endswith(".register") and c.args and isinstance(c.args[0], ast.Name) and c.args[0].id == "suite":
            registered = True
            continue
        return None
    return v.func.id if registered else None


def py_symbols(text):
    """-> {symbol: (dump, refs, strings)} or None when the text does not parse. Symbols: each top-level def or class by
    name; each assignment to one name by that name, a dict literal of constant keys also key by key ('N[k]') and a
    tuple, list or set literal of strings element by element; each
    imported name; '<call f>' for a bare f() that only registers another file's chains; '<module>' for every other top-level
    statement together."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    out, other = {}, []
    defs = {st.name: st for st in tree.body if isinstance(st, ast.FunctionDef)}
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
            f = _registers_a_file(st, defs)
            if f:   # its chains live in the file it loads; an added registration changes no other check
                out["<call %s>" % f] = (ast.dump(st), set(), set())
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


# ---- C#, by member and by scene section -----------------------------------------------------------------------------
# One proof file can hold every scene of a mod (ExplosiveKnockback RM_KnockbackProof.cs: 2,832 lines, one `case
# "<entry>":` section per scene). Related by file, one scene's edit sent all 54 scene checks of visit 5 back
# (2026-11-23). A lexical read, no compiler: a file it cannot read relates whole.

CS_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CS_TYPE_KW = ("class", "struct", "interface", "enum", "record")
# Unity calls these by name on a MonoBehaviour; nothing in the file names them
UNITY_MESSAGES = {"Awake", "Start", "Update", "LateUpdate", "FixedUpdate", "OnGUI", "OnDestroy", "OnEnable",
                  "OnDisable", "OnApplicationQuit", "OnApplicationFocus", "OnApplicationPause"}
CS_LIST_TOKENS = {"new", "string"}


def cs_mask(text):
    """-> (code, plain, strings) or None when a comment or a literal does not close. code: the text with comments and
    the contents of string and char literals blanked (same length, newlines kept; an interpolation hole stays code);
    plain: the text with comments alone blanked; strings: [(position, value)] of each string literal."""
    n = len(text)
    code, plain = list(text), list(text)
    strings = []

    def blank(buf, a, b):
        for k in range(a, b):
            if buf[k] != "\n":
                buf[k] = " "

    def simple(j):
        """A regular string from the quote at j: -> its end (after the closing quote), or -1."""
        k = j + 1
        while k < n and text[k] != '"':
            if text[k] == "\n":
                return -1
            k += 2 if text[k] == "\\" else 1
        return k + 1 if k < n else -1

    i = 0
    while i < n:
        c = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            blank(code, i, j)
            blank(plain, i, j)
            i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j < 0:
                return None
            blank(code, i, j + 2)
            blank(plain, i, j + 2)
            i = j + 2
        elif c == "'":
            j = i + 1
            j = text.find("'", j + 2 if j < n and text[j] == "\\" else j + 1)
            if j < 0 or j - i > 12:
                return None
            blank(code, i + 1, j)
            i = j + 1
        elif c == '"' or (c in "$@" and re.match(r'[$@]{1,2}"', text[i:i + 3])):
            pre = re.match(r'[$@]{0,2}', text[i:i + 2]).group(0)
            q = i + len(pre)
            if "@" not in pre and text.startswith('"""', q):   # a raw literal (@""" is a verbatim one opening on "")
                j = text.find('"""', q + 3)
                if j < 0:
                    return None
                strings.append((i, text[q + 3:j]))
                blank(code, q + 1, j + 2)
                i = j + 3
                continue
            verb, interp = "@" in pre, "$" in pre
            k, val = q + 1, []
            while True:
                if k >= n:
                    return None
                ch = text[k]
                if verb and ch == '"':
                    if text.startswith('""', k):
                        val.append('"')
                        blank(code, k, k + 2)
                        k += 2
                        continue
                    break
                if not verb and ch == '"':
                    break
                if not verb and ch == "\n":
                    return None
                if not verb and ch == "\\":
                    val.append(text[k:k + 2])
                    blank(code, k, k + 2)
                    k += 2
                    continue
                if interp and ch == "{":
                    if text.startswith("{{", k):
                        blank(code, k, k + 2)
                        k += 2
                        continue
                    depth, k = 1, k + 1                         # a hole: code, its own strings blanked
                    while k < n and depth:
                        if text[k] == '"':
                            e = simple(k)
                            if e < 0:
                                return None
                            blank(code, k + 1, e - 1)
                            k = e
                            continue
                        depth += {"{": 1, "}": -1}.get(text[k], 0)
                        k += 1
                    if depth:
                        return None
                    continue
                val.append(ch)
                blank(code, k, k + 1)
                k += 1
            strings.append((i, "".join(val)))
            i = k + 1
        else:
            i += 1
    return "".join(code), "".join(plain), strings


def _pairs(code, open_c, close_c):
    st, out = [], {}
    for i, ch in enumerate(code):
        if ch == open_c:
            st.append(i)
        elif ch == close_c:
            if not st:
                return None
            out[st.pop()] = i
    return out if not st else None


class CsUnit:
    __slots__ = ("key", "name", "kind", "spans", "parent", "labels", "flags", "text", "refs", "strs", "static", "calls",
                 "arity", "head")

    def __init__(self, key, name, kind, a, b, parent):
        self.key, self.name, self.kind, self.spans, self.parent = key, name, kind, [(a, b)], parent
        self.labels, self.flags, self.static = set(), set(), False
        self.calls, self.arity, self.head = {}, (0, float("inf")), None


def _strip_attrs(code, a, b, sq):
    """-> (start after any leading [attribute] sections, had one)."""
    had = False
    while True:
        m = re.compile(r"\s*").match(code, a, b)
        a = m.end()
        if a < b and code[a] == "[" and a in sq and sq[a] < b:
            a, had = sq[a] + 1, True
        else:
            return a, had


def cs_units(text):
    """-> {key: CsUnit} or None when the file cannot be read. Units: each member of each type (by name and signature),
    each nested type's own head, each section of each switch (by its labels; stacked labels are one section), each
    element of a string-literal list field ('N[value]'), and '<file>' (usings, namespace heads, anything unnamed)."""
    m = cs_mask(text)
    if m is None:
        return None
    code, plain, strings = m
    br, pa, sq = _pairs(code, "{", "}"), _pairs(code, "(", ")"), _pairs(code, "[", "]")
    if br is None or pa is None or sq is None:
        return None
    units = {}
    filed = CsUnit("<file>", "<file>", "file", 0, 0, None)
    filed.spans = []
    units["<file>"] = filed

    def add(u):
        k, i = u.key, 1
        while u.key in units:
            i += 1
            u.key = "%s#%d" % (k, i)
        units[u.key] = u
        return u

    def flat(a, b):
        """code[a:b] with each bracketed group's inside cut: a parameter's default (`string stuff = null`) is not an
        initializer of the member."""
        out, i = [], a
        while i < b:
            ch = code[i]
            if ch in "([" and (pa if ch == "(" else sq).get(i, b) < b:
                out.append("()" if ch == "(" else "[]")
                i = (pa if ch == "(" else sq)[i] + 1
                continue
            out.append(ch)
            i += 1
        return "".join(out)

    def items(a, b):
        """Top-level items of a body [a, b): (start, end, brace) -- brace the position of the item's own body '{'."""
        out, i, s = [], a, a
        while i < b:
            ch = code[i]
            if ch == ";":
                out.append((s, i + 1, None))
                s = i + 1
            elif ch == "{":
                head = flat(s, i)
                j = br[i]
                if re.search(r"(?<![=!<>])=(?![=>])|=>", head):     # an initializer: the item ends at its ';'
                    i = j + 1
                    continue
                out.append((s, j + 1, i))
                s = i = j + 1
                continue
            elif ch in "([":
                i = (pa if ch == "(" else sq)[i] + 1
                continue
            i += 1
        if code[s:b].strip():
            out.append((s, b, None))
        return out

    def body(a, b, prefix, parent, is_type):
        for s, e, brace in items(a, b):
            if not code[s:e].strip():
                continue
            hs, attr = _strip_attrs(code, s, e, sq)
            head = code[hs:brace if brace is not None else e]
            words = CS_WORD.findall(head)
            paren = head.find("(")
            mk = re.search(r"\b(class|struct|interface|enum|record)\b", head)
            if mk and paren >= 0 and mk.start() > paren:
                mk = None                                          # `where T : class` in a method's head
            if "namespace" in words or words[:1] == ["using"] or (not is_type and not mk):
                filed.spans.append((s, brace + 1 if brace is not None and "namespace" in words else e))
                if brace is not None and "namespace" in words:
                    filed.spans.append((br[brace], br[brace] + 1))
                    body(brace + 1, br[brace], prefix, parent, False)
                continue
            if mk and brace is not None and mk.group(1) != "enum":
                tw = CS_WORD.findall(head[mk.end():])
                nm = tw[0] if tw else "<anon>"
                u = add(CsUnit(prefix + nm, nm, "type", s, brace + 1, parent))
                u.spans.append((br[brace], br[brace] + 1))
                if attr:
                    u.flags.add("attribute")
                body(brace + 1, br[brace], prefix + nm + "/", u, True)
                continue
            cut = re.search(r"\(|(?<![=!<>])=(?![=>])|=>|\{|;", head)
            tok = cut.group(0) if cut else ";"
            bw = CS_WORD.findall(head[:cut.start()] if cut else head)
            nm = bw[-1] if bw else "<anon>"
            if mk:                                                 # an enum: one unit
                tw = CS_WORD.findall(head[mk.end():])
                nm, tok = (tw[0] if tw else "<anon>"), "enum"
            sig, p = "", None
            if tok == "(":
                p = hs + cut.start()
                sig = "(%s)" % " ".join(code[p + 1:pa.get(p, p)].split())
            kind = "method" if tok == "(" else "field"
            u = add(CsUnit(prefix + nm + sig, nm, kind, s, e, parent))
            if kind == "method":
                u.head, u.arity = p, params_range(p + 1, pa.get(p, p))
            if attr:
                u.flags.add("attribute")
            if "override" in words or (kind == "method" and nm in UNITY_MESSAGES):
                u.flags.add("called by the engine")
            if nm == "<anon>":
                u.flags.add("unnamed")
            # shared storage: a static field or auto-property, not a computed property (`static Map Map => ...`)
            u.static = (kind == "field" and "static" in words and "const" not in words and tok != "=>" and
                        (brace is None or not re.sub(r"\b(get|set|init|private|protected|internal)\b|[\s;]", "",
                                                     code[brace + 1:br[brace]])))
            if kind == "field" and tok == "=" and "const" not in words and "static" not in words:
                u.flags.add("instance initializer")
            if kind == "field" and tok == "=":
                init = code[hs + cut.end():e]
                rest = set(CS_WORD.findall(init)) - CS_LIST_TOKENS
                lits = [(p, v) for p, v in strings if hs + cut.end() <= p < e]
                if lits and not rest and not re.sub(r'[\s{}\[\],;"$@]', "", init):
                    for p, v in lits:                               # a string list relates element by element
                        q2 = p + len(re.match(r'[$@]*', code[p:p + 2]).group(0))
                        add(CsUnit("%s[%s]" % (u.key, v), v, "elem", p, code.index('"', q2 + 1) + 1, u))
            if kind == "method" and brace is not None:
                switches(brace + 1, br[brace], u.key, u)

    def switches(a, b, prefix, parent):
        """Each switch statement in [a, b) that no deeper switch holds, its sections as children of parent."""
        for mm in re.finditer(r"\bswitch\s*\(", code[a:b]):
            p = a + mm.end() - 1
            q = pa.get(p)
            if q is None:
                continue
            r = re.compile(r"\s*").match(code, q + 1).end()
            if r >= b or code[r] != "{":
                continue
            if any(a2 <= r < b2 for u2 in units.values() if u2.parent is parent and u2.kind == "case"
                   for a2, b2 in u2.spans):
                continue                                           # a deeper switch: its section reads it
            end, labels, i = br[r], [], r + 1
            while i < end:
                ch = code[i]
                if ch == "{":
                    i = br[i] + 1
                    continue
                if ch == "(":
                    i = pa[i] + 1
                    continue
                lm = re.compile(r"(case\b[^:;{}]*|default\s*):").match(code, i)
                if lm and not re.match(r"[A-Za-z0-9_.]", code[i - 1]):   # `goto case "x";` ends on ';', no label
                    labels.append((i, lm.end()))
                    i = lm.end()
                    continue
                i += 1
            groups, made = [], []
            for ls, le in labels:
                if groups and not code[groups[-1][-1][1]:ls].strip():
                    groups[-1].append((ls, le))
                else:
                    groups.append([(ls, le)])
            for g, grp in enumerate(groups):
                gs = grp[0][0]
                ge = groups[g + 1][0][0] if g + 1 < len(groups) else end
                labs = set()
                for ls, le in grp:
                    vals = [v for pp, v in strings if ls <= pp < le]
                    labs.update(vals or [" ".join(code[ls:le].split())])
                u = add(CsUnit("%s/case:%s" % (prefix, "|".join(sorted(labs))), "", "case", gs, ge, parent))
                u.labels = labs
                made.append((u, grp[-1][1]))
            for u, after in made:
                if falls_out(after, u.spans[0][1]):
                    u.flags.add("falls out")
                switches(after, u.spans[0][1], u.key, u)
            if parent is not None and parent.kind == "method" and made and lone_top(a, b, p) and plain_tail(end + 1, b):
                tail = add(CsUnit("%s/after switch" % prefix, "", "case", end + 1, b, parent))
                tail.flags.add("after switch")

    def args(i, j):
        """The count of arguments in code[i:j] (inside a call's parentheses), or None when unsure (a `<` may be a
        generic's comma)."""
        if not code[i:j].strip():
            return 0
        if "<" in code[i:j]:
            return None
        n, k = 1, i
        while k < j:
            ch = code[k]
            if ch in "([{":
                q = (pa if ch == "(" else sq if ch == "[" else br).get(k)
                if q is None or q >= j:
                    return None
                k = q + 1
                continue
            n += ch == ","
            k += 1
        return n

    def params_range(i, j):
        """(fewest, most) arguments a method whose parameter list is code[i:j] takes; (0, inf) when unsure."""
        whole = (0, float("inf"))
        if not code[i:j].strip():
            return (0, 0)
        if "<" in code[i:j] or "[" in code[i:j]:
            return whole
        parts = code[i:j].split(",") if "(" not in code[i:j] and "{" not in code[i:j] else None
        if parts is None:
            return whole
        if any(re.match(r"\s*params\b", x) for x in parts):
            return whole
        return (sum("=" not in x for x in parts), len(parts))

    def calls(own, head):
        """{word: the argument counts it is called with} over the spans `own`; None for an occurrence that is no plain
        call (a method group, a generic call, unsure). head: a method's own '(' (its name before it is no call)."""
        out = {}
        for a, b in own:
            for m in CS_WORD.finditer(code, a, b):
                q = re.compile(r"\s*").match(code, m.end()).end()
                if head is not None and q == head:
                    continue
                n = args(q + 1, pa[q]) if q < len(code) and code[q] == "(" and q in pa else None
                out.setdefault(m.group(0), set()).add(n)
        return out

    CONTROL = re.compile(r"\s*(?:else\s+)?(?:if|else|for|foreach|while|do|try|catch|finally|lock|using|checked|unchecked"
                         r"|unsafe|fixed)\b")

    def falls_out(a, b):
        """True unless the section [a, b) surely ends its method: its last statement at its own level (or in the one
        bare block it ends with) is `return` or `throw`, and it holds no break, goto, continue or yield (each may leave
        the switch). Unsure is True."""
        if re.search(r"(?<![A-Za-z0-9_])(?:break|goto|continue|yield)(?![A-Za-z0-9_])", code[a:b]):
            return True
        i, start, last, bare = a, a, None, None
        while i < b:
            ch = code[i]
            if ch in "([{":
                j = (pa if ch == "(" else sq if ch == "[" else br).get(i)
                if j is None or j >= b:
                    return True
                if ch == "{" and not code[start:i].strip():          # a bare block: a statement of its own
                    bare, start = (i + 1, j), j + 1
                elif ch == "{" and CONTROL.match(flat(start, i)):    # if/else/try ... { }: the statement ends here
                    bare, start, last = None, j + 1, None
                i = j + 1
                continue
            if ch == ";":
                last, start, bare = (start, i), i + 1, None
            i += 1
        if code[start:b].strip():
            return True
        if bare is not None:
            return falls_out(*bare)
        if last is None:
            return True
        return not re.match(r"\s*(?:return|throw)(?![A-Za-z0-9_])", code[last[0]:last[1]])

    def lone_top(a, b, p):
        """True when the switch whose '(' is at p is the one switch of the method body [a, b) and stands at its top
        level (no block of the body holds it)."""
        if any(a <= k < p and v > p for k, v in br.items()):
            return False
        tops = [m.start() + a for m in re.finditer(r"(?<![A-Za-z0-9_])switch\s*\(", code[a:b])
                if not any(a <= k < m.start() + a and v > m.start() + a for k, v in br.items())]
        return len(tops) == 1

    def plain_tail(a, b):
        """True when the code [a, b) after a switch holds only plain statements and control blocks: no lambda, no local
        function (a section before it may call one), no switch."""
        if "=>" in code[a:b] or re.search(r"(?<![A-Za-z0-9_])switch(?![A-Za-z0-9_])", code[a:b]):
            return False
        for m in re.finditer(r"\{", code[a:b]):
            q = a + m.start()
            h = max(code.rfind(";", a, q), code.rfind("{", a, q), code.rfind("}", a, q)) + 1
            if not CONTROL.match(flat(max(h, a), q)):
                return False
        return True

    body(0, len(code), "", None, False)
    kids = {}
    for u in units.values():
        if u.parent is not None:
            kids.setdefault(u.parent.key, []).extend(u.spans)
    for u in units.values():
        own = []
        for a, b in u.spans:
            cut = sorted((x, y) for x, y in kids.get(u.key, []) if a <= x < b)
            p = a
            for x, y in cut:
                own.append((p, x))
                p = max(p, y)
            own.append((p, b))
        u.text = " ".join(" ".join(plain[a:b].split()) for a, b in own)
        u.refs = {w for a, b in own for w in CS_WORD.findall(code[a:b])}
        u.calls = calls(own, u.head)
        u.strs = {v for p, v in strings if any(a <= p < b for a, b in own)}
    return units


def cs_changed(old, new):
    """Unit keys that differ between two readings (added, removed, or different own text)."""
    return {k for k in set(old) | set(new) if (old.get(k).text if k in old else None) !=
            (new.get(k).text if k in new else None)}


def cs_reach(units, seeds, owned, added=frozenset(), names_only=False):
    """-> (reached keys, anchored): from the seeds (the check's id and entry). A case section is reached by a label
    that is a seed or a string a reached section or method holds (`goto case "x"`), or with its method when no check's
    seed labels it (owned: every check's seeds); a member by its name; a string-list element by its value, or with its
    list when it was there before (added: the elements new at this commit, reached by their value only); a unit's
    parents with it; the code after a method's switch only when the method is called by name (an overload's count of
    arguments decides) or a reached section of the switch can fall out. names_only: the seeds are member names (the words a check reaches in another file), never strings
    or labels: a word like `x` is no `case "x":` and no string a method holds, and a member counts only when its type's
    name is reached too."""
    names, strs = set(seeds), (set() if names_only else set(seeds))
    reached, anchored, grew, direct, called = set(), False, True, set(), {w: {None} for w in seeds}
    sections, overloads = {}, {}
    for u in units.values():
        if u.kind == "case" and u.parent is not None and "after switch" not in u.flags:
            sections.setdefault(u.parent.key, []).append(u)
        if u.kind == "method":
            overloads[u.name] = overloads.get(u.name, 0) + 1

    def is_called(u):
        """A call of method u by name: its name with a fitting count of arguments when an overload shares the name."""
        got = called.get(u.name)
        if not got:
            return False
        lo, hi = u.arity
        return overloads.get(u.name, 0) < 2 or any(n is None or lo <= n <= hi for n in got)
    while grew:
        grew = False
        for k, u in units.items():
            if u.kind == "file" or (k in reached and (u.kind != "method" or k in direct)):
                continue                        # a method reached as a section's parent may yet be called by name
            if "after switch" in u.flags:      # runs when its method is called by name, or a reached section falls out
                anchor = False
                hit = u.parent.key in reached and (u.parent.key in direct or any(
                    c.key in reached and "falls out" in c.flags for c in sections.get(u.parent.key, ())))
            elif u.kind == "case":
                hit = bool(u.labels & strs) or (not (u.labels & owned) and u.parent is not None
                                                and u.parent.key in reached)
                anchor = bool(u.labels & seeds)
            elif u.kind == "elem" and names_only:               # the word `none` is no element "none"
                anchor = False
                hit = u.parent.key in reached and k not in added
            elif u.kind == "elem":
                anchor = u.name in seeds
                hit = anchor or (u.parent.name in names and k not in added)
            else:
                anchor = u.name in seeds or (u.kind == "method" and not names_only and bool(u.strs & seeds))
                hit = anchor or u.name in names
                if names_only and hit and u.kind != "type":     # `live` of RM_FrameProbe is not any `live`: its type too
                    t = u.parent
                    while t is not None and t.kind != "type":
                        t = t.parent
                    hit = anchor = t is None or t.name in names
            if not hit:
                continue
            if u.kind == "method":
                if anchor or is_called(u):                      # called by name, not only its sections' parent
                    direct.add(k)
                if k in reached:
                    grew = grew or k in direct
                    continue
            anchored = anchored or anchor
            p = u
            while p is not None:
                if p.key not in reached:
                    reached.add(p.key)
                    names |= p.refs
                    for w, ns in (p.calls or {}).items():      # a method's name in its own head is no call of it
                        called.setdefault(w, set()).update(ns)
                    if p.kind in ("case", "method"):
                        strs |= p.strs
                p = p.parent
            grew = True
    return reached, anchored


# ---- the relation ---------------------------------------------------------------------------------------------------

def _srchash_hashes(text, mod):
    """{C# file a DLL is compiled from, repo-relative: its hash}, from its .srchash (paths relative to Source/)."""
    out = {}
    base = mod_root(mod) + "/Source"
    for ln in (text or "").splitlines():
        if ln.startswith("#") or " " not in ln:
            continue
        h, rel = ln.split(" ", 1)
        out[os.path.normpath(os.path.join(base, rel.strip())).replace("\\", "/")] = h
    return out


def compiled(git, mod, sha):
    """{repo path: hash}: every C# file the mod's DLLs were compiled from at the commit, by its .srchash files."""
    out = {}
    names = git.show(sha, mod_root(mod) + "/Assemblies")
    for p in names.splitlines() if names else ():       # None: the mod has no Assemblies folder at the commit
        if p.endswith(".srchash"):
            for f, h in _srchash_hashes(git.show(sha, "%s/Assemblies/%s" % (mod_root(mod), p)), mod).items():
                out[f] = "%s %s" % (out[f], h) if f in out else h       # a file two DLLs share
    return out


def scope(git, mod, sha, specs):
    """The paths a change is read under: the mod's source, its design folder, every path a check declares, and every
    C# file the mod's DLLs are compiled from."""
    paths = {mod_root(mod), "design/concepts/%s" % mod}
    for s in specs.values():
        paths.update(declared(s, mod)[0])
    paths.update(compiled(git, mod, sha))
    return sorted(p for p in paths if in_repo(p))


class Relation:
    """The change relation of one mod's test table, read at commit NEW. `touches(id, old)` answers one check."""

    def __init__(self, root, mod, tests, new=None, runner=subprocess.run, old_tests=None, compare_mod_lists=False):
        self.root, self.mod, self.tests = root, mod, dict(tests)
        self.git = Git(root, runner)
        self.new = self.git.rev(new or "HEAD")
        self._scope = {}
        self._py = {}
        self.old_tests = old_tests          # {old sha: {id: spec}} for a test; else read from git
        self.compare_mod_lists = compare_mod_lists
        self._evidence = None
        self.declare(read_declarations(os.path.join(root, DECLARATIONS % mod)))

    def declare(self, d):
        self.extra, self.left_out_why, self.scene_check_off = d

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

    def _cs(self, sha, path):
        """The C# units of a file at a commit, read once per relation; None when absent or unreadable."""
        k = ("cs", sha, path)
        if k not in self._py:
            store, sk = _shared("cs", self.root, self.git.run, sha, path)
            if store is not None and sk in store:
                self._py[k] = store[sk]
                return self._py[k]
            txt = self.git.show(sha, path)
            self._py[k] = cs_units(txt) if txt is not None else None
            if store is not None and txt is not None:
                store[sk] = self._py[k]
        return self._py[k]

    def _owned(self):
        """Every check's seeds (id and entry): a case section no seed labels runs with its method, for every check."""
        if not hasattr(self, "_owned_seeds"):
            self._owned_seeds = {x for t, s in self.tests.items() for x in (t, (s or {}).get("entry")) if x}
        return self._owned_seeds

    def _cs_reach(self, sha, path, seeds, old=None, names_only=False):
        """cs_reach at a commit; old: the commit before, whose absence of a string-list element makes it added."""
        k = ("csreach", sha, path, tuple(sorted(seeds)), old, names_only)
        if k not in self._py:
            u = self._cs(sha, path)
            before = self._cs(old, path) if old else None
            added = {x for x, v in (u or {}).items() if v.kind == "elem" and before is not None and x not in before}
            self._py[k] = cs_reach(u, seeds, self._owned(), added, names_only) if u is not None else (set(), False)
        return self._py[k]

    def _cs_named_elsewhere(self, sha, path, name):
        """True when a word `name` stands in another C# or Python file of the mod at the commit (a caller this read of one
        file cannot see: another class, a scene script, the bridge). A list or a file git cannot show counts as naming it:
        what cannot be read relates whole."""
        k = ("named", sha, path, name)
        if k not in self._py:
            if ("modsrc", sha) not in self._py:
                out = self.git._git("ls-tree", "-r", "--name-only", sha, "--", mod_root(self.mod) + "/")
                self._py[("modsrc", sha)] = None if out is None else [
                    f for f in out.decode().splitlines() if f.endswith((".cs", ".py"))]
            files = self._py[("modsrc", sha)]
            rx = re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name))
            texts = [self.git.show(sha, f) for f in files or () if f != path]
            self._py[k] = files is None or any(t is None or rx.search(t) for t in texts)
        return self._py[k]

    def cs_touches(self, f, o, seeds, named=False):
        """-> (touches, why) for one changed C# file: by member and by switch section (cs_units). named: the file is one
        the check's declared C# files name a type of (cs_named_files), and seeds are the names the check reaches there."""
        a, b = self._cs(o, f), self._cs(self.new, f)
        if a is None or b is None:
            return True, "does not read at one commit (related whole)"
        seeds = {s for s in seeds if s}
        ro, anc_o = self._cs_reach(o, f, seeds, None, named)
        rn, anc_n = self._cs_reach(self.new, f, seeds, o, named)
        if not named and not (anc_o or anc_n):
            return True, "no member or case section of it names %s (related whole)" % " or ".join(sorted(seeds))
        chg = cs_changed(a, b)
        if not chg:
            return False, ""
        for k in list(chg):                                     # an instance field's initializer runs with its type
            for side in (a, b):
                u = side.get(k)
                if u is not None and "instance initializer" in u.flags and u.parent is not None:
                    chg.add(u.parent.key)
        for k in sorted(chg):
            for side, sha in ((a, o), (b, self.new)):
                u = side.get(k)
                if u is None:
                    continue
                if u.kind == "file":
                    return True, "%s changed (related whole)" % ("a using or namespace line" if k == "<file>" else k)
                ext = u.flags & {"attribute", "called by the engine", "unnamed"}
                if ext and named:                       # the engine calls it on its type: a check that names the type
                    t = u
                    while t is not None and t.kind != "type":
                        t = t.parent
                    if t is None or t.name in seeds:
                        return True, "%s is %s, and it reaches %s (related whole)" % (
                            k, sorted(ext)[0], t.name if t is not None else "the file")
                    continue
                if ext:
                    return True, "%s is %s (related whole)" % (k, sorted(ext)[0])
                if not named and u.kind in ("method", "field", "type") and self._cs_named_elsewhere(sha, f, u.name):
                    return True, "%s is named in another file of the mod (related whole)" % k
        unowned = [] if named else [k for k in sorted(chg) if not self._cs_owned(o, f, k)]
        if unowned:
            return True, "%s: reached by no check (related whole)" % ", ".join(unowned[:4])
        got = sorted(k for k in chg if k in rn or k in ro)
        if got:
            return True, ", ".join(got[:6]) + (" ..." if len(got) > 6 else "")
        statics = {side[k].name for side, r in ((a, ro), (b, rn)) for k in r if k in side and side[k].static}
        for k in sorted(chg):
            for side in (a, b):
                u = side.get(k)
                if u is not None and u.refs & statics:
                    return True, "%s uses the shared static %s it reads" % (k, ", ".join(sorted(u.refs & statics)))
        return False, ""

    def _cs_own(self, sha):
        """The mod's own .cs files at the commit, of the C# projects the mod's DLLs are built from: a file whose nearest
        .csproj is one no .srchash names (an offline SelfTest program) never runs in the game. When no .srchash names a
        project, every C# file of the mod counts."""
        k = ("csown", sha)
        if k not in self._py:
            out = self.git._git("ls-tree", "-r", "--name-only", sha, "--", mod_root(self.mod) + "/")
            files = out.decode().splitlines() if out else []
            built = set()
            for p in files:
                if p.startswith(mod_root(self.mod) + "/Assemblies/") and p.endswith(".srchash"):
                    txt = self.git.show(sha, p)
                    if txt is None:                 # a .srchash git cannot show: which project ships is unknown
                        built = set()
                        break
                    for ln in txt.splitlines():
                        if ln.startswith("# project:"):
                            built.add(ln.split(":", 1)[1].strip())
            projs = [p for p in files if p.endswith(".csproj")]

            def project(f):
                d = f.rsplit("/", 1)[0]
                while d.startswith(mod_root(self.mod)):
                    mine = [p for p in projs if p.rsplit("/", 1)[0] == d]
                    if mine:
                        return mine[0]
                    d = d.rsplit("/", 1)[0]
                return None
            own = []
            for f in files:
                pr = project(f) if f.endswith(".cs") else None
                if built and pr is not None and not any(pr.endswith(b) or b.endswith(pr) for b in built):
                    continue
                if f.endswith(".cs") and not derived(f):
                    own.append(f)
            self._py[k] = own
        return self._py[k]

    def _cs_types(self, sha):
        """{path of _cs_own: the type names it defines} at the commit (a file that does not read defines none)."""
        k = ("cstypes", sha)
        if k not in self._py:
            m = {}
            for f in self._cs_own(sha):
                u = self._cs(sha, f)
                m[f] = {x.name for x in (u or {}).values() if x.kind == "type"}
            self._py[k] = m
        return self._py[k]

    def _compiled(self, sha):
        k = ("compiled", sha)
        if k not in self._py:
            self._py[k] = compiled(self.git, self.mod, sha)
        return self._py[k]

    def shipped_cs(self, o):
        """-> (ships, recompiled): every C# file that ships at either commit (a .srchash lists it, or it is the mod's own
        in a project a .srchash names), and those whose .srchash hash differs between the two: they changed in the DLL,
        though their text may have landed before OLD (FlowWorks 4e3323090718)."""
        a, b = self._compiled(o), self._compiled(self.new)
        ships = set(a) | set(b) | set(self._cs_own(o)) | set(self._cs_own(self.new))
        # a commit with no .srchash at all says nothing of what its DLL was compiled from
        return ships, ({f for f in set(a) | set(b) if a.get(f) != b.get(f)} if a and b else set())

    def cs_named_files(self, files, o):
        """The mod's C# files, outside `files`, that define a type a C# file of `files` names (a partial class's other
        parts among them), to a fixed point, at either commit: the helpers a proof file calls (RM_KnockbackVerdicts.cs)."""
        seen, todo = set(), [f for f in files if f.endswith(".cs")]
        while todo:
            f = todo.pop()
            if f in seen:
                continue
            seen.add(f)
            for sha in (self.new, o):
                u = self._cs(sha, f)
                if u is None and self._cs_unreadable(sha, f):  # what it names is unknown: it names every file
                    todo.extend(q for q in self._cs_types(sha) if q not in seen)
                    continue
                words = {w for x in u.values() for w in x.refs} if u is not None else set()
                todo.extend(q for q, names in self._cs_types(sha).items() if q not in seen and names & words)
        return seen - set(files)

    def _cs_names(self, files, named, o, seeds):
        """-> (names the check reaches across its declared C# files and the named ones, anchored in a declared one)."""
        names, anchored = set(), False
        if any(self._cs_unreadable(sha, f) for f in list(files) + list(named) for sha in (o, self.new)):
            return names, False                      # a file that does not read: what the check reaches is unknown
        for f in files:
            for sha, prev in ((o, None), (self.new, o)):
                r, a = self._cs_reach(sha, f, seeds, prev)
                anchored = anchored or a
                u = self._cs(sha, f)
                names |= {w for k in r for w in u[k].refs} if u is not None else set()
        size = -1
        while size != len(names):
            size = len(names)
            for f in named:
                for sha, prev in ((o, None), (self.new, o)):
                    r, _ = self._cs_reach(sha, f, names, prev, True)
                    u = self._cs(sha, f)
                    names = names | ({w for k in r for w in u[k].refs} if u is not None else set())
        return names, anchored

    def part_hits(self, tid, f, o):
        """-> (hit, why, changed, reached) for a changed C# file that check `tid` declares by its parts: the changed units,
        and those of them that the declared parts reach. Not readable, a part the file holds at neither commit, a `~` with
        nothing to follow, or a changed using or namespace line: the whole file (reached is every changed unit)."""
        spec = self.tests.get(tid) or {}
        parts = self._parts(tid, spec)
        a, b = self._cs(o, f), self._cs(self.new, f)
        if a is None or b is None:
            return True, "does not read at one commit (related whole)", {"<file>"}, {"<file>"}
        chg = cs_changed(a, b)
        if not chg:
            return False, "", set(), set()
        for k in list(chg):                                     # an instance field's initializer runs with its type
            for u in (a.get(k), b.get(k)):
                if u is not None and "instance initializer" in u.flags and u.parent is not None:
                    chg.add(u.parent.key)
        lost = sorted(n for n in parts[f] - {REACHED} if not any(u.name == n for x in (a, b) for u in x.values()))
        if lost:
            return True, "it declares %s, which the file does not hold (related whole)" % ", ".join(lost), chg, chg
        for k in sorted(chg):
            if any(x[k].kind == "file" for x in (a, b) if k in x):
                return True, "%s changed (related whole)" % ("a using or namespace line" if k == "<file>" else k), chg, chg
        words = set()
        if REACHED in parts[f]:
            words = self._part_words(tid, o)
            if not words:
                return True, "it declares ~ and no other C# that reads, to follow (related whole)", chg, chg
        got = set()
        for sha, u, prev in ((o, a, None), (self.new, b, o)):
            r = self._part_reach(sha, f, parts[f] - {REACHED}, frozenset(words), prev)
            whole = {k for k, x in u.items() if x.kind == "type" and x.name in (parts[f] | words)}
            for k in chg & set(u):
                x = u[k]
                if k in r:
                    got.add(k)
                elif x.flags & {"attribute", "called by the engine", "unnamed"}:     # no name in the code leads to it
                    t = x.parent
                    while t is not None and t.kind != "type":
                        t = t.parent
                    if t is None or t.key in whole:
                        got.add(k)
        return bool(got), ", ".join(sorted(got)[:6]) + (" ..." if len(got) > 6 else ""), chg, got

    def _part_reach(self, sha, f, names, words, prev=None):
        """The units of `f` at a commit that the declared names (a type: all it holds) and the words of the check's other
        declared C# (`~`) reach inside the file."""
        k = ("partreach", sha, f, tuple(sorted(names)), words, prev)
        if k not in self._py:
            u = self._cs(sha, f)
            got, seeds = set(), set(words)
            if u is None:                                       # absent at this commit; one that does not read never gets here
                self._py[k] = got
                return got
            for key, x in u.items():
                t = x
                while t is not None and t.name not in names:
                    t = t.parent
                if t is not None and x.kind != "file":
                    got.add(key)
            for key in got:
                t = u[key]
                while t is not None:                            # its own type's members by name: Spot() inside Fire
                    seeds |= t.refs | ({t.name} if t.kind == "type" else set())
                    t = t.parent
            before = self._cs(prev, f) if prev else None
            added = {x for x, v in u.items() if v.kind == "elem" and before is not None and x not in before}
            self._py[k] = got | cs_reach(u, seeds, self._owned(), added, True)[0] if seeds else got
        return self._py[k]

    def _part_words(self, tid, o):
        """Every word of the C# that the check declares apart from its `~` files, and then of what they reach in those."""
        k = ("partwords", tid, o)
        if k not in self._py:
            spec = self.tests.get(tid) or {}
            parts = self._parts(tid, spec)
            paths, _ = self._paths(tid, spec)
            words = set()
            for sha in (o, self.new):
                for f in {p for p in paths if p.endswith(".cs")} | {f for f in self._cs_own(sha) if any(
                        covers(p, f) for p in paths)}:
                    if self._cs_unreadable(sha, f):              # what it names is unknown: nothing to follow
                        words = set()
                        self._py[k] = words
                        return words
                    u = self._cs(sha, f)
                    if u is None:                                # absent at this commit
                        continue
                    names = parts.get(f)
                    keys = set(u) if names is None else self._part_reach(sha, f, names - {REACHED}, frozenset())
                    words |= {w for x in keys for w in u[x].refs}
            size = -1 if words else 0
            while size != len(words):
                size = len(words)
                for f in [f for f, n in parts.items() if REACHED in n]:
                    for sha in (o, self.new):
                        u = self._cs(sha, f)
                        words |= {w for x in self._part_reach(sha, f, parts[f] - {REACHED}, frozenset(words))
                                  for w in u[x].refs}            # an absent file reaches nothing
            self._py[k] = words
        return self._py[k]

    def _cs_unreadable(self, sha, path):
        """True when the file is at the commit and does not read as C# (absent is not unreadable)."""
        return self._cs(sha, path) is None and self.git.show(sha, path) is not None

    def _cs_owned(self, o, f, key):
        """True when some check of the table reaches the unit at either commit."""
        k = ("csowned", o, self.new, f)
        if k not in self._py:
            seen = set()
            for t, s in self.tests.items():
                sd = {x for x in (t, (s or {}).get("entry")) if x}
                seen |= self._cs_reach(o, f, sd)[0] | self._cs_reach(self.new, f, sd, o)[0]
            self._py[k] = seen
        return key in self._py[k]

    def touches(self, tid, old):
        """-> (state, why, files): state 'untouched' | 'touched' | 'unreadable'. files: the changed files that touch. A
        check that runs in the game and declares no C# that ships is never untouched by a change of shipped C#: that part
        of its relation cannot be read, so it runs again (Pyrelands a6f05380df: 1 of 40 read as touched)."""
        st, why, files = self._touches(tid, old)
        spec = self.tests.get(tid) or {}
        paths, whole = self._paths(tid, spec)
        o = self.git.rev(old)
        if st != "untouched" or whole or not str(spec.get("kind", "")).startswith("live") or o == self.new:
            return st, why, files
        ships, recompiled = self.shipped_cs(o)
        wrong = self._left_out_touched(tid, spec, o, sorted({f for f in self.change(o) if f in ships} | recompiled), recompiled)
        if wrong:
            return wrong
        if any(covers(p, f) for p in paths for f in ships) or NONE in self._declared_exercises(tid, spec):
            return st, why, files
        cs = sorted({f for f in self.change(o) if f in ships} | recompiled)
        if not cs:
            return st, why, files
        return "unreadable", "it runs in the game and declares no C# file, and C# that ships changed (%s%s)" % (
            ", ".join(cs[:6]), " and %d more" % (len(cs) - 6) if len(cs) > 6 else ""), cs

    def left_out(self, tid, o=None, changed=()):
        """declaration_check's reading of one check: {(file, unit): why} its entry leaves out; None when it could not look."""
        import declaration_check as DC
        if self._evidence is None:
            self._evidence = DC.Evidence(self)
        return self._evidence.left_out(tid, o, changed)

    def _left_out_touched(self, tid, spec, o, cs, recompiled):
        """The answer for a check whose entry leaves out C# that its scene names, when shipped C# changed (`cs`): an entry
        that says `none` is refuted and has no readable relation; else the check is touched by a change in a type that it
        left out. None: the entry holds, or the change is elsewhere."""
        if not cs or self.scene_check_off.startswith("off:"):
            return None
        left = self.left_out(tid, o, cs)
        if not left:
            return None
        import declaration_check as DC
        named = "its entry leaves out C# that its scene names: %s" % "; ".join(DC.lines(left)[:4])
        if NONE in self._declared_exercises(tid, spec) and not declared_cs(self._declared_exercises(tid, spec)):
            return "unreadable", "it says none, and " + named, cs
        hit = []
        for f in cs:
            keys = {k for g, k in left if g == f}
            if not keys:
                continue
            a, b = self._cs(o, f), self._cs(self.new, f)
            if a is None or b is None or f in recompiled:
                hit.append(f)
                continue
            heads = {k.split("/")[0] if "/" in k else k for k in keys}
            if any(k == "<file>" or k.split("/")[0] in heads for k in cs_changed(a, b)):
                hit.append(f)
        return ("touched", "%s changed, and %s" % (", ".join(hit), named), hit) if hit else None

    def _declared_exercises(self, tid, spec):
        return _aslist(spec.get("exercises")) + self.extra.get(tid, [])

    def _paths(self, tid, spec):
        return declared(dict(spec, exercises=self._declared_exercises(tid, spec)), self.mod)

    def _parts(self, tid, spec):
        return declared_parts(dict(spec, exercises=self._declared_exercises(tid, spec)))

    def _touches(self, tid, old):
        spec = self.tests.get(tid) or {}
        paths, whole = self._paths(tid, spec)
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
        if tid in ot:
            keys = [k for k in RUN_KEYS if run_key(ot[tid], k) != run_key(spec, k)]
            if self.compare_mod_lists and "tier" in keys and str(spec.get("kind", "")).startswith("live"):
                keys.remove("tier")         # build_match compares the recorded and current lists
            if keys:
                return "touched", "its test-table entry changed (%s)" % ", ".join(keys), ["test_table.json"]
        if whole:
            under = [f for f in ch if covers(mod_root(self.mod), f)]
            # an ignored file never ships, but a check that declares it reads it (its own script above all)
            hit = [f for f in under if not self.unshipped(f) or any(covers(p, f) for p in paths)]
            if hit:
                return "touched", "a whole-mod check: %d changed file(s) under the mod" % len(hit), hit
            if under:
                return ("untouched", "a whole-mod check, and each of the %d changed file(s) under the mod is one its "
                        ".hashignore lists (never ships; the mod hash does not move)" % len(under), [])
            return "untouched", "a whole-mod check, and nothing under the mod changed", []
        imported = self.py_closure([p for p in paths if p.endswith(".py")], o)
        redone = self.shipped_cs(o)[1] - set(ch)     # changed in the DLL, its text unchanged between the commits
        decl_cs = sorted({f for f in ch if f.endswith(".cs") and any(covers(p, f) for p in paths)} |
                         {p for p in paths if p.endswith(".cs")})
        cs_named = self.cs_named_files(decl_cs, o) if decl_cs else set()
        imported |= cs_named
        mine = [f for f in sorted(set(ch) | redone) if not derived(f) and (any(covers(p, f) for p in paths) or f in imported)]
        if not mine:
            return "untouched", "no changed file is one it declares or its Python imports", []
        seeds = {tid, spec.get("entry")}
        # the C# the check lists as exercised: for a check that anchors in no C#, that list is the relation
        listed = any(_clean(p).endswith(".cs") for p in self._declared_exercises(tid, spec))
        parts = self._parts(tid, spec)
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
            if f in redone:
                if f in cs_named and not any(covers(p, f) for p in paths) and listed and not self._cs_names(
                        decl_cs, sorted(cs_named), o, {s for s in seeds if s})[1]:
                    continue
                hits.append(f)
                why.append("%s: recompiled into the DLL (its .srchash hash differs; related whole)" % f)
                continue
            if f.endswith(".cs"):
                if f in cs_named and not any(covers(p, f) for p in paths):
                    names, anchored = self._cs_names(decl_cs, sorted(cs_named), o, {s for s in seeds if s})
                    if not anchored and listed:
                        continue
                    got, how = ((True, "a C# file it names a type of, and it anchors in none of its own (related "
                                 "whole)") if not anchored else self.cs_touches(f, o, names, named=True))
                elif f in parts:
                    got, how = self.part_hits(tid, f, o)[:2]
                else:
                    got, how = self.cs_touches(f, o, seeds)
                if got:
                    hits.append(f)
                    why.append("%s: %s" % (f, how))
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
        """Changed files under the mod's source that no check declares (derived files left out), for declaring; of a C# file
        that checks declare only by its parts, the changed members that none of them reaches (`F.cs::member`)."""
        ch = self.change(old) or []
        o = self.git.rev(old)
        decl, by_part = set(), {}
        for t, s in self.tests.items():
            parts = self._parts(t, s or {})
            decl.update(p for p in self._paths(t, s or {})[0] if p not in parts)
            for f in parts:
                by_part.setdefault(f, []).append(t)
        out = []
        for f in ch:
            if not covers(mod_root(self.mod), f) or derived(f) or any(covers(p, f) for p in decl):
                continue
            if f not in by_part:
                out.append(f)
                continue
            left = None
            for t in by_part[f]:
                _, _, chg, got = self.part_hits(t, f, o)
                left = (chg if left is None else left) - got
            out.extend("%s%s%s" % (f, PART, k) for k in sorted(left or ()))
        return out


def relate(root, mod, tests, last_rows, new=None, runner=subprocess.run, old_tests=None, compare_mod_lists=False):
    """tests: {id: spec}; last_rows: {id: row or None}. -> {rows: {id: {state, why, files, old}}, touched, unreadable,
    untouched, norow, undeclared, new}. compare_mod_lists means the caller judges live tier changes by list membership."""
    rel = Relation(root, mod, tests, new=new, runner=runner, old_tests=old_tests, compare_mod_lists=compare_mod_lists)
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
