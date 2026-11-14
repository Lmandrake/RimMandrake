# RIMMANDRAKE_FIND_RIVER_SWIM_BRUISES_FUEGO_HURT_FIVE_TIMES

## spec

A colonist swimming a natural river took a bruise every few hundred ticks (live 2026-11-12, Fuego and Diana). Find the damage source.

## finding 2026-11-14 (offline)
## Verdict

**Our mod, not vanilla, and by design: FlowWorks' River Works current bruises a pawn it sweeps.** [measured from code]
The owner chose that harm option by card on 2026-10-03 (ledger BENCH.jsonl tsn 1791044251558402874, item
`SURFACE_RIVER_WEIRS_1`: *"being swept bruises and can make a pawn drop what it carries"*, option 7 of
`design/RimMandrake/river_works_mod_design_2026-10-03.md` card 2). So the bruises are working as designed. Two real
problems sit beside them (below).

## The code path (proven from code)

`src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs`
- `Scan()` (every 250 ticks) registers every carried thing on a current cell; player colonists are carried
  (`RM_RiverMath.CarriedKind`: `players || carryStrangers`; only fliers and river-native races are exempt).
- `StepOne()` moves the pawn one cell downstream every cadence (`RM_RiverMath.Cadence`: 45 ticks/cell in the
  fast lane `WaterMovingChestDeep`, 90 in the edge lane, divided by strength x river-size factor).
- After each move, if the shove behaves as the fast lane (`HazardsApply(centre, crossingHazardsEnabled)`),
  `ApplyHazards()` rolls `bruiseChancePerStep` (default **0.15**, PROVISIONAL) and deals
  `new DamageInfo(DamageDefOf.Blunt, Rand.Range(2f, 5f))`: Blunt with **no instigator, no weapon, random part**.
  Blunt on flesh is a Bruise.

Fit to the live note: 5 bruises over z 66 -> 8 (58 cells) in ~2500 ticks = 43 ticks/cell, the fast-lane cadence;
expected bruises 58 x 0.15 = 8.7, P(<=5) ~ 0.15, so 5 is ordinary. "A bruise every few hundred ticks" = 1/0.15 x 45
= ~300 ticks. [measured: arithmetic on the note's numbers]

## Ranked hypotheses

| rank | hypothesis | confidence | the one observation that confirms it |
|---|---|---|---|
| 1 | FlowWorks `ApplyHazards` bruise roll on a fast-lane shove | [guess ~90%] that it was the live source; the source itself is [measured] | each bruise lands on a tick where the pawn's cell jumped exactly one cell downstream, with no BattleLog entry and no instigator; flipping Mod Settings "Being swept is dangerous" off (or `bruiseChancePerStep=0`) makes the bruises stop while the drift continues |
| 2 | a creature strike (Greentide `RM_CompBankAmbusher`, `RM_CompAquaticAmbusher` / Dhollock) | [guess ~5%] | an instigator pawn in the BattleLog; BankAmbusher deals **Bite** (a bite wound, not a bruise), so it cannot be the Bruise source [measured]; any melee animal leaves a combat-log line |
| 3 | vanilla 1.6 / Odyssey swimming damage | [guess ~2%] | none found: in the decompiled 1.6 tree (`D:\ClaudeWork\retired-trees\archmagi-dev-2026-10-27\reference\rimworld-decompiled`, contains `JobDriver_GoSwimming`, so it is 1.6) no file mentioning Swimming / IsWater / WaterDeep calls `TakeDamage` [measured] |
| 4 | another of our mods' area damage (spill sheet, hazards) | [guess ~3%] | a non-Blunt hediff, or bruises off the river cells |

## Problem A — a swept pawn's job freezes (likely defect, not the bruise) [measured from code, ~85%]

`Move()` calls `pawn.pather.StopDead()` then `pawn.Notify_Teleported(false)`. Vanilla
(`Verse/Pawn.cs:1752`, `Verse.AI/Pawn_PathFollower.cs:204,412`): both leave the pather with `moving = false`,
no path, and **do not end the job** (`endCurrentJob: false`). A Goto toil (`Toils_Goto.GotoCell`) starts its path
once in `initAction` and completes only on `PatherArrival`, which now never comes. So after the first shove the
pawn stops walking for good and rides the current as a passenger until the carry ends (bend, bank, ford, weir,
map edge), and then stands frozen in that job until something ends it (Fuego and Diana had to be drafted).

That matches both live runs: Fuego was ordered `Goto (75,38)` (west, across the river) and instead travelled
58 cells straight **south** (downstream); Diana, ordered to (36,38), went 65 cells south down the same channel
(`D:\ClaudeWork\rimmandrake\conductor\afk_20261112_night\live\tools\wade.py`).

It contradicts the design (§3.1): *"a colonist told to cross will be dragged and re-path, repeatedly"* and the
edge lane *"a pawn there can still wade across or out"*. Today no pawn re-paths and no edge-lane pawn can wade out.
The fast lane is "inescapable" by design, so the bruise toll then runs for the whole length of the river.
Also untested: whether the sea's TerminalBiomes shove (same idiom, cited in the file header) freezes jobs too.

Not fixed here: the fix is small in lines (restart the path, or end the job, after the move) but it changes the
carry's feel and touches a VALIDATED mod, and it can only be proven live. Filed as its own item.

## Problem B — the health number does not add up [measured lower bound]

Vanilla summary health multiplies `1 - Severity/(75 x HealthScale)` per injury (`Verse/SummaryHealthHandler.cs`,
`Verse/Hediff_Injury.cs:116`). Five Blunt hits of at most 5 each give at least 0.933^5 = **0.71**, not the 0.56
reported. So either Fuego carried earlier injuries, or `IncomingDamageFactor` > 1, or something else also hurt
Fuego. Unexplained; read Fuego's full hediff list on the next run.

## Live run sheet (NOT run; offline helper)

Tier: any list with FlowWorks + all DLC; a map with a natural river (the TropicalRainforest quicktest of 2026-11-12).
1. `rimflow bridge take --for "river bruise source"`; note a colonist P on dry land beside the fast lane.
2. Read P's hediffs (`jawa` pawn health read) -> baseline list; record summary health.
3. Order P undrafted `jawa/ordered_job Goto` to a cell across the river. Advance 60 ticks at a time for 3000 ticks;
   each step log: P position, `P.CurJob.def`, `P.pather.Moving`, the BattleLog count, P's hediff list.
4. Confirm rank 1: every new Bruise appears on a step where P moved exactly one cell downstream, no new BattleLog
   entry. Confirm Problem A: after the first downstream jump `pather.Moving` stays false, `CurJob` stays Goto, P
   never moves except downstream.
5. Set Mod Settings `crossingHazardsEnabled=false` (or `bruiseChancePerStep=0`), repeat with a second colonist:
   drift continues, zero bruises.
6. Draft both, release the bridge. Evidence to `D:\ClaudeWork\rimmandrake\conductor\night_20261114\`.
