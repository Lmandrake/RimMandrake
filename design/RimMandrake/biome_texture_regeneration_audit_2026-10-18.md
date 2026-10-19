# Biome texture regeneration audit, 2026-10-18

Owner request, 2026-10-18: *"Ensure the biome textures have been regenerated."* Read-only on art. Measured at git
HEAD 49f734a92 on this clone, against the art-ledger and artpipe state of that minute. Another helper was copying
donor art in as stand-ins and retiring donor mods at the same time, so DONOR counts can move. A biome with zero map
tiles is not a defect and is not counted anywhere here.

## Headline

**Not yet: the biome textures are not all regenerated.**

- **Flora, fauna and fish rosters (919 rows, 27 BiomeDefs with a roster):** 664 are our regenerated, installed art
  (72%) and 1 is script-derived from ours. 85 more are live art with no pipeline record (UNPROVEN: 72 of them stems the
  owner ruled on in a review sheet, 13 with no trace). **125 still draw donor bytes, 30 are geometric placeholders and
  14 have no live art of ours at all** (11 donor-only, 3 nothing).
- **Every art-bearing def of the biome, engine and kit mods (1409 defs, including terrain, buildings, items and icons):**
  791 regenerated (56%), 1 derived, 150 unproven, **162 donor bytes, 61 placeholders, 244 draw a vanilla or donor
  texPath.** 52 of the 68 biome TerrainDefs are among those 244, so terrain is the least-regenerated art we ship.
- **Worst five** by count of defs certainly not ours (donor + placeholder + vanilla/donor texPath): Terminal Biomes 71,
  Fever Wood 42, Weeping Stones 39, Greentide 39, The Rot 32. By share ours: The Rot 23%, Fever Wood 34%, Weeping
  Stones 42%, Greentide 44%, Lantern Deeps 46%.
- **The backlog is mostly install-and-review, not generation.** Of 254 roster rows that are not regenerated, 240 have a
  render of ours somewhere in the artpipe state (143 of those only a render joined by creature name, not bound to this
  graphic); 14 have none, and 8 of those 14 are stems the owner ruled on. Eighteen true no-render gaps were queued.

## Method (evidence named per class)

Instruments: `src/RimMandrake/Utils/art/biome_census.py` (rosters; re-run today into the scratchpad: 919 rows over 34
BiomeDefs, 7 of them rosterless), `src/RimMandrake/Utils/art/texture_regen_audit.py` (new; def view, classification,
evidence), `placeholder_detect.py` (flat, geometric, borrowed), `artledger.Index` (16608 variants, sha lookup),
`artpipe_state.py find` and the artpipe state directory listings (`done`, `failed`, `pending`, `active`, `_artsrc`).

Every picture on disk is hashed (sha256) and looked up in the art ledger. First match wins:

| class | rule |
|---|---|
| PLACEHOLDER | `placeholder_detect`: flat (8 colours or fewer), geometric ellipse or rectangle, or a borrowed vanilla picture |
| DONOR | the exact bytes are a ledger variant of kind `donor` (vanilla or donor-mod extract); donor wins even when the same bytes also carry an artpipe record |
| REGEN | the bytes are an artpipe render, an `art install` result or an `artpipe-collect` |
| DERIVED | bytes made by one of our scripts (mirror, flip, composite) |
| UNPROVEN | in the repo, but the ledger holds no artpipe, install or donor record of those exact bytes. NOT counted as regenerated. Split into: owner sheet decided (the stem appears in a `decisions.json`, so he ruled on it and the live picture is probably his pick installed by older tooling), commit cites install (git log of the texture names install, regen, render, sheet), and no record |
| EXTERNAL | the def's texPath resolves to no file under any `src/` Textures folder: vanilla Core or DLC, or a donor mod's own folder. Counted as borrowed, never ours |

