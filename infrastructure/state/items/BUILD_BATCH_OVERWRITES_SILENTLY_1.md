# BUILD_BATCH_OVERWRITES_SILENTLY_1 — a later op destroys an earlier building, both report placed

Measured live 2026-08-26. Across eight `jawa/build_batch` calls in one run, the tool reported
`placed` 4+1+1+3+3+1+3+65 = **81**, exactly the ops requested, with `failed: []` everywhere.
The map afterwards holds **78**.

The three missing things were each destroyed by a LATER op whose multi-cell footprint covered
them (a `Table1x2c` over a `DiningChair`, a `Shelf` over two earlier `Shelf`s). Both the
destroying op and the destroyed op reported success.

🔴 **`placed` counts spawn attempts, not survivors.** A caller diffing `placed` against
`requested` — which is exactly what `TEMPLATE_ENGINE_ACCEPTANCE_1` criterion 3 asks for — sees a
perfect run.

**What to change.** `jawa/build_batch` already has a `wipeExisting` parameter; when a spawn
displaces an existing building the tool should either refuse the op (default) or report it in a
`displaced[]` array naming what was destroyed. Silence is the defect, not the wipe.

⇒ Until then, the only honest success signal is a **cell-by-cell read-back**, and that belongs in
`skills/rimbridge/references/silent-failures.md` (appended).

Evidence: `infrastructure/state/evidence/template_engine_acceptance_2026-08-26_CHECK.md`
