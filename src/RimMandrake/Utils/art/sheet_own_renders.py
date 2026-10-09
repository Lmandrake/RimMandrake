#!/usr/bin/env python3
"""sheet_own_renders.py -- the small "keep the own render?" sheet (2026-10-09).

    python3 sheet_own_renders.py            writes Transient/own_render_keep_sheet_2026-10-09.{html,decisions.json}
                                            + _img/ thumbnails + the ledger snapshot (infrastructure/state/art/sheets/)

Seven slots whose current picture is a shared, owner-kept one (the venomvine thicket picture copied onto five
venomvine plants; the Cistrel/Nubrith placeholder shared by both) and a finished OWN render for each. Columns:
A = what the game shows now, B = the finished own render. His keep on B names B's sha in the snapshot, which
`art.py ingest` turns into a ruling and `art.py install ... --ruling` can use. Installs nothing. The decisions
file is written only when absent (prefill, never his ruling). Thicket row (RM_VenomvineThicket) is not on it.
"""
from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402
from art_sheet import thumb  # noqa: E402

SKILL = Path.home() / ".claude" / "skills" / "review-sheets" / "assets"
SRC = L.REPO_ROOT / "src" / "RimMandrake"
ART = Path("/mnt/d/Luke/dev/_artpipe/_artsrc")
SHEET_ID = "own_render_keep_sheet_2026-10-09"
OUT = L.REPO_ROOT / "Transient" / f"{SHEET_ID}.html"

# row id, plant name, one-line description (from its def), current png, own render dir/name, texPath graphic
VV = "LeaningScrub/Textures/Things/Plant/RM_{n}VenomvineX/RM_{n}VenomvineX_a.png"
ROWS = [
    ("RM_StranglerVenomvine", "strangler venomvine",
     "Rope-thin black canes wound tight round a wall or tree; it does not strike, it holds and slowly tightens until the mortar gives.",
     "LeaningScrub/Textures/Things/Plant/RM_StranglerVenomvine/RM_StranglerVenomvine_a.png", "RM_StranglerVenomvine",
     "Things/Plant/RM_StranglerVenomvine"),
    ("RM_WeeperVenomvine", "weeper venomvine",
     "Every cane ends in a slow bead of tea-coloured venom; the ground under it is a ring of dark pools where nothing green grows.",
     "LeaningScrub/Textures/Things/Plant/RM_WeeperVenomvine/RM_WeeperVenomvine_a.png", "RM_WeeperVenomvine",
     "Things/Plant/RM_WeeperVenomvine"),
    ("RM_SleeperVenomvine", "dead venomvine (the sleeper)",
     "A grey, brittle, dead-looking snarl that is not dead: anything heavy that steps beside it wakes it, black and angry.",
     "LeaningScrub/Textures/Things/Plant/RM_SleeperVenomvine/RM_SleeperVenomvine_a.png", "RM_SleeperVenomvine",
     "Things/Plant/RM_SleeperVenomvine"),
    ("RM_SleeperAwakeVenomvine", "awakened venomvine (the sleeper, awake)",
     "What a sleeper becomes once something has stepped beside it: an ordinary, furious venomvine stand.",
     "LeaningScrub/Textures/Things/Plant/RM_SleeperAwakeVenomvine/RM_SleeperAwakeVenomvine_a.png", "RM_SleeperAwakeVenomvine",
     "Things/Plant/RM_SleeperAwakeVenomvine"),
    ("RM_LureVenomvine", "lure venomvine",
     "Pale, pearl-soft fruit hangs among the black canes, sweet enough to smell across a field; the fruit is the bait, the thicket the trap.",
     "LeaningScrub/Textures/Things/Plant/RM_LureVenomvine/RM_LureVenomvine_a.png", "RM_LureVenomvine",
     "Things/Plant/RM_LureVenomvine"),
    ("RM_Cistrel", "cistrel",
     "A chest-high cup of stiff waxy leaves (rust-red outside, pale inside) holding clear standing water: the only safe drinking water in the Fever Wood.",
     "FeverWood/Textures/Things/Plant/RM_Cistrel/RM_Cistrel_a.png", "regen_fw_cistrel_own_v1",
     "Things/Plant/RM_Cistrel/RM_Cistrel_a"),
    ("RM_Nubrith", "nubrith",
     "A low leathery dome on a squat stalk that glows a steady warm amber downward: the only natural light in the crown; a leaf that glows, not a mushroom.",
     "FeverWood/Textures/Things/Plant/RM_Nubrith/RM_Nubrith_a.png", "regen_fw_nubrith_own_v1",
     "Things/Plant/RM_Nubrith/RM_Nubrith_a"),
]

