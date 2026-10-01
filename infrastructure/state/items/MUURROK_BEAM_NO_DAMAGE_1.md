# MUURROK_BEAM_NO_DAMAGE_1 — the muurrok's mirror beam fires and hurts nothing

Found by the FOUNDRY live session round 2 (`Transient/LIVE_SESSION_2_2026-10-01.md`, full list, RM_Stillsand quicktest,
deployed `7caa6b5c9`). Part of `STILLSAND_EVENT_CREATURES_LIVE_1` criterion 3.

## What was seen
- `jawa/pawn_use_verb pawn=<RM_Muurrok> action=cast verb="mirror crest"` was **accepted** 4 times under Clear weather
  (the verb read `Bursting`, so the burst ran). Targets: one moving muffalo, then three muffalo downed with
  `jawa/pawn_force_incapacitate` on a cleared gravel pad 12 cells away (inside 3.9..22.9). ~270 ticks per cast.
- No target, and no pawn anywhere on the map, gained `Burn` (the `hediff` of `RM_MirrorGlare`). No exception in Player.log.
- The weather gate works: the same cast is refused (`IsStillUsableBy` false) under `RM_DuneGale` and `Sandstorm`.

## Where to look (`src/RimMandrake/Stillsand/Source/RM_Verb_MirrorBeam.cs`)
`TryCastShot` returns true without hitting when `TryGetHitCell` fails; `HitCell` scales damage by `SunFactor`. Either the
hit cell is never found, or the damage rounds to 0, or `HitCell` applies to the cell without finding the pawn. Read it
against vanilla `Verb_ShootBeam.TryCastShot`/`ApplyDamage` before changing anything.

## criteria
- On a Stillsand quicktest, a cast at a downed pawn 8-15 cells away in Clear weather leaves `Burn` on it
  (`jawa/list_pawns includeHealth`), with no exception in Player.log.
