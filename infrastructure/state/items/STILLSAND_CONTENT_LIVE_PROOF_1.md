# STILLSAND_CONTENT_LIVE_PROOF_1 — prove the built Stillsand cast live, swap the four placeholders

Remainder of `STILLSAND_BEDAZZLE_CONTENT_1` (closed at its commit): everything it built was checked
offline (validate_patch: every texPath resolves in the mod's own Textures, no parse or parent
errors; the assembly builds and carries its `.srchash`). Nothing was run in a game.

## spec

1. **Quicktest atlas** on `RM_Stillsand`: spawn every `RM_` Stillsand pawn kind and plant once and
   look for magenta or a donor texture. The free mod must load with `sarg.alphaanimals` and
   SWBestiary both absent.
2. **The zuurrik, live.** Spill blood on sand cells (a downed animal bleeding out, or spawned
   `Filth_Blood`) until at least `zuurrikBloodThreshold` (8) cells in one 8-cell radius are
   stained. A swarm of `RM_Zuurrik` should wake within ~600 ticks, strip the stain and the bodies
   beside it, and re-bury with dust puffs after three quiet polls. Check the wake message, that it
   never attacks an unwounded pawn, and that the toggle in Mod Settings turns it off.
3. **Swap the four placeholders** when their jobs render (`infrastructure/artpipe/pending/`,
   `art_lists/stillsand_content_fill.csv`): `RM_Zuurrik` (3 facings; today the oorrik render),
   `RM_Vaalok` (3 facings; today the aurrok render), `RM_DuneCrawler` and `RM_GlassPearl` (item icons;
   today the old SWBestiary egg and trophy icons).
4. **The hourbloom has no incident.** `RM_Hourbloom` exists but nothing names it as a bloom incident's
   `bloomPlant`. Decide with the ExplosiveGrowth wiring whether a Stillsand bloom incident is owed.
5. **Loomma and soorrak runtime checks:** the loomma's `RM_LoommaSunstruck` clock (lethal in the open,
   recovers in shade) and the soorrak's real flight (state read, never a screenshot hunt; owner
   present for any visual).

## criteria

- Atlas clean, as above. A quicktest map shows every fill-out def spawned and the zuurrik waking on blood.
- The four placeholder renders are replaced and no `RM_Zuurrik`/`RM_Vaalok` folder still holds another
  species' art.