A def is classed by its worst picture. UNMEASURED: defs whose texPath is inherited from a `ParentName` or set in C#;
mask files; the texture a donor mod draws for a donor-only row unless the ledger holds it; and, for UNPROVEN, whether the
bytes are in truth hand-made, rescaled pipeline output (a 2026-10-16 facing rescale re-saved 168 pictures, which can
leave a sha with no artpipe record; RM_Chittik is such a case, installed from `rot_swarmling_v2`) or an unregistered copy.

Instrument checks made before trusting any number:

- `biome_census.py` was **blind to artpipe jobs.** `artpipe_state.py find` changed its heading to `N raw text hit(s)`,
  the parser expected `N hit(s)`, and the census's own probe `_artpipe_jobs_anooba` read 0 (it was 9 on 2026-10-07).
  Fixed with one regex in `biome_census.py`; the re-run probe reads 10. The `stoneback` probe reads 0 and is stale, not
  broken: the stoneback was renamed RM_Bokka (`WildAnimals_LongShade.xml` says so).
- `texture_regen_audit.py` asserts that its evidence instrument sees known-present stems (`korrum`, `giantleaf`) before
  it reports anything; both hit. A search by defName stem alone is not enough: `RM_RawGiantLeaf` finds nothing there,
  yet `giantleaf_v1`, `regen_fw_giantleaf_varb_v1` and `regen_fw_giantleaf_varc_v1` are done renders (the beautiful giant
  leaf the owner remembers). Every "no render anywhere" claim here uses a normalised substring over all state directories
  plus the ledger, and stems under 4 characters are never claimed (Faa, Mee, Laa were left out of the job file for that).

## Roster view, per biome (flora, fauna, fish; census rows)

| biome (BiomeDef) | roster rows | regenerated (ours) | derived | unproven: owner sheet decided | unproven: no record | donor bytes | placeholder | no live art | % ours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Long Shade | 67 | 45 | 0 | 2 | 1 | 19 | 0 | 0 | 67% |
| Stillsand | 30 | 26 | 0 | 2 | 0 | 2 | 0 | 0 | 86% |
| Blue Desert | 20 | 16 | 0 | 4 | 0 | 0 | 0 | 0 | 80% |
| Abyss | 26 | 24 | 0 | 2 | 0 | 0 | 0 | 0 | 92% |
| Cauldron | 38 | 31 | 0 | 3 | 0 | 4 | 0 | 0 | 81% |
| Contagion | 36 | 35 | 0 | 0 | 0 | 1 | 0 | 0 | 97% |
| Fever Wood | 42 | 19 | 0 | 4 | 1 | 4 | 14 | 0 | 45% |
| Cracked Lands (RM_FloodedCanyon) | 25 | 14 | 0 | 3 | 0 | 6 | 0 | 2 | 56% |
| Gelatinous Slime | 15 | 12 | 0 | 1 | 0 | 2 | 0 | 0 | 80% |
| Greentide | 66 | 46 | 0 | 4 | 2 | 14 | 0 | 0 | 69% |
| Grey Sea | 31 | 12 | 0 | 2 | 0 | 17 | 0 | 0 | 38% |
| Lantern Deeps | 23 | 22 | 0 | 1 | 0 | 0 | 0 | 0 | 95% |
| Leaning Scrub | 88 | 60 | 0 | 4 | 1 | 23 | 0 | 0 | 68% |
| Miasma | 62 | 36 | 0 | 16 | 3 | 7 | 0 | 0 | 58% |
| Nightside Ice | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 100% |
| Pyrelands | 18 | 12 | 0 | 5 | 1 | 0 | 0 | 0 | 66% |
| Rust Cathedral | 5 | 3 | 0 | 2 | 0 | 0 | 0 | 0 | 60% |
| The Chill | 29 | 25 | 0 | 0 | 0 | 1 | 3 | 0 | 86% |
| The Forge | 24 | 11 | 0 | 1 | 0 | 7 | 0 | 5 | 45% |
| The Rot | 56 | 43 | 0 | 2 | 1 | 10 | 0 | 0 | 76% |
| The Scald | 27 | 19 | 0 | 1 | 0 | 0 | 7 | 0 | 70% |
| The Sump | 20 | 19 | 0 | 1 | 0 | 0 | 0 | 0 | 95% |
| Twilight Sea | 42 | 33 | 1 | 4 | 2 | 1 | 1 | 0 | 80% |
| Warscar | 18 | 13 | 0 | 5 | 0 | 0 | 0 | 0 | 72% |
| Wasteland | 33 | 26 | 0 | 3 | 1 | 0 | 0 | 3 | 78% |
| Webwork | 24 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 100% |
| Weeping Stones | 50 | 34 | 0 | 0 | 0 | 7 | 5 | 4 | 68% |
| **all** | **919** | **664** | **1** | **72** | **13** | **125** | **30** | **14** | **72%** |

