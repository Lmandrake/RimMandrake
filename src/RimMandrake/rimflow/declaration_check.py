#!/usr/bin/env python3
"""The DECLARATION CHECK: does a check's entry (what it exercises) leave out C# that its own scene names? No AI.

Item RIMMANDRAKE_CATCH_WRONG_CHECK_DECLARATION_FOUR_PLANTS_MISSED; page
design/specs/2026-11-24-declaration-check/boundary.md. The change relation (rerun_relation.py) believes an entry of
version/exercises.json. This module reads the entry against the scene: the scene names C#, the entry must hold it.

  python3 src/RimMandrake/rimflow/declaration_check.py --mod M [--new SHA] [--table FILE] [--recall]
      one NAMED line per thing a check's entry leaves out; exit 0 none named, 1 some named, 2 could not look (a check whose
      scene was not found, a table that cannot be read). --recall drops each declared C# path in turn and counts how many
      drops are named: what this check can see.

What a scene names, read from the strings of the Python it reaches (scene_reach):
  type    a C# type of the mod by its full name (jawa/static_call)         -> the type
  method  a C# method that one type of the mod defines (ProbeDome)         -> the method
  def     a def of the mod                                                 -> the types its XML names, and the members that
                                                                              name the def (the job that gives a hediff)
  switch  a static field of a *Settings type                               -> the members that read it
  field   a field it reads of a def ("BiomeDef/X", "baseWeatherCommonalities") -> the members that name the field
A name in more than SHARED(n) checks' scenes is staging and names nothing: a scene places grass, and does not test it.

An entry may leave a thing out on purpose, with its reason, beside `checks`:
  "left_out": {"<check id>": {"<F.cs>::Type,member" or "<F.cs>": "<why>"}}
An entry there with no reason leaves nothing out. "scene_check": "off: <why>" in the same file keeps a left-out name from
rerunning a check (a table whose names nobody has judged yet); this command still prints them.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import rerun_relation as RR     # noqa: E402

KINDS = ("type", "method", "def", "switch", "field")
ROSTER = 3      # a constant or table of this many names is a list that the scene walks: it names nothing of one check
DEF_SPEC = re.compile(r"^[A-Za-z.]*Def/")
FIELD = re.compile(r"^[a-z][a-z0-9]*[A-Z]\w*$")


def shared(n):
    """The most checks a name may stand in and still say something of one check. Staging (grass, firebreak, the settings
    a site turns off) stands in nearly all; Pyrelands 2026-11-24, 40 checks: 3, 4 and 6 gave the same names."""
    return max(4, n // 10)


def live(spec):
    return str((spec or {}).get("kind", "")).startswith("live")


def tokens(s):
    """The names a string holds: a whole identifier, a dotted name, or several of them in a path or list. Prose: none."""
    return [] if not s or re.search(r"\s", s) else [w for w in re.split(r"[^\w.]+", s) if w]


class CouldNotLook(Exception):
    """A scene, a C# file or the mod's defs that cannot be read: nothing is known of what an entry leaves out."""


def scene_reach(tabs, seeds):
    """{(file, symbol)} that a scene reaches, narrower than rerun_relation.py_reach (which errs towards a rerun): from the
    symbols that a seed names, or else that hold one as a string, by the names the code uses. A seed in another scene's
    list (a run order, a message) is not that scene."""
    def key(y):
        m = re.match(r"^(.*)\[(.*)\]$", y)
        return m.groups() if m else (None, None)
    syms = [(p, y, v) for p, t in tabs.items() for y, v in t.items() if y != "<module>" and v[0] != "dict"]
    got = {(p, y): v for p, y, v in syms if y in seeds or key(y)[1] in seeds}
    if not got:
        got = {(p, y): v for p, y, v in syms if v[2] & seeds}
        names = {s for v in got.values() for s in v[2] if RR.IDENT.match(s)}    # what a row names to dispatch to
    else:
        names = {s for (p, y), v in got.items() if key(y)[1] in seeds for s in v[2] if RR.IDENT.match(s)}
    names |= {r for v in got.values() for r in v[1]}
    grew = True
    while grew:
        grew = False
        for p, y, v in syms:
            if (p, y) in got:
                continue
            n, _ = key(y)
            if y in names or (n is not None and (n in names or n + "[?]" in names)):
                got[(p, y)] = v
                names |= v[1]
                grew = True
    return set(got)


