#!/usr/bin/env python3
"""Selftest: the retired name RUT_FuelSnows stays out of live docs and code, and the biome paint list
tells the def truth (FUELSNOWS_NAME_CULL_FROM_LIVE_DOCS).

RUT_FuelSnows was the name of the Auroral Umbra land from 2026-09-21 until the owner renamed it back to
RUT_Umbra (card 2026-10-19, "Let's call it the Auroral Umbra then"). Live text kept calling it a biome.
Source of the repair: design/RimMandrake/biome_name_provenance_audit_2026-10-28.md, repairs table.

1. No file names RUT_FuelSnows unless it is a historic record (dated archive trees below) or one of the
   HISTORIC files, each of which names it only as the retired name. A new mention fails: either it is
   live text (rewrite it to RUT_Umbra) or a record (add it here with the reason).
2. infrastructure/state/facts/biome_paint_list.md: every row's label equals its BiomeDef's label in src/.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAME = "RUT_FuelSnows"
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()

# Trees that are records by kind: transcripts, handoffs, closed items, ledgers, review logs, art history.
HISTORIC_TREES = (
    "Transient/", "conversations/", "infrastructure/state/handoffs/", "infrastructure/state/items/closed/",
    "infrastructure/state/ledger/", "infrastructure/state/code_review/", "infrastructure/state/art/",
    "infrastructure/state/art_rulings/", "infrastructure/dashboards/",
    "infrastructure/state/queue/",  # projections of the ledger: they quote item titles of their day
)
# Files that name RUT_FuelSnows only as the retired name, or are dated snapshots of their day.
HISTORIC = {
    SELF: "this test",
    "src/RimMandrake/Utils/selftest_ops_watch_cause_book_corpus.json": "replay corpus of ledger spawn rows",
    "src/RimMandrake/Utils/selftest_baroque_biomes_list_page.py": "asserts the page no longer names it",
    "src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Umbra.xml": "rename history comment",
    "src/RimUtinni/UtinniPatches/Defs/Misc/RUT_UmbraRename_Aliases.xml": "the load alias for old saves",
    "src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PropaneLakeFauna.xml": "'briefly named' note",
    "design/Jawa/fauna/biome_name_migration.py": "'was RUT_FuelSnows' note",
    "design/Jawa/mods/biome_flora.py": "'RUT_FuelSnows 2026-09-21..2026-10-20' note",
    "design/RimMandrake/flowworks_liquid_matrix.md": "'named RUT_FuelSnows 2026-09-21..2026-10-20' note",
    "design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md": "'briefly RUT_FuelSnows' correction",
    "design/RimMandrake/explosive_growth_bench_design_pass_2026-10-16.md": "dated PROPOSAL, measured 10-16",
    "design/RimMandrake/alpha_biomes_hits_2026-10-16.json": "dated scan output of 2026-10-16",
    "design/RimMandrake/biome_name_provenance_audit_2026-10-28.md": "the audit that found the name",
    "design/RimMandrake/world_remake_2026-10-19/02_world_pipeline.md": "'rename was reversed' note",
    "design/RimMandrake/world_remake_2026-10-19/13_owner_rulings_2026-10-19.md": "the ruling itself",
    "design/RimMandrake/world_remake_2026-10-19/PLAN.md": "'rename was reversed' note",
    "design/RimMandrake/world_remake_2026-10-19/paint_inputs_remap.json": "'remap is cancelled' note",
    "infrastructure/state/items/AURORAL_UMBRA_RENAME_BACK_TO_DARK.md": "the rename-back item",
    "infrastructure/state/items/CUT_FALLOUT_GENERATED_DATA_1.md": "dated run narrative",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", "bin", "obj"}
TEXT = {".md", ".py", ".xml", ".json", ".jsonl", ".csv", ".html", ".txt", ".cs", ".yaml", ".yml", ".sh"}


def live_mentions():
    hits = []
    stack = [ROOT]
    while stack:
        d = stack.pop()
        for p in d.iterdir():
            if p.is_dir():
                if p.name not in SKIP_DIRS and not p.is_symlink():
                    stack.append(p)
                continue
            if p.suffix.lower() not in TEXT:
                continue
            rel = p.relative_to(ROOT).as_posix()
            if rel.startswith(HISTORIC_TREES) or rel in HISTORIC:
                continue
            try:
                if NAME in p.read_text(encoding="utf-8", errors="replace"):
                    hits.append(rel)
            except OSError:
                continue
    return hits


def src_labels():
    labels = {}
    for p in (ROOT / "src").rglob("*.xml"):
        try:
            r = ET.parse(p).getroot()
        except (ET.ParseError, OSError):
            continue
        for b in r.iter("BiomeDef"):
            n, lab = b.findtext("defName"), b.findtext("label")
            if n and lab is not None:
                labels[n] = lab.strip()
    return labels


def paint_rows():
    text = (ROOT / "infrastructure/state/facts/biome_paint_list.md").read_text(encoding="utf-8")
    rows = {}
    for line in text.splitlines():
        m = re.match(r"\| `([A-Za-z0-9_]+)` \|", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[m.group(1)] = cells
    return rows


def main():
    fails = []
    hits = live_mentions()
    for h in hits:
        fails.append(f"live file names {NAME}: {h}")
    rows = paint_rows()
    labels = src_labels()
    if len(rows) < 30 or len(labels) < 30:  # sanity: the instrument can see the table and the defs
        fails.append(f"instrument blind: {len(rows)} paint rows, {len(labels)} src BiomeDefs")
    for name, cells in rows.items():
        if name not in labels:
            fails.append(f"paint row {name}: no BiomeDef in src/")
        elif cells[1] != labels[name]:
            fails.append(f"paint row {name}: label {cells[1]!r} != src {labels[name]!r}")
    if NAME in rows:
        fails.append(f"paint list still has a {NAME} row")
    for f in fails:
        print("FAIL:", f)
    print(f"{'FAIL' if fails else 'PASS'}: {len(rows)} paint rows vs {len(labels)} src BiomeDefs, "
          f"{len(hits)} live {NAME} mentions")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
