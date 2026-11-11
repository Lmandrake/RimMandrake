## spec
found-by: BENCH helper (2026-11-05), writing live proofs for GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC. Existing M22a/b rows use the synthetic `explode:x,z,r,dmg,kinetic` token (a cloned Bomb carrying a local RM_KineticBlastExtension). The gap is an optional registered damage defName and a runnable proof using an actual KineticArms definition (src/RimMandrake/KineticArms/Defs/DamageDefs/RM_KineticArms_Damages.xml), with setting readback and per-arm census `kineticSways` deltas. This L0 tooling item does not discharge the separate A2 L2 visible-sway acceptance.
## criteria
- A1 L0: AerialProbe explode takes an optional damage defName; offline selftest covers the parse
- A2 L0: a validation_aerial.py row: kineticSway on + kinetic blast near a tail -> census kineticSways > 0; off -> 0 (MOD class, names the setting key)
- A3 L0: infrastructure/state/live_proofs/GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC.txt with live-mods GimmeSomeSlack, KineticArms running that row
