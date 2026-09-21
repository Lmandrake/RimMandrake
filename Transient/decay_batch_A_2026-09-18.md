# Queue Decay Verification — Batch A — 2026-09-18

## LIVESTOCK_STARTER_TRIO_1
Wants: build onnik+karrask+moornak trio; blocked 2026-09-10 on owner ruling for moornak's spec (simple vs richer).
VERDICT: STALE_BLOCKER — CONFIRMED
- EVIDENCE: ledger 2026-09-10T05:26:10Z BENCH note: "OWNER RULED 2026-09-09: the RICHER moornak spec ships"
- EVIDENCE: `src/RimStarWars/SWBestiary/Defs/Livestock/ThingDefs_Animals/ThingDefs_Onnik.xml` and `ThingDefs_Karrask.xml` exist (onnik/karrask built, commits `4a0fc3a2a`/`ba4fadecb`)
- EVIDENCE: no moornak ThingDef/PawnKindDef anywhere (`find src -iname "*moornak*"` returns only 3 mockup PNGs under `src/RimStarWars/SWBestiary/art/Livestock/mockups/`)
Parent should: clear the needs:owner block (owner already ruled 2026-09-09) and re-file as LIVE work for FOUNDRY to build the richer moornak per the ruling; onnik/karrask are done.

