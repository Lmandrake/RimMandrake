# BENCH_REBOOT_HANDOFF_202610230105 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610220912`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Order (owner, 2026-10-22): cap five helpers, light orchestrator, handoff at ~50% context — his words:
*"Stay a light orchestrator. Handoff only when your context gets to around 50%, and I'll restart you then."*
That handoff never fired (this session auto-compacted at 00:21Z with none; this file was written afterwards
by a helper from the transcript). **The seat cannot see its own context fill: hand off on a proxy you can see**
(a closed helper wave, ~6 h, or `compaction_check.py`), not on a feeling of 50% (filed: lessons
20261023T010455Z-BENCH-handoff-at-50-context-does-not). And the owner's pick for **2026-10-23 is a
no-blocking day** (`--by-card "Which experiment first? → A no-blocking day, then re-measure"`, 23:23Z):
helpers auto-dispatched, delegated calls made per `design/RimMandrake/delegation_policy.md` and logged
`--why "delegated: <class>"`, question cards ONLY for its §2 list, never asked while a helper slot is empty
or a helper result is unread; at day's end rerun the bottleneck measurement and compare with
`Transient/pile_2026-10-22/harness_research/bottleneck_measure.md` (423 min blocked in cards on 10-22).

## What the owner should see

- **Tonight's walk is staged:** RimWorld UP on `RM_fw_walkthrough_20261022b` (DLL c963216c28), map C, paused,
  camera on stop 1, overflow OFF, small list fw_gss_sitting; bridge HELD by BENCH "holding for the owner's
  walkthrough (save b)". Script: `D:\Luke\dev\RimMandrake\Transient\pile_2026-10-22\walk_tonight.md`
  (11 stops). Original save `RM_fw_walkthrough_20261022.rws` untouched.
- **His saved Mod Settings keep `joinFittings=false`**: the joint fittings he picked will not show in his game
  until that setting is switched on (default is now ON; his saved value wins). Not on the walk sheet.
- **Owner words held only by the compaction summary until now** (verbatim, 2026-10-22):
  *"Foundry also has some of the flowworks items. It's been told to prioritize them."* (15:47Z) ·
  *"Ok, I'd like you to make a deep plan now for today's work. To advance FlowWorks to the most ready state
  possible today without human interaction, what can you do? I can occasionally answer question cards or
  review a few art png's (collections) on the phone but not much. So what can we do to get the functionality
  as ready as possible to walk through it live together tonight productively? Take risks, be bold, let's get
  things working! And make that live walk as dense and productive as possible. Make that plan, give me options
  in a question card, and then let's follow it!"* (15:31Z) · harness request *"Make a subagent do web research
  on agent systems like Devin …"* (22:45Z; full text in the conversations record).
- **Pond-shallowing vs drain order** (fixer G, 22:33Z): the "ponds shallow out before mud" setting is ON by
  default, so a real lake in play never uses the drain-order fix. May need his ruling. Not filed.
- **Scrapper shut gates C/D are installed but never drawn** (material picture always wins); showing them is a
  code change only if he wants Scrapper to outrank material.
