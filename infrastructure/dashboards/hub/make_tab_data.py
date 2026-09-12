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
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "data"


def fp(path: pathlib.Path) -> dict:
    b = path.read_bytes()
    return {"path": str(path.relative_to(REPO)), "bytes": len(b),
            "sha256_12": hashlib.sha256(b).hexdigest()[:12]}


def iso(loose: str) -> str:
    # sources write "2026-09-11 16:58"; the contract wants ISO UTC (local
    # clock — the sources stamp local time, good enough for age lamps)
    return loose.replace(" ", "T") + (":00Z" if loose.count(":") == 1 else "Z")


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
    # post-freeze check of the frozen CSV against the canonical save.
    src = REPO / "world/_audit/post_freeze_2026-09-11.json"
    v = json.loads(src.read_text())
    OUT.joinpath("worldmap.json").write_text(json.dumps({
        "generatedAt": v["generatedAt"],
        "source": fp(src),
        "artifactUrl": "https://claude.ai/code/artifact/f8b14a7a-b8ed-4787-8104-b055ebf2f45c",
        "note": "Post-freeze verification: the frozen CSV matches the canonical save "
                "on every engine field, 0/21872 tiles differ. Live save: "
                "CANONICAL_ASHKARR_2026-09-09.rws.",
        "worldFrozenAt": "2026-09-09T12:24:00Z",
        "openOffline": "Bookkeeping owed: canon.yml planet census (deprecated lineage) and "
                       "the CSV region column (5 ruled renames + The Abandoned Mines). "
                       "Live-game checks (rivers count, dump provenance, loads-clean, "
                       "mutators) ride WORLDMAP_AUDIT_LIVE_CHECKS_1.",
    }, indent=1))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:] or ["health", "maturity", "worldmap"]
    for name in only:
        {"health": health, "maturity": maturity, "worldmap": worldmap}[name]()
        print(f"wrote data/{name}.json")
