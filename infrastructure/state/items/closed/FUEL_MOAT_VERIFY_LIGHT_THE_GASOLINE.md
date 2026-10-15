# FUEL_MOAT_VERIFY_LIGHT_THE_GASOLINE

Live proof of CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15). Built and offline-green; never run live.
Progress and numbers: `Transient/release_push_2026-10-15/fuel_moat.md`.

## run

- Deploy FlowWorks + EmpirePursuit (`deploy_custom_mods.py --mod FlowWorks|EmpirePursuit --apply`), then
  `python3 src/RimMandrake/FlowWorks/northstar/extension_proof.py` for chains `fuel_moat_chemfuel` and
  `fuel_moat_astrofuel` (rows: chemfuel_moat_goes_up, chemfuel_inferno_off_smoulders, astrofuel_channel_detonates,
  utinni_blast_summons_raid, astrofuel_detonation_off_burns).
- Review map: stations "Chemfuel goes up like gasoline" and "Astrofuel detonates" (frozen unlit; cards say how to light).

## look for

- Hitching: time a detonation of a large astrofuel body (e.g. 30x30 dug D2) with the TPS read; the plan holds <=4 blasts and
  <=400 emptied cells a tick (offline: 20k cells planned in 15 ms), but the live cost of 4 vanilla Bomb explosions a tick is
  UNMEASURED.
- Knockback (PawnFlyer_Stun) on a pawn mid-job; a muffalo dying before the throw reads UNMEASURED.
- The investigating raid's CenterDrop onto a burning moat.
