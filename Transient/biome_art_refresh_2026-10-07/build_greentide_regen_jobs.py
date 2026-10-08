#!/usr/bin/env python3
"""Build fill_queue rows for the owner's 2026-10-08 (UTC) Greentide sheet rulings. Notes carried verbatim.

Same method as build_feverwood_regen_jobs.py. Ids start `regen_gt_` so that, at equal priority, they sort
(and are claimed) after every `miasma_*` and `regen_fw_*` job -- the daemon orders pending by (priority, filename).
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
DECF = json.load(open(REPO / "Transient/biome_ffar/greentide_sheet_2026-10-05.decisions.json"))
DEC = DECF["decisions"]
SNAP = json.load(open(REPO / "infrastructure/state/art/sheets/greentide_sheet_2026-10-05.snapshot.json"))["rows"]
CANON = REPO / "design/RimStarWars/canon_references"
STORE = Path("/mnt/d/Luke/dev/_artstore")
PRI = 0
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
REG = ("greentide register: a gallery jungle standing in permanent ground-hugging steam over warm rivers, "
       "deep churned mud between the roots, a low fog that never lifts, everything growing fast and wet; "
       "dim green steam-lit light, saturated wet greens, dark wet bark")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic, grounded and alien, naturalistic and "
         "botanically/zoologically believable, never cartoonish; one centred subject on a fully transparent "
         "background.")
F3 = ["east", "south", "north"]
P = "regen_gt_"
SW = "swanimals/"


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


def pow2(ds, floor=256, cap=1024):
    px = ds * 128
    c = floor
    while c < px and c < cap:
        c *= 2
    return c


rows = []
OWN = set()
DS = {}


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
    OWN.add(P + id)
    r.update(kw)
    if r.get("derive_from") and r["derive_from"].startswith("@"):
        r["derive_from"] = P + r["derive_from"][1:]
    rows.append(r)


POSES = {1: "wings raised high in a V at the top of the upstroke",
         2: "wings level and spread wide mid-downstroke",
         3: "wings swept fully down at the bottom of the downstroke",
         4: "wings level and rising mid-upstroke"}


def flight(slug, d, base_master, desc, cw, frames, texprefix, canon=None, owner_note="", extra_canon=None, tag=""):
    """whole-body directional flip-book frames, derived from the new standing east master."""
    for n in range(1, frames + 1):
        pose = POSES[n] if frames == 4 else {1: POSES[1], 2: POSES[3], 3: POSES[4]}[n]
        kw = {}
        if canon:
            kw["canon"] = canon
        row(f"{slug}_flying{tag}_{n}_v1", d,
            f"RimWorld creature FLYING animation frame {n} of {frames} (whole-body flip-book frame, not a wing "
            f"layer), the same individual as the accepted standing render: {desc}. In flight, body level, legs "
            f"tucked, {pose}. One animal, whole body, centred.", cw, owner_note=owner_note,
            derive_from="@" + base_master if not base_master.startswith("!") else base_master[1:],
            target_texpath=f"{texprefix}{n}", **kw)


# adult (largest) drawSize from the PawnKindDefs / race defs
DS.update({"RSW_Beldon": 4.0, "RSW_Dragonsnake": 4.0, "RSW_Hawkbat": 2.0, "RSW_Kinrath": 2.5, "RSW_Klorslug": 2.5,
           "RSW_Lylek": 4.0, "RSW_Mott": 1.5, "RSW_PekoPeko": 3.5, "RSW_ShiroTrap": 1.5, "RM_CanopySwinger": 1.1,
           "RSW_Diggerpede": 1.0, "RM_Yammeth": 0.9})

# ============================ CANON REDO ============================================================
# ---- Beldon
bel = ("a huge floating gas-bladder creature: a cluster of four or five swollen, glossy, translucent "
       "orange-peach spherical bladders mottled with warm orange-red blotches and fine dark speckles, fused "
       "into one lumpy mass; ragged frilled spiny crests between the topmost bladders; a broad flat fleshy fin "
       "trailing at the rear; a dark crimson crust of small knobbly bead-like growths along the underside from "
       "which a cloud of long, thin, dark thread-like tendrils hangs. Hand-painted-guidebook anatomy, "
       "rendered realistically")
row("canon_beldon_v1", "RSW_Beldon",
    "RimWorld creature sprite of the Star Wars canon beldon, drawn from the attached canon illustration "
    f"(first image): {bel}. The second attached image is the CURRENT in-game donor sprite, to be used only as "
    "concept guidance for the overall pose and proportion; redraw it far more realistically and in much "
    "higher quality. Ignore any purple colour: the bladders are orange. One animal, whole body, centred.", 512,
    canon="beldon", canon_reference=[str(CANON / "beldon/wookieepedia_woswfg.webp"), img("RSW_Beldon", "A", "east")],
    target_texpath=SW + "Beldon/Beldon")
flight("beldon", "RSW_Beldon", "canon_beldon_v1_east", "a floating beldon, " + bel, 512, 3,
       SW + "Beldon/Beldon_Flying_", canon="beldon")

# ---- Dragonsnake (middle canon image, pale snake on black)
ds_ = ("a colossal pallid serpent: a very long, thick, smooth, glossy cream-white flesh-pale body ringed with "
       "faint ribbing along the neck, held in heavy coils; a long drooping skull-like head with a narrow "
       "bony snout, sunken shadowed eye sockets, and a wide mouth lined with long needle-like fangs and wet "
       "pink-red gums. No limbs. Subtle grey-brown shading on the upper back")
row("canon_dragonsnake_v1", "RSW_Dragonsnake",
    "RimWorld creature sprite of the Star Wars canon dragonsnake, drawn from the attached canon image (the "
    f"middle canon image, the pale snake rising from dark water): {ds_}. The background is fully transparent, "
    "not black. Standing/resting pose, head raised. One animal, whole body, centred.", 512,
    canon="dragonsnake", canon_reference=[str(CANON / "dragonsnake/wookieepedia_mandalorianandgrogu.jpg")],
    target_texpath=SW + "Dragonsnake/Dragonsnake")
row("canon_dragonsnake_v1_swim", "RSW_Dragonsnake",
    f"RimWorld creature SWIMMING sprite of the dragonsnake, the same individual as the accepted standing render: "
    f"{ds_}. Shown swimming, the body low and level as if half-submerged in undulating coils, head just "
    "above the surface, the outline clean against transparency (the water is drawn by the game). One animal, "
    "whole body, centred.", 512, canon="dragonsnake", derive_from="@canon_dragonsnake_v1_east",
    target_texpath=SW + "Dragonsnake/Dragonsnake_Swimming")

# ---- Hawkbat (purple + tan Legends illustration)
hb = ("a pterosaur/bat-like flier, NOT a bird (no feathers, no beak): a slim body with a long thin neck and a "
      "small narrow reptilian head with a short snout, a green eye and small head tufts; two huge triangular "
      "leathery membrane wings with long pointed tips, ribbed by radiating fine veins; the membranes banded "
      "violet-purple along the bones and veins fading to pale tan-gold between them, with tan-cream underwing; "
      "clawed wing-hooks, short legs and a thin tail")
row("canon_hawkbat_v1", "RSW_Hawkbat",
    "RimWorld creature sprite of the Star Wars canon hawkbat, following the attached purple-and-tan canon "
    f"illustration very closely: {hb}. Standing/perched pose, wings folded. One animal, whole body, centred.",
    256, canon="hawkbat", canon_reference=[str(CANON / "hawkbat/wookieepedia_legends_infobox.jpg")],
    target_texpath=SW + "Hawkbat/Hawkbat")
row("canon_hawkbat_juv_v1", "RSW_Hawkbat",
    f"RimWorld creature sprite of the juvenile hawkbat, the same individual as the accepted adult render, "
    f"younger and smaller with softer paler purple-tan colouring and proportionally larger head: {hb}. "
    "Standing/perched pose, wings folded. One animal, whole body, centred.", 256, canon="hawkbat",
    derive_from="@canon_hawkbat_v1_east", target_texpath=SW + "Hawkbat/Hawkbat_j")
flight("hawkbat", "RSW_Hawkbat", "canon_hawkbat_v1_east", hb, 256, 4, SW + "Hawkbat/Hawkbat_Flying_", canon="hawkbat")
flight("hawkbat", "RSW_Hawkbat", "canon_hawkbat_juv_v1_east", "a juvenile, smaller and paler " + hb, 256, 4,
       SW + "Hawkbat/Hawkbat_j_Flying_", canon="hawkbat", tag="_j")

# ---- Kinrath (mantis shape; donor art as geometry)
kn = ("a tall, slender, four-long-legged mantis/spider-like predator: a narrow upright segmented body, a long "
      "upward-curving segmented neck ending in a small elongated head with clustered small eyes, two folded "
      "raptorial mantis forelimbs, and four very long, thin, multi-jointed legs; gold-tan banded skin with "
      "orange-brown mottling and darker joints, glossy chitin plates")
row("canon_kinrath_v1", "RSW_Kinrath",
    "RimWorld creature sprite of the Star Wars canon kinrath, following the attached canon illustration "
    f"closely (it looks closest to a mantis): {kn}. The second attached image is the donor art, to be studied "
    "ONLY for geometry (limb count and body proportions). One animal, whole body, centred.", 512, canon="kinrath",
    canon_reference=[str(CANON / "kinrath/wookieepedia_legends_infobox_viperkinrath.png"), img("RSW_Kinrath", "D", "east")],
    target_texpath=SW + "Kinrath/Kinrath")

# ---- Klorslug (red and white Legends concept art)
kl = ("a long, low, armoured centipede-slug: a ribbed, segmented body of glossy deep crimson-red plates with "
      "paler pinkish-white bands, a gaping round maw ringed with spiky red plates at the front, a row of long "
      "curved bone-white claw-spines along each flank in place of legs, and a thick curling segmented tail with "
      "a spiked tip")
row("canon_klorslug_v1", "RSW_Klorslug",
    "RimWorld creature sprite of the Star Wars canon klorslug, following the attached canon illustration "
    f"precisely (the red-and-white one): {kl}. One animal, whole body, centred.", 512, canon="klorslug",
    canon_reference=[str(CANON / "klorslug/wookieepedia_legends_1.webp")], target_texpath=SW + "Klorslug/Klorslug")
row("canon_klorslug_juv_v1", "RSW_Klorslug",
    f"RimWorld creature sprite of the juvenile klorslug, the same individual as the accepted adult render, "
    f"smaller and shorter with softer paler red-white colouring: {kl}. One animal, whole body, centred.", 512,
    canon="klorslug", derive_from="@canon_klorslug_v1_east", target_texpath=SW + "Klorslug/Klorslug_j")

# ---- Lylek
ly = ("a many-limbed ambush horror: a hunched olive-green body of overlapping spiked bark-like plates over a "
      "pale cream belly, three small snaking heads on thick necks (one central head with a wide toothy open "
      "mouth, two smaller flanking heads), six very long thin spiked spider-like legs, and two long black "
      "whip-like tentacle tails curling at the rear")
row("canon_lylek_v1", "RSW_Lylek",
    "RimWorld creature sprite of the Star Wars canon lylek, following the attached canon illustration "
    f"closely: {ly}. One animal, whole body, centred.", 512, canon="lylek",
    canon_reference=[str(CANON / "lylek/wookieepedia_canon_1.webp")], target_texpath=SW + "Lylek/Lylek")

# ---- Mott (female master, male + swimming derived)
mo = ("a heavy stocky dog/hippo/rhino-like quadruped: a barrel body with a tan-grey back and rust-orange "
      "shoulders and legs, crossed by fine pale cream stripes over the flanks and legs; a broad blunt hippo-like "
      "snout with a small horn at the nose and small ears or horns on the head, a small dark eye and a wide "
      "mouth; short thick legs with splayed toes")
row("canon_mott_f_v1", "RSW_Mott",
    f"RimWorld creature sprite of the female Star Wars canon mott, following the attached canon photograph "
    f"closely: {mo}. One animal, whole body, centred.", 256, canon="mott",
    canon_reference=[str(CANON / "mott/wookieepedia_canon_1.webp")], target_texpath=SW + "Mott/Mott_f")
row("canon_mott_m_v1", "RSW_Mott",
    f"RimWorld creature sprite of the male mott, the same species and palette as the accepted female render "
    f"but a bit more massive with a heavier horn and bolder stripes: {mo}.", 256, canon="mott",
    derive_from="@canon_mott_f_v1_east", target_texpath=SW + "Mott/Mott_m")
for sx in ("f", "m"):
    row(f"canon_mott_{sx}_swim_v1", "RSW_Mott",
        f"RimWorld creature SWIMMING sprite of the {'female' if sx == 'f' else 'male'} mott, the same "
        f"individual as the accepted standing render: {mo}. Shown swimming, the body low and level as if "
        "half-submerged, legs paddling, the outline clean against transparency. One animal, whole body, centred.",
        256, canon="mott", derive_from="@canon_mott_f_v1_east" if sx == "f" else "@canon_mott_m_v1_east",
        target_texpath=SW + f"Mott/Mott_{sx}_Swimming")

# ---- PekoPeko (female master; male + all flight derived)
pk = ("a long-necked, elegant blue flier: slate-to-peacock blue plumage over the wings and a very long trailing "
      "tail of narrow feathers edged with pale gold, a long slim neck, a small head with a small yellow-gold "
      "crest and a short hooked bill, and slim clawed legs")
row("canon_pekopeko_f_v1", "RSW_PekoPeko",
    "RimWorld creature sprite of the female Star Wars canon peko-peko, following the attached canon field-guide "
    f"illustration very closely: {pk}. Standing/perched pose, wings folded. One animal, whole body, centred.",
    512, canon="pekopeko", canon_reference=[str(CANON / "pekopeko/wookieepedia_fieldguide.jpg")],
    target_texpath=SW + "PekoPeko/PekoPeko_f")
row("canon_pekopeko_m_v1", "RSW_PekoPeko",
    f"RimWorld creature sprite of the male peko-peko, the same species as the accepted female render but "
    f"brighter, bolder blue with a larger gold crest and longer tail: {pk}. Standing/perched pose, wings "
    "folded.", 512, canon="pekopeko", derive_from="@canon_pekopeko_f_v1_east", target_texpath=SW + "PekoPeko/PekoPeko_m")
flight("pekopeko", "RSW_PekoPeko", "canon_pekopeko_f_v1_east", "a female " + pk, 512, 4,
       SW + "PekoPeko/PekoPeko_f_Flying_", canon="pekopeko", tag="_f")
flight("pekopeko", "RSW_PekoPeko", "canon_pekopeko_m_v1_east", "a male, brighter " + pk, 512, 4,
       SW + "PekoPeko/PekoPeko_m_Flying_", canon="pekopeko", tag="_m")

# ---- ShiroTrap (shiro + trap plant)
st = ("a squat armoured turtle-like animal (a shiro: a spined, ridged dome shell, stubby legs, a blunt snout, "
      "mossy olive-green skin) with a trap plant growing from its back: a rosette of broad coral-orange leaves "
      "striped with gold, and two or three long stalks each ending in a red toothed snapping trap-mouth with "
      "small berry-like buds")
row("canon_shirotrap_v1", "RSW_ShiroTrap",
    "RimWorld creature sprite of the Star Wars canon shiro-trap: a shiro with a trap plant on it, per the "
    f"attached canon illustration (the first image): {st}. The second attached image is the in-game Shiro, "
    "the turtle body to use as concept guidance for the animal half; the trap plant on top is drawn from the "
    "canon image. One animal, whole body, centred.", 256, canon="shirotrap",
    canon_reference=[str(CANON / "shirotrap/wookieepedia_canon_1.webp"), img("RSW_Shiro", "A", "east")],
    target_texpath=SW + "ShiroTrap/ShiroTrap")
for suf, what in (("i", "an infant, tiny, with a small sprout of trap plant just starting on its shell"),
                  ("j", "a juvenile, smaller than the adult, with a half-grown trap plant on its shell")):
    row(f"canon_shirotrap_{suf}_v1", "RSW_ShiroTrap",
        f"RimWorld creature sprite of the shiro-trap as {what}, the same individual as the accepted adult "
        f"render: {st}. One animal, whole body, centred.", 256, canon="shirotrap",
        derive_from="@canon_shirotrap_v1_east", target_texpath=SW + f"ShiroTrap/ShiroTrap_{suf}")

# ============================ INVENTED REDO =========================================================
ook = ("a drawn-out, narrow-bodied canopy climber, very long and thin, its limbs jointed one time more than they "
       "need to be so each reach folds out like a tape, hooked hands, a long gripping tail; it hangs between "
       "the giants and is hard to tell from a vine")
row("ookala_v2", "RM_CanopySwinger",
    f"RimWorld creature sprite, the ookala, design based on the attached in-game render (concept guidance "
    f"only): {ook}. Make it far more alien and ELONGATED: a stretched, spindly, unfamiliar anatomy, not a "
    "monkey. One animal, whole body, centred.", 256, canon_reference=[img("RM_CanopySwinger", "A", "east")],
    target_texpath="Things/Pawn/Animal/RM_CanopySwinger/RM_CanopySwinger")

for v in "abc":
    row(f"tuun_v2{v}", "RM_Tuun",
        f"RimWorld fish-item icon, the tuun (option {v} of 3, vary the design): a small quick bark-mottled "
        "octopus that climbs root causeways, based on the attached chosen render (column B, good concept) but "
        "made MORE ALIEN: unfamiliar proportions, an odd many-lobed body, bark-textured mottling, bright thief's "
        "eyes. Realistic. One item, centred.", 256, facings=[], canon_reference=[img("RM_Tuun", "B")],
        target_texpath="Things/Item/Fish/RM_Tuun")

row("gristle_v2", "RSW_Diggerpede",
    "RimWorld creature sprite, the gristle (no canon-library entry exists; invented creature): a long, flat-plated "
    "burrower the length of a man, every segment carrying a pair of short digging legs, the head armoured in a heavy "
    "shovel-edged shield with hooked mandibles, a body of tough rubbery muscle over a chitin frame. Make it "
    "REALISTIC: believable arthropod anatomy, segmented plates, real chitin texture. One animal, whole body, "
    "centred.", 256, canon_reference=[img("RSW_Diggerpede", "A", "east")],
    target_texpath="swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Diggerpede/Diggerpede")

row("saluksis_v2", "VFEI2_Swarmling",
    "RimWorld creature sprite, the saluksis (formerly the swarmling), design based on the attached render "
    "(column B, rot_swarmling_v2, concept guidance): a small insectoid with a bulbous milk-white abdomen sac, made "
    "YET MORE ALIEN: unfamiliar asymmetric anatomy, extra joints and odd sensory organs, glossy "
    "wet chitin. Realistic. One animal, whole body, centred.", 256,
    canon_reference=[img("VFEI2_Swarmling", "B", "east")], target_texpath="Things/Pawn/Animal/Swarmling/Swarmling")

# ============================ PLANT VARIANTS ========================================================
DESC, VIS = {}, {}
for f in (REPO / "src/RimMandrake/Greentide/Defs/ThingDefs_Plants").glob("*.xml"):
    for el in ET.parse(f).getroot():
        dn = el.findtext("defName")
        if dn:
            DESC[dn] = " ".join((el.findtext("description") or "").split())
            vs = el.findtext("plant/visualSizeRange")
            if vs:
                VIS[dn] = float(vs.split("~")[1])
DESC["Plant_Grass"] = ("ordinary wild grass: a clump of fine blade tufts, the Greentide's wet green ground cover "
                       "(drawn in game with ReGrowth's RG_Grass)")
DESC["Plant_TallGrass"] = "tall wild grass: long arching blades in a dense wet clump (drawn in game with RG_Grass)"
VIS.update({"Plant_Grass": 1.0, "Plant_TallGrass": 1.5})


def pdesc(d):
    s = DESC[d].replace("⚠️", "").strip()
    return s[:600].rsplit(" ", 1)[0] + "." if len(s) > 600 else s


def nm(d):
    return d.replace("Plant_", "").replace("_Wild", "").replace("RM_", "").lower()


ONE = {"RM_Brakkel": "A", "RM_Cundral": "A", "RM_Gorbeleth": "A", "RM_Maddrick": "A"}
TWO = {"Plant_Grass": "B", "Plant_TallGrass": "B", "RM_Ghemmel": "A", "RM_Greatbole": "A", "RM_Illurin": "A",
       "RM_Kaddrath": "A", "RM_Mirrelbole": "A", "RM_Mourvel": "A", "RM_Nemmer": "A", "RM_Phorrik": "A",
       "RM_Quathis": "A", "RM_Sarnstilt": "A", "RM_Sarquin": "A", "RM_Thalquith": "B", "RM_Tumbel": "A",
       "RM_Veluthar": "A", "RM_Wollick": "A", "RM_YearningFruit": "B", "RM_Zhorrel": "B"}
for d in list(ONE) + list(TWO):
    h = DEC[d]
    want = ONE.get(d) or TWO.get(d)
    assert h["decision"] == want, (d, h["decision"], want)
for d, col in list(ONE.items()) + list(TWO.items()):
    vs = ["b"] if d in ONE else ["b", "c"]
    cw = pow2(VIS[d])
    realistic = ("much more realistic" if d in TWO else "realistic")
    for v in vs:
        extra = {}
        if cw > 256:
            extra["oversize_reason"] = ("plant visualSizeRange max %.1f cells x 128 px/cell exceeds 1024; "
                                        "generator ceiling" % VIS[d]) if VIS[d] * 128 > 1024 else \
                                       "plant visualSizeRange max %.1f cells x 128 px/cell" % VIS[d]
        if d == "RM_Greatbole":
            extra["oversize_reason"] = ("giant tree, drawSize 12-16 cells: 1024 is the generator ceiling "
                                        "(~64-85 px/cell)")
        row(f"{nm(d)}_var{v}_v1", d,
            f"RimWorld plant sprite, the {nm(d)}: a NEW, {realistic.upper()} VARIANT ({v}) of the same species as the "
            "attached chosen render -- same species, palette, structure and scale, a different individual with "
            f"its own shape and arrangement, so a stand of them reads varied. {pdesc(d)} Naturalistic, believable "
            "botanical rendering, painted from a real plant's anatomy. One whole plant, centred.", cw, facings=[],
            canon_reference=[img(d, col)], **extra)

# ============================ FLYER: Yammeth ========================================================
ym = ("a light, wiry canopy flier with two pairs of broad membrane wings in hot magenta and acid yellow, and a "
      "throat sac it puffs out to scream")
flight("yammeth", "RM_Yammeth", "!RM_Yammeth_east", ym, 256, 4, "Things/Pawn/Animal/RM_Yammeth/RM_Yammeth_Flying_",
       owner_note=note("RM_Yammeth"))

out = Path(__file__).with_name("greentide_regen_jobs.json")
out.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
print(len(rows), "rows ->", out)
