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

Need inference (needs/advise), LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: a need from a SURE source is ADDED to the planned
load by the pre-slot gate (relentless_live_round.mod_gap/batch_gap), derived every time and never written into a proof;
the run row records it with its file:line evidence (`env`). Every other need only warns. `live-without: <mods>` is the
explicit opt-out for a proof that intends a mod's absence: never inferred, a planned load holding one is refused before
the slot, and batch_gap never puts a rider needing X on a load with one that is live-without X. A name on an absence
line (`--absent RUT_PaleMoss`, "not loaded", "not present", "forbid") is no evidence of need (the blind review's caution).
CLI: `check --item ID` (the books' current file), `replay [--enforce] --fixture F` (the census replay), `migrate` (every
live proof), `extract` (builds the fixture), `baseline` (runs.jsonl's mod-list rows in a window).
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
BOOKS = os.path.dirname(os.path.realpath(os.path.join(HERE, "..", "..", "..", ".git")))     # a release tree's .git links to books
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

    def __init__(self, folders, folded=None, game=None, packages=None, repo_pids=None, namespaces=None, deps=None,
                 defs=None, stale=None):
        self.folders = set(folders) if folders is not None else None
        self.folded = dict(folded or {})
        self.targets = {t for t, _k in self.folded.values()}
        self.game = set(game) if game is not None else None
        self._packages = packages
        self.repo_pids = {k.lower(): v for k, v in (repo_pids or {}).items()}
        self.namespaces = dict(namespaces or {})     # C# root namespace -> repo mod folder (advice only)
        self._deps = deps                            # mod folder or packageId -> [dependency packageIds]
        self._defs = defs                            # RM_/RSW_/RUT_ defName -> [mod folders defining it] (or callable)
        self._stale = stale                          # {mod: why} or callable(mod) -> why or None: its index entry is
        #                                              older than what the game folder holds (needs() then only warns)

    @property
    def defs(self):
        if callable(self._defs):
            try:
                self._defs = self._defs()
            except Exception:
                self._defs = {}
        return self._defs or {}

    def stale_for(self, mod):
        """Why the index's knowledge of `mod` (its namespace, defNames) is older than its deployed copy, or None."""
        if callable(self._stale):
            try:
                return self._stale(mod)
            except Exception:
                return None
        return (self._stale or {}).get(mod)

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
                "deps": {k: v for k, v in sorted(self.deps.items()) if v},
                "defs": {k: list(v) for k, v in sorted(self.defs.items())},
                "stale": dict(self._stale) if isinstance(self._stale, dict) else {}}

    @classmethod
    def from_json(cls, d):
        return cls(d.get("folders"), {k: tuple(v) for k, v in (d.get("folded") or {}).items()}, d.get("game"),
                   d.get("packages"), d.get("repo_pids"), d.get("namespaces"), d.get("deps"), d.get("defs"),
                   d.get("stale"))


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
    game, GAME_DIR = None, ""
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
    srcs = dict(dirs or {})

    def stale(mod):
        """A mod whose deployed DLL is not the repo's build (its Assemblies/*.dll.srchash differs from the committed one):
        the namespace and defName index, read from the repo, speaks for a build the game folder does not hold, so a need
        from it only warns until the deploy gate puts the build there. (File mtimes cannot say this: a fresh clone's
        checkout is newer than every deployed DLL.)"""
        if mod not in srcs or game is None:
            return None
        mine = _srchashes(srcs[mod])
        if not mine:
            return None
        theirs = _srchashes(os.path.join(GAME_DIR, "Mods", mod))
        if theirs != mine:
            return "%s's deployed DLL is not the repo's build (.srchash %s)" % (
                mod, "missing" if not theirs else "differs")
        return None
    idx = Index(list(dirs) if dirs is not None else None, folded, game, lambda: list(scan()), pids, namespaces, all_deps,
                lambda: repo_defs(srcs), stale)
    if not blind:
        _DEFAULT = idx
    return idx


DEF_TAG = re.compile(r"<defName>\s*((?:RM|RSW|RUT)_[A-Za-z0-9_]+)\s*</defName>")


def repo_defs(srcs):
    """{repo mod folder: its source dir} -> {RM_/RSW_/RUT_ defName: [folders whose Defs/ define it]}. Our prefixes only:
    a donor defName needs the def dump, and an unprefixed one is too generic to name an owner."""
    out = {}
    for folder, src in sorted(srcs.items()):
        for dp, dn, fn in os.walk(src):
            dn[:] = [d for d in dn if d not in (".git", "obj", "bin", "Source", "Textures", "Sounds")]
            if "Defs" not in dp.replace("\\", "/").split("/"):
                continue
            for f in fn:
                if not f.endswith(".xml"):
                    continue
                try:
                    with open(os.path.join(dp, f), encoding="utf-8", errors="replace") as fh:
                        body = fh.read()
                except OSError:
                    continue
                for d in DEF_TAG.findall(body):
                    if folder not in out.setdefault(d, []):
                        out[d].append(folder)
    return out


def _srchashes(mod_dir):
    """{name: the "# dll:" line} of a mod tree's Assemblies/*.dll.srchash stamps (dll_source_stamp.py), {} if none."""
    out = {}
    d = os.path.join(mod_dir, "Assemblies")
    try:
        names = [f for f in os.listdir(d) if f.endswith(".dll.srchash")]
    except OSError:
        return out
    for f in names:
        try:
            with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                out[f] = next((l.strip() for l in fh if l.startswith("# dll:")), "")
        except OSError:
            out[f] = ""
    return out


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

ABSENT = re.compile(r"absent|absence|not\s+loaded|not\s+present|forbid|must\s+not|lacks?\b|without", re.I)
# where a script names a mod: a quoted string, a --mod/--with/--enable argument, a src/<tier>/<Mod>/ or Mods/<Mod>/ path,
# or (anywhere) a dotted token an installed mod carries as its packageId (7f.alienworlds.tidallylocked). A bare word in
# prose ("[RM Minerals] quarry") is no evidence: it named Minerals for every proof that ran live_log_check.py.
QUOTED = re.compile(r"[\"']([A-Za-z0-9][\w.\-]*)[\"']")
FLAG = re.compile(r"--(?:mods?|with|enable|needs?|requires?)[ =]+((?:[A-Za-z0-9][\w.\-]*(?:[ ,]+|$))+)")
DEFNAME = re.compile(r"(?<![\w.])((?:RM|RSW|RUT)_[A-Za-z0-9_]+)\b")
RWS = re.compile(r"(?<![\w])([\w./\\\-]+\.rws)\b")
PATHSEG = re.compile(r"(?:src/(?:RimMandrake|RimStarWars|RimUtinni)|Mods)[/\\]([\w.\-]+)")
# the same path spelled as os.path.join(REPO, "src", "RimUtinni", "AshkarrWeatherSuite", ...) (HORRORS_RAIDING_FACTION_1)
PATHJOIN = re.compile(r"[\"']src[\"']\s*,\s*[\"'](?:RimMandrake|RimStarWars|RimUtinni)[\"']\s*,\s*[\"']([\w.\-]+)[\"']")
DOTTED = re.compile(r"(?<![\w.])([A-Za-z0-9][\w\-]*(?:\.[\w\-]+)+)")
SCRIPT = re.compile(r"(?:^|\s)((?:\./)?src/[^\s'\"]+\.py)\b")
SRC_MOD = re.compile(r"^src/(?:RimMandrake|RimStarWars|RimUtinni)/([^/]+)/")


# a proof line that runs modcheck: `modcheck/cli.py run <Mod> [<Mod> ...] --flags`. modcheck composes each mod's own list
# (runner.composed_ids: hard dependencies, the mod or its composed mod, its tier closure) and refuses the run as
# stale_load unless the RUNNING load holds every id of it (runner.verify_loaded_list), so the gate must plan them all.
# GAMEENV_FIX_PROOFSITE_9E77C59D_ITEMS_WAIT: ACC_BIOMES_FIXES_LIVE_RERUN_1 named RimMandrake.Biomes, GimmeSomeSlack and
# UtinniPatches; LeaningScrub's tier also wants mandrake.rsw.swbestiary, and A2 read "not loaded: mandrake.rsw.swbestiary"
# twice (2026-11-06 09:03Z, 09:54Z) on a game no lane step could fix.
MODCHECK_RUN = re.compile(r"modcheck/cli\.py\s+run\s+((?:[A-Za-z][\w.\-]*\s*)+?)(?=\s+-|\s*[;<>|&]|\s*$)")


def modcheck_runs(text):
    """The mod folders a proofs file's `live-proof` lines hand to `modcheck/cli.py run`, in order, no repeats."""
    out = []
    for line in (text or "").splitlines():
        if not re.match(r"^\s*(?:[-*]\s+)?`?live-proof\b", line):
            continue
        for m in MODCHECK_RUN.finditer(line):
            for t in m.group(1).split():
                if t not in out:
                    out.append(t)
    return out


_RUNNER = []


def modcheck_composed(mod):
    """runner.composed_ids(mod): the packageIds modcheck composes and checks in the running load for one mod. Loaded by
    path under a private module name (a bare `import runner` could find another runner on sys.path). Raises what the
    runner raises (RuntimeError: no src folder of that name)."""
    if not _RUNNER:
        import importlib.util
        path = os.path.join(UTILS, "modcheck", "runner.py")
        spec = importlib.util.spec_from_file_location("_relentless_modcheck_runner", path)
        mod_ = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod_)
        _RUNNER.append(mod_)
    return list(_RUNNER[0].composed_ids(mod))


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
NEED_CUE = re.compile(r"\b(?:active|loaded|enabled|needs?|requires?|depends\s+on|stag(?:e|er|ing))\b", re.I)
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
    cue = bool(NEED_CUE.search(line))
    toks = [(t, "quoted") for t in QUOTED.findall(line)]
    toks += [(t, "cli") for run in FLAG.findall(line) for t in re.split(r"[ ,]+", run) if t]
    toks += [(t, "path") for t in PATHSEG.findall(line) + PATHJOIN.findall(line)]
    toks += [(t, "cue" if cue else "package") for t in DOTTED.findall(line) if t.lower() in pk]
    if cue:       # "with RimThemes + MenuShell active": a bare mod folder on a line that needs it
        names = set(index.folders or ()) | set(index.game or ()) | set(index.folded) | index.targets
        toks += [(t, "cue") for t in WORD.findall(line) if t in names]
    defs = index.defs
    for t in DEFNAME.findall(line):     # one of our defNames: the mod that defines it, when exactly one does
        owners = sorted(set(defs.get(t) or ()))
        toks += [(o, "defname" if len(owners) == 1 else "defname_multi") for o in owners]
    for t in TYPE_STR.findall(line):        # a C# type of ours: its longest root namespace names the mod
        parts = t.split(".")
        for k in range(len(parts) - 1, 0, -1):
            ns = ".".join(parts[:k])
            if ns in index.namespaces:
                toks.append((index.namespaces[ns], "type"))
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


