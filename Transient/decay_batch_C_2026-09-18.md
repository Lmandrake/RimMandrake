# Queue Decay Verification — Batch C — 2026-09-18

## BIOME_ENRICHMENT_DESERT_WASTELAND_1
(1) Wants: place mutator/landmark kit into Desert (57.4% zero-mutator) + Wasteland (63.7%) from their own biome sheets; stated blocker: neither sheet names a concrete placeable defName kit.
(2) VERIFY: item file + ledger both show `block` ts 2026-09-10T02:17:06, no activity since. `rimflow show` not re-run (not in my spot-check batch) but no later ledger line touches this id.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: items/BIOME_ENRICHMENT_DESERT_WASTELAND_1.md:26-66 (kit has no real defNames); ledger ts 2026-09-10T02:17:06 "no concrete placeable defNames... needs owner to name mutators"; unrelated but relevant — `f082d783e` (2026-09-18) ordered a region re-audit that may shift biome %s again, not yet run.
Action: leave open; owner still needs to either name concrete TileMutatorDefs or rule that density-of-existing-mutators satisfies the ask.

## DESERT_WRAPS_ART_COMMISSION_1
(1) Wants: original desert-wrap apparel (full body-type matrix) + devolved head shape; stated blocker (item file/queue): "Awaits the owner's pick... do not build."
(2) VERIFY: `infrastructure/state/queue/FOUNDRY.md:435-436` still renders `state: doing (BLOCKED)`. But ledger notes ts 2026-09-10T05:57:04Z and 05:59:13Z (seat BENCH) record the owner's actual picks: "ALL FOUR wrap styles ship... 'stunning, we need all of them'" and "BOTH head shapes ship... Style-pick block fully resolved: 4 wraps + 2 option heads; full body-type matrix buildable now." No later ledger event moves the state or starts the build.
(3) Verdict: **STALE_BLOCKER**, CONFIRMED. EVIDENCE: ledger ts 2026-09-10T05:57:04Z "ALL FOUR wrap styles ship"; ledger ts 2026-09-10T05:59:13Z "full body-type matrix buildable now"; items/DESERT_WRAPS_ART_COMMISSION_1.md:59 still says "Awaits the owner's pick... do not build" (never updated).
Action: item file and blocked state are stale — the pick was made 8 days ago; unblock and start the full body-type × direction matrix build.

## JAWA_PATCHES_SPLIT_1
(1) Wants: triage/split Jawa_Patches into RUT/RSW/RM + extract 5 straddle packs; stated blocker: straddle extractions ride inside `MOD_CONSOLIDATION_SPRINT_1`, which is unclaimed.
(2) VERIFY: physical split confirmed executed at `2385af29` (2026-09-04), `src/SPLIT_Phase3/Jawa_Patches` re-confirmed empty (0 files) 2026-09-09. `rimflow show MOD_CONSOLIDATION_SPRINT_1` → state **ready**, still unclaimed today.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: commit `2385af29` (split executed); `rimflow show MOD_CONSOLIDATION_SPRINT_1` → "ready row - needs offline"; items/JAWA_PATCHES_SPLIT_1.md:110-123 (gate named, "do not start standalone").
Action: no action available under this item alone; unblocks only when `MOD_CONSOLIDATION_SPRINT_1` is claimed — that's the owner's scheduling call per the item's own note.

## TREE_GRAPHICS_OWNERSHIP_1
(1) Wants: own tree art at our scale (sweetline trees), immunize against BetterTrees/Comigo/Maal rescaling; stated blocker (historical): art generation blocked on Codex contention, then on an owner art-pick.
(2) VERIFY: item file's own "Owed #1 RESOLVED 2026-09-18" section says all 14 candidate PNGs landed as a `Graphic_Random` rotation, canvas grown to 10 cells, per direct owner ruling ("I absolutely love ALL of them... Make that sweetline tree ten cells wide"). Confirmed via `git log`: commits `0d9116326` "Land all 14 RUT_SweetlineTree art candidates as a rotation, grow canopy to 10 cells" and merge `539448f8e`, both today.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: commit `0d9116326` (2026-09-18); items/TREE_GRAPHICS_OWNERSHIP_1.md:114-165 ("Owed #1 RESOLVED... Owed #2... still open"); item's own criteria checklist still has 2 of 3 boxes unchecked (live spawn verify, world placement).
Action: real work remains — live spawn verify (dev-trigger, BetterTrees-immunity log check) and the world-placement pass are still owed, not decayed.
**Note per brief**: the task's premise "TREE_TRIO_RETIRE_1" (all three tree-retexture mods OUT once vegetation regen lands) does **not exist** as a ledger item or item file — `grep`/`git log --grep` across the whole ledger and items/ found zero hits. If the owner actually ruled this, it needs filing; until then it can't be verified against anything and reads as a not-yet-recorded premise, not a decayed one.

