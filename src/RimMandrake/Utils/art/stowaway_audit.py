#!/usr/bin/env python3
"""stowaway_audit — prove a foreign-copy artpipe output reached no creature (ARTEVAL_CROPPED_COPIES_AUDIT_TWO_STOWAWAYS).

A "stowaway" is an artpipe output that is really an unrelated render (a centre-square crop of another job's image,
found by FOREIGN_GUARD_WIDEN_MIRROR_CROP). For each one this walks every consumer the repo records and fails when
the bad bytes can still reach the creature:

  ledger   the sha is purged AND banned (so no sheet offers it and no install takes it)
  live     no live slot in the art ledger, and no PNG under src/**/Textures, holds the sha
  rulings  no owner keep targets the sha
  eval     every art_eval decision that judged it is listed; none is an ACCEPT
  sheets   every sheet snapshot column showing it is listed; no sheet's pick resolves to that column

Exit 0 every check holds, 1 one fails, 2 UNMEASURED (an instrument saw nothing it should have seen).
Read-only. Usage: stowaway_audit.py [--item ARTEVAL_CROPPED_COPIES_AUDIT_TWO_STOWAWAYS]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

REPO = L.REPO_ROOT

# item -> [(job, sha256, subject)]; the shas are the job's variant events in the art ledger
STOWAWAYS = {
    "ARTEVAL_CROPPED_COPIES_AUDIT_TWO_STOWAWAYS": [
        ("arteval_RM_Dustflutter_r1_east",
         "35a568db803f3f77212ccc753959e742ed4f2b4b4af6b98942bde50053e0029d", "RM_Dustflutter"),
        ("arteval_RM_Peeper_r3_south",
         "6ea0411c0f4d290ccc196cb5f3ace0cc9da5976f37e504cd0d9264035f93e52b", "RM_Peeper"),
    ],
}


def _decisions_for(sheet_id: str) -> list[Path]:
    return sorted(p for p in (REPO / "Transient").rglob(f"{sheet_id}.decisions.json")
                  if "decisions_snapshot" not in str(p) and "premigration" not in str(p))


def _walk_strings(o, path=()):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from _walk_strings(v, path + (str(k),))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk_strings(v, path + (str(i),))
    elif isinstance(o, str):
        yield path, o


def audit(item: str) -> tuple[int, list[str]]:
    out, bad, blind = [], 0, 0
    idx = L.Index()
    if not idx.variants:
        return 2, ["UNMEASURED: the art ledger folded no variants"]
    rows = STOWAWAYS[item]
    shas = {s for _, s, _ in rows}

    for job, sha, subj in rows:
        out.append(f"== {job} {sha[:16]} ({subj})")
        if sha not in idx.variants:
            blind += 1
            out.append("  UNMEASURED ledger: no variant event carries this sha (wrong sha?)")
        jobs = {v.get("job") for v in idx.variants.get(sha, [])}
        out.append(f"  variant jobs: {sorted(j for j in jobs if j)}")
        ok_p, ok_b = idx.is_purged(sha), sha in idx.bans
        out.append(f"  ledger: purged={ok_p} banned={ok_b} (ban subject {(idx.bans.get(sha) or {}).get('subject')})")
        bad += (not ok_p) + (not ok_b)
        live = [k for k, ev in idx.live.items() if ev.get("sha") == sha]
        out.append(f"  live slots holding it: {live or 'none'}")
        bad += bool(live)
        keeps = [r["id"] for r in idx.rulings_by_sha.get(sha, []) if L.normalise_verdict(r.get("verdict", "")) == "keep"]
        out.append(f"  owner keeps on it: {keeps or 'none'}")
        bad += bool(keeps)

    # src textures: hash every PNG under the subjects' texture folders, plus a whole-tree sweep for the two shas
    pngs = list((REPO / "src").rglob("Textures/**/*.png"))
    if len(pngs) < 100:
        blind += 1
        out.append(f"UNMEASURED src: only {len(pngs)} PNGs under src/**/Textures")
    hits = [str(p.relative_to(REPO)) for p in pngs if hashlib.sha256(p.read_bytes()).hexdigest() in shas]
    out.append(f"src/**/Textures: {len(pngs)} PNGs hashed, holding a stowaway: {hits or 'none'}")
    bad += len(hits)

    # art_eval decisions that judged either picture
    runs = sorted((REPO / "infrastructure/state/art_eval/runs").glob("*/decisions.jsonl"))
    if not runs:
        blind += 1
        out.append("UNMEASURED eval: no art_eval run decisions found")
    n_eval = 0
    for f in runs:
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            seen = set((d.get("image_sha256") or {}).values()) | set((d.get("source_sha256") or {}).values())
            if seen & shas:
                n_eval += 1
                dropped = d.get("owner_packet_dropped")
                out.append(f"  eval {f.parent.name}: {d.get('subject')} {d.get('candidate')} -> {d.get('decision')}"
                           + (f" (owner packet dropped {dropped.get('faces')}: {dropped.get('why')})" if dropped else ""))
                bad += d.get("decision") == "ACCEPT"
    out.append(f"eval decisions that judged a stowaway: {n_eval} (an ACCEPT among them fails)")

    # sheets: snapshot columns showing either picture, and whether that column is the sheet's pick
    snaps = sorted((REPO / "infrastructure/state/art/sheets").glob("*.snapshot.json"))
    if not snaps:
        blind += 1
        out.append("UNMEASURED sheets: no sheet snapshots found")
    n_col = 0
    for sp in snaps:
        text = sp.read_text(encoding="utf-8")
        if not any(s in text for s in shas):
            continue
        snap = json.loads(text)
        cols = set()
        for path, s in _walk_strings(snap):
            if s in shas and len(path) >= 4 and path[0] == "rows" and path[2] == "columns":
                cols.add((path[1], path[3]))
        sheet_id = sp.name[: -len(".snapshot.json")]
        decs = _decisions_for(sheet_id)
        for row, col in sorted(cols):
            n_col += 1
            picks = []
            for dp in decs:
                dec = (json.loads(dp.read_text(encoding="utf-8")).get("decisions") or {}).get(row) or {}
                picks.append(dec.get("decision"))
            picked = col in picks
            out.append(f"  sheet {sheet_id} row {row} column {col}: picks {picks or 'no decisions file'}"
                       f"{'  <-- PICKED' if picked else ''}")
            bad += picked
    out.append(f"sheet columns showing a stowaway: {n_col} (now never offered: purged+banned)")

    if bad:
        return 1, out + [f"FAIL: {bad} consumer(s) still carry a stowaway"]
    if blind:
        return 2, out + [f"UNMEASURED: {blind} instrument(s) saw nothing"]
    return 0, out + ["PASS: neither stowaway reaches its creature; every consumer listed above"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--item", default="ARTEVAL_CROPPED_COPIES_AUDIT_TWO_STOWAWAYS", choices=sorted(STOWAWAYS))
    a = ap.parse_args(argv)
    code, lines = audit(a.item)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