def advise(text, scripts, have, index, named=None, build=None, saves=None, exclude=(), composer=None):
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
    plan that composed it).
    composer: mod folder -> the packageIds modcheck composes for it (default modcheck_composed); every one a proof's
    `modcheck/cli.py run <Mod>` would check in the running load is a sure need ("proof_modcheck")."""
    have = set(have)
    named = set(have if named is None else named)
    out, seen, memo = [], {}, {}
    # saves: {path: header text} of the fixture saves (.rws) the proof names: their <modIds> are the load they need
    pid_of = {v: k for k, v in index.repo_pids.items()}

    def res(tok):
        if tok not in memo:
            memo[tok] = resolve(tok, index, near=False)
        return memo[tok]

    def hit(mod, at, line, src, need=None):
        need = have if need is None else need
        if mod and mod not in need and index.repo_pids.get(mod) not in need and pid_of.get(mod) not in need \
                and not mod.startswith(BASE):
            entry = {"mod": mod, "at": at, "line": line.strip()[:160], "src": src}
            if mod not in seen:
                seen[mod] = len(out)
                out.append(entry)
            elif src in SURE and out[seen[mod]]["src"] not in SURE:     # the strongest evidence speaks for the mod
                out[seen[mod]] = entry

    def scan(path, body):
        for n, line in enumerate((body or "").splitlines(), 1):
            if path == PROOFS_DIR and re.match(r"^\s*(?:[-*]\s+)?`?live-(?:mods|deploy|without)\s*:", line):
                continue
            typed = set()
            for tok, src in _tokens(line, index, typed):
                r = res(tok)
                if r["kind"] in RESOLVED:
                    hit(r["canon"], "%s:%d" % (path, n), line, ("proof_" if path == PROOFS_DIR else "script_") + src,
                        named if src == "type" else None)
    for mod in sorted(build or ()):
        if mod in index.folded:
            hit(index.folded[mod][0], "build: %s" % mod, "the build's %s is folded into %s: the load holds that mod, "
                "not %s; name it" % (mod, index.folded[mod][0], mod), "folded", named)
    for path in proof_scripts(text):
        m = SRC_MOD.match(path)
        if m:
            r = resolve(m.group(1), index)
            if r["kind"] in RESOLVED:
                hit(r["canon"], "%s:0" % path, "the proof script lives in this mod", "script_home")
    for path, head in sorted((saves or {}).items()):
        for pid in save_mod_ids(head):
            r = res(pid)
            if r["kind"] in RESOLVED:
                hit(r["canon"], "%s:0" % path, "the fixture save was made with %s loaded" % pid, "fixture")
    scan(PROOFS_DIR, text)
    for mc in modcheck_runs(text):
        try:
            ids = (composer or modcheck_composed)(mc)
        except Exception as ex:  # noqa: BLE001 - an unknown mod or a broken tier speaks as a warning, never a crash
            hit(mc, "%s: modcheck run %s" % (PROOFS_DIR, mc), "modcheck cannot compose %s: %s: %s"
                % (mc, type(ex).__name__, ex), "proof_modcheck_unknown")
            continue
        for pid in ids:
            r = res(pid)
            if r["kind"] in RESOLVED:
                hit(r["canon"], "%s: modcheck run %s" % (PROOFS_DIR, mc), "modcheck run %s composes %s and refuses "
                    "the run (stale_load) unless the running load holds it" % (mc, pid), "proof_modcheck")
    for path, body in sorted((scripts or {}).items()):
        scan(path, body)
    # exclude: mods the proof is live-without; a closure is never walked from one (it would add what it hangs on)
    no = {pid_of.get(m, m) for m in exclude} | {index.repo_pids.get(str(m).lower(), m) for m in exclude}
    sure = {a["mod"] for a in out if a["src"] in SURE and a["mod"] not in no
            and index.repo_pids.get(str(a["mod"]).lower(), a["mod"]) not in no}
    for mod, dep, via in closure_gaps(have | sure, index):
        hit(dep, "About.xml of %s" % mod, "%s needs %s through %s; modlist_swap --enable adds only immediate "
                                         "dependencies of a folder" % (mod, dep, via), "closure")
    return out


MODIDS = re.compile(r"<modIds>(.*?)</modIds>", re.S)


def save_mod_ids(head):
    """A .rws header (its first bytes) -> the packageIds in <meta><modIds>, lower-case, in order."""
    m = MODIDS.search(head or "")
    return [x.strip().lower() for x in re.findall(r"<li>([^<]+)</li>", m.group(1))] if m else []


def proof_saves(text):
    """The fixture saves (*.rws) a proofs file's non-absence lines name, in order."""
    out = []
    for line in (text or "").splitlines():
        if ABSENT.search(STRIP_ABSENT.sub(" ", line)):
            continue
        for p in RWS.findall(line):
            if p not in out:
                out.append(p)
    return out


