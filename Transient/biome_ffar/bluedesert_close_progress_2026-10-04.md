# Blue Desert close — progress 2026-10-04 (BENCH helper)

## 1 ingest + install — DONE
- decisions.json carried the FIRST sitting's snapshotId (4a3c4f2f…); every second-sitting pick resolves only in the refreshed snapshot 0a169dd0… and every first-sitting pick resolves identically in both, so the stamp was corrected to 0a169dd0 and ingested: 14 rulings.
- `ingest.py` ignored the sheet's `variants` list; it now emits a keep ruling per kept variant column (4 more: Chimeglobe B, Glassfern C, Palefloss B, C).
- The install plan's plant targets (`Things/Plant/X/X.png`) were wrong: the three plants are already Graphic_Random folders (`Things/Plant/X/X/X_a.png`). Installed into the folders instead.
- Installed 16 via `--ruling`: Dovvik B×3, Murrek C×3 (RM_Murrek.png single skipped — no def reads it), Utikka B×3, Vrisk B east+south (B has no north; old north stays), Chimeglobe_b, Glassfern_a(=B)+_b(=C), Palefloss_b, _c. Chimeglobe A / Palefloss A were already live.
- Glassfern old A (49c80e23) purged per owner after replacement. Vhaulk purge a25f92f1 refused: that sha is live as RUT_AncientShieldedTurret (AssailantSalvage) — not touched.
- Untouched prefill rows (Dorrak, Krissek, Vekkit) carry no ruling.

## 2 def work — in progress
- Dorrak/Krissek/Vekkit: PawnKindDef texPaths -> own art, tint dropped; A sets installed (--owner-said "go!…", rows were untouched prefill). ed84f84ca
- AA_Thunderbeast: src/RimMandrake/BlueDesert/Patches/AA_Thunderbeast_BlueDesert.xml (FindMod "Alpha Animals"): texPath -> AA_Thunderbeast_BlueDesert, bodySize 0.75, drawSizes halved, hydrocarbon description. GLOBAL change (spawns elsewhere too).
- Vapaad: src/RimUtinni/UtinniPatches/Patches/Vapaad_BlueDesertArt.xml (FindMod SWAC Continued): body texPath -> RUT_Vapaad. 63776e580

## 3 variants — DONE (plants were already Graphic_Random folders; see step 1)
## 4 validate — validate_patch 2 files 0 errors (610-mod FULL list); selftest_bluedesert ALL OK; run_selftests 176/179, 3 failures not ours (JOE_Landopus label drift, bridgetools DLL surface, StarWarsPatches semantics passes standalone)
## 5 deploy — HELD: `--compose biomes` plan carries other seats' LongShade/Stillsand/WeepingStones edits + CreatureBehaviors DLL; UtinniPatches plan carries others' Absorbed_Cephaloids/Desert/WildAnimals edits. Not applied.
## 6 notes — done on BIOME_FLORAFAUNA_ART_REVIEW_1 and LONGSHADE_SHEET_STRUCTURAL_RULINGS_1
