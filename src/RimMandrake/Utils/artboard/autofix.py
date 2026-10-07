"""Pre-review triage for a contact board, under the owner's policy of 2026-10-06 (typed, verbatim):
"(1) plus regen the art if you already know how, only go to human if you need judgement to fix it".

So every finding lands in exactly one class:

  STAGING    the board was staged wrong (refused op, subject off its cell, crop off the frame, a recipe typo).
             Fixed silently: re-stage (nudged origin / other rotation / fixed recipe) and re-capture. Never shown.
  ART_FIX    the art or its draw code is wrong in a way we already know how to fix (magenta = texPath unbound or
             file missing; an alpha hole; a texture cut off by its canvas; a catalogued draw-code defect).
             Fixed without asking: art-ledger search first, then regenerate / patch, then re-run the board.
  JUDGEMENT  needs an eye: wrong colour family, two states that look the same, drift from an approved reference,
             any vision-read FAIL or UNSURE, a catalogued design question, anything this module does not know.
             Only these reach the owner board.

    cd src/RimMandrake/Utils && python3 -m artboard.autofix <out dir> [--vision answers.txt]

<out dir> is an artboard run folder (report.json; live_report.json when it came from artboard.live). --vision is
the one batched image read's answer, one line per tile: "#3 FAIL the hose kinks" / "#4 PASS" / "#5 UNSURE ...".
Writes triage.json + triage.md beside the report. Pure logic; selftest_autofix.py.
"""
import json
import os
import re
import sys

STAGING_CHECKS = {
    "STAGE_REFUSED": "the stager refused an op: re-stage at a nudged origin or another rotation, or fix the recipe",
    "OFF_CELL": "the drawn mass is off its cell: the stager moved it (or a drawOffset): re-stage on the exact cell",
    "OUT_OF_FRAME": "the crop leaves the frame: fix the capture rect / origin",
    "BAD_BOARD": "the recipe names an unknown subject: fix the recipe",
}
ART_CHECKS = {
    "MISSING_TEXTURE": "magenta: the texPath does not bind or the file is missing - search the art ledger "
                       "(artpipe_state.py find) for a finished render first, regenerate only if none",
    "HOLE": "an enclosed ground-coloured hole in the silhouette: alpha hole - regenerate / repaint the alpha",
    "TRUNCATED": "a ruler-straight edge on an organic subject: the texture is cut by its canvas - regenerate with padding",
}
JUDGEMENT_CHECKS = {
    "WRONG_COLOUR": "the colour family is not the expected one",
    "IDENTICAL": "two states that must differ render the same",
    "REF_DRIFT": "drifted from the owner-approved reference",
    "OVERFLOW": "draws well past its cell",
    "EMPTY": "nothing drawn on the cell",
}

# Catalogued, already-diagnosed defects per (recipe, subject): what the fix is and which class it is. A catalogue
# entry wins over the generic check class, so a known draw-code fix is applied without asking and a pending design
# call always reaches the owner however clean the crop looks.
KNOWN = {
    ("gss_states", "cord_unpowered"): ("ART_FIX", "GPT A19: PowerStripDark is drawn at aspect 1 (SectionLayer_RM_MessyCords.cs:163) "
                                       "though its texture is 64x32 like PowerStrip's 0.5 - draw it at 0.5"),
    ("gss_states", "hose_behind_uturn"): ("JUDGEMENT", "fuzz G2 / live MX_H FAILs: the outlet blend kinks a hose whose target is behind "
                                          "the reel (bend 0.02-0.4 vs 0.6-2.0); the fix (a radius-held arc out of the outlet, or a "
                                          "different outlet rule) is a design call"),
}


def parse_vision(text):
    """'#3 FAIL why' lines -> {'#3': ('FAIL', 'why')}. Unknown words are kept as UNSURE (never silently PASS)."""
    out = {}
    for line in (text or "").splitlines():
        m = re.match(r"\s*[-*]?\s*(#\d+)\W+\s*(PASS|FAIL|UNSURE)?\b\s*(.*)", line, re.I)
        if not m:
            continue
        word = (m.group(2) or "UNSURE").upper()
        out[m.group(1)] = (word, m.group(3).strip())
    return out


def classify(check):
    if check in STAGING_CHECKS:
        return "STAGING", STAGING_CHECKS[check]
    if check in ART_CHECKS:
        return "ART_FIX", ART_CHECKS[check]
    if check in JUDGEMENT_CHECKS:
        return "JUDGEMENT", JUDGEMENT_CHECKS[check]
    return "JUDGEMENT", "unknown check %s - an eye decides" % check