# A need from one of these is ENFORCED (added to the planned load before the slot): the proof says so itself (a --mod /
# --needs / --enable argument, a staging-cue line naming an installed mod), the proof script lives in the mod, the build's
# folded source is that composed mod, a fixture save was made with it, a C# type or one of our defNames has exactly one
# owner, a proof line runs `modcheck/cli.py run <Mod>` whose composed list holds it, or a resolved mod hard-depends on
# it. Everything else (a quoted name, a packageId in prose, a defName several mods define) only warns: a false positive
# costs a warning line, never an extra mod in someone's load.
SURE = ("folded", "script_home", "fixture", "proof_cli", "proof_cue", "proof_type", "script_type", "script_path",
        "proof_defname", "script_defname", "closure", "proof_modcheck")
INDEXED = ("proof_type", "script_type", "proof_defname", "script_defname", "closure")    # trust the index's age
def live_without(text):
    """A live_proofs file -> the names its `live-without:` lines give (every line, in order, no repeats): mods the proof
    INTENDS to run without (it measures their absence). A `# ...` tail is a comment."""
    import relentless_live_round as R
    return R.live_mods(text, R.LIVE_WITHOUT)


def _one(index):
    return lambda m: index.repo_pids.get(str(m).lower(), m)    # a repo packageId and its folder are one mod


