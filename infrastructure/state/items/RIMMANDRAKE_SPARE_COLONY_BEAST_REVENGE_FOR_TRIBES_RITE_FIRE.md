## spec
The Deep Desert Tribes' fire rite (mod `mandrake.rut.pyrelandsmechanics`, `LordToil_RUT_RiteHarvest.Init`) lights its front with
`IgniteRiteFront(at, lead)`, so the tribal lead harvester is `Fire.instigator`, and `Fire.TrySpread` hands that instigator to
every child fire. Vanilla `Fire.DoFireDamage` passes `instigator ?? this`, and `Pawn_MindState.Notify_DamageTaken` turns a wild
animal Manhunter when the instigator is a Pawn whose faction is humanlike, at `manhunterOnDamageChance` times 3 (no distance is
passed, so `GetManhunterOnDamageChance` clamps its distance factor to 3), with the vanilla letter "<animal> revenge: ... is
attacking after being harmed!". So every wild animal that the rite's burn touches rolls revenge and then hunts the colony
for a fire the colony did not set. Fire-hawks seek burns by design (`JobGiver_RUT_FireHawkSeekBurn`), so they meet it first:
RM_FireHawk 0.15 x 3 = 0.45 per burn hit, before the instigator's factors.

[measured] Pyrelands visit 2, run 1 (2026-11-21, game a, JawaBench vitals telemetry
`tps_20261121T033246Z_2dfeb90980524ffb9043ca39d97954e4_9632_002.jsonl`, epoch 54): letter "The fire rite" at tick 770701,
four pawns left the map at ticks 796681-797101, then letter "Fire-hawk revenge" (ThreatSmall) at tick 845150 while hawk
92656 was burning (job ExtinguishSelf, health 0.978 -> 0.934). Colonists asleep; no player building on the map; every fire
in the run's start save was lit by a wild hawk (no faction). That run had the Tribes mod on its list by mistake
(RIMMANDRAKE_TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER_IN_BURN_WALK took it off every Pyrelands tier).

The comment on `PyrelandsFireFront.IgniteAt` says the tribe's name on the rite fire costs no arson debt; it does not name
this vanilla consequence. Nothing in either mod reads the tribe's name off a fire except `MapComponent_BurnLine.IsPlayerAttributed`,
which only counts the player's.

This belongs to the Tribes mod's own Design Version 0.1.0, which starts only after Pyrelands 0.1.0 passes
(design/concepts/Pyrelands/version/VERSION.json scope). Do not work it before then.

## verify
The live run in the acceptance test below: after "The fire rite", no "<animal> revenge" letter in the vitals telemetry over one
game day with wild fire-hawks in the burn, and a player-set fire still reads IsPlayerAttributed true.

## criteria
- A peaceful rite never makes a wild animal take revenge on the colony for the rite's fire.
- A fire the player sets still counts as the player's arson (IsPlayerAttributed unchanged).
- Whether the rite fire keeps the tribe's name (and something else stops the revenge roll) or carries no name is the Tribes
  mod's design call at its 0.1.0.

## Acceptance test
Live (no offline oracle can read vanilla's revenge roll; the instigator decision lives in Verse code): on a list with the Tribes
mod, send one rite through the fire clock, keep two wild RM_FireHawk in its burn for one game day, read the vitals telemetry.
Red today: a "<animal> revenge" ThreatSmall letter after "The fire rite" (seen once, visit 2 run 1). Green: no revenge letter
across the day, and a player-set fire on the same map still reads IsPlayerAttributed true. If the fix moves the decision into a
pure kernel function (no Verse types), its offline test is written with the fix.

## refs
file: src/RimUtinni/PyrelandsMechanics/Source/LordJob_RUT_FireRite.cs
file: src/RimMandrake/Pyrelands/Source/PyrelandsFireFront.cs
