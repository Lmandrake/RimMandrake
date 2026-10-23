#!/usr/bin/env python3
"""Per-biome digest of a fauna art-eval sitting: what the judges saw, verdicts, what changed, owner candidates.

    python3 fauna_digest.py <Biome> --roster a,b,c --out Transient/art_fauna_<biome>_2026-10-23.md

Reads infrastructure/state/art_eval/runs/fauna_*/decisions.jsonl (first pass + candidate rounds),
infrastructure/state/art_eval/fauna_installs.jsonl and the head-to-head compare.json files. Paths are printed in the
owner's Windows spelling.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runner as R  # noqa: E402

ROOT = R.ROOT


def win(p) -> str:
    s = str(p)
    if s.startswith("/mnt/d/"):
        return "D:\\" + s[7:].replace("/", "\\")
    if s.startswith(str(ROOT)):
        return "D:\\Luke\\dev\\RimMandrake\\" + s[len(str(ROOT)) + 1:].replace("/", "\\") + "  (clone path " + s + ")"
    return s


def load_runs():
    recs = []
    for f in sorted((ROOT / "infrastructure/state/art_eval/runs").glob("fauna_*/decisions.jsonl")):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            r["_run"] = f.parent.name
            recs.append(r)
    return recs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("biome")
    ap.add_argument("--roster", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    roster = a.roster.split(",")
    recs = load_runs()
    installs = {}
    fi = ROOT / "infrastructure/state/art_eval/fauna_installs.jsonl"
    if fi.is_file():
        for line in fi.read_text().splitlines():
            r = json.loads(line)
            installs.setdefault(r["def"], []).append(r)
    work = R.storage_root()
    L = [f"# Fauna art digest - {a.biome} - 2026-10-23", "",
         "Judged by the art-evaluation pipeline (Opus first, GPT second look on weak, 3-round regen), then a head-to-head "
         "second opinion before any replacement. Every judgment is `delegated: art`, never owner approval. "
         "Nothing here was reviewed by the owner.", ""]
    L += ["| creature | first pass | kept art | rounds | outcome |", "|---|---|---|---|---|"]
    detail = []
    n = {"judged": 0, "accepted": 0, "regenerated": 0, "removed": 0}
    for d in roster:
        mine = [r for r in recs if r["subject"] == d]
        first = next((r for r in mine if r.get("candidate") in (None, "live")), None)
        cands = [r for r in mine if str(r.get("candidate", "")).startswith("r")]
        if not first:
            L.append(f"| {d} | not judged | | | |")
            continue
        n["judged"] += 1
        band = (first.get("opus") or {}).get("band", "-")
        ins = installs.get(d, [])
        if first["decision"] == "ACCEPT":
            out = "kept as installed (pipeline ACCEPT)"
            n["accepted"] += 1
        elif ins:
            out = f"REPLACED by regen round {ins[-1]['round']} (kept art replaced: {ins[-1]['replaced_kept']})"
            n["regenerated"] += 1
        elif first["decision"] == "HOLD_INPUT":
            out = "held: " + "; ".join(first["reasons"])[:90]
        else:
            last = cands[-1] if cands else None
            out = (f"regen filed; candidate {last['candidate']}: {last['decision']}, not installed" if last
                   else "regen filed, candidate not yet judged")
        L.append(f"| {d} | {first['decision']} ({band}) | | {len(cands)} | {out} |")
        detail.append((d, first, cands, ins))
    L += ["", f"Counts: judged {n['judged']}, accepted as installed {n['accepted']}, regenerated and installed {n['regenerated']}, "
          f"removed {n['removed']}.", "", "## What the judges saw, per creature", ""]
    for d, first, cands, ins in detail:
        card = work / "runs" / first["_run"] / d
        L.append(f"### {d}")
        L.append(f"- first pass `{first['_run']}`: {first['decision']} - " + "; ".join(first["reasons"])[:400])
        for fn in ("facings.png", "scale.png"):
            if (card / fn).is_file():
                L.append(f"  - saw `{win(card / fn)}`")
        for c in cands:
            cd = work / "runs" / c["_run"] / d
            L.append(f"- candidate {c['candidate']} `{c['_run']}`: {c['decision']} - " + "; ".join(c["reasons"])[:300])
            if (cd / "facings.png").is_file():
                L.append(f"  - saw `{win(cd / 'facings.png')}`")
            cmpf = work / "fauna_cands" / "cmp" / f"{d}_{c['candidate']}" / "compare.json"
            if cmpf.is_file():
                cj = json.loads(cmpf.read_text())
                L.append(f"  - head-to-head: winner {cj.get('winner')}, install_b {cj.get('install_b')} - {str(cj.get('reason'))[:300]}")
        for i in ins:
            L.append(f"- INSTALLED round {i['round']} ({i['at']}); revert (art ledger, kept files only restore through the card): ")
            for cmd in i["revert"]:
                L.append("  - `" + " ".join(cmd) + "`")
    Path(a.out).write_text("\n".join(L) + "\n")
    print(f"{a.out}: {n}")


if __name__ == "__main__":
    main()
