#!/usr/bin/env python3
"""Build fill_queue rows for the owner's Long Shade sheet rulings (desert_sheet_2026-10-04). Notes carried verbatim.

Same method as build_greentide_regen_jobs.py. Ids start `regen_ls_canon_` / `regen_ls_x_` so that, at equal
priority 0, they sort (and are claimed) after every miasma_*, regen_fw_* and regen_gt_* job, canon first.

Anchoring: a picked east whose own job is in artpipe done/ is used as a real `derive_from` master. A picked east
whose job is in failed/ (canon-gate failure the owner overrode) cannot be a master -- artpiped routes every job
derived from a failed master straight to failed/ -- so those rows attach the picked PNG as the first
`canon_reference` instead (the daemon attaches only the first existing canon_reference).
"""
import json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
DECF = json.load(open(REPO / "Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json"))
DEC = DECF["decisions"]
SNAP = json.load(open(REPO / "infrastructure/state/art/sheets/desert_sheet_2026-10-04.snapshot.json"))["rows"]
CANON = REPO / "design/RimStarWars/canon_references"
STORE = Path("/mnt/d/Luke/dev/_artstore")
PRI = 0
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
REG = ("long shade register: an open desert of ochre deep-sand sheets and pale-gold cracked hardpan under a "
       "perpetual golden hour: the sun pinned on the horizon forever, apricot at the horizon and rose, the last "
       "ten minutes before dusk that never end; lit surfaces warm amber, ochre and rust, every shaded fold a cool "
       "violet-blue (that warm/cool split is the signature); light the subject with a warm apricot key from the "
       "front-top and cool violet in its own undersides and recesses, but bake NO cast shadow onto the ground "
       "-- the engine draws the long parallel shadows; no night, no rain and nothing rain-slicked")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic, grounded and alien, naturalistic and "
         "zoologically/botanically believable, never cartoonish; one centred subject on a fully transparent "
         "background.")
F3 = ["east", "south", "north"]
NS = ["south", "north"]
SW = "swanimals/"
P = "regen_ls_"


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
DS = {}


def row(id, d, prompt, cw, facings=F3, canon=None, owner_note=None, neutral=False, **kw):
    n = note(d) if owner_note is None else owner_note
    r = {"id": P + id, "rimflow_item_id": ITEM, "target_def": d, "prompt": lead(n) + prompt,
         "style_notes": STYLE, "canvas_w": cw, "canvas_h": cw, "facings": facings,
         "background": "transparent", "channel": "codex", "priority": PRI}
    if neutral:
        r["biome_neutral"] = True
    else:
        r["biome_register"] = REG
    if canon:
        r["canon"] = canon
    if n:
        r["owner_note"] = n
    if d in DS:
        r["drawsize"] = DS[d]
    if cw > 256:
        r["oversize_reason"] = kw.pop("oversize", f"drawSize {DS.get(d)} cells x 128 px/cell")
    kw.pop("oversize", None)
    r.update(kw)
    if r.get("derive_from") and r["derive_from"].startswith("@"):
        r["derive_from"] = P + r["derive_from"][1:]
    rows.append(r)


POSES = {1: "wings raised high at the top of the upstroke",
         2: "wings level and spread wide mid-downstroke",
         3: "wings swept fully down at the bottom of the downstroke",
         4: "wings level and rising mid-upstroke"}


def flight(slug, d, master, desc, cw, frames, texprefix, canon, owner_note, ref_canon):
    """whole-body directional flip-book frames derived from the picked standing east (a done job)."""
    for n in range(1, frames + 1):
        row(f"{slug}_flying_{n}_v1", d,
            f"RimWorld creature FLYING animation frame {n} of {frames} (whole-body flip-book frame, not a wing "
            f"layer), the same individual as the accepted standing render: {desc}. In flight, body level, legs "
            f"tucked, {POSES[n]}. One animal, whole body, centred.", cw, canon=canon, neutral=True,
            owner_note=owner_note, derive_from=master, canon_reference=[str(ref_canon)],
            target_texpath=f"{texprefix}{n}")