RENDER = r"""<script id="RENDER">
window.itemBody = it => `
<div class="effect"><b>${esc(it.name)}</b> &mdash; ${esc(it.desc)}</div>
<div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:8px">
  ${it.pics.map(p => `<figure style="margin:0;text-align:center">
     <div style="background:#2a1f16;border:1px solid #5a4320;border-radius:6px;padding:6px">
       <img src="${esc(p.src)}" width="256" height="256" style="display:block;image-rendering:auto" alt="${esc(p.cap)}"></div>
     <figcaption style="margin-top:4px"><b>${esc(p.letter)}</b> &middot; ${esc(p.cap)}<br><code>${esc(p.sha)}</code></figcaption></figure>`).join('')}
</div>`;
</script>
"""


def main() -> None:
    imgdir = OUT.parent / (OUT.stem + "_img")
    items, snap_rows = [], {}
    for rid, name, desc, cur_rel, render, graphic in ROWS:
        cur = SRC / cur_rel
        rend = ART / render / f"{render}.png"
        for p in (cur, rend):
            if not p.is_file():
                raise SystemExit(f"MISSING {p}")
        sc, sr = L.store_put_file(cur), L.store_put_file(rend)
        shared = "the copied thicket picture" if "Venomvine" in rid else "the shared Cistrel/Nubrith placeholder"
        pics = [{"letter": "A", "cap": f"IN GAME now ({shared})", "sha": sc[:12], "src": thumb(sc, imgdir, size=256)},
                {"letter": "B", "cap": "finished own render", "sha": sr[:12], "src": thumb(sr, imgdir, size=256)}]
        items.append({"id": rid, "group": "venomvine" if "Venomvine" in rid else "Fever Wood", "label": name,
                      "name": name, "desc": desc, "effect": desc, "pics": pics, "prefill": "B",
                      "thumbs": {}, "letters": ["A", "B"]})
        snap_rows[rid] = {"subject_key": name.split(" (")[0].replace(" ", "").lower(), "res": graphic,
                          "columns": {"A": {"single": sc}, "B": {"single": sr}},
                          "graphic_of": {"A": graphic, "B": graphic},
                          "labels": {"A": "IN GAME now", "B": "own render " + render}}
    snap = {"sheetId": SHEET_ID, "built": L.now(), "rows": snap_rows}
    snap["snapshotId"] = hashlib.sha1(json.dumps(snap_rows, sort_keys=True).encode()).hexdigest()[:16]
    sp = L.ledger_dir() / "sheets" / f"{SHEET_ID}.snapshot.json"
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(snap, indent=1, sort_keys=True))

    dec = OUT.with_suffix(".decisions.json")
    cfg = {
        "sheetId": SHEET_ID, "title": "Own renders vs shared pictures",
        "subtitle": f"{len(items)} plants - nothing is installed from this sheet",
        "briefHtml": ("<p>Seven plants currently show a picture that is shared with other plants: five venomvine kinds show the "
                      "copied <b>thicket</b> picture, and Cistrel and Nubrith show one shared Fever Wood placeholder. Each now has a "
                      "finished picture of its own. For each row: <b>A</b> = what the game shows now, <b>B</b> = the new own render. "
                      "Pick <b>B</b> to say &ldquo;keep the own render&rdquo; (that names the exact picture); pick <b>A</b> to keep what is there.</p>"
                      "<p>The thicket plant itself is not on this sheet and keeps its picture either way. Picking B only records your "
                      "ruling; the install is a separate step.</p>"),
        "criterion": "Ordered by plant, no ranking: A is the current picture, B the new own render. Looks and fit to the description are yours to judge.",
        "invented": ["B is pre-selected because the whole point of the renders was to give each plant a picture of its own; that is my default, not your ruling."],
        "posture": {"mode": "pick-one", "explain": "Each row: A keeps the current picture, B takes the own render, hold decides later."},
        "options": [{"key": "A", "label": "A keep current", "hotkey": "1", "color": "#98a2b3", "counts": "out", "bulk": False},
                    {"key": "B", "label": "B keep own render", "hotkey": "2", "color": "#5ac37f", "counts": "in", "bulk": False},
                    {"key": "hold", "label": "hold", "hotkey": "h", "color": "#e8b64c", "counts": "out"}],
        "groupLabel": "group", "media": True, "decisionsFile": dec.name, "decisionsPath": str(dec), "sheetPath": str(OUT),
    }
    tpl = (SKILL / "sheet_template.html").read_text()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<!-- ══ FILL IN #3 (optional)", RENDER + "\n<!-- ══ FILL IN #3 (optional)", 1)
    tpl = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", tpl, count=1, flags=re.S)
    OUT.write_text(tpl)
    if not dec.exists():
        dec.write_text(json.dumps({
            "sheetId": SHEET_ID, "posture": "pick-one", "snapshot": str(sp.relative_to(L.REPO_ROOT)),
            "snapshotId": snap["snapshotId"], "criterion": cfg["criterion"],
            "reviewStatus": {"state": "prefill", "by": None, "at": None, "evidence": "generated by sheet_own_renders.py; no human has ruled"},
            "decisions": {it["id"]: {"decision": "B", "note": "", "prefill": "B"} for it in items}}, indent=1))
    print("OK", OUT, len(items), "rows")


if __name__ == "__main__":
    main()