class Evidence:
    """What every check's scene names of the mod's C#, read once per relation. `o` is the older commit, or None."""

    def __init__(self, rel, kinds=KINDS):
        self.rel, self.sha, self.kinds = rel, rel.new, kinds
        self.tids = [t for t, s in rel.tests.items() if live(s)]
        self.limit = shared(len(self.tids))
        self.reach, count, self.blind = {}, {}, {}
        for t in self.tids:
            try:
                self.reach[t] = self._scene(t)
            except CouldNotLook as e:
                self.reach[t], self.blind[t] = None, str(e)
            for x in self.reach[t] or ():
                count[x] = count.get(x, 0) + 1
        swept = {}                                  # a table the scene walks whole names nothing by its entries
        self.names, self.fields, stands = {}, {}, {}
        for t in self.tids:
            swept.clear()
            for p, y in self.reach[t] or ():
                if "[" in y:
                    swept[(p, y.split("[")[0])] = swept.get((p, y.split("[")[0]), 0) + 1
            names, fields = {}, {}
            for p, y in sorted(self.reach[t] or ()):
                if count[(p, y)] > self.limit or ("[" in y and swept[(p, y.split("[")[0])] >= ROSTER):
                    continue
                dump, _, strs = rel._syms(self.sha, p)[y]
                if not dump.startswith(("FunctionDef", "AsyncFunctionDef", "ClassDef")) and len(strs) >= ROSTER:
                    continue
                reads_def = any(DEF_SPEC.match(s) for s in strs)
                for s in strs:
                    for w in tokens(s):
                        names.setdefault(w, y)
                        if reads_def and FIELD.match(w) and len(w) >= 8:
                            fields.setdefault(w, y)
            self.names[t], self.fields[t] = names, fields
            for w in names:
                stands[w] = stands.get(w, 0) + 1
        self.staging = {w for w, n in stands.items() if n > self.limit}
        self._idx = {}

    def _scene(self, tid):
        """{(file, symbol)} that the check's id and entry reach; None when no Python of the mod anchors them."""
        rel, sha, spec = self.rel, self.sha, self.rel.tests[tid] or {}
        paths, _ = rel._paths(tid, spec)
        pys = [p for p in paths if p.endswith(".py")]
        files = sorted(set(pys) | rel.py_closure(pys, sha))
        entry = spec.get("entry") if spec.get("entry") != "__main__" else None      # the file run as a program
        seeds = {x for x in (tid, entry) if x}

        def symbols(p):                             # a file the commit lacks holds none; one that does not parse is unknown
            got = rel._syms(sha, p)
            if got is None:
                raise CouldNotLook("%s does not parse" % p)
            return got

        def read(fs):
            return scene_reach({p: symbols(p) for p in fs}, seeds)
        got = read(files)
        if not got and not entry:       # no entry: the file is the scene
            got = {(p, y) for p in pys for y in symbols(p) if y != "<module>"}
        if not got:                                 # a chain in a file loaded by its path (firehawk_rewards_live.py)
            more = [f for fs in rel._mod_py(sha).values() for f in fs if not os.path.basename(f).startswith("selftest_")]
            more = {f for f in more if any(y in seeds or v[2] & seeds for y, v in symbols(f).items())}
            got = read(sorted(more | rel.py_closure(more, sha)))
        return got or None

    def _index(self, sha, files=None):
        """What the mod's C# and XML hold at a commit: {types, methods, uses, switches} and {def: types its XML names}.
        files: the C# files to read at an older commit (the changed ones); its switches and defs are NEW's."""
        key = (sha, files)
        if key in self._idx:
            return self._idx[key]
        rel = self.rel
        ix = {"types": {}, "methods": {}, "uses": {}, "switch": {}, "defs": {}}
        for f in files if files is not None else sorted(set(rel._cs_own(sha)) | set(rel._compiled(sha))):
            units = rel._cs(sha, f)
            if units is None and rel._cs_unreadable(sha, f):
                raise CouldNotLook("%s does not read as C#" % f)
            for k, u in units.items() if units is not None else ():
                if u.kind == "file":
                    continue
                for w in u.refs | {s for s in u.strs if RR.IDENT.match(s)}:
                    ix["uses"].setdefault(w, set()).add((f, k))
                if u.kind == "type":
                    ix["types"].setdefault(u.name, set()).add((f, k))
                elif u.kind == "method" and u.parent is not None:
                    ix["methods"].setdefault(u.name, set()).add((f, k, u.parent.name))
                elif u.kind == "field" and u.parent is not None and u.parent.name.endswith("Settings") and u.static:
                    ix["switch"].setdefault(u.name, set()).add(u.parent.name)
        if files is not None:
            new = self._index(rel.new)
            ix["switch"], ix["defs"] = new["switch"], new["defs"]
            self._idx[key] = ix
            return ix
        out = rel.git._git("ls-tree", "-r", "--name-only", sha, "--", RR.mod_root(rel.mod) + "/")
        if out is None:
            raise CouldNotLook("git cannot list the mod at %s" % sha[:10])
        for p in out.decode().splitlines():
            if not p.endswith(".xml") or "/Defs/" not in p:
                continue
            txt = rel.git.show(sha, p)
            try:
                root = ET.fromstring(txt) if txt is not None else None
            except ET.ParseError:
                root = None
            if root is None:
                raise CouldNotLook("%s does not read as XML" % p)
            for d in root:
                n = d.findtext("defName", "").strip()
                if not n:
                    continue
                for e in d.iter():
                    for v in (e.text if e.text is not None else "", e.get("Class", "")):
                        b = v.strip().rsplit(".", 1)[-1]
                        if "." in v and b in ix["types"]:
                            ix["defs"].setdefault(n, set()).add(b)
                ix["defs"].setdefault(n, set())
        self._idx[key] = ix
        return ix

    def wanted(self, tid, sha, files=None):
        """[(kind, name, symbol, {(file, unit key)})]: what the check's scene names at a commit. One unit of a set held is
        enough (a type is held by any of its members); members that name a def, a switch or a field are a set each."""
        ix, out = self._index(sha, files), []

        def units_of(type_name):
            got = set()
            for f, k in ix["types"].get(type_name, ()):
                got |= {(f, x) for x, u in self.rel._cs(sha, f).items() if x == k or self._inside(u, k)}
            return got
        for w, y in sorted(self.names.get(tid, {}).items()):
            b = w.rsplit(".", 1)[-1]
            if w in self.staging:
                continue
            if "type" in self.kinds and "." in w and b in ix["types"]:
                out.append(("type", b, y, units_of(b)))
            own = ix["methods"].get(w, set())
            if "method" in self.kinds and w[:1].isupper() and len(w) >= 8 and len({t for _, _, t in own}) == 1:
                out.append(("method", w, y, {(f, k) for f, k, _ in own}))
            if w in ix["defs"] and "def" in self.kinds:
                out.extend(("def", w, y, {u}) for u in sorted(ix["uses"].get(w, ())) if self._acts(sha, *u))
                out.extend(("def", w, y, units_of(c)) for c in sorted(ix["defs"][w]))
            if w in ix["switch"] and "switch" in self.kinds:
                for f, k in sorted(ix["uses"].get(w, ())):
                    u = self.rel._cs(sha, f)[k]
                    t = self._type(u)
                    if t is not None and t.name in ix["switch"][w]:
                        continue                                    # the settings type itself
                    if u.refs & ix["switch"][w]:                    # read of the setting, not a parameter of that name
                        out.append(("switch", w, y, {(f, k)}))
        if "field" in self.kinds:
            for w, y in sorted(self.fields.get(tid, {}).items()):
                if w in self.staging or w in ix["methods"] or w in ix["switch"]:
                    continue
                out.extend(("field", w, y, {u}) for u in sorted(ix["uses"].get(w, ())) if self._acts(sha, *u))
        return out

    def _acts(self, sha, f, k):
        """False for a field or a list element: it holds the name (DefOf, a def-name constant), it does nothing with it."""
        return self.rel._cs(sha, f)[k].kind not in ("field", "elem", "type")

    @staticmethod
    def _inside(u, key):
        while u is not None:
            if u.key == key:
                return True
            u = u.parent
        return False

    @staticmethod
    def _type(u):
        while u is not None and u.kind != "type":
            u = u.parent
        return u

    def held(self, tid, sha, o=None):
        """-> f(file, unit key): does the check's entry hold the unit (or leave it out with a reason)?"""
        rel, spec = self.rel, self.rel.tests[tid] or {}
        paths, _ = rel._paths(tid, spec)
        parts = rel._parts(tid, spec)
        words = rel._part_words(tid, o or rel.new)
        out = {}
        for p, why in (rel.left_out_why.get(tid) or {}).items():
            if str(why or "").strip():
                n = RR.part_names(p)
                c = RR._clean(p)
                out[c] = None if n is None or out.get(c, "") is None else (out.get(c) or set()) | n
        memo = {}

        def reach(f, names, ws):
            k = (f, tuple(sorted(names)), bool(ws))
            if k not in memo:
                memo[k] = rel._part_reach(sha, f, names, ws)
            return memo[k]

        def named(f, key, names):
            u = rel._cs(sha, f)[key]
            while u is not None:
                if u.name in names:
                    return True
                u = u.parent
            return False

        def f_held(f, key):
            if f in out and (out[f] is None or named(f, key, out[f])):
                return True
            if not any(RR.covers(p, f) for p in paths):
                return False
            if f not in parts:
                return True
            n = parts[f] - {RR.REACHED}
            return key in reach(f, n, frozenset(words) if RR.REACHED in parts[f] else frozenset())
        return f_held

    def left_out(self, tid, o=None, changed=()):
        """-> {(file, unit key): why} that the check's scene names and its entry leaves out, at NEW and, in the changed
        files, at the older commit o; None when its scene was not found; {} when none. A check with no C# list, or the whole mod, has no entry
        to be wrong."""
        rel, spec = self.rel, self.rel.tests.get(tid) or {}
        if not live(spec) or not entry_of(rel, tid):
            return {}
        if self.reach.get(tid) is None:
            self.blind.setdefault(tid, "no Python of the mod holds its scene (its id or entry)")
            return None
        try:
            return self._left_out(tid, o, changed)
        except CouldNotLook as e:
            self.blind[tid] = str(e)
            return None

    def _left_out(self, tid, o, changed):
        rel = self.rel
        got = {}
        for sha, files in ((rel.new, None),) + (((o, tuple(sorted(changed))),) if o and o != rel.new else ()):
            held = self.held(tid, sha, o)
            for kind, name, sym, units in self.wanted(tid, sha, files):
                if units and not any(held(f, k) for f, k in units):
                    for f, k in units:
                        got.setdefault((f, k), "%s %s, in %s" % (kind, name, sym))
        return got


