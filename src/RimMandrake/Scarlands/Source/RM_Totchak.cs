using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_TOTCHAK_WAKES_1. The totchak sleeps in the Last Line posing as a wall segment (stock dormancy),
    // wakes when the ground around it is demolished, eats ruin walls first then player walls, and after its
    // grazing days walks to another wall line and lies down again.
    public class CompProperties_Totchak : CompProperties
    {
        public int checkIntervalTicks = 60;
        public CompProperties_Totchak() { compClass = typeof(CompTotchak); }
    }

    public class CompTotchak : ThingComp
    {
        public static readonly List<CompTotchak> All = new List<CompTotchak>();
        private bool announced;

        public CompProperties_Totchak Props { get { return (CompProperties_Totchak)props; } }
        public CompCanBeDormant Dormant { get { return parent.GetComp<CompCanBeDormant>(); } }
        public bool IsAsleep { get { CompCanBeDormant d = Dormant; return d != null && !d.Awake; } }

        public override void PostExposeData() { base.PostExposeData(); Scribe_Values.Look(ref announced, "announced", false); }
        public override void PostSpawnSetup(bool respawningAfterLoad) { base.PostSpawnSetup(respawningAfterLoad); if (!All.Contains(this)) All.Add(this); }
        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish) { base.PostDeSpawn(map, mode); All.Remove(this); }

        public override string CompInspectStringExtra()
        {
            return IsAsleep ? "Part of the Last Line. It is breathing, slowly." : null;
        }

        // The waking letter fires for ANY wake (demolition, damage, a nearby build), once per waking.
        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned || !parent.IsHashIntervalTick(Props.checkIntervalTicks)) return;
            CompCanBeDormant d = Dormant;
            if (d == null) return;
            // Switched off while awake (announced or not): back to sleep, the same state a disabled waking gets.
            if (d.Awake && !RM_WarscarSettings.totchakEnabled) { d.ToSleep(); announced = false; return; }
            if (d.Awake && !announced)
            {
                announced = true;
                if (!RM_WarscarSettings.totchakEnabled) { d.ToSleep(); announced = false; return; }
                Find.LetterStack.ReceiveLetter("A wall stood up",
                    "Part of the Last Line just stood up.", LetterDefOf.ThreatSmall, new LookTargets(parent));
            }
            else if (!d.Awake) announced = false;
        }

        public int AwakeTicks()
        {
            CompCanBeDormant d = Dormant;
            if (d == null || !d.Awake || d.wokeUpTick == int.MinValue) return 0;
            return Find.TickManager.TicksGame - d.wokeUpTick;
        }

        public bool ShouldLieDown()
        {
            return AwakeTicks() > RM_WarscarSettings.totchakGrazeDays * 60000f;
        }

        // Called by the demolition postfixes. Empty-registry fast path first: explosions fire constantly.
        public static void Demolition(Map map, IntVec3 pos)
        {
            if (All.Count == 0 || map == null || !RM_WarscarSettings.totchakEnabled) return;
            float r = RM_WarscarSettings.totchakWakeRadius;
            for (int i = 0; i < All.Count; i++)
            {
                CompTotchak c = All[i];
                if (c.parent.Map != map || !c.IsAsleep) continue;
                if (c.parent.Position.DistanceTo(pos) <= r) c.Dormant.WakeUp();
            }
        }

        public static bool IsWall(Thing t)
        {
            return t is Building && t.def.graphicData != null && (t.def.graphicData.linkFlags & LinkFlags.Wall) != 0
                   && t.def.passability == Traversability.Impassable;
        }
    }

    // RM_ChotrixPatches already runs PatchAll over this whole assembly. A second PatchAll under another Harmony id
    // applied every [HarmonyPatch] twice (Harmony dedupes only per owner): the glower damage prefix compounded to
    // x0.25 and the screened inspect line printed twice.
    public static class RM_TotchakPatches
    {
    }

    [HarmonyPatch(typeof(Mineable), "DestroyMined")]
    public static class Patch_Mineable_DestroyMined
    {
        public static void Prefix(Mineable __instance)
        {
            if (CompTotchak.All.Count == 0) return;
            CompTotchak.Demolition(__instance.Map, __instance.Position);
        }
    }

    [HarmonyPatch(typeof(GenExplosion), "DoExplosion")]
    public static class Patch_GenExplosion_DoExplosion
    {
        public static void Prefix(IntVec3 center, Map map)
        {
            if (CompTotchak.All.Count == 0) return;
            CompTotchak.Demolition(map, center);
        }
    }

    [HarmonyPatch(typeof(Thing), "Destroy")]
    public static class Patch_Thing_Destroy
    {
        public static void Prefix(Thing __instance, DestroyMode mode)
        {
            if (CompTotchak.All.Count == 0 || mode != DestroyMode.Deconstruct) return;
            CompTotchak.Demolition(__instance.MapHeld, __instance.PositionHeld);
        }
    }

    // Wall choice: ruin walls (no faction, weight 4) before player walls (weight 1) when both reachable.
    public class JobGiver_TotchakGnaw : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            CompTotchak c = pawn.TryGetComp<CompTotchak>();
            if (c == null || !RM_WarscarSettings.totchakEnabled || pawn.Downed || pawn.InMentalState || c.IsAsleep) return null;
            Thing wall = FindWall(pawn, false) ?? (RM_WarscarSettings.totchakEatsPlayerWalls ? FindWall(pawn, true) : null);
            return wall == null ? null : JobMaker.MakeJob(RM_TotchakDefOf.RM_TotchakGnaw, wall);
        }

        public static Thing FindWall(Pawn pawn, bool player)
        {
            Thing best = null; float bestD = 45f * 45f;
            List<Thing> all = pawn.Map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            for (int i = 0; i < all.Count; i++)
            {
                Thing t = all[i];
                if (!CompTotchak.IsWall(t)) continue;
                if (player ? t.Faction != Faction.OfPlayer : t.Faction != null) continue;
                float d = (t.Position - pawn.Position).LengthHorizontalSquared;
                if (d >= bestD || !pawn.CanReach(t, PathEndMode.Touch, Danger.Deadly)) continue;
                best = t; bestD = d;
            }
            return best;
        }
    }

    [DefOf]
    public static class RM_TotchakDefOf
    {
        public static JobDef RM_TotchakGnaw;
        public static JobDef RM_TotchakLieDown;
        static RM_TotchakDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_TotchakDefOf)); }
    }

    public class JobDriver_TotchakGnaw : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) { return true; }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !RM_WarscarSettings.totchakEnabled);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil bite = new Toil();
            bite.defaultCompleteMode = ToilCompleteMode.Never;
            bite.tickAction = delegate
            {
                if (pawn.IsHashIntervalTick(60)) Bite(TargetThingA);
                if (TargetThingA == null || TargetThingA.Destroyed) ReadyForNextToil();
            };
            yield return bite;
        }

        private void Bite(Thing wall)
        {
            if (wall == null || wall.Destroyed) return;
            float dmg = 14f * pawn.BodySize * RM_WarscarSettings.totchakBiteScale;
            IntVec3 pos = wall.Position; Map map = wall.Map;
            float hpBefore = wall.HitPoints;
            wall.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg, 0f, -1f, pawn));
            // Nutrition from the wall's stuff mass, in proportion to the bite taken.
            float mass = wall.GetStatValue(StatDefOf.Mass, true);
            if (pawn.needs != null && pawn.needs.food != null)
                pawn.needs.food.CurLevel += Mathf.Clamp(mass * 0.002f * (Mathf.Min(dmg, hpBefore) / Mathf.Max(1f, wall.MaxHitPoints)) * 50f, 0f, 0.05f);
            if (wall.Destroyed && map != null)
            {
                ThingDef slag = ThingDef.Named("ChunkSlagSteel");   // the readable sign of a gnawed wall
                Thing chunk = ThingMaker.MakeThing(slag);
                GenPlace.TryPlaceThing(chunk, pos, map, ThingPlaceMode.Near);
            }
        }
    }

    // After its grazing days: walk to a wall line elsewhere and go dormant there.
    public class JobGiver_TotchakLieDown : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            CompTotchak c = pawn.TryGetComp<CompTotchak>();
            if (c == null) return null;
            if (c.IsAsleep)   // a dormant pawn needs the stock sleep job to stand still
            {
                Job sleep = JobMaker.MakeJob(JobDefOf.Wait_AsleepDormancy, pawn.Position);
                sleep.forceSleep = true;
                return sleep;
            }
            if (pawn.Downed || pawn.InMentalState || !c.ShouldLieDown()) return null;
            IntVec3 cell = FindLieDownCell(pawn);
            return cell.IsValid ? JobMaker.MakeJob(RM_TotchakDefOf.RM_TotchakLieDown, cell) : null;
        }

        private static IntVec3 FindLieDownCell(Pawn pawn)
        {
            Map map = pawn.Map; IntVec3 best = IntVec3.Invalid; float bestD = 1e9f;
            List<Thing> all = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            for (int i = 0; i < all.Count; i++)
            {
                Thing t = all[i];
                if (!CompTotchak.IsWall(t) || t.Faction != null) continue;
                float d = (t.Position - pawn.Position).LengthHorizontalSquared;
                if (d < 15f * 15f || d > 80f * 80f || d >= bestD) continue;   // elsewhere, not here
                for (int k = 0; k < 4; k++)
                {
                    IntVec3 n = t.Position + GenAdj.CardinalDirections[k];
                    if (n.InBounds(map) && n.Standable(map) && pawn.CanReach(n, PathEndMode.OnCell, Danger.Deadly)) { best = n; bestD = d; break; }
                }
            }
            return best;
        }
    }

    public class JobDriver_TotchakLieDown : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) { return true; }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);
            Toil lie = new Toil();
            lie.defaultCompleteMode = ToilCompleteMode.Instant;
            lie.initAction = delegate
            {
                CompCanBeDormant d = pawn.TryGetComp<CompCanBeDormant>();
                if (d != null) d.ToSleep();
            };
            yield return lie;
        }
    }

    // GenStep: find a straight run of fortified wall, remove three cells, put the dormant totchak in the gap.
    public class GenStep_TotchakInWall : GenStep
    {
        public override int SeedPart { get { return 84921733; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_WarscarSettings.totchakEnabled) return;
            ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail("AncientFortifiedWall");
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Totchak");
            if (wallDef == null || kind == null) return;
            List<Thing> walls = map.listerThings.ThingsOfDef(wallDef);
            List<IntVec3> centers = new List<IntVec3>(); List<IntVec2> axes = new List<IntVec2>();
            for (int i = 0; i < walls.Count; i++)
            {
                IntVec3 p = walls[i].Position;
                if (Run(map, wallDef, p, 1, 0)) { centers.Add(p + new IntVec3(1, 0, 0)); axes.Add(new IntVec2(1, 0)); }
                if (Run(map, wallDef, p, 0, 1)) { centers.Add(p + new IntVec3(0, 0, 1)); axes.Add(new IntVec2(0, 1)); }
            }
            if (centers.Count == 0) return;
            int pick = Rand.Range(0, centers.Count);
            IntVec3 c = centers[pick]; IntVec2 a = axes[pick];
            for (int k = -1; k <= 1; k++)
            {
                IntVec3 cell = c + new IntVec3(a.x * k, 0, a.z * k);
                Building b = cell.GetEdifice(map);
                if (b != null && b.def == wallDef) b.Destroy(DestroyMode.Vanish);
            }
            Pawn p2 = PawnGenerator.GeneratePawn(kind, null);
            GenSpawn.Spawn(p2, c, map);
            Job sleep = JobMaker.MakeJob(JobDefOf.Wait_AsleepDormancy, c);
            sleep.forceSleep = true;
            p2.jobs.StartJob(sleep, JobCondition.InterruptForced);
        }

        private static bool Run(Map map, ThingDef wallDef, IntVec3 p, int dx, int dz)
        {
            for (int k = 0; k < 3; k++)
            {
                IntVec3 c = new IntVec3(p.x + dx * k, 0, p.z + dz * k);
                if (!c.InBounds(map)) return false;
                Building b = c.GetEdifice(map);
                if (b == null || b.def != wallDef) return false;
            }
            return true;
        }
    }
}
