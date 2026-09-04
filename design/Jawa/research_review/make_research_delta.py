#!/usr/bin/env python3
"""make_research_delta.py - build the DELTA review sheet for RESEARCH_TREE_NORMALIZATION_1.

Owner ruling 2026-09-04 by card ("Delta sheet only"): the frozen deck round 3
covered tree placement; the remaining owner pass covers only what the deck never
showed him:
  1. every row whose current manifest fate differs from the 09-03 prefill sheet
  2. the faction-held rows and their holders
  3. the new RUT_Rites / RUT_Antiq rows

Reads:  infrastructure/output/research_manifest_draft.csv        (schema v2)
        design/Jawa/research_review/research_review_decisions.json  (09-03 prefill)
Writes: design/Jawa/research_review/research_delta_decisions.json   (PREFILL ONLY)
        design/Jawa/research_review/research_delta_review.html      (from the template)

GUARD: refuses to overwrite a decisions file the sheet has touched (savedBy /
writeCount are stamped only by the sheet's own plumbing, never by this script).
Override: --i-know-this-overwrites-the-owners-decisions
"""
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MANIFEST = ROOT / "infrastructure/output/research_manifest_draft.csv"
OLD_DECISIONS = HERE / "research_review_decisions.json"
OUT_DECISIONS = HERE / "research_delta_decisions.json"
OUT_SHEET = HERE / "research_delta_review.html"
TEMPLATE = Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html"


def cut_group(note: str) -> str:
    n = note.lower()
    if "mechanoid" in n:
        return "Cut - all mechanoid research (your frozen deck, 2026-09-04)"
    if "anomaly row" in n or "anomaly" in n:
        return "Cut - Anomaly rows (rule 5: content stays, research goes)"
    if "saber" in n or "force" in n or "jedi" in n or "sith" in n:
        return "Cut - lightsaber / Force tech (nobody teaches it)"
    if "droid" in n or "unbolting" in n:
        return "Cut - droid construction (Free Droid Enclave-owned)"
    return "Cut - other (v4 model / deck)"


def cut_reason(note: str) -> str:
    # lead with the consequence; the note column carries provenance prose
    first = note.split("|")[0].strip()
    if first.startswith("owner frozen deck"):
        return "deck ruling: " + first.split(":", 1)[1].strip()
    return first


