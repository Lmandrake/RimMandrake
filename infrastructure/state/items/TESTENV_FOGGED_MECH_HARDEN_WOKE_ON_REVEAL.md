# TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL

Filed by BENCH 2026-10-15 (live round 5). Evidence: `Transient/bench_live_20261015_r5/live/gss/who_downed.json`,
`gss_proof_all_run1.log`, `gss_proof_all_run3.log`, `origin_run3.json`, and probes `live/probes/arrival_origin_1.json` and
`arrival_origin_2.json`.

What happened in GSS `proof_all` on fresh quicktest maps:
- Run 1: a ThreatBig "Area revealed" letter arrived 2 ticks after the noon pin. A hostile `Mech_Militor` arrived 58 ticks later
  and downed a colonist.
- Run 3: `Mech_Lancer` and 2 `RM_HullBolt` arrived during the aerial block. That map carried AncientExostriderRemains.
- The probes ran the pin with no fog reveal and saw 0 arrivals.

## mechanism (rimsage 1.6 source, read 2026-10-15)

- `FogGrid.NotifyAreaRevealed`: the ThreatBig "Area revealed" letter fires when `FloodFillerFog.FloodUnfog` uncovers a
  mechanoid pawn. FloodUnfog also sets `mindState.Active = true` on every pawn it uncovers, which wakes sleeping pawns.
- `Verse/TriggerUnfogged`: when its cell is unfogged after having been fogged, it sends its signal. `SignalAction_Ambush`,
  `SignalAction_DormancyWakeUp` and the other `SignalAction_*` things answer that signal.
- RectTrigger and RadialTrigger fire when a colonist comes near.
- All of these are Ethereal things, so they can be listed and vanished. A Vanish destroy never activates them.
- Which trigger fired in r5 is UNPROVEN: `pawn_origin` read notFound after the save/load. The fix covers every trigger class.

## built (2026-10-15, offline)

- `src/RimMandrake/Utils/modcheck/testenv_guards.py` `disarm_fog_triggers()` lists TriggerUnfogged, RectTrigger,
  RadialTrigger, TriggerContainerEmptied and the 11 Core `SignalAction_*` defs. It vanishes them with `destroy_batch`
  categories=Ethereal and reads them back. A failed or truncated listing is never reported as verified.
- `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` P3, in this order before the clock moves:
  1. Disarm the triggers.
  2. Destroy hostile buildings.
  3. Vanish non-colonists (`destroy_bulk nonColonists`), which includes fogged sleeping mechs.
  4. Pin noon and apply the quiet profile.
  5. Disarm again, then read hostile pawns back.

  P3 FAILs (SITE) unless the triggers read back disarmed and no hostile pawn is left. The new evidence fields are
  `fogTriggersDisarmed`, `fogTriggersAfterQuiet` and `hostilePawnsLeft`.
- `src/RimMandrake/Utils/validation_core.py` `reveal()` disarms before a colonist's sight unfogs anything. It is used by
  `prepare_site`, the aerial and style sites, and FlowWorks' sites. Its result carries `fogTriggers`. `prepare_site` records
  its site UNMEASURED/SITE when a trigger reads back still armed.
- Offline checks, all green:
  - `selftest_testenv_guards.py`: disarm verified, refuses a failed or truncated listing, reports a trigger that survives.
    `reveal` disarms before the first teleport. `prepare_site` refuses an armed site (the can-fail check).
  - `selftest_proof_all.py` 5b: the disarm runs before `destroy_bulk` and the pin. Triggers that survive FAIL P3, and a
    hostile pawn left FAILs P3.

## proof (next live round, bridge held, game up on the gimmesomeslack / ratchet_pilot tier)

```
python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\gss_fogguard.log" | grep -E "P3_|aerial|ABORTED|NOT PASS"
```

Then read the P3 row and the vitals journal:
- P3 PASS, with `fogTriggersDisarmed.found` recorded (on maps with ancient dangers it should be above 0),
  `fogTriggersAfterQuiet.verified` true and `hostilePawnsLeft` empty.