# adult (largest) drawSize read from the defs; canvas = next pow2 of drawSize*128, floor 256, ceiling 1024
DS.update({"RSW_Sketto": 1.25, "RSW_TeeMuss": 3.0, "RSW_Falumpaset": 4.0, "RSW_Nerf": 2.0, "RSW_Dewback": 4.0,
           "RSW_Uvak": 3.5, "RSW_Shyrack": 2.0, "RSW_Gorg": 1.05, "RSW_FrilledGorg": 1.5, "JOE_Landopus": 0.8,
           "RM_Dakkra": 2.0, "RM_Chorn": 5.0, "RM_Venomvine": 1.2})
SAME = ("The FIRST attached image is the owner's accepted EAST (side) render of this very individual: draw the "
        "{v} view of exactly that animal -- same species, anatomy, colouring, markings, scale and painted style.")

# =============================== CANON ================================================================
# ---- Sketto (picked C east; canon prop photo anatomy). Flight from the same pick (done master absent -> canon_ref)
sk = ("a small, lean, dragonfly-like reptile: a slim elongated body, a long thin neck, a small narrow "
      "wedge-shaped head with a mouth full of fangs and two long curved tusk-like fangs hanging from the upper "
      "jaw, four narrow long translucent insect-like veined wings (two pairs), a very long thin whip-like tail "
      "as long as the body or longer ending in a small tuft or fan, and four thin spindly clawed legs")
SK_E = img("RSW_Sketto", "C", "east")
SK_CANON = str(CANON / "sketto/wookieepedia_canon_1.webp")
for v in NS:
    row(f"canon_sketto_v1", "RSW_Sketto",
        f"RimWorld creature sprite of the Star Wars canon sketto, {v.upper()} view: {sk}. " + SAME.format(v=v)
        + " Follow the canon closely. One animal, whole body, centred.", pow2(DS["RSW_Sketto"]), facings=[v],
        canon="sketto", neutral=True, canon_reference=[SK_E, SK_CANON], target_texpath=SW + "Sketto/Sketto")
# flight: the Sketto C east's job is in failed/, so no derive master -> picked PNG is the anchor
for n in range(1, 5):
    row(f"canon_sketto_flying_{n}_v1", "RSW_Sketto",
        f"RimWorld creature FLYING animation frame {n} of 4 (whole-body flip-book frame, not a wing layer), the "
        f"same individual as the accepted standing render: {sk}. In flight, body level, legs tucked, "
        f"{POSES[n]}. " + SAME.format(v="flying") + " One animal, whole body, centred.", 256,
        canon="sketto", neutral=True, canon_reference=[SK_E, SK_CANON],
        target_texpath=SW + "Sketto/Sketto_Flying_" + str(n))

# ---- TeeMuss (picked C east is 256 < 512 canvas -> east re-render at 512, N/S derived from the new east)
tm = ("a long-legged, deep-chested camel-like ungulate with knobby knees, an arched neck carried forward, a long "
      "thin tail with a dark brush, mottled tan to sandy-brown short hide with a shaggy darker gold mane along "
      "neck and back, a heavy blunt wrinkled head with a short trunk-like nose boss, small horn nubs and a hooked "
      "dark lower tusk, long wide pointed dark ears bent back, and broad two-toed cream hooves")
TM_E = img("RSW_TeeMuss", "C", "east")
TM_CANON = str(CANON / "teemuss/wookieepedia_canon_1.webp")
cw = pow2(DS["RSW_TeeMuss"])
row("canon_teemuss_v1", "RSW_TeeMuss",
    f"RimWorld creature sprite of the Star Wars canon tee-muss, EAST (side) view, REDRAWN AT THE PROPER FULL "
    f"RESOLUTION ({cw}x{cw}): {tm}. The FIRST attached image is the owner's accepted render at too low a "
    "resolution: reproduce that exact individual, pose and colouring, but sharp and detailed at full size. "
    "One animal, whole body, centred.", cw, facings=["east"], canon="teemuss", neutral=True,
    canon_reference=[TM_E, TM_CANON], target_texpath=SW + "TeeMuss/TeeMuss")
