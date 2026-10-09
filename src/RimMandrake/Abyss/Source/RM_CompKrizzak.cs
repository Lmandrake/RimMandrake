using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared;
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

    // LIGHT_LEDGER_ONE_1: a krizzak's bite is the "abyss.krizzak" multiplier in the shared light ledger, composed with the
    // Dark and everything else on the lamp (before this the two took turns: the Dark skipped a lamp a krizzak held).
    // The arithmetic is still RM_DarkKernel.Krizzak*, run in normalised units: kOriginal 1, radius = the bite's share.
    // Not saved, as before: a reload gives the light back and a krizzak still sitting on it bites again.
    public class RM_MapComponent_KrizzakDimming : MapComponent
    {
        private const int RecoverInterval = 250;
        private const string Owner = "abyss.krizzak";

        private class Entry { public int lastFed; }
        private readonly Dictionary<CompGlower, Entry> dimmed = new Dictionary<CompGlower, Entry>();
        private readonly List<CompGlower> scratch = new List<CompGlower>();

        public RM_MapComponent_KrizzakDimming(Map map) : base(map) { }

        public bool IsDimmed(CompGlower g) { return dimmed.ContainsKey(g); }

        private static RM_DarkKernel.Lamp LampOf(CompGlower g, Entry e)
        {
            return new RM_DarkKernel.Lamp
            {
                radius = e != null ? LightLedger.Get(g, "mul:" + Owner, 1f) : 1f,
                kPresent = e != null,
                kOriginal = e != null ? 1f : 0f,
                kLastFed = e != null ? e.lastFed : 0
            };
        }

        // The dimming arithmetic (feed floor, recovery pace, when an entry is spent) is RM_DarkKernel.Krizzak*; these read
        // the bite's share in, call it, and write the share and the entry back.
        public bool AtFloor(CompGlower g, float minFraction)
        {
            dimmed.TryGetValue(g, out Entry e);
            return RM_DarkKernel.KrizzakAtFloor(LampOf(g, e), minFraction);
        }

        public void Feed(CompGlower g, float fraction, float minFraction)
        {
            if (g == null || g.parent == null || !g.parent.Spawned) return;
            dimmed.TryGetValue(g, out Entry e);
            RM_DarkKernel.Lamp lamp = LampOf(g, e);
            bool shrank = RM_DarkKernel.KrizzakFeed(ref lamp, Find.TickManager.TicksGame, fraction, minFraction);
            if (e == null) { e = new Entry(); dimmed[g] = e; }
            e.lastFed = lamp.kLastFed;
            if (shrank)
            {
                LightLedger.SetMul(g, Owner, lamp.radius);
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
                if (g.parent == null || !g.parent.Spawned) { LightLedger.ClearMul(g, Owner); dimmed.Remove(g); continue; }
                RM_DarkKernel.Lamp lamp = LampOf(g, e);
                RM_DarkKernel.KrizzakRecover(ref lamp, now);
                if (!lamp.kPresent) { LightLedger.ClearMul(g, Owner); dimmed.Remove(g); }
                else LightLedger.SetMul(g, Owner, lamp.radius);
            }
        }
    }
}
