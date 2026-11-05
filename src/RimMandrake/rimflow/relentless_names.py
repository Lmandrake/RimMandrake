#!/usr/bin/env python3
"""The one resolver for the mod names a live_proofs file gives (`live-mods:` / `live-deploy:`), asked before a game slot.

LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING (census 2026-11-05, 31 items lost about 57 item-games to the mod list): a name
was read three different ways (relentless_live.is_package, modlist_swap.split_names, deploy_custom_mods), so a wrong one
went unseen until a load refused it, and one rider's `RimMandrake.FlowWorks` held a whole batched load
(OPS_CHURN_DIAGNOSE_TITANIC_WYZE_DMPL). Here a name resolves ONCE, against one index of what this machine can load:

    folder      a repo mod folder, or a folder in the game's Mods folder (kept as written)
    composed    a compose target (RimMandrake.Biomes): a folder, even with its dot (OPS_CHURN_DIAGNOSE_OLLOPOM_JLHV_AJHK)
    folded      a source folded into a composed mod (Stillsand, CreatureBehaviors): normalised to its target, the mod
                the load really holds; deploy_custom_mods.folded() is the verification
    repo_pid    the packageId of one of our repo mods (mandrake.rsw.armoury): loaded by packageId, as before
    package     a packageId some installed mod carries (Steam workshop, the game's Mods folder, DLC): loaded, never deployed
    unverified  the index for that shape could not be read (a walled box, an unmounted drive): passed on, never refused,
                because an instrument that cannot see is no evidence of a wrong name
    unknown     none of these: REFUSED, with what the name looked like and the nearest known names

Need inference (advise) is ADVISORY: a warning with file:line evidence, never written into a proof. A name on an absence
line (`--absent RUT_PaleMoss`, "not loaded", "forbid") is no evidence of need (the blind review's caution).
CLI: `check --item ID` (the books' current file), `replay --fixture F` (the census replay), `extract` (builds it).
"""
import argparse
import difflib
import json
import os
import posixpath
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
PROOFS_DIR = "infrastructure/state/live_proofs"

RESOLVED = ("folder", "composed", "folded", "repo_pid", "package")
FOLDERISH = ("folder", "composed", "folded")
PATHISH = re.compile(r"[/\\]|\.(?:xml|txt|json|py|md|rws)$", re.I)
CORE = "ludeon.rimworld"
BASE = ("ludeon.rimworld", "brrainz.harmony")     # in every list we load: never advice


class Index(object):
    """What this machine can load. folders: repo mod folders; folded: {source: (target, key)}; game: folder names in the
    game's Mods folder (None: unreadable); packages: installed packageIds, lower-case (None: unreadable), or a callable
    returning them (paid only when a dotted non-folder name is asked); repo_pids: {packageId lower: repo folder}."""

    def __init__(self, folders, folded=None, game=None, packages=None, repo_pids=None, namespaces=None, deps=None):
        self.folders = set(folders) if folders is not None else None
        self.folded = dict(folded or {})
        self.targets = {t for t, _k in self.folded.values()}
        self.game = set(game) if game is not None else None
        self._packages = packages
        self.repo_pids = {k.lower(): v for k, v in (repo_pids or {}).items()}
        self.namespaces = dict(namespaces or {})     # C# root namespace -> repo mod folder (advice only)
        self._deps = deps                            # mod folder or packageId -> [dependency packageIds]

    @property
    def deps(self):
        if callable(self._deps):
            try:
                self._deps = self._deps()
            except Exception:
                self._deps = {}
        return self._deps or {}

    @property
    def packages(self):
        if callable(self._packages):
            try:
                self._packages = {p.lower() for p in self._packages()}
            except Exception:     # an unreadable workshop folder is blindness, never a refusal
                self._packages = None
        return self._packages

    def is_folder(self, name):
        """A mod folder this machine has by that exact name (modlist_swap.is_mod_folder's question)."""
        return self.kind(name) in FOLDERISH

    def kind(self, name):
        return resolve(name, self)["kind"]

    def known(self):
        out = set(self.folders or ()) | set(self.folded) | self.targets | set(self.game or ())
        return out | set(self.packages or ()) | set(self.repo_pids)

    def as_json(self):
        return {"folders": sorted(self.folders) if self.folders is not None else None,
                "folded": {k: list(v) for k, v in sorted(self.folded.items())},
                "game": sorted(self.game) if self.game is not None else None,
                "packages": sorted(self.packages) if self.packages is not None else None,
                "repo_pids": dict(sorted(self.repo_pids.items())),
                "namespaces": dict(sorted(self.namespaces.items())),
                "deps": {k: v for k, v in sorted(self.deps.items()) if v}}

    @classmethod
    def from_json(cls, d):
        return cls(d.get("folders"), {k: tuple(v) for k, v in (d.get("folded") or {}).items()}, d.get("game"),
                   d.get("packages"), d.get("repo_pids"), d.get("namespaces"), d.get("deps"))


