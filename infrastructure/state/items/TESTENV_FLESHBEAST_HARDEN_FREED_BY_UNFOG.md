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
