using System;
using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LongShade
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_MIDDENS_DESIGN_1 — the lee-side middens.
    //
    // Owner rulings 2026-10-03 (question card, recorded on the item):
    //   * a midden is a HEAP that regrows over weeks and can be re-searched;
    //   * searching yields VANILLA items only (no sample item);
    //   * the vrekka is in and BUILDS the heaps — kill or drive them off and
    //     the middens stop regrowing.
    //
    // Shape copied from SHRUBLAND_SCRAPNEST_BIRDS_1 (SWBestiary's
    // CompScrapHoarder / JobGiver_HoardScrap): a BuildingNaturalBase heap no
    // colonist builds, a ThinkNode_JobGiver inserted at the vanilla
    // Animal_PreMain tag (no think-tree clone), the animal builds a heap by a
    // direct spawn when it has none in range. Searching copies Scarlands'
    // WorkGiver_DefuseOrdnance: a Command_Toggle on the thing + a
    // WorkGiver_Scanner + a wait-with-progress-bar JobDriver.
    //
    // REGROWTH IS THE VREKKA. There is no timer on the heap: a layer is added
    // only by a living builder-race animal tending it (RM_VrekkaTendMidden).
    // That makes "kill them and the middens stop" true by construction,
    // with nothing to keep in sync.
    //
    // All numbers are PROVISIONAL first values (CompProperties_RM_MiddenHeap
    // in Defs/ThingDefs_Buildings/RM_LongShade_Middens.xml carries them).
    // ════════════════════════════════════════════════════════════════════

    /// <summary>One weighted row of a midden's search table. Vanilla items only (ruled 2026-10-03).</summary>
    public class RM_MiddenYield
    {
        public ThingDef thing;
        public IntRange count = new IntRange(1, 1);
        public float weight = 1f;
    }

    public class CompProperties_RM_MiddenHeap : CompProperties
    {
        /// <summary>Race defNames that build and tend these heaps. Unloaded names are skipped.</summary>
        public List<string> builderRaces = new List<string>();

        public int maxLayers = 4;
        /// <summary>Layers a freshly built heap starts with (what the builder dragged there first).</summary>
        public int startLayers = 1;
        /// <summary>Layer progress one tend adds; a layer completes at 1.0.</summary>
        public float tendGain = 0.1f;
        /// <summary>Minimum ticks between two tends of the same heap.</summary>
        public int tendCooldownTicks = 30000;
        public int tendDurationTicks = 400;

        public int searchTicks = 900;
        public int rollsPerLayer = 2;
        public List<RM_MiddenYield> yields = new List<RM_MiddenYield>();

        public int maxHeapsPerMap = 6;
        public float minHeapSpacing = 16f;
        /// <summary>A heap further than this is not the animal's own; it builds one nearer.</summary>
        public float heapSearchRadius = 30f;
        public int buildRadius = 10;
        /// <summary>Middens sit in the lee: a new heap only goes where ShadeAt is at least this.</summary>
        public float minBuildShade = 0.5f;

        public CompProperties_RM_MiddenHeap()
        {
            compClass = typeof(RM_CompMiddenHeap);
        }

        private List<ThingDef> builderCache;

        public bool IsBuilder(ThingDef race)
        {
            if (builderCache == null)
            {
                builderCache = new List<ThingDef>();
                for (int i = 0; i < builderRaces.Count; i++)
                {
                    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(builderRaces[i]);
                    if (d != null) builderCache.Add(d);
                }
            }
            return race != null && builderCache.Contains(race);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef)) yield return e;
            if (yields.NullOrEmpty()) yield return "RM_CompMiddenHeap: empty yields table";
            if (maxLayers < 1) yield return "RM_CompMiddenHeap: maxLayers < 1";
        }
    }

    public class RM_CompMiddenHeap : ThingComp
    {
        public int layers;
        public float progress;
        public int lastTendTick = -999999;
        public bool searchWanted;

        public CompProperties_RM_MiddenHeap Props => (CompProperties_RM_MiddenHeap)props;

        public bool CanTendNow =>
            RM_LongShadeKernel.CanTendNow(layers, Props.maxLayers, Find.TickManager.TicksGame, lastTendTick, Props.tendCooldownTicks);

        public void Tend()
        {
            lastTendTick = Find.TickManager.TicksGame;
            RM_LongShadeKernel.Tend(ref layers, ref progress, Props.tendGain, Props.maxLayers);
        }

        public void Search(Pawn searcher)
        {
            Map map = parent.Map;
            IntVec3 at = parent.Position;
            int rolls = RM_LongShadeKernel.SearchRolls(layers, Props.rollsPerLayer);
            for (int i = 0; i < rolls; i++)
            {
                if (!Props.yields.TryRandomElementByWeight(y => y.weight, out RM_MiddenYield y) || y.thing == null) continue;
                foreach (int stack in RM_LongShadeKernel.StackSplit(y.count.RandomInRange, y.thing.stackLimit))
                {
                    Thing t = ThingMaker.MakeThing(y.thing);
                    t.stackCount = stack;
                    GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
                }
            }
            layers = 0;
            progress = 0f;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref layers, "rmMiddenLayers", 0);
            Scribe_Values.Look(ref progress, "rmMiddenProgress", 0f);
            Scribe_Values.Look(ref lastTendTick, "rmMiddenLastTend", -999999);
            Scribe_Values.Look(ref searchWanted, "rmMiddenSearchWanted", false);
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            sb.Append("Layers: ").Append(layers).Append(" / ").Append(Props.maxLayers);
            int since = Find.TickManager.TicksGame - lastTendTick;
            if (RM_LongShadeKernel.Untended(lastTendTick, Find.TickManager.TicksGame, GenDate.TicksPerDay))
            {
                sb.Append("\nUntended: nothing is adding to it.");
            }
            else
            {
                sb.Append("\nLast tended ").Append(since.ToStringTicksToPeriod()).Append(" ago.");
            }
            if (searchWanted) sb.Append("\nMarked for searching when stocked.");
            return sb.ToString();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            yield return new Command_Toggle
            {
                defaultLabel = "Search midden",
                defaultDesc = "A miner digs through the heap whenever it holds at least one layer, and takes "
                    + "what the wind and the vrekka piled there. Searching flattens it; it only builds back up "
                    + "while vrekka keep tending it.",
                icon = TexCommand.Attack,
                isActive = () => searchWanted,
                toggleAction = delegate { searchWanted = !searchWanted; }
            };
        }
    }

    [DefOf]
    public static class RM_LongShadeMiddenDefOf
    {
        public static ThingDef RM_LongShadeMidden;
        public static JobDef RM_VrekkaTendMidden;
        public static JobDef RM_SearchMidden;

        static RM_LongShadeMiddenDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_LongShadeMiddenDefOf));
        }
    }

    // ── the vrekka: build a heap, tend a heap ─────────────────────────────
    public class JobGiver_RM_VrekkaMidden : ThinkNode_JobGiver
    {
        public override float GetPriority(Pawn pawn)
        {
            return Eligible(pawn, out _) ? 5f : 0f;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!Eligible(pawn, out CompProperties_RM_MiddenHeap props)) return null;
            ThingDef heapDef = RM_LongShadeMiddenDefOf.RM_LongShadeMidden;
            List<Thing> heaps = pawn.Map.listerThings.ThingsOfDef(heapDef);
            var spawned = new List<Thing>(heaps.Count);
            var dist = new List<float>(heaps.Count);
            var tendable = new List<bool>(heaps.Count);
            for (int i = 0; i < heaps.Count; i++)
            {
                Thing h = heaps[i];
                if (!h.Spawned) continue;
                float d = h.Position.DistanceTo(pawn.Position);
                spawned.Add(h);
                dist.Add(d);
                // reachability is only asked of a heap that is in range and tendable (it is the costly test)
                RM_CompMiddenHeap c = d > props.heapSearchRadius ? null : h.TryGetComp<RM_CompMiddenHeap>();
                tendable.Add(c != null && c.CanTendNow && pawn.CanReach(h, PathEndMode.Touch, Danger.Some));
            }
            int pick = RM_LongShadeKernel.NearestTendable(dist, tendable, props.heapSearchRadius, out bool anyInRange);
            Thing best = pick >= 0 ? spawned[pick] : null;

            if (!anyInRange)
            {
                if (RM_LongShadeSettings.middenVrekkaBuildEnabled) TryBuildHeap(pawn, heapDef, props);
                return null;
            }
            if (best == null || !RM_LongShadeSettings.middenRegrowthEnabled) return null;
            return JobMaker.MakeJob(RM_LongShadeMiddenDefOf.RM_VrekkaTendMidden, best);
        }

        private static bool Eligible(Pawn pawn, out CompProperties_RM_MiddenHeap props)
        {
            props = null;
            if (!RM_LongShadeSettings.modEnabled) return false;
            if (!RM_LongShadeSettings.middenVrekkaBuildEnabled && !RM_LongShadeSettings.middenRegrowthEnabled) return false;
            if (pawn == null || pawn.Map == null || pawn.Dead || pawn.Downed || !pawn.Awake()) return false;
            props = RM_LongShadeMiddenDefOf.RM_LongShadeMidden?.GetCompProperties<CompProperties_RM_MiddenHeap>();
            if (props == null || !props.IsBuilder(pawn.def)) return false;
            if (pawn.mindState == null || pawn.mindState.anyCloseHostilesRecently) return false;
            Need_Food food = pawn.needs?.food;
            if (food != null && food.CurLevelPercentage < pawn.RaceProps.FoodLevelPercentageWantEat) return false;
            Need_Rest rest = pawn.needs?.rest;
            if (rest != null && rest.CurLevelPercentage < 0.4f) return false;
            return true;
        }

        private static void TryBuildHeap(Pawn pawn, ThingDef heapDef, CompProperties_RM_MiddenHeap props)
        {
            Map map = pawn.Map;
            List<Thing> existing = map.listerThings.ThingsOfDef(heapDef);
            if (!RM_LongShadeKernel.ShouldBuildHeap(false, existing.Count, props.maxHeapsPerMap)) return;
            RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid grid;
            try { grid = RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid.For(map); }
            catch (Exception e)
            {
                Log.WarningOnce("[RM LongShade] middens: shade grid unavailable: " + e.Message, 0x4D4944);
                return;
            }
            if (grid == null) return;

            bool Validator(IntVec3 c)
            {
                if (!c.InBounds(map) || !c.Standable(map) || c.Fogged(map)) return false;
                // Never inside the player's base, and never under a roof (a roof is the colony's shade, not a lee).
                if (map.areaManager.Home[c] || c.Roofed(map)) return false;
                if (c.GetEdifice(map) != null || c.GetFirstItem(map) != null) return false;
                if (grid.ShadeAt(c) < props.minBuildShade) return false;
                for (int i = 0; i < existing.Count; i++)
                {
                    if (!RM_LongShadeKernel.SpacingOk(existing[i].Position.DistanceTo(c), props.minHeapSpacing)) return false;
                }
                return pawn.CanReach(c, PathEndMode.OnCell, Danger.Some);
            }

            if (!CellFinder.TryFindRandomCellNear(pawn.Position, map, props.buildRadius, Validator, out IntVec3 cell)) return;
            Thing heap = GenSpawn.Spawn(heapDef, cell, map, WipeMode.Vanish);
            RM_CompMiddenHeap comp = heap.TryGetComp<RM_CompMiddenHeap>();
            if (comp != null)
            {
                comp.layers = RM_LongShadeKernel.ClampStartLayers(props.startLayers, props.maxLayers);
                comp.lastTendTick = Find.TickManager.TicksGame;
            }
        }
    }

    public class JobDriver_RM_VrekkaTendMidden : JobDriver
    {
        // A wild animal reserves nothing: a colonist's search must never be blocked by a vrekka.
        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            CompProperties_RM_MiddenHeap props = job.GetTarget(TargetIndex.A).Thing?.TryGetComp<RM_CompMiddenHeap>()?.Props;
            yield return Toils_General.Wait(props?.tendDurationTicks ?? 400, TargetIndex.A);
            Toil fin = ToilMaker.MakeToil("RM_VrekkaTendMidden_Add");
            fin.initAction = delegate
            {
                RM_CompMiddenHeap c = job.GetTarget(TargetIndex.A).Thing?.TryGetComp<RM_CompMiddenHeap>();
                if (c != null && c.parent.Spawned && c.CanTendNow) c.Tend();
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }
    }

    // ── the colonist: search a stocked heap ───────────────────────────────
    public class WorkGiver_RM_SearchMidden : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForDef(RM_LongShadeMiddenDefOf.RM_LongShadeMidden);
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RM_LongShadeSettings.modEnabled;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobOnThing(pawn, t, forced) != null;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_CompMiddenHeap c = t.TryGetComp<RM_CompMiddenHeap>();
            if (c == null || !c.searchWanted || c.layers < 1) return null;
            if (t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, -1, null, forced)) return null;
            return JobMaker.MakeJob(RM_LongShadeMiddenDefOf.RM_SearchMidden, t);
        }
    }

    public class JobDriver_RM_SearchMidden : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            CompProperties_RM_MiddenHeap props = job.GetTarget(TargetIndex.A).Thing?.TryGetComp<RM_CompMiddenHeap>()?.Props;
            yield return Toils_General.Wait(props?.searchTicks ?? 900, TargetIndex.A)
                .FailOnDespawnedNullOrForbidden(TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A);
            Toil fin = ToilMaker.MakeToil("RM_SearchMidden_Take");
            fin.initAction = delegate
            {
                RM_CompMiddenHeap c = job.GetTarget(TargetIndex.A).Thing?.TryGetComp<RM_CompMiddenHeap>();
                if (c == null || !c.parent.Spawned || c.layers < 1) return;
                c.Search(pawn);
                pawn.skills?.Learn(SkillDefOf.Mining, 100f);
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }
    }
}
