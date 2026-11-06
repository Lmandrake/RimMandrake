## spec
found-by: BENCH helper (2026-11-05), writing live proofs for GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC. Its A2 L2 ("kineticSway on, tails visibly sway; off, they hang still") has no live row and no way to make one today: AerialProbe `explode:x,z,r,dmg` uses only DamageDefOf.Bomb, and sway is triggered only by a DamageDef carrying RM_KineticBlastExtension (KineticArms mod, src/RimMandrake/KineticArms/Defs/DamageDefs/RM_KineticArms_Damages.xml). The probe census already exposes `kineticSways`.
## criteria
- A1 L0: AerialProbe explode takes an optional damage defName; offline selftest covers the parse
- A2 L0: a validation_aerial.py row: kineticSway on + kinetic blast near a tail -> census kineticSways > 0; off -> 0 (MOD class, names the setting key)
- A3 L0: infrastructure/state/live_proofs/GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC.txt with live-mods GimmeSomeSlack, KineticArms running that row
