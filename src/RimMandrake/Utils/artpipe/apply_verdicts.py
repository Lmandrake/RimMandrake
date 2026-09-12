#!/usr/bin/env python3
"""apply_verdicts.py — consumes the decisions JSON downloaded from a
`make_verdict_sheet.py` review sheet and turns each ACCEPT/REJECT row into a
real `artreg.py verdict` call.

This script NEVER writes `infrastructure/artpipe/registry.jsonl` itself —
`artreg.py` is that file's sole writer (see its own module docstring and
`infrastructure/artpipe/README.md`). It only ever shells out to
`artreg.py verdict --target ... --result ... --by owner-sheet --notes ...`,
and by default it only PRINTS the commands it would run (dry-run). Pass
`--apply` to actually execute them.

SKIP rows in the decisions file are left untouched — no event is written for
them, ever, in either mode.

Decisions JSON shape (as exported by the sheet's footer download link):
{
  "sheet": "art_verdict_sheet_2026-09-12",
  "total_lanes": 147,
  "exported_at": "...",
  "decisions": [
    {"target": "aa_frostmite/east", "job_id": "aa_frostmite_v1_east",
     "decision": "accepted"|"rejected", "notes": "..."},
    ...
  ]
}
Rows with decision "skipped" or "" should not normally appear (the sheet's
own export only emits decided rows), but are tolerated and skipped here too,
defensively — never treated as an implicit reject.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTREG = HERE / "artreg.py"

VALID_RESULTS = ("accepted", "rejected")


def load_decisions(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    rows = data.get("decisions")
    if rows is None:
        raise SystemExit(f"apply_verdicts: {path} has no top-level 'decisions' list — "
                          f"is this a real export from the sheet's download link?")
    return rows


def build_commands(rows: list[dict], by: str) -> tuple[list[list[str]], list[dict]]:
    """Returns (commands, skipped_rows)."""
    commands = []
    skipped = []
    seen_targets = set()
    for row in rows:
        target = row.get("target")
        decision = row.get("decision")
        job_id = row.get("job_id")
        notes = row.get("notes") or ""
        if not target:
            skipped.append({**row, "_reason": "no target field"})
            continue
        if decision not in VALID_RESULTS:
            skipped.append({**row, "_reason": f"decision {decision!r} is not accepted/rejected "
                                               f"(SKIP rows are left untouched, on purpose)"})
            continue
        if target in seen_targets:
            skipped.append({**row, "_reason": f"duplicate row for target {target!r} — "
                                               f"first occurrence already queued, this one dropped"})
            continue
        seen_targets.add(target)
        cmd = [sys.executable, str(ARTREG), "verdict",
               "--target", target, "--result", decision,
               "--by", by, "--notes", notes]
        if job_id:
            cmd += ["--job-id", job_id]
        commands.append(cmd)
    return commands, skipped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("decisions_json", type=Path,
                     help="the JSON file downloaded from the review sheet's footer link")
    ap.add_argument("--apply", action="store_true",
                     help="actually run the artreg.py verdict commands (default: dry-run, print only)")
    ap.add_argument("--by", default="owner-sheet",
                     help="the --by value recorded on each verdict event (default: owner-sheet)")
    args = ap.parse_args(argv)

    if not args.decisions_json.is_file():
        print(f"apply_verdicts: ERROR no such file: {args.decisions_json}", file=sys.stderr)
        return 2

    rows = load_decisions(args.decisions_json)
    commands, skipped = build_commands(rows, args.by)

    print(f"decisions file: {args.decisions_json}")
    print(f"rows in file: {len(rows)} · actionable (accept/reject): {len(commands)} · "
          f"skipped/untouched: {len(skipped)}")
    print()

    for cmd in commands:
        print(" ".join(_shellquote(c) for c in cmd))

    if skipped:
        print()
        print(f"-- {len(skipped)} row(s) left untouched --")
        for s in skipped:
            print(f"  target={s.get('target')!r} decision={s.get('decision')!r}: {s['_reason']}")

    if not args.apply:
        print()
        print("dry-run only — pass --apply to execute these against artreg.py "
              "(the sole writer of registry.jsonl)")
        return 0

    print()
    print(f"-- applying {len(commands)} verdict(s) --")
    failures = 0
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        target = cmd[cmd.index("--target") + 1]
        if result.returncode != 0:
            failures += 1
            print(f"FAILED  {target}: {result.stderr.strip()}")
        else:
            print(f"OK      {target}: {result.stdout.strip()}")
    if failures:
        print(f"\n{failures} of {len(commands)} verdict(s) failed — see above", file=sys.stderr)
        return 1
    return 0


def _shellquote(s: str) -> str:
    if s == "" or any(c in s for c in " \t\n\"'$`\\"):
        return "'" + s.replace("'", "'\\''") + "'"
    return s


if __name__ == "__main__":
    sys.exit(main())
