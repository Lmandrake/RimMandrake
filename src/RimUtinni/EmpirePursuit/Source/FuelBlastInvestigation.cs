/* CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL — a FlowWorks fuel blast draws the Empire.
 * Owner, by card 2026-10-15: "In Utinni such a thing should instantly summon raids coming to check out what is going
 * on as quickly as they can get there and massive imperial heat increase."
 *
 * FlowWorks (mandrake.rm.flowworks) is SOFT, like Visibility and Aftermath in EmpireLadder.cs: its
 * RimMandrake.FlowWorks.RM_FuelFireEvents events are bound by reflection, so this mod gains no dependency and does
 * nothing when FlowWorks is absent. The heat is the Colony Visibility dial (the Empire's attention meter, design
 * empire_escalation_ladder_design_2026-10-02.md §1: one meter, not a second one), raised through
 * EmpireSearch.AdjustVisibility; with Visibility absent only the raid comes.
 *
 * On an astrofuel detonation (or a chemfuel fire past FlowWorks' large-fire size): Visibility up by the settings dial
 * (a detonation up to twice it, a fire a third), then ONE forced RaidEnemy per map per day by the pursuing faction
 * (the vanilla raid picks any hostile faction when the pursuer is not hostile or absent), dropping by pod onto the
 * blast after RFPSettings.fuelBlastDropHours. Forced, so the storyteller-spacing patch passes it. PROVISIONAL numbers. */
