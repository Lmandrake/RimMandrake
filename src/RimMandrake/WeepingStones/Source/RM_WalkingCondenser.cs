using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
    // WEEPINGSTONES_WALKING_CONDENSER_1. The oldest gorrask carries a running machine grown into its shell.
    // It settles for a season; while settled a pool grows round it (a ring of WaterShallow, original terrain
    // remembered per cell) and the truce field is rebuilt so IsTruceWater holds there. When it moves on the pool
    // dries back over days, with a letter. Vanilla seasons only (quadrum = 15 days by default); no new heat or weather.

    public class CompProperties_WalkingCondenser : CompProperties
    {
        public int maxRadius = 5;
        public float growDays = 3f;   // days for the ring to reach maxRadius
        public float dryDays = 4f;    // days for the pool to dry back; never instant
        public CompProperties_WalkingCondenser() { compClass = typeof(RM_CompWalkingCondenser); }
    }

    public class RM_CondenserWorld : WorldComponent
    {
        public bool spawned;     // one per world
        public bool ended;       // machine cut out: the moving oasis is over for good
        public int buyerPoolUntilTick = -1;
        public Faction buyer;
        // WEEPINGSTONES_CONDENSER_QUESTS_1: the quest holding the crab (-1 none), whether a quest has settled its fate,
        // and who took it to their arena.
        public int claimQuestId = -1;
        public bool questsSettled;
        public Faction capturedBy;

        public RM_CondenserWorld(World w) : base(w) { }

        public static RM_CondenserWorld Get() { return Find.World?.GetComponent<RM_CondenserWorld>(); }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref spawned, "spawned");
            Scribe_Values.Look(ref ended, "ended");
            Scribe_Values.Look(ref buyerPoolUntilTick, "buyerPoolUntilTick", -1);
            Scribe_References.Look(ref buyer, "buyer");
            Scribe_Values.Look(ref claimQuestId, "claimQuestId", -1);
            Scribe_Values.Look(ref questsSettled, "questsSettled");
            Scribe_References.Look(ref capturedBy, "capturedBy");
        }
    }

    // Spawns the one condenser gorrask on a Weeping Stones map, once per world.
    public class RM_MapComponent_CondenserSpawner : MapComponent
    {
        public RM_MapComponent_CondenserSpawner(Map map) : base(map) { }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            if (!RM_WeepingStonesSettings.condenserEnabled) return;
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            if (w == null || w.spawned || w.ended) return;
            if (map.Biome == null || map.Biome.defName != "RM_WeepingStones") return;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_GorraskCondenser");
            if (kind == null) return;
            IntVec3 cell;
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 30,
                    c => c.Standable(map) && !c.Fogged(map) && c.GetTerrain(map).passability == Traversability.Standable, out cell))
                return;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, -1,
                forceGenerateNewPawn: true));
            GenSpawn.Spawn(p, cell, map);
            w.spawned = true;
        }
    }

    public enum RM_CondenserPhase : byte { Settled, Waiting, Walking, Gone }

    public class RM_CompWalkingCondenser : ThingComp
    {
        public RM_CondenserPhase phase = RM_CondenserPhase.Settled;
        public int phaseStartTick = -1;
        public int settleTick = -1;
        public int poolRadius = 0;
        public bool drying;
        public int dryStartTick;
        public IntVec3 target = IntVec3.Invalid;
        public Dictionary<IntVec3, string> poolCells = new Dictionary<IntVec3, string>();
        private List<IntVec3> _k; private List<string> _v;

        public CompProperties_WalkingCondenser Props => (CompProperties_WalkingCondenser)props;
        private Pawn Crab => parent as Pawn;
        private static int SeasonTicks => Mathf.RoundToInt(RM_WeepingStonesSettings.condenserSeasonDays * GenDate.TicksPerDay);

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            if (!respawningAfterLoad && settleTick < 0) { settleTick = Find.TickManager.TicksGame; }
        }

        // A Pawn ticks Normal (never Rare), so gate a 250-tick cadence by hand.
        public override void CompTick()
        {
            if (!parent.IsHashIntervalTick(250)) return;
            Pawn crab = Crab;
            if (crab == null || !crab.Spawned || crab.Dead || crab.Map == null) return;
            if (!RM_WeepingStonesSettings.condenserEnabled) { if (poolCells.Count > 0) StartDrying(crab, silent: true); StepDrying(crab); return; }
            int now = Find.TickManager.TicksGame;
            switch (phase)
            {
                case RM_CondenserPhase.Settled:
                    GrowPool(crab);
                    if (now - settleTick >= SeasonTicks) BeginWaiting(crab, now);
                    break;
                case RM_CondenserPhase.Waiting:
                    // one day's grace for the player to choose; the pool starts drying as it prepares to move
                    if (now - phaseStartTick >= GenDate.TicksPerDay) BeginWalking(crab);
                    break;
                case RM_CondenserPhase.Walking:
                    StepDrying(crab);
                    if (!target.IsValid || crab.Position.DistanceTo(target) < 3f || now - phaseStartTick > 3 * GenDate.TicksPerDay)
                    {
                        phase = RM_CondenserPhase.Settled; settleTick = now; poolRadius = 0; drying = false;
                    }
                    else if (crab.CurJob == null || crab.CurJob.def != JobDefOf.Goto)
                    {
                        crab.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Goto, target), JobCondition.InterruptForced);
                    }
                    break;
            }
            if (drying && phase != RM_CondenserPhase.Walking) StepDrying(crab);
        }

        // --- pool ----------------------------------------------------------------------------------------
        private void GrowPool(Pawn crab)
        {
            int max = Props.maxRadius;
            if (poolRadius >= max) return;
            // CompTickRare is 250 ticks; growDays*60000/250 steps to cover max radius
            float stepsTotal = Props.growDays * GenDate.TicksPerDay / 250f;
            float perStep = max / Mathf.Max(1f, stepsTotal);
            poolRadius = Mathf.Min(max, Mathf.Max(poolRadius, 1) + (Rand.Chance(perStep % 1f) ? 1 : 0) + Mathf.FloorToInt(perStep));
            Map map = crab.Map;
            TerrainDef water = TerrainDefOf.WaterShallow;
            bool changed = false;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(crab.Position, poolRadius, true))
            {
                if (!c.InBounds(map) || poolCells.ContainsKey(c)) continue;
                TerrainDef cur = map.terrainGrid.TerrainAt(c);
                if (cur == null || cur.IsWater || cur.passability == Traversability.Impassable) continue;
                if (c.GetEdifice(map) != null) continue;
                poolCells[c] = cur.defName;
                map.terrainGrid.SetTerrain(c, water);
                changed = true;
            }
            if (changed) RebuildTruce(map);
        }

        private void StartDrying(Pawn crab, bool silent)
        {
            if (drying || poolCells.Count == 0) return;
            drying = true; dryStartTick = Find.TickManager.TicksGame;
            if (!silent)
                Find.LetterStack.ReceiveLetter("RM_CondenserDryingLabel".Translate(),
                    "RM_CondenserDryingText".Translate(), LetterDefOf.NeutralEvent, new LookTargets(crab));
        }

        private void StepDrying(Pawn crab)
        {
            if (!drying || poolCells.Count == 0 || crab?.Map == null) { if (poolCells.Count == 0) drying = false; return; }
            Map map = crab.Map;
            float stepsTotal = Props.dryDays * GenDate.TicksPerDay / 250f;
            int n = Mathf.Max(1, Mathf.CeilToInt(poolCells.Count / Mathf.Max(1f, stepsTotal)));
            // dry the outermost cells first
            foreach (IntVec3 c in poolCells.Keys.OrderByDescending(k => k.DistanceToSquared(crab.Position)).Take(n).ToList())
            {
                RestoreCell(map, c);
            }
            RebuildTruce(map);
            if (poolCells.Count == 0) drying = false;
        }

        private void RestoreCell(Map map, IntVec3 c)
        {
            if (poolCells.TryGetValue(c, out string orig))
            {
                TerrainDef td = DefDatabase<TerrainDef>.GetNamedSilentFail(orig);
                if (td != null && c.InBounds(map)) map.terrainGrid.SetTerrain(c, td);
                poolCells.Remove(c);
            }
        }

        public void DryAllNow(Map map)
        {
            foreach (IntVec3 c in poolCells.Keys.ToList()) RestoreCell(map, c);
            RebuildTruce(map);
        }

        private static void RebuildTruce(Map map)
        {
            // IsTruceWater scans terrain once at FinalizeInit; the pool moves, so rebuild the field.
            map.GetComponent<RimMandrake.EnvironmentalHazards.RM_MapComponent_WaterTruce>()?.Rebuild();
        }

        // --- seasonal move ----------------------------------------------------------------------------------
        private void BeginWaiting(Pawn crab, int now)
        {
            phase = RM_CondenserPhase.Waiting; phaseStartTick = now;
            target = IntVec3.Invalid;
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            ChoiceLetter letter = (ChoiceLetter)LetterMaker.MakeLetter(DefDatabase<LetterDef>.GetNamed("RM_CondenserChoiceLetter"));
            RM_ChoiceLetter_Condenser l = letter as RM_ChoiceLetter_Condenser;
            if (l != null)
            {
                l.crab = crab;
                l.Label = "RM_CondenserStirsLabel".Translate();
                l.Text = "RM_CondenserStirsText".Translate();
                l.lookTargets = new LookTargets(crab);
                l.StartTimeout(GenDate.TicksPerDay);
                Find.LetterStack.ReceiveLetter(l);
            }
            StartDrying(crab, silent: false);
        }

        private void BeginWalking(Pawn crab)
        {
            phase = RM_CondenserPhase.Walking; phaseStartTick = Find.TickManager.TicksGame;
            if (!target.IsValid) target = PickRandomSite(crab);
            if (target.IsValid)
                crab.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Goto, target), JobCondition.InterruptForced);
            else { phase = RM_CondenserPhase.Settled; settleTick = Find.TickManager.TicksGame; poolRadius = 0; }
        }

        private IntVec3 PickRandomSite(Pawn crab)
        {
            Map map = crab.Map;
            for (int i = 0; i < 40; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.DistanceTo(crab.Position) < 25f || !c.Standable(map) || c.GetTerrain(map).IsWater) continue;
                if (!map.reachability.CanReach(crab.Position, c, PathEndMode.OnCell, TraverseParms.For(crab))) continue;
                return c;
            }
            return IntVec3.Invalid;
        }

        // spot nearest the player's home area where the crab can stand and reach
        public IntVec3 PickSiteOnPlayerLand(Pawn crab)
        {
            Map map = crab.Map;
            IntVec3 home = IntVec3.Invalid;
            if (map.areaManager.Home != null && map.areaManager.Home.TrueCount > 0)
                home = map.areaManager.Home.ActiveCells.RandomElement();
            else
            {
                Pawn col = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
                if (col != null) home = col.Position;
            }
            if (!home.IsValid) return IntVec3.Invalid;
            IntVec3 best = IntVec3.Invalid;
            if (CellFinder.TryFindRandomCellNear(home, map, 8,
                    c => c.Standable(map) && !c.GetTerrain(map).IsWater && c.GetEdifice(map) == null
                         && map.reachability.CanReach(crab.Position, c, PathEndMode.OnCell, TraverseParms.For(crab)), out best))
                return best;
            return IntVec3.Invalid;
        }

        // --- the three choices (all resolve through the letter) ----------------------------------------------
        public void Choice_Guide()
        {
            Pawn crab = Crab; if (crab == null || !crab.Spawned) return;
            IntVec3 c = PickSiteOnPlayerLand(crab);
            if (!c.IsValid)
            {
                Messages.Message("RM_CondenserGuideNoSite".Translate(), crab, MessageTypeDefOf.RejectInput, false);
                return;
            }
            target = c;
            Find.LetterStack.ReceiveLetter("RM_CondenserGuideLabel".Translate(),
                "RM_CondenserGuideText".Translate(), LetterDefOf.PositiveEvent, new LookTargets(c, crab.Map));
        }

        public void Choice_Sell()
        {
            Pawn crab = Crab; if (crab == null) return;
            Faction buyer = Find.FactionManager.AllFactionsVisible
                .Where(f => !f.IsPlayer && !f.defeated && !f.HostileTo(Faction.OfPlayer) && f.def.humanlikeFaction)
                .OrderByDescending(f => f.PlayerGoodwill).FirstOrDefault();
            if (buyer == null)
            {
                Messages.Message("RM_CondenserSellNoBuyer".Translate(), crab, MessageTypeDefOf.RejectInput, false);
                return;
            }
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            if (w != null) { w.buyer = buyer; w.buyerPoolUntilTick = Find.TickManager.TicksGame + SeasonTicks; }
            int payout = 1500;
            Map home = Find.AnyPlayerHomeMap;
            if (home != null)
            {
                Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver); silver.stackCount = payout;
                DropPodUtility.DropThingsNear(DropCellFinder.TradeDropSpot(home), home, new List<Thing> { silver });
            }
            buyer.TryAffectGoodwillWith(Faction.OfPlayer, 10, true, true, null);
            Find.LetterStack.ReceiveLetter("RM_CondenserSellLabel".Translate(),
                "RM_CondenserSellText".Translate(buyer.Name, payout), LetterDefOf.PositiveEvent);
        }

        public void Choice_Cut()
        {
            Pawn crab = Crab; if (crab == null || !crab.Spawned) return;
            Map map = crab.Map; IntVec3 pos = crab.Position;
            DryAllNow(map);
            ThingDef plantDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_AncientCondenserPlant");
            RM_CondenserWorld w = RM_CondenserWorld.Get(); if (w != null) w.ended = true;
            if (plantDef != null)
            {
                Thing built = ThingMaker.MakeThing(plantDef, GenStuff.DefaultStuffFor(plantDef));
                Thing mini = built.def.Minifiable ? (Thing)MinifyUtility.MakeMinified(built) : built;
                GenPlace.TryPlaceThing(mini, pos, map, ThingPlaceMode.Near);
            }
            crab.Kill(null);
            Find.LetterStack.ReceiveLetter("RM_CondenserCutLabel".Translate(),
                "RM_CondenserCutText".Translate(), LetterDefOf.NegativeEvent, new LookTargets(pos, map));
        }

        // The crab dying by any other hand ends the oasis too, with a sign.
        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            if (poolCells.Count > 0 && previousMap != null) DryAllNow(previousMap);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WeepingStonesSettings.condenserEnabled) return null;
            switch (phase)
            {
                case RM_CondenserPhase.Settled: return "RM_CondenserInspectSettled".Translate(poolCells.Count);
                case RM_CondenserPhase.Waiting: return "RM_CondenserInspectWaiting".Translate();
                default: return "RM_CondenserInspectWalking".Translate();
            }
        }

        public override void PostExposeData()
        {
            Scribe_Values.Look(ref phase, "phase", RM_CondenserPhase.Settled);
            Scribe_Values.Look(ref phaseStartTick, "phaseStartTick", -1);
            Scribe_Values.Look(ref settleTick, "settleTick", -1);
            Scribe_Values.Look(ref poolRadius, "poolRadius");
            Scribe_Values.Look(ref drying, "drying");
            Scribe_Values.Look(ref dryStartTick, "dryStartTick");
            Scribe_Values.Look(ref target, "target", IntVec3.Invalid);
            Scribe_Collections.Look(ref poolCells, "poolCells", LookMode.Value, LookMode.Value, ref _k, ref _v);
            if (poolCells == null) poolCells = new Dictionary<IntVec3, string>();
        }
    }

    public class RM_ChoiceLetter_Condenser : ChoiceLetter
    {
        public Pawn crab;

        public override IEnumerable<DiaOption> Choices
        {
            get
            {
                RM_CompWalkingCondenser comp = crab?.TryGetComp<RM_CompWalkingCondenser>();
                if (comp != null && crab.Spawned && !crab.Dead)
                {
                    yield return new DiaOption("RM_CondenserOptGuide".Translate()) { action = comp.Choice_Guide, resolveTree = true };
                    yield return new DiaOption("RM_CondenserOptSell".Translate()) { action = comp.Choice_Sell, resolveTree = true };
                    yield return new DiaOption("RM_CondenserOptCut".Translate()) { action = comp.Choice_Cut, resolveTree = true };
                }
                yield return Option_Close;
            }
        }

        public override bool CanDismissWithRightClick => false;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref crab, "crab");
        }
    }
}
