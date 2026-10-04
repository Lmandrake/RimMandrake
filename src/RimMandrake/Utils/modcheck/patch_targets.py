#!/usr/bin/env python3
"""patch_targets.py — offline check that every PatchOperation in a mod lands on something.

A patch whose xpath matches nothing logs NOTHING in RimWorld (PatchOperationConditional and
PatchOperationFindMod both return true on no match), so the only way to learn it offline is to
replay the patches against the raw XML the game would see. This module:

  1. indexes installed mods by About.xml (both mod roots + this repo's src/), by packageId and name;
  2. builds ONE merged <Defs> document from the game Data (Core + every DLC), every src/ mod, and
     the donor mods the checked mod names (About modDependencies/loadAfter + every
     PatchOperationFindMod <mods> name) — never the whole workshop (walking it alone takes ~72 s);
  3. replays the mod's Patches/ files in load order (sorted path), APPLYING Add / Replace / Remove
     so a later op can see what an earlier one added, and grades every op:

     PASS        the xpath matched >= 1 node (or a Conditional's test resolved and its branch passed)
     FAIL        a NON-test op matched nothing: a silent no-op in game
     SKIP        inside a FindMod branch for a mod that is not installed (UNMEASURED, not a pass)
     UNMEASURED  an operation class this replay does not model, or an xpath lxml cannot evaluate

  A Conditional whose test matches nothing and has no <nomatch> is a guard sitting idle; that is a
  PASS only when the def its xpath names IS indexed (an "already applied" guard) and a FAIL when
  the def itself is absent (the guard can never fire).

  🔴 MayRequire on an <Operation> element is IGNORED by the 1.6 engine (CLAUDE.md, 2026-09-27): such
  an op is replayed as unconditional and its result carries a note, never skipped.

    python3 -m modcheck.patch_targets src/RimStarWars/StarWarsPatches     (from src/RimMandrake/Utils)
"""
from __future__ import annotations

import os
import re
import sys
from copy import deepcopy
from pathlib import Path

from lxml import etree

GAME_DATA = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")
MOD_ROOTS = (Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"),
             Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"))
REPO_SRC = Path(__file__).resolve().parents[3]          # .../src
VERSION = "1.6"

_DEFNAME = re.compile(r'(\w+)\[\s*defName\s*=\s*["\']([^"\']+)["\']')
_NAMEATTR = re.compile(r'(\w+)\[\s*@Name\s*=\s*["\']([^"\']+)["\']')
_PARSER = etree.XMLParser(recover=True, remove_comments=True, remove_blank_text=True)


# ---------------------------------------------------------------- mod discovery

def about_of(moddir: Path) -> dict | None:
    p = moddir / "About" / "About.xml"
    if not p.is_file():
        return None
    try:
        r = etree.parse(str(p), _PARSER).getroot()
    except (etree.XMLSyntaxError, OSError):
        return None
    if r is None:
        return None
    lis = lambda tag: [(li.text or "").strip().lower() for li in r.findall(f"{tag}/li") if li.text]
    deps = [(d.findtext("packageId") or "").strip().lower() for d in r.findall("modDependencies/li")]
    return {"dir": moddir, "packageId": (r.findtext("packageId") or "").strip().lower(),
            "name": (r.findtext("name") or "").strip(),
            "wants": sorted({x for x in deps + lis("loadAfter") if x})}


def mod_index(roots=MOD_ROOTS, src=REPO_SRC, game_data=GAME_DATA) -> list[dict]:
    """Every installed mod's About (src/ first, so our own copy wins over a deployed one), plus the
    game's own Core/DLC folders (FindMod names a DLC by its folder name, e.g. "Biotech")."""
    out = []
    if game_data and Path(game_data).is_dir():
        for d in sorted(Path(game_data).iterdir()):
            a = about_of(d)
            if a:
                a["name"] = a["name"] or d.name
                a["game"] = True
                out.append(a)
    dirs = []
    if src and Path(src).is_dir():
        dirs += [d for tier in sorted(Path(src).iterdir()) if tier.is_dir() for d in sorted(tier.iterdir())]
    for r in roots:
        if Path(r).is_dir():
            dirs += sorted(Path(r).iterdir())
    for d in dirs:
        a = about_of(d)
        if a:
            out.append(a)
    return out


def defs_dirs(moddir: Path) -> list[Path]:
    """The Defs folders the game would read for VERSION: LoadFolders.xml when present, else the
    conventional root / <ver> / Common."""
    moddir = Path(moddir)
    lf = moddir / "LoadFolders.xml"
    bases: list[Path] = []
    if lf.is_file():
        try:
            r = etree.parse(str(lf), _PARSER).getroot()
            node = r.find("v" + VERSION) if r is not None else None
            if node is not None:
                bases = [moddir / (li.text or "").strip().strip("/") for li in node.findall("li")]
        except etree.XMLSyntaxError:
            bases = []
    if not bases:
        bases = [moddir, moddir / VERSION, moddir / "Common"]
    return [b / "Defs" for b in bases if (b / "Defs").is_dir()]


# ---------------------------------------------------------------- where does a def live?

CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "rimmandrake" / "def_locations.json"
_DEF_RX = re.compile(r"<(\w+)\b[^>]*>\s*<defName>\s*([^<\s]+)\s*</defName>")


def _fingerprint(moddir: Path) -> str:
    """Mod dir + About.xml + each Defs dir mtime: cheap (no tree walk; walking every mod's Defs
    subtree on /mnt/c cost ~3 min). A Steam update rewrites the folder, which moves these."""
    parts = []
    for p in (Path(moddir), Path(moddir) / "About" / "About.xml", *defs_dirs(moddir)):
        try:
            parts.append(str(int(p.stat().st_mtime)))
        except OSError:
            parts.append("-")
    return "|".join(parts)


def location_index(mods, cache: Path | None = CACHE, log=None) -> dict[str, list[str]]:
    """'Type/defName' -> [mod dirs], over every installed mod outside src/. A regex scan (cheap) cached
    per mod by a Defs-tree mtime fingerprint, so only a changed mod is re-read. Used only to find WHICH
    donor to load into the merged document when the declared donors do not hold a target def."""
    import json
    old = {}
    if cache and cache.is_file():
        try:
            old = json.loads(cache.read_text())
        except ValueError:
            old = {}
    new, out, rescanned = {}, {}, 0
    for m in mods:
        if m.get("game") or str(m["dir"]).startswith(str(REPO_SRC)):
            continue
        key = str(m["dir"])
        fp = _fingerprint(m["dir"])
        ent = old.get(key)
        if not ent or ent.get("fp") != fp:
            names = set()
            for d in defs_dirs(m["dir"]):
                for dp, _ds, fs in os.walk(d):
                    for fn in fs:
                        if fn.endswith(".xml"):
                            try:
                                txt = (Path(dp) / fn).read_text(errors="replace")
                            except OSError:
                                continue
                            names |= {f"{t}/{n}" for t, n in _DEF_RX.findall(txt)}
            ent = {"fp": fp, "defs": sorted(names)}
            rescanned += 1
        new[key] = ent
        for n in ent["defs"]:
            out.setdefault(n, []).append(key)
    if cache and (rescanned or set(new) != set(old)):
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(new))
    if log:
        log(f"location index: {len(new)} mods, {rescanned} rescanned, {len(out)} defs")
    return out


