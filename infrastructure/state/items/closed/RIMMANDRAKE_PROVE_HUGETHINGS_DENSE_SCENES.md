# RIMMANDRAKE_PROVE_HUGETHINGS_DENSE_SCENES

Dense live proof set for HugeThings (owner addendum 2026-11-12: few dense scenes, every row fails alone, a shared
control). Plan and inventory: `D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\HugeThings\plan.md` and
`inventory.md` (40 acceptance rows; before 6 PROVEN / 25 WEAK / 9 NO). Serves the live half (A2 L2) of
RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES. Proof lines: `infrastructure/state/live_proofs/<this id>.txt`;
tier `mods__mandrake_rm_hugethings__mandrake_rm_hugethingstestraces__mandrake_rm_biomes__neku_largepawns`.

## spec
- Showcases exit 0 PASS / 1 MOD FAIL / 2 UNMEASURED (`showcase_common.Showcase.exit_code`), so a site or harness
  fault is never charged to the mod.
- `showcase_plants_live.py --no-door`: the door seal is BLOCKED (9+ Codex rounds, owner question 1) and is not required.
- `showcase_titan_live.py` gains the CONTROL phase: the same-mass UNTIERED `RM_TestTitanT2Control` is sent at the
  sealed goal and must leave the 24-wall ring whole, so CROSSING_destroys can be credited to the titan's tier.

## criteria
- A1 L0: selftest_showcases (CONTROL, --no-door, exit codes, control-breaks-ring mutant red), footprint, fuzz, lint, test_races, titanic_lint, walls_slots selftests green.
- A2 L2: showcase_plants_live.py --no-door: PLANT_grown, PLANT_trunk_solid, PLANT_cap_open, PLANT_selection PASS on the restored calm site.
- A3 L2: showcase_titan_live.py: CONTROL, CROSSING, DEATH, CROWD rows PASS in order on the restored calm site.
- A4 L2: test_titan_footprint_live.py six rows PASS on this tier (regression guard of 2026-11-06).

## not proven here
Door seal (row 14), hitbox / save-load relink / mapgen trunks (rows 10-12), validation.py static chains (need a
modcheck run), custom tiers, flyers (never live). Owner Designer questions: inventory.md "Needs the owner's Designer work".
