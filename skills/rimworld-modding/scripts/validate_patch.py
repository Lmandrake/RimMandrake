#!/usr/bin/env python3
"""
validate_patch.py - static + live validation for RimWorld XML PatchOperation files.

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
                     INFO for a conditional test (a legitimate no-op guard).
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
  python3 validate_patch.py custom_patches/MyMod/Patches \
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
  --quiet         suppress info lines.

NOTES ON THE XPATH ENGINE
=========================
Python's ElementTree supports a useful subset of XPath 1.0. RimWorld uses full
XPath via System.Xml. Where ElementTree cannot evaluate an expression (e.g.
starts-with(), contains(), or/and inside predicates) this script says
"UNSUPPORTED" and skips the live check rather than guessing. That is deliberate:
a wrong hit-count is worse than no hit-count. Simple defName predicates,
positional predicates and path steps - which is the large majority of real
patches - are translated and evaluated correctly.

MAINTENANCE
===========
The one thing to keep current is OPS_NEEDING_XPATH and MODIFYING_OPS below.
If Ludeon adds a PatchOperation class, add it there or this script will let an
unguarded operation through without comment.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

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


def check_structure(root: ET.Element, f: Findings) -> list[tuple[ET.Element, str, str]]:
    """
    Walk every operation, run the static checks, and return the list of
    (element, path, xpath) tuples to be evaluated live.
    """
    if root.tag != "Patch":
        f.error(f"root element is <{root.tag}>, expected <Patch>")

    to_evaluate: list[tuple[ET.Element, str, str]] = []

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

        if cls in OPS_NEEDING_XPATH:
            if xp is None:
                f.error(f"{path} ({cls}): no <xpath> child")
            elif not xp:
                f.error(f"{path} ({cls}): <xpath> is empty")
            else:
                to_evaluate.append((op, path, xp))

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
    if not s:
        return None

    # [defName="X"]  ->  [defName='X']   (ET wants the child-value form)
    s = re.sub(r'\[\s*(\w+)\s*=\s*"([^"]*)"\s*\]', r"[\1='\2']", s)
    s = re.sub(r"\[\s*@(\w+)\s*=\s*\"([^\"]*)\"\s*\]", r"[@\1='\2']", s)

    # Anything left that ET will choke on
    if re.search(r"\[[^\]]*[()][^\]]*\]", s):
        return None
    return s


# --------------------------------------------------------------------------
# Load-set resolution: ModsConfig + About.xml + LoadFolders.xml
# --------------------------------------------------------------------------

DEFAULT_MODS_CONFIG = os.path.join(
    os.path.expanduser("~"), "AppData", "LocalLow", "Ludeon Studios",
    "RimWorld by Ludeon Studios", "Config", "ModsConfig.xml")


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
    for root_dir in defs_roots:
        if not os.path.isdir(root_dir):
            print(f"  info    --defs path not found, skipping: {root_dir}")
            continue
        candidates = [root_dir]
        try:
            candidates += [os.path.join(root_dir, e) for e in sorted(os.listdir(root_dir))]
        except OSError:
            pass
        for cand in candidates:
            if not os.path.isdir(cand):
                continue
            got = read_about(cand)
            if not got:
                continue
            pid, name = got
            if pid not in index:
                index[pid] = ModInfo(pid, name, cand)
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

    versioned = os.path.join(mod_dir, version) if version else ""
    if versioned and os.path.isdir(versioned):
        folders.append(versioned)
    else:
        folders.append(mod_dir)
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
                    docs.append((p, ET.parse(p).getroot(), mod.name))
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
                    docs.append((p, ET.parse(p).getroot(), owner))
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
        print(f"  info    {len(missing)} active packageId(s) have no folder under "
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

def count_matches(et_xpath: str, docs) -> tuple[int, list[str], list[ET.Element], int]:
    """
    Evaluate the xpath over the load set.

    Returns (total hits, per-file locations labelled by MOD, matched elements,
    number of distinct mods hit). The mod label is what turns "7 matches in
    Races_Animal_Armadillo.xml" - which reads like a duplicated file - into
    either one mod (a real duplicate, worth a warning) or several mods (several
    definitions of the same def, which is normal).
    """
    total = 0
    where: list[str] = []
    elems: list[ET.Element] = []
    mods_hit: list[str] = []
    for path, root, mod_name in docs:
        try:
            hits = root.findall(et_xpath)
        except Exception:
            continue
        if hits:
            total += len(hits)
            where.append(f"{mod_name}: {os.path.basename(path)}({len(hits)})")
            elems.extend(hits)
            if mod_name not in mods_hit:
                mods_hit.append(mod_name)
    return total, where, elems, len(mods_hit)


def check_value_shape(op: ET.Element, cls: str, path: str,
                      targets: list[ET.Element], f: Findings) -> None:
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


def check_live(to_evaluate, docs, f: Findings,
               scanner: PatchScanner | None = None,
               own_basename: str = "") -> None:
    for op, path, xp in to_evaluate:
        cls = short(op.get("Class", ""))
        et_xp = to_elementtree_xpath(xp)
        if et_xp is None:
            f.info(f"{path} ({cls}): xpath uses an XPath feature this checker "
                   f"cannot evaluate - live hit count skipped. Verify by hand: {xp}")
            continue

        n, where, elems, n_mods = count_matches(et_xp, docs)
        loc = ("  in " + ", ".join(where[:4]) + (" ..." if len(where) > 4 else "")) if where else ""

        if cls in ("PatchOperationAdd", "PatchOperationInsert"):
            check_value_shape(op, cls, path, elems, f)

        if n == 0:
            if cls in MODIFYING_OPS:
                leaf = leaf_name(xp)
                creators = scanner.mods_mentioning(leaf, own_basename) if scanner else []
                if creators:
                    named = ", ".join(f"'{c}'" for c in creators[:3])
                    more = f" (+{len(creators) - 3} more)" if len(creators) > 3 else ""
                    f.warn(f"{path} ({cls}): 0 nodes in the on-disk Defs, but "
                           f"'{leaf}' appears in a PatchOperation in {named}{more}. "
                           f"This node is probably CREATED by that mod's patch at "
                           f"runtime, which this validator cannot see. Make sure "
                           f"your mod loads AFTER it.\n              {xp}")
                else:
                    f.error(f"{path} ({cls}): xpath matches 0 nodes in the loaded "
                            f"Defs. This operation would silently do nothing.\n"
                            f"              {xp}")
            else:
                f.info(f"{path} ({cls}): test xpath matches 0 nodes - the guard "
                       f"will be a no-op with these mods active. Expected if the "
                       f"target mod is not installed.")
        elif n > 1 and cls in DESTRUCTIVE_OPS and n_mods == 1:
            f.warn(f"{path} ({cls}): xpath matches {n} nodes IN ONE MOD and this "
                   f"operation applies to ALL of them{loc}. If you meant one, add "
                   f"a positional predicate such as [1] or [2] - and put the same "
                   f"predicate in the conditional test.\n              {xp}")
        elif n > 1 and cls in DESTRUCTIVE_OPS:
            f.info(f"{path} ({cls}): {n} match(es) across {n_mods} mods{loc}. "
                   f"Several mods define this def; RimWorld merges them into one "
                   f"document and this operation patches every matching node. "
                   f"Usually correct - do NOT add a positional predicate to "
                   f"'fix' it.")
        else:
            f.info(f"{path} ({cls}): {n} match(es){loc}")


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
                  have_defs: bool, quiet: bool) -> tuple[int, int, int]:
    """Returns (exit_code, n_errors, n_warnings) for one patch file."""
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

    to_evaluate = check_structure(root, f)

    if have_defs:
        if docs:
            check_live(to_evaluate, docs, f, scanner, os.path.basename(path))
        else:
            f.warn("no def files found under the given --defs paths; "
                   "live xpath checks skipped")
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
    ap.add_argument("--quiet", action="store_true",
                    help="suppress info lines")
    args = ap.parse_args()

    files, bad = collect_patch_files(args.patch)
    for b in bad:
        print(f"cannot read {b}")
    if not files:
        return 2

    mods_config = args.mods_config
    if mods_config is None and os.path.isfile(DEFAULT_MODS_CONFIG):
        mods_config = DEFAULT_MODS_CONFIG
    if mods_config and not os.path.isfile(mods_config):
        print(f"cannot read --mods-config {mods_config}")
        return 2

    print(f"\nvalidate_patch.py - {len(files)} patch file(s)\n")

    docs: list = []
    mods: list[ModInfo] = []
    scanner: PatchScanner | None = None
    if args.defs:
        docs, mods = build_load_set(args.defs, mods_config, args.all_versions)
        scanner = PatchScanner(mods)

    total_err = total_warn = 0
    for p in files:
        print(f"\n=== {p} ===")
        _rc, ne, nw = validate_file(p, docs, scanner, bool(args.defs), args.quiet)
        total_err += ne
        total_warn += nw

    if len(files) > 1:
        verdict = "FAIL" if total_err else "OK"
        print(f"{verdict} TOTAL - {len(files)} file(s), {total_err} error(s), "
              f"{total_warn} warning(s)")

    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
