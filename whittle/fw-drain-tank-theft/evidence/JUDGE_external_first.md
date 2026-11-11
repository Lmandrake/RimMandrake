**Verdict: all four requirements are met, with the limits listed below. Evidence is limited to source code and raw receipts.**

**1. Owner use is never charged to the player — met.**
- **Source:** `RM_LiquidTheft.Record` (`Machinery/RM_LiquidTheft.cs:53-68`) only records a change when the current actor belongs to the player, is on the same map, and the tank is foreign. `TheftTick` no longer uses `PlayerReaches` at all. Before the fix, theft was any stock change on a tank the player could reach (red source, lines 47-55).
- **Callers:** every production tank change sits inside a scope that names who acted, opened before the first change:
  - Pump `TryDraw`/`TryPour` (covering the pond, outflow and hose-fill helpers)
  - Converter, pipe adapter, reaction, bath, ice melter, sprinkler and faucet
  - Both bottle jobs and drinking from a tank, scoped to the pawn
  - Tank Fill/Empty moves, scoped to the player's mover tank (`RM_LiquidNet.cs:904`; foreign tanks are always in Store mode, so the other end of any foreign pair is the player's mover)
  - Dump and gravity overflow, which only apply to player tanks (`RM_LiquidNet.cs:948`)
  - The Cauldron gas tap (`RM_GasTap.cs:76`) and the GlowTank reflection bridge, whose boxed scope is restored on return or exception (`FlowWorksWaterBridge.cs:71`)
- **Faucets:** faucet drinking is attributed to the faucet, but `BestFaucet` only offers a pawn faucets of its own faction (`Building_RM_PipeFaucet.cs:131`).
- **Unscoped writes:** only setup, debug and probe code mutates tanks without a scope.
- **Live run:** the owner's pump filled the foreign tank (0→10000) with `pending=[]`. This happened while an idle player pump touched the tank (`reach=True`) and an active player pump moved 10000 elsewhere. After that, caught, charges and goodwill were all 0.

**2. Real theft is still detected and punished; refused or restored moves are not — met.**
- Changes are recorded only after validation and before an emptying clears the liquid, so a refusal records nothing. Put-backs run under the same actor and cancel out; netting is per liquid, so a same-volume swap to a different liquid is still visible (`RecordChange`).
- Witness, catch and goodwill code is unchanged from the original. Pending changes are discarded every pass, as the original snapshot was, so a witness who arrives later cannot catch an old move.
- Settings off, ownership change and a defeated faction all discard pending changes. Pending changes, the victim, the caught-by faction and accrued ticks are saved, and old saves load with empty pending changes.
- Each of these has a check that executes the extracted production code: refused/restored, partial split, owner refill, identity swap, nested scopes and exceptions, removed route, settings, and save/load.
- Limits:
  - The tank Fill/Empty moves, Dump, machine callers and jobs are only checked by a source-text lint that confirms the scope is present. They have no behavioural test.
  - Two setup spawners are exempt by allowlist (`RM_LiquidWorksRuins`, `RM_CauldronRuinKit`).

**3. Regression checks are tied to the shipping code and builds — met.**
- **Red:** `red1` fails only `TankTheft_production_owner_use_idle_or_unrelated_active_player_reaches` (1260/1261 passed). `external_red3` fails the Luminous and Cauldron attribution checks, which is a real production failure.
- **Green:** `external_green2` passes 1278/1278 plus the hose suites.
- **Source binding:** the harness `.targets` file extracts the shipping method bodies verbatim. The staged source hashes for `RM_LiquidTheft.cs` (979418a2…), `Building_LiquidTank.cs` (ef18c0fb…) and `RM_LiquidNet.cs` (2ceff670…) match the final readback, and the stage readback shows no mismatches.
- **Builds:** FlowWorks, Cauldron and LuminousPigment each built with 0 warnings and 0 errors.
- **DLL identity:** the live game loaded the same FlowWorks DLL as the final readback (sha `ec29517d…`, MVID matches the file).
- **External deploy:** only the four DLL/stamp files were deployed; that deploy passed, and the 38 unrelated files that differed from the full plan stayed unchanged.

**4. Live proof — met, with limits.**
- **Actors:** the tank and pump 24589 belonged to OutlanderCivil "Andia"; pumps 24590 (idle, off) and 24591 belonged to the player; the witness was Human24593 of the same faction.
- **Theft arm:** the player pump moved 10000 into the tank and the pending change was `+10000`. It survived an occupied save/load (load advanced 1 tick with pumps disabled; water in the three cells unchanged). The next pass caught the player with no early accrual.
- **Goodwill:** after `prime`, a real second transfer cost the faction −2 goodwill through the vanilla goodwill call, and an idle pass accrued nothing.
- **Time:** 2 setup ticks with pumps disabled to refresh hose indexes, plus 1 load tick; checked against `end-start`.
- **Restore:** passed with settings restored; existing and protected saves unchanged; game stopped and bridge released.
- **Log tap:** 0 lines lost and no new errors. The one allowed error ("CurKindLifeStage … Shiki", seq 32) happened during the site load before any test fixture existed and occurred once, so the allowance hides nothing.
- Limits:
  - Scheduling was bypassed through the proof entry points.
  - The caught day's goodwill timer was compressed (`prime`).
  - Hoses held no liquid during the run, so the hose-fill path was not exercised live.
  - The GlowTank and gas-tap fixes have no in-game demonstration.
  - Two WHITTLE save files were left in the Saves folder.
  - The live script's recorded hash predates attempt 4. The output structure matches the current script, but there is no hash taken after the run.

would show: yes