def nearest(name, index, n=3):
    """The known names a mistyped one most likely meant: the part after its last dot, a case-only difference, then
    difflib over every known name (case folded)."""
    known = sorted(index.known())
    low = {k.lower(): k for k in known}
    out = []
    tail = name.rsplit(".", 1)[-1]
    for cand in (name, tail):
        if cand.lower() in low and low[cand.lower()] != name:
            out.append(low[cand.lower()])
    for m in difflib.get_close_matches(name.lower(), list(low), n=n + 2, cutoff=0.6):
        if low[m] not in out and low[m] != name:
            out.append(low[m])
    return out[:n]


def resolve(name, index, near=True):
    """One `live-mods:` name -> {"name", "kind", "canon", "why"[, "near"]} (kinds: module docstring). Pure on `index`.
    near=False skips the nearest-name search (advise scans whole data files; only a refusal needs it)."""
    out = {"name": name, "kind": "unknown", "canon": None, "why": None}
    if index.folders is None:
        out.update(kind="unverified", canon=name, why="the repo's mod folders could not be read")
        return out
    if PATHISH.search(name):
        out["why"] = "looks like a file path, not a mod: name the mod folders or packageIds the file lists"
    elif name in index.folded:
        out.update(kind="folded", canon=index.folded[name][0],
                   why="folded into %s: the load holds that mod, not %s" % (index.folded[name][0], name))
        return out
    elif name in index.targets:
        out.update(kind="composed", canon=name)
        return out
    elif name in index.folders or name in (index.game or ()):
        out.update(kind="folder", canon=name)
        return out
    elif "." in name:
        low = name.lower()
        if low in index.repo_pids:
            out.update(kind="repo_pid", canon=low,      # loaded by packageId as before, never planned as a tree
                       why="the packageId of repo mod %s (name the folder to have it deployed too)" % index.repo_pids[low])
            return out
        pk = index.packages
        if pk is None:
            out.update(kind="unverified", canon=low, why="no installed-packageId index could be read")
            return out
        if low in pk or low.startswith(CORE):
            out.update(kind="package", canon=low)
            return out
        out["why"] = "looks like a packageId, but no installed mod (workshop, game Mods folder, DLC) carries it"
    else:
        if index.game is None and not any(n.lower() == name.lower() for n in index.folders):
            out.update(kind="unverified", canon=name, why="the game's Mods folder could not be read")
            return out
        out["why"] = "no mod folder of that name in the repo or the game's Mods folder"
    near = nearest(name, index) if near else None
    if near:
        out["near"] = near
    return out


def check(names, index):
    """A proof's names -> {"mods": canonical names a load needs (no repeats, unknown ones left out), "refused": [...],
    "normalized": [...], "unverified": [...]} (resolve's dicts)."""
    out = {"mods": [], "refused": [], "normalized": [], "unverified": []}
    for n in names:
        r = resolve(n, index)
        if r["kind"] == "unknown":
            out["refused"].append(r)
            continue
        if r["kind"] == "folded":
            out["normalized"].append(r)
        elif r["kind"] == "unverified":
            out["unverified"].append(r)
        if r["canon"] not in out["mods"]:
            out["mods"].append(r["canon"])
    return out


def refusal(refused):
    """check()'s refused list -> one actionable line, or None."""
    if not refused:
        return None
    return "live-mods names no mod this machine has: " + "; ".join(
        "%r %s%s" % (r["name"], r["why"], (" (nearest: %s)" % ", ".join(r["near"])) if r.get("near") else "")
        for r in refused)


# --------------------------------------------------------------------------- the index on this machine

_DEFAULT = None


