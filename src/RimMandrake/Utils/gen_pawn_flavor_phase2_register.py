#!/usr/bin/env python3
"""Generate the Phase 2 lore-prose review sheet (PAWN_FLAVOR_PHASE2_PROSE_1).

Emits design/Jawa/worldbuilding/review/pawn_flavor_phase2_register.html and,
when no owner-touched decisions file exists, the prefill JSON beside it.

Inputs (both committed, both read-only here):
  * infrastructure/output/pawn_flavor_phase2_census.csv - the COMMON/OCCASIONAL/
    DORMANT census over every ThoughtDef/MentalBreakDef/XenotypeDef reachable in
    the live 585-mod set (row = defType, defName, modName, currentLabelOrText,
    tier, oneLineWhy). This generator rows the COMMON tier (497 rows) plus the
    OCCASIONAL tier (1,286 rows, added in the OCCASIONAL-extension pass) - 1,783
    rows total. DORMANT stays out of scope (see pawn_flavor_design.md item 6).
  * infrastructure/output/pawn_flavor_phase2_prose_draft.json - the drafted
    Star-Wars/Jawa-scavenger replacement prose for every COMMON+OCCASIONAL row,
    keyed "<defType>::<defName>". Field shape varies by defType (ThoughtDef/
    XenotypeDef carry label+description; MentalBreakDef carries label+
    beginLetter+recoveryMessage, since the prose actually lives on the linked
    MentalStateDef, not on MentalBreakDef itself - several rows have no linked
    MentalStateDef at all and carry only a label).

This is a DRAFT-REVIEW sheet, not a keep/cut sheet like Phase 1's
gen_pawn_flavor_register.py: every row already carries a proposed replacement:
the owner's decision is approve / tweak (note holds the correction) / reject
(regenerate later) / skip (not yet looked at). Default prefill is "approve" -
the agent decided, the human disagrees.

🔴 The decisions file is the OWNER'S once it carries `savedAt` (stamped only by
the page). This generator refuses to overwrite it without
--i-know-this-overwrites-the-owners-decisions.
"""
import argparse
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CENSUS_CSV = os.path.join(ROOT, "infrastructure", "output", "pawn_flavor_phase2_census.csv")
PROSE_JSON = os.path.join(ROOT, "infrastructure", "output", "pawn_flavor_phase2_prose_draft.json")
OUT_DIR = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "review")
HTML_OUT = os.path.join(OUT_DIR, "pawn_flavor_phase2_register.html")
DEC_OUT = os.path.join(OUT_DIR, "pawn_flavor_phase2_register.decisions.json")
DEC_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\pawn_flavor_phase2_register.decisions.json"
HTML_NATIVE = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\pawn_flavor_phase2_register.html"

DEFTYPE_ORDER = {"ThoughtDef": 0, "MentalBreakDef": 1, "XenotypeDef": 2}


def fmt_proposed(defType, p):
    if defType == "MentalBreakDef":
        bits = ["label: " + p.get("label", "")]
        if p.get("beginLetter"):
            bits.append("announce: " + p["beginLetter"])
        if p.get("recoveryMessage"):
            bits.append("recovery: " + p["recoveryMessage"])
        return "\n".join(bits)
    return "label: " + p.get("label", "") + "\n" + p.get("description", "")


ROWED_TIERS = {"COMMON", "OCCASIONAL"}


def build_rows():
    census = list(csv.DictReader(open(CENSUS_CSV, encoding="utf-8")))
    wanted = [r for r in census if r["tier"] in ROWED_TIERS]
    prose = json.load(open(PROSE_JSON, encoding="utf-8"))

    rows = []
    missing = []
    for r in wanted:
        key = r["defType"] + "::" + r["defName"]
        p = prose.get(key)
        if p is None:
            missing.append(key)
            continue
        rows.append({
            "id": key,
            "defType": r["defType"],
            "defName": r["defName"],
            "modName": r["modName"],
            "tier": r["tier"],
            "group": r["defType"] + " \u00b7 " + r["modName"],
            "why": r["oneLineWhy"],
            "current": r["currentLabelOrText"],
            "proposed": fmt_proposed(r["defType"], p),
        })
    if missing:
        raise SystemExit("REFUSED: %d COMMON/OCCASIONAL census rows have no drafted prose (first 5: %s) - "
                          "draft prose for every row before generating."
                          % (len(missing), missing[:5]))

    rows.sort(key=lambda r: (DEFTYPE_ORDER.get(r["defType"], 9), r["modName"], r["defName"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true")
    args = ap.parse_args()

    rows = build_rows()
    prefill = {r["id"]: {"d": "approve", "n": ""} for r in rows}

    if os.path.exists(DEC_OUT):
        try:
            existing = json.load(open(DEC_OUT, encoding="utf-8"))
        except ValueError:
            existing = {}
        if existing.get("savedAt") and not getattr(
                args, "i_know_this_overwrites_the_owners_decisions"):
            print("REFUSED: %s carries savedAt=%s - it holds the owner's decisions.\n"
                  "Re-run with --i-know-this-overwrites-the-owners-decisions to discard them."
                  % (DEC_OUT, existing.get("savedAt")))
        else:
            write_prefill(prefill)
    else:
        write_prefill(prefill)

    html = render_html(rows, prefill)
    os.makedirs(OUT_DIR, exist_ok=True)
    open(HTML_OUT, "w", encoding="utf-8").write(html)
    print("wrote %s (%d rows)" % (HTML_OUT, len(rows)))


def write_prefill(prefill):
    payload = {
        "sheet": "pawn_flavor_phase2_register",
        "posture": "draft-review; default APPROVE - a row left untouched ships the drafted prose as-is",
        "prefill": True,
        "rows": prefill,
    }
    json.dump(payload, open(DEC_OUT, "w", encoding="utf-8"), indent=1)
    print("wrote prefill %s (%d rows)" % (DEC_OUT, len(prefill)))


def render_html(rows, prefill):
    data_json = json.dumps(rows)
    prefill_json = json.dumps(prefill)
    tpl = open(os.path.join(os.path.dirname(__file__),
                            "pawn_flavor_phase2_register_template.html"), encoding="utf-8").read()
    return (tpl.replace("/*__DATA__*/[]", data_json)
               .replace("/*__PREFILL__*/{}", prefill_json)
               .replace("__DEC_NATIVE__", DEC_NATIVE.replace("\\", "\\\\"))
               .replace("__HTML_NATIVE__", HTML_NATIVE.replace("\\", "\\\\")))


if __name__ == "__main__":
    sys.exit(main())