# ---------------------------------------------------------------- the merged document

class DefIndex:
    def __init__(self, defs_dirs_list):
        self.root = etree.Element("Defs")
        self.files = 0
        self.by_name: dict[tuple[str, str], int] = {}
        for d in defs_dirs_list:
            self.add_dir(d)

    def add_dir(self, d):
        for dp, _ds, fs in os.walk(d):
            for fn in sorted(fs):
                if fn.endswith(".xml"):
                    self._add(Path(dp) / fn)

    def _add(self, path: Path):
        try:
            r = etree.parse(str(path), _PARSER).getroot()
        except (etree.XMLSyntaxError, OSError, ValueError):
            return
        if r is None:
            return
        self.files += 1
        for el in list(r):
            if not isinstance(el.tag, str):
                continue
            self.root.append(el)
            dn = el.findtext("defName")
            if dn:
                self.by_name[(el.tag, dn.strip())] = self.by_name.get((el.tag, dn.strip()), 0) + 1
            if el.get("Name"):
                self.by_name[(el.tag, "@" + el.get("Name"))] = 1

    def select(self, xpath: str):
        xp = xpath.strip()
        if not xp.startswith("/"):
            xp = "/" + xp
        return etree.ElementTree(self.root).xpath(xp)

    def has_def(self, ty: str, name: str) -> bool:
        return (ty, name) in self.by_name

    def named_defs(self, xpath: str) -> list[tuple[str, str]]:
        return ([(t, n) for t, n in _DEFNAME.findall(xpath)]
                + [(t, "@" + n) for t, n in _NAMEATTR.findall(xpath)])


# ---------------------------------------------------------------- replay

MODELED = {"PatchOperationAdd", "PatchOperationReplace", "PatchOperationRemove",
           "PatchOperationConditional", "PatchOperationFindMod", "PatchOperationSequence"}


