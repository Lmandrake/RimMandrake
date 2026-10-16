# Donor art census, 2026-10-15 (read-only; nothing queued, installed or committed)

Scope: every donor mod other than `mlie.starwarsanimalcollection` (SW done). Method and honest limits first, then per-donor tables.

## Method (and what it can miss)

1. **Donor-served texture census** (my script, scratchpad `census.py`): every texPath/iconPath/graphicPath/immatureGraphicPath in our `src/**/*.xml` (3,648 distinct), minus those that resolve to a PNG under any `src/**/Textures` (directional `_north/_south/_east/_west` suffixes stripped, folders counted), then looked up in the loose `Textures/` of all 1,271 workshop mods. First pass without suffix stripping falsely showed 1,316 unresolved (it flagged the SW swanimals paths); with it, 293 remain, of which ~97 are vanilla/DLC bundled art and the rest are vanilla-retexture mods (VTE, Tang, Gerrymon...), which are NOT donors. **Only these are real donor-served textures in our own defs** (list below).
2. **Donor-def dependency census** (`refs2.py`/`art5.py`): donor ThingDef/PawnKindDef/TerrainDef names still named in active (comment-stripped) XML in `src/`, minus patch files that merely tune the donor def (MegafaunaYield, AnimalTolerances, WeaponTags, label/resize patches, ...). Those leave nothing to draw. Remaining rows are roster/def uses that need a port or a swap.
3. **Existence proof per row**: `artpipe_state.py find` (25,146 entries + ledger), `_artsrc`/`done` job-id name search, and src Textures name search. A hit means pixels exist, NOT that the owner approved them or that the def is wired. "ap" below = artpipe job-id hits by name stem (heuristic, can miss renamed targets and over-match).
- Not measured: Droid Depot art path (droids use RimWorld-side bodies/skins, rendering path not traced); Alpha Biomes terrain texture binding. Flagged per donor.
- Reminder: a donor's own PawnKindDefs patched for `Dessicated` paths (AnimalDessicatedTexPaths_Fix, GrimTerraTexPaths_Fix) are donor-def patches; they die with the donor and owe no art.

## A. Proven donor-served textures in OUR defs (the only real "art to queue now")

| donor | our def | donor texPath served | file | art exists? |
|---|---|---|---|---|
| sarg.alphaanimals | `RSW_SandLion` (adult, juvenile, child) | `Things/Pawn/Animal/AA_SandLion/AA_SandLion` | `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_SandLion.xml` | NO (ledger has donor variants only) |
| sarg.alphaanimals | `RSW_SandLion` dessicated | `.../AA_Dessicated_SandLion` | same | NO |
| sarg.alphaanimals | `RM_EggTuskcoilFertilized`, `RM_EggTuskcoilUnfertilized` | `Things/Item/Resource/AA_EggBeetle` | `src/RimMandrake/LongShade/Defs/ThingDefs_Items/RM_LongShade_FaunaSupport.xml` (l.60, 82) | NO (sibling `RM_EggGulloth` is done and installed) |
| sarg.alphaanimals | `RM_BlackChitin` | `Things/Item/Resource/AA_Chitin` | same file l.136 | NO |
| sarg.alphaanimals | `RSW_CactusMeat` | `Things/Item/Resource/AA_Cactipine_Meat` | `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Items.xml` l.77 | NO |
| oskarpotocki.vfe.insectoid2 | `RSW_InsectChitin` | `Things/Item/VFEI_Chitin` (marked TEMP PLACEHOLDER) | same Items file l.46 | NO |
| biomesteam.biomescaverns | `RUT_FungalSoil` item | `BMT_Caverns/Terrains/MycelialSoil` | `src/RimUtinni/FungalSoilTrade/Defs/ThingDefs_Items/RUT_FungalSoil.xml` l.35 | NOT an art job: our own `RotSporeKit/Terrains/MycelialSoil` exists, repoint |
| neronix17.hd.pawns | SW_HeadTypes FurCovered heads x10, gene icons Gene_Darkvision / Gene_FacialRidges | ambiguous (VTE also serves FurCovered heads) | StarWarsRaces | UNVERIFIED: heads maybe vanilla-retex; check before filing |

