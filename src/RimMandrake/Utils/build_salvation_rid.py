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
from pathlib import Path

IDEOS = Path(
    "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
    "RimWorld by Ludeon Studios/Ideos"
)
SRC = IDEOS / "The Salvation.rid"
OUT = IDEOS / "The Salvation (CREATE).rid"
REPO = Path("/mnt/d/Luke/dev/Rimworld")
DESC_DOC = REPO / "design/Jawa/worldbuilding/ideoligion/the_salvation_description.md"

# ---------------------------------------------------------------- description

# The player-facing text. Kept here as one string so the file the game reads and
# the doc the owner reviews cannot drift; the doc carries the sourcing, this
# carries the bytes. Newlines are real newlines — RimWorld renders them.
DESCRIPTION = (
    '"We were content with our simple lives of scavenging, with little need for '
    "the extravagant luxuries of our ancestors. Then we found the Cradle, and "
    'the Cradle was owed."\n\n'
    "We are the Keepers of the Second Hand. We hold that nothing is ever truly "
    "lost - only owed, only mislaid, only waiting for a better master. What "
    "others throw down, we inherit. What others break, we are owed the waking "
    "of.\n\n"
    "Nine gods argue over us, and not one of them agrees.\n\n"
    "Ishko the Unmaskable is the pair of orange eyes in the dark. He teaches "
    "cover, the covered body, the shot no one saw fired; the grave is the "
    "deepest hiding, and a Jawa who dies unseen has hidden perfectly. Ohm the "
    "All-Current is the spark that wakes a dead engine, and he rides in the "
    "Cradle-Mind - lonely for his lost hands. Oomo the Unspilled is the drop "
    "that never falls, and he counts every mouthful and every egg. Mob'Unloo "
    "the Ever-Owed keeps the ledger and asks only how much: a thing is right if "
    "it profited and wrong if it cost, and an unpaid debt follows you past "
    "death. Rekko of the Second Hand is the scarred hand rising from the heap; "
    "a wreck is not neutral scrap but a thing with a past, and a machine that "
    "could still be repaired is not scrap at all - it is a sleeping hand, owed "
    "its waking. Ta'Baa the Unrooted is farewell itself, the cunning coward, "
    "who holds that a clan which stops is already dead and that the launch is "
    "the holiest rite there is. Zizzik the Spark-Maker is the rattle you can "
    "never locate; we honour him so that he sleeps. Sh'kaar the All-Searing is "
    "the sun that never sets, and he is not our friend - against him there are "
    "only three moves: hide, abandon the plan, or run. Ozzik the Shamed is the "
    "tarnished crown half-buried in sand, the memory that we were once great "
    "and cannot bear it. He is a trap, and we love him anyway.\n\n"
    "No act pleases all nine. To trade boldly offends the god who says do not "
    "be seen. To hide well offends the god who says leave. To restore the "
    "Cradle honours Rekko and feeds Ozzik in the same motion. This is not a "
    "flaw in the faith. This is the faith: the Council argues, it never "
    "announces, and we are always losing gracefully.\n\n"
    "So: do not beg - the one who begs has thrown away his hands. Do not be "
    "caught - he does not condemn the theft, he condemns being bad at it. And "
    "never melt what can still be made to work.\n\n"
    "We are saved by what we salvage."
)

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

# Owner ruled: cut to ONE relic. Lore caps relics at one of modest value
# (jawa_xenotype_and_religion.md:109, :346, :351) and the ion blaster is the
# doc's own named candidate (:350) - "the tool the first Jawa used to open the
# crashed Factory ship's hull". Verified 2026-08-14: no `Precept_<ID>` anywhere
# in the file references 6558 or 6559, so both blocks lift out cleanly.
RELICS_TO_CUT = ["Trade-Hood", "Endcrux"]

# The surviving relic keeps a generator name; the lore gives it a real one.
RELIC_RENAME = ("Scavenging Relic", "The Founding Ion Blaster")

# Precept swaps land here once the lore sweep reports. Each is
# (issue_label, old_def, new_def) and is applied by locating the <li> whose
# <def> matches old_def and rewriting only that one line.
PRECEPT_SWAPS: list[tuple[str, str, str]] = []


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
        report += ["precepts:"] + log

    text, log = refresh_symbols(text)
    report += ["symbols:"] + log

    # Post-conditions. Cheap, and each one has a real failure mode behind it.
    n_precepts = text.count("\t\t\t<li Class=\"Precept") + len(
        re.findall(r"\t\t\t<li>\n\t\t\t\t<name>", text)
    )
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
