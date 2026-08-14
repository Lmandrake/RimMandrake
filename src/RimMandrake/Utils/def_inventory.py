#!/usr/bin/env python3
"""
def_inventory.py — the whole modded def database, offline, inheritance resolved.

VERSION 1.0  (2026-08-10)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Docs/manifest: src/RimMandrake/Utils/README.md  ("def_inventory.py" section)
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

CHANGELOG
  1.0  first cut. Layer 1 of a three-layer design: this module is the generic,
       category-agnostic machinery lifted out of animal_inventory.py v1.4 —
       load-set resolution, the two-pass scan, and the <ParentName> resolver —
       generalised from "ThingDefs that have a <race>" to ALL 495 def types.
       animal_inventory.py is deliberately NOT ported onto it yet; it stays the
       proven reference implementation that this module is verified against.
       Layer 2 (projections: per-category column sets) and layer 3 (the offline
       vs live diff) are separate tools and are NOT in here.

WHY THIS EXISTS
===============
animal_inventory.py parses all 8,294 def XML files in the load set and then
throws away everything that is not a ThingDef with a <race> — 50,165 of 51,408
def nodes, 494 of 495 def types. Every question about any other def type
("which mod really owns this ResearchProjectDef", "what does this
GeneDef actually resolve to after its abstract base merges") currently has no
offline answer at all, despite the parse already having been paid for.

The expensive and subtle parts of that tool are not animal-specific:

  * resolving WHICH folders the game loads (rimworld_loadset — version folders
    and LoadFolders.xml make the on-disk file set a superset of the load set),
  * the two-pass scan (a parent may be declared by a mod that loads AFTER its
    children, so nothing can be resolved until every file has been read),
  * and <ParentName> inheritance with RimWorld's own merge semantics.

Those three things are what this module is. Everything category-specific —
which fields matter, what a column means, what counts as "an animal" — belongs
in a projection layer built ON TOP of this, never in here.

THE KEY INTERFACE
=================
Every DefRecord exposes `.element`: the def's XML element with its whole
ParentName ancestry already merged in. A projection layer runs its xpaths
against THAT, and therefore cannot accidentally read pre-inheritance values.
That was the entire v1.2->v1.3 bug in animal_inventory.py (fields read off the
def's own element reported blank for the majority of animals, whose abstract
base supplied them), and this interface is the structural fix: there is no
convenient way to get the unresolved node by accident. `.own` is still there
when you genuinely want the raw declaration, e.g. to compute which fields were
inherited — but you have to ask for it by name.

USAGE (the real deliverable — this is a library first, a CLI second)
====================================================================
    from def_inventory import build

    ds = build()                                  # defaults = this machine
    td = ds.get("ThingDef", "Muffalo")
    td.element.find("race/baseBodySize").text     # inheritance already applied
    td.modName, td.loadOrder, td.sourceFile       # provenance
    td.inheritChain                               # ['AnimalThingBase', 'BasePawn']

    for rec in ds.of_type("GeneDef"):
        ...

    ds.depth_histogram()                          # {0: n, 1: n, ...}

CLI (inspection and the raw dump)
=================================
    python def_inventory.py --summary                 # per-type counts, no files
    python def_inventory.py --out DIR                 # defs/<Type>.json + manifest.json
    python def_inventory.py --out DIR --types ThingDef,PawnKindDef

The dump mirrors src/RimMandrake/RimDefDump's layout (defs/<DefType>.json +
manifest.json) and its vocabulary (defName, defType, modName, packageId,
loadOrder) so the offline and live photographs of the same mod set are
trivially joinable. One deliberate divergence: `loadOrder` here is 1-based,
matching rimworld_loadset and the existing animals.csv column, while
RimDefDump's is the 0-based index into RunningModsListForReading. Add one when
joining. It is called out here because a silent off-by-one in a join key is the
kind of thing that produces confident wrong answers.

WHAT THIS CANNOT SEE (documented honestly, do not forget it)
============================================================
  * PatchOperation results. Patches apply at load; this reads base XML. A def
    that only exists after a patch, or a field a patch rewrites, is invisible.
    This is the single biggest blind spot and it has already cost this project
    three game loads (the dangling wildAnimals entries that killed CWAS exist
    only after Primordial Geysers' patch runs).
  * MayRequire / MayRequireAnyOf. Not evaluated anywhere, including on inherited
    <li> nodes, so a resolved list can contain entries a real load would drop.
  * Mod-vs-mod override winners. Recorded, not adjudicated: `duplicateOwners`
    names every mod that declared a given (defType, defName) and the last in
    load order wins here. The game's winner is usually but not certainly the
    same one.
  * Duplicate abstract Names across mods. Same rule, same caveat.
  * True shortHashes. `shortHashCandidate` uses RimWorld's StableStringHash but
    the game bumps collisions across the whole loaded set per defType. Treat it
    as a candidate until a live dump confirms it.
  * C#-side defaults. A field the XML never mentions is simply absent here; the
    game's field initialiser value is not knowable from XML.
  * Post-load cross-reference resolution, StatWorker output, and anything else
    that only exists in the running DefDatabase. That is RimDefDump's job.

PERFORMANCE
===========
Run natively on Windows. 8,294 files are parsed exactly once. Inheritance
MERGING is lazy — walking the ParentName chain is cheap and happens for every
def up front (so inheritDepth / inheritChain / unresolvedParent are always
available), but the deepcopy-and-merge that produces `.element` only happens on
first access, and resolutions of abstract parents are cached and shared. So
--summary and the inheritance histogram cost a scan; a full dump costs a scan
plus 51k merges. Through a network/device-bridge mount the filesystem does
~210 files/sec and this becomes minutes; natively it is seconds.
"""

