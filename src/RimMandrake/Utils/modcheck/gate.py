"""modcheck.gate -- the known-good gate: do not re-run a chain whose recorded result still holds because none of its
INPUTS changed (test_orchestration_two_machines_2026-10-25 §4 #2, KNOWN_GOOD_BUILD_SKIP_UNCHANGED_PASS).

    python3 src/RimMandrake/Utils/modcheck/gate.py preview --mod FlowWorks     what a run now would skip, and why not
    python3 src/RimMandrake/Utils/modcheck/gate.py audit <run.json> [...]      skip rate and MISSES of shadow runs

Every chain a run executes gets a CHAIN MANIFEST, written into its chain dict (`gate`) and appended to
Transient/modcheck/gate_index.jsonl when the sheet is written. Its key is a sha over:
  runtime  status.runtime_hash(mod dir): Defs, Patches, C# Source and the rest the game loads (the built DLL is not
           hashed -- builds are not byte-stable -- but a deployed DLL differing from the repo's makes the key unresolved);
  profile  the composed test list (MINIMAL file + the package ids composed onto it), the runtime hash of every REPO mod
           in it (src/**/About/About.xml), and the run flags that change what a chain sees (situational, policy, hold);
  harness  status.test_closure of runner.py and suite.py (the whole modcheck harness those import);
  code     the chain's slice: its own top-level statement, every same-file top-level def/assignment it reaches by name
           (transitively), the module preamble (imports, sys.path, any statement that is not a plain def/assign), the
           suite module's preamble, and the full test_closure of every local module the slice imports or names;
  inputs   the files matching the chain's declared `inputs=` globs (Suite.chain). A glob matching nothing is unresolved.
A chain that declares no inputs is SCANNED: a slice that opens, lists, globs, parses or shells out (open, os.walk,
json.load, subprocess...) reads something the key cannot see -> `inputs_known` false -> never skipped. A declaration
(even `inputs=[]`, "reads nothing beyond its code") overrides the scan.

decide(): a chain is SKIPPED when the newest record at its current key is a settled run (below), not partial (or a
partial one covering a prefix request), and no valid FAIL was ever recorded at that key (the flake guard). A record is
SETTLED when it has no FAIL and no invalid row, at least one PASS, and every non-PASS row is an UNMEASURED the code
itself declares (`live check owed`, `no ... result at the current mod hash`): with the key unchanged those repeat.
A skipped chain is filled from the record: its components keep their verdicts with freshness "reused@<file>", phase_s
0, and `gate` names the record -- so the run is never `fresh_green` (runner summary.reuse) and run() never writes a
GREEN status entry from it.

MODE (env MODCHECK_GATE / `run --gate`): on (default) | shadow (decide, never skip: `would_skip`) | off (no manifest).
PURPOSE (env MODCHECK_PURPOSE / `run --purpose`): fix | guard (the gate applies) | sweep | sensitivity | flake |
commission (the gate is advisory: `would_skip`, the chain runs -- a deliberate full sweep measures the gate).
A MISS is a would_skip chain whose fresh run recorded a valid FAIL, or lost a PASS the record had (`audit`).

LIMITS: third-party mods and the game build are not in the key (the profile hashes repo mods only); a local module's
import side effects count only when the slice names or imports it; a helper module's own file reads are covered only
through the data literals test_closure sees. Offline and pure but for reads, except index_run's one append.
"""
import argparse
import ast
import glob
import hashlib
import json
import os
import re
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.dirname(HERE)
SRC = os.path.dirname(UTILS)                       # src/RimMandrake
ROOT = os.path.dirname(os.path.dirname(SRC))
SHEET_DIR = os.path.join(ROOT, "Transient", "modcheck")
INDEX = "gate_index.jsonl"
MINIMAL = os.path.join(ROOT, "infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml")
SCHEMA = 1

