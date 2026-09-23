# Biome design readiness — 24 sheets, 2026-09-23

Grades the 24 rows of `Transient/biome_standalone_status_2026-09-23.md` on design
completeness (not build status). Sheets found under `design/` per that table's
`design` column; read whole.

## Criteria (exact test used)

1. `rulings` — YES if the sheet has a frozen/ruled decisions block, or a
   `.decisions.json` companion exists (`ls Transient/*<biome>*decisions.json`),
   or an inline `## ruling` / `RULED` section that is non-empty.
2. `flora` — YES if a plant roster gives defNames (backticked `RUT_`/`RM_`/`RSW_`/
   vanilla names), not prose descriptions only.
3. `fauna` — YES if an animal roster gives defNames, same test.
4. `terrain+weather` — YES if terrain/ground mix and weather/temperature are
   stated as values (fractions, ranges), not adjectives.
5. `open` — count of lines matching (case-insensitive):
   `open question|TBD|TODO|\?\?|UNRULED|needs (the )?owner|owner to rule`

VERDICT: `WIRING-READY` if 1–4 all YES and `open` ≤ 2; else `DESIGN-PASS-OWED`
with the missing criterion named (≤15 words).

## Status table

**Flora/fauna evidence note:** every sheet in `design/Jawa/worldbuilding/biomes/`
carries a companion roster at `design/Jawa/worldbuilding/biomes/rosters/<sheet>.json`
(schema `rosters/_SCHEMA.md`, all authored 2026-09-09 from the owner-ruled
`BIOME_FAUNA_ASSIGNMENT_SITTING_1` sitting) holding the actual `fauna`/`flora`
arrays of `{"def": "<defName>", ...}` rows. The prose sheets themselves almost
never inline a defName roster (they describe ecology in concept terms, e.g.
"the megafauna", "the cycle plant") — the roster JSON is where the defName-level
roster genuinely lives, and several sheets point at it by name inline (e.g.
`arid_shrubland.md:152` cites `rosters/arid_shrubland.json`). flora/fauna below
are graded against these roster files (non-empty array = YES), since that is
where "a roster with defNames" is actually satisfiable pre-wiring; inline
sheet defNames are noted separately where present.

