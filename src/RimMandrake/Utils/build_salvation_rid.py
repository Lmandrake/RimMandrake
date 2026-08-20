#!/usr/bin/env python3
"""build_salvation_rid.py — surgically edit the owner's Jawa ideoligion .rid.

The source is the owner's own file; this script NEVER rewrites it in place and
never pretty-prints. A .rid is Scribe output — tab-indented, with typed
`Class="..."` attributes and `IsNull="True"` sentinels — and a generic XML
round-trip reformats all 160 KB, which makes the owner's diff unreadable and
risks dropping an attribute. Every edit here is a targeted string operation on
the exact text, and the script asserts each one landed.

Usage:
    python3 src/RimMandrake/Utils/build_salvation_rid.py --check
    python3 src/RimMandrake/Utils/build_salvation_rid.py --write

--check  parses, applies every edit in memory, reports what changed, writes nothing.
--write  writes the result to the Ideos folder as a NEW file beside the original.

The original `The Salvation.rid` is never touched. Output is a separate name so
the owner can load both in the ideo browser and compare.
"""

import argparse
import re
import shutil
import sys
import zlib
from pathlib import Path

IDEOS = Path(
    "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
    "RimWorld by Ludeon Studios/Ideos"
)
SRC = IDEOS / "The Salvation.rid"
OUT = IDEOS / "The Salvation (built).rid"
REPO = Path("/mnt/d/Luke/dev/Rimworld")
DESC_DOC = REPO / "design/Jawa/worldbuilding/ideoligion/the_salvation_description.md"

# ---------------------------------------------------------------- description

# 🔑 The player-facing text is NOT kept here any more. It has ONE source -
# the doc named by DESC_DOC above - and `salvation_description.py` renders it for
# every consumer (this script, the faction def, the committed .rid). It used to be
# a literal in this file, which meant four hand-maintained copies and no way to
# notice drift. Run `salvation_description.py --check` to prove they still agree.
from salvation_description import text as _description_text

DESCRIPTION = _description_text()

# ---------------------------------------------------------------- edit tables

# Owner-ruled, 2026-08-14. Each entry is (description, old_exact, new_exact).
SIMPLE_EDITS = [
    (
        "name: the 2026-08-08 lock",
        "\t\t<name>Path of Scavengers</name>\n",
        "\t\t<name>The Salvation</name>\n",
    ),
]

# Owner ruled: add AM_Fertility, which is the meme AM_LovinFrequency_Exuberant
# requires. Without it that precept does not resolve.
MEME_ADDITIONS = ["AM_Fertility"]

# Owner ruled: cut to ONE relic. Lore caps relics at one of modest value and the
# ion blaster is the named candidate - "the tool the first Jawa used to open the
# crashed Factory ship's hull". Ruling of record:
# design/Jawa/worldbuilding/ideoligion/APPROVED.md (Founding Ion Blaster). Verified 2026-08-14: no `Precept_<ID>` anywhere
# in the file references 6558 or 6559, so both blocks lift out cleanly.
RELICS_TO_CUT = ["Trade-Hood", "Endcrux"]

# The surviving relic keeps a generator name; the lore gives it a real one.
RELIC_RENAME = ("Scavenging Relic", "The Founding Ion Blaster")

# Precept swaps. Each is (issue_label, old_def, new_def), applied by rewriting
# the single <def> line of the matching <li>. Every replacement was checked in
# the live dump on 2026-08-14: all are `RimWorld.Precept` (no extra fields to
# author), all have empty `requiredMemes`, and none of their `conflictingMemes`
# is in this ideo's set.
PRECEPT_SWAPS: list[tuple[str, str, str]] = [
    # STRONG. Slavery is load-bearing lore (:427 "core, not optional") but the
    # vanilla Slavery precept covers humans, and in this stack nearly every
    # captive is an alien - so the doctrine was landing on almost nobody.
    ("alien slavery", "HAR_AlienSlavery_Acceptable", "HAR_AlienSlavery_Honorable"),
    # STRONG. Cannibalism_Horrible was already set for humans while eating
    # aliens sat neutral - half the taboo unenforced, and the bigger half.
    ("eating aliens", "HAR_EatingAliens_Acceptable", "HAR_EatingAliens_Abhorrent"),
    # STRONG. The owner is adding the AM_Fertility meme; this is the precept
    # that gives it teeth (Fertility +0.20). Without it the meme is decorative.
    ("fertility", "AM_FertilityIssue_Normal", "AM_FertilityIssue_Increased"),
    # MODERATE. The gear triad's third axis - "proud of humble gear, indifferent
    # to provenance, COMPULSIVE about condition" (:388). Condition was the one
    # axis with no bite.
    ("tattered apparel", "VME_TatteredApparel_Disapproved", "VME_TatteredApparel_Abhorrent"),
    # MODERATE. "walk, burrow, pry, carry, flee, endure" (:335). Mood-only, so
    # it does not violate the no-work-multiplier pillar.
    ("dumb labor", "VME_DumbLabor_Indifferent", "VME_DumbLabor_Exalted"),
]

