I found no blocking defect. Every frozen bullet holds on source and raw evidence, with the limits listed below. I did not read any maker, pilot or judge conclusions, and I wrote nothing.

## Bullet 1: owner use with player equipment in reach is not billed — **holds**

- **Every mutation goes through two methods.** Searching all of `src/RimMandrake`, production tank stock changes only through `TryAddLiquid` and `TryRemoveLiquid` (`Building_LiquidTank.cs:112-141`). The other direct writes are debug, legacy-unit conversion on load, and the destroy-spill. Both methods record the change only after it passes validation.
- **Recording needs a player actor.** `Record` (`RM_LiquidTheft.cs:53-68`) records nothing unless the current actor is the player's, is on the same map, and the tank is foreign. Reaching the tank (`PlayerReaches`) is now only a diagnostic and plays no part in billing.
- **Entry scopes carry the right actor**, and each one is opened before its first mutation:
  - pump `TryDraw`/`TryPour`: the pump (`Building_LiquidPump.cs:303,489`);
  - converter, pipe adapter and reaction: the machine (`parent`);
  - bath and ice melter: the bill giver;
  - faucet, sprinkler head, both bottle job drivers, and drinking from a tank: the device or pawn;
  - tank settle: the player's Empty/Fill tank (`RM_LiquidNet.cs:904`); foreign tanks always behave as Store, so they can never be the mover;
  - Dump and gravity overflow: the Dump tank (`RM_LiquidNet.cs:948`);
  - gas tap `Deliver`: the tap (`RM_GasTap.cs:76`);
  - GlowTank draw: the GlowTank, through a reflected scope (`FlowWorksWaterBridge.cs:71`).
- **Hose fills are covered.** `FillFrom` runs synchronously inside whichever scope called it.
- **Unscoped setup records nothing.** The `RM_CauldronRuinKit` setup returns early for player-owned kits. With no scope open the actor is null, so ruin and debug writes are never billed.
- **Nested scopes and exceptions** restore the previous actor; this is tested for both the core scope and the reflected one.
- **Live negative arm:**
  - the owner's powered pump moved +10000 into the foreign tank;
  - an idle, adjacent player pump was off;
  - a reachable, active player pump (its tank room included this tank) pumped 10000 out to an unrelated outflow;
  - the tank read pending `[]`, caughtBy `none`, ticks 0, goodwill 0, even though `reach=True` and a witness was present.

## Bullet 2: real player transfers keep the existing consequences — **holds**

- **Witness, catch and goodwill code is unchanged** from `red_sources/Machinery/RM_LiquidTheft.cs:57-83`. Only the "touched" gate changed: it was "stock differs and the player reaches the tank"; it is now "a player change was recorded for the current owner".
- **Offline cases that run the shipping method bodies:**
  - refusals roll back, and put-backs cancel;
  - a partial split bills only the units actually kept (-10 and -5);
  - an equal-volume swap to a different liquid is still caught;
  - owner replenishment does not hide a player withdrawal;
  - theft disabled, ownership change and a defeated faction all consume stale changes;
  - a witness arriving later cannot catch an unseen move;
  - the real `ExposeData` keeps pending changes and the caught state, and old saves default to no pending change.
- **Live positive arm:** player pump +10000 → pending saved and loaded unchanged → real `TheftTick` caught it (caught=1, ticks 0) → tick remainder compressed to 59750 → a real second +10000 transfer charged -2 goodwill → an idle tick charged nothing more.
- **Limit:** the live positive is the player pumping water *into* the foreign tank. That counts under the pre-existing rule, which billed any change. A *withdrawal* positive is only shown offline (`Take`, the Luminous draw).

## Bullet 3: regression checks tied to shipping source, and the builds pass — **holds**

- **Reds:**
  - `red1`: 1260/1261 passed; the one failure was the owner-use-with-player-in-reach test.
  - `external_red3`: production behavioural failures on the original Luminous and Cauldron sources (GasTap hash `196a23…`).
- **Final green:** `external_green2` passed 1278/1278, with the hose suites at 188/188 and 457/457.
- **Tests run shipping code.** `TankTheftHarness.targets` extracts the real bodies of `Record`, `TheftTick`, the scope, the tank methods and `ExposeData`, plus the real bridge file and gas-tap `Deliver`.
- **Hashes line up end to end.** Theft/tank/pump source hashes match across `external_green2`, `final_readback` and `final_readback_external2`. The core DLL `ec29517d…` equals the DLL whose identity was checked when live attempt 4 loaded it.
- **Builds:** FlowWorks, Cauldron and LuminousPigment all built with 0 warnings and 0 errors.
- **Narrow deploy:** four DLL/stamp files only, unrelated drift preserved, backups retained.
- **Limits:**
  - `external_red3` ran an older caller check (`ca63…`) that passed. So the external entries in the final caller check were never shown failing on the original sources; only its own built-in planted-mutation cases show it can fail.
  - The engine (enumeration, witness, scribe) is replaced by test doubles.

## Bullet 4: disposable live proof — **holds**

- **Right build, real actors.** The loaded FlowWorks DLL's MVID matched its file and its hash equals `ec29517d…`. Actors were a real owner pump, two player pumps, and a staged witness from the owner faction (`Human24593`). Source and outlet deltas were exact.
- **Run and cleanup.** Status `PASS`, `restore.status` `PASS`, and every setting read back at its original value. Existing saves were unchanged and protected save hashes are identical. The two `WHITTLE_*` saves were left in place. Cleanup stopped the game, measured it DOWN, and released the bridge.
- **Script match.** The script hash `4ac6cd…` recorded after the run equals the current script.
- **Log.** The single allowed error ("CurKindLifeStage … Shiki") is matched by exact message, captured on the unchanged site before any fixture existed, and still has RepeatCount 1 at the end. `new_errors` is empty, nothing was lost, and the log sentinel is present.
- **Limits:**
  - Scheduling is bypassed by the `ProofDrawCycle` and `Proof` adapters, which still call the real `TryDraw` and `TheftTick`.
  - Time advanced only for 2 hose-refresh ticks (tank unchanged across both) plus 1 bounded load tick, with pumps disabled during the load; ticks went 3 → 6.
  - The day-long remainder was compressed by `prime` after the genuine catch.
  - `hoseHoldsLiquid` was off during the live run, so hose filling was not exercised in game.
  - GlowTank, gas tap, settle, Dump and the job drivers are offline only.

## Minor, untested edge cases (not blocking)

- A pending-change key whose liquid def was removed, on save load.
- Running against an older FlowWorks build without the actor API: LuminousPigment then turns its feed off with a warning, and Cauldron (which hard-references FlowWorks) needs the new DLL. The two were deployed together.

would show: yes