import argparse
import copy
import json
import os
import sys
import time
from collections import Counter, defaultdict

# Shared load-set resolver. Lives beside this file so every offline tool in the
# project agrees on which folders the game actually reads. Do NOT reimplement
# it here: it encodes two traps (version folders, conditional LoadFolders.xml)
# that produce confident wrong numbers rather than errors.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimworld_loadset import (build_load_set, def_dirs,   # noqa: E402
                              parse_xml as _loadset_parse_xml)

__all__ = ["build", "DefSet", "DefRecord", "element_to_dict",
           "resolve_inherit", "INHERIT_MAX_DEPTH",
           "D_CONFIG", "D_WORKSHOP", "D_LOCAL", "D_DATA"]

VERSION = "1.0"

# ---------------------------------------------------------------- defaults
# Resolved per-platform rather than hardcoded to C:\ — see src/RimMandrake/Utils/game_paths.py.
# These were four Windows literals until 2026-08-13, which made every default
# unusable under WSL while failing with "No such file or directory", i.e.
# naming a missing file instead of the wrong interpreter.
from game_paths import MODS_CONFIG, WORKSHOP, LOCAL_MODS, GAME_DATA

D_CONFIG = MODS_CONFIG
D_WORKSHOP = WORKSHOP
D_LOCAL = LOCAL_MODS
D_DATA = GAME_DATA


# ---------------------------------------------------------------- helpers
def stable_string_hash(s):
    """RimWorld GenText.StableStringHash. See the shortHash caveat up top."""
    if s is None:
        return 0
    num = 23
    for ch in s:
        num = (num * 31 + ord(ch)) & 0xFFFFFFFF
    if num >= 0x80000000:
        num -= 0x100000000
    return num


def short_hash(defname):
    return (stable_string_hash(defname) % 65535) + 1 if defname else ""


def txt(node, path, default=""):
    """Text of the first match, stripped. None-safe on both node and match."""
    if node is None:
        return default
    el = node.find(path)
    return el.text.strip() if el is not None and el.text else default


def parse_xml(path):
    """Tolerant parse. Same implementation the load-set resolver uses."""
    return _loadset_parse_xml(path)


def walk_xml(root_dir):
    for dp, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(".xml"):
                yield os.path.join(dp, f)