# Precepts ADDED on issues the ideo held no position on at all. This is where
# the named doctrines were missing - each one below is a lore line that had no
# mechanical existence in the file.
#
# `name` is the IssueDef's own label, read from the dump, because that is what
# the .rid stores and what the UI shows. IDs are minted above the file's current
# maximum; seeds are derived from the defName so a re-run is byte-identical.
PRECEPT_ADDITIONS = [
    # STRONG. ":324 The clan sleeps as one body; to sleep alone is to be already
    # exiled." The doc flags this "add this precept immediately". Note the
    # vanilla Barracks_Preferred is ILLEGAL here (requires the Collectivist
    # meme); the Alpha Memes one has no meme requirement.
    dict(name="barracks", defName="AM_Barracks_Preferred"),
    # STRONG. The light-taboo (:216) - to make a light in the dark is to do
    # Sh'kaar's work.
    dict(name="lighting", defName="Darklight_Preferred"),
    # STRONG. ":126 ambush from cover and darkness." Carries no comps but four
    # statOffsets: +0.25 accuracy in darkness, -0.20 in light.
    dict(name="combat in darkness", defName="DarknessCombat_Preferred"),
    # STRONG, and deliberately the "distance" position, not the melee one.
    dict(name="combat prowess", defName="AM_CombatProwess_Increased"),
    # STRONG. ":126 to fight hand-to-hand is to be dragged out of cover, into
    # the open, seen and gripped - the impious way to fight." Melee/Ranged is a
    # legal axis: WeaponClassPairDef `MeleeRanged` ships, and both
    # WeaponClassDefs exist.
    dict(
        name="weapons",
        defName="NobleDespisedWeapons",
        cls="Precept_Weapon",
        extra=[("noble", "Ranged"), ("despised", "Melee")],
    ),
    # STRONG. The Never-Nudes (:126, :132 apparel-always) and the hooded look
    # (:360). `_Subordinate` so it does not fight armour; `_Strong` for the
    # full mood. Also makes members ARRIVE wearing it.
    # ⚠️ OWNER: `guy762_JawaHood` ("hood, heavy") is also live and is literally
    # named for the species. One word to change if you prefer it.
    dict(
        name="apparel desire",
        defName="ApparelDesired_Strong_Subordinate",
        cls="Precept_Apparel",
        extra=[("apparelDef", "OuterRim_DesertHood")],
    ),
    # Ta'Baa's theology, and it costs NO meme slot - `requiredMemes` is empty.
    # MEASURED: `GravshipUtility::ArriveNewMap` unconditionally stamps
    # `IdeoManager.lastResettledTick`, which is the only thing this precept's
    # ThoughtWorker reads. So a jump to a fresh tile IS a resettle to the
    # engine, not "building our own base again". +4 mood for 5 days after a
    # landing, -3 once you sit 20+ days, +30% caravan speed.
    # ⚠️ Landing back on a tile you already hold resets nothing -
    # `ArriveExistingMap` does not write the field.
    dict(name="nomadic", defName="Nomadic_Preferred"),
]


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def apply_simple(text: str, edits) -> tuple[str, list[str]]:
    log = []
    for label, old, new in edits:
        n = text.count(old)
        if n != 1:
            fail(f"{label}: expected exactly 1 match, found {n}")
        text = text.replace(old, new)
        log.append(f"  {label}")
    return text, log


