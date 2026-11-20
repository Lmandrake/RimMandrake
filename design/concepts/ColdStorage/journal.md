# ColdStorage: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

ColdStorage entered the pipeline at intake on the owner's words of 2026-11-20 (ledger 19:49Z, 11:49 AM PST), after
RimFridge left the live mod list that morning (item RIMFRIDGE_DROP_FIX_INBOUND_REFS, sha 8eb6ed07b3): "Also we need to
reproduce rimfridge. In the new system it needs to be ticketed into part of a mod." (item
RIMMANDRAKE_ADMIT_COLD_STORAGE_AS_PIPELINE_MOD_RIMFRIDGE_GONE). His words admit it; they do not move it past intake.

## The mod as it stands

- **Waiting on:** its readiness list (none written yet) and its switch, which is OFF (`./pipe off ColdStorage`); then a
  word that moves it from intake to the Designer (spec §4 "Intake", exit row).
- **Stage now:** Intake, ideas waiting, since 2026-11-20 11:58 AM PST.
- **Mod:** `src/RimMandrake/ColdStorage` (mandrake.rm.coldstorage, namespace RimMandrake.ColdStorage), the generic
  engine and generic devices. The Star Wars cooling ladder a player builds lives in `src/RimStarWars/Cuisine`
  (mandrake.rsw.cuisine); the tar seal in `src/RimMandrake/TheSump`.
- **Design Version:** 0.1.0, open (`version/VERSION.json`). No locked design. The proposed 0.1.0 and what waits for a
  later version: `admission_proposal.md` (a proposal for the Designer and the owner, not a lock).
- **Design input:** `design/RimStarWars/cold_storage_line_2026-10-26.md` (written before the pipeline; input, not settled).
- **First-touch Designer item:** COLDSTORAGE_DESIGN_FIRST_TOUCH.
- **Next:** write the readiness list for ColdStorage (`admission_proposal.md` §What must happen before it runs).

## History

### 2026-11-20 11:58 AM PST, admitted to ideas waiting (Intake) (by BENCH)

- 2026-11-20, BENCH: seeded at intake. Measured the same day: 214/0 offline selftest
  (`selftest_coldstorage.py`), every cold-storage building and item still drawn with a borrowed vanilla texture, the
  live proof `coldstorage_live_proof.py` A1-A6 never run, ColdStorage and Cuisine both in the live 315-mod list and in
  `infrastructure/state/modlists/manifest.FULL.json`. Detail: `admission_proposal.md` §What exists.