## DROID_ORACLE_VOICE_DESIGN_1
(1) Wants: design (not build) four droid Oracle consumers (W/B/O/R) with prescribed fallbacks; stated blocker: deliberately dormant per owner card 14 ("design now, do not build") — only his read of the doc un-parks it.
(2) VERIFY: `rimflow show` confirms current state `doing BLOCKED`, same reason as the 2026-09-10 ledger block note. Design doc reconciled against the built `OracleClient.cs` (§2.6) same session. No later ledger activity.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: ledger ts 2026-09-10T02:32:36Z "dormant... nothing closes it but the owner's read"; items/DROID_ORACLE_VOICE_DESIGN_1.md:78-97 (7 open owner questions); `rimflow show` current state matches.
Action: no decay — correctly parked, waiting on the owner's read, unchanged in 8 days.

## GRAFFITI_PUNK_IDEOLIGION_SCOPE_1
(1) Wants: widen base RM Graffiti into a punk/urban + ideoligion-sigil system; stated blocker: design draft awaiting owner ruling on forks F1-F10.
(2) VERIFY: `rimflow show` confirms `doing BLOCKED`, identical reason to the 2026-09-10 block note. No supersession found — none of the task's listed supersessions (painterly art law, canon library, proposals suite, liquids framework, worldgen click, Iriaz, settlement roster) touch graffiti/ideoligion content.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: ledger ts 2026-09-10T02:32:39Z; items/GRAFFITI_PUNK_IDEOLIGION_SCOPE_1.md:159-193 (F1-F10 + 5 named owner questions); `rimflow show` unchanged.
Action: no decay; still needs the owner's fork rulings before a build item is filed.

