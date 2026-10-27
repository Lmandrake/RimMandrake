#!/usr/bin/env python3
"""leftovers.py -- archive-then-delete OUR OWN leftovers, only after a check proves nothing reads them.

    python3 src/RimMandrake/Utils/leftovers.py scan  [--kind K ...] [--md OUT.md] [--tsv OUT.tsv]
    python3 src/RimMandrake/Utils/leftovers.py check   <path> [--json]
    python3 src/RimMandrake/Utils/leftovers.py archive <path>
    python3 src/RimMandrake/Utils/leftovers.py delete  <path> [--item ID] [--no-ledger]
    python3 src/RimMandrake/Utils/leftovers.py retire  <path> [--item ID] [--no-ledger]   (archive, then delete)

Delegation: owner card 2026-10-26 19:06, "Archive then delete, in digest (Recommended)"
(canon.yml `leftovers_archive_then_delete_delegated`, delegation_policy.md section 2.2,
item LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE). Anything not OURS, or not proven unread AND pushed, stays his.

Kinds and what `check` must prove (every reason below is a NOT-SAFE reason; SAFE needs none of them):

  save     a dev savegame (Saves/*.rws, or a Saves_backup_*/Saves_archive_* folder). Ours = an agent name
           prefix (SAVE_PREFIXES). Never canonical: the canon.yml start_savegame, CANONICAL_SAVE.md's file and
           anything named CANONICAL*/ASHKARR_DEV* (or a folder holding one) is REFUSED outright. Read = its name
           appears in any tracked repo file (items, docs, scenes), or it is a review save (an unjudged review
           save counts as read), or it is younger than --min-age-days.
  clone    a scratch git clone under CLONE_ROOTS whose origin is this repo's origin. Read/unpushed = dirty or
           untracked files, a stash, a merge/rebase in progress, extra worktrees, any local commit not on a
           remote ref and not patch-equivalent to this repo's origin/main, a live process with its cwd inside,
           or git activity younger than --min-age-days.
  modfolder a folder in the game Mods dir whose About.xml packageId starts `mandrake.`. Read = that packageId
           is active in ModsConfig.xml (parsed), listed in a canonical save's mod list, or named anywhere in the
           repo (About.xml in src, test tier lists, docs).
  setting  a Config file of ours: Mod_<Folder>_<Class>.xml[.bak*] for a mod folder of ours, or an agent-made
           ModsConfig backup. Read = it is a live settings file of a deployed folder, or its filename is named
           in the repo.
  picture  a PNG under a Textures/ folder of ours (repo src, or a deployed mandrake mod with no repo copy).
           Read = its texture path (or a prefix ending at / _ - or a digit: Graphic_Multi/Random/mask
           variants) appears in any XML or C# of ours, any deployed mod XML, or the newest def dump; a UI/ path
           cannot be cleared (it may override a vanilla ContentFinder texture by path).
  patch    a Patches/*.xml of ours that names a retired mod. SAFE only if EVERY top-level Operation is a
           PatchOperationFindMod whose mods are ALL retired (retired_mods.json) and which has no <nomatch>.

Repo files (picture, patch) must also be tracked, unmodified and identical on origin/main ("everything is
pushed"). Every 0-reference verdict is backed by a sanity probe: the same instrument, pointed at a reference
known to exist, must find it -- if the probe fails the verdict is UNMEASURED, never SAFE.

archive  writes <agent storage>/backups/leftovers/<date>/<kind>__<name>.(tar.gz|bundle) plus a .manifest.json
         (per-file sha256, or the bundle's refs). Agent storage comes from `agent_storage.py` (override:
         LEFTOVERS_ARCHIVE_ROOT).
delete   refuses unless check is SAFE now AND an archive for this exact path exists and verifies against the
         path as it is now. Then deletes, appends acts.jsonl beside the archives, and logs a rimflow note with
         --why "delegated: leftovers ..." so the daily digest lists it (delegation_policy section 5).
"""

import argparse
import datetime as _dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

KINDS = ("save", "clone", "modfolder", "setting", "picture", "patch")
SAFE, NOT_SAFE, REFUSED, UNMEASURED = "SAFE", "NOT-SAFE", "REFUSED", "UNMEASURED"

# Agent-made save names. Anything else in Saves is not provably ours and is refused.
SAVE_PREFIXES = ("RM_", "NS_", "BENCH_", "FOUNDRY_", "rimbridge_save_", "FWSWEEP_", "FOUNDER_",
                 "LIVEVERIFY_", "REHEARSAL_", "PYRE_WALK", "BLAND_NORTHSTAR", "XENOTYPE_SKIN_REVIEW",
                 "XENO_HEADS_REVIEW", "PYRELANDS_REVIEW", "SCALD_REVIEW", "FLOWWORKS_OWNER_REVIEW",
                 "FLIGHT_")
CANONICAL_MARKS = ("CANONICAL", "ASHKARR_DEV")
REVIEW_MARK = re.compile(r"review", re.I)
TOKEN = re.compile(r"[\w\-.]+(?:/[\w\-.]+)+/?")
# A texPath with NO slash ("gamorreanaxe") names a file/folder at the Textures root: TOKEN cannot see it.
# BARE_XML takes the text of an element whose tag names a path/texture/icon/graphic/mask; BARE_JSON the same for
# a def-dump key; CS_LIT any C# string literal. Bare tokens can clear only Textures-root files (and, from XML/dump,
# Textures-root folders) -- a bare word never vouches for a deeper path.
BARE_MARK = "\x00bare:"
BARE_XML = re.compile(r"<([A-Za-z_][\w.]*)(?:\s[^<>]*)?>\s*([\w\-.]+)\s*</\1\s*>")
BARE_JSON = re.compile(r'"(\w+)"\s*:\s*"([\w\-.]+)"')
CS_LIT = re.compile(r'"([\w\-.]+)"')
PATHISH = ("path", "tex", "icon", "graphic", "image", "sprite")  # not "mask": placementMask is an enum


def _pathish(tag):
    t = tag.lower()
    return any(k in t for k in PATHISH) and not t.endswith("class")


def _tok(t):
    """A composed C# path ("Debris/RM_ScorchDebris_" + i) names every file after its trailing separator."""
    return t.lower().strip("/").rstrip("_-")


def bare_from_xml(txt):
    return {m.group(2).lower() for m in BARE_XML.finditer(txt) if _pathish(m.group(1))}


def _now():
    return time.time()


