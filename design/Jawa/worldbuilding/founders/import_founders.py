#!/usr/bin/env python3
"""Splice the exported founders back into a RimWorld savegame.

    python3 design/Jawa/worldbuilding/founders/import_founders.py <destination.rws>

The 8 fragments beside this file (6 founders + 2 named colony animals) are verbatim
`<li Class="Pawn">` elements lifted out of CANONICAL_ASHKARR_START_2026-09-12.rws.
They are SOUND and must never be re-exported. What they are not is portable: a save
is full of ids that mean something only inside the save that issued them, and this
script is the half that translates them.

🔴 THE DEFECT THIS SCRIPT EXISTS FOR
------------------------------------
A `loadID` collision does not error. It RESOLVES, to the wrong object.

MEASURED 2026-09-21: a splice that remapped only faction/ideo/map/position loaded
cleanly, logged nothing, and silently dropped the `Wimp` trait from 5 of the 6
founders. `Wimp` is the only trait they carry with a non-null `<sourceGene>`. The
destination had already issued gene loadIDs 0-1633, so `Gene_342/382/422/462/814`
resolved into ITS OWN unrelated genes and the trait evaporated. The sixth founder,
Sekki, kept it — `Gene_2009` sat above the destination's issued range. 6 of 6 agree,
negative case included.

⇒ Every save-local id in the fragments is reallocated here, above whatever the
destination has already issued, and every reference to it is rewritten with it.

WHAT GETS REMAPPED
------------------
  faction   `Faction_21`  -> the destination's PlayerColony faction loadID
  ideo      `Ideo_20`     -> the destination player faction's primaryIdeo
  map       `<map>0</map>`-> the destination map's uniqueID
  position  source cells  -> a row on the destination map
  genes     every `<loadID>` under genes/, and every `Gene_<n>` reference
  hediffs   every `<loadID>` under hediffSet/hediffs
  jobs      every `<loadID>` under jobs/curJob
  abilities `<Id>` under abilities/, and every `Ability_<n>` token with it
  things    ONLY if the destination has already issued one of the fragments' ids
  uniqueIDsManager  nextThingID / nextGeneID / nextHediffID / nextJobID / nextAbilityID

🔴 ALLOCATION IS NOT A FIXED OFFSET. The 2026-09-21 proving run used +1,000,000,
which worked and is still the same class of bug as the collision it fixed — it is
correct only for destinations that happen to be below it. Here every class gets its
base from `max(destination counter, highest id the destination actually issued) + 1`,
read by PARSING the destination, and ids are then handed out densely from that base.

🔴 BINARY MODE ONLY. A `.rws` is written back as bytes, never through a text-mode
handle: a text write converts LF->CRLF (or the reverse) across a 10 MB file and
corrupts it silently. The destination is read as bytes, patched as bytes, and the
size delta is checked and printed.

🔴 KEEPER SAVES ARE REFUSED BY NAME. `CANONICAL_ASHKARR_START_*` and
`ASHKARR_FALLLINE_*` are two of the three artifacts ruled to survive the world
remake. This script will not write to them under any flag.

Provenance: infrastructure/state/items/closed/FOUNDERS_IMPORTER_OWED_1.md,
Transient/founders_roundtrip_2026-09-21.md, and README.md beside this file.
Regression guard: src/RimMandrake/Utils/selftest_import_founders.py.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from xml.parsers import expat

HERE = os.path.dirname(os.path.abspath(__file__))

# Saves that must never be written to, matched on basename. These hold work that
# cannot be regenerated; a botched splice into one costs the campaign.
KEEPER_GLOBS = ("CANONICAL_ASHKARR_START_*", "ASHKARR_FALLLINE_*")

# Where an integer <loadID> sits decides WHICH counter it came out of. RimWorld
# keeps a separate counter per class, so the same integer can legitimately be both
# a gene id and a hediff id — which is exactly why a blind text substitution of
# `<loadID>977</loadID>` is wrong and this map is keyed on the element's path.
# Key: an ancestor tag. Value: the id class.
LOADID_CLASS_BY_ANCESTOR = {
    "endogenes": "gene",
    "xenogenes": "gene",
    "hediffs": "hediff",
    "curJob": "job",
    "jobs": "job",
}

# `<Id>` elements that are an ability's unique id (path li/abilities/abilities/li/Id).
ABILITY_ID_ANCESTOR = "abilities"

# uniqueIDsManager counters this script raises, and the id class each one governs.
COUNTER_FOR_CLASS = {
    "gene": "nextGeneID",
    "hediff": "nextHediffID",
    "job": "nextJobID",
    "ability": "nextAbilityID",
    "thing": "nextThingID",
}


class ImportError_(RuntimeError):
    """A refusal or an inconsistency the caller must see, not a traceback."""


# --------------------------------------------------------------------------- #
# byte-accurate element spans
# --------------------------------------------------------------------------- #

class Span:
    """One element located in the raw bytes, with its text span."""

    __slots__ = ("path", "tag", "text_start", "text_end", "elem_start", "elem_end")

    def __init__(self, path, tag, text_start, text_end, elem_start, elem_end):
        self.path = path            # tuple of ancestor tags, root first, incl. tag
        self.tag = tag
        self.text_start = text_start  # byte index just after '>' of the start tag
        self.text_end = text_end      # byte index of '<' of the end tag
        self.elem_start = elem_start  # byte index of '<' of the start tag
        self.elem_end = elem_end      # byte index just after '>' of the end tag


def scan_spans(data: bytes, want: set[str]) -> list[Span]:
    """Locate every element whose tag is in `want`, by byte offset.

    expat is used rather than ElementTree because the whole point is to patch the
    ORIGINAL bytes in place: re-serialising a parsed tree would re-indent the file,
    re-escape its text and rewrite its attribute quoting. For a savegame that is a
    gratuitous rewrite of 10 MB we have no need to touch.
    """
    spans: list[Span] = []
    stack: list[str] = []
    # start-tag byte index per depth, pushed on StartElement
    starts: list[int] = []
    p = expat.ParserCreate()

    def start(name, _attrs):
        stack.append(name)
        starts.append(p.CurrentByteIndex)

    def end(name):
        elem_start = starts.pop()
        elem_end_tag = p.CurrentByteIndex          # '<' of '</name>'
        path = tuple(stack)
        stack.pop()
        if name not in want:
            return
        gt = data.index(b">", elem_start)
        if data[gt - 1:gt] == b"/":                # self-closing: no text
            text_start = text_end = gt
            elem_end = gt + 1
        else:
            text_start = gt + 1
            text_end = elem_end_tag
            elem_end = data.index(b">", elem_end_tag) + 1
        spans.append(Span(path, name, text_start, text_end, elem_start, elem_end))

    p.StartElementHandler = start
    p.EndElementHandler = end
    p.Parse(data, True)
    return spans


def apply_patches(data: bytes, patches: list[tuple[int, int, bytes]]) -> bytes:
    """Replace byte ranges. Applied right-to-left so earlier offsets stay valid."""
    out = data
    for start, end, repl in sorted(patches, key=lambda t: -t[0]):
        out = out[:start] + repl + out[end:]
    return out


# --------------------------------------------------------------------------- #
# the destination
# --------------------------------------------------------------------------- #

class Destination:
    """Everything the splice needs to know about the save it is writing into.

    Every field here is PARSED out of the destination. Nothing is assumed, and in
    particular no id range is assumed — see `issued_max`.
    """

    def __init__(self, path: str, data: bytes | None = None):
        self.path = path
        self.data = data if data is not None else read_binary(path)
        text = self.data.decode("utf-8-sig")
        root = ET.fromstring(text)
        game = root.find("game")
        if game is None:
            raise ImportError_("%s has no <game> element — not a savegame" % path)

        # --- uniqueIDsManager ------------------------------------------------
        uid = game.find("uniqueIDsManager")
        if uid is None:
            raise ImportError_("%s has no <uniqueIDsManager>" % path)
        self.counters = {c.tag: int((c.text or "0").strip()) for c in uid
                         if (c.text or "").strip().lstrip("-").isdigit()}

        # --- player faction and its ideo -------------------------------------
        self.player_faction = None
        self.primary_ideo = None
        fm = game.find("world/factionManager/allFactions")
        for f in (fm if fm is not None else []):
            if (f.findtext("def") or "").strip() == "PlayerColony":
                self.player_faction = (f.findtext("loadID") or "").strip()
                self.primary_ideo = (f.findtext("ideos/primaryIdeo") or "").strip()
                break
        if not self.player_faction:
            raise ImportError_(
                "%s has no PlayerColony faction — there is nobody for the founders "
                "to belong to. (There is no <isPlayer> field in this schema; the "
                "PlayerColony def is the tell.)" % path)

        # --- the map ----------------------------------------------------------
        maps = game.find("maps")
        if maps is None or len(maps) == 0:
            raise ImportError_("%s has no maps — nowhere to put the founders" % path)
        idx = int((game.findtext("currentMapIndex") or "0").strip())
        idx = idx if 0 <= idx < len(maps) else 0
        self.map_index = idx
        m = maps[idx]
        self.map_unique_id = (m.findtext("uniqueID") or "0").strip()
        self.map_size = parse_vec(m.findtext("mapInfo/size") or "(250, 1, 250)")

        # --- issued id ranges, and the things already present ------------------
        self.thing_ids = set()
        self.issued_max = {k: -1 for k in COUNTER_FOR_CLASS}
        self._scan_issued(root)

        # --- where the founders go, in bytes -----------------------------------
        self.things_insert_at = self._find_things_end()

        # --- a sensible landing spot -------------------------------------------
        self.anchor = self._colonist_anchor(m)

    # ---- helpers ----------------------------------------------------------- #

    def _scan_issued(self, root: ET.Element) -> None:
        """Read the HIGHEST id the destination has actually handed out, per class.

        The counter alone is not enough: a counter can be lower than an id already
        present in the file (hand-edited saves, merged worlds, mod-spawned objects),
        and allocating from the counter alone would then collide with a live object.
        Both are consulted and the larger wins.
        """
        parents = {ch: p for p in root.iter() for ch in p}

        def ancestors(e):
            out = []
            cur = parents.get(e)
            while cur is not None:
                out.append(cur.tag)
                cur = parents.get(cur)
            return out

        for e in root.iter("loadID"):
            txt = (e.text or "").strip()
            if not txt.lstrip("-").isdigit():
                continue                      # verb loadIDs are strings, not ints
            cls = None
            for anc in ancestors(e):
                if anc in LOADID_CLASS_BY_ANCESTOR:
                    cls = LOADID_CLASS_BY_ANCESTOR[anc]
                    break
            if cls:
                self.issued_max[cls] = max(self.issued_max[cls], int(txt))

        for e in root.iter("Id"):
            txt = (e.text or "").strip()
            if txt.isdigit() and ABILITY_ID_ANCESTOR in ancestors(e):
                self.issued_max["ability"] = max(self.issued_max["ability"], int(txt))

        for e in root.iter("id"):
            txt = (e.text or "").strip()
            if not txt:
                continue
            self.thing_ids.add(txt)
            m = re.search(r"(\d+)$", txt)
            if m:
                self.issued_max["thing"] = max(self.issued_max["thing"], int(m.group(1)))

    def _find_things_end(self) -> int:
        """Byte offset of `</things>` for the chosen map.

        `<things>` is not unique in a save, so the element is picked by its full
        path and by which map it belongs to, never by "the first one".
        """
        seen = -1
        for sp in scan_spans(self.data, {"things"}):
            if sp.path[:3] != ("savegame", "game", "maps"):
                continue
            if len(sp.path) != 5 or sp.path[3] != "li":
                continue
            seen += 1
            if seen == self.map_index:
                return sp.text_end
        raise ImportError_("could not locate <things> for map %d in %s"
                           % (self.map_index, self.path))

    def _colonist_anchor(self, m: ET.Element) -> tuple[int, int]:
        """Middle of the destination's own player pawns, else the map centre.

        Dropping the founders next to the colony they are joining beats the map
        origin: it is far more likely to be walkable, indoors-adjacent and visible.
        """
        fref = "Faction_%s" % self.player_faction
        xs, zs = [], []
        things = m.find("things")
        for t in (things if things is not None else []):
            if (t.findtext("faction") or "").strip() != fref:
                continue
            pos = t.findtext("pos")
            if not pos:
                continue
            v = parse_vec(pos)
            xs.append(v[0])
            zs.append(v[2])
        if xs:
            return (sorted(xs)[len(xs) // 2], sorted(zs)[len(zs) // 2])
        return (self.map_size[0] // 2, self.map_size[2] // 2)


def parse_vec(s: str) -> tuple[int, int, int]:
    nums = re.findall(r"-?\d+", s)
    if len(nums) < 3:
        raise ImportError_("cannot parse vector %r" % s)
    return tuple(int(n) for n in nums[:3])


def read_binary(path: str) -> bytes:
    with open(path, "rb") as fh:                  # binary: see module docstring
        return fh.read()


# --------------------------------------------------------------------------- #
# the fragments
# --------------------------------------------------------------------------- #

def fragment_files(folder: str = HERE) -> list[str]:
    """The 8 fragments, in manifest order, so the placement row is deterministic."""
    manifest = os.path.join(folder, "_manifest.json")
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as fh:
            return [os.path.join(folder, e["file"]) for e in json.load(fh)]
    return sorted(os.path.join(folder, f) for f in os.listdir(folder)
                  if f.endswith(".xml") and not f.startswith("_"))


class Fragment:
    """One exported pawn, its raw bytes, and every save-local id it carries."""

    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.data = read_binary(path)
        # A fragment is a bare <li> preceded by a provenance comment; expat wants
        # one root, so the element is parsed alone. ⚠️ The comment itself contains
        # the text `<li Class="Pawn">`, so the first `<li` in the file is NOT the
        # element — anchor on the one that starts a line.
        m = re.search(rb"(?m)^<li\b", self.data)
        if not m:
            raise ImportError_("%s: no top-level <li> element" % self.name)
        cut = m.start()
        self.prefix = self.data[:cut]
        self.body = self.data[cut:]
        self.spans = scan_spans(self.body, {
            "loadID", "Id", "id", "faction", "ideo", "map", "pos",
            "sourceGene", "overriddenByGene", "ability",
        })
        # Every Thing id this fragment DECLARES — the pawn plus the apparel and
        # weapons carried inline. All of them live in the destination's single
        # Thing-id namespace, so all of them count for nextThingID and for the
        # collision check, not just the pawn's own.
        self.thing_ids = [
            self.body[sp.text_start:sp.text_end].decode("utf-8").strip()
            for sp in self.spans if sp.tag == "id"
        ]
        if not self.thing_ids or ("li", "id") not in [sp.path for sp in self.spans]:
            raise ImportError_("%s has no top-level <id>" % self.name)
        self.thing_id = next(self.body[sp.text_start:sp.text_end].decode("utf-8").strip()
                             for sp in self.spans if sp.path == ("li", "id"))

    def ids_by_class(self) -> dict[str, set[int]]:
        """Every integer save-local id in this fragment, bucketed by class."""
        out = {k: set() for k in COUNTER_FOR_CLASS}
        for sp in self.spans:
            txt = self.body[sp.text_start:sp.text_end].decode("utf-8").strip()
            cls = classify(sp)
            if cls and txt.lstrip("-").isdigit():
                out[cls].add(int(txt))
        for tid in self.thing_ids:
            m = re.search(r"(\d+)$", tid)
            if m:
                out["thing"].add(int(m.group(1)))
        return out


def classify(sp: Span) -> str | None:
    """Which id counter this element's value came out of, by its path."""
    if sp.tag == "loadID":
        for anc in reversed(sp.path[:-1]):
            if anc in LOADID_CLASS_BY_ANCESTOR:
                return LOADID_CLASS_BY_ANCESTOR[anc]
        return None                                # verb loadID: a string, skipped
    if sp.tag == "Id" and ABILITY_ID_ANCESTOR in sp.path[:-1]:
        return "ability"
    return None