# ---------------------------------------------------------------- inheritance
# <ThingDef ParentName="AnimalThingBase"> is not decoration: most defs of most
# types get the bulk of their content from an abstract base, frequently one
# owned by a DIFFERENT mod. RimWorld resolves this AFTER every mod's XML has
# been read, so a parent may sit anywhere in load order relative to its
# children — which is why the scan below is two-pass.
#
# Merge rule, mirroring XmlInheritance.RecursiveNodeCopyOverwriteElements:
#   * the CHILD's own value always wins; a parent value only fills a gap;
#   * a node whose children are <li> items — tools, comps, lifeStageAges,
#     tradeTags, any List<> — is REPLACED WHOLESALE by a child that declares
#     it. It is NOT merged element-wise. Getting this wrong invents list
#     entries the def does not have;
#   * a node whose children are named elements — race, statBases, wildBiomes —
#     merges per child name, recursively;
#   * a leaf value node replaces its parent's outright;
#   * Inherit="False" forces wholesale replacement regardless.
#
# These semantics are byte-for-byte the ones animal_inventory.py v1.4 shipped
# and were verified against 1,243 animals. Do not "improve" them without
# re-running src/RimMandrake/Utils/def_inventory verification against observed/2026-08-13/inventory/animals.csv.
INHERIT_MAX_DEPTH = 20

# Name/ParentName/Abstract describe a node's own place in the graph and must
# never be copied down from a parent (RimWorld strips them from the clone too).
_INHERIT_ATTRS = ("Name", "ParentName", "Abstract")


def _is_list_node(el):
    """True when this node's children are <li> items, i.e. a RimWorld List<>."""
    return any(ch.tag == "li" for ch in el)


def _overwrite(child, cur):
    """cur takes the child's content wholesale: text, children, attributes."""
    cur.text = child.text
    cur[:] = [copy.deepcopy(ch) for ch in child]
    cur.attrib.update(child.attrib)


def _merge_into(child, cur):
    """Lay one child node over the already-resolved parent node cur, in place."""
    if (child.get("Inherit") or "").strip().lower() == "false":
        _overwrite(child, cur)
        return
    # Either side being a text leaf, or either side being a <li> list, means the
    # child replaces the node outright. Everything else is an element container
    # and merges per child name — including a child that is EMPTY, which is a
    # no-op, not a wipe. (Clearing an inherited list needs Inherit="False";
    # that is the whole reason the attribute exists.)
    if ((child.text or "").strip() or (cur.text or "").strip()
            or _is_list_node(child) or _is_list_node(cur)):
        _overwrite(child, cur)
        return
    cur.attrib.update(child.attrib)
    for ce in child:
        match = cur.find(ce.tag)
        if match is None:
            cur.append(copy.deepcopy(ce))
        else:
            _merge_into(ce, match)
            # NOTE: cur.find() returns the FIRST match, so a def that declares
            # the same container twice (three Mythic Ages animals declare
            # <comps> twice) folds the second onto the first and the second
            # wins — which is what RimWorld does, since it assigns the field
            # once per node. Do not "fix" this into a merge.


def _walk_chain(node, by_name):
    """
    Walk a def's ParentName ancestry without copying anything.

    Returns (ancestors, chain, unresolved):
      ancestors  - the ancestor ELEMENTS, nearest parent first
      chain      - their Names, same order and (barring a break) same length
      unresolved - the ParentName that could not be followed, or ""

    Two failure modes are reported rather than swallowed: a ParentName with no
    matching Name anywhere in the load set, and a cycle (or a chain longer than
    INHERIT_MAX_DEPTH). Both land in `unresolved`. This is cheap — dict lookups
    only — so it runs eagerly for every def in the load set.
    """
    chain, ancestors, visited, unresolved = [], [], set(), ""
    n = node
    while len(chain) < INHERIT_MAX_DEPTH:
        pn = (n.get("ParentName") or "").strip()
        if not pn:
            break
        if pn in visited:                       # cycle
            unresolved = pn
            break
        visited.add(pn)
        p = by_name.get(pn)
        if p is None:                           # parent defined by no active mod
            unresolved = pn
            break
        chain.append(pn)
        ancestors.append(p)
        n = p
    else:
        unresolved = (n.get("ParentName") or "").strip()   # depth cap hit
    return ancestors, chain, unresolved


