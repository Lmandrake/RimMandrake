#!/usr/bin/env python3
"""build_species_sheet.py — one command to (re)build the Lantern Deeps
FLORA/FAUNA species review sheet (a species roster, not an art-verdict sheet —
compare build_art_sheet.py, which reviews the 49 raw texture slots).

One row per plant/animal that actually spawns in RM_LanternDeeps, showing the
art the def renders with RIGHT NOW (not the intended art): the biome def's own
<wildPlants>/<wildAnimals> commonality tables are the enumeration and the sort
key — DeepFloraPlanter.cs (2026-09-18 comment) confirms the plant list is read
directly off map.Biome.wildPlants at spawn time, so there is no separate
"planter species table" to reconcile against it.

Usage:
    python3 build_species_sheet.py                 # dry run: validates the plan, writes nothing
    python3 build_species_sheet.py --apply          # writes the sheet + thumbnails + decisions seed

Then review it with the review-sheets sidecar (this subagent does not serve it
— the parent session does):
    python3 <review-sheets skill>/assets/serve_sheet.py --sheet <out> --decisions <decisions>
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html")

OUT_HTML = REPO_ROOT / "Transient" / "deeps_flora_fauna_review_2026-09-18.html"
OUT_THUMBS_DIR = REPO_ROOT / "Transient" / "deeps_review_thumbs_2026-09-18"
OUT_DECISIONS = REPO_ROOT / "Transient" / "deeps_flora_fauna_review_2026-09-18.decisions.json"

LD_TEX = REPO_ROOT / "src/RimMandrake/LanternDeeps/Textures/RM_LanternDeeps/Things"
ARTSRC = REPO_ROOT / "infrastructure/artpipe/_artsrc"
SWB_TEX = REPO_ROOT / "src/RimStarWars/SWBestiary/Textures"
ART_DECISIONS = REPO_ROOT / "Transient/deeps_art_review_2026-09-18.decisions.json"

THUMB_MAX = 160

# ---------------------------------------------------------------------------
# FLORA — RM_LanternDeeps.wildPlants, MEASURED from
# src/RimMandrake/LanternDeeps/Defs/Biomes/RM_LanternDeeps.xml (2026-09-18).
# Each: (defName, label, commonality, description, texPath, art_source)
# art_source is a Path to the actual PNG this row renders with right now, or
# None if none was found anywhere (MISSING).
# ---------------------------------------------------------------------------
FLORA = [
    ("RM_DeepMycelium", "mycelium", 5.0,
     "Extremely wide-spread mycelium of many different species, carpeting the floors of the Deeps. Herbivores eat it where it grows.",
     "RM_LanternDeeps/Things/Plant/Mycelium",
     LD_TEX / "Plant/Mycelium/A.png", "owned", ""),
    ("RM_ZivvitTaper", "zivvit taper", 1.0,
     "A mushroom with a long narrow cap that glows at the tip. Cave dwellers use zivvit the way other people use flowers, or candles.",
     "RM_LanternDeeps/Things/Plant/ZivvitTaper",
     LD_TEX / "Plant/ZivvitTaper/A.png", "owned", ""),
    ("RM_QuorrFern", "quorr fern", 0.5,
     "A symbiosis between two species of mushroom and a fern, unique to the crystal voids. Quorr is what the Deeps have instead of undergrowth.",
     "RM_LanternDeeps/Things/Plant/QuorrFern",
     LD_TEX / "Plant/QuorrFern/A.png", "owned", ""),
    ("RM_ThrakkCap", "thrakk cap", 0.5,
     "A strong crystal-capped mushroom tree. Slow-growing, but thrakk wood is very tough and very handsome, and it does not much care what it grows in.",
     "RM_LanternDeeps/Things/Plant/ThrakkCap",
     LD_TEX / "Plant/ThrakkCap/A.png", "owned", ""),
    ("RM_NurrikGill", "nurrik gill", 0.4,
     "Its cap is almost black; its gills glow brightly beneath. Nurrik grows in water, or in ground wet enough to pass for it.",
     "RM_LanternDeeps/Things/Plant/NurrikGill",
     LD_TEX / "Plant/NurrikGill/A.png", "owned", ""),
    ("RM_OsskBramble", "ossk bramble", 0.3,
     "Tangled, thorny shoots tipped with crystal. Ossk grows in clusters and slows anyone moving over it; grazers strip it anyway.",
     "RM_LanternDeeps/Things/Plant/OsskBramble",
     LD_TEX / "Plant/OsskBramble/A.png", "owned", ""),
    ("RM_BrellikBulb", "brellik bulb", 0.3,
     "With brightly glowing amber tips, brellik draws animals to eat it and unwittingly carry its durable spores through the dark.",
     "RM_LanternDeeps/Things/Plant/BrellikBulb",
     LD_TEX / "Plant/BrellikBulb/A.png", "owned", ""),
    ("RM_KuvraSpout", "kuvra spout", 0.2,
     "An aquatic fungus that grows as an upside-down cone and glows in the dark. Kuvra cones, dried, hold liquid.",
     "RM_LanternDeeps/Things/Plant/KuvraSpout",
     LD_TEX / "Plant/KuvraSpout/a.png", "owned", ""),
    ("RM_Lanternstone_Sowable", "fast growing lanternstone", 0.1,
     "Unlike its volatile cousins this strain grows fast and does not shatter when damaged — but it will only take root in fertile ground. Cave dwellers farm it for light and for trade.",
     "RM_LanternDeeps/Things/Crystals/LanternstoneMedium (shared with the Medium rock formation Building)",
     LD_TEX / "Crystals/LanternstoneMedium/B.png", "owned",
     "Variant A of this texPath FAILED the facts gate twice (art_review sheet, 2026-09-18) — ships with B/C only. Immature stage (LanternstoneSowableImmature) is also on disk."),
    ("RM_VellokReed", "vellok reed", 0.05,
     "An aquatic fungus tall enough to be logged, lit from inside. Vellok grows fast in the shallows, but it does not yield much usable material.",
     "RM_LanternDeeps/Things/Plant/VellokReed",
     LD_TEX / "Plant/VellokReed/A.png", "owned", ""),
    ("RM_TwitchingPuffer", "twitching puffer", 0.02,
     "A swollen spore-bladder ringed with finger-length tentacles that twitch as it pumps. The tentacles are its fruit and regrow when cut; the ball, if torn, puffs stinging spores.",
     "RM_LanternDeeps/Things/Plant/TwitchingPuffer/PufferGrown",
     ARTSRC / "twitchingpuffer_grown_v1/twitchingpuffer_grown_v1.png", "approved-not-wired",
     "Grown-stage render only — facts-PASS in infrastructure/artpipe/done, but NOT recorded in any owner decisions file yet (not in deeps_art_review_2026-09-18.decisions.json). Immature and harvested/leafless stages also render PASS in artsrc, none wired to Textures/."),
    ("RM_PrennaLace", "prenna lace", 0.02,
     "A grey fungus that grows cloth-like lace from under its cap. Prenna is the Deeps' one source of fabric.",
     "RM_LanternDeeps/Things/Plant/PrennaLace/PrennaLaceGrown",
     ARTSRC / "greyladygrown_a_v1/greyladygrown_a_v1.png", "approved-not-wired",
     "Grown-stage variant A shown; owner recorded 'keep' on all 4 PrennaLace renders (deeps_art_review_2026-09-18.decisions.json, 2026-09-18) — approved, just never copied into Textures/."),
]

# ---------------------------------------------------------------------------
# FAUNA — RM_LanternDeeps.wildAnimals, MEASURED from the same biome def
# 2026-09-24 (re-measured; was 16 rows when this sheet last ran 2026-09-18).
# DEEPS_FAUNA_VERDICTS_1 (closed be9f3b513, 2026-09-19) cut 8 of the original
# 16 kinds from <wildAnimals> (AaroxisDendoria, AaroxisDendoriaLarvae,
# BloodropLarvae, BovineBeetleLarvae, FacetMoth, MossBeetle, PodWorm,
# RoyalRhino) and renamed 4 survivors (label+description only, defName
# unchanged, edited in RSW_BiomesTeamPort_Races.xml): RSW_BloodropMoth ->
# "drinker", RSW_BovineBeetle -> "grabber" (bodySize 2.45 -> 4), RSW_GlowSlug
# -> "glowbulb", RSW_FacetMothLarvae -> "soulchime". 8 restyle art jobs were
# FILED for the survivors but not yet wired — texPaths below still point at
# the original donor art (confirmed still on disk 2026-09-24), so this is
# accurate for "art the def renders with RIGHT NOW".
# All 8 are RSW_ ports living in one file:
# src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml
# No LanternDeeps-owned race ThingDef and no other patch names this biome
# anywhere else in src/ (re-grepped 2026-09-24) — this IS the complete cast.
# Each: (defName, label, commonality, bodySize, description, texPath, art PNG path)
# ---------------------------------------------------------------------------
SWB_ANIM = SWB_TEX / "swanimals/BiomesTeam/BMT_Caverns/Things/Animal"
FAUNA = [
    ("RSW_BloodropMoth", "drinker", 0.25, 0.77,
     "A pale, near-silent flier that drains blood into swollen storage sacs beneath its carapace using a razor-sharp proboscis. Strangely, a meal from a warm-blooded surface creature poisons it — it dies rapidly afterward.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/BloodropMoth/BloodropMoth",
     SWB_ANIM / "BloodropMoth/BloodropMoth_south.png"),
    ("RSW_GlowSlug", "glowbulb", 0.2, 0.4,
     "A pale-blue slug of the deep voids, lit from within by the slow burn of its own hydrocarbon sap - the yellow fluid under its skin is a light oil, not blood, and it will not freeze however far the cave runs down. Easily spotted in any dark environment by that steady glow, and by whatever else is hunting in the dark.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/GlowSlug/GlowSlug",
     SWB_ANIM / "GlowSlug/GlowSlug_south.png"),
    ("RSW_BovineBeetle", "grabber", 0.1, 4.0,
     "A small room-sized blob of pale yellow substance under a glass-like carapace, moving on many small legs. Its single great pincer-ending arm can hold a victim fast and slowly crush them.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/BovineBeetle/BovineBeetle",
     SWB_ANIM / "BovineBeetle/BovineBeetle_south.png"),
    ("RSW_Gembug", "gembug", 0.1, 0.335,
     "Commonly found in crystal caverns, the gembug is a smaller relative of the pillbug known for its gem-like exoskeleton.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Gembug/Blue/Jewelbug",
     SWB_ANIM / "Gembug/Blue/Jewelbug_south.png"),
    ("RSW_Megapleura", "megapleura", 0.1, 2.4,
     "A relative of the trilobite beetle, the megapleura has grown to massive proportions while living deep within the Rim's crust. While odd in appearance, it is largely harmless.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Megapleura/Megapleura",
     SWB_ANIM / "Megapleura/Megapleura_south.png"),
    ("RSW_ShatterjawBeetle", "shatterjaw beetle", 0.1, 1.0,
     "One of the most dangerous inhabitants of the crystal caves, the shatterjaw hunt with their large mandibles, crushing and cutting prey to pieces before feeding.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/ShatterjawBeetle/ShatterJaw",
     SWB_ANIM / "ShatterjawBeetle/ShatterJaw_south.png"),
    ("RSW_MossBeetleLarvae", "moss grub", 0.1, 0.7,
     "A large beetle commonly found in dark, damp places, it feeds off low underbrush in caverns. While not the best source of meat, it works when little else is available.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/MossBeetle/MossGrub",
     SWB_ANIM / "MossBeetle/MossGrub_south.png"),
    ("RSW_FacetMothLarvae", "soulchime", 0.05, 0.7,
     "A stubby larva-like creature that builds armor from crystal shards it gathers off the ground. It emits a powerful psychic stun on anyone who approaches too closely and alarms it, but a tamed one has a soothing effect on those nearby.",
     "swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FacetMoth/Crystalpillar",
     SWB_ANIM / "FacetMoth/Crystalpillar_south.png"),
]


def first_words(desc, n=20):
    words = desc.split()
    if len(words) <= n:
        return desc
    return " ".join(words[:n]) + "…"


def make_thumb(src: Path, dst: Path):
    from PIL import Image
    if not src.exists():
        return False
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    scale = min(1.0, THUMB_MAX / max(w, h))
    if scale < 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst)
    return True


def build_flora_items(thumbs_rel):
    items = []
    n_owned = n_appnw = n_missing = 0
    for row in FLORA:
        defName, label, commonality, desc, texpath, art_src, chip = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
        note_extra = row[7] if len(row) > 7 else ""
        thumb_file = f"{defName}.png"
        thumb_rel = f"{thumbs_rel}/{thumb_file}"
        if chip == "owned":
            n_owned += 1
        elif chip == "approved-not-wired":
            n_appnw += 1
        else:
            n_missing += 1
        chip_label = {"owned": "owned", "approved-not-wired": "approved — not yet wired", "missing": "MISSING"}[chip]
        effect = (f"[{chip_label}] weight {commonality} · {first_words(desc)}"
                  + (f" — {note_extra}" if note_extra else ""))
        items.append({
            "id": defName,
            "label": f"{label} [{defName}]",
            "group": "Deeps flora",
            "effect": effect,
            "thumb": thumb_rel,
            "prefill": "keep",
            "inferred": False,
            "contested": chip != "owned",
            "occurs": True,
            "_art_src": art_src,
            "_thumb_file": thumb_file,
        })
    return items, {"owned": n_owned, "approved_not_wired": n_appnw, "missing": n_missing}


def build_fauna_items(thumbs_rel):
    items = []
    n_donor = n_missing = 0
    for defName, label, commonality, bodysize, desc, texpath, art_src in FAUNA:
        thumb_file = f"{defName}.png"
        thumb_rel = f"{thumbs_rel}/{thumb_file}"
        exists = art_src.exists()
        if exists:
            n_donor += 1
            chip_label = "donor"
        else:
            n_missing += 1
            chip_label = "MISSING"
        effect = (f"[{chip_label}] weight {commonality} · bodySize {bodysize} · "
                  f"{first_words(desc)}")
        items.append({
            "id": defName,
            "label": f"{label} [{defName}]",
            "group": "Deeps fauna",
            "effect": effect,
            "thumb": thumb_rel if exists else None,
            "prefill": "keep",
            "inferred": False,
            "contested": not exists,
            "occurs": True,
            "_art_src": art_src if exists else None,
            "_thumb_file": thumb_file if exists else None,
        })
    return items, {"donor": n_donor, "missing": n_missing}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the sheet, thumbnails and decisions seed (default: dry run)")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print(f"ERROR: sheet template not found at {TEMPLATE}", file=sys.stderr)
        return 1

    thumbs_rel = OUT_THUMBS_DIR.name
    flora_items, flora_counts = build_flora_items(thumbs_rel)
    fauna_items, fauna_counts = build_fauna_items(thumbs_rel)
    items = flora_items + fauna_items

    print(f"# build_species_sheet.py plan — {len(flora_items)} flora rows, {len(fauna_items)} fauna rows")
    print(f"  flora: {flora_counts}")
    print(f"  fauna: {fauna_counts}")
    for it in items:
        art = it.get("_art_src")
        ok = "OK " if art and Path(art).exists() else "N/A"
        print(f"  [{ok}] {it['group']:14s} {it['id']}")

    if not args.apply:
        print(f"\nDry run only. Re-run with --apply to write:\n  {OUT_HTML}\n  {OUT_THUMBS_DIR}/*.png\n  {OUT_DECISIONS}")
        return 0

    # Refuse to clobber a real decisions file (skill §7/§8: only the sheet's
    # own plumbing may stamp savedBy/writeCount>0 on a save).
    if OUT_DECISIONS.exists():
        try:
            existing = json.loads(OUT_DECISIONS.read_text())
        except (OSError, json.JSONDecodeError):
            existing = {}
        if existing.get("savedBy") or (existing.get("writeCount") or 0) > 0:
            print(f"REFUSED: {OUT_DECISIONS} already carries savedBy/writeCount — "
                  "that is a human's review, not a pre-fill. Not overwriting.", file=sys.stderr)
            return 1

    OUT_THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    made = 0
    for it in items:
        art = it.pop("_art_src", None)
        tf = it.pop("_thumb_file", None)
        if art and tf:
            if make_thumb(Path(art), OUT_THUMBS_DIR / tf):
                made += 1
            else:
                print(f"WARNING: no source art for {it['id']} at {art}", file=sys.stderr)

    n_flora_notowned = flora_counts["approved_not_wired"] + flora_counts["missing"]
    n_fauna_notowned = fauna_counts["donor"] + fauna_counts["missing"]

    cfg = {
        "sheetId": "deeps_flora_fauna_review_2026-09-18",
        "title": "Lantern Deeps — flora & fauna species review",
        "subtitle": f"{len(flora_items)} plants + {len(fauna_items)} animals · CAVERNS_PARITY_BUILD_1",
        "briefHtml": (
            "<p>One row per species that actually spawns in the Lantern Deeps pocket biome "
            "(<code>RM_LanternDeeps</code>'s own <code>&lt;wildPlants&gt;</code>/"
            "<code>&lt;wildAnimals&gt;</code> commonality tables — "
            "<code>DeepFloraPlanter.cs</code> reads that same list directly at spawn time, "
            "there is no separate species table to reconcile). Shows the art the def renders "
            "with RIGHT NOW, not the intended art.</p>"
            f"<p><b>Default is KEEP.</b> This sheet is a BLACKLIST: every row ships as-is "
            "unless you mark it otherwise. <b>Cut</b> removes the species from the biome's "
            "spawn table (a real edit to RM_LanternDeeps.xml); <b>Regen</b> leaves the "
            "species in but files a new artpipe job for its art; on a row already chipped "
            "'approved — not yet wired', picking (or leaving) Keep is what gets it copied "
            "into <code>Textures/</code> by a wire_art.py-style pass — nothing here does "
            "that copy itself.</p>"
            f"<p><b>{n_flora_notowned}</b> flora rows are not yet wired with owned art "
            f"({flora_counts['approved_not_wired']} approved renders sitting in "
            f"<code>infrastructure/artpipe/_artsrc/</code>, {flora_counts['missing']} truly "
            f"missing). <b>{fauna_counts['donor']}</b> of {len(fauna_items)} fauna rows render "
            "on SWBestiary donor art (no Lantern-Deeps-owned creature art exists for any of "
            f"them); {fauna_counts['missing']} fauna row(s) have no art found at all.</p>"
        ),
        "criterion": "Sorted by spawn commonality within each group, from the biome def's own "
                     "<wildPlants>/<wildAnimals> weights — this ranks how often the player "
                     "actually MEETS the species, not its design worth or its art quality.",
        "invented": [
            "Two groups only: 'Deeps flora' (12 rows = every entry in RM_LanternDeeps.wildPlants, "
            "which is also every non-abstract plant ThingDef under LanternDeeps/Defs/) and "
            "'Deeps fauna' (8 rows = every entry in RM_LanternDeeps.wildAnimals; no "
            "LanternDeeps-owned race ThingDef exists, and no patch elsewhere in src/ names "
            "this biome, so the wildAnimals list IS the complete cast).",
            "The four lanternstone rock formations (Small/Medium/Large/Huge) are EXCLUDED from "
            "flora — they are Buildings scattered by GenStep_ScatterLanternstone, not Plant "
            "ThingDefs, and are not in wildPlants. Only the sowable lanternstone (a genuine "
            "Plant, in wildPlants at weight 0.1) is included.",
            "Flora thumbnail is the GROWN-stage graphic (the def's main texPath, first "
            "Graphic_Random variant alphabetically); a species with separate immature/leafless "
            "art (TwitchingPuffer, PrennaLace, the sowable lanternstone) shows only the grown "
            "stage here, with the other stages named in the row's note.",
            "Fauna thumbnail is the south-facing sprite of the PawnKindDef's LAST life stage "
            "(the adult form) — larvae/pupae that also appear in wildAnimals (e.g. "
            "RSW_BovineBeetleLarvae) get their OWN row using THEIR OWN life-stage art, not a "
            "crop of the adult's.",
            "Chip 'approved — not yet wired' covers two different states, both noted per-row: "
            "PrennaLace's renders carry a recorded owner 'keep' decision in "
            "deeps_art_review_2026-09-18.decisions.json; TwitchingPuffer's renders only passed "
            "the automated facts gate and have never been shown to the owner before now.",
        ],
        "posture": {"mode": "blacklist", "explain": "Default is KEEP — every row ships as-is "
                    "unless you mark it Cut (removed from the biome's spawn table) or Regen "
                    "(art redone, species stays). Undecided rows behave as KEEP, same as an "
                    "explicit Keep — this is a blacklist, not a whitelist."},
        "options": [
            {"key": "keep", "label": "Keep", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regen art", "hotkey": "2", "color": "#e0a83c", "counts": "in"},
            {"key": "cut", "label": "Cut species", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
            {"key": "undecided", "label": "Undecided", "hotkey": "4", "color": "#888", "counts": "in"},
        ],
        "groupLabel": "group",
        "media": True,
        "decisionsFile": OUT_DECISIONS.name,
        "decisionsPath": str(OUT_DECISIONS),
        "sheetPath": str(OUT_HTML),
    }

    html = TEMPLATE.read_text()
    html = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(cfg, indent=2) + m.group(2),
        html, count=1, flags=re.S,
    )
    html = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, indent=2) + m.group(2),
        html, count=1, flags=re.S,
    )
    OUT_HTML.write_text(html)

    OUT_DECISIONS.write_text(json.dumps({
        "sheetId": cfg["sheetId"], "posture": "blacklist", "frozen": False,
        "writeCount": 0, "decisions": {},
    }, indent=2) + "\n")

    print(f"\nWrote {OUT_HTML}")
    print(f"Wrote {made} thumbnail(s) to {OUT_THUMBS_DIR}")
    print(f"Decisions file: {OUT_DECISIONS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
