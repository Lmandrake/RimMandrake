using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.CrackedLands
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_GPT_ENRICHMENT_1 §5 + §6 — WHAT THE RECEDE LEAVES BEHIND.
    //
    // Called once per flood by RM_MapComponent_CanyonFlood.RecedeFlood with
    // the wetted footprint (both halves: walled cells and FlowWorks-raised
    // cells). Owns two short-lived things, each with its own clock and its
    // own Mod Settings toggle. (A third, THE MIGRANT SKY -- this biome's own fliers
    // flying in to feed on the carpet and out at the dry -- was CUT 2026-10-23 by the fluff review,
    // design/RimMandrake/fluff_cuts_2026-10-23.md.)
    //
    //   THE IRQIT CARPET (§5)  a bounded cohort of RM_Irqit on the wetted
    //     cells, each carrying RM_IrqitFloodBorn (the readable sign: the
    //     health tab says what it is and that it dies at the dry). At the dry
    //     — the same soakDecayDays the ground stays soaked — every survivor
    //     dies where it stands; the corpses ARE the windrows. Nothing
    //     vanishes. The "breeds once" half needs no simulation: the next
    //     flood's cohort is that generation, hatched from the clay.
    //
    //   FLOODLINE SALVAGE (§6, the scatter half only)  a disciplined handful
    //     of half-buried industrial components and slag on the wetted cells,
    //     spawned forbidden. Whatever is still lying unclaimed where it was
    //     exposed when the clock runs out is taken back by the mud, with a
    //     message saying so. A claim stake stands beside each piece while it
    //     is open, and on a chance per flood a rival crew comes for what is
    //     left (RM_ClaimCrew.cs, CRACKEDLANDS_SALVAGE_CLAIM_CREW_1).
    //
    //   THE BURIED WRECK  on a chance per flood, one half-buried wreck silhouette
    //     on the wetted cells, a real deconstructible wreck that lasts until
    //     the next recede, which takes it back (its description says so).
    // ════════════════════════════════════════════════════════════════════
    public class RM_FloodlineClaim : IExposable
    {
        public Thing piece;
        public IntVec3 cell;
        public Thing stake;

        public void ExposeData()
        {
            Scribe_References.Look(ref piece, "piece");
            Scribe_Values.Look(ref cell, "cell");
            Scribe_References.Look(ref stake, "stake");
        }
    }

    public class RM_MapComponent_RecedeAftermath : MapComponent
    {
        private List<Pawn> cohort = new List<Pawn>();
        private int cohortDieTick = -1;

        private List<RM_FloodlineClaim> salvage = new List<RM_FloodlineClaim>();
        private int salvageExpireTick = -1;

        private int crewArrivalTick = -1;
        private Lord crewLord;
        private Pawn crewTrader;
        private Thing crewProp;
        private int crewHeldAtArrival;

        private List<Thing> floodWrecks = new List<Thing>();

        public RM_MapComponent_RecedeAftermath(Map map) : base(map)
        {
        }

        // TUNED: one irqit per 8 wetted cells, capped by the setting — enough
        // to read as a carpet on a default flood (40–400 cells) without a
        // pawn-count spike. The "millions" are the art's job, not the tick's.

        // TUNED: 1–3 components + 1–3 slag chunks per flood — "loot tables need
        // discipline or the flood becomes a slot machine" (review §H).
        private static readonly IntRange ComponentCount = new IntRange(1, 3);
        private static readonly IntRange SlagCount = new IntRange(1, 3);

        // TUNED: how many wetted cells are tried as a wreck site before the flood gives up on leaving one.
        private const int WreckSiteTries = 60;

        public void OnRecede(List<IntVec3> wetted)
        {
            if (wetted == null || wetted.Count == 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            int dryTicks = RM_CanyonRulesKernel.DryTicks(RM_CrackedLandsSettings.soakDecayDays);
            TakeBackFloodWrecks();

            if (RM_CrackedLandsSettings.recedeFeastEnabled)
            {
                SpawnCohort(wetted, now + dryTicks);
            }
            if (RM_CrackedLandsSettings.floodlineSalvageEnabled)
            {
                SpawnSalvage(wetted, now + RM_CanyonRulesKernel.SalvageTicks(RM_CrackedLandsSettings.salvageDecayDays));
                if (crewArrivalTick < 0 && !CrewOnMap() && RM_ClaimKernel.CrewComes(RM_CrackedLandsSettings.claimCrewEnabled,
                    Rand.Value, RM_CrackedLandsSettings.claimCrewChance, OpenCount()))
                {
                    crewArrivalTick = now + Rand.RangeInclusive(RM_ClaimKernel.ArrivalDelayMinTicks, RM_ClaimKernel.ArrivalDelayMaxTicks);
                }
            }
            if (RM_CrackedLandsSettings.floodWrecksEnabled && Rand.Chance(RM_CrackedLandsSettings.floodWreckChance))
            {
                SpawnFloodWreck(wetted);
            }
        }

        private static bool GoodGround(IntVec3 c, Map map)
        {
            return c.InBounds(map) && c.Standable(map) && !c.Fogged(map)
                && map.terrainGrid.TerrainAt(c) is TerrainDef t && !t.IsWater;
        }

        private void SpawnCohort(List<IntVec3> wetted, int dieTick)
        {
            PawnKindDef kind = RM_CrackedLandsDefOf.RM_Irqit;
            int want = RM_CanyonRulesKernel.CohortWant(RM_CrackedLandsSettings.irqitCohortMax, wetted.Count);
            if (kind == null || want <= 0)
            {
                return;
            }
            List<IntVec3> pool = wetted.FindAll(c => GoodGround(c, map));
            int spawned = 0;
            for (int i = 0; i < want && pool.Count > 0; i++)
            {
                IntVec3 c = pool.RandomElement();
                Pawn p = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(p, c, map);
                p.health.AddHediff(RM_CrackedLandsDefOf.RM_IrqitFloodBorn);
                cohort.Add(p);
                spawned++;
            }
            if (spawned > 0)
            {
                cohortDieTick = dieTick;
                Messages.Message(
                    "The flood-touched mud is moving: an irqit carpet has hatched in the wet clay. It will be gone by the time the ground dries.",
                    new LookTargets(cohort[cohort.Count - 1]), MessageTypeDefOf.NeutralEvent);
            }
        }

        private void SpawnSalvage(List<IntVec3> wetted, int expireTick)
        {
            List<IntVec3> pool = wetted.FindAll(c => GoodGround(c, map) && c.GetFirstItem(map) == null);
            if (pool.Count == 0)
            {
                return;
            }
            int nComp = ComponentCount.RandomInRange;
            int nSlag = SlagCount.RandomInRange;
            for (int i = 0; i < nComp + nSlag && pool.Count > 0; i++)
            {
                IntVec3 c = pool.RandomElement();
                pool.Remove(c);
                Thing t = ThingMaker.MakeThing(i < nComp ? ThingDefOf.ComponentIndustrial : ThingDefOf.ChunkSlagSteel);
                GenSpawn.Spawn(t, c, map);
                t.SetForbidden(true, false);
                salvage.Add(new RM_FloodlineClaim { piece = t, cell = c });
            }
            salvageExpireTick = expireTick;
            if (RM_CrackedLandsSettings.claimStakesEnabled)
            {
                for (int i = 0; i < salvage.Count; i++)
                {
                    PlantStake(salvage[i]);
                }
            }
            if (salvage.Count > 0)
            {
                Messages.Message(
                    "The receding water has scoured wreckage out of the mud along the flood line, and old claim stakes with it. Unclaimed, the mud will take it back.",
                    new LookTargets(salvage[salvage.Count - 1].piece), MessageTypeDefOf.PositiveEvent);
            }
        }

        // One stake on a free cell touching the piece. No free cell: the piece stands unstaked rather than crowding anything.
        private void PlantStake(RM_FloodlineClaim claim)
        {
            if (claim.stake != null)
            {
                return;
            }
            foreach (IntVec3 offset in GenAdj.AdjacentCells)
            {
                IntVec3 c = claim.cell + offset;
                if (GoodGround(c, map) && c.GetFirstBuilding(map) == null && c.GetFirstItem(map) == null)
                {
                    claim.stake = GenSpawn.Spawn(RM_CrackedLandsDefOf.RM_ClaimStake, c, map);
                    return;
                }
            }
        }

        private bool IsOpen(RM_FloodlineClaim claim)
        {
            Thing t = claim.piece;
            return t != null && RM_ClaimKernel.Open(t.Spawned, t.Map == map, t.Position == claim.cell, t.IsForbidden(Faction.OfPlayer));
        }

        private bool IsStealable(RM_FloodlineClaim claim)
        {
            Thing t = claim.piece;
            return t != null && RM_ClaimKernel.Stealable(t.Spawned, t.Map == map, t.Position == claim.cell);
        }

        public int OpenCount()
        {
            return salvage.FindAll(IsOpen).Count;
        }

        public int StealableCount()
        {
            return salvage.FindAll(IsStealable).Count;
        }

        public Thing NearestPieceFor(Pawn pawn, bool stealing)
        {
            Thing best = null;
            float bestDist = float.MaxValue;
            for (int i = 0; i < salvage.Count; i++)
            {
                RM_FloodlineClaim claim = salvage[i];
                if (!(stealing ? IsStealable(claim) : IsOpen(claim)))
                {
                    continue;
                }
                float d = pawn.Position.DistanceToSquared(claim.cell);
                if (d < bestDist && pawn.CanReserveAndReach(claim.piece, PathEndMode.ClosestTouch, Danger.Deadly))
                {
                    best = claim.piece;
                    bestDist = d;
                }
            }
            return best;
        }

        // A stake stands while its piece is open: claimed, dug out, or reclaimed by the mud, it comes down.
        private void ClearDeadStakes()
        {
            for (int i = 0; i < salvage.Count; i++)
            {
                RM_FloodlineClaim claim = salvage[i];
                if (claim.stake != null && !IsOpen(claim))
                {
                    RemoveStake(claim);
                }
            }
        }

        private static void RemoveStake(RM_FloodlineClaim claim)
        {
            if (claim.stake != null && claim.stake.Spawned)
            {
                claim.stake.Destroy(DestroyMode.Vanish);
            }
            claim.stake = null;
        }

        private void SpawnFloodWreck(List<IntVec3> wetted)
        {
            ThingDef def = Rand.Bool ? RM_CrackedLandsDefOf.RM_CanyonWreckHull : RM_CrackedLandsDefOf.RM_CanyonWreckSpeeder;
            List<IntVec3> pool = wetted.InRandomOrder().Take(WreckSiteTries).ToList();
            foreach (IntVec3 c in pool)
            {
                CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, def.size);
                if (rect.Cells.All(x => GoodGround(x, map) && x.GetEdifice(map) == null && x.GetFirstItem(map) == null && x.GetFirstPawn(map) == null))
                {
                    Thing wreck = GenSpawn.Spawn(def, c, map);
                    floodWrecks.Add(wreck);
                    Messages.Message("The flood has rolled a wreck into the open, half buried on the flood line. The next flood will take it back.",
                        new LookTargets(wreck), MessageTypeDefOf.PositiveEvent);
                    return;
                }
            }
        }

        private void TakeBackFloodWrecks()
        {
            int taken = 0;
            for (int i = 0; i < floodWrecks.Count; i++)
            {
                Thing w = floodWrecks[i];
                if (w != null && w.Spawned)
                {
                    w.Destroy(DestroyMode.Vanish);
                    taken++;
                }
            }
            floodWrecks.Clear();
            if (taken > 0)
            {
                Messages.Message("The flood has taken back the wreck it left on the flood line.", MessageTypeDefOf.NeutralEvent);
            }
        }

        private bool CrewOnMap()
        {
            return crewLord != null && map.lordManager.lords.Contains(crewLord) && crewLord.ownedPawns.Count > 0;
        }

        private static bool Eligible(Faction f)
        {
            return !f.IsPlayer && !f.defeated && !f.temporary && !f.Hidden && f.def.humanlikeFaction && !f.HostileTo(Faction.OfPlayer);
        }

        private static Faction FirstOfDef(string defName, System.Func<Faction, bool> test)
        {
            return Find.FactionManager.AllFactionsListForReading.Find(f => f.def.defName == defName && test(f));
        }

        // The profile's first faction that is at peace with the player. None: nobody comes, and nothing says so, because
        // nothing happened. forceNeutral (debug only) makes the profile's first present faction neutral instead.
        public string SendCrew(bool forceNeutral = false)
        {
            RM_ClaimCrewProfileDef profile = RM_CrackedLandsDefOf.RM_ClaimCrew_Scavengers;
            if (OpenCount() == 0)
            {
                return "no open claim";
            }
            if (CrewOnMap())
            {
                return "crew already here";
            }
            string picked = RM_ClaimKernel.PickFaction(profile.factionDefs, n => FirstOfDef(n, Eligible) != null);
            Faction faction = picked == null ? null : FirstOfDef(picked, Eligible);
            if (faction == null && forceNeutral)
            {
                picked = RM_ClaimKernel.PickFaction(profile.factionDefs, n => FirstOfDef(n, f => !f.defeated) != null);
                faction = picked == null ? null : FirstOfDef(picked, f => !f.defeated);
                if (faction != null)
                {
                    faction.TryAffectGoodwillWith(Faction.OfPlayer, -faction.GoodwillWith(Faction.OfPlayer), false, false);
                }
            }
            if (faction == null)
            {
                return "no eligible faction";
            }
            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Neutral))
            {
                return "no entry cell";
            }
            List<Pawn> crew = new List<Pawn>();
            int n2 = Rand.RangeInclusive(RM_ClaimKernel.CrewMin, RM_ClaimKernel.CrewMax);
            for (int i = 0; i < n2; i++)
            {
                PawnKindDef kind = faction.RandomPawnKind();
                if (kind == null)
                {
                    break;
                }
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction, PawnGenerationContext.NonPlayer, map.Tile));
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(entry, map, 5), map);
                crew.Add(p);
            }
            if (crew.Count == 0)
            {
                return "faction has no pawn kind";
            }
            IntVec3 claim = ClaimCentre();
            crewLord = LordMaker.MakeNewLord(faction, new RM_LordJob_SalvageClaim(faction, claim, RM_ClaimKernel.StayTicks), map, crew);
            crewTrader = crew.Find(p => p.DevelopmentalStage.Adult()) ?? crew[0];
            OpenShop(crewTrader, profile.traderKind, faction);
            crewHeldAtArrival = CrewHeld();
            ThingDef prop = profile.campProp.NullOrEmpty() ? null : DefDatabase<ThingDef>.GetNamedSilentFail(profile.campProp);
            if (prop != null && CellFinder.TryFindRandomCellNear(claim, map, 8, c => PropFits(c, prop), out IntVec3 propCell))
            {
                crewProp = GenSpawn.Spawn(prop, propCell, map);
            }
            Find.LetterStack.ReceiveLetter(profile.arrivalLabel, string.Format(profile.arrivalText, faction.Name), LetterDefOf.NeutralEvent,
                new LookTargets(crew), faction);
            return "sent " + crew.Count + " of " + faction.def.defName;
        }

        private bool PropFits(IntVec3 c, ThingDef prop)
        {
            return GenAdj.OccupiedRect(c, Rot4.North, prop.size).Cells.All(x => GoodGround(x, map) && x.GetEdifice(map) == null
                && x.GetFirstItem(map) == null && x.GetFirstPawn(map) == null);
        }

        private IntVec3 ClaimCentre()
        {
            int x = 0, z = 0, count = 0;
            for (int i = 0; i < salvage.Count; i++)
            {
                if (IsOpen(salvage[i]))
                {
                    x += salvage[i].cell.x;
                    z += salvage[i].cell.z;
                    count++;
                }
            }
            IntVec3 mean = new IntVec3(x / count, 0, z / count);
            return CellFinder.TryFindRandomCellNear(mean, map, 6, c => c.Standable(map), out IntVec3 found) ? found : salvage.Find(IsOpen).cell;
        }

        // Vanilla's small-trader conversion (IncidentWorker_VisitorGroup) with our trader kind.
        private static void OpenShop(Pawn pawn, TraderKindDef kind, Faction faction)
        {
            pawn.mindState.wantsToTradeWithColony = true;
            PawnComponentsUtility.AddAndRemoveDynamicComponents(pawn, actAsIfSpawned: true);
            pawn.trader.traderKind = kind;
            pawn.inventory.DestroyAll();
            ThingSetMakerParams parms = default(ThingSetMakerParams);
            parms.traderDef = kind;
            parms.tile = pawn.Map.Tile;
            parms.makingFaction = faction;
            foreach (Thing item in ThingSetMakerDefOf.TraderStock.root.Generate(parms))
            {
                if (!pawn.inventory.innerContainer.TryAdd(item))
                {
                    item.Destroy();
                }
            }
        }

        // What a crew member digs out goes on the shop's shelf (the trader's own dig stays there); once they have gone, the
        // claim's props go with them.
        private void CrewTick()
        {
            if (!CrewOnMap())
            {
                crewLord = null;
                crewTrader = null;
                if (crewProp != null && crewProp.Spawned)
                {
                    crewProp.Destroy(DestroyMode.Vanish);
                }
                crewProp = null;
                return;
            }
            // A piece the player claims mid-dig stays his: the visitor stops. Hostile, they no longer care.
            if (!crewLord.faction.HostileTo(Faction.OfPlayer))
            {
                for (int i = 0; i < crewLord.ownedPawns.Count; i++)
                {
                    Pawn p = crewLord.ownedPawns[i];
                    Job job = p.CurJob;
                    if (job != null && job.def == JobDefOf.TakeInventory
                        && salvage.Find(c => c.piece == job.targetA.Thing) is RM_FloodlineClaim dug && !IsOpen(dug))
                    {
                        p.jobs.EndCurrentJob(JobCondition.InterruptForced);
                    }
                }
            }
            if (crewTrader == null || !crewTrader.Spawned || crewTrader.Dead || !crewLord.ownedPawns.Contains(crewTrader))
            {
                return;
            }
            List<Pawn> crew = crewLord.ownedPawns;
            for (int i = 0; i < crew.Count; i++)
            {
                ThingOwner stock = crew[i].inventory.innerContainer;
                for (int j = stock.Count - 1; j >= 0 && crew[i] != crewTrader; j--)
                {
                    if (IsSalvageDef(stock[j].def))
                    {
                        stock.TryTransferToContainer(stock[j], crewTrader.inventory.innerContainer);
                    }
                }
            }
        }

        private static bool IsSalvageDef(ThingDef def)
        {
            return def == ThingDefOf.ComponentIndustrial || def == ThingDefOf.ChunkSlagSteel;
        }

        // Pieces of salvage-def stock the crew holds. A taken piece can merge into a stack, so the count, not the Thing, is the read.
        private int CrewHeld()
        {
            int held = 0;
            List<Pawn> crew = crewLord.ownedPawns;
            for (int i = 0; i < crew.Count; i++)
            {
                ThingOwner stock = crew[i].inventory.innerContainer;
                for (int j = 0; j < stock.Count; j++)
                {
                    if (IsSalvageDef(stock[j].def))
                    {
                        held += stock[j].stackCount;
                    }
                }
            }
            return held;
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % 250 != 0)
            {
                return;
            }

            if (RM_CanyonRulesKernel.Due(cohortDieTick, now))
            {
                int died = 0;
                for (int i = 0; i < cohort.Count; i++)
                {
                    Pawn p = cohort[i];
                    if (p != null && p.Spawned && !p.Dead && p.Map == map)
                    {
                        p.Kill(null);
                        died++;
                    }
                }
                cohort.Clear();
                cohortDieTick = -1;
                if (died > 0)
                {
                    Messages.Message("The mud has stiffened. The irqit carpet has died where it stood, in windrows along the flood line.",
                        MessageTypeDefOf.NeutralEvent);
                }
            }

            CrewTick();
            ClearDeadStakes();
            if (RM_CanyonRulesKernel.Due(crewArrivalTick, now))
            {
                crewArrivalTick = -1;
                SendCrew();
            }

            if (RM_CanyonRulesKernel.Due(salvageExpireTick, now))
            {
                int taken = 0;
                for (int i = 0; i < salvage.Count; i++)
                {
                    // Only what still lies forbidden exactly where the mud
                    // exposed it — anything a pawn touched, claimed or moved
                    // is the player's now.
                    if (IsOpen(salvage[i]))
                    {
                        salvage[i].piece.Destroy(DestroyMode.Vanish);
                        taken++;
                    }
                    RemoveStake(salvage[i]);
                }
                salvage.Clear();
                salvageExpireTick = -1;
                if (taken > 0)
                {
                    Messages.Message("The mud has taken back the floodline salvage nobody claimed.", MessageTypeDefOf.NeutralEvent);
                }
            }
        }

        public string DebugStateReport()
        {
            return string.Format("cohort={0} cohortDieTick={1} salvage={2} salvageExpireTick={3} now={4} stakes={5} stakesBeside={6} open={7} floodWrecks={8}",
                cohort.Count, cohortDieTick, salvage.Count, salvageExpireTick, Find.TickManager.TicksGame,
                salvage.FindAll(c => c.stake != null && c.stake.Spawned).Count,
                salvage.FindAll(c => c.stake != null && c.stake.Spawned && c.stake.Position.AdjacentTo8WayOrInside(c.cell)).Count,
                OpenCount(), floodWrecks.FindAll(w => w != null && w.Spawned).Count);
        }

        public string DebugCrewReport()
        {
            bool here = CrewOnMap();
            int near = 0;
            if (here)
            {
                IntVec3 c = salvage.Count > 0 ? salvage[0].cell : crewLord.ownedPawns[0].Position;
                near = crewLord.ownedPawns.FindAll(p => p.Spawned && p.Position.InHorDistOf(c, 20f)).Count;
            }
            return string.Format("crew={0} crewArrivalTick={1} faction={2} goodwill={3} hostile={4} raid={5} lordJob={6} toil={7} duty={8} near={9} trader={10} canTrade={11} goods={12} heldGain={13} open={14} prop={15}",
                here ? crewLord.ownedPawns.Count : 0, crewArrivalTick,
                here ? crewLord.faction.def.defName : "none",
                here ? crewLord.faction.GoodwillWith(Faction.OfPlayer) : 0,
                here && crewLord.faction.HostileTo(Faction.OfPlayer),
                here && crewLord.LordJob is LordJob_AssaultColony,
                here ? crewLord.LordJob.GetType().Name : "none",
                here ? crewLord.CurLordToil.GetType().Name : "none",
                here ? (crewLord.ownedPawns[0].mindState.duty?.def?.defName ?? "none") : "none",
                near,
                crewTrader != null,
                crewTrader != null && crewTrader.CanTradeNow,
                crewTrader?.trader != null ? crewTrader.trader.Goods.Count() : 0,
                here ? CrewHeld() - crewHeldAtArrival : 0, OpenCount(), crewProp != null && crewProp.Spawned);
        }

        /// <summary>Debug: the production relation drop, so the lord's own trigger fires. Returns the kind it landed on.</summary>
        public string DebugCollapseRelations()
        {
            if (!CrewOnMap())
            {
                return "no crew";
            }
            Faction f = crewLord.faction;
            f.TryAffectGoodwillWith(Faction.OfPlayer, -200, false, false);
            return f.RelationKindWith(Faction.OfPlayer).ToString();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref cohort, "cohort", LookMode.Reference);
            Scribe_Values.Look(ref cohortDieTick, "cohortDieTick", -1);
            Scribe_Collections.Look(ref salvage, "claims", LookMode.Deep);
            Scribe_Values.Look(ref salvageExpireTick, "salvageExpireTick", -1);
            Scribe_Values.Look(ref crewArrivalTick, "crewArrivalTick", -1);
            Scribe_References.Look(ref crewLord, "crewLord");
            Scribe_References.Look(ref crewTrader, "crewTrader");
            Scribe_References.Look(ref crewProp, "crewProp");
            Scribe_Values.Look(ref crewHeldAtArrival, "crewHeldAtArrival");
            Scribe_Collections.Look(ref floodWrecks, "floodWrecks", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (cohort == null) cohort = new List<Pawn>();
                if (salvage == null) salvage = new List<RM_FloodlineClaim>();
                if (floodWrecks == null) floodWrecks = new List<Thing>();
                cohort.RemoveAll(p => p == null);
                floodWrecks.RemoveAll(w => w == null);
                // A reference that failed to resolve is a destroyed piece.
                foreach (RM_FloodlineClaim dead in salvage.FindAll(c => c != null && c.piece == null))
                {
                    RemoveStake(dead);
                }
                salvage.RemoveAll(c => c == null || c.piece == null);
            }
        }
    }
}