def default_index():
    """The index from the repo (deploy_custom_mods.mod_dirs/folded and each mod's About.xml packageId), the game's Mods
    folder listing, and modset_builder.scan for installed packageIds (lazy: about 11 s over the Windows mount). Cached per
    process only when every part read: a blind part is read again next time."""
    global _DEFAULT
    if _DEFAULT is not None:
        return _DEFAULT
    if UTILS not in sys.path:
        sys.path.insert(0, UTILS)
    import xml.etree.ElementTree as ET
    blind = False
    try:
        import deploy_custom_mods as D
        dirs = D.mod_dirs()
        folded = D.folded()
    except SystemExit:
        dirs, folded, blind = None, {}, True
    pids, deps, namespaces = {}, {}, {}

    def about(path):
        try:
            root = ET.parse(os.path.join(path, "About", "About.xml")).getroot()
        except (OSError, ET.ParseError):
            return None, []
        dep = [(e.findtext("packageId") or "").strip().lower() for e in root.iter("li") if e.find("packageId") is not None]
        return (root.findtext("packageId") or "").strip().lower() or None, [d for d in dep if d]
    for folder, src in (dirs or {}).items():
        pid, dep = about(src)
        if pid:
            pids[pid] = folder
        deps[folder] = dep
        for proj in _csprojs(src):
            ns = _root_namespace(proj)
            if ns and ns not in namespaces:
                namespaces[ns] = folder
    game = None
    try:
        from game_paths import GAME_DIR
        mods = os.path.join(GAME_DIR, "Mods")
        if os.path.isdir(mods):
            game = [d for d in os.listdir(mods) if os.path.isfile(os.path.join(mods, d, "About", "About.xml"))]
            for t in {t for t, _k in folded.values()}:      # the composed mod's packageId (mandrake.rm.biomes)
                pid, dep = about(os.path.join(mods, t))
                if pid:
                    pids[pid] = t
                deps[t] = dep
    except (ImportError, OSError):
        game = None
    blind = blind or game is None
    scanned = {}

    def scan():
        if "s" not in scanned:
            import modset_builder
            if not any(os.path.isdir(b) for b in (modset_builder.WORKSHOP, modset_builder.LOCAL_MODS)):
                raise OSError("no workshop or game Mods folder")
            scanned["s"] = modset_builder.scan()
        return scanned["s"]

    def all_deps():
        out = dict(deps)
        try:
            out.update({p: r.get("deps") or [] for p, r in scan().items() if p not in pids})
        except OSError:
            pass
        return out
    idx = Index(list(dirs) if dirs is not None else None, folded, game, lambda: list(scan()), pids, namespaces, all_deps)
    if not blind:
        _DEFAULT = idx
    return idx


def _csprojs(src):
    out = []
    for base, dnames, files in os.walk(src):
        dnames[:] = [d for d in dnames if d not in ("bin", "obj", "Textures", "Defs", "Patches", "Languages")]
        out += [os.path.join(base, f) for f in files if f.endswith(".csproj") and "SelfTest" not in f]
    return out


def _root_namespace(proj):
    try:
        with open(proj, encoding="utf-8", errors="replace") as f:
            m = re.search(r"<RootNamespace>\s*([\w.]+)\s*</RootNamespace>", f.read())
    except OSError:
        return None
    return m.group(1) if m else os.path.splitext(os.path.basename(proj))[0]


# --------------------------------------------------------------------------- advisory need inference

ABSENT = re.compile(r"absent|absence|not\s+loaded|forbid|must\s+not|lacks?\b|without", re.I)
# where a script names a mod: a quoted string, a --mod/--with/--enable argument, a src/<tier>/<Mod>/ or Mods/<Mod>/ path,
# or (anywhere) a dotted token an installed mod carries as its packageId (7f.alienworlds.tidallylocked). A bare word in
# prose ("[RM Minerals] quarry") is no evidence: it named Minerals for every proof that ran live_log_check.py.
QUOTED = re.compile(r"[\"']([A-Za-z0-9][\w.\-]*)[\"']")
FLAG = re.compile(r"--(?:mod|mods|with|enable)[ =]+([\w.\-]+)")
PATHSEG = re.compile(r"(?:src/(?:RimMandrake|RimStarWars|RimUtinni)|Mods)[/\\]([\w.\-]+)")
DOTTED = re.compile(r"(?<![\w.])([A-Za-z0-9][\w\-]*(?:\.[\w\-]+)+)")
SCRIPT = re.compile(r"(?:^|\s)((?:\./)?src/[^\s'\"]+\.py)\b")
SRC_MOD = re.compile(r"^src/(?:RimMandrake|RimStarWars|RimUtinni)/([^/]+)/")


def proof_scripts(text):
    """The repo scripts a proofs file's `live-proof` lines run (src/....py), in order."""
    out = []
    for line in (text or "").splitlines():
        if not re.match(r"^\s*(?:[-*]\s+)?`?live-proof\b", line):
            continue
        for m in SCRIPT.finditer(line):
            p = m.group(1)[2:] if m.group(1).startswith("./") else m.group(1)
            if p not in out:
                out.append(p)
    return out


IMPORT = re.compile(r"^\s*(?:import\s+([\w, ]+)|from\s+(\w+)\s+import\b)", re.M)
DATAFILE = re.compile(r"[\"']([\w\-]+\.(?:json|csv|ya?ml))[\"']")
MAX_DATA = 512 * 1024


