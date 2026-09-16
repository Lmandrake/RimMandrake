#!/usr/bin/env python3
"""Build the Pyrelands fauna+flora art review sheet.

Two generators, deliberately separate (review-sheets skill §7):
  the SHEET always rebuilds — it renders from the decisions file, so a fixed
  renderer can be picked up mid-review;
  the DECISIONS pre-fill is locked — it refuses to overwrite a file the sheet
  has touched unless --i-know-this-overwrites-the-owners-decisions is passed.

Usage:
    python3 src/RimMandrake/Utils/build_pyrelands_art_sheet.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "Transient", "pyrelands_art_review")
ART = os.path.join(OUT, "art")
TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
SHEET = os.path.join(OUT, "pyrelands_art.html")
DECISIONS = os.path.join(OUT, "pyrelands_art_decisions.json")
THUMB_PX = 256

U = "src/RimUtinni"
S = "src/RimStarWars"
P = "src/RimMandrake/Pyrelands/Textures/Things"

# id, group, label, [(facing, path)], prefill, effect
ROWS: list[tuple] = [
    # ── invented / non-canon fauna: ours outright ───────────────────────────
    ("razorjack", "Invented fauna (ours)", "Razorjack", [
        ("east", f"{U}/RazorjackArtOverride/Textures/Things/Pawn/Animal/AA_Razorjack/AA_Razorjack_east.png"),
        ("north", f"{U}/RazorjackArtOverride/Textures/Things/Pawn/Animal/AA_Razorjack/AA_Razorjack_north.png"),
        ("south", f"{U}/RazorjackArtOverride/Textures/Things/Pawn/Animal/AA_Razorjack/AA_Razorjack_south.png"),
    ], "keep", "Fire-follower recast. Full painterly set, deployed. No structural defect found."),

    ("barbslinger", "Invented fauna (ours)", "Barbslinger", [
        ("east", f"{U}/BarbslingerArtOverride/Textures/Things/Pawn/Animal/AA_BarbSlinger/AA_BarbSlinger_east.png"),
        ("north", f"{U}/BarbslingerArtOverride/Textures/Things/Pawn/Animal/AA_BarbSlinger/AA_BarbSlinger_north.png"),
        ("south", f"{U}/BarbslingerArtOverride/Textures/Things/Pawn/Animal/AA_BarbSlinger/AA_BarbSlinger_south.png"),
    ], "keep", "Ash-grazer. South landed in the 09-14 facing wave, completing the set."),

    ("firewasp", "Invented fauna (ours)", "FireWasp", [
        ("east", f"{U}/FireWaspArtOverride/Textures/Things/Pawn/Animal/AA_FireWasp/AA_FireWasp_east.png"),
        ("north", f"{U}/FireWaspArtOverride/Textures/Things/Pawn/Animal/AA_FireWasp/AA_FireWasp_north.png"),
        ("south", f"{U}/FireWaspArtOverride/Textures/Things/Pawn/Animal/AA_FireWasp/AA_FireWasp_south.png"),
    ], "keep", "Full painterly set. Smallest canvases in the roster — check it reads at play zoom."),

    ("boomsnake", "Invented fauna (ours)", "Boomsnake", [
        ("east", f"{U}/BoomsnakeArtOverride/Textures/Things/Pawn/Animal/Reptile/Boomsnake/Boomsnake_east.png"),
        ("north", f"{U}/BoomsnakeArtOverride/Textures/Things/Pawn/Animal/Reptile/Boomsnake/Boomsnake_north.png"),
        ("south", f"{U}/BoomsnakeArtOverride/Textures/Things/Pawn/Animal/Reptile/Boomsnake/Boomsnake_south.png"),
    ], "keep", "N/S landed in the 09-14 facing wave. The item file still lists these as missing."),

    ("mantistanis", "Invented fauna (ours)", "Mantistanis", [
        ("east", f"{U}/MantistanisArtOverride/Textures/Things/Pawn/Animal/Megafauna/Insectoid/GR_Mantistanis_east.png"),
        ("north", f"{U}/MantistanisArtOverride/Textures/Things/Pawn/Animal/Megafauna/Insectoid/GR_Mantistanis_north.png"),
        ("south", f"{U}/MantistanisArtOverride/Textures/Things/Pawn/Animal/Megafauna/Insectoid/GR_Mantistanis_south.png"),
    ], "keep", "South landed in the 09-14 facing wave. Item file lists it as missing — stale."),

    ("firehawk", "Invented fauna (ours)", "FireHawk", [
        ("east", f"{U}/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_east.png"),
        ("north", f"{U}/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_north.png"),
        ("south", f"{U}/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_south.png"),
    ], "keep", "Ours, was a lone east sprite. Now a full set and deployed."),

    ("furnacebeast", "Invented fauna (ours)", "FurnaceBeast", [
        ("east", f"{U}/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FurnaceBeast/FurnaceBeast_east.png"),
        ("north", f"{U}/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FurnaceBeast/FurnaceBeast_north.png"),
        ("south", f"{U}/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FurnaceBeast/FurnaceBeast_south.png"),
    ], "keep", "Ours, was a lone east sprite. Now a full set and deployed."),

    ("greengoo", "Invented fauna (ours)", "GreenGoo", [
        ("east", f"{U}/GreenGooArtOverride/Textures/Things/Pawn/Animal/AA_GreenGoo/AA_GreenGoo_east.png"),
        ("north", f"{U}/GreenGooArtOverride/Textures/Things/Pawn/Animal/AA_GreenGoo/AA_GreenGoo_north.png"),
        ("south", f"{U}/GreenGooArtOverride/Textures/Things/Pawn/Animal/AA_GreenGoo/AA_GreenGoo_south.png"),
    ], "keep", "You praised this one. Faceless slime: no rear cue is possible, so the facing law may not apply."),

    # ── SW-canon fauna ──────────────────────────────────────────────────────
    ("orray", "SW-canon fauna", "Orray", [
        ("east", f"{S}/OrrayArtOverride/Textures/swanimals/Orray/Orray_east.png"),
        ("north", f"{S}/OrrayArtOverride/Textures/swanimals/Orray/Orray_north.png"),
        ("south", f"{S}/OrrayArtOverride/Textures/swanimals/Orray/Orray_south.png"),
    ], "rerender", "FACING BROKEN: north is a side profile, not a rear view. Confirmed by eye tonight."),

    ("anooba_f", "SW-canon fauna", "Anooba (female)", [
        ("east", f"{S}/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_f_east.png"),
        ("north", f"{S}/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_f_north.png"),
        ("south", f"{S}/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_f_south.png"),
    ], "rerender", "FACING BROKEN: north is a full frontal face, teeth to camera. Confirmed by eye tonight."),

    ("anooba_m", "SW-canon fauna", "Anooba (male)", [
        ("east", f"{S}/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_m_east.png"),
        ("north", f"{S}/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_m_north.png"),
        ("south", f"{S}/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_m_south.png"),
    ], "rerender", "DUPLICATE: byte-identical to the female in all three facings. No male art exists."),

    ("iriaz", "SW-canon fauna", "Iriaz", [
        ("east", f"{S}/IriazArtOverride/Textures/swanimals/Iriaz/Iriaz_east.png"),
        ("north", f"{S}/IriazArtOverride/Textures/swanimals/Iriaz/Iriaz_north.png"),
        ("south", f"{S}/IriazArtOverride/Textures/swanimals/Iriaz/Iriaz_south.png"),
    ], "", "UNDECIDED ON PURPOSE — identity unruled: canon library says four-legged Dantooine antelope, this art is the two-legged Dathomir read."),

    ("nuna_f", "SW-canon fauna", "Nuna (female)", [
        ("east", f"{S}/NunaArtOverride/Textures/swanimals/Nuna/Nuna_f_east.png"),
        ("north", f"{S}/NunaArtOverride/Textures/swanimals/Nuna/Nuna_f_north.png"),
        ("south", f"{S}/NunaArtOverride/Textures/swanimals/Nuna/Nuna_f_south.png"),
    ], "keep", "The real female set — full painterly, deployed."),

    ("nuna_m", "SW-canon fauna", "Nuna (male)", [
        ("east", f"{S}/NunaArtOverride/Textures/swanimals/Nuna/Nuna_m_east.png"),
        ("north", f"{S}/NunaArtOverride/Textures/swanimals/Nuna/Nuna_m_north.png"),
        ("south", f"{S}/NunaArtOverride/Textures/swanimals/Nuna/Nuna_m_south.png"),
    ], "rerender", "DUPLICATE: north+south are byte-identical to the female. Only east is real male art."),

    ("zeer", "SW-canon fauna", "Zeer", [
        ("east", f"{S}/ZeerArtOverride/Textures/swanimals/Zeer/Zeer_east.png"),
        ("north", f"{S}/ZeerArtOverride/Textures/swanimals/Zeer/Zeer_north.png"),
        ("south", f"{S}/ZeerArtOverride/Textures/swanimals/Zeer/Zeer_south.png"),
    ], "keep", "Full painterly set, deployed. drawSize 4.0 measured from SWAC adult lifeStages."),

    ("dalgo", "SW-canon fauna", "Dalgo", [
        ("east", f"{S}/DalgoArtOverride/Textures/swanimals/Dalgo/Dalgo_east.png"),
        ("north", f"{S}/DalgoArtOverride/Textures/swanimals/Dalgo/Dalgo_north.png"),
        ("south", f"{S}/DalgoArtOverride/Textures/swanimals/Dalgo/Dalgo_south.png"),
    ], "keep", "Full painterly set, deployed."),

    ("gizka", "SW-canon fauna", "Gizka", [
        ("east", f"{S}/GizkaArtOverride/Textures/swanimals/Gizka/Gizka_east.png"),
        ("north", f"{S}/GizkaArtOverride/Textures/swanimals/Gizka/Gizka_north.png"),
        ("south", f"{S}/GizkaArtOverride/Textures/swanimals/Gizka/Gizka_south.png"),
    ], "keep", "Full set. You raised its ecosystem grain 0.3 to 1.0 — the pyramid law puts it on top."),

    ("gizka_w", "SW-canon fauna", "Gizka (wild variant)", [
        ("east", f"{S}/GizkaArtOverride/Textures/swanimals/Gizka/GizkaW_east.png"),
        ("north", f"{S}/GizkaArtOverride/Textures/swanimals/Gizka/GizkaW_north.png"),
        ("south", f"{S}/GizkaArtOverride/Textures/swanimals/Gizka/GizkaW_south.png"),
    ], "keep", "PARTIAL DUPLICATE: differs from tame Gizka on east only; north+south are the same file. Intended?"),

    # ── outside the pipeline ────────────────────────────────────────────────
    ("bolotaur", "Outside our pipeline", "Bolotaur", [
        ("east", f"{S}/SWBestiary/Textures/swanimals/Bolotaur/Bolotaur_east.png"),
        ("north", f"{S}/SWBestiary/Textures/swanimals/Bolotaur/Bolotaur_north.png"),
        ("south", f"{S}/SWBestiary/Textures/swanimals/Bolotaur/Bolotaur_south.png"),
    ], "keep", "NOT OURS: donor SWBestiary art, ~7 KB per facing, zero registry records. You already ruled it DONE."),

    ("gualaar", "Outside our pipeline", "Gualaar", [],
     "keep", "NO ART IN THIS REPO — lives in a donor mod outside src/, so nothing can be shown here. You already ruled it DONE."),

    ("boomalope", "Outside our pipeline", "Boomalope", [],
     "needsart", "THE ONE GENUINE HOLE: no sprite anywhere in the repo and no registry record. Reskin rides the in-joke lane."),

    # ── flora ───────────────────────────────────────────────────────────────
    ("embergrass", "Flora (ours)", "EmberGrass A/B/C", [
        ("A", f"{P}/Plant/RM_FE_EmberGrass/RM_FE_EmberGrassA.png"),
        ("B", f"{P}/Plant/RM_FE_EmberGrass/RM_FE_EmberGrassB.png"),
        ("C", f"{P}/Plant/RM_FE_EmberGrass/RM_FE_EmberGrassC.png"),
    ], "keep", "Three painterly variants, deployed. The only flora that shipped in wave 2."),

    ("embergrass_leafless", "Flora (ours)", "EmberGrass leafless", [
        ("A", f"{P}/Plant/RM_FE_EmberGrass_Leafless/RM_FE_EmberGrass_LeaflessA.png"),
    ], "keep", "The post-burn state. One variant only — does one read as enough after a fire sweep?"),

    ("quickgrass", "Flora (ours)", "Quickgrass A/B", [
        ("A", f"{P}/Plant/RM_FE_Quickgrass/RM_FE_QuickgrassA.png"),
        ("B", f"{P}/Plant/RM_FE_Quickgrass/RM_FE_QuickgrassB.png"),
    ], "keep", "Mature pair. Item file lists Quickgrass as not started — stale, it rendered 09-14."),

    ("quickgrass_stages", "Flora (ours)", "Quickgrass growth stages", [
        ("sprout A", f"{P}/Plant/RM_FE_QuickgrassStages/RM_FE_Quickgrass_Sprout_A.png"),
        ("sprout B", f"{P}/Plant/RM_FE_QuickgrassStages/RM_FE_Quickgrass_Sprout_B.png"),
        ("half A", f"{P}/Plant/RM_FE_QuickgrassStages/RM_FE_Quickgrass_Half_A.png"),
        ("half B", f"{P}/Plant/RM_FE_QuickgrassStages/RM_FE_Quickgrass_Half_B.png"),
    ], "keep", "Sprout and half stages — this is what EXPLOSIVE_PLANT_GROWTH_1 animates through."),

    ("quickgrass_leafless", "Flora (ours)", "Quickgrass leafless", [
        ("A", f"{P}/Plant/RM_FE_Quickgrass_Leafless/RM_FE_Quickgrass_LeaflessA.png"),
    ], "keep", "The post-burn state. One variant only."),

    ("scorchfruit", "Flora (ours)", "ScorchFruit pod + item", [
        ("pod (plant)", f"{P}/Plant/RM_FE_ScorchFruitPod.png"),
        ("item", f"{P}/Item/Resource/RM_FE_ScorchFruit.png"),
    ], "keep", "Plant and its harvested resource. Check the two read as the same thing."),

    ("fulgurite", "Flora (ours)", "Fulgurite", [
        ("item", f"{P}/Item/Resource/RM_FE_Fulgurite.png"),
    ], "keep", "Resource item only — lightning-fused sand. No plant sprite by design."),
]

OPTIONS = [
    {"key": "keep", "label": "Keep", "hotkey": "k", "counts": "in",
     "hint": "ships as it is"},
    {"key": "rerender", "label": "Re-render", "hotkey": "r", "counts": "out",
     "hint": "right creature, art must be redone"},
    {"key": "cut", "label": "Cut", "hotkey": "x", "counts": "out",
     "hint": "should not be in the biome at all"},
    {"key": "needsart", "label": "Needs art", "hotkey": "n", "counts": "out",
     "hint": "nothing exists yet"},
]

CONFIG = {
    "title": "Pyrelands art — fauna & flora re-ruling",
    "decisionsFile": os.path.basename(DECISIONS),
    "brief": (
        "Every render made under the cartoonish lawset is back on the table — your ruling of "
        "2026-09-14 restored the painterly style and put the whole 09-12 to 09-14 era up for "
        "re-examination. This is that pass for Pyrelands, the one biome being taken all the way "
        "so you can walk it.\n\n"
        "Default is KEEP: art ships as it is unless you mark it otherwise. Three facings are "
        "shown per creature (east / north / south) because the facing law — north faces away, "
        "south faces toward — is the defect that keeps recurring, and it is only visible with "
        "the set side by side.\n\n"
        "Sprites are shown at 256 px, which is larger than the game draws them. If something "
        "looks fine here and wrong in game, that gap is the thing worth telling me about."
    ),
    "criterion": (
        "Pre-filled on PROVENANCE — whether a sprite came through the restored painterly wave "
        "and whether it has a structural defect I could prove (wrong facing, duplicate file). "
        "That ranks pipeline-currency, NOT beauty. I have not judged whether any of these are "
        "good art, and the rows you overrule are the ones worth having built this for."
    ),
    "posture": {
        "mode": "blacklist",
        "note": "Default KEEP. Only rows you mark re-render / cut / needs-art are acted on.",
    },
    "invented": [
        "Pre-filled 'keep' for every row that came through the 09-14 painterly wave with no "
        "provable structural defect — that is a provenance judgement, not an art judgement. I "
        "looked at exactly two sprites tonight (Anooba north, Orray north) to confirm the facing "
        "bug; every other 'keep' is unseen by me.",
        "Split Anooba f/m, Nuna f/m and Gizka/GizkaW into separate rows because the files are "
        "separate — even though three of those turned out to be duplicates.",
        "Showed the ArtOverride sprite and hid the older SWBestiary donor copy on every row that "
        "has both, assuming the override is what the game binds. Bolotaur is the exception: "
        "SWBestiary is all it has.",
        "Grouped flora by plant with growth stages on one row, rather than one row per PNG.",
        "Treated the registry's legibility pass/fail as carrying no weight, because your ruling "
        "demoted that gate to advisory. Nothing here is pre-filled on it.",
    ],
    "sources": [
        "infrastructure/artpipe/registry.jsonl (1810 records, MEASURED)",
        "infrastructure/state/items/PYRELANDS_CREATURE_RERENDER_1.md (roster + walk verdicts)",
        "infrastructure/state/items/ART_PAINTERLY_RESTORATION_1.md (the ruling)",
        "sha256 of every sprite pair suspected of being a duplicate",
    ],
}

RENDER_JS = r"""
// The template already prints the label and a zoomable east thumb; this adds the three
// facings side by side, because the facing law (N away / S toward) is only checkable with
// the set together. Images are EAGER on purpose: lazy ones never entered the viewport and
// so never loaded at all. Each facing carries data-zoom so the template's existing
// click-to-zoom delegation ([data-zoom]) picks it up for free.
window.itemBody = it => {
  const facs = (it.imgs || []).map(f =>
    `<figure class="fac" data-zoom="${esc(f.src)}" data-cap="${esc(it.label||it.id)} \u2014 ${esc(f.facing)}">`
    + `<img src="${esc(f.src)}" alt="${esc(it.label||it.id)} ${esc(f.facing)}" decoding="async">`
    + `<figcaption>${esc(f.facing)}</figcaption></figure>`
  ).join("");
  const gallery = facs
    ? `<div class="facings">${facs}</div>`
    : `<div class="facings noart">no sprite in this repo \u2014 nothing to look at</div>`;
  const flag = (it.flag || "").trim();
  const badge = flag
    ? `<div class="flagline"><span class="flag flag-${esc(it.flagKind||'note')}">${esc(flag)}</span></div>`
    : "";
  return badge + gallery + `<div class="effect">${esc(it.effect || "")}</div>`;
};
"""

RENDER_CSS = r"""
<style id="ARTSHEET_CSS">
  /* --rowh feeds contain-intrinsic-size; image rows are tall, so raise it rather than
     setting auto, which would invalidate the declaration. */
  :root{ --rowh:250px; }
  .flagline{ margin:2px 0 6px; }
  .facings{ display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; margin:2px 0 8px; }
  .facings.noart{ color:var(--dim); font-style:italic; padding:12px 0; }
  .fac{ margin:0; text-align:center; cursor:zoom-in; }
  .fac img{
    width:150px; height:150px; object-fit:contain; display:block;
    image-rendering:pixelated;
    background:
      linear-gradient(45deg,#3a3f47 25%,transparent 25%,transparent 75%,#3a3f47 75%),
      linear-gradient(45deg,#3a3f47 25%,#2c3037 25%,#2c3037 75%,#3a3f47 75%);
    background-size:16px 16px; background-position:0 0,8px 8px;
    border:1px solid var(--line); border-radius:8px;
  }
  .fac:hover img{ border-color:var(--accent); }
  .fac figcaption{ font:11px ui-monospace,monospace; color:var(--dim); margin-top:4px;
    text-transform:uppercase; letter-spacing:.6px; }
  .flag{ font:11px/1.7 ui-monospace,monospace; padding:1px 9px; border-radius:999px;
    border:1px solid; text-transform:uppercase; letter-spacing:.5px; }
  .flag-facing{ color:#ffd9d9; border-color:var(--bad);  background:#3a1e1e; }
  .flag-dupe  { color:#ffe9c2; border-color:var(--warn); background:#3a2f18; }
  .flag-ruling{ color:#d8e6ff; border-color:var(--info); background:#1d2839; }
  .flag-noart { color:#e6d8ff; border-color:#9a7bd8;     background:#2a2138; }
  .flag-donor { color:#d9f2e4; border-color:var(--ok);   background:#1b2f24; }
</style>
"""

FLAGS = {
    "orray":      ("facing law broken", "facing"),
    "anooba_f":   ("facing law broken", "facing"),
    "anooba_m":   ("duplicate of female", "dupe"),
    "nuna_m":     ("duplicate of female", "dupe"),
    "gizka_w":    ("partial duplicate", "dupe"),
    "iriaz":      ("your ruling owed", "ruling"),
    "boomalope":  ("no art exists", "noart"),
    "gualaar":    ("no art in repo", "noart"),
    "bolotaur":   ("donor art, not ours", "donor"),
}


def stage_art(thumb_px: int) -> dict[str, str]:
    """Copy each sprite to art/ as a downscaled thumbnail. Returns src-path -> rel-path."""
    from PIL import Image
    os.makedirs(ART, exist_ok=True)
    mapping: dict[str, str] = {}
    for row in ROWS:
        for _facing, rel in row[3]:
            src = os.path.join(REPO, rel)
            if not os.path.isfile(src):
                print(f"  MISSING SOURCE: {rel}", file=sys.stderr)
                continue
            flat = rel.replace("/", "__")
            dst = os.path.join(ART, flat)
            im = Image.open(src).convert("RGBA")
            if max(im.size) > thumb_px:
                im.thumbnail((thumb_px, thumb_px), Image.Resampling.LANCZOS)
            im.save(dst)
            mapping[rel] = f"art/{flat}"
    return mapping


def build_items(mapping: dict[str, str]) -> list[dict]:
    items = []
    for rid, group, label, facings, prefill, effect in ROWS:
        imgs = [{"facing": f, "src": mapping[r]} for f, r in facings if r in mapping]
        flag, kind = FLAGS.get(rid, ("", ""))
        it = {
            "id": rid,
            "group": group,
            "label": label,
            "effect": effect,
            "prefill": prefill,
            "imgs": imgs,
        }
        if imgs:
            it["thumb"] = imgs[0]["src"]
        if flag:
            it["flag"], it["flagKind"] = flag, kind
        items.append(it)
    return items


def write_sheet(items: list[dict]) -> None:
    html = open(TEMPLATE, encoding="utf-8").read()

    def swap(doc: str, sid: str, body: str) -> str:
        # Anchored to line start: the template's header comment contains the LITERAL text
        # `<script id="CONFIG" ...>` (indented), and an unanchored match ate everything from
        # that comment to the real block's closing tag — taking the whole stylesheet with it.
        pat = re.compile(r'(^<script id="%s"[^>]*>)(.*?)(^</script>)' % sid, re.S | re.M)
        if not pat.search(doc):
            raise SystemExit(f"template has no <script id={sid}> block at line start")
        return pat.sub(lambda m: m.group(1) + body + m.group(3), doc, count=1)

    html = swap(html, "CONFIG", "\n" + json.dumps(CONFIG, indent=2) + "\n")
    html = swap(html, "ITEMS", "\n" + json.dumps(items, indent=1) + "\n")
    # The template's <script id="RENDER"> ships INSIDE an HTML comment (it is optional), so
    # anything written there is inert text the browser never runs — measured, and invisible to
    # every scripted check. Inject a live <script> in head instead; card() reads
    # window.itemBody at render time, so defining it before the main script is enough.
    injected = RENDER_CSS + "<script id=\"ARTSHEET_RENDER\">" + RENDER_JS + "</script>\n"
    if "</head>" not in html:
        raise SystemExit("template has no </head> to inject into")
    html = html.replace("</head>", injected + "</head>", 1)
    os.makedirs(OUT, exist_ok=True)
    with open(SHEET, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  sheet   {SHEET}")


def write_decisions(items: list[dict], force: bool) -> None:
    if os.path.isfile(DECISIONS):
        try:
            cur = json.load(open(DECISIONS, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cur = {}
        # Guard on the keys the SIDECAR stamps and a pre-fill generator can never emit.
        # "touchedBySheet" is DERIVED by the sidecar for --status and is not present on
        # disk — guarding on it silently never fired, which is how a generator overwrites
        # the owner's verdicts with its own guesses.
        stamped = [k for k in ("savedBy", "writeCount", "savedAt") if k in cur]
        if stamped and not force:
            print(f"  decisions REFUSED: the sheet has written to this file "
                  f"(sidecar keys present: {', '.join(stamped)}) — his verdicts would be "
                  f"overwritten by my guesses.")
            print("  pass --i-know-this-overwrites-the-owners-decisions if that is truly intended.")
            return
    doc = {
        "sheet": os.path.basename(SHEET),
        "posture": CONFIG["posture"]["mode"],
        "postureNote": CONFIG["posture"]["note"],
        "criterion": CONFIG["criterion"],
        "options": [o["key"] for o in OPTIONS],
        "decisions": {
            it["id"]: {"value": it["prefill"], "prefilled": True}
            for it in items if it["prefill"]
        },
    }
    with open(DECISIONS, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    print(f"  prefill {DECISIONS}  ({len(doc['decisions'])}/{len(items)} rows)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--thumb-px", type=int, default=THUMB_PX)
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions",
                    dest="force", action="store_true")
    args = ap.parse_args()

    CONFIG["options"] = OPTIONS
    print("staging art…")
    mapping = stage_art(args.thumb_px)
    items = build_items(mapping)
    print(f"  {len(mapping)} sprites staged, {len(items)} rows")
    write_sheet(items)
    write_decisions(items, args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