def needs(text, scripts, named, build, index, saves=None):
    """LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: what the gate adds to a proof's planned load, derived each time and never
    written into the proof. text: the proofs file; scripts: gather_scripts; named: check(live_mods(text))["mods"]; build:
    the build's own mod folders. -> {"planned": the load (named + the build's mods normalised + "add"), "add": [advise
    dicts with "src" in SURE], "warn": [the rest, with "why" when a sure one was degraded], "without": the canonical mods
    of `live-without:`, "without_refused": [resolve dicts of names no mod has], "conflict": [planned mods the proof is
    live-without]}. Idempotent: the same inputs give the same answer, and a proof that names every addition gets none."""
    one = _one(index)
    wchk = check(live_without(text), index)
    without = set(wchk["mods"])
    without_id = {one(m) for m in without}
    bchk = check(sorted(build or ()), index)
    base = []       # what the gate plans already: live-mods and the build's own folders as derived (a folded source too)
    for m in list(named) + sorted(build or ()):
        if m not in base:
            base.append(m)
    base_id = {one(m) for m in base}
    adv = advise(text, scripts, set(named) | set(bchk["mods"]), index, named=list(named), build=build, saves=saves,
                 exclude=without)
    add, warn = [], []
    for a in adv:
        if one(a["mod"]) in base_id:
            continue        # a type of a build mod, say: planned already, no addition
        if one(a["mod"]) in without_id:
            warn.append(dict(a, why="live-without names it: never added"))
        elif a["src"] not in SURE:
            warn.append(a)
        elif a["src"] in INDEXED and index.stale_for(a["mod"]):
            warn.append(dict(a, why="index stale: %s" % index.stale_for(a["mod"])))
        else:
            add.append(a)
    planned = list(base)
    for a in add:
        if a["mod"] not in planned and one(a["mod"]) not in {one(m) for m in planned}:
            planned.append(a["mod"])
    conflict = [m for m in planned if one(m) in without_id]
    return {"planned": planned, "add": add, "warn": warn, "without": sorted(without),
            "without_refused": wchk["refused"], "conflict": conflict}