Everything else in the census was vanilla/VTE/Tang noise or SW `swanimals/*_Flying_` flip-book frame-prefix strings (not files).

## B. Per-donor remaining art, ranked closest to retirement

"Jobs" = new sprites with no render anywhere. "Install" = render exists, needs port/wire/owner Accept (not a job). Wiring work (swap roster row, repoint) is not art and not counted.

| rank | donor | remaining art JOBS | renders to install / wire | notes |
|---:|---|---:|---|---|
| 1 | `lingluo.cockroach` | 0 | 0 | only `Ling_Cockroach` mentioned in comments now |
| 1 | `who.vfee.isopodageneline` | 0 | 0 | Warscar ports exist with textures (RM_ElectricGryllotalpa, RM_JuggernautBeetle, ElectricTick, all in Scarlands); leftover refs are patches (Emperorisopod/Grenadierworm in MegafaunaYield). Must retire WITH insectoid2 |
| 1 | `biomesteam.biomespollutedlands` | 0 | 0 | ports done (RSW_Screecher, RSW_Sacapillar, ...) , leftovers are patch/yield rows |
| 1 | `biomesteam.biomescaverns` | 0 | 0 | six crystal fauna are EVICTION patches (`LanternDeeps/Patches/RUT_LanternDeepEvictCrystalFauna.xml`); only the MycelialSoil repoint (no art) |
| 1 | `mlie.horrors` | 0 | `Visceral` render exists (`gapall_Visceral_v1`) | `Terrorworm` row in `RM_LeaningScrub_Biome.xml` is a STALE donor row: it is already `RM_Vurra` (art ledger: "resolves to RM_Vurra, originals Terrorworm", 4 bound). Swap the row, no art. Biome/HorrorWeb/MaggotNest refs unmeasured |
| 6 | `oskarpotocki.vfe.insectoid2` | **1** (InsectChitin icon) | `VFEI2_Megathrips` (`gapall_VFEI2_Megathrips_v1`), `VFEI2_Swarmling` (`gapall_VFEI2_BlackSwarmling_v1`, `rot_swarmling_v2`, `miasma_swarmling_green_v3`) need port + wire | `VFEI2_InfestedShipPart/Chunk` are vault SymbolDefs: replace with an owned wreck def, no art needed |
| 7 | `regrowth.botr.core` | 0 | 7 plant rows all have renders (`gapfin_/gapbs_RG_*`, `brambles_v1`); `Plant_Grass` is an own-tex-heavy case | owner decision "which are ported" is UNMEASURED; port exists for Rimclaw |
| 8 | `grimterra.biomesmod` | ~4 (GRimThornvine, GRim1Thornvine, GRim2Thornvine, TreePalma) | `GRimMoss` renders exist (`grimmoss_v1`) | Thornvines touched only by a RUT edibility patch, so possibly no spawn use: verify before filing. Also 4 donor species with tex-path patches live in rosters/tolerances |
| 9 | `sarg.alphaanimals` | **5 sprite groups from A** + creatures below | ~25 renders exist unwired (AngelMoth, Mantrap, Lockjaw, Plasmorph, OcularJelly, Aerofleet...) | roster rows with NO render: `AA_BloodShrimp`, `AA_RaptorShrimp`, `AA_Needlepost` (Skorra art `gapall_RSW_Skorra_v1` awaiting owner), `AA_Eyeling`, `AA_Cactipine` (ported as RM_Chikka, stale row), `AA_GreenGoo`, `AA_AcanthamoebaGiganteaSmall/Large`, `AA_SandLion` (see A) => ~7 creature jobs, 2 of them item-like death bursts. Wiring is the bulk (39 PawnKind rows) |
| 10 | `vanillaexpanded.vgeneticse` | ~1 (`GR_ParagonRat`?) | `GR_Molebear` render exists | 5 rows all in resize/label patches: possibly 0; plus cross-dep: `GR_Beetlefleet` needs Alpha Animals |
| 11 | `sarg.alphabiomes` | ~18 terrain textures (AB_ForsakenSand, AB_FineForsakenSand, AB_DarkMud, AB_PackedIce, AB_SnowOverRocks, AB_BlackPebbles, AB_HardenedGrass(+Fertile), AB_LushGrass, AB_GrassySand, AB_TarMud, AB_SoilOnCrackedMetal, AB_FertileMud, AB_LiquidSlime, GU_AlienSand x3) | ~45 plant renders exist (legacy_/rot_/gap* ids) | terrain binding UNMEASURED, needs an owner decision on whether biome terrain counts as "art owed" |
| 12 | `neronix17.outerrim.droiddepot` | 18 droid PawnKinds, 0 renders | 0 | Droidworks core dependency by design (Races_OuterRim, DROIDWORKS_* items); retirement is a project, not an art queue. Not graded |

