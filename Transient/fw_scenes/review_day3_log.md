# FlowWorks review day 3 log 2026-10-17 (FOUNDRY reviewer, scratch clone review3)

base: 7986cc51e (origin/main; no FlowWorks C# commits since round 2)

## Files

(per-file entries appended below)
- now: Swimming/RM_Swim.cs (1041) whole
- Swimming/RM_Swim.cs (1041): read whole; nothing functional found. Fixed false doc (profile cache 'a quarter of a second' -> 60 ticks). lastWarn still write-only, bounded by our pawns (harmless). -> CLEAN candidate
- now: RM_LiquidStock.cs (1359) whole
- RM_LiquidStock.cs (1359): read whole (incl. round-2 Refill dL fix); checked CollectBody clears its buffers, Histogram is cumulative (DepthReport h[s+1] right), exact stage threshold 0.5 dL matches StageForExact. Nothing found -> CLEAN candidate
- now: RM_MapComponent_Excavation.cs (3190) whole
- RM_MapComponent_Excavation.cs (3190): read whole. DOUBT :2390 decided BUG (latent: every production caller with exact-level off passes one level, but the public all-or-nothing contract broke for dl > 1 level: first levels written then false, a caller keeping its liquid creates water). Fixed: room for all levels checked, one write. SelfTest LevelPour_whole_level_pour_is_all_or_nothing. Rest nothing (BedLevelsAt :1171 rec re-read is redundant, harmless). Stays DIRTY (fixed).
- now: RimMandrakeFlowWorksMod.cs (1860) whole
- DOUBT Mod.cs:684 decided BUG: pitDrowningHeadFraction greyed under pitDrowningEnabled, but RM_Swim reads it (IsSwimming exhaustion, NearestFooting) with drowning off, against the file's own rule (dependent only where unreachable). Fixed: Independent, slider drawn outside the greyed scope, tooltip names swimming. SelfTest Relative_head_fraction_live_with_drowning_off.
- now: rest of RimMandrakeFlowWorksMod.cs (1009-1870)
- RimMandrakeFlowWorksMod.cs (1868): read whole. Fixed two false player texts (mouseover tooltip 'ponds show their bed, scaled by how full' -> floor and water over it, limitless says never dry; levelExact 'the two settings below' -> one is above). Plus the :684 fix above. Stays DIRTY (edited).
- DOUBT RM_WaterBodyMendGame.cs:551 next
- DOUBT RM_WaterBodyMendGame.cs:551 decided NOT A BUG: vanilla DoTerrainChangedEffects (RimSage, Verse/TerrainGrid.cs:502) calls Overlaps inside the per-thing plant loop; the only calls before it are Plant/Filth Destroy() on the same square, none of which writes terrain in vanilla, and every postfix runs after the loop. A nested change could only come from another mod's Destroy hook and its effect is the vanilla answer (plant dies), never a throw.
- now: SelfTest/*.cs (66 files, ~17.7k lines): harness first, then tautology/swallow scan, then the six pit-rule tests
- SelfTest after fixes: 562/562 (2 new cases ok), hose 342/342. Committing fixes now; SelfTest file reads continue after.
