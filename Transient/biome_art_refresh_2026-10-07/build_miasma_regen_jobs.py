#!/usr/bin/env python3
"""Build fill_queue rows for the owner's 2026-10-08 (UTC) Miasma sheet rulings. Notes carried verbatim."""
import json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
DEC = json.load(open(REPO / "Transient/biome_ffar/miasma_sheet_2026-10-05.decisions.json"))["decisions"]
SNAP = json.load(open(REPO / "infrastructure/state/art/sheets/miasma_sheet_2026-10-05.snapshot.json"))["rows"]
CANON = REPO / "design/RimStarWars/canon_references"
STORE = Path("/mnt/d/Luke/dev/_artstore")
PRI = 0  # lowest number = claimed first; lowest ever used in the queue is 1
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
REG = ("miasma register: a salt-crusted mangal forest under a green-gold haze, brackish channels, "
       "rainbow-hued plants; gold-green light, pale salt crust")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic, grounded and alien; one centred subject "
         "on a fully transparent background.")
F3 = ["east", "south", "north"]


def note(d):
    h = DEC[d]
    assert h.get("at"), d
    return h["note"]


def img(d, col, key=None):
    v = SNAP[d]["columns"][col]
    h = v[key] if key else next(iter(v.values()))
    p = STORE / h[:2] / f"{h}.png"
    assert p.is_file(), p
    return str(p)


def lead(n):
    return f'Owner\'s note, verbatim, overrides everything below: "{n}" ' if n else ""


rows = []
# adult (largest) drawSize per def, read from src/ defs (donor AA defs from the workshop XML)
DS = {"RSW_Vornskyr": 3.0, "RSW_Zakkeg": 5.0, "RSW_Blixus": 4.0, "RSW_Blarth": 1.0, "RSW_MarshHaunt": 2.0,
      "RSW_Bogwing": 1.4, "RSW_LaaJuv": 0.96, "RSW_OpeeSeaKillerJuv": 1.8, "RSW_YobshrimpJuv": 0.8,
      "AA_Lockjaw": 2.25, "AA_Mantrap": 1.75, "RSW_PodWorm": 3.25, "RM_Nogtyl": 12.0,
      "RM_Aphreen": 1.0, "RM_Braskeen": 0.85, "RM_Ommolyn": 0.6, "RM_Velluric": 0.7, "RM_Nemreth": 0.75,
      "RM_Nyssolet": 0.8, "RM_Pallasheen": 0.55, "RM_Sarrash": 1.0, "RM_Thrannock": 1.3, "RM_Ullavess": 1.1,
      "RM_Vellamine": 0.9, "RM_Wessaline": 1.0}


def row(id, d, prompt, cw, facings=F3, **kw):
    n = kw.pop("owner_note", None)
    if n is None:
        n = note(d)
    r = {"id": id, "rimflow_item_id": ITEM, "target_def": d, "prompt": lead(n) + prompt,
         "style_notes": STYLE, "canvas_w": cw, "canvas_h": cw, "facings": facings,
         "background": "transparent", "channel": "codex", "priority": PRI, "biome_register": REG}
    if n:
        r["owner_note"] = n
    if d in DS:
        r["drawsize"] = DS[d]
    r.update(kw)
    rows.append(r)


# ---- canon, "follow canon precisely" -------------------------------------------------------------
row("miasma_canon_vornskyr_v2", "RSW_Vornskyr",
    "RimWorld creature sprite of the Star Wars canon vornskr, drawn to match the attached canon image "
    "precisely: a lean quadruped canine/reptile-hybrid predator with smooth hairless dark grey to near-black "
    "reptilian hide, tall pointed bat-like ears, a narrow snarling muzzle with prominent visible fangs, red "
    "eyes, four clawed digits per paw, and a long whip-thin tail ending in a distinct bushy black tuft. "
    "One animal, whole body, centred.", 512, canon="vornskyr",
    canon_reference=[str(CANON / "vornskyr/wookieepedia_alienarchive.jpg")])
