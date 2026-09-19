#!/usr/bin/env python3
"""build_review_sheet.py — the Rot flora/fauna + new-art review sheet, 2026-09-18.

Builds ONE owner-facing review sheet over three groups:
  A) Rot flora  — every <li> in RUT_TheRot.xml's <wildPlants>, PLUS the patch-added
     entries (RotPaleTree_WildSpawn.xml, RotGuardianGroves_WildSpawn.xml), PLUS every
     non-abstract plant ThingDef under RotSporeKit/Defs/ThingDefs_Plants and
     PlantBases that isn't already wild-listed (fungiponics-only crops).
  B) Rot fauna  — RUT_TheRot.xml's <wildAnimals> (MEASURED 9, not the 15 the build
     brief named — see the report) plus RUT_Emberscythe, with the kin-mechanics
     assignment drafted in Transient/rot_fauna_assignment_draft_20260918.md.
  C) New art landed (other waves) — artpipe jobs completed after 2026-09-18 00:00
     PDT that are NOT already covered by another dedicated review sheet built today
     (see the report for what was excluded and why: canon_* has its own sheet at
     Transient/canon_regen_wave1_2026-09-18/, and the Lantern Deeps texture slots
     have their own sheet at Transient/deeps_art_review_2026-09-18.html).

Usage:
    python3 build_review_sheet.py             # dry run: prints the plan, writes nothing
    python3 build_review_sheet.py --apply      # writes the sheet + thumbnails + decisions seed

Then review it:
  python3 <review-sheets skill>/assets/check_sheet.py <out.html> --decisions <out.decisions.json>
  python3 <review-sheets skill>/assets/serve_sheet.py --sheet <out.html> --decisions <out.decisions.json>
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html")

OUT_HTML = REPO_ROOT / "Transient" / "rot_flora_fauna_review_2026-09-18.html"
OUT_THUMBS_DIR = REPO_ROOT / "Transient" / "rot_review_thumbs_2026-09-18"
OUT_DECISIONS = REPO_ROOT / "Transient" / "rot_flora_fauna_review_2026-09-18.decisions.json"
SHEET_ID = "rot_flora_fauna_review_2026-09-18"

ARTSRC = REPO_ROOT / "infrastructure" / "artpipe" / "_artsrc"
THUMB_MAX = 160

# Donor mod roots (coordinator-supplied, 2026-09-18 correction — About.xml lists
# dependencies before the packageId, which is why the first packageId grep missed
# them). Absolute paths outside the repo; resolved directly, never copied into src/.
WORKSHOP = Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")
AB_ROOT = WORKSHOP / "1841354677"   # Alpha Biomes (sarg.alphabiomes)
AA_ROOT = WORKSHOP / "1541721856"   # Alpha Animals (sarg.alphaanimals)
GAME_MODS = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods")
RAW_VANILLA = REPO_ROOT / "Transient" / "rot_review_thumbs_2026-09-18" / "_raw_vanilla"

# ── to-scale panels (owner ask, 2026-09-18 late pass) ────────────────────────
# Same method as src/RimMandrake/Utils/gen_plant_register.py (_scale_panel,
# _human_figure, mesh tiling) and gen_creature_register.py (_scale_panel for
# pawns) — copied rather than imported: those modules pull in cherrypicker,
# game_paths, rimworld_loadset (live def-dump / Windows-path machinery) that
# this generator's own hand-curated ROWS data doesn't need or want as a
# dependency. PX_PER_CELL/HUMAN_CELLS match exactly; PANEL_MAX_PX (240) is
# THIS sheet's own cap — the reference scripts build big inspection images
# (SCALE_CAP 1200-1500px) for a dedicated art-review page, but this is a row
# thumbnail on a mixed sheet, so the owner asked for 240px max here.
PX_PER_CELL = 64
HUMAN_CELLS = 1.5
PANEL_MAX_PX = 240
MESH_CAP = 9
HUMAN_ANCHOR = REPO_ROOT / "design" / "Jawa" / "worldbuilding" / "review" / "assets" / "human_anchor_south.png"

# MEASURED 2026-09-18: graphicData.drawSize is 1.0 (vanilla default) for EVERY
# one of the 40 Group A flora defs — resolved the full ParentName chain for
# each (through RotSporeKit's own abstracts and AlphaBiomes' AB_CavePlantBase)
# and grepped every file in scope for the literal string "drawSize": it
# appears exactly once in the whole flora set, on RUT_MedicineFungal (an
# ingredient item, not a plant). None of these defs override it. The apparent
# ankle-high-to-building-sized spread the descriptions promise comes entirely
# from <plant><visualSizeRange>, which scales the SAME 1x1 quad up at growth —
# printed on the row and used for the scale panel's box; see mature_cells()
# below and CONFIG.invented on the sheet.
FLORA_DRAWSIZE = (1.0, 1.0)  # (x, y) — constant, see note above
#
# visualSizeRange is RESOLVED FROM THE DEFS AT BUILD TIME, never transcribed.
# It was hand-transcribed twice (2026-09-18, and a "correction" the same night)
# and was wrong both times: the second pass asserted that 13 rows set no
# visualSizeRange of their own and inherited the vanilla PlantBase 0.3~1.00.
# MEASURED 2026-09-19 against AlphaBiomes' own Plants_MycoticJungle.xml: all 13
# DO set one, and 11 were being drawn 1.0 cell wide when the def says up to 6
# (AB_GiantAgarilux 3.5~6, AB_DribblingCap and AB_SlimyPholiota and
# AB_RecurvedStropharia 3.5~5, AB_ArbuscularMycorrhiza 2~3.5, ...). The owner
# ruled 11 rows' widths against those too-small panels as a result.
# A table also goes stale against our OWN defs the moment a size ruling is
# applied to them, which had already happened by 2026-09-19. So: parse.
PLANT_DEF_DIRS = [
    REPO_ROOT / "src" / "RimUtinni",
    REPO_ROOT / "src" / "RimStarWars",
    REPO_ROOT / "src" / "RimMandrake",
    Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs"),
    AB_ROOT / "1.6",
    AA_ROOT / "1.6",
]


def _plant_def_index():
    """defName (and abstract Name) -> (own visualSizeRange text or None, ParentName).

    Indexes every ThingDef reachable in PLANT_DEF_DIRS so a def's size can be
    resolved through its own node first, then its ParentName chain (custom
    abstracts included), then the vanilla Plant bases. MEASURED 2026-09-19:
    none of the 40 Group A defNames is defined twice across these roots, so
    there is no precedence question to get wrong. A donor mod that ships both
    1.5/ and 1.6/ is read from 1.6 — the version the game loads."""
    index = {}
    for root in PLANT_DEF_DIRS:
        if not root.exists():
            continue
        for f in root.rglob("*.xml"):
            try:
                tree = ET.parse(f)
            except ET.ParseError:
                continue
            for node in tree.getroot().iter("ThingDef"):
                vsr = node.findtext("./plant/visualSizeRange")
                vsr = vsr.strip() if vsr else None
                parent = node.get("ParentName")
                for key in (node.findtext("defName"), node.get("Name")):
                    if key and key not in index:
                        index[key] = (vsr, parent)
    return index


def resolve_visual_size_range(defname, index):
    """(min, max), authored_on_this_def — walking the ParentName chain.

    Raises if nothing in the chain sets a visualSizeRange, rather than falling
    back to a 1x1 quad: a silent fallback is what drew 11 giant mushrooms
    ankle-high and cost the owner a whole mis-ruled sitting."""
    seen, cur, hops = set(), defname, 0
    while cur and cur not in seen:
        seen.add(cur)
        entry = index.get(cur)
        if entry is None:
            break
        vsr, parent = entry
        if vsr:
            lo, hi = (float(x) for x in vsr.split("~"))
            return (lo, hi), hops == 0
        cur, hops = parent, hops + 1
    raise KeyError(
        f"{defname}: no visualSizeRange anywhere in its ParentName chain. "
        f"Fix the def or the def roots — do NOT substitute a default.")


_VSR_INDEX = _plant_def_index()
# defName -> maxMeshCount (absent/None means 1 — a single sprite per cell).
FLORA_MESH = {
    "AB_Bryolux": 4, "RUT_Dewshrooms": 9, "RUT_FruitingBodies": 25,
    "RUT_Wrinklecap": 4, "RUT_Pusmelon": 4, "RUT_RustPuff": 4,
    "RUT_Sagecrust": 9, "RUT_CrimsonCap": 4, "RUT_VioletWimple": 4,
    "RUT_MortalMorelPlant": 4, "RUT_BlastpodShroom": 1, "RUT_FurnaceCap": 4,
    "RUT_PaleMoss": 9,
}
# Adult (last) life-stage bodyGraphicData.drawSize per fauna defName — MEASURED
# from each race's PawnKindDef life stages (RSW_/AA_ from their own source;
# RUT_Emberscythe from its own def in this repo).
FAUNA_DRAWSIZE = {
    "RSW_FungalWeevil": 1.8, "AA_Swarmling": 1.75, "AA_Agaripod": 3.8,
    "AA_MycoidColossus": 6.0, "RSW_BovineBeetle": 3.0, "AA_Agaripawn": 2.0,
    "AA_Wildpawn": 2.0, "AA_Wildpod": 3.8, "RSW_FungalMantis": 3.0,
    "RUT_Emberscythe": 2.2,
}

# ============================================================================
# GROUP A — Rot flora
# Fields: (defName, label, source, commonality_or_None, desc20, texPath, art_status,
#          thumb_src_relpath_or_None, note)
# art_status in {owned, shared-placeholder, donor, vanilla}
# commonality is None for the 3 non-wild RotSporeKit-only plants (fungiponics crop /
# pale-tree companion / a furnace cap with no wildPlants entry of its own).
# ============================================================================

RUT_TEX = "src/RimUtinni/RotSporeKit/Textures/RotSporeKit/Things/Plant"

FLORA = [
    # --- AlphaBiomes donor wild plants (sarg.alphabiomes) — from RUT_TheRot.xml <wildPlants> ---
    ("AB_Bryolux", "bryolux", "AlphaBiomes (sarg.alphabiomes)", 10, "A blue moss typically found in deep, dark caves. It is sticky, with tangled fibers, which slows anyone walking over", "Things/Plant/Bryolux", "vanilla", str(RAW_VANILLA / "AB_Bryolux_vanilla.png"), "texPath has no art file in the AlphaBiomes Workshop mod itself (confirmed by search) because it doesn't need one — vanilla Core ships this exact texPath (Graphic_Random BryoluxA/B/C in the base resources.assets); extracted BryoluxA, first alphabetically."),
    ("AB_Glowstool", "glowstool", "AlphaBiomes (sarg.alphabiomes)", 3, "A small brown mushroom typically found in caves. It smells like an old, dirty rag pulled from the stomach of", "Things/Plant/Glowstool", "vanilla", str(RAW_VANILLA / "AB_Glowstool_vanilla.png"), "texPath has no art file in the AlphaBiomes Workshop mod itself because it doesn't need one — vanilla Core ships this texPath (GlowstoolA/B in resources.assets); extracted GlowstoolA."),
    ("AB_Agarilux", "agarilux", "AlphaBiomes (sarg.alphabiomes)", 2, "An enormous purple mushroom. Its size and glowing protrusions make this fungus beautiful to look at. This agarilux variant has", "Things/Plant/Agarilux", "vanilla", str(RAW_VANILLA / "AB_Agarilux_vanilla.png"), "texPath has no art file in the AlphaBiomes Workshop mod itself (only Giant/Prime variants ship their own) because it doesn't need one — vanilla Core ships this texPath (AgariluxA/B in resources.assets); extracted AgariluxA."),
    ("AB_GiantAgarilux", "giant agarilux", "AlphaBiomes (sarg.alphabiomes)", 2, "A colossal purple mushroom. Its size and glowing protrusions make this fungus beautiful to look at. Its stalk has been", "Things/Plants/AB_GiantAgarilux", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_GiantAgarilux/AB_GiantAgariluxA.png"), ""),
    ("AB_GlowingAgarilux", "glowing agarilux", "AlphaBiomes (sarg.alphabiomes)", 1, "An enormous purple mushroom, glowing in darkness with a faint purple luminiscence. Its size and glowing protrusions make this fungus", "Things/Plant/Agarilux", "vanilla", str(RAW_VANILLA / "AB_Agarilux_vanilla.png"), "shares the same bare 'Agarilux' texPath as AB_Agarilux — vanilla Core art (AgariluxA), same file as that row."),
    ("AB_LilacBeacon", "lilac beacon", "AlphaBiomes (sarg.alphabiomes)", 0.5, "The lilac beacon is a tall mushroom with a bright purple cap. It is much more nutritive than other fungi,", "Things/Plants/AB_LilacBeacon", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_LilacBeacon/AB_LilacBeaconA.png"), ""),
    ("AB_WitchesOyster", "witches' oyster", "AlphaBiomes (sarg.alphabiomes)", 0.5, "A small, ramified fungal colony with a pungent aroma. A witches' oyster produces caps that take quite a long time", "Things/Plants/AB_WitchesOyster", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_WitchesOyster.png"), ""),
    ("AB_RecurvedStropharia", "recurved stropharia", "AlphaBiomes (sarg.alphabiomes)", 0.3, "A big greyish mushroom. Its size and glowing protrusions make this fungus beautiful to look at. Its stalk has been", "Things/Plants/AB_RecurvedStropharia", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_RecurvedStropharia.png"), ""),
    ("AB_ArbuscularMycorrhiza", "arbuscular mycorrhiza", "AlphaBiomes (sarg.alphabiomes)", 0.2, "A mycorrhiza is a symbiotic association between a fungus and a plant. This particular organism is highly advanced, and the", "Things/Plants/AB_ArbuscularMycorrhiza", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_ArbuscularMycorrhiza/AB_ArbuscularMycorrhizaA.png"), ""),
    ("AB_SlimyPholiota", "slimy pholiota", "AlphaBiomes (sarg.alphabiomes)", 0.2, "A blueish-pink mushroom, secreting a slimy substance that attracts insects. This substance paralyzes the insects, and eventually kills them, being", "Things/Plants/AB_SlimyPholiota", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_SlimyPholiota/AB_SlimyPholiotaA.png"), "folder also holds a duplicate 'AB_SlimyPholiotaA copy.png' — skipped, used the real AB_SlimyPholiotaA.png"),
    ("AB_AgaricusDomeCap", "agaricus domecap", "AlphaBiomes (sarg.alphabiomes)", 0.1, 'Everything about this fungus screams "I\'m toxic, stay away from me". Of course this doesn\'t stop some enterprising individuals from', "Things/Plants/AB_AgaricusDomeCap", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_AgaricusDomeCap.png"), ""),
    ("AB_DribblingCap", "dribbling cap", "AlphaBiomes (sarg.alphabiomes)", 0.1, "A huge pink mushroom, constantly dribbling a pungent, resin-like substance. This substance is a potent neurotoxin that could potentially be", "Things/Plants/AB_DribblingCap", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_DribblingCap/AB_DribblingCapA.png"), ""),
    ("AB_AgariluxPrime", "Agarilux Prime", "AlphaBiomes (sarg.alphabiomes)", 0.01, "An unbelievably large exemplar of Agarilux. This myconic colony has adapted perfectly to its environment, releasing large clouds of extremely", "Things/Plants/AB_AgariluxPrime", "donor", str(AB_ROOT / "Textures/Things/Plants/AB_AgariluxPrime.png"), ""),

    # --- RotSporeKit-owned wild plants (ported field-for-field from BiomesCaverns_src) ---
    ("RUT_Dewshrooms", "dewshrooms", "RotSporeKit (mandrake.rut.rotsporekit)", 0.5, "Dewshrooms light up to attract small prey, which becomes trapped in their sticky gills.", "RotSporeKit/Things/Plant/Seadew", "owned", f"{RUT_TEX}/Seadew/BMT_SeadewA.png", ""),
    ("RUT_FruitingBodies", "mold fruiting bodies", "RotSporeKit (mandrake.rut.rotsporekit)", 0.5, "The fruiting bodies of a mold that grows in caverns.", "RotSporeKit/Things/Plant/FruitingBodies", "owned", f"{RUT_TEX}/FruitingBodies/FruitingBodyA.png", "texPath also reused as a placeholder by RUT_FalseFruit (Guardian Groves, art queued)"),
    ("RUT_Nuitae", "nuitae", "RotSporeKit (mandrake.rut.rotsporekit)", 0.5, "While its cap's exterior is largely dark in color, its underside glows brightly. It grows most often in water or", "RotSporeKit/Things/Plant/Nuitae", "owned", f"{RUT_TEX}/Nuitae/Nuitae_A.png", ""),
    ("RUT_Wrinklecap", "wrinklecap", "RotSporeKit (mandrake.rut.rotsporekit)", 0.5, "A subterranean fungus that grows in damp environments. It is often eaten by fungivores.", "RotSporeKit/Things/Plant/Wrinklecap", "owned", f"{RUT_TEX}/Wrinklecap/Wrinkle1.png", ""),
    ("RUT_Arpeau", "arpeau", "RotSporeKit (mandrake.rut.rotsporekit)", 0.4, "Fast-growing, but doesn't yield much usable material. Aquatic fungus.", "RotSporeKit/Things/Plant/Arpeau", "owned", f"{RUT_TEX}/Arpeau/Arpeau_A.png", ""),
    ("RUT_Nogtyl", "nogtyl", "RotSporeKit (mandrake.rut.rotsporekit)", 0.4, "A strong wood-like mushroom. Fast-growing, but doesn't yield much usable material. It can only be grown by people on marshy", "RotSporeKit/Things/Plant/Nogtyl", "owned", f"{RUT_TEX}/Nogtyl/Nogtyl_A.png", ""),
    ("RUT_FlakespireFungus", "flakespire fungus", "RotSporeKit (mandrake.rut.rotsporekit)", 0.3, "A strong purple mushroom tree. Slow-growing, but this woody fungus is very strong and attractive.", "RotSporeKit/Things/Plant/FlakespireFungus", "owned", f"{RUT_TEX}/FlakespireFungus/Flakespirefungus_a.png", ""),
    ("RUT_Pusmelon", "pusmelon", "RotSporeKit (mandrake.rut.rotsporekit)", 0.3, "A green, gourd-like fungus that produces sacs of foul-smelling liquid.", "RotSporeKit/Things/Plant/Pusmelon", "owned", f"{RUT_TEX}/Pusmelon/BMT_PusmelonA.png", ""),
    ("RUT_RustPuff", "rustpuff", "RotSporeKit (mandrake.rut.rotsporekit)", 0.3, "A large puffball mushroom with flaky, rust-colored spores.", "RotSporeKit/Things/Plant/RustPuff", "owned", f"{RUT_TEX}/RustPuff/BMT_RustPuffA.png", ""),
    ("RUT_Sagecrust", "sagecrust", "RotSporeKit (mandrake.rut.rotsporekit)", 0.3, "A tough, leafy lichen that can survive with minimal light.", "RotSporeKit/Things/Plant/Sagecrust", "owned", f"{RUT_TEX}/Sagecrust/BMT_SagecrustA.png", ""),
    ("RUT_BleedingTooth", "bleeding tooth", "RotSporeKit (mandrake.rut.rotsporekit)", 0.2, "A huge mushroom that secretes a red, blood-like fluid.", "RotSporeKit/Things/Plant/BleedingTooth", "owned", f"{RUT_TEX}/BleedingTooth/BMT_BleedingToothA.png", ""),
    ("RUT_Brightbell", "shinebell", "RotSporeKit (mandrake.rut.rotsporekit)", 0.2, "A small pretty mushroom that glows in the dark.", "RotSporeKit/Things/Plant/Brightbell", "owned", f"{RUT_TEX}/Brightbell/Brightbell_A.png", 'the_rot.md names it "shinebell" (label), defName Brightbell — a fixed donor typo (BMT_Brightbells never existed), not a guess'),
    ("RUT_CrimsonCap", "crimson cap", "RotSporeKit (mandrake.rut.rotsporekit)", 0.2, "A large crimson-capped mushroom. It is pretty enough to be used for decor but not much else.", "RotSporeKit/Things/Plant/CrimsonCap", "owned", f"{RUT_TEX}/CrimsonCap/CrimsonCap_a.png", "texPath also reused as a placeholder by RUT_FurnaceCap and RUT_AgelessCap (both art queued)"),
    ("RUT_GreyLady", "Grey Lady", "RotSporeKit (mandrake.rut.rotsporekit)", 0.2, "A grey fungus that grows cloth-like lace from its cap.", "RotSporeKit/Things/Plant/GreyLady/GreyLadyGrown", "owned", f"{RUT_TEX}/GreyLady/GreyLadyGrown/GreyLadyGrownA.png", "texPath also reused as a placeholder by RUT_RegenerantVeil (Guardian Groves, art queued)"),
    ("RUT_Shinecap", "shine cap", "RotSporeKit (mandrake.rut.rotsporekit)", 0.2, "This large mushroom lives in symbiosis with a surprisingly tasty slime mold called Glimmerslime.", "RotSporeKit/Things/Plant/Shinecap/ShinecapGrown", "owned", f"{RUT_TEX}/Shinecap/ShinecapGrown/ShinecapGrown_a.png", ""),
    ("RUT_VioletWimple", "violet wimple", "RotSporeKit (mandrake.rut.rotsporekit)", 0.2, "A big violet-capped mushroom. While not very productive, it does produce edible fungus.", "RotSporeKit/Things/Plant/VioletWimple", "owned", f"{RUT_TEX}/VioletWimple/BMT_VioletWimpleA.png", "texPath also reused as a placeholder by RUT_EuphoricCrown (Guardian Groves, art queued)"),
    ("RUT_MortalMorelPlant", "mortal morel", "RotSporeKit (mandrake.rut.rotsporekit)", 0.15, "A slow-growing mushroom which yields fungal medicine when harvested. Sowing and harvesting this fungus are both very labor-intensive because of", "RotSporeKit/Things/Plant/MortalMorel", "owned", f"{RUT_TEX}/MortalMorel/CavernalMorel_A.png", "texPath folder says MortalMorel, on-disk files are CavernalMorel_* — pre-existing naming oddity, not fixed here"),
    ("RUT_Skulltop", "skulltop", "RotSporeKit (mandrake.rut.rotsporekit)", 0.1, "An extremely deadly mushroom that steadily releases polluting toxic spores into the air. These spores rapidly produce toxic buildup in", "RotSporeKit/Things/Plant/Skulltop/Skulltop", "owned", f"{RUT_TEX}/Skulltop/Skulltop/Skulltop_A.png", "the biome's lesser defender (AlphaBiomes gas-producer comp)"),
    ("RUT_BlastpodShroom", "blastpod shroom", "RotSporeKit (mandrake.rut.rotsporekit)", 0.05, "A wild fungus prized for its dangerously volatile pods, which can be refined into chemfuel. It cannot be cultivated —", "RotSporeKit/Things/Plant/Boomshroom/BoomshroomGrown", "owned", f"{RUT_TEX}/Boomshroom/BoomshroomGrown/BoomshroomGrown_A.png", "wild-only per owner ruling 2026-09-06, no sow tags"),

    # --- patch-added wild plants (separate files, never edit RUT_TheRot.xml directly) ---
    ("RUT_PaleTree", "pale tree", "RotSporeKit (mandrake.rut.rotsporekit)", 0.01, "A bone-white tree that hums faintly at dusk, sacred to the wandering Wildsteam creed. Meditating in its shade for long", "Things/Plant/TreeAnima", "vanilla", str(RAW_VANILLA / "RUT_PaleTree_vanilla.png"), "added by RotPaleTree_WildSpawn.xml (PatchOperationAdd), Royalty-gated; reuses vanilla TreeAnima verbatim (extracted TreeAnimaA from Data/Royalty/AssetBundles/resources_royalty, first alphabetically of A-E) — one of the 22 new-art jobs FAILED tonight on quota"),
    ("RUT_AgelessCap", "ageless cap", "RotSporeKit (mandrake.rut.rotsporekit)", 0.03, "A pale, swollen mushroom rumored to hold back the years of anyone who tastes it right. It does not defend", "RotSporeKit/Things/Plant/CrimsonCap", "shared-placeholder", None, "added by RotGuardianGroves_WildSpawn.xml; texPath shared with RUT_CrimsonCap and RUT_FurnaceCap — one of the 22 new-art jobs FAILED tonight on quota"),
    ("RUT_RegenerantVeil", "regenerant veil", "RotSporeKit (mandrake.rut.rotsporekit)", 0.03, "A translucent, slow-pulsing veil of fungal tissue, threaded straight into the grove's own mycelial network. Wound it and the", "RotSporeKit/Things/Plant/GreyLady/GreyLadyGrown", "shared-placeholder", None, "added by RotGuardianGroves_WildSpawn.xml; the alarm plant for ROT_GUARDIAN_GROVES_1 (currently 0 fauna responders — see Group B); texPath shared with RUT_GreyLady — one of the 22 new-art jobs FAILED tonight on quota"),
    ("RUT_EuphoricCrown", "euphoric crown", "RotSporeKit (mandrake.rut.rotsporekit)", 0.02, "A broad, faintly luminous cap that brews into the Rot's own pleasure tea. It keeps no defense of its own", "RotSporeKit/Things/Plant/VioletWimple", "shared-placeholder", None, "added by RotGuardianGroves_WildSpawn.xml; texPath shared with RUT_VioletWimple — one of the 22 new-art jobs FAILED tonight on quota"),
    ("RUT_FalseFruit", "false fruit", "RotSporeKit (mandrake.rut.rotsporekit)", 0.05, "Grown at the edge of a euphoric crown's own root mat, and shaped to match it. It looks exactly like", "RotSporeKit/Things/Plant/FruitingBodies", "shared-placeholder", None, "added by RotGuardianGroves_WildSpawn.xml, the lure ring; texPath shared with RUT_FruitingBodies — one of the 22 new-art jobs FAILED tonight on quota"),

    # --- non-wild RotSporeKit plant ThingDefs (not in wildPlants at all) ---
    ("RUT_DulcisPlant", "dulcis", "RotSporeKit (mandrake.rut.rotsporekit)", None, "An oddly sweet mushroom grown by cave dwellers in place of berries. It can survive in a wide range of", "RotSporeKit/Things/Plant/Dulcis/DulcisGrown", "owned", f"{RUT_TEX}/Dulcis/DulcisGrown/DulcisGrown_a.png", "fungiponics' default grow target, NOT in wildPlants (sow-only, mustBeWildToSow paradoxically true — grows wild-style once sown); a same-day regen pass (dulcisgrown_a_v1 etc, PASS, not yet wired) reshot this already-owned art — see the report"),
    ("RUT_FurnaceCap", "furnace cap", "RotSporeKit (mandrake.rut.rotsporekit)", None, "A squat, thick-walled mushroom that runs its metabolism hot enough to steam in cold air. Cut one open and the", "RotSporeKit/Things/Plant/CrimsonCap", "shared-placeholder", None, "ROT_WARM_MAT_1; NOT in wildPlants (not yet wild-spawned, ThingDef only); texPath shared with RUT_CrimsonCap/RUT_AgelessCap — one of the 22 new-art jobs FAILED tonight on quota"),
    ("RUT_PaleMoss", "pale moss", "RotSporeKit (mandrake.rut.rotsporekit)", None, "A faintly glowing moss that only takes root beneath a pale tree, fed by whatever the tree is doing underground.", "Things/Plant/Grass_Anima", "vanilla", str(RAW_VANILLA / "RUT_PaleMoss_vanilla.png"), "NOT in wildPlants (companion-spawn only, grows beneath RUT_PaleTree); Royalty-gated; reuses vanilla Grass_Anima verbatim (extracted Grass_AnimaA from the base resources.assets, first alphabetically of A-C) — one of the 22 new-art jobs FAILED tonight on quota"),
]

# ============================================================================
# GROUP B — Rot fauna
# MEASURED: RUT_TheRot.xml <wildAnimals> has 9 entries, not the 15 the build brief
# named. No patch was found adding more (checked every Patches/*.xml referencing
# these defNames) — the fauna_assignment draft's 15-row table appears to describe a
# PROPOSED roster (6 BMT_ cavern kinds not yet wired into the biome), not the live
# one. Reported here as measured, not as briefed — see the build report.
# Fields: (defName, label, commonality, xmlClass, bodySize_or_None, source, thumb,
#          kinTag, woundLink, mend, alarm, trade)
# ============================================================================
FAUNA = [
    ("RSW_FungalWeevil", "fungal weevil", 0.4, "ingest-strange, import", 0.5,
     "SWBestiary (mandrake.rsw.swbestiary)",
     "src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FungalWeevil/FungalWeevil_south.png",
     "RotBroodmates", "no", "mend ∝ bodySize", "no", "broods recover if you leave survivors; finish a brood or expect it back"),
    ("AA_Swarmling", "swarmling", 0.3, "hybrid-vermin, adjust-keep", 0.3,
     "Alpha Animals (sarg.alphaanimals)",
     str(AA_ROOT / "Textures/Things/Pawn/Animal/AA_Swarmling/AA_Swarmling_south.png"),
     "RotSwarm", "YES", "no", "YES", "one body: wound one, wound the swarm — both ways (a grenade into a swarm mirrors 60% of every hit across the pack)"),
    ("AA_Agaripod", "agaripod", 0.25, "hybrid-native, keep", 4.0,
     "Alpha Animals (sarg.alphaanimals); AgaripodArtOverride (game Mods folder) overrides the base art",
     str(GAME_MODS / "AgaripodArtOverride/Textures/Things/Pawn/Animal/AA_Agaripod/AA_Agaripod_south.png"),
     "RotAgarikin", "YES", "mend ∝ bodySize", "no", "the flagship organ: hunting one agari wounds every agari within 12 cells, but a huddled herd knits together"),
    ("AA_MycoidColossus", "mycoid colossus", 0.25, "hybrid-giant, keep", 6.0,
     "Alpha Animals (sarg.alphaanimals); MycoidColossusArtOverride (game Mods folder) overrides the base art",
     str(GAME_MODS / "MycoidColossusArtOverride/Textures/Things/Pawn/Animal/AA_MycoidColossus/AA_MycoidColossus_south.png"),
     "none (solitary)", "no", "no", "YES", "the forest walks over, when it's near — rare (0.25), the jackpot alarm response"),
    ("RSW_BovineBeetle", "bovine beetle", 0.2, "ingest-producer, import", 2.45,
     "SWBestiary (mandrake.rsw.swbestiary)",
     "src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/BovineBeetle/BovineBeetle_south.png",
     "RotHerd", "YES", "mend ∝ bodySize", "no", "a tamed train spreads a raid volley across the herd, but one wild predator strike bloodies the whole line"),
    ("AA_Agaripawn", "agaripawn", 0.2, "hybrid-native, keep", 1.4,
     "Alpha Animals (sarg.alphaanimals)",
     str(AA_ROOT / "Textures/Things/Pawn/Animal/AA_Agaripawn/AA_Agaripawn_south.png"),
     "RotAgarikin", "YES", "mend ∝ bodySize", "no", "same organ as the agaripod — the flagship's other half"),
    ("AA_Wildpawn", "wildpawn", 0.2, "hybrid-native, adjust-keep", 1.4,
     "Alpha Animals (sarg.alphaanimals)",
     str(AA_ROOT / "Textures/Things/Pawn/Animal/AA_Wildpawn/AA_Wildpawn_south.png"),
     "RotWildkin", "no", "mend ∝ bodySize", "no", "the fastest healer in the biome, but only in company — split them before you hunt"),
    ("AA_Wildpod", "wildpod", 0.2, "hybrid-native, adjust-keep", 4.0,
     "Alpha Animals (sarg.alphaanimals); WildpodArtOverride (game Mods folder) overrides the base art",
     str(GAME_MODS / "WildpodArtOverride/Textures/Things/Pawn/Animal/AA_Wildpod/AA_Wildpod_south.png"),
     "RotWildkin", "no", "mend ∝ bodySize", "no", "same organ as the wildpawn — the soft-aura variant"),
    ("RSW_FungalMantis", "fungal mimic mantis", 0.15, "guardian, import", 2.0,
     "SWBestiary (mandrake.rsw.swbestiary)",
     "src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FungalMantis/FungalMantis_south.png",
     "none (solitary predator)", "no", "no", "YES", "the false-fruit trap now has teeth — the mantis you never saw answers"),
    ("RUT_Emberscythe", "emberscythe mantis", None, "NOT in RUT_TheRot — a Pyrelands fire-follower shipped in this same kit", 1.3,
     "RotSporeKit (mandrake.rut.rotsporekit) — art is a vanilla Megascarab recolor placeholder, per its own header comment",
     str(RAW_VANILLA / "RUT_Emberscythe_vanilla_south.png"),
     "none", "no", "no (already has a solo InjuryHealingFactor 1.6)", "no", "keep Rot kin-mechanics out of fire country — wrong biome, already self-sufficient"),
]

# ============================================================================
# GROUP C — new art landed (other waves), scoped to what ISN'T already served by
# another dedicated sheet built today. See build report for the exclusion count.
# Fields: (job_id, target_def_or_note, mod, verdict, thumb_src_abs, wired)
# ============================================================================
GROUP_C = [
    ("twistingthornweed_v1_r2", "RUT_TwistingThornweed (twisting thornweed)", "UtinniPatches — RUT_PollutedFlora.xml (Cracked Lands / Poison Forest biomes, unrelated to the Rot or Lantern Deeps)",
     "facts PASS, validator skipped (no reference on this job)", ARTSRC / "twistingthornweed_v1_r2" / "twistingthornweed_v1_r2.png", False,
     "r2 supersedes a failed v1 attempt (not shown); 256x256"),
    ("twitchingpuffer_grown_v1", "RUT_TwitchingPuffer, grown stage", "LanternDeeps — RUT_DeepFlora.xml",
     "facts PASS, validator skipped (no reference on this job)", ARTSRC / "twitchingpuffer_grown_v1" / "twitchingpuffer_grown_v1.png", False,
     "finished AFTER today's Lantern Deeps sheet was built (that sheet still shows this slot as 'pending')"),
    ("twitchingpuffer_harvested_v2", "RUT_TwitchingPuffer, harvested/leafless stage", "LanternDeeps — RUT_DeepFlora.xml",
     "facts PASS, validator skipped (no reference on this job)", ARTSRC / "twitchingpuffer_harvested_v2" / "twitchingpuffer_harvested_v2.png", False,
     "v1 (not shown) rendered a wrapped cocoon — content miss; this v2 replaces it and finished AFTER today's Lantern Deeps sheet was built"),
    ("twitchingpuffer_immature_v1", "RUT_TwitchingPuffer, immature stage", "LanternDeeps — RUT_DeepFlora.xml",
     "facts PASS, validator skipped (no reference on this job)", ARTSRC / "twitchingpuffer_immature_v1" / "twitchingpuffer_immature_v1.png", False,
     "finished AFTER today's Lantern Deeps sheet was built"),
    ("twitchingpuffer_tendrils_v1", "RUT_PufferTendrils (harvested item)", "LanternDeeps — RUT_LanternstoneItems.xml",
     "facts PASS, validator skipped (no reference on this job)", ARTSRC / "twitchingpuffer_tendrils_v1" / "twitchingpuffer_tendrils_v1.png", False,
     "finished AFTER today's Lantern Deeps sheet was built"),
]

CANON_EXCLUDED = 39   # canon_* x {east,north,south} for 13 creatures — Transient/canon_regen_wave1_2026-09-18/
DEEPS_EXCLUDED = 45   # Lantern Deeps texture slots (minus the 4 dulcis + 5 puffer already handled above) — deeps_art_review_2026-09-18.html
DULCIS_EXCLUDED = 4   # dulcis* jobs — the target defName (RUT_DulcisPlant) is IN this sheet's Group A already


def thumb_name(defname_or_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", defname_or_id) + ".png"


def make_thumb(src: Path, dst: Path):
    """Plain thumbnail — still used for Group C (new art), which isn't a
    creature or a plant and has no drawSize/cells to be 'to scale' against."""
    from PIL import Image
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGBA")
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        im.save(dst)


def _human_figure(hh, Image):
    """A REAL RimWorld colonist body, the same asset the creature/plant scale
    sheets use (design/Jawa/worldbuilding/review/assets/human_anchor_south.png
    — the engine's own body+head sprites composited top-down), scaled to hh px
    tall (HUMAN_CELLS cells). Falls back to a crude outline only if that asset
    is gone, and deliberately crudely so the fallback is obvious on sight."""
    from PIL import ImageDraw
    try:
        im = Image.open(HUMAN_ANCHOR).convert("RGBA")
        k = hh / float(im.height)
        return im.resize((max(1, int(im.width * k)), hh), Image.LANCZOS)
    except Exception:                                        # noqa: BLE001
        fig = Image.new("RGBA", (max(6, int(hh * 0.45)), hh), (0, 0, 0, 0))
        ImageDraw.Draw(fig).rectangle([0, 0, fig.width - 1, hh - 1],
                                       outline=(255, 80, 80, 255))
        return fig


def _cap_panel(panel, Image):
    """Downscale to PANEL_MAX_PX if the built panel is wider/taller than that
    — this sheet's own cap (see the PANEL_MAX_PX note above)."""
    if max(panel.size) > PANEL_MAX_PX:
        k = PANEL_MAX_PX / float(max(panel.size))
        panel = panel.resize((max(1, int(panel.width * k)), max(1, int(panel.height * k))),
                              Image.LANCZOS)
    return panel


def _mesh_offsets(mesh):
    """The sub-grid the engine prints a multi-mesh plant on, in CELL fractions
    — identical to gen_plant_register.py's _mesh_offsets (Plant.Print,
    Plant.cs:1000-1020): side = sqrt(mesh), each copy at a grid center. No
    jitter, because a review picture must be identical between two runs."""
    side = int(round(mesh ** 0.5)) or 1
    step = 1.0 / side
    return [(((i // side) + 0.5) * step, ((i % side) + 0.5) * step)
            for i in range(side * side)]


def make_plant_scale_panel(src: Path, dst: Path, cells: float, mesh: int):
    """The plant at true in-game screen size (a `cells` x `cells` quad, the
    engine's own render, times a mesh-tiled sub-grid when maxMeshCount > 1)
    beside a human on a 1-cell grid. Same method as
    gen_plant_register.py's _scale_panel; copied here, see the module note."""
    from PIL import Image, ImageDraw
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as raw:
        im = raw.convert("RGBA")
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)

        hh = int(round(HUMAN_CELLS * PX_PER_CELL))
        fig = _human_figure(hh, Image)
        fig_w = fig.width
        quad = max(8, int(round(cells * PX_PER_CELL)))
        footprint = max(quad, PX_PER_CELL) if mesh > 1 else quad
        gap, pad = 12, 8
        tw = pad + fig_w + gap + footprint + pad
        th = pad + max(hh, footprint) + pad
        panel = Image.new("RGBA", (tw, th), (16, 22, 18, 255))
        d = ImageDraw.Draw(panel)
        for x in range(pad, tw, PX_PER_CELL):
            d.line([(x, 0), (x, th)], fill=(32, 42, 34, 255))
        for y in range(th - pad, -1, -PX_PER_CELL):
            d.line([(0, y), (tw, y)], fill=(32, 42, 34, 255))

        base_y = th - pad
        panel.alpha_composite(fig, (pad, base_y - hh))

        k = min(quad / float(im.width), quad / float(im.height))
        cw, ch = max(1, int(round(im.width * k))), max(1, int(round(im.height * k)))
        spr = im.resize((cw, ch), Image.LANCZOS if im.width > cw else Image.NEAREST)

        left = pad + fig_w + gap
        if mesh <= 1:
            panel.alpha_composite(spr, (left, base_y - ch))
        else:
            cell = max(footprint, PX_PER_CELL)
            for fx, fz in _mesh_offsets(mesh):
                x = left + int(fx * cell) - cw // 2
                y = base_y - int(fz * cell) - ch // 2
                x = max(0, min(tw - cw, x))
                y = max(0, min(th - ch, y))
                panel.alpha_composite(spr, (x, y))

        panel = _cap_panel(panel, Image)
        panel.convert("RGB").save(dst, optimize=True)


def make_creature_scale_panel(src: Path, dst: Path, cells: float):
    """The creature at true in-game screen size (a `cells` x `cells` box, its
    adult bodyGraphicData.drawSize) beside a human on a 1-cell grid. Same
    method as gen_creature_register.py's _scale_panel; copied, see module note."""
    from PIL import Image, ImageDraw
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as raw:
        im = raw.convert("RGBA")
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)

        box = max(8, int(round(cells * PX_PER_CELL)))
        hh = int(round(HUMAN_CELLS * PX_PER_CELL))
        k = min(box / float(im.width), box / float(im.height))
        cw, ch = max(1, int(round(im.width * k))), max(1, int(round(im.height * k)))
        fig = _human_figure(hh, Image)
        fig_w = fig.width
        gap, pad = 12, 8
        tw = pad + fig_w + gap + cw + pad
        th = pad + max(hh, ch) + pad
        panel = Image.new("RGBA", (tw, th), (18, 21, 26, 255))
        d = ImageDraw.Draw(panel)
        for x in range(pad, tw, PX_PER_CELL):
            d.line([(x, 0), (x, th)], fill=(34, 39, 47, 255))
        for y in range(th - pad, -1, -PX_PER_CELL):
            d.line([(0, y), (tw, y)], fill=(34, 39, 47, 255))

        base_y = th - pad
        panel.alpha_composite(fig, (pad, base_y - fig.height))
        cre = im.resize((cw, ch), Image.LANCZOS if im.width > cw else Image.NEAREST)
        panel.alpha_composite(cre, (pad + fig_w + gap, base_y - ch))

        panel = _cap_panel(panel, Image)
        panel.convert("RGB").save(dst, optimize=True)


def mature_cells_flora(defname):
    """drawSize.x * visualSizeRange.max — 'true in-game scale' at growth 1.0,
    same formula as gen_plant_register.py's mature_cells(). visualSizeRange is
    the size that actually varies per plant (drawSize is a constant 1.0 on
    every Group A def — see FLORA_DRAWSIZE's note), and it is read from the
    defs on every run, so a size ruling applied to a def shows up on the next
    sheet with no transcription step to get wrong."""
    (vmin, vmax), _ = resolve_visual_size_range(defname, _VSR_INDEX)
    return FLORA_DRAWSIZE[0] * vmin, FLORA_DRAWSIZE[0] * vmax


def vsr_is_inherited(defname):
    """True when the size comes from a parent def, not this def's own node."""
    _, authored = resolve_visual_size_range(defname, _VSR_INDEX)
    return not authored


def build_items(thumbs_relpath):
    items = []
    counts = {"A": 0, "B": 0, "C": 0}
    # thumb_jobs entries: {"kind": "plant"|"creature"|"plain", "src", "dst", "rel", ...extra}
    thumb_jobs = []

    # ---- Group A ----
    for defname, label, source, comm, desc, texpath, status, thumb_src, note in FLORA:
        counts["A"] += 1
        mincells, mcells = mature_cells_flora(defname)
        mesh = min(FLORA_MESH.get(defname, 1), MESH_CAP)
        inherited = vsr_is_inherited(defname)
        # Headline: mature size (what governs the panel and what a player
        # actually sees), drawSize demoted to a secondary note — drawSize is a
        # constant 1.0 on every Group A row and printing it first was
        # wallpaper (owner correction, 2026-09-18).
        sizetxt = f"mature size {mcells:.2f} cells (grows {mincells:.2f}→{mcells:.2f})"
        sizetxt += " [vanilla Plant-base default, not authored on this def]" if inherited else ""
        sizetxt += f"; drawSize {FLORA_DRAWSIZE[0]:.1f} × {FLORA_DRAWSIZE[1]:.1f} cells (vanilla default on every Group A row, never overridden — not what drives apparent size here)"
        if mesh > 1:
            sizetxt += f"; {mesh} meshes/cell (Graphic_Random tiling)"
        thumb_rel = None
        if thumb_src:
            dst_rel = f"{thumbs_relpath}/{thumb_name(defname)}"
            dst_abs = REPO_ROOT / "Transient" / thumbs_relpath / thumb_name(defname)
            thumb_jobs.append({"kind": "plant", "src": REPO_ROOT / thumb_src, "dst": dst_abs,
                                "rel": dst_rel, "cells": mcells, "mesh": mesh})
            thumb_rel = dst_rel
        commtxt = f"wildPlants commonality {comm}" if comm is not None else "not in wildPlants (sow/companion-only)"
        effect = f"{commtxt} — {status.upper()}. {sizetxt}. {desc}…"
        if note:
            effect += f" [{note}]"
        prefill = "keep"
        items.append({
            "id": f"A_{defname}",
            "label": f"{label} [{defname}]",
            "group": "A) Rot flora",
            "effect": effect,
            "thumb": thumb_rel,
            "prefill": prefill,
            "sortkey": -(comm or 0),
            "meta": {"source": source, "texPath": texpath, "artStatus": status, "commonality": comm,
                     "drawSize": list(FLORA_DRAWSIZE), "matureCells": round(mcells, 3), "mesh": mesh},
        })

    # ---- Group B ----
    for defname, label, comm, xmlclass, bodysize, source, thumb_src, kintag, woundlink, mend, alarm, trade in FAUNA:
        counts["B"] += 1
        adult_cells = FAUNA_DRAWSIZE.get(defname)
        commtxt = f"commonality {comm}" if comm is not None else "not in wildAnimals"
        bstxt = f"bodySize {bodysize}" if bodysize is not None else "bodySize n/a (not in wildAnimals)"
        dstxt = (f"adult drawSize {adult_cells:.2f} × {adult_cells:.2f} cells"
                 if adult_cells is not None else "adult drawSize UNMEASURED")
        thumb_rel = None
        if thumb_src:
            dst_rel = f"{thumbs_relpath}/{thumb_name(defname)}"
            dst_abs = REPO_ROOT / "Transient" / thumbs_relpath / thumb_name(defname)
            thumb_jobs.append({"kind": "creature", "src": REPO_ROOT / thumb_src, "dst": dst_abs,
                                "rel": dst_rel, "cells": adult_cells or 1.0})
            thumb_rel = dst_rel
        effect = (f"{commtxt} — class: {xmlclass}. {dstxt}. {bstxt}. "
                  f"kin tag: {kintag} | wound-link: {woundlink} | {mend} | alarm-responder: {alarm}. "
                  f"Trade: {trade}")
        items.append({
            "id": f"B_{defname}",
            "label": f"{label} [{defname}]",
            "group": "B) Rot fauna",
            "effect": effect,
            "thumb": thumb_rel,
            "prefill": "keep",
            "sortkey": -(comm or 0),
            "meta": {"source": source, "bodySize": bodysize, "kinTag": kintag, "adultDrawSize": adult_cells},
        })

    # ---- Group C ----
    for job_id, target, mod, verdict, thumb_abs, wired, note in GROUP_C:
        counts["C"] += 1
        dst_rel = f"{thumbs_relpath}/{thumb_name(job_id)}"
        thumb_jobs.append({"kind": "plain", "src": thumb_abs,
                            "dst": REPO_ROOT / "Transient" / thumbs_relpath / thumb_name(job_id),
                            "rel": dst_rel})
        effect = f"target: {target} | mod: {mod} | verdict: {verdict} | wired: {'YES' if wired else 'not wired'}. {note}"
        items.append({
            "id": f"C_{job_id}",
            "label": f"{job_id}",
            "group": "C) New art landed (other waves)",
            "effect": effect,
            "thumb": dst_rel,
            "prefill": "approve" if "PASS" in verdict and wired else "undecided",
            "sortkey": 0,
            "meta": {"target": target, "mod": mod, "wired": wired},
        })

    items.sort(key=lambda it: (it["group"], it["sortkey"]))
    for it in items:
        del it["sortkey"]
    return items, counts, thumb_jobs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the sheet, thumbnails and decisions seed (default: dry run)")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true", dest="force_overwrite",
                    help="required to regenerate the decisions file if it already carries savedBy/writeCount")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print(f"ERROR: sheet template not found at {TEMPLATE}", file=sys.stderr)
        return 1

    thumbs_relpath = OUT_THUMBS_DIR.name
    items, counts, thumb_jobs = build_items(thumbs_relpath)
    print(f"# build_review_sheet.py plan — {len(items)} rows "
          f"(A={counts['A']} flora, B={counts['B']} fauna, C={counts['C']} new-art)")
    for it in items:
        print(f"  [{'thumb' if it['thumb'] else 'NO-THUMB':8s}] {it['group']:32s} {it['id']}")

    if not args.apply:
        print(f"\nDry run only. Re-run with --apply to write:\n  {OUT_HTML}\n  {OUT_THUMBS_DIR}/*.png\n  {OUT_DECISIONS}")
        return 0

    # --- freeze protection: never overwrite a decisions file the owner has touched ---
    if OUT_DECISIONS.exists():
        try:
            existing = json.loads(OUT_DECISIONS.read_text())
        except Exception:
            existing = {}
        if (existing.get("savedBy") or existing.get("writeCount")) and not args.force_overwrite:
            print(f"REFUSED: {OUT_DECISIONS} already carries savedBy/writeCount — the owner has reviewed this. "
                  f"Pass --i-know-this-overwrites-the-owners-decisions to overwrite anyway.", file=sys.stderr)
            return 1

    OUT_THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    made, missing = 0, []
    made_by_kind = {"plant": 0, "creature": 0, "plain": 0}
    for job in thumb_jobs:
        src, dst, kind = job["src"], job["dst"], job["kind"]
        if not src.exists():
            missing.append(str(src))
            continue
        try:
            if kind == "plant":
                make_plant_scale_panel(src, dst, job["cells"], job["mesh"])
            elif kind == "creature":
                make_creature_scale_panel(src, dst, job["cells"])
            else:
                make_thumb(src, dst)
            made += 1
            made_by_kind[kind] += 1
        except Exception as exc:
            missing.append(f"{src} ({exc})")
    print(f"\nThumbnails written: {made} (plant scale panels: {made_by_kind['plant']}, "
          f"creature scale panels: {made_by_kind['creature']}, plain: {made_by_kind['plain']}); "
          f"missing/failed: {len(missing)}")
    for m in missing:
        print(f"  NO THUMB: {m}")

    cfg = {
        "sheetId": SHEET_ID,
        "title": "The Rot — flora, fauna & new-art review",
        "subtitle": f"{len(items)} rows — {counts['A']} flora, {counts['B']} fauna, {counts['C']} new-art (other waves)",
        "briefHtml": (
            "<p><b>Posture: BLACKLIST.</b> Every row defaults to <b>keep</b> (flora/fauna) or its own "
            "pre-filled call (new-art). Nothing is removed or wired unless you mark it otherwise — "
            "disagreeing is the whole point of this page.</p>"
            "<p><b>Group A — Rot flora:</b> every wildPlants entry in "
            "<code>RUT_TheRot.xml</code> (base + two patch files that append entries without editing "
            "that file directly), plus every non-abstract RotSporeKit plant ThingDef that isn't wild-spawned "
            "at all (fungiponics crop, pale-tree companion, the not-yet-wild-spawned furnace cap). "
            f"<b>{counts['A']}</b> rows. <code>cut</code> removes the species from the Rot (its wildPlants "
            "entry, or the ThingDef itself for the 3 non-wild rows); <code>regen</code> files an artpipe job.</p>"
            "<p><b>Group B — Rot fauna:</b> the build brief said 15 wildAnimals entries; "
            "<b>MEASURED 9</b> in the live <code>RUT_TheRot.xml</code> — see the build report for where "
            "the other 6 (all BMT_ cavern donor kinds) come from and why they are NOT shown here as if they "
            "were live. Plus RUT_Emberscythe (ships in this kit but is Pyrelands, not Rot). Kin-mechanics "
            "columns are the draft in <code>Transient/rot_fauna_assignment_draft_20260918.md</code>; the mend "
            "column reads <b>“mend ∝ bodySize”</b> for every tagged row per tonight's ruling "
            "(no longer a flat severity/day number). <code>cut</code> removes the species from wildAnimals.</p>"
            "<p><b>Group C — new art landed (other waves):</b> artpipe jobs that finished after "
            "2026-09-18 00:00 PDT and are NOT already covered by another dedicated sheet built today — "
            "39 canon_* creature-fidelity renders already have their own sheet "
            "(<code>Transient/canon_regen_wave1_2026-09-18/</code>) and 45 Lantern Deeps texture slots already "
            "have theirs (<code>Transient/deeps_art_review_2026-09-18.html</code>); both are excluded here to "
            "avoid a second, disagreeing review surface over the same renders — see the build report. "
            f"<b>{counts['C']}</b> rows remain: one totally unrelated biome's plant (twisting thornweed) and "
            "four Lantern Deeps puffer stages that finished AFTER that sibling sheet was already built (so it "
            "still shows them as pending). <code>approve</code> wires the PNG into its mod's Textures/; "
            "<code>reject</code> sends it back for a regen.</p>"
            "<p>Start with donor art where new art is unavailable — owner's instruction. The 22 "
            "Guardian-Groves/Furnace-Cap/Pale-Tree new-art jobs FAILED tonight on a codex quota limit and are "
            "still queued to re-run; until then those rows keep their shared-placeholder or vanilla texPath.</p>"
            "<p><b>Scale panels (owner ask):</b> every Group A/B thumbnail with a source image is now a "
            "TO-SCALE panel — the sprite at its true in-game cell size beside a real colonist "
            "(human_anchor_south.png, 1.5 cells tall), on a 1-cell grid, capped at 240px wide. A plant's "
            "in-game size is <code>plant.visualSizeRange</code> (its max at maturity), NOT "
            "<code>graphicData.drawSize</code> — drawSize measures 1.0 × 1.0 on every one of the 40 flora "
            "rows and drives nothing, so each row leads with <b>mature size {max} cells (grows {min}→"
            "{max})</b> and demotes drawSize to a secondary note. visualSizeRange is resolved through the full "
            "inheritance chain including vanilla RimWorld's own Plant bases (PlantBase/TreeBase default to "
            "0.3~1.0 / 1.5~2.0 when nothing else overrides) — every one of the 40 rows resolves a real range, "
            "none are a guess. Fauna rows print the adult life stage's drawSize plus bodySize (fauna drawSize "
            "genuinely does vary per race, unlike flora's). See CONFIG.invented for the full sourcing.</p>"
        ),
        "criterion": "Sorted by commonality within each group (flora/fauna) — ranks how often the player "
                     "meets it, not its worth. Group C is unordered (five rows).",
        "invented": [
            "Group A scope reading: 'plant ThingDef' means a def carrying a <plant> block, not every ThingDef "
            "in the ThingDefs_Plants folder — excludes co-located harvested items/resources/projectiles "
            "(RUT_Glimmerslime, RUT_MedicineFungal, RUT_MoonlessSilk, RUT_RawDulcis, RUT_BlastSpore, "
            "RUT_Proj_BlastSporeSac, RUT_ChokingSpores).",
            "Group B: the build brief said 15 wildAnimals; the live RUT_TheRot.xml MEASURES 9. No patch was "
            "found adding the other 6 (all BMT_ cavern donor kinds named in the fauna_assignment draft) to this "
            "biome's wildAnimals — they read as a PROPOSED roster in that draft, not a landed one. Reported "
            "as measured (9 + RUT_Emberscythe = 10 rows), not as briefed.",
            "AA_ (Alpha Animals) and AB_ (Alpha Biomes) donor mods ARE reachable — the first pass's "
            "'unreachable' claim was a resolver bug: an About.xml packageId grep missed both because their "
            "About.xml lists <modDependencies> (which name OTHER packageIds) before the mod's own <packageId> "
            "line, and a naive whole-file grep for the substring still should have hit it, but the two greps run "
            "that pass happened to time out past budget before reaching either folder. Corrected 2026-09-18 late "
            "pass using the coordinator-supplied Workshop ids (Alpha Biomes 1841354677, Alpha Animals "
            "1541721856) plus the game Mods folder's *ArtOverride mods, which take priority over the base "
            "donor art where one exists (AgaripodArtOverride, MycoidColossusArtOverride, WildpodArtOverride).",
            "4 of 13 AlphaBiomes plant rows (AB_Bryolux, AB_Glowstool, AB_Agarilux, AB_GlowingAgarilux) have no "
            "art file in the AlphaBiomes Workshop mod itself, and that is CORRECT, not a gap: their texPaths "
            "(Things/Plant/Bryolux, Glowstool, Agarilux) are vanilla Core cave-plant textures the donor mod "
            "deliberately reuses rather than shipping its own — Core has stocked Bryolux/Agarilux/Glowstool "
            "art since 1.4. Resolved the same way as RUT_PaleTree/PaleMoss/Emberscythe: UnityPy against the "
            "base resources.assets, bare letter-suffix Graphic_Random names with no prefix (BryoluxA, "
            "AgariluxA, GlowstoolA), first alphabetically. Art status on these 4 rows is 'vanilla', not "
            "'donor'.",
            "RUT_PaleTree/RUT_PaleMoss (vanilla TreeAnima/Grass_Anima) and RUT_Emberscythe (vanilla Megascarab "
            "recolor) were extracted via UnityPy under Windows python.exe: TreeAnima and Grass_Anima are "
            "Graphic_Random families with no underscore (bare letter suffix, e.g. TreeAnimaA / Grass_AnimaA — "
            "picked the first alphabetically per the reading-rimworld-graphics skill), Megascarab resolves "
            "directly to 'Megascarab_south' in the base resources.assets. TreeAnima/Grass_Anima come from the "
            "Royalty DLC's own bundle (Data/Royalty/AssetBundles/resources_royalty), not the base game's "
            "resources.assets — Core ships no AssetBundles of its own, Royalty does.",
            "Group C scope: excluded 39 canon_* creature-fidelity manifests (already served by "
            "Transient/canon_regen_wave1_2026-09-18/, its own sheet) and 45 Lantern Deeps texture-slot "
            "manifests (already served by Transient/deeps_art_review_2026-09-18.html) to avoid a duplicate, "
            "disagreeing review surface over renders someone is already reviewing today. The 4 dulcis* jobs are "
            "also excluded from Group C because their target (RUT_DulcisPlant) is a Group A row in THIS sheet.",
            "'wired' in Group C is a literal md5 byte-match between the artpipe _artsrc PNG and every PNG under "
            "src/**/Textures/ — none of the 5 remaining rows matched, so all five read 'not wired'.",
            "A plant's in-game size is <plant><visualSizeRange> (its MAX at maturity), NOT "
            "graphicData.drawSize — owner correction, 2026-09-18. drawSize IS measured 1.0 × 1.0 on "
            "every one of the 40 Group A flora defs (confirmed by grep: the literal string 'drawSize' occurs "
            "exactly once in the whole flora file set, on RUT_MedicineFungal, an item not a plant) — but that's "
            "wallpaper, not the size signal, and the headline text now leads with mature size "
            "(visualSizeRange.max) with drawSize demoted to a secondary note.",
            "visualSizeRange is now resolved through the FULL inheritance chain, including vanilla RimWorld's "
            "own Plant bases, not just each def's own tag and its RotSporeKit/AlphaBiomes custom abstract. "
            "MEASURED from the game's own Data/Core/Defs/ThingDefs_Plants/Plants_Bases.xml: PlantBaseNonEdible "
            "sets 0.3~1.00 (PlantBase inherits it unchanged), TreeBase sets 1.5~2.0. Resolving through that "
            "fixed one real number — RUT_FlakespireFungus (RUT_CaveTreeBase -> TreeBase) is 1.5~2.0, not the "
            "first pass's fallback of a bare 1.0 — and correctly re-labels the other 12 rows that inherit "
            "PlantBase's 0.3~1.0 (11 AlphaBiomes donor rows + RUT_BleedingTooth) as 'vanilla default, "
            "inherited', not 'not set'. Every one of the 40 flora rows now resolves a REAL visualSizeRange; "
            "none are an un-sourced guess.",
            "Scale panels reuse the exact method in gen_plant_register.py's _scale_panel/_human_figure (plants, "
            "including its mesh-tiling sub-grid for maxMeshCount > 1) and gen_creature_register.py's "
            "_scale_panel (fauna) — copied rather than imported, because both modules pull in cherrypicker / "
            "game_paths / rimworld_loadset (live def-dump and Windows-path machinery) this generator's own "
            "hand-curated ROWS tables don't use. The human figure is the SAME real colonist sprite those "
            "scripts use (design/Jawa/worldbuilding/review/assets/human_anchor_south.png, already on disk — "
            "no re-extraction needed). PX_PER_CELL (64) and HUMAN_CELLS (1.5) match those scripts exactly; the "
            "240px panel cap is THIS sheet's own (the reference scripts build much larger dedicated inspection "
            "images, 1200-1500px, for a page whose only job is art review — this is a row thumbnail on a mixed "
            "sheet, so 240px per the owner's instruction here).",
            "Fauna cell size is the ADULT (last) life stage's bodyGraphicData.drawSize, MEASURED per race from "
            "its own PawnKindDef life-stage list (RSW_/AA_ from their own source files, RUT_Emberscythe from "
            "this repo) — not a fitted or inferred figure.",
        ],
        "posture": {"mode": "blacklist", "explain": "Default is KEEP for flora/fauna. A row only leaves the "
                    "biome if you mark it cut. Group C defaults to its own pre-filled approve/undecided call."},
        "options": [
            {"key": "keep", "label": "Keep", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "regen", "label": "Regen art", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "cut", "label": "Cut", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
            {"key": "undecided", "label": "Undecided", "hotkey": "4", "color": "#98a2b3", "counts": "in"},
            {"key": "approve", "label": "Approve (wire in)", "hotkey": "5", "color": "#5ac37f", "counts": "in"},
            {"key": "reject", "label": "Reject (regen)", "hotkey": "6", "color": "#e06c6c", "counts": "out"},
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

    if not OUT_DECISIONS.exists() or args.force_overwrite:
        seed = {"sheetId": SHEET_ID, "posture": "blacklist", "frozen": False, "writeCount": 0, "decisions": {}}
        OUT_DECISIONS.write_text(json.dumps(seed, indent=2) + "\n")

    print(f"\nWrote {OUT_HTML}")
    print(f"Decisions file: {OUT_DECISIONS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