ENV_MODE, ENV_PURPOSE, ENV_HISTORY = "MODCHECK_GATE", "MODCHECK_PURPOSE", "MODCHECK_GATE_HISTORY"
ON, SHADOW, OFF = "on", "shadow", "off"
RUN, SKIP, WOULD = "run", "skip", "would_skip"
GATED_PURPOSES = ("fix", "guard")
ADVISORY_PURPOSES = ("sweep", "sensitivity", "flake", "commission")
PURPOSES = GATED_PURPOSES + ADVISORY_PURPOSES

# a non-PASS row the chain code itself declares: with code and inputs unchanged it comes back the same
OWED = re.compile(r"UNMEASURED: (live check owed|no [\w .-]+ result at the current mod hash)")
# calls that read the filesystem or the world outside the key: (attribute or function name, required base or None)
_READS = {"open": None, "listdir": None, "scandir": None, "walk": None, "exists": None, "isfile": None,
          "isdir": None, "getmtime": None, "getsize": None, "glob": None, "iglob": None, "read_text": None,
          "read_bytes": None, "Popen": None, "check_output": None, "check_call": None,
          "load": ("json", "pickle", "yaml"), "parse": ("ET", "ElementTree", "etree", "minidom"),
          "run": ("subprocess",), "call": ("subprocess",), "system": ("os",), "popen": ("os",)}


def mode(environ=None):
    v = str((environ if environ is not None else os.environ).get(ENV_MODE, "")).strip().lower()
    return OFF if v in ("0", "off", "no", "false") else SHADOW if v in ("shadow", "report") else ON


def purpose(environ=None):
    v = str((environ if environ is not None else os.environ).get(ENV_PURPOSE, "")).strip().lower()
    return v if v in PURPOSES else "guard"


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def _hash_files(paths, base):
    h = hashlib.sha256()
    for p in sorted(set(paths)):
        with open(p, "rb") as f:
            h.update(os.path.relpath(p, base).replace(os.sep, "/").encode("utf-8") + b"\0" + f.read() + b"\0")
    return h.hexdigest()


def _status():
    import status as st  # noqa: E402 - modcheck dir on sys.path
    return st


# ------------------------------------------------------------------------------------------------ code slice
def _top_index(tree):
    """{name: [top-level stmt]} for plain defs, classes and Name-target assignments; and the preamble statements."""
    names, pre = {}, []
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.setdefault(st.name, []).append(st)
        elif isinstance(st, (ast.Assign, ast.AnnAssign)) and all(
                isinstance(t, ast.Name) for t in (st.targets if isinstance(st, ast.Assign) else [st.target])):
            for t in (st.targets if isinstance(st, ast.Assign) else [st.target]):
                names.setdefault(t.id, []).append(st)
        elif not (isinstance(st, ast.Expr) and isinstance(getattr(st, "value", None), ast.Constant)):
            pre.append(st)      # imports, sys.path edits, augmented/attribute assigns, ifs, loops (not the docstring)
    return names, pre


def _start(st):
    return min([st.lineno] + [d.lineno for d in getattr(st, "decorator_list", [])])


def _referenced(nodes):
    out = set()
    for n in nodes:
        for x in ast.walk(n):
            if isinstance(x, ast.Name):
                out.add(x.id)
    return out


def _imports(nodes):
    """[(module, level, bound name or None)] for every import inside `nodes` (function bodies included)."""
    out = []
    for n in nodes:
        for x in ast.walk(n):
            if isinstance(x, ast.Import):
                out += [(a.name, 0, (a.asname or a.name).split(".")[0]) for a in x.names]
            elif isinstance(x, ast.ImportFrom):
                for a in x.names:
                    out.append(((x.module or ""), x.level, a.asname or a.name))
                    out.append((("%s.%s" % (x.module, a.name)) if x.module else a.name, x.level, a.asname or a.name))
    return out