class Replay:
    def __init__(self, index: DefIndex, installed_names: set[str], installed_ids: set[str]):
        self.ix = index
        self.names = installed_names
        self.ids = installed_ids
        self.results: list[dict] = []

    def _rec(self, where, op, status, why="", matched=None):
        self.results.append({"where": where, "class": op.get("Class"), "xpath": (op.findtext("xpath") or "").strip(),
                             "status": status, "why": why, "matched": matched})

    def _select(self, where, op):
        xp = (op.findtext("xpath") or "").strip()
        try:
            return self.ix.select(xp)
        except etree.XPathError as e:
            self._rec(where, op, "UNMEASURED", f"lxml cannot evaluate the xpath: {e}")
            return None

    def run_op(self, op, where, skip_reason=None):
        cls = op.get("Class") or ""
        note = ""
        if op.get("MayRequire") and op.tag == "Operation":
            note = f"MayRequire={op.get('MayRequire')!r} on <Operation> is INERT in 1.6: replayed unconditionally. "
        if skip_reason:
            self._rec(where, op, "SKIP", skip_reason)
            for ch in self._children(op):
                self.run_op(ch, where + ">", skip_reason)
            return True
        if cls not in MODELED:
            self._rec(where, op, "UNMEASURED", note + f"{cls} is not modelled by this replay")
            return True
        if cls == "PatchOperationSequence":
            ok = True
            for i, ch in enumerate(op.findall("operations/li")):
                if not self.run_op(ch, f"{where}>seq[{i}]"):
                    ok = False
            return ok
        if cls == "PatchOperationFindMod":
            wanted = [(li.text or "").strip() for li in op.findall("mods/li")]
            found = any(w in self.names or w.lower() in self.ids for w in wanted)
            br, other = ("match", "nomatch") if found else ("nomatch", "match")
            for ch in op.findall(other):
                self.run_op(ch, f"{where}>{other}",
                            skip_reason=f"FindMod {wanted} {'present' if found else 'NOT installed'}: branch never runs")
            for ch in op.findall(br):
                self.run_op(ch, f"{where}>{br}")
            return True
        nodes = self._select(where, op)
        if nodes is None:
            return True
        n = len(nodes)
        if cls == "PatchOperationConditional":
            br = "match" if n else "nomatch"
            branch = op.find(br)
            if branch is not None:
                self._rec(where, op, "PASS", note + f"test matched {n}: runs <{br}>", n)
                return self.run_op(branch, f"{where}>{br}")
            named = self.ix.named_defs(op.findtext("xpath") or "")
            absent = [f"{t}/{nm}" for t, nm in named if not self.ix.has_def(t, nm)]
            if n == 0 and absent:
                self._rec(where, op, "FAIL", note + f"guard can never fire: {', '.join(absent)} is not in any indexed mod", n)
                return False
            self._rec(where, op, "PASS", note + ("test matched: no <match>" if n else
                                                 "guard idle (already applied); the def it names exists"), n)
            return True
        if n == 0:
            named = self.ix.named_defs(op.findtext("xpath") or "")
            absent = [f"{t}/{nm}" for t, nm in named if not self.ix.has_def(t, nm)]
            why = (f"def not in any indexed mod: {', '.join(absent)}" if absent
                   else "the def exists but the path below it matches nothing")
            self._rec(where, op, "FAIL", note + "matches nothing (silent no-op in game): " + why, 0)
            return False
        self._apply(cls, op, nodes)
        self._rec(where, op, "PASS", note.strip(), n)
        return True

    @staticmethod
    def _children(op):
        for tag in ("match", "nomatch"):
            yield from op.findall(tag)
        yield from op.findall("operations/li")

    def _apply(self, cls, op, nodes):
        value = op.find("value")
        kids = [deepcopy(c) for c in value] if value is not None else []
        for node in nodes:
            if not isinstance(node, etree._Element):
                continue
            if cls == "PatchOperationAdd":
                if (op.findtext("order") or "").strip() == "Prepend":
                    for i, c in enumerate(kids):
                        node.insert(i, deepcopy(c))
                else:
                    for c in kids:
                        node.append(deepcopy(c))
            elif cls == "PatchOperationReplace":
                parent = node.getparent()
                if parent is None:
                    continue
                at = parent.index(node)
                parent.remove(node)
                for i, c in enumerate(kids):
                    parent.insert(at + i, deepcopy(c))
            elif cls == "PatchOperationRemove":
                parent = node.getparent()
                if parent is not None:
                    parent.remove(node)


def patch_files(moddir: Path) -> list[Path]:
    out = []
    for d in defs_dirs(moddir):
        p = d.parent / "Patches"
        if p.is_dir():
            out += sorted(p.rglob("*.xml"))
    return out


def findmod_names(files) -> set[str]:
    s = set()
    for f in files:
        try:
            r = etree.parse(str(f), _PARSER).getroot()
        except etree.XMLSyntaxError:
            continue
        for e in r.iter():
            if isinstance(e.tag, str) and e.get("Class") == "PatchOperationFindMod":
                s |= {(li.text or "").strip() for li in e.findall("mods/li")}
    return s