def set_description(text: str) -> tuple[str, list[str]]:
    """Replace <description> and <descriptionTemplate> with the same string.

    RimWorld writes both, and the editor re-rolls the prose when they disagree,
    so they must move together.
    """
    log = []
    for tag in ("description", "descriptionTemplate"):
        pat = re.compile(rf"(\t\t<{tag}>)(.*?)(</{tag}>\n)", re.S)
        m = pat.search(text)
        if not m:
            fail(f"<{tag}> not found")
        text = pat.sub(lambda mm: mm.group(1) + DESCRIPTION + mm.group(3), text, count=1)
        log.append(f"  <{tag}> replaced ({len(m.group(2))} -> {len(DESCRIPTION)} chars)")
    return text, log


def add_memes(text: str, memes) -> tuple[str, list[str]]:
    log = []
    for meme in memes:
        if f"<li>{meme}</li>" in text:
            log.append(f"  {meme}: already present, skipped")
            continue
        anchor = "\t\t\t<li>VME_Trader</li>\n"
        if text.count(anchor) != 1:
            fail(f"meme anchor not unique for {meme}")
        text = text.replace(anchor, anchor + f"\t\t\t<li>{meme}</li>\n")
        log.append(f"  +{meme}")
    return text, log


def cut_precept(text: str, name: str) -> tuple[str, str]:
    """Lift out the whole <li ...>...</li> whose <name> is `name`.

    Returns (text, id) so the caller can confirm nothing referenced that ID.
    """
    needle = f"<name>{name}</name>"
    i = text.find(needle)
    if i < 0:
        fail(f"precept {name!r} not found")
    start = text.rfind("\t\t\t<li", 0, i)
    end = text.find("\t\t\t</li>\n", i)
    if start < 0 or end < 0:
        fail(f"could not bound the <li> for {name!r}")
    end += len("\t\t\t</li>\n")
    block = text[start:end]
    m = re.search(r"<ID>(\d+)</ID>", block)
    pid = m.group(1) if m else "?"
    refs = text.count(f"Precept_{pid}")
    if refs:
        fail(f"{name!r} (ID {pid}) still has {refs} inbound Precept_{pid} references")
    return text[:start] + text[end:], pid


def rename_precept(text: str, old: str, new: str) -> str:
    needle = f"<name>{old}</name>"
    if text.count(needle) != 1:
        fail(f"rename source {old!r} is not unique")
    return text.replace(needle, f"<name>{new}</name>", 1)


def swap_precepts(text: str, swaps) -> tuple[str, list[str]]:
    log = []
    for label, old_def, new_def in swaps:
        needle = f"\t\t\t\t<def>{old_def}</def>\n"
        if text.count(needle) != 1:
            fail(f"{label}: <def>{old_def}</def> is not unique")
        text = text.replace(needle, f"\t\t\t\t<def>{new_def}</def>\n", 1)
        log.append(f"  {label}: {old_def} -> {new_def}")
    return text, log


def add_precepts(text: str, additions) -> tuple[str, list[str]]:
    """Append new <li> precept blocks just before </precepts>.

    A precept is only safe to hand-author when its `preceptClass` needs no
    generated content. Every entry here was checked against the live dump and
    against a real save's serialization, so the shapes below are copied, not
    guessed.
    """
    log = []
    used = {int(i) for i in re.findall(r"<ID>(\d+)</ID>", text)}
    next_id = max(used) + 1
    close = "\t\t</precepts>\n"
    if text.count(close) != 1:
        fail("</precepts> is not unique")

    blocks = []
    for a in additions:
        if f"<def>{a['defName']}</def>" in text:
            log.append(f"  {a['defName']}: already present, skipped")
            continue
        pid = next_id
        next_id += 1
        # Deterministic seed: the game only uses it to pick generated flavour,
        # and a stable value keeps re-runs byte-identical. crc32, NOT hash() -
        # Python randomises string hashing per process, which would make every
        # run produce a different file for no reason.
        seed = zlib.crc32(a["defName"].encode()) - 2_147_483_648
        cls = f' Class="{a["cls"]}"' if a.get("cls") else ""
        b = [
            f"\t\t\t<li{cls}>\n",
            f"\t\t\t\t<name>{a['name']}</name>\n",
            f"\t\t\t\t<def>{a['defName']}</def>\n",
            f"\t\t\t\t<ID>{pid}</ID>\n",
            f"\t\t\t\t<randomSeed>{seed}</randomSeed>\n",
            "\t\t\t\t<usesDefiniteArticle>True</usesDefiniteArticle>\n",
        ]
        for k, v in a.get("extra", []):
            b.append(f"\t\t\t\t<{k}>{v}</{k}>\n")
        b.append("\t\t\t</li>\n")
        blocks.append("".join(b))
        detail = " ".join(f"{k}={v}" for k, v in a.get("extra", []))
        log.append(f"  +{a['defName']} (ID {pid}){' ' + detail if detail else ''}")

    if blocks:
        text = text.replace(close, "".join(blocks) + close, 1)
    return text, log


