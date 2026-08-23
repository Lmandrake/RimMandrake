#!/usr/bin/env python3
"""
validate_patch.py - static + live validation for RimWorld mod XML:
PatchOperation files under Patches/ AND def files under Defs/.

WHAT IS SCANNED, AND WHAT IS NOT
================================
Until 2026-08-13 this tool checked <Patch> files ONLY. Every file whose root was
<Defs> was reported as "root element is <Defs>, expected <Patch>" - so pointing
it at a whole mod, which `traps-xml-and-defs.md` explicitly tells you to do
before a deploy ("validate EVERY file in the mod folder, the blast radius is the
mod"), produced one false ERROR per def file. A mod whose content is defs got
either a clean bill of health it had not earned (aim at Patches/) or a wall of
noise (aim at the mod root). Both readings were wrong.

It now dispatches on the ROOT ELEMENT, and the run banner states exactly what it
scanned and what it could not:

  <Patch>  -> the PatchOperation checks, unchanged, byte for byte.
  <Defs>   -> the def checks listed below.
  anything else -> ERROR, as before.

The def checks are deliberately a SHORTLIST of mechanical, decidable failures.
This is not a def linter and does not pretend to be one; the banner says so.
What it does NOT check is stated out loud rather than left to be assumed:
field names, field types, value ranges, C# class members, and anything a
PatchOperation creates at load time.

WHY THIS EXISTS
===============
RimWorld patches fail silently. A PatchOperation whose xpath matches nothing is
skipped with a single log line among thousands; a PatchOperationRemove whose
xpath matches more nodes than you expected deletes all of them without comment.
Both mistakes cost a full game restart to discover, which in a large mod stack
is several minutes each. This script finds them in under a second.

WHY THE LIVE HALF IS SCOPED TO THE REAL LOAD SET
================================================
The naive version of this script walked every Defs/**.xml under every --defs
root. On a 562-mod stack that is 33,173 files, because the Workshop tree holds
~1,200 mods (most of them inactive) and nearly all of them ship one folder per
game version - 1.0, 1.1, ... 1.6. Only ONE of those folders ever loads.

The result was not merely slow, it was WRONG in the dangerous direction. An
xpath for the Armadillo reported "7 matches" - seven version folders of a single
mod - and the script then advised adding a positional predicate like [1] to a
PatchOperationRemove. That advice would have deleted the wrong node in the real
game, where the true count is 1. A validator that cries wolf is worse than none.

So the live half now reconstructs the load set the game will actually build:
  * read ModsConfig.xml, take <activeMods> IN ORDER  (never <knownExpansions>,
    which duplicates the DLC entries already inside activeMods - counting both
    has burned this project twice);
  * map every installed mod folder to the packageId that is a DIRECT CHILD of
    <ModMetaData> (a first-match regex picks up packageIds inside
    <modDependencies> and resolves Harmony to Camera+, which is how that trap
    announces itself);
  * keep only active mods, in load order;
  * resolve each mod's def folders through its LoadFolders.xml for the target
    game version, honouring both IfModActive and IfModNotActive;
  * read Defs only from those folders.

Match locations are reported per MOD, not per bare filename, so two mods
defining the same def is visible instead of looking like one duplicated file.

WHAT IT CHECKS
==============
Static (no game install needed):
  1. The file parses as XML at all.
  2. No comment body contains '--'  (a hard XML parse error in most parsers,
     and the single easiest way to break a patch file while documenting it).
  3. Root element is <Patch>.
  4. Every <Operation> carries a Class attribute.
  5. Every operation that needs an <xpath> has a non-empty one.
  6. Operations that modify another mod's content are wrapped in
     PatchOperationConditional / PatchOperationFindMod  (warning, not error).
  7. For a Conditional, the test xpath equals the inner operation's xpath
     (warning when they differ - usually a copy-paste slip).
  8. PatchOperationReplace <value> contains an element, not bare text.

Live (with --defs pointing at real Defs directories):
  9. Each xpath is executed against the resolved load set, and the number of
     matching nodes is reported, grouped by mod.
       0 matches  -> ERROR for an inner operation (the patch would no-op),
                     INFO for a conditional test (a legitimate no-op guard),
                     and INFO for an operation in the <match> branch of a
                     conditional testing the SAME xpath - that branch is simply
                     unreachable at 0 matches, so it cannot no-op silently.
       >1 matches -> WARNING on Remove/Replace only when the extra nodes live
                     in ONE mod (a genuine duplicate you are about to hit all
                     of). Spread across several mods it is an INFO line: that
                     is several mods defining the same def, and patching all of
                     their nodes in the merged document is usually intended.

THE RUNTIME-PATCH BLIND SPOT
============================
This script evaluates UNPATCHED defs. Every node that another mod's
PatchOperation creates at load time is invisible to it, so a perfectly correct
xpath can report 0 matches. When that happens the script greps the active mods'
Patches/**/*.xml for the xpath's leaf element name; if some other mod's patch
mentions it, the ERROR is downgraded to a WARNING naming that mod - and the
thing to check is that your mod loads AFTER it. It cannot do better than that:
short of running the game, the merged document does not exist.

EXIT CODES
==========
  0  clean (warnings allowed)
  1  one or more errors in any file
  2  could not read any patch file

USAGE
=====
  python3 validate_patch.py Patches/MyPatch.xml

  # a whole mod at once - the blast radius of a deploy is the mod, not the diff
  python3 validate_patch.py src/MyMod/Patches \
      --defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" \
      --defs "C:/Program Files (x86)/Steam/steamapps/workshop/content/294100" \
      --defs "C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"

  # only fail on errors, stay quiet otherwise
  python3 validate_patch.py MyPatch.xml --quiet

FLAGS
=====
  patch...        one or more files OR directories (directories are searched
                  recursively for *.xml). Defs are loaded once and reused.
  --defs PATH     repeatable root to search for installed mods. Each root, and
                  each immediate subdirectory of it, counts as a mod if it has
                  About/About.xml - which covers Data/<Core|Royalty|...>,
                  workshop/content/294100/<id>, and RimWorld/Mods/<name>.
  --mods-config   ModsConfig.xml to define the active set and target version.
                  Defaults to the standard LocalLow path when it exists.
  --all-versions  escape hatch: scan every version folder of every installed
                  mod, active or not. Restores the old inflated counts. Useful
                  only when you are deliberately auditing files the game will
                  never load.
  --live DUMPDIR  a RimDefDump folder. Re-streams the whole dump (~1.3 GB) on
                  every run to rebuild the defName set.
  --defnames FILE the same set, precomputed. Identical checks, a set lookup
                  instead of a gigabyte of I/O. Write it once with
                  `--live DUMPDIR --write-defnames FILE`, then pass --defnames
                  forever after. Wins over --live when both are given.
  --quiet         suppress info lines.

NOTES ON THE XPATH ENGINE
=========================
RimWorld evaluates patch xpaths with System.Xml, which implements FULL XPath
1.0. Python's ElementTree implements only a subset of it: it cannot evaluate
text(), contains(), starts-with(), not(), or/and, axes or unions. Historically
this script said "UNSUPPORTED" and skipped the live check for those rather than
guessing - deliberate, because a wrong hit-count is worse than none, but a real
gap, and gaps cluster on the interesting expressions. Nobody needs text() for a
simple stat edit.

So this script now uses lxml when it is importable. lxml wraps libxml2 and
implements the same full XPath 1.0 as System.Xml, which turns that whole class
of skipped checks into real ones.

The split is deliberately conservative, because four agents depend on this
tool's verdicts:

  * an xpath that to_elementtree_xpath() CAN translate is still evaluated with
    findall(). lxml ships the very same ElementPath engine as ElementTree, so
    those answers do not move whichever library parsed the tree.
  * lxml's full XPath is used ONLY for expressions ElementTree had to skip.

An lxml upgrade can therefore only ADD findings, never silently change an
existing one. Without lxml the script behaves exactly as it always did, prints
one line saying so, and never fails on the missing import.

MAINTENANCE
===========
The one thing to keep current is OPS_NEEDING_XPATH and MODIFYING_OPS below.
If Ludeon adds a PatchOperation class, add it there or this script will let an
unguarded operation through without comment.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

# --------------------------------------------------------------------------
# XPath engine: lxml when it is importable, ElementTree otherwise
# --------------------------------------------------------------------------
# STRICTLY OPTIONAL, like --live. This script ships as a portable skill and has
# to keep working on a machine with nothing but the standard library, so the
# import is guarded and a missing lxml costs exactly the checks it would have
# added - never an exception, never a changed verdict. See the module docstring
# for why the two engines are used side by side rather than one replacing the
# other.
try:
    from lxml import etree as LET                      # type: ignore
    HAVE_LXML = True
    LXML_VERSION = ".".join(str(x) for x in LET.LXML_VERSION)
except Exception:                                       # pragma: no cover
    LET = None                                          # type: ignore
    HAVE_LXML = False
    LXML_VERSION = ""

if HAVE_LXML:
    # remove_comments/remove_pis make lxml's trees shaped like ElementTree's,
    # which drops both during parse. Without them a def node's children can
    # include comment objects whose .tag is a FUNCTION, and check_value_shape
    # sorts child tags as strings - that is a TypeError crash, not a wrong
    # answer, so it is not optional.
    #
    # huge_tree lifts libxml2's node/depth limits (some mods ship very large
    # def files); resolve_entities=False keeps an external entity in a def file
    # from being fetched.
    _DEF_PARSER_ARGS = dict(remove_comments=True, remove_pis=True,
                            resolve_entities=False, huge_tree=True)
    _DEF_PARSER = LET.XMLParser(**_DEF_PARSER_ARGS)
    _DEF_PARSER_RECOVER = LET.XMLParser(recover=True, **_DEF_PARSER_ARGS)


def parse_def_doc(path: str):
    """
    Parse one Defs/*.xml into a root element. Raises on total failure; every
    caller counts the failures and reports them as skipped files.
    """
    if not HAVE_LXML:
        return ET.parse(path).getroot()
    try:
        return LET.parse(path, _DEF_PARSER).getroot()
    except Exception:
        # ElementTree accepts a handful of files libxml2's strict parser
        # rejects. Dropping such a file from the load set would show up as a
        # false "xpath matches 0 nodes", i.e. the exact failure mode this
        # validator exists to prevent - so recover instead of losing it.
        root = LET.parse(path, _DEF_PARSER_RECOVER).getroot()
        if root is None:
            raise ValueError(f"unparseable even in recover mode: {path}")
        return root


def _is_element(node) -> bool:
    """
    A full-XPath evaluation can return strings (text() or @attr) as well as
    element nodes. Only elements may go on to check_value_shape.
    """
    if isinstance(node, (str, bytes, bool, int, float)):
        return False
    return hasattr(node, "tag")


def engine_banner() -> str:
    """One line naming the xpath engine, and what the weaker one costs."""
    if HAVE_LXML:
        return (f"xpath engine: lxml {LXML_VERSION} - full XPath 1.0, the same "
                f"class of engine RimWorld itself uses, so text(), contains(), "
                f"starts-with(), not() and boolean predicates are CHECKED.")
    return ("xpath engine: xml.etree - a subset of XPath 1.0 only. Expressions "
            "using text(), contains(), starts-with(), not(), or/and, axes or "
            "unions are reported UNSUPPORTED and skipped. Install lxml "
            "('python -m pip install lxml') to have those checked too.")


# --------------------------------------------------------------------------
# Operation taxonomy
# --------------------------------------------------------------------------

# Operations that require an <xpath> child to mean anything.
OPS_NEEDING_XPATH = {
    "PatchOperationAdd",
    "PatchOperationInsert",
    "PatchOperationReplace",
    "PatchOperationRemove",
    "PatchOperationAttributeAdd",
    "PatchOperationAttributeSet",
    "PatchOperationAttributeRemove",
    "PatchOperationSetName",
    "PatchOperationAddModExtension",
    "PatchOperationConditional",
    "PatchOperationTest",
}

# Operations that actually change the document. These are the ones that want a
# guard, and the ones where a surprising hit count matters.
MODIFYING_OPS = {
    "PatchOperationAdd",
    "PatchOperationInsert",
    "PatchOperationReplace",
    "PatchOperationRemove",
    "PatchOperationAttributeAdd",
    "PatchOperationAttributeSet",
    "PatchOperationAttributeRemove",
    "PatchOperationSetName",
    "PatchOperationAddModExtension",
}

# Destructive ops where matching more nodes than intended is a real hazard.
DESTRUCTIVE_OPS = {"PatchOperationRemove", "PatchOperationReplace",
                   "PatchOperationSetName", "PatchOperationAttributeRemove"}

GUARD_OPS = {"PatchOperationConditional", "PatchOperationFindMod"}
CONTAINER_OPS = {"PatchOperationSequence"} | GUARD_OPS


def short(cls: str) -> str:
    """'Verse.PatchOperationRemove' -> 'PatchOperationRemove'."""
    return cls.rsplit(".", 1)[-1] if cls else ""


# --------------------------------------------------------------------------
# Finding collector
# --------------------------------------------------------------------------

class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def info(self, msg: str) -> None:
        self.infos.append(msg)

    def report(self, quiet: bool = False) -> int:
        for m in self.errors:
            print(f"  ERROR   {m}")
        for m in self.warnings:
            print(f"  WARN    {m}")
        if not quiet:
            for m in self.infos:
                print(f"  info    {m}")
        print()
        if self.errors:
            print(f"FAIL - {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
            return 1
        print(f"OK - 0 errors, {len(self.warnings)} warning(s)")
        return 0


# --------------------------------------------------------------------------
# Static checks
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# The dictionary-keyed field trap
# --------------------------------------------------------------------------
#
# A List<Foo> whose Foo declares LoadDataFromXmlCustom and reads the NODE NAME
# as a def reference is DICTIONARY-KEYED: the entry's tag is the def and its
# text is the value.
#
#     <wildAnimals><AA_Skyeel>1.0</AA_Skyeel></wildAnimals>      correct
#     <wildAnimals><li><animal>AA_Skyeel</animal>...</li></...>  DISCARDS THE DEF
#
# The <li> form makes FirstChild an element rather than text, the parse throws
# ArgumentNullException, and RimWorld drops the ENTIRE def. Nothing in the patch
# reports it; the def simply stops existing.
#
# This cost this project twice in one day: 101 CharacterDefs via `skillGains`
# and 26 BiomeDefs -- 94.8% of the planet -- via `wildAnimals`.
#
# The list is MEASURED, not remembered: for every field in the 1,558 vanilla def
# files, take the set of child tag names and ask what fraction are defNames in a
# 578-mod def dump. A field whose children are >=80% defNames, and which vanilla
# never writes with <li>, is dictionary-keyed. Regenerate with:
#     infrastructure/state/observed/2026-08-22/biome_cast/custom_loader_fields.txt
DICT_KEYED_FIELDS = {
    "statBases", "skillGains", "costList", "statOffsets", "skillRequirements",
    "possessions", "prefabs", "killedLeavings", "equippedStatOffsets",
    "products", "mutatorChances", "xenotypeChances", "terrain", "roomDefs",
    "scatterTerrain", "escorts", "baseWeatherCommonalities", "wildAnimals",
    "junkScaterrers", "saltwater_Uncommon", "saltwater_Common",
    "freshwater_Uncommon", "freshwater_Common", "coastalWildAnimals",
    "butcherProducts", "wildPlants", "pollutionWildAnimals",
    "comboLandmarkMutators", "scatter", "traits", "traders",
    "structureMemeWeights", "guards", "carriers", "perimeterScatteredThings",
    "killedLeavingsRanges", "fixedInventory", "perimeterScatterTerrain",
    "mtbDaysByBiome", "itemsToDrop", "customCountRanges", "bodyTypeGraphicPaths",
    "mineableCounts", "killedLeavingsPlayerHostile", "fillInterior",
}


def check_dict_keyed_fields(root: ET.Element, f: Findings) -> None:
    """
    Refuse an <li> written as a direct child of a dictionary-keyed field.

    This is a whole-def-loss defect and it is invisible at load: the patch
    applies, the XML is well-formed, and the def vanishes.
    """
    for el in root.iter():
        if el.tag not in DICT_KEYED_FIELDS:
            continue
        if not any(isinstance(c.tag, str) and c.tag == "li" for c in el):
            continue
        n = sum(1 for c in el if isinstance(c.tag, str) and c.tag == "li")
        example = ""
        first = next((c for c in el if isinstance(c.tag, str) and c.tag == "li"), None)
        if first is not None:
            inner = [c.tag for c in first if isinstance(c.tag, str)]
            if inner:
                example = (f" Found <li><{inner[0]}>...; the correct form is "
                           f"<SomeDefName>value</SomeDefName>.")
        f.error(
            f"<{el.tag}> holds {n} <li> element(s). This field is DICTIONARY-KEYED - "
            f"its entry tag IS the defName and its text is the value.{example} "
            f"An <li> here throws inside LoadDataFromXmlCustom and RimWorld "
            f"DISCARDS THE ENTIRE DEF, silently, with nothing in the patch to show "
            f"for it. This exact defect cost 26 BiomeDefs and 101 CharacterDefs in "
            f"one day."
        )


COMMENT_RE = re.compile(rb"<!--(.*?)-->", re.DOTALL)


def check_comments(raw: bytes, f: Findings) -> None:
    """
    XML forbids '--' inside a comment body. Most parsers reject the whole file,
    so this is a total-loss failure caused by something as innocent as a row of
    dashes used as a separator, or an ASCII arrow '->'.

    Checked on raw bytes because if the file fails to parse we still want to say
    *why*, and ElementTree's message ("not well-formed") does not name this.
    """
    for m in COMMENT_RE.finditer(raw):
        body = m.group(1)
        if b"--" in body:
            line = raw[: m.start()].count(b"\n") + 1
            snippet = body.decode("utf-8", "replace").strip().splitlines()
            preview = snippet[0][:70] if snippet else ""
            f.error(
                f"line ~{line}: comment body contains '--', which is illegal in "
                f"XML and breaks the whole file. Use '===' for rules and 'to' or "
                f"an arrow character instead. Near: {preview!r}"
            )
    # Unterminated comment: an odd count of '<!--' vs '-->'
    if raw.count(b"<!--") != raw.count(b"-->"):
        f.error("mismatched comment delimiters ('<!--' count != '-->' count)")


def iter_operations(elem: ET.Element, path: str = ""):
    """
    Yield (operation_element, human_readable_path) for every operation in the
    tree, descending into Sequence/Conditional/FindMod containers.
    """
    for i, op in enumerate(elem.findall("./Operation")):
        here = f"{path}Operation[{i + 1}]"
        yield op, here
        yield from _descend(op, here)


def _descend(op: ET.Element, path: str):
    cls = short(op.get("Class", ""))
    if cls == "PatchOperationSequence":
        ops = op.find("operations")
        if ops is not None:
            for j, sub in enumerate(ops.findall("li")):
                sub_path = f"{path} > operations/li[{j + 1}]"
                yield sub, sub_path
                yield from _descend(sub, sub_path)
    elif cls in GUARD_OPS:
        for branch in ("match", "nomatch"):
            sub = op.find(branch)
            if sub is not None:
                sub_path = f"{path} > {branch}"
                yield sub, sub_path
                yield from _descend(sub, sub_path)


def xpath_of(op: ET.Element) -> str | None:
    node = op.find("xpath")
    if node is None:
        return None
    return (node.text or "").strip()


def _guarded_by_identical_test(path: str, xp: str,
                               cond_tests: dict[str, str]) -> bool:
    """
    True for the one shape a 0-match CANNOT be a silent no-op in: an operation
    in the <match> branch of a PatchOperationConditional whose test xpath is
    byte-identical to the operation's own.

    If the test had matched nothing the <match> branch would never have run, so
    "matches 0 nodes, this does nothing" is a FALSE POSITIVE — the <nomatch>
    branch is what fires, and that is the whole point of the add-if-missing
    idiom (Jawa_Doctrine/Patches/DroidsAreMachines.xml: Replace under <match>,
    Add under <nomatch>, because neither FleshTypeDef declares <isOrganic> on
    disk — it is a C# field default).

    Deliberately narrow. <nomatch> is NOT included (an op there really can be a
    no-op), a differing xpath is NOT included (that is the copy-paste slip the
    warning above already catches), and only the immediately enclosing
    conditional counts. Widening any of those would blunt the 0-match check,
    which catches real bugs.
    """
    suffix = " > match"
    if not path.endswith(suffix):
        return False
    return cond_tests.get(path[: -len(suffix)]) == xp


def _dead_in_nomatch(path: str, xp: str,
                     cond_tests: dict[str, str]) -> bool:
    """
    The exact mirror of _guarded_by_identical_test(), and the OPPOSITE verdict.

    Reaching <nomatch> PROVES the test xpath matched nothing. So an operation
    there carrying that same xpath can never match either: it is dead on
    arrival, and no def dump is needed to know it. That is what makes this
    worth checking statically -- without --defs the 0-match check does not run
    at all, so today this shape passes silently.

    ⚠️ Only the FIRST operation in the branch is provably dead. A later
    sibling CAN legitimately use the test's xpath, because an earlier one may
    have created the node:

        nomatch: Sequence
          li[1] Add     xpath=/Defs/X            value=<foo>1</foo>   # creates
          li[2] Replace xpath=/Defs/X/foo        value=<foo>2</foo>   # now matches

    Contrived, but legal, and flagging it would be a false positive -- which is
    the one thing a static check must not produce.

    The healthy idiom is the differing xpath: test /Defs/X/foo, and Add
    /Defs/X. That is add-if-missing and is already covered by its own warning.
    """
    for suffix in (" > nomatch", " > nomatch > operations/li[1]"):
        if path.endswith(suffix):
            return cond_tests.get(path[: -len(suffix)]) == xp
    return False


def check_structure(root: ET.Element, f: Findings) -> list[tuple[ET.Element, str, str, bool]]:
    """
    Walk every operation, run the static checks, and return the list of
    (element, path, xpath, guarded_by_identical_test) tuples to be evaluated
    live. iter_operations yields a container BEFORE descending into it, so a
    conditional's test xpath is always recorded before its branches are seen.
    """
    if root.tag != "Patch":
        f.error(f"root element is <{root.tag}>, expected <Patch>")

    to_evaluate: list[tuple[ET.Element, str, str, bool]] = []
    cond_tests: dict[str, str] = {}

    top_level = root.findall("./Operation")
    if not top_level:
        f.warn("no <Operation> elements found - this patch file does nothing")

    for op, path in iter_operations(root):
        cls_attr = op.get("Class", "")
        cls = short(cls_attr)

        if not cls_attr:
            f.error(f"{path}: missing Class attribute")
            continue

        xp = xpath_of(op)

        if cls == "PatchOperationConditional" and xp:
            cond_tests[path] = xp

        if cls in OPS_NEEDING_XPATH:
            if xp is None:
                f.error(f"{path} ({cls}): no <xpath> child")
            elif not xp:
                f.error(f"{path} ({cls}): <xpath> is empty")
            else:
                if _dead_in_nomatch(path, xp, cond_tests):
                    f.error(
                        f"{path} ({cls}): this xpath is byte-identical to the "
                        f"enclosing conditional's test, and it is in <nomatch>. "
                        f"Reaching <nomatch> PROVES the test matched nothing, so "
                        f"this operation cannot match either - it is dead on "
                        f"arrival, whatever the defs say. For add-if-missing, "
                        f"the <nomatch> op must target the PARENT of the tested "
                        f"node, not the node itself.")
                to_evaluate.append(
                    (op, path, xp,
                     _guarded_by_identical_test(path, xp, cond_tests)))

        if cls == "PatchOperationFindMod" and op.find("mods") is None:
            f.error(f"{path} (PatchOperationFindMod): no <mods> child")

        if cls == "PatchOperationTest":
            f.warn(f"{path}: PatchOperationTest is obsolete - use "
                   f"PatchOperationConditional")

        # Replace's <value> must contain an element, not bare text. Supplying
        # only inner text produces a malformed def that loads and misbehaves.
        if cls == "PatchOperationReplace":
            val = op.find("value")
            if val is None:
                f.error(f"{path} (PatchOperationReplace): no <value> child")
            elif len(list(val)) == 0:
                f.error(f"{path} (PatchOperationReplace): <value> has no child "
                        f"element. Replace swaps the whole node, so <value> must "
                        f"contain the element itself, e.g. "
                        f"<value><MoveSpeed>5.2</MoveSpeed></value>")

        if cls in ("PatchOperationAdd", "PatchOperationInsert",
                   "PatchOperationAddModExtension"):
            if op.find("value") is None:
                f.error(f"{path} ({cls}): no <value> child")

        if cls in ("PatchOperationAttributeAdd", "PatchOperationAttributeSet",
                   "PatchOperationAttributeRemove"):
            if op.find("attribute") is None:
                f.error(f"{path} ({cls}): no <attribute> child")

        # Guard check: a modifying op sitting at the top level is unguarded.
        if cls in MODIFYING_OPS and " > " not in path:
            f.warn(f"{path} ({cls}): not wrapped in PatchOperationConditional or "
                   f"PatchOperationFindMod. If the target mod is absent or fixes "
                   f"its def upstream, this logs a red error on every launch.")

        # Conditional test vs inner op xpath.
        if cls == "PatchOperationConditional" and xp:
            for branch in ("match", "nomatch"):
                sub = op.find(branch)
                if sub is None:
                    continue
                sub_xp = xpath_of(sub)
                sub_cls = short(sub.get("Class", ""))
                if sub_xp and sub_cls in MODIFYING_OPS and sub_xp != xp:
                    f.warn(f"{path} > {branch} ({sub_cls}): inner xpath differs "
                           f"from the conditional test.\n"
                           f"              test:  {xp}\n"
                           f"              inner: {sub_xp}\n"
                           f"            Intentional for add-if-missing patterns; "
                           f"otherwise it means you test one node and edit another.")
            if op.find("match") is None and op.find("nomatch") is None:
                f.warn(f"{path}: PatchOperationConditional with neither <match> "
                       f"nor <nomatch> - does nothing")

    return to_evaluate


# --------------------------------------------------------------------------
# Live xpath evaluation
# --------------------------------------------------------------------------

# ElementTree understands a restricted XPath. Translate the common RimWorld
# idioms; refuse anything we cannot translate faithfully.
UNSUPPORTED_TOKENS = ("starts-with(", "contains(", " or ", " and ", "not(",
                      "text()", "::", "|")


def rebase_for_root_element(xp: str) -> str:
    """
    Strip the leading `Defs` step so an xpath can be evaluated against the <Defs>
    ROOT ELEMENT rather than against the document.

    🔴 RimWorld evaluates a patch xpath against the XmlDocument, whose CHILD is
    <Defs>, so `Defs/XenotypeDef[...]` and `/Defs/XenotypeDef[...]` both mean the
    same thing there. lxml and ElementTree evaluate against the <Defs> element
    itself, where `Defs/...` means `Defs/Defs/...` and matches NOTHING.

    ⚠️ `to_elementtree_xpath` already handled this for the ElementPath branch. The
    lxml branch did not, so EVERY xpath using text(), contains(), starts-with(),
    not(), an axis or a union - exactly the expressions that force the lxml branch -
    came back 0 and read as a dead xpath. Found 2026-08-22 when 25 of the 28
    operations in `BodySizeIsReal.xml` reported 0 while the same expression matched
    when run against the same file by hand.
    """
    s = xp.strip()
    if s.startswith("/Defs/"):
        return s[len("/Defs/"):]
    if s.startswith("//"):
        return "." + s
    if s.startswith("/"):
        return s
    if s.startswith("Defs/"):
        return s[len("Defs/"):]
    return s


def to_elementtree_xpath(xp: str) -> str | None:
    """
    Convert a RimWorld xpath into an ElementTree-evaluable one, relative to the
    <Defs> root. Returns None when faithful translation is not possible.
    """
    if any(tok in xp for tok in UNSUPPORTED_TOKENS):
        return None

    s = xp.strip()
    if s.startswith("/Defs/"):
        s = s[len("/Defs/"):]
    elif s.startswith("//"):
        s = ".//" + s[2:]
    elif s.startswith("/"):
        return None
    # 🔴 `Defs/...` with NO leading slash is equally valid and equally common in the
    # wild, because RimWorld evaluates the xpath against the XmlDocument — whose CHILD
    # is <Defs> — while ElementTree and lxml evaluate against the <Defs> ROOT ELEMENT.
    # So the bare form silently means `Defs/Defs/...` here and matches nothing.
    # ⚠️ It reported a FALSE "0 nodes in the on-disk Defs" on every such op, which is
    # the same shape as a genuinely dead xpath — the one thing this validator exists to
    # tell apart. Found 2026-08-21 when all four ops of a patch known to work in game
    # came back 0; 42 xpaths across this repo's own patches were affected.
    elif s.startswith("Defs/"):
        s = s[len("Defs/"):]
    if not s:
        return None

    # [defName="X"]  ->  [defName='X']   (ET wants the child-value form)
    s = re.sub(r'\[\s*(\w+)\s*=\s*"([^"]*)"\s*\]', r"[\1='\2']", s)
    s = re.sub(r"\[\s*@(\w+)\s*=\s*\"([^\"]*)\"\s*\]", r"[@\1='\2']", s)

    # Anything left that ET will choke on
    if re.search(r"\[[^\]]*[()][^\]]*\]", s):
        return None

    # 🔴 ElementPath's [N] is "the Nth sibling carrying this tag". XPath 1.0's is
    # "the Nth of the nodes the PREVIOUS predicate kept". They disagree the moment
    # a step carries two predicates, and the disagreement reads as a DEAD xpath
    # rather than as a wrong one - which is the one failure this tool exists to
    # catch, reported backwards. Measured on Royalty's Empire, whose pawnGroupMakers
    # are Trader, Combat(100), Combat(10), Settlement:
    #   li[kindDef="Combat"][1]  ET -> 0 matches (li[1] is the Trader)
    #                            RimWorld -> the commonality-100 group
    # RimWorld evaluates with System.Xml, so RimWorld is the one that is right.
    if re.search(r"\]\s*\[", s):
        return None

    # ElementPath compares [tag='text'] and nothing else. [commonality=100] is a
    # legal XPath 1.0 numeric comparison that findall() silently never matches.
    if re.search(r"\[[^\]]*=\s*[^'\"\]]", s):
        return None

    return s


# --------------------------------------------------------------------------
# Load-set resolution: ModsConfig + About.xml + LoadFolders.xml
# --------------------------------------------------------------------------

_MODS_CONFIG_TAIL = os.path.join(
    "AppData", "LocalLow", "Ludeon Studios",
    "RimWorld by Ludeon Studios", "Config", "ModsConfig.xml")

DEFAULT_MODS_CONFIG = os.path.join(os.path.expanduser("~"), _MODS_CONFIG_TAIL)


def find_mods_config() -> tuple[str | None, list[str]]:
    """
    Locate ModsConfig.xml. Returns (path or None, paths tried).

    🔴 `expanduser("~")` ALONE IS WRONG UNDER WSL, and it fails silently in the
    worst direction: `~` is /home/<user>, the file is never found, and the tool
    drops to an UNSCOPED scan of every installed mod and every version folder -
    whose own docstring says its match counts do not describe the running game.
    The run still prints OK. Measured 2026-08-14: every WSL `--defs` run without
    an explicit --mods-config had been silently unscoped.
    """
    tried: list[str] = []
    cands = [os.path.join(os.path.expanduser("~"), _MODS_CONFIG_TAIL)]
    for env in ("USERPROFILE", "HOME"):
        v = os.environ.get(env)
        if v:
            cands.append(os.path.join(v, _MODS_CONFIG_TAIL))
    # WSL: the Windows profile is mounted, and ~ never points at it.
    for drive in sorted(glob.glob("/mnt/[a-z]/Users/*")):
        cands.append(os.path.join(drive, _MODS_CONFIG_TAIL))
    hits: list[str] = []
    for c in cands:
        if c in tried:
            continue
        tried.append(c)
        if os.path.isfile(c):
            hits.append(c)
    if not hits:
        return None, tried
    # More than one profile can hold one; the game reads the newest.
    hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return hits[0], tried


class LoadSetUnmeasurable(RuntimeError):
    """
    The load set could not be measured at all - a --defs root was unreadable,
    or so few active mods resolved that the def set cannot describe the running
    game. 🔴 UNMEASURABLE IS A DISTINCT, TERMINAL OUTCOME FROM MEASURED-ZERO.
    Never let it degrade into "no matches found"; that reads as a clean bill of
    health for exactly the patches this tool exists to catch.
    """


class ModInfo:
    """One installed mod: where it lives, what it is called, what it loads."""

    __slots__ = ("package_id", "name", "folder", "folders")

    def __init__(self, package_id: str, name: str, folder: str) -> None:
        self.package_id = package_id          # lowercased
        self.name = name                      # display name for reports
        self.folder = folder                  # mod root directory
        self.folders: list[str] = []          # resolved content folders


def parse_xml(path: str) -> ET.Element | None:
    """Tolerant parse: retry once without the XML declaration (BOM/encoding)."""
    try:
        return ET.parse(path).getroot()
    except Exception:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
            raw = re.sub(r"^\s*<\?xml[^>]*\?>", "", raw).strip()
            return ET.fromstring(raw)
        except Exception:
            return None


def parse_mods_config(path: str) -> tuple[list[str], str]:
    """
    Return (active packageIds lowercased, in load order; 'major.minor' version).

    Deliberately ignores <knownExpansions>. Those entries are ALSO present in
    <activeMods>; adding them produces a double count of the DLC and has caused
    two separate wrong-answer incidents on this project.
    """
    root = parse_xml(path)
    if root is None:
        raise OSError(f"cannot parse ModsConfig at {path}")

    active: list[str] = []
    node = root.find("activeMods")
    if node is not None:
        for li in node.findall("li"):
            if li.text and li.text.strip():
                active.append(li.text.strip().lower())

    version = ""
    vnode = root.find("version")
    if vnode is not None and vnode.text:
        m = re.match(r"\s*(\d+\.\d+)", vnode.text)
        if m:
            version = m.group(1)
    return active, version


def read_about(mod_dir: str) -> tuple[str, str] | None:
    """
    (packageId lowercased, display name) from <mod_dir>/About/About.xml.

    The packageId MUST be a direct child of the root <ModMetaData>. A regex for
    the first packageId in the file, or a recursive find(), happily returns one
    out of a <modDependencies> block instead - which silently maps Harmony to
    Camera+ and poisons the whole mod index.
    """
    about = os.path.join(mod_dir, "About", "About.xml")
    if not os.path.isfile(about):
        return None
    root = parse_xml(about)
    if root is None:
        return None
    pid_node = root.find("packageId")          # direct child only
    if pid_node is None or not (pid_node.text or "").strip():
        return None
    name_node = root.find("name")
    name = (name_node.text or "").strip() if name_node is not None else ""
    return pid_node.text.strip().lower(), (name or os.path.basename(mod_dir.rstrip("/\\")))


def discover_mods(defs_roots: list[str]) -> dict[str, ModInfo]:
    """
    Index every installed mod under the given roots by packageId.

    A candidate directory is the root itself or any IMMEDIATE subdirectory; it
    is a mod when About/About.xml exists. That covers all three real layouts:
      steamapps/workshop/content/294100/<id>/
      RimWorld/Data/<Core|Royalty|Odyssey|...>/
      RimWorld/Mods/<name>/
    First root wins on a packageId collision.
    """
    index: dict[str, ModInfo] = {}
    unreadable: list[str] = []
    for root_dir in defs_roots:
        # 🔴 PROBE BY ENUMERATION, NOT isdir. A root can pass isdir and still
        # fail to list (permissions, a dead symlink, /mnt/c after a WSL
        # restart, a Windows path handed to a Linux interpreter). The old code
        # printed "path not found, skipping" and carried on, which turns an
        # ABSENT root into an EMPTY one - every xpath under it then reads as
        # "matches 0 nodes", and a conditional-guarded file can come back OK
        # against a load set that is missing most of the game.
        try:
            entries = sorted(os.listdir(root_dir))
        except OSError as e:
            unreadable.append(f"{root_dir}  ({e.strerror or e})")
            continue
        candidates = [root_dir] + [os.path.join(root_dir, e) for e in entries]
        for cand in candidates:
            if not os.path.isdir(cand):
                continue
            got = read_about(cand)
            if not got:
                continue
            pid, name = got
            if pid not in index:
                index[pid] = ModInfo(pid, name, cand)
    if unreadable:
        raise LoadSetUnmeasurable(
            "--defs root(s) could not be read, so the load set is UNMEASURABLE, "
            "not empty:\n    " + "\n    ".join(unreadable) +
            "\n  A missing root is not a smaller game - it is no answer at all. "
            "Fix the path (or run the interpreter that can see it) and re-run.")
    return index


def _norm_rel(rel: str) -> str:
    """'/' and '\\' both mean the mod root. Otherwise normalise separators."""
    rel = (rel or "").strip()
    if rel in ("", "/", "\\", ".", "./"):
        return ""
    return rel.replace("\\", "/").strip("/")


def _condition_ok(li: ET.Element, active: set[str]) -> bool:
    """
    Honour IfModActive / IfModNotActive, case-insensitively, comma tolerant.

    IfModNotActive is load-bearing, not decoration: Vanilla Animals Expanded
    uses it to drop four animals when Odyssey is active. Resolving it the wrong
    way invents or hides defs, which is precisely the bug class this validator
    exists to catch.
    """
    want = li.get("IfModActive")
    if want:
        ids = [x.strip().lower() for x in want.split(",") if x.strip()]
        if not all(i in active for i in ids):
            return False
    nope = li.get("IfModNotActive")
    if nope:
        ids = [x.strip().lower() for x in nope.split(",") if x.strip()]
        if any(i in active for i in ids):
            return False
    return True


def resolve_load_folders(mod_dir: str, version: str, active: set[str]) -> list[str]:
    """
    The content folders this mod contributes at the target game version.

    With a LoadFolders.xml: take the <v{major.minor}> block and every <li> in
    it whose IfModActive / IfModNotActive condition holds. ElementTree drops
    comments for us, so commented-out entries cost nothing to ignore.

    Without one (or without a block for this version): <mod>/<version> if it
    exists, else the mod root.
    """
    lf = os.path.join(mod_dir, "LoadFolders.xml")
    folders: list[str] = []

    if version and os.path.isfile(lf):
        root = parse_xml(lf)
        if root is not None:
            block = root.find(f"v{version}")
            if block is not None:
                for li in block.findall("li"):
                    if not _condition_ok(li, active):
                        continue
                    rel = _norm_rel(li.text)
                    p = os.path.join(mod_dir, *rel.split("/")) if rel else mod_dir
                    if os.path.isdir(p) and p not in folders:
                        folders.append(p)
                return folders

    # No LoadFolders.xml: the game loads the mod ROOT *and* the versioned
    # folder, not one or the other. Getting this wrong silently hides content,
    # which for a validator means false "target not found" verdicts.
    #
    # Measured on a 562-mod stack (2026-08-10): 35 active mods ship a root
    # Defs/ alongside a version folder — RIMMSqol (178 defs), Way Better
    # Romance (64), Numbers (40), LWM's Deep Storage (18), Adaptive Storage
    # Framework (11) — for 667 def nodes and 24 PatchOperations total. The
    # giveaway was 28 defs across 4 mods failing to resolve
    # ParentName="AdaptiveStorageBase": the framework declares that base in its
    # ROOT Defs/ThingDefBase.xml. Those mods work in game and the log carries
    # no inheritance errors, so the root is definitely loaded.
    #
    # Order: root first, then versioned, so a version-specific override wins
    # over the root's copy of the same def under last-in-wins.
    versioned = os.path.join(mod_dir, version) if version else ""
    folders.append(mod_dir)
    if versioned and os.path.isdir(versioned) and versioned != mod_dir:
        folders.append(versioned)
    return folders


def _iter_def_xml(start_dir: str):
    """Every *.xml under start_dir, skipping VCS/cache noise."""
    for dirpath, dirnames, filenames in os.walk(start_dir):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for fn in filenames:
            if fn.lower().endswith(".xml"):
                yield os.path.join(dirpath, fn)


def _is_defs_dir(dirpath: str) -> bool:
    """The unscoped heuristic: this directory is, or sits under, a Defs tree."""
    return (os.path.basename(dirpath).lower() == "defs"
            or f"{os.sep}Defs{os.sep}" in dirpath + os.sep)


# Every parsed doc is a (path, root_element, mod_display_name) triple: the mod
# name is what makes a multi-mod match distinguishable from a duplicated file.
def load_defs_scoped(mods: list[ModInfo]) -> tuple[list, int]:
    """Parse Defs/**/*.xml from each active mod's resolved folders, in order."""
    docs: list = []
    skipped = 0
    seen: set[str] = set()
    for mod in mods:
        for folder in mod.folders:
            defs_dir = os.path.join(folder, "Defs")
            if not os.path.isdir(defs_dir):
                continue
            for p in _iter_def_xml(defs_dir):
                key = os.path.normcase(os.path.abspath(p))
                if key in seen:
                    continue
                seen.add(key)
                try:
                    docs.append((p, parse_def_doc(p), mod.name))
                except Exception:
                    skipped += 1
    return docs, skipped


