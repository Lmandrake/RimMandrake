# RIMMANDRAKE_DROP_TRIBES_FROM_PYRELANDS_TEST_TIERS

## spec
By card 2026-11-13 ~9:30 PM PST ("Own mod, own version, later") the Tribes mod (mandrake.rut.pyrelandsmechanics) stays out of
test mod lists until its own 0.1.0 starts. [measured] `modset_builder.py` TIERS whose `want` includes it: pyrelands,
ratchet_pilot, biomes_sprint, evening_20261113 (inherits ratchet_pilot), acc_green_min2, heap_full_on_steve. Remove it from the
Pyrelands-testing ones (pyrelands, ratchet_pilot, biomes_sprint; evening_20261113 follows) AFTER tonight's showing; owner said change nothing tonight.
Check what depends on it (a tier's patches may guard on it) with modset_builder plan before and after. Acceptance: plan for
`pyrelands` and `ratchet_pilot` lists no mandrake.rut.pyrelandsmechanics and resolves.
