# TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG

Filed by BENCH 2026-10-15 (live round 7, ratchet_pilot tier, HEAD 0207ac8fc2). Evidence in
`Transient/bench_live_20261015_r7/live/`: `gss/gss_fogguard2_2a_fleshbeast_preflight.log`,
`gss/gss_fogguard2_2b_fleshbeast_preflight.log`, `gss/vitals_2a.json`, `gss/vitals_2b.json`, and the probes
`probes/calm_probe_1.json`, `probes/calm_probe_2.json` (script `probes/calm_probe.py`).

## what happened

GSS `proof_all --live` aborted in preflight on fresh quicktest maps. P2c's new `calm_map()` (the
TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM guard) read back calm: triggers disarmed, non-colonists destroyed, fog cleared and
verified. Then the 600-tick control advance stopped at once on `hostile_arrival: present at arm` for Anomaly fleshbeasts (faction
Entities): Trispike + Toughspike (2a), 2 Fingerspike + 2 Toughspike + Bulbfreak (2b).

## what the probes measured (no tick advanced)

On a fresh map, `calm_probe.py` lists hostile pawns after each step of the calm.
- Probe 2 listed **0 hostiles** after `disarm_fog_triggers`, the hostile-building pass and `destroy_bulk nonColonists`.
  `destroy_bulk` walks `AllPawnsSpawned`, so this listing includes fogged spawned pawns.
- Straight after `clear_map_fog` (`jawa/set_fog unfogAll`, i.e. `FogGrid.ClearAllFog`) the same listing showed **4 fleshbeasts**,
  still at tick 1. Probe 1 showed 3.
- Their ids (38xx) are map-gen era. `pawn_origin` has no row for them. The incident journal and the letters are empty.
- They survive save/load.

So the whole-map unfog, the last step of the calm, RELEASES pawns that were not spawned before it. That step's own hostile
check runs before the unfog, so it cannot see them. 4 of 5 fresh maps this round had them (map 1 did not).

## mechanism: presumed, unproven

Vanilla 1.6 `FogGrid.Unfog` calls `Thing.Notify_Unfogged` on every thing in the cell and fires `MapEvents.CellFogChanged`.
Neither vanilla path spawns a pawn: rimsage shows only `PathFinderMapData` listening to the event, and only `Pawn` overrides
`Notify_Unfogged`. So the spawner is presumably a mod on the tier (a dormant-fleshbeast holder, or an unfog-triggered spawner),
or an Anomaly comp that rimsage's search missed. Not traced.

## guard (to build)

- After `clear_map_fog`, `calm_map()` should sweep again: run `destroy_bulk nonColonists`, list hostiles, and repeat until the
  hostile list is empty. Cap it at 3 passes. A map that will not calm FAILs P2c SITE, as now.
- `testenv_guards.clear_map_fog` should report `hostilesAfter`, so nothing a later step has to look for goes unseen.
- Also trace which thing releases them (list every Thing in the 5x5 around the spawn cells before the unfog), so the
  mechanism stops being presumed.
- Offline check that can go red: a model where the unfog spawns a hostile. Today's calm returns `calm: true`; the guarded one
  must sweep it or FAIL.

## verify (next live round)

Same as TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM: `proof_all.py --live --no-shots` on 3+ fresh maps with no preflight
GovernorStop, and `control_noise_calm` recording any hostiles that the unfog freed and the calm then swept.

## guard built (BENCH 2026-10-15, offline; `Transient/experiment_2026-10-14/testenv_hardening_3.md`)

- `testenv_guards.clear_map_fog()` (Utils/modcheck) now sweeps AGAIN after the unfog. It reads hostiles back and, while
  any is listed, runs `destroy_bulk nonColonists` and reads again, at most `MAX_UNFOG_SWEEPS` = 3 times.
- It records `releasedByUnfog` (ids), `sweepPasses` and `hostilesAfter`. `verified` now also needs `hostilesAfter == []`.
  A map that keeps releasing hostiles is `SITE: the unfog keeps releasing hostiles`, and P2c / P3 FAIL SITE without
  ticking.
- `proof_all.calm_map()` gets this through `clear_map_fog`. `control_noise_calm.mapFog` and P3's `mapFogCleared` carry
  `releasedByUnfog`. What the control and P3 measure is unchanged.
- Offline checks that can go red:
  - `selftest_testenv_guards` `test_map_fog`: the unfog alone leaves the released fleshbeasts (can-fail); the guard
    sweeps and records them; a map that keeps releasing fails SITE after 3 sweeps. Mutation (re-sweep removed): 2 checks
    red.
  - `selftest_proof_all` 5e: p2c sweeps the released hostiles before the control save; a map that keeps releasing FAILs
    P2c and never ticks; P3 FAILs on hostiles left, PASSes when they are swept.

## spawner: what the search found (the guard does not depend on it)

