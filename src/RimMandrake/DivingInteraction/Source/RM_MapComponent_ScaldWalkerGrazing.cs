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

        // Per-pawn trample/warn ticks (thingIDNumber -> tick). Not saved: a reload forgets a cooldown, which at worst
        // repeats one warning.
        private readonly Dictionary<int, int> lastTrample = new Dictionary<int, int>();
        private readonly Dictionary<int, int> lastWarn = new Dictionary<int, int>();
        private readonly List<Pawn> movingWalkers = new List<Pawn>();

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % RM_WalkerTrampleKernel.SweepInterval == 0 && RM_DivingSettings.masterEnabled
                && RM_DivingSettings.walkerTrampleEnabled)
            {
                TrampleSweep(now);
            }
            if (now % SweepInterval != 0)
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

        // SCALD_WALKING_PASTURE_1, trample half (owner card 2026-10-09). RM_WalkerTrampleKernel decides; this measures
        // and plays it: blunt damage from the walker, a message for the player's own people, a caution message first.
        private void TrampleSweep(int now)
        {
            ResolveDefs();
            if (walkerDef == null)
            {
                return;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            movingWalkers.Clear();
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn w = pawns[i];
                if (w.def == walkerDef && !w.Dead && !w.Downed && w.pather != null && w.pather.Moving)
                {
                    movingWalkers.Add(w);
                }
            }
            if (movingWalkers.Count == 0)
            {
                return;
            }
            for (int i = pawns.Count - 1; i >= 0; i--)
            {
                Pawn p = pawns[i];
                if (p.def == walkerDef || p.Dead || !p.Spawned || p.RaceProps == null || !p.RaceProps.Humanlike)
                {
                    continue;
                }
                float best = float.PositiveInfinity;
                Pawn bestWalker = null;
                for (int k = 0; k < movingWalkers.Count; k++)
                {
                    float d = (movingWalkers[k].Position - p.Position).LengthHorizontalSquared;
                    if (d < best)
                    {
                        best = d;
                        bestWalker = movingWalkers[k];
                    }
                }
                int id = p.thingIDNumber;
                int lt = lastTrample.TryGetValue(id, out int a) ? a : -1;
                int lw = lastWarn.TryGetValue(id, out int b) ? b : -1;
                // trampleEnabled is true here: MapComponentTick only calls this sweep when the toggle is on.
                RM_WalkerTrampleKernel.Outcome o = RM_WalkerTrampleKernel.Decide(best, p.Downed, now, lt, lw,
                    true, RM_DivingSettings.walkerTrampleWarning);
                bool ours = p.Faction == Faction.OfPlayer;
                if (o == RM_WalkerTrampleKernel.Outcome.Trample)
                {
                    lastTrample[id] = now;
                    lastWarn[id] = now;
                    float dmg = RM_WalkerTrampleKernel.Damage(RM_DivingSettings.walkerTrampleDamage);
                    p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg, 0f, -1f, bestWalker));
                    if (ours)
                    {
                        Messages.Message("RM_WalkerTrampled".Translate(p.LabelShort), p, MessageTypeDefOf.NegativeHealthEvent);
                    }
                }
                else if (o == RM_WalkerTrampleKernel.Outcome.Warn)
                {
                    lastWarn[id] = now;
                    if (ours)
                    {
                        Messages.Message("RM_WalkerTrampleWarning".Translate(p.LabelShort), p, MessageTypeDefOf.CautionInput, false);
                    }
                }
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