def _resolve(mod, level, here, dirs):
    if not mod:
        return None
    rel = mod.replace(".", os.sep)
    among = dirs
    if level:
        base = here
        for _ in range(level - 1):
            base = os.path.dirname(base)
        among = [base]
    for d in among:
        for cand in (os.path.join(d, rel + ".py"), os.path.join(d, rel, "__init__.py")):
            if os.path.isfile(cand):
                return os.path.abspath(cand)
    return None


def _scan_reads(nodes, fname):
    hits = []
    for n in nodes:
        for x in ast.walk(n):
            if not isinstance(x, ast.Call):
                continue
            f = x.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name not in _READS:
                continue
            need = _READS[name]
            base = f.value if isinstance(f, ast.Attribute) else None
            bname = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", None)
            if need is not None and bname not in need:
                continue
            if bname == "Image":      # PIL opening a screenshot this run took: an output, not an input
                continue
            hits.append("%s@%s:%d" % (name, fname, x.lineno))
    return hits


class _Module(object):
    def __init__(self, path):
        self.path = path
        with open(path, encoding="utf-8") as f:
            self.src = f.read()
        self.tree = ast.parse(self.src, filename=path)
        self.names, self.pre = _top_index(self.tree)

    def text(self, st):
        return ast.get_source_segment(self.src, st) or ast.dump(st)

    def containing(self, line):
        for st in self.tree.body:
            if _start(st) <= line <= getattr(st, "end_lineno", st.lineno):
                return st
        return None


def code_slice(fn, suite_file, mod_dir, _cache=None):
    """{"code": sha, "files": [...], "reads": [...], "unresolved": [...]} for chain function `fn` (the registered
    wrapper or the raw function). Pure but for reads; `_cache` {path: _Module} shares parses across chains."""
    st_mod = _status()
    cache = _cache if _cache is not None else {}
    raw = fn
    while getattr(raw, "__wrapped__", None) is not None:
        raw = raw.__wrapped__
    out = {"code": None, "files": [], "reads": [], "unresolved": []}
    try:
        path = os.path.abspath(raw.__code__.co_filename)
        line = raw.__code__.co_firstlineno
    except AttributeError:
        out["unresolved"].append("chain %r has no code object" % (fn,))
        return out

    def mod_of(p):
        if p not in cache:
            cache[p] = _Module(p)
        return cache[p]

    try:
        m = mod_of(path)
        sm = mod_of(os.path.abspath(suite_file)) if suite_file else None
    except (OSError, SyntaxError, ValueError) as ex:
        out["unresolved"].append("parse %s: %s" % (os.path.basename(path), type(ex).__name__))
        return out
    first = m.containing(line)
    if first is None:
        out["unresolved"].append("%s:%d not inside a top-level statement" % (os.path.basename(path), line))
        return out
    picked, todo = [], [first]
    seen = set()
    while todo:
        st = todo.pop()
        if id(st) in seen:
            continue
        seen.add(id(st))
        picked.append(st)
        for name in _referenced([st]):
            todo.extend(m.names.get(name, ()))
    picked.sort(key=_start)
    texts = ["slice:" + m.text(st) for st in picked] + ["pre:" + m.text(st) for st in m.pre]
    if sm is not None and sm is not m:
        texts += ["suitepre:" + sm.text(st) for st in sm.pre]
    # local modules: imported inside the slice, or bound by a preamble import whose name the slice uses
    used = _referenced(picked)
    here = os.path.dirname(path)
    dirs = st_mod._import_dirs(mod_dir, here)
    mods = set()
    for mod, level, bound in _imports(picked):
        p = _resolve(mod, level, here, dirs)
        if p:
            mods.add(p)
    for mod, level, bound in _imports(m.pre):
        if bound in used:
            p = _resolve(mod, level, here, dirs)
            if p:
                mods.add(p)
    files = set()
    for p in sorted(mods):
        if p == path:
            continue
        got, unres = st_mod.test_closure(p, mod_dir)
        files.update(got)
        out["unresolved"] += unres
    files.discard(path)
    base = os.path.dirname(os.path.abspath(mod_dir))
    out["files"] = sorted(os.path.relpath(p, base).replace(os.sep, "/") for p in files)
    out["reads"] = _scan_reads(picked, os.path.basename(path))
    try:
        out["code"] = _sha({"texts": texts, "modules": _hash_files(files, base) if files else None,
                            "file": os.path.relpath(path, base).replace(os.sep, "/")})
    except OSError as ex:
        out["unresolved"].append("hash: %s" % ex)
    return out