## MORNING_RULING_BATCH_1
(1) Wants: 9 staged decisions from the 2026-09-09/10 sitting (wraps pick, crystal ingest, art-default flip, homeless-486 bucketing, 17 Move mappings, garb-sheet pick, gemini-quality thumbs-up, fish qs, mech-presence table); stated blocker (last note, ts 2026-09-10T14:19:50Z): "Remaining open in this batch: (1) wraps, (6) garb sheet, (7) gemini quality."
(2) VERIFY: (2)(8)(9) confirmed RULED same day (crystal ingest, fish, mech table — each spun into its own closed/executing item). (4)(5) resolved same day per the 14:19:50 note. **(1) wraps is actually stale in this batch's OWN tracking**: two notes on `DESERT_WRAPS_ART_COMMISSION_1` itself, ts 05:57:04Z and 05:59:13Z — *before* the 14:19:50Z note that still lists "(1) wraps" as open — record the owner picking all 4 wrap styles + both heads. (6) garb sheet and (7) gemini quality: no ledger line anywhere names them resolved; `rimflow show MORNING_RULING_BATCH_1` → still `proposed`, no item file.
(3) Verdict: **NEEDS_OWNER** for (6)/(7), **UNCERTAIN** overall (the batch's own bookkeeping contradicts itself on (1)). EVIDENCE: ledger ts 2026-09-10T14:19:50Z ("Remaining open... (1) wraps"); ledger ts 2026-09-10T05:57:04Z/05:59:13Z (wraps actually ruled, contradicts the later note); `rimflow show MORNING_RULING_BATCH_1` → state `proposed`.
Action: (1) can be struck off this batch (already ruled, see DESERT_WRAPS_ART_COMMISSION_1 above); (6) SW background-garb pick and (7) gemini-quality thumbs-up genuinely still need the owner — no evidence either was ever answered.

## EXPLOSIVE_PLANT_GROWTH_1
(1) Wants: water-soaked plants visibly grow, with a designed terminal moment + custom mod actions; stated blocker (last doing-audit, ts implied 2026-09-13): TPS perf benchmark unrun, per-biome variant roster still PROPOSED.
(2) VERIFY: item file confirms design fully ruled 4/4 (2026-09-10 morning sitting: injury/knockdown ceiling, soak-farming, Nectar Flush IN, stepped default). No ledger entry after the 2026-09-13 doing-audit note.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: ledger ts 2026-09-10T07:46:18Z (all 4 owner questions RULED); ledger ts 2026-09-13T09:17:49Z ("doing-audit: open work = TPS perf benchmark (unrun) + per-biome roster still PROPOSED"); items/EXPLOSIVE_PLANT_GROWTH_1.md:27-38.
Action: real work remains (perf benchmark before any build promise); not decayed, just not yet started.

## RUT_SCAVENGEREVENTS_BUILD_1
(1) Wants: port 8 Mo'Events mechanics as native IncidentWorkers, retire mlie.moevents; stated blocker: 7/8 built+deployed but never proven-fires (needs a restart), RescueTraitor needed a design call.
(2) VERIFY: owner ruled 2026-09-11 "Cut it, ship 7/8 events without a rescue-flavor incident" — RescueTraitor blocker resolved. A 2026-09-12 code-review pass (DIRTY_CODE_REVIEW_STANDING_LOOP_1) found and fixed a real bug (empty corpse in ShipBreak) and explicitly restates: "none of these 7 workers have ever been proven-fires in a live load — that verification is separately owed."
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: ledger ts 2026-09-11T04:49:16Z (RescueTraitor cut, ruled); ledger ts 2026-09-12T05:02:15Z ("none of these 7 workers have ever been proven-fires... separately owed"); items/RUT_SCAVENGEREVENTS_BUILD_1.md:169-172.
Action: proven-fires bridge test for the 7 is still the real remaining gap, unchanged since 2026-09-12; retirement of mlie.moevents still gated on it.

## VQE_ANCIENTS_CURATION_1
(1) Wants: 6-part curation of VQE Ancients (cut 3 archite abilities, keep 2 stat genes, audit Empire patch, relabel quest strings, verify site-tile biome at fire time, feed 4 creatures into dungeon-guardians roster); stated blocker: step 5 (site-tile check) can't run until the quest self-fires (~day 30-118), currently day 1.8.
(2) VERIFY: steps 1/3/6 confirmed done (ledger + item file); step 4 (string relabel) landed 2026-09-13 (`VQEQuestText_AreForsaken.xml`, validate_patch clean 7/7); step 2 needs no action (never touched, confirmed).
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: ledger ts 2026-09-13T07:53:07Z (step 4 done, 9 phrases relabeled); items/VQE_ANCIENTS_CURATION_1.md:53-59 (step 5 genuinely not-yet-fireable); ledger ts 2026-09-10T22:25:44Z (steps 1/3/6 verified).
Action: step 5 is a real, time-gated wait (not a stale blocker) — flag when the quest actually fires (day 30-118) rather than chase it now.

## GOO_BOOM_COMMISSION_1
(1) Wants: commission ONE fleshy Assailant-dungeon boom creature (RUT_Vhessk) replacing the whole cut boom family; stated blocker (last note, ts 2026-09-10): design brief done, 9 open calls needed owner ruling before build.
(2) VERIFY: all 9 calls confirmed RULED same day (2026-09-10, "owner cards, recommendations accepted" — v1 zero-C# worker, stat package, Boomalope body reuse, glow painted-in, spawn wiring deferred to ASSAILANT_DUNGEON_BUILD_1, brief location). `rimflow show` still returns `doing BLOCKED` with the pre-ruling reason text (stale reason string) — but the item's own file shows the rulings landed and says "UNBLOCKED: build phase is FOUNDRY's."
(3) Verdict: **LIVE**, CONFIRMED (build genuinely not started — no defs/art/C# committed under this item anywhere in `git log`). EVIDENCE: items/GOO_BOOM_COMMISSION_1.md:63-73 ("all 9 open calls RULED... UNBLOCKED: build phase is FOUNDRY's"); `rimflow show GOO_BOOM_COMMISSION_1` → reason text still reads the pre-ruling "8 open calls" language (stale reason string, not a stale block — the block state itself should have flipped to ready/doing-unblocked).
Action: rulings are in; nobody has claimed the build. Recorded reason string is stale cosmetically but the underlying work (ThingDef/PawnKindDef, art) is genuinely unbuilt — treat as ready-to-build, not still-needing-owner.

## RESEARCH_TRIO_RETIRE_1
(1) Wants: retire steppingstones + als.gravtech(.bc), re-validate the research recost; stated blocker: 17 live `ResearchProjectDef`s (several carrying dated 2026-09-01/09-04 owner rulings) would be silently deleted — needs an owner pick among port/accept-loss/counter-patch.
(2) VERIFY: `STAT_NORMALIZATION_AUDIT_1`'s Wave 3/Wave 4 rulings (2026-09-11) closed the AUDIT item itself but explicitly say "execution lives in... RESEARCH_TRIO_RETIRE_1" — i.e. the parent audit closing did NOT rule the 3-route question this item escalated. No ledger event since the 2026-09-11T07:10:24Z block.
(3) Verdict: **NEEDS_OWNER**, CONFIRMED. EVIDENCE: ledger ts 2026-09-11T06:36:39Z ("ALL FOUR WAVES now ruled; execution lives in... RESEARCH_TRIO_RETIRE_1" — the wave ruling is procedural, not the route pick); ledger ts 2026-09-11T07:10:24Z (3 routes laid out, "Owner AFK, not FOUNDRY's to pick"); `rimflow show` confirms `doing BLOCKED`, same reason, 7 days idle.
Action: genuinely still needs the owner to pick port / accept-loss / counter-patch for the 17 rows; not decayed, not superseded.

## BMT_FAUNA_ABSORPTION_1
(1) Wants: port 71 (68 unique) `BMT_`-prefixed creatures from the `biomesteam.*` family into RSW tier, then retire the 3 donor mods; stated blocker: 3 gates before retirement is safe (regenerate a generated cast-patch file, resolve 7 straggler defNames, replace a donor-only compiled GameCondition).
(2) VERIFY: port itself confirmed complete (68/68, validate_patch clean). Gate 2 (7 stragglers) RULED CUT by the owner 2026-09-11. Gate 3 (SporeCloud) has a built replacement as of TODAY (`ROT_SPORECLOUD_PORT_1`, commit `44b4f3549`, 2026-09-18) — but its own closing note is explicit: **"Do NOT clear BMT_FAUNA_ABSORPTION_1 gate 3 until that live proof actually runs"** — the quicktest dev-trigger proof has not run. Gate 1 (BiomeCast_Ashkarr.xml regenerate) has no evidence of having run.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: ledger ts 2026-09-18T01:25:53Z ("OWED: live quicktest proof... Do NOT clear... gate 3 until that live proof actually runs"); ledger ts 2026-09-11T15:59:37Z (gate 2 ruled CUT); items/BMT_FAUNA_ABSORPTION_1.md:107-150 (3 gates named).
Action: do not treat gate 3 as clear — the mechanism was built today but is explicitly unverified live; gate 1 (regenerate) still has no evidence of execution either.

## JAWA_PHRASING_RSW_TIER_CARD_1
(1) Wants: owner ruling on whether generic "Jawa" phrasing is allowed in RSW-tier text or must stay RUT-only; stated blocker: needs:owner, single filed event, no item file.
(2) VERIFY: `rimflow show` confirms `proposed`, 1 history event only (the file event, 2026-09-11T20:25:26Z). No later mention anywhere in design/ or infrastructure/state/ (grep across both trees found only the reboot-handoff doc restating the same open question, nothing resolving it).
(3) Verdict: **NEEDS_OWNER**, CONFIRMED. EVIDENCE: `rimflow show JAWA_PHRASING_RSW_TIER_CARD_1` → "proposed... history (1 events)"; ledger ts 2026-09-11T20:25:26Z (only event); grep of design/ + infrastructure/state/items/ finds no resolving reference.
Action: genuinely still open, not decayed — nobody has answered it in 7 days; still a live card question for the owner.

## WORLDMAP_FINAL_REVIEW_1
(1) Wants: studio-grade final worldmap review ("is this THE map?") — measured audits + STARE + text pass + verdict report; stated blocker: needs owner (report done, awaiting his read), ts 2026-09-13T09:17:41Z.
(2) VERIFY: all 4 phases delivered by 2026-09-11/12 (`Transient/final_review/WORLDMAP_REVIEW_REPORT.md`, provisional verdict YES pending owner read). The task's own supersession list confirms the owner has since actively been ruling on this report's findings TODAY: "worldgen click DONE (canonical save 2026-09-12)" and "live settlement roster is canon 2026-09-18" are both rulings recorded under `WORLDMAP_DOCS_PASS_1` (2026-09-18), directly answering punch-list items from this report (settlement count 96-vs-120, worldgen-click gate docs). Sarlacc-landmark punch item explicitly noted as "superseded by GAPING_DOOM_SITE_1 + SARLACC_WORLDMAP_RELOCATE_1 in flight" — active follow-through, not neglect.
(3) Verdict: **LIVE**, CONFIRMED. EVIDENCE: `rimflow show WORLDMAP_FINAL_REVIEW_1` → "doing... needs owner"; ledger ts 2026-09-18T17:58:53Z (`WORLDMAP_DOCS_PASS_1` rulings 2-5, citing this report's findings by name); ledger ts 2026-09-18T18:05:40Z (rulings 6-9, same pass, region re-audit ordered).
Action: not stale — the owner is actively working the punch list via `WORLDMAP_DOCS_PASS_1` card sittings as of today; this item stays open correctly until the final "is this THE map?" verdict is recorded, which per (h) still owes a post-restart region re-audit.