"Unproven, sheet decided" is mostly art the owner picked on a review sheet; "no record" needs adjudication. The seabed
floors and RM_ChillCrater have no roster rows. Roster rows include the RSW_ and RUT_ ports a biome casts, so this view
covers the twins' biome-specific animals and plants.

## Def view, per mod (every def with a texture path: terrain, buildings, items, icons, creatures, plants)

| mod folder (compose key) | art-bearing defs | regenerated (ours) | derived | unproven: sheet decided | unproven: commit cites install | unproven: no record | donor bytes | placeholder | vanilla/donor texPath (external) | unresolved (ours-named) | % ours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CreatureBehaviors (engine) | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 50% |
| ExplosiveGrowth (engine) | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 33% |
| EnvironmentalHazards (engine) | 8 | 5 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 62% |
| Abyss (biome) | 45 | 30 | 0 | 4 | 0 | 2 | 7 | 0 | 2 | 0 | 66% |
| BlueDesert (biome) | 32 | 23 | 0 | 0 | 0 | 0 | 7 | 0 | 2 | 0 | 71% |
| Cauldron (biome) | 46 | 35 | 0 | 1 | 0 | 0 | 1 | 0 | 9 | 0 | 76% |
| Contagion (biome) | 60 | 44 | 0 | 3 | 0 | 2 | 0 | 0 | 10 | 1 | 73% |
| FeverWood (biome) | 69 | 24 | 0 | 1 | 0 | 2 | 0 | 33 | 9 | 0 | 34% |
| CrackedLands (biome) | 31 | 19 | 0 | 0 | 0 | 0 | 4 | 1 | 7 | 0 | 61% |
| GelatinousSlime (biome) | 35 | 19 | 0 | 0 | 0 | 0 | 4 | 0 | 12 | 0 | 54% |
| Greentide (biome) | 78 | 35 | 0 | 1 | 0 | 3 | 17 | 0 | 22 | 0 | 44% |
| LanternDeeps (biome) | 56 | 26 | 0 | 5 | 0 | 9 | 13 | 0 | 3 | 0 | 46% |
| LeaningScrub (biome) | 58 | 33 | 0 | 1 | 2 | 0 | 8 | 0 | 14 | 0 | 56% |
| LongShade (biome) | 51 | 32 | 0 | 2 | 0 | 2 | 12 | 0 | 3 | 0 | 62% |
| Miasma (biome) | 54 | 35 | 0 | 4 | 2 | 0 | 5 | 0 | 8 | 0 | 64% |
| NightsideIce (biome) | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 100% |
| Pyrelands (biome) | 28 | 15 | 1 | 2 | 0 | 1 | 1 | 0 | 8 | 0 | 57% |
| RustCathedral (biome) | 16 | 5 | 0 | 1 | 0 | 3 | 0 | 0 | 7 | 0 | 31% |
| Stillsand (biome) | 72 | 57 | 0 | 1 | 0 | 1 | 10 | 1 | 2 | 0 | 79% |
| TerminalBiomes (biome) | 224 | 133 | 0 | 15 | 3 | 2 | 25 | 8 | 38 | 0 | 59% |
| TheForge (biome) | 23 | 13 | 0 | 0 | 0 | 0 | 3 | 0 | 6 | 1 | 56% |
| TheRot (biome) | 116 | 27 | 0 | 22 | 9 | 26 | 28 | 0 | 4 | 0 | 23% |
| TheSump (biome) | 46 | 28 | 0 | 0 | 0 | 1 | 0 | 8 | 9 | 0 | 60% |
| Warscar (biome) | 62 | 47 | 0 | 2 | 0 | 2 | 2 | 0 | 9 | 0 | 75% |
| Wasteland (biome) | 49 | 35 | 0 | 0 | 5 | 5 | 1 | 0 | 3 | 0 | 71% |
| Webwork (biome) | 42 | 28 | 0 | 0 | 0 | 2 | 0 | 9 | 3 | 0 | 66% |
| WeepingStones (biome) | 69 | 29 | 0 | 1 | 0 | 0 | 10 | 0 | 29 | 0 | 42% |
| DivingInteraction (kit) | 25 | 4 | 0 | 0 | 0 | 0 | 2 | 0 | 19 | 0 | 16% |
| **all biome/engine/kit mods** | **1409** | **791** | **1** | **66** | **21** | **63** | **162** | **61** | **242** | **2** | **56%** |
| TWIN:RimUtinni/UtinniPatches (twin, not biome-attributed) | 174 | 64 | 0 | 4 | 2 | 17 | 1 | 1 | 85 | 0 | 36% |
| TWIN:RimStarWars/SWBestiary (twin, not biome-attributed) | 632 | 37 | 1 | 47 | 7 | 124 | 394 | 2 | 20 | 0 | 6% |

