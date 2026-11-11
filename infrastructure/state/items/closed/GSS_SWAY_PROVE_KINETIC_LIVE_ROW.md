## spec
found-by: BENCH helper (2026-11-05), writing live proofs for GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC. Existing M22a/b rows use the synthetic `explode:x,z,r,dmg,kinetic` token (a cloned Bomb carrying a local RM_KineticBlastExtension). The completed tooling adds an optional registered damage defName and a runnable proof using an actual KineticArms definition (src/RimMandrake/KineticArms/Defs/DamageDefs/RM_KineticArms_Damages.xml), with setting readback and per-arm census `kineticSways` deltas. This L0 tooling item does not discharge the separate A2 L2 visible-sway acceptance.
## criteria
- A1 L0: AerialProbe explode takes an optional damage defName; offline selftest covers the parse
- A2 L0: a validation_aerial.py row: kineticSway on + kinetic blast near a tail -> census kineticSways > 0; off -> 0 (MOD class, names the setting key)
- A3 L0: infrastructure/state/live_proofs/GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC.txt with live-mods GimmeSomeSlack, KineticArms running that row

## Completed 2026-11-11

Published artifact 732415605fcea4c88e8e67c9a5e30c787e08a2cd and evidence 305b705440da308e408f60e9fecb46dff8541a79 satisfy the three L0 criteria. The explicit launcher uses `--kinetic-damage RM_Repulse_Palm` and requires both fresh MOD rows and driver success. Generic GSS-only callers keep the synthetic default.

Focused runner PASS 4/4. Normal GSS 4485/4485 and aerial 155/155 remain current by final C#/project-input hashes. Shipping build has zero warnings/errors, with all 70 DLL stamp inputs rehashed. Fresh independent Opus accepted and actual Whittle validators passed. Parent independently decoded both complete observer traces and matched 149 final inputs. Evidence is in `whittle/fw-drain-kinetic-sway/`.

Actual KineticArms integration, visible sway, allocation behavior and live gameplay acceptance remain unverified on the separate GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC item. Strict selector parsing rejects padded/extra fields. Early source commits 0cd82b62db and 913a415fdf lack the requested coauthor trailers. Their history is preserved and the omission is disclosed.