def gather_scripts(text, read):
    """{repo path: content} of what a proofs file's lines run, and the data they read, one hop: each proof script
    (proof_scripts), plus every data file (.json/.csv/.yaml, by literal name, in the reader's own directory) that the
    script or a sibling module it imports names. A sibling module is a route to its data, never scanned itself (a shared
    harness module would advise every proof). read(path) -> str or "" (git show at a sha, or the books' file).
    ART_OVERRIDE_FAMILY_SCRIPT_1: its donors were named only in art_fold_manifest.json, read through art_fold_check."""
    out, readers = {}, {}
    for p in proof_scripts(text):
        body = read(p)
        if body:
            out[p] = readers[p] = body
    for p, body in list(readers.items()):
        d = posixpath.dirname(p)
        for m in IMPORT.finditer(body):
            for n in (m.group(1) or m.group(2) or "").split(","):
                n = n.strip().split(" ")[0]
                q = posixpath.join(d, n + ".py")
                if n and q not in readers:
                    b = read(q)
                    if b:
                        readers[q] = b
    for p, body in readers.items():
        d = posixpath.dirname(p)
        for m in DATAFILE.finditer(body):
            q = posixpath.join(d, m.group(1))
            if q not in out:
                b = read(q)
                if b and len(b) <= MAX_DATA:
                    out[q] = b
    return out


