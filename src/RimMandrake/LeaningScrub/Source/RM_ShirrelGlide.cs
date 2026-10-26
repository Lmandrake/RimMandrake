using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // SHIRREL_DECIDE_GALE_GLIDE — owner by card 2026-10-26 07:21 ("Shirrel ... How should the Gale glide work? -> Real
    // glide as a flyer", option B, chosen over the ground dash knowing flight cannot be live-tested).
    //
    //   GLIDE  — while the Gale blows, an idle wild shirrel beside a tree launches as a real 1.6 flyer
    //            (Pawn_FlightTracker, the eruptors' RM_Flight.TryLaunch path) on a Goto job aimed hopMin..hopMax cells
    //            DOWNWIND (the Lean's one wind, RM_MapComponent_Lean.Downwind), and lands by itself: the Goto ends, or
    //            MaxFlightTime runs out (the def's cap), whichever is first.
    //   GATE   — the def carries MaxFlightTime so the tracker CAN fly it, and flightStartChanceOnJobStart is 0; on top of
    //            that a postfix on Pawn_FlightTracker.CanFlyNow answers false for a shirrel unless its own launch is in
    //            progress (RM_GlideKernel.CanFlyNow). Decompiled 1.6: CanFlyNow gates both StartFlying and the
    //            tryStartFlying branch of Notify_JobStarted, so no job def (overrideFlyChance included) lifts it outside
    //            the glide; a shirrel already in the air keeps vanilla's keep-flying / ForceLand handling.
    //   TETHER — it binds to the nearest sweetline tree (homeTrees) through CreatureBehaviors' RM_CompHomeTether, so after
    //            a hop it walks back home. No sweetline tree on the map (most maps: sweetlineTreeMapChance) -> unbound, a
    //            plain wild animal that may still launch from any tree (launchFromAnyTree, PROVISIONAL: without it the
    //            glide would not exist on most Scrub maps).
    //   ART    — no flying flip-book frames exist yet (flyingAnimationFramePathPrefix unset). GetBestFlyAnimation returns
    //            null and the shirrel flies drawn with its normal body graphic, lifted by the tracker: correct, plainer.
    //   OFF    — Mod Settings "Shirrel: glides on the Gale" (shirrelGlideEnabled, default on). Off: no launch, no binding
    //            (tether home cleared: a plain wild animal), and the gate still holds so it never flies at all.
    // Must be listed AFTER RM_CompProperties_HomeTether in the def's comps (its bind overrides the tether's spawn home).
    // Verify by STATE read only (RM_ShirrelGlideProof); a live look at the glide is a joint session with the owner.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_ShirrelGlide : CompProperties
    {
        public List<ThingDef> homeTrees = new List<ThingDef>();
        public bool launchFromAnyTree = true;
        public float launchRadius = 3f;
        public float hopMin = 10f;
        public float hopMax = 16f;
        public float glideMtbHours = 1.5f;
        public int checkIntervalTicks = 250;

        public RM_CompProperties_ShirrelGlide()
        {
            compClass = typeof(RM_CompShirrelGlide);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef)) yield return e;
            if (homeTrees.NullOrEmpty()) yield return "RM_CompProperties_ShirrelGlide: homeTrees is empty (nothing to bind to)";
            else
                foreach (ThingDef d in homeTrees)
                    if (d == null || d.plant == null || !d.plant.IsTree) yield return "RM_CompProperties_ShirrelGlide: home tree " + d + " is not a tree";
            if (hopMin <= 0f || hopMax < hopMin) yield return "RM_CompProperties_ShirrelGlide: hopMin/hopMax must be 0 < hopMin <= hopMax";
            int tether = parentDef.comps == null ? -1 : parentDef.comps.FindIndex(c => c is RM_CompProperties_HomeTether);
            int self = parentDef.comps == null ? -1 : parentDef.comps.IndexOf(this);
            if (tether < 0) yield return "RM_CompProperties_ShirrelGlide: " + parentDef.defName + " has no RM_CompProperties_HomeTether";
            else if (self >= 0 && self < tether) yield return "RM_CompProperties_ShirrelGlide: must be listed after RM_CompProperties_HomeTether";
            if (parentDef.GetStatValueAbstract(StatDefOf.MaxFlightTime) <= 0f)
                yield return "RM_CompProperties_ShirrelGlide: " + parentDef.defName + " has no MaxFlightTime (the tracker cannot fly it)";
        }
    }

    public class RM_CompShirrelGlide : ThingComp
    {
        private Thing boundTree;
        private int glides;
        private int lastGlideTick = -1;
        private bool launching;   // true only inside Launch(); never saved

        public RM_CompProperties_ShirrelGlide Props => (RM_CompProperties_ShirrelGlide)props;
        public Thing BoundTree => boundTree;
        public bool Launching => launching;
        public int Glides => glides;
        public int LastGlideTick => lastGlideTick;
        private Pawn Pawn => parent as Pawn;
        private RM_CompHomeTether Tether => parent.TryGetComp<RM_CompHomeTether>();

        public static bool FeatureOn => RM_WindCalendar.On(RM_LeaningScrubSettings.shirrelGlideEnabled);

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad) Bind();
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            int interval = Mathf.Max(1, Props.checkIntervalTicks);
            if (!parent.Spawned || !parent.IsHashIntervalTick(interval, delta)) return;
            Bind();
            TryGlide(interval);
        }

        // ------------------------------------------------------------------ bind
        private bool TreeValid(Thing t)
        {
            return t != null && t.Spawned && !t.Destroyed && t.Map == parent.Map;
        }

        private void Bind()
        {
            RM_CompHomeTether tether = Tether;
            if (!FeatureOn)
            {
                if (boundTree != null || (tether != null && tether.Home.IsValid))
                {
                    boundTree = null;
                    tether?.SetHome(IntVec3.Invalid);   // off: a plain wild animal
                }
                return;
            }
            if (!TreeValid(boundTree))
            {
                boundTree = Nearest(HomeTreesOn(parent.Map), parent.Position);
            }
            IntVec3 home = boundTree != null ? boundTree.Position : IntVec3.Invalid;
            if (tether != null && tether.Home != home) tether.SetHome(home);
        }

        private IEnumerable<Thing> HomeTreesOn(Map map)
        {
            foreach (ThingDef d in Props.homeTrees)
                if (d != null)
                    foreach (Thing t in map.listerThings.ThingsOfDef(d))
                        if (t.Spawned && !t.Destroyed) yield return t;
        }

        private static Thing Nearest(IEnumerable<Thing> things, IntVec3 from)
        {
            Thing best = null;
            int bestD = int.MaxValue;
            foreach (Thing t in things)
            {
                int d = (t.Position - from).LengthHorizontalSquared;
                if (d < bestD) { bestD = d; best = t; }
            }
            return best;
        }

        private bool NearLaunchTree(Pawn pawn)
        {
            Map map = pawn.Map;
            float r = Mathf.Max(1f, Props.launchRadius);
            if (TreeValid(boundTree) && (boundTree.Position - pawn.Position).LengthHorizontalSquared <= r * r) return true;
            if (boundTree != null && !Props.launchFromAnyTree) return false;
            int cells = GenRadial.NumCellsInRadius(r);
            for (int i = 0; i < cells; i++)
            {
                IntVec3 c = pawn.Position + GenRadial.RadialPattern[i];
                if (!c.InBounds(map)) continue;
                Plant p = c.GetPlant(map);
                if (p != null && p.def.plant != null && p.def.plant.IsTree
                    && (Props.launchFromAnyTree || Props.homeTrees.Contains(p.def))) return true;
            }
            return false;
        }

        private static bool Idle(Pawn pawn)
        {
            Job cur = pawn.CurJob;
            return cur == null || cur.def == JobDefOf.Wait_Wander || cur.def == JobDefOf.GotoWander || cur.def == JobDefOf.Wait;
        }

        // The tracker's own answer with the gate lifted (cooldown, already flying, vacuum, MaxFlightTime).
        private bool VanillaCanFly(Pawn pawn)
        {
            if (pawn.flight == null) return false;
            launching = true;
            try { return pawn.flight.CanFlyNow; }
            finally { launching = false; }
        }

        // ------------------------------------------------------------------ glide
        private void TryGlide(int interval)
        {
            Pawn pawn = Pawn;
            if (pawn == null || pawn.Dead || !pawn.Spawned || pawn.jobs == null) return;
            Map map = pawn.Map;
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            bool gale = RM_WindCalendar.IsGale(map);
            if (!FeatureOn || !gale || lean == null) return;   // cheap gates first; the kernel repeats them for the record
            bool ok = RM_GlideKernel.ShouldGlide(FeatureOn, gale, lean != null, pawn.Faction == null, Idle(pawn), pawn.Awake(),
                pawn.Downed, pawn.InMentalState, NearLaunchTree(pawn), VanillaCanFly(pawn), Rand.Value,
                RM_GlideKernel.ChancePerCheck(Props.glideMtbHours, interval));
            if (ok) Launch(pawn, lean.Downwind);
        }

        /// <summary>One downwind hop: Goto a landing cell, then take off on it. Returns whether the pawn is in the air.</summary>
        public bool Launch(Pawn pawn, Vector2 downwind)
        {
            Map map = pawn.Map;
            float dist = RM_GlideKernel.HopDistance(Props.hopMin, Props.hopMax, Rand.Value);
            RM_GlideKernel.HopTarget(pawn.Position.x, pawn.Position.z, downwind.x, downwind.y, dist, map.Size.x, map.Size.z, 3,
                out int tx, out int tz);
            IntVec3 aim = new IntVec3(tx, 0, tz);
            if (!CellFinder.TryFindRandomCellNear(aim, map, 3,
                    c => c.InBounds(map) && c.Standable(map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some),
                    out IntVec3 dest))
            {
                return false;
            }
            Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
            job.locomotionUrgency = LocomotionUrgency.Jog;
            pawn.jobs.StartJob(job, JobCondition.InterruptForced);
            launching = true;
            try { RM_Flight.TryLaunch(pawn); }   // after StartJob, never before (RM_Flight's own rule)
            finally { launching = false; }
            bool up = pawn.flight != null && pawn.flight.Flying;
            if (up)
            {
                glides++;
                lastGlideTick = Find.TickManager.TicksGame;
            }
            return up;
        }

        public override string CompInspectStringExtra()
        {
            Pawn pawn = Pawn;
            return RM_GlideKernel.Describe(FeatureOn, TreeValid(boundTree), boundTree?.LabelShortCap,
                pawn?.flight != null && pawn.flight.Flying);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref boundTree, "rmShirrelTree");
            Scribe_Values.Look(ref glides, "rmShirrelGlides", 0);
            Scribe_Values.Look(ref lastGlideTick, "rmShirrelLastGlide", -1);
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_ShirrelGlidePatches
    {
        private static readonly AccessTools.FieldRef<Pawn_FlightTracker, Pawn> PawnRef =
            AccessTools.FieldRefAccess<Pawn_FlightTracker, Pawn>("pawn");

        static RM_ShirrelGlidePatches()
        {
            var target = AccessTools.PropertyGetter(typeof(Pawn_FlightTracker), nameof(Pawn_FlightTracker.CanFlyNow));
            if (target == null)
            {
                Log.Warning("[RM LeaningScrub] shirrel glide: Pawn_FlightTracker.CanFlyNow not found; the shirrel's flight is ungated.");
                return;
            }
            new Harmony("mandrake.rm.leaningscrub").Patch(target,
                postfix: new HarmonyMethod(typeof(RM_ShirrelGlidePatches), nameof(CanFlyNow_Postfix)));
        }

        public static void CanFlyNow_Postfix(Pawn_FlightTracker __instance, ref bool __result)
        {
            if (!__result) return;
            RM_CompShirrelGlide glide = PawnRef(__instance)?.TryGetComp<RM_CompShirrelGlide>();
            __result = RM_GlideKernel.CanFlyNow(__result, glide != null, glide != null && glide.Launching);
        }
    }

    // jawa/static_call proof hook. PURE STATE READ of every spawned glider on the current map: it launches nothing and
    // advances nothing (owner: never live-test a flyer's flight without him present). PASS when every glider can ever fly
    // (MaxFlightTime > 0), the gate refuses take-off to every grounded glider, and none is in the air outside the Gale.
    public static class RM_ShirrelGlideProof
    {
        public static string ProofGlide(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED no map";
            List<Pawn> gliders = map.mapPawns.AllPawnsSpawned.Where(p => p.TryGetComp<RM_CompShirrelGlide>() != null).ToList();
            if (gliders.Count == 0) return "UNMEASURED no glider (RM_Shirrel) spawned on the current map";
            bool gale = RM_WindCalendar.IsGale(map);
            int canEver = 0, gateHeld = 0, grounded = 0, flying = 0, bound = 0;
            foreach (Pawn p in gliders)
            {
                RM_CompShirrelGlide g = p.TryGetComp<RM_CompShirrelGlide>();
                if (p.flight == null) continue;
                if (p.flight.CanEverFly) canEver++;
                if (g.BoundTree != null) bound++;
                if (p.flight.Flying) { flying++; continue; }
                grounded++;
                if (!p.flight.CanFlyNow) gateHeld++;
            }
            string s = " gliders=" + gliders.Count + " canEverFly=" + canEver + " grounded=" + grounded + " gateHeld=" + gateHeld
                + " flying=" + flying + " bound=" + bound + " gale=" + gale + " feature=" + RM_CompShirrelGlide.FeatureOn
                + " flipbook=" + (Pawn_FlightTracker.GetBestFlyAnimation(gliders[0]) != null);
            if (canEver != gliders.Count) return "FAIL a glider cannot ever fly (MaxFlightTime missing)" + s;
            if (gateHeld != grounded) return "FAIL the gate let a grounded glider take off outside its launch" + s;
            if (!gale && flying > 0) return "FAIL a glider is in the air outside the Gale" + s;
            return "PASS" + s;
        }
    }
}
