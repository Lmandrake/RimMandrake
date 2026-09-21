#!/usr/bin/env python3
"""Fills sheet_template.html with CONFIG/ITEMS/RENDER for the desert verdict sheet."""
import json
from pathlib import Path

REPO = Path("/mnt/d/Luke/dev/Rimworld")
OUT_DIR = REPO / "Transient"
SHEET_ID = "desert_art_verdict_2026-09-20"
TEMPLATE = Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html")
DATA = OUT_DIR / "_desert_verdict_build_data.json"
OUT_HTML = OUT_DIR / f"{SHEET_ID}.html"
OUT_DECISIONS = OUT_DIR / f"{SHEET_ID}.decisions.json"

raw_items = json.loads(DATA.read_text())

# Reshape into template-facing ITEMS: id/label/group/thumb/meta(kept)/effect
items = []
for it in raw_items:
    m = it["meta"]
    n_render = len(m["renders"])
    n_donor = len(m["donors"])
    effect = (f"{n_render}/3 facings rendered (own art) · donor comparison "
              f"{'available' if n_donor else 'UNAVAILABLE'} ({m.get('donor_source') or 'none'}) · "
              f"{'canon brief available' if m['must_show'] else 'no canon reference entry'}")
    items.append({
        "id": it["id"],
        "label": it["label"],
        "group": it["group"],
        "thumb": it["thumb"],
        "effect": effect,
        "prefill": "keep",   # see CONFIG.invented — this is NOT an art-quality judgment
        "meta_": m,   # consumed only by the custom RENDER script below
    })

items_json = json.dumps(items, indent=None, separators=(",", ":"))