def resolve_inherit(node, by_name, cache, walked=None):
    """
    Merge a def with its whole ParentName ancestry.

    Returns (resolved element, chain, unresolvedParent). The chain is listed
    nearest parent first. The resolved element is always a fresh copy unless the
    def has no parent at all, so the indexed source nodes are never mutated —
    which is what makes lazy resolution safe.

    `cache` maps an abstract Name to its own fully resolved element, so a base
    shared by 400 defs is merged once. `walked` is the (ancestors, chain,
    unresolved) triple from _walk_chain if the caller already has it.
    """
    ancestors, chain, unresolved = walked or _walk_chain(node, by_name)

    if not ancestors:
        return node, chain, unresolved

    # Start from the nearest ancestor whose own resolution is already cached;
    # everything above it is already folded into that cached element.
    base, start = None, None
    for i, pn in enumerate(chain):
        if pn in cache:
            base = cache[pn][0]
            start = i
            break
    if base is None:
        base = ancestors[-1]                    # topmost we managed to reach
        remaining = ancestors[:-1]
    else:
        remaining = ancestors[:start]

    resolved = copy.deepcopy(base)
    for anc in reversed(remaining):             # farthest first, nearest last
        for k in _INHERIT_ATTRS:
            resolved.attrib.pop(k, None)
        _merge_into(anc, resolved)
    for k in _INHERIT_ATTRS:
        resolved.attrib.pop(k, None)
    _merge_into(node, resolved)
    resolved.attrib.clear()
    resolved.attrib.update(node.attrib)

    name = (node.get("Name") or "").strip()
    # Cache the load-order winner only, and never a broken chain: a cycle
    # resolves differently depending on where you entered it.
    if name and not unresolved and by_name.get(name) is node:
        cache[name] = (resolved, chain, unresolved)
    return resolved, chain, unresolved


# ---------------------------------------------------------------- dict view
def element_to_dict(el):
    """
    A resolved element as plain nested Python (JSON-ready).

    Shape rules, chosen so the result diffs cleanly and loses nothing that
    carries meaning:

      * leaf with no attributes            -> its text, as a string ("" if empty)
      * every child is <li>                -> a LIST of converted children
      * otherwise                          -> a dict keyed by child tag

    ATTRIBUTES ARE DATA, not decoration, and are the easiest thing to lose here.
    `<deathAction Class="DeathActionProperties_Divide"/>` and
    `<li Class="CompProperties_Milkable">` both carry their real payload in the
    attribute; a converter that keeps only element text silently drops 14 of the
    77 defs with a death action and every comp that uses the short form. So
    attributes are emitted as "@Name" keys, and a leaf that HAS attributes
    becomes a dict with its text under "#text".

    Duplicate non-<li> child tags collapse LAST-WINS, matching both the game
    (it assigns the field once per node, so the last block wins) and the merge
    semantics above. A handful of real mods ship such defs; the earlier block is
    dead XML in game and is dead here too.
    """
    kids = list(el)
    attrs = {("@" + k): v for k, v in el.attrib.items()}

    if not kids:
        text = (el.text or "").strip()
        if not attrs:
            return text
        out = dict(attrs)
        if text:
            out["#text"] = text
        return out

    if all(ch.tag == "li" for ch in kids):
        items = [element_to_dict(ch) for ch in kids]
        if not attrs:
            return items
        out = dict(attrs)
        out["li"] = items
        return out

    out = dict(attrs)
    lis = []
    for ch in kids:
        if ch.tag == "li":                      # mixed container: keep them all
            lis.append(element_to_dict(ch))
        else:
            out[ch.tag] = element_to_dict(ch)   # last wins, see docstring
    if lis:
        out["li"] = lis
    text = (el.text or "").strip()
    if text:
        out["#text"] = text
    return out


