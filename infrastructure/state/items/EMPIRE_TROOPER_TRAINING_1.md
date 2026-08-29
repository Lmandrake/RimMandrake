# EMPIRE_TROOPER_TRAINING_1

## spec
`Jawa_Empire_Grunt/Heavy/Specialist` (JawaFactionRoster.xml:43/96/144) carry no
training hediffs — `grep -c Training` on the roster file is 0, measured
2026-08-28. OuterRim's own troopers ship shooting-stat trainings
(`OuterRim_StormtrooperTraining`, `_ISBTraining`, `_DeathTrooperTraining`,
Defs/HediffDefs/ in workshop 2919248699/1.6). Apply the stormtrooper line to our
three kinds via the SAME mechanism `OuterRim_ImpStormtrooper` uses — read that
def for the field name; do not guess it (PawnKindDef hediff fields differ by
version and mod).

## verify
Offline: the mechanism copied verbatim from `OuterRim_ImpStormtrooper`, field
name quoted with the source path:line. The hediff defNames must carry
`MayRequire="Neronix17.OuterRim.GalacticEmpire"` gating if the field supports it,
or the item must state why not.

## criteria
A pawn of each kind spawned on a quicktest (may piggyback EMPIRE_RAID_QUICKTEST_1)
shows the training hediff in its health tab.

## Watch out
- The hediffs' C# class `Hediff_Training` lives in Outer Rim CORE, not the
  Galactic Empire DLL — both mods must be active for the class to resolve.
- The OuterRim FACTION stays cut; this touches pawnkinds only. Nothing here may
  reference `OuterRim_GalacticEmpire` the FactionDef.