def load_defs_all_versions(defs_roots: list[str],
                           index: dict[str, ModInfo]) -> tuple[list, int]:
    """
    The old unscoped behaviour, kept as an escape hatch: every Defs tree under
    every root, inactive mods and stale version folders included. Match counts
    from this mode do NOT describe the running game.
    """
    owners = sorted(((m.folder, m.name) for m in index.values()),
                    key=lambda t: len(t[0]), reverse=True)
    docs: list = []
    skipped = 0
    for root_dir in defs_roots:
        if not os.path.isdir(root_dir):
            continue
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            if not _is_defs_dir(dirpath):
                continue
            owner = os.path.basename(dirpath)
            for folder, name in owners:
                if dirpath == folder or dirpath.startswith(folder + os.sep):
                    owner = name
                    break
            for fn in filenames:
                if not fn.lower().endswith(".xml"):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    docs.append((p, parse_def_doc(p), owner))
                except Exception:
                    skipped += 1
    return docs, skipped


def build_load_set(defs_roots: list[str], mods_config: str | None,
                   all_versions: bool) -> tuple[list, list[ModInfo]]:
    """
    Resolve the load set and parse it. Prints the scoping summary.
    Returns (docs, active ModInfo list in load order).
    """
    index = discover_mods(defs_roots)

    if mods_config and not all_versions:
        try:
            active_ids, version = parse_mods_config(mods_config)
        except OSError as e:
            print(f"  info    {e} - falling back to an unscoped scan")
            mods_config = None

    if all_versions or not mods_config:
        docs, skipped = load_defs_all_versions(defs_roots, index)
        mods = list(index.values())
        for m in mods:
            m.folders = [m.folder]
        if all_versions:
            print(f"  info    --all-versions: UNSCOPED scan of {len(index):,} "
                  f"installed mod(s), every version folder. Match counts do not "
                  f"describe the running game.")
        else:
            print(f"  info    no ModsConfig.xml available - unscoped scan of "
                  f"{len(index):,} installed mod(s).")
        if skipped:
            print(f"  info    {skipped} def file(s) could not be parsed and were skipped")
        print(f"  info    load set: {len(docs):,} def files")
        return docs, mods

    active_set = set(active_ids)
    mods: list[ModInfo] = []
    missing: list[str] = []
    for pid in active_ids:                     # load order is meaningful
        mod = index.get(pid)
        if mod is None:
            missing.append(pid)
            continue
        mod.folders = resolve_load_folders(mod.folder, version, active_set)
        mods.append(mod)

    docs, skipped = load_defs_scoped(mods)

    if skipped:
        print(f"  info    {skipped} def file(s) could not be parsed and were skipped")
    print(f"  info    load set: {len(active_ids):,} active mods, {len(mods):,} found "
          f"on disk, target version {version or '?'} -> {len(docs):,} def files")
    if missing:
        shown = ", ".join(missing[:10])
        more = f" (+{len(missing) - 10} more)" if len(missing) > 10 else ""
        # 🔴 A FEW missing mods is a broken install and worth a line. MOST of
        # them missing means the roots do not describe this game, and every
        # xpath answer below would be wrong in the safe-looking direction.
        # Measured 2026-08-14: the same check under Windows python.exe saw 22
        # of 580 active mods and reported it as info.
        if len(missing) > max(10, len(active_ids) // 10):
            raise LoadSetUnmeasurable(
                f"{len(missing)} of {len(active_ids)} active mods have no folder "
                f"under --defs, so the load set does NOT describe the running "
                f"game and its match counts are meaningless: {shown}{more}\n"
                f"  Roots given: {', '.join(defs_roots)}\n"
                f"  Usually a path an interpreter cannot see (a Windows python "
                f"reading /mnt/c, or the reverse), not a broken install.")
        print(f"  WARN    {len(missing)} active packageId(s) have no folder under "
              f"--defs - a broken install or a renamed mod: {shown}{more}")
    return docs, mods


# --------------------------------------------------------------------------
# The runtime-patch blind spot: what other mods' Patches/ mention
# --------------------------------------------------------------------------

class PatchScanner:
    """
    Lazy, single-pass index of the active mods' Patches/**/*.xml text.

    Only touched when an xpath matches 0 nodes, which is rare, so the cost is
    normally zero. Built at most once per process.
    """

    def __init__(self, mods: list[ModInfo]) -> None:
        self._mods = mods
        self._files: list[tuple[str, str, str]] | None = None   # (mod, basename, text)

    def _build(self) -> None:
        if self._files is not None:
            return
        self._files = []
        for mod in self._mods:
            for folder in mod.folders:
                pdir = os.path.join(folder, "Patches")
                if not os.path.isdir(pdir):
                    continue
                for p in _iter_def_xml(pdir):
                    try:
                        with open(p, encoding="utf-8", errors="replace") as fh:
                            self._files.append((mod.name, os.path.basename(p), fh.read()))
                    except OSError:
                        continue

    def mods_mentioning(self, name: str, ignore_basename: str = "") -> list[str]:
        """Display names of mods whose patch files contain `name` as text."""
        if not name:
            return []
        self._build()
        out: list[str] = []
        for mod_name, base, text in self._files or ():
            if ignore_basename and base.lower() == ignore_basename.lower():
                continue    # our own deployed copy of the file under validation
            if mod_name in out:
                continue
            if name in text:
                out.append(mod_name)
        return out


def leaf_name(xp: str) -> str:
    """'/Defs/ThingDef[defName="X"]/race/wildBiomes/Desert[2]' -> 'Desert'."""
    seg = xp.strip().rstrip("/").split("/")[-1]
    seg = re.sub(r"\[.*$", "", seg).strip().lstrip("@")
    return seg


# --------------------------------------------------------------------------
# Matching and reporting
# --------------------------------------------------------------------------

def count_matches(xp: str, docs) -> tuple[int, list[str], list, int, bool]:
    """
    Evaluate a RimWorld xpath over the load set.

    Returns (total hits, per-file locations labelled by MOD, matched ELEMENTS,
    number of distinct mods hit, unsupported). The mod label is what turns
    "7 matches in Races_Animal_Armadillo.xml" - which reads like a duplicated
    file - into either one mod (a real duplicate, worth a warning) or several
    mods (several definitions of the same def, which is normal).

    Two engines, chosen per expression and never per taste:

      translatable  -> findall() with the translated expression. This is the
                       historical path and it stays byte-identical, because
                       lxml implements the same ElementPath as ElementTree.
      not           -> lxml's full XPath 1.0, if lxml is importable; otherwise
                       unsupported=True and the caller skips the check exactly
                       as it always did.
    """
    et_xpath = to_elementtree_xpath(xp)
    compiled = None
    if et_xpath is None:
        if not HAVE_LXML:
            return 0, [], [], 0, True
        try:
            compiled = LET.XPath(rebase_for_root_element(xp))
        except Exception:
            # Not valid XPath 1.0 at all, or uses a namespace prefix we have
            # no mapping for. Saying "cannot evaluate" is honest; guessing is
            # not. RimWorld will log its own error for a truly malformed one.
            return 0, [], [], 0, True

    total = 0
    where: list[str] = []
    elems: list = []
    mods_hit: list[str] = []
    for path, root, mod_name in docs:
        try:
            if compiled is not None:
                hits = compiled(root)
                if not isinstance(hits, list):
                    # count(), boolean(), string()... RimWorld's patch xpaths
                    # must select a NODE SET, so there is no hit count to
                    # report here and pretending it is 0 would be a false error.
                    return 0, [], [], 0, True
            else:
                hits = root.findall(et_xpath)
        except Exception:
            continue
        if hits:
            total += len(hits)
            where.append(f"{mod_name}: {os.path.basename(path)}({len(hits)})")
            elems.extend(h for h in hits if _is_element(h))
            if mod_name not in mods_hit:
                mods_hit.append(mod_name)
    return total, where, elems, len(mods_hit), False



def _dump_collisions(raw):
    """(collided type names -> counts in write order, total defs lost).

    A def dump whose manifest names the same TYPE twice has silently overwritten
    one type's file with another's. The duplicate keys are the ONLY surviving
    evidence — `json.load` discards them, because a dict cannot hold a duplicate
    key — so a validator that does not look here cannot tell the reader that the
    ground truth it is validating against has holes in it.

    🔑 This is deliberately a local 8 lines rather than an import. The canonical
    implementation is `measure.dumpdb.read_manifest` in the
    `measuring-large-artifacts` skill, but this file ships as part of a skill to
    machines that may not have it, and a validator that cannot run is worse than
    one that repeats a little logic. If the two ever disagree, the skill wins.
    """
    order = {}
    try:
        def hook(pairs):
            return dict(pairs)
        json.loads(raw, object_pairs_hook=lambda ps: (
            [order.setdefault(k, []).append(v) for k, v in ps]
            if ps and all(isinstance(v, int) for _, v in ps) and len(ps) > 50
            else None) or dict(ps))
    except ValueError:
        return {}, 0
    coll = {k: v for k, v in order.items() if len(v) > 1}
    return coll, sum(sum(v[:-1]) for v in coll.values())


def check_value_shape(op: ET.Element, cls: str, path: str,
                      targets: list, f: Findings) -> None:
    """
    Compare the shape of <value>'s children against the children the target node
    ALREADY has in the real Defs.

    RimWorld has two different child shapes and they are not interchangeable:

      plain list        <tools><li>...</li><li>...</li></tools>
      dictionary-keyed  <wildBiomes><Desert>0.3</Desert></wildBiomes>
                        <baseWeatherCommonalities><Clear>18</Clear></...>
                        <statBases><MoveSpeed>4.6</MoveSpeed></statBases>

    In the dictionary form the ELEMENT NAME is the def. Writing <li> there makes
    the engine look for a def literally named "li", which fails to resolve and
    then throws the ENTIRE parent def away — so a shape mistake does not merely
    fail to apply, it deletes content that was previously working. This check
    exists because that happened: an <li>-shaped add into
    <baseWeatherCommonalities> destroyed seven BiomeDefs including three Core
    ones, and the only log evidence was a cross-reference error naming "li".

    Comparing against the live node is better than a hardcoded field list,
    because it stays correct for modded fields nobody has enumerated.
    """
    val = op.find("value")
    if val is None or not targets:
        return
    value_kids = [c.tag for c in val]
    if not value_kids:
        return

    existing = [c.tag for t in targets for c in t]
    if not existing:
        return  # nothing to compare against; can't judge

    target_is_list = all(t == "li" for t in existing)
    value_is_list = all(k == "li" for k in value_kids)

    if target_is_list and not value_is_list:
        f.error(
            f"{path} ({cls}): value shape mismatch. The target node's existing "
            f"children are all <li> (a plain list), but <value> supplies "
            f"{sorted(set(value_kids))}. Wrap each entry in <li>.")
    elif not target_is_list and value_is_list:
        f.error(
            f"{path} ({cls}): value shape mismatch. The target node is "
            f"DICTIONARY-KEYED — its existing children are named after defs "
            f"(e.g. {', '.join(sorted(set(existing))[:3])}) — but <value> uses "
            f"<li>. RimWorld will look for a def literally named 'li', fail to "
            f"resolve it, and DISCARD THE WHOLE PARENT DEF. Write "
            f"<DefName>value</DefName> instead of <li>.")


# --------------------------------------------------------------------------
# the live def index  (optional)
# --------------------------------------------------------------------------
# The on-disk Defs are what an author WROTE. They are not what the game HAS:
# PatchOperations run at load and can create, rewrite or delete defs, and this
# validator cannot see any of it. That blind spot is why a "0 nodes matched"
# result has always been ambiguous -- it might be a typo, or it might be a node
# some other mod creates at runtime, and the checker could only guess by looking
# for the leaf name in other mods' patch files.
#
# A live dump (src/RimMandrake/RimDefDump) removes the guess. With one, "does this def
# actually exist in the running game" becomes a lookup.
#
# STRICTLY OPTIONAL. This script ships as a portable skill and must keep working
# on a machine that has never produced a dump; without --live every check below
# is skipped and behaviour is unchanged.

_LIVE_DEFNAME_RE = re.compile(r'"defName"\s*:\s*"([^"]+)"')
# /Defs/ThingDef[defName="X"]/...  or  /Defs/ThingDef[@Name="X"]/...
_XPATH_IDENT_RE = re.compile(r'\[\s*@?(defName|Name)\s*=\s*"([^"]+)"\s*\]')


class LiveIndex:
    """defNames present in a live DefDump, or an empty index if none was given."""

    def __init__(self) -> None:
        self.names: set[str] = set()
        self.by_type: dict[str, set[str]] = {}
        self.game_version = ""
        self.mod_count = 0
        self.loaded = False
        #: (collided type name -> counts in write order, total defs lost).
        #: Non-empty means the ground truth this validator is checking against
        #: has holes, and a `0` read from it means "unmeasured", not "none".
        self.dump_collisions: tuple = ({}, 0)

    def has(self, name: str) -> bool:
        return name in self.names

    @classmethod
    def load(cls, dumpdir: str) -> "LiveIndex":
        idx = cls()
        defs_dir = os.path.join(dumpdir, "defs")
        if not os.path.isdir(defs_dir):
            # Tolerate being pointed at the defs/ folder itself.
            if os.path.basename(dumpdir.rstrip("\\/")).lower() == "defs":
                defs_dir = dumpdir
            else:
                print(f"  (--live: no defs/ under {dumpdir}; live checks skipped)")
                return idx

        # 🔴 defs/ ACCUMULATES; it is not a snapshot. RimDefDump writes a file per
        # def type that exists NOW and never deletes the file for a type that has
        # stopped existing, so a folder that looks freshly written can hold
        # orphans from a mod removed weeks ago. Measured 2026-08-13: 528 files on
        # disk against 511 live types — 17 orphans, oldest 2026-08-10, including
        # SkinDef.json from four mech mods removed that afternoon. They put 174
        # dead defNames into the index, and a dead defName in the index makes a
        # patch that references a REMOVED def validate clean. Fail-toward-success.
        #
        # manifest.json IS a true snapshot of the load, so it is the authority on
        # which types are live. Restrict to it when it is present.
        live_types: set[str] | None = None
        man = os.path.join(os.path.dirname(defs_dir), "manifest.json")
        if os.path.isfile(man):
            try:
                with open(man, encoding="utf-8") as fh:
                    raw = fh.read()
                m = re.search(r'"gameVersion"\s*:\s*"([^"]+)"', raw)
                idx.game_version = m.group(1) if m else ""
                m = re.search(r'"modCount"\s*:\s*(\d+)', raw)
                idx.mod_count = int(m.group(1)) if m else 0
                try:
                    # ⚠️ KEYS ONLY, and that is why this is correct. The 532
                    # defCounts entries sit under 517 distinct NAMES, so a
                    # plain parse loses no name — only the shadowed VALUES.
                    # Verified 2026-08-21 by set comparison against a
                    # duplicate-preserving parse; do not "fix" this to read a
                    # value without reading `dump_collisions` below.
                    counts = (json.loads(raw).get("defCounts") or {})
                    if counts:
                        live_types = set(counts.keys())
                except (ValueError, AttributeError):
                    live_types = None
                idx.dump_collisions = _dump_collisions(raw)
            except OSError:
                pass

        # Streamed with a carry-over tail: ThingDef.json alone can be several
        # hundred MB, and a validator that needs a gigabyte of RAM is a
        # validator nobody runs.
        skipped_orphans: list[str] = []
        for fn in sorted(os.listdir(defs_dir)):
            if not fn.lower().endswith(".json"):
                continue
            deftype = fn[:-5]
            if live_types is not None and deftype not in live_types:
                skipped_orphans.append(deftype)
                continue
            found: set[str] = set()
            try:
                with open(os.path.join(defs_dir, fn), encoding="utf-8",
                          errors="replace") as fh:
                    tail = ""
                    while True:
                        chunk = fh.read(4 << 20)
                        if not chunk:
                            break
                        blob = tail + chunk
                        for m in _LIVE_DEFNAME_RE.finditer(blob):
                            found.add(m.group(1))
                        # A defName could straddle a chunk boundary.
                        tail = blob[-256:]
            except OSError:
                continue
            if found:
                idx.by_type[deftype] = found
                idx.names |= found

        coll, lost = getattr(idx, "dump_collisions", ({}, 0))
        # Only the collisions that actually LOST defs make a count unmeasured.
        # Where every earlier writer held 0, the name is ambiguous but the count
        # is right — and warning about those would be an unearned warning, which
        # is how a warning gets ignored.
        harmful = {k: v for k, v in coll.items() if sum(v[:-1])}
        if harmful:
            # The dump itself is damaged, and a reader who does not know that
            # will read a `0` from it as "none exist". Say it where the numbers
            # are being used, not in a file nobody opens.
            print(f"  (--live: ⚠️ the dump lost {lost} defs to {len(harmful)} "
                  f"filename collision(s) — a count of "
                  f"{', '.join(sorted(harmful)[:4])}"
                  f"{' …' if len(harmful) > 4 else ''} from it is UNMEASURED, "
                  f"not zero. `measure coverage` names them.)")

        if skipped_orphans:
            # Say it out loud. A silently-narrowed index is the same class of
            # problem as the wide one it replaced.
            print(f"  (--live: skipped {len(skipped_orphans)} orphan def-type "
                  f"file(s) absent from manifest.json — stale leftovers from "
                  f"removed mods, not part of this load: "
                  f"{', '.join(skipped_orphans[:6])}"
                  f"{' …' if len(skipped_orphans) > 6 else ''})")

        idx.loaded = bool(idx.names)
        return idx

    # ----------------------------------------------------------------
    # the same index, precomputed  (--defnames / --write-defnames)
    # ----------------------------------------------------------------
    # load() above re-derives this set on EVERY run by regex-streaming the whole
    # DefDump - 1.3 GB, of which 810 MB is ThingDef.json - to end up with a few
    # hundred thousand short strings. The names are the only part any check
    # actually consults (has()), so the read is ~99.9% waste, paid per
    # invocation, on a slow mount, by four agents.
    #
    # So: extract once, keep the extract. The file is small enough to commit,
    # cannot be regenerated without a game load, and its value does not expire
    # with the dump - which by CLAUDE.md's own test makes it a work product
    # rather than a cache.
    #
    # THE FORMAT IS NOT NEW. It mirrors manifest.json's key names
    # (gameVersion / modCount / defCounts, as written by
    # observed/.../dumps/capture_manifest.py) and adds the one thing manifest
    # withholds - the names themselves, under defNames, keyed by def type so
    # by_type survives the round trip. A plain text file of one defName per
    # line is also accepted, because that is what a human writes by hand.

    @classmethod
    def load_names(cls, path: str) -> "LiveIndex":
        """
        Load a precomputed defName list written by --write-defnames (JSON), or
        any file of one bare defName per line.
        """
        idx = cls()
        try:
            with open(path, encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as e:
            print(f"  (--defnames: cannot read {path}: {e}; live checks skipped)")
            return idx

        if raw.lstrip().startswith("{"):
            try:
                blob = json.loads(raw)
            except ValueError as e:
                print(f"  (--defnames: {path} is not valid JSON: {e}; "
                      f"live checks skipped)")
                return idx
            idx.game_version = str(blob.get("gameVersion", "") or "")
            try:
                idx.mod_count = int(blob.get("modCount", 0) or 0)
            except (TypeError, ValueError):
                idx.mod_count = 0
            for deftype, names in (blob.get("defNames") or {}).items():
                found = {str(n) for n in names}
                if found:
                    idx.by_type[str(deftype)] = found
                    idx.names |= found
        else:
            # One name per line. '#' starts a comment so a hand-kept list can
            # say where it came from; that provenance is the whole reason the
            # JSON form carries gameVersion.
            for line in raw.splitlines():
                line = line.split("#", 1)[0].strip()
                if line:
                    idx.names.add(line)

        idx.loaded = bool(idx.names)
        if not idx.loaded:
            print(f"  (--defnames: {path} held no defNames; live checks skipped)")
        return idx

    def write_names(self, path: str, source: str = "") -> None:
        """Persist this index in the --defnames JSON form."""
        blob = {
            "tool": "validate_patch.py --write-defnames",
            "source": source,
            "gameVersion": self.game_version,
            "modCount": self.mod_count,
            "defCounts": {t: len(n) for t, n in sorted(self.by_type.items())},
            "defNames": {t: sorted(n) for t, n in sorted(self.by_type.items())},
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(blob, fh, indent=1, sort_keys=False)
            fh.write("\n")


def xpath_identity(xp: str) -> str | None:
    """
    The concrete defName an xpath aims at, if it names one.

    Deliberately returns None for [@Name="X"]. A Name is an ABSTRACT def: an
    inheritance template that is never registered in the DefDatabase, so a live
    dump contains none of them by construction. Checking abstracts against a
    live index reports every correct patch-the-parent operation as a missing
    def -- which is exactly what this check did on its first run, flagging all
    three Force_LightsaberBase operations as errors when they were right.
    """
    m = _XPATH_IDENT_RE.search(xp)
    if not m or m.group(1) != "defName":
        return None
    return m.group(2)


def check_live(to_evaluate, docs, f: Findings,
               scanner: PatchScanner | None = None,
               own_basename: str = "",
               live: "LiveIndex | None" = None) -> None:
    for op, path, xp, guarded in to_evaluate:
        cls = short(op.get("Class", ""))
        n, where, elems, n_mods, unsupported = count_matches(xp, docs)
        if unsupported:
            f.info(f"{path} ({cls}): xpath uses an XPath feature this checker "
                   f"cannot evaluate - live hit count skipped. Verify by hand: {xp}")
            continue

        loc = ("  in " + ", ".join(where[:4]) + (" ..." if len(where) > 4 else "")) if where else ""

        if cls in ("PatchOperationAdd", "PatchOperationInsert"):
            check_value_shape(op, cls, path, elems, f)

        # A def named in the xpath that does not exist at runtime is broken no
        # matter how many on-disk nodes matched -- it may have been overridden
        # away, renamed, or simply mistyped.
        ident = xpath_identity(xp)
        if live is not None and live.loaded and ident and not live.has(ident):
            f.error(f"{path} ({cls}): '{ident}' does not exist in the LIVE game "
                    f"(checked against a def dump of {live.mod_count} mods). "
                    f"Typo, renamed def, or lost to an override.\n"
                    f"              {xp}")

        if n == 0:
            if cls in MODIFYING_OPS:
                leaf = leaf_name(xp)
                creators = scanner.mods_mentioning(leaf, own_basename) if scanner else []
                # With a live dump the old ambiguity is decidable: either the
                # target really is there at runtime (patch-created, fine) or it
                # is not (genuinely broken). Without one, fall back to guessing
                # from other mods' patch files.
                if guarded:
                    # Unreachable branch, not a no-op. See
                    # _guarded_by_identical_test() for why this is the ONE shape
                    # where 0 matches proves nothing.
                    f.info(f"{path} ({cls}): 0 nodes on disk, but this operation "
                           f"is in the <match> branch of a conditional testing "
                           f"the SAME xpath, so it cannot silently no-op - with "
                           f"0 matches the branch never runs at all and <nomatch> "
                           f"fires instead. Check the <nomatch> branch is right.")
                elif live is not None and live.loaded and ident:
                    if live.has(ident):
                        f.info(f"{path} ({cls}): 0 nodes on disk, but '{ident}' "
                               f"EXISTS in the live game - created or completed by "
                               f"another mod's patch. Load after it.")
                    else:
                        f.error(f"{path} ({cls}): 0 nodes on disk AND '{ident}' is "
                                f"absent from the live game. This operation does "
                                f"nothing.\n              {xp}")
                elif creators:
                    named = ", ".join(f"'{c}'" for c in creators[:3])
                    more = f" (+{len(creators) - 3} more)" if len(creators) > 3 else ""
                    f.warn(f"{path} ({cls}): 0 nodes in the on-disk Defs, but "
                           f"'{leaf}' appears in a PatchOperation in {named}{more}. "
                           f"This node is probably CREATED by that mod's patch at "
                           f"runtime, which this validator cannot see. Make sure "
                           f"your mod loads AFTER it."
                           f"{'' if live is None else ' Pass --live to decide this.'}"
                           f"\n              {xp}")
                else:
                    f.error(f"{path} ({cls}): xpath matches 0 nodes in the loaded "
                            f"Defs. This operation would silently do nothing.\n"
                            f"              {xp}")
            else:
                f.info(f"{path} ({cls}): test xpath matches 0 nodes - the guard "
                       f"will be a no-op with these mods active. Expected if the "
                       f"target mod is not installed.")
        elif n > 1 and cls in DESTRUCTIVE_OPS and n_mods == 1:
            f.warn(f"{path} ({cls}): xpath matches {n} nodes in ONE mod folder and "
                   f"this operation applies to ALL of them{loc}. If you meant one, "
                   f"add a positional predicate such as [1] or [2] - and put the "
                   f"same predicate in the conditional test.\n              {xp}")
        elif n > 1 and cls in DESTRUCTIVE_OPS:
            f.info(f"{path} ({cls}): {n} match(es) across {n_mods} mod folders{loc}. "
                   f"Several mods define this def; RimWorld merges them into one "
                   f"document and this operation patches every matching node. "
                   f"Usually correct - do NOT add a positional predicate to "
                   f"'fix' it.")
        else:
            f.info(f"{path} ({cls}): {n} match(es){loc}")


# --------------------------------------------------------------------------
# Defs/ checks
# --------------------------------------------------------------------------
# A SHORTLIST, on purpose. These are the def failures that are mechanically
# decidable from files on disk and that cost a ~25-minute game load to find any
# other way. Everything else - field names, types, value ranges, C# members - is
# NOT checked and the banner says so, because a validator that implies more
# coverage than it has is worse than one that has none.
#
#   1. the file parses as XML at all                (shared with the patch path)
#   2. no '--' inside a comment body                (shared with the patch path)
#   3. every concrete def has a <defName>
#   4. no (defType, defName) pair defined twice inside the mod
#   5. ParentName resolves to a def carrying that Name=   (needs --defs)
#   6. every Class="..." is one some shipping def already uses  (needs --defs)
#   7. every texPath / uiIconPath resolves to a file on disk
#
# KNOWN LIMITATIONS, stated rather than assumed:
#   * If the mod under validation is ALSO deployed and active, its deployed copy
#     is inside the load set, so checks 5 and 6 can confirm themselves against
#     it. They still catch a typo, which is what they are for.
#   * A mod that ships Assemblies/ may legitimately name its own C# classes, so
#     check 6 drops to an info line for those mods instead of a warning.
#   * texPath resolution is by directory listing, not by RimWorld's own loader.
#     A path that resolves here can still fail in game if it is shadowed.

_TEX_EXT = (".png", ".jpg", ".jpeg")
_TEX_DIRECTIONS = ("_north", "_south", "_east", "_west")
_ICON_TAGS = {"uiiconpath", "iconpath", "menuiconpath", "leaflessgraphicpath"}


def _is_texture_tag(tag: str) -> bool:
    """<texPath>, <graphicData><texPath>, <uiIconPath> and friends."""
    if not isinstance(tag, str):
        return False
    t = tag.lower()
    return t.endswith("texpath") or t in _ICON_TAGS


def find_mod_root(path: str) -> str | None:
    """The nearest ancestor directory holding About/About.xml, or None."""
    d = os.path.dirname(os.path.abspath(path))
    prev = ""
    while d and d != prev:
        if os.path.isfile(os.path.join(d, "About", "About.xml")):
            return d
        prev, d = d, os.path.dirname(d)
    return None


class TextureIndex:
    """
    'Does this texPath exist?' answered by cached directory listings.

    Listings rather than an os.walk: the Workshop tree holds ~1,200 mods and
    walking every Textures/ folder would take longer than the game load this
    check exists to save. A texPath names exactly one directory, so one
    os.listdir per (root, directory) pair answers every query in it.

    Matching is case-INSENSITIVE with an exact-case flag returned alongside.
    NTFS does not care and Linux does, so a case slip is invisible on the
    machine that wrote it and fatal on the one that ships it.
    """

    def __init__(self, roots: list[str], own_top: set[str] | None = None,
                 vanilla_loose: bool = False) -> None:
        self.roots = roots
        # Top-level folder names inside THIS mod's own Textures/. A texPath
        # whose first segment is one of these is the mod's own art, so a miss is
        # its own bug. A path under any other namespace may belong to vanilla or
        # to another mod - see `vanilla_loose`.
        self.own_top = own_top or set()
        # 🔴 Is the GAME's own art on disk as loose PNGs? On a Steam install it
        # is NOT: Data/Core, Data/Biotech and the rest ship About/, Defs/ and
        # Languages/ only, with every texture inside a Unity asset bundle.
        # Measured 2026-08-13. So a def pointing at a perfectly correct vanilla
        # path such as UI/Icons/Xenotypes/Pigskin resolves to nothing here, and
        # calling that an ERROR is a false alarm - which on the first full-stack
        # run it duly was, twice, on Jawa_Patches.
        self.vanilla_loose = vanilla_loose
        self._listing: dict[str, dict[str, str]] = {}

    def _names(self, d: str) -> dict[str, str]:
        key = os.path.normcase(d)
        got = self._listing.get(key)
        if got is None:
            try:
                got = {n.lower(): n for n in os.listdir(d)}
            except OSError:
                got = {}
            self._listing[key] = got
        return got

    def find(self, texpath: str) -> tuple[str | None, bool]:
        """(absolute path of the first hit, exact-case) or (None, False)."""
        rel = texpath.replace("\\", "/").strip().strip("/")
        if not rel:
            return None, False
        parent_rel, _, base = rel.rpartition("/")
        for root in self.roots:
            d = os.path.join(root, *parent_rel.split("/")) if parent_rel else root
            names = self._names(d)
            if not names:
                continue
            # Graphic_Single: <path>.png
            for ext in _TEX_EXT:
                hit = names.get((base + ext).lower())
                if hit:
                    return os.path.join(d, hit), hit == base + ext
            # Graphic_Multi: <path>_north.png ...
            for direction in _TEX_DIRECTIONS:
                for ext in _TEX_EXT:
                    hit = names.get((base + direction + ext).lower())
                    if hit:
                        return os.path.join(d, hit), hit[:len(base)] == base
            # A folder of variants (Graphic_Random, pawn bodies)
            hit = names.get(base.lower())
            if hit and os.path.isdir(os.path.join(d, hit)):
                return os.path.join(d, hit), hit == base
        return None, False


class LoadSetIndex:
    """
    Abstract def Names and Class attribute values present in the load set.

    Both are LAZY. Collecting Class values walks every element of every def file
    in the load set, which is only worth doing if a def under validation
    actually carries a Class attribute - and abstract Names are only needed if
    one carries a ParentName.
    """

    def __init__(self, docs) -> None:
        self._docs = docs
        self._names: set[str] | None = None
        self._classes: set[str] | None = None

    def abstract_names(self) -> set[str]:
        if self._names is None:
            s: set[str] = set()
            for _p, root, _m in self._docs:
                for child in root:                 # Name= is top level only
                    n = child.get("Name") if hasattr(child, "get") else None
                    if n:
                        s.add(n)
            self._names = s
        return self._names

    def classes(self) -> set[str]:
        if self._classes is None:
            s: set[str] = set()
            for _p, root, _m in self._docs:
                for el in root.iter():
                    try:
                        c = el.get("Class")
                    except AttributeError:         # a comment/PI node
                        continue
                    if c:
                        s.add(c)
                        s.add(short(c))
            self._classes = s
        return self._classes


class DefContext:
    """
    A pre-pass over the files under validation.

    Two of the def checks are cross-file and cannot be answered one file at a
    time: a duplicate defName is only visible once every file has been read, and
    a ParentName may point at an abstract declared in a sibling file of a mod
    that is not deployed yet (so the load set has never heard of it).
    """

    def __init__(self, files: list[str]) -> None:
        self.def_files: list[str] = []
        self.patch_files: list[str] = []
        self.other_files: list[str] = []
        self.meta_files: list[str] = []
        self.lang_files: list[str] = []
        self.local_names: set[str] = set()
        self.defname_locs: dict[tuple[str, str], list[str]] = {}

        for p in files:
            try:
                root = ET.parse(p).getroot()
            except Exception:
                self.other_files.append(p)         # the per-file pass reports it
                continue
            if root.tag == "Patch":
                self.patch_files.append(p)
                continue
            if root.tag in ("ModMetaData", "loadFolders"):
                self.meta_files.append(p)
                continue
            # Counted apart from `other_files` so the banner does not advertise
            # translations as files it could not classify.
            if root.tag == "LanguageData":
                self.lang_files.append(p)
                continue
            if root.tag != "Defs":
                self.other_files.append(p)
                continue
            self.def_files.append(p)
            for child in root:
                if not isinstance(child.tag, str):
                    continue
                nm = child.get("Name")
                if nm:
                    self.local_names.add(nm)
                if (child.get("Abstract") or "").lower() == "true":
                    continue
                dn = child.find("defName")
                if dn is not None and (dn.text or "").strip():
                    self.defname_locs.setdefault(
                        (child.tag, dn.text.strip()), []).append(p)


def check_def_structure(root: ET.Element, path: str, f: Findings,
                        ctx: DefContext | None,
                        tex: TextureIndex | None,
                        index: LoadSetIndex | None,
                        mod_ships_dll: bool) -> None:
    """Run the def shortlist over one <Defs> document."""
    kids = [c for c in root if isinstance(c.tag, str)]
    if not kids:
        f.warn("<Defs> contains no def elements - this file does nothing")
    dup_reported: set[tuple[str, str]] = set()   # one line per clash, not per copy

    for n, child in enumerate(kids, 1):
        tag = child.tag
        abstract = (child.get("Abstract") or "").lower() == "true"
        name_attr = child.get("Name") or ""
        dn = child.find("defName")
        defname = (dn.text or "").strip() if dn is not None and dn.text else ""
        who = defname or (f"Name={name_attr}" if name_attr else f"<{tag}> #{n}")

        # 3. a concrete def with no defName never enters the DefDatabase.
        if not defname and not abstract and not name_attr:
            f.error(f"<{tag}> #{n}: no <defName> and no Name= attribute. A def "
                    f"with neither is never registered and never inherited "
                    f"from - it is dead weight the game loads and discards.")
        if abstract and not name_attr:
            f.warn(f"<{tag}> #{n}: Abstract=\"True\" with no Name= attribute. "
                   f"Nothing can ever inherit from it.")

        # 4. duplicate (defType, defName) inside the mod.
        if defname and not abstract and ctx is not None:
            locs = ctx.defname_locs.get((tag, defname), [])
            if len(locs) > 1 and (tag, defname) not in dup_reported:
                dup_reported.add((tag, defname))
                here = sum(1 for x in locs if x == path)
                others = sorted({x for x in locs if x != path})
                where = (f"{here} times in this file" if here > 1 else "")
                if others:
                    where = (where + "; also in " if where else "also in ") + \
                            ", ".join(others[:3])
                f.error(f"{tag} '{defname}': defined more than once inside this "
                        f"mod ({where}). RimWorld keeps the LAST one loaded and "
                        f"the earlier definitions vanish silently.")

        # 5. ParentName must name an abstract that actually exists.
        parent = child.get("ParentName")
        if parent:
            known_local = ctx is not None and parent in ctx.local_names
            if not known_local and index is not None:
                if parent not in index.abstract_names():
                    f.error(f"{tag} '{who}': ParentName=\"{parent}\" resolves to "
                            f"no def carrying Name=\"{parent}\", in this mod or "
                            f"anywhere in the load set. The def fails to "
                            f"resolve and is DISCARDED - it will not exist in "
                            f"game.")
            elif not known_local and index is None:
                f.info(f"{tag} '{who}': ParentName=\"{parent}\" is not declared "
                       f"in the files scanned. Pass --defs to check it against "
                       f"the real load set.")

        # 6/7. class attributes and texture paths, anywhere in the subtree.
        for el in child.iter():
            if not isinstance(el.tag, str):
                continue

            cls_attr = el.get("Class")
            if cls_attr and index is not None:
                if cls_attr not in index.classes():
                    msg = (f"{tag} '{who}': <{el.tag} Class=\"{cls_attr}\"> - no "
                           f"def in the load set uses that class. A Class the "
                           f"game cannot resolve throws away the whole parent "
                           f"def.")
                    if mod_ships_dll:
                        f.info(msg + " This mod ships Assemblies/, so it may be "
                                     "its own class - confirm it is public and "
                                     "the namespace matches.")
                    else:
                        f.warn(msg + " This mod ships no Assemblies/, so there "
                                     "is nothing here to define it.")

            if _is_texture_tag(el.tag) and (el.text or "").strip():
                tp = el.text.strip()
                if tex is None:
                    continue
                hit, exact = tex.find(tp)
                if hit is None:
                    top = tp.replace("\\", "/").strip("/").split("/")[0].lower()
                    mine = top in tex.own_top
                    where = (f"<{el.tag}>{tp}</{el.tag}> - no file, folder or "
                             f"_north/_south/_east/_west variant of that path "
                             f"exists under any Textures/ root scanned.")
                    if mine or tex.vanilla_loose:
                        f.error(f"{tag} '{who}': {where} '{top}/' IS this mod's "
                                f"own texture namespace, so nothing else can "
                                f"supply it. The thing renders as a pink "
                                f"placeholder."
                                if mine else
                                f"{tag} '{who}': {where} The thing renders as a "
                                f"pink placeholder.")
                    else:
                        f.warn(f"{tag} '{who}': {where} Cannot be called a typo: "
                               f"the GAME's own textures are inside Unity asset "
                               f"bundles, not loose files, so a correct vanilla "
                               f"path looks identical to a wrong one from here. "
                               f"'{top}/' is not this mod's namespace either. "
                               f"Check it against a def that already works.")
                elif not exact:
                    f.warn(f"{tag} '{who}': <{el.tag}>{tp}</{el.tag}> only "
                           f"matches with different CASE ({os.path.basename(hit)}). "
                           f"Windows does not care; a case-sensitive filesystem "
                           f"does, and so does the Workshop upload.")


def _textures_for(path: str, mods: list[ModInfo] | None,
                  cache: dict | None) -> tuple[TextureIndex | None, bool]:
    """
    (TextureIndex for the mod this def file belongs to, does it ship a DLL).

    Root ORDER is the whole point: the mod's own Textures/ first, then every
    active mod in load order. Own-first means the common case - a def naming art
    the same mod ships - is answered by one listdir, and the wide search only
    runs for paths that miss, which are the ones about to be an error anyway.
    """
    mod_root = find_mod_root(path)
    if mod_root is None:
        # Not laid out as a mod (a loose Defs folder, a scratch file). Fall back
        # to the nearest ancestor that has a Textures/ sibling.
        d = os.path.dirname(os.path.abspath(path))
        prev = ""
        while d and d != prev:
            if os.path.isdir(os.path.join(d, "Textures")):
                mod_root = d
                break
            prev, d = d, os.path.dirname(d)
    if mod_root is None:
        return None, False

    if cache is not None and mod_root in cache:
        return cache[mod_root]

    roots: list[str] = []
    own: list[str] = []

    def add(p: str, is_own: bool = False) -> None:
        if os.path.isdir(p) and p not in roots:
            roots.append(p)
            if is_own:
                own.append(p)

    add(os.path.join(mod_root, "Textures"), True)
    try:                                    # versioned folders: 1.6/Textures
        for e in sorted(os.listdir(mod_root)):
            add(os.path.join(mod_root, e, "Textures"), True)
    except OSError:
        pass
    for m in (mods or ()):
        for folder in m.folders or [m.folder]:
            add(os.path.join(folder, "Textures"))

    own_top: set[str] = set()
    for p in own:
        try:
            own_top |= {n.lower() for n in os.listdir(p)}
        except OSError:
            pass

    # Vanilla art is loose only on an unusual install. Detected rather than
    # assumed: Core is the mod every load set contains.
    vanilla_loose = False
    for m in (mods or ()):
        if m.package_id == "ludeon.rimworld":
            vanilla_loose = any(os.path.isdir(os.path.join(fo, "Textures"))
                                for fo in (m.folders or [m.folder]))
            break

    ships_dll = False
    for base in (mod_root,) + tuple(
            os.path.join(mod_root, e) for e in (os.listdir(mod_root)
                                                if os.path.isdir(mod_root) else ())):
        adir = os.path.join(base, "Assemblies")
        if os.path.isdir(adir):
            try:
                if any(n.lower().endswith(".dll") for n in os.listdir(adir)):
                    ships_dll = True
                    break
            except OSError:
                pass

    got = (TextureIndex(roots, own_top, vanilla_loose), ships_dll)
    if cache is not None:
        cache[mod_root] = got
    return got


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def collect_patch_files(targets: list[str]) -> tuple[list[str], list[str]]:
    """Expand FILE / DIRECTORY arguments into a sorted list of *.xml files."""
    files: list[str] = []
    bad: list[str] = []
    seen: set[str] = set()

    def add(p: str) -> None:
        key = os.path.normcase(os.path.abspath(p))
        if key not in seen:
            seen.add(key)
            files.append(p)

    for t in targets:
        if os.path.isfile(t):
            add(t)
        elif os.path.isdir(t):
            found = sorted(_iter_def_xml(t))
            if not found:
                bad.append(f"{t} (directory contains no .xml)")
            for p in found:
                add(p)
        else:
            bad.append(t)
    return files, bad


def validate_file(path: str, docs, scanner: PatchScanner | None,
                  have_defs: bool, quiet: bool,
                  live: "LiveIndex | None" = None,
                  ctx: DefContext | None = None,
                  index: LoadSetIndex | None = None,
                  tex_cache: dict | None = None,
                  mods: list[ModInfo] | None = None) -> tuple[int, int, int]:
    """Returns (exit_code, n_errors, n_warnings) for one XML file.

    Dispatches on the ROOT ELEMENT: <Patch> takes the PatchOperation path
    unchanged, <Defs> takes the def shortlist, anything else is still an error.
    """
    f = Findings()
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as e:
        print(f"  ERROR   cannot read {path}: {e}\n")
        print("FAIL - 1 error(s), 0 warning(s)")
        return 1, 1, 0

    check_comments(raw, f)

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        f.error(f"XML does not parse: {e}")
        return f.report(quiet), len(f.errors), len(f.warnings)

    # About.xml and LoadFolders.xml are swept up by any directory argument and
    # are not patches. Reporting them as "expected <Patch>" was a false error
    # that punished exactly the habit the deploy skill asks for - validate the
    # WHOLE mod folder, About.xml included, because the blast radius is the mod.
    if root.tag == "ModMetaData":
        pid = root.find("packageId")
        if pid is None or not (pid.text or "").strip():
            f.error("About.xml has no <packageId> as a direct child of "
                    "<ModMetaData>. The mod is not loadable and not deployable.")
        if root.find("name") is None:
            f.warn("About.xml has no <name>; the mod list will show the folder "
                   "name instead.")
        f.info("About.xml: parsed, packageId and name checked. Nothing else "
               "here is validated.")
        return f.report(quiet), len(f.errors), len(f.warnings)

    if root.tag == "loadFolders":
        f.info("LoadFolders.xml: parsed. Folder resolution is exercised by the "
               "--defs load set, not checked here.")
        return f.report(quiet), len(f.errors), len(f.warnings)

    # 🔴 Languages/ is NOT a patch folder, and reading it as one made this gate
    # cry wolf. `<LanguageData>` is exactly what a keyed translation or a
    # DefInjected override must have; reporting it as "expected <Patch>" put a
    # fake ERROR — and therefore `FAIL TOTAL` — on a mod with zero real defects.
    # ⚠️ A gate that fails a clean mod gets ignored, which costs more than the
    # gate ever saved: Jawa_Patches read FAIL on 1 fake error while 11 real ones
    # had just been cleared.
    # ⛔ Do not "fix" this by skipping the Languages/ DIRECTORY. Dispatching on
    # the root element is right for the same reason it was right for About.xml:
    # the deploy skill asks a seat to validate the WHOLE mod folder, because the
    # blast radius is the mod.
    if root.tag == "LanguageData":
        n = len([c for c in root if isinstance(c.tag, str)])
        f.info(f"translation file: parsed, {n} key(s). Translations are not this "
               "tool's business — no patch or def check applies to them.")
        return f.report(quiet), len(f.errors), len(f.warnings)

    if root.tag == "Defs":
        tex, ships_dll = _textures_for(path, mods, tex_cache)
        check_def_structure(root, path, f, ctx, tex, index, ships_dll)
        if index is None:
            f.info("no --defs given; ParentName resolution and Class-attribute "
                   "checks were SKIPPED. texPath checks used this mod's own "
                   "Textures/ only, so a path served by another mod cannot be "
                   "told apart from a typo.")
        return f.report(quiet), len(f.errors), len(f.warnings)

    check_dict_keyed_fields(root, f)
    to_evaluate = check_structure(root, f)

    if have_defs:
        if docs:
            check_live(to_evaluate, docs, f, scanner, os.path.basename(path), live)
        else:
            f.warn("no def files found under the given --defs paths; "
                   "live xpath checks skipped")
    elif live:
        # --defnames without --defs. These are NOT the same check and saying
        # "static checks only" here invited exactly the wrong conclusion: that
        # a clean run had validated the xpaths. It had not. The index proves a
        # defNAME exists; only --defs can prove an XPATH matches anything.
        f.info("--defnames index in use: defName existence IS checked, but "
               "xpath matching is NOT. An xpath that matches nothing still "
               "passes here - that is the most common silent failure, and "
               "only --defs catches it.")
    else:
        f.info("no --defs given; static checks only. Pass --defs to catch "
               "xpaths that match nothing (the most common silent failure).")

    return f.report(quiet), len(f.errors), len(f.warnings)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate RimWorld XML PatchOperation files against the "
                    "mod load set the game will actually build.")
    ap.add_argument("patch", nargs="+",
                    help="patch XML file(s) and/or directories to search "
                         "recursively for *.xml")
    ap.add_argument("--defs", action="append", default=[],
                    help="root directory to search for installed mods "
                         "(repeatable). e.g. the RimWorld Data folder, the "
                         "Workshop content folder and RimWorld/Mods. Without "
                         "this, only static checks run.")
    ap.add_argument("--mods-config", default=None,
                    help="path to ModsConfig.xml. Defaults to the standard "
                         "LocalLow location when it exists. Defines which mods "
                         "are active and which game version to resolve.")
    ap.add_argument("--all-versions", action="store_true",
                    help="scan every version folder of every installed mod, "
                         "active or not (the old unscoped behaviour). Inflates "
                         "match counts; use only for deliberate audits.")
    ap.add_argument("--live", default=None, metavar="DUMPDIR",
                    help="a live def dump (the DefDump folder written by "
                         "RimDefDump, containing defs/ and manifest.json). "
                         "Turns 'does this def exist in the running game' from "
                         "a guess into a lookup: catches typos, renamed defs "
                         "and defs lost to an override, and decides whether a "
                         "0-match xpath is patch-created or simply broken. "
                         "Optional - everything works without it.")
    ap.add_argument("--defnames", default=None, metavar="FILE",
                    help="a precomputed defName list (written by "
                         "--write-defnames, or one bare defName per line). "
                         "Exactly the same checks as --live, without "
                         "re-streaming the whole multi-gigabyte dump on every "
                         "run. Wins over --live if both are given.")
    ap.add_argument("--write-defnames", default=None, metavar="FILE",
                    help="extract the defNames from the --live dump into FILE "
                         "and exit. Run once per dump; use --defnames FILE "
                         "thereafter.")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress info lines")
    args = ap.parse_args()

    # Extraction is a mode, not a side effect of a validation run: it needs a
    # dump and produces a file, and doing it silently inside a normal run would
    # make one invocation mean two different things.
    if args.write_defnames:
        if not args.live:
            print("--write-defnames needs --live DUMPDIR to extract from")
            return 2
        src = LiveIndex.load(args.live)
        if not src.loaded:
            print(f"--write-defnames: no defNames found under {args.live}")
            return 2
        src.write_names(args.write_defnames, args.live)
        print(f"wrote {len(src.names):,} defNames across {len(src.by_type)} "
              f"def types to {args.write_defnames}")
        return 0

    files, bad = collect_patch_files(args.patch)
    for b in bad:
        print(f"cannot read {b}")
    if not files:
        return 2

    mods_config = args.mods_config
    if mods_config is None:
        mods_config, tried = find_mods_config()
        if mods_config is None and args.defs and not args.all_versions:
            print("  WARN    no ModsConfig.xml found, so --defs cannot be scoped "
                  "to the ACTIVE mods. Every match count below is an UNSCOPED "
                  "count over every installed mod and every version folder, and "
                  "does not describe the running game.")
            print(f"  WARN    looked in {len(tried)} location(s); pass "
                  f"--mods-config explicitly to fix this.")
    if mods_config and not os.path.isfile(mods_config):
        print(f"cannot read --mods-config {mods_config}")
        return 2

    # THE BANNER MUST SAY WHAT WAS NOT SCANNED.
    # This tool spent months checking Patches/ only while reporting "OK", which
    # reads as "this mod is fine" and never was. A verdict is only as honest as
    # its stated scope, so the scope is printed on every run, before any finding.
    ctx = DefContext(files)
    print(f"\nvalidate_patch.py - {len(files)} XML file(s): "
          f"{len(ctx.patch_files)} <Patch>, {len(ctx.def_files)} <Defs>"
          + (f", {len(ctx.meta_files)} About/LoadFolders" if ctx.meta_files else "")
          + (f", {len(ctx.lang_files)} translation" if ctx.lang_files else "")
          + (f", {len(ctx.other_files)} neither" if ctx.other_files else ""))
    print("  SCANNED     Patches/: operation shape, guards, value shape, live "
          "xpath hit counts")
    print("              Defs/:    XML parse, comment bodies, missing/duplicate "
          "defName, ParentName")
    print("                        resolution, Class attributes, texPath "
          "existence and case")
    print("  NOT SCANNED field names, field types, value ranges, C# class "
          "members, and any node")
    print("              a PatchOperation creates at load time. This is not a "
          "def linter.")
    if not args.defs:
        print("  NOTE        no --defs: ParentName and Class checks are SKIPPED "
              "and no xpath is executed.")
    print()

    docs: list = []
    mods: list[ModInfo] = []
    scanner: PatchScanner | None = None
    if args.defs:
        # Only --defs evaluates xpaths, so this is the only place the engine
        # choice can change an answer - and the only place worth naming it.
        print(f"  info    {engine_banner()}")
        try:
            docs, mods = build_load_set(args.defs, mods_config, args.all_versions)
        except LoadSetUnmeasurable as e:
            print(f"  ERROR   UNMEASURABLE - {e}")
            print("  ERROR   Refusing to report a verdict. An unreadable load "
                  "set is not a passing one.")
            return 2
        scanner = PatchScanner(mods)

        # ⚠️ ASKED-FOR-AND-COULDN'T-DO IS A FAILURE, NOT A WARNING.
        #
        # Passing --defs is a request for live xpath checks, which are the only
        # thing that catches an xpath matching nothing — the most common silent
        # failure in this whole file format. If zero def files loaded, NONE of
        # that ran, and the run has no more authority than a bare static check.
        #
        # Until 2026-08-13 this warned per-file and still exited 0, so
        # `refresh.py --patches` under WSL printed
        # "validate (with --live) ok (exit 0)" and then "Everything is current"
        # while validating literally nothing. The three --defs roots it passed
        # were C:\ literals that do not exist from Linux. Found by a retired seat.
        #
        # Worse than a clean break: both interpreters "worked" and only one
        # validated. So: refuse, name every root tried, and exit non-zero.
        if not docs:
            print("\n  ERROR   --defs was given but ZERO def files loaded, so "
                  "no live xpath check ran.")
            print("          This is a FAILURE to validate, not a clean run. "
                  "Roots tried:")
            for r in args.defs:
                print("            %-5s %s"
                      % ("ok" if os.path.exists(r) else "MISSING", r))
            print("          If these are Windows paths and you are on WSL, "
                  "use the /mnt/c/... form")
            print("          (src/RimMandrake/Utils/game_paths.py resolves them per-platform).")
            print("\nFAIL - could not validate")
            return 1

    live: LiveIndex | None = None
    if args.defnames:
        # Same index, same checks, same wording downstream - only the source of
        # the names differs, so --defnames wins outright rather than merging.
        live = LiveIndex.load_names(args.defnames)
        source = f"defName list {args.defnames}"
        if live.loaded and args.live:
            print(f"  info    --defnames given; --live {args.live} not read")
    elif args.live:
        live = LiveIndex.load(args.live)
        source = "live dump"
    if live is not None:
        if live.loaded:
            # by_type is empty for a bare one-name-per-line list; saying
            # "across 1 def types" there would be an invented number.
            print(f"{source}: {len(live.names)} defNames"
                  + (f" across {len(live.by_type)} def types" if live.by_type else "")
                  + (f", RimWorld {live.game_version}" if live.game_version else "")
                  + (f", {live.mod_count} mods" if live.mod_count else ""))
        else:
            print(f"{source}: nothing usable found; live checks skipped")

    index = LoadSetIndex(docs) if (args.defs and docs) else None
    tex_cache: dict = {}

    total_err = total_warn = 0
    for p in files:
        print(f"\n=== {p} ===")
        _rc, ne, nw = validate_file(p, docs, scanner, bool(args.defs), args.quiet,
                                    live, ctx, index, tex_cache, mods)
        total_err += ne
        total_warn += nw

    if len(files) > 1:
        verdict = "FAIL" if total_err else "OK"
        print(f"{verdict} TOTAL - {len(files)} file(s), {total_err} error(s), "
              f"{total_warn} warning(s)")
        # ⭐ The verdict already keys off ERRORS only, but a bare "0 error(s),
        # 183 warning(s)" still reads as a failing mod, and most of that 183 is
        # one benign shape — `nomatch` whose inner xpath differs from the
        # conditional test, which is how add-if-missing patches are written.
        # Say so, or the next seat goes hunting through 183 lines for a defect
        # the tool already knows is intentional.
        if not total_err and total_warn:
            print(f"     ⇒ nothing here fails. {total_warn} warning(s) are "
                  "advisory; the add-if-missing `nomatch` shape is the common "
                  "one and is intentional.")

    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