def refresh_symbols(text: str) -> tuple[str, list[str]]:
    """usedSymbols is the ledger of strings the generator already consumed.

    Leaving 'Path of scavengers' in it after renaming the ideo leaves a stale
    entry that the editor may re-offer. Effect is UNVERIFIED; the correction is
    free, so make it.
    """
    old = (
        "\t\t\t<li>Path of scavengers</li>\n"
        "\t\t\t<li>scavenging</li>\n"
        "\t\t\t<li>Scavenger</li>\n"
    )
    if text.count(old) != 1:
        return text, ["  usedSymbols: block not matched, left alone"]
    new = (
        "\t\t\t<li>The Salvation</li>\n"
        "\t\t\t<li>scavenging</li>\n"
        "\t\t\t<li>Scavenger</li>\n"
    )
    return text.replace(old, new, 1), ["  usedSymbols: 'Path of scavengers' -> 'The Salvation'"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="apply in memory, write nothing")
    g.add_argument("--write", action="store_true", help="write the new .rid")
    args = ap.parse_args()

    if not SRC.exists():
        fail(f"source not found: {SRC}")
    text = SRC.read_text(encoding="utf-8")
    original_len = len(text)

    report: list[str] = []

    text, log = apply_simple(text, SIMPLE_EDITS)
    report += ["name:"] + log

    text, log = set_description(text)
    report += ["description:"] + log

    text, log = add_memes(text, MEME_ADDITIONS)
    report += ["memes:"] + log

    report += ["relics:"]
    for name in RELICS_TO_CUT:
        text, pid = cut_precept(text, name)
        report.append(f"  -{name} (ID {pid}, 0 inbound refs)")
    text = rename_precept(text, *RELIC_RENAME)
    report.append(f"  {RELIC_RENAME[0]!r} -> {RELIC_RENAME[1]!r}")

    if PRECEPT_SWAPS:
        text, log = swap_precepts(text, PRECEPT_SWAPS)
        report += ["precepts changed:"] + log

    if PRECEPT_ADDITIONS:
        text, log = add_precepts(text, PRECEPT_ADDITIONS)
        report += ["precepts added:"] + log

    text, log = refresh_symbols(text)
    report += ["symbols:"] + log

    # Post-conditions. Cheap, and each one has a real failure mode behind it.
    ids = re.findall(r"<ID>(\d+)</ID>", text)
    if len(ids) != len(set(ids)):
        fail("duplicate precept IDs after edit")
    for ref in set(re.findall(r"Precept_(\d+)", text)):
        if ref not in set(ids):
            fail(f"dangling reference Precept_{ref} - it points at a cut precept")
    if "<savedideo>" not in text or "</savedideo>" not in text:
        fail("root element damaged")

    print("\n".join(report))
    print(f"\n{original_len:,} -> {len(text):,} bytes · {len(ids)} precepts · IDs unique · no dangling refs")

    if args.write:
        if OUT.exists():
            backup = OUT.with_suffix(".rid.bak")
            shutil.copy2(OUT, backup)
            print(f"previous output backed up: {backup}")
        OUT.write_text(text, encoding="utf-8")
        print(f"WROTE {OUT}")
        print(f"the owner's original is untouched: {SRC}")
    else:
        print("--check only, nothing written")


if __name__ == "__main__":
    main()
