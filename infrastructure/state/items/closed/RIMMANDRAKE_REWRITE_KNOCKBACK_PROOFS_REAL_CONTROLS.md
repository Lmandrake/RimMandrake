# RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS

## spec

Step 8 of `design/concepts/ExplosiveKnockback/plan.md`. The 17-row `script_audit` in `design/concepts/ExplosiveKnockback/record.json` lists what each existing scene in `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` lacks and which scene in `scenes.json` it becomes. Each scene asserts its start (INVALID otherwise) and runs the control named in scenes.json.

## Watch out

- The airborne-spared case (`spared_states`) forces the pawn's flying state with a test hook and reads it: never launch a live flight (standing ruling).
- `caps`, `tick_cap`, `shelf` and `items` currently assert behaviour his answers reverse (d_c_all_fly, d_c_wild, d_goods_fly). Rewrite or remove them, and do not keep them green.
- shield_counter, immunity_window, lookup_projectile, lookup_zero_wins, impact_factor, body_override and emp_no_throw have never run live.
