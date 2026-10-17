# Mod set for the review walk (2026-10-17)

Produced by `Transient/review_walk_2026-10-17/walk_modlist.py` (last step of `deploy_all.sh`, game DOWN only).
`python3 walk_modlist.py` prints the plan and writes nothing; `--apply` backs up the live `ModsConfig.xml` to
`Transient/review_walk_2026-10-17/ModsConfig.PRE_WALK_<stamp>.xml` and then writes the walk list.

**Roots:** all five DLC + Harmony; GSS; FlowWorks; composed Baroque Biomes (`mandrake.rm.biomes`); UtinniPatches (`mandrake.rut.patches`);
SWBestiary; StarWarsPatches; plus the bridge helpers the live list already carries (`brrainz.rimbridgeserver`, `ray1203.simplecamerasetting`).
**Closure (hard dependencies from each About.xml; the composed mod's 10 from the deploy plan):** `oskarpotocki.vanillafactionsexpanded.core` and
`oskarpotocki.vfe.insectoid2` (SWBestiary), `sarg.alphabiomes` and `mandrake.rm.luminouspigment` (biomes), `mandrake.rm.weathersuite` (UtinniPatches). 20 mods in total.
The script exits non-zero (writes nothing) if any dependency is not on the owner's full list or has no About.xml.

**Which baseline I used, and why:** `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (what `modlist_swap.py --restore` puts back).
Measured: it holds exactly the same 548 ids as `deployed/config/ModsConfig.full-post-dead-removal-20261016.xml`, and is a strict subset of
`...full-found-live-20261016.xml` / `...pre-dead-removal-20261016.xml` (551; the extras are `mandrake.rm.explosivegrowth`, `mandrake.rut.plantgrowth`,
`vlvop.tormentmaster.expansion`, all retired on 2026-10-16, so correctly absent). The walk list keeps FULL's load order and `knownExpansions` block.
It already carries `mandrake.rm.biomes` and none of the folded standalone ids (no leaningscrub, explosivegrowth, plantgrowth).

**Why not `modlist_swap.py`:** it only swaps between two stored files (FULL / MINIMAL); it cannot build a custom set. Restore afterwards with
`python3 src/RimMandrake/Utils/modlist_swap.py --restore --apply` (owner's full list) or copy the PRE_WALK backup back.
Caveats: GSS sits after FlowWorks here (FULL's order; FlowWorks `loadAfter` GSS) - unchanged owner order, not verified in a load.
Nothing was written to the live `ModsConfig.xml` while preparing this.
