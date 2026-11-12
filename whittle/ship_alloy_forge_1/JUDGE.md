# SHIP_ALLOY_FORGE_1: judge's verdict (fresh eyes, 2026-11-11)

What I did: read STATEMENT.md, NOTES.md and the item file's spec section. Read the three files in evidence/. Re-ran
`prove_alloy_forge_offline.py` against the same vfef and capture inputs (exit 0, output byte-identical to
evidence/offline_proof.txt). Ran `validation.py` (STATIC: PASS, 0 findings). Checked the source myself: the zersium
GenStep, the mine-shaft vein rule, the Forge biome def, and the capture's def-type list.

- **L1 true.** RUT_ZersiumForgeLumps.xml scatters RSW_MineableZersium with `allowedBiomes` = RM_TheForge only
  (RM_TheForge is defined in src/RimMandrake/TheForge/Defs/BiomeDefs/RM_TheForge_Biome.xml). The proof shows
  scatter=0, preventMeteorite=true, deepCommonality unset. The proof's L1 check skips one route,
  `RM_MineShaft_RSW_MineableZersium` (in the capture census). I looked at it: MineShaftMod `onlyMapVeins` defaults to
  true, so the shaft offers that bill only on a map that already has the vein. With default settings no other biome
  has a source. This is a source and def reading, not a generated map.
- **L2 true.** offline_proof shows RSW_AlloyDurasteel, Steel 10 + RSW_Zersium 2 -> RSW_Durasteel 10, first in the
  patched forge's bill order with no research. The 2026-11-06 live capture also has that ProcessDef. RSW_Zersium's
  description fits canon (a mineral that turns steel into durasteel). The colour and coldness in it are invented
  detail, but nothing in it contradicts canon.
- **L3 true, offline and at capture time.** VFEFactory_AlloyPlasteel needs RM_WM_PlasteelAlloying. That project needs
  the forge's own project plus AdvancedFabrication, and durasteel needs no research, so plasteel unlocks after
  durasteel. The census covered 317 mods, 1867 RecipeDefs and 398 ProcessDefs, and the instrument can see (it finds 3
  plasteel producers). Its only other plasteel routes are slag re-melt, which the owner's card calls "Re-melt salvage",
  not fabrication. Limits: the census reads only RecipeDef.products and ProcessDef results. The capture has no
  ItemProcessor/CombinationDef types, so no route was missed there. The capture is 5 days older than the source.
- **L4 true.** settings_toggles.txt and the source show four toggles: alloyForgeProgressiveGate, plasteelAlloyEnabled,
  durasteelAlloyEnabled and zersiumForgeEnabled. Each defaults to true in both the field and Scribe, has a label and
  tooltip, and has an applier. This is a source grep. No evidence shows a toggle changing behaviour, and L4 does not ask
  for that.
- **L5 cannot tell (not done).** No minimal-list load is in evidence/. The builder's own commit says "L5 live load
  still owed". The only live run in NOTES.md (2026-10-10) used the full 565-mod list, not the minimal list. It ran
  before RSW_Durasteel existed: RSW_AlloyDurasteel was absent. The 2026-11-06 capture loaded 317 mods and brings no
  Player.log config-error count. To settle L5: a minimal-list load on the current build, with get_defs showing both
  gates and the durasteel process, and a Player.log with no config errors beyond the baseline.

Where the evidence flatters: all of it is offline or source-level. The forge-cost line is the proof's own "C# mirror"
of the patcher, not the game applying it. The toggles are a grep, never flipped. The one live def capture predates
the source and has no log.

would show: no
