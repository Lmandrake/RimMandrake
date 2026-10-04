# Desert-family art version census, 2026-10-04 (ART_VERSION_WRANGLING_1)

Rows: **109** (92 creatures, 17 plants) from `Transient/desert_art_review_2026-10-03.html`. Variants found: **718** (repo-current 246, donor-bundle 207, artpipe 161, donor-loose 48, git-history 39, canon-library 17). One row per variant in `Transient/art_census_desert_2026-10-04.csv`; every variant side by side in `Transient/art_census_desert_2026-10-04/index.html` (thumbnails 256px). Builder: `Transient/art_census_desert_build_2026-10-04.py` + `Transient/art_census_desert_report_2026-10-04.py`.

## Headline

1. **The 2026-10-03 sheet's "current art" column was the CORPSE texture for 65 of 109 rows.** Its builder took the *last* `texPath` in the def, which is `dessicatedBodyGraphicData` (`..._Dessicated`) - the skeleton. That is the "crude skeletons" the owner saw. For **12** of those rows the live art is actually our own regenerated/approved art (an ArtOverride mod or a wired artpipe render), which the sheet never showed.
2. **23 rows already have own (non-donor) art live in the repo.** Live-art kind across all rows: donor copy 51, no live texture resolved 30, own 23, unknown 5 (donor copy = live PNG hash-matches the donor sprite, mostly mlie SWAC ported by MLIE_FAUNA_ABSORPTION_1; unknown = no donor art found to compare).
3. **14 rows where the owner previously KEPT art (earlier review sheet) and the 2026-10-03 "Keep render" would now REPLACE that live own art** with the uninformed desert_swaca/desertportb render: anooba, bolotaur, bouldermit, eyeling, iridonian reek, Jamel, kreetle, mammoth worm, ronto, sand prowler, terramorph, whisperbird, wildpod, zeer. Do not wire these without a side-by-side.
4. **20 rows where owner-kept art exists AND the live path was overwritten by later commits** (timelines below) - this is "older art I liked being replaced".
5. **The desert renders were not canon-informed.** Every `desert_swaca_*` / `desertportb_*` job (DESERT_FAMILY_PORT_EXECUTION_1, 2026-09-20) has `reference: null`, a generic prompt (Wookieepedia one-liner + "painterly game-art style") and style note "our own art (not the donor mod's)" - no canon-library brief, no `## Must show`, no biome context. Compare PYRELANDS_CREATURE_RERENDER_1 / ART_REGEN_WAVE4 / canon_regen jobs, which cite the canon library or the owner's identity rulings.
6. **Repo vs deployed:** 0 rows have a deployed texture that differs from the repo or has no repo twin; every matched texture in the game Mods folder is byte-identical to its repo file (MD5). Rows whose def texPaths differ between the repo def and the deployed def: none.

Method caveats: "live" = file at the def's texPath in the latest-loading active mod (ModsConfig order); variants matched by name tokens of donor name, ported defName and render job, so a renamed set under an unrelated name can be missed. `likely_from_job` is a 16x16 average-hash nearest neighbour (<=20/256), a hint not provenance. "owner ruling" lists every decisions file ever committed (incl. deleted) whose key matches; prefill-state files are agent guesses, not his. Droids (7), Rat and three vanilla-art plants have no variants: Outer Rim droid art is bundled under names this pass did not resolve.

## Owner-kept art later overwritten, or about to be (worst first)

