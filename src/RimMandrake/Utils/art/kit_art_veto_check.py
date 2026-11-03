#!/usr/bin/env python3
"""kit_art_veto_check.py — proof for SPRINT_KIT_ART_SKETCH_BEFORE_THE_VETO.

Checks that the per-line judge veto of the 15 guessed biome-sprint kit designs is complete and consistent:

  * every row of the design doc's "Commissioned" table carries a verdict cell (KEEP / VETO / DROP), and a row is
    struck through exactly when it is VETO or DROP;
  * the verdict file holds the same 15 pieces, in the same order, with the same decision;
  * every VETO line, and every REDO picture, quotes the violated source and says what was seen;
  * every job id of the job file is judged, facing by facing (21 pictures);
  * every KEEP picture is a sha present in the art store (so the render cannot be stranded again).

Exit 0 all hold, 1 a check failed (each failure printed), 2 an input is missing or unreadable.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
sys.path.insert(0, str(HERE.parents[1]))  # src/RimMandrake/Utils, for rmpaths

DOC = REPO / "design/RimMandrake/kit_art_designs_2026-10-16.md"
JOBS = REPO / "design/RimMandrake/kit_art_jobs_2026-10-16.json"
VERDICTS = REPO / "infrastructure/state/delegated/2026-11-03/kit_art_veto.json"
DECISIONS = ("KEEP", "VETO", "DROP")


def store_root() -> Path:
    env = os.environ.get("ARTSTORE")
    if env:
        return Path(env)
    from rmpaths import rm_str
    return Path(rm_str("artstore"))


def doc_rows(text: str) -> list:
    """The Commissioned table's body rows, each as a list of cells."""
    lines = text.split("\n")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith("## Commissioned"))
    except StopIteration:
        return []
    rows = []
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        if not ln.startswith("| ") or ln.startswith("| piece |"):
            continue
        rows.append([c.strip() for c in ln.strip().strip("|").split(" | ")])
    return rows


def facings_of(job: dict) -> list:
    """A job's facings; the job file spells them as one string, "east,south,north"."""
    f = job.get("facings") or []
    if isinstance(f, str):
        f = f.split(",")
    return [x.strip() for x in f if x.strip()]


def piece_name(cell: str) -> str:
    """'~~Comb-hold lean-to (camp kit)~~' -> 'Comb-hold lean-to'."""
    cell = cell.replace("~~", "").strip()
    return re.sub(r"\s*\(.*\)$", "", cell).strip()


def main() -> int:
    for p in (DOC, JOBS, VERDICTS):
        if not p.is_file():
            print(f"UNMEASURED: missing {p}")
            return 2
    try:
        verdict = json.loads(VERDICTS.read_text())
        jobs = json.loads(JOBS.read_text())
    except (OSError, ValueError) as e:
        print(f"UNMEASURED: unreadable input: {e}")
        return 2
    bad = []
    rows = doc_rows(DOC.read_text())
    lines = verdict.get("lines") or []
    if len(rows) != 15:
        bad.append(f"design doc table has {len(rows)} rows, expected 15")
    if len(lines) != 15:
        bad.append(f"verdict file has {len(lines)} lines, expected 15")

    for i, (row, line) in enumerate(zip(rows, lines), 1):
        if len(row) != 5:
            bad.append(f"doc row {i}: {len(row)} cells, expected 5 (no verdict column?)")
            continue
        name, cell = piece_name(row[0]), row[4]
        dec = next((d for d in DECISIONS if cell.startswith(d)), None)
        if dec is None:
            bad.append(f"doc row {i} ({name}): verdict cell {cell!r} is not KEEP/VETO/DROP")
            continue
        struck = row[0].startswith("~~") and row[0].endswith("~~")
        if struck != (dec in ("VETO", "DROP")):
            bad.append(f"doc row {i} ({name}): struck={struck} but verdict {dec}")
        if line.get("piece") != name:
            bad.append(f"line {i}: verdict file piece {line.get('piece')!r} != doc {name!r}")
        if line.get("decision") != dec:
            bad.append(f"line {i} ({name}): verdict file {line.get('decision')!r} != doc {dec}")
        if dec == "VETO" and not (line.get("quote") and line.get("source") and line.get("seen")):
            bad.append(f"line {i} ({name}): VETO without quote/source/seen")
        if dec == "KEEP" and not line.get("why"):
            bad.append(f"line {i} ({name}): KEEP without a why")

    judged = {}
    for line in lines:
        for pic in line.get("pictures") or []:
            judged[(pic.get("job"), pic.get("facing"))] = (line, pic)
    store = store_root()
    for job in jobs:
        jid = job.get("id")
        facings = facings_of(job)
        names = [(f"{jid}_{f}", f) for f in facings] if facings else [(jid, None)]
        for name, facing in names:
            hit = [v for (j, f), v in judged.items() if j == name and (facing is None or f == facing)]
            if not hit:
                bad.append(f"job {name}: no picture verdict")
                continue
            line, pic = hit[0]
            v = pic.get("verdict")
            if v == "REDO" and not (pic.get("violated") and pic.get("quote") and pic.get("seen")):
                bad.append(f"job {name}: REDO without violated/quote/seen")
            if v == "KEEP":
                if line.get("decision") != "KEEP":
                    bad.append(f"job {name}: picture KEEP under a {line.get('decision')} line")
                sha = pic.get("picture") or ""
                if not re.fullmatch(r"[0-9a-f]{64}", sha):
                    bad.append(f"job {name}: KEEP picture {sha!r} is not an art-store sha")
                elif not (store / sha[:2] / f"{sha}.png").is_file():
                    bad.append(f"job {name}: KEEP picture {sha[:12]} not in the art store {store}")
    n_jobs = sum(max(1, len(facings_of(j))) for j in jobs)
    if n_jobs != len(judged):
        bad.append(f"{len(judged)} pictures judged, job file has {n_jobs}")

    for b in bad:
        print("FAIL", b)
    keep = sum(1 for ln in lines if ln.get("decision") == "KEEP")
    print(f"{'PASS' if not bad else 'FAIL'}: {len(rows)} doc rows, {len(lines)} verdict lines "
          f"({keep} KEEP), {len(judged)} pictures, store {store}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
