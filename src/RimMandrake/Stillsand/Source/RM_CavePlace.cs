using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // STILLSAND_CAVE_AS_PLACE_1 — the precious cave as a place, not a prop table.
    //   1. preservation: nothing rots on a roofed cave cell (RM_CavePreservation)
    //   2. (the drip, one ambient water sound per cave, was CUT 2026-10-23, fluff review)
    //   3. the lens grotto's grown-biosilica wall ring (RM_CaveElement_WallRing)
    //   4. (the taken cave's own tribal mark was CUT 2026-10-23, fluff review)
    public static class RM_CavePreservation
    {
        // Vanilla rots on a 250-tick Rare tick (or per-tick on Normal); a 60-tick scan freezes an
        // arrival before it gains a measurable sliver of progress.
        public const int ScanInterval = 60;

        private static readonly FieldInfo vanishField =
            typeof(Corpse).GetField("vanishAfterTimestamp", BindingFlags.Instance | BindingFlags.NonPublic);

        public static void Scan(RM_MapComponent_PreciousCave comp)
        {
            Map map = comp.map;
            bool on = RM_PreciousCaveSettings.preservationEnabled && !comp.DenHeld();

            // Release first: anything that left the cave, lost its roof, or whose switch went off.
            for (int i = comp.frozenThings.Count - 1; i >= 0; i--)
            {
                Thing t = comp.frozenThings[i];
                if (t == null || t.Destroyed || !on || !InCave(comp, t))
                {
                    if (t is Corpse released && t != null && vanishField != null
                        && comp.frozenVanish.TryGetValue(released.thingIDNumber, out int savedVanish))
                    {
                        // Put back the vanish clock preservation zeroed (0 disables vanishing).
                        vanishField.SetValue(released, savedVanish);
                    }
                    if (t != null)
                    {
                        comp.frozenVanish.Remove(t.thingIDNumber);
                    }
                    if (t is ThingWithComps twc)
                    {
                        CompRottable rot = twc.GetComp<CompRottable>();
                        if (rot != null)
                        {
                            rot.disabled = false;
                        }
                    }
                    comp.frozenThings.RemoveAt(i);
                }
            }
            if (!on)
            {
                return;
            }

            for (int i = 0; i < comp.caveCells.Count; i++)
            {
                IntVec3 c = comp.caveCells[i];
                if (!c.InBounds(map) || !map.roofGrid.Roofed(c))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(map);
                for (int j = things.Count - 1; j >= 0; j--)
                {
                    TryFreeze(comp, things[j]);
                    if (things[j] is Building_Storage store && store.GetSlotGroup() != null)
                    {
                        foreach (Thing held in store.GetSlotGroup().HeldThings.ToList())
                        {
                            TryFreeze(comp, held);
                        }
                    }
                }
            }
        }

        private static void TryFreeze(RM_MapComponent_PreciousCave comp, Thing t)
        {
            // A storage building straddling the cave edge holds slot cells outside it: only what
            // actually sits on a roofed cave cell is taken over.
            if (!(t is ThingWithComps twc) || comp.frozenThings.Contains(t) || !InCave(comp, t))
            {
                return;
            }
            CompRottable rot = twc.GetComp<CompRottable>();
            if (rot == null || rot.disabled)
            {
                return; // not rottable, or someone else's switch (never take it over)
            }
            rot.disabled = true;
            comp.frozenThings.Add(t);
            if (t is Corpse corpse && vanishField != null && corpse.InnerPawn != null && corpse.InnerPawn.RaceProps.Animal)
            {
                object prior = vanishField.GetValue(corpse);
                if (prior is int priorTicks && priorTicks != 0)
                {
                    comp.frozenVanish[corpse.thingIDNumber] = priorTicks;
                }
                vanishField.SetValue(corpse, 0); // a desiccated animal corpse otherwise vanishes with time
            }
        }

        private static bool InCave(RM_MapComponent_PreciousCave comp, Thing t)
        {
            if (t.MapHeld != comp.map || !t.SpawnedOrAnyParentSpawned)
            {
                return false;
            }
            IntVec3 c = t.PositionHeld;
            if (!comp.caveCells.Contains(c) || !comp.map.roofGrid.Roofed(c))
            {
                return false;
            }
            // carried by a pawn: not spawned itself and held by a pawn -> back in the weather
            return !(t.ParentHolder is Pawn_CarryTracker);
        }
    }

    public static class RM_CavePlaceUtil
    {
        /// <summary>Rock cells touching the cave floor (8-neighbourhood), natural rock only.</summary>
        public static List<IntVec3> WallRingCells(Map map, IEnumerable<IntVec3> floor)
        {
            HashSet<IntVec3> floorSet = new HashSet<IntVec3>(floor);
            HashSet<IntVec3> ring = new HashSet<IntVec3>();
            foreach (IntVec3 f in floorSet)
            {
                for (int i = 0; i < 8; i++)
                {
                    IntVec3 n = f + GenAdj.AdjacentCells[i];
                    if (n.InBounds(map) && !floorSet.Contains(n) && IsNaturalRock(n, map))
                    {
                        ring.Add(n);
                    }
                }
            }
            return ring.ToList();
        }

        public static bool IsNaturalRock(IntVec3 c, Map map)
        {
            if (map == null || !c.InBounds(map))
            {
                return false;
            }
            Building b = c.GetEdifice(map);
            return b != null && b.def.building != null && b.def.building.isNaturalRock;
        }
    }

    /// <summary>Replaces the natural-rock ring around the chamber with a mineable wall def
    /// (the lens grotto's grown biosilica). Off in Mod Settings: the rock stays rock.</summary>
    public class RM_CaveElement_WallRing : RM_SetPieceElement
    {
        public ThingDef wall;
        public float chance = 1f;

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            if (wall == null || !RM_PreciousCaveSettings.wallRingEnabled)
            {
                return;
            }
            RM_PreciousCaveContext ctx = RM_PreciousCaveContext.For(loc, map);
            int n = 0;
            foreach (IntVec3 c in RM_CavePlaceUtil.WallRingCells(map, ctx.floor))
            {
                if (chance < 1f && !Rand.Chance(chance))
                {
                    continue;
                }
                c.GetEdifice(map)?.Destroy(DestroyMode.Vanish);
                GenSpawn.Spawn(ThingMaker.MakeThing(wall), c, map);
                n++;
            }
            Log.Message("[Stillsand] cave place: " + wall.defName + " ring of " + n + " cells");
        }
    }
}