# ------------------------------------------------------------------------------------------------ inputs, profile
def inputs_hash(globs, mod_dir):
    """(sha or None, file count, unresolved) over a chain's declared inputs, each relative to `mod_dir`:
      "<glob>"             every matching file (`**` recursive); matching nothing is unresolved (a typo never skips);
      "?<glob>"            the same, but may match nothing (a driver result not yet written);
      "@mod_hash"          status.mod_hash(mod_dir) -- what a reader of "a result at the current mod hash" keys on;
      "@closure:<script>"  status.test_closure of a helper script the chain shells out to (its imports and data)."""
    st = _status()
    files, unresolved, extra = set(), [], []
    for g in globs:
        if g == "@mod_hash":
            extra.append(("mod_hash", st.mod_hash(mod_dir)))
            continue
        if g.startswith("@closure:"):
            script = os.path.normpath(os.path.join(mod_dir, g[len("@closure:"):]))
            if not os.path.isfile(script):
                unresolved.append("input %s: no such script" % g)
                continue
            got, unres = st.test_closure(script, mod_dir)
            files.update(got)
            unresolved += unres
            continue
        optional = g.startswith("?")
        pat = g[1:] if optional else g
        got = [p for p in glob.glob(os.path.join(mod_dir, pat), recursive=True) if os.path.isfile(p)
               and "__pycache__" not in p and not p.endswith(".pyc")]
        if not got and not optional:
            unresolved.append("input %s matches nothing" % g)
        files.update(os.path.abspath(p) for p in got)
    base = os.path.dirname(os.path.abspath(mod_dir))
    try:
        return _sha({"files": _hash_files(files, base) if files else None, "extra": extra}), len(files), unresolved
    except OSError as ex:
        return None, len(files), unresolved + ["input read: %s" % ex]


_REPO_IDS = {}


def repo_mods():
    """{packageId (lower): mod dir} for every repo mod with an About/About.xml under src/ (cached per process)."""
    if _REPO_IDS:
        return _REPO_IDS
    import xml.etree.ElementTree as ET
    for root, dirs, files in os.walk(os.path.join(ROOT, "src")):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "Source", "art_source", "Textures", "Defs",
                                                "Patches", "node_modules", "obj", "bin")]
        if os.path.basename(root) == "About" and "About.xml" in files:
            try:
                pid = ET.parse(os.path.join(root, "About.xml")).getroot().findtext("packageId")
            except (ET.ParseError, OSError):
                continue
            if pid:
                _REPO_IDS.setdefault(pid.strip().lower(), os.path.dirname(root))
    return _REPO_IDS


def minimal_ids(path=MINIMAL):
    import xml.etree.ElementTree as ET
    try:
        return [li.text.strip().lower() for li in ET.parse(path).getroot().iter("li") if li.text]
    except (ET.ParseError, OSError):
        return None


def profile(package_ids, flags=None):
    """The profile part of a manifest: the composed list, the runtime hash of each repo mod in it, the run flags."""
    st = _status()
    ids = minimal_ids()
    unresolved = [] if ids is not None else ["MINIMAL list unreadable"]
    composed = [str(p).lower() for p in package_ids or ()]
    allids = list(ids or []) + [p for p in composed if p not in (ids or [])]
    repo = repo_mods()
    hashes = {}
    for pid in allids:
        d = repo.get(pid)
        if d:
            try:
                hashes[pid] = st.runtime_hash(d)
            except OSError as ex:
                unresolved.append("runtime %s: %s" % (pid, ex))
    return {"minimal": ids, "composed": composed, "repo_runtime": hashes, "flags": dict(flags or {})}, unresolved


