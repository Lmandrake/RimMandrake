# MachineLooks: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

Machine Looks ("RimMandrake: Machine Looks") entered the pipeline at intake by a Conductor act (item
RIMMANDRAKE_ADMIT_MACHINE_LOOKS_MOD_WITH_FRIDGE_AND_BATTERY, per ruling
RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS), on the decision in
`design/specs/2026-11-20-vanilla-electrical-art-home/design.md`: Gimme Some Slack keeps the electrical installation
(wires, switches, poles, lights); Machine Looks takes the vanilla appliances (battery, heater, cooler, benches, research
benches, turrets, televisions, generators, solar) in the four looks Scrapper, Industrial, Modern and Futuristic. The
owner asked for it on 2026-11-20, 3:30 PM PST (`D:\ClaudeWork\rimmandrake\conductor\gss_walk_20261120_his_words.md`,
Message 2): "Go ahead and commission different looks for the battery at this time for the various styles too, like we
did for the lamp already." The fridge art is folded in on his words of the same evening
(`conversations/2026-11-20-2350-97f0c93f.md` line 116, "your call"); the cold-storage FUNCTION stays parked for
Cuisine/ColdStorage. Admission does not move it past intake.

## The mod as it stands

- **Waiting on:** its readiness list (none written yet; `admission_proposal.md` §What must happen before it runs), its
  switch, which is OFF (`./pipe off MachineLooks`), and a free slot (`maturation_dispatch.json` max_live 3; 3 of 3
  live at admission); then a word that moves it from intake to the Designer (spec §4 "Intake", exit row).
- **Stage now:** Intake, ideas waiting, since 2026-11-23 4:05 AM PST.
- **Mod:** `src/RimMandrake/MachineLooks` (mandrake.rm.machinelooks, namespace RimMandrake.MachineLooks, prefix RM_).
  The folder does not exist yet; the Designer's first build creates it.
- **Design Version:** 0.1.0, open (`version/VERSION.json`). No locked design. The proposed 0.1.0 (battery first, the
  fridge pictures, the kept art) and what waits for a later version: `admission_proposal.md` (a proposal for the
  Designer and the owner, not a lock).
- **Design input:** `design/specs/2026-11-20-vanilla-electrical-art-home/` (`design.md`, `commissions.md`, `art/`;
  written before the pipeline; input, not settled). Kept and candidate art: `kept_art.md`.
- **First-touch Designer item:** RIMMANDRAKE_DESIGN_MACHINE_LOOKS_FIRST_TOUCH_BATTERY_LEADS.
- **Next:** write the readiness list for Machine Looks (`admission_proposal.md` §What must happen before it runs).

## History

### 2026-11-23 4:05 AM PST, admitted to ideas waiting (Intake) (by BENCH)

- 2026-11-23, BENCH: seeded at intake. Measured the same day: no mod folder (`src/RimMandrake/MachineLooks` absent);
  7 battery pictures KEEP in the art store (Scrapper, Industrial, Futuristic east + north; Modern east), the Modern
  battery north REDO three times and owed (RIMMANDRAKE_REDO_MODERN_BATTERY_NORTH_VIEW_FAILED_JUDGE_THRICE); 4 look
  icons KEEP; 13 cold-storage renders of 2026-10-26 in the art store, never judged. Nothing installed in any mod.
  Detail: `kept_art.md`, `admission_proposal.md` §What exists.