Closest to retirement ART-wise: cockroach, isopod, pollutedlands, caverns, horrors (all 0 art). They stay installed only for wiring/swap work: Horrors Terrorworm row and VFEI2 pair. insectoid2 and isopod retire together.

## C. Existing-art proof for the jobs proposed below

- `artpipe_state.py find` on SandLion, Cactipine, BlackChitin, MycelialSoil, BeardedYak, GrenadeBug, InsectChitin, FurCovered, Tuskcoil: none bound (SandLion: 3 ledger variants all of the DONOR pixels, 1 name-matched job). Tuskcoil only has `RSW_Tuskcoil` creature renders, no egg.
- `RM_BlackChitin`, `RSW_CactusMeat`, `RSW_InsectChitin`, `RM_EggTuskcoil*Fertilized`: "0 bound, 0 name-matched; 0 raw text hits".
- Canon library: no entry for sand lion (AA_SandLion is the mod's own invention), so no canon target. Brief source = the donor's own description + our def; donor art is a style/anatomy reference only (no donor pixels, per no-donor-art rule).

## D. Ready job list for the top-2 donors (NOT filed; fill_queue-style; rows need canvas_w/canvas_h, `facings` list)

Top 2 by fewest remaining jobs among donors that HAVE jobs: **#1 insectoid2 (1 job)**, **#2 Alpha Animals (the 5 proven rows; the 7 creature jobs need an owner keep/cut first)**. Item style: match `RM_EggGulloth` (done job, 128x128, drawSize 1.0, transparent, "biome register" optional); creature style: match `donorart_*` rows in `design/RimMandrake/donor_pack_art_commission2_2026-10-15.json` (512 floor for >=2.5 drawSize, painterly natural-history, transparent, east master + north/south derived).

```json
[
 {"id":"donorart_vfei_chitin_v1","rimflow_item_id":"DONOR_DEFS_PORT_TO_OURS_1","target_def":"RSW_InsectChitin",
  "target_texpath":"Things/Item/VFEI_Chitin","install_to":"src/RimStarWars/SWBestiary/Textures/Things/Item/VFEI_Chitin.png",
  "canvas_w":128,"canvas_h":128,"drawsize":1.0,"facings":[],"background":"transparent",
  "brief_source":"RSW_DesertPortMisc_Items.xml l.40-48 description: 'An extremely thick composition of rare minerals and biomass, commonly found in a form of insect exoskeletons.' (donor VFEI2_Chitin). Graphic_StackCount: also needs a _a/_b stack look? CHECK donor stack art count before filing.",
  "canon":null,"style_notes":"inventory item icon, a small stack of thick dark insect-shell plates, painterly vanilla-RimWorld, no outline, regenerate: do NOT reuse donor pixels"},

 {"id":"donorart_sandlion_v1","target_def":"RSW_SandLion","target_texpath":"Things/Pawn/Animal/AA_SandLion/AA_SandLion",
  "install_to":"src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/AA_SandLion/AA_SandLion_{facing}.png",
  "canvas_w":512,"canvas_h":512,"drawsize":2.5,"facings":["east","south","north"],"background":"transparent",
  "brief_source":"donor AA_SandLion description (Races_SandLion.xml): arctic-lion variant engineered by a navy as an ambush animal for extreme heat, no light-reflecting pelt; digs in. Our def drawSize 1.2 / 1.85 / 2.5 per stage, all stages share one texPath.",
  "canon":null,"note":"ALSO re-point texPath off the 'AA_' folder name once installed (fold into retirement)."},
 {"id":"donorart_sandlion_dessicated_v1","target_def":"RSW_SandLion","target_texpath":"Things/Pawn/Animal/AA_SandLion/AA_Dessicated_SandLion",
  "canvas_w":512,"canvas_h":512,"drawsize":2.5,"facings":["east","south","north"],"background":"transparent",
  "brief_source":"dried corpse of the sand lion above; standard RimWorld Dessicated look, bleached bone, shrunken hide"},

 {"id":"donorart_tuskcoil_egg_v1","target_def":"RM_EggTuskcoilFertilized","target_texpath":"Things/Item/Resource/AA_EggBeetle",
  "install_to":"src/RimMandrake/LongShade/Textures/Things/Item/Resource/RM_EggTuskcoil.png (then repoint both egg defs l.60,l.82)",
  "canvas_w":128,"canvas_h":128,"drawsize":1.0,"facings":[],"background":"transparent",
  "brief_source":"RM_LongShade_FaunaSupport.xml egg defs + sibling art `RM_EggGulloth` (done, same register); tuskcoil = RSW_Tuskcoil, art `RSW_Tuskcoil_*` in _artsrc. Fertilized and unfertilized share the texture today: one icon is enough."},
 {"id":"donorart_blackchitin_v1","target_def":"RM_BlackChitin","target_texpath":"Things/Item/Resource/AA_Chitin",
  "install_to":"src/RimMandrake/LongShade/Textures/Things/Item/Resource/RM_BlackChitin.png (repoint l.136)",
  "canvas_w":128,"canvas_h":128,"drawsize":1.0,"facings":[],"background":"transparent",
  "brief_source":"RM_LongShade_FaunaSupport.xml l.130-140 description; Long Shade palette (amber/ochre lighting) as in RM_EggGulloth job"},
 {"id":"donorart_cactus_meat_v1","target_def":"RSW_CactusMeat","target_texpath":"Things/Item/Resource/AA_Cactipine_Meat",
  "install_to":"src/RimStarWars/SWBestiary/Textures/Things/Item/Resource/RSW_CactusMeat.png (repoint l.77)",
  "canvas_w":128,"canvas_h":128,"drawsize":1.0,"facings":[],"background":"transparent",
  "brief_source":"RSW_DesertPortMisc_Items.xml l.72-80 label 'plant meat'; vanilla raw-meat shape language, pale green-white fibrous flesh"}
]
```

Canon reference slot: none apply (no SW canon for any of these; canon library is Star Wars creature/droid only). Briefs must be authored from def text; `rimworld-canon-references` does not gate these.

## E. Safe to queue immediately vs not

SAFE NOW (all proven missing, no owner ruling blocks): the 6 rows in D (1 insectoid2 item + 5 Alpha Animals rows). Installing needs the usual `art.py install --owner-said` on his Accept; cosmetic changes need his permission but replacing donor-served textures for retirement is established practice.

NOT YET: Alpha Animals creature rows without renders (`AA_BloodShrimp`, `AA_RaptorShrimp`, `AA_Eyeling`, `AA_GreenGoo`, `AA_Acanthamoeba*`) need keep/cut (project rule: cut list first); Alpha Biomes terrain, Droid Depot, GrimTerra thornvines need measurement or owner decision. Horrors/Caverns/Polluted/Isopod/cockroach need wiring, not art.

## F. Traps seen

- My first texture pass overcounted 1,316 unresolved because directional suffixes were not stripped: 1,023 false hits. Instrument sanity: it flagged SW swanimals paths that the handoff says are fine.
- Comment text counts as a "reference": comment-stripping dropped Isopod from 5 defs to 0 (they are port comments).
- `Terrorworm`, `AA_Cactipine`, `AA_Needlepost` are donor rows for creatures already ported (RM_Vurra, RM_Chikka, RM_Skorra): do not file art for them.