def entry_of(rel, tid):
    """True when the check has a C# list that can be wrong: `none` or a C# path in its exercises, not the whole mod."""
    spec = rel.tests.get(tid) or {}
    if rel._paths(tid, spec)[1]:
        return False
    ex = rel._declared_exercises(tid, spec)
    return RR.NONE in ex or any(RR._clean(p).endswith(".cs") for p in ex)


def lines(left):
    """One line per (file, why) of a left_out reading."""
    by = {}
    for (f, k), why in left.items():
        by.setdefault((f, why), []).append(k)
    out = []
    for (f, why), ks in sorted(by.items()):
        top = sorted(ks, key=lambda k: (k.count("/"), k))
        out.append("%s::%s%s (%s)" % (f, top[0], " and %d more" % (len(ks) - 1) if len(ks) > 1 else "", why))
    return out


def read(rel):
    """-> (named {tid: [lines]}, unseen {tid: why}) over every check of the table."""
    ev = Evidence(rel)
    named, unseen = {}, {}
    for t in ev.tids:
        left = ev.left_out(t)
        if left is None:
            unseen[t] = ev.blind[t]
        elif left:
            named[t] = lines(left)
    return named, unseen


def recall(rel):
    """-> (drops, caught, {tid: [dropped path not named]}): each declared C# path dropped from its check alone."""
    ev = Evidence(rel)
    n = got = 0
    missed = {}
    for t in ev.tids:
        if not entry_of(rel, t):
            continue
        real = rel.extra.get(t, [])
        before = ev.left_out(t)
        if before is None:
            raise CouldNotLook("%s: %s" % (t, ev.blind[t]))
        for p in real:
            if not RR._clean(p).endswith(".cs") or RR.part_names(p) == {RR.REACHED}:
                continue
            rel.extra[t] = [x for x in real if x != p] or [RR.NONE]
            rel._py = {k: v for k, v in rel._py.items() if k[0] not in ("partwords",)}
            n += 1
            if set(ev.left_out(t)) - set(before):
                got += 1
            else:
                missed.setdefault(t, []).append(p)
        rel.extra[t] = real
        rel._py = {k: v for k, v in rel._py.items() if k[0] not in ("partwords",)}
    return n, got, missed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod", required=True)
    ap.add_argument("--new", default="HEAD")
    ap.add_argument("--table", help="an exercises.json to read instead of the mod's own")
    ap.add_argument("--recall", action="store_true")
    ap.add_argument("--root", default=RR.REPO)
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.root, "design/concepts/%s/version/test_table.json" % a.mod), encoding="utf-8") as f:
            t = json.load(f).get("tests")
        tests = t if isinstance(t, dict) else {x.get("id"): x for x in t}
        rel = RR.Relation(a.root, a.mod, tests, new=a.new)
        if a.table:
            rel.declare(RR.read_declarations(a.table))
    except (OSError, ValueError, AttributeError, TypeError) as e:
        print("COULD NOT LOOK: %s: %s" % (type(e).__name__, e))
        return 2
    if not rel.new:
        print("COULD NOT LOOK: git cannot resolve %s" % a.new)
        return 2
    if a.recall:
        try:
            n, got, missed = recall(rel)
        except CouldNotLook as e:
            print("COULD NOT LOOK: %s" % e)
            return 2
        for t in sorted(missed):
            print("not named  %s: %s" % (t, ", ".join(x.rsplit("/", 1)[-1] for x in missed[t])))
        print("recall: %d of %d dropped C# paths are named" % (got, n))
        return 0
    named, unseen = read(rel)
    for t in sorted(named):
        for ln in named[t]:
            print("NAMED  %s leaves out %s" % (t, ln))
    for t in unseen:
        print("COULD NOT LOOK  %s: %s" % (t, unseen[t]))
    entries = sum(1 for t, s in tests.items() if live(s) and entry_of(rel, t))
    if rel.scene_check_off.startswith("off:"):
        print("SCENE CHECK OFF for the rerun decision (%s)" % rel.scene_check_off)
    print("declarations: %d check(s) with a C# list, %d named, %d could not be read" % (entries, len(named), len(unseen)))
    return 2 if unseen or not entries else (1 if named else 0)


if __name__ == "__main__":
    sys.exit(main())
