# WreckedMachines: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

WreckedMachines entered the pipeline as the all-Fable experiment: one mod built start to finish on Fable 5.2. He chose
it on 2026-11-19 about 8:35 AM PST (item RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST): "Ok, Wrecked Machines
it is. It has a generic possible implementation and then the Utinni-specific weaving it into the god-ship concept.
First decision would be whether we even bother with the generic version. I suspect it's a good, strong concept save for
the much larger lift in terms of art generation, but we're pretty good at that. Then the Utinni specialization would
bring in the holy aspects of repairing the work. Could even be extended to ship components and things. Needs a LOT of
work using our modern Design passes of course, we didn't have anything like that before." He gave the go on
2026-11-26 2:33 PM PST (item RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO): "I authorize you to do an all
fable experiment on wrecked machines. We can afford it. Let's see how it goes. Gather all those tickets together as a
bundle, design run for it to clarify and put needed bars and tests, then let's see how fable 5.2 does. Hopefully
beautifully. Of course it should intelligently subagent fanout as needed."

## The mod as it stands

- **Waiting on:** the offline build (Stage 3), which the Dispatch tick launches; nothing waits on him
- **Stage now:** Stage 3, offline build, since 2026-11-27 5:35 AM PST (`version/stage_record.json`).
- **Mod:** `src/RimMandrake/WreckedMachines` (mandrake.rm.wreckedmachines, namespace RimMandrake.WreckedMachines,
  prefix RM_), the generic RimMandrake tier. The Utinni layer and ship parts are later work.
- **Design Version:** 0.1.0, locked on 2026-11-27 by the pipeline (`version/VERSION.json`). Its 30 bars are in
  `version/locked_bars.json`, and `version/bars.md` pins the locked files.
- **Model:** every builder role on Fable 5.2 (`pipe model WreckedMachines fable`); a Fable builder may start subagents
  (Sonnet or Opus, never Fable). Judges and the in-game driver keep their own models.
- **Design input:** `design/specs/2026-11-26-wrecked-machines-fable/tickets_bundle.md` (the 10 open tickets, read
  against the code). The old `DESIGN.md`, `MACHINES.md`, `V2.md` and the north-star walk are input, not settled.
- **Small list:** `version/small_list.json`, tier `wreckedmachines_solo`.
- **Next:** the offline build (Stage 3). It builds the 10 specified tests of `version/test_table.json`
  (`stage3_build_list`) red first, does the build work that `version/preflight.json` names, and remakes the table.

## History

### 2026-11-26, admitted at intake, then moved to the Designer on his go (by BENCH)

- Readiness: `D:\ClaudeWork\rimmandrake\conductor\readiness_wreckedmachines_20261126.md` reads READY for the design
  stage and NOT READY for the build and in-game stages (the check count waits for the locked design).
- Seeded at intake, advanced to the Designer on his words, `designer_stage.py init` on the item
  RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST.

### 2026-11-26 4:58 PM PST, stage change: ideas waiting (Intake) to Designer (Stage 1) (by BENCH)

- Why: his go of 2026-11-26 2:33 PM PST on RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO; first-touch item RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST; readiness D:\ClaudeWork\rimmandrake\conductor\readiness_wreckedmachines_20261126.md READY for the design stage
- Checks passed: order, by, version, hold, intake_closed.
- Owner said: I authorize you to do an all fable experiment on wrecked machines. We can afford it. Let's see how it goes. Gather all those tickets together as a bundle, design run for it to clarify and put needed bars and tests, then let's see how fable 5.2 does. Hopefully beautifully. Of course it should intelligently subagent fanout as needed.
- Was, "Stage now": - **Stage now:** Intake, ideas waiting, since 2026-11-26 5:00 PM PST (admitted the same afternoon; see history).
- Was, "Waiting on": - **Waiting on:** the Designer's first-touch run (`role_launch.py run-now --role Designer --concept design/concepts/WreckedMachines`); nothing waits on him.
- Record: `version/stage_record.json`.

### 2026-11-27 4:54 AM PST, stage change: Designer (Stage 1) to Preflight (Stage 2) (by BENCH)

