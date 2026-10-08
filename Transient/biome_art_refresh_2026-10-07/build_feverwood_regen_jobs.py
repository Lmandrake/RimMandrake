#!/usr/bin/env python3
"""Build fill_queue rows for the owner's 2026-10-08 (UTC) Feverwood sheet rulings. Notes carried verbatim.

Same method as build_miasma_regen_jobs.py. Ids start `regen_fw_` so that, at equal priority, they sort
(and are claimed) after every `miasma_*` job — the daemon orders pending by (priority, filename).
"""
import json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
DEC = json.load(open(REPO / "Transient/biome_ffar/feverwood_sheet_2026-10-05.decisions.json"))["decisions"]
SNAP = json.load(open(REPO / "infrastructure/state/art/sheets/feverwood_sheet_2026-10-05.snapshot.json"))["rows"]
CANON = REPO / "design/RimStarWars/canon_references"
STORE = Path("/mnt/d/Luke/dev/_artstore")
PRI = 0
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
REG = ("fever wood register: a drowned jungle where colossal fused trunks have stilled the swamp into black "
       "unrippled mirror pools over deep mud; living-wood boughways high above; a permanent green canopy "
       "ceiling, hot wet gloom, dim green-gold filtered light, wet dark bark")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic, grounded and alien, naturalistic and "
         "botanically/zoologically believable, never cartoonish; one centred subject on a fully transparent "
         "background.")
F3 = ["east", "south", "north"]
P = "regen_fw_"


def note(d):
    h = DEC[d]
    assert h.get("at"), d
    return h["note"]


def img(d, col, facing=None):
    v = SNAP[d]["columns"][col]
    h = v[facing] if facing else next(iter(v.values()))
    p = STORE / h[:2] / f"{h}.png"
    assert p.is_file(), p
    return str(p)


def lead(n):
    return f'Owner\'s note, verbatim, overrides everything below: "{n}" ' if n else ""


rows = []
# adult (largest) drawSize from src/ PawnKindDefs; Thornbug is the owner's "three cells wide".
DS = {"RSW_Fambaa": 8.0, "RSW_Gelagrub": 4.0, "RM_Brathek": 1.5, "RM_Chellow": 0.65, "RM_Drommath": 0.8,
      "RM_Murrelith": 0.7, "RM_Thornbug": 3.0}


def row(id, d, prompt, cw, facings=F3, **kw):
    n = kw.pop("owner_note", None)
    if n is None:
        n = note(d)
    r = {"id": P + id, "rimflow_item_id": ITEM, "target_def": d, "prompt": lead(n) + prompt,
         "style_notes": STYLE, "canvas_w": cw, "canvas_h": cw, "facings": facings,
         "background": "transparent", "channel": "codex", "priority": PRI, "biome_register": REG}
    if n:
        r["owner_note"] = n
    if d in DS:
        r["drawsize"] = DS[d]
    if "derive_from" in kw and not kw["derive_from"].startswith(("feverwood_",)):
        kw["derive_from"] = P + kw["derive_from"]
    r.update(kw)
    rows.append(r)


# ---- canon ------------------------------------------------------------------------------------------
row("canon_fambaa_v1", "RSW_Fambaa",
    "RimWorld creature sprite of the Star Wars canon fambaa, drawn from the attached canon field-guide image: "
    "a huge broad low-slung amphibian with thick pillar-like legs and broad feet with wide splayed toes, "
    "YELLOW scaled reptilian hide covered in GREEN spots/mottling, a pale cream underside and inner legs, a "
    "LONG neck carried straight FORWARD (not upward) ending in a wide-mouthed head with a single curved tusk "
    "jutting from the lower jaw, and a long tapering cartilage tail. Wild, no saddle or harness. One animal, "
    "whole body, centred.", 1024, canon="fambaa",
    canon_reference=[str(CANON / "fambaa/wookieepedia_fieldguide.jpg"), img("RSW_Fambaa", "D", "east")],
    target_texpath="swanimals/Fambaa/Fambaa")
