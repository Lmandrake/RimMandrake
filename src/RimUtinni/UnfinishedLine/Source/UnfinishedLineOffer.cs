using System.Collections.Generic;
using System.Linq;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_SPINE_COUNT_1 — the chain's firing route (design §3.2, route 2: a dedicated
    /// GiveQuest incident). The gates live here because QuestNode_GetFaction cannot filter on
    /// goodwill: the chain is on, the day is late enough, the Enclaves exist, are not hostile and
    /// like the player enough, the player can repair droids at a shop, and both factions still
    /// hold a settlement on the planet.
    /// </summary>
    public class IncidentWorker_RUT_UnfinishedLine : IncidentWorker_GiveQuest
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            return Gates(out string _) && base.CanFireNowSub(parms);
        }

        public static bool Gates(out string why)
        {
            if (!UnfinishedLineSettings.chainEnabled)
            {
                why = "chain disabled in Mod Settings";
                return false;
            }
            if (GenDate.DaysPassed < UnfinishedLineSettings.earliestDay)
            {
                why = "day " + GenDate.DaysPassed + " < " + UnfinishedLineSettings.earliestDay;
                return false;
            }
            Faction enclaves = LineFactions.Enclaves;
            Faction hive = LineFactions.Hive;
            if (enclaves == null || hive == null)
            {
                why = "faction missing (enclaves " + (enclaves != null) + ", hive " + (hive != null) + ")";
                return false;
            }
            if (enclaves.HostileTo(Faction.OfPlayer))
            {
                why = "enclaves hostile";
                return false;
            }
            if (enclaves.PlayerGoodwill < UnfinishedLineSettings.minEnclaveGoodwill)
            {
                why = "enclave goodwill " + enclaves.PlayerGoodwill + " < " + UnfinishedLineSettings.minEnclaveGoodwill;
                return false;
            }
            ResearchProjectDef shop = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(LineFactions.ShopRepairResearch);
            if (shop == null || !shop.IsFinished)
            {
                why = LineFactions.ShopRepairResearch + (shop == null ? " missing" : " not researched");
                return false;
            }
            bool enclaveHome = Find.WorldObjects.Settlements.Any(s => s.Faction == enclaves);
            bool hiveHome = Find.WorldObjects.Settlements.Any(s => s.Faction == hive);
            if (!enclaveHome || !hiveHome)
            {
                why = "no settlement (enclaves " + enclaveHome + ", hive " + hiveHome + ")";
                return false;
            }
            why = "open";
            return true;
        }
    }

    /// <summary>Deterministic triggers and state reads, so nothing is ever verified by waiting for the
    /// storyteller (rimworld-quests §7). The Proof* methods are for jawa/static_call; the debug actions
    /// sit under Dev mode -> Debug actions -> Quests.</summary>
    public static class UnfinishedLineProof
    {
        public const string ParentDefName = "RUT_UnfinishedLine";

        public static Quest FindChain()
        {
            return Find.QuestManager.QuestsListForReading
                .Where(q => q.root != null && q.root.defName == ParentDefName)
                .OrderByDescending(q => q.appearanceTick)
                .FirstOrDefault();
        }

        public static QuestPart_RUT_SequentialSubquests Spine(Quest q)
        {
            return q?.PartsListForReading.OfType<QuestPart_RUT_SequentialSubquests>().FirstOrDefault();
        }

        /// <summary>"GATES open" or "GATES closed: why".</summary>
        public static string ProofGates()
        {
            return IncidentWorker_RUT_UnfinishedLine.Gates(out string why) ? "GATES open" : "GATES closed: " + why;
        }

        /// <summary>Offers the chain's parent now, skipping the gates, and accepts it when
        /// <paramref name="accept"/>. Returns the parent's state and the spine's.</summary>
        public static string ProofOffer(bool accept)
        {
            QuestScriptDef root = DefDatabase<QuestScriptDef>.GetNamedSilentFail(ParentDefName);
            if (root == null) return "REFUSED: no " + ParentDefName;
            Map map = Find.AnyPlayerHomeMap;
            float points = map != null ? StorytellerUtility.DefaultThreatPointsNow(map) : 500f;
            Slate slate = new Slate();
            slate.Set("points", points);
            if (!root.CanRun(slate, (IIncidentTarget)map ?? Find.World))
            {
                return "REFUSED: " + ParentDefName + " cannot run (TestRun false: Enclaves/Hive missing or hostile, or no Enclave settlement)";
            }
            Quest q = QuestUtility.GenerateQuestAndMakeAvailable(root, slate);
            if (accept && q.State == QuestState.NotYetAccepted)
            {
                q.Accept(null);
            }
            return ProofChain();
        }

        /// <summary>Offers the chain's current beat now (the parent must be accepted).</summary>
        public static string ProofNextBeat()
        {
            Quest q = FindChain();
            QuestPart_RUT_SequentialSubquests spine = Spine(q);
            return spine == null ? "REFUSED: no chain quest" : spine.ForceNextBeat() + " || " + ProofChain();
        }

        /// <summary>"CHAIN state | part ... | children [def:state, ...]".</summary>
        public static string ProofChain()
        {
            Quest q = FindChain();
            if (q == null) return "CHAIN none";
            QuestPart_RUT_SequentialSubquests spine = Spine(q);
            string kids = string.Join(", ", q.GetSubquests().Select(c => c.root.defName + ":" + c.State));
            return "CHAIN " + q.State + " | " + (spine?.Describe() ?? "no spine part") + " | children [" + kids + "]";
        }

        /// <summary>Starts (true) or quietly ends (false) the brokered truce and reads the Hive back:
        /// "TRUCE active|off | hive goodwill N | relation K".</summary>
        public static string ProofTruce(bool start)
        {
            GameComponent_RUT_UnfinishedLine comp = GameComponent_RUT_UnfinishedLine.Get;
            if (comp == null) return "REFUSED: no GameComponent_RUT_UnfinishedLine";
            if (start) comp.StartTruce();
            else comp.EndTruce(false);
            Faction hive = LineFactions.Hive;
            if (hive == null) return "REFUSED: no Hive faction";
            return "TRUCE " + (comp.truceActive ? "active" : "off") + " | hive goodwill " + hive.GoodwillWith(Faction.OfPlayer)
                + " | relation " + hive.RelationKindWith(Faction.OfPlayer);
        }

        /// <summary>Accepts the pending beat if offered, then ends it with the given outcome, so a walk can
        /// reach a later beat without playing the earlier ones. "ENDED def:Outcome || CHAIN ...".</summary>
        public static string ProofEndBeat(bool success)
        {
            Quest q = FindChain();
            Quest beat = q?.GetSubquests().FirstOrDefault(c => c.State == QuestState.Ongoing || c.State == QuestState.NotYetAccepted);
            if (beat == null) return "REFUSED: no pending beat || " + ProofChain();
            if (beat.State == QuestState.NotYetAccepted) beat.Accept(null);
            beat.End(success ? QuestEndOutcome.Success : QuestEndOutcome.Fail, sendLetter: false);
            return "ENDED " + beat.root.defName + ":" + beat.State + " || " + ProofChain();
        }

        /// <summary>Beat 3 (any action but "state" accepts an offered beat first). action: "state" reads the part; "home" carries undelivered cores (still on the
        /// unvisited site, or anywhere) to the home map's trade drop spot; "sell" / "refuse" answer the broker.
        /// "CORES ... || CHAIN ...".</summary>
        public static string ProofCores(string action)
        {
            Quest beat = Find.QuestManager.QuestsListForReading
                .Where(x => x.root?.defName == "RUT_UnfinishedLine_3_Cores" && (x.State == QuestState.Ongoing || x.State == QuestState.NotYetAccepted))
                .OrderByDescending(x => x.appearanceTick).FirstOrDefault();
            if (beat != null && beat.State == QuestState.NotYetAccepted && action != "state") beat.Accept(null);
            QuestPart_RUT_PatternCores part = beat?.PartsListForReading.OfType<QuestPart_RUT_PatternCores>().FirstOrDefault();
            if (part == null) return "REFUSED: no offered or ongoing Pattern Cores beat || " + ProofChain();
            string did = "state";
            switch (action)
            {
                case "home":
                    Map home = Find.AnyPlayerHomeMap;
                    if (home == null) return "REFUSED: no home map";
                    IntVec3 spot = DropCellFinder.TradeDropSpot(home);
                    foreach (Thing c in part.LiveCores.ToList())
                    {
                        if (c.Spawned) c.DeSpawn();
                        else c.holdingOwner?.Remove(c);
                        GenPlace.TryPlaceThing(c, spot, home, ThingPlaceMode.Near);
                    }
                    did = "home";
                    break;
                case "sell":
                    did = part.Sell();
                    break;
                case "refuse":
                    did = part.Deliver();
                    break;
            }
            return "CORES " + did + " | " + part.Describe() + " | beat " + beat.State + " || " + ProofChain();
        }

        /// <summary>Spawns <paramref name="count"/> wild-droid-pack droids near the home map's centre and
        /// reports how many ordered pairs of them are hostile to each other (the pack contract: 0) and
        /// whether each is hostile to the player. "PACK n | mutual hostile pairs k | hostile to player m".</summary>
        public static string ProofWildPack(int count)
        {
            Map map = Find.AnyPlayerHomeMap;
            if (map == null) return "REFUSED: no home map";
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RSW_DW_OuterRim_ImperialLaborDroid");
            if (kind == null) return "REFUSED: no RSW_DW_OuterRim_ImperialLaborDroid";
            List<Pawn> pack = new List<Pawn>();
            for (int i = 0; i < count; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer,
                    map.Tile, forceGenerateNewPawn: true, canGeneratePawnRelations: false));
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(map.Center, map, 8), map);
                GenStep_RUT_FoundryRuin.MakePack(p);
                pack.Add(p);
            }
            int mutual = 0;
            foreach (Pawn a in pack)
                foreach (Pawn b in pack)
                    if (a != b && a.HostileTo(b)) mutual++;
            int toPlayer = pack.Count(p => p.HostileTo(Faction.OfPlayer));
            int inState = pack.Count(p => p.MentalState is MentalState_RUT_WildDroidPack);
            return "PACK " + pack.Count + " | in pack state " + inState + " | mutual hostile pairs " + mutual + " | hostile to player " + toPlayer;
        }

        [DebugAction("Quests", "Offer The Unfinished Line (skip gates)", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DebugOffer()
        {
            Messages.Message(ProofOffer(false), MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Quests", "Unfinished Line: offer next beat now", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DebugNextBeat()
        {
            Messages.Message(ProofNextBeat(), MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Quests", "Unfinished Line: why is it not offered", allowedGameStates = AllowedGameStates.Playing)]
        private static void DebugGates()
        {
            Messages.Message(ProofGates(), MessageTypeDefOf.NeutralEvent, false);
        }
    }
}