- **anooba [Anooba]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner keep in `art_review_2026-09-12` key `anooba_v1_east`
  - owner keep in `art_review_2026-09-12` key `anooba_v1_north`
  - owner keep in `art_review_2026-09-12` key `anooba_v1_south`
  - owner better in `keyline_ab_2026-09-13` key `anooba_v1_east`
  - owner good in `legibility_final_review_2026-09-13` key `anooba_v1_east`
  - owner good in `legibility_final_review_2026-09-13` key `anooba_v1_north`
  - owner good in `legibility_final_review_2026-09-13` key `anooba_v1_south`
  - owner adopt-b in `toyfig_pilot_2026-09-13` key `anooba`
  - owner keep in `creature_art_decisions.json` key `Anooba`
  - owner approve in `creature_art_register` key `c:Anooba`
  - 2026-09-12 git-history (path deleted): `swanimals/Anooba/Anooba_f_south.png` <- e62125946 MLIE_FAUNA_ABSORPTION_1: port Anooba, Beldon, Bolotaur (89 -> 86 remaining) [MLIE_FAUNA_ABSORPTION_1]
  - 2026-09-12 git-history (path deleted): `swanimals/Anooba/Anooba_m_south.png` <- e62125946 MLIE_FAUNA_ABSORPTION_1: port Anooba, Beldon, Bolotaur (89 -> 86 remaining) [MLIE_FAUNA_ABSORPTION_1]
  - 2026-09-13 git-history (overwritten): `swanimals/Anooba/Anooba_f_south.png` <- 645b93f2e ART_PAINTERLY_RESTORATION_1: revert Anooba/Orray/FireHawk/FurnaceBeast to painterly v1 (owner ordered Pyrelands-wide painterly reg
  - 2026-09-13 git-history (overwritten): `swanimals/Anooba/Anooba_f_south.png` <- dde341c12 Canon-5 lawset renders installed (Anooba/Orray/Zeer/Gizka/Dalgo), Pyrelands flora art in; FULL.LATEST +42 override mods (631)
  - 2026-09-17 git-history (overwritten): `swanimals/Anooba/Anooba_f_south.png` <- 9e7e773a0 Wire approved Pyrelands creature render wave into art-override mods
  - 2026-09-17 git-history (overwritten): `swanimals/Anooba/Anooba_m_south.png` <- 9e7e773a0 Wire approved Pyrelands creature render wave into art-override mods
  - LIVE now: `src/RimStarWars/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_f_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
  - LIVE now: `src/RimStarWars/AnoobaArtOverride/Textures/swanimals/Anooba/Anooba_m_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
  - 2026-10-03 sheet: **keep**
- **zeer [Zeer]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner keep in `creature_art_decisions.json` key `Zeer`
  - owner approve in `creature_art_register` key `c:Zeer`
  - 2026-09-13 git-history (overwritten): `swanimals/Zeer/Zeer_south.png` <- dde341c12 Canon-5 lawset renders installed (Anooba/Orray/Zeer/Gizka/Dalgo), Pyrelands flora art in; FULL.LATEST +42 override mods (631)
  - 2026-09-14 git-history (overwritten): `swanimals/Zeer/Zeer_south.png` <- 751ac722d ART_PAINTERLY_RESTORATION_1: Zeer + Dalgo full painterly sets, rear-view norths, canon-library-cited [ART_PAINTERLY_RESTORATION_1]
  - 2026-09-17 git-history (overwritten): `swanimals/Zeer/Zeer_south.png` <- 9e7e773a0 Wire approved Pyrelands creature render wave into art-override mods
  - LIVE now: `src/RimStarWars/ZeerArtOverride/Textures/swanimals/Zeer/Zeer_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
  - 2026-10-03 sheet: **keep**
- **nuna [Nuna]**
  - owner keep in `creature_art_decisions.json` key `Nuna`
  - owner approve in `creature_art_register` key `c:Nuna`
  - 2026-09-14 git-history (overwritten): `swanimals/Nuna/Nuna_f_south.png` <- 3a255e2bb ART_PAINTERLY_RESTORATION_1: Razorjack full set + Nuna (m N/S interim-copied from f) + Gizka easts, painterly via Codex before wee
  - 2026-09-14 git-history (overwritten): `swanimals/Nuna/Nuna_f_south.png` <- 7c9f2c7b7 Revert "ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library en
  - 2026-09-14 git-history (overwritten): `swanimals/Nuna/Nuna_f_south.png` <- f209d892c ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library entry; Nun
  - 2026-09-17 git-history (overwritten): `swanimals/Nuna/Nuna_f_south.png` <- 9e7e773a0 Wire approved Pyrelands creature render wave into art-override mods
  - 2026-09-17 git-history (overwritten): `swanimals/Nuna/Nuna_m_south.png` <- 9e7e773a0 Wire approved Pyrelands creature render wave into art-override mods
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/Nuna/Nuna_f_south.png` (2026-09-09, d75b06098 MLIE_FAUNA_ABSORPTION_1: Wave B (Dewback/Vulptex/Porg/Nuna/Wampa/Acklay), Wave A) [donor copy (dist 0)]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/Nuna/Nuna_m_south.png` (2026-09-09, d75b06098 MLIE_FAUNA_ABSORPTION_1: Wave B (Dewback/Vulptex/Porg/Nuna/Wampa/Acklay), Wave A) [donor copy (dist 0)]
  - 2026-10-03 sheet: **current** - "We already had a good looking Nuna"
- **wildpod [AA_Wildpod]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner right in `bulk_art_misroute_2026-09-19` key `Things/Pawn/Animal/AA_Wildpod/AA_Wildpod`
  - owner keep in `rot_art_landed_20260920` key `AA_Wildpod`
  - owner approve in `creature_art_register` key `c:AA_Wildpod`
  - 2026-09-13 git-history (overwritten): `Things/Pawn/Animal/AA_Wildpod/AA_Wildpod_south.png` <- cea007c3a Art-review platform: install every gate-passed render awaiting verdict (95 stems)
  - 2026-09-20 git-history (path deleted): `RotSpecies/Wildpod/Wildpod_south.png` <- 06966e55d Land the Rot artpipe backlog: 22 wave-1 + 58 wave-2 renders wired
  - LIVE now: `src/RimUtinni/WildpodArtOverride/Textures/Things/Pawn/Animal/AA_Wildpod/AA_Wildpod_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
  - 2026-10-03 sheet: **keep** - "Tint different shades for fun"
- **bolotaur [Bolotaur]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner approve in `creature_art_register` key `c:Bolotaur`
  - 2026-09-12 git-history (overwritten): `swanimals/Bolotaur/Bolotaur_south.png` <- e62125946 MLIE_FAUNA_ABSORPTION_1: port Anooba, Beldon, Bolotaur (89 -> 86 remaining) [MLIE_FAUNA_ABSORPTION_1]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/Bolotaur/Bolotaur_south.png` (2026-09-24, e19716d5b OFFBIOME_SHEET_RERENDERS_1: wire v3 bolotaur + fulgurite art, deployed | deploye) [own/regenerated]
  - 2026-10-03 sheet: **keep**
- **gizka [Gizka]**
  - owner keep in `creature_art_decisions.json` key `Gizka`
  - owner approve in `creature_art_register` key `c:Gizka`
  - 2026-09-14 git-history (overwritten): `swanimals/Gizka/Gizka_south.png` <- 7c9f2c7b7 Revert "ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library en
  - 2026-09-14 git-history (overwritten): `swanimals/Gizka/Gizka_south.png` <- f209d892c ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library entry; Nun
  - 2026-09-17 git-history (overwritten): `swanimals/Gizka/Gizka_south.png` <- bd9a1b8ee Gizka: dino_v5 is the locked set (owner, 2026-09-17)
  - 2026-09-17 git-history (overwritten): `swanimals/Gizka/Gizka_south.png` <- de46f98c1 Gizka biped + Iriaz v2 wired (owner rulings 2026-09-17)
  - LIVE now: `src/RimStarWars/GizkaArtOverride/Textures/swanimals/Gizka/Gizka_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
  - 2026-10-03 sheet: **redo** - "We had a good Gizka.... it didn't need to be redone, and it isn't a frog."
- **iriaz [Iriaz]**
  - owner keep in `creature_art_decisions.json` key `Iriaz`
  - owner approve in `creature_art_register` key `c:Iriaz`
  - 2026-09-14 git-history (overwritten): `swanimals/Iriaz/Iriaz_south.png` <- 7c9f2c7b7 Revert "ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library en
  - 2026-09-14 git-history (overwritten): `swanimals/Iriaz/Iriaz_south.png` <- f209d892c ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library entry; Nun
  - 2026-09-17 git-history (overwritten): `swanimals/Iriaz/Iriaz_south.png` <- de46f98c1 Gizka biped + Iriaz v2 wired (owner rulings 2026-09-17)
  - 2026-09-18 git-history (overwritten): `swanimals/Iriaz/Iriaz_south.png` <- af9a1f94b ZEER_EAST_TOP_CLIP_1: three clipped facings repaired inside their own canvases [ZEER_EAST_TOP_CLIP_1]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/Iriaz/Iriaz_south.png` (2026-09-12, e2b1262d3 MLIE_FAUNA_ABSORPTION_1: defName-drift sweep + Iriaz/Mudhorn ported | deployed i) [donor copy (dist 0)]
  - 2026-10-03 sheet: **keep**
- **Jamel [Jamel]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner right in `bulk_art_misroute_2026-09-19` key `swanimals/Jamel/Jamel`
  - owner approve in `creature_art_register` key `c:Jamel`
  - 2026-09-17 git-history (overwritten): `swanimals/Jamel/Jamel_south.png` <- bab45edca MLIE_FAUNA_ABSORPTION_1 Pass 11: port IridonianReek, Jakobeast, Jamel, Jimvu (60 -> 56 remaining) [MLIE_FAUNA_ABSORPTION_1]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/Jamel/Jamel_south.png` (2026-09-18, 3f891c5c7 CAVERNS_ARTOVERRIDE_REHOME_1: ten ArtOverride mods rehomed into SWBestiary and r) [own/regenerated]
  - 2026-10-03 sheet: **keep**
- **kreetle [Kreetle]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner keep in `art_review_2026-09-12` key `kreetle_v1_east`
  - owner keep in `art_review_2026-09-12` key `kreetle_v1_north`
  - owner keep in `art_review_2026-09-12` key `kreetle_v1_south`
  - owner keep in `creature_art_decisions.json` key `Kreetle`
  - owner approve in `creature_art_register` key `c:Kreetle`
  - 2026-09-11 git-history (overwritten): `swanimals/Kreetle/Kreetle_south.png` <- 1dfd4b36f ART_REGEN_WAVE1_WIRE_IN_1: wire 5 SW-canon creature art redos (Kreetle, Horax, Fambaa, Dragonsnake, Zakkeg) [ART_REGEN_WAVE1_WIRE_
  - LIVE now: `src/RimStarWars/KreetleArtOverride/Textures/swanimals/Kreetle/Kreetle_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [donor copy (dist 0), own (ArtOverride mod)]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/Kreetle/Kreetle_j_south.png` (2026-09-17, 10013ce07 MLIE_FAUNA_ABSORPTION_1 Pass 15: port Kreetle, Krykna, Kwi (45 -> 42 remaining) ) [donor copy (dist 0), own (ArtOverride mod)]
  - 2026-10-03 sheet: **keep**
- **ronto [Ronto]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner keep in `art_review_2026-09-12` key `ronto_v1_east`
  - owner keep in `art_review_2026-09-12` key `ronto_v1_north`
  - owner keep in `art_review_2026-09-12` key `ronto_v1_south`
  - 2026-09-11 git-history (overwritten): `swanimals/Ronto/Ronto_south.png` <- 9fa637b8e Wire ART_REGEN_WAVE4 art into 7 creatures: Ronto/Anooba/Dewback (SW-canon) + Grithe/Kroffa/Grutt/Puffmite (reimagined) [ART_REGEN_
  - LIVE now: `src/RimStarWars/RontoArtOverride/Textures/swanimals/Ronto/Ronto_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
  - 2026-10-03 sheet: **keep**
- **terramorph [AA_Terramorph]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner keep in `art_review_2026-09-12` key `aa_terramorph_v1_east`
  - owner keep in `art_review_2026-09-12` key `aa_terramorph_v1_south`
  - owner right in `bulk_art_misroute_2026-09-19` key `Things/Pawn/Animal/AA_Terramorph/AA_Terramorph`
  - owner good in `legibility_final_review_2026-09-13` key `aa_terramorph_v1_east`
  - owner good in `legibility_final_review_2026-09-13` key `aa_terramorph_v1_north`
  - owner good in `legibility_final_review_2026-09-13` key `aa_terramorph_v1_north_r2`
  - owner good in `legibility_final_review_2026-09-13` key `aa_terramorph_v1_south`
  - owner adopt-b in `toyfig_pilot_2026-09-13` key `terramorph`
  - owner approve in `creature_art_register` key `c:AA_Terramorph`
  - 2026-09-13 git-history (overwritten): `Things/Pawn/Animal/AA_Terramorph/AA_Terramorph_south.png` <- cea007c3a Art-review platform: install every gate-passed render awaiting verdict (95 stems)
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/RSW_Khorrak/RSW_Khorrak_south.png` (2026-10-03, 2154ef2ea SWBestiary: move 9 DesertPort animal textures to their renamed defNames (all 9 w) [own/regenerated]
  - 2026-10-03 sheet: **keep**
- **whisperbird [Whisperbird]** - WOULD BE REPLACED AGAIN by the 10-03 keep
  - owner keep in `art_review_2026-09-12` key `whisperbird_v1_east`
  - owner keep in `art_review_2026-09-12` key `whisperbird_v1_north`
  - owner keep in `art_review_2026-09-12` key `whisperbird_v1_south`
  - owner right in `bulk_art_misroute_2026-09-19` key `swanimals/Whisperbird/Whisperbird`
  - owner good in `legibility_final_review_2026-09-13` key `whisperbird_v1_east`
  - owner good in `legibility_final_review_2026-09-13` key `whisperbird_v1_south`
  - owner keep in `creature_art_decisions.json` key `Whisperbird`
  - owner approve in `creature_art_register` key `c:Whisperbird`
  - 2026-09-13 git-history (overwritten): `swanimals/Whisperbird/Whisperbird_south.png` <- cea007c3a Art-review platform: install every gate-passed render awaiting verdict (95 stems)
  - LIVE now: `src/RimStarWars/WhisperbirdArtOverride/Textures/swanimals/Whisperbird/Whisperbird_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
  - 2026-10-03 sheet: **keep**
- **landopus [JOE_Landopus]**
  - owner keep in `creature_art_decisions.json` key `JOE_Landopus`
  - 2026-09-11 git-history (overwritten): `Things/Pawn/Animal/landopus/landopus_south.png` <- 5ad48a078 STAT_NORM_WAVE2_RETIRE_1: port Cephaloids/VE Succulents/VAE Waste's Megatardi, verify+retire 6 more [STAT_NORM_WAVE2_RETIRE_1]
  - 2026-09-11 git-history (overwritten): `Things/Pawn/Animal/landopus/swimming_landopus_south.png` <- 5ad48a078 STAT_NORM_WAVE2_RETIRE_1: port Cephaloids/VE Succulents/VAE Waste's Megatardi, verify+retire 6 more [STAT_NORM_WAVE2_RETIRE_1]
  - LIVE now: `src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/landopus/landopus_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [unknown (no donor to compare)]
  - 2026-10-03 sheet: **redo** - "This is just horrible. It should be an octopus with blue rings that drags itself along the ground, not a man creature with loctupus legs. "
- **Grank [Grank]**
  - owner keep in `art_review_2026-09-12` key `grank_v1_east`
  - owner keep in `art_review_2026-09-12` key `grank_v1_north`
  - owner keep in `art_review_2026-09-12` key `grank_v1_south`
  - owner good in `legibility_final_review_2026-09-13` key `grank_v1_east`
  - owner good in `legibility_final_review_2026-09-13` key `grank_v1_north`
  - owner good in `legibility_final_review_2026-09-13` key `grank_v1_south`
  - owner keep in `creature_art_decisions.json` key `Grank`
  - owner approve in `creature_art_register` key `c:Grank`
  - 2026-09-13 git-history (overwritten): `swanimals/Grank/Grank_south.png` <- cea007c3a Art-review platform: install every gate-passed render awaiting verdict (95 stems)
  - LIVE now: `src/RimStarWars/GrankArtOverride/Textures/swanimals/Grank/Grank_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
- **greater krayt dragon [GreaterKraytDragon]**
  - owner keep in `art_review_2026-09-12` key `greaterkraytdragon_v1_east`
  - owner keep in `art_review_2026-09-12` key `greaterkraytdragon_v1_north`
  - owner keep in `art_review_2026-09-12` key `greaterkraytdragon_v1_south`
  - 2026-09-13 git-history (overwritten): `swanimals/GreaterKraytDragon/GreaterKraytDragon_south.png` <- cea007c3a Art-review platform: install every gate-passed render awaiting verdict (95 stems)
  - LIVE now: `src/RimStarWars/GreaterKraytDragonArtOverride/Textures/swanimals/GreaterKraytDragon/GreaterKraytDragon_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
- **horax [Horax]**
  - owner keep in `art_review_2026-09-12` key `horax_v1_east`
  - owner keep in `art_review_2026-09-12` key `horax_v1_north`
  - owner keep in `art_review_2026-09-12` key `horax_v1_south`
  - 2026-09-11 git-history (overwritten): `swanimals/Horax/Horax_south.png` <- 1dfd4b36f ART_REGEN_WAVE1_WIRE_IN_1: wire 5 SW-canon creature art redos (Kreetle, Horax, Fambaa, Dragonsnake, Zakkeg) [ART_REGEN_WAVE1_WIRE_
  - LIVE now: `src/RimStarWars/HoraxArtOverride/Textures/swanimals/Horax/Horax_south.png` (2026-09-20, 1135036ce art: zero the sub-visible export halo across 241 of our facing sprites | deploye) [own (ArtOverride mod)]
- **krayt dragon [KraytDragon]**
  - owner keep in `art_review_2026-09-12` key `greaterkraytdragon_v1_east`
  - owner keep in `art_review_2026-09-12` key `greaterkraytdragon_v1_north`
  - owner keep in `art_review_2026-09-12` key `greaterkraytdragon_v1_south`
  - owner keep in `creature_art_decisions.json` key `KraytDragon`
  - owner approve in `creature_art_register` key `c:KraytDragon`
  - 2026-09-13 git-history (overwritten): `swanimals/GreaterKraytDragon/GreaterKraytDragon_south.png` <- cea007c3a Art-review platform: install every gate-passed render awaiting verdict (95 stems)
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/KraytDragon/KraytDragon_f_south.png` (2026-09-17, 74e9d4953 MLIE_FAUNA_ABSORPTION_1 Pass 14: port KraytDragon, KowakianMonkeyLizard, Klorslu) [donor copy (dist 0)]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/KraytDragon/KraytDragon_j_south.png` (2026-09-17, 74e9d4953 MLIE_FAUNA_ABSORPTION_1 Pass 14: port KraytDragon, KowakianMonkeyLizard, Klorslu) [donor copy (dist 0)]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/KraytDragon/KraytDragon_m_south.png` (2026-09-17, 74e9d4953 MLIE_FAUNA_ABSORPTION_1 Pass 14: port KraytDragon, KowakianMonkeyLizard, Klorslu) [donor copy (dist 0)]
  - 2026-10-03 sheet: **redo** - "unify faces"
- **moss beetle [RSW_MossBeetle]**
  - owner approve in `creature_art_register` key `c:BMT_MossBeetle`
  - 2026-09-11 git-history (overwritten): `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/MossBeetle/MossGrub_south.png` <- a72757b9d BMT_FAUNA_ABSORPTION_1: port 68 biomesteam.* creatures to RSW_/SWBestiary tier [BMT_FAUNA_ABSORPTION_1]
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/MossBeetle/MossBeetle_south.png` (2026-09-11, a72757b9d BMT_FAUNA_ABSORPTION_1: port 68 biomesteam.* creatures to RSW_/SWBestiary tier |) [unknown (no donor to compare)]
  - 2026-10-03 sheet: **keep**
- **mynock [Mynock]**
  - owner keep in `creature_art_decisions.json` key `Mynock`
  - owner approve in `creature_art_register` key `c:Mynock`
  - 2026-09-08 git-history (overwritten): `swanimals/Mynock/Mynock_south.png` <- a085bf59c Mynock custom art (south/east/north): hideous wet practical-effects redesign
  - LIVE now: `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock.png` (2026-09-11, 75115178c RSW_Mynock: reuse the existing regenerated Mynock art (IKEE_MYNOCK_ART_REGEN_1) ) [donor copy (dist 8)]
  - 2026-10-03 sheet: **current**
- **wildpawn [AA_Wildpawn]**
  - owner keep in `rot_art_landed_20260920` key `AA_Wildpawn`
  - owner approve in `creature_art_register` key `c:AA_Wildpawn`
  - 2026-09-20 git-history (path deleted): `RotSpecies/Wildpawn/Wildpawn_south.png` <- 06966e55d Land the Rot artpipe backlog: 22 wave-1 + 58 wave-2 renders wired
  - 2026-10-03 sheet: **keep** - "Tint different shades for fun"

## Rows whose best candidate is probably NOT the desert render

Provenance only (owner-kept, canon-informed, or own art already live) - eyes decide, on the contact sheet.

| row | live art | other render sets | canon-informed sets | owner earlier kept | 10-03 decision |
|---|---|---|---|---|---|
| anooba [Anooba] | own (ArtOverride mod) | 6: anooba_toyfig_a, anooba_toyfig_b2, anooba_v1, pyrelands_anooba_f_v3, pyrelands_anooba_v1 | 2 | art_review_2026-09-12; creature_art_decisions.json; creature_art_register; keyline_ab_2026-09-13; legibility_final_review_2026-09-13; toyfig_pilot_2026-09-13 | keep |
| bolotaur [Bolotaur] | own/regenerated | 2: offbiome_bolotaur_v2, offbiome_bolotaur_v3 | 2 | creature_art_register | keep |
| bouldermit [AA_BoulderMit] | own/regenerated | 1: RSW_Korrum | 0 | creature_art_decisions.json; creature_art_register | keep |
| cactipine [AA_Cactipine] | - | 1: RSW_Spinerat | 0 | creature_art_decisions.json; creature_art_register | redo |
| desert ave [AA_DesertAve] | own/regenerated | 2: RM_Ossik, RSW_Sandstrider | 0 | creature_art_decisions.json; creature_art_register | redo |
| eopie [Eopie] | donor copy (dist 0) | 1: canon_eopie_v1 | 0 | creature_art_decisions.json; creature_art_register | redo |
| eyeling [AA_Eyeling] | own/regenerated | 2: RM_Ikee, RSW_Stareling | 0 | creature_art_decisions.json; creature_art_register | keep |
| fuelmite [VFEI2_Fuelmite] | - | 1: RSW_Cindermite | 0 | creature_art_decisions.json; creature_art_register | - |
| gigantelope [AA_Gigantelope] | own/regenerated | 2: RM_Thurra, RSW_Sandhorn | 0 | creature_art_register | redo |
| gizka [Gizka] | own (ArtOverride mod) | 8: pyrelands_gizka_2leg_option, pyrelands_gizka_biped_v3_north_r2, pyrelands_gizka_biped_v3_south_r2, pyrelands_gizka_biped_v4_east_r2, pyrelands_gizka_biped_v4_south_r2 | 7 | creature_art_decisions.json; creature_art_register | redo |
| Grank [Grank] | own (ArtOverride mod) | 1: grank_v1 | 0 | art_review_2026-09-12; creature_art_decisions.json; creature_art_register; legibility_final_review_2026-09-13 | - |
| greater krayt dragon [GreaterKraytDragon] | own (ArtOverride mod) | 1: greaterkraytdragon_v1 | 0 | art_review_2026-09-12 | - |
| horax [Horax] | own (ArtOverride mod) | 1: horax_v1 | 0 | art_review_2026-09-12 | - |
| iriaz [Iriaz] | donor copy (dist 0) | 4: pyrelands_iriaz_v1, pyrelands_iriaz_v1_north_r2, pyrelands_iriaz_v2, pyrelands_iriaz_v3 | 2 | creature_art_decisions.json; creature_art_register | keep |
| iridonian reek [IridonianReek] | donor copy (dist 0); own/regenerated | 0:  | 0 | creature_art_decisions.json; creature_art_register | keep |
| Jamel [Jamel] | own/regenerated | 0:  | 0 | bulk_art_misroute_2026-09-19; creature_art_register | keep |
| krayt dragon [KraytDragon] | donor copy (dist 0) | 1: greaterkraytdragon_v1 | 0 | art_review_2026-09-12; creature_art_decisions.json; creature_art_register | redo |
| kreetle [Kreetle] | donor copy (dist 0); own (ArtOverride mod) | 3: canon_kreetle_v1, facingrepair_kreetle_v1, kreetle_v1 | 0 | art_review_2026-09-12; creature_art_decisions.json; creature_art_register | keep |
| mammoth worm [AA_MammothWorm] | own/regenerated | 2: RM_Ulgga, RSW_Tuskcoil | 0 | creature_art_decisions.json; creature_art_register | keep |
| moss beetle [RSW_MossBeetle] | unknown (no donor to compare) | 1: deeps_mossbeetlelarvae_v2 | 0 | creature_art_register | keep |
| needlepost [AA_Needlepost] | - | 1: RSW_Barbthorn | 0 | creature_art_decisions.json; creature_art_register | redo |
| needleroll [AA_Needleroll] | own/regenerated | 2: RM_Kudda, RSW_Spineroller | 0 | creature_art_decisions.json; creature_art_register | redo |
| nuna [Nuna] | donor copy (dist 0) | 4: pyrelands_nuna_female_v1, pyrelands_nuna_v1, pyrelands_nuna_v1_north_r2, pyrelands_nuna_v2 | 2 | creature_art_decisions.json; creature_art_register | current |
| ronto [Ronto] | own (ArtOverride mod) | 1: ronto_v1 | 0 | art_review_2026-09-12 | keep |
| sand prowler [AA_SandProwler] | own/regenerated | 2: RM_Vosska, RSW_Dunestalker | 0 | creature_art_decisions.json; creature_art_register | keep |
| sand squid [AA_SandSquid] | own/regenerated | 2: RM_Ommok, RSW_Sandmaw | 0 | creature_art_decisions.json; creature_art_register | redo |
| terramorph [AA_Terramorph] | own/regenerated | 4: RM_Khorrak, RSW_Ferroclaw, aa_terramorph_v1, aa_terramorph_v1_north_r2 | 0 | art_review_2026-09-12; bulk_art_misroute_2026-09-19; creature_art_register; legibility_final_review_2026-09-13; toyfig_pilot_2026-09-13 | keep |
| terrorworm [Terrorworm] | - | 1: RSW_Ashworm | 0 | creature_art_register | keep |
| tetra slug [AA_TetraSlug] | own/regenerated | 3: RM_Vozzik, RM_VozzikSkeleton, RSW_Voltmaw | 0 | creature_art_register | redo |
| vulptex [Vulptex] | donor copy (dist 0) | 1: canon_vulptex_v1 | 0 | creature_art_decisions.json; creature_art_register | keep |
| war wyrm [WarWyrm] | donor copy (dist 0) | 1: RSW_WarWyrmSkeleton | 0 | creature_art_decisions.json; creature_art_register | redo |
| whisperbird [Whisperbird] | own (ArtOverride mod) | 2: canon_whisperbird_v1, whisperbird_v1 | 1 | art_review_2026-09-12; bulk_art_misroute_2026-09-19; creature_art_decisions.json; creature_art_register; legibility_final_review_2026-09-13 | keep |
| wildpawn [AA_Wildpawn] | - | 2: RSW_Sporepaw, rot_wildpawn_v2 | 0 | creature_art_register; rot_art_landed_20260920 | keep |
| wildpod [AA_Wildpod] | own (ArtOverride mod) | 2: RSW_Sporemass, rot_wildpod_v2 | 0 | bulk_art_misroute_2026-09-19; creature_art_register; rot_art_landed_20260920 | keep |
| zeer [Zeer] | own (ArtOverride mod) | 3: pyrelands_zeer_v1, pyrelands_zeer_v2, pyrelands_zeer_v2_east_r2 | 2 | creature_art_decisions.json; creature_art_register | keep |
| aaklac [AB_Aaklac] | - | 2: RSW_VellaraBloom, aaklac_v1 | 0 | bulk_art_misroute_2026-09-19 | keep |
| bloddle plant [Plant_Bloddle] | - | 1: bloddle_v1 | 0 | bulk_art_misroute_2026-09-19 | keep |
| brambles [Plant_Brambles] | - | 1: rut_grellspine | 0 | - | keep |
| bush [Plant_Bush] | - | 1: rut_grellbush | 0 | - | keep |
| creep stern [RG_Plant_CreepStern] | - | 2: RSW_Starvine, creepstern_v1 | 0 | - | keep |
| crimson cushion [RG_Plant_CrimsonCushion] | - | 2: RSW_EmberCarpet, crimsoncushion_v1 | 0 | - | keep |
| dervish [RG_Plant_Dervish] | - | 2: RSW_Whirlbloom, dervish_v1 | 0 | - | keep |
| dessert tree [AB_DessertTree] | - | 1: RSW_SweetbarkTree | 0 | - |  |
| grass [RG_Plant_AridGrass] | - | 2: RSW_Scrubgrass, aridgrass_v1 | 0 | - | keep |
| hardy grass [AB_HardyGrass] | - | 2: RSW_Dunegrass, hardygrass_v1 | 0 | - | keep |
| wild healroot [Plant_HealrootWild] | - | 1: rut_wildhealroot | 0 | - | redo |
| giant stikehr [AB_GiantStikehr] | - | 1: giantstikehr_v1 | 0 | - | redo |
| low shrubs [Plant_ShrubLow] | - | 1: shrublow_v1 | 0 | - | - |
| ripthorn [Plant_Ripthorn] | - | 1: ripthorn_v1 | 0 | - | - |

## Per row

| row | variants | repo-current | git versions | artpipe sets | donor | live (repo) | deployed differs | sheet showed corpse | owner art rulings (earlier) |
|---|---|---|---|---|---|---|---|---|---|
| anooba [Anooba] | 18 | 2 | 6 | 7 | 2 | own (ArtOverride mod) | 0 | YES | art_review_2026-09-12=keep; creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep; keyline_ab_2026-09-13=better; legibility_final_review_2026-09-13=good;  |
| bantha [Bantha] | 14 | 6 | 0 | 1 | 6 | donor copy (dist 0) | 0 | YES | creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| bolotaur [Bolotaur] | 7 | 1 | 1 | 3 | 1 | own/regenerated | 0 | YES | creature_art_register=approve; pyrelands_art_decisions.json=rerender |
| bouldermit [AA_BoulderMit] | 9 | 1 | 0 | 1 | 7 | own/regenerated | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve; stoneback_identity_2026-09-22=renamed |
| cactipine [AA_Cactipine] | 2 | 0 | 0 | 1 | 1 | none resolved | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| cannok [Cannok] | 4 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| clodhopper [Clodhopper] | 5 | 2 | 0 | 1 | 1 | donor copy (dist 0) | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| convor [Convor] | 23 | 10 | 0 | 1 | 10 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| corinathoth [Corinathoth] | 4 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| desert ave [AA_DesertAve] | 8 | 2 | 0 | 2 | 4 | own/regenerated | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| eopie [Eopie] | 20 | 14 | 0 | 2 | 2 | donor copy (dist 0) | 0 | YES | canon_regen_wave2_2026-09-18=; canon_review_decisions.json=3; creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| eyeling [AA_Eyeling] | 5 | 2 | 0 | 2 | 1 | own/regenerated | 0 |  | contagion_cast_art_review=regen; creature_art_decisions.json=keep; creature_art_register=approve |
| falumpaset [Falumpaset] | 13 | 6 | 0 | 1 | 6 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| feral grazer [FeralGrazer] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| feral nerf [FeralNerf] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| frilled gorg [FrilledGorg] | 21 | 10 | 0 | 1 | 10 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| fuelmite [VFEI2_Fuelmite] | 3 | 1 | 0 | 1 | 1 | none resolved | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| gigantelope [AA_Gigantelope] | 10 | 2 | 0 | 2 | 6 | own/regenerated | 0 |  | creature_art_register=approve |
| gizka [Gizka] | 16 | 2 | 4 | 9 | 1 | own (ArtOverride mod) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep; pyrelands_art_decisions.json=; pyrelands_art_decisions.json=rerender |
| gorg [Gorg] | 19 | 14 | 0 | 1 | 4 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| granite slug [GraniteSlug] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| Grank [Grank] | 5 | 1 | 1 | 2 | 1 | own (ArtOverride mod) | 0 | YES | art_review_2026-09-12=keep; bulk_art_misroute_2026-09-19=misrouted; creature_art_decisions.json=keep; creature_art_register=approve; legibility_final_review_2026-09-13=good |
| greater krayt dragon [GreaterKraytDragon] | 5 | 1 | 1 | 2 | 1 | own (ArtOverride mod) | 0 | YES | art_review_2026-09-12=keep; bulk_art_misroute_2026-09-19=misrouted; creature_art_decisions.json=shrink; creature_art_register=revise |
| gutkurr [Gutkurr] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| horax [Horax] | 5 | 1 | 1 | 2 | 1 | own (ArtOverride mod) | 0 | YES | art_review_2026-09-12=keep; creature_art_decisions.json=replace; creature_art_register=replace; legibility_grading_2026-09-13=mud |
| hrumph [Hrumph] | 5 | 2 | 0 | 1 | 2 | donor copy (dist 0) | 0 | YES | creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| igitz [Igitz] | 7 | 3 | 0 | 1 | 3 | donor copy (dist 0) | 0 | YES | creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| imperial toad [RSW_ImperialToad] | 2 | 1 | 0 | 1 | 0 | unknown (no donor to compare) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| iriaz [Iriaz] | 13 | 2 | 4 | 5 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep; pyrelands_art_decisions.json=rerender |
| iridonian reek [IridonianReek] | 4 | 2 | 0 | 1 | 1 | donor copy (dist 0); own/regenerated | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| jakobeast [Jakobeast] | 6 | 2 | 0 | 1 | 3 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| Jamel [Jamel] | 4 | 1 | 1 | 1 | 1 | own/regenerated | 0 | YES | bulk_art_misroute_2026-09-19=right; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| jellypot [RSW_Jellypot] | 2 | 1 | 0 | 1 | 0 | unknown (no donor to compare) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| jimvu [Jimvu] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| kowakian monkey-lizard [KowakianMonkeyLizard] | 13 | 6 | 0 | 1 | 6 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| krayt dragon [KraytDragon] | 14 | 4 | 1 | 3 | 6 | donor copy (dist 0) | 0 | YES | art_review_2026-09-12=keep; bulk_art_misroute_2026-09-19=misrouted; creature_art_decisions.json=keep; creature_art_decisions.json=shrink; creature_art_register=approve; creature_art_register=revise |
| kreetle [Kreetle] | 9 | 2 | 1 | 4 | 2 | donor copy (dist 0); own (ArtOverride mod) | 0 | YES | art_review_2026-09-12=keep; canon_regen_wave3_2026-09-23=; canon_review_decisions.json=3; creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep; legibilit |
| krykna [Krykna] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| Kwi [Kwi] | 1 | 1 | 0 | 0 | 0 | unknown (no donor to compare) | 0 | YES | desert_art_verdict_2026-09-20=keep |
| kybuck [Kybuck] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| landopus [JOE_Landopus] | 5 | 2 | 2 | 1 | 0 | unknown (no donor to compare) | 0 |  | creature_art_decisions.json=keep |
| longtail gorg [LongtailGorg] | 25 | 12 | 0 | 1 | 12 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| loth-cat [Lothcat] | 5 | 2 | 0 | 1 | 2 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| mammoth worm [AA_MammothWorm] | 7 | 2 | 0 | 2 | 3 | own/regenerated | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| massiff [Massiff] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| moss beetle [RSW_MossBeetle] | 7 | 3 | 1 | 3 | 0 | unknown (no donor to compare) | 0 | YES | creature_art_register=approve |
| mudhorn [Mudhorn] | 9 | 2 | 0 | 1 | 3 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| mynock [Mynock] | 9 | 2 | 1 | 1 | 5 | donor copy (dist 8) | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| needlepost [AA_Needlepost] | 2 | 0 | 0 | 1 | 1 | none resolved | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| needleroll [AA_Needleroll] | 5 | 2 | 0 | 2 | 1 | own/regenerated | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| nerf [Nerf] | 8 | 3 | 0 | 1 | 4 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| nuna [Nuna] | 17 | 4 | 5 | 5 | 2 | donor copy (dist 0) | 0 | YES | canon_review_decisions.json=3; creature_art_decisions.json=keep; creature_art_register=approve; desert_art_verdict_2026-09-20=keep; pyrelands_art_decisions.json= |
| pikobis [Pikobis] | 5 | 2 | 0 | 1 | 2 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| porg [Porg] | 24 | 11 | 0 | 1 | 11 | donor copy (dist 0) | 0 | YES | canon_review_decisions.json=2; creature_art_decisions.json=keep; creature_art_register=approve |
| Pufferpig [Pufferpig] | 4 | 2 | 0 | 1 | 1 | donor copy (dist 0) | 0 |  | creature_art_register=approve; desert_art_verdict_2026-09-20=keep |
| qormot [Qormot] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| ronto [Ronto] | 5 | 1 | 1 | 2 | 1 | own (ArtOverride mod) | 0 | YES | art_review_2026-09-12=keep; creature_art_decisions.json=shrink; creature_art_register=revise |
| runyip [Runyip] | 9 | 4 | 0 | 1 | 4 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| sand prowler [AA_SandProwler] | 7 | 2 | 0 | 2 | 3 | own/regenerated | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| sand squid [AA_SandSquid] | 8 | 2 | 0 | 2 | 4 | own/regenerated | 0 |  | creature_art_decisions.json=keep; creature_art_register=approve |
| Scavrats [Scavrat] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| scurrier [Scurrier] | 5 | 2 | 0 | 1 | 2 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| shaak [Shaak] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| shyrack [Shyrack] | 11 | 5 | 0 | 1 | 5 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| skalder [Skalder] | 6 | 2 | 0 | 1 | 3 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| sketto [Sketto] | 11 | 5 | 0 | 1 | 5 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| strill [Strill] | 5 | 2 | 0 | 1 | 2 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| tee muss [TeeMuss] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| terramorph [AA_Terramorph] | 9 | 3 | 1 | 4 | 1 | own/regenerated | 0 |  | art_review_2026-09-12=keep; bulk_art_misroute_2026-09-19=right; creature_art_register=approve; desert_art_verdict_2026-09-20=keep; legibility_final_review_2026-09-13=good; toyfig_pilot_2026-09-13=adop |
| terrorworm [Terrorworm] | 1 | 0 | 0 | 1 | 0 | none resolved | 0 |  | creature_art_register=approve |
| tetra slug [AA_TetraSlug] | 6 | 2 | 0 | 3 | 1 | own/regenerated | 0 |  | creature_art_register=approve |
| urusai [Urusai] | 11 | 5 | 0 | 1 | 5 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| uvak [Uvak] | 11 | 5 | 0 | 1 | 5 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| varactyl [Varactyl] | 5 | 2 | 0 | 1 | 2 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| voorpak [Voorpak] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| vulptex [Vulptex] | 5 | 1 | 0 | 2 | 1 | donor copy (dist 0) | 0 | YES | canon_regen_wave2_2026-09-18=; canon_review_decisions.json=4; creature_art_decisions.json=keep; creature_art_register=approve |
| war wyrm [WarWyrm] | 5 | 1 | 0 | 2 | 2 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| whisperbird [Whisperbird] | 14 | 5 | 1 | 3 | 5 | own (ArtOverride mod) | 0 | YES | art_review_2026-09-12=keep; bulk_art_misroute_2026-09-19=right; canon_regen_wave4_2026-09-23=; creature_art_decisions.json=keep; creature_art_register=approve; legibility_final_review_2026-09-13=good |
| wildpawn [AA_Wildpawn] | 5 | 1 | 1 | 2 | 1 | none resolved | 0 |  | creature_art_register=approve; rot_art_landed_20260920=keep |
| wildpod [AA_Wildpod] | 7 | 2 | 2 | 2 | 1 | own (ArtOverride mod) | 0 |  | bulk_art_misroute_2026-09-19=right; creature_art_register=approve; rot_art_landed_20260920=keep |
| womp rat [WompRat] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| worrt [Worrt] | 15 | 10 | 0 | 1 | 4 | donor copy (dist 0) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve |
| wraid [Wraid] | 3 | 1 | 0 | 1 | 1 | donor copy (dist 0) | 0 | YES | creature_art_register=approve |
| zeer [Zeer] | 9 | 1 | 3 | 4 | 1 | own (ArtOverride mod) | 0 | YES | creature_art_decisions.json=keep; creature_art_register=approve; pyrelands_art_decisions.json= |
| aaklac [AB_Aaklac] | 7 | 2 | 0 | 2 | 3 | none resolved | 0 |  | bulk_art_misroute_2026-09-19=right; flora_legibility_sheet_2026-09-17=works |
| bloddle plant [Plant_Bloddle] | 11 | 2 | 0 | 2 | 7 | none resolved | 0 |  | bulk_art_misroute_2026-09-19=right; flora_legibility_sheet_2026-09-17=works |
| brambles [Plant_Brambles] | 3 | 2 | 0 | 1 | 0 | none resolved | 0 |  |  |
| bush [Plant_Bush] | 3 | 2 | 0 | 1 | 0 | none resolved | 0 |  |  |
| creep stern [RG_Plant_CreepStern] | 11 | 0 | 0 | 2 | 9 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| crimson cushion [RG_Plant_CrimsonCushion] | 2 | 0 | 0 | 2 | 0 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| dervish [RG_Plant_Dervish] | 5 | 0 | 0 | 2 | 3 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| dessert tree [AB_DessertTree] | 5 | 1 | 0 | 1 | 3 | none resolved | 0 |  |  |
| grass [RG_Plant_AridGrass] | 2 | 0 | 0 | 2 | 0 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| hardy grass [AB_HardyGrass] | 3 | 1 | 0 | 2 | 0 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| wild chak-root plant [Plant_Chakroot_Wild] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  |  |
| wild healroot [Plant_HealrootWild] | 3 | 2 | 0 | 1 | 0 | none resolved | 0 |  |  |
| wild hubba gourd plant [Plant_HubbaGourd_Wild] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  |  |
| wild nysyllin plant [Plant_Nysyllin_Wild] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  |  |
| rat [Rat] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 | YES | creature_art_decisions.json=keep |
| giant stikehr [AB_GiantStikehr] | 5 | 0 | 0 | 1 | 4 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| low shrubs [Plant_ShrubLow] | 7 | 0 | 0 | 1 | 6 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| ripthorn [Plant_Ripthorn] | 8 | 0 | 0 | 1 | 7 | none resolved | 0 |  | flora_legibility_sheet_2026-09-17=works |
| Destroyer Droid [OuterRim_DestroyerDroid] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  | creature_art_register=approve |
| DUM Repair Droid [OuterRim_DUMDroid] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  | creature_art_register=approve |
| fx-7 medical droid [OuterRim_FX7Droid] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  | creature_art_register=approve |
| GNK Power Droid [OuterRim_GNKDroid] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  | creature_art_register=approve |
| MSE Repair Droid [OuterRim_MSEDroid] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  | creature_art_register=approve |
| Muckraker Crab Droid [OuterRim_MuckrakerDroid] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  | creature_art_register=approve |
| salvage assist droid [OuterRim_SalvageAssistDroid] | 0 | 0 | 0 | 0 | 0 | none resolved | 0 |  | creature_art_register=approve |
