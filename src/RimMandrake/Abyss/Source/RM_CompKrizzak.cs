using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Abyss
{
    // ABYSS_KRIZZAK_BUILD_1. The light-thief. A krizzak finds the nearest lit thing (glow plant, powered
    // lamp: anything with a lit CompGlower), flies to it and, once settled, shrinks that glower's radius
    // a step at a time down to a floor. It takes no power and damages nothing. Recovery is owned by
    // RM_MapComponent_KrizzakDimming: radius creeps back once no krizzak has fed on it for a while.
    // Dimmed radii are NOT scribed (CompGlower's radius override is not either), so a reload restores
    // full light: deliberate, the safe direction.
    public class CompProperties_Krizzak : CompProperties
    {
        public float searchRadius = 12f;
        public float settleDistance = 2.5f;
        public float dimFraction = 0.12f;        // of the glower's own radius per feed
        public float minRadiusFraction = 0.25f;  // never below this share of the original
        public float maxFeedTemperature = 35f;   // scatters from heat: no feeding above this

        public CompProperties_Krizzak()
        {
            compClass = typeof(CompKrizzak);
        }
    }

    public class CompKrizzak : ThingComp
    {
        private const int CheckInterval = 120;
        private CompProperties_Krizzak Props => (CompProperties_Krizzak)props;

        public override void CompTick()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || !pawn.IsHashIntervalTick(CheckInterval)) return;
            if (!RM_AbyssSettings.krizzakLightEatingEnabled) return;
            if (pawn.Faction == Faction.OfPlayer) return;           // a tamed one is a pet, not a thief
            if (pawn.AmbientTemperature > Props.maxFeedTemperature) return;

            Map map = pawn.Map;
            CompGlower target = null;
            float best = float.MaxValue;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, Props.searchRadius, true))
            {
                if (!c.InBounds(map)) continue;
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t is Pawn) continue;
                    CompGlower g = t.TryGetComp<CompGlower>();
                    if (g == null || !g.Glows) continue;
                    var dim = map.GetComponent<RM_MapComponent_KrizzakDimming>();
                    if (dim != null && dim.AtFloor(g, Props.minRadiusFraction)) continue;
                    float d = pawn.Position.DistanceToSquared(t.Position);
                    if (d < best) { best = d; target = g; }
                }
            }
            if (target == null) return;

            if (best <= Props.settleDistance * Props.settleDistance)
            {
                map.GetComponent<RM_MapComponent_KrizzakDimming>()?.Feed(target, Props.dimFraction, Props.minRadiusFraction);
                Need_Food food = pawn.needs?.food;
                if (food != null) food.CurLevel += 0.02f;
            }
            else if (pawn.CurJob == null || pawn.CurJob.def != JobDefOf.Goto)
            {
                Job job = JobMaker.MakeJob(JobDefOf.Goto, target.parent.Position);
                pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }
        }
    }

    public class RM_MapComponent_KrizzakDimming : MapComponent
    {
        private const int RecoverInterval = 250;
        private const int RecoverAfterTicks = 600;

        private class Entry { public float original; public int lastFed; }
        private readonly Dictionary<CompGlower, Entry> dimmed = new Dictionary<CompGlower, Entry>();
        private readonly List<CompGlower> scratch = new List<CompGlower>();

        public RM_MapComponent_KrizzakDimming(Map map) : base(map) { }

        public bool IsDimmed(CompGlower g) { return dimmed.ContainsKey(g); }

        public bool AtFloor(CompGlower g, float minFraction)
        {
            return dimmed.TryGetValue(g, out Entry e) && g.GlowRadius <= e.original * minFraction + 0.01f;
        }

        public void Feed(CompGlower g, float fraction, float minFraction)
        {
            if (g == null || g.parent == null || !g.parent.Spawned) return;
            if (!dimmed.TryGetValue(g, out Entry e))
            {
                e = new Entry { original = g.GlowRadius };
                dimmed[g] = e;
            }
            e.lastFed = Find.TickManager.TicksGame;
            float next = Mathf.Max(e.original * minFraction, g.GlowRadius - e.original * fraction);
            if (next < g.GlowRadius)
            {
                g.GlowRadius = next;
                g.ForceRegister(map);
                RM_MapComponent_AbyssSoundscape.LampClatter(map, g.parent);   // ABYSS_SOUNDSCAPE_BUILD_1
            }
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (dimmed.Count == 0 || now % RecoverInterval != 0) return;
            scratch.Clear();
            scratch.AddRange(dimmed.Keys);
            foreach (CompGlower g in scratch)
            {
                Entry e = dimmed[g];
                if (g.parent == null || !g.parent.Spawned) { dimmed.Remove(g); continue; }
                if (now - e.lastFed < RecoverAfterTicks) continue;
                float next = Mathf.Min(e.original, g.GlowRadius + e.original * 0.1f);
                g.GlowRadius = next;
                g.ForceRegister(map);
                if (next >= e.original - 0.01f) dimmed.Remove(g);
            }
        }
    }
}
