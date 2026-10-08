#!/usr/bin/env python3
"""Leaning Scrub sheet (leaningscrub_sheet_2026-10-05) — the owner's 2026-10-08 redo / N-S / flight / "more X" notes as
artpipe jobs. Notes carried verbatim. Priority 0, ids `regen_ls2_*` (behind the 0vv_* venomvine jobs and every earlier
priority-0 job). Same anchoring as build_longshade_regen_jobs.py: the picked picture is the FIRST canon_reference
(its master jobs sit in failed/ — canon-gate — so they cannot be derive_from masters), the canon-library image second;
`canon` folds the entry's visual brief + Must show in."""
import json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
DEC = json.load(open(REPO / "infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json"))["decisions"]
SNAP = json.load(open(REPO / "infrastructure/state/art/sheets/leaningscrub_sheet_2026-10-05.snapshot.json"))["rows"]
CANON = REPO / "design/RimStarWars/canon_references"
STORE = Path("/mnt/d/Luke/dev/_artstore")
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
REG = ("leaning scrub register: a windswept arid scrubland plain of knee-high silver-green fuzz under a pale overcast "
       "sky, soft diffuse light; the subject keeps its own natural colours, no strong biome grade; bake NO cast shadow")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic, grounded and alien, naturalistic and zoologically "
         "believable, never cartoonish or cute; one centred subject on a fully transparent background.")
F3, NS = ["east", "south", "north"], ["south", "north"]
SAME = ("The FIRST attached image is the owner's accepted EAST (side) render of this very individual: draw the {v} view "
        "of exactly that animal -- same species, anatomy, colouring, markings, scale and painted style.")
POSES = {1: "wings raised high at the top of the upstroke", 2: "wings level and spread wide mid-downstroke",
         3: "wings swept fully down at the bottom of the downstroke", 4: "wings level and rising mid-upstroke"}
rows = []


def note(d):
    v = DEC[d]
    assert v.get("at"), d
    return v.get("note") or ""


def img(d, col, facing="east"):
    h = SNAP[d]["columns"][col][facing]
    p = STORE / h[:2] / f"{h}.png"
    assert p.is_file(), p
    return str(p)


def lead(n):
    return f'Owner\'s note, verbatim, overrides everything below: "{n}" ' if n else ""


def row(id, d, prompt, facings, texpath, canon=None, refs=(), cw=256, neutral=True):
    n = note(d)
    r = {"id": "regen_ls2_" + id, "rimflow_item_id": ITEM, "target_def": d, "prompt": lead(n) + prompt,
         "style_notes": STYLE, "canvas_w": cw, "canvas_h": cw, "facings": facings, "background": "transparent",
         "channel": "codex", "priority": 0, "target_texpath": texpath}
    if neutral:
        r["biome_neutral"] = True
    else:
        r["biome_register"] = REG
    if canon:
        r["canon"] = canon
    if refs:
        r["canon_reference"] = [str(x) for x in refs]
    if n:
        r["owner_note"] = n
    rows.append(r)


SW = "swanimals/"
# ---- Grank: N/S of the picked E, canon precisely ("look at the parent image")
GR = ("the canon saw-toothed grank of Naboo: a medium-sized, heavy-jawed predatory scavenger, gnarled and hunched, "
      "with a mouth of sharp saw-like teeth")
for v in NS:
    row("canon_grank_v1", "RSW_Grank", f"RimWorld creature sprite of the Star Wars canon grank, {v.upper()} view: {GR}. "
        + SAME.format(v=v) + " Follow the canon reference image PRECISELY. One animal, whole body, centred.", [v],
        SW + "Grank/Grank", canon="grank",
        refs=[img("RSW_Grank", "E"), CANON / "grank/wookieepedia_infobox.webp"])
# ---- Lothcat: N/S of the picked D, less cartoonish
LC = "the canon loth-cat of Lothal: a small, lithe, temperamental feline hunter with sharp teeth and claws"
for v in NS:
    row("canon_lothcat_v1", "RSW_Lothcat", f"RimWorld creature sprite of the Star Wars canon loth-cat, {v.upper()} "
        f"view: {LC}. " + SAME.format(v=v) + " Realistic and naturalistic, NOT cartoonish. One animal, whole body, "
        "centred.", [v], SW + "Lothcat/Lothcat_f", canon="lothcat",
        refs=[img("RSW_Lothcat", "D"), CANON / "lothcat/wookieepedia_canon_1.webp"])