def read_head(path, n=262144):
    """The first n bytes of a repo file (a .rws header), as text; "" when unreadable."""
    try:
        with open(os.path.join(BOOKS, path), "rb") as f:
            return f.read(n).decode("utf-8", "replace")
    except OSError:
        return ""


def gather_saves(text, head=read_head):
    """{path: header} of the fixture saves a proofs file names, read with head(path) (unreadable ones left out)."""
    out = {}
    for p in proof_saves(text):
        h = head(p)
        if h:
            out[p] = h
    return out


def without_conflict(nd):
    """needs() -> one refusal line when the planned load holds a mod the proof is live-without, or names one no mod
    has, else None. Refused BEFORE the slot: staging only enables, so the load would hold it."""
    parts = []
    if nd["without_refused"]:
        parts.append("live-without names no mod this machine has: " + "; ".join(
            "%r %s" % (r["name"], r["why"]) for r in nd["without_refused"]))
    if nd["conflict"]:
        parts.append("live-without %s, but the planned load holds it (the build's mods or live-mods); staging only "
                     "enables, so this load cannot serve the proof" % ", ".join(nd["conflict"]))
    return "; ".join(parts) or None


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


# an addition outside the repair's own names is still right when its evidence states the need: a hard About.xml
# dependency, the composed mod the build's folded source loads as, the proof's own load condition (--needs X, --enable X,
# "Stager: the list ALSO needs X"), or the mod the proof script lives in
SELF_EVIDENT = ("closure", "folded", "proof_cli", "proof_cue", "script_home", "fixture", "proof_modcheck")