row("canon_teemuss_v1_ns", "RSW_TeeMuss",
    f"RimWorld creature sprite of the tee-muss at full resolution ({cw}x{cw}): {tm}. Same individual as the "
    "accepted east render.", cw, facings=NS, canon="teemuss", neutral=True, derive_from="@canon_teemuss_v1_east",
    canon_reference=[TM_CANON, TM_E], target_texpath=SW + "TeeMuss/TeeMuss")

# ---- Falumpaset (picked C east 256; def adult drawSize 4.0 -> 512: east re-render too, judgement addition)
fa = ("a huge barrel-bodied, heavy-rumped herbivore on long thick legs, a long thick downward-sloping neck and a "
      "smallish head held low with a droopy pendulous lip, small round ears and eyes, no horns; tan to mid-brown "
      "finely wrinkled short-haired hide with scattered dark brown spots and a lighter belly; broad splayed dark "
      "feet with darker lower legs; a short thin tail with a small tuft")
FA_E = img("RSW_Falumpaset", "C", "east")
FA_CANON = str(CANON / "falumpaset/wookieepedia_canon_1.webp")
cw = pow2(DS["RSW_Falumpaset"])
row("canon_falumpaset_v1", "RSW_Falumpaset",
    f"RimWorld creature sprite of the Star Wars canon falumpaset, EAST (side) view, redrawn at the def's full "
    f"resolution ({cw}x{cw}) so the set matches: {fa}. The FIRST attached image is the owner's accepted render "
    "(256 px): reproduce that exact individual, pose and colouring, sharp at full size. One animal, whole "
    "body, centred.", cw, facings=["east"], canon="falumpaset", neutral=True, canon_reference=[FA_E, FA_CANON],
    target_texpath=SW + "Falumpaset/Falumpaset")
row("canon_falumpaset_v1_ns", "RSW_Falumpaset",
    f"RimWorld creature sprite of the falumpaset: {fa}. Same individual as the accepted east render.", cw,
    facings=NS, canon="falumpaset", neutral=True, derive_from="@canon_falumpaset_v1_east",
    canon_reference=[FA_CANON, FA_E], target_texpath=SW + "Falumpaset/Falumpaset")

# ---- Nerf (picked E east = the default/female graphic swanimals/Nerf/Nerf_f)
ne = ("a heavy stocky bison-like bovine: humped shoulders higher than the rump, a big shaggy head carried low, "
      "long coarse thick curly deep chocolate-brown fur forming a heavy mane over shoulders and neck, short strong "
      "legs with dark hoof feet, two dark grey curved horns sweeping out and up, a broad dark grey muzzle, small "
      "eyes under the fur and a thin hairless rope-like tail")
NE_E = img("RSW_Nerf", "E", "east")
NE_CANON = str(CANON / "nerf/wookieepedia_canon_1.webp")
for v in NS:
    row(f"canon_nerf_v1", "RSW_Nerf",
        f"RimWorld creature sprite of the Star Wars canon nerf, {v.upper()} view (the female/default graphic): {ne}. "
        + SAME.format(v=v) + " One animal, whole body, centred.", pow2(DS["RSW_Nerf"]), facings=[v], canon="nerf",
        neutral=True, canon_reference=[NE_E, NE_CANON], target_texpath=SW + "Nerf/Nerf_f")

# ---- Dewback (picked H east 256; wants 4 cells wide -> canvas 512, east re-render + N/S derived)
de = ("a long, low-slung scaly reptile with a warm olive-green to yellow-green hide, darker and more mottled "
      "toward the back ridge, raised pebbled scale texture, a long heavy tail, a broad blunt-snouted head with a "
      "wide mouth and short thick legs built to carry a rider")
