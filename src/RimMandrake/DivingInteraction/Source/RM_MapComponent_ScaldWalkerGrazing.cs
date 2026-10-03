using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SCALD_WALKING_PASTURE_1 — where a bottom-walker grazes, the crowncarpet mat is cropped and its
    // pigment-rich underside (RM_CrowncarpetFresh, LuminousPigment) is left lying bare. The herd's
    // grazing is the only source; the crew job (RM_WorkGiver_GatherGrazedMat) works behind it.
    // Walker-less maps pay one def lookup per sweep. Everything resolves by defName: this assembly
    // never references the TerminalBiomes/LuminousPigment assemblies.
    public class RM_MapComponent_ScaldWalkerGrazing : MapComponent
    {
        public const int SweepInterval = 250;
        public const float GrazeRadius = 2.5f;
        public const int MaxPlantsPerWalkerPerSweep = 2;
        public const int YieldPerPlant = 2;

        private static ThingDef walkerDef, plantDef, freshDef;
        private static bool resolved;

        public RM_MapComponent_ScaldWalkerGrazing(Map map) : base(map)
        {
        }

        public static void ResolveDefs()
        {
            if (resolved)
            {
                return;
            }
            resolved = true;
            walkerDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ScaldWalker");
            plantDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Crowncarpet");
            freshDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_CrowncarpetFresh");
        }

        public static ThingDef FreshMatDef { get { ResolveDefs(); return freshDef; } }
        public static ThingDef WalkerDef { get { ResolveDefs(); return walkerDef; } }

        public static bool IsWalker(Pawn p)
        {
            return p != null && p.def == WalkerDef && p.Spawned && !p.Dead;
        }

        /// <summary>True when a living walker is within <paramref name="radius"/> cells of the cell.</summary>
        public static bool WalkerNear(Map map, IntVec3 cell, float radius, bool movingOnly)
        {
            ThingDef w = WalkerDef;
            if (w == null)
            {
                return false;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            float r2 = radius * radius;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.def != w || p.Dead || (movingOnly && !p.pather.Moving))
                {
                    continue;
                }
                if ((p.Position - cell).LengthHorizontalSquared <= r2)
                {
                    return true;
                }
            }
            return false;
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % SweepInterval != 0)
            {
                return;
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.walkerGrazingEnabled)
            {
                return;
            }
            ResolveDefs();
            if (walkerDef == null || plantDef == null || freshDef == null)
            {
                return;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = pawns.Count - 1; i >= 0; i--)
            {
                Pawn p = pawns[i];
                if (p.def != walkerDef || p.Dead || p.Downed || p.pather.Moving)
                {
                    continue; // a walker grazes standing still; a moving herd exposes nothing
                }
                Graze(p);
            }
        }

        private void Graze(Pawn walker)
        {
            int taken = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(walker.Position, GrazeRadius, true))
            {
                if (taken >= MaxPlantsPerWalkerPerSweep)
                {
                    break;
                }
                if (!c.InBounds(map))
                {
                    continue;
                }
                Plant plant = c.GetPlant(map);
                if (plant == null || plant.def != plantDef)
                {
                    continue;
                }
                plant.Destroy();
                Thing fresh = ThingMaker.MakeThing(freshDef);
                fresh.stackCount = YieldPerPlant;
                GenPlace.TryPlaceThing(fresh, c, map, ThingPlaceMode.Near);
                taken++;
            }
        }
    }
}
