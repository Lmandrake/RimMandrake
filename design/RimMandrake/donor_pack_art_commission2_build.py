#!/usr/bin/env python3
"""Builds design/RimMandrake/donor_pack_art_commission2_2026-10-15.json: one artpipe row per DONOR-bytes texture slot
(adult, juvenile, female, swimming, alternate colour) of the 40 KEEP_DONOR_ART_FOR_NOW species. Slot list from
/tmp/dp_slots.json (made by parsing each PawnKindDef: body/female/swim/alternate graphics); sizes = def drawSize."""
import json, re, shutil, os
from pathlib import Path
R = Path("/home/mandrake/rm/foundry"); CANON = R/"design/RimStarWars/canon_references"
REFS = Path("/mnt/d/Luke/dev/_artpipe/_refs/donorpack")
slots = json.load(open("/tmp/dp_slots.json"))
CANONSLUG = {"Grazer": "grazerdomestic"}
SKIP_TP = {"swanimals/Reek/Reek_j", "swanimals/Gullipud/Gullipud_i", "swanimals/Gullipud/Gullipud_j_Swimming_skip"}
TINTED = {"Rancor", "ChrysalideRancor", "Nexu", "Rycrit", "Squall"}
FLYERS = {"Thranta", "Drexl", "Warbird", "Brezak"}
ALTCOL = {
 "RancorA": "tan-brown hide", "RancorB": "mottled blue-grey hide", "RancorC": "grey-brown hide",
 "RancorD": "dark umber-brown hide", "RancorE": "very dark charcoal-brown hide",
 "TukataA": "blue-grey hide", "TukataB": "drab grey-green hide", "TukataC": "dark charcoal-blue hide",
 "TetnissCrabA": "weathered grey scrap-helmet shell", "TetnissCrabB": "rust-brown scrap shell", "TetnissCrabC": "olive-grey scrap shell"}
STYLE = ("Realistic painted natural-history illustration of a living animal, grounded believable anatomy, matte textured "
         "hide, soft painted edges, readable silhouette at game zoom (owner ruling 2026-10-08: realistic, not cartoon).")

def sections(t):
    out = {}; cur = None
    for line in t.splitlines():
        if line.startswith("## "): cur = line[3:].strip().lower(); out[cur] = []
        elif cur: out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}

def brief_bullets(b):
    keep = []; on = False
    for line in b.splitlines():
        if line.startswith("- "): on = True
        if on: keep.append(line)
    t = " ".join(x.strip() for x in keep)
    t = re.sub(r"top-down", "seen from above", t, flags=re.I); t = re.sub(r"\*\*|`", "", t); t = re.sub(r"\s+", " ", t)
    return t[:1500]

def must(m):
    return [re.sub(r"^- \[ \]\s*", "", l).strip() for l in m.splitlines() if l.startswith("- [")]

