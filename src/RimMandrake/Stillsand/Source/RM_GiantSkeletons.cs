using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SKELETONS_TRACKS_1 §1–5 — the giant skeletons.
    // Design: stillsand_turn3_development_2026-09-30.md §3.1.
    //
    //   Building_GiantSkeleton  the ribcage: a multi-cell building, the bone
    //                           harp's host, deconstructed slowly for its
    //                           leavings (a krayt's skull, sometimes a pearl).
    //   the skull               a separate building (RM_GiantSkull) whose
    //                           footprint is a full cast-shade pocket: it carries
    //                           CreatureBehaviors' shipped RM_CompProperties_ShadeGear
    //                           (footprint, depth 1, both sun kinds), so the
    //                           shade grid every consumer reads counts it. No
    //                           second shade system here.
    //   the ribs' lee stripes   the same comp in lee mode at depth 0.5 on the
    //                           ribcage — partial cover; the sand's glare floor
    //                           still applies (RM_MapComponent_ShadeGrid).
    //   RM_CompBoneHarp         a wind sustainer per skeleton, louder in wind.
    //   RM_GenStep_GiantSkeletons   0..N per map, sparse, often with an ollim.
    //   RM_MapComponent_SkeletonRemains  a giant's corpse becomes its skeleton
    //                           where it fell, after a configurable delay.
    //
    // Every class is data-driven: a skeleton def carries
    // RM_GiantSkeletonExtension, a race carries RM_SkeletonRemainsExtension
    // naming its skeleton, and a biome opts in with RM_SkeletonBiomeExtension.
    // The RSW skeletons (krayt, greater krayt, war wyrm) are XML in SWBestiary
    // on these same classes.
    // ════════════════════════════════════════════════════════════════════

    /// <summary>One deconstruct leaving: count of thing, with a chance.</summary>
    public class RM_SkeletonLeaving
    {
        public ThingDef thing;
        public int count = 1;
        public float chance = 1f;
    }

    /// <summary>On a skeleton building's ThingDef.</summary>
    public class RM_GiantSkeletonExtension : DefModExtension
    {
        /// <summary>The skull building laid beside this skeleton, or null.</summary>
        public ThingDef skull;

        /// <summary>Relative chance the map genstep picks this skeleton. 0 =
        /// only ever from a corpse.</summary>
        public float genstepWeight = 1f;

        /// <summary>What deconstructing it leaves. Giant bone joins this list
        /// once DESIGN_MATERIALS_REVIEW_1 names the one bone material.</summary>
        public List<RM_SkeletonLeaving> leavings = new List<RM_SkeletonLeaving>();
    }

    /// <summary>On a giant race's ThingDef: the skeleton its corpse becomes.</summary>
    public class RM_SkeletonRemainsExtension : DefModExtension
    {
        public ThingDef skeleton;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (skeleton == null)
            {
                yield return "RM_SkeletonRemainsExtension has no skeleton";
            }
        }
    }

    /// <summary>On a BiomeDef: this biome keeps its giants' bones, and sees
    /// what comes over its horizon.</summary>
    public class RM_SkeletonBiomeExtension : DefModExtension
    {
        public bool corpsesBecomeSkeletons = true;
        public bool horizonWarnings = true;
        /// <summary>Genstep chances of 0, 1 and 2+ skeletons (the 2+ share
        /// is capped by the Mod Settings maximum).</summary>
        public float chanceNone = 0.3f;
        public float chanceOne = 0.5f;
        public float chanceOllim = 0.6f;
    }

    public class Building_GiantSkeleton : Building
    {
        public RM_GiantSkeletonExtension Ext => def.GetModExtension<RM_GiantSkeletonExtension>();

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = MapHeld;
            IntVec3 pos = PositionHeld;
            base.Destroy(mode);
            if (mode != DestroyMode.Deconstruct || map == null)
            {
                return;
            }
            RM_GiantSkeletonExtension ext = Ext;
            if (ext == null)
            {
                return;
            }
            foreach (RM_SkeletonLeaving l in ext.leavings)
            {
                if (l.thing == null || l.count <= 0 || !Rand.Chance(l.chance))
                {
                    continue;
                }
                Thing t = ThingMaker.MakeThing(l.thing);
                t.stackCount = Mathf.Min(l.count, l.thing.stackLimit);
                GenPlace.TryPlaceThing(t, pos, map, ThingPlaceMode.Near);
            }
        }

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder(base.GetInspectString());
            RM_GiantSkeletonExtension ext = Ext;
            if (ext != null && ext.leavings.Any(l => l.thing != null))
            {
                if (sb.Length > 0)
                {
                    sb.AppendLine();
                }
                sb.Append("Deconstruct for: ");
                sb.Append(string.Join(", ", ext.leavings.Where(l => l.thing != null)
                    .Select(l => l.thing.label + (l.chance < 1f ? " (sometimes)" : ""))));
            }
            return sb.ToString();
        }
    }

    // ── the bone harp ───────────────────────────────────────────────────

    public class RM_CompProperties_BoneHarp : CompProperties
    {
        public SoundDef sound;
        /// <summary>The SoundDef's SoundParamSource_External name.</summary>
        public string windParam = "Wind";

        public RM_CompProperties_BoneHarp()
        {
            compClass = typeof(RM_CompBoneHarp);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (sound == null)
            {
                yield return "RM_CompProperties_BoneHarp has no sound";
            }
            if (parentDef.tickerType != TickerType.Normal)
            {
                yield return "RM_CompProperties_BoneHarp needs tickerType Normal (a sustainer is maintained every tick)";
            }
        }
    }

    /// <summary>Wind across the ribs: a sustainer whose external param is
    /// the map's wind speed, so the moan rises in a gale (the SoundDef's
    /// curve maps it to volume). The vanilla wind turbine's pattern
    /// (CompPowerPlantWind.CompTick, RimSage).</summary>
    public class RM_CompBoneHarp : ThingComp
    {
        private Sustainer sustainer;

        public RM_CompProperties_BoneHarp Props => (RM_CompProperties_BoneHarp)props;

        public override void CompTick()
        {
            base.CompTick();
            if (!RM_SkeletonSettings.boneHarpEnabled || Props.sound == null || !parent.Spawned)
            {
                EndSustainer();
                return;
            }
            if (sustainer == null || sustainer.Ended)
            {
                sustainer = Props.sound.TrySpawnSustainer(SoundInfo.InMap(parent));
            }
            if (sustainer == null)
            {
                return;
            }
            sustainer.Maintain();
            sustainer.externalParams[Props.windParam] = parent.Map.windManager.WindSpeed;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            EndSustainer();
        }

        private void EndSustainer()
        {
            if (sustainer != null && !sustainer.Ended)
            {
                sustainer.End();
            }
            sustainer = null;
        }
    }

    // ── placement ───────────────────────────────────────────────────────

    public static class RM_SkeletonPlacer
    {
        /// <summary>Every cell is in bounds, standable, unbuilt and not a
        /// player-claimed spot.</summary>
        public static bool Fits(ThingDef def, IntVec3 center, Rot4 rot, Map map, int edgeMargin)
        {
            CellRect r = GenAdj.OccupiedRect(center, rot, def.size);
            if (!r.InBounds(map) || r.minX < edgeMargin || r.minZ < edgeMargin
                || r.maxX >= map.Size.x - edgeMargin || r.maxZ >= map.Size.z - edgeMargin)
            {
                return false;
            }
            foreach (IntVec3 c in r)
            {
                if (!c.Standable(map) || c.GetEdifice(map) != null)
                {
                    return false;
                }
                List<Thing> list = c.GetThingList(map);
                for (int i = 0; i < list.Count; i++)
                {
                    Thing t = list[i];
                    if (t is Building || t is Pawn || (t.def.category == ThingCategory.Item && t.Faction != null))
                    {
                        return false;
                    }
                }
            }
            return true;
        }

        /// <summary>Finds a fitting centre at or near <paramref name="near"/>.</summary>
        public static bool TryFindSpot(ThingDef def, IntVec3 near, Map map, int radius, int edgeMargin, out IntVec3 spot)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(near, radius, true))
            {
                if (c.InBounds(map) && Fits(def, c, Rot4.North, map, edgeMargin))
                {
                    spot = c;
                    return true;
                }
            }
            spot = IntVec3.Invalid;
            return false;
        }

        /// <summary>Spawns the skeleton and, beside it, its skull (east or
        /// west, whichever fits). Returns the skeleton, or null.</summary>
        public static Thing Place(ThingDef skeletonDef, IntVec3 center, Map map)
        {
            Thing skeleton = GenSpawn.Spawn(ThingMaker.MakeThing(skeletonDef), center, map, Rot4.North, WipeMode.VanishOrMoveAside);
            ThingDef skullDef = skeletonDef.GetModExtension<RM_GiantSkeletonExtension>()?.skull;
            if (skullDef != null)
            {
                CellRect r = skeleton.OccupiedRect();
                int halfSkull = (skullDef.size.x + 1) / 2;
                List<IntVec3> tries = new List<IntVec3>
                {
                    new IntVec3(r.maxX + halfSkull + 1, 0, r.CenterCell.z),
                    new IntVec3(r.minX - halfSkull - 1, 0, r.CenterCell.z),
                };
                if (Rand.Bool)
                {
                    tries.Reverse();
                }
                foreach (IntVec3 c in tries)
                {
                    if (c.InBounds(map) && Fits(skullDef, c, Rot4.North, map, 1))
                    {
                        GenSpawn.Spawn(ThingMaker.MakeThing(skullDef), c, map, Rot4.North, WipeMode.VanishOrMoveAside);
                        break;
                    }
                }
            }
            return skeleton;
        }

        public static IEnumerable<ThingDef> PlaceableSkeletons =>
            DefDatabase<ThingDef>.AllDefsListForReading.Where(d =>
                (d.GetModExtension<RM_GiantSkeletonExtension>()?.genstepWeight ?? 0f) > 0f);
    }

    /// <summary>§4: zero to two skeletons per map, sparse, often with a
    /// tower ollim, kneel ollims and loomma tenants in their shade.</summary>
    public class RM_GenStep_GiantSkeletons : GenStep
    {
        public ThingDef towerOllim;
        public ThingDef kneelOllim;
        public PawnKindDef tenant;
        public IntRange kneelCount = new IntRange(3, 6);
        public IntRange tenantCount = new IntRange(0, 2);
        public int edgeMargin = 12;
        public float minSpacing = 40f;

        public override int SeedPart => 518306741;

        public override void Generate(Map map, GenStepParams parms)
        {
            RM_SkeletonBiomeExtension biome = map.Biome?.GetModExtension<RM_SkeletonBiomeExtension>();
            if (biome == null || !RM_SkeletonSettings.skeletonPlacementEnabled)
            {
                return;
            }
            int count = RollCount(biome, RM_SkeletonSettings.maxSkeletonsPerMap);
            List<ThingDef> pool = RM_SkeletonPlacer.PlaceableSkeletons.ToList();
            if (count <= 0 || pool.Count == 0)
            {
                return;
            }
            List<IntVec3> placed = new List<IntVec3>();
            for (int n = 0; n < count; n++)
            {
                ThingDef def = pool.RandomElementByWeight(d => d.GetModExtension<RM_GiantSkeletonExtension>().genstepWeight);
                if (!CellFinder.TryFindRandomCellNear(map.Center, map, Mathf.Max(map.Size.x, map.Size.z) / 2,
                        c => placed.All(p => p.DistanceTo(c) >= minSpacing)
                             && RM_SkeletonPlacer.Fits(def, c, Rot4.North, map, edgeMargin),
                        out IntVec3 spot))
                {
                    continue;
                }
                Thing skeleton = RM_SkeletonPlacer.Place(def, spot, map);
                placed.Add(spot);
                if (Rand.Chance(biome.chanceOllim))
                {
                    Dress(skeleton, map);
                }
            }
        }

        /// <summary>Rolls 0, 1 or 2+ against the biome's chances, capped by
        /// the settings maximum. Public for the selftest.</summary>
        public static int RollCount(RM_SkeletonBiomeExtension biome, int max)
        {
            if (max <= 0)
            {
                return 0;
            }
            float r = Rand.Value;
            int n = r < biome.chanceNone ? 0 : r < biome.chanceNone + biome.chanceOne ? 1 : 2;
            return Mathf.Min(n, max);
        }

        private void Dress(Thing skeleton, Map map)
        {
            CellRect around = skeleton.OccupiedRect().ExpandedBy(3);
            if (towerOllim != null)
            {
                SpawnPlant(towerOllim, around, map, 1);
            }
            if (kneelOllim != null)
            {
                SpawnPlant(kneelOllim, around, map, kneelCount.RandomInRange);
            }
            if (tenant != null)
            {
                int n = tenantCount.RandomInRange;
                for (int i = 0; i < n; i++)
                {
                    if (TryFreeCell(around, map, out IntVec3 c))
                    {
                        GenSpawn.Spawn(PawnGenerator.GeneratePawn(tenant), c, map);
                    }
                }
            }
        }

        private static void SpawnPlant(ThingDef def, CellRect around, Map map, int n)
        {
            for (int i = 0; i < n; i++)
            {
                if (!TryFreeCell(around, map, out IntVec3 c))
                {
                    return;
                }
                Thing t = ThingMaker.MakeThing(def);
                if (t is Plant p)
                {
                    p.Growth = Rand.Range(0.4f, 1f);
                }
                GenSpawn.Spawn(t, c, map);
            }
        }

        private static bool TryFreeCell(CellRect r, Map map, out IntVec3 cell)
        {
            for (int i = 0; i < 30; i++)
            {
                IntVec3 c = r.EdgeCells.RandomElement();
                if (c.InBounds(map) && c.Standable(map) && c.GetPlant(map) == null && c.GetFirstBuilding(map) == null)
                {
                    cell = c;
                    return true;
                }
            }
            cell = IntVec3.Invalid;
            return false;
        }
    }

    /// <summary>§5: your kills become the map's history. A giant's corpse
    /// lying in the open on a biome that keeps its bones becomes its
    /// skeleton where it fell, after RM_SkeletonSettings.corpseToSkeletonDays.
    /// A MapComponent scan, not a comp on the generated corpse def: the
    /// corpse ThingDefs are generated at load, and a scan of the map's
    /// corpse group on a long interval is cheap.</summary>
    public class RM_MapComponent_SkeletonRemains : MapComponent
    {
        private const int ScanInterval = GenTicks.TickLongInterval;

        public RM_MapComponent_SkeletonRemains(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % ScanInterval != 37)
            {
                return;
            }
            Scan();
        }

        /// <summary>One pass. Public so a dev tool / state read can force it.
        /// Returns how many corpses became skeletons.</summary>
        public int Scan(bool ignoreDelay = false)
        {
            RM_SkeletonBiomeExtension biome = map.Biome?.GetModExtension<RM_SkeletonBiomeExtension>();
            if (biome == null || !biome.corpsesBecomeSkeletons || !RM_SkeletonSettings.corpseToSkeletonEnabled)
            {
                return 0;
            }
            int delay = Mathf.RoundToInt(RM_SkeletonSettings.corpseToSkeletonDays * GenDate.TicksPerDay);
            int now = Find.TickManager.TicksGame;
            int converted = 0;
            List<Thing> corpses = map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse).ToList();
            foreach (Thing t in corpses)
            {
                if (!(t is Corpse corpse) || !corpse.Spawned || corpse.InnerPawn == null)
                {
                    continue;
                }
                ThingDef skeletonDef = corpse.InnerPawn.def.GetModExtension<RM_SkeletonRemainsExtension>()?.skeleton;
                if (skeletonDef == null)
                {
                    continue;
                }
                if (!ignoreDelay && (corpse.timeOfDeath < 0 || now - corpse.timeOfDeath < delay))
                {
                    continue;
                }
                // Find room first; with none (it fell against a wall), the
                // corpse stays and is tried again next scan.
                if (!RM_SkeletonPlacer.TryFindSpot(skeletonDef, corpse.Position, map, 8, 1, out IntVec3 spot))
                {
                    continue;
                }
                corpse.Destroy(DestroyMode.Vanish);
                RM_SkeletonPlacer.Place(skeletonDef, spot, map);
                converted++;
            }
            return converted;
        }
    }
}