row("miasma_canon_laajuv_v1", "RSW_LaaJuv",
    "RimWorld creature sprite of the Star Wars canon laa (fantailed laa), a young one, drawn to match the "
    "attached canon image precisely: a deep rounded pot-bellied fish with a very large swept-back fan tail "
    "(upper lobe dark teal, lower lobe pale cream), teal/blue-green back with orange-red speckles, pale "
    "peach-cream belly, a long forward-pointing snout with thick pale red-tinted pucker lips, a large round "
    "eye, a big wing-like dark pectoral fin, and two long thin whip filaments, one trailing from the top of "
    "the head and one dangling from the chin ending in a small glowing orange bulb. One fish, whole body, "
    "centred.", 256, canon="laascalefish",
    canon_reference=[str(CANON / "laascalefish/wookieepedia_canon_1.webp")])
row("miasma_canon_opeejuv_v1", "RSW_OpeeSeaKillerJuv",
    "RimWorld creature sprite of the Star Wars canon opee sea killer, a young one, drawn to match the "
    "attached canon image precisely: a huge fish-like head with an enormous gaping mouth lined with double "
    "rows of long pale conical teeth and a purple-lilac mouth interior, wrinkled lumpy face with bulbous "
    "orange-red eyes set high, long thin whip antennae rising from the crown ending in dark blue-purple lure "
    "bulbs, a long segmented arched armour-plated back tapering to a point like a lobster tail, "
    "reddish-orange/coral-red skin and plates, broad fan-shaped pectoral fins and three pairs of thin "
    "jointed crab-like legs under the rear body, the pink-mauve tongue just showing at the mouth. One "
    "animal, whole body, centred.", 256, canon="opeeseakiller",
    canon_reference=[str(CANON / "opeeseakiller/wookieepedia_canon_1.webp")])
row("miasma_canon_yobshrimpjuv_v1", "RSW_YobshrimpJuv",
    "RimWorld creature sprite of the yobshrimp, a young one, drawn to match the attached PURPLE live-animal "
    "reference precisely: a small crustacean with a flat wedge-shaped lilac-purple carapace drawn out to a "
    "long sharp forward rostrum, dark violet mottling and small raised bumps, paler lilac belly, bright green "
    "stalked eyes, two long thin whip antennae trailing back, short bristly crab-like walking legs, and two "
    "very long jointed arms ending in huge thin scissor claws raised up and back over the body. One animal, "
    "whole body, centred.", 256, canon="paleyobshrimp",
    canon_reference=[str(CANON / "paleyobshrimp/wookieepedia_legends_1.webp")])
row("miasma_canon_zakkeg_v2", "RSW_Zakkeg",
    "RimWorld creature sprite of the Star Wars canon zakkeg of Dxun, drawn to match the attached RED canon "
    "image precisely: a stegosaur-like reptilian quadruped built like a battle tank, rust-red/copper-brown "
    "thick knobbed bumpy armoured hide over the whole body, a jagged spiked ridge running along the spine "
    "from head to tail, a low-slung reptilian head with visible fangs and small yellow eyes, four heavy thick "
    "clawed legs and a tapered tail. One animal, whole body, centred.", 1024, canon="zakkeg",
    canon_reference=[str(CANON / "zakkeg/wookieepedia_kotor2_juvenile.png")])

# ---- canon swimmers / flyer: "no new art" -> body + motion graphic -----------------------------------
SW = {
    "RSW_Blarth": ("blarth", 256, "wookieepedia_legends_1.webp",
                   "a rotund, low-slung amphibian with a barrel body and short stubby legs, smooth wrinkled "
                   "rubbery pale powder blue-grey hide with a lighter cream belly and soft peach highlights, "
                   "small circular whorl dimples over back and flanks, a wide flat toad-like head with a very "
                   "broad mouth, one or two curved lower tusks, small half-lidded eyes, a big flat pink tongue "
                   "lolling out with drool, and a long tapering prehensile tail ending in tiny finger-like nubs"),
    "RSW_Blixus": ("blixus", 512, "wookieepedia_canon_1.webp",
                   "a low crab/trilobite-like animal under a smooth teal-blue armoured half-shell of overlapping "
                   "flared plates, soft pinkish-tan underbelly, a wide lip-lined slit mouth low on the front "
                   "with two small pincer claws beside it, two small amber eyes under the carapace brim, exactly "
                   "six stiff blade-like blue-grey chitin legs angled down and forward, and exactly five very "
                   "long ringed flesh-pink tentacles, each longer than the body, grey and thorn-spiked toward "
                   "the tips and ending in a flat pink sucker-pad"),
    "RSW_MarshHaunt": ("marshhaunt", 256, "wookieepedia_canon_1.webp",
                       "a hulking hunched headless-looking swamp beast far taller than a person, its skull sunk "
                       "deep between the shoulders, peeling ragged dark grey-green to teal leathery skin mottled "
                       "with blotches and trailing moss-like strands, a cluster of dark red berry-like bulbs/eyes "
                       "heaped on top where the head should be, and huge dark-clawed forelimbs hanging low"),
}
for d, (slug, cw, ref, desc) in SW.items():
    base = f"miasma_canon_{slug}_v1"
    row(base, d, f"RimWorld creature sprite of the Star Wars {slug}, matching the attached canon image: {desc}. "
        "Standing pose. One animal, whole body, centred.", cw, canon=slug,
        canon_reference=[str(CANON / slug / ref)])
    row(f"{base}_swim", d, f"RimWorld creature SWIMMING sprite of the Star Wars {slug}, the same individual as "
        f"the accepted standing render: {desc}. Shown swimming, the body low and level as if half-submerged, "
        "limbs paddling or trailing, the outline clean against transparency (the water is drawn by the game). "
        "One animal, whole body, centred.", cw, canon=slug, derive_from=f"{base}_east",
        target_texpath=f"swanimals/{d[4:]}/{d[4:]}_Swimming")

