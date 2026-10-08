# Long Shade sheet — enactment (2026-10-07/08, BENCH helper)

Source: `Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json` (the RM_LongShade sheet, port 40813). md5 at start 28ebd518…, writeCount 901, 93 decisions: 54 from his 2026-10-08 UTC session, 36 from 2026-10-05, 3 no-`at` prefills (ignored).

## Status
- [x] decisions read
- [x] install / purge
- [ ] regen queued
- [x] names / descriptions / tiers / cuts (descriptions; no new renames/tiers/cuts were asked today)
- [ ] def changes
- [ ] validate + selftests
- [ ] commits

## Log
### Part 1 — install / purge (done)
- Copy of decisions: infrastructure/state/art_rulings/2026-10-08_longshade_desert_sheet_2026-10-04.decisions.json.
- ingest (--defer-redo-jobs): 142 rulings, 3 rejected, ~232 purges; re-run after installs cleared Horax (+ retired fleshbeast) purges. 3 refused: Eopie in-game bytes he kept as variant A (correct).
- Installed full S/E/N sets (24 rows, 72 files, script `longshade_install_plan.py`): Gennok C, Gloomcast E, Bolotaur E, FeralGrazer C, Gutkurr C, Horax E (HoraxArtOverride), Hrumph D, IridonianReek D, Jakobeast E, Jamel D, Jimvu C, Krykna C, Kwi C, LongtailGorg F, Runyip G, Shaak C, Shyrack C, Uvak C, Varactyl D (Varactyl_f), Voorpak D, Wraid C (= WraidAlpha C, same texPath), Zeer I (ZeerArtOverride).
- Dunejelly D -> own path Things/Pawn/Animal/RM_Dunejelly (donor Jellypot path carries a colour mask); def repointed.
- Bantha F -> swanimals/Bantha/BanthaR (BanthaW has colour masks); adolescent/adult stages repointed, shader Cutout, female dark tint dropped, donor colour alternates off (chance 0) — they would muddy the canon colours. Calf keeps BanthaW_j (his pick C).
- RSW_GreatDevourer A (our render) -> SWBestiary Things/Pawn/Animal/RSW_GreatDevourer; the three Alpha Animals donor alternates removed. Dessicated still donor.
- Plants (`longshade_install_plants.py`): Shadespire D, Vorrel B, Chakroot C replace the live picture; Graphic_Random variants added: Dewfringe B-F, Pavecrust B-F, SurraGrass B-D, VellaraBloom B-D, Maidenbloom B (10-05 click never carried out).
- Already current (pick = in game): Bokka B (70ec8378e), Eopie G (+j F), FrilledGorg F, Gorg F, Iriaz I, Ronto F, Skalder D, Worrt E, HubbaGourd B, all juvenile/swim picks.
- MatureFleshbeast: def was cut 10-04 but its 3 textures were still in LongShade; retired through the ledger on his words "Remove this, no longer needed".
- Skalder and Voorpak notes are the 10-05 redo notes carried over verbatim; today's pick is the result -> no new job.

### Descriptions / sizes (done, sonnet helper, longshade_descriptions.md)
- Fresh descriptions from the art: Oreclaw, Ski'ra'lim, Dunejelly (from pick D), Chorn.
- Chorn drawSize 4.4 -> 5.0 (all stages x1.136, shadow scaled); Dewback adult 3 -> 4 (stages scaled; shadow not scaled).
