# Donor art census and donor-mod retirement, 2026-10-18

Owner, 2026-10-18: *"Focus on retiring donor art fully."* Then: *"Just put in placeholder art for now or donor copies
and retire these mods!!! Just get it done."* Then: *"Yes. Simply accept all art as currently rendered to get this done.
We will re review at a later time. No more art blockers."* (the last two relayed to FOUNDRY by the coordinator).
Standing ruling 2026-10-05: no donor art is kept, vanilla counts as donor, donor art stays on sheets as past art only.

FOUNDRY, offline. The game and the bridge were not touched. Nothing has been deployed: a donor-off live round is owed
(`DONOR_FOUR_RETIRE_JUST_GET_IT_DONE`).

## 1. Instruments (all re-runnable)

| question | command | notes |
|---|---|---|
| which texPaths our XML names, and who serves each | `python3 src/RimMandrake/Utils/donor_retire_census.py srctex --json OUT` | today's `src/` (placeholder_lint walk), resolved against our Textures first, then the gametex index of both game roots + AssetBundle extracts. A retexture pack's copy of a base-game path is `VANILLA_RETEXTURED`. |
| the same from the live def dump | `... donor_retire_census.py tex --json OUT` | the 2026-10-16T09-47-54Z DefDump (549 mods). Sees runtime-made defs (GravTide crossable rocks) but not defs added after the capture. SANITY: `RSW_WreckedSkiff` must read OURS or it aborts. |
| live (non-comment) references to a donor packageId | `... donor_retire_census.py refs --json OUT` | XML read as elements: MayRequire attributes, `<li>` packageIds, About.xml. `.cs/.py/.json` by string. |
| who hard-depends on a donor | `... donor_retire_census.py deps` | every installed About.xml. Probe: finds `daria40k.alphaanimalspatchoutposts -> sarg.alphaanimals`. |
| copy borrowed art into our mods as marked stand-ins | `python3 src/RimMandrake/Utils/art/donor_standins.py plan|apply` | art ledger provenance `kind=donor, standin=true`; repoints `*Path` elements to `StandIn/<orig>`. |
| the save | `save_donor_census.py`, `save_donor_rewrite.py` | control `<def>Human</def>` = 75. |
| roster / def regeneration state | `art/biome_census.py` + `art/texture_regen_audit.py` | see `biome_texture_regeneration_audit_2026-10-18.md`. |

## 2. The census, as measured at the start (HEAD 1f1ecdfeb, 2026-10-18 ~17:30 PDT)

### 2.1 texPaths our src XML names: 3,267

| class | texPaths | meaning | next action |
|---|---:|---|---|
| OURS_SRC | 2,948 | a picture under our `src/**/Textures` | regenerated or not: `texture_regen_audit.py` decides (2.4) |
| OURS (deployed only) | 92 | a mandrake mod in the game folder ships it, `src/` does not | deploy drift; check before the next `--prune` |
| VANILLA | 170 | base game or DLC bundle | vanilla counts as donor: a render of ours is owed (regen jobs) |
| VANILLA_RETEXTURED / _UNINDEXED | 7 + 7 | a retexture pack overrides a base-game path, or Core is not fully indexed | as VANILLA |
| DONOR (active mod) | 23 | another active mod serves it | stand-in copy (done, 3.1); a render owed |
| DONOR_BUNDLE | 3 | a donor AssetBundle | 2 vanilla paths (Thrumbo, Hive); 1 donor gene icon (`Outland/.../Bulb`) left |
| DONOR_INACTIVE | 4 | only an inactive mod ships it: magenta in game | stand-in copy (done) |
| MISSING | 13 | nowhere | 11 had a finished render: installed (3.1) |

### 2.2 The same from the 10-16 def dump: 5,395 texture slots, 3,084 texPaths

