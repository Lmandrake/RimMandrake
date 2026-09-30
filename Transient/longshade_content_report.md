# LONGSHADE_BEDAZZLE_CONTENT_1 — execution report (in progress)

Started 2026-09-29. Scope: parts 1-4, 6 of the spec. Parts 5, 7, 8 out of scope (listed as remaining).

## Part 1 — wire finished art (Ossik/Kudda/Thurra/Vosska/Khorrak/Ommok/Ulgga + vorrel family)
STATUS: DONE
- Found donor renders under old port names in `src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/RSW_{Sandstrider,Spineroller,Sandhorn,Dunestalker,Ferroclaw,Sandmaw,Tuskcoil}/` (already committed, tracked).
- Copied into `src/RimMandrake/LongShade/Textures/Things/Pawn/Animal/RM_{Ossik,Kudda,Thurra,Vosska,Khorrak,Ommok,Ulgga}/RM_<name>_{east,north,south}.png`. texPaths in RM_LongShade_Fauna.xml already pointed at the right RM_ path — pure file placement, no XML texPath change needed. Removed the now-stale "art pending" / "DESERT_PORT_PLACEHOLDER_ART_1" comments (21 lines).
- Khorrak reconciliation (DESERT_FAMILY_PORT_EXECUTION_1): used RSW_Ferroclaw's 3-facing render, not the older aa_terramorph_v1 job (which had a failed north originally) — matches the existing in-file comment that already named Ferroclaw as the target.
- Vorrel family: no PNG for these ever reached this worktree/git history under either name. Traced the actual rendered pixels via the artpipe job manifests' own `worker_self_report.out` path to `infrastructure/artpipe/_artsrc/rutstaggerseed_v1/` and `rutstaggerseeddish_v1/` in the **main checkout** (uncommitted daemon output, readable cross-tree though not part of this worktree's git history). Wired: `RM_Vorrel` plant graphic (Graphic_Random folder) <- rutstaggerseed_v1.png; `RM_VorrelFruit` item icon <- same render (the job's own style_notes says it covers both the bush and "the harvested item... a small pile of the same pale seed-filled fruits"); `RM_VorrelSeedDish` <- rutstaggerseeddish_v1.png.

## Part 6 — remove Alpha Animals texture deps (RM_GreatDevourer, RM_Groundrunner, RM_MatureFleshbeast)
STATUS: DONE (repoint), art BLOCKED
- Repointed all texPaths (bodyGraphicData, dessicatedBodyGraphicData, alternateGraphics) from `Things/Pawn/Animal/AA_*` onto this mod's own `Things/Pawn/Animal/RM_*` paths for all three creatures. No file exists at the new paths (checked artpipe done/_artsrc/pending/registry in both this worktree and the main checkout) — 3 jobs each are QUEUED in `infrastructure/artpipe/pending/` (RM_GreatDevourer_*, RM_Groundrunner_*, RM_MatureFleshbeast_*, not filed by me) but not yet rendered.
- Per instruction, did NOT queue new jobs (already queued by someone else) and did NOT repoint back at donor art. All three are now intentionally magenta, BLOCKED on those pending renders landing. Marked BLOCKED in each ThingDef's header comment.

## Part 2 — five filler defs (sollak, gennok, tebbra, dakkra, pirrik)
STATUS: DONE
- New file `src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fillers.xml`: RM_Sollak (bs 4.0, huge-herd), RM_Gennok (bs 2.4, herd/pack endurer), RM_Tebbra (bs 0.35, herd-small), RM_Dakkra (bs 1.6, burst predator carrying `RM_CompProperties_HeatBurstPredator` per the RSW_WraidAlpha template, defaults left as shipped). All four carry `RM_ShadeSeekingWanderExtension`. Bodies are vanilla (QuadrupedAnimalWithHooves / QuadrupedAnimalWithPawsAndTail) — no cross-mod BodyDef pulled in.
- Art: sollak/gennok/tebbra wired from the owner-ruled `_b` redo set (09-27 sheet: `Transient/desert_fillout_art_review/decisions.json` — IMPROVE verdicts); dakkra from its original KEEP render. All copied cross-tree from the main checkout's uncommitted artpipe `_artsrc/` output (never reached this worktree's git history).
- Wired inline into `RM_LongShade.xml`'s `wildAnimals` at 0.1/0.3/0.6/0.05 respectively (pyramid: only sollak exceeds bs 2, per the review doc's own note).
- Pirrik is NOT a filler def here — see part 4 (merged with RSW_GlitterBird).