bw_desc = ("a pterosaur-like light flier: tiny slim body, long thin neck, small bird-like head with a short "
           "pointed beak and one round yellow-orange eye, two huge narrow membrane wings each longer than the "
           "body with pointed tips, brown-mauve membrane with dark green leading-edge bones, a very long thin "
           "straight whip tail, spindly hind legs with large splayed 3-toed talons, teal/blue-green back and "
           "limbs over a pale grey-mauve belly, smooth scaleless skin")
row("miasma_canon_bogwing_v1", "RSW_Bogwing", "RimWorld creature sprite of the Star Wars bogwing, matching the "
    f"attached canon image: {bw_desc}. Perched/walking pose, wings folded high. One animal, whole body, centred.",
    256, owner_note="", canon="bogwing", canon_reference=[str(CANON / "bogwing/wookieepedia_canon_1.webp")])
POSES = {1: "wings raised high in a V at the top of the upstroke",
         2: "wings level and spread wide mid-downstroke",
         3: "wings swept fully down at the bottom of the downstroke",
         4: "wings level and rising mid-upstroke"}
for n, pose in POSES.items():
    row(f"miasma_canon_bogwing_flying_{n}_v1", "RSW_Bogwing",
        f"RimWorld creature FLYING animation frame {n} of 4 (whole-body flip-book frame, not a wing layer) of "
        f"the Star Wars bogwing, the same individual as the accepted standing render: {bw_desc}. In flight, "
        f"body level, legs tucked back, {pose}. One animal, whole body, centred.", 256, owner_note="",
        canon="bogwing", derive_from="miasma_canon_bogwing_v1_east",
        target_texpath=f"swanimals/Bogwing/Bogwing_Flying_{n}")

# ---- renamed / redesigned subjects ------------------------------------------------------------------
row("miasma_siezer_v1", "AA_Lockjaw",
    "RimWorld creature sprite, the siezer: an alien mud-swimming beast whose MASSIVE head is half the size of "
    "its relatively reduced body, a toothy lock-jawed whale-like head with a heavy clamped jaw lined with "
    "interlocking teeth, a stubby tapering body and broad flippers it uses to shove itself through the mud, "
    "smooth mottled mud-dark hide. Alien and whale-like in build. One animal, whole body, centred.", 512)
mn = note("AA_Mantrap")
e_img = img("AA_Mantrap", "E")
row("miasma_lastvine_calm_v1", "AA_Mantrap",
    "RimWorld creature sprite, the lastvine, CALM state, design based on the attached chosen render (column "
    "E): a sessile-looking plant-beast at rest, its single closed mouth-pod hanging down heavy like a ripe "
    "pod, fang-like thorns folded shut around the sealed mouth, no arms, a mass of root-like legs gripping "
    "the ground. One creature, whole body, centred.", 256, canon_reference=[e_img],
    target_texpath="Things/Pawn/Animal/AA_Mantrap/AA_Mantrap")
