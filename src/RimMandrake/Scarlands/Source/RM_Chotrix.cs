using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_CHOTRIX_BUILD_1. The chotrix is invisible while standing or stalking (stock invisibility hediff),
    // shows for a few seconds when it strikes, hunts only lone small prey, and flees after one bite if hurt.
    // Its readable signs (prints, dragged-kill marks, the tetchik silence ring) are RM_ChotrixSigns.cs and the
    // Geiger choir; the static registry and SilenceRadius below are what the choir reads.
    public class CompProperties_Chotrix : CompProperties
    {
        public HediffDef cloakHediff;
        public int checkIntervalTicks = 10;
        public int revealTicks = 240;
        public int fleeTicks = 900;
        public float hurtBelow = 0.9f;
        public float hungerBelow = 0.7f;
        public float smallPreyBodySize = 0.6f;
        public float lonePawnRadius = 12f;
        public float loneAnimalRadius = 8f;
        public float silenceRadius = 9f;
        public int nightStartHour = 20;
        public int nightEndHour = 6;
        // Calves of these are prey (matched by defName so the list can name defs from other mods).
        public List<string> calfPreyDefNames = new List<string>();
        public CompProperties_Chotrix() { compClass = typeof(CompChotrix); }
    }

    public class CompChotrix : ThingComp
    {
        public static readonly List<CompChotrix> All = new List<CompChotrix>();
        private int revealUntil = -1;
        private int fleeUntil = -1;
        private int lastStrike = -99999;
        public int nextHuntCheck;
        // The last pawn it bit, for the drag (WARSCAR_CHOTRIX_SIGNS_1). Not saved: a reload forgets one fresh kill.
        public Pawn lastVictim;
        public bool victimDragged;
        public int lastStrikeTick { get { return lastStrike; } }

        public CompProperties_Chotrix Props { get { return (CompProperties_Chotrix)props; } }
        public Pawn Pawn { get { return parent as Pawn; } }
        // Read by the Geiger choir: tetchik go quiet within this many cells of a living chotrix.
        public float SilenceRadius { get { return Props.silenceRadius; } }
        public bool Fleeing { get { return Find.TickManager.TicksGame < fleeUntil; } }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref revealUntil, "revealUntil", -1);
            Scribe_Values.Look(ref fleeUntil, "fleeUntil", -1);
            Scribe_Values.Look(ref lastStrike, "lastStrike", -99999);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad) { base.PostSpawnSetup(respawningAfterLoad); if (!All.Contains(this)) All.Add(this); }
        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish) { base.PostDeSpawn(map, mode); All.Remove(this); }

        public void Struck(Pawn victim)
        {
            int now = Find.TickManager.TicksGame;
            lastStrike = now;
            if (victim != null && victim != lastVictim) { lastVictim = victim; victimDragged = false; }
            revealUntil = now + Mathf.RoundToInt(RM_WarscarSettings.chotrixRevealSeconds * 60f);
            Reveal();
        }

        public override void CompTick()
        {
            base.CompTick();
            Pawn p = Pawn;
            if (p == null || !p.Spawned || p.Dead || !parent.IsHashIntervalTick(Props.checkIntervalTicks)) return;
            int now = Find.TickManager.TicksGame;
            if (!RM_WarscarSettings.chotrixEnabled || p.Downed) { Reveal(); return; }
            // Hurt shortly after a bite: flee. Checked before the reveal window returns, so a long reveal setting
            // (up to 15 s = 900 ticks) cannot outlast this 600-tick window and silently disable the flight.
            if (now - lastStrike < 600 && now >= fleeUntil && p.health.summaryHealth.SummaryHealthPercent < Props.hurtBelow)
                fleeUntil = now + Props.fleeTicks;
            if (now < revealUntil) return;
            Cloak();
            // Heat shimmer when it runs: the readable sign for an invisible thing.
            if (p.pather != null && p.pather.Moving && p.jobs != null && p.jobs.curJob != null
                && p.jobs.curJob.locomotionUrgency >= LocomotionUrgency.Jog)
                FleckMaker.ThrowHeatGlow(p.Position, p.Map, 1f);
        }

        private void Cloak()
        {
            Pawn p = Pawn;
            if (Props.cloakHediff == null || p.health == null) return;
            if (p.health.hediffSet.GetFirstHediffOfDef(Props.cloakHediff) == null)
                p.health.AddHediff(HediffMaker.MakeHediff(Props.cloakHediff, p));
        }

        private void Reveal()
        {
            Pawn p = Pawn;
            if (Props.cloakHediff == null || p.health == null) return;
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Props.cloakHediff);
            if (h == null) return;
            p.GetInvisibilityComp()?.BecomeVisible(instant: true);
            p.health.RemoveHediff(h);
        }

        public override string CompInspectStringExtra()
        {
            return Fleeing ? "Hurt. Running." : null;
        }
    }

    [HarmonyPatch(typeof(Verb_MeleeAttack), "TryCastShot")]
    public static class Patch_Verb_MeleeAttack_TryCastShot_Chotrix
    {
        public static void Postfix(Verb_MeleeAttack __instance, bool __result)
        {
            if (!__result || CompChotrix.All.Count == 0) return;
            Pawn p = __instance.CasterPawn;
            if (p == null) return;
            CompChotrix c = p.TryGetComp<CompChotrix>();
            if (c != null) c.Struck(__instance.CurrentTarget.Thing as Pawn);
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_ChotrixPatches
    {
        static RM_ChotrixPatches() { RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.warscar.chotrix"), typeof(RM_ChotrixPatches).Assembly, "RimMandrake.Scarlands"); }
    }

    // Hunts lone small animals, calves of the listed species, and lone pawns at night. Never a group of two or more.
    public class JobGiver_ChotrixHunt : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            CompChotrix c = pawn.TryGetComp<CompChotrix>();
            if (c == null || !RM_WarscarSettings.chotrixEnabled || pawn.Downed || pawn.InMentalState || c.Fleeing) return null;
            int now = Find.TickManager.TicksGame;
            if (now < c.nextHuntCheck) return null;
            c.nextHuntCheck = now + 120;
            if (pawn.needs == null || pawn.needs.food == null || pawn.needs.food.CurLevelPercentage > c.Props.hungerBelow) return null;
            Pawn prey = FindPrey(pawn, c.Props);
            if (prey == null) return null;
            Job j = JobMaker.MakeJob(JobDefOf.AttackMelee, prey);
            j.maxNumMeleeAttacks = 1;
            j.expiryInterval = 900;
            j.checkOverrideOnExpire = true;
            j.locomotionUrgency = LocomotionUrgency.Walk; // stalking; it speeds up only on the bite
            return j;
        }

        public static bool IsNight(Map map, CompProperties_Chotrix pr)
        {
            int h = GenLocalDate.HourInteger(map);
            return h >= pr.nightStartHour || h < pr.nightEndHour;
        }

        public static Pawn FindPrey(Pawn pawn, CompProperties_Chotrix pr)
        {
            Map map = pawn.Map;
            bool night = IsNight(map, pr);
            IReadOnlyList<Pawn> all = map.mapPawns.AllPawnsSpawned;
            Pawn best = null; float bestD = 40f * 40f;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn t = all[i];
                if (t == pawn || t.Dead || t.Downed || !t.Spawned) continue;
                float d = (t.Position - pawn.Position).LengthHorizontalSquared;
                if (d >= bestD) continue; // distance first: IsLone walks every pawn (belt SC-4)
                if (!IsPreyKind(t, pr, night) || !IsLone(t, pr)) continue;
                if (!pawn.CanReach(t, PathEndMode.Touch, Danger.Deadly)) continue;
                best = t; bestD = d;
            }
            return best;
        }

        public static bool IsPreyKind(Pawn t, CompProperties_Chotrix pr, bool night)
        {
            if (t.RaceProps.Humanlike) return night && t.Faction != null;
            if (!t.RaceProps.Animal || t.def.HasComp(typeof(CompChotrix))) return false;
            if (t.def.race.baseBodySize <= pr.smallPreyBodySize) return true;
            bool calf = t.ageTracker != null && t.ageTracker.CurLifeStage != null && !t.ageTracker.CurLifeStage.reproductive;
            return calf && pr.calfPreyDefNames.Contains(t.def.defName);
        }

        // Lone = nothing else of its kind or company within the radius.
        public static bool IsLone(Pawn t, CompProperties_Chotrix pr)
        {
            bool human = t.RaceProps.Humanlike;
            float r = human ? pr.lonePawnRadius : pr.loneAnimalRadius;
            IReadOnlyList<Pawn> all = t.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn o = all[i];
                if (o == t || o.Dead || !o.Spawned || o.Downed) continue;
                if ((o.Position - t.Position).LengthHorizontalSquared > r * r) continue;
                if (human ? (o.RaceProps.Humanlike || (o.Faction != null && o.Faction == t.Faction)) : o.def == t.def) return false;
            }
            return true;
        }
    }

    // Hurt after a bite: run from the nearest hostile.
    public class JobGiver_ChotrixFlee : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            CompChotrix c = pawn.TryGetComp<CompChotrix>();
            if (c == null || !RM_WarscarSettings.chotrixEnabled || !c.Fleeing || pawn.Downed) return null;
            Pawn threat = null; float bestD = 30f * 30f;
            IReadOnlyList<Pawn> all = pawn.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn o = all[i];
                if (o == pawn || o.Dead || o.Downed || !pawn.HostileTo(o)) continue;
                float d = (o.Position - pawn.Position).LengthHorizontalSquared;
                if (d < bestD) { bestD = d; threat = o; }
            }
            if (threat == null) return null;
            IntVec3 dest = CellFinderLoose.GetFleeDest(pawn, new List<Thing> { threat }, 24f);
            if (dest == pawn.Position) return null;
            Job j = JobMaker.MakeJob(JobDefOf.Flee, dest, threat);
            j.locomotionUrgency = LocomotionUrgency.Sprint;
            return j;
        }
    }

    // 1-2 per map, away from the map centre (where the player lands).
    public class GenStep_ChotrixOnMap : GenStep
    {
        public override int SeedPart { get { return 84921741; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_WarscarSettings.chotrixEnabled) return;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Chotrix");
            if (kind == null) return;
            int n = Mathf.Clamp(Mathf.RoundToInt(RM_WarscarSettings.chotrixPerMap), 0, 2);
            if (n == 2 && Rand.Bool) n = 1; // "one or two": half the maps get one
            for (int i = 0; i < n; i++)
            {
                IntVec3 cell;
                if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.Walkable(map) && (c - map.Center).LengthHorizontal > 30f, out cell)) return;
                GenSpawn.Spawn(PawnGenerator.GeneratePawn(kind, null), cell, map);
            }
        }
    }

    // Permanent cloak lacquer: still and unseen = invisible. Stateless, so a save/load cannot desync it
    // (the hediff itself is saved with the pawn; the comp re-evaluates every interval).
    public class CompProperties_LacquerCloak : CompProperties
    {
        public HediffDef hediff;
        public int checkIntervalTicks = 20;
        public CompProperties_LacquerCloak() { compClass = typeof(CompLacquerCloak); }
    }

    public class CompLacquerCloak : ThingComp
    {
        public CompProperties_LacquerCloak Props { get { return (CompProperties_LacquerCloak)props; } }
        private Pawn Wearer { get { Apparel a = parent as Apparel; return a == null ? null : a.Wearer; } }

        public override void CompTick()
        {
            base.CompTick();
            Pawn w = Wearer;
            if (w == null || !w.Spawned || !parent.IsHashIntervalTick(Props.checkIntervalTicks)) return;
            // DEEPFIRE_WORLD_LIGHT_1 (d): a pawn carrying a lit light (a deepfire glow, read from the shared light ledger)
            // cannot vanish, and one that starts glowing while hidden is revealed on the next check
            bool glowing = RM_WarscarSettings.lacquerDeniedWhileGlowing && LightLedger.CarriesLitLight(w);
            bool want = RM_WarscarSettings.lacquerCloakEnabled && !w.Downed && !w.Dead && !glowing && IsStill(w) && !Seen(w);
            Hediff h = w.health.hediffSet.GetFirstHediffOfDef(Props.hediff);
            if (want && h == null) w.health.AddHediff(HediffMaker.MakeHediff(Props.hediff, w));
            else if (!want && h != null) { w.GetInvisibilityComp()?.BecomeVisible(instant: false); w.health.RemoveHediff(h); }
        }

        public override void Notify_Unequipped(Pawn pawn)
        {
            base.Notify_Unequipped(pawn);
            if (pawn == null || pawn.health == null) return;
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(Props.hediff);
            if (h != null) { pawn.GetInvisibilityComp()?.BecomeVisible(instant: true); pawn.health.RemoveHediff(h); }
        }

        private static bool IsStill(Pawn w)
        {
            return (w.pather == null || !w.pather.Moving) && (w.stances == null || !w.stances.FullBodyBusy);
        }

        // Unseen = no awake hostile pawn with line of sight within the seen radius.
        private static bool Seen(Pawn w)
        {
            float r = RM_WarscarSettings.lacquerSeenRadius;
            IReadOnlyList<Pawn> all = w.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn o = all[i];
                if (o == w || o.Dead || o.Downed || !o.HostileTo(w) || o.Awake() == false) continue;
                if ((o.Position - w.Position).LengthHorizontalSquared > r * r) continue;
                if (GenSight.LineOfSight(o.Position, w.Position, w.Map)) return true;
            }
            return false;
        }
    }
}
