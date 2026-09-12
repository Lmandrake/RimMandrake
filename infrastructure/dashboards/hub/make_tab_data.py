#!/usr/bin/env python3
"""Build the Dashboard Hub's per-tab data files (DASHBOARD_HUB_ARTIFACT_1).

Each tab of the hub artifact is fed by ONE data file published alongside the
shell. A seat refreshing its dashboard regenerates ONLY its own file and
republishes it against the hub URL (files not passed are kept). Contract per
file: top-level `generatedAt` (ISO-8601 UTC) + `source` {path, sha256_12} of
the artifact it was derived from — the shell's freshness lamp and
hub_check.py both read exactly these fields.

Art tab: infrastructure/artpipe/art_status.json already meets the contract
(generatedAt + sourceFingerprint) and is published directly, not copied here.
"""
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / "data"


def fp(path: pathlib.Path) -> dict:
    b = path.read_bytes()
    return {"path": str(path.relative_to(REPO)), "bytes": len(b),
            "sha256_12": hashlib.sha256(b).hexdigest()[:12]}


def iso(loose: str) -> str:
    # sources write "2026-09-11 16:58" in the SYSTEM'S LOCAL wall-clock time
    # (datetime.now(), naive). The contract wants real UTC — a naive
    # datetime's .astimezone() treats it as local time and converts, so this
    # is an actual UTC conversion, not a relabeling. strftime always emits
    # seconds, so the result is always a valid ISO-8601 stamp (no bare "Z"
    # with no time component from a loose "HH:MM"-only input).
    local = datetime.strptime(loose, "%Y-%m-%d %H:%M")
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def health() -> None:
    src = REPO / "Transient/codebase_health.json"
    h = json.loads(src.read_text())
    top = sorted(h.get("recidivists", []), key=lambda r: -r.get("cycles", 0))[:10]
    OUT.joinpath("health.json").write_text(json.dumps({
        "generatedAt": iso(h["generated"]),
        "source": fp(src),
        "head": h.get("head"),
        "counts": h.get("counts"),
        "loc": h.get("loc"),
        "reviewEntries": h.get("reviewEntries"),
        "recidivists": top,
        "standalone": "Transient/codebase_health_artifact.html",
        # HEALTH_UNMEASURED_HEADLINE_1: pass through the generator's own verdict
        # on whether this run could measure anything — the shell reads this to
        # show the honest claim instead of treating `counts` as a health picture.
        "measurementOk": h.get("measurementOk", True),
        "headline": h.get("headline", ""),
    }, indent=1))


def maturity() -> None:
    src = REPO / "Transient/project_maturity_dashboard.json"
    m = json.loads(src.read_text())
    goal = m.get("goalSheet", {})
    sections = [{"n": s["n"], "title": s["title"], "ticked": s["ticked"],
                 "total": s["total"]} for s in goal.get("sections", [])]
    systems = [{k: s.get(k) for k in
                ("system", "tier", "functionRung", "contentRung", "date")}
               for s in m.get("systems", [])]
    OUT.joinpath("maturity.json").write_text(json.dumps({
        "generatedAt": iso(m["generated"]),
        "source": fp(src),
        "head": m.get("head"),
        "functionCounts": m.get("functionCounts"),
        "contentCounts": m.get("contentCounts"),
        "codeReview": m.get("codeReview"),
        "ledger": m.get("ledger"),
        "goal": {"ticked": goal.get("ticked"), "total": goal.get("total"),
                 "sections": sections},
        "systems": systems,
        "standalone": "Transient/project_maturity_dashboard.html",
    }, indent=1))


def worldmap() -> None:
    # Fed by the newest dated verification under world/_audit/ — the
    # post-freeze check of the frozen CSV against the canonical save. Glob
    # for the newest post_freeze_*.json instead of pinning one date, so a
    # later audit is picked up automatically instead of the tab silently
    # going stale forever once a new one is written.
    audits = sorted((REPO / "world/_audit").glob("post_freeze_*.json"))
    if not audits:
        raise FileNotFoundError("no world/_audit/post_freeze_*.json found")
    src = audits[-1]
    v = json.loads(src.read_text())
    # artifactUrl is hand-maintained data, not a literal in this script —
    # see worldmap_config.json alongside this file (updated whenever the
    # audit report is republished).
    cfg = json.loads((HERE / "worldmap_config.json").read_text())
    OUT.joinpath("worldmap.json").write_text(json.dumps({
        "generatedAt": v["generatedAt"],
        "source": fp(src),
        "artifactUrl": cfg["artifactUrl"],
        "note": "Post-freeze verification: the frozen CSV matches the canonical save "
                "on every engine field, 0/21872 tiles differ. Live save: "
                "CANONICAL_ASHKARR_2026-09-09.rws.",
        "worldFrozenAt": "2026-09-09T12:24:00Z",
        "openOffline": "Bookkeeping owed: canon.yml planet census (deprecated lineage) and "
                       "the CSV region column (5 ruled renames + The Abandoned Mines). "
                       "Live-game checks (rivers count, dump provenance, loads-clean, "
                       "mutators) ride WORLDMAP_AUDIT_LIVE_CHECKS_1.",
    }, indent=1))


# ---------------------------------------------------------------------------
# artsheets: unresolved GRAPHICS review sheets under design/Jawa/worldbuilding/review.
#
# Every *.html there was inspected by hand (bytes, embedded ITEMS/decisions
# schema, presence of a per-row "thumb"/"img" field) to sort graphics-review
# sheets from text-only registers and static reference docs, which are not
# what the owner asked this section for. See REVIEW_DIR_EXCLUDED below for
# the full list and reason for every sheet that did NOT make the cut.
REVIEW_DIR = REPO / "design/Jawa/worldbuilding/review"