# --------------------------------------------------------------------------- #
# allocation
# --------------------------------------------------------------------------- #

def allocate(dest: Destination, fragments: list[Fragment]) -> dict[str, dict[int, int]]:
    """Hand every fragment id a new one above everything the destination issued.

    🔴 The base is COMPUTED, per destination, per class:

        base = max(destination counter, highest id the destination issued) + 1

    and ids are then dense from there. Two different destinations therefore produce
    two different id sets for the same fragments — which is the whole point. A fixed
    offset (the +1,000,000 of the proving run) is correct only by luck and is the
    same class of bug as the collision it was papering over.
    """
    wanted: dict[str, set[int]] = {k: set() for k in COUNTER_FOR_CLASS}
    for f in fragments:
        for cls, ids in f.ids_by_class().items():
            wanted[cls] |= ids

    mapping: dict[str, dict[int, int]] = {}
    for cls, ids in wanted.items():
        if cls == "thing":
            # Thing ids are STRINGS (`Human470521`), not counter values, and they
            # are handled by plan_thing_ids — which leaves them alone unless the
            # destination actually holds one. Only nextThingID is derived here.
            continue
        counter = dest.counters.get(COUNTER_FOR_CLASS[cls], 0)
        base = max(counter, dest.issued_max.get(cls, -1) + 1)
        mapping[cls] = {old: base + i for i, old in enumerate(sorted(ids))}
    return mapping