## Part 3 — rename JOE_Cephalope -> RM_Qorrax
STATUS: DONE
- This is a SHARED def (`src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`) used by both RM_LongShade and RM_Stillsand (terrain-bound across both deserts per the Q7 ruling) plus 5 other Utinni biomes via `Absorbed_Cephaloids_Patches.xml`. Renamed defName+label+race pointer+hatcherPawn in the source def; repointed bodyGraphicData to the new own art (dessicated/swimming graphics left on the pre-existing donor-absorbed "cephalope" texture folder in the SAME mod — not a cross-mod dependency, no new render owed there).
- Fixed every functional reference: `RM_LongShade.xml`, `RUT_Desert.xml`, `RUT_ExtremeDesert.xml` (frozen twins — updated since leaving the old defName would silently break their wildAnimals row), `WildAnimals_Stillsand.xml`, `AnimalTolerances_Ashkarr.xml` (8 xpaths), `MegafaunaYield.xml` (6 xpaths), `Absorbed_Cephaloids_Patches.xml` (10 tag pairs across 5 other biomes). Also touched the two owning mods' own About.xml prose and the closest header comments; left older provenance-only prose elsewhere (SWBestiary About.xml, RM_Stillsand_Biome.xml comments) as historical record.
- Art: moved the 3 `RM_Qorrax_{east,north,south}.png` (KEEP verdict) into `src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/RM_Qorrax/` (the def's actual owning mod, not LongShade).

## Part 4 — merge RSW_GlitterBird + pirrik into RM_Pirrik
STATUS: DONE
- Deleted `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_GlitterBird.xml` outright (its eggs too — nothing else referenced them). Removed its wildAnimals row from `WildAnimals_LongShade.xml`'s Add block (37 -> 36 rows, header/count comments corrected).
- Built `RM_Pirrik` fresh in `RM_LongShade_Fillers.xml`: carries the donor's `RM_ShadowFollowerExtension` (searchRadius 60, unchanged mechanism) but uses vanilla "Bird" body (not the donor's cross-mod RSW_FlyingAvian) and the sheet's own pirrik art (real renders — no flying flip-book frames exist, so none declared; flight is the MaxFlightTime/FlightCooldown stat pair alone, per the flyer standing rule). New eggs `RM_EggPirrikFertilized/Unfertilized` added to `RM_LongShade_FaunaSupport.xml`.
- Wired inline on `RM_LongShade.xml` at the donor's old 0.2 weight. Result: exactly one glitter-bird/pirrik def in the repo (verified by grep).

## Verification
- XML parse: all 16 touched/created XML files parse clean (python xml.etree).
- defName collisions: none. Each new creature has exactly 2 declarations (ThingDef+PawnKindDef, expected); grep confirms zero remaining `<defName>JOE_Cephalope</defName>` / `<JOE_Cephalope>` / `race>JOE_Cephalope<` anywhere in src/.
- texPath resolution: every part 1/2/3/4 texPath resolves to a real file (caught and fixed a bug where RM_Ossik's north/south facings were never copied in an early pass — only east had landed). The only unresolved texPaths are the pre-declared part 6 BLOCKED trio (RM_GreatDevourer/RM_Groundrunner/RM_MatureFleshbeast) plus two untouched vanilla Core dessicated paths (Iguana, Spelopede) that resolve from Core's own Data folder, not this repo.
- `run_selftests.py`: 76/78 passed, 1 unmeasured (bridgetools DLL, needs Windows .NET SDK), 1 failed — `selftest_deployed_biome_refs.py`, the pre-declared known failure. Its 21 dangling refs are all `RUT_TheRot`/`RUT_Contagion`/`RUT_Miasma`/`RUT_TheForge`/`RUT_WeepingStones` rows, none touched by this item.

## Remaining (out of scope, not touched)
- Part 5: gloomcast's own art (still a Horax texture copy)
- Part 7: mirrak def + art (paired with LONGSHADE_BEDAZZLE_MECHANICS_1)
- Part 8: maidenbloom + skarrok/vrekka/sippra/tazzok/shadespire/pavecrust — unruled, owed an owner review sheet first

## Commits
(none yet)
