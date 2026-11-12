# Notes (newest first)

## 2026-11-11 19:58 -08:00, CLAUDE_STEVEDESKTOP_OFFLINE1, setup
- The work looks DONE already: commit `d85a6202` (2026-11-01) wrote the judgment (verdict GO), the evidence JSON, the
  A/B tool, `selftest_biome_transitions_verdict.py`, and `src/RimMandrake/TerminalBiomes/Patches/RM_MixedBiome_Inert.xml`.
  That patch drops Odyssey's MixedBiome worker, which left a dead map on our biomes once the mod was gone.
- Why it is still open: Relentless started it 2026-11-01 23:40, then reclaimed it at 00:29 because
  `relentless_rules.json` `pool_ids_exclude` lists it. No close was ever recorded. 0 runs, so the mode is whittle.
- Remaining work: re-check at today's main that the selftest passes, that the patch validates, and that no doc written
  since 2026-11-01 contradicts the verdict; then close with evidence.
- Live parts: the A/B was run on 2026-11-01 (a scratch quicktest world). This round is offline and does not re-run it.
  Whether the game's Mods folder holds the patch is a live-lane question: note it on the item, don't settle it here.
- Classification of past failures: none (0 runs).
- Limits the doc admits: a 22/23-mod list, two border pairs, one seed each. Geological Landforms itself is not judged
  here (`LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT`).
