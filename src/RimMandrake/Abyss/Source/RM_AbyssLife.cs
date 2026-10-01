using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_GHARREK_BUILD_1 + ABYSS_DURRGAK_BUILD_1.
    //
    // RM_MapComponent_Gust   the shared gust signal (review report section 5 item 8 asks for ONE
    //                        controller so the gharrek and any later system read the same wind).
    //                        MINIMAL: a seeded on/off pulse on a random calendar. A later wind
    //                        system can replace the scheduling and keep IsGusting().
    // CompRM_Gharrek         dormant (slowed hediff) in the still, opens and feeds in a gust.
    // CompRM_Durrgak         wild durrgaks lay rings of RM_DurrgakCairn.
    // RM_MapComponent_AbyssSigns  cairn rings and a steel-lined cache exist on an Abyss map
    //                        whether or not a durrgak is in sight.
    //
    // UNTESTED LIVE: compiled and def-validated only.
    // ════════════════════════════════════════════════════════════════════

    public static class RM_AbyssUtil
    {
        public static bool IsAbyssMap(Map map)
        {
            string n = map?.Biome?.defName;
            return n == "RM_Abyss" || n == "RUT_Abyss";
        }
    }

    public class RM_MapComponent_Gust : MapComponent
    {
        private int nextGustTick = -1;
        private int gustEndTick = -1;

        public RM_MapComponent_Gust(Map map) : base(map) { }

        public bool GustActive
        {
            get { return Find.TickManager.TicksGame < gustEndTick; }
        }

        public static bool IsGusting(Map map)
        {
            if (map == null || !RM_AbyssSettings.gustsEnabled) return false;
            RM_MapComponent_Gust c = map.GetComponent<RM_MapComponent_Gust>();
            return c != null && c.GustActive;
        }

        public override void MapComponentTick()
        {
            if (!RM_AbyssSettings.gustsEnabled || !RM_AbyssUtil.IsAbyssMap(map)) return;
            int now = Find.TickManager.TicksGame;
            if (nextGustTick < 0)
            {
                nextGustTick = now + Rand.Range(15000, 45000);
                return;
            }
            if (now >= nextGustTick)
            {
                gustEndTick = now + Rand.Range(900, 1800);
                nextGustTick = gustEndTick + Rand.Range(25000, 75000);
            }
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref nextGustTick, "nextGustTick", -1);
            Scribe_Values.Look(ref gustEndTick, "gustEndTick", -1);
        }
    }

    public class CompProperties_RM_Gharrek : CompProperties
    {
        public float foodPerPulse = 0.05f;

        public CompProperties_RM_Gharrek()
        {
            compClass = typeof(CompRM_Gharrek);
        }
    }

    public class CompRM_Gharrek : ThingComp
    {
        private const int Interval = 250;
        private static HediffDef dormantDef;

        private CompProperties_RM_Gharrek Props
        {
            get { return (CompProperties_RM_Gharrek)props; }
        }

        public override void CompTick()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead) return;
            if (!pawn.IsHashIntervalTick(Interval)) return;
            if (dormantDef == null) dormantDef = DefDatabase<HediffDef>.GetNamedSilentFail("RM_GharrekDormant");
            if (dormantDef == null) return;

            Hediff dormant = pawn.health.hediffSet.GetFirstHediffOfDef(dormantDef);
            bool gust = RM_MapComponent_Gust.IsGusting(pawn.Map);
            bool reflex = RM_AbyssSettings.gharrekReflexEnabled;

            if (gust || !reflex)
            {
                if (dormant != null) pawn.health.RemoveHediff(dormant);
                if (gust && reflex)
                {
                    Need_Food food = pawn.needs?.food;
                    if (food != null) food.CurLevel = Mathf.Min(food.MaxLevel, food.CurLevel + Props.foodPerPulse);
                    FleckMaker.ThrowMicroSparks(pawn.DrawPos, pawn.Map);
                }
            }
            else if (dormant == null && !pawn.Downed)
            {
                pawn.health.AddHediff(dormantDef);
            }
        }
    }

    public static class RM_DurrgakRings
    {
        private static ThingDef cairnDef;
        private const int MaxCairnsOnMap = 80;

        public static ThingDef CairnDef
        {
            get
            {
                if (cairnDef == null) cairnDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_DurrgakCairn");
                return cairnDef;
            }
        }

        public static bool TryPlaceRing(Map map, IntVec3 center, float radius, bool withCache)
        {
            ThingDef def = CairnDef;
            if (def == null || map == null) return false;
            if (map.listerThings.ThingsOfDef(def).Count >= MaxCairnsOnMap) return false;
            int placed = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, false))
            {
                // keep only the rim of the disc, so it reads as a ring
                if (c.DistanceTo(center) < radius - 1.1f) continue;
                if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null) continue;
                if (!c.GetTerrain(map).affordances.Contains(TerrainAffordanceDefOf.Light)) continue;
                if (c.GetFirstThing(map, def) != null) continue;
                GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
                placed++;
            }
            if (placed < 3) return false;
            if (withCache && center.Standable(map) && center.GetFirstItem(map) == null)
            {
                Thing steel = ThingMaker.MakeThing(ThingDefOf.Steel);
                steel.stackCount = Rand.RangeInclusive(8, 30);
                GenPlace.TryPlaceThing(steel, center, map, ThingPlaceMode.Near);
            }
            return true;
        }
    }

    public class CompProperties_RM_Durrgak : CompProperties
    {
        public int ringIntervalTicks = 30000;

        public CompProperties_RM_Durrgak()
        {
            compClass = typeof(CompRM_Durrgak);
        }
    }

    public class CompRM_Durrgak : ThingComp
    {
        private int nextRingTick = -1;

        private CompProperties_RM_Durrgak Props
        {
            get { return (CompProperties_RM_Durrgak)props; }
        }

        public override void CompTick()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed) return;
            if (!pawn.IsHashIntervalTick(500)) return;
            if (!RM_AbyssSettings.durrgakSignsEnabled) return;
            // tamed durrgaks tidy (vanilla Haul training) instead of laying rings
            if (pawn.Faction != null) return;
            int now = Find.TickManager.TicksGame;
            if (nextRingTick < 0) nextRingTick = now + Rand.Range(Props.ringIntervalTicks / 4, Props.ringIntervalTicks);
            if (now < nextRingTick) return;
            nextRingTick = now + Rand.Range(Props.ringIntervalTicks, Props.ringIntervalTicks * 2);
            if (pawn.CurJob != null && pawn.CurJob.def == JobDefOf.Wait_Combat) return;
            RM_DurrgakRings.TryPlaceRing(pawn.Map, pawn.Position, Rand.Range(2.5f, 3.9f), false);
        }

        public override void PostExposeData()
        {
            Scribe_Values.Look(ref nextRingTick, "nextRingTick", -1);
        }
    }

    // Rings and a steel-lined cache exist on an Abyss map from the start, durrgak in sight or not.
    public class RM_MapComponent_AbyssSigns : MapComponent
    {
        private bool placed;

        public RM_MapComponent_AbyssSigns(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (placed) return;
            if (Find.TickManager.TicksGame % 120 != 7) return;
            placed = true;
            if (!RM_AbyssSettings.durrgakSignsEnabled || !RM_AbyssUtil.IsAbyssMap(map)) return;
            int rings = Rand.RangeInclusive(2, 4);
            for (int i = 0; i < rings; i++)
            {
                IntVec3 c;
                if (!CellFinder.TryFindRandomCell(map, v => v.Standable(map) && !v.Fogged(map) && v.GetEdifice(map) == null
                                                              && v.DistanceToEdge(map) > 8, out c)) break;
                RM_DurrgakRings.TryPlaceRing(map, c, Rand.Range(2.5f, 4.2f), i == 0 || Rand.Chance(0.4f));
            }
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref placed, "placed", false);
        }
    }
}
