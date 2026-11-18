"""mod_names.py -- the one resolver for the mod names a live_proofs file gives (`live-mods:` / `live-deploy:`).

Moved verbatim from rimflow/relentless_names.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
FOLDERISH = ("folder", "composed", "folded")
PATHISH = re.compile(r"[/\\]|\.(?:xml|txt|json|py|md|rws)$", re.I)
CORE = "ludeon.rimworld"


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