| # | mod | sheet(s) | rulings | flora | fauna | terrain+weather | open | VERDICT | why |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stillsand | dune_sea.md + deep_desert.md | YES (dune_sea.md:3, deep_desert.md:3 — FROZEN banner) | YES (rosters/dune_sea_deep_desert.json: 3 defs — RSW_LightPipeNub, RSW_Plant_Bloddle, RSW_Ollim) | YES (rosters/dune_sea_deep_desert.json: 16 defs) | YES (dune_sea.md:50 "+70°C dayside..."; deep_desert.md:23-28 per-region temp/arc table) | 0 (dune_sea.md:0, deep_desert.md:0) | WIRING-READY | — |
| 2 | LongShade | desert.md | YES (desert.md:3) | YES (rosters/desert.json: 9 defs) | YES (rosters/desert.json: 53 defs) | YES (desert.md:23-24 arc/hilliness/temp table; :302 dew line) | 0 | WIRING-READY | — |
| 3 | TheRot | the_rot.md + kits/rot_kit_spec.md | YES (the_rot.md:3; + `Transient/rot_flora_fauna_review_2026-09-18.decisions.json` + `Transient/rot_size_rejudge_2026-09-19.decisions.json`, both frozen/ruled) | YES (rosters/the_rot.json: 30 defs) | YES (rosters/the_rot.json: 20 defs) | YES (the_rot.md:18-19,26,29,82 temp p10/median/p90, dew-point arc) | 0 (the_rot.md:0, rot_kit_spec.md:0) | WIRING-READY | — |
| 4 | Wasteland | wasteland.md | YES (wasteland.md:3) | YES (rosters/wasteland.json: 9 defs) | YES (rosters/wasteland.json: 15 defs) | YES (wasteland.md:33-35 three-band arc/temp/elevation table) | 0 | WIRING-READY | — |
| 5 | NightsideIce | nightside_ice.md | YES (nightside_ice.md:3) | YES-by-law (rosters/nightside_ice.json `flora_purged`: "flora list ships empty by law: §6 — no photosynthesis"; sheet §6 bans all plant life) | YES (rosters/nightside_ice.json: 10 defs) | YES (nightside_ice.md:27,30,58 temp p10/median/p90, elevation) | 0 | WIRING-READY | flora zero is a RULING, not a gap (corrected 2026-09-23) |
| 6 | ForsakenCrags | forsaken_crags.md | YES (forsaken_crags.md:3) | YES (rosters/forsaken_crags.json: 8 defs) | YES (rosters/forsaken_crags.json: 16 defs) | YES (forsaken_crags.md:24,79,96 temp p10/median/p90, ambient band) | 0 | WIRING-READY | — |
| 7 | BlueDesert | the_blue_desert.md | YES (the_blue_desert.md:3) | YES (rosters/the_blue_desert.json: 3 defs) | YES-thin (rosters/the_blue_desert.json: 2 defs — AA_Thunderbeast, Vapaad) | YES (the_blue_desert.md:25 temp median; :92-94 hydrocarbon phase points) | 0 | WIRING-READY | fauna roster is only 2 defs — see UNCERTAIN |
| 8 | FloodedCanyon | the_cracked_lands.md | YES (the_cracked_lands.md:3) | YES (rosters/the_cracked_lands.json: 6 defs) | YES (rosters/the_cracked_lands.json: 12 defs) | YES (the_cracked_lands.md:25 temp p10/median/p90) | 0 | WIRING-READY | — |
| 9 | LeaningScrub | arid_shrubland.md | YES (arid_shrubland.md:3) | YES (rosters/arid_shrubland.json: 11 defs) | YES (rosters/arid_shrubland.json: 41 defs) | YES (arid_shrubland.md:32-33,37 insolation/hilliness/temp table) | 0 | WIRING-READY | — |
| 10 | PoisonForest | poison_forest.md | YES (poison_forest.md:3) | YES (rosters/poison_forest.json: 9 defs) | YES (rosters/poison_forest.json: 24 defs) | YES (poison_forest.md:33-35 temp median/p10/p90) | 0 | WIRING-READY | — |
| 11 | TerminalBiomes | the_scald.md, kits/scald_kit_spec.md, the_propane_lakes.md, terminator_sea.md, the_twilight_deep.md, the_grey_deep.md | YES (the_scald.md:3 + 4 siblings, all FROZEN) | **NO** (rosters/the_scald.json flora=0, the_grey_sea.json flora=0, the_twilight_sea.json flora=0; only rosters/the_propane_lakes.json has 4 — 3 of 4 sub-biome rosters are empty) | YES (the_scald.json 8, the_propane_lakes.json 6, the_grey_sea.json 8, the_twilight_sea.json 15 defs) | YES (the_scald.md:29; the_propane_lakes.md:19,28,36; terminator_sea.md:70,91,226) | 1 (scald_kit_spec.md:166 `?? false` — C# null-coalescing snippet, not a design gap; all 5 sheets otherwise 0) | DESIGN-PASS-OWED | flora near-empty: scald/grey-sea/twilight-sea rosters carry 0 plant defs |
| 12 | RustCathedral | the_rust_cathedral.md, kits/rust_cathedral_kit_spec.md | YES (the_rust_cathedral.md:3) | **NO** (rosters/the_rust_cathedral.json: flora=0) | YES-thin (rosters/the_rust_cathedral.json: 3 defs) | YES (the_rust_cathedral.md:35 temp median 62.5°C, rain~zero) | 0 | DESIGN-PASS-OWED | flora roster empty — rosters/the_rust_cathedral.json carries 0 plant defs |
| 13 | Greentide | the_greentide.md, kits/greentide_kit_spec.md | YES (the_greentide.md:3) | YES (rosters/the_greentide.json: 11 defs) | YES (rosters/the_greentide.json: 22 defs) | YES (the_greentide.md:26,30,37,126 tile share, temp median, wet-bulb) | 1 (the_greentide.md:43 `diseaseMtbDays 50` — field-name false positive on "TBD", not a real gap) | WIRING-READY | — |
| 14 | WeepingStones | weeping_stones.md | YES (weeping_stones.md:3) | YES (rosters/weeping_stones.json: 4 defs) | YES (rosters/weeping_stones.json: 10 defs) | YES (weeping_stones.md:35,53,74 temp p10/p90, elevation) | 0 | WIRING-READY | — |
| 15 | Pyrelands | the_pyrelands.md | YES (the_pyrelands.md:3) | YES-thin (rosters/the_pyrelands.json: 1 def — RM_FE_Plant_Quickgrass) | YES (rosters/the_pyrelands.json: 14 defs) | YES (the_pyrelands.md:30 sun/temp median) | 0 | WIRING-READY | flora roster is only 1 def — see UNCERTAIN |
| 16 | Contagion | the_contagion.md | YES (the_contagion.md:3) | YES (rosters/the_contagion.json: 10 defs) | YES (rosters/the_contagion.json: 16 defs) | YES (the_contagion.md:36,38,40 rainfall/temp/elevation) | 1 (the_contagion.md:195 "Cure: unruled" — genuine open item, within budget) | WIRING-READY | one real open item (cure mechanism unruled) but under the ≤2 budget |
| 17 | Webwork | the_webwork.md, kits/webwork_kit_spec.md | YES (the_webwork.md:3) | YES (rosters/the_webwork.json: 7 defs) | YES (rosters/the_webwork.json: 6 defs) | YES (the_webwork.md:32 temp p10/median/p90) | 1 (the_webwork.md:46 `diseaseMtbDays 35` — field-name false positive, not a real gap) | WIRING-READY | — |
| 18 | GelatinousSlime | the_slime.md, the_slime_gene_lists.md | YES (the_slime.md:3; gene list itself "✅ ACCEPTED, owner 2026-09-06") | YES (rosters/the_slime.json: 5 defs) | YES (rosters/the_slime.json: 12 defs) | YES (the_slime.md:31 temp p10/median/p90) | 0 | WIRING-READY | — |
| 19 | Miasma | the_miasma.md, kits/miasma_kit_spec.md | YES (the_miasma.md:3) | YES (rosters/the_miasma.json: 4 defs) | YES (rosters/the_miasma.json: 33 defs) | YES (the_miasma.md:31,36 sun/temp median) | 3 (the_miasma.md:40 + miasma_kit_spec.md:187,289 — all three are `diseaseMtbDays` field-name hits on the "TBD" pattern, not real gaps) | DESIGN-PASS-OWED | open=3, all three are `diseaseMtbDays` false-positive hits, not real gaps |
| 20 | Scarlands | the_scarlands.md, kits/scarlands_kit_spec.md | YES (the_scarlands.md:3) | YES-thin (rosters/the_scarlands.json: 1 def — RUT_ScorchedStars) | YES (rosters/the_scarlands.json: 15 defs) | YES (the_scarlands.md:29,44 sun/temp median) | 0 | WIRING-READY | flora roster is only 1 def — see UNCERTAIN |
| 21 | TheForge | the_forge.md, kits/forge_kit_spec.md | YES (the_forge.md:3) | YES (rosters/the_forge.json: 10 defs) | YES (rosters/the_forge.json: 9 defs) | YES (the_forge.md:25 sun/temp range) | 0 | WIRING-READY | — |
| 22 | FeverWood | the_fever_wood.md, kits/fever_wood_kit_spec.md | YES (the_fever_wood.md:3) | YES (rosters/the_fever_wood.json: 7 defs) | YES (rosters/the_fever_wood.json: 12 defs) | YES (the_fever_wood.md:28 sun/temp median) | 0 | WIRING-READY | — |
| 23 | TheSump | the_sump.md, kits/sump_kit_spec.md | YES (the_sump.md:3) | YES-thin (rosters/the_sump.json: 1 def — AB_TarPuddle) | YES (rosters/the_sump.json: 5 defs) | YES (the_sump.md:32 temp p10/median/p90, elevation) | 1 (sump_kit_spec.md:253 `diseaseMtbDays` — field-name false positive, not a real gap) | WIRING-READY | flora roster is only 1 def — see UNCERTAIN |
| 24 | LanternDeeps | the_lantern_deeps.md | YES (the_lantern_deeps.md:3; + `Transient/lantern_deeps_strange_life_2026-09-20.decisions.json`) | **NO** (rosters/the_lantern_deeps.json: flora=0; file notes species mix beyond the 3 imported fauna is still Owed) | YES-thin (rosters/the_lantern_deeps.json: 3 defs) | YES (the_lantern_deeps.md:13,27,37 temp thresholds, elevation) | 0 | DESIGN-PASS-OWED | flora roster empty — rosters/the_lantern_deeps.json flora=0, species mix still Owed |

## WIRING-READY (spec order)

1. Stillsand
2. LongShade
3. TheRot
4. Wasteland
6. ForsakenCrags
7. BlueDesert
8. FloodedCanyon
9. LeaningScrub
10. PoisonForest
13. Greentide
14. WeepingStones
15. Pyrelands
16. Contagion
17. Webwork
18. GelatinousSlime
20. Scarlands
21. TheForge
22. FeverWood
23. TheSump

20 of 24 (NightsideIce re-graded 2026-09-23).

## DESIGN-PASS-OWED (missing criterion each)

5. ~~NightsideIce~~ — RE-GRADED WIRING-READY 2026-09-23: the empty flora roster is the sheet's §6 law (no photosynthetic life), recorded in the roster's `flora_purged`, not a gap
11. TerminalBiomes — flora: 3 of 4 sub-biome rosters (scald/grey-sea/twilight-sea) carry 0 plant defs
12. RustCathedral — flora: roster (`rosters/the_rust_cathedral.json`) has 0 plant defs
19. Miasma — open: literal count is 3, but all three are `diseaseMtbDays` field-name hits, not real gaps (see UNCERTAIN)
24. LanternDeeps — flora: roster (`rosters/the_lantern_deeps.json`) has 0 plant defs; species mix beyond 3 imported fauna still Owed

4 of 24 (after the NightsideIce re-grade).

