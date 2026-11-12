# BIOME_TRANSITIONS_JUDGE_VS_BAROQUE: done statement

Owner, C06, 2026-10-10 (`design/RimMandrake/mod_audit/OWNER_RULINGS.md`): *"Also need to look at transitions. With our
baroque biomes they may no longer make sense and actually need to go."* and *"Experiments required to validate."*
The item carries no `## Done when`; these bullets come from its title and that ruling, nothing more.

- **A judgment exists, with a verdict.** `design/RimMandrake/biome_transitions_judgment_2026-11-01.md` states keep or go.
  Evidence: the doc's verdict line.
- **The verdict rests on an experiment, not opinion.** A same-tile A/B on our biomes with and without the mod, with a
  control. Evidence: `design/RimMandrake/biome_transitions_judgment_2026-11-01.evidence.json` and the tool that made it,
  `src/RimMandrake/Utils/biome_transitions_ab.py`; `selftest_biome_transitions_verdict.py` checks the doc's numbers
  against the evidence.
- **The mod lists and docs match the verdict.** If GO: the mod is off the full list and forbidden on the sprint tiers,
  and no live doc says to keep it. Evidence: `python3 src/RimMandrake/Utils/run_selftests.py --only
  selftest_biome_transitions_verdict` passes at the closing sha.
- **Whatever the removal breaks is fixed.** Evidence: the fix for what the mod was hiding (the Odyssey `MixedBiome`
  dead map) exists in the TerminalBiomes mod tree and validates against the defs.
