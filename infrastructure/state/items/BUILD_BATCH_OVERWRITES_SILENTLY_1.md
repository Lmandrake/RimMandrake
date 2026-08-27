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

---

# ✅ ALREADY FIXED IN SOURCE — re-read at HEAD 2026-08-27, seat BUILD. ⛔ NOT DEPLOYED.

**This item reads as open and is not.** The fix went in after it was filed and is sitting
in the undeployed build — the game copy's tool surface reads **166** against the build's
**238** — which is exactly why the live measurement still showed the defect.
Evidence: `infrastructure/state/evidence/BUILD_BATCH_OVERWRITES_SILENTLY_1.txt`.

`jawa/build_batch` in `JawaBenchMapTools.cs` now returns:

| field | meaning |
|---|---|
| `placed` | spawns that succeeded — **not** the number of things on the map |
| `survived` | counted after every op (`!t.Destroyed`) — this is the honest number |
| `lostToLaterOps` | `placed - survived` |
| `displaced[]` | everything this batch destroyed, each with `placedByThisBatch` |
| `refuseIfDisplaces` | opt-in refusal instead of wiping |

🔑 **It predicts the destruction rather than noticing it afterwards** —
`GenSpawn.SpawningWipes(td, other.def)` builds a `doomed` list *before* the spawn, which is
what makes `refuseIfDisplaces` possible at all and what lets `displaced[]` name the op that
did it. `placedByThisBatch` is precisely the measured case: the destroyed thing was placed
by an earlier op of the same run, so `placed` had already counted it.

⚠️ **`refuseIfDisplaces` defaults OFF on purpose**, and the reason is in the parameter's own
description: a door legitimately replaces the wall in its cell, so refusing by default would
break ordinary layouts. Turn it on when a generator's output must not eat itself.

## Prove it
```
jawa/build_batch {ops:"DiningChair:10,10;Table1x2c:10,10"}
jawa/build_batch {ops:"DiningChair:12,10;Table1x2c:12,10", refuseIfDisplaces:true}
```
**Expect** first: `placed 2, survived 1, lostToLaterOps 1`, `displaced[0].destroyed
"DiningChair"` with `placedByThisBatch: true`. Second: the table op in `failed[]`, chair
still standing.

## Watch out
- ⚠️ **`displaced[]` also fires for pre-existing buildings**, not only for things this batch
  placed — that is what `placedByThisBatch: false` means. A non-empty `displaced[]` with
  `lostToLaterOps: 0` is a *correct* wipe of scenery, not a defect.
- 🔑 **The advice in `skills/rimbridge/references/silent-failures.md` is now over-strict.**
  It says a cell-by-cell read-back is the only honest success signal. Once this deploys,
  `survived` is that signal. ⛔ Do not delete the read-back advice until the tool has been
  proven live — the note there should be updated by whoever runs the proof, not now.