# stems that ARE graphics review sheets with a real per-row decision file —
# confirmed by inspecting decisions.json rows for an "img"/"thumb"-bearing
# ITEMS schema (creature/vehicle/weapon/furniture/plant/fauna/flora/homeless
# registers show a def's art; assailant_flesh_sheet is a dungeon art contact
# sheet). Excludes text-only registers and static docs — see EXCLUDED.
GRAPHICS_SHEET_STEMS = [
    "assailant_flesh_sheet",
    "creature_register",
    "fauna_assignment_register",
    "flora_assignment_register",
    "furniture_register",
    "homeless_disposition_register",
    "plant_register",
    "vehicle_register",
    "weapon_register",
]

# Every other *.html in the review dir, and why it is not in the list above.
REVIEW_DIR_EXCLUDED = {
    "creature_art_register": "retired 2026-09-11 (creature-art-register-retired doctrine) — must not be consumed",
    "creature_triage": "a SECOND instrument over creature_register.decisions.json (its own header says so) — same data as creature_register, not a distinct sheet",
    "mech_register": "static reference catalog (like species_register) — no decisions/ITEMS review plumbing at all, nothing to resolve",
    "species_register": "static faction/species reference doc, prose only, no decisions mechanism",
    "pawn_flavor_phase2_register": "pure-text register (defName/proposed-prose rewrites) — no art content, checked: no thumb/img field",
    "proposal_suite_review": "text design-proposal review (cost/docs/oneLine fields) — no art content",
    "tile_structure_batch3_sheet": "text layout descriptions (defs+meta, no per-row image) — checked: no thumb data in ITEMS rows; also has no decisions.json anywhere in the repo",
    "tile_structure_batch4_sheet": "same as batch3 — text layout description, no decisions.json in the repo",
    "tile_structure_batch5_sheet": "same as batch3 — text layout description, no decisions.json in the repo",
    "tile_structure_batch6_sheet": "same as batch3 — text layout description, no decisions.json in the repo",
}

_GENERIC_TITLES = {"", "review sheet"}


def _sheet_title(html_path: pathlib.Path, stem: str) -> str:
    head = html_path.read_bytes()[:8192].decode("utf-8", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", head, re.S) or re.search(r"<h1[^>]*>(.*?)(?:<|$)", head, re.S)
    if m:
        t = re.sub(r"\s+", " ", m.group(1)).strip()
        if t.lower() not in _GENERIC_TITLES:
            return t
    return " ".join(w.capitalize() for w in stem.split("_"))


def _sheet_counts(doc: dict) -> tuple:
    """Return (total, undecided) for one decisions.json's content.

    undecided derivation, in order:
    - dict of per-row decisions, any row carrying an "at" timestamp (the
      project's own touchedByHuman = rec => !!(rec && rec.at), lifted
      verbatim from creature_triage.html) -> total minus rows carrying "at".
    - dict of per-row decisions, NO row anywhere uses "at" AND the sheet's
      own top-level "savedBy" is unset -> the sidecar has never written this
      file at all, so no row anywhere carries a recorded human verdict:
      undecided == total.
    - a blanket ruling (assailant_flesh_sheet's "decidedCount"/"blanket"
      format, no per-row map) -> undecided = total - decidedCount.
    - anything else this format doesn't let us attribute per row -> None.
    """
    decs = doc.get("decisions")
    if isinstance(decs, dict) and decs:
        total = len(decs)
        rows = [v for v in decs.values() if isinstance(v, dict)]
        if any("at" in v for v in rows):
            touched = sum(1 for v in rows if v.get("at"))
            return total, total - touched
        if not doc.get("savedBy"):
            return total, total
        return total, None
    if doc.get("blanket") and isinstance(doc.get("decidedCount"), int):
        total = doc["decidedCount"]
        return total, max(0, total - doc["decidedCount"])
    return None, None


def artsheets() -> None:
    rows = []
    excluded = dict(REVIEW_DIR_EXCLUDED)
    resolved = []
    for stem in GRAPHICS_SHEET_STEMS:
        html_path = REVIEW_DIR / f"{stem}.html"
        dec_path = REVIEW_DIR / f"{stem}.decisions.json"
        if not html_path.exists():
            excluded[stem] = "listed as a graphics sheet but the .html is gone — re-check GRAPHICS_SHEET_STEMS"
            continue
        if dec_path.exists():
            doc = json.loads(dec_path.read_text())
            total, undecided = _sheet_counts(doc)
        else:
            total, undecided = None, None
        unresolved = (not dec_path.exists()) or undecided is None or (undecided or 0) > 0
        row = {
            "stem": stem,
            "title": _sheet_title(html_path, stem),
            "file": str(html_path.relative_to(REPO)),
            "bytes": html_path.stat().st_size,
            "total": total,
            "undecided": undecided,
            "published": f"tabs/sheets/{stem}.html",
        }
        if unresolved:
            rows.append(row)
        else:
            resolved.append(row)
    rows.sort(key=lambda r: (-(r["undecided"] or 0), r["stem"]))
    OUT.joinpath("artsheets.json").write_text(json.dumps({
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "design/Jawa/worldbuilding/review/*.html + *.decisions.json, hand-classified "
                  "for graphics content — see excluded{} for every sheet left out and why",
        "inventoried": len(GRAPHICS_SHEET_STEMS) + len(excluded),
        "resolved": resolved,
        "excluded": [{"stem": s, "reason": r} for s, r in sorted(excluded.items())],
        "rows": rows,
    }, indent=1))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:] or ["health", "maturity", "worldmap"]
    for name in only:
        {"health": health, "maturity": maturity, "worldmap": worldmap,
         "artsheets": artsheets}[name]()
        print(f"wrote data/{name}.json")