The two twin rows are not attributed to a biome (SWBestiary holds the Star Wars bestiary for the whole planet): 394 of
its 632 defs are donor bytes. Whatever a biome roster casts from it is already counted in the roster view.

**Terrain.** Of 68 TerrainDefs in the biome mods, 8 are regenerated, 8 unproven and **52 point at vanilla
`Terrain/Surfaces` textures** (Terminal Biomes 17, Pyrelands 5, Gelatinous Slime 5, Greentide 4, The Forge 4, The Sump 4,
Fever Wood 3, others fewer). Two ours-named pawn-render paths do not resolve (`RM_OcularJelly_TentacleA`,
`RM_ColossalAerofleet_FeelerA`): UNMEASURED, probably a folder-per-frame graphic.

## Ranked biggest gaps

1. **Terminal Biomes** (224 defs, 71 not ours): 17 vanilla terrains, 25 donor-byte defs, 8 placeholders, 11 unproven
   PawnKinds. Grey Sea alone has 17 donor roster rows (Brinecomb, BrineCrown, Hoarstock, Masonmat...).
2. **Fever Wood** (42): 33 geometric placeholders (14 roster plants: Drommath, Ammeth, Cistrel...; 19 items and Sekkulaath
   buildings), 9 vanilla paths.
3. **Weeping Stones** (39): 29 vanilla or donor texPaths, 10 donor roster rows, 5 placeholders.
4. **Greentide** (39): 17 donor-byte defs (14 roster rows), 22 vanilla texPaths (4 of them terrain).
5. **The Rot** (32 not ours, 23% ours): 28 donor-byte defs and 57 unproven, 22 of those owner-sheet-decided; the
   `*Marsh` plant variants draw donor RotSporeKit textures.
6. **Leaning Scrub and Long Shade**: 23 and 19 donor roster rows (Star Wars fauna ports: Bantha, Eopie, Gorg, Nerf, Worrt...).
7. **Lantern Deeps**: 13 donor, 9 unproven with no record (the lanternstone walls), 5 sheet-decided.
8. **The Forge** 12 roster rows donor or without live art; **The Scald** 7 placeholders; **The Sump** 8 placeholder items;
   **Webwork** 9 placeholder items; **Blue Desert** 7 donor-byte defs.
