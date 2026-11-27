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

- **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-26 4:58 PM PST).
- **Stage now:** Stage 1, the Designer, since 2026-11-26 4:58 PM PST (`version/stage_record.json`).
- **Mod:** `src/RimMandrake/WreckedMachines` (mandrake.rm.wreckedmachines, namespace RimMandrake.WreckedMachines,
  prefix RM_), the generic RimMandrake tier. The Utinni layer and ship parts are later work.
- **Design Version:** 0.1.0, open (`version/VERSION.json`). No locked design yet; the Designer's Lock step cuts it.
- **Model:** every builder role on Fable 5.2 (`pipe model WreckedMachines fable`); a Fable builder may start subagents
  (Sonnet or Opus, never Fable). Judges and the in-game driver keep their own models.
- **Design input:** `design/specs/2026-11-26-wrecked-machines-fable/tickets_bundle.md` (the 10 open tickets, read
  against the code). The old `DESIGN.md`, `MACHINES.md`, `V2.md` and the north-star walk are input, not settled.
- **Small list:** `version/small_list.json`, tier `wreckedmachines_solo`.
- **Next:** the Designer's first touch.

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