def next_counters(mapping: dict[str, dict[int, int]], dest: Destination,
                  final_thing_numbers: set[int]) -> dict[str, int]:
    """The counter values the destination must carry after the splice.

    One past the highest id handed out, so the receiving game never issues an id
    that collides with an imported object. `final_thing_numbers` are the numeric
    suffixes the imported Things end up with — the exported ones when nothing
    forced a rename, the reallocated ones when something did.
    """
    out = {}
    for cls, counter in COUNTER_FOR_CLASS.items():
        highest = (max(final_thing_numbers, default=-1) if cls == "thing"
                   else max(mapping[cls].values(), default=-1))
        out[counter] = max(dest.counters.get(counter, 0), highest + 1)
    return out


# --------------------------------------------------------------------------- #
# rewriting a fragment
# --------------------------------------------------------------------------- #

def rewrite(frag: Fragment, dest: Destination, mapping: dict[str, dict[int, int]],
            pos: tuple[int, int], thing_id_map: dict[str, str]) -> bytes:
    """Return the fragment's bytes with every save-local reference translated."""
    patches: list[tuple[int, int, bytes]] = []

    def put(sp: Span, value: str) -> None:
        patches.append((sp.text_start, sp.text_end, value.encode("utf-8")))

    for sp in frag.spans:
        raw = frag.body[sp.text_start:sp.text_end].decode("utf-8").strip()
        cls = classify(sp)
        if cls and raw.lstrip("-").isdigit():
            old = int(raw)
            if old not in mapping[cls]:
                raise ImportError_("%s: unallocated %s id %d" % (frag.name, cls, old))
            put(sp, str(mapping[cls][old]))
            continue
        if sp.tag == "faction" and raw.startswith("Faction_"):
            put(sp, "Faction_%s" % dest.player_faction)
        elif sp.tag == "ideo" and raw.startswith("Ideo_"):
            put(sp, dest.primary_ideo or raw)
        elif sp.tag == "map" and sp.path == ("li", "map"):
            put(sp, dest.map_unique_id)
        elif sp.tag == "pos" and sp.path == ("li", "pos"):
            put(sp, "(%d, 0, %d)" % pos)
        elif sp.tag in ("sourceGene", "overriddenByGene") and raw.startswith("Gene_"):
            # 🔴 THE `Wimp` CASE. These point at a gene by its save-local loadID.
            # Left alone they resolve into the DESTINATION's genes and the
            # gene-sourced trait is dropped with nothing in the log.
            old = int(raw.split("_", 1)[1])
            if old not in mapping["gene"]:
                raise ImportError_("%s: %s -> %s references a gene the fragment "
                                   "does not declare" % (frag.name, sp.tag, raw))
            put(sp, "Gene_%d" % mapping["gene"][old])
        elif sp.tag == "ability" and raw.startswith("Ability_"):
            old = int(raw.split("_", 1)[1])
            if old in mapping["ability"]:
                put(sp, "Ability_%d" % mapping["ability"][old])

    out = apply_patches(frag.body, patches)

    # Verb loadIDs embed the ability id as a string (`Ability_677_0`), and thing
    # ids appear inside verb loadIDs too (`Thing_RSW_Dewback669123_0_Smash`).
    # Token substitution is the only thing that reaches those.
    # ⚠️ ONE pass, via a single alternation — chained `.replace()` calls re-replace
    # their own output, which silently collapsed two ids onto one when a new id
    # reused a number still present in the text.
    tokens = {("Ability_%d_" % old): ("Ability_%d_" % new)
              for old, new in mapping["ability"].items()}
    tokens.update(thing_id_map)
    if tokens:
        pat = re.compile(b"|".join(re.escape(k.encode("utf-8"))
                                   for k in sorted(tokens, key=len, reverse=True)))
        out = pat.sub(lambda m: tokens[m.group(0).decode("utf-8")].encode("utf-8"), out)

    ET.fromstring(out.decode("utf-8"))            # a fragment that no longer parses
    return out                                    # must never reach the save