rows = []
for sp, S in slots.items():
    slug = CANONSLUG.get(sp, sp.lower()); d = CANON/slug
    secs = sections((d/"description.md").read_text(errors="replace"))
    lines = must(secs["must show"]); bullets = brief_bullets(secs["visual brief"])
    imgs = sorted([p for p in d.iterdir() if p.suffix.lower() in (".webp", ".png", ".jpg", ".jpeg") and not p.name.startswith("donor_")],
                  key=lambda p: (0 if "canon" in p.name else 1, p.name))
    if not imgs:
        imgs = [d/"donor_current_sprite.png"]
    dst = REFS/slug; dst.mkdir(parents=True, exist_ok=True)
    cref = []
    for p in imgs:
        shutil.copy2(p, dst/p.name); cref.append(str(dst/p.name))
    label = re.sub(r"(?<!^)([A-Z])", r" \1", sp).lower()
    for tp, v in S.items():
        if tp in SKIP_TP or "Reek/Reek_j" in tp or tp.endswith("Gullipud_i"): continue
        base = tp.split("/")[-1]; roles = set(v["roles"]); sizes = [float(x) for x in v["sizes"]]
        if "corpse" in roles and roles == {"corpse"}: continue
        if "alt" in roles:
            kind = "alt"; sizes = [max(float(x) for x in slots[sp][f"swanimals/{sp}/{sp}"]["sizes"])] if f"swanimals/{sp}/{sp}" in slots[sp] else [max(float(x) for t2 in S.values() for x in t2["sizes"])]
        elif "swim" in roles: kind = "swim"
        elif "female" in roles and "body" not in roles: kind = "female"
        elif (base.endswith("_j") and sp != "TetnissCrab") or base == "RancorW": kind = "juv"
        else: kind = "adult"
        ds = max(sizes); cells = ds
        canvas = 512 if ds <= 4 else 768
        if kind == "adult" and sp == "TetnissCrab": pass
        sid = re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")
        jid = f"donorart_{sid}_v1"
        if kind == "juv":
            who = ("a JUVENILE (young, smaller, softer-featured, proportionally larger head and eyes; keeps the species' colours and "
                   "signature features in a younger form)")
        elif kind == "female": who = "the FEMALE (same species and colours; a distinct individual, slightly lighter build, no invented dimorphism beyond that)"
        elif kind == "swim": who = "its SWIMMING pose (body low in the water at the surface, limbs paddling or trailing, a few painted ripples hugging the body; still the full animal)"
        elif kind == "alt": who = f"a COLOUR VARIANT of the adult with {ALTCOL.get(base, 'a distinct colouring')} (same anatomy and pose as the normal adult, only the colouring differs)"
        else: who = "the ADULT"
        if base.endswith("_m") and sp in ("Grazer", "LothWolf", "Mastmot"): who = "the MALE adult" if kind == "adult" else who
        rel = (f"{cells:g}x{cells:g} cells (drawSize {cells:g}); a colonist is about 1 cell, so this animal is about {cells:g} colonists "
               f"across the frame")
        if cells < 1: rel = f"{cells:g}x{cells:g} cells (drawSize {cells:g}); about {int(round(cells*100))}% of one colonist's cell, a small animal that still fills its square frame"
        ms = " ".join(f"({i}) {x}." if not x.endswith('.') else f"({i}) {x}" for i, x in enumerate(lines, 1))
        tint = (" Paint the FINAL FULL COLOUR directly: this creature's current donor art is a greyscale tint mask, ours must carry its own colours, "
                "stripes and markings with no mask and no flat grey.") if sp in TINTED else ""
        fly = " If it flies, show it airborne in side profile with the wings half-spread, both wings fully inside the frame." if sp in FLYERS else ""
        prompt = (f"RimWorld creature sprite of {who} of the {label} (canon: {slug}). SCALE: footprint {rel}. CANVAS: {canvas}x{canvas}, square, "
                  f"matching the square drawSize; the animal fills the frame width. VIEW: orthographic side view facing right (east), standing "
                  f"naturally on a transparent background, whole animal in frame, centred. SUBJECT (from the canon entry): {bullets} "
                  f"MUST SHOW: {ms}{tint}{fly}")
        rows.append({
            "id": jid, "rimflow_item_id": "DONOR_DEFS_PORT_TO_OURS_1", "prompt": prompt, "canvas_w": canvas, "canvas_h": canvas,
            "drawsize": cells, **({"oversize_reason": "detail floor: 512px minimum so the painted anatomy reads (owner: sizing errs generous)"} if canvas > int(128*cells) and canvas == 512 else {}),
            "facings": "east,south,north", "priority": 31, "style_notes": STYLE, "canon": slug, "canon_reference": cref,
            "target_def": f"RSW_{sp}", "target_texpath": tp, "install_to": f"src/RimStarWars/SWBestiary/Textures/{tp}_{{facing}}.png",
            "biome_neutral": True, "background": "transparent", "_species": sp, "_kind": kind})
json.dump([{k: v for k, v in r.items() if not k.startswith("_")} for r in rows],
          open(R/"design/RimMandrake/donor_pack_art_commission2_2026-10-15.json", "w"), indent=1)
print(len(rows), "rows"); 
from collections import Counter; print(Counter(r["_kind"] for r in rows))
for r in rows: print(r["id"], r["_kind"], r["drawsize"], r["canvas_w"])
