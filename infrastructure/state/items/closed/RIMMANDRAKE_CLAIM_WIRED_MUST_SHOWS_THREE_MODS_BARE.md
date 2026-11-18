# RIMMANDRAKE_CLAIM_WIRED_MUST_SHOWS_THREE_MODS_BARE

## spec

`python3 src/RimMandrake/Utils/testq/selftest_testq_coverage.py` is red on main (watched 2026-11-17 ~11:20 AM PST):
"the committed wired_mods.json holds >= 6 mods, each selectable" fails because three wired mods are refused by the
modcheck preview, `validated must-show lines no component claims`:

- Contagion: contagion_bloom_reads_unwholesome, contagion_burn_reads_as_danger, contagion_flora_reads_as_flesh,
  contagion_repulsor_clears_sky, contagion_sunbeam_reads_as_beam, contagion_unfinished_read_malf
- FeverWood: feverwood_branch_home, feverwood_water_memory
- LeaningScrub: scrub_fire_and_belief, scrub_native_ecology, scrub_routes_deliberate, scrub_tree_economy,
  scrub_vines_integral, scrub_wind_home

Evidence: `D:\ClaudeWork\rimmandrake\conductor\helpers\drop_1114_evidence\cov.txt` lines 34-38 (G5 coverage: 32 of 130
harnessed mods wired and selectable). The refusal is modcheck's (same class as
RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE), not the dropped 18c limit: the filler would send each refused
selection to SteveDesktop to die INVALID after a deploy.

## fix

Give each line a component in the mod's `validation.py` that really tests it (`shows=<id>`). Until a mod's lines are
claimed, unwire it from `src/RimMandrake/Utils/testq/wired_mods.json` with its reason, as Graffiti was, and re-wire it in
the change that claims them. Removing or un-validating a must-show line loosens a north-star bar: the owner's call.

## verify

    python3 src/RimMandrake/Utils/testq/selftest_testq_coverage.py

## criteria

The selftest exits 0, and `python3 src/RimMandrake/Utils/modcheck/cli.py run <Mod> --chains <its wired chains> --preview`
exits 0 for each of the three mods that stays wired.
