## spec
ExplosiveGrowth's `scope_native_only` row (`src/RimMandrake/ExplosiveGrowth/validation.py` ~line 954) returns
UNMEASURED whenever a campaign layer is loaded, because the Utinni roster in `mandrake.rut.patches` puts every biome
in scope (validation.py line ~965). The sprint tier `biomes_sprint` loads `mandrake.rut.patches`, so on the sprint's
one launch this row cannot PASS and M1 (0 UNMEASURED) cannot hold for ExplosiveGrowth.

Resolution (no code change needed): run that single chain on the `explosivegrowth_solo` tier (Baroque Biomes + the
bridge, a seconds-long minimal load) in the same live sitting, after the biomes_sprint suites. Ordered in
`Transient/biome_sprint_live_order_2026-10-16.md` step 9. Alternatively the owner marks it a solo-tier row at S0.

## done when
`scope_native_only` PASS on `explosivegrowth_solo`, recorded with `rimflow verify`, and the EG manifest names the tier.