# ---------------------------------------------------------------- records
class DefRecord(object):
    """
    One def node, its provenance, and its place in the inheritance graph.

    `.own` is the def's raw declared element. `.element` is that element with
    its whole ParentName ancestry merged in — the one a projection should read.
    Resolution is lazy and memoised; `release()` drops the memo when you are
    streaming a large dump and do not want 51k merged trees resident at once.
    """

    __slots__ = ("defType", "defName", "key", "abstractName", "parentName",
                 "modName", "packageId", "workshopId", "loadOrder", "sourceFile",
                 "own", "inheritDepth", "inheritChain", "unresolvedParent",
                 "duplicateOwners", "_ds", "_walked", "_resolved")

    def __init__(self, defType, defName, key, node, mod, rel, walked):
        self.defType = defType
        self.defName = defName
        self.key = key
        self.abstractName = (node.get("Name") or "").strip()
        self.parentName = (node.get("ParentName") or "").strip()
        self.modName = mod["name"]
        self.packageId = mod["packageId"]
        self.workshopId = mod["workshopId"]
        self.loadOrder = mod["order"]           # 1-based; see the CLI note
        self.sourceFile = rel
        self.own = node
        self.duplicateOwners = []               # filled after the scan
        self._ds = None
        self._walked = walked
        self.inheritChain = list(walked[1])
        self.inheritDepth = len(self.inheritChain)
        self.unresolvedParent = walked[2]
        self._resolved = None

    @property
    def isAbstract(self):
        """RimWorld treats Abstract="True" as 'never instantiate, only inherit'."""
        return (self.own.get("Abstract") or "").strip().lower() == "true"

    @property
    def element(self):
        """The inheritance-RESOLVED element. This is the interface projections use."""
        if self._resolved is None:
            resolved, _, _ = resolve_inherit(
                self.own, self._ds.by_name, self._ds._cache, self._walked)
            self._resolved = resolved
        return self._resolved

    def release(self):
        """Drop the memoised resolution (the merge is cheap to redo, RAM is not)."""
        self._resolved = None

    @property
    def label(self):
        return txt(self.element, "label")

    @property
    def shortHashCandidate(self):
        return short_hash(self.defName)

    def as_dict(self, include_xml=True):
        """
        The record as JSON-ready plain data.

        Field names deliberately mirror src/RimMandrake/RimDefDump (defName, defType,
        label, modName, packageId) so the offline and live dumps of the same mod
        set join on the obvious keys. The nested resolved XML lives under "def"
        rather than being splatted at the top level, so provenance keys can
        never be shadowed by a def that happens to declare a <modName> field.
        """
        out = {
            "defName": self.defName,
            "defType": self.defType,
            "label": self.label,
            "modName": self.modName,
            "packageId": self.packageId,
            "workshopId": self.workshopId,
            "loadOrder": self.loadOrder,
            "sourceFile": self.sourceFile.replace("\\", "/"),
            "shortHashCandidate": self.shortHashCandidate,
            "abstractName": self.abstractName,
            "parentName": self.parentName,
            "isAbstract": self.isAbstract,
            "inheritDepth": self.inheritDepth,
            "inheritChain": self.inheritChain,
            "unresolvedParent": self.unresolvedParent,
            "duplicateOwners": self.duplicateOwners,
        }
        if include_xml:
            out["def"] = element_to_dict(self.element)
        return out

    def __repr__(self):
        return "<DefRecord %s/%s from %s>" % (self.defType, self.defName or self.key,
                                              self.modName)