def package_ids_for(mod_folder):
    """The ids runner.run() composes onto MINIMAL for `mod_folder` (deps, own id, composed tier) -- for `preview`."""
    import runner as R  # noqa: E402
    mod_dir = R.find_mod_dir(mod_folder)
    folded = R.composed_into(mod_folder)
    out = [d for d in R.mod_dependency_ids(mod_dir)]
    own = folded[1] if folded else R.mod_package_id(mod_dir)
    if own not in out:
        out.append(own)
    if folded:
        out.extend(t for t in R.tier_package_ids(mod_folder) if t not in out)
    return out


def deployed_dll_check(mod_dir, mod_folder):
    """None when the game's copy of the mod carries the repo's DLLs (or there is no game copy to compare: 'unseen'
    is returned as a note, not a refusal); else the mismatch."""
    try:
        if UTILS not in sys.path:
            sys.path.insert(0, UTILS)
        from game_paths import LOCAL_MODS  # noqa: E402
    except Exception:  # noqa: BLE001 - no game here (CI, a reader host)
        return None
    game = os.path.join(LOCAL_MODS, mod_folder, "Assemblies")
    if not os.path.isdir(game):
        return None
    for p in glob.glob(os.path.join(mod_dir, "Assemblies", "*.dll")):
        g = os.path.join(game, os.path.basename(p))
        try:
            with open(p, "rb") as a, open(g, "rb") as b:
                if hashlib.sha256(a.read()).digest() != hashlib.sha256(b.read()).digest():
                    return "deployed %s differs from the repo's" % os.path.basename(p)
        except OSError:
            return "deployed %s missing" % os.path.basename(p)
    return None


# ------------------------------------------------------------------------------------------------ records
def row_settled(c):
    v = str(c.get("verdict") or "")
    if c.get("validity") == "invalid" or v.startswith("FAIL"):
        return False
    return v.startswith("PASS") or bool(OWED.search(str(c.get("detail") or "")))


def classify(chain):
    """'pass' (settled), 'fail' (a valid FAIL), 'invalid' or 'other' for a runner chain dict."""
    comps = [c for c in chain.get("components") or [] if c.get("execution") != "not_run"]
    if any(str(c.get("verdict") or "").startswith("FAIL") and c.get("validity") != "invalid" for c in comps):
        return "fail"
    if any(c.get("validity") == "invalid" for c in comps):
        return "invalid"
    rv = (((chain.get("situational") or {}).get("runValidity") or {}).get("verdict"))
    if rv in ("DISRUPTED", "INDETERMINATE"):
        return "other"
    if comps and all(row_settled(c) for c in comps) and any(str(c.get("verdict") or "").startswith("PASS")
                                                            for c in comps):
        return "pass"
    return "other"


def history_dirs(environ=None):
    env = (environ if environ is not None else os.environ).get(ENV_HISTORY, "")
    return [SHEET_DIR] + [d for d in env.split(os.pathsep) if d.strip()]


def load_index(dirs=None):
    """[(dir, record)] from every gate_index.jsonl in `dirs` (default: history_dirs()); torn lines skipped."""
    out = []
    for d in dirs or history_dirs():
        p = os.path.join(d, INDEX)
        try:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(r, dict) and r.get("key"):
                        out.append((d, r))
        except OSError:
            continue
    return out


def index_run(mod, summary, json_path, environ=None):
    """Append one line per FRESHLY RUN chain with a manifest key (skipped chains are not new evidence)."""
    lines = []
    stamp = os.path.basename(json_path).rsplit("_", 1)[-1].split(".")[0]
    for ch in summary.get("chains") or []:
        g = ch.get("gate") or {}
        if not g.get("key") or g.get("action") == SKIP:
            continue
        comps = ch.get("components") or []
        lines.append({"schema": SCHEMA, "mod": mod, "chain": ch.get("name"), "key": g["key"],
                      "file": os.path.basename(json_path), "stamp": stamp, "class": classify(ch),
                      "rows": [c.get("name") for c in comps if c.get("execution") != "not_run"],
                      "partial": any(c.get("execution") == "not_run" for c in comps),
                      "host": socket.gethostname(), "purpose": g.get("purpose"),
                      "body_s": (ch.get("phase_s") or {}).get("body")})
    if not lines:
        return 0
    with open(os.path.join(os.path.dirname(os.path.abspath(json_path)), INDEX), "a", encoding="utf-8") as f:
        for r in lines:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return len(lines)