def _named_in_patches(files) -> set[tuple[str, str]]:
    out = set()
    for f in files:
        txt = Path(f).read_text(errors="replace")
        out |= set(_DEFNAME.findall(txt))
    return out


def check_mod(moddir, mods=None, game_data=GAME_DATA, extra_defs=(), locate=True, cache=CACHE):
    """Replay a mod's patches. Returns (results, meta). `mods` defaults to mod_index().
    locate=True: a def the patches name that no declared donor holds is looked up in the cached
    location_index and its owning mod is added to the merged document."""
    moddir = Path(moddir).resolve()
    mods = mod_index() if mods is None else mods
    me = about_of(moddir) or {"wants": [], "packageId": ""}
    files = patch_files(moddir)
    wanted_names = findmod_names(files)
    wanted_ids = set(me["wants"])
    by_id = {m["packageId"]: m for m in mods}
    by_name = {m["name"]: m for m in mods}
    donors = {}
    for pid in wanted_ids:
        if pid in by_id:
            donors[by_id[pid]["dir"]] = by_id[pid]
    for nm in wanted_names:
        if nm in by_name:
            donors[by_name[nm]["dir"]] = by_name[nm]
    dirs = []
    if Path(game_data).is_dir():
        dirs += [d / "Defs" for d in sorted(Path(game_data).iterdir()) if (d / "Defs").is_dir()]
    dirs += defs_dirs(moddir)                      # the checked mod's own defs, wherever it lives
    src_mods = [m for m in mods if str(m["dir"]).startswith(str(REPO_SRC)) and Path(m["dir"]).resolve() != moddir]
    for m in src_mods + [m for m in donors.values() if m not in src_mods]:
        dirs += defs_dirs(m["dir"])
    dirs += [Path(x) for x in extra_defs]
    located = []
    ix = DefIndex(dirs)
    if locate:
        missing = {f"{t}/{n}" for t, n in _named_in_patches(files) if not ix.has_def(t, n)}
        if missing:
            loc = location_index(mods, cache)
            have = {str(m["dir"]) for m in donors.values()}
            for key in sorted({d for n in missing for d in loc.get(n, [])} - have):
                for d in defs_dirs(Path(key)):
                    ix.add_dir(d)
                located.append(key)
    rp = Replay(ix, {m["name"] for m in mods}, {m["packageId"] for m in mods})
    for f in files:
        r = etree.parse(str(f), _PARSER).getroot()
        for i, op in enumerate(x for x in r if isinstance(x.tag, str)):
            rp.run_op(op, f"{f.name}#{i}")
    meta = {"files": len(files), "defs_files": ix.files, "donors": sorted(m["name"] for m in donors.values()),
            "missing_wanted": sorted((wanted_ids - set(by_id)) | (wanted_names - set(by_name))), "index": ix,
            "located": located}
    return rp.results, meta


def sanity(ix: DefIndex) -> list[str]:
    """Proves the instrument can see: Core Steel and its statBases resolve, a missing child and a
    bogus def do not. Returns problems (empty = it can see)."""
    bad = []
    if len(ix.select('/Defs/ThingDef[defName="Steel"]/statBases')) != 1:
        bad.append("Core ThingDef Steel/statBases not found: the index cannot see the game Data")
    if ix.select('/Defs/ThingDef[defName="Steel"]/noSuchChild'):
        bad.append("a missing child reads as present")
    if ix.select('/Defs/ThingDef[defName="RM_NoSuchDef_Probe"]'):
        bad.append("a bogus def reads as present")
    return bad


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    results, meta = check_mod(Path(argv[0]))
    s = sanity(meta["index"])
    from collections import Counter
    c = Counter(r["status"] for r in results)
    print(f"{argv[0]}: {meta['files']} patch files, {len(results)} ops; index {meta['defs_files']} def files; "
          f"donors {len(meta['donors'])} declared + {len(meta['located'])} located by def")
    if meta["missing_wanted"]:
        print(f"  named but NOT installed: {meta['missing_wanted']}")
    print("  SANITY " + ("ok" if not s else "BROKEN: " + "; ".join(s)))
    print("  " + "  ".join(f"{k} {v}" for k, v in sorted(c.items())))
    for why, k in Counter(r["why"] for r in results if r["status"] == "SKIP").items():
        print(f"  SKIP x{k}: {why}")
    for r in results:
        if r["status"] in ("FAIL", "UNMEASURED"):
            print(f"  {r['status']:<10} {r['where']}  {r['xpath'][:110]}\n             {r['why']}")
    return 1 if (s or c.get("FAIL")) else 0


if __name__ == "__main__":
    sys.exit(main())
