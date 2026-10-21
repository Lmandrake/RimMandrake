# WORLD_PATHS_VERIFY_WATER_FINALLY_WET

Owner, 2026-10-20, looking at the in-game map: *"Strangely I see what looks like a blue road on the Scald's shore
towards the Anvil. Looks like a river, but it isn't. And the river is shown brown and red. Odd colors for roads and
rivers."*

**What changed (c94bb0c92 Baroque Biomes + tools, 59e61a395 FlowWorks; built, offline only; the ledger title's 401fee537 was rebased away):**
- **Baroque Biomes `RM_WorldPaths.cs`:** the Stone road layer changes from slate (0.15, 0.25, 0.25) to grey-brown
  (0.18, 0.15, 0.12). The slate was the "blue road": a 69-tile StoneRoad network from the Scald shore into the Anvil.
  When FlowWorks colours are off, the fallback water is now blue-grey.
- **Ancient highway:** it is now old asphalt, not gold. Owner, 2026-10-20: *"Instead of the strange yellow highlights it
  should show as old asphalt broken from long ago"*. The fill is dark grey-black with a pale worn centre stripe. The
  broken pieces are intended and are not joined.
- **FlowWorks River Colours:** the elevation gradient is gone. That gradient was the brown and red rivers, because its
  anchors matched no tile. Rivers are now blue-grey water (0.08, 0.16, 0.30), tinted only in four biomes: RM_Contagion
  blood red, RM_Miasma brackish, RM_Wasteland toxic green, RM_RustCathedral verdigris. The scribe keys are new.
- **Superseded:** the owner's 2026-09-06 gradient ruling ("Red rivers in the mountains, turning immediately to brackish
  green/brown in the jungles, and a toxic brown/blue near their end.") and the same-day card *River gradient blends into
  land → Darken, same hues*. This feedback replaces those colours. Red now appears only inside the Contagion.
- **Contrast:** every value PASSES, with fill dE ≥ 22 and casing/bank ≥ 5:1. Full text:
  `design/Jawa/worldbuilding/world_paths_readable_2026-10-20.md` §6.
- **Preview:** `D:\ClaudeWork\rimmandrake\scratch\pathcolors\preview_paths_2026-10-20.png`

**What decides it:** a live look at the Scald shore toward the Anvil, a Greentide river and a Contagion river. Stone
roads should read brown-grey, not like a river. Rivers should read blue, red inside the Contagion only.

`WORLD_PATHS_VERIFY_WATER_FINALLY_WET` — built, committed, not deployed; NEXT: deploy BiomesShell (Baroque Biomes compose) and FlowWorks with `deploy_custom_mods.py --apply` at the next game-down, then screenshot the Scald shore, the Anvil and a Contagion river on the planet map and show the owner.