# ------------------------------------------------------------------------------------------------ the gate
class Gate(object):
    """One per suite run. `suite` the (possibly filtered) suite; `full_suite` the module's suite (for the inputs and
    offline declarations); `package_ids` what run() composed; `flags` run flags in the profile."""

    def __init__(self, suite, mod, mod_dir, package_ids, flags=None, environ=None, index=None, full_suite=None):
        env = environ if environ is not None else os.environ
        self.mode, self.purpose = mode(env), purpose(env)
        self.suite, self.full = suite, full_suite or suite
        self.mod, self.mod_dir = mod, mod_dir
        self.suite_file = os.path.join(mod_dir, "validation.py")
        self.environ = env
        self._cache, self._man = {}, {}
        self._index = index
        self.common_unresolved = []
        st = _status()
        try:
            self.runtime = st.runtime_hash(mod_dir)
        except OSError as ex:
            self.runtime = None
            self.common_unresolved.append("runtime: %s" % ex)
        self.profile, unres = profile(package_ids, flags)
        self.common_unresolved += unres
        files = set()
        for s in ("runner.py", "suite.py"):
            got, unres = st.test_closure(os.path.join(HERE, s), mod_dir)
            files.update(got)
            self.common_unresolved += unres
        self.harness = _hash_files(files, os.path.dirname(os.path.abspath(mod_dir)))
        dll = deployed_dll_check(mod_dir, mod)
        if dll:
            self.common_unresolved.append(dll)

    def index(self):
        if self._index is None:
            self._index = [r for _, r in load_index(history_dirs(self.environ)) if r.get("mod") == self.mod]
        return self._index

    def manifest(self, name, fn):
        if name in self._man:
            return self._man[name]
        declared = (getattr(self.full, "chain_inputs", {}) or {}).get(name)
        if declared is None:
            declared = (getattr(self.suite, "chain_inputs", {}) or {}).get(name)
        sl = code_slice(fn, self.suite_file, self.mod_dir, self._cache)
        unresolved = list(self.common_unresolved) + sl["unresolved"]
        ih, nfiles = None, 0
        if declared is not None:
            ih, nfiles, unres = inputs_hash(declared, self.mod_dir)
            unresolved += unres
        known = declared is not None or not sl["reads"]
        parts = {"schema": SCHEMA, "chain": name, "runtime": self.runtime, "profile": _sha(self.profile),
                 "harness": self.harness, "code": sl["code"], "inputs": ih, "declared": declared}
        m = {"key": _sha(parts), "parts": parts, "unresolved": unresolved, "inputs_known": known,
             "reads": sl["reads"][:12], "input_files": nfiles, "code_files": len(sl["files"])}
        self._man[name] = m
        return m

    def decide(self, name, fn, scope=None):
        """{"action", "key", "why", "record"}; never raises (a gate that breaks runs the chain)."""
        if self.mode == OFF:
            return {"action": RUN, "key": None, "why": "gate off", "record": None}
        try:
            m = self.manifest(name, fn)
        except Exception as ex:  # noqa: BLE001
            return {"action": RUN, "key": None, "why": "manifest error %s: %s" % (type(ex).__name__, ex),
                    "record": None}
        d = {"action": RUN, "key": m["key"], "record": None, "purpose": self.purpose,
             "unresolved": m["unresolved"][:6], "inputs_known": m["inputs_known"], "reads": m["reads"]}
        if m["unresolved"]:
            d["why"] = "manifest unresolved: %s" % "; ".join(m["unresolved"])[:200]
            return d
        if not m["inputs_known"]:
            d["why"] = "inputs unknown (reads %s; declare inputs=)" % ", ".join(m["reads"][:3])
            return d
        same = [r for r in self.index() if r.get("key") == m["key"] and r.get("chain") == name]
        if not same:
            d["why"] = "no record at this key"
            return d
        if any(r.get("class") == "fail" for r in same):
            d["why"] = "a valid FAIL was recorded at this key (flake guard)"
            return d
        want = set((scope or {}).get("requested_rows") or ()) if (scope or {}).get("mode") == "prefix" else None
        usable = [r for r in same if r.get("class") == "pass"
                  and (not r.get("partial") or (want is not None and want <= set(r.get("rows") or ())))]
        newest = max(same, key=lambda r: (str(r.get("stamp")), str(r.get("file"))))
        if not usable or newest not in usable:
            d["why"] = "newest record at this key is %s%s" % (newest.get("class"),
                                                              " (partial)" if newest.get("partial") else "")
            return d
        d["record"] = {k: newest.get(k) for k in ("file", "stamp", "host", "class", "purpose", "body_s")}
        if self.mode == SHADOW or self.purpose in ADVISORY_PURPOSES:
            d["action"], d["why"] = WOULD, "known good at %s (%s)" % (
                newest.get("file"), "gate shadow" if self.mode == SHADOW else "purpose %s" % self.purpose)
        else:
            d["action"], d["why"] = SKIP, "known good at %s" % newest.get("file")
        return d

    def reused_chain(self, name, d, dirs=None):
        """The chain dict for a SKIPPED chain, filled from its record, or None when the record cannot be read."""
        rec = d.get("record") or {}
        for base in dirs or history_dirs(self.environ):
            p = os.path.join(base, rec.get("file") or "")
            if not os.path.isfile(p):
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    run = json.load(f)
            except (OSError, ValueError):
                return None
            for ch in (run.get("summary") or {}).get("chains") or []:
                if ch.get("name") == name:
                    comps = []
                    for c in ch.get("components") or []:
                        c = dict(c)
                        c["freshness"] = "reused@%s" % rec["file"]
                        comps.append(c)
                    return {"name": name, "components": comps, "situational": None, "modal_check": None,
                            "site_hold": None, "env_reset": None,
                            "phase_s": {"hold": 0.0, "body": 0.0, "teardown": 0.0}, "gate": stamp(d)}
        return None