- **Compaction-loss audit** for his question: `D:\Luke\dev\RimMandrake\Transient\pile_2026-10-22\compaction_loss.md`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS` — picks A-D (bolder caps) and pumps E/F/G installed; needs his in-game look; NEXT: show pipes/pumps at the walk's fittings stop and close it on his word.
- `walk tonight (RM_fw_walkthrough_20261022b)` — save built, game UP paused at stop 1, bridge held by BENCH; NEXT: run `Transient/pile_2026-10-22/walk_tonight.md` with the owner and record each decision as data.
- `walk-rebuild helper a95636a2fbad20c90` — finished (76ea7a6f1f, final state in walk_rebuild.md); NEXT: report "save b ready, paused at stop 1" to the owner (promised by BENCH 23:23Z).
- `joinFittings saved setting` — owner's config has false; NEXT: ask him before the walk to tick joint fittings on (or switch it via the Mod Settings bridge call with his OK).
- `NO_BLOCKING_DAY_2026-10-23 (HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM)` — picked by card 23:23Z; NEXT: run 10-23 without blocking cards, then rerun the bottleneck measurement and compare to 10-22.
- `DELEGATION_POLICY_BUILD_AGENTS_ASK_AGENTS` — policy + art_judge_brief written (453c73eefe); daily digest script not built; NEXT: build the delegation digest and show him the policy on the phone.
- `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` — stages 0-3 built, switch OFF, fuel numbers researched; NEXT: run `sheet_overflow_proof.py --fresh-map` live (stage-4 acceptance) incl. fuel-fire and mixed-liquid rows.
- `fuel spill leftovers` — propane 30% instant flash and gasoline cold/roof evaporation not built (fuel_spill_research.md); NEXT: file them as one item under CANAL_OVERFLOW.
- `pond shallowing vs drain order` — fixer G finding, unfiled; NEXT: file it as a FOUNDRY/BENCH item with the owner-ruling question.
- `RSW_Rycrit` — no def, empty texture folder (art helper 15:44Z, unfiled); NEXT: search src/ and the roster, then file or drop it.
- `spare test machine` — owner: *"There is a machine we could use."*; bottleneck helper skipped it; NEXT: ask him which machine and fold it into the test-service (R1) follow-up.
- `live checks owed` — CAUSEWAY, DRAWDOWN, RAILING, SETTINGS_SEARCH, SUSPENSION_BUTTONS, GLOWTANK, walk_gaps_proof, pipe_levelling_perf_proof (needs a 325x325 map no bridge tool makes) built/offline only; NEXT: put them on the 10-23 belt after the walk.

## Traps learned

- Transcript extractors (`compaction_check.py --extract`, `conversations.py`) drop mid-turn owner messages and all card answers; read the raw jsonl (filed: lessons 20261023T010455Z-BENCH-transcript-extractors-drop-owner-words-compaction).
- "Handoff at ~50%" cannot fire by feel (filed: lessons 20261023T010455Z-BENCH-handoff-at-50-context-does-not).
- A side clone loses the repo-local noreply identity; 2b85094eb0 went to the public repo with the gmail committer (filed: lessons 20261022T160123Z-BENCH-pushing-from-side-clone-bench-when).
- An open AskUserQuestion card blocks the orchestrator: 423 min on 10-22 (filed: lessons 20261022T232137Z-BENCH-askuserquestion-card-blocks-orchestrating-seat-2026).
- After a rebase moves the FlowWorks DLL, rebuild from committed HEAD; `./publish` now does it itself, 8ead9dd3b1 (filed: lessons 20261022T232612Z-BENCH-since-8ead9dd3b1-publish-lands-committed-mod).

## Closed since the last handoff (8)

- `ART_SHEET_FIX_SIBLING_KEEPS_UNSEEN` — c87bbf460392
- `TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM` — d03ca752f4
- `PIT_COVER_WIDEN_PLANKS_BEAR_BOOTS` — 41fb948b5e
- `DRILL_PLACEMENT_ENFORCE_NO_DRY_HOLES` — 41fb948b5e
- `LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM` — 0ab8470911
- `MOAT_LEVEL_DIAGNOSE_HALF_METRE_VANISHES` — 0ab8470911
- `BLEED_WELL_STRINGS_RENAME_TAP_RETIRED` — f68f12652e
- `PUBLISH_DLL_FIX_BINARIES_STOP_ARGUING` — 8ead9dd3b19e

## Filed and still open (13) — the next seat's queue

- `WALL_REACH_TUNE_REBUILDS_TENFOLD` — Wall-aware reach map rebuilds ~900-1000 times per 1000 ticks on a quiet map (60-tick throttle should cap ~133); ~2.3 ms each = ~2 ms/tick. MEASURED on
- `PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS` — Draft FlowWorks pipe art: real 3-/4-way fittings, one coupling per joint, matched end cap per look, three more pump looks (review sheet, nothing insta
- `CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP` — Raiders at a 4 m sheer ring never fill (RAIDERS_TRENCH A3): raid_trench_proof --direct --depth 8 on 41fb948b5e, 3 AssaultColony gunners stood at the l
- `DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE` — deep_lake_proof live on 41fb948b5e (72x72 painted lake, lakeDepthScale 2, stock set to 25%): DL_shallow_dries_first FAIL maxDryBed=13 > minWetBed=12 (
- `OVERFLOW_DIAGNOSE_FIRST_WET_RUN` — First live run of sheet_overflow_proof (CANAL_OVERFLOW stage-4 rows) on deployed FlowWorks 3be0f5c66f, fresh map, tier 14: 5 PASS (FILLIN_HOMELESS_SPI
- `SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY` — REGRESSION (PASS 2026-10-16 -> FAIL today): liquid_checks L5_switched_off_hose_spills on deployed FlowWorks 3be0f5c66f, tier fw_gss_sitting: an Outflo
- `SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING` — SUSPENSION_BRIDGE A7 half: with RM_SuspensionSettings.suspensionBridgesBuildable set False (jawa/mod_settings_field valueAfter False, read back False)
- `RAILING_MATERIAL_FIX_MADE_OF_NOTHING` — RM_MapComponent_SuspensionBridges.PlaceRailing (RM_MapComponent_SuspensionBridges.cs ~1206): RM_SuspensionRailing is madeFromStuff (stuffCategories, c
- `SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND` — FlowWorks Mod Settings search (f68f12652e) does not match a visible checkbox's own words: typing 'Liquid crosses', 'crosses between', 'huge network' o
- `GLOWTANK_DRINK_DIAGNOSE_DRY_BESIDE_THE_SEA` — GLOW_TANK_LIQUID_FEED_1 A2 live FAIL (deployed FlowWorks ee9fa61fbc + LuminousPigment, tier fw_gss_sitting): an RM_GlowTank (powered, seeded, culture 
- `TIMBER_LEAF_DIAGNOSE_UP_AND_INVISIBLE` — A raised TIMBER drawbridge leaf with no winch draws nothing (ProofLeaf: raised 3/3, hinge A, tip=True) while a raised steel leaf with a winch draws it
- `DELEGATION_POLICY_BUILD_AGENTS_ASK_AGENTS` — Delegation policy: agents decide nearly everything, art included, by asking another agent against drafted prose constraints/requirements; owner then r
- `HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM` — Measure from logs whether live game time is the limiting factor (what would 2x in-game test throughput buy with LLM delays unchanged?) and whether per

## Commits

```
b2bebee51f conversations: catch-up 1 record(s)
375a003ccf Compaction loss audit of BENCH 5453bc27 (pinned); 3 lessons (2 new, 1 written 10-22 but never committed)
7909ef9617 Ledger: BENCH/OWNER shards from today's card rulings and delegated calls
76ea7a6f1f Walk rebuild: final state (save b on c963216c28, paused at stop 1, bridge held by BENCH)
63d3f40aee SHOKKWEAVE_RETIRE_EGGS_MOVE_TO_HUTTS implemented (L0); deploy + live owed
c186eb52ec Ledger: file SHOKKWEAVE_RETIRE_EGGS_MOVE_TO_HUTTS, drop SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1, clean marks
2234d07e7a Cut mandrake.rut.shokkweaveeconomy; egg broker + Wildsteam weavers now in UtinniPatches (Biome card 5)
b93cf9984a Art ledger: drop my own three malformed Shyrack _4 events (unpushed)
2968e80902 Art ledger: Shyrack _4 live events carry a mechanical reason (rename, bytes unchanged)
151ee3c9b8 Art ledger: Shyrack_Flying_44 -> _4 live events (owner card 14)
72378e3a1d Webwork driver mock: route to the chain models instead of the generic MockGame Mock run was 1 PASS/11 FAIL/75 UNMEASURED (generic mock had no jawa/static_call: harness fault). Now 75/0/3; the 3 UNMEASURED are honest.
31e1a98437 Regenerate Empire/Wildsteam/Droids cast from notes (owner card 13) Other 8 factions also drift from the generator; not touched.
0edc65b1f1 Shyrack 4th flying frame renamed _44 -> _4 (owner card 14) frameCount 4 never resolved the _44 files; bytes unchanged, art ledger already-live.
5bc68218ff Ledger: ROACHES_MOD_RETIRE_SAVE_STILL_NAMES_ONE implemented
53e855bd84 Biome cards 12-14 answered
b0a6257df4 GPT review findings: TheRot verified (5 fixed in 292c84956), owner Q11
e4e911ff5d Cut mod rut.rustcathedralroaches (owner, Biome card 4 -> cut roaches mod now)
292c849567 TheRot: GPT deep review fixes (a destroyed hwelgrue releases its passenger, stockpiled pawns are not swallowed, one mat-root heat push per room per sweep, master switch gates retaliation; draft bar 4 advance is 90,000 ticks, not 36,000) Selftests 4/4; DLL rebuilt. Live-only to prove.
fcdbd72ace Biome cards 7-9 answered by card
fc2682bacb Delete 5 dead patches + 3 dead JawaWorld_BiomeMix entries (owner card 2, 2026-10-22)
... 329 more: git log --oneline aa7d50ba10..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     holding for the owner's walkthrough (save b)

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/pile_2026-10-22/art_helper_day.md   BENCH art helper (10-22), unpinned edit
 M Transient/pile_2026-10-22/belt_failures.md   BENCH belt/fixer helpers (10-22)
?? deployed/config/ModsConfig.swap-active.json   BENCH walk tier marker — KEEP until modset_builder.py --restore
?? "src/RimMandrake/FlowWorks/northstar/--mock-faults gc_every"   BENCH proof-author helper: junk files from a mis-quoted argv; delete
?? "src/RimMandrake/FlowWorks/northstar/--mock-faults no_link"   BENCH proof-author helper: junk files from a mis-quoted argv; delete
?? "src/RimMandrake/FlowWorks/northstar/--mock-faults old_deploy"   BENCH proof-author helper: junk files from a mis-quoted argv; delete
?? "src/RimMandrake/FlowWorks/northstar/--mock-faults slow"   BENCH proof-author helper: junk files from a mis-quoted argv; delete
?? "src/RimMandrake/FlowWorks/northstar/--mock-faults small_map"   BENCH proof-author helper: junk files from a mis-quoted argv; delete
?? src/RimMandrake/FlowWorks/northstar/deep_lake_proof_result_20261022T153940.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T134328.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T134727.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T134835.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135233.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135310.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135339.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135449.json   BENCH belt helper (live proof output)
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135550.json   BENCH belt helper (live proof output)
```

