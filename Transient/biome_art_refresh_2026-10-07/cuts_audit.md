# Cuts / moves / deletions audit — past review sheets (2026-10-08)

Owner, 2026-10-08: *"Run through past sheets and make sure that any art I cut or creatures I moved or deleted from game or biome were carried out."*

Status: DONE (audit + enactment). Selftests 337/337. Nothing deployed.

## Method
- Scope: all 130 `*.decisions.json` under `Transient/` and `infrastructure/state/art_rulings/`. Human = a row with an `at`/`decidedAt` stamp, or a sheet whose `reviewStatus.state` is `ruled`. Prefill-only sheets (cauldron, floodedcanyon, theforge, therot, wasteland, weepingstones, lantern_deeps_strange_life, longshade_content/extras, mc_matrix, mineral_numbers, canon_regen waves, junk_reskin, flora_legibility, desert_sitting1, art_doubles_compare) and retired sheets (landmark_density, twilight_deep_sitting) were not treated as rulings.
- Extraction: every human row whose decision is cut-like (`cut`, `hold`+cut note, `reject`, `misrouted`, `not_deeps`) or whose note matches cut/remove/drop/move/belongs/tier/biome words — 222 distinct row+note pairs after de-duplicating the art_rulings copies; blanket `replace` rows (desert_family, port_*) are ports, not cuts.
- Art: every `purge` sha on a human row (1,426 entries) checked against the art ledger index (`is_purged`, live slots, store).
- Rosters: a parser over every `src/**/*.xml` — BiomeDef `wildAnimals`/`wildPlants`/`fishTypes` read as ELEMENTS (`<DefName>commonality</DefName>`, fresh/saltwater sub-lists recursed), plus patch-added rows resolved from each PatchOperation's own `xpath`. Sanity probes: `AA_Slurrypede` (cut from RM_Miasma tonight) reads absent from RM_Miasma and present only in the frozen RUT_ twins; `RM_Kudda`/`RSW_Kudda` (7663b4e5c) read as no def, no roster; `RSW_Gizka` reads its 4 patch-added RM homes. Def references outside rosters (explosive-growth rosters, gensteps, C#) grepped for each surviving uncast def.
- Design roster JSONs (`design/Jawa/worldbuilding/biomes/rosters/`) checked for rows still claiming a cut creature is cast.

## (a) Art purge / cut

| Sheet | His words | Before | Action | Commit |
|---|---|---|---|---|
| 1,426 purge shas across the biome_ffar sheets | (per-row purge clicks) | 1,397 purged | — | — |
| webwork / RM_Brimlock `9e0e6c1d33b1` | "No viable art, try again." | missing — refused at ingest because the pillar-arm bytes were live on the Kudda/Venomvine slots | both slots since replaced; purge applied through the ledger with the sheet's own note | 1e1c8963c |
| deepfire_pigment cuts (crowncarpet_a, rutwelcomeblanket_v1, rainbowpigment a/b/c) | `cut` (whitelist sheet) | done — none live | — | — |
| art_review_2026-09-12 bgtest_a/b cuts | `cut` | done — test renders, none live | — | — |
| art_review_2026-09-06 Enhydriodon/Gorilla/Revenant | "Don't need" / reject | done — redesign renders never installed | — | — |

**Purges correctly REFUSED because the picture is still live** (the ledger will not delete a live picture; each waits on its replacement render):
- `RSW_Vozzik` purge (deep_desert + rustcathedral) = the live `RM_Vozzik` art in Stillsand (redo: "obviously entirely synthetic").
- `RSW_Eopie` purge (desert + leaningscrub) = live `EopieA` in StarWarsPatches/SWBestiary; he picked G (Long Shade) / E (Leaning Scrub).
- `VFEI2_Swarmling` (greentide) = live Swarmling art in TheRot (redo as Saluksis).
- `RM_Dredgel` east (thesump) — redo "make it go all the different directions".
- `RM_Hollu` and `RM_Lunoowa` (twilightsea) — redo as waveglass.
- `92592a786b3e` (purged on Noohm/Shulla/Loohn/Lunoowa/Noolim/Weloon rows) = live `RM_Sorruth.png`; Sorruth is cut from the Grey Sea but its def remains (see (b)).
- `a25f92f19950` (purged on NightMule/Aveluthia/Vhaulk rows) = live turret texture `RUT_AncientShieldedTurret` — correct where it is; it was wrong only on those rows.

## (b) Cut from a biome — all carried out