def stamp(d):
    """The `gate` field a chain dict carries."""
    return {k: d.get(k) for k in ("action", "key", "why", "record", "purpose", "inputs_known") if k in d}


def summarize(chains):
    by = {RUN: [], SKIP: [], WOULD: []}
    saved = 0.0
    for ch in chains:
        g = ch.get("gate") or {}
        a = g.get("action")
        if a in by:
            by[a].append(ch.get("name"))
            if a in (SKIP, WOULD):
                saved += float(((g.get("record") or {}).get("body_s")) or 0.0)
    return {"run": by[RUN], "skipped": by[SKIP], "would_skip": by[WOULD], "record_body_s": round(saved, 1)}


# ------------------------------------------------------------------------------------------------ audit / preview
def audit_run(run, dirs=None):
    """{chains, would_skip, misses: [...], drift: [...]} for one run JSON: each would_skip chain's fresh rows against
    its record's. A miss: a valid FAIL now, or a row PASS in the record that is not PASS now. Drift: other changes."""
    chains = (run.get("summary") or run).get("chains") or []
    out = {"chains": len(chains), "would_skip": 0, "skipped": 0, "misses": [], "drift": [], "unreadable": []}
    for ch in chains:
        g = ch.get("gate") or {}
        if g.get("action") == SKIP:
            out["skipped"] += 1
        if g.get("action") != WOULD:
            continue
        out["would_skip"] += 1
        rec = None
        for base in dirs or history_dirs():
            p = os.path.join(base, (g.get("record") or {}).get("file") or "")
            if os.path.isfile(p):
                try:
                    with open(p, encoding="utf-8") as f:
                        rr = json.load(f)
                except (OSError, ValueError):
                    break
                rec = next((c for c in (rr.get("summary") or {}).get("chains") or [] if c.get("name") == ch["name"]),
                           None)
                break
        if rec is None:
            out["unreadable"].append(ch["name"])
            continue
        old = {c.get("name"): c for c in rec.get("components") or []}
        for c in ch.get("components") or []:
            v = str(c.get("verdict") or "")
            o = str((old.get(c.get("name")) or {}).get("verdict") or "")
            if v.startswith("FAIL") and c.get("validity") != "invalid":
                out["misses"].append("%s/%s: FAIL now (record %s)" % (ch["name"], c.get("name"), o or "absent"))
            elif o.startswith("PASS") and not v.startswith("PASS"):
                out["misses"].append("%s/%s: %s now, PASS in record" % (ch["name"], c.get("name"), v))
            elif v != o:
                out["drift"].append("%s/%s: %s -> %s" % (ch["name"], c.get("name"), o or "absent", v))
    return out


