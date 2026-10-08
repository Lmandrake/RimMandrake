# BENCH_REBOOT_HANDOFF_202610081345 — READ FIRST on wake

Follows `BENCH_HANDOFF_202610080200`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
A review sheet can offer art that is not art: the venomvine "art" was a white pillar-limb image the generator returned for the wrong prompt (wired unreviewed at bbe171ebc), and 21+ plants shipped as flat-circle placeholders the owner then picked because sheets offered them as ordinary columns. Never trust a sheet column or an installed texture without looking. The placeholder guard (detector + sheet/install/lint/artpipe enforcement, 7d8586163..8b4347a96) and the wrong-subject sweep (Transient/biome_art_refresh_2026-10-07/wrong_subject_art.md) are the instruments now.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Morning brief with his open questions:** `D:\Luke\dev\RimMandrake\Transient\MORNING_2026-10-08.md`: Leaning Scrub Q1–4 (Iriaz H/I purged-yet-ticked, Scurrier E female-only, four donor-plant picks, deploy timing) and Vaalok (Aurrok-kept bytes block install; script ready).
- **Refreshed sheets of the six biomes he ruled tonight**, with new redraws flagged "NEW — awaiting your ruling": `D:\Luke\dev\RimMandrake\Transient\biome_art_refresh_2026-10-07\MORNING_SHEETS.md`. Rerun `Transient/biome_art_refresh_2026-10-07/refresh_ruled_sheets.sh` first; about 520 jobs were still pending at 00:30.
- **Canon gap census:** 104 of 115 canon creatures were never canon-regenerated, and 63 rows have a canon render on the sheet that was never installed (`canon_gap_census.md`). Sheets still unreviewed: Cauldron, Flooded Canyon, The Forge, The Rot, Weeping Stones, Wasteland, plus the rest.
- **Huge Things** is merged with TitanicCreatures (c954ccdca), and all GPT-review owner questions are ruled (9580bc4ad). NOT deployed, and it has never run in game. The combined walk plan is `Transient/huge_titan_walk_plan_2026-10-07.md`.
- **Shipped with a flag:** 15 cut creatures and 34 dependent defs were deleted outright on his card (d074b131a). Fourteen owner-kept textures of those creatures remain on disk, and retiring them needs his typed words.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `HUGE_THINGS_GPT_REVIEW_1` — closed at 9580bc4ad (review, triage, 9 FOUNDRY fix items, all owner questions ruled); NEXT: nothing, FOUNDRY works the 9 items plus TITAN_CAMPS_SCAVENGERS_EVENTS_1.
- `HUGE_THINGS_FOOTPRINT_1` — merged mod built, tested (75/75 mutants), not deployed; bridge held by FOUNDRY; NEXT: when the bridge frees, run `deploy_custom_mods.py --mod HugeThings --apply`, move `Mods/TitanicCreatures` aside, cold load, then build the walk save from `Transient/huge_titan_walk_plan_2026-10-07.md`.
- `OVERNIGHT_REDRAWS` — about 520 art jobs pending (priority 0, failed jobs requeued at -10; failed_jobs.md); NEXT: run `Transient/biome_art_refresh_2026-10-07/refresh_ruled_sheets.sh`, open the six sheets for him, and install only what he rules.
- `MORNING_QUESTIONS` — 5 questions in Transient/MORNING_2026-10-08.md; NEXT: put them to him as question cards on his first message.
- `JAWABENCH_DLL_GAME_COPY` — DLL rebuilt in the repo with 3 tools (untracked artifacts dir), game copy stale; NEXT: once the game is closed, run `build.py --gm --apply` (rimbridge-companion skill).
- `WEATHER_STONES_BORROWED_ART` — RM_CondenserWater, RM_KarrekPaste and RM_SeepStone wear vanilla chemfuel, pemmican and jade art; NEXT: queue our own item art at priority 0.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A plain `git fetch` from a 10G-capped seat window can OOM-kill it; run it in its own scope with `systemd-run --user --scope -p MemoryMax=20G git fetch` (filed: lessons 8b1860f2e).
- The bench clone is shared by every helper agent, so `git reset --keep origin/main` refuses on any helper's dirty file; the push recipe is fetch-in-scope → reset --keep → cherry-pick, each in a SEPARATE Bash call, because the ledger-lint hook evaluates HEAD before the command runs (see: this handoff).
- fill_queue.py treated priority 0 as blank and filed at 100; fixed by the Feverwood regen agent (see: feverwood_regen.md).
- Owner rule: geometric placeholder art may never be a selectable pick or variant (filed: lessons 3446cd70b).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (11) — the next seat's queue

