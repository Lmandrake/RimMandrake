#!/usr/bin/env python3
"""Build the regenerated-art review sheet from the review-sheets template.
One row per validated render, thumbnailed, grouped by regen wave, prefilled 'keep'.
SAFE to re-run for the SHEET (renders from decisions). The DECISIONS file is written
only if absent (never overwrites the owner's grading)."""
import json, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TEMPLATE = os.path.join(os.path.expanduser("~"),
    ".claude/skills/review-sheets/assets/sheet_template.html")

# wave -> the owner-facing character of that batch (from the job style_notes / item)
WAVE_LABEL = {}

def build():
    items, seen = [], set()
    for jp in sorted(glob.glob(os.path.join(REPO, "infrastructure/artpipe/done/*.json"))):
        if jp.endswith(".manifest.json"): continue
        j = json.load(open(jp))
        jid = j["id"]
        if not os.path.isfile(os.path.join(HERE, "images", jid + ".png")): continue
        stem = jid.rsplit("_", 1)[0]
        facing = j.get("facing") or "—"
        wave = j.get("rimflow_item_id") or "unknown"
        # label reads as creature + facing; sort key clusters a creature's facings
        creature = stem.replace("aa_", "").replace("_v1", "").replace("_", " ")
        items.append({
            "id": jid,
            "label": f"{creature} · {facing}",
            "group": wave,
            "thumb": f"images/{jid}.png",
            "effect": (j.get("style_notes") or j.get("prompt","")[:160]),
            "meta": {"facing": facing, "sort": stem},
            "prefill": "keep",
        })
    items.sort(key=lambda it: (it["group"], it["meta"]["sort"], it["meta"]["facing"]))
    decisions = {
        "posture": "whitelist",
        "decisions": {it["id"]: {"decision": it["prefill"], "prefill": it["prefill"], "note": ""}
                      for it in items},
    }
    return items, decisions

CONFIG = {
    "sheetId": "art_regen_2026_09_12",
    "title": "Regenerated creature art — grading pass",
    "subtitle": "148 validated renders · 58 creatures × 3 facings",
    "briefHtml": (
        "<p>Every render here <b>passed the offline validator</b> (real alpha, silhouette "
        "inside the footprint, correct 512² canvas). That is all the validator can judge. "
        "It <b>cannot</b> tell whether the sprite reads as the <i>right creature</i>, whether "
        "it is good art, or whether it matches the owner's direction for that biome. "
        "That judgement is this pass.</p>"
        "<p>Pre-filled <b>Keep</b> throughout — overrule freely. <b>Redraw</b> = regenerate "
        "with a better prompt (leave a note saying what's wrong); <b>Cut</b> = this creature "
        "shouldn't carry custom art at all. Facings of one creature sit next to each other; "
        "judge the set, not just one angle.</p>"),
    "criterion": ("Ordered by regen wave then creature — a wave shares a prompt-direction, "
                  "so whole waves often share a virtue or a flaw. Order is NOT quality: the "
                  "validator ranked nothing, it only gated."),
    "invented": [],
    "posture": {"mode": "whitelist",
                "explain": "Keep/Redraw stay wired in; Cut strips the custom art for that render."},
    "options": [
        {"key": "keep",   "label": "Keep",   "hotkey": "1", "color": "#5ac37f", "counts": "in"},
        {"key": "redraw", "label": "Redraw", "hotkey": "2", "color": "#e8b64c", "counts": "in"},
        {"key": "cut",    "label": "Cut",    "hotkey": "3", "color": "#e06c6c", "counts": "out"},
    ],
    "groupLabel": "wave",
    "media": True,
    "decisionsFile": "decisions.json",
}

def swap(html, tag, payload):
    open_tag = f'<script id="{tag}" type="application/json">'
    a = html.index(open_tag)
    s = a + len(open_tag)
    e = html.index("</script>", s)
    return html[:s] + "\n" + payload + "\n" + html[e:]

def main():
    items, decisions = build()
    html = open(TEMPLATE, encoding="utf-8").read()
    html = swap(html, "CONFIG", json.dumps(CONFIG, indent=2))
    html = swap(html, "ITEMS", json.dumps(items, indent=1))
    open(os.path.join(HERE, "sheet.html"), "w", encoding="utf-8").write(html)
    dpath = os.path.join(HERE, "decisions.json")
    if os.path.exists(dpath):
        print("decisions.json exists — left untouched (owner's grading is safe)")
    else:
        json.dump(decisions, open(dpath, "w", encoding="utf-8"), indent=2)
        print(f"wrote decisions.json ({len(decisions['decisions'])} pre-filled keep)")
    print(f"sheet.html: {len(items)} rows")

if __name__ == "__main__":
    sys.exit(main())