def preview(mod_folder, environ=None):
    import runner as R  # noqa: E402
    mod_dir = R.find_mod_dir(mod_folder)
    suite = R.load_validation(mod_dir)
    flags = {"situational": False, "policy": "abort", "hold": True}
    g = Gate(suite, mod_folder, mod_dir, package_ids_for(mod_folder), flags, environ=environ)
    rows = []
    for name, fn in suite.chains:
        d = g.decide(name, fn)
        rows.append((name, d["action"], d.get("why", ""), d.get("key")))
    return g, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preview", help="what a run now would skip, per chain")
    p.add_argument("--mod", required=True)
    p.add_argument("--json", action="store_true")
    a2 = sub.add_parser("audit", help="skip rate and misses of runs (would_skip chains vs their records)")
    a2.add_argument("runs", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "preview":
        t0 = time.time()
        g, rows = preview(a.mod, environ=dict(os.environ, **{ENV_MODE: SHADOW}))
        if a.json:
            print(json.dumps([dict(zip(("chain", "action", "why", "key"), r)) for r in rows], indent=1))
            return 0
        n = sum(1 for r in rows if r[1] in (SKIP, WOULD))
        print("%s: %d of %d chains known good now (%.1fs); purpose %s" % (a.mod, n, len(rows), time.time() - t0,
                                                                         g.purpose))
        for name, act, why, key in rows:
            print("  %-34s %-10s %s  %s" % (name, act, (key or "-")[:10], why[:150]))
        return 0
    tot = {"chains": 0, "would_skip": 0, "skipped": 0, "misses": [], "drift": [], "unreadable": []}
    for path in a.runs:
        with open(path, encoding="utf-8") as f:
            r = audit_run(json.load(f))
        for k in ("chains", "would_skip", "skipped"):
            tot[k] += r[k]
        for k in ("misses", "drift", "unreadable"):
            tot[k] += ["%s: %s" % (os.path.basename(path), x) for x in r[k]]
    ws = tot["would_skip"] + tot["skipped"]
    print("runs %d, chains %d, known-good %d (skip rate %.0f%%), audited %d, misses %d (miss rate %s)" % (
        len(a.runs), tot["chains"], ws, 100.0 * ws / max(1, tot["chains"]), tot["would_skip"], len(tot["misses"]),
        "%.0f%%" % (100.0 * len({m.split("/")[0] for m in tot["misses"]}) / tot["would_skip"])
        if tot["would_skip"] else "n/a"))
    for k in ("misses", "drift", "unreadable"):
        for x in tot[k]:
            print("  %s %s" % (k[:-1] if k != "drift" else "drift", x))
    return 0


if __name__ == "__main__":
    sys.exit(main())