DE_E = img("RSW_Dewback", "H", "east")
DE_CANON = str(CANON / "dewback/wookieepedia_infobox.jpg")
cw = pow2(4.0)
row("canon_dewback_v1", "RSW_Dewback",
    f"RimWorld creature sprite of the Star Wars canon dewback, EAST (side) view, drawn FOUR CELLS WIDE: the "
    f"animal fills the full {cw}px canvas width (128 px per cell), {de}. The FIRST attached image is the owner's "
    "accepted render at only 256 px: reproduce that exact individual and colouring but redrawn large, sharp and "
    "detailed. One animal, whole body, centred.", cw, facings=["east"], canon="dewback", neutral=True,
    canon_reference=[DE_E, DE_CANON], target_texpath=SW + "Dewback/Dewback",
    oversize="owner: make it four cells wide; 4 cells x 128 px/cell = 512")
row("canon_dewback_v1_ns", "RSW_Dewback",
    f"RimWorld creature sprite of the dewback, drawn FOUR CELLS WIDE (fills the {cw}px canvas): {de}. Same "
    "individual as the accepted east render.", cw, facings=NS, canon="dewback", neutral=True,
    derive_from="@canon_dewback_v1_east", canon_reference=[DE_CANON, DE_E],
    target_texpath=SW + "Dewback/Dewback", oversize="owner: make it four cells wide; 4 cells x 128 px/cell = 512")

# ---- Uvak flight (C standing set is a done job: real derive_from)
uv = ("a wyvern-like flying mount: a heavy scaled reptilian torso, strong hind legs with dark four-toed talons, a "
      "long thick tapering tail, a long neck, a bird-like head with a long thick hooked raven-like beak and a "
      "wide red mouth interior, an emerald eye, dark grey pebbled hide and large bat-style leathery wings with "
      "visible finger-bone ribs and red-orange to pink membrane")
flight("canon_uvak", "RSW_Uvak", "longshade_rsw_uvak_v1_east", uv, 256, 4, SW + "Uvak/Uvak_Flying_", "uvak",
       note("RSW_Uvak"), CANON / "uvak/wookieepedia_canon_1.webp")
# ---- Shyrack flight
sh = ("a bat/pterosaur-like eyeless flier: a heavy bulbous pot-bellied body, two large leathery bat wings with dark "
      "bony struts and purple membrane, a blunt wrinkled domed pinkish-tan head with deep folds and a toothed "
      "mouth and NO eyes, long thin hind legs with large hooked dark talons, a thin sinuous tail, a tan "
      "pinkish-flesh body with blue-violet limbs")
flight("canon_shyrack", "RSW_Shyrack", "longshade_rsw_shyrack_v1_east", sh, 256, 4, SW + "Shyrack/Shyrack_Flying_",
       "shyrack", note("RSW_Shyrack"), CANON / "shyrack/wookieepedia_legends_1.webp")

# ---- variants: east-only ticked variants get N and S (picked east = first canon_reference). NEW texPaths.
VARIANTS = (("RSW_Gorg", "L", "gorg", "Gorg/GorgV_L", "a gorg, a hunched, long-clawed, big-headed bipedal "
             "predator-lizard of the desert"),
            ("RSW_FrilledGorg", "I", "frilledgorg", "FrilledGorg/FrilledGorgV_I", "a frilled gorg, a gorg with a "
             "ragged frill of leaf-like flaps around its head and body"),
            ("RSW_FrilledGorg", "K", "frilledgorg", "FrilledGorg/FrilledGorgV_K", "a frilled gorg, a gorg with a "
             "ragged frill of leaf-like flaps around its head and body"))
for d, col, slug, tex, desc in VARIANTS:
    e = img(d, col, "east")
    for v in NS:
        row(f"canon_{slug}_{col.lower()}_v1", d,
            f"RimWorld creature sprite, {v.upper()} view of a colour/pattern VARIANT of {desc}. "
            + SAME.format(v=v) + " One animal, whole body, centred.", pow2(DS[d]), facings=[v], neutral=True,
            canon_reference=[e], target_texpath=SW + tex)

# =============================== NON-CANON ============================================================
# ---- Landopus (thraia): half-buried-in-sand look, picked F east
lp = ("a bad-tempered, sand-coloured land octopus-squid HALF-BURIED IN RIPPLED SAND: the lower body and most of "
      "the arms buried, only the upper mantle with its scatter of odd vivid blue ringed circles, the watchful "
      "eyes, a few long slender tentacle tips and the wicked slender parrot-like beak emerging from the surface")