row("canon_gelagrub_v1", "RSW_Gelagrub",
    "RimWorld creature sprite of the Star Wars canon gelagrub (larval form), drawn to match the attached canon "
    "Databank image precisely: a fat soft caterpillar/grub body, long and low, with a blunt rounded "
    "headless-looking front and no neck, tapering to a smaller rump; a bulbous wrinkled face with a wide "
    "drooping lipless dark mouth and two round black eyes stacked one above the other on the side of a raised "
    "wrinkled brow mound; rows of short thick soft blob-ended leg-stumps under a low-hung belly; dark "
    "teal/grey-green skin with a glossy translucent segmented bright cobalt-blue back; smooth wet gelatinous "
    "skin, no fur, no hard shell. Big enough to be ridden. No rider. One animal, whole body, centred.", 512,
    canon="gelagrub", canon_reference=[str(CANON / "gelagrub/wookieepedia_canon_1.webp")],
    canon_na=[6], canon_na_reason="scale is the def's drawSize (4.0); no rider is drawn on a wild-animal sprite",
    target_texpath="swanimals/Gelagrub/Gelagrub")

# ---- invented fauna -----------------------------------------------------------------------------------
row("brathek_v2", "RM_Brathek",
    "RimWorld creature sprite, the brathek: a WOOD-BORING LARVA that rasps its way into living trees. A heavy "
    "ringed grub the length of a forearm, pale, wet and soft, with a dark hard rasping head-capsule broader "
    "than the body -- a blunt rounded scraping plate edged with file-like ridges and small mandibles, NOT a "
    "drill, cone or spike -- and a row of little stubby gripper peg legs along its underside that it braces "
    "against the gallery walls. One animal, whole body, centred.", 256)

cn = note("RM_Chellow")
row("chellow_v2_south", "RM_Chellow",
    "Edit this chellow sprite, SOUTH-facing: keep the body, plumage, legs, bare wrinkled head and glowing "
    "translucent throat-fan exactly, but REMOVE THE BEAK entirely: the mouth is a lipless soft whistling flap "
    "of bare skin at the front of the face. Fully transparent background.", 256, facings=[],
    derive_from="feverwood_chellow_south")
row("chellow_v2", "RM_Chellow",
    "The chellow, the same individual as the accepted beakless south render: squat and round, no feathers on "
    "the head (bare wrinkled skin), a translucent veined throat-fan lit faintly from behind, and NO BEAK -- a "
    "lipless whistling flap of skin for a mouth. Redraw it facing the requested direction (east = side "
    "profile). One bird, whole body, centred.", 256, facings=["east", "north"], derive_from="chellow_v2_south")

dn = note("RM_Drommath")
row("drommath_v2", "RM_Drommath",
    "The drommath, generalising the accepted SOUTH render to the requested facing: the same taut grey "
    "inflating sac-creature, same palette, mouth and gripping legs, redrawn facing the requested direction. "
    "Only the animal itself is drawn: no branch, bark, perch or any wood anywhere in the image. One animal, "
    "whole body, centred.", 256, facings=["east", "north"], derive_from="feverwood_drommath_south")

for f in F3:
    row(f"murrelith_v2_{f}", "RM_Murrelith",
        f"Edit this murrelith sprite, {f.upper()}-facing: keep the bird's body, pose and silhouette, but make the "
        "long trailing ribbon-streamers beautifully translucent, glowing rainbow/iridescent colours, regal and "
        "elegant, hanging and twisting. Fully transparent background.", 256, facings=[],
        derive_from=f"feverwood_murrelith_{f}")

# whole-body directional flight flip-book (no wing layer), derived from the new standing east master.
POSES = {1: "wings raised high in a V at the top of the upstroke",
         2: "wings level and spread wide mid-downstroke",
         3: "wings swept fully down at the bottom of the downstroke",
         4: "wings level and rising mid-upstroke"}
for d, slug, base, desc in (
        ("RM_Chellow", "chellow", "chellow_v2_east",
         "squat round bird, bare wrinkled head, translucent throat-fan, lipless skin-flap mouth, no beak"),
        ("RM_Murrelith", "murrelith", "murrelith_v2_east",
         "long-tailed bird trailing translucent rainbow ribbon-streamers instead of vaned quills")):
    for n, pose in POSES.items():
        row(f"{slug}_flying_{n}_v1", d,
            f"RimWorld creature FLYING animation frame {n} of 4 (whole-body flip-book frame, not a wing layer) of "
            f"the {slug}, the same individual as the accepted standing render: {desc}. In flight, body level, "
            f"legs tucked, {pose}. One bird, whole body, centred.", 256, owner_note="",
            derive_from=base, target_texpath=f"Things/Pawn/Animal/RM_FeverWoodBirds/RM_{slug.title()}_Flying_{n}")