config = {
    "sheetId": SHEET_ID,
    "title": "Desert family art verdict — DESERT_FAMILY_PORT_EXECUTION_1",
    "subtitle": "25 rows: 24 desert-port creatures with all-PASS new renders, plus Ferroclaw's earlier WAVE5 art",
    "briefHtml": (
        "<p><b>Why this sheet exists:</b> the owner ruled <i>“All of the desert sheet "
        "should be keep but replace with our own version of creature and art. Port. All of "
        "them. Now.”</i> (DESERT_FAMILY_PORT_EXECUTION_1). The artpipe daemon is mid-run on "
        "this item &mdash; <b>this sheet holds only the rows that have ALREADY LANDED on disk and "
        "PASS-validated</b> as of this build (measured live against "
        "<code>infrastructure/artpipe/registry.jsonl</code> + <code>artreg.build_status()</code>, "
        "never a stale census). ~52 more facings are still queued behind these and are NOT on this "
        "sheet &mdash; there is nothing to look at yet. <b>Rebuild this sheet later</b> by re-running "
        "the same generator once more jobs land (rows are keyed by defName, so re-running is safe "
        "to do repeatedly as the queue drains).</p>"
        "<p><b>Each row:</b> our new render (all rendered facings, south/east/north) next to the "
        "DONOR art it would replace, and the canon <code>## Must show</code> checklist where one "
        "exists (<code>design/RimStarWars/canon_references/</code> &mdash; 9 of these 25 have an "
        "entry; the rest are creatures outside that 137-entry library, not a gap in this sheet).</p>"
        "<div class='panel' style='border-color:#5a2b2b;background:#1a0e0e'>"
        "<h3 style='color:#ffb0b0'>⚠ Two things this sheet flags but does NOT resolve</h3>"
        "<ul style='margin:4px 0 0 16px;padding:0'>"
        "<li><b>RSW_MossBeetle</b> is NOT on this sheet at all (no art job exists for it in this wave). "
        "It was ruled <b>CUT</b> on 2026-09-19 (<code>deeps_flora_fauna_review_2026-09-18.decisions.json</code>), "
        "one day before this item's blanket “replace all of them” ruling. The two rulings "
        "disagree and this sheet takes no side &mdash; say which one stands.</li>"
        "<li><b>RSW_Ferroclaw</b> (row below, labelled “khorrak”) shows art from an EARLIER, "
        "unrelated job (<code>aa_terramorph</code>, <code>ART_REGEN_WAVE5_QUEUE_1</code>) because "
        "today's own desert-port job for it hasn't rendered yet. If you keep this art, the newer "
        "duplicate job should be cancelled rather than generating a second candidate.</li>"
        "</ul></div>"
    ),
    "criterion": ("None that a metric can rank — art quality is eye judgment only "
                   "(the Rot wave found 4 of 61 bad renders and only a human eye caught them). "
                   "Rows are pre-filled KEEP only because every one PASSED the automated facts "
                   "checker (alpha/canvas/facing sanity) — that is an administrative pass, "
                   "not a look. Overrule freely; that is the entire point of this sheet."),
    "invented": [
        "Pre-filled every row KEEP so the sheet isn't blank — this reflects ONLY that the "
        "automated facts-checker passed it (transparent background, right canvas, no crop), "
        "which is not a quality or canon-fit judgment. No render on this sheet has been looked "
        "at by a human eye yet.",
        "Grouped every creature with 2 or 3 rendered facings under “Ready for review” and "
        "everything with fewer under “Partial / needs attention” — an organizing split "
        "I chose, not an owner rule.",
        "For Ferroclaw, showing the OLDER aa_terramorph art (south+east PASS) rather than waiting for "
        "today's desertportb_ferroclaw job to render — judged this was more useful than an empty "
        "row, but it is a real judgment call, not a neutral default.",
        "Where a canon reference entry exists, preferring its curated donor_current_sprite.png for the "
        "SOUTH donor image and falling back to the live deployed texture (texPath resolved against the "
        "loaded mod set) for east/north — mixing two sources for one creature's donor comparison.",
    ],
    "posture": {
        "mode": "verdict",
        "explain": ("Not an include/exclude sheet — nothing here is stripped or kept by a posture. "
                     "Each row is a judgment on OUR OWN new render: KEEP wires it into the def next, "
                     "REGENERATE throws it back to the queue, NEEDS WORK means close but flag exactly "
                     "what (say it in the note).")
    },
    "options": [
        {"key": "keep", "label": "Keep", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
        {"key": "regenerate", "label": "Regenerate", "hotkey": "2", "color": "#e8b64c", "counts": "out"},
        {"key": "needs-work", "label": "Needs work", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
    ],
    "groupLabel": "status",
    "media": True,
    "decisionsFile": f"{SHEET_ID}.decisions.json",
    "decisionsPath": "",
    "sheetPath": "",
}
config_json = json.dumps(config, indent=2)

render_script = r"""
<script id="RENDER">
(function(){
  function facingRow(facingLabel, renderSrc, donorSrc) {
    var mk = function(src, tag){
      if (!src) return '<div class="thumb" style="width:96px;height:96px;flex:0 0 96px;display:flex;'
        + 'align-items:center;justify-content:center;font-size:10px;color:#5f6b7a">no '+tag+'</div>';
      return '<div class="thumb" style="width:96px;height:96px;flex:0 0 96px" data-zoom="'+esc(src)+'" '
        + 'data-cap="'+esc(facingLabel+' '+tag)+'"><img src="'+esc(src)+'" loading="lazy" alt=""></div>';
    };
    return '<div style="display:flex;gap:6px;align-items:center;margin:3px 0">'
      + '<span style="width:44px;font-size:10.5px;color:var(--dim);text-transform:uppercase">'+esc(facingLabel)+'</span>'
      + mk(renderSrc,'new') + mk(donorSrc,'donor')
      + '</div>';
  }
  window.itemBody = function(it){
    var m = it.meta_ || {};
    var renders = m.renders || {}, donors = m.donors || {};
    var facings = ['south','east','north'];
    var rows = facings.map(function(f){ return facingRow(f, renders[f], donors[f]); }).join('');
    var must = (m.must_show||[]).length
      ? '<details style="margin-top:6px" open><summary style="cursor:pointer;color:var(--accent);font-size:11.5px">canon &mdash; must show ('+m.must_show.length+')</summary>'
        + '<ul style="margin:4px 0 0 16px;padding:0;font-size:11.5px;color:#c3cad6">'
        + m.must_show.map(function(s){return '<li>'+esc(s)+'</li>';}).join('') + '</ul></details>'
      : '<div style="margin-top:6px;font-size:11px;color:var(--dim)">no canon reference entry for this creature</div>';
    var note = m.note_prefill ? '<div class="mark contested" style="display:block;margin-top:5px;padding:4px 8px">'+esc(m.note_prefill)+'</div>' : '';
    var canonLink = m.canon_dir ? '<div style="font-size:10.5px;color:var(--dim);margin-top:4px">canon: '+esc(m.canon_dir)+'</div>' : '';
    return '<div class="effect">'+esc(it.effect||'')+'</div>' + note
      + '<div style="margin-top:6px">' + rows + '</div>' + must + canonLink;
  };
})();
</script>
"""

html = TEMPLATE.read_text(encoding="utf-8")
html = html.replace(
    '<script id="CONFIG" type="application/json">\n{\n  "sheetId": "demo_sheet",\n  "title": "Review sheet",\n  "subtitle": "",\n  "briefHtml": "<p>Replace this with the brief. State it IN the page: the sheet outlives the conversation, and six weeks later nobody remembers what \\"serious tone\\" meant.</p>",\n  "criterion": "",\n  "invented": [],\n  "posture": { "mode": "whitelist", "explain": "" },\n  "options": [\n    { "key": "keep", "label": "Keep",  "hotkey": "1", "color": "#5ac37f", "counts": "in" },\n    { "key": "cut",  "label": "Cut",   "hotkey": "2", "color": "#e06c6c", "counts": "out" }\n  ],\n  "groupLabel": "group",\n  "media": false,\n  "decisionsFile": "decisions.json",\n  "decisionsPath": "",\n  "sheetPath": ""\n}\n</script>',
    f'<script id="CONFIG" type="application/json">\n{config_json}\n</script>'
)
html = html.replace(
    '<script id="ITEMS" type="application/json">\n[]\n</script>',
    f'<script id="ITEMS" type="application/json">\n{items_json}\n</script>'
)
# insert RENDER script before the closing of the commented-out example block area —
# simplest reliable anchor: right before "<script>\n\"use strict\";"
anchor = '<script>\n"use strict";'
assert anchor in html, "anchor not found"
html = html.replace(anchor, render_script + "\n" + anchor)

OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
OUT_HTML.write_text(html, encoding="utf-8")
print(f"wrote {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes)")

if not OUT_DECISIONS.is_file():
    prefilled = {it["id"]: {"decision": "keep", "prefill": "keep", "note": ""} for it in items}
    OUT_DECISIONS.write_text(json.dumps({
        "decisions": prefilled,
        "posture": "verdict",
        "criterion": config["criterion"],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote pre-filled {OUT_DECISIONS} ({len(prefilled)} rows)")
else:
    print(f"decisions file already exists, left untouched: {OUT_DECISIONS}")
