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
    from PIL import Image
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGBA")
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        im.save(dst)


def build_items(thumbs_relpath):
    items = []
    counts = {"A": 0, "B": 0, "C": 0}
    thumb_jobs = []  # (src_abs, dst_abs, dst_relpath)

    # ---- Group A ----
    for defname, label, source, comm, desc, texpath, status, thumb_src, note in FLORA:
        counts["A"] += 1
        thumb_rel = None
        if thumb_src:
            dst_rel = f"{thumbs_relpath}/{thumb_name(defname)}"
            thumb_jobs.append((REPO_ROOT / thumb_src, REPO_ROOT / "Transient" / thumbs_relpath / thumb_name(defname), dst_rel))
            thumb_rel = dst_rel
        commtxt = f"wildPlants commonality {comm}" if comm is not None else "not in wildPlants (sow/companion-only)"
        effect = f"{commtxt} — {status.upper()}. {desc}…"
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
            "meta": {"source": source, "texPath": texpath, "artStatus": status, "commonality": comm},
        })

    # ---- Group B ----
    for defname, label, comm, xmlclass, bodysize, source, thumb_src, kintag, woundlink, mend, alarm, trade in FAUNA:
        counts["B"] += 1
        thumb_rel = None
        if thumb_src:
            dst_rel = f"{thumbs_relpath}/{thumb_name(defname)}"
            thumb_jobs.append((REPO_ROOT / thumb_src, REPO_ROOT / "Transient" / thumbs_relpath / thumb_name(defname), dst_rel))
            thumb_rel = dst_rel
        commtxt = f"commonality {comm}" if comm is not None else "not in wildAnimals"
        bstxt = f"bodySize {bodysize}" if bodysize is not None else "bodySize n/a (not in wildAnimals)"
        effect = (f"{commtxt} — class: {xmlclass}. {bstxt}. "
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
            "meta": {"source": source, "bodySize": bodysize, "kinTag": kintag},
        })

    # ---- Group C ----
    for job_id, target, mod, verdict, thumb_abs, wired, note in GROUP_C:
        counts["C"] += 1
        dst_rel = f"{thumbs_relpath}/{thumb_name(job_id)}"
        thumb_jobs.append((thumb_abs, REPO_ROOT / "Transient" / thumbs_relpath / thumb_name(job_id), dst_rel))
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
    for src, dst, _rel in thumb_jobs:
        if not src.exists():
            missing.append(str(src))
            continue
        try:
            make_thumb(src, dst)
            made += 1
        except Exception as exc:
            missing.append(f"{src} ({exc})")
    print(f"\nThumbnails written: {made}; missing/failed: {len(missing)}")
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