- `HUGE_THINGS_GPT_REVIEW_1` — Merged Huge Things: full GPT review — concepts, implementation, bugs, unforeseen challenges, opportunities, extensions to other mods and game content 
- `PLANT_FOOTPRINT_HARDENING_1` — Huge Things plant adapter hardening from the full GPT review (A2.3, A3.3, A3.8, A3.11, A3.12, C3.2, C4.9, ThingsUnderMouse alloc)
- `PLANT_INTERACTION_GUARDS_1` — Huge Things plant interaction guards from the full GPT review (A3.4 interaction cells, A3.6 quest items, A3.7 dedup identity, C3.3 hitbox graphic, C3.
- `CORPSE_SITE_SAFETY_1` — Titan corpse-site conversion and harvest safety from the full GPT review (B3.1 deferred conversion, B3.3 spawn result, B3.11 placement commit, B3.12 n
- `TITAN_WAKE_FIXES_1` — Titan wake step fixes from the full GPT review (B3.6 per-step dedup, B3.7 real-move only, B3.8 flying, B2.4 gate order, B3.18 life-stage qualification
- `HUGETHINGS_SETTINGS_HARDENING_1` — Huge Things settings: validate every numeric on load, honest labels, translation keys (B3.19/C3.6/D3.3, A2.7/D1.5, B4.6)
- `LARGEPAWNS_BRIDGE_HARDENING_1` — Large Pawns bridge: turn its PathClearingUtility wall-break off as ruled, and make reconcile atomic (B3.15, B3.16)
- `TITAN_ROOF_AVOIDANCE_1` — Titans never path under thick roof, footprint-wide, as card #1 rules (B3.5/D3.1/D1.4; fix B2.6 comment)
- `TITAN_BREAKTHROUGH_CLEARING_1` — Titans smash THROUGH built obstacles and eligible giant plants instead of detouring, as card #1 rules (B3.4/C3.5/D3.2)
- `HUGETHINGS_TEST_HONESTY_1` — Huge Things test apparatus honesty fixes from the full GPT review (C3.7, C3.8, C3.9, C2.5a/c/d, C2.6)
- `TITAN_CAMPS_SCAVENGERS_EVENTS_1` — Huge Things titans: corpse camps, scavenger draw, footfall-warned titan events. Ruled by cards #4/#5 2026-09-09, never built, no item carried them (fo

## Commits

```
28fb848a6 cuts_audit: cite the post-rebase shas
d074b131a Delete from the game the 15 cut creatures and plants still in the files, with their eggs, products and every reference
f3a7513c5 Vashuu: new Greentide river fish wearing the mee's old picture; old niim art stored for the next sea sitting
6c097fd51 FOUNDRY handoff after 23:16 OOM kill: remaining L0 triage, acc_biomes fixes, L1 tiers, TerminalBiomes review
5438ed5d3 GPT top-ten reviews 5-9 (Stillsand, DivingInteraction, Scarlands, LuminousPigment, FeverWood); L0 observations + post-L0 selftest run
7cb362930 Canon library INDEX regenerated after GPT review merge
0efb39e2a Canon fauna GPT review batch 11 verified against Wookieepedia; verified fixes merged, claims logged
579af1d24 Canon fauna GPT review batch 03 verified against Wookieepedia; verified fixes merged, claims logged
25a27f476 Canon fauna GPT review batch 09 verified against Wookieepedia; verified fixes merged, claims logged
0464074bb Canon fauna GPT review batch 02 verified against Wookieepedia; verified fixes merged, claims logged
b5cdc802c Canon fauna GPT review batch 04 verified against Wookieepedia; verified fixes merged, claims logged
4d3ffd106 Canon fauna GPT review batch 06 verified against Wookieepedia; verified fixes merged, claims logged
20b543cbf Canon fauna GPT review batch 12 verified against Wookieepedia; verified fixes merged, claims logged
81d3c03a3 Canon fauna GPT review batch 08 verified against Wookieepedia; verified fixes merged, claims logged
be976153c Canon fauna GPT review batch 05 verified against Wookieepedia; verified fixes merged, claims logged
01440c5b6 Canon fauna GPT review batch 07 verified against Wookieepedia; verified fixes merged, claims logged
37def927f Canon fauna GPT review batch 10 verified against Wookieepedia; verified fixes merged, claims logged
130fe45a1 Canon fauna GPT review batch 01 verified against Wookieepedia; verified fixes merged, claims logged
481cdf12b GPT canon review verification: log and proposal skeletons
68ffa8b2e cuts_audit: cite the Scaa Lumsigh sha
... 142 more: git log --oneline 8b1f1aa42..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     FOUNDRY: deploy clean tree, acc_biomes L1/L2 acceptance sitting

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? conversations/   earlier BENCH windows: conversation exports and ModsConfig tier backups (not this window)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   earlier BENCH windows: conversation exports and ModsConfig tier backups (not this window)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   earlier BENCH windows: conversation exports and ModsConfig tier backups (not this window)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   earlier BENCH windows: conversation exports and ModsConfig tier backups (not this window)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   earlier BENCH art helpers: collected textures no def references yet (cuts_audit / ASSESSMENT.md list them)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   earlier BENCH art helpers: collected textures no def references yet (cuts_audit / ASSESSMENT.md list them)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   earlier BENCH art helpers: collected textures no def references yet (cuts_audit / ASSESSMENT.md list them)
```

