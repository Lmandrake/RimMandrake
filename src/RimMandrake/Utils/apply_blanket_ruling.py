#!/usr/bin/env python3
"""apply_blanket_ruling.py — stamp ONE owner decision onto every row of a review
sheet's decisions file, with provenance that never pretends to be a sitting.

WHY THIS EXISTS
    Sometimes the owner rules a whole sheet in one sentence instead of tapping
    through it ("replace everything"). That IS a real decision and it must be
    recorded — but recording it as though he clicked 109 rows is a forgery, and
    it is precisely the failure the review-sheets skill's SS8 exists to stop:
    an agent's guesses committed under the owner's name.

    So this writes the ruling, and writes down HOW it arrived:
      savedBy       'owner-blanket-ruling'   (never 'review-sheet-page', never
                                              the sidecar's own stamp)
      approvalRoute a paragraph saying the verdict is uniform BY INSTRUCTION,
                    that the sheet was never clicked, and that no individual row
                    carries an individual judgement.

🔴 A consumer can therefore always tell three things apart: a real sitting, a
   blanket ruling, and an agent's pre-fill. Keep it that way.

⛔ Never use this to record a decision the owner did not actually state, and
   never use it to "finish" a sheet he started tapping — that would overwrite
   real per-row judgements with a uniform one. It REFUSES when the file already
   carries sheet-written rows, unless --over-sitting is passed deliberately.

    python3 apply_blanket_ruling.py --decisions F.json --sheet S.html \
        --decision replace --said "<his words, verbatim>" [--apply]
"""
import argparse
import datetime
import json
import re
import sys


def sheet_row_ids(path):
    """Row ids straight from the sheet's ITEMS block — the authority on what
    rows exist. Deriving them from the decisions file instead would silently
    skip every row nobody has touched, which is most of them."""
    html = open(path, encoding="utf-8").read()
    m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        sys.exit(f"FAIL: no ITEMS block in {path} — is this a review sheet?")
    return [r["id"] for r in json.loads(m.group(1))]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--decision", required=True, help="the option key, e.g. replace")
    ap.add_argument("--said", required=True, help="his words, VERBATIM — never paraphrased")
    ap.add_argument("--note", default="", help="extra one-line note per row")
    ap.add_argument("--item", default="", help="ledger item that executes this ruling")
    ap.add_argument("--over-sitting", action="store_true",
                    help="allow overwriting rows a real sitting wrote (think first)")
    ap.add_argument("--apply", action="store_true", help="write; otherwise report only")
    a = ap.parse_args()

    ids = sheet_row_ids(a.sheet)
    doc = json.load(open(a.decisions, encoding="utf-8"))

    # Refuse to flatten a real sitting. A sidecar/page write is the tell.
    prior = doc.get("savedBy")
    if prior in ("review-sheet-page", "sidecar") and not a.over_sitting:
        sys.exit(f"REFUSED: {a.decisions} was written by '{prior}' — that is a real sitting, and a "
                 "blanket ruling would overwrite per-row judgements. Pass --over-sitting only if "
                 "the owner explicitly said to discard them.")

    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    note = a.note or f"Owner blanket ruling {now[:10]}: {a.decision} applied to every row."
    doc["decisions"] = {i: {"decision": a.decision, "note": note, "at": now} for i in ids}
    doc["decisionRowCount"] = len(ids)
    doc["savedBy"] = "owner-blanket-ruling"
    doc["approvedAt"] = now
    doc["approvedSaid"] = a.said
    doc["approvalRoute"] = (
        f"BLANKET ruling in conversation, applied uniformly to all {len(ids)} rows. The sheet was "
        "NOT clicked: every row carries the SAME decision and the same note, and no row carries an "
        "individual owner judgement. The uniformity is his instruction, not a default and not an "
        "agent's pre-fill — any pre-fill that was here has been replaced."
        + (f" Execution: {a.item}." if a.item else ""))
    doc["frozen"] = True
    doc["frozenMeaning"] = f"Owner ruled every row '{a.decision}' on {now[:10]}. Reopen only on his word."

    print(f"{a.decisions}\n  rows: {len(ids)}  ->  all '{a.decision}'  (was savedBy={prior!r})")
    if not a.apply:
        print("  DRY RUN — pass --apply to write.")
        return
    with open(a.decisions, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("  written, frozen.")


if __name__ == "__main__":
    main()
