"""belt_bridge5: build the FlowWorks owner review sheet (review-sheets template) + its pre-fill decisions file.
python3 Transient/belt_bridge5_make_sheet.py  (WSL, repo root)"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import northstar as N        # noqa: E402
import site_spec as S        # noqa: E402
import validation_v2 as V    # noqa: E402

TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
OUTDIR = os.path.join(ROOT, "Transient", "belt_bridge5_review")
SHEET = os.path.join(OUTDIR, "FlowWorks_owner_review.html")
DEC = os.path.join(OUTDIR, "FlowWorks_owner_review.decisions.json")
RESULT = "validation_v2_result_20261005T162414.json"
SAVE = "NS_FlowWorks_Review_20261005"

# The scene on the review save that shows each promoted bar (validation_v2.SCENES, X/P phases).
SHOT_FOR = {"X1": "X_promoted", "X2": "X_promoted", "X3": "X_promoted", "X4": "X_promoted",
            "X5": "X_promoted", "X6": "X_promoted", "X7": "X_promoted", "X8": "X_promoted",
            "X9": "X_promoted", "P4": "P_pits"}
WHERE = {"X1": "X_strip cells (131..134, 70)", "X2": "X_strip (131..134, 70)", "X3": "X_strip (131..134, 70)",
         "X4": "X_strip D=4 end (134, 70)", "X5": "X_strip / slime cell", "X6": "X_two rows z74/z76, junction (134, 75)",
         "X7": "X_race_tar z79 vs X_race_water z82", "X8": "X_cover (140..141, 70..71)",
         "X9": "X_cover (140..141, 70..71)", "P4": "P_walk pit (166, 100)"}


def main():
    walk = N.find_walk(ROOT, "FlowWorks")
    w = N.parse(walk)
    res = json.load(open(os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar", RESULT)))
    rows = {r["id"]: r for r in res["rows"]}
    plot_of = {}
    for p in S.PLOTS:
        for b in p["bars"]:
            plot_of.setdefault(b, p["id"])
    items, dec = [], {}
    for kind, ids, texts in (("must show", w["must_show"], w["must_show_text"]),
                             ("cannot show", w["cannot_show"], w["cannot_show_text"])):
        tmap = texts if isinstance(texts, dict) else dict(zip(ids, texts or []))
        for bar in ids:
            text = str(tmap.get(bar, "")).strip()
            row_id = V.PROMOTED.get(bar)
            row = rows.get(row_id) if row_id else None
            key = (row_id or "")[:2]
            it = {"id": bar, "label": bar, "group": "%s / plot %s" % (kind, plot_of.get(bar, "-")),
                  "effect": text[:300] or "(no text parsed)"}
            if row:
                it["meta"] = "LIVE %s %s: %s | on the review save at %s" % (
                    row_id, row["status"], str(row.get("detail", ""))[:260], WHERE.get(key, "?"))
                it["thumb"] = SHOT_FOR.get(key, "X_promoted") + ".png"
                it["prefill"] = "right"
                it["contested"] = True
                dec[bar] = {"decision": "right", "note": "prefill: state read PASSED live; the LOOK is yours"}
            else:
                it["meta"] = ("no single live state row names this bar; v2 functional phases all PASS (74/74). "
                              "The look is judged by validation.py's visual half, which has NOT run.")
                it["prefill"] = ""
                dec[bar] = {"decision": "", "note": "left open on purpose: only your eyes decide a look bar"}
            items.append(it)
    config = {
        "sheetId": "flowworks_owner_review_20261005",
        "title": "FlowWorks — owner review",
        "subtitle": "v2 live GREEN 74/0 on the flowworks tier, 2026-10-05",
        "briefHtml": (
            "<p>FlowWorks' functional script (validation_v2) ran <b>LIVE GREEN: 74 PASS, 0 FAIL, 0 UNBUILT</b> "
            "on the 10-mod flowworks tier (result <code>%s</code>). modcheck now reads "
            "<b>PENDING-OWNER-REVIEW</b>: the only thing between FlowWorks and GREEN-minimal is your review, "
            "recorded with <code>modcheck review FlowWorks --owner-said \"...\"</code>.</p>"
            "<p>One row per north-star bar (38 must-show, 5 cannot-show). The 10 bars promoted from UNBUILT today "
            "carry a live state read and a screenshot; they are pre-filled <i>looks right</i> and marked contested, "
            "because a state read proves the mechanism, not the look. Every other bar is left open on purpose.</p>"
            "<p><b>Walk it in game:</b> load the save <code>%s</code> (Saves folder) and look at the coordinates on "
            "each row. Screenshots of every scene group are beside this page.</p>") % (RESULT, SAVE),
        "criterion": "Pre-filled only where a live state row passed; that ranks mechanism, not appearance.",
        "invented": [],
        "posture": {"mode": "whitelist",
                    "explain": "A bar marked looks right counts toward your review; looks wrong reopens it."},
        "options": [
            {"key": "right", "label": "Looks right", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "wrong", "label": "Looks wrong", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
            {"key": "cantsee", "label": "Can't judge here", "hotkey": "3", "color": "#e8b64c", "counts": "out"},
        ],
        "groupLabel": "bar kind / site plot",
        "media": True,
        "decisionsFile": os.path.basename(DEC),
        "decisionsPath": "", "sheetPath": "",
    }
    html = open(TEMPLATE, encoding="utf-8").read()
    html = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                  lambda m: m.group(1) + "\n" + json.dumps(config, indent=1) + "\n" + m.group(3), html, 1, re.S)
    html = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                  lambda m: m.group(1) + "\n" + json.dumps(items, indent=1) + "\n" + m.group(3), html, 1, re.S)
    open(SHEET, "w", encoding="utf-8").write(html)
    json.dump({"posture": "whitelist", "decisions": dec,
               "reviewStatus": {"state": "prefill", "by": None, "at": None,
                                "evidence": "generated by Transient/belt_bridge5_make_sheet.py; nobody has ruled"}},
              open(DEC, "w", encoding="utf-8"), indent=1)
    print("%d rows (%d pre-filled) -> %s" % (len(items), sum(1 for i in items if i["prefill"]), SHEET))


if __name__ == "__main__":
    main()
