using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // WHO GETS READ, AND WHEN (spec §3, spike A's application half).
    //
    // The hediff's own comp owns the RATE and the cure geography; this owns
    // only APPLICATION — noticing that a creature is standing on the body and
    // giving it the hediff at severity ~0.
    //
    // 🔑 THIS COMPONENT EXISTS ON EVERY MAP IN EVERY SAVE, including maps with
    // no slime anywhere, so the not-my-biome path has to be nearly free: one
    // modulo, one terrain-tag lookup per pawn, once every 500 ticks.
    //
    // 🔴 COLONISTS ARE NOT EXEMPT (§3 law 1) and animals are not exempt
    // either. The only exemptions are SlimeUtility.IsResistant — non-flesh,
    // the RM_SlimeResistant modExtension, and the Biotech resistance gene —
    // and all three are DATA another mod can claim.
    // ════════════════════════════════════════════════════════════════════
    public class MapComponent_SlimeExposure : MapComponent
    {
        private const int CheckIntervalTicks = 500;

        public MapComponent_SlimeExposure(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            if (SlimeDefs.Slimification == null)
            {
                return;
            }

            try
            {
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < pawns.Count; i++)
                {
                    Pawn pawn = pawns[i];
                    if (pawn == null || pawn.Dead)
                    {
                        continue;
                    }
                    if (!SlimeUtility.IsBeingRead(pawn))
                    {
                        continue;
                    }
                    if (SlimeUtility.IsResistant(pawn))
                    {
                        continue;
                    }

                    if (!pawn.health.hediffSet.HasHediff(SlimeDefs.Slimification))
                    {
                        pawn.health.AddHediff(SlimeDefs.Slimification);
                    }

                    // The ruled read-mark flavor hook (§10, round 2), a
                    // mod-settings toggle, on by default. Only creatures the
                    // body has actually got into leave a mark, and only rarely
                    // — this runs for every pawn on a crowded map.
                    if (SlimeSettings.flavorReadMarks
                        && SlimeDefs.SlimeSmear != null
                        && pawn.Position.InBounds(map)
                        && Rand.Chance(0.06f))
                    {
                        HediffComp_Slimification comp = SlimeUtility.GetSlimification(pawn);
                        if (comp != null && comp.parent.Severity >= 0.2f)
                        {
                            FilthMaker.TryMakeFilth(pawn.Position, map, SlimeDefs.SlimeSmear, 1,
                                                    FilthSourceFlags.None, false);
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] exposure tick: " + e.Message, 0x51A12);
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // FARMS FAIL BY CONVERSION (spec §2, spike F).
    //
    // "Cultivated fields on slime terrain revert within a few harvests."
    // The slime-grass terrain is fertility 1.0 — better than rich soil — and
    // that is bait. Sowing on it starts the clock; the ground goes back to
    // ordinary rich slime and the field's yield with it.
    //
    // 🔑 SOWN GROUND ONLY. The check is "is there a growing zone here", so an
    // untouched slime-grass meadow stays fertile forever and only a farm is
    // punished. That is the difference between a mechanic and a nuisance.
    //
    // ⚠️ The cell budget below is a fraction of the map per pass, not a full
    // scan: on a 250x250 map this looks at ~60 cells every in-game hour, which
    // walks a realistic field down over a few harvests without ever touching a
    // whole-map loop.
    // ════════════════════════════════════════════════════════════════════
    public class MapComponent_SlimeFieldConversion : MapComponent
    {
        private const int CheckIntervalTicks = 2500;
        private const float CellsPerAttempt = 1000f;

        // Resolved once per map at FinalizeInit, never per tick.
        private bool biomeUsesSlimeGrass;

        public MapComponent_SlimeFieldConversion(Map map) : base(map)
        {
        }

        // 🔑 THE GATE IS READ OFF THE BIOME'S OWN TERRAIN TABLE, NOT OFF THIS
        // MOD'S BIOME defName. Any biome — this mod's, the RUT campaign
        // layer's, anyone's — that lays RM_Slime_Grass in terrainsByFertility
        // or a terrainPatchMaker gets the farm-conversion mechanic, and a map
        // that has never heard of slime costs one bool check per pass.
        public override void FinalizeInit()
        {
            base.FinalizeInit();
            biomeUsesSlimeGrass = BiomeLaysSlimeGrass(map.Biome);
        }

        private static bool BiomeLaysSlimeGrass(BiomeDef biome)
        {
            if (biome == null || SlimeDefs.SlimeGrass == null)
            {
                return false;
            }
            if (biome.terrainsByFertility != null)
            {
                for (int i = 0; i < biome.terrainsByFertility.Count; i++)
                {
                    if (biome.terrainsByFertility[i].terrain == SlimeDefs.SlimeGrass)
                    {
                        return true;
                    }
                }
            }
            if (biome.terrainPatchMakers != null)
            {
                for (int i = 0; i < biome.terrainPatchMakers.Count; i++)
                {
                    List<TerrainThreshold> thresholds = biome.terrainPatchMakers[i].thresholds;
                    if (thresholds == null)
                    {
                        continue;
                    }
                    for (int j = 0; j < thresholds.Count; j++)
                    {
                        if (thresholds[j].terrain == SlimeDefs.SlimeGrass)
                        {
                            return true;
                        }
                    }
                }
            }
            return false;
        }

        public override void MapComponentTick()
        {
            if (!biomeUsesSlimeGrass)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            if (SlimeDefs.SlimeGrass == null || SlimeDefs.SlimeRich == null)
            {
                return;
            }

            int attempts = (int)(map.Area / CellsPerAttempt);
            if (attempts < 1)
            {
                attempts = 1;
            }

            try
            {
                for (int i = 0; i < attempts; i++)
                {
                    IntVec3 c = CellFinder.RandomCell(map);
                    if (map.terrainGrid.TerrainAt(c) != SlimeDefs.SlimeGrass)
                    {
                        continue;
                    }
                    Zone_Growing zone = map.zoneManager.ZoneAt(c) as Zone_Growing;
                    if (zone == null)
                    {
                        continue;
                    }
                    map.terrainGrid.SetTerrain(c, SlimeDefs.SlimeRich);
                    if (SlimeDefs.SlimeSmear != null)
                    {
                        FilthMaker.TryMakeFilth(c, map, SlimeDefs.SlimeSmear, 1,
                                                FilthSourceFlags.None, false);
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] field conversion: " + e.Message, 0x51A13);
            }
        }
    }
}
