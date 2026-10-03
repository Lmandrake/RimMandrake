using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // GELATINOUSSLIME_FARM_RUINS_1 — failed farms sinking into slime-grass.
    //
    // Runs once at generation on a Slime map (GenStep.Generate never runs on
    // load). Places 2-4 ruins of VANILLA things only (Fence, Wall, Silver,
    // Steel, WoodLog, a lost knife), each on ground that is already the
    // slime ladder: a field outline of RM_Slime_Grass where the crops were,
    // a dead irrigation channel of RM_Slime_Mud, a half-fence on two sides
    // (some posts gone, the rest at low hitpoints), and a collapsed shed in
    // one corner (a few wall stubs plus its last contents). All positions
    // and counts are [INVENTED]. Nothing here makes a faction, a pawn or a
    // hostile: the story is told by what is left, not by who is there.
    // ════════════════════════════════════════════════════════════════════
    public class MapComponent_SlimeFarmRuins : MapComponent
    {
        public List<IntVec3> ruinSites = new List<IntVec3>();

        public MapComponent_SlimeFarmRuins(Map map) : base(map)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref ruinSites, "ruinSites", LookMode.Value);
            if (ruinSites == null)
            {
                ruinSites = new List<IntVec3>();
            }
        }
    }

    public class GenStep_SlimeFarmRuins : GenStep
    {
        public override int SeedPart => 0x51A21;

        private const int FieldW = 9;
        private const int FieldH = 7;
        private const int Margin = 2;

        public override void Generate(Map map, GenStepParams parms)
        {
            try
            {
                if (SlimeDefs.GelatinousSlime == null || map.Biome != SlimeDefs.GelatinousSlime
                    || !SlimeSettings.farmRuinsEnabled)
                {
                    return;
                }
                TerrainDef grass = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Grass");
                TerrainDef mud = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Mud");
                ThingDef fence = DefDatabase<ThingDef>.GetNamedSilentFail("Fence");
                ThingDef wall = DefDatabase<ThingDef>.GetNamedSilentFail("Wall");
                if (grass == null || fence == null || wall == null)
                {
                    return;
                }

                MapComponent_SlimeFarmRuins comp = map.GetComponent<MapComponent_SlimeFarmRuins>();
                int want = Rand.RangeInclusive(2, 4);
                int placed = 0;
                for (int attempt = 0; attempt < 60 && placed < want; attempt++)
                {
                    IntVec3 origin = CellFinderLoose.RandomCellWith(c => c.InBounds(map), map, 50);
                    if (!origin.IsValid)
                    {
                        continue;
                    }
                    if (!SiteFits(map, origin))
                    {
                        continue;
                    }
                    BuildRuin(map, origin, grass, mud, fence, wall);
                    if (comp != null)
                    {
                        comp.ruinSites.Add(origin);
                    }
                    placed++;
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] farm ruins genstep: " + e.Message, 0x51A21);
            }
        }

        // The whole footprint (field + shed margin) must already be standable
        // slime terrain, so "terrain under them is the slime ladder" holds by
        // construction and nothing is built across water or rock.
        private static bool SiteFits(Map map, IntVec3 o)
        {
            for (int dx = -Margin - 5; dx < FieldW + Margin; dx++)
            {
                for (int dz = -Margin; dz < FieldH + Margin + 4; dz++)
                {
                    IntVec3 c = new IntVec3(o.x + dx, 0, o.z + dz);
                    if (!c.InBounds(map) || c.Fogged(map) || !c.Standable(map))
                    {
                        return false;
                    }
                    TerrainDef t = c.GetTerrain(map);
                    if (!t.HasTag("RM_SlimeTerrain") || t.IsWater)
                    {
                        return false;
                    }
                    if (c.GetEdifice(map) != null)
                    {
                        return false;
                    }
                }
            }
            return true;
        }

        private static void BuildRuin(Map map, IntVec3 o, TerrainDef grass, TerrainDef mud,
                                      ThingDef fence, ThingDef wall)
        {
            // Field outline of slime-grass where the crops were.
            for (int x = 0; x < FieldW; x++)
            {
                for (int z = 0; z < FieldH; z++)
                {
                    if (x == 0 || z == 0 || x == FieldW - 1 || z == FieldH - 1)
                    {
                        map.terrainGrid.SetTerrain(new IntVec3(o.x + x, 0, o.z + z), grass);
                    }
                }
            }

            // Dead irrigation channel: a mud line running off the west edge.
            if (mud != null)
            {
                int cz = o.z + FieldH / 2;
                for (int x = -5; x < 0; x++)
                {
                    map.terrainGrid.SetTerrain(new IntVec3(o.x + x, 0, cz), mud);
                }
            }

            // Half-sunk fence along the south and east sides: ~55% of posts
            // survive, all at low hitpoints, and the ground under them is mud.
            for (int x = -1; x <= FieldW; x++)
            {
                TryFencePost(map, new IntVec3(o.x + x, 0, o.z - 1), fence, mud);
            }
            for (int z = 0; z <= FieldH; z++)
            {
                TryFencePost(map, new IntVec3(o.x + FieldW, 0, o.z + z), fence, mud);
            }

            // Collapsed shed in the north-west corner: a 4x3 footprint of
            // wall stubs (40% survive, very damaged) and its last contents.
            IntVec3 so = new IntVec3(o.x - 1, 0, o.z + FieldH + 1);
            for (int x = 0; x < 4; x++)
            {
                for (int z = 0; z < 3; z++)
                {
                    bool edge = x == 0 || z == 0 || x == 3 || z == 2;
                    IntVec3 c = new IntVec3(so.x + x, 0, so.z + z);
                    if (edge && Rand.Chance(0.4f))
                    {
                        Place(map, c, wall, 0.1f, 0.35f);
                        if (mud != null && Rand.Chance(0.5f))
                        {
                            map.terrainGrid.SetTerrain(c, mud);
                        }
                    }
                }
            }
            IntVec3 loot = new IntVec3(so.x + 1, 0, so.z + 1);
            DropLoot(map, loot, "Silver", Rand.RangeInclusive(18, 60));
            DropLoot(map, loot, "Steel", Rand.RangeInclusive(10, 30));
            DropLoot(map, loot, "WoodLog", Rand.RangeInclusive(15, 40));
            // The last ledger (story object, RM_SlimeFarmLedger).
            DropLoot(map, loot, "RM_SlimeFarmLedger", 1);
            // The lost tool.
            DropLoot(map, new IntVec3(o.x + 2, 0, o.z + 2), "MeleeWeapon_Knife", 1);
        }

        private static void TryFencePost(Map map, IntVec3 c, ThingDef fence, TerrainDef mud)
        {
            if (!Rand.Chance(0.55f))
            {
                return;
            }
            if (Place(map, c, fence, 0.15f, 0.5f) && mud != null && Rand.Chance(0.5f))
            {
                map.terrainGrid.SetTerrain(c, mud);
            }
        }

        private static bool Place(Map map, IntVec3 c, ThingDef def, float hpMin, float hpMax)
        {
            if (!c.InBounds(map) || c.GetEdifice(map) != null)
            {
                return false;
            }
            TerrainDef t = c.GetTerrain(map);
            if (t.IsWater || !t.HasTag("RM_SlimeTerrain"))
            {
                return false;
            }
            Plant p = c.GetPlant(map);
            if (p != null)
            {
                p.Destroy();
            }
            ThingDef stuff = ThingDefOf.WoodLog;
            Thing th = ThingMaker.MakeThing(def, def.MadeFromStuff ? stuff : null);
            th.HitPoints = Math.Max(1, (int)(th.MaxHitPoints * Rand.Range(hpMin, hpMax)));
            GenSpawn.Spawn(th, c, map);
            return true;
        }

        private static void DropLoot(Map map, IntVec3 c, string defName, int count)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (d == null || !c.InBounds(map))
            {
                return;
            }
            Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
            t.stackCount = Math.Min(count, d.stackLimit);
            GenPlace.TryPlaceThing(t, c, map, ThingPlaceMode.Near);
        }
    }
}