- Why: the Design Version 0.1.0 is locked (the pipeline's lock of 2026-11-27, Evidence-for-Ask ruling) and its 30 bars are recorded in version/locked_bars.json; steward run on RIMMANDRAKE_ADVANCE_WRECKEDMACHINES_LOCKED_VERSION_TO_PREFLIGHT
- Checks passed: order, by, version, hold, locked.
- Steward confirms: read: stage.json status locked at stage 5; coverage_verdict.json verdict covered, signed, CALIBRATED, gaps none (judge rm-coverage-judge-1795781593); exam.json 20 of 20 with 2 Readers; VERSION.json state locked 0.1.0, bars_total 30; lock-bars recorded 30 ids at lock commit 063eb68488. Verdict: the Designer's exit is met
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: the Design Version 0.1.0 is locked (the pipeline's lock of 2026-11-27, Evidence-for-Ask ruling) and its 30 bars are recorded in version/locked_bars.json; steward run on RIMMANDRAKE_ADVANCE_WRECKEDMACHINES_LOCKED_VERSION_TO_PREFLIGHT
- Was, "Stage now": - **Stage now:** Stage 1, the Designer, since 2026-11-26 4:58 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-26 4:58 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-27 4:50 AM PST, the lock commit in `version/VERSION.json` corrected, and the bars recorded (by BENCH)

- What changed: `locked_from_commit` was `b53e34d70527cdd6ab1d8c37c74716851708ddc1`. It is now
  `063eb68488bc5cccc3dd2671617fff0a731a591c`. No bar, no locked file and no other field of the lock changed.
- Why: `b53e34d705` was the HEAD of the dispatch clone at the lock, a ledger commit that never reached origin/main under
  that sha. No other clone holds it, so `maturation.py lock-bars WreckedMachines` refused ("tree.json at b53e34d705...
  cannot be read"). `063eb68488` is the parent of `b53e34d705` and is on origin/main.
- Why the meaning is the same: each of the 9 locked files (`tree.json`, `sheet.md`, `scenes.json`, `floor.json`,
  `exam.json`, `record.json`, `plan.md`, `stage.json`, `coverage_verdict.json`) has the same git blob at `b53e34d705`
  (read in `/home/mandrake/rm/dispatch`) and at `063eb68488`. The blobs are in `version/bars.md`.
- The cause is fixed in the pipeline at commit `50b17bd053` (page
  `design/specs/2026-11-27-lock-commit-is-landed/boundary.md`): the pipeline's lock now names a commit that origin/main
  holds.
- `maturation.py lock-bars` then recorded 30 bars in `version/locked_bars.json` and wrote `version/bars.md`.

### 2026-11-27 5:36 AM PST, Preflight (Stage 2) run: the test table made, the record reads refuse with 3 refusals, all build work (by BENCH)

- Steward run on RIMMANDRAKE_STEWARD_WRECKEDMACHINES_PREFLIGHT_STAGE. No locked file changed; `version/bars.md` needs no
  re-pin (check C12 of the preflight compares the 8 bar files with their pins: all equal).
- **The test table** (`version/test_table.json`, read view `version/test_table.md`) is made by
  `version/pilot_throwaway/make_test_table.py`, with no model. It holds the 30 locked bars and 48 tests: 7 built offline
  tests, 26 in-game scenes with their entry written, 10 tests specified for Stage 3, 4 explorations and his walk.
  - Each bar-to-test pair comes from the locked files by one of ten rules, written in the table (`pairs_from`). The
    signed coverage verdict is a delta round, and its checklist holds only what it read again. So rule R1 also reads the
    full round (`coverage_verdict.json` at git `89b10e6f1a`).
  - The steward wrote three kinds of text, and the table marks each for the Stage 4 challenger: `why_game` of each
    in-game scene (quoted from `plan.md`, "offline simulation" and "risks"), `cheaper_why` of 17 scenes, and the
    proposed files of the specified tests.
  - The scene size check (`src/RimMandrake/rimflow/scene_size.py`) refused 12 in-game scenes at the first publish: 8 for
    their span, 9 for their count of clauses, 5 of them for both. Each now carries its `cheaper_why`, as do the 5 scenes
    that the steward had named before. The spans are sums of wait ceilings: each long wait ends at the reading it waits
    for, so the real play is not measured before the build. Three of the 12 are state reads with no clock.
  - Each built offline test was run. 6 are green. `sc_text_names_no_setting` is red: the read finds the setting's words
    in the mod's texts as built.
- **Delegated call (evidence-for-ask).** The bars `inv_wealth_exclusion` and `inv_turret_line` have scope `later` and no
  scene. The table decides them with one specified offline test, `T_LATER_STAYS_OUT`: 0.1.0 ships neither of them
  half-built. Pyrelands decides its two cut bars the same way (`T_CUT_STAYS_CUT`). The other choice is his card to take
  the two ids out of the locked bars; no recorded evidence speaks for it.
- **The preflight record** (`version/preflight.json`) is written by `version/pilot_throwaway/preflight_wreckedmachines.py`
  in 14 s: 19 checks, 17 pass, verdict refuse, 3 refusals. Each refusal is build work on a sound bar:
  - `sc_text_names_no_setting` is red today. It decides `no_setting_named`, `levels_told_apart` and
    `inv_distillation_module`. `plan.md` ("Changed") gives the fix to the build: "The setting words leave every text".
  - `sc_study_without_research_reinvented` and `sc_cannery_tier` each name a tier of their own that
    `src/RimMandrake/Utils/modset_builder.py` does not define. The scenes are written; Stage 3 defines the two tiers.
  - 10 deciding or supporting tests are specified and not built (`stage3_build_list` in the table). The spec counts
    these as Stage 3 work, not as refusals.
- **The preflight was seen to refuse.** `version/pilot_throwaway/plant_preflight_faults.py` plants 29 faults in copies of
  the table: each one is refused by the check that guards it. A changed `plan.md` was refused by C12 and then restored.
- 15 of the 30 bars have every deciding check runnable today. The other 15 wait on the build work above.
- Not judged here: whether each `why_game` is true, and whether a cheaper test could decide a bar. Those questions are
  the Stage 4 challenger's (spec, Stage 2, "On the cheapest stage that can decide it").

### 2026-11-27 5:35 AM PST, stage change: Preflight (Stage 2) to Offline build (Stage 3) (by BENCH)

- Why: Preflight (Stage 2) ran: version/preflight.json reads refuse with 3 refusals, each of them build work on a sound bar, none a fault of the spec; the test table holds the 30 locked bars; steward run on RIMMANDRAKE_STEWARD_WRECKEDMACHINES_PREFLIGHT_STAGE
- Checks passed: order, by, version, hold, preflight_record, steward_confirms.
- Steward confirms: read: version/preflight.json (program pilot_throwaway/preflight_wreckedmachines.py, 19 checks, 17 pass, verdict refuse, 3 refusals) and version/test_table.json (30 locked bars, 48 tests, 15 bars runnable today). Each remaining refusal is unbuilt behaviour or an unbuilt check part, not a spec fault: (1) C6 sc_text_names_no_setting is red today because the built mod's texts still hold the setting's words, an unbuilt behaviour that plan.md gives to the build ('The setting words leave every text'); (2) and (3) C10b the tiers of sc_study_without_research_reinvented and sc_cannery_tier are not defined in modset_builder.TIERS, an unbuilt part of two checks whose scene entries are written. Ten more tests are specified and not built (stage3_build_list), which the spec counts as Stage 3 work. The 13 checks of real files, defs, mods, bridge tools, items, pins, stages, kinds and held statements pass; the preflight refused 29 of 29 planted faults. Verdict: the Stage 2 exit is met for the spec; the refusals go to the offline build
- Owner said: per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: Preflight (Stage 2) ran: version/preflight.json reads refuse with 3 refusals, each of them build work on a sound bar, none a fault of the spec; the test table holds the 30 locked bars; steward run on RIMMANDRAKE_STEWARD_WRECKEDMACHINES_PREFLIGHT_STAGE
- Was, "Stage now": - **Stage now:** Stage 2, preflight, since 2026-11-27 4:54 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** the Preflight run (Stage 2), which the Dispatch tick launches; nothing waits on him
- Record: `version/stage_record.json`.

### 2026-11-27 7:40 AM PST, Offline build (Stage 3), first run: 15 bars not runnable to 7; the mechanism compiled and not yet run in the game (by BENCH)

- Run on RIMMANDRAKE_AUTOBUILD_WRECKEDMACHINES_FIFTEEN_BARS_LEFT, stopped by the account line; its `LEFT OPEN:` note holds the
  exact state and the next steps. Last code sha `bc2612d8ac`.
- **Checks built.** Green, each seen red on a planted fault: `T_DISTILLATION_LOADS`, `T_REPAIR_STATE_WALK` (8 rows, 416 states
  by 16 events on 2 machines and 4000 random strings; 17 of 17 faults planted in the kernel went red), `T_LATER_STAYS_OUT`,
  `T_NEIGHBOUR_NAMES`, `T_LEVEL_NUMBERS`, `T_ONBOARDING_TABLE_OFFLINE`. Red first, by design: `T_ONBOARDED_SET` and
  `T_ONBOARDING_COMPLETE` (3 of 20 lines on the table; pictures and the judge's records owed) and `T_FORGE_GATES_GONE` (the
  forge is not onboarded). The two scene tiers are defined. `sc_old_save` is not written.
- **Build.** `src/RimMandrake/WreckedMachines/DESIGN.md` is the build's contract. The repair record and its transitions are in
  the Verse-free kernel. The C# of the repair on the machine, the study toggle and its work giver, the process and speed
  sync, `machineLines` in Mod Settings and the proof type compile; none of it has run in the game. The smelter, the power cell
  and the emanator are on the onboarding table in the new shape; 17 machines are stamped and staged under
  `Source/onboarding_staged`, to land when their pictures pass the judge.
- **A check that was wrong.** The text scene's Star Wars name list read one word, `None`, from `biome_rulings.md`; it now
  reads the canon library (244 names) and was seen to fail on a planted name. Its label read missed a lower-case "repaired".
- **Neighbours.** The Armoury no longer names the deleted `RM_WM_AutomatedSmelter_Repaired` (same landing, rule
  `R_neighbour_names`). Cold Storage's and the Cuisine mod's names are kept as they read them.
- **Not tested, with the reason.** No in-game check ran: ArchBig was taken and the mod deployed at 7:35 AM PST, and the account
  line came before the first load. The offline model: the repair state machine has its generator (the walk); the mod's other
  decisions (study, placement, pictures) are the game's own machinery and are read live.