row("miasma_lastvine_reared_v1", "AA_Mantrap",
    "RimWorld creature sprite, the lastvine, REARED attack state, the same creature as the calm pod form "
    "(design based on the attached chosen render, column E): the pod reared up high, split open into a huge "
    "gaping single maw ringed with fang-like thorns, actively writhing tentacles lashing around it, no arms, "
    "root-like legs pulling it along hungrily. Terrifying. One creature, whole body, centred.", 256,
    canon_reference=[e_img], target_texpath="Things/Pawn/Animal/AA_Mantrap/AA_Mantrap_Reared")
row("miasma_hellslantern_v1", "RSW_PodWorm",
    "RimWorld creature sprite, the hell's lantern: a slow, heavy, venomous swamp worm, its fat segmented body "
    "dragging low, a glowing lantern-like lure swelling at its head lit from within with sickly light, "
    "venom-wet hooked mouthparts and dripping glands along its flanks marking it as poisonous. One animal, "
    "whole body, centred.", 512)
for f in F3:
    row(f"miasma_swarmling_green_v1_{f}", "VFEI2_Swarmling",
        f"RimWorld creature sprite, the swarmling, {f.upper()}-facing: keep this render's shape exactly, "
        "including the big bulbous abdomen sac, and recolour the whole animal a sickly diseased green.",
        256, facings=[], derive_from=f"rot_swarmling_v2_{f}")

# ---- plants: redo -----------------------------------------------------------------------------------
row("miasma_aphreen_v2", "RM_Aphreen",
    "RimWorld plant sprite seen from above at a slight angle, the aphreen: an upright bushy plant of narrow "
    "leaves in tight whorls, mature growth dusty green, every new growing tip flushed hot pink-red and covered "
    "in fine pale fur as if inflamed, the flush fading as each leaf matures. Naturalistic botanical rendering. "
    "One whole plant, centred.", 256, facings=[])
for st, desc in (("closed", "each arm's hinged blade pair snapped CLOSED, a caught scuttler's outline just "
                            "visible between the interlocking teeth"),
                 ("open", "each arm ending in a pair of hinged blades held OPEN, fringed with stiff interlocking "
                          "teeth, blade interiors raw wet pink, waiting")):
    row(f"miasma_braskeen_{st}_v2", "RM_Braskeen",
        f"RimWorld plant sprite seen from above, the braskeen ({st.upper()} state): a flat predatory whorl "
        f"floating on the water surface, {desc}. Naturalistic, botanically believable. One whole plant, "
        "centred.", 256, facings=[])
VAR = "abc"
for i, v in enumerate(VAR):
    row(f"miasma_ommolyn_v2{v}", "RM_Ommolyn",
        f"RimWorld plant sprite seen from above at a slight angle, the ommolyn (variant {v} of 3, vary the "
        "shape): an alien swamp lure-plant, a strange pale bloom on a short stalk over sprawling slick "
        "mud-surface leaves, its form unmistakably alien, hinting at something waiting below the mud. "
        "One whole plant, centred.", 256, facings=[])
    row(f"miasma_velluric_v2{v}", "RM_Velluric",
        f"RimWorld plant sprite seen from above a shallow channel, the velluric (variant {v} of 3, vary the "
        "shape): an alien aquatic bladder-plant, a pale flower on a thin stalk above the waterline over a "
        "visibly complex drifting mass of translucent bladders and trailing filaments just beneath the "
        "surface. One whole plant, centred.", 256, facings=[])

# ---- plants: add variants consistent with the chosen column A ---------------------------------------
ADD = {"RM_Nemreth": 256, "RM_Nogtyl": 1024, "RM_Nyssolet": 256, "RM_Pallasheen": 256, "RM_Sarrash": 256,
       "RM_Thessamor": 256, "RM_Thrannock": 256, "RM_Ullavess": 256, "RM_Vellamine": 256, "RM_Wessaline": 256}
for d, cw in ADD.items():
    a = img(d, "A")
    nm = d[3:].lower()
    for v in "bc":
        row(f"miasma_{nm}_var{v}_v1", d,
            f"RimWorld plant sprite, the {nm}: a NEW VARIANT ({v}) of the same species as the attached chosen "
            "render -- same species, palette, structure and scale, a different individual with its own shape "
            "and arrangement, so a field of them reads varied. One whole plant, centred.", cw, facings=[],
            canon_reference=[a])

out = Path(__file__).with_name("miasma_regen_jobs.json")
out.write_text(json.dumps(rows, indent=1))
print(len(rows), "rows ->", out)