- **Generator, presumed (strong association): vanilla `SymbolResolver_Interior_AncientTemple`** (an ancient shrine). Its
  threat branch is 50% `randomFleshbeastGroup` (2-5 fleshbeasts, `Faction.OfEntities`, `LordJob_FleshbeastAssault`)
  when Anomaly is active, else 65% `randomMechanoidGroup` (1-5, `wakeSleepingMechanoidsOnUnfogged`), else 1-2 hives.
  That is exactly the observed set: 2-5 fleshbeasts with LordJob_FleshbeastAssault (r7 scene report), mech groups
  (r7 2c, r6 map 3) and hives (r6).
- On the probe-2 map the only triggers disarmed were one `RectTrigger` + one `SignalAction_Letter`. That is the pair
  `SymbolResolver_AncientTemple` spawns for its "ancient shrine" ThreatBig warning (`destroyIfUnfogged`).
- **UNPROVEN: why those pawns are absent from `AllPawnsSpawned` until the unfog.**
  `SymbolResolver_SinglePawn` spawns them at mapgen, and `destroy_bulk` and `list_pawns` both walk `AllPawnsSpawned`.
- RULED OUT:
  - vanilla `FogGrid.ClearAllFog` -> `Unfog` -> `Thing.Notify_Unfogged` (codex, quest "Unfogged" signal,
    `CompLetterOnRevealed`) and `Pawn.Notify_Unfogged` (wake only), per rimsage 1.6. The only `CellFogChanged`
    subscriber is `PathFinderMapData`. None of them spawns a pawn.
  - our src: no Harmony patch on FogGrid or Notify_Unfogged.
  - the tier's third-party DLLs: VEF, KCSG, AlphaBehavioursAndEvents and AlphaBiomes, searched UTF-8 and UTF-16. None
    names `Notify_Unfogged` or `FogGrid.Unfog` as a patch target.
  - def dump `GenStepDef` / `ThingDef` comps: no unfog-triggered pawn spawner. CompPawnSpawnOnWakeup cocoons and
    MechCapsule spawn on wake, not on unfog.
- To close it live: on a fresh map, BEFORE `clear_map_fog`, run `jawa/list_things` with no group filter in a 9x9 around
  the temple's RectTrigger cell, plus `jawa/scene_report` with held-pawn coverage. Then unfog and read the same rect.

## live proof (next round; same as TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM)

```
timeout 1200 python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\gss_unfogsweep_<n>.log" | grep -E "P2c_|P3_|ABORTED|NOT PASS|GOVERNOR_STOP"
```
Run it on 3 or more fresh quicktest maps. Bar:
- No preflight GovernorStop at arm.
- `control_noise_calm.mapFog.verified` true, with `releasedByUnfog` listed on any map that has a shrine.
- `hostilesAfter == []`.

## live proof r8 (BENCH 2026-10-15, HEAD 22b596181b, ratchet_pilot 22 mods): PASS

Evidence `Transient/bench_live_20261015_r8/live/gss/` (`proof_all_{1,2,3}.json`, `gss_unfogsweep_{1,2,3}.log`), write-up
`Transient/bench_live_20261015_r8/SITTING.md` §2. 3 of 3 attempts ran 110/110, no preflight GovernorStop. `mapFog.verified` true and
`hostilesAfter == []` on all three. `releasedByUnfog`: map 1 [] (shrine pair present, nothing released), map 2 5 fleshbeasts,
map 3 5 mechs (RM_HullBolt x2, Mech_Militor, RM_LivingBolt, Mech_Pikeman); one sweep pass each. P3 PASS, hostilePawnsLeft [].

**Spawner, cheap read** (`live/probes/spawner_probe.py`, `spawner_probe_{1..4}.json`; fresh maps, no tick, no sweep before the unfog):
- 3 of 4 maps released hostiles at `jawa/set_fog unfogAll` (8 fleshbeasts; 2 mechs; 2 mechs). Each group stands in an ancient
  shrine: AncientCryptosleepCasket, AncientHermeticCrate, Urn, Column, Slate within 3 cells, the RectTrigger + SignalAction_Letter
  pair in or next to it. That fits the presumed `SymbolResolver_Interior_AncientTemple` threat branch.
- `jawa/pawn_origin`, same epoch, before any save: every one is `firstObservedSpawn` at **tick 0**, `spawnChain mapgen:Settlement#N`,
  no generation observation. Factions Entities / Mechanoid. Thing ids sit next to the triggers' ids (RectTrigger12799 ->
  Bulbfreak12824..28), far below the wild animals (38533+). Incident journal empty.
- An UNFILTERED `jawa/list_pawns` (AllPawnsSpawned) at tick 1, before the unfog, lists none of those ids.
- So the unfog does NOT generate them. Mapgen makes them with the shrine and the recorder sees their SpawnSetup at tick 0, yet they
  are out of `AllPawnsSpawned` until the unfog. What holds them out (a despawn the recorder does not see, or a holder) is UNPROVEN.