## MENTALBREAK_DESCRIPTION_UNUSED_1
Wants: cut/wire MentalBreakDef.description field, which FOUNDRY found is never authored or read; owner ruled 2026-09-05 to cut it, conditional on validation.
VERDICT: DONE_UNRECORDED — CONFIRMED
- EVIDENCE: `src/RimMandrake/Utils/gen_pawn_flavor_phase2_apply.py:393-426` MentalBreakDef branch reads only label/beginLetter/recoveryMessage, never `p.get("description")`
- EVIDENCE: `infrastructure/output/pawn_flavor_phase2_prose_draft.json` — 33 of 33 MentalBreakDef rows carry no `description` key (measured via json parse)
- EVIDENCE: ledger 2026-09-05T04:48:33Z BENCH note: "OWNER RULING...CUT the field...VALIDATED same sitting"; not present in any live queue/*.md
Parent should: close the item — the cut is already in effect (code and data both confirm), nothing left to build.

## REOPEN_DESTROYS_CLEANCOUNT_STREAK_1
Wants: `reopen` in code_review_status.py deletes the JSON entry outright, resetting cleanCount/streak; owner ruled 2026-09-04 to preserve history (mark dirty, keep entry, add status field) instead.
VERDICT: LIVE — CONFIRMED
- EVIDENCE: `src/RimMandrake/Utils/code_review_status.py:626` `del data[rel]` still deletes the entry on reopen
- EVIDENCE: same file's own comment at lines 621-625: "this drops the entry's cleanCount...not a change to make inside a review pass" — deliberately left unfixed
- EVIDENCE: ledger 2026-09-05T04:48:36Z BENCH note: "OWNER RULING...PRESERVE HISTORY...schema gains a status field"; no commit found matching `--grep REOPEN_DESTROYS_CLEANCOUNT` or "status field"
Parent should: file/build the ruled fix (dirty-but-kept entry + status field) — the owner ruling is real and still unimplemented.

## DIRTY_CODE_REVIEW_STANDING_LOOP_1
Wants: a standing loop that keeps working through the DIRTY file backlog with code_review_status.py, wave by wave, no end state.
VERDICT: LIVE — CONFIRMED (working as designed, a standing loop is never "done")
- EVIDENCE: 109 ledger events for this id spanning 2026-09-03 → 2026-09-18 (today)
- EVIDENCE: 2026-09-18T03:33:45Z FOUNDRY note: "FlowWorks wave...full-file reviewed all 71 reachable dirty/never-recorded XML+C#+py files"
- EVIDENCE: 2026-09-18T02:54:40Z FOUNDRY note: "re-derived dirty count (git ls-files=1841 tracked, was citing stale 261/1867)" — loop self-correcting its own instrument
Parent should: leave it running — this is a standing loop, not a task with a close condition; no action needed.

## DESIGNATE_BATCH_OVER_DESIGNATES_1
Wants: DesignateBatch's wantThings loop designates EVERY Thing in a cell instead of only the type-appropriate one; owner ruled 2026-09-04 "FIX PROPERLY - filter by the designation's own target rules".
VERDICT: LIVE — CONFIRMED
- EVIDENCE: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchMapTools.cs:1347` `foreach (var t in map.thingGrid.ThingsListAtFast(c).ToList())` — no `dd.CanDesignateThing(t)` filter, adds a Designation for every Thing found
- EVIDENCE: `git log --grep CanDesignateThing` across the file's whole history returns nothing; no commit found matching `--grep DESIGNATE_BATCH_OVER_DESIGNATES`
- EVIDENCE: ledger 2026-09-05T04:48:28Z BENCH note: "OWNER RULING...FIX PROPERLY - filter by the designation's own target rules"
Parent should: file/build the ruled fix — add a `dd.CanDesignateThing(t).Accepted` (or equivalent) check before `AddDesignation` in the wantThings branch; still unbuilt.

## BRIDGETOOLS_TILE_LAYER_DROPPED_1
Wants: bridgetools tile resolution (flagged during wave30 GroupTools review) drops layer/surface id, risking wrong-layer writes; owner ruled 2026-09-04 "FIX - thread the layer/surface id through".
VERDICT: DONE_UNRECORDED — UNCERTAIN
- EVIDENCE: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGroupTools.cs:570,661,686` all construct `new PlanetTile(tile, grid.Surface)` — surface threaded, not the bare int→PlanetTile implicit conversion (grep of all 19 `new PlanetTile(` calls repo-wide found none using bare int)
- EVIDENCE: git blame on `JawaBenchGroupTools.cs:570` dates the surface-threading to `948c33993` (2026-08-26), BEFORE the item was even filed (2026-09-03) — so either the review flagged a since-superseded snapshot or a different call site
- EVIDENCE: `JawaBenchWorldTools.cs:17-90` carries an explicit multi-PlanetLayer model (`layerId`, `grid.PlanetLayers`) already present at `b1943aa93` (2026-08-19), also pre-dating the item
Parent should: re-verify with the original reviewer's exact file/line (not just the title) before closing — current code shows no unguarded int→PlanetTile path, but I could not confirm this is the exact line the wave-30 review meant.

## HELIX_TELLUROX_SHELL_LOAD_CRASH_1
Wants: fix HelixTellurox's alleged mod-load-crash-to-Core-only plus a null butcherProducts NRE in RSW_TelluroxShell corpse-gen.
VERDICT: DONE_UNRECORDED — CONFIRMED (the real defect); crash attribution OVERTAKEN (debunked)
- EVIDENCE: `git show 3468e2a0` — "Fix Tellurox butcherProducts: defName-as-element form, was the `<li>` custom-loader trap" — still present on disk at `src/RimStarWars/SWBestiary/Defs/HelixTellurox/ThingDefs_Races/Races_Tellurox.xml:67-69`
- EVIDENCE: ledger 2026-09-04T21:51:33Z BENCH note: the crash signature "fired in tonight's healthy 22-mod load with NO Tellurox active," traced to third-party `Invisible Conduit Continued`'s malformed About.xml, "harmless beyond log noise"
- EVIDENCE: ledger 2026-09-06T21:06:47Z FOUNDRY note (RED review): same crash string found in 7 logs including minimal-list runs with `grep -ic helixtellurox = 0` — "attribution is undermined"; last event on record, still claimed by OWNER since 2026-09-04T21:43:59Z with no close
Parent should: close the real defect (fixed+deployed) and drop the crash-to-Core-only framing from the title/attribution — it was never this mod's fault; only housekeeping (release the stale OWNER claim, optionally confirm with one more live relaunch) remains.

## ANTIQUITIES_TREE_BUILD_1
Wants: build Antiquities slice 1 (research tree + items + reading loop) per `design/Jawa/antiquities_design.md`; item's own md already narrates it live-verified DONE 2026-09-04 with 3 more bugs found+fixed 2026-09-05, deploy/re-review owed at next shutdown window.
VERDICT: DONE_UNRECORDED — CONFIRMED (fully landed, not just claimed)
- EVIDENCE: `src/RimUtinni/Antiquities/Source/JobDriver_ExamineAntiquity.cs:91` `if (ticksLeftThisToil > 0)` — the interruption-exploit guard the item said was fixed-but-undeployed is present
- EVIDENCE: `src/RimUtinni/Antiquities/Source/JobDriver_ExamineAntiquity.cs:56` `AverageOfRelevantSkillsFor(...)` — the claimed-but-unwired skill-scaling fix is present
- EVIDENCE: `python3 src/RimMandrake/Utils/code_review_status.py check` → `CLEAN src/RimUtinni/Antiquities/Source/JobDriver_ExamineAntiquity.cs (clean at e758283f4 on 2026-09-11)` — the fresh post-fix review the item said was owed has happened; ledger's last event (2026-09-08T15:25:45Z BENCH) records `capability Antiquities function_rung=validated`
Parent should: close the item — slice 1 is built, live-verified, fix-reviewed and marked clean; slices 2-12 are separate unscoped future items per the doc's own build-plan table.

## UI_SHELL_SLICE_BUILD_1
Wants: build+ship RimUtinni Shell theme mod (button atlases, palette, loader/menu-bg art) with a RimThemes-coexistence gate proven live.
VERDICT: DONE_UNRECORDED — CONFIRMED
- EVIDENCE: item md's own final section (2026-09-05, dated last): "§4/§5 is now genuinely complete for what bridge automation can prove" — gizmo/float-menu panel non-reskin ruled a RimThemes-upstream limitation affecting every theme equally via a Cyberpunk control test, "Nothing to fix on the Utinni Shell side"
- EVIDENCE: md section "cold-load verdicts": "Loader art on a real cold load: MEASURED PASS", "Theme persistence across restart: MEASURED PASS" (twice, including across a mod-list-changing restart), "Runtime def presence: MEASURED PASS"
- EVIDENCE: ledger has no `close` event (last is `claim OWNER` 2026-09-05T21:40:00Z) — item is substantively finished but was never formally closed
Parent should: close the item — every criterion in its own checklist is checked off or explicitly ruled out-of-scope (upstream RimThemes limitation); only formal ledger closure is missing.

## NINEFOLD_DEBUG_GAME_READY_CRASH_1
Wants: `start_debug_game_ready`'s quicktest crashes RimWorldWin64 on the full 596-600 mod list; named after Ninefold's satiation log lines, which were the last lines before the crash. Criteria: a reachable quicktest map OR a confirmed named root cause.
VERDICT: NEEDS_OWNER — CONFIRMED
- EVIDENCE: item md's own reasoning (2026-09-06) already suspected Ninefold was not the cause ("this item's name should not be read as an accusation against that file")
- EVIDENCE: ledger 2026-09-08T21:11:49Z FOUNDRY note (3rd reproduction): "the crash tail names a specific culprit and it is NOT Ninefold. Stack: Caveworld_Flora_Unleashed.MapComponent_CaveFungus...dying inside GenSpawn.Spawn with six third-party prefixes/postfixes" — Ninefold lines are coincidental trailing log output, not the cause
- EVIDENCE: no `close` event in the ledger; criteria's OR-branch ("a confirmed, named root cause") is now met, but no remedy decision recorded (keep Caveworld_Flora_Unleashed and route around the debug quicktest vs. cut/patch it)
Parent should: re-title/re-attribute away from Ninefold (it's cleared), and take the Caveworld_Flora_Unleashed/GenSpawn.Spawn finding to the owner for a remedy ruling — the diagnostic half is done, the decision half isn't.

## ASSAILANT_DUNGEON_BUILD_1
Wants: build the Assailant's first-impact dungeon (thaw-gate, three-band layout, reveal beat); item's own watch-out says creative lock-in must happen WITH the owner, not solo.
VERDICT: LIVE — CONFIRMED (correctly blocked, awaiting a joint session; item file itself is stale on rulings already landed)
- EVIDENCE: ledger 2026-09-06T12:52:36Z FOUNDRY block: "creative lock-in owed with the owner...KCSG authoring/art/dialogue is a joint BENCH+owner session, not solo FOUNDRY build" — last event, still open
- EVIDENCE: ledger 2026-09-01T22:37:11Z + 2026-09-03/09-04 OWNER/BENCH notes: mechanical questions (thaw = QuestNode+map-trigger, power core = vanilla AIPersonaCore, tile-choice procedure) were already ruled and "SPEC LANDED, BUILDABLE, handed to FOUNDRY" — but the item's own md (`infrastructure/state/items/ASSAILANT_DUNGEON_BUILD_1.md`) still lists "thaw-trigger's concrete implementation" and "the power-core item's exact defName" under unresolved "held for the owner" bullets, not updated to reflect those rulings
- EVIDENCE: item md's `## verify`/`## criteria` checklists are 100% unchecked; no build has started
Parent should: leave it open (correctly gated on a joint creative session per its own doctrine), but first refresh the item md to reflect the 09-01/09-03 mechanical rulings already made so the next session doesn't re-litigate them as open questions.
