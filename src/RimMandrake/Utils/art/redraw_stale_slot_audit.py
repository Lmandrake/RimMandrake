#!/usr/bin/env python3
"""redraw_stale_slot_audit.py — audit redraw/accept slots keyed by a STALE lane (REDRAW_STALE_SLOT_KEY_AUDIT_DUPES).

The 93d799120b enact fix (ENACT_STALE_SLOT_KEY_MIGRATE_PATH) resolves or refuses a `pick` slot whose key is a lane
today's sheet no longer has (an older build's texPath). It deliberately left `redraw` and `accept` slots alone: a slot
key is hashed into the redraw job id (enact: det_id("ask", sheet, row, json(ask))), so remapping a key would file a
second job for a slot already queued. This read-only audit says, for every such slot, what that left behind:

  DUPLICATE   jobs exist under the stale key AND under the lane it resolves to today (two renders for one ask)
  MISROUTED   a job was filed under the stale key: its `slot` is a lane today's sheet does not have (its facings and
              its install target are the old path's)
  WOULD_FILE  a redraw / asks.more / asks.facings on a stale key with no job yet: an enact may file it at the old lane
              (an upper bound: cut, held and undecided rows are not excluded; confirm with an enact dry run)
  ACCEPT_OVERRIDDEN  an `accept` on a stale key while jobs redraw the lane it resolves to (his accept does not reach it)
  ACCEPT_STALE       an `accept` on a stale key, nothing redrawing its lane (harmless; listed so it is seen)

Usage: redraw_stale_slot_audit.py [--out report.md] [decisions.json ...]   (default: every *.decisions.json in the repo)
Exit 0 always for a completed audit (it reports; it does not gate); 2 on a usage error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import enact as E  # noqa: E402
import artledger as L  # noqa: E402
import decisions_v2 as DV  # noqa: E402

ASK_KINDS = ("slot", "more", "facings")


def ask_entries(v: dict, prim: str | None) -> list[dict]:
    """Every redraw-kind ask enact would build for this row, exactly as build_plan builds it (the dict is hashed into
    the job id, so its keys and values must match enact's step 3b byte for byte)."""
    dec = (DV.owner_view(v).get("decision") or "").strip()
    asks = DV.asks_of(v)
    out = []
    for g, st in (v.get("slots") or {}).items():
        if isinstance(st, dict) and not st.get("migrated") and st.get("state") == "redraw" \
                and not (g == prim and dec == "redo"):
            out.append({"kind": "slot", "slot": g, "n": 1, "base": None, "how": ""})
    for k, m in enumerate(asks.get("more") or []):
        if isinstance(m, dict):
            out.append({"kind": "more", "slot": m.get("slot") or prim, "n": max(1, min(int(m.get("n") or 1), 8)),
                        "base": m.get("base"), "how": m.get("how") or "", "k": k})
    fa = asks.get("facings")
    if isinstance(fa, dict) and fa.get("faces"):
        out.append({"kind": "facings", "slot": fa.get("slot") or prim, "n": 1, "base": fa.get("from"),
                    "how": "draw the missing facing(s) " + ", ".join(fa["faces"]), "faces": fa["faces"]})
    return out


def ask_id(sheet: str, row: str, w: dict) -> str:
    return L.det_id("ask", sheet, row, json.dumps(w, sort_keys=True))[:8]


def jobs_for(jobs: list[dict], sheet: str, row: str, w: dict) -> list[dict]:
    aid = ask_id(sheet, row, w)
    return [j for j in jobs if str(j.get("id", "")).startswith(f"enact_{aid}_")]


def row_jobs_at(jobs: list[dict], row: str, lane: str) -> list[dict]:
    """every enact job for this def whose slot is `lane` (any ask, any sheet)"""
    return [j for j in jobs if j.get("target_def") == row and j.get("slot") == lane
            and str(j.get("id", "")).startswith("enact_")]


def audit_row(sheet: str, row: str, v: dict, cur_row: dict, ruled_row: dict | None, jobs: list[dict]) -> list[dict]:
    """Findings for one decisions row. `ruled_row` is that row on the sheet he clicked on (None: not provable)."""
    lanes_now = E.lanes_of(cur_row)
    if not lanes_now:
        return []       # no lane data today: enact refuses these rows' slots by name already
    prim = cur_row.get("res")

    def resolve(g):
        if ruled_row is None:
            return None, "the sheet you clicked on cannot be read"
        return E.resolve_ruled_lane(ruled_row, cur_row, g)

    def jl(js):
        return sorted(f"{j['id']}[{j.get('_state', '?')}]" for j in js)
    out = []
    for w in ask_entries(v, prim):
        g = w.get("slot")
        if not g or g in lanes_now:
            continue
        d, why = resolve(g)
        mine = jobs_for(jobs, sheet, row, w)
        rec = {"row": row, "kind": w["kind"], "slot": g, "resolved": d, "why": why, "stale_jobs": jl(mine)}
        if mine:
            twins = [j for j in row_jobs_at(jobs, row, d) if j not in mine] if d else []
            if twins:
                out.append(rec | {"class": "DUPLICATE", "twin_jobs": jl(twins)})
            else:
                out.append(rec | {"class": "MISROUTED"})
        else:
            out.append(rec | {"class": "WOULD_FILE"})
    for g, st in (v.get("slots") or {}).items():
        if not isinstance(st, dict) or st.get("migrated") or st.get("state") != "accept" or g in lanes_now:
            continue
        d, why = resolve(g)
        over = row_jobs_at(jobs, row, d) if d else []
        out.append({"row": row, "kind": "accept", "slot": g, "resolved": d, "why": why,
                    "class": "ACCEPT_OVERRIDDEN" if over else "ACCEPT_STALE", "twin_jobs": jl(over)})
    return out


def audit_file(decisions: Path, jobs: list[dict]) -> tuple[list[dict], str]:
    """(findings, error) for one decisions file."""
    try:
        doc = json.loads(Path(decisions).read_text())
    except (OSError, ValueError) as e:
        return [], f"unreadable: {type(e).__name__}"
    if not isinstance(doc, dict) or not isinstance(doc.get("snapshot"), str) or not doc["snapshot"].strip():
        return [], "names no snapshot"
    snap_path = Path(doc["snapshot"])
    if not snap_path.is_absolute():
        snap_path = L.REPO_ROOT / snap_path
    if not snap_path.is_file():
        return [], f"snapshot missing: {doc['snapshot']}"
    try:
        snap = json.loads(snap_path.read_text())
    except (OSError, ValueError):
        return [], "snapshot unreadable"
    sheet = doc.get("sheetId") or snap.get("sheetId") or Path(decisions).stem
    rows = snap.get("rows") or {}
    out = []
    for row, v in (doc.get("decisions") or {}).items():
        if not isinstance(v, dict) or not v.get("at"):
            continue
        cur_row = rows.get(row) or {}
        lanes_now = E.lanes_of(cur_row)
        keys = {w.get("slot") for w in ask_entries(v, cur_row.get("res"))} | \
               {g for g, st in (v.get("slots") or {}).items() if isinstance(st, dict) and st.get("state") == "accept"}
        if not lanes_now or not (keys - lanes_now - {None}):
            continue        # nothing stale on this row: never read git
        ruled, _why = E.ruled_snapshot(snap_path, snap, v.get("decidedAt") or v.get("at"))
        rrow = ((ruled or {}).get("rows") or {}).get(row) if ruled else None
        for f in audit_row(sheet, row, v, cur_row, rrow, jobs):
            out.append(f | {"decisions": str(decisions)})
    return out, ""


def default_files() -> list[Path]:
    root = L.REPO_ROOT
    return sorted(p for p in root.rglob("*.decisions.json") if ".git" not in p.parts)


def report(findings: list[dict], errors: dict, n_files: int) -> str:
    by = {}
    for f in findings:
        by.setdefault(f["class"], []).append(f)
    L_ = [f"# Redraw/accept slots keyed by a stale lane — audit (REDRAW_STALE_SLOT_KEY_AUDIT_DUPES)", "",
          f"decisions files read: {n_files}; unreadable or without a snapshot: {len(errors)}", "",
          "| class | count |", "|---|---|"]
    for c in ("DUPLICATE", "MISROUTED", "WOULD_FILE", "ACCEPT_OVERRIDDEN", "ACCEPT_STALE"):
        L_.append(f"| {c} | {len(by.get(c, []))} |")
    L_.append("")
    for c, fs in by.items():
        L_.append(f"## {c}")
        for f in fs:
            L_.append(f"- `{f['decisions']}` {f['row']} {f['kind']} slot `{f['slot']}` -> "
                      f"{f['resolved'] or 'unresolved (' + f['why'] + ')'}"
                      + (f"; stale jobs {', '.join(f['stale_jobs'])}" if f.get("stale_jobs") else "")
                      + (f"; twin jobs {', '.join(f['twin_jobs'])}" if f.get("twin_jobs") else ""))
        L_.append("")
    if errors:
        L_.append("## files not audited")
        L_ += [f"- `{k}`: {e}" for k, e in sorted(errors.items())]
    return "\n".join(L_) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    files = [Path(f) for f in a.files] or default_files()
    jobs = E.load_jobs()
    findings, errors = [], {}
    for f in files:
        fs, err = audit_file(f, jobs)
        findings += fs
        if err:
            errors[str(f)] = err
    text = report(findings, errors, len(files))
    if a.out:
        Path(a.out).write_text(text)
        print(f"wrote {a.out}: {len(findings)} finding(s) over {len(files)} file(s)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
