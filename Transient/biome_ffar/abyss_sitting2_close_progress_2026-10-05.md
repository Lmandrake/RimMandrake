# Abyss sheet — sitting 2 close (2026-10-05)

Owner: "The Abyss sheet done". Decisions: `Transient/biome_ffar/abyss_sheet_2026-10-04.decisions.json`, 24 rulings stamped 20:00-20:11 (03:00-03:11Z).

## Rulings read (group) — DONE
Raw decisions committed first. Stamped ruled (sitting 2 evidence) and `art.py ingest --redo-jobs`: 48 rulings, 33 purges, 0 unresolved.
1 purge refused: crags_hulggarok east (a25f92f19950) is live as `src/RimMandrake/AssailantSalvage/Textures/Things/Building/Ancient/RUT_AncientShieldedTurret.png` — byte-identical picture, so it stays until that turret gets other art.
Redo-jobs check: NightMule + Septimum against this sitting's jobs; RM_Wickwood against its sitting-1 jobs (the note is the same text carried over).

## Family look — DONE
Pitch/inky black + FOUR GLOWING YELLOW EYES. rimflow note on ABYSS_SHEET_DONOR_PORT_1 (quotes "Make hide pitch black with four glowing yellow eyes"); appended to `infrastructure/state/lessons/20261005T150818Z-BENCH-owner-s-preferred-invented-name-style.md`.
Nightling: his note says yellow eyes, no count, so its drawn eye count is kept.

## Installs — DONE (15, all `art.py install --ruling`)
- RM_Cindermare B facings (east/north/south); def Graphic_Single -> Graphic_Multi.
- RM_Skarnix (ishvarith) C = gekkrith facings; def -> Graphic_Multi.
- RM_Drokattak (ombrathia) C = v2 over the old set.
- RM_Etchcap A/B/C -> `Etchcap/Etchcap_{a,b,c}.png` (fixes the Graphic_Random-on-a-file defect).
- RM_Wickwood A/B/C -> `RM_Wickwood/RM_Wickwood_{a,b,c}.png`, def -> Graphic_Random. Size NOT doubled again: 2.6~3.6 was applied at 11a821c18 for the same note.
- Old singles `Etchcap.png`, `RM_Wickwood.png`, `RM_Cindermare.png`, `RM_Skarnix.png` left in place, unread by the new graphic classes: the art guard refuses retiring an owner-kept picture with a mechanical reason, and refuses his words without one, so a move-retire has no legal form today.
- Donor rows (AA_/AB_/AG_) are not installed: no owned path until the port; picks recorded on ABYSS_SHEET_DONOR_PORT_1.

## Cuts — DONE
AA_ShadowCharger, AA_Thunderox removed from RM_Abyss.xml AND RUT_Abyss.xml; roster json evictions; port rows RM_Sirathia/RM_Velessith deleted from the item.

## Descriptions / labels rewritten — DONE (10 + 1 new)
Looked at each pick. Full rewrites to match the image: nevarithia (Darkbeast), ysvaltha (DuskProwler), lirrith (Murkling), aveluthia (NightMule), sesserith (Nightling), ombrathia (RM_Drokattak, def), ishvarith (RM_Skarnix, def). Final-look eye/colour edits: moravatha, ossumatha, olumetha. Donor rows live in the item's table.

## Jobs queued — DONE (32), `Transient/biome_ffar/abyss_sitting2_jobs_2026-10-05.json`
- 21 family recolours, derived per facing from his pick (`abyss_{moravatha,ossumatha,ysvaltha,lirrith,aveluthia,olumetha,sesserith}_v3_*`).
- 6 variants: giant glow globe, glowberry bush, glow globe (b/c_v2 each, derive_from the pick).
- 3 glowing-grass tints of his B/C/D (a/c derive_from; b failed the canon gate so it rides `reference`).
- 1 tree mushroom C re-render at 1024 (x4 size).
- 1 paddle vine (new AG_Septimum).
Every row carries his note verbatim as owner_note. sheet_row_overrides.json updated with the new job ids and the paddle vine name.

## AG_Septimum — DONE
New name **paddle vine** / `RM_PaddleVine` (plain descriptive, not the family style).

## Validation
validate_patch OK on the 4 edited defs. Abyss validation.py: all PASS after correcting its etchcap check (it looked for a single PNG under a Graphic_Random def, i.e. it encoded the defect).
run_selftests 185/188: selftest_art (scaled_review_gate, another agent's), ledger_lint (FOUNDRY shard behind origin), bridgetools tool_metadata. None touched here.

## Commits
(pending)
