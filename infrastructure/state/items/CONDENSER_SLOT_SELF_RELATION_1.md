# CONDENSER_SLOT_SELF_RELATION_1 — WeepingStones quest slot resolve logs a red error every call

Found by the kernel extraction audit, `Transient/kernel_audit_20261008.md` (2026-10-08).

## spec
Commit `44de46280`. Old `src/RimMandrake/WeepingStones/Source/RM_CondenserQuests.cs:31-36` `Usable()`
rejected `f.IsPlayer` before reading anything relational. New `RM_CondenserQuests.cs:35-43` `Resolve()`
builds a `FactionInfo` for EVERY faction, including the player's own, reading `f.PlayerGoodwill` and
`f.HostileTo(Faction.OfPlayer)`. For the player faction that asks `RelationWith(self)`, which logs
"Tried to get relation between faction X and itself" (RimSage, `Faction.cs:487-493`). The faction
picked is unchanged (the kernel filters `isPlayer`), but every slot resolve now writes a red error
to Player.log.

Fix: skip the relational reads (goodwill/hostile) when `f.IsPlayer` (fill defaults), or filter the
player out before building the info list.

## verify
Offline: the info builder never calls PlayerGoodwill/HostileTo on `Faction.OfPlayer`.

## criteria
No relation-with-itself error from Resolve; slot choice unchanged.