row("thornbug_v2", "RM_Thornbug",
    "RimWorld creature sprite, the thornbug, design based on the attached render (good concept): a great "
    "thorn-shaped insect clamped flush to bark, its body one long curved armoured thorn, secreting sweet "
    "nectar -- now a BIG animal, about three cells wide, so the body is long and massive with fine realistic "
    "chitin detail. Only the insect is drawn, no bark. One animal, whole body, centred.", 512,
    canon_reference=[img("RM_Thornbug", "A", "east")])

# ---- plants: redo, 3 fresh realistic variants ---------------------------------------------------------
DESC = {}
import xml.etree.ElementTree as ET
for el in ET.parse(REPO / "src/RimMandrake/FeverWood/Defs/ThingDefs_Plants/RM_FeverWoodFlora.xml").getroot():
    if el.findtext("defName"):
        DESC[el.findtext("defName")] = " ".join((el.findtext("description") or "").split())
for el in ET.parse(REPO / "src/RimMandrake/FeverWood/Defs/ThingDefs_Plants/RM_GiantLeaf.xml").getroot():
    if el.findtext("defName"):
        DESC[el.findtext("defName")] = " ".join((el.findtext("description") or "").split())


def plant_desc(d):
    # drop the trailing gameplay sentence(s) after the visual ones? keep all: they name what it is for
    return DESC[d].replace("⚠️", "").strip()


# canvas = max visualSizeRange x 128, rounded up to a power of two (Ammeth: owner's "twice as big" = 2.8)
REDO = {"RM_Ammeth": (512, None), "RM_Cistrel": (256, "B"), "RM_Corvath": (256, "B"), "RM_Skimmel": (256, "B"),
        "RM_Sodderel": (256, "B"), "RM_Thulvane": (512, "B"), "RM_Tullick": (256, "B"), "RM_Varnoth": (512, "B"),
        "RM_Verrow": (256, "B"), "RM_Wanlith": (256, "B")}
for d, (cw, col) in REDO.items():
    nm = d[3:].lower()
    for v in "abc":
        extra = {}
        anchor = ""
        if col:
            extra["canon_reference"] = [img(d, col)]
            anchor = ("Keep the attached render's concept, but redraw it far more REALISTICALLY, as a real "
                      "plant photographed and painted, not a cartoon. ")
        if cw > 256:
            extra["oversize_reason"] = ("owner: regenerate twice as big (visualSizeRange max 1.4 -> 2.8 cells)"
                                        if d == "RM_Ammeth" else "plant visualSizeRange max >2 cells x 128 px/cell")
        big = ("Drawn TWICE AS BIG as before: a large plant filling the canvas. " if d == "RM_Ammeth" else "")
        row(f"{nm}_v2{v}", d,
            f"RimWorld plant sprite seen from above at a slight angle, the {nm} (variant {v} of 3, vary the shape "
            f"and arrangement so a field of them reads varied): {plant_desc(d)} {anchor}{big}"
            "Naturalistic botanical rendering. One whole plant, centred.", cw, facings=[], **extra)

# ---- plants: keep the chosen render, add 2 realistic variants -----------------------------------------
ADD = {"Plant_HydenockTree_Wild": (512, "A"), "Plant_JoganTree_Wild": (512, "B"), "RM_Claithe": (256, "B"),
       "RM_GiantLeaf": (256, "A"), "RM_Halquin": (256, "B"), "RM_Maulith": (256, "B"), "RM_Nubrith": (256, "B"),
       "RM_Ossagrel": (256, "A"), "RM_Plennith": (256, "B"), "RM_Seepril": (256, "B")}
for d, (cw, col) in ADD.items():
    nm = d.replace("Plant_", "").replace("_Wild", "").replace("RM_", "").lower()
    what = plant_desc(d) + " " if d in DESC else ""
    for v in "bc":
        row(f"{nm}_var{v}_v1", d,
            f"RimWorld plant sprite, the {nm}: a NEW, REALISTIC VARIANT ({v}) of the same species as the attached "
            f"chosen render -- same species, palette, structure and scale, a different individual with its own "
            f"shape and arrangement, so a field of them reads varied. {what}Naturalistic, believable botanical "
            "rendering. One whole plant, centred.", cw, facings=[], canon_reference=[img(d, col)],
            **({"oversize_reason": "canopy tree; donor def's visualSizeRange not in src/, tree canvas chosen"}
               if cw > 256 else {}))

out = Path(__file__).with_name("feverwood_regen_jobs.json")
out.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
print(len(rows), "rows ->", out)