def plan_thing_ids(dest: Destination, fragments: list[Fragment]) -> dict[str, str]:
    """Rename fragment thing ids ONLY if the destination already uses one.

    The 2026-09-21 proving run kept the ids as exported and the relation graph — a
    closed set of 62 `Thing_*` references across the 8 files — resolved. Renaming
    when nothing forces it would be gratuitous churn on the one thing that was
    measured to work. Renaming when something DOES force it is not optional: two
    things with one id is a corrupt save.
    """
    declared = [tid for f in fragments for tid in f.thing_ids]
    if not any(tid in dest.thing_ids for tid in declared):
        return {}
    # The new ids must clear the fragments' OWN numbers as well as the
    # destination's, because the rewrite is a token substitution over the
    # fragment text: a new id that reuses a number still present in the text
    # would be indistinguishable from the old one it replaced.
    own_max = max((int(m.group(1)) for tid in declared
                   if (m := re.search(r"(\d+)$", tid))), default=-1)
    base = max(dest.issued_max["thing"], own_max) + 1
    out = {}
    for i, tid in enumerate(sorted(set(declared))):
        out[tid] = "%s%d" % (re.sub(r"\d+$", "", tid), base + i)
    return out


# --------------------------------------------------------------------------- #
# writing
# --------------------------------------------------------------------------- #