def triage(report, recipe=None, live=None, vision=None, tiles=None):
    """report: artboard report.json dict; live: live_report.json dict (STAGE_REFUSED); vision: parse_vision output;
    tiles: vision_key.json 'tiles' (tile label -> subject id). Returns {rows, by_class, owner}."""
    rows = {}

    def add(sid, cls, what, check):
        r = rows.setdefault(sid, {"id": sid, "items": []})
        r["items"].append({"class": cls, "check": check, "action": what})

    for sid, errs in ((live or {}).get("stage_refused") or {}).items():
        add(sid, "STAGING", STAGING_CHECKS["STAGE_REFUSED"] + " (" + "; ".join(errs)[:200] + ")", "STAGE_REFUSED")
    for row in report.get("rows", []):
        for f in row.get("findings", []):
            cls, what = classify(f["check"])
            add(row["id"], cls, what + " - " + f.get("detail", ""), f["check"])
    tile_id = {t["tile"]: t["id"] for t in (tiles or [])}
    for lab, (word, why) in (vision or {}).items():
        sid = tile_id.get(lab)
        if sid and word != "PASS":
            add(sid, "JUDGEMENT", "vision read %s: %s" % (word, why), "VISION_" + word)
    name = recipe or report.get("_recipe")
    every = {r["id"] for r in report.get("rows", [])} | set(rows)
    for sid in every:
        k = KNOWN.get((name, sid))
        if k:
            add(sid, k[0], k[1], "KNOWN")
    # a subject's class is its most demanding item: JUDGEMENT > ART_FIX > STAGING. A staging fault hides the art, so a
    # subject with any STAGING item is re-staged first and its other findings wait for the clean capture.
    out = []
    for sid, r in sorted(rows.items()):
        classes = {i["class"] for i in r["items"]}
        if "STAGING" in classes and not any(i["check"] == "KNOWN" for i in r["items"]):
            r["class"] = "STAGING"
        elif "JUDGEMENT" in classes:
            r["class"] = "JUDGEMENT"
        elif "ART_FIX" in classes:
            r["class"] = "ART_FIX"
        else:
            r["class"] = "STAGING"
        out.append(r)
    by = {c: [r["id"] for r in out if r["class"] == c] for c in ("STAGING", "ART_FIX", "JUDGEMENT")}
    return {"recipe": name, "rows": out, "by_class": by, "owner": by["JUDGEMENT"],
            "clean": sorted(every - set(rows))}


def write(out_dir, t):
    json.dump(t, open(os.path.join(out_dir, "triage.json"), "w"), indent=1)
    lines = ["# Pre-review triage - %s" % t.get("recipe"), "",
             "Policy (owner 2026-10-06): staging faults fixed silently, known art fixes applied without asking, "
             "only judgement reaches the owner.", "",
             "| class | count | subjects |", "|---|---|---|"]
    for c in ("STAGING", "ART_FIX", "JUDGEMENT"):
        lines.append("| %s | %d | %s |" % (c, len(t["by_class"][c]), ", ".join(t["by_class"][c]) or "-"))
    lines += ["", "Clean (no finding): %d" % len(t["clean"]), ""]
    for r in t["rows"]:
        lines.append("- **%s** [%s]: %s" % (r["id"], r["class"], " | ".join(i["action"] for i in r["items"])[:600]))
    open(os.path.join(out_dir, "triage.md"), "w").write("\n".join(lines) + "\n")


def main(argv=None):
    a = list(argv if argv is not None else sys.argv[1:])
    if not a:
        print(__doc__)
        return 2
    out = a[0]
    rep = json.load(open(os.path.join(out, "report.json")))
    live = json.load(open(os.path.join(out, "live_report.json"))) if os.path.exists(os.path.join(out, "live_report.json")) else None
    vision = tiles = None
    if "--vision" in a:
        vision = parse_vision(open(a[a.index("--vision") + 1]).read())
        kp = os.path.join(out, "vision_key.json")
        tiles = json.load(open(kp))["tiles"] if os.path.exists(kp) else []
    t = triage(rep, (live or {}).get("recipe"), live, vision, tiles)
    write(out, t)
    print("TRIAGE %s: staging %d (fix silently), art %d (fix without asking), owner %d, clean %d -> %s"
          % (t["recipe"], len(t["by_class"]["STAGING"]), len(t["by_class"]["ART_FIX"]), len(t["owner"]), len(t["clean"]),
             os.path.join(out, "triage.md")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
