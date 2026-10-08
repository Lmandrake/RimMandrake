using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using RimMandrake.CreatureBehaviors;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SAND_SWIM_REMAINDER_1 §4 — the thumper (the ground-caller). A staked drum that holds a
    // water charge (a CompRefuelable fed RM_StilledWater, so vanilla refuel jobs and the auto-refuel
    // toggle do the hauling) and, every beat, spends one flask, wets a small radius of sand, and calls
    // every SUBMERGED sand swimmer within radius (RM_CompSandSwim.Submerged, CreatureBehaviors) with a
    // Goto toward it. Uncharged it does nothing: no wets, no calls. The swimmer's own comp surfaces it
    // at hard ground; its wake is the ordinary submerged wake along the way.
    // Hostile or wild swimmers only: a player-faction (tamed) swimmer is never summoned.
    // Settings: RM_SandSwimRemSettings.thumperEnabled / thumperRadius.
    // ════════════════════════════════════════════════════════════════════
    /// <summary>Shared by the thumper and the sand-fishing wake: send submerged, non-player, non-hunting
    /// swimmers a Goto toward a cell. The swimmer's own comp keeps it under on sand and surfaces it on hard ground.</summary>
    public static class RM_SwimmerCalls
    {
        public static int Call(Map map, IntVec3 at, float radius, int max, int arriveRadius)
        {
            var found = new List<Pawn>();
            RM_SandSwimUtility.SubmergedSwimmersNear(map, at, radius, 0f, found);
            found.Sort((x, y) => (x.Position - at).LengthHorizontalSquared.CompareTo((y.Position - at).LengthHorizontalSquared));
            var cands = new List<RM_CallCand>(found.Count);
            for (int i = 0; i < found.Count; i++)
            {
                Pawn p = found[i];
                Job cur = p.CurJob;
                cands.Add(new RM_CallCand
                {
                    id = i,
                    distSq = (p.Position - at).LengthHorizontalSquared,
                    player = p.Faction == Faction.OfPlayer,
                    downed = p.Downed,
                    cantMove = p.pather == null || p.jobs == null,
                    busyHunting = cur != null && (cur.def == JobDefOf.AttackMelee || cur.def == JobDefOf.PredatorHunt),
                });
            }
            var dests = new Dictionary<int, IntVec3>();
            List<int> chosen = RM_SunKernel.SelectCalls(cands, max, arriveRadius, i =>
            {
                IntVec3 d = CellNear(map, at, found[i], arriveRadius);
                dests[i] = d;
                return d.IsValid;
            });
            for (int k = 0; k < chosen.Count; k++)
            {
                Pawn p = found[chosen[k]];
                Job go = JobMaker.MakeJob(JobDefOf.Goto, dests[chosen[k]]);
                go.locomotionUrgency = LocomotionUrgency.Walk;
                go.expiryInterval = 1500;
                p.jobs.StartJob(go, JobCondition.InterruptForced, null, false, true);
            }
            return chosen.Count;
        }

        private static IntVec3 CellNear(Map map, IntVec3 at, Pawn p, int radius)
        {
            IntVec3 best = IntVec3.Invalid;
            float bestD = 99999f;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(at, radius, false))
            {
                if (!c.InBounds(map) || !c.Standable(map)) continue;
                float d = (c - p.Position).LengthHorizontalSquared;
                if (d < bestD) { bestD = d; best = c; }
            }
            return best;
        }
    }

    public class RM_CompProperties_Thumper : CompProperties
    {
        public int beatIntervalTicks = 600;
        public int wetCellRadius = 2;
        public int wetTicks = 15000;
        public int maxCallsPerBeat = 4;
        public int arriveRadius = 3;

        public RM_CompProperties_Thumper() { compClass = typeof(RM_CompThumper); }
    }

    public class RM_CompThumper : ThingComp
    {
        private int lastBeatTick = -99999;
        private int beatsTotal;
        private int lastCalled;

        public RM_CompProperties_Thumper Props { get { return (RM_CompProperties_Thumper)props; } }
        public int BeatsTotal { get { return beatsTotal; } }
        public int LastCalled { get { return lastCalled; } }

        public bool Charged
        {
            get
            {
                CompRefuelable fuel = parent.GetComp<CompRefuelable>();
                return fuel != null && fuel.HasFuel;
            }
        }

        public override void CompTick()
        {
            if (!parent.Spawned || !parent.IsHashIntervalTick(60)) return;
            if (!RM_SandSwimRemSettings.thumperEnabled) return;
            int now = Find.TickManager.TicksGame;
            CompRefuelable fuel = parent.GetComp<CompRefuelable>();
            if (!RM_SunKernel.BeatDue(true, now, lastBeatTick, Props.beatIntervalTicks, fuel != null && fuel.HasFuel)) return;
            lastBeatTick = now;
            Beat(fuel);
        }

        public void Beat(CompRefuelable fuel)
        {
            fuel.ConsumeFuel(1f);
            beatsTotal++;
            Map map = parent.Map;
            RM_MapComponent_WetSand wet = RM_MapComponent_WetSand.For(map);
            if (wet != null)
            {
                int r = Props.wetCellRadius;
                foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, r, true))
                {
                    if (c.InBounds(map)) wet.MarkWet(c, Props.wetTicks);
                }
                wet.NotePour(parent.Position, 600);
            }
            FleckMaker.ThrowDustPuffThick(parent.DrawPos, map, 1.4f, new Color(0.78f, 0.69f, 0.52f, 0.9f));
            lastCalled = CallSwimmers();
        }

        // Submerged swimmers in radius that are not busy hunting get a Goto toward the thumper.
        public int CallSwimmers()
        {
            return RM_SwimmerCalls.Call(parent.Map, parent.Position, RM_SandSwimRemSettings.thumperRadius,
                Props.maxCallsPerBeat, Props.arriveRadius);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_SandSwimRemSettings.thumperEnabled) return "Thumper switched off in Mod Settings.";
            return Charged ? "Charged: it beats every " + Props.beatIntervalTicks.ToStringTicksToPeriod() + "."
                           : "Uncharged: it needs stilled water.";
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            if (parent.Spawned) GenDraw.DrawRadiusRing(parent.Position, RM_SandSwimRemSettings.thumperRadius);
        }

        public override void PostExposeData()
        {
            Scribe_Values.Look(ref lastBeatTick, "rmThumperLastBeat", -99999);
            Scribe_Values.Look(ref beatsTotal, "rmThumperBeats", 0);
        }
    }

    // Mod Settings for the sand-swim remainder; Expose/Draw are called from RM_StillsandSettings.
    public static class RM_SandSwimRemSettings
    {
        public static bool thumperEnabled = true;
        public static float thumperRadius = 40f;
        public static bool sandFishingWakeEnabled = true;
        public static float sandFishingWakeChance = 0.15f;
        public static bool driftSwimEnabled = true;
        public static float driftSwimDepth = 0.3f;
        public static bool listeningHissEnabled = true;
        public static bool listeningSingingEnabled = true;
        public static bool listeningWarningEnabled = true;
        public static bool listeningRumbleEnabled = true;
        public static float singingWarningCells = 12f;

        public static void Expose()
        {
            Scribe_Values.Look(ref thumperEnabled, "sw_thumperEnabled", true);
            Scribe_Values.Look(ref thumperRadius, "sw_thumperRadius", 40f);
            Scribe_Values.Look(ref sandFishingWakeEnabled, "sw_sandFishingWakeEnabled", true);
            Scribe_Values.Look(ref sandFishingWakeChance, "sw_sandFishingWakeChance", 0.15f);
            Scribe_Values.Look(ref driftSwimEnabled, "sw_driftSwimEnabled", true);
            Scribe_Values.Look(ref driftSwimDepth, "sw_driftSwimDepth", 0.3f);
            Scribe_Values.Look(ref listeningHissEnabled, "sw_listeningHissEnabled", true);
            Scribe_Values.Look(ref listeningSingingEnabled, "sw_listeningSingingEnabled", true);
            Scribe_Values.Look(ref listeningWarningEnabled, "sw_listeningWarningEnabled", true);
            Scribe_Values.Look(ref listeningRumbleEnabled, "sw_listeningRumbleEnabled", true);
            Scribe_Values.Look(ref singingWarningCells, "sw_singingWarningCells", 12f);
        }

        public static void Draw(Listing_Standard list)
        {
            list.GapLine();
            list.Label("Under the sand");
            list.CheckboxLabeled("Thumper calls swimmers", ref thumperEnabled,
                "A charged, beating thumper wets the sand around it and calls submerged sand swimmers within its radius toward it. Off: it never beats.");
            list.Label("Thumper call radius: " + Mathf.RoundToInt(thumperRadius) + " cells");
            thumperRadius = Mathf.Round(list.Slider(thumperRadius, 10f, 80f));
            list.CheckboxLabeled("Sand fishing draws a stalker wake", ref sandFishingWakeEnabled,
                "A fishing session on deep sand has a small chance to draw a nearby submerged swimmer toward the fisher. Off: fishing is quiet.");
            list.Label("Chance per catch: " + sandFishingWakeChance.ToStringPercent());
            sandFishingWakeChance = Mathf.Round(list.Slider(sandFishingWakeChance, 0f, 1f) * 100f) / 100f;
            list.CheckboxLabeled("Swimmers swim through deep drifts", ref driftSwimEnabled,
                "Where the dune engine is present, a drift of sand at or above the depth below counts as swim ground. Off: only sand terrain does.");
            list.Label("Drift depth that counts as swim ground: " + driftSwimDepth.ToString("0.00"));
            driftSwimDepth = Mathf.Round(list.Slider(driftSwimDepth, 0.1f, 1f) * 20f) / 20f;
            list.GapLine();
            list.Label("The Listening");
            list.CheckboxLabeled("Wind hiss and saltation", ref listeningHissEnabled,
                "The always-on room tone of the sand, scaled by wind speed. Off: no hiss bed.");
            list.CheckboxLabeled("Singing dunes", ref listeningSingingEnabled,
                "A slab sliding off a slip face booms. Off: the dunes stay quiet.");
            list.CheckboxLabeled("Singing-dune warning", ref listeningWarningEnabled,
                "A one-line warning the first time a singing slip face comes near one of your buildings.");
            list.Label("Warning distance: " + Mathf.RoundToInt(singingWarningCells) + " cells");
            singingWarningCells = Mathf.Round(list.Slider(singingWarningCells, 4f, 40f));
            list.CheckboxLabeled("Rumble and breach sounds", ref listeningRumbleEnabled,
                "Stillsand's own rumble and breach sounds for swimmers. Off: swimmers use whatever sound their extension names, if any.");
        }
    }
}