def refuse_keeper(path: str) -> None:
    name = os.path.basename(path)
    for glob in KEEPER_GLOBS:
        # The bare glob already covers `.rws`, `.rws.bak-*` and any other suffix —
        # a keeper's backups are keepers too.
        if fnmatch.fnmatch(name, glob):
            raise ImportError_(
                "REFUSED: %s matches keeper pattern %r.\n"
                "  These saves are ruled to survive the world remake and cannot be "
                "regenerated. This script will not write to one under any flag.\n"
                "  Splice into a COPY, load it, and save from inside the game."
                % (name, glob))


def patch_counters(data: bytes, counters: dict[str, int]) -> bytes:
    """Raise the uniqueIDsManager counters, in place, by byte offset."""
    patches = []
    for sp in scan_spans(data, set(counters)):
        if sp.path[:3] != ("savegame", "game", "uniqueIDsManager"):
            continue
        patches.append((sp.text_start, sp.text_end,
                        str(counters[sp.tag]).encode("utf-8")))
    return apply_patches(data, patches)


def dominant_eol(data: bytes) -> bytes:
    """CRLF if the destination is CRLF. Keeps the spliced file internally uniform."""
    crlf = data.count(b"\r\n")
    return b"\r\n" if crlf and crlf * 2 > data.count(b"\n") else b"\n"


