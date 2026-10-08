#!/usr/bin/env python3
"""Venomvine rescue (owner, 2026-10-08): fresh art for EVERY venomvine species, queued at the FRONT of the artpipe.

Ids start `0vv_` so that, at priority 0, they sort (and are claimed: artpiped sorts by (priority, filename)) ahead of
every other priority-0 job (miasma_*, regen_*). Notes carried verbatim. The Long Shade helper's
`regen_ls_x_venomvine_v2` is folded in here (its note verbatim) and withdrawn from pending.

Anchors: a species whose accepted picture exists gets that picture as the first `canon_reference` (anatomy/identity
anchor for a variation, not a restyle reference). The six newer forms have NO real art (they borrowed a pillar-arm
render that was never a venomvine) so they are generated fresh from the design brief.
"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEC = json.load(open(REPO / "Transient/biome_ffar/leaningscrub_sheet_2026-10-05.decisions.json"))["decisions"]
STORE = Path("/mnt/d/Luke/dev/_artstore")
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
CHAT = "Please please generate all the venomvines"          # his typed message tonight (relayed by BENCH)
LS_NOTE = "REDO THE VENOM VINE!! Totally wrong art."         # his Long Shade row note (desert_sheet_2026-10-04)

REG_SCRUB = ("leaning scrub register: a windswept arid scrubland plain of knee-high silver-green fuzz under a pale "
             "overcast sky, soft diffuse light; everything leans sunward with the prevailing wind; the subject keeps "
             "its own natural colours, no strong biome grade; bake NO cast shadow onto the ground")
REG_LONG = ("long shade register: an open desert of ochre deep-sand sheets and pale-gold cracked hardpan under a "
            "perpetual golden hour; lit surfaces warm amber, ochre and rust, every shaded fold a cool violet-blue; "
            "light the subject with a warm apricot key from the front-top and cool violet in its own undersides, "
            "but bake NO cast shadow onto the ground")
STYLE = ("Matte painterly vanilla-RimWorld house style, realistic, grounded and alien, botanically believable, never "
         "cartoonish, no outlines; one centred subject on a fully transparent background, no ground, no props.")
LAWS = ("Venomvine visual laws: a near-black island of woody cane (never green), man-height or more, leaning sunward "
        "like everything on the plain, with its OWN accent colour on the shared near-black; thorns are short, "
        "recurved and bone-pale; NO Earth-nameable look-alike (no briar, bramble, rose or bamboo silhouette). "
        "This is a THORNY VINE PLANT -- absolutely NOT a pillar, column, arm, limb, worm, stone or sculpture. "
        "Seen at the slight top-down three-quarter RimWorld camera angle.")
VARY = ("Variation {n} of {k}: a distinctly different individual of the same species (different growth form, size, "
        "density and lean), clearly the same plant.")


def store(sha):
    p = STORE / sha[:2] / f"{sha}.png"
    assert p.is_file(), p
    return str(p)


def rnote(d):
    v = DEC.get(d) or {}
    return (v.get("note") or "") if v.get("at") else ""


rows = []


def job(slug, d, body, texpath, note, n, k, reg=REG_SCRUB, anchor=None, extra=""):
    lead = f'Owner\'s note, verbatim, overrides everything below: "{note}" ' if note else ""
    r = {"id": f"0vv_{slug}_v{n}", "rimflow_item_id": ITEM, "target_def": d,
         "prompt": lead + f"RimWorld plant sprite: {body} {LAWS} " + VARY.format(n=n, k=k) + (" " + extra if extra else ""),
         "style_notes": STYLE, "biome_register": reg, "canvas_w": 256, "canvas_h": 256, "facings": [],
         "background": "transparent", "channel": "codex", "priority": 0, "target_texpath": texpath}
    if note:
        r["owner_note"] = note
    if anchor:
        r["canon_reference"] = [store(anchor)]
        r["prompt"] += (" The attached image is the owner's ACCEPTED picture of this species: keep its species "
                        "identity, palette and painted style; draw a new individual, not a copy.")
    rows.append(r)


LSF = "Things/Plant/"
# --- 1. the desert venomvine (Long Shade, RM_Venomvine): folds regen_ls_x_venomvine_v2 in -------------------------
vv = ("the desert venomvine, a low, matted tangle of thick woody rust-dark runners sprawling flat across the "
      "ground, the whole plant in dark rust-umber and dried-blood brown with NO green anywhere; short recurved "
      "thorns line the undersides of the runners in paler bone-tan and catch the light so the hooks read clearly; "
      "a few runners lift into low arches but nothing stands tall: a wide, snarled, ankle-high tangle that reads as "
      "hostile and territorial at a glance.")
for n in range(1, 5):
    r = job("desert_venomvine", "RM_Venomvine", vv, LSF + "RM_Venomvine/RM_Venomvine", f"{LS_NOTE} / {CHAT}", n, 4,
            reg=REG_LONG)
for r in rows:  # this species is low and desert: the 'man-height' law does not apply
    r["prompt"] = r["prompt"].replace("man-height or more, ", "low and ankle-high (the desert form), ")

# --- 2. the six forms that wore the pillar-arm picture: fresh, from the design brief ----------------------------
SIX = {
    "RM_RearingVenomvine": ("rearing venomvine, AT REST: a near-black thicket form whose canes lie low in long "
                            "sunward sweeps, laid lower and flatter than the base thicket; pale bone-grey banding "
                            "hidden on the undersides of the canes."),
    "RM_WalkingVenomvine": ("walking venomvine: a long, low, wedge-shaped stand; its tail is old near-black man-high "
                            "cane, tapering sunward into a leading edge of thin new runners laid flat along the "
                            "ground and pointing sunward; accent: the new runners are a dull rust-ochre, soft-looking "
                            "and thornless, reading clearly as the young end against the black tail."),
    "RM_HoardVenomvine": ("hoard venomvine: a squat, very dense near-black knot, man-high, its canes coiled inward "
                          "like a fist rather than leaning out; accent: small cold metallic glints scattered deep in "
                          "the interior -- bits of metal, glass and wire grown into the cane; a scrap nest with no "
                          "bird."),
    "RM_QuenchVenomvine": ("quench venomvine: thick near-black canes with swollen joints every hand-span along each "
                           "cane like knuckles; accent: the knuckle swellings carry a faint wet slate-blue sheen."),
    "RM_SwornVenomvine": ("sworn venomvine: a cultivated-looking near-black venomvine, cut and trained -- canes bound "
                          "in lines, the top flat and level like a clipped hedge, unmistakably grown on purpose; "
                          "accent: small knots of pale undyed fibre tied along the canes, the planters' marks."),
    "RM_SheddingVenomvine": ("shedding venomvine: a tall, ragged near-black stand whose sunward face is stripped bare, "
                             "showing pale scarred cane where thorns have torn away; at its downwind foot a small fan "
                             "of rust-coloured thorn litter."),
}
for d, body in SIX.items():
    slug = d[3:].replace("Venomvine", "").lower() + "_venomvine"
    note = rnote(d) or CHAT
    for n in range(1, 5):
        job(slug, d, body, f"{LSF}{d}/{d}", note, n, 4)
# extra states the briefs ask for (wiring is a follow-up: no C# reads a state graphic yet)
for n in range(1, 3):
    job("rearing_venomvine_reared", "RM_RearingVenomvine",
        "rearing venomvine, REARED: every near-black cane snapped bolt upright AGAINST the sunward lean, a black fan "
        "standing straight up; the pale bone-grey banding on the cane undersides now shows as a pale flash.",
        f"{LSF}RM_RearingVenomvine_Reared/RM_RearingVenomvine_Reared", rnote("RM_RearingVenomvine") or CHAT, n, 2)
    job("quench_venomvine_spent", "RM_QuenchVenomvine",
        "quench venomvine, SPENT after bursting on fire: thick near-black canes whose knuckle swellings are collapsed "
        "and cracked open, the cane scorched and dull, the slate-blue sheen gone.",
        f"{LSF}RM_QuenchVenomvine_Spent/RM_QuenchVenomvine_Spent", rnote("RM_QuenchVenomvine") or CHAT, n, 2)

# --- 3. the species with an accepted picture: more variations anchored on it ------------------------------------
ANCH = {  # def: (accepted sha, count, body)
    "RM_VenomvineThicket": ("29ae79060e162f6fc7259a748839739ae3472935fbd61ae52058afa4ab11ff96", 3,
                            "venomvine thicket, the base fortress form: a standing wall of woven near-black canes "
                            "rising past man-height, ranks of recurved bone-pale thorns, too dense to cut."),
    "RM_TwitcherVenomvine": ("2ee6a868c73c", 2, "twitcher venomvine: a stand that strikes once at whatever comes "
                             "close with one whip-crack of a long cane, then droops, visibly spent."),
    "RM_DrippingVenomvine": ("6cb4791ebe11", 2, "dripping venomvine: a stand that hangs surplus venom in amber "
                             "beads along every cane."),
    "RM_HollowVenomvine": ("63f3f99400cb", 2, "hollow venomvine: an old stand dead from the inside and standing "
                           "anyway, tubes of grey cane with galleries wide enough to crawl through."),
    "RM_CrownVenomvine": ("26cacbc18993", 2, "crown venomvine: the rarest stand, climbing past man-height into a "
                          "single black column that flowers at the top -- the only flower on the plain."),
}
for d, (sha, k, body) in ANCH.items():
    full = next(p.stem for p in STORE.glob(f"{sha[:2]}/{sha}*.png")) if len(sha) < 64 else sha
    slug = d[3:].replace("Venomvine", "").lower() + "_venomvine"
    for n in range(1, k + 1):
        job(slug, d, body, f"{LSF}{d}/{d}", (rnote(d) + " / " if rnote(d) else "") + CHAT, n, k, anchor=full)

out = Path(__file__).with_name("venomvine_regen_jobs.json")
out.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
print(len(rows), "rows ->", out)