def _sha256(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _run(cmd, cwd=None, env=None, timeout=300):
    p = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=timeout)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def _git(repo, *args, env=None, timeout=300):
    env = dict(env if env is not None else os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"     # a check must not refresh (write) the index it is judging
    return _run(["git", "-C", repo] + list(args), env=env, timeout=timeout)


def _size(path):
    if os.path.isfile(path) or os.path.islink(path):
        return os.lstat(path).st_size
    rc, out, _ = _run(["du", "-sb", path], timeout=300)
    if rc == 0 and out.split():
        return int(out.split()[0])
    tot = 0
    for d, _dirs, files in os.walk(path):
        for f in files:
            try:
                tot += os.lstat(os.path.join(d, f)).st_size
            except OSError:
                pass
    return tot


def _newest_mtime(path, limit=20000):
    if os.path.isfile(path):
        return os.stat(path).st_mtime
    newest, n = 0.0, 0
    for d, dirs, files in os.walk(path):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in files:
            n += 1
            try:
                newest = max(newest, os.lstat(os.path.join(d, f)).st_mtime)
            except OSError:
                pass
            if n > limit:
                return newest
    return newest or os.stat(path).st_mtime


def _inside(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root.rstrip("/") + "/")


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.1f %s" % (n, unit) if unit != "B" else "%d B" % n
        n /= 1024.0


def default_archive_root():
    env = os.environ.get("LEFTOVERS_ARCHIVE_ROOT")
    if env:
        return env
    tool = os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")
    rc, out, err = _run([sys.executable, tool], timeout=60)
    base = out.strip()
    if rc != 0 or not base:
        raise SystemExit("leftovers: cannot read agent storage from %s: %s" % (tool, err.strip()))
    return os.path.join(base, "backups", "leftovers")


class Ctx(object):
    """Every root the tool reads. Defaults are the live machine; tests pass fixture roots."""

    def __init__(self, repo=None, saves=None, config=None, mods=None, clone_roots=None, archive_root=None,
                 dump=None, retired=None, canon_saves=None, min_age_days=7.0, clone_min_age_days=2.0):
        self.repo = repo or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
        if saves is None or config is None or mods is None:
            import game_paths as gp
            saves = saves or gp.SAVES
            config = config or os.path.join(gp.LOCALLOW, "Config")
            mods = mods or gp.LOCAL_MODS
            if dump is None:
                dump = gp.DEF_DUMP
        self.saves, self.config, self.mods = saves, config, mods
        self.userdata = os.path.dirname(saves.rstrip("/"))
        self.dump = dump or ""
        self.clone_roots = clone_roots if clone_roots is not None else [
            "/home/mandrake/rm/scratch", "/mnt/d/ClaudeWork/rimmandrake"]
        self._archive_root = archive_root
        self.min_age = min_age_days * 86400
        self.clone_min_age = clone_min_age_days * 86400
        self._retired = retired
        self._canon_saves = canon_saves
        self._cache = {}

    # ---------- shared facts ----------
    @property
    def archive_root(self):
        if self._archive_root is None:
            self._archive_root = default_archive_root()
        return self._archive_root

    def retired(self):
        if self._retired is None:
            import retired_mods
            ents = retired_mods.entries()
            s = set()
            for e in ents:
                if e.get("packageId"):
                    s.add(e["packageId"].strip().lower())
                for n in e.get("modNames") or []:
                    s.add(n.strip().lower())
            self._retired = s
        return self._retired

    def canon_save_names(self):
        """Save file names that are canonical, read from canon.yml + CANONICAL_SAVE.md (never guessed)."""
        if self._canon_saves is None:
            names = set()
            for rel in ("infrastructure/state/canon.yml", "infrastructure/state/CANONICAL_SAVE.md"):
                p = os.path.join(self.repo, rel)
                if os.path.exists(p):
                    txt = io.open(p, encoding="utf-8", errors="replace").read()
                    for m in re.finditer(r"start_savegame:\s*(\S+\.rws)", txt):
                        names.add(m.group(1))
                    for m in re.finditer(r"\*\*File\*\*:\s*`([^`]+\.rws)`", txt):
                        names.add(m.group(1))
            self._canon_saves = names
        return self._canon_saves

    def origin_url(self):
        if "origin" not in self._cache:
            rc, out, _ = _git(self.repo, "config", "--get", "remote.origin.url")
            self._cache["origin"] = out.strip() if rc == 0 else ""
        return self._cache["origin"]

    def origin_main(self):
        if "origin_main" not in self._cache:
            sha = ""
            for ref in ("refs/remotes/origin/main", "refs/heads/main", "HEAD"):
                rc, out, _ = _git(self.repo, "rev-parse", "--verify", "-q", ref)
                if rc == 0 and out.strip():
                    sha = out.strip()
                    break
            self._cache["origin_main"] = sha
        return self._cache["origin_main"]

    def git_grep_files(self, needle):
        """Tracked repo files naming `needle` (fixed string, case-insensitive)."""
        rc, out, _ = _git(self.repo, "grep", "-I", "-l", "-i", "-F", "-e", needle, "--", ".", timeout=300)
        return [l for l in out.splitlines() if l] if rc in (0, 1) else None

    def repo_pids(self):
        if "pids" not in self._cache:
            rc, out, _ = _git(self.repo, "ls-files", "--", "*About/About.xml")
            pids = {}
            for rel in out.splitlines():
                pid = read_pid(os.path.join(self.repo, rel))
                if pid:
                    pids[pid.lower()] = rel
            self._cache["pids"] = pids
        return self._cache["pids"]

    def active_pids(self):
        if "active" not in self._cache:
            out = set()
            p = os.path.join(self.config, "ModsConfig.xml")
            if os.path.exists(p):
                root = ET.parse(p).getroot()
                for li in root.findall("./activeMods/li"):
                    if li.text:
                        out.add(li.text.strip().lower())
            self._cache["active"] = out
        return self._cache["active"]

    def canon_save_pids(self):
        if "canonpids" not in self._cache:
            from modsconfig_from_save import mod_list
            out, seen = set(), []
            for name in sorted(self.canon_save_names()):
                p = os.path.join(self.saves, name)
                if os.path.exists(p):
                    seen.append(name)
                    out |= {x.strip().lower() for x in mod_list(p)["modIds"]}
            self._cache["canonpids"] = (out, seen)
        return self._cache["canonpids"]

    def deployed(self):
        """{folder name: packageId(lower) or None} for the game Mods dir."""
        if "deployed" not in self._cache:
            d = {}
            if os.path.isdir(self.mods):
                for name in sorted(os.listdir(self.mods)):
                    full = os.path.join(self.mods, name)
                    if os.path.isdir(full):
                        pid = read_pid(os.path.join(full, "About", "About.xml"))
                        d[name] = pid.lower() if pid else None
            self._cache["deployed"] = d
        return self._cache["deployed"]

    def our_mod_folders(self):
        """Folder names that are ours: deployed mandrake.* folders and repo mod dirs with an About.xml."""
        s = {n for n, p in self.deployed().items() if p and p.startswith("mandrake.")}
        for rel in self.repo_pids().values():
            s.add(rel.split("/")[-3])
        return s

    # ---------- picture references ----------
    def ref_tokens(self):
        """Lower-case path-like strings from every XML/C# of ours, deployed mod XML, and the def dump."""
        if "tokens" in self._cache:
            return self._cache["tokens"]
        toks, bdir, bfile = set(), set(), set()
        rc, out, _ = _git(self.repo, "ls-files", "--", "*.xml", "*.cs")
        for rel in out.splitlines():
            if not rel.startswith("src/"):
                continue
            try:
                txt = io.open(os.path.join(self.repo, rel), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            toks.update(_tok(t) for t in TOKEN.findall(txt))
            if rel.endswith(".xml"):
                bdir.update(bare_from_xml(txt))
            else:
                bfile.update(m.lower() for m in CS_LIT.findall(txt))
        for name in self.deployed():
            for d, _dirs, files in os.walk(os.path.join(self.mods, name)):
                for f in files:
                    if f.lower().endswith(".xml"):
                        try:
                            txt = io.open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
                        except OSError:
                            continue
                        toks.update(_tok(t) for t in TOKEN.findall(txt))
                        bdir.update(bare_from_xml(txt))
        dump = self.dump_tokens()
        toks |= {t for t in dump if not t.startswith(BARE_MARK)}
        bdir |= {t[len(BARE_MARK):] for t in dump if t.startswith(BARE_MARK)}
        toks.discard("")
        bdir.discard("")
        self._cache["tokens"] = toks
        self._cache["bare"] = (bdir, bfile | bdir)
        return toks

    def bare_tokens(self):
        """(folder-or-file names from path-like XML/dump fields, file names also from C# literals), lower-case."""
        self.ref_tokens()
        return self._cache["bare"]

    def dump_tokens(self):
        if not self.dump or not os.path.isdir(self.dump):
            return set()
        cache_dir = os.environ.get("LEFTOVERS_CACHE", "/mnt/d/ClaudeWork/rimmandrake/leftovers/cache")
        cache = os.path.join(cache_dir, "dump_tokens_v3_%s.txt" % os.path.basename(self.dump.rstrip("/")))
        if os.path.exists(cache):
            return set(io.open(cache, encoding="utf-8").read().split("\n"))
        toks = set()
        for d, _dirs, files in os.walk(self.dump):
            for f in files:
                if f.endswith(".json"):
                    txt = io.open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
                    toks.update(_tok(t) for t in TOKEN.findall(txt.replace("\\/", "/")))
                    toks.update(BARE_MARK + m.group(2).lower() for m in BARE_JSON.finditer(txt)
                                if _pathish(m.group(1)))
        try:
            os.makedirs(cache_dir, exist_ok=True)
            io.open(cache, "w", encoding="utf-8").write("\n".join(sorted(toks)))
        except OSError:
            pass
        return toks


def read_pid(about):
    if not os.path.exists(about):
        return None
    try:
        txt = io.open(about, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return None
    m = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", txt, re.I)
    return m.group(1) if m else None


def tex_rel(path):
    """'.../Textures/Things/Foo/Bar_north.png' -> 'things/foo/bar_north' (lower)."""
    p = path.replace("\\", "/")
    i = p.lower().rfind("/textures/")
    if i < 0:
        return None
    return os.path.splitext(p[i + len("/textures/"):])[0].lower()


def tex_referenced(rel, toks, bare=None):
    """A texture is referenced by its own path or by a prefix ending at a variant boundary. `bare` =
    ctx.bare_tokens(): slashless texPaths, which can only name a Textures-root file or (dir set) folder."""
    if rel in toks:
        return rel
    for i in range(3, len(rel)):
        if rel[i] in "/_-" or rel[i].isdigit() or rel[i - 1] == "/":
            if rel[:i] in toks:
                return rel[:i]
    if bare:
        bdir, bfile = bare
        if "/" in rel:
            top = rel.split("/", 1)[0]
            return top if top in bdir else None
        return tex_referenced(rel, bfile)
    return None


def classify_patch(path, retired):
    """-> (aimed_only_at_retired: bool, detail). Strict: every top-level Operation must be a FindMod of
    retired mods only, with no <nomatch> (nomatch fires exactly when the mod is absent, i.e. is live)."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return False, "unparseable XML: %s" % e
    ops = [c for c in root if c.tag == "Operation"]
    if not ops:
        return False, "no top-level Operation"
    for op in ops:
        cls = op.get("Class", "")
        if not cls.endswith("PatchOperationFindMod"):
            return False, "top-level Operation %s is not a FindMod" % cls
        if op.find("nomatch") is not None:
            return False, "FindMod has <nomatch> (live when the mod is absent)"
        mods = [li.text.strip() for li in op.findall("./mods/li") if li.text and li.text.strip()]
        if not mods:
            return False, "FindMod lists no mods"
        live = [m for m in mods if m.lower() not in retired]
        if live:
            return False, "FindMod names a live mod: %s" % ", ".join(live)
    return True, "%d FindMod op(s), all aimed at retired mods" % len(ops)


# ======================================================================================== kind detection
def kind_of(ctx, path):
    p = os.path.realpath(path)
    if _inside(p, ctx.saves) and p.lower().endswith(".rws"):
        return "save"
    if os.path.dirname(p) == os.path.realpath(ctx.userdata) and re.match(r"Saves_(backup|archive)",
                                                                          os.path.basename(p)):
        return "save"
    if _inside(p, ctx.config) and os.path.isfile(p):
        return "setting"
    if p.lower().endswith(".png") and "/textures/" in p.lower():
        return "picture"
    if p.lower().endswith(".xml") and "/patches/" in p.lower():
        return "patch"
    if os.path.dirname(p) == os.path.realpath(ctx.mods) and os.path.isdir(p):
        return "modfolder"
    if os.path.isdir(os.path.join(p, ".git")):
        return "clone"
    return None


def owner_of_mod_path(ctx, p):
    """For a path inside the game Mods dir: (folder, pid) of its mod folder."""
    rel = os.path.relpath(os.path.realpath(p), os.path.realpath(ctx.mods))
    folder = rel.split(os.sep)[0]
    return folder, ctx.deployed().get(folder)


def repo_file_pushed(ctx, p):
    """None if the repo file is tracked, clean and identical on origin/main; else the reason."""
    rel = os.path.relpath(os.path.realpath(p), os.path.realpath(ctx.repo))
    rc, out, _ = _git(ctx.repo, "ls-files", "--error-unmatch", "--", rel)
    if rc != 0:
        return "not tracked in git (nothing pushed)"
    rc, out, _ = _git(ctx.repo, "status", "--porcelain", "--", rel)
    if out.strip():
        return "modified in the working tree"
    om = ctx.origin_main()
    rc, _o, _e = _git(ctx.repo, "diff", "--quiet", om, "--", rel)
    if rc != 0:
        return "differs from origin/main (unpushed)"
    return None


# ======================================================================================== checks
class Verdict(object):
    def __init__(self, path, kind):
        self.path, self.kind = path, kind
        self.status = SAFE
        self.reasons, self.evidence = [], []
        self.size = 0

    def no(self, reason):
        if self.status == SAFE:
            self.status = NOT_SAFE
        self.reasons.append(reason)

    def refuse(self, reason):
        self.status = REFUSED
        self.reasons.append(reason)

    def blind(self, reason):
        if self.status in (SAFE, NOT_SAFE):
            self.status = UNMEASURED
        self.reasons.append(reason)

    def as_dict(self):
        return {"path": self.path, "kind": self.kind, "verdict": self.status, "reasons": self.reasons,
                "evidence": self.evidence, "size": self.size}


def probe_repo_grep(ctx, v):
    """The repo reference search must see a reference known to exist: a canonical save name."""
    names = sorted(ctx.canon_save_names())
    if not names:
        v.blind("probe: no canonical save name readable from canon.yml/CANONICAL_SAVE.md")
        return False
    hits = ctx.git_grep_files(os.path.splitext(names[0])[0])
    if not hits:
        v.blind("probe: git grep could not see known reference %r" % names[0])
        return False
    v.evidence.append("probe: git grep sees %r in %d file(s)" % (names[0], len(hits)))
    return True


def check_save(ctx, p, v):
    name = os.path.basename(p)
    canon = ctx.canon_save_names()
    if name in canon or any(m in name.upper() for m in CANONICAL_MARKS) or name.split(".rws")[0] + ".rws" in canon:
        return v.refuse("canonical save (or a copy/derivative of one): never a leftover")
    if os.path.isdir(p):
        if not re.match(r"Saves_(backup|archive)", name):
            return v.refuse("not a save backup folder of ours")
        for d, _dirs, files in os.walk(p):
            for f in files:
                if f in canon or any(m in f.upper() for m in CANONICAL_MARKS):
                    return v.refuse("folder holds a canonical save copy (%s)" % f)
    elif not name.lower().startswith(tuple(x.lower() for x in SAVE_PREFIXES)):
        return v.refuse("save name has no agent prefix: not provably ours")
    if not probe_repo_grep(ctx, v):
        return
    stem = name[:-4] if name.lower().endswith(".rws") else name
    hits = ctx.git_grep_files(stem)
    if hits is None:
        return v.blind("git grep failed")
    if hits:
        v.no("named in %d repo file(s): %s" % (len(hits), ", ".join(hits[:3])))
    else:
        v.evidence.append("0 repo files name %r" % stem)
    if REVIEW_MARK.search(name):
        v.no("review save: counts as read until he has judged it")
    age = _now() - _newest_mtime(p)
    if age < ctx.min_age:
        v.no("younger than %.0f days (%.1f d)" % (ctx.min_age / 86400, age / 86400))


def _proc_cwds():
    out = []
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                out.append(os.readlink("/proc/%s/cwd" % pid))
            except OSError:
                pass
    return out


def check_clone(ctx, p, v):
    rp = os.path.realpath(p)
    if not any(_inside(rp, r) and rp != os.path.realpath(r) for r in ctx.clone_roots):
        return v.refuse("not under a scratch clone root of ours (%s)" % ", ".join(ctx.clone_roots))
    if _inside(ctx.repo, rp) or _inside(rp, ctx.repo):
        return v.refuse("this is (or holds) the working clone itself")
    rc, url, _ = _git(p, "config", "--get", "remote.origin.url")
    url = url.strip()
    ours = ctx.origin_url()
    if not url or not ours or url.rstrip("/").removesuffix(".git") != ours.rstrip("/").removesuffix(".git"):
        return v.refuse("origin %r is not this repo's origin: not ours" % url)
    gd = os.path.join(p, ".git")
    # HEAD/reflog only: the index mtime moves whenever anyone runs `git status`
    # there (a read), so it is not evidence of work; dirty work is caught below.
    act = max([os.stat(os.path.join(gd, f)).st_mtime for f in ("HEAD", "logs/HEAD")
               if os.path.exists(os.path.join(gd, f))] or [_now()])
    age = _now() - act
    if age < ctx.clone_min_age:
        v.no("git activity %.1f h ago (< %.0f d)" % (age / 3600, ctx.clone_min_age / 86400))
    rc, st, err = _git(p, "status", "--porcelain", "--untracked-files=all")
    if rc != 0:
        return v.blind("git status failed: %s" % err.strip()[:200])
    if st.strip():
        v.no("%d dirty/untracked path(s)" % len(st.splitlines()))
    # ignored files: the bundle keeps refs only, so an ignored file (a local .env, data, notes) would be lost
    rc, ign, err = _git(p, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory")
    if rc != 0:
        return v.blind("git ls-files --ignored failed: %s" % err.strip()[:200])
    ign = [l for l in ign.splitlines() if l.strip() and "__pycache__" not in l and not l.endswith(".pyc")]
    if ign:
        v.no("%d ignored path(s) the bundle would not keep (e.g. %s)" % (len(ign), ign[0]))
    rc, stash, _ = _git(p, "stash", "list")
    if stash.strip():
        v.no("%d stash entr(ies)" % len(stash.splitlines()))
    gd = os.path.join(p, ".git")
    for marker in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD", "BISECT_LOG"):
        if os.path.exists(os.path.join(gd, marker)):
            v.no("operation in progress (%s)" % marker)
    rc, wt, _ = _git(p, "worktree", "list", "--porcelain")
    if wt.count("worktree ") > 1:
        v.no("has extra worktrees")
    # unpushed: commits on any local branch, tag or HEAD not on any remote ref ...
    rc, out, err = _git(p, "rev-list", "HEAD", "--branches", "--tags", "--not", "--remotes")
    if rc != 0:
        return v.blind("rev-list failed: %s" % err.strip()[:200])
    unpushed = [s for s in out.split() if s]
    if unpushed:
        # ... and not patch-equivalent to this repo's origin/main (publish rebases, so shas change).
        om = ctx.origin_main()
        env = dict(os.environ)
        alt = os.path.join(ctx.repo, ".git", "objects")
        env["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = alt + (":" + env["GIT_ALTERNATE_OBJECT_DIRECTORIES"]
                                                         if env.get("GIT_ALTERNATE_OBJECT_DIRECTORIES") else "")
        rc, heads, _ = _git(p, "for-each-ref", "--format=%(objectname)", "refs/heads")
        rc, tags, _ = _git(p, "for-each-ref", "--format=%(objectname) %(*objectname)", "refs/tags")
        tips = set(heads.split()) | {_git(p, "rev-parse", "HEAD")[1].strip()} | {
            l.split()[-1] for l in tags.splitlines() if l.strip()}
        plus = set()
        for tip in sorted(t for t in tips if t):
            rc, ch, err = _git(p, "cherry", om, tip, env=env, timeout=300)
            if rc != 0:
                return v.blind("git cherry against origin/main failed: %s" % err.strip()[:200])
            plus |= {l[2:].strip() for l in ch.splitlines() if l.startswith("+ ")}
        real = [s for s in unpushed if s in plus]
        if real:
            v.no("%d commit(s) not on any remote and not on origin/main (e.g. %s)" % (len(real), real[0][:10]))
        else:
            v.evidence.append("%d local-only sha(s), all patch-equivalent on origin/main" % len(unpushed))
    else:
        v.evidence.append("every local commit is on a remote ref")
    for cwd in _proc_cwds():
        if _inside(cwd, rp):
            v.no("a live process has its cwd inside (%s)" % cwd)
            break


def check_modfolder(ctx, p, v):
    pid = read_pid(os.path.join(p, "About", "About.xml"))
    if not pid or not pid.lower().startswith("mandrake."):
        return v.refuse("packageId %r is not mandrake.*: not ours" % pid)
    pid = pid.lower()
    # probes: each instrument must see a known mandrake packageId
    repo = ctx.repo_pids()
    act = ctx.active_pids()
    cpids, cseen = ctx.canon_save_pids()
    if not repo:
        return v.blind("probe: no About.xml packageId readable in the repo")
    known = sorted(repo)[0]
    hits = ctx.git_grep_files(known)
    if not hits:
        return v.blind("probe: git grep cannot see known packageId %s" % known)
    if not any(x.startswith("mandrake.") for x in act):
        return v.blind("probe: ModsConfig.xml parsed to no mandrake.* id (blind or wrong file)")
    if not cseen:
        v.blind("probe: no canonical save readable for its mod list")
        return
    if not any(x.startswith("mandrake.") for x in cpids):
        return v.blind("probe: canonical save mod list holds no mandrake.* id")
    v.evidence.append("probes: %d repo pids, git grep sees %s, %d active, canon saves %s" % (
        len(repo), known, len(act), ",".join(cseen)))
    if pid in repo:
        v.no("packageId has source in the repo (%s): deployed copy, not an orphan" % repo[pid])
    if pid in act:
        v.no("active in ModsConfig.xml")
    if pid in cpids:
        v.no("in a canonical save's mod list")
    hits = ctx.git_grep_files(pid)
    if hits:
        v.no("named in %d repo file(s): %s" % (len(hits), ", ".join(hits[:3])))


def check_setting(ctx, p, v):
    name = os.path.basename(p)
    m = re.match(r"Mod_(.+?)_([A-Za-z_][\w]*?)\.xml(\..*)?$", name)
    is_backup_mc = bool(re.match(r"ModsConfig\..+", name)) and name != "ModsConfig.xml"
    if m and not m.group(1).isdigit():
        folder, cls, bak = m.group(1), m.group(2), m.group(3)
        # Mod_<Folder>_<Class>.xml: a folder name may itself hold '_' -- consider every split, prefer a real folder
        stem = name[len("Mod_"):name.lower().index(".xml")]
        splits = [(stem[:i], stem[i + 1:]) for i in range(1, len(stem) - 1) if stem[i] == "_"]
        for f_, c_ in splits:
            if f_ in ctx.deployed() or f_ in ctx.our_mod_folders():
                folder, cls = f_, c_
                break
        live = [f_ for f_, _c in splits if f_ in ctx.deployed()]
        if not bak and live:
            v.no("live settings file of deployed mod folder %s" % live[0])
        ours = folder in ctx.our_mod_folders()
        if not ours:
            rc, out, _ = _git(ctx.repo, "grep", "-l", "-E", r"class\s+%s\b" % re.escape(cls), "--", "*.cs")
            ours = bool(out.strip())
        if not ours:
            # a mod of ours since retired: its About.xml once lived in the repo
            rc, out, _ = _git(ctx.repo, "log", "--all", "-1", "--format=%h", "--",
                              "src/*/%s/About/About.xml" % folder)
            ours = bool(out.strip())
            if ours:
                v.evidence.append("folder %s had an About.xml in repo history (%s)" % (folder, out.strip()))
        if not ours:
            return v.refuse("settings of folder %r / class %r: not provably ours" % (folder, cls))
    elif not is_backup_mc:
        return v.refuse("not a settings file of ours")
    if not probe_repo_grep(ctx, v):
        return
    hits = ctx.git_grep_files(name)
    if hits:
        v.no("named in %d repo file(s): %s" % (len(hits), ", ".join(hits[:3])))
    else:
        v.evidence.append("0 repo files name %r" % name)
    age = _now() - os.stat(p).st_mtime
    if age < ctx.min_age:
        v.no("younger than %.0f days" % (ctx.min_age / 86400))


def _picture_owner(ctx, p, v):
    rp = os.path.realpath(p)
    if _inside(rp, os.path.join(ctx.repo, "src")):
        return "repo"
    if _inside(rp, ctx.mods):
        folder, pid = owner_of_mod_path(ctx, rp)
        if pid and pid.startswith("mandrake."):
            return "deployed"
        v.refuse("in mod folder %s (packageId %r): not ours" % (folder, pid))
        return None
    v.refuse("not under repo src/ or a deployed mandrake mod")
    return None


def picture_probe(ctx, v):
    """The reference set must see a texPath that a repo def is known to use."""
    if "picprobe" not in ctx._cache:
        rc, out, _ = _git(ctx.repo, "grep", "-h", "-o", "-m1", "-E", r"<texPath>[^<]+</texPath>", "--",
                          "src/*.xml")
        known = None
        for line in out.splitlines():
            known = re.sub(r"</?texPath>", "", line).strip().lower()
            if known:
                break
        toks = ctx.ref_tokens()
        ok = bool(known) and tex_referenced(known, toks) is not None
        # a slashless texPath (Textures-root file) must be visible too, when the repo has one
        rc, out, _ = _git(ctx.repo, "grep", "-h", "-o", "-m1", "-E", r"<texPath>[A-Za-z0-9_.-]+</texPath>", "--",
                          "src/*.xml")
        bare_known = None
        for line in out.splitlines():
            bare_known = re.sub(r"</?texPath>", "", line).strip().lower()
            if bare_known:
                break
        if bare_known and tex_referenced(bare_known, set(), ctx.bare_tokens()) is None:
            ok, known = False, bare_known
        ctx._cache["picprobe"] = (ok, known, len(toks), bare_known)
    ok, known, n, bare_known = ctx._cache["picprobe"]
    if not ok:
        v.blind("probe: reference set (%d strings) cannot see known texPath %r" % (n, known))
    else:
        v.evidence.append("probe: %d reference strings, sees known texPath %r%s" % (
            n, known, " and slashless %r" % bare_known if bare_known else ""))
    return ok


def check_picture(ctx, p, v):
    where = _picture_owner(ctx, p, v)
    if not where:
        return
    rel = tex_rel(p)
    if not rel:
        return v.refuse("not under a Textures/ folder")
    if where == "repo":
        r = repo_file_pushed(ctx, p)
        if r:
            v.no(r)
    else:
        folder, pid = owner_of_mod_path(ctx, p)
        if pid in ctx.repo_pids():
            src_mod = os.path.dirname(os.path.dirname(os.path.join(ctx.repo, ctx.repo_pids()[pid])))
            for d, _dirs, files in os.walk(src_mod):
                if os.path.basename(p) in files and tex_rel(os.path.join(d, os.path.basename(p))) == rel:
                    v.no("the repo source of %s still ships this texture (judge the repo copy)" % folder)
                    break
    if not picture_probe(ctx, v):
        return
    hit = tex_referenced(rel, ctx.ref_tokens(), ctx.bare_tokens())
    if hit:
        v.no("referenced as %r" % hit)
    elif rel.startswith("ui/"):
        v.no("UI/ path: may override a vanilla ContentFinder texture by path; cannot be cleared")
    elif "/rimthemes/" in p.replace("\\", "/").lower():
        v.no("RimThemes theme texture: read by its file name (Class.Field), never by a texPath; cannot be cleared")
    else:
        v.evidence.append("0 references to %r" % rel)


def check_patch(ctx, p, v):
    where = _picture_owner(ctx, p, v)
    if not where:
        return
    ret = ctx.retired()
    if not ret or "sarg.alphabiomes" not in ret:
        return v.blind("probe: retired_mods.json did not load the known retired id sarg.alphabiomes")
    ok, detail = classify_patch(p, ret)
    if where == "repo":
        r = repo_file_pushed(ctx, p)
        if r:
            v.no(r)
    if not ok:
        v.no(detail)
    else:
        v.evidence.append(detail)


CHECKERS = {"save": check_save, "clone": check_clone, "modfolder": check_modfolder, "setting": check_setting,
            "picture": check_picture, "patch": check_patch}


def check(ctx, path, kind=None):
    path = os.path.abspath(path)
    kind = kind or kind_of(ctx, path)
    v = Verdict(path, kind)
    if not os.path.lexists(path):
        v.refuse("does not exist")
        return v
    if os.path.islink(path):
        v.refuse("is a symlink")
        return v
    if kind is None:
        v.refuse("not a leftover kind this tool knows (outside our clones/storage/mod folders)")
        return v
    for bad in ("/mnt/d/Luke/dev", os.path.expanduser("~/dev")):
        if _inside(path, bad):
            v.refuse("under %s: read-only or not ours" % bad)
            return v
    try:
        v.size = _size(path)
    except OSError:
        pass
    CHECKERS[kind](ctx, path, v)
    return v


# ======================================================================================== scan
def scan(ctx, kinds=KINDS):
    """-> list of candidate paths per kind (a candidate is not a verdict: run check)."""
    out = {k: [] for k in kinds}
    if "save" in out and os.path.isdir(ctx.saves):
        for f in sorted(os.listdir(ctx.saves)):
            if f.lower().endswith(".rws"):
                out["save"].append(os.path.join(ctx.saves, f))
        for f in sorted(os.listdir(ctx.userdata)):
            if re.match(r"Saves_(backup|archive)", f):
                out["save"].append(os.path.join(ctx.userdata, f))
    if "clone" in out:
        for root in ctx.clone_roots:
            if not os.path.isdir(root):
                continue
            for d, dirs, _files in os.walk(root):
                depth = os.path.relpath(d, root).count(os.sep)
                if ".git" in dirs and d != root:
                    out["clone"].append(d)
                    dirs[:] = []
                    continue
                dirs[:] = [x for x in dirs if not x.startswith(".") and x != "node_modules"]
                if depth >= 3:
                    dirs[:] = []
    if "modfolder" in out:
        repo = ctx.repo_pids()
        for name, pid in ctx.deployed().items():
            if pid is None or not pid.startswith("mandrake.") or pid not in repo:
                out["modfolder"].append(os.path.join(ctx.mods, name))
    if "setting" in out and os.path.isdir(ctx.config):
        ours = ctx.our_mod_folders()
        for f in sorted(os.listdir(ctx.config)):
            full = os.path.join(ctx.config, f)
            if not os.path.isfile(full):
                continue
            m = re.match(r"Mod_(.+?)_([A-Za-z_]\w*?)\.xml(\..*)?$", f)
            if m and not m.group(1).isdigit():
                if m.group(3) or m.group(1) not in ctx.deployed() or m.group(1) not in ours:
                    out["setting"].append(full)
            elif re.match(r"ModsConfig\..+", f) and f != "ModsConfig.xml":
                out["setting"].append(full)
    if "picture" in out:
        toks, bare = ctx.ref_tokens(), ctx.bare_tokens()
        rc, files, _ = _git(ctx.repo, "ls-files", "--", "src/*.png")
        for rel in files.splitlines():
            t = tex_rel(rel)
            if t and not tex_referenced(t, toks, bare):
                out["picture"].append(os.path.join(ctx.repo, rel))
        repo_rels = {}
        for rel in files.splitlines():
            t = tex_rel(rel)
            if t:
                repo_rels.setdefault(t, rel)
        for name, pid in ctx.deployed().items():
            if not pid or not pid.startswith("mandrake."):
                continue
            for d, _dirs, fs in os.walk(os.path.join(ctx.mods, name)):
                for f in fs:
                    if f.lower().endswith(".png"):
                        full = os.path.join(d, f)
                        t = tex_rel(full)
                        if t and t not in repo_rels and not tex_referenced(t, toks, bare):
                            out["picture"].append(full)
    if "patch" in out:
        ret = ctx.retired()
        pat = re.compile("|".join(re.escape(r) for r in sorted(ret)), re.I) if ret else None
        paths = []
        rc, files, _ = _git(ctx.repo, "ls-files", "--", "src/*.xml")
        paths += [os.path.join(ctx.repo, r) for r in files.splitlines() if "/patches/" in r.lower()]
        for name, pid in ctx.deployed().items():
            if pid and pid.startswith("mandrake."):
                for d, _dirs, fs in os.walk(os.path.join(ctx.mods, name)):
                    if "/patches" in d.lower().replace("\\", "/"):
                        paths += [os.path.join(d, f) for f in fs if f.lower().endswith(".xml")]
        for full in paths:
            try:
                txt = io.open(full, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if pat and pat.search(txt):
                out["patch"].append(full)
    return out


def winpath(p):
    m = re.match(r"^/mnt/([a-z])/(.*)$", p)
    if m:
        return "%s:\\%s" % (m.group(1).upper(), m.group(2).replace("/", "\\"))
    return p


def dryrun(ctx, kinds, md, tsv):
    cands = scan(ctx, kinds)
    rows = []
    for k in kinds:
        for p in cands[k]:
            rows.append(check(ctx, p, k))
    return render(rows, kinds, md, tsv)


def read_tsv(path):
    """Rows of an earlier dry run's TSV (so per-kind runs can be merged into one report)."""
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 6:
                continue
            v = Verdict(f[3], f[0])
            v.status, v.size = f[1], int(f[2] or 0)
            v.reasons = [x for x in f[4].split(" | ") if x]
            v.evidence = [x for x in f[5].split(" | ") if x]
            rows.append(v)
    return rows


def render(rows, kinds, md, tsv):
    lines = ["# Leftovers dry run -- %s" % _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
             "",
             "Tool: src/RimMandrake/Utils/leftovers.py (scan + check only; nothing archived or deleted).",
             "SAFE = would be archived then deleted; NOT-SAFE = something reads it or it is unpushed;",
             "REFUSED = not ours / canonical; UNMEASURED = the instrument's sanity probe failed.",
             "",
             "| kind | candidates | total size | SAFE (size) | NOT-SAFE | REFUSED | UNMEASURED |",
             "|---|---|---|---|---|---|---|"]
    for k in kinds:
        rk = [r for r in rows if r.kind == k]
        by = {s: [r for r in rk if r.status == s] for s in (SAFE, NOT_SAFE, REFUSED, UNMEASURED)}
        lines.append("| %s | %d | %s | %d (%s) | %d | %d | %d |" % (
            k, len(rk), human(sum(r.size for r in rk)), len(by[SAFE]), human(sum(r.size for r in by[SAFE])),
            len(by[NOT_SAFE]), len(by[REFUSED]), len(by[UNMEASURED])))
    lines += ["", "Full per-candidate list: %s" % winpath(tsv), ""]
    for k in kinds:
        rk = [r for r in rows if r.kind == k]
        lines += ["## %s (%d)" % (k, len(rk)), ""]
        cap = 60
        order = sorted(rk, key=lambda r: ({SAFE: 0, UNMEASURED: 1, NOT_SAFE: 2, REFUSED: 3}[r.status], r.path))
        for r in order[:cap]:
            lines.append("- %s `%s` %s -- %s" % (r.status, winpath(r.path), human(r.size),
                                                 "; ".join(r.reasons) or "; ".join(r.evidence[-1:])))
        if len(rk) > cap:
            lines.append("- ... %d more in the TSV" % (len(rk) - cap))
        lines.append("")
    os.makedirs(os.path.dirname(md), exist_ok=True)
    io.open(md, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    with io.open(tsv, "w", encoding="utf-8") as fh:
        fh.write("kind\tverdict\tsize\tpath\treasons\tevidence\n")
        for r in rows:
            fh.write("\t".join([r.kind, r.status, str(r.size), r.path, " | ".join(r.reasons),
                                " | ".join(r.evidence)]) + "\n")
    return rows


# ======================================================================================== archive / delete
def _archive_base(ctx, path, kind):
    tag = re.sub(r"[^\w.\-]+", "_", os.path.basename(path.rstrip("/")))
    h = hashlib.sha1(os.path.realpath(path).encode()).hexdigest()[:8]
    day = _dt.date.today().isoformat()
    return os.path.join(ctx.archive_root, day, "%s__%s__%s" % (kind, tag, h))


def _file_list(path):
    if os.path.isfile(path):
        return [(os.path.basename(path), path)]
    out = []
    for d, dirs, files in os.walk(path):
        dirs.sort()
        for f in sorted(files):
            full = os.path.join(d, f)
            if not os.path.islink(full):
                out.append((os.path.relpath(full, os.path.dirname(path.rstrip("/"))), full))
    return out


def _refs(repo):
    rc, out, _ = _git(repo, "for-each-ref", "--format=%(objectname) %(refname)", "refs/heads", "refs/tags",
                      "refs/remotes")
    return sorted(l for l in out.splitlines() if l and not l.endswith("/HEAD"))


def archive(ctx, path, kind=None):
    path = os.path.abspath(path)
    kind = kind or kind_of(ctx, path)
    v = check(ctx, path, kind)
    if v.status == REFUSED:
        raise SystemExit("REFUSED archive of %s: %s" % (path, "; ".join(v.reasons)))
    base = _archive_base(ctx, path, kind)
    os.makedirs(os.path.dirname(base), exist_ok=True)
    man = {"source": os.path.realpath(path), "kind": kind, "created": _dt.datetime.now().isoformat(),
           "size": v.size, "check": v.as_dict()}
    if kind == "clone":
        arc = base + ".bundle"
        rc, out, err = _git(path, "bundle", "create", arc, "--all", timeout=540)
        if rc != 0:
            raise SystemExit("git bundle failed: %s" % err.strip())
        man["format"] = "git-bundle"
        man["refs"] = [r for r in _refs(path) if " refs/heads/" in r or " refs/tags/" in r]
        man["head"] = _git(path, "rev-parse", "HEAD")[1].strip()
    else:
        arc = base + ".tar.gz"
        files = []
        with tarfile.open(arc, "w:gz", compresslevel=6) as tf:
            for rel, full in _file_list(path):
                files.append({"rel": rel, "size": os.path.getsize(full), "sha256": _sha256(full)})
                tf.add(full, arcname=rel, recursive=False)
        man["format"] = "tar.gz"
        man["files"] = files
    man["archive"] = arc
    man["archive_sha256"] = _sha256(arc)
    io.open(base + ".manifest.json", "w", encoding="utf-8").write(json.dumps(man, indent=1))
    ok, why = verify(ctx, path, base + ".manifest.json")
    if not ok:
        raise SystemExit("archive written but does not verify: %s" % why)
    return base + ".manifest.json"


def verify(ctx, path, manifest):
    """Does the archive named by `manifest` hold `path` exactly as it is now?"""
    try:
        man = json.load(io.open(manifest, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return False, "manifest unreadable: %s" % e
    if man.get("source") != os.path.realpath(path):
        return False, "manifest is for %s" % man.get("source")
    arc = man.get("archive")
    if not arc or not os.path.exists(arc):
        return False, "archive file missing"
    if _sha256(arc) != man.get("archive_sha256"):
        return False, "archive sha256 mismatch"
    if man["format"] == "git-bundle":
        rc, out, err = _run(["git", "bundle", "verify", arc], cwd=path)
        if rc != 0:
            return False, "git bundle verify failed: %s" % err.strip()[:200]
        rc, heads, _ = _run(["git", "bundle", "list-heads", arc])
        inbundle = {l.split()[0] for l in heads.splitlines() if l.strip()}
        now = [r for r in _refs(path) if " refs/heads/" in r or " refs/tags/" in r]
        if now != man["refs"]:
            return False, "refs changed since the bundle"
        missing = [r for r in now if r.split()[0] not in inbundle]
        if missing:
            return False, "bundle lacks %s" % missing[0]
        if _git(path, "rev-parse", "HEAD")[1].strip() != man["head"]:
            return False, "HEAD moved since the bundle"
        return True, "bundle verifies, %d ref(s)" % len(now)
    want = {f["rel"]: f for f in man["files"]}
    cur = _file_list(path)
    if sorted(r for r, _ in cur) != sorted(want):
        return False, "file set changed since the archive"
    for rel, full in cur:
        if os.path.getsize(full) != want[rel]["size"] or _sha256(full) != want[rel]["sha256"]:
            return False, "%s changed since the archive" % rel
    with tarfile.open(arc, "r:gz") as tf:
        seen = 0
        for m in tf.getmembers():
            if not m.isfile():
                continue
            f = want.get(m.name)
            if not f:
                return False, "archive holds unexpected %s" % m.name
            h = hashlib.sha256()
            fh = tf.extractfile(m)
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
            if h.hexdigest() != f["sha256"]:
                return False, "archive copy of %s is corrupt" % m.name
            seen += 1
    if seen != len(want):
        return False, "archive holds %d of %d files" % (seen, len(want))
    return True, "tar verifies, %d file(s)" % seen


def find_manifest(ctx, path):
    rp = os.path.realpath(path)
    best = None
    if not os.path.isdir(ctx.archive_root):
        return None
    for day in sorted(os.listdir(ctx.archive_root), reverse=True):
        d = os.path.join(ctx.archive_root, day)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d), reverse=True):
            if f.endswith(".manifest.json"):
                try:
                    if json.load(io.open(os.path.join(d, f), encoding="utf-8")).get("source") == rp:
                        return os.path.join(d, f)
                except (OSError, ValueError):
                    continue
    return best


def delete(ctx, path, item="LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE", ledger=True, kind=None):
    path = os.path.abspath(path)
    v = check(ctx, path, kind)
    if v.kind == "picture":
        # ruling: a picture leaves only through the art ledger (art.py), never a raw file delete; the
        # leftovers check also does not consult art-ledger keeps or review-sheet decisions.
        raise SystemExit("REFUSED delete of %s: a picture leaves only through the art ledger (art.py), "
                         "not leftovers.py" % path)
    if v.status != SAFE:
        raise SystemExit("REFUSED delete of %s: check is %s (%s)" % (path, v.status, "; ".join(v.reasons)))
    man = find_manifest(ctx, path)
    if not man:
        raise SystemExit("REFUSED delete of %s: no archive for it under %s (run archive first)" % (
            path, ctx.archive_root))
    ok, why = verify(ctx, path, man)
    if not ok:
        raise SystemExit("REFUSED delete of %s: archive %s does not verify: %s" % (path, man, why))
    arc = json.load(io.open(man, encoding="utf-8"))["archive"]
    tracked = _inside(path, ctx.repo)
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
    act = {"ts": _dt.datetime.now().isoformat(), "kind": v.kind, "path": os.path.realpath(path),
           "size": v.size, "archive": arc, "manifest": man, "verify": why, "evidence": v.evidence}
    with io.open(os.path.join(ctx.archive_root, "acts.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(act) + "\n")
    line = "deleted leftover %s %s (%s); archive %s" % (v.kind, winpath(path), human(v.size), winpath(arc))
    if ledger:
        cli = os.path.join(ctx.repo, "src", "RimMandrake", "rimflow", "cli.py")
        rc, out, err = _run([sys.executable, cli, "note", item, "--text", line,
                             "--why", "delegated: leftovers (archive-then-delete, owner card 2026-10-26 19:06)"],
                            cwd=ctx.repo)
        if rc != 0:
            print("WARNING: deleted, but the rimflow note failed -- log it by hand: %s" % err.strip()[:300])
    if tracked:
        print("repo file removed: stage the deletion with `git add %s` and commit with a 'Delegated:' line"
              % os.path.relpath(path, ctx.repo))
    print(line)
    return act


# ======================================================================================== cli
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--kind", action="append", choices=KINDS)
    s.add_argument("--md", default="/mnt/d/ClaudeWork/rimmandrake/leftovers/dryrun.md")
    s.add_argument("--tsv", default=None)
    s.add_argument("--merge", nargs="+", metavar="TSV",
                   help="no scan: merge earlier per-kind TSVs into one report")
    for name in ("check", "archive", "delete", "retire"):
        c = sub.add_parser(name)
        c.add_argument("path")
        c.add_argument("--kind", choices=KINDS)
        if name == "check":
            c.add_argument("--json", action="store_true")
        if name in ("delete", "retire"):
            c.add_argument("--item", default="LEFTOVERS_BUILD_ARCHIVE_THEN_DELETE")
            c.add_argument("--no-ledger", action="store_true")
    a = ap.parse_args(argv)
    ctx = Ctx()
    if a.cmd == "scan":
        kinds = tuple(a.kind) if a.kind else KINDS
        tsv = a.tsv or os.path.splitext(a.md)[0] + ".tsv"
        if a.merge:
            rows = [r for t in a.merge for r in read_tsv(t)]
            kinds = tuple(k for k in KINDS if any(r.kind == k for r in rows))
            rows = render(rows, kinds, a.md, tsv)
        else:
            rows = dryrun(ctx, kinds, a.md, tsv)
        for k in kinds:
            rk = [r for r in rows if r.kind == k]
            print("%-9s %5d candidates %10s  SAFE %d  NOT-SAFE %d  REFUSED %d  UNMEASURED %d" % (
                k, len(rk), human(sum(r.size for r in rk)), *[sum(1 for r in rk if r.status == st)
                                                              for st in (SAFE, NOT_SAFE, REFUSED, UNMEASURED)]))
        print("wrote %s and %s" % (a.md, tsv))
        return 0
    if a.cmd == "check":
        v = check(ctx, a.path, a.kind)
        if a.json:
            print(json.dumps(v.as_dict(), indent=1))
        else:
            print("%s %s (%s, %s)" % (v.status, a.path, v.kind, human(v.size)))
            for r in v.reasons:
                print("  - " + r)
            for e in v.evidence:
                print("  + " + e)
        return 0 if v.status == SAFE else 1
    if a.cmd == "archive":
        print("archived: %s" % archive(ctx, a.path, a.kind))
        return 0
    if a.cmd == "retire":
        if (a.kind or kind_of(ctx, os.path.abspath(a.path))) == "picture":
            raise SystemExit("REFUSED retire of %s: a picture leaves only through the art ledger (art.py), "
                             "not leftovers.py" % a.path)
        if not find_manifest(ctx, a.path) or not verify(ctx, a.path, find_manifest(ctx, a.path))[0]:
            v = check(ctx, a.path, a.kind)
            if v.status != SAFE:
                raise SystemExit("REFUSED retire of %s: check is %s (%s)" % (a.path, v.status, "; ".join(v.reasons)))
            archive(ctx, a.path, a.kind)
    delete(ctx, a.path, a.item, ledger=not a.no_ledger, kind=a.kind)
    return 0


if __name__ == "__main__":
    sys.exit(main())