| Sheet (biome) | Subject | His words | Status | Commit |
|---|---|---|---|---|
| abyss (RM_Abyss) | AA_DuskRat, AA_Frostling, AA_NightAve, AA_ShadowCharger, AA_Thunderox | "no longer needed, cut" | done — cast nowhere | (abyss sittings) |
| abyss | RM_Vosska | "doesn't belong here." | done — only in RM_Stillsand | structural rulings |
| feverwood (RM_FeverWood) | RM_Gorrameth, RM_Lommerel, RM_Nemmel, RM_Skethral, RM_Thavrik | "cut no longer needed" | done — uncast; defs kept | 093caf2ca |
| greentide | RM_Sytheclaw | "This should not be in this biome" | done — out of RM_Greentide; stays Pyrelands | ce1772c72 |
| greysea | RM_Sorruth, RM_SorruthCatch | "cut don't need" | done — uncast; defs kept | 20fd7cf7c |
| lanterndeeps | RM_BovineBeetle, RM_Chiller, RM_GlowSlug, RM_ShatterjawBeetle | "cut dont need" / "Too magical, cut" | done — defs deleted | 66a0d9db1 |
| lanterndeeps | RSW_BovineBeetle, RSW_GlowSlug, RSW_ShatterjawBeetle | "cut dont need" | done — not in Lantern Deeps (GlowSlug stays in frozen RUT_FeverWood) | 8c988d74b |
| lanterndeeps | RM_OsskBramble | "cut don't need" | done — uncast; GenStep_DeepFloraGate only gates removal, explosive-growth roster spawns nothing | 66a0d9db1 |
| lanterndeeps | RM_FacetMothLarvae / RM_Megapleura / RM_MossBeetleLarvae "cut" + RSW_ twin "I like… RimMandrake tier" | merge, not a cut | done — RSW_ defs retired, RM_ def cast wearing the RSW picture (moss grub's eyeless repaint installed) | 8c988d74b, f3cbef031 |
| leaningscrub | RM_Skorra, RSW_ImperialToad | "Just cut this" / "no longer needed" | done — uncast | 818c513d9, f19fcfdcc |
| miasma | AA_Slurrypede | "cut from this biome" | done | af2b54fe2 |
| rustcathedral | GR_Mecharat | "cut no longer need" | done | — |
| thechill | RM_Keelgrass | "cut no longer needed" | done — def deleted | 865c70ad6 |
| thesump | RM_Brommet, RUT_Plant_Wick | "terrestrial, cut" / "cut this no longer needed" | done — uncast | 040980b2b |
| warscar | AA_SpinedGow, RSW_CrystalFairyMole | "Cut this, no longer needed" | done | 653e02afb |
| deeps_flora_fauna 2026-09-18 | RSW_AaroxisDendoria(+Larvae), BloodropLarvae, BovineBeetleLarvae, FacetMoth, MossBeetle, PodWorm, RoyalRhino | `cut` | done — none in Lantern Deeps (survivors elsewhere are correct: cuts are biome-scoped) | — |
| rot_flora_fauna 2026-09-18 | RSW_BovineBeetle, RUT_Emberscythe | `cut` | done — not in RM_TheRot (RM_Emberscythe lives in the Pyrelands) | — |
| pyrelands 2026-09-15 | boomalope | `cut` | done | — |
| desert_art_review 2026-10-03 | RSW_ImperialToad, AB_DessertTree | "Cut it" / "THIS IS CUT" | done | — |

**Stale design-roster rows fixed** (the XML had the cut; the roster JSON still said cast): `the_rust_cathedral.json` GR_Mecharat, `the_scarlands.json` RSW_CrystalFairyMole and AA_SpinedGow (said "move:ExtremeDesert"), `arid_shrubland.json` RSW_ImperialToad → evictions `cut`. Commit 1e1c8963c.

## (c) Deleted from the game — all carried out

| Sheet | Subject | His words | Status | Commit |
|---|---|---|---|---|
| desert (Long Shade) | RM_Kudda, RSW_Kudda | "Just cut this creature. It's dumb." | done — defs deleted | 7663b4e5c |
| desert | RM/RSW_MatureFleshbeast, RM/RSW_Ossik, RM/RSW_Thurra, RSW_DommoTree | "Remove this" / "no longer needed" / "cut this" | done — defs deleted | structural rulings 2026-10-05 |
| gelatinousslime | RM_Glurro | "Don't need this, cut it and its ability." | done — def, salve and ability gone (no reference left in src) | c46bfc123 |

## (d) Moved (biome or tier) — all carried out but one

| Sheet | Subject | His words | Status | Commit |
|---|---|---|---|---|
| contagion | RM_Shambles | "this belongs in the Rot, not here." | done — RM_TheRot only | — |
| deep_desert | RSW_Vozzik → Rust Cathedral | "This should be moved to the Rust Cathedral Biome." | done (patch-added) | structural rulings |
| deep_desert | RM/RSW_Ollim, RSW_LightPipeNub, RSW_Drazzik → RM tier | "belongs in RimMandrake level" | done | structural rulings |
| desert | Dewfringe, Jellypot, Khorrak, Ommok (→Miasma, ×0.5), TruffleMole (→Leaning Scrub), Ulgga (→Stillsand, ×2), Ultracactus (→Ultriss Pad, Stillsand), Vosska (→Stillsand) | (see sheet) | done | structural rulings |
| lanterndeeps | Gembug, BloodropMoth, FacetMothLarvae, Megapleura → RM tier | "RimMandrake tier" | done | 8c988d74b |
| leaningscrub | RSW_TunnelSnake → RM tier | "RimMandrake tier" | done | cf40abca6 |
| miasma | RSW_AaroxisDendoria → RM_Liliana; RSW_RustNipperJuv "not SW tier" | | done | af2b54fe2 |
| thescald | RSW_ElderSando → RM_GrippingTerror, Twilight Sea; RSW_SandoAquaMonster → Twilight Sea | "It does not belong in the Scald." | done | — |
| twilightsea | RM_SaltBladeTwilight → Grey Sea, less solitary | "Move it there" | done | 9f77e21e2 |
| twilightsea | RM_Hollu B render → new creature Dancing Skresh | | done | 9f77e21e2 |
| twilightsea | RSW_Faa old art → new Greentide river fish "Scaa Lumsigh" | "Move this image to that fishing source" | **missing → ENACTED**: `RM_ScaaLumsigh` (Greentide fish file, RM_Greentide freshwater_Uncommon 0.2), old faa east facing installed via the art ledger under his RSW_Faa ruling | 588cfd395 |
| twilightsea | RSW_Mee old art → Greentide river fish | "move this fish art to the Greentide rivers as fishable" | **ENACTED** after the card: `RM_Vashuu` (name INVENTED by the agent), freshwater_Common 0.3, old mee east facing via the art ledger | f3a7513c5 |
| twilightsea | RM_Niim old art | "can be kept for fishing elsewhere" | **STORED** after the card: owner-keep ruling (`raw_verdict: reserve`) on the three niim v1 shas, for the next sea sitting; no new species | f3a7513c5 |

## Answered by question card 2026-10-08 00:24 PDT — enacted
1. Mee picture → new river fish `RM_Vashuu` (f3a7513c5).
2. Niim picture → stored for the next sea sitting (f3a7513c5).
3. Cut creatures still in the files → **deleted from the game** (d074b131a): RM_Gorrameth, RM_Lommerel, RM_Nemmel, RM_Skethral, RM_Thavrik (+2 eggs), RM_Sorruth, RM_SorruthCatch, RM_Brommet (+RM_BrommetWool), RUT_Plant_Wick (+RUT_WickStem, its only harvest), RM_Skorra, RSW_ImperialToad (+2 eggs), RSW_CrystalFairyMole, RSW_BovineBeetle (+2 eggs), RSW_GlowSlug (+2 eggs, gastropod meat, its meat base and raw-eat thought, 4 sounds), RSW_ShatterjawBeetle (+larva, pupa, 2 eggs). The list is `deleted_defs_2026-10-08.json` beside this file.
   - References fixed: RUT_FeverWood roster (glowslug), RUT_ExplosiveGrowthRoster (wick), RUT_Sump header, AnimalTolerances_Ashkarr (4 blocks), TheSump validation `wick_garden_crop` + walk + required_checks.json, FeverWood def floors, placeholder_allowlist (5 entries), cast_assignment.csv (3 rows), armoury desc csv (12 rows), roster JSONs (fever wood, grey sea, cracked lands, rot, arid shrubland, scarlands), port-file headers.
   - Art: 26 unreferenced textures retired through the ledger (archived in the store, history kept) by `retire_deleted_creature_textures.py`. **14 owner-kept textures stay on disk unreferenced**: RM_Thavrik ×3, RM_Gorrameth ×3, RM_Lommerel ×3, RM_Nemmel ×3, RM_Sorruth, RM_Skethral_a. The ledger refuses to retire a picture he kept without his typed words.
   - Kept on purpose: the grapple mechanic (RM_PincerGrapple/RM_PincerCrush/RM_Grappled, CreatureBehaviors C#), now used by no creature. Bovine grub/pupa: sandpillar eggs still hatch them. Shared item textures (eggs, meat, wood).
   - Not edited: dated design proposals, closed items and past sheet decisions (history); generated `creature_register_rows.json` (rebuilt from the next def dump). Open items that still mention a deleted creature: FEVERWOOD_RM_CAST_COMPLETION_1, SUMP_MECHANICS_1, DEEPS_FAUNA_MECHANICS_1/2, FLYER_FLIPBOOK_ART_1 (thavrik), SEA_FISHABLES_ALIVE_IN_DEPTHS_1, LEANINGSCRUB_SHEET_ART_REDO_1.
