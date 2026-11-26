#!/usr/bin/env python3
"""regress_holds.py - does the regression set hold on the CURRENT prompts and templates (criteria_ledger.md step 5)?

    python3 src/RimMandrake/Utils/art_eval/regress_holds.py [--rows SUBJ,...] [--codes CODE,...]

Reads the newest regression run (`infrastructure/state/art_eval/regression_runs/*.json`) whose versions key equals the
current set's key (runner.regress_set). Exit 0 when that run judged every row, every failed row names its open
criteria-ledger miss (`known_miss`), each subject in --rows has a row and that row passed, and, with --codes, each
--rows subject's decision blocked on at least one of those codes (so a row refused for some other fault does not count
as the judge seeing this one). Exit 1 otherwise, with the reason. Exit 2 when it could not look.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def blocking_codes(rec: dict) -> set:
    out = set()
    for side in ("opus", "gpt"):
        det = (rec.get(side) or {}).get("detail") or {}
        out |= {f.get("code") for f in det.get("blocking") or [] if isinstance(f, dict)}
    return out - {None}


def verdict(rows_needed: list, codes: set, state: Path | None = None, current: tuple | None = None) -> tuple[int, str]:
    """state: the art_eval state folder (default runner.STATE); current: (number of rows, versions key) of the set
    (default runner.regress_set()). Both are for the selftest."""
    if state is None or current is None:
        import runner as RN
        state = RN.STATE if state is None else state
        if current is None:
            _, specs, key = RN.regress_set()
            current = (len(specs), key)
    n_specs, vk = current
    runs = []
    for p in (state / "regression_runs").glob("*.json"):
        try:
            d = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        if d.get("versions_key") == vk:
            runs.append((str(d.get("at")), p.name, d))
    if not runs:
        return 1, f"no regression run on the current versions ({vk[:20]}…): run `runner.py regress`"
    at, name, d = max(runs)
    rows = d.get("rows") or []
    if len(rows) != n_specs:
        return 1, f"{name} judged {len(rows)} rows; the set has {n_specs}: run `runner.py regress` again"
    held = [f"{r['subject']} {r['got']}" for r in rows if r.get("unmeasured")]
    if held:
        return 1, f"{name}: {len(held)} row(s) decided nothing (a HOLD is not a pass): {held}"
    bad = [f"{r['subject']} got {r['got']}" for r in rows if not r.get("pass") and not r.get("known_miss")]
    if bad:
        return 1, f"{name}: rows fail with no open miss named: {bad}"
    recs = {}
    dec = state / "runs" / d.get("run", "") / "decisions.jsonl"
    if codes and dec.is_file():
        for line in dec.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                recs[r.get("subject")] = r
    for subj in rows_needed:
        hit = [r for r in rows if r.get("subject") == subj]
        if not hit:
            return 1, f"{name}: no regression row for {subj}"
        if not all(r.get("pass") for r in hit):
            return 1, f"{name}: {subj} row failed ({[r.get('got') for r in hit]})"
        if codes:
            seen = blocking_codes(recs.get(subj) or {})
            if not seen & codes:
                return 1, f"{name}: {subj} was refused, but on {sorted(seen) or 'no blocking code'}, none of {sorted(codes)}"
    return 0, f"{name} ({at}): {d.get('passed')}/{d.get('total')} on the current versions, the rest are named misses"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", default="", help="subjects whose rows must be present and pass")
    ap.add_argument("--codes", default="", help="each --rows subject must block on one of these codes")
    a = ap.parse_args(argv)
    try:
        rc, why = verdict([x for x in a.rows.split(",") if x], {x for x in a.codes.split(",") if x})
    except Exception as e:  # noqa: BLE001 - could not look is its own exit
        print(f"regress_holds: COULD NOT LOOK: {e}")
        return 2
    print(("HOLDS: " if rc == 0 else "DOES NOT HOLD: ") + why)
    return rc


if __name__ == "__main__":
    sys.exit(main())
