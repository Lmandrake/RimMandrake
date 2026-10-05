#!/usr/bin/env python3
"""ingest.py — an art compare sheet's decisions file -> owner ruling / purge events.

Rules (design §3, owner rulings 2026-10-04):
  * The file must carry the sidecar's plumbing stamp (`savedBy` + `writeCount`) or a
    `reviewStatus.state == "ruled"`. A file only a generator wrote is the agent's guess.
  * ONLY rows the owner touched (an `at` stamp) become rulings. An untouched prefill is
    never a ruling, even on a ruled sheet.
  * A column decision resolves through the sheet's SNAPSHOT (row -> column -> facing -> sha)
    written at generation time, so a regenerated column cannot be approved under an old label.
  * Each row may carry `purge: [sha...]` — the owner's reject+purge. A purge of a live
    picture is refused (counted, reported); everything else is deleted from the store.
  * Nothing is installed. Installing is `art.py install`, a separate step.
"""
from __future__ import annotations

import json
from pathlib import Path

import artledger as L


def ingest(decisions_path: Path, dry_run: bool = False) -> dict:
    doc = json.loads(Path(decisions_path).read_text())
    rs = doc.get("reviewStatus") if isinstance(doc.get("reviewStatus"), dict) else {}
    plumbed = bool(doc.get("savedBy")) and int(doc.get("writeCount") or 0) > 0
    if not plumbed and rs.get("state") != "ruled":
        return {"ok": False, "error": "no sidecar plumbing stamp and reviewStatus is not 'ruled' — "
                                      "this is still the generator's prefill; nothing ingested"}
    snap_path = Path(doc.get("snapshot") or "")
    if not snap_path.is_absolute():
        snap_path = L.REPO_ROOT / snap_path
    if not snap_path.is_file():
        return {"ok": False, "error": f"snapshot {snap_path} missing — cannot resolve columns to pictures"}
    snap = json.loads(snap_path.read_text())
    if doc.get("snapshotId") and snap.get("snapshotId") and doc["snapshotId"] != snap["snapshotId"]:
        return {"ok": False, "error": "decisions were made against a different snapshot of this sheet"}
    idx = L.Index()
    w = L.Writer({e["id"] for e in idx.events})
    via = str(decisions_path)
    out = {"ok": True, "rulings": 0, "purged": 0, "purge_refused": 0, "untouched": 0, "unresolved": []}
    for row, v in (doc.get("decisions") or {}).items():
        if not isinstance(v, dict):
            continue
        if not v.get("at"):
            out["untouched"] += 1
            continue
        # A row touched only to purge never turns its prefill into a ruling: the page stamps
        # decidedAt on a real decision click; purgeTouched marks a purge-only touch.
        decided = bool(v.get("decidedAt")) or not v.get("purgeTouched")
        srow = (snap.get("rows") or {}).get(row)
        dec = (v.get("decision") or "").strip()
        note = (v.get("note") or "").strip()
        cols = (srow or {}).get("columns") or {}
        if dec and srow and decided:
            if dec in cols:
                shas = sorted({s for s in cols[dec].values() if s})
                ev = {"type": "ruling", "id": L.det_id("ruling-sheet", via, row, dec, v.get("at")),
                      "target": {"shas": shas, "column": dec, "row": row}, "verdict": "keep", "by": "owner",
                      "said": note, "note": note, "at": v.get("at"), "trust": "ruled", "via": via,
                      "subject_key": srow.get("subject_key", ""), "source_file": via,
                      "evidence": "sidecar savedBy/writeCount" if plumbed else "reviewStatus ruled"}
            else:
                ev = {"type": "ruling", "id": L.det_id("ruling-sheet", via, row, dec, v.get("at")),
                      "target": {"row": row, "subject_key": srow.get("subject_key", "")},
                      "verdict": L.normalise_verdict(dec), "raw_verdict": dec, "by": "owner", "said": note,
                      "note": note, "at": v.get("at"), "trust": "ruled", "via": via,
                      "subject_key": srow.get("subject_key", ""), "source_file": via}
            if not dry_run and w.add(ev):
                out["rulings"] += 1
            # per-biome sheets: a row's extra graphics (swimming, flying …) carry their own pick
            for g, pl in sorted((v.get("picks") or {}).items()):
                if pl in cols and pl != dec:
                    pev = {**ev, "id": L.det_id("ruling-sheet", via, row, pl, v.get("at")), "verdict": "keep",
                           "target": {"shas": sorted({s for s in cols[pl].values() if s}), "column": pl,
                                      "row": row, "graphic": g}}
                    pev.pop("raw_verdict", None)
                    if not dry_run and w.add(pev):
                        out["rulings"] += 1
        # kept variants: extra columns the owner marked as valid in-game variants of the pick
        if srow and decided:
            for vl in sorted(set(v.get("variants") or [])):
                if vl in cols and vl != dec:
                    vev = {"type": "ruling", "id": L.det_id("ruling-sheet", via, row, vl, v.get("variantsAt") or v.get("at")),
                           "target": {"shas": sorted({s for s in cols[vl].values() if s}), "column": vl,
                                      "row": row, "variant_of": dec},
                           "verdict": "keep", "by": "owner", "said": note, "note": note,
                           "at": v.get("variantsAt") or v.get("at"), "trust": "ruled", "via": via,
                           "subject_key": srow.get("subject_key", ""), "source_file": via,
                           "evidence": "sidecar savedBy/writeCount" if plumbed else "reviewStatus ruled"}
                    if not dry_run and w.add(vev):
                        out["rulings"] += 1
        if dec and decided and not (srow and dec):
            out["unresolved"].append(row)
        for sha in v.get("purge") or []:
            if dry_run:
                continue
            w.flush()
            try:
                L.purge(sha, owner_said=note or f"reject+purge on sheet {snap.get('sheetId')}",
                        via=via, release_keep=True)
                out["purged"] += 1
            except L.Refused as e:
                out["purge_refused"] += 1
                out.setdefault("refusals", []).append(f"{sha[:12]}: {e}")
            w = L.Writer()
    w.flush()
    return out