def _case_scripts(case):
    sc = case.get("scripts") or {}
    if isinstance(sc, str):     # an older fixture froze the dict's repr
        import ast
        sc = ast.literal_eval(sc)
    return sc


def enforce_case(case, index, also=()):
    """One frozen run -> needs() over it, scored: "miss" the repair-added mods the planned load still lacks, "wrong"
    additions neither the repair named nor SELF_EVIDENT, "add" every addition as mod@src."""
    import relentless_live_round as R
    one = _one(index)
    text = case.get("text") or ""
    named = check(R.live_mods(text), index)["mods"]
    nd = needs(text, _case_scripts(case), named, case.get("build_mods") or [], index)
    eff = {one(m) for m in nd["planned"]} | {one(m) for m in check(nd["planned"], index)["mods"]}
    truth = {one(m) for m in list(case.get("added") or []) + list(case.get("added_later") or []) + list(also)}
    return {"miss": [m for m in case.get("added") or [] if one(m) not in eff],
            "wrong": ["%s@%s" % (a["mod"], a["at"]) for a in nd["add"]
                      if one(a["mod"]) not in truth and a["src"] not in SELF_EVIDENT],
            "add": ["%s@%s" % (a["mod"], a["src"]) for a in nd["add"]], "conflict": nd["conflict"]}


