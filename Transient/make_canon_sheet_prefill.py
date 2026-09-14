#!/usr/bin/env python3
"""Generate the CONFIG/ITEMS blocks and a pre-filled decisions.json for the
canon-creature disagreement review sheet (CANON_REFERENCE_LIBRARY_1).

Reads the 24-row disagreement census plus each creature's description.md,
picks a best-guess "canonical look" per row (favoring the image the
Visual brief calls out as most confirmatory of the sourced text — never the
donor sprite when the brief flags it as a mismatch), and writes:
  - Transient/canon_review_sheet.html   (template with CONFIG/ITEMS filled in)
  - Transient/canon_review_decisions.json

Re-run this ONLY to regenerate the sheet's rows before the owner has opened
it — do not run this against a decisions file the owner has started ruling
in; it would overwrite his choices with these guesses.
"""
import json
import os
import re
import sys
import html as htmlmod

REPO = "/mnt/d/Luke/dev/Rimworld"
DISAGREEMENTS = "/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/9a25e492-5fac-46d4-bbe1-c0420ea9d162/scratchpad/canon_disagreements.json"
TEMPLATE = "/mnt/d/Luke/dev/Rimworld/Transient/canon_review_sheet.html"
IMG_ROOT = "canon_review_images"  # relative to Transient/, where sheet.html lives

OPTION_KEYS = ["1", "2", "3", "4"]


def esc(s):
    return htmlmod.escape(str(s), quote=True)


def read_sections(md_path):
    text = open(md_path, encoding="utf-8").read()

    def section(name, stop_names):
        m = re.search(rf"## {re.escape(name)}\n(.*?)(?=\n## (?:{'|'.join(stop_names)})|\Z)",
                       text, re.S)
        return m.group(1).strip() if m else ""

    sourced = section("Sourced text (Wookieepedia)", ["Visual brief"])
    visual = section("Visual brief", ["Source URLs"])
    return sourced, visual


def guess_pick(images, visual_brief, disagreement):
    """Best-guess which image (by index, 1-based) the brief treats as most
    canon-confirmatory. Never picks the donor sprite when the brief flags it
    as wrong. This is a SUGGESTION for the owner to overrule, not a finding."""
    vb = visual_brief.lower()
    dis = disagreement.lower()
    donor_flagged_wrong = (
        "donor" in dis or
        ("donor" in vb and any(w in vb for w in
            ["mismatch", "does not match", "doesn't match", "wrong", "not match"]))
    )
    for i, fname in enumerate(images, start=1):
        if fname.startswith("donor_") and donor_flagged_wrong:
            continue
        # crude signal: infobox / official art images are usually the cleanest single
        # confirmatory reference
        if "infobox" in fname.lower() or "official" in fname.lower():
            return str(i)
    # fall back: first non-donor image if donor is flagged wrong, else first image
    for i, fname in enumerate(images, start=1):
        if donor_flagged_wrong and fname.startswith("donor_"):
            continue
        return str(i)
    return "1"


