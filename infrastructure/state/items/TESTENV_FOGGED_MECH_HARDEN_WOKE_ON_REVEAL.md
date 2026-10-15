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
