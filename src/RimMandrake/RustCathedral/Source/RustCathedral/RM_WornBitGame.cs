using System.Collections.Generic;
using System.Linq;
using RimMandrake.RustCathedral.Hum;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.RustCathedral
{
    /// <summary>The arc's world state: one drill head out at a time. A GameComponent because a QuestPart has no tick and the
    /// freed hulk outlives the quest.</summary>
    public class RM_WornBitGame : GameComponent
    {
        private const int PollTicks = 250;

        public Pawn hulk;
        public Quest quest;
        public RM_RefurbishYard yard;
        public RM_WornBitStage stage = RM_WornBitStage.None;
        public int fee;
        public bool haggled;
        public int readyTick = -1;
        public bool demandRolled;
        public int secondFee;

        public int lastFavourTick = -1;
        public Map favourMap;
        public int favourUntilTick = -1;
        public int homeTile = -1;

        public bool mapLossReported;
        private List<int> landedMaps = new List<int>();

        public RM_WornBitGame(Game game)
        {
        }

        public static RM_WornBitGame Instance => Current.Game?.GetComponent<RM_WornBitGame>();

        public bool ArcRunning => stage >= RM_WornBitStage.AwaitingHead && stage <= RM_WornBitStage.Collected;

        public bool RestorationOpen => stage == RM_WornBitStage.Collected;

        public bool FavourAt(Map map) { return favourMap != null && favourMap == map; }

        public override void ExposeData()
        {
            Scribe_References.Look(ref hulk, "hulk", saveDestroyedThings: true);
            Scribe_References.Look(ref quest, "quest");
            Scribe_References.Look(ref yard, "yard");
            Scribe_Values.Look(ref stage, "stage", RM_WornBitStage.None);
            Scribe_Values.Look(ref fee, "fee", 0);
            Scribe_Values.Look(ref haggled, "haggled", false);
            Scribe_Values.Look(ref readyTick, "readyTick", -1);
            Scribe_Values.Look(ref demandRolled, "demandRolled", false);
            Scribe_Values.Look(ref secondFee, "secondFee", 0);
            Scribe_Values.Look(ref lastFavourTick, "lastFavourTick", -1);
            Scribe_References.Look(ref favourMap, "favourMap");
            Scribe_Values.Look(ref favourUntilTick, "favourUntilTick", -1);
            Scribe_Values.Look(ref homeTile, "homeTile", -1);
            Scribe_Values.Look(ref mapLossReported, "mapLossReported", false);
            Scribe_Collections.Look(ref landedMaps, "landedMaps", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && landedMaps == null)
            {
                landedMaps = new List<int>();
            }
        }

        // ---- stage 2 ----

        public static Faction FindRefurbisher()
        {
            return Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => !f.defeated && !f.IsPlayer && !f.temporary
                && f.def.HasModExtension<RM_DrillRefurbisherExtension>());
        }

        /// <summary>Fires on unbitting. No refurbisher in the world means no quest: the hulk stays Unbitted and it says so.</summary>
        public void OfferQuest(Pawn borehulk)
        {
            hulk = borehulk;
            homeTile = borehulk.Map.Tile;
            demandRolled = false;
            secondFee = 0;
            haggled = false;
            Faction faction = FindRefurbisher();
            if (faction == null || !TryFindYardTile(faction, borehulk.Map.Tile, out PlanetTile tile))
            {
                // Not silent and not a dead end: GameComponentTick asks again every day.
                Messages.Message("Nobody within reach takes this kind of work yet.", borehulk, MessageTypeDefOf.NeutralEvent, historical: false);
                return;
            }
            var created = (RM_RefurbishYard)WorldObjectMaker.MakeWorldObject(RM_WornBitDefOf.RM_RefurbishYard);
            created.Tile = tile;
            created.SetFaction(faction);
            Find.WorldObjects.Add(created);
            yard = created;
            fee = RM_WornBitKernel.ScaledFee(RM_RustCathedralSettings.wornBitFee, RM_WornBitKernel.WealthFactor(WealthNow()));
            stage = RM_WornBitStage.AwaitingHead;
            quest = QuestUtility.GenerateQuestAndMakeAvailable(RM_WornBitDefOf.RM_WornBitRefurbishment, 0f);
            if (quest.State == QuestState.NotYetAccepted)
            {
                quest.Accept(null);
            }
            QuestUtility.SendLetterQuestAvailable(quest);
        }

        private static float WealthNow()
        {
            return Find.Maps.Where(m => m.IsPlayerHome).Sum(m => m.wealthWatcher.WealthTotal);
        }

        private static bool TryFindYardTile(Faction faction, PlanetTile near, out PlanetTile tile)
        {
            Settlement closest = Find.WorldObjects.Settlements.Where(s => s.Faction == faction)
                .OrderBy(s => Find.WorldGrid.ApproxDistanceInTiles(s.Tile, near)).FirstOrDefault();
            PlanetTile root = closest != null ? closest.Tile : near;
            return TileFinder.TryFindPassableTileWithTraversalDistance(root, 3, 12, out tile,
                t => !Find.WorldObjects.AnyWorldObjectAt(t));
        }

        public void OnHeadHandedOver(int paid)
        {
            stage = RM_WornBitStage.Refurbishing;
            readyTick = Find.TickManager.TicksGame + RefurbishTicks;
            Find.LetterStack.ReceiveLetter("Work order signed", "The yard has the drill head. It will be ready in " + RM_RustCathedralSettings.wornBitRefurbishDays.ToString("0.#") + " days. The truce holds while the order stands.",
                LetterDefOf.NeutralEvent, yard);
        }

        public static int RefurbishTicks => (int)(RM_RustCathedralSettings.wornBitRefurbishDays * GenDate.TicksPerDay);

        public bool RollSecondDemand()
        {
            if (!demandRolled)
            {
                demandRolled = true;
                secondFee = Rand.Chance(RM_RustCathedralSettings.wornBitSecondDemandChance)
                    ? RM_WornBitKernel.ScaledFee(fee / 2, 1f)
                    : 0;
            }
            return secondFee > 0;
        }

        public void OnHeadCollected()
        {
            stage = RM_WornBitStage.Collected;
            Find.LetterStack.ReceiveLetter("The drill head is yours", "The refurbished drill head is out of the yard. Carry it back to the borehulk, with the parts in a stockpile, and the restoration can begin.",
                LetterDefOf.PositiveEvent, hulk);
            yard?.Destroy();
            yard = null;
        }

        /// <summary>Attacking the yard voids the order: the head is gone and the quest ends in failure.</summary>
        public void VoidOrder()
        {
            stage = RM_WornBitStage.Failed;
            Find.LetterStack.ReceiveLetter("The work order is void", "The truce is broken and the yard is shut. The drill head is lost. The borehulk stays as it is.",
                LetterDefOf.NegativeEvent, hulk);
            yard?.Destroy();
            yard = null;
            quest?.End(QuestEndOutcome.Fail, sendLetter: false);
        }

        // ---- after the fork ----

        public void OnRestored(Pawn borehulk)
        {
            hulk = borehulk;
            stage = RM_WornBitStage.Finished;
            homeTile = borehulk.Map.Tile;
            foreach (Map m in Find.Maps)
            {
                if (!landedMaps.Contains(m.uniqueID))
                {
                    landedMaps.Add(m.uniqueID);
                }
            }
            quest?.End(QuestEndOutcome.Success, sendLetter: false);
        }

        public bool FreedHulkAlive => hulk != null && !hulk.Dead && hulk.TryGetComp<RM_CompBorehulkDrill>()?.FreedWild == true;

        public string FavourRefusal(Map map)
        {
            if (!RM_RustCathedralSettings.wornBitFavoursEnabled || !FreedHulkAlive)
            {
                return "nothing to ask";
            }
            if (RM_WornBit.OnCathedralGround(map))
            {
                return "it never mines for you on this ground";
            }
            if (favourMap != null)
            {
                return "it is already out on a favour";
            }
            int cooldown = (int)(RM_RustCathedralSettings.wornBitFavourCooldownDays * GenDate.TicksPerDay);
            if (!RM_WornBitKernel.FavourReady(Find.TickManager.TicksGame, lastFavourTick, cooldown))
            {
                return "it came not long ago";
            }
            return null;
        }

        public void StartFavour(Map map)
        {
            if (FavourRefusal(map) != null)
            {
                return;
            }
            lastFavourTick = Find.TickManager.TicksGame;
            favourMap = map;
            favourUntilTick = lastFavourTick + (int)(RM_RustCathedralSettings.wornBitFavourDays * GenDate.TicksPerDay);
            if (hulk.Spawned)
            {
                homeTile = hulk.Map.Tile;
                hulk.DeSpawn();
            }
            else if (Find.WorldPawns.Contains(hulk))
            {
                Find.WorldPawns.RemovePawn(hulk);
                Find.WorldPawns.ForcefullyKeptPawns.Remove(hulk);
            }
            GenSpawn.Spawn(hulk, CellFinder.RandomEdgeCell(map), map);
            hulk.TryGetComp<RM_CompBorehulkDrill>().favourLine = "It came as a friend would, for a while.";
            Find.LetterStack.ReceiveLetter("The borehulk came", "The borehulk heard the ask and trundled in. It will work the mining designations here for a few days, then go home. It takes no orders.",
                LetterDefOf.PositiveEvent, hulk);
        }

        private void EndFavour()
        {
            favourMap = null;
            favourUntilTick = -1;
            RM_CompBorehulkDrill comp = hulk?.TryGetComp<RM_CompBorehulkDrill>();
            if (comp == null || hulk.Dead)
            {
                return;
            }
            comp.favourLine = null;
            Map home = Find.Maps.FirstOrDefault(m => m.Tile == homeTile);
            Find.LetterStack.ReceiveLetter("The borehulk left", "The favour is done. The borehulk has gone home.", LetterDefOf.NeutralEvent, hulk);
            if (hulk.Spawned)
            {
                hulk.DeSpawn();
            }
            if (home != null)
            {
                GenSpawn.Spawn(hulk, CellFinder.RandomEdgeCell(home), home);
            }
            else
            {
                Find.WorldPawns.PassToWorld(hulk, PawnDiscardDecideMode.KeepForever);
            }
        }

        // ---- the tick ----

        public override void GameComponentTick()
        {
            if (Find.TickManager.TicksGame % PollTicks != 0)
            {
                return;
            }
            if (stage == RM_WornBitStage.Refurbishing && Find.TickManager.TicksGame >= readyTick)
            {
                stage = RM_WornBitStage.ReadyForCollection;
                Find.LetterStack.ReceiveLetter("The drill head is ready", "The yard sends word: the refurbished drill head can be collected. Mind the price. It has been known to go up.",
                    LetterDefOf.NeutralEvent, yard);
            }
            if (favourMap != null && (Find.TickManager.TicksGame >= favourUntilTick || !Find.Maps.Contains(favourMap)))
            {
                EndFavour();
            }
            if (stage == RM_WornBitStage.None && Find.TickManager.TicksGame % GenDate.TicksPerDay == 0 && hulk != null && hulk.Spawned
                && hulk.TryGetComp<RM_CompBorehulkDrill>()?.State == RM_BorehulkDrillState.Unbitted)
            {
                OfferQuest(hulk);
            }
            KeepHulkOnRecord();
            NoticeLandings();
        }

        // A hulk whose map is gone waits in the world record; the next landing on Cathedral ground finds it.
        private void KeepHulkOnRecord()
        {
            if (hulk == null || hulk.Dead || hulk.Spawned || hulk.Destroyed)
            {
                return;
            }
            if (!Find.WorldPawns.Contains(hulk))
            {
                return;
            }
            Find.WorldPawns.ForcefullyKeptPawns.Add(hulk);
            if (!mapLossReported)
            {
                mapLossReported = true;
                Find.LetterStack.ReceiveLetter("The borehulk stays behind", "The borehulk's ground has been left. It waits in the world record, and it will be there at the next landing on Cathedral ground.",
                    LetterDefOf.NeutralEvent);
            }
            Map ground = Find.Maps.FirstOrDefault(RM_WornBit.OnCathedralGround);
            if (ground != null)
            {
                Find.WorldPawns.RemovePawn(hulk);
                Find.WorldPawns.ForcefullyKeptPawns.Remove(hulk);
                GenSpawn.Spawn(hulk, CellFinder.RandomEdgeCell(ground), ground);
                mapLossReported = false;
            }
        }

        // Kept: each new landing on Cathedral ground starts the hum a band lower.
        private void NoticeLandings()
        {
            bool kept = hulk != null && !hulk.Dead && hulk.TryGetComp<RM_CompBorehulkDrill>()?.Kept == true;
            foreach (Map m in Find.Maps)
            {
                if (landedMaps.Contains(m.uniqueID) || !RM_WornBit.OnCathedralGround(m))
                {
                    continue;
                }
                landedMaps.Add(m.uniqueID);
                if (kept && RM_RustCathedralSettings.wornBitLandingBandEnabled)
                {
                    RM_MapComponent_BiomeAttitude.AddIrritation(m, RM_RustCathedralSettings.wornBitLandingIrritation);
                }
            }
        }
    }

    /// <summary>Keeps the hulk out of world-pawn GC for the life of the quest and points the quest log at the yard and the hulk.</summary>
    public class RM_QuestPart_WornBit : QuestPart
    {
        public override IEnumerable<GlobalTargetInfo> QuestLookTargets
        {
            get
            {
                RM_WornBitGame g = RM_WornBitGame.Instance;
                if (g?.yard != null)
                {
                    yield return g.yard;
                }
                if (g?.hulk != null && g.hulk.Spawned)
                {
                    yield return g.hulk;
                }
            }
        }

        public override bool QuestPartReserves(Pawn p)
        {
            return p == RM_WornBitGame.Instance?.hulk;
        }

        public override string DescriptionPart
        {
            get
            {
                RM_WornBitGame g = RM_WornBitGame.Instance;
                if (g == null)
                {
                    return null;
                }
                switch (g.stage)
                {
                    case RM_WornBitStage.AwaitingHead:
                        return "Bring the worn drill head and " + g.fee + " silver to the yard. A caravan walks it in; a ship can land close by, and no drop pod will lift it.";
                    case RM_WornBitStage.Refurbishing:
                        return "The yard has the head. Ready in " + (g.readyTick - Find.TickManager.TicksGame).ToStringTicksToPeriod() + ".";
                    case RM_WornBitStage.ReadyForCollection:
                        return "The refurbished head is ready at the yard. The price may have gone up.";
                    case RM_WornBitStage.Collected:
                        return g.hulk != null && g.hulk.Spawned
                            ? "Bring the refurbished head to the borehulk's map and restore it."
                            : "The borehulk's ground has been left. It waits for the next landing on Cathedral ground.";
                }
                return null;
            }
        }
    }

    /// <summary>The quest is thin on purpose: the stages are the game component's; this adds the part that shows them.</summary>
    public class RM_QuestNode_WornBit : QuestNode
    {
        protected override bool TestRunInt(Slate slate)
        {
            return true;
        }

        protected override void RunInt()
        {
            QuestGen.quest.AddPart(new RM_QuestPart_WornBit());
        }
    }

    /// <summary>Added to the comms console by patch: the ask. A freed borehulk has no gizmo and no order.</summary>
    public class RM_CompProperties_BorehulkFavour : CompProperties
    {
        public RM_CompProperties_BorehulkFavour()
        {
            compClass = typeof(RM_CompBorehulkFavour);
        }
    }

    public class RM_CompBorehulkFavour : ThingComp
    {
        public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
        {
            RM_WornBitGame g = RM_WornBitGame.Instance;
            if (g == null || !g.FreedHulkAlive || !RM_RustCathedralSettings.wornBitFavoursEnabled)
            {
                yield break;
            }
            string refusal = g.FavourRefusal(parent.Map);
            Map map = parent.Map;
            yield return refusal != null
                ? new FloatMenuOption("Ask the borehulk for a favour: " + refusal, null)
                : new FloatMenuOption("Ask the borehulk for a favour", delegate { g.StartFavour(map); });
        }
    }
}