# ---- Whisperbird: N/S + 4 flight frames from the picked F
WB = ("the canon whisper bird of Yavin 4: an energetic avian with radiant plumage, a long dexterous tongue, built "
      "for noiseless flight")
for v in NS:
    row("canon_whisperbird_v1", "RSW_Whisperbird", f"RimWorld creature sprite of the Star Wars canon whisper bird, "
        f"{v.upper()} view: {WB}. " + SAME.format(v=v) + " One animal, whole body, centred.", [v],
        SW + "Whisperbird/Whisperbird", canon="whisperbird",
        refs=[img("RSW_Whisperbird", "F"), CANON / "whisperbird/wookieepedia_alienarchive.jpg"])
for n in range(1, 5):
    row(f"canon_whisperbird_flying_{n}_v1", "RSW_Whisperbird",
        f"RimWorld creature FLYING animation frame {n} of 4 (whole-body flip-book frame, not a wing layer), the same "
        f"individual as the accepted standing render: {WB}. In flight, body level, legs tucked, {POSES[n]}. "
        + SAME.format(v="flying") + " One animal, whole body, centred.", F3,
        SW + f"Whisperbird/Whisperbird_Flying_{n}", canon="whisperbird",
        refs=[img("RSW_Whisperbird", "F"), CANON / "whisperbird/wookieepedia_alienarchive.jpg"])
# ---- Redo rows (two versions each so he has a choice), anchored on the column he named / picked
REDO = [("RSW_Convor", "convor", "D", "the canon convor of Wasskah: a short, plump-bodied mammavian, an excellent flier",
         SW + "Convor/Convor", CANON / "convor/wookieepedia_convoree_infobox.png",
         "The attached first image is column D, the one the owner called close: keep its anatomy but make it LESS CUTE -- "
         "a wild animal, not a pet toy."),
        ("RSW_Kybuck", "kybuck", "C", "the canon kybuck of Kashyyyk: a fast bipedal ungulate herd animal, tauntaun-like",
         SW + "Kybuck/Kybuck", CANON / "kybuck/wookieepedia_canon_1.webp",
         "The attached first image is the owner's 'almost there' render: keep it, and ADD the canon head-bone "
         "arrangement -- a single solid bone plate across the top of the head, mounted onto and joined with the horns."),
        ("RSW_Urusai", "urusai", "C", "the canon urusai of Tatooine: a winged reptavian carrion scavenger riding thermals",
         SW + "Urusai/Urusai", CANON / "urusai/wookieepedia_canon_1.webp",
         "The attached first image is the owner's pick; redraw it to match the canon imagery (second image)."),
        ]
for d, slug, col, desc, tp, cimg, how in REDO:
    for k in (1, 2):
        row(f"canon_{slug}_v{k + 1}", d, f"RimWorld creature sprite of the Star Wars canon {slug}: {desc}. {how} "
            "Follow the canon closely. One animal, whole body, centred.", F3, tp, canon=slug,
            refs=[img(d, col), cimg])
# ---- Zellik: more alien, anchored on the picked B (ours, not canon)
ZK = ("the zellik, a hunched, folded-umbrella-like scrubland creature that perches on boughs and turbine heads and "
      "opens out when the wind dies")
for k in (1, 2):
    row(f"x_zellik_v{k + 1}", "RM_Zellik", f"RimWorld creature sprite: {ZK}. The attached image is the owner's pick: "
        "keep its body plan but make it MORE ALIEN -- stranger proportions, unfamiliar anatomy, nothing Earth-like. "
        "One animal, whole body, centred.", F3, "Things/Pawn/Animal/RM_Zellik/RM_Zellik",
        refs=[img("RM_Zellik", "B")], neutral=False)
# ---- Scrap-nest bird: "Redo to canon very carefully." -- no canon-library entry exists; 'canon' = its own design text
SN = ("the scrap-nest bird, a shrubland scavenger with an oil-dark gloss and an eye for anything that catches the light; "
      "it nests deep in venomvine and lines the nest with stolen wire, lens-glass, chips of hull and beads of gold")
for k in (1, 2):
    row(f"x_scrapnestbird_v{k + 1}", "RSW_ScrapNestBird", f"RimWorld creature sprite: {SN}. Follow this description "
        "very carefully. One bird, whole body, centred.", F3,
        "Things/Pawn/Animal/RSW_ScrapNestBird/RSW_ScrapNestBird", refs=[img("RSW_ScrapNestBird", "A")], neutral=False)

out = Path(__file__).with_name("leaningscrub_regen_jobs.json")
out.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
print(len(rows), "rows ->", out)
