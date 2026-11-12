# Judge: SUMP_SINKING_RITE_BUILD_1

Judge: fresh-eyes Relentless judge (CLAUDE_STEVEDESKTOP_OFFLINE4 subagent), 2026-11-11. I did not read DONE.md or BROADEN.md.

## What I looked at
- `evidence/build.log`: the Rites mod builds, 0 warnings / 0 errors, built from source `da35190c81e3+dirty` (a dirty tree, so the build is not tied to a commit).
- `evidence/kernel_selftest.txt`: 49 engine-free kernel cases PASS (pure C# logic compiled outside RimWorld).
- I re-ran `run_selftests.py --only selftest_sinking_kernel` myself: GREEN, PASS 1/1 (output `D:\ClaudeWork\rimmandrake\judge_sinking_selftest.txt`; the harness summary does not echo the per-case lines, so the 49 count comes from the builder's file).
- `src/RimUtinni/Rites/validation.py` lines 792-970: a live `sinking` chain exists, but its own header says "Written offline, never run by the builder". No live output is in the evidence.

The criteria say every one of these state reads goes "through debug `[Tool]`s, recorded as cases in validation.py", meaning it is read from a running game. The evidence has no live run. A kernel test shows the arithmetic and the decision logic are right. It cannot show that the game hooks work: a GenExplosion reaching the bulge, the storyteller's real next Imperial tick, the Ninefold ledger, the Stolen claims, Thing destruction, hediffs, and the letter.

## Per line
1. **Pitch offering: `RM_TarLull_Beast` ~15 days; construction wake refused, GenExplosion wakes.** Cannot tell. The kernel cases `pitch_rider_beast_lull_15_days`, `beast_lull_refuses_construction` and `beast_lull_explosion_wakes` show the decision function. Nothing shows the map condition on a real map or a real GenExplosion reaching the hook. A live run of the `sinking` chain's pitch case would settle it.
2. **Dig-find offering: trap counter 3; three forced rolls leave TrapArmed false on every `RM_CompWorkedLottery`, no explosion, counter 0; the fourth arms.** Cannot tell. The kernel counter logic passes (`dig_find_trap_counter_reads_3`, `three_trap_rolls_fizzle_counter_0`, `fourth_trap_roll_arms_normally`). Nothing reads real `RM_CompWorkedLottery` comps or the explosion log. The live dig-find case would settle it.
3. **Any Sinking: `RUT_ImperialHoldOff` at 5x the interval, next Imperial incident moved out 5x, Heat unchanged; `RUT_TarLull_Raids` and a lowered seeded raid roll; one Ishko delta tagged "The Sinking"; foreign Stolen claim wiped, colonist untouched, letter names the item.** Cannot tell. The kernel shows the 5x arithmetic, the raid chance, the Ishko delta size and tag, and the ownership filter. The live parts are all unseen: the real incident queue, the Heat component (the live code itself says EmpirePursuit / RimProperty may be absent and would read UNMEASURED), the Ninefold store, Stolen claims on real Things, and the letter text. The live "any Sinking" cases would settle it.
4. **Offered Thing destroyed; pawn or corpse refused with a reason; no new hediff or stat.** Cannot tell. The refusal kernel cases pass (`refused_pawn_with_reason`, `refused_corpse_with_reason`, `refusal_applies_no_effect`). Nothing shows a real Thing despawned or the hediff count unchanged on real pawns.
5. **Each Mod Settings toggle off removes exactly its effect.** Cannot tell. Six kernel toggle cases plus three mid-effect cases pass. Nothing shows the real settings fields gating the real effects. The live toggle loop in `validation.py` would settle it.

## Staged or flattering
- All the evidence is offline unit logic. The selftest and the kernel were written by the same builder, so its passing shows the code agrees with itself, not with the game.
- The build is from a dirty tree.
- The live chain admits it has never been run and expects corrections ("the first live run owes the corrections").

## Verdict
No statement line is shown false. None is shown true either, as the criteria define true (live state reads). This item needs a live lane: run the `sinking` chain in `src/RimUtinni/Rites/validation.py` against a game with mandrake.rut.rites loaded, then judge again.

would show: no