def enforce_replay(fx, bar=17):
    """The enforcement replay (LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT criteria 1-2) -> (exit, report). An R1/R2 item is
    right when EVERY one of its failed runs, as frozen, would have had each mod its next repair added put in the planned
    load. Exit 0 only when at least `bar` R1/R2 items are right, no case or PASS proof gets a wrong addition, and no PASS
    proof is refused by its own live-without."""
    index = Index.from_json(fx["index"])
    items, wrong, pass_add, pass_refused = {}, [], [], []
    for case in fx["cases"]:
        if case["root"] not in ("R1", "R2"):
            continue
        got = enforce_case(case, index)
        it = items.setdefault(case["item"], {"right": True, "miss": [], "runs": 0})
        it["runs"] += 1
        it["right"] = it["right"] and not got["miss"]
        it["miss"] = sorted(set(it["miss"]) | set(got["miss"]))
        wrong += ["%s: %s" % (case["item"], w) for w in got["wrong"]]
    repaired = {}      # a PASS proof's item: what its own repairs named (a sibling clause failed without it)
    for case in fx["cases"]:
        repaired.setdefault(case["item"], set()).update((case.get("added") or []) + (case.get("added_later") or []))
    for case in fx["passes"]:
        got = enforce_case(case, index, repaired.get(case["item"], ()))
        wrong += ["PASS %s: %s" % (case["item"], w) for w in got["wrong"]]
        pass_add += ["%s: %s" % (case["item"], a) for a in got["add"]]
        if got["conflict"]:
            pass_refused.append(case["item"])
    right = sum(1 for v in items.values() if v["right"])
    rep = {"items": items, "right": "%d/%d" % (right, len(items)), "wrong": wrong, "pass_n": len(fx["passes"]),
           "pass_additions": pass_add, "pass_refused": pass_refused, "bar": bar}
    return (0 if right >= bar and not wrong and not pass_refused else 1), rep


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
    p = sub.add_parser("check", help="resolve an item's live-mods names; refusals exit 1, the gate's additions and "
                                     "advice are printed")
    p.add_argument("--item", required=True)
    p = sub.add_parser("replay", help="the census replay over a frozen fixture")
    p.add_argument("--fixture", required=True)
    p.add_argument("--enforce", action="store_true", help="score the enforced needs (criteria 1-2) instead of advice")
    p.add_argument("--report", help="write the whole report here")
    p = sub.add_parser("extract", help="freeze the census and the last PASS proofs into a fixture (needs git)")
    p.add_argument("--census", required=True, help="json: [{item, root[, sha][, text, rider_of]}]")
    p.add_argument("--runs", default="/home/mandrake/rm/relentless/live/runs.jsonl")
    p.add_argument("--out", required=True)
    p = sub.add_parser("migrate", help="every live_proofs file: what the gate would add, warn and refuse (read only)")
    p.add_argument("--out", help="write the list (json) here")
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
    if a.cmd == "migrate":
        import relentless_live_round as R
        index = default_index()
        d = os.path.join(BOOKS, PROOFS_DIR)
        rows = []
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".txt") or fn.count(".") > 1:     # <ID>.<kind>.txt is a proof's data, not a proof
                continue
            with open(os.path.join(d, fn), encoding="utf-8", errors="replace") as f:
                text = f.read()
            chk = check(R.live_mods(text), index)
            nd = needs(text, gather_scripts(text, read_books), chk["mods"], [], index, saves=gather_saves(text))
            rows.append({"item": fn[:-4], "named": chk["mods"], "without": nd["without"],
                         "add": [{k: x[k] for k in ("mod", "src", "at", "line")} for x in nd["add"]],
                         "warn": len(nd["warn"]), "conflict": without_conflict(nd)})
            for x in nd["add"]:
                print("ADD %s %s (%s %s)" % (fn[:-4], x["mod"], x["src"], x["at"]))
            if rows[-1]["conflict"]:
                print("CONFLICT %s: %s" % (fn[:-4], rows[-1]["conflict"]))
        if a.out:
            with open(a.out, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=1, sort_keys=True)
        print("%d proofs, %d with additions, %d additions, %d conflicts" % (
            len(rows), sum(1 for r in rows if r["add"]), sum(len(r["add"]) for r in rows),
            sum(1 for r in rows if r["conflict"])))
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
        nd = needs(text, scripts, chk["mods"], [], index, saves=gather_saves(text))
        for adv in nd["add"]:
            print("ADDED AT THE GATE (derived, not written into the proof) %s [%s]: %s  %s" % (
                adv["mod"], adv["src"], adv["at"], adv["line"]))
        for adv in nd["warn"]:
            print("ADVICE (not added, not written) %s may be needed%s: %s  %s" % (
                adv["mod"], (" (%s)" % adv["why"]) if adv.get("why") else "", adv["at"], adv["line"]))
        why = "; ".join(x for x in (refusal(chk["refused"]), without_conflict(nd)) if x) or None
        print(why or "OK %s names %s" % (a.item, ", ".join(chk["mods"]) or "no mods"))
        return 1 if why else 0
    if a.cmd == "replay":
        with open(a.fixture, encoding="utf-8") as f:
            fx = json.load(f)
        if a.enforce:
            code, rep = enforce_replay(fx)
            if a.report:
                with open(a.report, "w", encoding="utf-8") as f:
                    json.dump(rep, f, indent=1, sort_keys=True)
            print("ENFORCE R1/R2 items right %s (bar %d)  wrong additions %d  PASS proofs %d: additions %d (none "
                  "wrong unless listed), refused by live-without %d  -> %s" % (
                rep["right"], rep["bar"], len(rep["wrong"]), rep["pass_n"], len(rep["pass_additions"]),
                len(rep["pass_refused"]), "OK" if code == 0 else "FAIL"))
            for item, it in sorted(rep["items"].items()):
                if not it["right"]:
                    print("  missed %s: the planned load still lacks %s" % (item, ", ".join(it["miss"])))
            for w in rep["wrong"]:
                print("  WRONG addition %s" % w)
            return code
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