class DefSet(object):
    """
    The whole resolved def database for one mod set.

    Attributes
      mods            list of mod dicts in LOAD ORDER (rimworld_loadset shape)
      missing         active packageIds with no folder on disk
      gameVersion     the 'major.minor' the load set was resolved against
      records         every DefRecord, in scan (= load) order
      defs            {(defType, key): DefRecord} — LAST in load order wins
      by_type         {defType: [DefRecord, ...]}
      by_name         {Name: raw element} — the GLOBAL abstract-parent index
      typeCounts      {defType: n} over EVERY def node seen, even filtered-out
                      ones, so --types never distorts the census
      fileCount / defNodeCount / abstractCount / nonDefsRootFiles
      nameCollisions  {Name: [defType, ...]} where one Name is claimed by more
                      than one def type — see the note on by_name below
      timings         {phase: seconds}

    `key` is the defName, or "<abstract:Name>" for an abstract def that declares
    no defName (RimWorld allows that; ~1.9k defs in this stack are abstract),
    or "<anon:file#i>" for the pathological node with neither.
    """

    def __init__(self):
        self.mods = []
        self.missing = []
        self.gameVersion = ""
        self.records = []
        self.defs = {}
        self.by_type = defaultdict(list)
        self.by_name = {}
        self.typeCounts = Counter()
        self.fileCount = 0
        self.defNodeCount = 0
        self.abstractCount = 0
        self.nonDefsRootFiles = 0
        self.nameCollisions = {}
        self.timings = {}
        self._cache = {}                        # Name -> (resolved, chain, unresolved)

    # -- lookups ---------------------------------------------------------
    def get(self, defType, defName):
        return self.defs.get((defType, defName))

    def of_type(self, defType):
        return self.by_type.get(defType, [])

    def types(self):
        return sorted(self.by_type)

    def depth_histogram(self):
        h = Counter(r.inheritDepth for r in self.records)
        return dict(sorted(h.items()))

    def unresolved(self):
        return [r for r in self.records if r.unresolvedParent]

    def duplicates(self):
        """Records whose (defType, defName) was declared by more than one mod."""
        return [r for r in self.records if len(r.duplicateOwners) > 1]

    def release(self):
        for r in self.records:
            r.release()
        self._cache.clear()


# ---------------------------------------------------------------- scan
def build(config=D_CONFIG, workshop=D_WORKSHOP, local=D_LOCAL, data=D_DATA,
          types=None, quiet=True, roots=None):
    """
    Resolve the load set, scan every def XML in it, and return a DefSet.

    `types` restricts which def types get a DefRecord — a fast-iteration lever,
    nothing more. It does NOT restrict the parse (every file is read regardless,
    because a parent may live in any file) and it does NOT restrict `by_name`
    or `typeCounts`. Filtering the inheritance index would silently break
    resolution for the types you did keep.

    Two passes, and they are not optional. PASS A reads every file once and
    indexes every node that carries a Name attribute; PASS B walks each def's
    ParentName chain against that index. A parent may be declared by a mod that
    loads AFTER its children, and RimWorld likewise resolves inheritance only
    once all XML is in.
    """
    t0 = time.perf_counter()
    ds = DefSet()
    want = set(types) if types else None

    try:
        mods, missing, version = build_load_set(config, roots or [workshop, local, data])
    except OSError as exc:
        raise SystemExit(str(exc))
    ds.mods, ds.missing, ds.gameVersion = mods, missing, version
    ds.timings["loadset"] = time.perf_counter() - t0
    if not quiet:
        ndirs = sum(len(m["contentDirs"]) for m in mods)
        print("load set: version %s, %d active mods -> %d content folders "
              "(%d unresolved packageIds)" % (version, len(mods), ndirs, len(missing)))

    # ---- pass A: read every file once, index every Name --------------------
    #
    # The Name index is GLOBAL, across all def types, on purpose. Name /
    # ParentName is an XML-layer mechanism in RimWorld (XmlInheritance runs over
    # the raw node graph before anything knows what a "ThingDef" is), so a
    # ParentName resolves against every named node in the load set, not just the
    # ones of the same type. animal_inventory.py indexes ThingDefs only, which
    # is correct for its narrower question but would be wrong here.
    t1 = time.perf_counter()
    staged = []                                  # (tag, node, mod, rel, order)
    name_types = defaultdict(set)
    for m in mods:
        for d in def_dirs(m, "Defs"):
            for path in walk_xml(d):
                root = parse_xml(path)
                if root is None:
                    continue
                ds.fileCount += 1
                if root.tag != "Defs":
                    # RimWorld only loads <Defs> documents out of Defs/. Count
                    # these so a surprising number is visible rather than a
                    # silent omission.
                    ds.nonDefsRootFiles += 1
                    continue
                rel = os.path.relpath(path, m["folder"])
                for i, node in enumerate(root):
                    ds.defNodeCount += 1
                    ds.typeCounts[node.tag] += 1
                    name = (node.get("Name") or "").strip()
                    if name:
                        ds.by_name[name] = node  # last in load order wins
                        name_types[name].add(node.tag)
                    if (node.get("Abstract") or "").strip().lower() == "true":
                        ds.abstractCount += 1
                    if want is None or node.tag in want:
                        staged.append((node, m, rel, i))
    ds.nameCollisions = {n: sorted(t) for n, t in name_types.items() if len(t) > 1}
    ds.timings["scan"] = time.perf_counter() - t1

    # ---- pass B: walk the inheritance chains, build the records -------------
    # Only the CHAIN is walked here (dict lookups, no copying). The actual merge
    # is deferred to first access of .element so that --summary and the depth
    # histogram do not pay for 51k deepcopies.
    t2 = time.perf_counter()
    owners = defaultdict(list)
    by_key = defaultdict(list)
    for node, m, rel, idx in staged:
        # defName / Name / ParentName are read off the def's OWN element on
        # purpose. Taking them post-merge would hand an abstract-only def its
        # parent's defName and make abstract records indistinguishable.
        dn = txt(node, "defName")
        name = (node.get("Name") or "").strip()
        if dn:
            key = dn
        elif name:
            key = "<abstract:%s>" % name
        else:
            key = "<anon:%s#%d>" % (rel.replace("\\", "/"), idx)
        rec = DefRecord(node.tag, dn, key, node, m, rel,
                        _walk_chain(node, ds.by_name))
        rec._ds = ds
        ds.records.append(rec)
        ds.by_type[node.tag].append(rec)
        ds.defs[(node.tag, key)] = rec           # last in load order wins
        owners[(node.tag, key)].append(m["name"])
        by_key[(node.tag, key)].append(rec)

    # duplicateOwners is recorded, never adjudicated — see "what this cannot
    # see". Every record sharing a key gets the full owner list, so a row that
    # LOST an override still tells you it was contested.
    for k, mlist in owners.items():
        if len(mlist) > 1:
            uniq = sorted(set(mlist))
            for r in by_key[k]:
                r.duplicateOwners = uniq
    ds.timings["resolve_chains"] = time.perf_counter() - t2
    ds.timings["total_build"] = time.perf_counter() - t0

    if not quiet:
        print("scanned %d files -> %d def nodes, %d distinct def types, "
              "%d abstract" % (ds.fileCount, ds.defNodeCount,
                               len(ds.typeCounts), ds.abstractCount))
    return ds