OURS 4,102 · VANILLA 1,124 · MISSING 36 · DONOR_BUNDLE 34 · VANILLA_RETEXTURED 31 · DONOR_INACTIVE 24 ·
VANILLA_UNINDEXED 24 · DONOR 20. Most of the dump's SWAC-bundle and MISSING rows were already fixed in `src/` after
the capture (Krayt, Rycrit, Taozin, Wampa, Yobshrimp now name regenerated art; L04's RM_ plants resolve). The 38
`L04_TEX_OURS` lines of `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` reduce to the four VPE-succulent plant paths
(`SnakePlantA`, `PincushionPlantA/B`, `EcheveriaA`), handled in 3.1.

### 2.3 Live references to donor packageIds in src/: 563 (46 more in FlowWorks, not touched)

The shipping layer's SWAC and Alpha Animals rows were already ported (Phase 0 P1/P2). What remained: 4 AA leather
fields, 1 AA damage worker, 18 About.xml rows, 11 frozen-twin biome workers on Alpha Biomes, 10 dead FindMod blocks,
~41 Alpha Biomes roster/terrain/disease rows in TheRot/TheForge/Miasma/TheSump/RustCathedral/Abyss, the Cauldron
garsulix (a VGE def that exists only while Alpha Animals loads), and ~80 unguarded Alpha Biomes rows in the frozen
`RUT_` twins, which are the biomes painted on the planet.

### 2.4 Rosters (918 rows, `texture_regen_audit.py`)

REGEN 654 · DONOR 136 · UNPROVEN 87 (72 of them stems the owner ruled on in a sheet) · PLACEHOLDER 27 ·
NO_LIVE_DONOR_ONLY 10 · NO_LIVE_ART 3 · DERIVED 1. About 240 of the non-REGEN rows have a finished render of ours in
the artpipe state; 18 true gaps were queued by the audit (`biome_texture_regen_jobs_2026-10-18.json`).

### 2.5 The canonical save (`CANONICAL_ASHKARR_START_2026-09-12.rws`)

1,691 donor defNames present, 8,945 element hits, most of them storage filters and price history. Non-benign:
SWAC 46 (world pawns Kreetle/Lothcat/Mynock, Scavrat on a map, worn leathers, drugs), Alpha Animals 15 (the ikee
`AA_Eyeling` x2 and its body), Alpha Biomes 42 (about 90 `AB_Mech_Ruined*` buildings on maps, 3 `AB_MagmaticQuagmire`
landmarks, work priorities, world-gen keys), **Alpha Memes 98 (ideoligion precepts, rituals, abilities, needs)**.
The world record `world/ASHKARR_WORLDMAP_tiles.csv` (export 2026-09-12) has 0 tiles on any `AB_` biome (probe:
`RUT_Wasteland` 1,853), so the planet's tiles do not need Alpha Biomes.

## 3. What was done

### 3.1 Art (commits on origin/main)

- `49f734a92`: 11 MISSING textures got their finished renders (Cauldron assay flecks and 5 dew overlays, Dakkra
  rest x3, CrawlSmear), through `artpipe_state.py collect`.
- `d95eb2771`: 20 borrowed texPaths copied into our mods as stand-ins under `StandIn/<orig texPath>` and repointed in 13
  XML files: RockTrollBaby (van.beasts), ReGrowth ChunkStone, 3 VPE-succulent plants, VFE IConduit, Kyber Synthetic,
  gravship GaussShot, 12 LFS eye attachments. `EcheveriaA` was refused (the owner sent that picture back for redo) and
  keeps its old path. Gap allowlist shrunk by 9.
- Alpha Biomes port (helper): 12 Rot plants, Forge terrains/plants/ash weathers, Miasma mud and three diseases, Sump
  and Cathedral terrains, Abyss sands, all as `RM_` defs with stand-in art (`71700b8b2`, `a6001c556`, `cfc9d28f9`,
  `03f9dcf36`, `283f8eb60`, `450f49208`, `bf9bf04f5`, `0ddbfb87e`).
- `e5c1f01e3` (helper): `RM_Garsulix` ported from VGE's Alpha Animals compat def, with the owner's label and tolerances.
- `20f2c5c98`: the 20 FloodedCanyon-stub PNGs (16 owner-kept) moved into `src/RimMandrake/CrackedLands` at the same
  paths; the stub and its compose entry `CrackedLandsKeptArt` deleted, on the owner's "No more art blockers" words.
- Bulk acceptance of waiting renders: see `TEXREGEN_STANDINS_INSTALL_RENDERS_WAITING`'s ledger note.

### 3.2 Retiring the mods

Retired (registered in `infrastructure/state/facts/retired_mods.json`): **Star Wars Animal Collection**
(`mlie.starwarsanimalcollection`), **Alpha Animals** (`sarg.alphaanimals`), **Alpha Animals Patch for Outposts**
(`daria40k.alphaanimalspatchoutposts`), **Alpha Biomes** (`sarg.alphabiomes`).

- `05c6ee9b2`: their rows left 18 About.xml files (RustCathedral and TheSump had hard Alpha Biomes dependencies); AA
  leathers now `RM_MediumChitin`/`RM_BlackChitin`; RM_Zrrik's vampiric worker is vanilla stab (heal owed); the 11 frozen
  twins' `AlphaBiomes.BiomeWorker_*` point at the RM_ counterpart's worker (worldgen-only field).
- `4bb89a74d`: 9 dead top-level FindMod blocks deleted.
- `8a960e9d6`, `8e001a5ba`: `modset_builder` keeps retired donors out of every tier and refuses a closure that drags
  one back. `infrastructure/state/modlists/ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml` (544 mods = FULL.LATEST
  minus the four) and `infrastructure/state/cherrypicker/CherryPicker.LIVE.CANDIDATE_DONORS_RETIRED_2026-10-18.xml` sit
  beside the originals. The live `ModsConfig.xml` and live Cherry Picker config are unchanged.
- The deployed composed Biomes About still hard-depends on Alpha Biomes until the next compose deploy; the compose
  dry run's About now lists no donor.
- Save: `Saves/CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18.rws` was written by
  `save_donor_rewrite.py` (6,677 edits: 3,337 renames to ports, 2,656 engine-rebuilt rows dropped; 7 HELD, all the ikee
  `AA_Eyeling` and its body). The canonical save is untouched. Alpha Biomes rows in it are report-only in the tool.

### 3.3 Deliberately NOT retired

Alpha Memes, Alpha Genes, VFE Insectoids 2, Isopoda, Horrors, Biomes! Caverns (already inactive), Cockroach, ReGrowth,
Vanilla Genetics Expanded. Alpha Memes carries 98 ideoligion references in the frozen save; the rest are gameplay
mods whose art is not borrowed by our defs beyond what 3.1 copied. Their guarded rows degrade safely. Owner decision:
`DONOR_TAIL_MODS_DECIDE_STAY_OR_GO`.

### 3.4 Re-measured at the end (HEAD 167558b24)

- texPaths our src XML names: 3,329. OURS_SRC 3,045 · VANILLA 162 (+8 unindexed, +7 retextured) · deployed-only 92 ·
  **DONOR 7 · DONOR_BUNDLE 3 · DONOR_INACTIVE 1 · MISSING 4**. What is left: the 3 vanilla-path bundle rows (Hive,
  Thrumbo) and the aoba `Wall` stuff-appearance path are vanilla in fact; 5 rows are our patches fixing OTHER mods'
  defs (GrimTerra, Isopoda, BMT Caverns dessicated art; they target donor defs, not ours); `EcheveriaA` (owner sent it
  back for redo); FlowWorks' ChunkStone; the gene horn `Bulb`; `RUT_FungalSoil` (`FUNGAL_SOIL_RESCUE_RETIRED_MOD_ART`).
  `texture_gap_lint`: PASS.
- Live references in src/ to the four retired packageIds: 0 in About.xml, 0 FindMod outside FlowWorks, 0 unguarded
  donor defNames (helper sweep). 95 `MayRequire` guards remain in the frozen `RUT_` twins: they drop out silently and
  die at the one-time paint. The rest are tooling strings and historical northstar JSON.
- Bulk acceptance (`bulk_accept_renders.py`, `25b9dc7c6`..`9d355d678`, ledger `167558b24`): 578 renders installed over
  donor, placeholder, stand-in or missing textures (197 needed his words past a keep or rejection), 34 texPaths repointed
  so vanilla art is not overwritten for every def; about 84 of the 176 flagged roster rows now draw our art. Not
  installed: ~92 roster rows / ~1,600 jobs with no single safe destination, 47 destinations whose renders he purged,
  8 owner-kept donor variants inside Random folders.

## 4. What is left, and for whom

| item | what | needs |
|---|---|---|
| `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` | deploy (compose + touched mods), then a donor-off load round on the candidate list: first exception, cross-ref and texture lines on RM_/RSW_/RUT_, spawn the ported species, mapgen TheRot/TheForge/Miasma/Sump/RustCathedral/Cauldron | game (FOUNDRY, L1) |
| canonical save | adopt the donor-free candidate save; the ikee `AA_Eyeling` swap to `RSW_Ikee` (runbook step 6) and the `AB_Mech_Ruined*` buildings / `AB_MagmaticQuagmire` landmarks | owner + game |
| `FLOWWORKS_AB_FINDMOD_DELETE_LAST_HOLDOUT` | `RM_PipeNetAdapters.xml` still names Alpha Biomes; `selftest_retired_mods.py` fails on it | FlowWorks owner |
| `ZRRIK_VAMPIRIC_STAB_REBUILD_OWN_BLOODLUST` | the heal, in our C# | offline |
| `DONOR_TAIL_MODS_DECIDE_STAY_OR_GO` | the eight tail mods | owner card |
| re-review | everything bulk-accepted today is provisional: *"We will re review at a later time."* | owner, later |
| stand-ins | every `StandIn/` picture and every VANILLA row still owes a render of ours | artpipe |
