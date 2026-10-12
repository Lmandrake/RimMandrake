# FOUNDRY_REBOOT_HANDOFF_202610120023 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610111255`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
A hand-rolled or stale art sheet is a failed human interaction: the owner could not tell what to click (no description, four unrelated items in one choice, "new" candidate identical to current). Ask by question card, or build a sheet where one row is one decision about one thing in plain words. Check that candidates differ before offering them. (filed: lessons, 20261011T212128Z-FOUNDRY-not-successful-human-interaction-owner-2026.md)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Three PROVISIONAL numbers/questions: Sun-Debt believers' mood toward the wringing still (+2 now, or no thought); the x1.5 sell premium for old-tongue transcriptions to the Helix and Deepwater; whether steam-catch item water has no settings toggle until FlowWorks builds the pipe form.
- Pyrelands sheet enacted by hand from his notes: Dalgo H east installed over his earlier keep (card-confirmed), Nuna females B only (random B/C deferred by card), Contagion originals Ocular Jelly and Infected Aerofleet dropped (card). Ashwallow redo art is rendered and waits on his pick.
- FlowWorks/GSS sitting is PARTIAL: no rimflow verify recorded; BENCH owns those checkouts now.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `FLOWWORKS_GSS_LIVE_SITTING` (results file Transient/flowworks_gss_sitting_results_20261011.md) — validation_v2 GREEN 61/61, extension proof polluted, A5-A16 and B loads owed; NEXT: BENCH reruns A5 on a clean map and restores ModsConfig with `modset_builder.py --restore` (game is UP on the 17-mod fw_gss_sitting list).
- `ART_CHECKS_REPAIR_FIXTURES_ART_MOVED` — filed; selftest_art_checks reads live art that the owner's swaps changed; NEXT: freeze its Dalgo/outline fixtures as committed files, never loosen thresholds.
- `ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE` — filed; NEXT: wire a direct heat hit to the existing burrow behaviour and add the dome pose.
- `STILLSAND_SOLAR_STILL_1` / `WARSCAR_OLD_TONGUE_1` / `GREENTIDE_MECHANICS_2` — built offline, checks owed live; NEXT: one minimal-list bridge sitting covering their L1/L2 criteria.
- `MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG` and `CANON_MATERIALS_BUILD_1` — carried from the prior handoff, untouched; NEXT: with the game down, deploy mineshaft+Armoury and swap Mines 2.0 off the live list.
- Local clone is behind origin by 18 commits; NEXT: `git pull --rebase origin main` once the two dirty regenerated files are committed or restored.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A pull in this clone can fail on untracked Transient/biome_ffar/img/*.webp that origin now tracks; move them aside, never reset (filed: lessons).
- A subagent's selftest red can be a live-art fixture, not its own work: selftest_art_checks failed after owner art swaps (see: ART_CHECKS_REPAIR_FIXTURES_ART_MOVED).
- `art.py install` takes the mod as a repo-relative path (src/RimMandrake/FlowWorks) and the FULL sha, and a wrong mod string writes a stray tree at repo root (see: skills/rimworld-review-sheets).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (11) — the next seat's queue

- `VALIDATION_V2_IDENTITY_WIRE_READS_ZERO` — validation_v2.py and proof_all write no deploy fingerprint/run_identity, so the report counts 0 proven; record run_identity at start and end (from FOU
- `WASTELAND_CONTAGION_PROBE_FIVE_LOOSE_ENDS` — Reproduce live the unresolved acc_biomes findings: Wasteland tipping + middenshell toggles, Contagion placement/inject/manhunter, per Transient/acc_bi
- `OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN` — Ollopom perceived-beauty DLL is deployed; run its validation.py perceived_beauty check on the next live session (pointer OLLOPOM_BEAUTY_LIVE_CHECK, BE
- `FLOWWORKS_LIQUID_KITS_WIRE_NO_REVIEW_ROW` — FlowWorks liquid kits have no feature row in src/RimMandrake/FlowWorks/human_review.py; add one (pointer FLOWWORKS_LIQUID_KITS, FOUNDRY_HANDOFF_202610
- `TELEMETRY_STACK_BUILD_AFTER_THE_MOVE` — Build telemetry: VictoriaMetrics + SQLite + Grafana + RimPulse alerts on E:, 1 s windows + flight recorder during tests (design Transient/weekly_clean
- `OLD_ART_SHEETS_REBUILD_WITH_SCALE_PANELS` — Rebuild sheet_conflicts_review_2026-10-09 and sluice_panning_warden_sheet_20261010 with art_sheet.py --subjects so the new scale gate stops refusing t
- `TELEMETRY_BUILD_DESIGN_ALREADY_PICKED` — Telemetry MVP build per Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md (owner picks in 00_SUMMARY.md)
- `LIQUID_KIT_COMMENTS_CORRECT_GHOST_PATCHES` — FlowWorks liquid kits cite two patches that do not exist: RM_FluidResidue.cs header says Patches/Kits/RM_TarResidue.xml puts the residue extension on 
- `TPS_VERDICT_FIX_SIX_SECONDS_NOT_THIRTY` — JawaBench sampler + tps_record reader: the sustained low/high TPS verdict counts 6 windows, which is 30 s at the 5 s cadence but only 6 s at the test 
- `ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE` — Ashwallow: assume the dome stance when heat-attacked (not only when a free Fire is within detectionRadius); dome pose art
- `ART_CHECKS_REPAIR_FIXTURES_ART_MOVED` — selftest_art_checks failed after owner art swaps: its fixtures read live art. Freeze them as committed fixtures

## Commits

```
c0e5519ed Ledger (FOUNDRY shard): GREENTIDE_MECHANICS_2 implemented, SCALD_MECHANICS_1 S2 note
45eb31d7c Scald S2: steam-catch now makes distilled water (it had no outputDef and produced nothing)
103ce2eaa Warscar old tongue: rest panels, transcriptions as antiquities with a Helix/Deepwater premium, unread panels in the research tooltip (PROVISIONAL)
39bd4aab8 FlowWorks harness: re-review fixes (27 files; checks that passed without a reading now FAIL/UNMEASURED)
7432ac095 FlowWorks L1: one liquid transfer service; every tank/world/VE move validated, reversible leg first, put back on refusal
772ff53b7 Rulings: liquid network = hose ends + tank jobs; real off-hose spill; pour kept; foreign tank = theft
b2c6f2e6d Ledger: STILLSAND_SOLAR_STILL_1 implemented at 8b7442ef5 (5 criteria owed live)
2dafd0502 FlowWorks liquid-network design rev 2: owner card answers recorded; tankless lake->canal pump transfer; free-end roles + pump mover + tank modes (H); click counts; revised Q1
741fde789 GSS art sheet rebuilt complete: 151 rows (every GSS texture per look + hoses moved to FlowWorks) + 8 new tap-clamp candidates
8b7442ef5 Stillsand solar still: brine dipping spot (the missing RM_Brine source), believers' 'drawing' thought replaces the outsiders' penalty; PROVISIONAL 5 brine/400 work, +2 mood
47ec4e74f Code review: selftest_flowworks_northstar.py clean on re-review
c593401e5 FlowWorks harness: fixes from the full-file review (28 files)
b0ba0e275 Ledger: LIQUID_LEDGER_BUILD_NO_UNIT_LOST filed and claimed (network design L1-L3)
faacce017 FlowWorks liquid-network semantics: final design (tank modes recommended), adversarial + GPT reviews, 5 owner cards
38d256a20 FlowWorks: re-review round 2 fixes
bb5a02ad2 GSS tap clamp v3: 8 vertical-bite candidates (2 per look), keyed masters, on-wire composites
002e32d67 FlowWorks live verify on fw_gss_sitting: v2 GREEN 61/61 (DLL e64a8af8a); FORCED_PIT_FALL_ROW done, PIT_FALL_ONLY_FORCED A1/A3 + BUILD_PROGRAM A2/A3 pass
f9497d64a Code review: 37 fixed FlowWorks files clean on full-file re-review
9e023a268 FlowWorks: universal pipe looks point at their owned atlases and icons (9f9f3d7035); tint dropped
a741c1bda Code review: GSS lamp-register / diveThrough files clean after full-file review
... 119 more: git log --oneline ed774a8ec..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-11T21:39:10Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   mine (regenerated by sheet rebuild)
 M Transient/modcheck/fixtures.json   another seat's or a tool's (modcheck), not mine
?? conversations/   mine (conversation record)
?? deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   subagent's (bridge agent backup)
?? infrastructure/state/art/sheets/own_render_keep_sheet_2026-10-11.snapshot.json   mine
?? infrastructure/state/art/sheets/sluice_panning_warden_sheet_2026-10-11.snapshot.json   mine
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T131544.json   subagent's (bridge agent run output)
```