def main():
    with open(DISAGREEMENTS) as f:
        rows = json.load(f)

    items = []
    prefill = {}
    sheet_id = "canon_reference_library_1_disagreements"

    for r in sorted(rows, key=lambda r: (-{"high": 2, "medium": 1, "low": 0}
                                          .get(r.get("confidence", "medium"), 1),
                                          r["creature"])):
        creature = r["creature"]
        folder = r["folder"]
        images = r["images"]
        md_path = os.path.join(REPO, folder, "description.md")
        sourced, visual = read_sections(md_path)

        img_entries = []
        for i, fname in enumerate(images[:4], start=1):
            rel = f"{IMG_ROOT}/{creature}/{fname}"
            img_entries.append({"key": str(i), "filename": fname, "path": rel})

        pick = guess_pick(images, visual, r["disagreement"])
        conf = r.get("confidence", "medium")

        items.append({
            "id": creature,
            "label": creature.capitalize(),
            "group": {"high": "High confidence disagreement",
                      "medium": "Medium confidence disagreement",
                      "low": "Low confidence disagreement"}.get(conf, "Disagreement"),
            "effect": r["disagreement"],
            "contested": True,
            "meta": {"confidence": conf},
            "thumb": img_entries[0]["path"] if img_entries else None,
            "images": img_entries,
            "sourced_text": sourced,
            "visual_brief": visual,
            "folder": folder,
            "prefill": pick,
        })
        prefill[creature] = {
            "decision": pick,
            "note": "",
            "prefill": pick,
        }

    n_imgs = max(len(it["images"]) for it in items)
    options = []
    colors = ["#5ac37f", "#5ac37f", "#5ac37f", "#5ac37f"]
    for i in range(1, n_imgs + 1):
        options.append({"key": str(i), "label": f"Image {i}", "hotkey": str(i),
                         "color": colors[(i - 1) % len(colors)]})

    config = {
        "sheetId": sheet_id,
        "title": "Canon creature reference — disagreements",
        "subtitle": "CANON_REFERENCE_LIBRARY_1 — 24 of 43 creatures where candidates disagree",
        "briefHtml": (
            "<p><b>Why this sheet exists:</b> the Wyyyschokk case — Wookieepedia TEXT alone "
            "described it as \"near-black to dark reddish-brown chitin\" and the AI render came "
            "out a generic brown spider, when the real canon (per the owner's own lore images) "
            "is blue-grey with a bold yellow-orange abdomen cross. Text undersells canon; images "
            "are the authority, and images often disagree with each other and with our current "
            "in-game donor sprite. Only the owner can pick the canonical look.</p>"
            "<p>Each row below is one of the 43 canon creatures in "
            "<code>design/RimStarWars/canon_references/</code> whose own research documented a "
            "real conflict — not everything needed a ruling, only these 24. Click a numbered "
            "image button to pick it as the canonical look, or just write your own ruling line "
            "in the note (e.g. \"blue-grey per image 2, but keep the donor's leg count\") — the "
            "note always wins over the button pick when both are present. Click any thumbnail to "
            "zoom it full-size before deciding.</p>"
            "<p>Rulings land back in each creature's own "
            "<code>design/RimStarWars/canon_references/&lt;creature&gt;/description.md</code> "
            "<code>## ruling</code> field once you're done — nothing here is final until that "
            "happens.</p>"
        ),
        "criterion": (
            "Rows are pre-filled with a SUGGESTED pick (the image the researching agent's own "
            "Visual brief called most confirmatory of the sourced canon text — never the donor "
            "sprite when the brief flagged it as a mismatch). This is a guess to react to, not a "
            "finding — read each Visual brief before trusting the pre-fill."
        ),
        "invented": [],
        "posture": {
            "mode": "ruling",
            "explain": (
                "Not a keep/cut list — every row needs a canonical-look RULING: which candidate "
                "image is correct, or your own line. All 24 rows need a decision; there is no "
                "'discard' side."
            ),
        },
        "options": options,
        "groupLabel": "confidence",
        "media": True,
        "decisionsFile": "canon_review_decisions.json",
        "decisionsPath": "",
        "sheetPath": "",
    }

    render_js = r"""
window.itemBody = it => {
  const gallery = (it.images || []).map(img => {
    const cap = `${it.label} — image ${img.key} (${img.filename})`;
    return `<div class="czthumb" data-zoom="${img.path.replace(/"/g,'&quot;')}" data-cap="${cap.replace(/"/g,'&quot;')}">
      <img src="${img.path}" loading="lazy" decoding="async" alt="">
      <div class="czcap">#${img.key} ${img.filename}</div>
    </div>`;
  }).join('');
  const details = `<details class="czdetails"><summary>sourced text + visual brief</summary>
    <div class="czsection"><b>Sourced text</b><br>${esc(it.sourced_text || '').replace(/\n/g,'<br>')}</div>
    <div class="czsection"><b>Visual brief</b><br>${esc(it.visual_brief || '').replace(/\n/g,'<br>')}</div>
    <div class="czsection czpath"><code>${esc(it.folder)}/description.md</code></div>
  </details>`;
  return `<div class="effect">${esc(it.effect || '')}</div>`
       + `<div class="czgallery">${gallery}</div>`
       + details;
};
function esc(s){return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
"""

    extra_css = """
.czgallery{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.czthumb{width:96px;cursor:zoom-in;text-align:center}
.czthumb img{width:96px;height:96px;object-fit:contain;border:1px solid var(--line);border-radius:5px;
  background-image:linear-gradient(45deg,#2a2f37 25%,transparent 25%,transparent 75%,#2a2f37 75%),
                   linear-gradient(45deg,#2a2f37 25%,transparent 25%,transparent 75%,#2a2f37 75%);
  background-size:12px 12px;background-position:0 0,6px 6px;background-color:#1a1d22}
.czcap{font-size:10px;color:var(--dim);margin-top:2px;word-break:break-all}
.czdetails{margin-top:6px;font-size:12px;color:var(--dim)}
.czdetails summary{cursor:pointer;color:var(--link)}
.czsection{margin-top:6px;white-space:normal}
.czpath{font-size:11px;color:var(--dim)}
"""

    html = open(TEMPLATE, encoding="utf-8").read()
    html = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(config, indent=2) + m.group(2),
        html, count=1, flags=re.S)
    html = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, indent=2) + m.group(2),
        html, count=1, flags=re.S)
    # inject RENDER block (replace the commented-out example block) and extra CSS
    html = html.replace(
        "<!-- ══ FILL IN #3 (optional) ═",
        f"<script id=\"RENDER\">{render_js}</script>\n<style>{extra_css}</style>\n<!-- ══ FILL IN #3 (optional, now used above) ═",
        1)
    with open(TEMPLATE, "w", encoding="utf-8") as f:
        f.write(html)

    decisions_doc = {"decisions": prefill}
    with open("/mnt/d/Luke/dev/Rimworld/Transient/canon_review_decisions.json", "w") as f:
        json.dump(decisions_doc, f, indent=2)

    print(f"wrote {len(items)} items to sheet; prefilled {len(prefill)} decisions")


if __name__ == "__main__":
    main()
