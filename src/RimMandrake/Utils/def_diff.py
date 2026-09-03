#!/usr/bin/env python3
"""
def_diff.py — the generic offline<->live def diff, across ALL def types.

VERSION 1.0  (2026-08-10)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Docs/manifest: src/RimMandrake/Utils/README.md  ("def_diff.py" section)
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

CHANGELOG
  1.0  first cut. LAYER 3 of the three-layer design. Generalises
       animal_live_diff.py (v1.0, animals-only, curated column list) from
       1,243 animals to the whole def database, and swaps its FIELD_MAP for a
       generic path-walk: every leaf the offline XML actually declares is
       looked up in the live reflected object and compared. The point of going
       generic is catching patches to fields nobody thought to curate — a
       curated column list can only ever confirm what you already suspected.

WHAT THIS IS
============
  layer 1  def_inventory.py   offline: load set + <ParentName> inheritance
  layer 2  animal_inventory.py  projection: curation for one category
  layer 3  THIS FILE          offline (base XML) vs live (post-patch DefDatabase)

The offline side knows which mod and which xpath to patch. The live side (a
`src/RimMandrake/RimDefDump` dump, mode=all) knows what actually resulted after every
PatchOperation ran and every cross-reference resolved. Neither is the truth on
its own; the join is the deliverable, and it retires four documented offline
limitations at once:

  * PatchOperation results        -> field deltas on matched defs
  * mod-vs-mod override winners   -> modName disagreements (settles the 375
                                     contested keys in vendor/wisdom/def_override_clusters.md)
  * shortHashCandidate is a guess -> checked against the real shortHash
  * "is this a weapon?" is guessed-> the live `is` block CALIBRATES the guess,
                                     and the accuracy is reported as a number

USAGE
=====
    python src/RimMandrake/Utils/def_diff.py --live "<DefDump dir>" [--types ThingDef,GeneDef]
                             [--out DIR]
    python src/RimMandrake/Utils/def_diff.py --selftest

OUTPUTS (to --out, default ./out)
    def_divergence.csv      one row per def, with status, identity checks, deltas
    def_diff_summary.csv    per defType, counts of every status
    classifier_accuracy.csv per category, how often the offline guess is right
    console                 the part actually read

THE STATUS VOCABULARY — and why each expected asymmetry gets its own bucket
==========================================================================
The single way to make this report worthless is to let expected asymmetries
outnumber real findings. RimWorld GENERATES thousands of defs at load that exist
in no XML, and the offline scan legitimately holds thousands of defs that can
never be live. Reported raw, that is ~10k rows of noise around a few hundred
rows of signal. So every known asymmetry is classified, never dropped, and the
`rule` column names the rule that did it so a reader can disagree with it.

  both               present both sides. Read deltaCount.
  category_mismatch  present both sides, AND the offline category classifier
                     disagrees with the engine's `is` block. A specialisation of
                     `both` (deltas are still computed and reported on the same
                     row). This is a statement about OUR classifier, not about
                     the game — see CLASSIFIER CALIBRATION below.
  live_only          the game has it, no XML declares it, and no generator rule
                     explains it. THIS IS THE INTERESTING BUCKET: a def created
                     by a PatchOperation, or a generator we have not modelled.
  live_generated     the game has it and a named rule explains it (corpse, meat,
                     leather, blueprint, frame, make-recipe...). Expected.
  offline_only       XML declares it, the game does not have it. Interesting:
                     patch-removed, or lost to a mod-vs-mod override.
  offline_abstract   Abstract="True" and/or a Name= node with no defName. These
                     exist to be inherited from and are NEVER registered as
                     defs. ~1.9k of them in this stack. Expected, not a finding.
  offline_mayrequire XML declares it behind MayRequire / MayRequireAnyOf naming
                     a packageId that is not in the load set. def_inventory does
                     not evaluate MayRequire; this bucket turns that documented
                     limitation into an explained category rather than noise.

VALUE COMPARISON IS DELIBERATELY TOLERANT
=========================================
Offline values are XML TEXT. Live values are typed JSON out of C# reflection.
Compared naively, everything disagrees. The rules (extending
animal_live_diff.values_agree):

  * numbers compare with a relative tolerance (float pipeline vs text pipeline)
  * booleans normalise across True/true/1
  * an EMPTY offline value is "no opinion", never a disagreement
  * live Defs are collapsed to a defName string by the reflector, so a
    <bloodDef>Filth_Blood</bloodDef> lines up with the string it emits
  * live enums are their names, which is also what the XML holds
  * live dictionaries are [{key,value}] arrays (DefReflector special-cases
    IDictionary because KeyValuePair exposes Key/Value as PROPERTIES) — so
    race.wildBiomes offline-as-a-dict resolves against them
  * offline FloatRange/IntRange text "1~3" resolves against the live
    {min,max} object
  * every reflector SENTINEL (<maxdepth:>, <cycle:>, <truncated>, <skipped:>,
    <read-failed:>, <write-failed:>, <enumerate-failed:>, <failed:>) is treated
    as "the dump declined to answer" and NEVER produces a delta
  * a shape mismatch (offline leaf vs live container, or a path the live object
    simply does not have) is skipped, not reported

The safety property that makes generic comparison usable at all: **failing to
resolve a path yields silence, never a delta.** Under-reporting is recoverable;
a report that cries wolf 4,000 times is not.

CLASSIFIER CALIBRATION (the `is` block)
=======================================
`ThingDef.IsWeapon` is C# logic, not an XML field. Offline can only approximate
category from XML shape. The live `is` block is the engine's own computed
answer, so classifier_accuracy.csv reports, per category, how often the offline
guess matches ground truth. That number is a deliverable in itself: it says how
much to trust an offline category filter, which is the thing every future
projection layer (weapons, apparel) will be built on.

MEMORY
======
defs/ThingDef.json is expected at ~100-400 MB. This tool processes **one def
type at a time** and never holds two live type files at once; within a type the
live defs are read by an INCREMENTAL parser (find `"defs": [`, then repeated
JSONDecoder.raw_decode over a bounded refill buffer), so peak live-side memory
is one def object plus the buffer, not the file. On the offline side, a matched
def's `.element` is resolved, converted, compared and `release()`d immediately,
so the 51k merged XML trees are never all resident either.

LIMITATIONS — read these before believing a number
==================================================
  * List deltas are limited. Leaves are compared by INDEX (comps.0.milkDef),
    which is correct only while list order survives the load — it does for
    XML-declared lists, but C# can append. A PatchOperationAdd shows up as a
    `#count` delta (suppressible with --no-list-counts); a PatchOperationRemove
    on a list may show up as nothing at all, because the offline index simply
    fails to resolve and failure is silent by design.
  * The generator rules (live_generated) are PATTERNS, not the engine's actual
    generator list. They are named in the `rule` column precisely so they can be
    challenged against real data. A wrong rule hides a real live_only.
  * The offline category classifier is an approximation by construction. Its
    error rate is the point of classifier_accuracy.csv, not a defect to hide.
  * C#-side defaults are invisible offline, so a field the XML never mentions is
    never compared. This tool can prove a declared value was CHANGED; it cannot
    prove an undeclared value is what you think.
  * Duplicate live defNames within one type are not possible (DefDatabase is
    keyed), but duplicate offline declarations are: the LAST in load order wins
    here, matching def_inventory. The `contested` column flags those rows.
  * MayRequire is evaluated only on the def's OWN root node, not on inherited
    <li> children. A def gated by a MayRequire on an ancestor is not bucketed.

SELF-TEST — 71 assertions, two phases
=====================================
    python src/RimMandrake/Utils/def_diff.py --selftest

Phase 1 builds a synthetic live dump in the EXACT schema DefDumper.cs emits
(identity block, `is` block on ThingDefs only, `fields` with "$type", nulls
omitted, Defs collapsed to defName strings, enums as names, dictionaries as
[{key,value}], every sentinel form) plus duck-typed offline records, and asserts
every classification, every tolerance rule and every identity check.

Phase 2 writes a minimal but REAL mod tree — ModsConfig.xml, About/About.xml,
Defs/ with an abstract base and a ParentName child — and runs the production
`run()` against it, so def_inventory.build(), inheritance resolution and the
DefRecord interface are covered too. Phase 1 alone would pass even if the
adapter to layer 1 were broken.

This is what makes the tool trustworthy before paying a ~23 minute game load.
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

# element_to_dict is the ONLY thing we need from layer 1's dict view, but the
# offline side is otherwise def_inventory.build() wholesale. Same sys.path dance
# def_inventory itself uses so this runs from any cwd.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from def_inventory import (build, element_to_dict,  # noqa: E402
                           short_hash as _short_hash,
                           D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA)

VERSION = "1.0"

# ---------------------------------------------------------------- tolerances
# Same constants animal_live_diff.py shipped with. A stat that survives a float
# pipeline in the game and a text pipeline on disk will not compare equal, and
# exact equality would report thousands of meaningless deltas.
REL_TOL = 1e-3
ABS_TOL = 1e-6

# Depth cap for the offline flatten. DefReflector's own cap is 6 (DefaultMaxDepth),
# below which it emits <maxdepth:...>; going deeper offline just produces paths
# that can never resolve, so 8 is generous headroom and nothing more.
MAX_DEPTH = 8

# A pathological def (a 4096-item list, the reflector's own cap) should not be
# allowed to produce 4096 comparisons. Truncation is recorded, never silent.
MAX_PATHS_PER_DEF = 4000

# Sentinels DefReflector emits when it declines to answer. Every one of these
# means "the dump does not know", so it can never be a delta. Kept as a prefix
# set rather than full strings because most carry a type name payload.
SENTINEL_PREFIXES = (
    "<maxdepth:", "<cycle:", "<truncated>", "<skipped:",
    "<read-failed:", "<write-failed:", "<enumerate-failed:", "<failed:",
)

# XML machinery that describes a node's place in the inheritance graph rather
# than any field of the def. def_inventory strips these from resolved elements
# already, but a def's OWN attributes survive onto `.element`. NOTE: @Class is
# deliberately NOT here — unlike these, it is real field data (which concrete
# C# class a comp/verb/li is), and compare_def()/live_step() below have their
# own special-case handling to diff it against the live "$type". Filtering it
# here at every depth (not just root) silently discarded it before that
# handling could ever see it.
SKIP_ATTR_KEYS = frozenset((
    "@ParentName", "@Name", "@Abstract", "@Inherit",
    "@MayRequire", "@MayRequireAnyOf",
))
# defName is the join key; comparing it against itself proves nothing.
SKIP_ROOT_KEYS = frozenset(("defName",))

# Live lists of objects are frequently keyed collections in disguise
# (List<StatModifier> is written as [{$type,stat,value}, ...] but the XML for it
# is <statBases><MoveSpeed>4.5</MoveSpeed></statBases>, i.e. a dict). These field
# names are how an item announces which key it is. Purely additive: if none
# matches, the lookup fails and the comparison is skipped, so a wrong guess here
# costs coverage, never correctness.
KEYISH_FIELDS = ("key", "stat", "def", "defName", "skill", "thing", "thingDef",
                 "hediff", "bodyPart", "bodyPartGroup", "tag", "name", "trait",
                 "gene", "recipe", "capacity", "damageDef", "activity")
VALUEISH_FIELDS = ("value", "count", "amount", "offset", "factor", "weight",
                   "commonality", "chance", "level", "severity")

_MISSING = object()

# Offline text form of a FloatRange/IntRange: "1~3", "0.5~1.5", "-3~4".
_RANGE_RE = re.compile(r"^\s*(-?[0-9.]+)\s*~\s*(-?[0-9.]+)\s*$")


# ---------------------------------------------------------------- comparison
def fnum(s):
    try:
        return float(str(s).strip())
    except Exception:
        return None


def norm_bool(s):
    t = str(s).strip().lower()
    if t in ("true", "1"):
        return "true"
    if t in ("false", "0"):
        return "false"
    return None


def is_sentinel(v):
    """True for any value DefReflector wrote instead of an answer."""
    if not isinstance(v, str):
        return False
    return v.endswith(">") and v.startswith(SENTINEL_PREFIXES)


def values_agree(offline, live):
    """
    True when the XML text and the reflected live value mean the same thing.

    Lenient in exactly the ways that would otherwise generate pure noise; see
    the module docstring. Returns True for anything it cannot adjudicate, which
    is the design: silence beats a false accusation.
    """
    if live is None or is_sentinel(live):
        return True                       # the dump declined to answer
    o = "" if offline is None else str(offline).strip()
    if o == "":
        return True                       # offline had nothing to say

    # A live container against an offline leaf is a shape mismatch, not a
    # disagreement — except for FloatRange/IntRange, whose offline text form
    # ("1~3") really is comparable to the live {min,max} object.
    if isinstance(live, dict):
        m = _RANGE_RE.match(o)
        if m and "min" in live and "max" in live:
            return (values_agree(m.group(1), live.get("min"))
                    and values_agree(m.group(2), live.get("max")))
        return True
    if isinstance(live, list):
        return True

    if isinstance(live, bool):
        ob = norm_bool(o)
        return ob is None or ob == ("true" if live else "false")

    if isinstance(live, (int, float)):
        of = fnum(o)
        if of is None:
            return True                   # e.g. offline "Auto" vs live 0 — no call
        if abs(of - live) <= ABS_TOL:
            return True
        denom = max(abs(of), abs(live))
        return denom > 0 and abs(of - live) / denom <= REL_TOL

    l = str(live).strip()
    if o == l:
        return True

    # Class names: XML almost always writes the SHORT name
    # (workerClass=BiomeWorker_Tundra) while the reflector writes Type.FullName
    # (RimWorld.BiomeWorker_Tundra). Identical thing, different spelling.
    # Measured on the first real run this was 429 of 1,587 deltas — 27% of
    # everything reported, and every one of them a lie. Compare on the last
    # dotted segment when one side is a namespace-qualified form of the other.
    if "." in l and not fnum(l) and l.rsplit(".", 1)[-1] == o.rsplit(".", 1)[-1]:
        return True

    ob, lb = norm_bool(o), norm_bool(l)
    if ob is not None and lb is not None:
        return ob == lb
    of, lf = fnum(o), fnum(l)
    if of is not None and lf is not None:
        if abs(of - lf) <= ABS_TOL:
            return True
        denom = max(abs(of), abs(lf))
        return denom > 0 and abs(of - lf) / denom <= REL_TOL
    return o.lower() == l.lower()


# ---------------------------------------------------------------- path walk
def live_step(cur, seg):
    """
    Advance one XML path segment into the live reflected object.

    The two representations are not the same shape and this function is where
    that is reconciled. Every branch that cannot reconcile returns _MISSING,
    which the caller turns into silence.
    """
    if isinstance(cur, dict):
        if seg in cur:
            return cur[seg]
        if seg == "@Class":
            # <li Class="CompProperties_Milkable"> vs the reflector's "$type".
            return cur.get("$type", _MISSING)
        return _MISSING

    if isinstance(cur, list):
        # element_to_dict names list children "li"; the live side is a bare
        # array, so "li" is transparent.
        if seg == "li":
            return cur
        if seg.isdigit():
            i = int(seg)
            return cur[i] if i < len(cur) else _MISSING

        # An IDictionary the reflector wrote as [{key,value}].
        for item in cur:
            if not isinstance(item, dict):
                break
            k = item.get("key", _MISSING)
            if k is not _MISSING and str(k) == seg:
                return item.get("value", _MISSING)

        # A List<T> that is really a keyed collection (StatModifier & friends).
        for item in cur:
            if not isinstance(item, dict):
                continue
            for kf in KEYISH_FIELDS:
                kv = item.get(kf)
                if isinstance(kv, str) and kv == seg:
                    for vf in VALUEISH_FIELDS:
                        if vf in item:
                            return item[vf]
                    return item
        return _MISSING

    return _MISSING


def live_lookup(fields, path):
    cur = fields
    for seg in path:
        cur = live_step(cur, seg)
        if cur is _MISSING:
            return _MISSING
    return cur


def flatten_offline(d, list_counts=True, max_depth=MAX_DEPTH,
                    max_paths=MAX_PATHS_PER_DEF):
    """
    element_to_dict output -> [(path_list, value, kind)].

    kind is "scalar" for a leaf the XML actually declares, or "count" for a
    list length. Driving the whole comparison from the OFFLINE side is the
    thing that bounds the noise: we only ever ask about values a mod author
    literally wrote, which is exactly the set a PatchOperation can have moved.
    """
    out = []
    truncated = [False]

    def rec(node, prefix, depth):
        if len(out) >= max_paths:
            truncated[0] = True
            return
        if isinstance(node, str):
            if node != "":
                out.append((prefix, node, "scalar"))
            return
        if isinstance(node, list):
            if list_counts and prefix:
                out.append((prefix, len(node), "count"))
            if depth >= max_depth:
                return
            for i, item in enumerate(node):
                rec(item, prefix + [str(i)], depth + 1)
            return
        if isinstance(node, dict):
            if depth >= max_depth:
                return
            for k, v in node.items():
                if k in SKIP_ATTR_KEYS:
                    continue
                if depth == 0 and k in SKIP_ROOT_KEYS:
                    continue
                rec(v, prefix + [k], depth + 1)

    rec(d, [], 0)
    return out, truncated[0]


def _short_class(s):
    return str(s).rsplit(".", 1)[-1]


def compare_def(off_dict, live_fields, list_counts=True):
    """
    Generic field-level diff for one matched def.

    Returns (deltas, skipped) where deltas is a list of "path: offline -> live"
    strings and skipped counts paths the live object did not have (shape
    mismatch or a field the reflector omitted because it was null).
    """
    deltas, skipped = [], 0
    paths, truncated = flatten_offline(off_dict, list_counts=list_counts)
    for path, val, kind in paths:
        if kind == "count":
            lv = live_lookup(live_fields, path)
            if lv is _MISSING or not isinstance(lv, list):
                skipped += 1
                continue
            if len(lv) != val:
                deltas.append("%s.#count: %d -> %d" % (".".join(path), val, len(lv)))
            continue

        lv = live_lookup(live_fields, path)
        if lv is _MISSING:
            skipped += 1
            continue
        if path and path[-1] == "@Class":
            # Class="Namespace.CompProperties_X" vs $type="CompProperties_X".
            if _short_class(val) != _short_class(lv) and not is_sentinel(lv):
                deltas.append("%s: %s -> %s" % (".".join(path), val, lv))
            continue
        if not values_agree(val, lv):
            deltas.append("%s: %s -> %s" % (".".join(path), val, lv))
    if truncated:
        deltas.append("<offline-paths-truncated at %d>" % MAX_PATHS_PER_DEF)
    return deltas, skipped


# ---------------------------------------------------------------- live reader
def iter_live_defs(path, chunk=4 << 20):
    """
    Stream the `defs` array of a defs/<Type>.json without loading the file.

    defs/ThingDef.json is expected at 100-400 MB; json.load on that is several
    GB of Python objects and there is no reason to hold more than one def at a
    time. This finds the `"defs"` member, then walks the array with repeated
    JSONDecoder.raw_decode over a refill buffer that is trimmed as it is
    consumed. A decode failure that is merely truncation is retried after a
    refill; a genuine syntax error still raises at EOF.
    """
    dec = json.JSONDecoder()
    with io.open(path, encoding="utf-8") as fh:
        buf = fh.read(chunk)
        i = buf.find('"defs"')
        while i < 0:
            more = fh.read(chunk)
            if not more:
                return
            buf += more
            i = buf.find('"defs"')
        i = buf.index(":", i) + 1

        eof = False
        while True:                                  # skip to '['
            while i < len(buf) and buf[i] in " \t\r\n":
                i += 1
            if i < len(buf):
                break
            more = fh.read(chunk)
            if not more:
                return
            buf += more
        if buf[i] != "[":
            raise ValueError("%s: 'defs' is not an array" % path)
        i += 1

        while True:
            while True:                              # skip whitespace/commas
                while i < len(buf) and buf[i] in " \t\r\n,":
                    i += 1
                if i < len(buf) or eof:
                    break
                more = fh.read(chunk)
                if not more:
                    eof = True
                else:
                    buf += more
            if i >= len(buf) or buf[i] == "]":
                return
            while True:
                try:
                    obj, end = dec.raw_decode(buf, i)
                    break
                except ValueError:
                    more = fh.read(chunk)
                    if not more:
                        raise
                    buf += more
            yield obj
            i = end
            if i >= chunk:                           # amortised buffer trim
                buf = buf[i:]
                i = 0


def load_manifest(live_dir):
    p = os.path.join(live_dir, "manifest.json")
    if not os.path.isfile(p):
        return {}
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- generated
# RimWorld GENERATES defs at load that exist in no XML anywhere. On the first
# full animals run, generated Corpse_* ThingDefs alone were 2,345 records — 49%
# of the file. Reported as live_only they would drown every real finding, so
# they are bucketed as live_generated WITH THE RULE NAMED, never dropped.
#
# Rules are ordered: the `is` block is the engine's own answer and beats a
# prefix guess. A prefix rule is strengthened to "<rule>+known-def" when the
# remainder after the prefix is a defName the offline scan really saw, which is
# the generator's own construction and therefore strong evidence.
GENERATOR_PREFIXES = (
    ("Corpse_", "corpse"),
    ("Meat_", "meat"),
    ("Leather_", "leather"),
    ("Blueprint_Install_", "blueprint-install"),
    ("Blueprint_Terrain_", "blueprint-terrain"),
    ("Blueprint_", "blueprint"),
    ("Frame_", "frame"),
    ("Make_", "recipe-make"),          # RecipeDef generated from <recipeMaker>
    ("Psytrainer_", "psytrainer"),     # ThingDefGenerator_Neurotrainer
    ("Neurotrainer_", "neurotrainer"),
)
_IS_FLAG_RULES = (("corpse", "is.corpse"), ("blueprint", "is.blueprint"),
                  ("frame", "is.frame"))


def generated_rule(defName, is_block, all_offline_names):
    """Name the rule that explains a live-only def, or return '' for none."""
    if isinstance(is_block, dict):
        for flag, rule in _IS_FLAG_RULES:
            if is_block.get(flag) is True:
                return rule
    for prefix, rule in GENERATOR_PREFIXES:
        if defName.startswith(prefix) and len(defName) > len(prefix):
            rest = defName[len(prefix):]
            if rest in all_offline_names:
                return rule + "+known-def"
            return rule
    return ""


# ---------------------------------------------------------------- classifier
# The offline approximation of the engine's computed category properties. Every
# one of these is a GUESS from XML shape; the live `is` block is the truth, and
# classifier_accuracy.csv reports how often the guess is right. That number is
# the deliverable — do not "fix" a category by making it agree with the live
# answer per-def, which would just launder the error.
#
# The C# each line is approximating (Verse.ThingDef / RaceProperties):
#   IsWeapon            category == Item && (verbs any || tools any)
#   IsRangedWeapon      IsWeapon && a verb has a projectile
#   IsMeleeWeapon       IsWeapon && !IsRangedWeapon
#   IsApparel           apparel != null
#   IsPlant             category == Plant
#   IsStuff             stuffProps != null
#   IsMedicine          statBases contains MedicalPotency
#   IsDrug              ingestible != null && drugCategory != None
#   IsBuildingArtificial category == Building && !building.isNaturalRock
#   Minifiable          minifiedDef != null
#   race.Animal         intelligence == Animal && !mechanoid
CLASSIFIER_CATEGORIES = (
    "weapon", "meleeWeapon", "rangedWeapon", "apparel", "plant", "stuff",
    "ingestible", "drug", "medicine", "buildingArtificial", "minifiable",
    "pawn", "animal", "humanlike", "toolUser", "mechanoid",
)
# Flags DefReflector only writes when the def is a pawn (race != null), so their
# ABSENCE is a real "false", not "unknown".
PAWN_ONLY_FLAGS = frozenset(("pawn", "animal", "humanlike", "toolUser",
                             "mechanoid", "flesh"))


def _node(d, *path):
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
        if cur is None:
            return None
    return cur


def _text(d, *path):
    v = _node(d, *path)
    return v.strip() if isinstance(v, str) else ""


def _nonempty_list(d, key):
    v = d.get(key) if isinstance(d, dict) else None
    if isinstance(v, list):
        return len(v) > 0
    if isinstance(v, dict):
        return bool(v.get("li"))
    return False


def classify_offline(d):
    """Best-effort category flags from the inheritance-resolved offline XML."""
    cat = _text(d, "category")
    has_verbs = _nonempty_list(d, "verbs")
    has_tools = _nonempty_list(d, "tools")

    verbs = d.get("verbs") if isinstance(d, dict) else None
    if isinstance(verbs, dict):
        verbs = verbs.get("li") or []
    ranged = any(isinstance(v, dict) and ("defaultProjectile" in v
                                          or "projectileDef" in v)
                 for v in (verbs or []))

    weapon = cat == "Item" and (has_verbs or has_tools)
    race = _node(d, "race")
    intelligence = _text(d, "race", "intelligence")
    flesh_type = _text(d, "race", "fleshType")
    is_mech = flesh_type == "Mechanoid"
    ingestible = _node(d, "ingestible") is not None
    drug_cat = _text(d, "ingestible", "drugCategory")

    return {
        "weapon": weapon,
        "rangedWeapon": weapon and ranged,
        "meleeWeapon": weapon and not ranged,
        "apparel": _node(d, "apparel") is not None,
        "plant": cat == "Plant",
        "stuff": _node(d, "stuffProps") is not None,
        "ingestible": ingestible,
        "drug": ingestible and drug_cat not in ("", "None"),
        "medicine": _node(d, "statBases", "MedicalPotency") is not None,
        "buildingArtificial": (cat == "Building"
                               and _text(d, "building", "isNaturalRock").lower() != "true"),
        "minifiable": _node(d, "minifiedDef") is not None,
        "pawn": race is not None,
        "animal": race is not None and intelligence in ("", "Animal") and not is_mech,
        "humanlike": intelligence == "Humanlike",
        "toolUser": intelligence in ("ToolUser", "Humanlike"),
        "mechanoid": is_mech,
    }


class ClassifierTally(object):
    """offline-says-yes / live-says-yes / agree / FP / FN per category."""

    def __init__(self):
        self.off_yes = Counter()
        self.live_yes = Counter()
        self.agree = Counter()
        self.fp = Counter()
        self.fn = Counter()
        self.evaluated = Counter()

    def feed(self, guess, is_block):
        """Returns the list of categories that disagreed for this def."""
        bad = []
        for cat in CLASSIFIER_CATEGORIES:
            live = is_block.get(cat, _MISSING)
            if live is _MISSING:
                if cat not in PAWN_ONLY_FLAGS:
                    continue          # not a ThingDef flag we can judge
                live = False          # absent pawn flag == not a pawn
            if not isinstance(live, bool):
                continue              # "<failed:Exception>" — no ground truth
            og = bool(guess.get(cat))
            self.evaluated[cat] += 1
            if og:
                self.off_yes[cat] += 1
            if live:
                self.live_yes[cat] += 1
            if og == live:
                self.agree[cat] += 1
            else:
                bad.append(cat)
                if og:
                    self.fp[cat] += 1
                else:
                    self.fn[cat] += 1
        return bad

    def rows(self):
        out = []
        for cat in CLASSIFIER_CATEGORIES:
            n = self.evaluated[cat]
            if not n:
                continue
            out.append({
                "category": cat,
                "evaluated": n,
                "offlineYes": self.off_yes[cat],
                "liveYes": self.live_yes[cat],
                "agree": self.agree[cat],
                "falsePositive": self.fp[cat],
                "falseNegative": self.fn[cat],
                "accuracy": round(self.agree[cat] / float(n), 4),
            })
        return out


# ---------------------------------------------------------------- offline side
class OfflineRec(object):
    """
    The duck type the diff engine consumes.

    def_inventory.DefRecord already satisfies it; the self-test builds these
    directly from XML strings so the comparison logic can be verified without a
    mod tree on disk.
    """

    __slots__ = ("defType", "defName", "modName", "shortHashCandidate",
                 "isAbstract", "own", "element", "duplicateOwners",
                 "loadOrder", "sourceFile", "_res")

    def __init__(self, defType, xml, modName="TestMod", shortHashCandidate=0,
                 loadOrder=1, sourceFile="test.xml", duplicateOwners=None):
        el = ET.fromstring(xml) if isinstance(xml, str) else xml
        self.defType = defType
        self.own = el
        self.element = el
        dn = el.find("defName")
        self.defName = (dn.text or "").strip() if dn is not None else ""
        self.modName = modName
        self.shortHashCandidate = shortHashCandidate
        self.isAbstract = (el.get("Abstract") or "").strip().lower() == "true"
        self.duplicateOwners = duplicateOwners or []
        self.loadOrder = loadOrder
        self.sourceFile = sourceFile

    def release(self):
        pass


def mayrequire_gate(rec, active_packages):
    """
    ('', '') if not gated, else (rule, missingPackageIds).

    MayRequire lists packageIds that must ALL be active; MayRequireAnyOf needs
    at least one. Case-insensitive, because ModsConfig and mod XML disagree on
    casing constantly. Read from the def's OWN node — see LIMITATIONS.
    """
    own = getattr(rec, "own", None)
    if own is None:
        return "", ""
    req = (own.get("MayRequire") or "").strip()
    anyof = (own.get("MayRequireAnyOf") or "").strip()
    if not req and not anyof:
        return "", ""
    active = set(p.lower() for p in active_packages)
    if req:
        need = [p.strip() for p in req.split(",") if p.strip()]
        missing = [p for p in need if p.lower() not in active]
        if missing:
            return "MayRequire", ",".join(missing)
    if anyof:
        need = [p.strip() for p in anyof.split(",") if p.strip()]
        if need and not any(p.lower() in active for p in need):
            return "MayRequireAnyOf", ",".join(need)
    return "", ""


# ---------------------------------------------------------------- the diff
DIV_COLUMNS = ["defType", "defName", "status", "rule", "offlineMod", "liveMod",
               "modMatch", "offlineShortHashCandidate", "liveShortHash",
               "hashMatch", "contested", "deltaCount", "deltas",
               "categoryMismatches"]

SUMMARY_STATUSES = ["both", "category_mismatch", "live_only", "live_generated",
                    "offline_only", "offline_abstract", "offline_mayrequire"]

SUMMARY_COLUMNS = (["defType", "liveDefs", "offlineDefs"] + SUMMARY_STATUSES
                   + ["hashMismatch", "modMismatch", "defsWithDeltas",
                      "deltaTotal", "contestedMatched", "contestedResolved"])

ACC_COLUMNS = ["category", "evaluated", "offlineYes", "liveYes", "agree",
               "falsePositive", "falseNegative", "accuracy"]


class DiffContext(object):
    def __init__(self, active_packages, all_offline_names, tally,
                 list_counts=True, max_delta_chars=600):
        self.active_packages = active_packages
        self.all_offline_names = all_offline_names
        self.tally = tally
        self.list_counts = list_counts
        self.max_delta_chars = max_delta_chars


def diff_type(defType, live_iter, offline_recs, ctx):
    """
    Diff one def type. `live_iter` yields live def objects in DefDumper schema.

    ONE DEF TYPE AT A TIME is the memory contract: the caller must not hold a
    previous type's live objects, and this function resolves, converts, compares
    and releases each offline element individually rather than materialising the
    whole type's merged XML.
    """
    # Abstract="True" nodes and Name=-only nodes exist to be inherited FROM and
    # are never registered as defs, so they must not compete for a match — an
    # abstract def that happens to carry a defName would otherwise shadow the
    # real one.
    winners, abstracts = {}, []
    for rec in offline_recs:
        if getattr(rec, "isAbstract", False) or not rec.defName:
            abstracts.append(rec)
            continue
        winners[rec.defName] = rec           # last in load order wins

    rows = []
    st = Counter()
    seen = set()
    live_count = 0

    for lv in live_iter:
        dn = lv.get("defName") or ""
        if not dn:
            continue
        live_count += 1
        is_block = lv.get("is") if isinstance(lv.get("is"), dict) else None
        live_mod = (lv.get("modName") or "").strip()
        live_hash = "" if lv.get("shortHash") is None else str(lv.get("shortHash")).strip()

        rec = winners.get(dn)
        if rec is None:
            rule = generated_rule(dn, is_block, ctx.all_offline_names)
            status = "live_generated" if rule else "live_only"
            st[status] += 1
            rows.append({"defType": defType, "defName": dn, "status": status,
                         "rule": rule, "offlineMod": "", "liveMod": live_mod,
                         "modMatch": "", "offlineShortHashCandidate": "",
                         "liveShortHash": live_hash, "hashMatch": "",
                         "contested": "", "deltaCount": "", "deltas": "",
                         "categoryMismatches": ""})
            continue

        seen.add(dn)

        # --- identity: the two things the offline scan can only guess at ---
        oh = str(rec.shortHashCandidate or "").strip()
        hash_match = "" if not oh or not live_hash else ("yes" if oh == live_hash else "NO")
        if hash_match == "NO":
            st["hashMismatch"] += 1

        om = (rec.modName or "").strip()
        mod_match = "" if not om or not live_mod else ("yes" if om == live_mod else "NO")
        if mod_match == "NO":
            st["modMismatch"] += 1

        contested = len(getattr(rec, "duplicateOwners", []) or []) > 1
        if contested:
            st["contestedMatched"] += 1
            if mod_match:
                st["contestedResolved"] += 1

        # --- fields: this is where PatchOperation results become visible ---
        off_dict = element_to_dict(rec.element)
        deltas, _skipped = compare_def(off_dict, lv.get("fields") or {},
                                       list_counts=ctx.list_counts)
        rec.release()

        # --- category calibration ---
        cat_bad = []
        if is_block is not None:
            cat_bad = ctx.tally.feed(classify_offline(off_dict), is_block)

        status = "category_mismatch" if cat_bad else "both"
        st[status] += 1
        if deltas:
            st["defsWithDeltas"] += 1
            st["deltaTotal"] += len(deltas)

        rows.append({"defType": defType, "defName": dn, "status": status,
                     "rule": "", "offlineMod": om, "liveMod": live_mod,
                     "modMatch": mod_match, "offlineShortHashCandidate": oh,
                     "liveShortHash": live_hash, "hashMatch": hash_match,
                     "contested": "yes" if contested else "",
                     "deltaCount": len(deltas),
                     "deltas": " | ".join(deltas)[:ctx.max_delta_chars],
                     "categoryMismatches": ",".join(cat_bad)})

    # --- offline records the live database does not have -------------------
    for rec in abstracts:
        st["offline_abstract"] += 1
        rows.append({"defType": defType,
                     "defName": rec.defName or ("<abstract:%s>" % (rec.own.get("Name") or "?")),
                     "status": "offline_abstract",
                     "rule": "Abstract" if getattr(rec, "isAbstract", False) else "no-defName",
                     "offlineMod": rec.modName, "liveMod": "", "modMatch": "",
                     "offlineShortHashCandidate": "", "liveShortHash": "",
                     "hashMatch": "", "contested": "", "deltaCount": "",
                     "deltas": "", "categoryMismatches": ""})

    for dn in sorted(set(winners) - seen):
        rec = winners[dn]
        gate, missing = mayrequire_gate(rec, ctx.active_packages)
        if gate:
            status, rule = "offline_mayrequire", "%s:%s" % (gate, missing)
        else:
            status, rule = "offline_only", ""
        st[status] += 1
        rows.append({"defType": defType, "defName": dn, "status": status,
                     "rule": rule, "offlineMod": rec.modName, "liveMod": "",
                     "modMatch": "",
                     "offlineShortHashCandidate": str(rec.shortHashCandidate or ""),
                     "liveShortHash": "", "hashMatch": "",
                     "contested": "yes" if len(getattr(rec, "duplicateOwners", []) or []) > 1 else "",
                     "deltaCount": "", "deltas": "", "categoryMismatches": ""})

    st["liveDefs"] = live_count
    st["offlineDefs"] = len(offline_recs)
    return rows, st


# ---------------------------------------------------------------- output
def write_csv(path, cols, rows):
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)


def report(per_type, totals, tally, manifest, out_dir, top_rows):
    print("\n=== offline (base XML) vs live (post-patch DefDatabase) ===")
    if manifest:
        print("live dump: RimWorld %s, %s mods, captured %s, mode=%s"
              % (manifest.get("gameVersion", "?"), manifest.get("modCount", "?"),
                 manifest.get("capturedUtc", "?"), manifest.get("mode", "?")))
    print("def types compared: %d" % len(per_type))
    print()
    print("  THE NUMBERS THAT MATTER")
    print("  contested keys matched     %6d   (offline flagged >1 owner)"
          % totals["contestedMatched"])
    print("  ... winner now resolved    %6d   <- settles vendor/wisdom/def_override_clusters.md"
          % totals["contestedResolved"])
    print("  mod attribution differs    %6d   <- offline named the LOSER of an override"
          % totals["modMismatch"])
    print("  shortHash mismatches       %6d   <- the candidate was wrong; use the live value"
          % totals["hashMismatch"])
    print("  defs with field deltas     %6d   (%d deltas)  <- PatchOperation results"
          % (totals["defsWithDeltas"], totals["deltaTotal"]))
    print()
    print("  PRESENCE")
    print("  both                       %6d" % totals["both"])
    print("  category_mismatch          %6d   <- matched, but OUR classifier disagreed"
          % totals["category_mismatch"])
    print("  live_only                  %6d   <- patch-created, or a generator we do not model"
          % totals["live_only"])
    print("  live_generated             %6d   <- engine-generated, rule named in the CSV"
          % totals["live_generated"])
    print("  offline_only               %6d   <- patch-removed or lost an override"
          % totals["offline_only"])
    print("  offline_abstract           %6d   <- Name=/Abstract, never registered. Expected."
          % totals["offline_abstract"])
    print("  offline_mayrequire         %6d   <- gated off by an inactive mod. Expected."
          % totals["offline_mayrequire"])

    acc = tally.rows()
    if acc:
        print("\n  OFFLINE CLASSIFIER vs THE ENGINE'S `is` BLOCK")
        print("  %-20s %8s %8s %8s %8s %8s" %
              ("category", "eval", "offYes", "liveYes", "wrong", "acc"))
        for r in acc:
            print("  %-20s %8d %8d %8d %8d %7.2f%%" %
                  (r["category"], r["evaluated"], r["offlineYes"], r["liveYes"],
                   r["falsePositive"] + r["falseNegative"], 100.0 * r["accuracy"]))

    if top_rows:
        print("\n  MOST-PATCHED DEFS")
        for r in top_rows:
            print("   %-16s %-30s %3d  %s"
                  % (r["defType"], r["defName"][:30], r["deltaCount"],
                     r["deltas"][:90]))

    print("\nwrote def_divergence.csv, def_diff_summary.csv, classifier_accuracy.csv to %s"
          % os.path.abspath(out_dir))


# ---------------------------------------------------------------- driver
def run(live_dir, out_dir, types=None, list_counts=True, max_delta_chars=600,
        offline_paths=None, quiet=False):
    defs_dir = os.path.join(live_dir, "defs")
    if not os.path.isdir(defs_dir):
        sys.exit("no defs/ folder in %s — that dump was written in mode=animals. "
                 "Put 'all' in dump_request.txt and reload. "
                 "See src/RimMandrake/RimDefDump/README.md." % live_dir)

    manifest = load_manifest(live_dir)
    live_types = {}
    for fn in sorted(os.listdir(defs_dir)):
        if fn.lower().endswith(".json"):
            live_types[fn[:-5]] = os.path.join(defs_dir, fn)

    op = offline_paths or {}
    ds = build(op.get("config", D_CONFIG), op.get("workshop", D_WORKSHOP),
               op.get("local", D_LOCAL), op.get("data", D_DATA),
               types=types, quiet=quiet)

    active = set(m["packageId"] for m in ds.mods if m.get("packageId"))
    for m in manifest.get("mods", []):
        if m.get("packageId"):
            active.add(m["packageId"])

    # Cheap (strings only) and needed by the generator rules: Corpse_Muffalo is
    # only confidently generated if Muffalo is a def we actually saw.
    all_names = set(r.defName for r in ds.records if r.defName)

    tally = ClassifierTally()
    ctx = DiffContext(active, all_names, tally, list_counts, max_delta_chars)

    # A def whose C# class lives in a namespace may be written in XML with the
    # namespace on the TAG (<AM.AnimDef>), but the live DefDatabase keys on the
    # class's SHORT name (AnimDef). Matching the two literally splits such a
    # type in half and reports every one of its defs as BOTH offline_only and
    # live_only. Measured before this fix: 231 of 515 offline types were split,
    # which alone accounted for most of 22,329 live_only and 6,847 offline_only
    # rows — i.e. the majority of the report was an artefact of tag spelling.
    #
    # Only collapse when the short name is a type the live dump actually has;
    # otherwise a genuinely-namespaced offline-only type keeps its full name and
    # stays visible rather than being silently merged into something else.
    def live_key(offline_type):
        if "." in offline_type:
            short = offline_type.rsplit(".", 1)[-1]
            if short in live_types:
                return short
        return offline_type

    offline_by_live = defaultdict(list)
    for t in ds.types():
        offline_by_live[live_key(t)].append(t)

    want = set(types) if types else None
    all_types = sorted(set(live_types) | set(offline_by_live))
    if want:
        all_types = [t for t in all_types if t in want]

    all_rows, per_type, totals = [], [], Counter()
    for dt in all_types:
        recs = []
        for src in offline_by_live.get(dt, [dt]):
            recs.extend(ds.of_type(src))
        path = live_types.get(dt)
        if path is None:
            # The live dump has no file for this type at all. Do not pretend the
            # defs were removed: say so in the rule column.
            live_iter = iter(())
        else:
            live_iter = iter_live_defs(path)
        rows, st = diff_type(dt, live_iter, recs, ctx)
        if path is None:
            for r in rows:
                if r["status"] == "offline_only":
                    r["rule"] = "no-live-file-for-type"
        all_rows.extend(rows)
        row = {"defType": dt}
        for k in (SUMMARY_COLUMNS[1:]):
            row[k] = st.get(k, 0)
        per_type.append(row)
        for k, v in st.items():
            totals[k] += v
        # ONE DEF TYPE AT A TIME: `rows` for the type is kept (it is small,
        # strings only) but the live objects and merged offline elements for
        # this type are now unreferenced and collectable.

    os.makedirs(out_dir, exist_ok=True)
    write_csv(os.path.join(out_dir, "def_divergence.csv"), DIV_COLUMNS, all_rows)
    write_csv(os.path.join(out_dir, "def_diff_summary.csv"), SUMMARY_COLUMNS, per_type)
    write_csv(os.path.join(out_dir, "classifier_accuracy.csv"), ACC_COLUMNS, tally.rows())

    top = sorted((r for r in all_rows if r["deltaCount"]),
                 key=lambda r: -r["deltaCount"])[:12]
    report(per_type, totals, tally, manifest, out_dir, top)
    return all_rows, per_type, totals, tally


# ---------------------------------------------------------------- self-test
def _synth_live_dir(tmp):
    """
    A synthetic DefDump in the EXACT schema DefDumper.cs emits.

    Every shape here is taken from the C#, not invented: the identity block
    (defName/defType/defTypeFull/label/shortHash/modName/packageId), the `is`
    block on ThingDefs only, `fields` as the reflected object with a "$type",
    nulls omitted, Defs collapsed to defName strings, enums as names,
    dictionaries as [{key,value}], and the sentinel strings.
    """
    live = os.path.join(tmp, "live")
    os.makedirs(os.path.join(live, "defs"))

    thing_defs = [
        # 1. clean match
        {"defName": "Muffalo", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "muffalo",
         "shortHash": 1111, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "plant": False,
                "stuff": False, "ingestible": False, "drug": False,
                "medicine": False, "buildingArtificial": False,
                "minifiable": False, "meleeWeapon": False,
                "rangedWeapon": False, "corpse": False,
                "pawn": True, "animal": True, "humanlike": False,
                "toolUser": False, "mechanoid": False, "flesh": True,
                "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "Muffalo",
                    "label": "muffalo", "category": "Pawn",
                    "statBases": [{"$type": "StatModifier", "stat": "MoveSpeed",
                                   "value": 4.5},
                                  {"$type": "StatModifier", "stat": "MarketValue",
                                   "value": 300.0}],
                    "race": {"$type": "RaceProperties", "baseBodySize": 2.4,
                             "intelligence": "Animal", "predator": False,
                             "trainability": "None"}}},
        # 2. a PatchOperation moved the speed and the label
        {"defName": "Thrumbo", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "royal thrumbo",
         "shortHash": 2222, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "plant": False,
                "stuff": False, "ingestible": False, "drug": False,
                "medicine": False, "buildingArtificial": False,
                "minifiable": False, "meleeWeapon": False, "rangedWeapon": False,
                "pawn": True, "animal": True, "humanlike": False,
                "toolUser": False, "mechanoid": False, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "Thrumbo",
                    "label": "royal thrumbo", "category": "Pawn",
                    "statBases": [{"$type": "StatModifier", "stat": "MoveSpeed",
                                   "value": 5.6}],
                    "race": {"$type": "RaceProperties", "baseBodySize": 4.0,
                             "intelligence": "Animal"}}},
        # 3. the offline hash candidate was wrong (collision bumped in game)
        {"defName": "Alphabeaver", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "alphabeaver",
         "shortHash": 3333, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "plant": False,
                "pawn": True, "animal": True, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "Alphabeaver",
                    "label": "alphabeaver", "category": "Pawn",
                    "race": {"$type": "RaceProperties", "baseBodySize": 0.5,
                             "intelligence": "Animal"}}},
        # 4. another mod won the override
        {"defName": "Armadillo", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "armadillo",
         "shortHash": 4444, "modName": "Beasts of the Rim (Continued)",
         "packageId": "someone.beasts",
         "is": {"weapon": False, "apparel": False, "plant": False,
                "pawn": True, "animal": True, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "Armadillo",
                    "label": "armadillo", "category": "Pawn",
                    "race": {"$type": "RaceProperties", "baseBodySize": 0.6,
                             "intelligence": "Animal"}}},
        # 5. engine-generated corpse — must NOT be reported as live_only
        {"defName": "Corpse_Muffalo", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "muffalo corpse",
         "shortHash": 5555, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"corpse": True, "weapon": False, "apparel": False,
                "category": "Item"},
         "fields": {"$type": "ThingDef", "defName": "Corpse_Muffalo"}},
        # 6. genuinely created by a patch — the interesting bucket
        {"defName": "PatchBornThing", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "patch born",
         "shortHash": 6666, "modName": "SomeMod", "packageId": "some.mod",
         "is": {"corpse": False, "weapon": False, "apparel": False,
                "category": "Item"},
         "fields": {"$type": "ThingDef", "defName": "PatchBornThing"}},
        # 7. every value the offline XML declares comes back as a SENTINEL
        {"defName": "SentinelBeast", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "sentinel beast",
         "shortHash": 7777, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "pawn": True,
                "animal": True, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "SentinelBeast",
                    "label": "sentinel beast", "category": "Pawn",
                    "description": "<truncated>",
                    "race": {"$type": "RaceProperties",
                             "baseBodySize": "<read-failed:NullReferenceException>",
                             "intelligence": "Animal",
                             "body": "<maxdepth:BodyDef>",
                             "leatherDef": "<cycle:ThingDef>"}}},
        # 8. dictionary-shaped values (DefReflector writes IDictionary as
        #    [{key,value}] — race.wildBiomes is exactly this)
        {"defName": "DictBeast", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "dict beast",
         "shortHash": 8888, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "pawn": True,
                "animal": True, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "DictBeast",
                    "label": "dict beast", "category": "Pawn",
                    "race": {"$type": "RaceProperties", "intelligence": "Animal",
                             "wildBiomes": [{"key": "Desert", "value": 0.5},
                                            {"key": "Tundra", "value": 0.2}]}}},
        # 9. tolerance cases: float drift, bool casing, empty offline, a range
        {"defName": "TolerantBeast", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "tolerant beast",
         "shortHash": 9999, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "pawn": True,
                "animal": True, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "TolerantBeast",
                    "label": "tolerant beast", "category": "Pawn",
                    "statBases": [{"$type": "StatModifier", "stat": "MarketValue",
                                   "value": 300.00000001}],
                    "race": {"$type": "RaceProperties", "intelligence": "Animal",
                             "predator": True, "lifeExpectancy": 12.0,
                             "gestationPeriodDays": {"$type": "FloatRange",
                                                     "min": 1.0, "max": 3.0}}}},
        # 10. our offline classifier gets the category wrong
        {"defName": "WeaponMisfit", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "odd weapon",
         "shortHash": 1212, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": True, "meleeWeapon": True, "rangedWeapon": False,
                "apparel": False, "plant": False, "stuff": False,
                "ingestible": False, "drug": False, "medicine": False,
                "buildingArtificial": False, "minifiable": False,
                "category": "Item"},
         "fields": {"$type": "ThingDef", "defName": "WeaponMisfit",
                    "label": "odd weapon", "category": "Item"}},
        # 11. classifier agrees (ranged weapon)
        {"defName": "Gun_Test", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "test gun",
         "shortHash": 1313, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": True, "meleeWeapon": False, "rangedWeapon": True,
                "apparel": False, "plant": False, "stuff": False,
                "ingestible": False, "drug": False, "medicine": False,
                "buildingArtificial": False, "minifiable": False,
                "category": "Item"},
         "fields": {"$type": "ThingDef", "defName": "Gun_Test",
                    "label": "test gun", "category": "Item",
                    "verbs": [{"$type": "VerbProperties",
                               "defaultProjectile": "Bullet_Test"}]}},
        # 12b. a patch swapped which C# class a comp instantiates -> a real
        #     delta, not silence. This is the case that proves the @Class vs
        #     $type special-case actually fires (it was dead code until it
        #     was fixed: SKIP_ATTR_KEYS filtered "@Class" out of the offline
        #     flatten at every depth, not just the root, so the comparison
        #     below never even saw a path to compare).
        {"defName": "ClassSwapBeast", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "class swap beast",
         "shortHash": 1515, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "pawn": True,
                "animal": True, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "ClassSwapBeast",
                    "label": "class swap beast", "category": "Pawn",
                    "comps": [{"$type": "CompProperties_Shearable"}],
                    "race": {"$type": "RaceProperties", "intelligence": "Animal"}}},
        # 12. a patch appended two comps -> a list-length delta
        {"defName": "ListBeast", "defType": "ThingDef",
         "defTypeFull": "Verse.ThingDef", "label": "list beast",
         "shortHash": 1414, "modName": "Core", "packageId": "ludeon.rimworld",
         "is": {"weapon": False, "apparel": False, "pawn": True,
                "animal": True, "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "ListBeast",
                    "label": "list beast", "category": "Pawn",
                    "comps": [{"$type": "CompProperties_Milkable",
                               "milkDef": "Milk"},
                              {"$type": "CompProperties_Shearable"},
                              {"$type": "CompProperties_Odd"}],
                    "race": {"$type": "RaceProperties", "intelligence": "Animal"}}},
    ]
    recipe_defs = [
        {"defName": "Make_Gun_Test", "defType": "RecipeDef",
         "defTypeFull": "Verse.RecipeDef", "label": "make test gun",
         "shortHash": 2001, "modName": "Core", "packageId": "ludeon.rimworld",
         "fields": {"$type": "RecipeDef", "defName": "Make_Gun_Test"}},
        {"defName": "CookMeal", "defType": "RecipeDef",
         "defTypeFull": "Verse.RecipeDef", "label": "cook meal",
         "shortHash": 2002, "modName": "Core", "packageId": "ludeon.rimworld",
         "fields": {"$type": "RecipeDef", "defName": "CookMeal",
                    "label": "cook meal", "workAmount": 400.0}},
    ]

    for name, defs in (("ThingDef", thing_defs), ("RecipeDef", recipe_defs)):
        with io.open(os.path.join(live, "defs", name + ".json"), "w",
                     encoding="utf-8") as f:
            f.write(json.dumps({"defType": name, "defs": defs,
                                "count": len(defs)}, separators=(",", ":")))

    with io.open(os.path.join(live, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "tool": "RimDefDump", "toolVersion": "1.0", "mode": "all",
            "capturedUtc": "2026-08-10T00:00:00Z", "gameVersion": "1.6.4871",
            "timingsMs": {"total": 1, "animals": 1, "allDefs": 1},
            "mods": [{"loadOrder": 1, "name": "Core", "packageId": "ludeon.rimworld"},
                     {"loadOrder": 2, "name": "ActiveMod", "packageId": "active.mod"}],
            "modCount": 2,
            "defCounts": {"ThingDef": len(thing_defs), "RecipeDef": len(recipe_defs)},
        }, indent=2))
    return live


def _synth_offline():
    T = lambda xml, **kw: OfflineRec("ThingDef", xml, **kw)   # noqa: E731
    recs = [
        T("""<ThingDef>
               <defName>Muffalo</defName><label>muffalo</label>
               <category>Pawn</category>
               <statBases><MoveSpeed>4.5</MoveSpeed><MarketValue>300</MarketValue></statBases>
               <race><baseBodySize>2.4</baseBodySize><intelligence>Animal</intelligence>
                     <predator>False</predator><trainability>None</trainability></race>
             </ThingDef>""", modName="Core", shortHashCandidate=1111),
        # label and MoveSpeed both moved by a patch -> exactly 2 deltas
        T("""<ThingDef>
               <defName>Thrumbo</defName><label>thrumbo</label>
               <category>Pawn</category>
               <statBases><MoveSpeed>5.0</MoveSpeed></statBases>
               <race><baseBodySize>4.0</baseBodySize><intelligence>Animal</intelligence></race>
             </ThingDef>""", modName="Core", shortHashCandidate=2222),
        T("""<ThingDef>
               <defName>Alphabeaver</defName><label>alphabeaver</label>
               <category>Pawn</category>
               <race><baseBodySize>0.5</baseBodySize><intelligence>Animal</intelligence></race>
             </ThingDef>""", modName="Core", shortHashCandidate=9998),
        T("""<ThingDef>
               <defName>Armadillo</defName><label>armadillo</label>
               <category>Pawn</category>
               <race><baseBodySize>0.6</baseBodySize><intelligence>Animal</intelligence></race>
             </ThingDef>""", modName="Odyssey", shortHashCandidate=4444,
          duplicateOwners=["Beasts of the Rim (Continued)", "Odyssey"]),
        # every declared value comes back as a sentinel -> must be 0 deltas
        T("""<ThingDef>
               <defName>SentinelBeast</defName><label>sentinel beast</label>
               <category>Pawn</category>
               <description>a long description</description>
               <race><baseBodySize>1.5</baseBodySize><intelligence>Animal</intelligence>
                     <body>QuadrupedAnimalWithHooves</body>
                     <leatherDef>Leather_Plain</leatherDef></race>
             </ThingDef>""", modName="Core", shortHashCandidate=7777),
        # dict-shaped: Desert agrees, Tundra was patched 0.9 -> 0.2
        T("""<ThingDef>
               <defName>DictBeast</defName><label>dict beast</label>
               <category>Pawn</category>
               <race><intelligence>Animal</intelligence>
                     <wildBiomes><Desert>0.5</Desert><Tundra>0.9</Tundra></wildBiomes></race>
             </ThingDef>""", modName="Core", shortHashCandidate=8888),
        # float drift, bool casing, an empty tag, and a FloatRange
        T("""<ThingDef>
               <defName>TolerantBeast</defName><label>tolerant beast</label>
               <category>Pawn</category>
               <statBases><MarketValue>300</MarketValue></statBases>
               <race><intelligence>Animal</intelligence><predator>True</predator>
                     <lifeExpectancy></lifeExpectancy>
                     <gestationPeriodDays>1~3</gestationPeriodDays></race>
             </ThingDef>""", modName="Core", shortHashCandidate=9999),
        # no verbs and no tools -> offline says "not a weapon", engine says it is
        T("""<ThingDef>
               <defName>WeaponMisfit</defName><label>odd weapon</label>
               <category>Item</category>
             </ThingDef>""", modName="Core", shortHashCandidate=1212),
        T("""<ThingDef>
               <defName>Gun_Test</defName><label>test gun</label>
               <category>Item</category>
               <verbs><li><defaultProjectile>Bullet_Test</defaultProjectile></li></verbs>
             </ThingDef>""", modName="Core", shortHashCandidate=1313),
        # the offline Class= names one comp, the live $type names another
        T("""<ThingDef>
               <defName>ClassSwapBeast</defName><label>class swap beast</label>
               <category>Pawn</category>
               <comps><li Class="CompProperties_Milkable"><milkDef>Milk</milkDef></li></comps>
               <race><intelligence>Animal</intelligence></race>
             </ThingDef>""", modName="Core", shortHashCandidate=1515),
        # one comp offline, three live -> a #count delta
        T("""<ThingDef>
               <defName>ListBeast</defName><label>list beast</label>
               <category>Pawn</category>
               <comps><li Class="CompProperties_Milkable"><milkDef>Milk</milkDef></li></comps>
               <race><intelligence>Animal</intelligence></race>
             </ThingDef>""", modName="Core", shortHashCandidate=1414),
        # never live: patch-removed or lost an override
        T("""<ThingDef>
               <defName>GhostThing</defName><label>ghost</label><category>Item</category>
             </ThingDef>""", modName="DeadMod", shortHashCandidate=7000),
        # abstract base: exists to be inherited from, never registered
        T("""<ThingDef Name="AnimalThingBase" Abstract="True">
               <category>Pawn</category>
             </ThingDef>""", modName="Core"),
        # gated behind a mod that is NOT in the load set
        T("""<ThingDef MayRequire="inactive.mod">
               <defName>GatedThing</defName><label>gated</label><category>Item</category>
             </ThingDef>""", modName="SomeMod", shortHashCandidate=7100),
        # gated behind a mod that IS active -> a real offline_only, not a bucket
        T("""<ThingDef MayRequire="active.mod">
               <defName>GatedActive</defName><label>gated but active</label>
               <category>Item</category>
             </ThingDef>""", modName="SomeMod", shortHashCandidate=7200),
    ]
    recipes = [
        OfflineRec("RecipeDef", """<RecipeDef>
               <defName>CookMeal</defName><label>cook meal</label>
               <workAmount>400</workAmount>
             </RecipeDef>""", modName="Core", shortHashCandidate=2002),
    ]
    return {"ThingDef": recs, "RecipeDef": recipes}


def _synth_mod_tree(tmp):
    """
    A minimal but REAL mod tree: ModsConfig.xml + About/About.xml + Defs/.

    Phase 1 of the self-test feeds the diff engine duck-typed OfflineRecs, which
    is the right way to test comparison logic. It does not test the adapter to
    layer 1. This does: build() runs for real here — load-set resolution, the
    two-pass scan, <ParentName> inheritance — so a DefRecord whose interface
    drifted (or an inheritance result that never reached the comparison) fails
    the gate instead of the first live run.
    """
    root = os.path.join(tmp, "mods")
    mod = os.path.join(root, "TestMod")
    os.makedirs(os.path.join(mod, "About"))
    os.makedirs(os.path.join(mod, "Defs"))

    def w(p, s):
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(s)

    w(os.path.join(mod, "About", "About.xml"),
      "<ModMetaData><packageId>test.mod</packageId>"
      "<name>Test Mod</name></ModMetaData>")
    w(os.path.join(mod, "Defs", "things.xml"), """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <ThingDef Name="TestAnimalBase" Abstract="True">
    <category>Pawn</category>
    <statBases><MoveSpeed>3.0</MoveSpeed></statBases>
    <race><intelligence>Animal</intelligence><baseHealthScale>1.0</baseHealthScale></race>
  </ThingDef>
  <ThingDef ParentName="TestAnimalBase">
    <defName>RealMuffalo</defName>
    <label>real muffalo</label>
    <statBases><MoveSpeed>4.5</MoveSpeed></statBases>
    <race><baseBodySize>2.4</baseBodySize></race>
  </ThingDef>
  <ThingDef ParentName="TestAnimalBase" MayRequire="not.installed">
    <defName>RealGated</defName>
    <label>gated</label>
  </ThingDef>
