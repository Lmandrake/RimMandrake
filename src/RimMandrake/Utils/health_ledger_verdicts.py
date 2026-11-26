#!/usr/bin/env python3
"""Outcome check of HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP: every game-health metric has a verdict, and every
metric ruled CUT is gone from the code.

Reads the "## Metrics ledger" table of design/RimMandrake/game_health_record.md. The last cell of each row is the
verdict. It starts with KEEP or CUT. A CUT cell names what must be gone after `gone:`, as `;`-free, comma-separated
specs: `<repo path>` (the file is absent) or `<repo path>::<text>` (the file is absent or lacks the text).
A CUT metric's id, quoted ("id" or 'id'), must also be absent from every .py, .cs and .json file under src/ and
infrastructure/stevedesktop/, so a reader left behind is seen.

    python3 src/RimMandrake/Utils/health_ledger_verdicts.py check      exit 0 holds, 1 does not (each fault printed)
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
RECORD = ROOT / "design/RimMandrake/game_health_record.md"
CODE_DIRS = ("src", "infrastructure/stevedesktop")
CODE_SUFFIXES = {".py", ".cs", ".json"}
SELF = pathlib.Path(__file__).resolve()


def ledger_rows(text: str) -> list[list[str]]:
    lines = text.split("\n## Metrics ledger", 1)[1].split("\n## ", 1)[0].splitlines()
    rows = [l for l in lines if l.startswith("| `")]
    return [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]


def faults() -> list[str]:
    out: list[str] = []
    rows = ledger_rows(RECORD.read_text(encoding="utf-8"))
    if not rows:
        return ["no metric rows found in the Metrics ledger table"]
    code_files = None
    for cells in rows:
        metric = cells[0].split("`")[1]
        verdict = cells[-1]
        if not re.match(r"\**(KEEP|CUT)\b", verdict):
            out.append(f"{metric}: no verdict (last cell must start KEEP or CUT): {verdict[:60]!r}")
            continue
        if not re.match(r"\**CUT\b", verdict):
            continue
        m = re.search(r"gone:\s*(.+)$", verdict)
        if not m:
            out.append(f"{metric}: CUT but names nothing after 'gone:'")
            continue
        for spec in [s.strip().strip("`") for s in m.group(1).split(",") if s.strip()]:
            path, _, needle = spec.partition("::")
            p = ROOT / path.strip()
            if p.exists() and (not needle or needle in p.read_text(encoding="utf-8", errors="replace")):
                out.append(f"{metric}: still present: {spec}")
        if code_files is None:
            code_files = [f for d in CODE_DIRS for f in (ROOT / d).rglob("*")
                          if f.suffix in CODE_SUFFIXES and f.is_file() and f.resolve() != SELF]
        quoted = (f'"{metric}"', f"'{metric}'")
        for f in code_files:
            try:
                body = f.read_text(encoding="utf-8", errors="replace")
            except FileNotFoundError:  # deleted since the scan began
                continue
            if any(q in body for q in quoted):
                out.append(f"{metric}: id still in code: {f.relative_to(ROOT)}")
    return out


def main(argv: list[str]) -> int:
    if argv[1:] != ["check"]:
        print(__doc__)
        return 2
    try:
        found = faults()
    except Exception as e:  # an unreadable record is a check that does not hold
        print(f"NOT HOLDING: could not read the record: {e}")
        return 1
    for f in found:
        print("  " + f)
    print("HOLDS" if not found else f"NOT HOLDING: {len(found)} fault(s)")
    return 0 if not found else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