- `jawa/vitals action=events` shows no `hostile_arrival` and no "Area revealed" ThreatBig letter after P3.
- The aerial block finishes without a restart.

Run 2 or 3 fresh maps, because r5 needed several maps to see it once.

## residual (r6 map 3, 2026-10-15) -- found and closed offline

What r6 map 3 showed (`Transient/bench_live_20261015_r6/live/gss/vitals_map3.json`, seq 133-155; `proof_all_map3.json`):
- P3 passed: 2 triggers vanished (RectTrigger, SignalAction_Letter), 15 non-colonists destroyed, `hostilePawnsLeft` [].
- The noon pin was at tick 15799. A ThreatBig "Area revealed" letter came at 15831, inside the matrix block.
- `RM_LivingBolt` and 2 `Mech_CentipedeGunner` (ids 4793-4797) arrived at 15868. Their ids are older than the map-gen pawn
  ERR (4886), yet they were in neither the P3 sweep nor the 15808 vitals census. So they were NOT spawned at P3.
- The core block's own calm destroyed them at 15868 (`blocks.core.nonColonistsDestroyedFirst` 3). There was no damage.

The path (rimsage 1.6 source, read 2026-10-15):
- The ThreatBig "Area revealed" letter comes only from `FogGrid.NotifyAreaRevealed`. Only `FloodUnfogAdjacent(..., sendLetters)`
  calls it.
- Mid-run, its one caller with letters on is `Building.DeSpawn` -> `FogGrid.Notify_FogBlockerRemoved`. Removing a fog-making
  edifice (rock, wall) next to unfogged ground floods the fogged pocket behind it. That flood wakes every pawn there and
  letters if one is a mechanoid.
- A colonist's sight does not do it: `Pawn.SpawnSetup` calls `FloodUnfog` with no letter. A door does not do it either
  (`Notify_PawnEnteringDoor` passes sendLetters false).
- The matrix block's board clear (`run_live.clear`: `destroy_batch categories=All`) removes such rock. So does every
  `prepare_site`.
- This is not a trigger type the guard missed (there was no trigger left) and not a reveal by a pawn's sight. It is a later
  fog-blocker removal.
- Where the 3 mechs were held before they spawned is PRESUMED, UNPROVEN: unspawned in some holder, and released when the
  clear destroyed it. The game is down, so it cannot be probed now. The fix does not depend on it.

The guard (`testenv_guards.clear_map_fog`, run as the last step of `proof_all.calm_map`, in p2c and again in P3):
- It unfogs the WHOLE map with `jawa/set_fog unfogAll` (`FogGrid.ClearAllFog`, which sends no letter) and reads back
  `foggedCellsNow` == 0.
- With no fog left, no later rock removal has a pocket to flood. No letter, no woken sleeper.
- It refuses to unfog while a hostile pawn is listed, because `Pawn.Notify_Unfogged` would wake him.
- P3 FAILs SITE unless `mapFogCleared.verified` is true.
- Fog is not what any GSS row measures. Sites are already unfogged by `prepare_site` and `reveal`.

Offline checks that can go red:
- `selftest_testenv_guards.py` `test_map_fog`: a fog-pocket model letters ThreatBig on a rock clear without the guard, and
  not after it. It also checks the refusal while a hostile is listed, a refused unfog, and fog left after the unfog.
- `selftest_proof_all.py` 5c: the unfog runs after `destroy_bulk` and before the pin. Fog left FAILs P3. A hostile left
  means no unfog.

Not covered: FlowWorks/aerial sites prepared outside proof_all still clear rock beside fog (`prepare_site`). Only proof_all
unfogs map-wide, because only it has swept every non-colonist first.

## proof (next live round)

Run it on 3 fresh maps (the r6 rate was 1 in 3):
```
timeout 1200 python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\gss_fogguard2_<n>.log" | grep -E "P2c_|P3_|ABORTED|NOT PASS"
```
Then read the result:
- P3 PASS with `mapFogCleared.verified` true and `foggedNow` 0, plus `res.control_noise_calm.calm` true.
- `jawa/vitals action=events` shows no "Area revealed" letter and no `hostile_arrival` after P3 on any map.