</Defs>
""")
    w(os.path.join(tmp, "ModsConfig.xml"),
      "<ModsConfigData><version>1.6.4871 rev123</version>"
      "<activeMods><li>test.mod</li></activeMods></ModsConfigData>")

    live = os.path.join(tmp, "reallive")
    os.makedirs(os.path.join(live, "defs"))
    things = [
        {"defName": "RealMuffalo", "defType": "ThingDef", "label": "real muffalo",
         "shortHash": _short_hash("RealMuffalo"), "modName": "Test Mod",
         "packageId": "test.mod",
         "is": {"weapon": False, "apparel": False, "pawn": True, "animal": True,
                "category": "Pawn"},
         "fields": {"$type": "ThingDef", "defName": "RealMuffalo",
                    "label": "real muffalo", "category": "Pawn",
                    "statBases": [{"$type": "StatModifier", "stat": "MoveSpeed",
                                   "value": 4.5}],
                    # baseHealthScale is INHERITED from the abstract base and
                    # then patched live. If .element were not the resolved
                    # element, offline would have nothing to say and this delta
                    # would silently vanish — the exact v1.2->v1.3 bug that cost
                    # animal_inventory.py a rewrite.
                    "race": {"$type": "RaceProperties", "baseBodySize": 2.4,
                             "intelligence": "Animal", "baseHealthScale": 2.5}}},
    ]
    with io.open(os.path.join(live, "defs", "ThingDef.json"), "w",
                 encoding="utf-8") as f:
        f.write(json.dumps({"defType": "ThingDef", "defs": things, "count": 1}))
    with io.open(os.path.join(live, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"gameVersion": "1.6.4871", "modCount": 1, "mode": "all",
                            "mods": [{"loadOrder": 1, "name": "Test Mod",
                                      "packageId": "test.mod"}]}))
    return live, os.path.join(tmp, "ModsConfig.xml"), root


def selftest():
    import shutil
    import tempfile

    tmp = tempfile.mkdtemp(prefix="defdiff_selftest_")
    try:
        live = _synth_live_dir(tmp)
        offline = _synth_offline()
        manifest = load_manifest(live)
        active = set(m["packageId"] for m in manifest.get("mods", []))
        all_names = set(r.defName for recs in offline.values()
                        for r in recs if r.defName)
        tally = ClassifierTally()
        ctx = DiffContext(active, all_names, tally)

        rows, per_type, totals = [], [], Counter()
        for dt in ("ThingDef", "RecipeDef"):
            r, st = diff_type(dt, iter_live_defs(
                os.path.join(live, "defs", dt + ".json")), offline[dt], ctx)
            rows.extend(r)
            per_type.append((dt, st))
            for k, v in st.items():
                totals[k] += v

        by = dict(((r["defType"], r["defName"]), r) for r in rows)
        TD = lambda n: by[("ThingDef", n)]                     # noqa: E731
        acc = dict((r["category"], r) for r in tally.rows())
        st_thing = dict(per_type)["ThingDef"]

        # A real CSV write, so a schema bug here fails the test rather than the
        # first real run.
        out = os.path.join(tmp, "out")
        os.makedirs(out)
        write_csv(os.path.join(out, "def_divergence.csv"), DIV_COLUMNS, rows)
        write_csv(os.path.join(out, "classifier_accuracy.csv"), ACC_COLUMNS,
                  tally.rows())
        with io.open(os.path.join(out, "def_divergence.csv"),
                     encoding="utf-8-sig", newline="") as f:
            csv_rows = list(csv.DictReader(f))

        checks = [
            # ---- streaming reader ----
            ("streaming reader found every live ThingDef", st_thing["liveDefs"] == 13),
            ("streaming reader handles a second type", totals["liveDefs"] == 15),
            # ---- presence classification ----
            ("clean match is 'both'", TD("Muffalo")["status"] == "both"),
            ("patched def still matches", TD("Thrumbo")["status"] == "both"),
            ("patch-created def is live_only", TD("PatchBornThing")["status"] == "live_only"),
            ("live_only counted once", totals["live_only"] == 1),
            ("generated corpse is live_generated",
             TD("Corpse_Muffalo")["status"] == "live_generated"),
            ("generated corpse names its rule",
             TD("Corpse_Muffalo")["rule"] == "is.corpse"),
            ("generated Make_ recipe bucketed",
             by[("RecipeDef", "Make_Gun_Test")]["status"] == "live_generated"),
            ("Make_ rule cites the known def",
             by[("RecipeDef", "Make_Gun_Test")]["rule"] == "recipe-make+known-def"),
            ("offline-only def flagged", TD("GhostThing")["status"] == "offline_only"),
            ("abstract base bucketed separately",
             any(r["status"] == "offline_abstract" and r["rule"] == "Abstract"
                 for r in rows)),
            ("abstract is not offline_only", totals["offline_abstract"] == 1),
            ("MayRequire on an inactive mod is bucketed",
             TD("GatedThing")["status"] == "offline_mayrequire"),
            ("MayRequire rule names the missing packageId",
             TD("GatedThing")["rule"] == "MayRequire:inactive.mod"),
            ("MayRequire on an ACTIVE mod is a real offline_only",
             TD("GatedActive")["status"] == "offline_only"),
            ("offline_only counted twice", totals["offline_only"] == 2),
            # ---- identity ----
            ("hash mismatch found", totals["hashMismatch"] == 1),
            ("Alphabeaver hash flagged", TD("Alphabeaver")["hashMatch"] == "NO"),
            ("matching hash says yes", TD("Muffalo")["hashMatch"] == "yes"),
            ("mod mismatch found", totals["modMismatch"] == 1),
            ("Armadillo override winner named", TD("Armadillo")["modMatch"] == "NO"
             and TD("Armadillo")["liveMod"] == "Beasts of the Rim (Continued)"),
            ("contested key marked", TD("Armadillo")["contested"] == "yes"),
            ("contested key counted as resolved", totals["contestedResolved"] == 1),
            # ---- field deltas ----
            ("unpatched def has zero deltas", TD("Muffalo")["deltaCount"] == 0),
            ("patched def has exactly 2 deltas", TD("Thrumbo")["deltaCount"] == 2),
            ("delta text names the label change", "label:" in TD("Thrumbo")["deltas"]),
            ("delta reaches inside a keyed live list (statBases)",
             "statBases.MoveSpeed" in TD("Thrumbo")["deltas"]),
            ("sentinels never produce a delta", TD("SentinelBeast")["deltaCount"] == 0),
            ("dictionary [{key,value}] resolves and only the patched key differs",
             TD("DictBeast")["deltaCount"] == 1
             and "wildBiomes.Tundra" in TD("DictBeast")["deltas"]),
            ("float tolerance holds", "MarketValue" not in TD("TolerantBeast")["deltas"]),
            ("bool True/true agrees", "predator" not in TD("TolerantBeast")["deltas"]),
            ("empty offline value is 'no opinion'",
             "lifeExpectancy" not in TD("TolerantBeast")["deltas"]),
            ("FloatRange '1~3' matches {min,max}",
             "gestationPeriodDays" not in TD("TolerantBeast")["deltas"]),
            ("tolerant def has no deltas at all", TD("TolerantBeast")["deltaCount"] == 0),
            ("list-length delta detected",
             "comps.#count: 1 -> 3" in TD("ListBeast")["deltas"]),
            ("Class= vs $type agrees on the short name",
             "@Class" not in TD("ListBeast")["deltas"]),
            ("a patched comp Class is caught, not silently skipped",
             TD("ClassSwapBeast")["deltaCount"] == 1
             and "comps.0.@Class: CompProperties_Milkable -> CompProperties_Shearable"
                 in TD("ClassSwapBeast")["deltas"]),
            ("defs-with-deltas tallied", totals["defsWithDeltas"] == 4
             and totals["deltaTotal"] == 5),
            ("a non-ThingDef type diffs too, and int-vs-float agrees",
             by[("RecipeDef", "CookMeal")]["status"] == "both"
             and by[("RecipeDef", "CookMeal")]["deltaCount"] == 0),
            # ---- classifier calibration ----
            ("classifier disagreement gets its own status",
             TD("WeaponMisfit")["status"] == "category_mismatch"),
            ("the disagreeing categories are named",
             "weapon" in TD("WeaponMisfit")["categoryMismatches"]),
            ("a correct classification stays 'both'", TD("Gun_Test")["status"] == "both"),
            # Calibration is only meaningful on MATCHED defs — a live_only def
            # has no offline guess to score, so the 13 live ThingDefs yield 11
            # evaluations, not 13.
            ("accuracy is scored over matched defs only",
             acc["weapon"]["evaluated"] == 11),
            ("the miss is a false NEGATIVE, not a false positive",
             acc["weapon"]["falseNegative"] == 1
             and acc["weapon"]["falsePositive"] == 0
             and abs(acc["weapon"]["accuracy"] - 10.0 / 11.0) < 1e-3),
            ("a flag missing from `is` is simply not scored",
             acc["meleeWeapon"]["evaluated"] == 4),
            ("ranged weapon guessed right",
             acc["rangedWeapon"]["falsePositive"] == 0),
            ("animal category is near-perfect offline",
             acc["animal"]["accuracy"] >= 0.9 and acc["animal"]["liveYes"] == 9),
            ("accuracy is a fraction", 0.0 <= acc["weapon"]["accuracy"] <= 1.0),
            ("pawn-only flags absent in `is` count as False",
             acc["pawn"]["liveYes"] == 9),
            ("category_mismatch is not double-counted as both",
             st_thing["both"] + st_thing["category_mismatch"] == 11),
            # ---- output ----
            ("CSV round-trips every row", len(csv_rows) == len(rows)),
            ("CSV carries the status column",
             csv_rows[0]["status"] in SUMMARY_STATUSES),
            ("summary column set covers every status",
             all(s in SUMMARY_COLUMNS for s in SUMMARY_STATUSES)),
            # ---- comparison primitives, directly ----
            ("is_sentinel spots <maxdepth:>", is_sentinel("<maxdepth:BodyDef>")),
            ("is_sentinel spots <truncated>", is_sentinel("<truncated>")),
            ("is_sentinel does not eat real text", not is_sentinel("a <b> c")),
            ("live enum name compares as text", values_agree("Animal", "Animal")),
            ("live Def collapses to defName", values_agree("Filth_Blood", "Filth_Blood")),
            ("numeric tolerance", values_agree("4.5", 4.5000001)),
            ("numeric intolerance", not values_agree("4.5", 5.6)),
            ("shape mismatch is silence", values_agree("4.5", [1, 2, 3])),
        ]

        # ---- phase 2: the real layer-1 adapter, through run() --------------
        rlive, rcfg, rroot = _synth_mod_tree(tmp)
        held, sys.stdout = sys.stdout, io.StringIO()   # run() prints its report
        try:
            rrows, _rpt, rtot, rtally = run(
                rlive, os.path.join(tmp, "realout"), types=["ThingDef"], quiet=True,
                offline_paths={"config": rcfg, "workshop": rroot,
                               "local": rroot, "data": rroot})
        finally:
            sys.stdout = held
        rby = dict((r["defName"], r) for r in rrows)
        checks += [
            ("run(): a real DefRecord matches", rby["RealMuffalo"]["status"] == "both"),
            ("run(): the real shortHashCandidate agrees",
             rby["RealMuffalo"]["hashMatch"] == "yes"),
            ("run(): the real modName agrees", rby["RealMuffalo"]["modMatch"] == "yes"),
            ("run(): an INHERITED field is compared (.element really is resolved)",
             "race.baseHealthScale: 1.0 -> 2.5" in rby["RealMuffalo"]["deltas"]),
            ("run(): the def's own value still beats its base",
             "MoveSpeed" not in rby["RealMuffalo"]["deltas"]),
            ("run(): a real Abstract= node is bucketed", rtot["offline_abstract"] == 1),
            ("run(): a real MayRequire= attribute is bucketed",
             rby["RealGated"]["status"] == "offline_mayrequire"
             and rby["RealGated"]["rule"] == "MayRequire:not.installed"),
            ("run(): the classifier scored the real record",
             rtally.rows()[0]["evaluated"] == 1),
            ("run(): all three CSVs land on disk",
             all(os.path.isfile(os.path.join(tmp, "realout", f))
                 for f in ("def_divergence.csv", "def_diff_summary.csv",
                           "classifier_accuracy.csv"))),
        ]

        bad = [n for n, ok in checks if not ok]
        for n, ok in checks:
            print(("ok   " if ok else "FAIL ") + n)
        print()
        if bad:
            print("%d FAILURES of %d" % (len(bad), len(checks)))
            return 1
        print("ALL PASS (%d checks)" % len(checks))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Diff the offline def database (base XML, inheritance "
                    "resolved) against a live RimDefDump dump (post-patch).")
    ap.add_argument("--live", help="a DefDump folder written by src/RimMandrake/RimDefDump "
                                   "in mode=all (needs defs/<Type>.json)")
    ap.add_argument("--types", default=None,
                    help="comma-separated def types to compare (default: all)")
    ap.add_argument("--out", default="out")
    ap.add_argument("--no-list-counts", action="store_true",
                    help="suppress list-length (#count) deltas, which is where "
                         "PatchOperationAdd shows up but also where C#-appended "
                         "list entries create noise")
    ap.add_argument("--max-delta-chars", type=int, default=600)
    ap.add_argument("--config", default=D_CONFIG)
    ap.add_argument("--workshop", default=D_WORKSHOP)
    ap.add_argument("--local", default=D_LOCAL)
    ap.add_argument("--data", default=D_DATA)
    ap.add_argument("--selftest", action="store_true",
                    help="verify every classification against a synthetic dump and exit")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if not a.live:
        ap.error("--live is required (or use --selftest)")

    types = [t.strip() for t in a.types.split(",") if t.strip()] if a.types else None
    t0 = time.perf_counter()
    run(a.live, a.out, types=types, list_counts=not a.no_list_counts,
        max_delta_chars=a.max_delta_chars,
        offline_paths={"config": a.config, "workshop": a.workshop,
                       "local": a.local, "data": a.data})
    print("total %.1fs" % (time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