LP_E = img("JOE_Landopus", "F", "east")
for v in NS:
    row(f"x_landopus_buried_v1", "JOE_Landopus",
        f"RimWorld creature sprite, {v.upper()} view: {lp}. " + SAME.format(v=v) + " Same half-buried-in-sand look. "
        + ("North is a true rear view from directly behind: no face, no eyes visible. " if v == "north" else "")
        + "One animal, whole body, centred.", pow2(DS["JOE_Landopus"]), facings=[v], derive_from="ls_regen_JOE_Landopus_swim_v1_east",
        canon_reference=[LP_E], target_texpath="Things/Pawn/Animal/landopus/landopus_buried")

# ---- Dakkra rest (fins flared) N/S from the done master ls_regen_RM_Dakkra_rest_v1_east
dk = ("the dakkra, a close, low shadow-ambush predator the size of a large dog: lean and low with a wide mouth "
      "and heavy forelimbs, dark slate hide with a warm rust line down the spine, AT REST in the shade: every spine "
      "fin fully erected and flared up in a tall fan of thin veined rust-to-apricot membrane and the tail-tip fan "
      "fully spread, crouched low and coiled in ambush")
DK_E = img("RM_Dakkra", "C", "east")
for v in NS:
    row(f"x_dakkra_rest_v1", "RM_Dakkra",
        f"RimWorld creature sprite, {v.upper()} view: {dk}. " + SAME.format(v=v) + " Fins flared. "
        + ("North is a true rear view from directly behind: no face, no eyes visible. " if v == "north" else "")
        + "One animal, whole body, centred.", pow2(DS["RM_Dakkra"]), facings=[v], derive_from="ls_regen_RM_Dakkra_rest_v1_east",
        canon_reference=[DK_E], target_texpath="Things/Pawn/Animal/RM_Dakkra/RM_Dakkra_rest")

# ---- Chorn: REDO 5 cells wide, 3 facings anchored on the in-game east (column A)
ch = ("a towering, long-legged giant five cells across with a flat rocky slab of a back, a raised hump over the "
      "shoulders and a long hooked beaked head on a thick neck; hide cracked and mottled ochre and rust like "
      "sun-baked stone; a standing herd is its own patch of shade")
CH_E = img("RM_Chorn", "A", "east")
cw = pow2(5.0)
row("x_chorn_v2", "RM_Chorn",
    f"RimWorld creature sprite, the chorn (formerly sollak): {ch}. The attached image is the current in-game "
    "EAST render: keep roughly the same animal, colouring and anatomy, but draw it FIVE CELLS WIDE -- the animal "
    f"fills the full width of the {cw}px canvas (the def draws it at 5.0 cells), huge and monumental, sharp, "
    "detailed. One animal, whole body, centred.", cw, canon_reference=[CH_E],
    target_texpath="Things/Pawn/Animal/RM_Sollak/RM_Sollak",
    oversize="owner: five cells wide; 5 x 128 = 640 px -> 1024 canvas (next power of two)")

# ---- Venomvine: REDO the plant (single image)
vv = ("RimWorld plant sprite, painterly vanilla-RimWorld flora style: the desert venomvine, a low, matted tangle of "
      "thick woody rust-dark runners sprawling flat across the ground, the whole plant in dark rust-umber and "
      "dried-blood brown with NO green anywhere. Short recurved thorns line the undersides of the runners in paler "
      "bone-tan and catch the light so the hooks read clearly. A few runners lift slightly into low arches but "
      "nothing stands tall: a wide, snarled, ankle-high thicket that reads as hostile and territorial at a "
      "glance -- a thorny vine, absolutely NOT a pillar, arm, column or limb. Single plant, one tangle, seen at "
      "the slight isometric RimWorld camera angle, centred, no ground scenery.")
row("x_venomvine_v2", "RM_Venomvine", vv, pow2(1.2), facings=[], target_texpath="Things/Plant/RM_Venomvine")

out = Path(__file__).with_name("longshade_regen_jobs.json")
out.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
print(len(rows), "rows ->", out)
