# MODCHECK_COMPOSED_BIOMES_LIST_1 — modcheck cannot build a test list for a biome inside mandrake.rm.biomes

**For:** FOUNDRY. **Found by:** the Pyrelands trial plan (`design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` §1.1). It blocks every biome's
north-star run, not only Pyrelands'. **Depends on:** BIOME_MOD_UNIFICATION_1.

MEASURED 2026-09-30 by reading `src/RimMandrake/Utils/modcheck/runner.py`:

- `_package_id` reads the **dev folder's** `About.xml`. For Pyrelands that is
  `mandrake.rm.pyrelands`, a packageId retired by the wave-2 fold.
- `compose_test_list` appends that id to MINIMAL with **no dependency closure**.
- A composed entry has no standalone deploy, so RimWorld silently drops the id. The "test" then
  runs on a list without the biome. It also rewrites the live ModsConfig.

## acceptance

- [ ] For any `Biomes.compose.json` entry with `wave <= compose_wave`, modcheck resolves the
      subject to `mandrake.rm.biomes`.
- [ ] The list is built through `modset_builder.py` tier closure (or a named tier on the walk),
      with `dlc: True` always.
- [ ] A selftest covers a composed entry and a standalone entry.
- [ ] A dry-run on Pyrelands prints a list containing `mandrake.rm.biomes`,
      `mandrake.rut.patches` and `mandrake.rsw.swbestiary`.