9. **Deep Diving kit**: 19 of 25 defs external (16% ours).

Roster rows certainly not ours, by biome (every one has a render of ours waiting in the artpipe state except
RM_UltrissPad and AB_ArbuscularMycorrhiza):

- **RM_LongShade**: donor (19): RSW_Bantha, RSW_Clodhopper, RSW_Eopie, RSW_Falumpaset, RSW_FrilledGorg, RSW_Gorg, RSW_Hrumph, RSW_IridonianReek, RSW_Jakobeast, RSW_LongtailGorg, RSW_Nerf, RSW_Runyip, RSW_Sketto, RSW_Worrt, RM_Shadespire, RM_Venomvine, RM_Vorrel, RSW_Plant_Chakroot_Wild, RSW_Plant_HubbaGourd_Wild
- **RM_Stillsand**: donor (2): RSW_Kreetle, RM_UltrissPad
- **RM_Cauldron**: donor (4): RSW_Neebray, RSW_Silooth, Visceral, RM_TwistingThornwood
- **RM_Contagion**: donor (1): RM_RustPuff
- **RM_FeverWood**: placeholder (14): RM_Drommath, RM_Ammeth, RM_Cistrel, RM_Corvath, RM_Maulith, RM_Nubrith, RM_Plennith, RM_Seepril, RM_Skimmel, RM_Sodderel, RM_Tullick, RM_Varnoth, RM_Verrow, RM_Wanlith; donor (4): RSW_Convor, RSW_Fambaa, RSW_LongtailGorg, RSW_Plant_Chakroot_Wild
- **RM_FloodedCanyon**: no live donor only (1): RM_Muttavaq; no live art (1): RM_Tarruq; donor (6): RSW_CanCell, RSW_Convor, RSW_Gornt, RSW_Woolamander, RM_CrackedThornwood, RM_Veqma
- **RM_GelatinousSlime**: donor (2): RM_Plant_Bellows, RM_Plant_Readerbloom
- **RM_Greentide**: donor (14): RSW_Beldon, RSW_Clodhopper, RSW_Convor, RSW_Falumpaset, RSW_Fambaa, RSW_Klorslug, RSW_Mott, RSW_PekoPeko, RSW_ShiroTrap, RSW_Worrt, RM_Gorbeleth, RM_Greatbole, RM_Mirrelbole, RM_YearningFruit
- **RM_GreySea**: donor (17): RM_Brinecomb, RM_BrineCrown, RM_CruciblePod, RM_CubicSculpture, RM_GlassVeilKelp, RM_Hoarstock, RM_Masonmat, RM_Milkwell, RM_MosaicFanPalm, RM_Mournweft, RM_Murkblush, RM_Neverset, RM_SaltBladeGrey, RM_SaltBladeTwilight, RM_SaltChimneyVine, RM_Saltswoon, RM_SpherePlant
- **RM_LeaningScrub**: donor (23): RSW_Bantha, RSW_Convor, RSW_Eopie, RSW_FrilledGorg, RSW_Gorg, RSW_Igitz, RSW_Kreetle, RSW_Kybuck, RSW_LongtailGorg, RSW_Mudhorn, RSW_Porg, RSW_Sketto, RSW_Worrt, Plant_Brambles, RG_Plant_AridGrass, RG_Plant_CreepStern, RG_Plant_CrimsonCushion, RG_Plant_Dervish, RM_Fuzz, RM_Grellbush, RM_Grellspine, RM_Tanglefuzz, RM_Whipfuzz
- **RM_Miasma**: donor (7): RSW_Blixus, RSW_Bogwing, RSW_MarshHaunt, RSW_Runyip, RM_Brelloch, RM_Immarel, RM_Quennath
- **RM_TheChill**: placeholder (3): RM_FessuCatch, RM_OdduCatch, RM_TarnnCatch; donor (1): RM_Thalquith
- **RM_TheForge**: no live donor only (5): LavaSnail, AB_TinkleGrass, IronScruff_PrimordialGrass, IronScruff_PrimordialTallGrass, Plant_MagmaCactus; donor (7): RSW_Beldon, RSW_LavaFlea, RSW_Tibidee, IronScruff_Bindweed, Plant_Fireweed, RM_CinderCrust, RM_FireLavender
- **RM_TheRot**: donor (10): RSW_ShiroTrap, RSW_Snoruuk, AB_ArbuscularMycorrhiza, AB_Bryolux, AB_DribblingCap, AB_GiantAgarilux, RM_EuphoricCrown, RM_FlakespireFungus, RM_Skulltop, RM_TollukCap
- **RM_TheScald**: placeholder (7): RM_Foamgorse, RM_Kettlewick, RM_Seepcandle, RM_Simmerlace, RM_Threshreed, RM_Thurlsponge, RM_Vekkfan
- **RM_TwilightSea**: donor (1): RM_HoolimbrePlant; placeholder (1): RM_NoothelmPlant
- **RM_Wasteland**: no live donor only (3): Plant_GrayGrass, Plant_Toxipotato, Plant_TreePolux
- **RM_WeepingStones**: placeholder (5): RM_Huldu, RM_Loomu, RM_Murrin, RM_Skarrin, RM_Vizhik; no live donor only (2): RM_Kirruk, RM_Vhakk; no live art (2): RM_Ssurr, RM_Vellak; donor (7): RSW_Bantha, RSW_Eopie, Plant_Ambrosia, RM_Dewblade, RM_Dewgourd, RM_Dripfringe, RM_Salvecomb

