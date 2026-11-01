#!/usr/bin/env python3
"""Prove CANON_HERD_LORE_ARBITRATION_1: every UNCLEAR lore row carries a judged delegated decision.

Reads the lore CSV, the decisions CSV beside it and the judge record, and asks rimflow whether
EXTRA_ART_PER_BIOME_COMMISSION_1 still waits on the item. Prints one line per failure; exit 0 means proven.
"""
import csv
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
ITEM = "CANON_HERD_LORE_ARBITRATION_1"
FOLDER = ROOT / "design/RimStarWars/canon_herd_lore"
VERDICT = ROOT / f"infrastructure/state/delegated/2026-11-01/{ITEM}.json"
SRC = f"delegated:design ({ITEM})"
ALLOWED = {"herd", "pack", "solitary", "leave default"}
UNCLEAR_ROWS = 45
GROUP_ROWS = 14
MORPH_ROWS = 8


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check_rows(lore, decisions, verdicts):
    """Return the failures across the lore rows, the decision rows and the judge rows."""
    bad = []
    unclear = [r["subject"] for r in lore if r["social"] == "UNCLEAR"]
    groups = [r["subject"] for r in lore if r["social"] == "GROUP"]
    if len(unclear) != UNCLEAR_ROWS:
        bad.append(f"lore CSV has {len(unclear)} UNCLEAR rows, expected {UNCLEAR_ROWS}")
    by_kind = {}
    for d in decisions:
        by_kind.setdefault(d["kind"], {})[d["subject"]] = d
    for kind, want in (("unclear", unclear), ("group", groups)):
        for subject in want:
            if subject not in by_kind.get(kind, {}):
                bad.append(f"{kind} row without a decision: {subject}")
    if len(by_kind.get("morph", {})) != MORPH_ROWS:
        bad.append(f"{len(by_kind.get('morph', {}))} morph rows, expected {MORPH_ROWS}")
    if len(groups) != GROUP_ROWS:
        bad.append(f"lore CSV has {len(groups)} GROUP rows, expected {GROUP_ROWS}")
    judged = {v["subject"]: v for v in verdicts}
    for d in decisions:
        name = d["subject"]
        if d["decision"] not in ALLOWED:
            bad.append(f"{name}: decision {d['decision']!r} is not one of the four")
        if d["src"] != SRC:
            bad.append(f"{name}: src is {d['src']!r}")
        if not d["basis"].strip():
            bad.append(f"{name}: no basis")
        v = judged.get(name)
        if v is None:
            bad.append(f"{name}: no judge verdict")
        elif v["decision"] != d["decision"]:
            bad.append(f"{name}: decision {d['decision']!r} differs from the judge's {v['decision']!r}")
    return bad


def still_blocked_on_item():
    """True when rimflow shows the art commission waiting on this item."""
    cli = ROOT / "src/RimMandrake/rimflow/cli.py"
    shown = subprocess.run([sys.executable, str(cli), "show", "EXTRA_ART_PER_BIOME_COMMISSION_1"],
                           capture_output=True, text=True, timeout=120, cwd=ROOT, check=True).stdout
    head = shown.split("--- items/")[0]
    if "EXTRA_ART_PER_BIOME_COMMISSION_1" not in head:
        raise SystemExit("rimflow show printed no item header: the instrument cannot see")
    return f"(on {ITEM})" in head


def main():
    record = json.loads(VERDICT.read_text(encoding="utf-8"))
    bad = check_rows(read_csv(FOLDER / "canon_herd_lore_2026-10-08.csv"),
                     read_csv(FOLDER / "canon_herd_lore_decisions.csv"), record["rows"])
    if "gpt" not in str(record["judge_model"]).lower():
        bad.append("the judge record does not name the independent GPT judge")
    if still_blocked_on_item():
        bad.append(f"EXTRA_ART_PER_BIOME_COMMISSION_1 is still blocked on {ITEM}")
    for line in bad:
        print("FAIL", line)
    print("PROVEN" if not bad else f"{len(bad)} FAILURES")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
