#!/usr/bin/env python3
"""Fold the owner's 66-row conflict sheet (sheet_conflicts_review_2026-10-09) back into the per-biome decisions
files, so `art.py enact <file>` carries each choice out. One-off; every touched row gets a `conflictSheet`
provenance record (what it was, what he chose, click or default).

Owner, typed 2026-10-09 ~17:5x PDT: "I have just finished that sheet. Every choice was deliberated. Anything
"not selected" is left as the default. Use them all and go now. Use your efficient sheet script."
=> clicked rows use `decision`, unclicked rows use the sheet's `prefill`.

    python3 Transient/sheet_conflicts_enact_fold_2026-10-09.py [--apply]
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = "sheet_conflicts_review_2026-10-09"

# ── what each (kind, choice) does to the ORIGINAL row ────────────────────────────────────────────────────────────
# Rows whose pick already ships through a port def's own slot (the follow-up renders his notes ordered are live
# there): the raw pick must NOT be installed over them; it is kept as a reference only.
PORTED = {"AA_CrepuscularBeetle": "RM_Moravatha", "AA_DarkVandal": "RM_Ossumatha", "AA_DuskProwler": "RM_Ysvaltha",
          "AA_Murkling": "RM_Lirrith", "AA_NightRam": "RM_Olumetha", "AB_GlowingGrass": "RM_GlowingGrass",
          "AA_Nightling": "RM_Sesserith"}
# Rows whose follow-through is done OUTSIDE the file (an install that creates/fills the slot, a job, a purge): the
# file keeps his letters; enact sees the result (installed_already / a later job covering the facing).
SIDE_ONLY = {"del:B", "failed:A", "kept:B", "noslot:A:RM_HoardVenomvine", "noslot:A:AA_Mantrap"}
OWNER_QUESTIONS = {"tier:A"}       # Great Devourer: default A contradicts his later 2026-10-08 card (RM_Gulloth)


def load(p):
    return json.loads((ROOT / p).read_text())


def write_atomic(path: Path, doc: dict, raw_before: bytes):
    payload = (json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".fold-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        if path.read_bytes() != raw_before:
            raise SystemExit(f"{path} changed under us — re-run")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main(argv):
    apply = "--apply" in argv
    html = (ROOT / f"Transient/{SHEET}.html").read_text()
    items = json.loads(re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', html, re.S).group(1))
    items = items if isinstance(items, list) else items["items"]
    dec = load(f"Transient/{SHEET}.decisions.json")
    maps = load(f"Transient/{SHEET}.map.json")["maps"]
    saved_at = dec.get("savedAt")
    by_file: dict[str, list] = {}
    for it in items:
        r = (dec["decisions"] or {}).get(it["id"]) or {}
        clicked = bool(r.get("decidedAt"))
        choice = r["decision"] if clicked else it.get("prefill")
        m = maps[it["id"]]
        by_file.setdefault(m["decisionsFile"], []).append(
            {"id": it["id"], "m": m, "choice": choice, "src": "click" if clicked else "default",
             "note": (r.get("note") or "").strip(), "when": r.get("decidedAt") or saved_at})
    report = []
    for f, rows in sorted(by_file.items()):
        path = ROOT / f
        raw = path.read_bytes()
        doc = json.loads(raw)
        snap = json.loads((ROOT / doc["snapshot"]).read_text()) if doc.get("snapshot") else {}
        changed = False
        for x in rows:
            m, choice, row = x["m"], x["choice"], x["m"]["row"]
            kind = m["kind"]
            v = doc["decisions"].get(row)
            if v is None:
                report.append(f"MISSING ROW {f} {row}")
                continue
            was = {k: v.get(k) for k in ("decision", "picks", "variants", "note", "at")}
            key = f"{kind}:{choice}"
            act = None
            if key in OWNER_QUESTIONS:
                act = "owner question — not folded"
            elif key in SIDE_ONLY or f"{key}:{row}" in SIDE_ONLY:
                act = "side action (install/job/purge) — letters unchanged"
            elif kind == "del" and choice == "A":
                drop = {s for line in m["conflictLines"] for s in re.findall(r"✕ ([0-9a-f]{12})", line)}
                before = list(v.get("purge") or [])
                v["purge"] = [s for s in before if s[:12] not in drop]
                act = f"drop the delete: {len(before) - len(v['purge'])} ✕ removed, kept"
            elif kind == "amb" and choice == "A":
                if row in PORTED:
                    v["reference_picks"] = {"decision": v.get("decision"), "picks": v.get("picks")}
                    v["picks"] = {g: l for g, l in (v.get("picks") or {}).items() if g != "_byname"}
                    v["decision"] = ""
                    act = f"pick ships as its note-follow-up at {PORTED[row]} (live); raw pick kept as reference"
                else:
                    main = (snap.get("rows") or {}).get(row, {}).get("res")
                    picks = dict(v.get("picks") or {})
                    letter = m["A"].get("letter") or picks.get("_byname")
                    picks.pop("_byname", None)
                    picks[main] = letter
                    v["picks"] = picks
                    act = f"column {letter} -> main graphic {main}"
            elif kind == "amb" and choice == "other":            # Shadow Charger "broken?": the row was CUT
                v["decision"] = "cut"
                act = "row is cut (his 2026-10-06 'Cut this.'); pick moot"
            elif kind in ("stale",) and choice in ("B", "other"):
                v["stale_letters_dropped"] = {"decision": v.get("decision"), "picks": v.get("picks"),
                                              "variants": v.get("variants")}
                v["decision"], v["picks"], v["variants"] = "", {}, []
                act = "leave the current art: unverifiable letters dropped"
            elif kind == "noslot" and choice == "A" and row in PORTED:
                v["reference_picks"] = {"decision": v.get("decision"), "picks": v.get("picks")}
                v["decision"], v["picks"] = "", {}
                act = f"pick ships as its note-follow-up at {PORTED[row]} (live); raw pick kept as reference"
            elif kind == "note" and choice == "A":
                if row == "RM_ContagionIkee":
                    act = "note followed by the kept row (A: keep his restored art) — --mark-done"
                else:
                    v["decision"] = "redo"
                    v["at"] = x["when"]
                    act = "queue a redraw following the note"
            elif kind == "kept" and choice == "A":
                v["reference_picks"] = {"decision": v.get("decision"), "picks": v.get("picks")}
                v["decision"] = ""
                v["picks"] = {g: l for g, l in (v.get("picks") or {}).items() if g != "_byname"}
                act = "keep the protected current picture; row pick withdrawn"
            elif kind in ("kept", "purgedpick") and choice == "other":     # Maulith / Readerbloom: regen
                v["decision"] = "redo"
                v["note"] = x["note"]
                v["at"] = x["when"]
                act = f"redo with his note {x['note']!r}"
            elif kind == "purgedpick" and choice == "A":
                letter = m["A"].get("letter")
                v["reference_picks"] = {"decision": v.get("decision"), "picks": v.get("picks")}
                v["decision"] = letter
                act = f"pick column {letter} instead"
            else:
                act = f"UNHANDLED {key}"
            if not act.startswith(("owner question", "side action", "note followed")) and not act.startswith("UNH"):
                changed = True
            v.setdefault("conflictSheet", []).append(
                {"sheet": SHEET, "item": x["id"], "kind": kind, "choice": choice, "by": x["src"],
                 "note": x["note"], "when": x["when"], "action": act, "was": was})
            changed = True
            report.append(f"{x['id']:52} {kind:10} {choice:5} {x['src']:7} {act}")
        if changed and apply:
            write_atomic(path, doc, raw)
    print("\n".join(report))
    print(f"{'APPLIED' if apply else 'DRY RUN'}: {sum(len(r) for r in by_file.values())} rows, {len(by_file)} files")


if __name__ == "__main__":
    main(sys.argv[1:])