# ---------------------------------------------------------------- CLI
def _write_json(path, obj, indent):
    # No BOM: RimDefDump writes plain utf-8 and the diff layer reads both.
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False,
                  indent=indent if indent else None,
                  separators=None if indent else (",", ":"))
        fh.write("\n")


def _manifest(ds, mode, out_types, timings, counts):
    return {
        "tool": "def_inventory.py",
        "toolVersion": VERSION,
        "source": "offline",
        "mode": mode,
        "capturedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gameVersion": ds.gameVersion,
        "note": ("Base XML with <ParentName> inheritance resolved. "
                 "PatchOperations have NOT run and MayRequire is not evaluated. "
                 "loadOrder is 1-based here, 0-based in RimDefDump's manifest."),
        "timingsMs": {k: int(v * 1000) for k, v in timings.items()},
        "mods": [{"loadOrder": m["order"], "name": m["name"],
                  "packageId": m["packageId"], "workshopId": m["workshopId"],
                  "rootDir": m["folder"],
                  "contentDirs": [os.path.relpath(c, m["folder"]).replace("\\", "/")
                                  for c in m["contentDirs"]]}
                 for m in ds.mods],
        "modCount": len(ds.mods),
        "missingPackageIds": ds.missing,
        "totals": {
            "defFiles": ds.fileCount,
            "nonDefsRootFiles": ds.nonDefsRootFiles,
            "defNodes": ds.defNodeCount,
            "defTypes": len(ds.typeCounts),
            "abstractDefs": ds.abstractCount,
            "recordsWritten": sum(counts.values()),
            "typesWritten": len(counts),
            "unresolvedParents": len(ds.unresolved()),
            "contestedKeys": len({r.key for r in ds.duplicates()}),
            "crossTypeNameCollisions": len(ds.nameCollisions),
        },
        "defCountsAll": dict(sorted(ds.typeCounts.items())),
        "defCounts": dict(sorted(counts.items())),
        "typesRequested": out_types,
        "inheritDepthHistogram": ds.depth_histogram(),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Offline dump of the whole modded def database, "
                    "<ParentName> inheritance resolved.")
    ap.add_argument("--config", default=D_CONFIG)
    ap.add_argument("--workshop", default=D_WORKSHOP)
    ap.add_argument("--local", default=D_LOCAL)
    ap.add_argument("--data", default=D_DATA)
    ap.add_argument("--out", default=None,
                    help="write defs/<DefType>.json + manifest.json here")
    ap.add_argument("--types", default=None,
                    help="comma-separated def types to keep (e.g. ThingDef,GeneDef)")
    ap.add_argument("--summary", action="store_true",
                    help="print per-type counts and the inheritance histogram; "
                         "write nothing")
    ap.add_argument("--indent", type=int, default=0,
                    help="JSON indent (0 = compact, much smaller on disk)")
    a = ap.parse_args(argv)

    if not a.out and not a.summary:
        ap.error("nothing to do: pass --out DIR or --summary")

    types = [t.strip() for t in a.types.split(",") if t.strip()] if a.types else None
    ds = build(a.config, a.workshop, a.local, a.data, types=types, quiet=False)

    hist = ds.depth_histogram()
    unres = ds.unresolved()
    print("inheritDepth histogram: " +
          "  ".join("%d:%d" % (k, v) for k, v in hist.items()))
    print("defs with an unresolved ParentName: %d" % len(unres))
    if ds.nameCollisions:
        print("cross-type abstract Name collisions: %d (e.g. %s)"
              % (len(ds.nameCollisions),
                 ", ".join("%s=%s" % (n, "/".join(t))
                           for n, t in list(sorted(ds.nameCollisions.items()))[:3])))

    if a.summary:
        print("\n%-44s %8s %8s" % ("defType", "records", "allNodes"))
        for t in sorted(ds.typeCounts, key=lambda x: (-ds.typeCounts[x], x)):
            print("%-44s %8d %8d" % (t, len(ds.of_type(t)), ds.typeCounts[t]))
        print("\n%d def types, %d def nodes, %d files, %d abstract, "
              "%d contested keys"
              % (len(ds.typeCounts), ds.defNodeCount, ds.fileCount,
                 ds.abstractCount, len({r.key for r in ds.duplicates()})))
        print("timings: " + "  ".join("%s=%.2fs" % (k, v)
                                      for k, v in ds.timings.items()))
        return 0

    # ---- raw dump, mirroring RimDefDump's layout ---------------------------
    t = time.perf_counter()
    defs_dir = os.path.join(a.out, "defs")
    os.makedirs(defs_dir, exist_ok=True)
    counts = {}
    for dt in ds.types():
        recs = ds.of_type(dt)
        payload = {"defType": dt, "source": "offline",
                   "defs": [r.as_dict() for r in recs], "count": len(recs)}
        _write_json(os.path.join(defs_dir, dt + ".json"), payload, a.indent)
        counts[dt] = len(recs)
        for r in recs:                       # do not hold 51k merged trees
            r.release()
    ds.timings["write"] = time.perf_counter() - t
    ds.timings["total"] = ds.timings["total_build"] + ds.timings["write"]

    _write_json(os.path.join(a.out, "manifest.json"),
                _manifest(ds, "all" if types is None else "types",
                          types, ds.timings, counts), 2)

    size = 0
    for dp, _, files in os.walk(a.out):
        for f in files:
            size += os.path.getsize(os.path.join(dp, f))
    print("\nwrote %d type files (%d defs) + manifest.json to %s"
          % (len(counts), sum(counts.values()), os.path.abspath(a.out)))
    print("on disk: %.1f MB    timings: %s" %
          (size / 1048576.0,
           "  ".join("%s=%.2fs" % (k, v) for k, v in ds.timings.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