using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RuthlessPursuingMechanoids
{
    [StaticConstructorOnStartup]
    public static class FuelBlastInvestigation
    {
        public static bool Bound { get; private set; }

        static FuelBlastInvestigation()
        {
            Type t = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_FuelFireEvents");
            if (t == null) return;
            Bound = Bind(t, "AstrofuelDetonated", nameof(OnDetonation)) & Bind(t, "LargeChemfuelFire", nameof(OnLargeFire));
            Log.Message("[EmpireSearch] fuel blasts bound to FlowWorks: " + Bound);
        }

        private static bool Bind(Type t, string evName, string handler)
        {
            EventInfo ev = t.GetEvent(evName, BindingFlags.Public | BindingFlags.Static);
            MethodInfo m = typeof(FuelBlastInvestigation).GetMethod(handler, BindingFlags.Public | BindingFlags.Static);
            if (ev == null || m == null) return false;
            try
            {
                ev.AddEventHandler(null, Delegate.CreateDelegate(ev.EventHandlerType, m));
                return true;
            }
            catch (Exception e)
            {
                Log.Warning("[EmpireSearch] could not bind FlowWorks " + evName + ": " + e.Message);
                return false;
            }
        }

        public static void OnDetonation(Map map, IntVec3 at, int cells)
        {
            Investigate(map, at, EmpireLadderMath.BlastVisibility(RFPSettings.fuelBlastVisibility, cells),
                "an astrofuel detonation of " + cells + " cells");
        }

        public static void OnLargeFire(Map map, IntVec3 at, int cells)
        {
            Investigate(map, at, EmpireLadderMath.FireVisibility(RFPSettings.fuelBlastVisibility),
                "a chemfuel fire of " + cells + " cells");
        }

        /// <summary>The visibility rise, then the investigating raid (once per map per day). Returns what it did, for the
        /// proof surface: "VIS +n" and "RAID queued at tick T" or "RAID cooling down" / "OFF".</summary>
        public static string Investigate(Map map, IntVec3 at, float visibility, string what)
        {
            if (!RFPSettings.fuelBlastInvestigationEnabled || map == null) return "OFF";
            if (visibility > 0f) EmpireSearch.AdjustVisibility(visibility, what);
            string result = "VIS +" + visibility.ToString("0");
            int now = Find.TickManager.TicksGame;
            MapComponent_EmpireSearch c = MapComponent_EmpireSearch.For(map);
            if (c != null && !EmpireLadderMath.InvestigationDue(c.lastFuelBlastTick, now, GenDate.TicksPerDay))
                return result + " | RAID cooling down";
            if (c != null) c.lastFuelBlastTick = now;
            Faction f = EmpireSearch.Part?.PursuitFaction ?? Faction.OfEmpire;
            if (f != null && (f.defeated || !f.HostileTo(Faction.OfPlayer))) f = null;
            IncidentParms parms = new IncidentParms
            {
                target = map,
                forced = true,
                faction = f,
                points = StorytellerUtility.DefaultThreatPointsNow(map),
                raidStrategy = RaidStrategyDefOf.ImmediateAttack,
                raidArrivalMode = PawnsArrivalModeDefOf.CenterDrop,
                spawnCenter = at,
            };
            int fire = now + EmpireLadderMath.InvestigationDelayTicks(RFPSettings.fuelBlastDropHours);
            QueuedIncident qi = new QueuedIncident(new FiringIncident(IncidentDefOf.RaidEnemy, null, parms), fire, GenDate.TicksPerHour * 6);
            bool queued = Find.Storyteller.incidentQueue.Add(qi);
            if (queued) lastQueued = qi;
            Messages.Message("RUT_FuelBlast_Seen".Translate(), new TargetInfo(at, map), MessageTypeDefOf.ThreatBig);
            Log.Message("[EmpireSearch] " + what + " on " + map + ": " + result + ", investigating raid "
                + (queued ? "queued for tick " + fire : "NOT queued") + " (" + (f?.Name ?? "any hostile faction") + ")");
            return result + " | RAID " + (queued ? "queued at tick " + fire : "not queued");
        }

        /// <summary>The investigating raid this session queued last (not saved: proof surfaces only).</summary>
        private static QueuedIncident lastQueued;

        private static bool StillQueued()
        {
            if (lastQueued == null || Find.Storyteller?.incidentQueue == null) return false;
            foreach (object o in Find.Storyteller.incidentQueue)
                if (o == lastQueued) return true;
            return false;
        }

        /// <summary>"STATE bound=b last=T queued=b fireIn=N vis=V" for the current map (vis -1 = Visibility absent).</summary>
        public static string ProofState(string arg)
        {
            Map map = Find.CurrentMap;
            int last = MapComponent_EmpireSearch.For(map)?.lastFuelBlastTick ?? -1;
            bool q = StillQueued();
            int fireIn = q ? lastQueued.FireTick - Find.TickManager.TicksGame : -1;
            return "STATE bound=" + Bound + " last=" + last + " queued=" + q + " fireIn=" + fireIn
                + " vis=" + EmpireSearch.Visibility().ToString("0.0");
        }

        /// <summary>WRITES. Fire the queued investigating raid now instead of hours later (the live proof does not wait):
        /// "FIRED b faction=..." or "REFUSED: nothing queued".</summary>
        public static string ProofFireNow(string arg)
        {
            if (!StillQueued()) return "REFUSED: nothing queued";
            QueuedIncident qi = lastQueued;
            Cancel(qi);
            bool fired = Find.Storyteller.TryFire(qi.FiringIncident, queued: true);
            return "FIRED " + fired + " faction=" + (qi.FiringIncident.parms.faction?.Name ?? "any");
        }

        /// <summary>WRITES. Drop the queued investigating raid (a proof that must not leave a raid for the next chain).</summary>
        public static string ProofCancel(string arg)
        {
            bool had = StillQueued();
            if (had) Cancel(lastQueued);
            return "CANCELLED " + had;
        }

        private static void Cancel(QueuedIncident qi)
        {
            var list = AccessTools.Field(typeof(IncidentQueue), "queuedIncidents")?.GetValue(Find.Storyteller.incidentQueue)
                as System.Collections.Generic.List<QueuedIncident>;
            list?.Remove(qi);
            if (lastQueued == qi) lastQueued = null;
        }

        /// <summary>static_call surface for the bridge: "x,z" runs Investigate on the current map as a 100-cell detonation
        /// would (the cooldown applies). "" reports whether the FlowWorks events are bound.</summary>
        public static string ProofInvestigate(string arg)
        {
            if (string.IsNullOrEmpty(arg)) return "BOUND " + Bound;
            Map map = Find.CurrentMap;
            string[] p = arg.Split(',');
            if (map == null || p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
                return "REFUSED: arg must be x,z on the current map";
            return Investigate(map, new IntVec3(x, 0, z), EmpireLadderMath.BlastVisibility(RFPSettings.fuelBlastVisibility, 100), "a proof blast");
        }
    }
}
