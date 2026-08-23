# PAWNKIND_RESISTANCE_UNDEFINED_1 69 of our pawn kinds have no initialResistanceRange; capturing one throws

## spec

## Measured, 2026-08-23, from observed/logs/2026-08-23_Player.log.final

69 of our own humanlike PawnKindDefs log
`Config error in <KIND>: initial resistance range is undefined for humanlike pawn kind.`
All 69 are `RimMandrake*_Kind` in
`D:\Luke\dev\Rimworld\src\Jawa\RimMandrake_StarWarsRaces\Defs\PawnKindDefs\RimMandrakePawnKinds.xml`.
That is roughly three quarters of the whole load's config-error volume.

## It is not only a log line

`initialResistanceRange` is `FloatRange?` (PawnKindDef.cs:105) and three vanilla call
sites dereference `.Value` with NO null guard:

- `Pawn_GuestTracker.SetGuestStatus`, Prisoner branch —
  `float num = pawn.kindDef.initialResistanceRange.Value.RandomInRange;`
  Throws NRE the moment one of these pawns is made a prisoner. It throws AFTER
  `DropAndForbidEverything()` and after the lord was notified, so the pawn is left
  half-transitioned.
- `ITab_Pawn_Visitor.cs:225` — the prisoner tab UI.
- `SanguophageUtility.cs:196` — hemogen resistance gain.

`initialWillRange` is safe: `BasePlayerPawnKind` sets it to `0~0`. Only resistance is
unset. Vanilla `Colonist` sets `<initialResistanceRange>13~21</initialResistanceRange>`;
our generator copies Colonist's apparel fields and stops short of this one.

## 🔴 The fix already exists in the generator and has never shipped

`src/RimMandrake/Utils/gen_races_mod.py:912` emits
`<initialResistanceRange>10~20</initialResistanceRange>`, with a comment describing
this exact defect. It was committed `e4d60403`, 2026-08-15 13:53.

The XML it writes was created 2026-08-15 05:56 (`ea504641`) — BEFORE that fix — and
has never been regenerated since. The two edits it took today (`e479d8ae` robes+hoods,
`9bb5a5bb` faction colours, 01:48 and 02:43) were made BY HAND into a file whose own
header says `GENERATED ... Do not hand-edit`.

⚠️ So the file is now hand-diverged from its generator. Re-running
`gen_races_mod.py` would emit the missing field AND discard today's hand edits.
Reconcile first, or add the one line to the 69 defs directly and fix the divergence
separately.

`Jawa_Patches/Defs/PawnKindDefs/JawaColonistPawnKinds.xml` is NOT affected — it sets
`13~21` at line 79.

## Verify

- `grep -c initialResistanceRange` on the src file returns 69, and on the deployed copy
  under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\RimMandrake_StarWarsRaces\`
  also returns 69. Both currently return 0.
- Next load: zero `initial resistance range is undefined` lines in Player.log.

## Watch out

- 🔴 **Do not "fix" this by re-running `gen_races_mod.py` and calling it done.** The XML
  it overwrites carries two hand edits made today that the generator does not know about
  (robes+hoods `e479d8ae`, faction colours `9bb5a5bb`). Regenerating silently reverts
  them, and the revert looks like a clean success.
- The deployed copy under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\`
  is a separate file. Writing src is not deploying it — `deploy_custom_mods.py --apply`.
- A passing grep proves the field is PRESENT. It does not prove the capture path works;
  that wants a live capture of one of these xenotypes, so it belongs in the next load's
  reading list.
- Filed by REP from a log reading, not from a game test. The 69 count is measured off
  `observed/logs/2026-08-23_Player.log.final`; the mechanism is read from RimWorld source
  (`PawnKindDef.cs:105`, `Pawn_GuestTracker.SetGuestStatus`), not inferred.