def splice(dest: Destination, fragments: list[Fragment],
           spacing: int = 2, anchor: tuple[int, int] | None = None) -> tuple[bytes, dict]:
    """Build the spliced save bytes. Pure: touches no file."""
    mapping = allocate(dest, fragments)
    thing_id_map = plan_thing_ids(dest, fragments)
    final_things = set()
    for f in fragments:
        for tid in f.thing_ids:
            m = re.search(r"(\d+)$", thing_id_map.get(tid, tid))
            if m:
                final_things.add(int(m.group(1)))
    counters = next_counters(mapping, dest, final_things)

    ax, az = anchor if anchor else dest.anchor
    width = spacing * (len(fragments) - 1)
    start_x = max(1, min(ax - width // 2, dest.map_size[0] - width - 2))
    az = max(1, min(az, dest.map_size[2] - 2))

    nl = dominant_eol(dest.data).decode("ascii")
    indent = "\t" * 6
    blocks = []
    for i, f in enumerate(fragments):
        body = rewrite(f, dest, mapping, (start_x + i * spacing, az), thing_id_map)
        text = re.sub(r"\r?\n", nl, body.decode("utf-8")).strip()
        blocks.append(nl + indent + text)
    payload = ("".join(blocks) + nl).encode("utf-8")

    out = dest.data[:dest.things_insert_at] + payload + dest.data[dest.things_insert_at:]
    out = patch_counters(out, counters)
    report = {
        "faction": "Faction_%s" % dest.player_faction,
        "ideo": dest.primary_ideo,
        "map": dest.map_unique_id,
        "row": [(start_x + i * spacing, az) for i in range(len(fragments))],
        "counters": counters,
        "allocated": {k: len(v) for k, v in mapping.items()},
        "bases": {k: min(v.values()) for k, v in mapping.items() if v},
        "thing_ids_renamed": thing_id_map,
        "mapping": mapping,
    }
    return out, report


def write_save(path: str, data: bytes, backup: bool = True) -> dict:
    """Back up, write in BINARY, and stat. Never a text-mode handle."""
    refuse_keeper(path)
    before = os.path.getsize(path) if os.path.exists(path) else 0
    bak = None
    if backup and os.path.exists(path):
        bak = "%s.bak-pre-founder-import-%s" % (path, time.strftime("%Y%m%dT%H%M%SZ",
                                                                   time.gmtime()))
        shutil.copy2(path, bak)
    with open(path, "wb") as fh:                   # 🔴 binary. See module docstring.
        fh.write(data)
    after = os.path.getsize(path)
    if after != len(data):
        raise ImportError_(
            "size on disk (%d) != bytes written (%d) — a text-mode handle or a "
            "line-ending translation got in. The save is suspect." % (after, len(data)))
    return {"backup": bak, "before": before, "after": after, "delta": after - before}


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Splice the exported founders into a destination savegame.")
    ap.add_argument("destination", help="path to the destination .rws")
    ap.add_argument("--out", help="write here instead of over the destination")
    ap.add_argument("--anchor", help="landing spot as x,z (default: beside the "
                                     "destination's own colonists)")
    ap.add_argument("--spacing", type=int, default=2, help="cells between pawns")
    ap.add_argument("--fragments", default=HERE, help="folder holding the fragments")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the plan and write nothing")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args(argv)

    try:
        target = args.out or args.destination
        refuse_keeper(target)                      # refuse before reading 17 MB

        dest = Destination(args.destination)
        frags = [Fragment(p) for p in fragment_files(args.fragments)]
        anchor = None
        if args.anchor:
            ax, az = (int(v) for v in args.anchor.replace(" ", "").split(","))
            anchor = (ax, az)

        data, report = splice(dest, frags, spacing=args.spacing, anchor=anchor)

        print("destination : %s" % args.destination)
        print("  faction   : Faction_%s   ideo %s   map %s"
              % (dest.player_faction, dest.primary_ideo, dest.map_unique_id))
        print("  issued max: %s" % dest.issued_max)
        print("  allocated : %s  (bases %s)" % (report["allocated"], report["bases"]))
        print("  counters  : %s" % report["counters"])
        print("  row       : %s" % report["row"])
        if report["thing_ids_renamed"]:
            print("  thing ids : RENAMED (destination already held one) %s"
                  % report["thing_ids_renamed"])
        for f in frags:
            g = sorted(f.ids_by_class()["gene"])
            if g:
                print("  %-46s genes %d..%d -> %d..%d"
                      % (f.name, g[0], g[-1],
                         report["mapping"]["gene"][g[0]],
                         report["mapping"]["gene"][g[-1]]))
        if args.dry_run:
            print("DRY RUN — nothing written.")
            return 0

        stat = write_save(target, data, backup=not args.no_backup)
        print("wrote %s  %d -> %d bytes (+%d)"
              % (target, stat["before"], stat["after"], stat["delta"]))
        if stat["backup"]:
            print("backup %s" % stat["backup"])
        return 0
    except ImportError_ as exc:
        print("\n%s\n" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