def main() -> int:
    force = "--i-know-this-overwrites-the-owners-decisions" in sys.argv
    if OUT_DECISIONS.exists():
        doc = json.loads(OUT_DECISIONS.read_text())
        if (doc.get("savedBy") or doc.get("writeCount")) and not force:
            sys.exit(
                "REFUSING: %s carries savedBy/writeCount - the sheet has written "
                "it, so it holds the OWNER'S decisions, not a prefill. Rerun with "
                "--i-know-this-overwrites-the-owners-decisions only if he says so."
                % OUT_DECISIONS
            )

    header = MANIFEST.open().readline().strip()  # "# fingerprint=... capturedUtc=..."
    with MANIFEST.open() as f:
        next(f)
        rows = list(csv.DictReader(f))
    old = json.loads(OLD_DECISIONS.read_text())["decisions"]

    items, seen = [], set()

    def add(row, group, effect, prefill="accept", **flags):
        if row["defName"] in seen:
            return
        seen.add(row["defName"])
        it = {
            "id": row["defName"],
            "label": row["defName"],
            "group": group,
            "effect": effect,
            "prefill": prefill,
            "meta": {"mod": row["source_mod"]} if row["source_mod"] else {},
        }
        it.update(flags)
        items.append(it)

    # 1. new rows (Rites / Antiquities) - show these first
    n_new = 0
    for r in rows:
        if r["defName"] in old:
            continue
        n_new += 1
        add(
            r,
            "NEW rows - The Rites & Antiquities (authored 2026-09-04)",
            "NEW %s %s, cost %s - %s" % (r["tab"], r["tier"], r["cost"], cut_reason(r["note"])),
        )

    # 2. faction-held rows, grouped by holder
    n_fh, n_defaulted = 0, 0
    for r in rows:
        if r["access"] != "faction-held":
            continue
        n_fh += 1
        inferred = "no specific sitting ruling found" in r["note"]
        n_defaulted += inferred
        add(
            r,
            "Faction-held by %s - earned via techprints, never bought" % (r["holder"] or "?"),
            "%s %s cost %s - locked behind %s techprints. accept = ships locked to this holder"
            % (r["tab"], r["tier"], r["cost"], r["holder"] or "?"),
            inferred=inferred,
        )

    # 3. fate changed since the 09-03 prefill (all untouched -> cut today)
    n_cut = 0
    for r in rows:
        o = old.get(r["defName"])
        if not o or o["prefill"] == r["fate"]:
            continue
        n_cut += 1
        add(
            r,
            cut_group(r["note"]),
            "was '%s' on 09-03, now '%s'. %s" % (o["prefill"], r["fate"], cut_reason(r["note"])),
        )

    prefill_decisions = {
        it["id"]: {"decision": it["prefill"], "prefill": it["prefill"], "note": ""}
        for it in items
    }
    OUT_DECISIONS.write_text(
        json.dumps(
            {
                "posture": "confirm-delta",
                "criterion": (
                    "Delta vs what the frozen deck already showed - grouped by why "
                    "each row is here, not by quality. Prefill is ACCEPT everywhere: "
                    "this sheet exists to collect your overrides."
                ),
                "generatedBy": "make_research_delta.py",
                "manifestFingerprint": header.lstrip("# ").strip(),
                "decisions": prefill_decisions,
            },
            indent=2,
        )
        + "\n"
    )

    config = {
        "sheetId": "research_delta_20260904",
        "title": "Research normalization - delta review",
        "subtitle": "the last owner pass on RESEARCH_TREE_NORMALIZATION_1",
        "briefHtml": (
            "<p><b>Everything the frozen deck (round 3, 2026-09-04) did NOT show you.</b> "
            "Three kinds of row: the %d NEW Rites/Antiquities rows, the %d faction-held rows "
            "and their holders, and the %d rows whose fate changed to <i>cut</i> since the "
            "09-03 sheet (your Anomaly / saber / droid / mechanoid rulings, applied). "
            "Prefill is <b>accept</b> on every row - click <b>wrong</b> and say what in the "
            "note. An unchanged row ships as shown.</p>"
        )
        % (n_new, n_fh, n_cut),
        "criterion": (
            "Grouped by WHY the row is on this sheet (new / holder / cut reason) - "
            "this orders explanation, not importance; it cannot rank what a row is worth to the campaign."
        ),
        "invented": [
            "%d of the %d faction-held rows carry 'no specific sitting ruling found' - "
            "their tab/tier was defaulted from the tier band by the manifest build, "
            "not ruled by you. They are marked 'inferred' and have their own filter."
            % (n_defaulted, n_fh),
        ],
        "posture": {
            "mode": "blacklist",
            "explain": (
                "Default is ACCEPT - every row ships exactly as written unless you "
                "mark it wrong. 'wrong' rows go back to BENCH with your note; nothing "
                "is stripped by leaving a row untouched."
            ),
        },
        "options": [
            {"key": "accept", "label": "Accept", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "wrong", "label": "Wrong", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "reason",
        "media": False,
        "decisionsFile": OUT_DECISIONS.name,
        "decisionsPath": str(OUT_DECISIONS),
        "sheetPath": str(OUT_SHEET),
    }

    html = TEMPLATE.read_text()
    html = html.replace(
        '<script id="CONFIG" type="application/json">',
        '<script id="CONFIG" type="application/json">\n', 1
    )
    import re

    html = re.sub(
        r'(<script id="CONFIG" type="application/json">).*?(</script>)',
        lambda m: m.group(1) + "\n" + json.dumps(config, indent=2) + "\n" + m.group(2),
        html, count=1, flags=re.S,
    )
    html = re.sub(
        r'(<script id="ITEMS" type="application/json">).*?(</script>)',
        lambda m: m.group(1) + "\n" + json.dumps(items, indent=1) + "\n" + m.group(2),
        html, count=1, flags=re.S,
    )
    OUT_SHEET.write_text(html)
    print(
        "rows: %d (%d new, %d faction-held [%d inferred], %d cut-delta) -> %s"
        % (len(items), n_new, n_fh, n_defaulted, n_cut, OUT_SHEET)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