def read_books(path):
    try:
        with open(os.path.join(BOOKS, path), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


STRIP_ABSENT = re.compile(r"--(?:without|absent|forbid|lacks?|not-loaded)[ =]+\S+")
NEED_CUE = re.compile(r"\b(?:active|loaded|enabled|needs?|requires?|depends\s+on)\b", re.I)
WORD = re.compile(r"(?<![\w.\-/\\])([A-Za-z][\w]*(?:\.[A-Za-z][\w]*)*)(?![\w\-/\\])")
TYPE_STR = re.compile(r"(?<![\w.])((?:[A-Z][\w]*\.){1,}[A-Z][\w]*)")


def _tokens(line, index, typed=None):
    """The mod names a line gives, as (token) in order: absence flags' arguments struck first; a line that still reads
    as an absence assertion gives none. typed: a set that collects the tokens a C# type gave (the mod whose DLL a call
    needs)."""
    line = STRIP_ABSENT.sub(" ", line)
    if ABSENT.search(line):
        return []
    pk = set(index.packages or ()) | set(index.repo_pids)
    toks = QUOTED.findall(line) + FLAG.findall(line) + PATHSEG.findall(line)
    toks += [t for t in DOTTED.findall(line) if t.lower() in pk]
    if NEED_CUE.search(line):       # "with RimThemes + MenuShell active": a bare mod folder on a line that needs it
        names = set(index.folders or ()) | set(index.game or ()) | set(index.folded) | index.targets
        toks += [t for t in WORD.findall(line) if t in names]
    for t in TYPE_STR.findall(line):        # a C# type of ours: its longest root namespace names the mod
        parts = t.split(".")
        for k in range(len(parts) - 1, 0, -1):
            ns = ".".join(parts[:k])
            if ns in index.namespaces:
                toks.append(index.namespaces[ns])
                if typed is not None:
                    typed.add(index.namespaces[ns])
                break
    return toks


def closure_gaps(have, index):
    """Transitive About.xml dependencies modlist_swap --enable would miss: it adds a FOLDER's immediate dependencies
    only (modlist_swap.enable), a packageId's whole closure (package_closure). -> [(mod, missing pid, via pid)]."""
    pid_of = {v: k for k, v in index.repo_pids.items()}
    folders = [m for m in sorted(have) if m in (index.folders or ()) or m in index.targets]
    # what the enable adds: every named mod, and each named FOLDER's immediate dependencies (a packageId: its closure)
    held = {pid_of.get(m, m.lower()) for m in have} | {d.lower() for m in folders for d in index.deps.get(m, [])}
    out = []
    for m in folders:
        first = [d.lower() for d in index.deps.get(m, [])]
        seen, queue = set(held), list(first)
        while queue:
            via = queue.pop(0)
            key = index.repo_pids.get(via, via)
            for d in index.deps.get(key, []):
                d = d.lower()
                if d not in seen and not d.startswith(BASE):
                    seen.add(d)
                    queue.append(d)
                    out.append((m, d, via))
    return out


def advise(text, scripts, have, index, named=None, build=None):
    """Need inference, ADVISORY ONLY. text: the proofs file; scripts: {repo path: content} of the scripts its proof
    lines run; have: the canonical mods the load will already hold (the build's and the proof's). -> [{"mod", "at"
    ("path:line"), "line"}]: a mod the proof lines or their scripts name (_tokens: a quoted name, a --mod/--needs-style
    argument, a src/<tier>/<Mod>/ path, an installed packageId, a C# type in one of our root namespaces), the subject
    mod a proof script lives in, or a transitive dependency the enable would not add, that `have` lacks. Never written
    anywhere: a name on an absence line (--absent RUT_PaleMoss, "must not be loaded") is skipped, not inverted.
    named: the mods live-mods names (check()["mods"]). A C# type the proof calls must be NAMED, not only derived from the
    build: a proof-only or later sha derives no build mod, and a derived one rode with a stale DLL
    (SETTLEMENT_VERBS_WAVE_1, fixed by naming RimProperty in c5e1eedf3a).
    build: the build's own mod folders as derived; a folded source among them is noted with the composed mod the load
    really holds unless live-mods names it (WARSCAR_HOSPICE_DESERTERS_1: 'the deploy plan does not cover Scarlands' on a
    plan that composed it)."""
    have = set(have)
    named = set(have if named is None else named)
    out, seen, memo = [], set(), {}
    pid_of = {v: k for k, v in index.repo_pids.items()}

    def res(tok):
        if tok not in memo:
            memo[tok] = resolve(tok, index, near=False)
        return memo[tok]

    def hit(mod, at, line, need=None):
        need = have if need is None else need
        if mod and mod not in need and index.repo_pids.get(mod) not in need and pid_of.get(mod) not in need \
                and mod not in seen \
                and not mod.startswith(BASE):
            seen.add(mod)
            out.append({"mod": mod, "at": at, "line": line.strip()[:160]})

    def scan(path, body):
        for n, line in enumerate((body or "").splitlines(), 1):
            if path == PROOFS_DIR and re.match(r"^\s*(?:[-*]\s+)?`?live-(?:mods|deploy)\s*:", line):
                continue
            typed = set()
            for tok in _tokens(line, index, typed):
                r = res(tok)
                if r["kind"] in RESOLVED:
                    hit(r["canon"], "%s:%d" % (path, n), line, named if tok in typed else None)
    for mod in sorted(build or ()):
        if mod in index.folded:
            hit(index.folded[mod][0], "build: %s" % mod, "the build's %s is folded into %s: the load holds that mod, "
                "not %s; name it" % (mod, index.folded[mod][0], mod), named)
    for path in proof_scripts(text):
        m = SRC_MOD.match(path)
        if m:
            r = resolve(m.group(1), index)
            if r["kind"] in RESOLVED:
                hit(r["canon"], "%s:0" % path, "the proof script lives in this mod")
    scan(PROOFS_DIR, text)
    for path, body in sorted((scripts or {}).items()):
        scan(path, body)
    for mod, dep, via in closure_gaps(have | seen, index):
        hit(dep, "About.xml of %s" % mod, "%s needs %s through %s; modlist_swap --enable adds only immediate "
                                         "dependencies of a folder" % (mod, dep, via))
    return out


# --------------------------------------------------------------------------- census replay

def judge_case(case, index):
    """One frozen proof (text, scripts, build mods) -> {"refused", "advice", "caught"}."""
    import relentless_live_round as R
    chk = check(R.live_mods(case.get("text") or ""), index)
    have = set(chk["mods"]) | set(check(case.get("build_mods") or [], index)["mods"])
    adv = advise(case.get("text") or "", case.get("scripts") or {}, have, index, named=chk["mods"],
                 build=case.get("build_mods") or [])
    one = lambda m: index.repo_pids.get(str(m).lower(), m)     # a repo packageId and its folder are one mod
    have_id = {one(m) for m in have}
    owed = [m for m in case.get("added") or [] if one(m) not in have_id]
    got = {"refused": [r["name"] for r in chk["refused"]], "normalized": [r["name"] for r in chk["normalized"]],
           "advice": ["%s@%s" % (a["mod"], a["at"]) for a in adv],
           "owed": owed, "hit": sorted(m for m in owed if one(m) in {one(a["mod"]) for a in adv}),
           "at": case.get("at"), "sha": case.get("sha"), "run_sha": case.get("run_sha")}
    # a warning that names none of the mods its later fix added is not a catch (any advice would do otherwise)
    got["caught"] = bool(chk["refused"] or chk["normalized"] or (adv and (got["hit"] or not owed)))
    if case.get("expect_kinds"):    # a case whose defect was a RIGHT name misread: caught when it resolves as expected
        kinds = [resolve(n, index)["kind"] for n in R.live_mods(case.get("text") or "")]
        got["kinds"] = kinds
        got["caught"] = bool(kinds) and all(k in case["expect_kinds"] for k in kinds)
    return got


def reach(case, index):
    """Why this case went unwarned, MEASURED from the frozen case (a diagnosis printed with the miss; never a pass)."""
    import relentless_live_round as R
    have = set(check(R.live_mods(case.get("text") or ""), index)["mods"]) | \
        set(check(case.get("build_mods") or [], index)["mods"])
    one = lambda m: index.repo_pids.get(str(m).lower(), m)     # a repo packageId and its folder are one mod
    have_id = {one(m) for m in have}
    owed = [m for m in case.get("added") or [] if one(m) not in have_id]
    if not owed:
        return "no warning at all, and every mod its later fix added was its build's or named at this run"
    pid_of = {v: k for k, v in index.repo_pids.items()}
    blob = "\n".join([case.get("text") or ""] + list((case.get("scripts") or {}).values())).lower()
    if not any(m.lower() in blob or pid_of.get(m, "\0") in blob for m in owed):
        return "its proof and scripts name none of %s" % ", ".join(owed)
    return "a name of %s is present but no rule read it (advice, if any, named other mods)" % ", ".join(owed)


def replay(fx):
    """The fixture -> (exit, report). A census item may hold several frozen cases (one per failed run, at that run's
    proof text, scripts and build). Exit 0 only when every R4 item is refused (or normalised: a folded source the load
    now takes as its composed mod), every R1 item is warned or refused in EVERY one of its cases, and no PASS proof is
    refused. A miss is a FAIL whatever its diagnosis: the criterion has no unreachable class."""
    index = Index.from_json(fx["index"])
    rep = {"R1": {}, "R2": {}, "R4": {}, "pass_refused": [], "pass_n": 0}
    ok = True
    for case in fx["cases"]:
        got = judge_case(case, index)
        if case["root"] == "R4" and not case.get("expect_kinds"):
            got["caught"] = bool(got["refused"] or got["normalized"])
        if not got["caught"]:
            got["why_missed"] = reach(case, index)
        it = rep[case["root"]].setdefault(case["item"], {"caught": True, "hit": [], "cases": []})
        it["cases"].append(got)
        it["caught"] = it["caught"] and got["caught"]
        it["hit"] = sorted(set(it["hit"]) | set(got["hit"]))
    for root in ("R1", "R4"):
        ok = ok and all(v["caught"] for v in rep[root].values())
    for case in fx["passes"]:
        got = judge_case(case, index)
        rep["pass_n"] += 1
        if got["refused"]:
            rep["pass_refused"].append({"item": case["item"], "refused": got["refused"]})
            ok = False
    for root in ("R1", "R2", "R4"):
        rep[root + "_caught"] = "%d/%d" % (sum(1 for v in rep[root].values() if v["caught"]), len(rep[root]))
        owing = {i for i, v in rep[root].items() if any(g["owed"] for g in v["cases"])}
        rep[root + "_hit"] = "%d/%d" % (sum(1 for i in owing if rep[root][i]["hit"]), len(owing))
        rep[root + "_cases"] = sum(len(v["cases"]) for v in rep[root].values())
    rep["pass_advised"] = sum(1 for c in fx["passes"] if judge_case(c, index)["advice"])
    return (0 if ok else 1), rep


def _git(args):
    return subprocess.run(["git", "-C", BOOKS] + args, capture_output=True, text=True, timeout=120).stdout


def _build_mods(item, sha):
    """The build's mods at `sha` as a load would derive them (relentless_live_round.item_mods), [] when unreadable."""
    import relentless_live_round as R
    try:
        return sorted(R.item_mods(R.RoundFx(seat="BENCH"), item, sha))
    except Exception:
        return []


def _frozen(item, sha, root, index, build_mods=None, build_sha=None):
    """The proofs file and what it runs (gather_scripts) as they stood at `sha`; the build's mods at build_sha (the run's
    own sha; default `sha`)."""
    text = _git(["show", "%s:%s/%s.txt" % (sha, PROOFS_DIR, item)])
    scripts = gather_scripts(text, lambda p: _git(["show", "%s:%s" % (sha, p)]))
    if build_mods is None:
        build_mods = _build_mods(item, build_sha or sha)
    return {"item": item, "root": root, "sha": sha, "text": text, "scripts": scripts, "build_mods": list(build_mods)}


def _rows(runs_path):
    import datetime
    rows = []
    with open(runs_path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict) and isinstance(r.get("at"), (int, float)):     # some rows carry epoch seconds
                r["at"] = datetime.datetime.fromtimestamp(r["at"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if isinstance(r, dict):
                rows.append(r)
    return rows


def _books_at(at):
    """The books' commit as they stood at a runs.jsonl time (the stager reads the books' current proofs file)."""
    return _git(["log", "-1", "--format=%H", "--before=" + at, "origin/main"]).strip() or \
        _git(["log", "-1", "--format=%H", "--before=" + at]).strip()


def extract(census, runs_path, out_path, n_pass=50):
    """Freeze the census cases and the last n_pass PASS proofs into a fixture the walled checker can replay with no git
    history. No hindsight: a census item gives one case per distinct failed run (outcome not PASS, with a sha), its proof
    text and scripts as the books held them at the run's time, its build mods at the run's sha; runs after the item's last
    live-mods change are left out (their failure was not that name). An item with no such run (or a census `sha`) is
    frozen at that sha or its oldest version. `added`: what the newest version's live-mods names that the case lacked."""
    import relentless_live_round as R
    index = default_index()
    idx_json = index.as_json()
    rows = _rows(runs_path)
    cases = []
    for c in census:
        if c.get("rider_of"):       # an ops case: one rider's text inside another's batch
            cases.append({"item": c["item"], "root": c["root"], "sha": None, "text": c["text"], "scripts": {},
                          "build_mods": [], "rider_of": c["rider_of"], "expect_kinds": c.get("expect_kinds")})
            continue
        path = "%s/%s.txt" % (PROOFS_DIR, c["item"])
        log = [l.split(" ", 1) for l in _git(["log", "--format=%H %cI", "--", path]).splitlines() if " " in l]
        shas = [h for h, _ in log]
        newest = check(R.live_mods(_git(["show", "%s:%s" % (shas[0], path)])), index)["mods"] if shas else []
        mods_at = {h: tuple(check(R.live_mods(_git(["show", "%s:%s" % (h, path)])), index)["mods"]) for h in shas}
        last_change = None          # the commit time of the newest version whose live-mods differs from its parent's
        for i in range(len(shas) - 1):
            if mods_at[shas[i]] != mods_at[shas[i + 1]]:
                last_change = log[i][1]
                break
        picks = []
        if not c.get("sha"):
            seen = set()
            for r in rows:
                if r.get("item") != c["item"] or r.get("outcome") == "PASS" or not r.get("sha") or not r.get("at"):
                    continue
                if last_change and _ts(r["at"]) >= _ts(last_change):
                    continue
                books = _books_at(r["at"])
                if not books:
                    continue
                key = (_git(["rev-parse", "--verify", "-q", "%s:%s" % (books, path)]).strip(), r["sha"])
                if key[0] and key not in seen:
                    seen.add(key)
                    picks.append((books, r["sha"], r["at"]))
        if not picks:
            pick = c.get("sha") or (shas[-1] if shas else None)
            picks = [(pick, None, None)] if pick else []
        for books, run_sha, at in picks:
            fr = _frozen(c["item"], books, c["root"], index, build_sha=run_sha)
            fr.update(run_sha=run_sha, at=at)
            was = set(check(R.live_mods(fr["text"]), index)["mods"])
            # a mod made after this run (NullTexTrace, 4394690bbf) was a new approach, not a name this run omitted
            fr["added"] = [m for m in newest if m not in was and _existed(m, books, index)]
            fr["added_later"] = [m for m in newest if m not in was and m not in fr["added"]]
            cases.append(fr)
    passes, seen = [], set()
    for row in reversed(rows):
        if row.get("outcome") != "PASS" or not row.get("sha") or not row.get("item"):
            continue
        key = (row["item"], row["sha"])
        if key in seen:
            continue
        seen.add(key)
        # the stager reads the books' proofs file at run time (941ec4ff05), as the failed cases are frozen
        books = _books_at(row["at"]) if row.get("at") else ""
        fr = _frozen(row["item"], books, "PASS", index, build_sha=row["sha"]) if books else {}
        if not fr.get("text"):
            fr = _frozen(row["item"], row["sha"], "PASS", index)
        fr.update(run_sha=row["sha"], at=row.get("at"))
        passes.append(fr)
        if len(passes) >= n_pass:
            break
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"index": idx_json, "cases": cases, "passes": passes}, f, indent=0, sort_keys=True)
    return len(cases), len(passes)


def _existed(mod, sha, index):
    """Was this repo mod's folder in the tree at `sha`? A packageId or a non-repo name: assumed (no history to read)."""
    if mod not in (index.folders or ()) or mod in index.targets:     # a composed target is built, not a tree
        return True
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        if _git(["ls-tree", "--name-only", sha, "src/%s/%s" % (tier, mod)]).strip():
            return True
    return False


def _ts(iso):
    """An ISO time (Z or an offset) -> epoch seconds, for ordering runs against commits."""
    import datetime
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


# a runs.jsonl row whose reason is the mod list (the census's R1/R2/R4/R5/R6 shapes), for the before/after count
MODLIST_CAUSE = re.compile(r"not in the running load|not enabled in ModsConfig|Type not found|installed in neither|"
                           r"no readable packageId|missing_mod|modlist gate|WRONG_TIER|does not cover|"
                           r"live-mods names no mod|not loaded on this tier", re.I)


def modlist_census(rows, since="", until="~"):
    """runs.jsonl rows -> {rows, nonpass, modlist_rows, modlist_items, modlist_games, by_cause}: the non-PASS rows in
    [since, until) whose reason is the mod list. The criterion's before/after measure (LIVE_MODS_ENFORCE_..._BOARDING)."""
    out = {"since": since, "until": until, "rows": 0, "nonpass": 0, "modlist_rows": 0}
    items, games, causes = set(), set(), {}
    for r in rows:
        at = r.get("at") or ""
        if not isinstance(at, str):     # one row of 859 (2026-11-05) carries epoch seconds
            import time
            at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(at)))
        if not (since <= at < until):
            continue
        out["rows"] += 1
        if r.get("outcome") in (None, "PASS"):
            continue
        out["nonpass"] += 1
        m = MODLIST_CAUSE.search(r.get("why") or "")
        if not m:
            continue
        out["modlist_rows"] += 1
        items.add(r.get("item"))
        games.add(r.get("game"))
        causes[m.group(0).lower()] = causes.get(m.group(0).lower(), 0) + 1
    out.update(modlist_items=len(items), modlist_games=len(games - {None}),
               by_cause=sorted(([n, k] for k, n in causes.items()), key=lambda x: (-x[0], x[1])))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check", help="resolve an item's live-mods names; refusals exit 1, advice is printed")
    p.add_argument("--item", required=True)
    p = sub.add_parser("replay", help="the census replay over a frozen fixture")
    p.add_argument("--fixture", required=True)
    p.add_argument("--report", help="write the whole report here")
    p = sub.add_parser("extract", help="freeze the census and the last PASS proofs into a fixture (needs git)")
    p.add_argument("--census", required=True, help="json: [{item, root[, sha][, text, rider_of]}]")
    p.add_argument("--runs", default="/home/mandrake/rm/relentless/live/runs.jsonl")
    p.add_argument("--out", required=True)
    p = sub.add_parser("baseline", help="runs.jsonl: the non-PASS rows whose reason is the mod list, in a window")
    p.add_argument("--runs", default="/home/mandrake/rm/relentless/live/runs.jsonl")
    p.add_argument("--since", default="")
    p.add_argument("--until", default="~")
    a = ap.parse_args(argv)
    sys.path.insert(0, HERE)
    if a.cmd == "baseline":
        if not os.path.isfile(a.runs):
            print("UNMEASURED: no %s" % a.runs)
            return 2
        rows = []
        with open(a.runs, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
        print(json.dumps(modlist_census(rows, a.since, a.until), sort_keys=True))
        return 0
    if a.cmd == "check":
        import relentless_live_round as R
        try:
            with open(os.path.join(BOOKS, PROOFS_DIR, a.item + ".txt"), encoding="utf-8") as f:
                text = f.read()
        except OSError:
            print("UNMEASURED: no %s/%s.txt" % (PROOFS_DIR, a.item))
            return 2
        index = default_index()
        chk = check(R.live_mods(text), index)
        scripts = gather_scripts(text, read_books)
        for r in chk["normalized"] + chk["unverified"]:
            print("NOTE %s -> %s: %s" % (r["name"], r["canon"], r["why"]))
        for adv in advise(text, scripts, chk["mods"], index, named=chk["mods"]):
            print("ADVICE (not written anywhere) %s may be needed: %s  %s" % (adv["mod"], adv["at"], adv["line"]))
        why = refusal(chk["refused"])
        print(why or "OK %s names %s" % (a.item, ", ".join(chk["mods"]) or "no mods"))
        return 1 if why else 0
    if a.cmd == "replay":
        with open(a.fixture, encoding="utf-8") as f:
            fx = json.load(f)
        code, rep = replay(fx)
        if a.report:
            with open(a.report, "w", encoding="utf-8") as f:
                json.dump(rep, f, indent=1, sort_keys=True)
        print("R4 caught %s  R1 caught %s over %d failed runs (advice names a mod later added: %s)  R2 caught %s (%s)  "
              "PASS proofs refused %d of %d, advised %d  -> %s" % (
            rep["R4_caught"], rep["R1_caught"], rep["R1_cases"], rep["R1_hit"], rep["R2_caught"], rep["R2_hit"],
            len(rep["pass_refused"]), rep["pass_n"], rep["pass_advised"], "OK" if code == 0 else "FAIL"))
        for root in ("R4", "R1", "R2"):
            for item, it in sorted(rep[root].items()):
                for got in it["cases"]:
                    if not got["caught"]:
                        print("  missed %s %s (run %s at %s): %s" % (root, item, (got.get("run_sha") or "-")[:10],
                                                                     got.get("at") or "-", got.get("why_missed")))
        for p in rep["pass_refused"]:
            print("  false refusal %s: %s" % (p["item"], ", ".join(p["refused"])))
        return code
    with open(a.census, encoding="utf-8") as f:
        census = json.load(f)
    n, m = extract(census, a.runs, a.out)
    print("froze %d census cases and %d PASS proofs into %s" % (n, m, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