## What was queued

`design/RimMandrake/biome_texture_regen_jobs_2026-10-18.json`: 18 jobs filed into the artpipe pending queue with
`fill_queue.py` (generation belongs to the daemon; nothing was generated here). They are the gaps with no render of ours
anywhere in the artpipe state: Vashuu catch item (it wears the mee's old picture, commit f3a7513c5), Ultriss Pad,
Sekkulaath cream, bloom tentacle and prison tank, Elder sealed relic, cargo float, raw salt, glowtank (the cube cage
shares its texPath), weak tar solvent, gaslight lamp, tar vault, Skerrel gall, gloomcast hide and meat, the shared scaled
egg (six defs), Vaulisk lure organ, hull salt crust. Builder: `src/RimMandrake/Utils/art/texture_regen_jobs.py`.

Deliberately NOT queued: every other DONOR or PLACEHOLDER row (a finished render already sits in the state; see
`TEXREGEN_STANDINS_INSTALL_RENDERS_WAITING`); the owner-sheet-decided unproven rows (regenerating would overwrite his
picks); AB_ArbuscularMycorrhiza (a donor roster name with no def of ours); Faa, Mee, Laa (state holds done and failed
renders); Chittik (installed from `rot_swarmling_v2`) and Frethik (a renamed sheet pick). `RM_RawGiantLeaf` is unproven,
not missing: its renders exist.

## Ledger items filed

- `TEXREGEN_GAPS_REDRAW_EIGHTEEN_QUEUED` (FOUNDRY): collect the 18 renders when the daemon finishes, one sheet per biome.
- `TEXREGEN_STANDINS_INSTALL_RENDERS_WAITING` (BENCH, needs owner): 125 donor roster rows plus 30 placeholders whose
  finished renders were never installed.
- `TEXREGEN_UNPROVEN_ASK_THE_SHEETS` (FOUNDRY): the 13 no-record roster rows and 63 no-record defs.
- `TEXREGEN_SWBESTIARY_DECIDE_NO_ROSTER_OWNS_IT` (BENCH, needs owner): 394 donor-byte SWBestiary defs in no biome roster.

## Re-running

`python3 src/RimMandrake/Utils/art/biome_census.py --no-wookiee --out <dir>`, then
`python3 src/RimMandrake/Utils/art/texture_regen_audit.py --census <dir>/census.json --out <audit.json>`. About 3 minutes
each; run both in the background.
