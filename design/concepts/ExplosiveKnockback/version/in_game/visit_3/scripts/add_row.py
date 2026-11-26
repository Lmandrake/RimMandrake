#!/usr/bin/env python3
"""Append one run row to visit_3/rows.jsonl for a check run outside batch.py (an owed case, a two-step command).

    python3 .../add_row.py TEST VERDICT OUTCOME --command "..." --log <captured output> [--note "..."] [--env ident_tier.json]

The captured output is copied to evidence/<TEST>.txt (CR stripped); the identity file (build_match.py identity, one per
deploy) is merged into the row, as batch.py does. VERDICT and OUTCOME are the caller's reading of the scene's own verdict
lines: PASS goes with SUCCESS, FAIL with MOD FAILURE, every other outcome with UNMEASURED."""
import argparse, datetime, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); VISIT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("test"); ap.add_argument("verdict", choices=["PASS", "FAIL", "UNMEASURED"]); ap.add_argument("outcome")
ap.add_argument("--command", required=True); ap.add_argument("--log", required=True); ap.add_argument("--note", default="")
ap.add_argument("--env", default="ident_tier.json"); ap.add_argument("--extra", default="{}", help="JSON merged into the row last (repair, class, spoiled_by, ...)"); ap.add_argument("--suffix", default="")
a = ap.parse_args()
if (a.verdict == "PASS") != (a.outcome == "SUCCESS") or (a.verdict == "FAIL") != (a.outcome == "MOD FAILURE"):
    sys.exit("verdict %s does not go with outcome %s" % (a.verdict, a.outcome))
ev = os.path.join("evidence", a.test + a.suffix + ".txt")
open(os.path.join(VISIT, ev), "w", encoding="utf-8").write(open(a.log, encoding="utf-8", errors="replace").read().replace("\r", ""))
ident = json.load(open(os.path.join(VISIT, a.env), encoding="utf-8"))
row = {"test": a.test, "verdict": a.verdict, "outcome": a.outcome, "forbidden": [], "held": ["non-colonist pawns swept before the visit's batches"],
       "site_checked": True, "site": {"biome": "AridShrubland", "map_ok": True, "note": "a fresh AridShrubland quicktest map ; each scene prepares its own cells"},
       **ident, "game": "archmagi", "command": a.command,
       "evidence": "design/concepts/ExplosiveKnockback/version/in_game/visit_3/" + ev, "note": a.note,
       "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M PST")}
row.update(json.loads(a.extra))
with open(os.path.join(VISIT, "rows.jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(row) + "\n")
print("row", a.test, a.verdict, a.outcome)
