using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Grammar;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_CORES_BEAT_1 — beat 3 "The Pattern Cores" (design §2.3). The pieces vanilla does
    /// not have:
    ///
    /// * A site that is a place, not a faction's camp: <see cref="SitePartWorker_RUT_FoundryRuin"/> makes the
    ///   three cores at quest-generation time (the SitePartWorker_ItemStash shape: part.things, and the list
    ///   on the slate as "cores" so cores.Destroyed is a real signal), and <see cref="GenStep_RUT_FoundryRuin"/>
    ///   builds the collapsed fabrication hall and its wild droids when the map is made.
    /// * A wild-droid PACK. Droidworks' wild droids are factionless humanlike manhunters, and
    ///   MentalState_Manhunter.ForceHostileTo(Thing) is true against any factionless humanlike, so two of them
    ///   fight each other (IncidentWorker_WildDroidCrash's header). <see cref="MentalState_RUT_WildDroidPack"/>
    ///   is the same state with one exception: it is not hostile to another pawn in the same state. The
    ///   think tree routes on the class (ThinkNode_ConditionalMentalStateClass uses IsInstanceOfType), so the
    ///   subclass gets the manhunter subtree unchanged.
    /// * The way home and the sell-out (Q3=A): <see cref="QuestPart_RUT_PatternCores"/> watches for all three
    ///   cores on a player home map, then sends the broker's offer (<see cref="ChoiceLetter_RUT_CoreBroker"/>).
    ///   Selling pays silver and Empire goodwill and tells the PARENT chain (<see cref="QuestPart_RUT_SignalParent"/>);
    ///   refusing, or letting the offer lapse, hands the cores to an Enclave courier.
    /// * Freed droids: a wild droid from the site taken prisoner and RELEASED without a restraining bolt walks
    ///   to the Enclaves, which pays Enclave goodwill (JobDriver_ReleasePrisoner sends the "Released" target
    ///   signal; the part tags the site's pack with the quest's "wildDroids" tag when the map is generated).
    /// </summary>
    public class MentalState_RUT_WildDroidPack : MentalState_Manhunter
    {
        public override bool ForceHostileTo(Thing t)
        {
            if (t is Pawn p && p.Faction == null && p.MentalState is MentalState_RUT_WildDroidPack)
            {
                return false;
            }
            return base.ForceHostileTo(t);
        }
    }

    [DefOf]
    public static class UnfinishedLineDefOf
    {
        public static MentalStateDef RUT_WildDroidPack;

        public static ThingDef RUT_FoundryPatternCore;

        public static LetterDef RUT_CoreBrokerOffer;

        public static HistoryEventDef RUT_LineCoresSoldToEmpire;

        public static HistoryEventDef RUT_LineWildDroidFreed;

        static UnfinishedLineDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(UnfinishedLineDefOf));
        }
    }

    public class SitePartWorker_RUT_FoundryRuin : SitePartWorker
    {
        public const int CoreCount = 3;

        public override void Notify_GeneratedByQuestGen(SitePart part, Slate slate, List<Rule> outExtraDescriptionRules, Dictionary<string, string> outExtraDescriptionConstants)
        {
            base.Notify_GeneratedByQuestGen(part, slate, outExtraDescriptionRules, outExtraDescriptionConstants);
            List<Thing> cores = new List<Thing>();
            for (int i = 0; i < CoreCount; i++)
            {
                cores.Add(ThingMaker.MakeThing(UnfinishedLineDefOf.RUT_FoundryPatternCore));
            }
            part.things = new ThingOwner<Thing>(part, oneStackOnly: false);
            part.things.dontTickContents = true;
            part.things.TryAddRangeOrTransfer(cores, canMergeWithExistingStacks: false);
            slate.Set("cores", cores);
        }

        public override string GetPostProcessedThreatLabel(Site site, SitePart sitePart)
        {
            return def.label + " (" + WildDroidCount(sitePart.parms.threatPoints) + " wild droids)";
        }

        public static int WildDroidCount(float points)
        {
            int max = Mathf.Max(1, UnfinishedLineSettings.ruinWildDroidsMax);
            return Mathf.Clamp(Mathf.RoundToInt(points / 150f), Mathf.Min(2, max), max);
        }
    }

    /// <summary>One entry of the ruin's wild-droid pool: plain fields and a plain &lt;li&gt; list, never
    /// PawnGenOption (its custom loader discards the whole def on an &lt;li&gt;).</summary>
    public class RUT_WildDroidOption
    {
        public PawnKindDef kind;

        public float weight = 1f;
    }

    /// <summary>The collapsed fabrication hall: a steel-walled hall with fallen sections, a metal floor,
    /// slag, the three cores inside, and the wild-droid pack (count by the site's threat points, capped by the
    /// setting) in and around it.</summary>
    public class GenStep_RUT_FoundryRuin : GenStep
    {
        public IntVec2 hallSize = new IntVec2(15, 11);

        public float wallCollapseChance = 0.3f;

        public int slagChunks = 8;

        public List<RUT_WildDroidOption> wildDroids = new List<RUT_WildDroidOption>();

        public override int SeedPart => 418836029;

        public override void Generate(Map map, GenStepParams parms)
        {
            CellRect hall = FindHall(map);
            BuildHall(map, hall);
            if (parms.sitePart?.things != null)
            {
                foreach (Thing core in parms.sitePart.things.ToList())
                {
                    IntVec3 cell = RandomInteriorCell(map, hall);
                    parms.sitePart.things.TryDrop(core, cell, map, ThingPlaceMode.Near, out Thing _);
                }
            }
            SpawnPack(map, hall, parms.sitePart?.parms?.threatPoints ?? 0f);
            MapGenerator.SetVar("RectOfInterest", hall);
            MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects").Add(hall.ExpandedBy(2));
        }

        private CellRect FindHall(Map map)
        {
            List<CellRect> used = MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects");
            for (int i = 0; i < 60; i++)
            {
                IntVec3 c = CellFinder.RandomClosewalkCellNear(map.Center, map, 25);
                CellRect r = CellRect.CenteredOn(c, hallSize.x, hallSize.z);
                if (!r.ExpandedBy(3).InBounds(map)) continue;
                if (used.Any(u => u.Overlaps(r))) continue;
                if (r.Cells.Count(x => x.GetTerrain(map).affordances.Contains(TerrainAffordanceDefOf.Heavy)) < r.Area * 0.8f) continue;
                return r;
            }
            return CellRect.CenteredOn(map.Center, hallSize.x, hallSize.z).ClipInsideMap(map);
        }

        private void BuildHall(Map map, CellRect hall)
        {
            TerrainDef floor = DefDatabase<TerrainDef>.GetNamedSilentFail("MetalTile");
            ThingDef rubble = ThingDefOf.Filth_RubbleBuilding;
            foreach (IntVec3 c in hall)
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t is Pawn) continue;
                    if (t.def.category == ThingCategory.Plant || t.def.category == ThingCategory.Building || t.def.category == ThingCategory.Item)
                    {
                        t.Destroy(DestroyMode.Vanish);
                    }
                }
                if (floor != null && c.GetTerrain(map).affordances.Contains(TerrainAffordanceDefOf.Heavy))
                {
                    map.terrainGrid.SetTerrain(c, floor);
                }
            }
            foreach (IntVec3 c in hall.EdgeCells)
            {
                if (Rand.Chance(wallCollapseChance))
                {
                    if (rubble != null) FilthMaker.TryMakeFilth(c, map, rubble);
                    continue;
                }
                Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.Steel);
                wall.HitPoints = Mathf.Max(1, Mathf.RoundToInt(wall.MaxHitPoints * Rand.Range(0.3f, 0.8f)));
                GenSpawn.Spawn(wall, c, map);
            }
            // Always a way in, whatever the collapse roll did: the middle of the south wall is gone.
            IntVec3 gap = new IntVec3(hall.CenterCell.x, 0, hall.minZ);
            for (int dx = -1; dx <= 1; dx++)
            {
                IntVec3 g = gap + new IntVec3(dx, 0, 0);
                g.GetEdifice(map)?.Destroy(DestroyMode.Vanish);
                if (rubble != null) FilthMaker.TryMakeFilth(g, map, rubble);
            }
            ThingDef slag = ThingDefOf.ChunkSlagSteel;
            for (int i = 0; i < slagChunks && slag != null; i++)
            {
                GenSpawn.Spawn(ThingMaker.MakeThing(slag), RandomInteriorCell(map, hall), map);
            }
        }

        private static IntVec3 RandomInteriorCell(Map map, CellRect hall)
        {
            CellRect inner = hall.ContractedBy(1);
            for (int i = 0; i < 40; i++)
            {
                IntVec3 c = inner.RandomCell;
                if (c.Standable(map) && c.GetFirstItem(map) == null) return c;
            }
            return inner.CenterCell;
        }

        private void SpawnPack(Map map, CellRect hall, float points)
        {
            List<RUT_WildDroidOption> legal = wildDroids.Where(o => o?.kind != null && o.weight > 0f).ToList();
            if (legal.Count == 0) return;
            int count = SitePartWorker_RUT_FoundryRuin.WildDroidCount(points);
            for (int i = 0; i < count; i++)
            {
                PawnKindDef kind = legal.RandomElementByWeight(o => o.weight).kind;
                Pawn droid = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                    kind, null, PawnGenerationContext.NonPlayer, map.Tile,
                    forceGenerateNewPawn: true, allowDead: false, allowDowned: false,
                    canGeneratePawnRelations: false, mustBeCapableOfViolence: false,
                    colonistRelationChanceFactor: 0f, forceAddFreeWarmLayerIfNeeded: false,
                    allowGay: true, allowPregnant: false, allowFood: false, allowAddictions: false));
                IntVec3 cell = CellFinder.RandomClosewalkCellNear(hall.CenterCell, map, Mathf.Max(hall.Width, hall.Height) / 2 + 3);
                GenSpawn.Spawn(droid, cell, map, Rot4.Random);
                MakePack(droid);
            }
        }

        public static bool MakePack(Pawn droid)
        {
            return droid.mindState.mentalStateHandler.TryStartMentalState(
                UnfinishedLineDefOf.RUT_WildDroidPack, "left in the foundry ruin since the company walked away",
                forced: true, forceWake: true, transitionSilently: true);
        }
    }

    /// <summary>The beat's working part (see the file header). Every behaviour reads its setting when it
    /// fires, so a settings change mid-quest takes effect.</summary>
    public class QuestPart_RUT_PatternCores : QuestPartActivable
    {
        public List<Thing> cores = new List<Thing>();

        public Site site;

        public Faction enclaves;

        public string inSignalMapGenerated;

        public string inSignalReleased;

        public string outSignalHome;

        public string outSignalSold;

        public string outSignalDelivered;

        public bool home;

        public bool decided;

        public int brokerDeadlineTick = -1;

        public int freed;

        public string WildDroidTag => "Quest" + quest.id + ".wildDroids";

        public IEnumerable<Thing> LiveCores => cores.Where(c => c != null && !c.Destroyed);

        public bool AllCoresHome
        {
            get
            {
                if (cores.Count == 0) return false;
                foreach (Thing c in cores)
                {
                    if (c == null || c.Destroyed) return false;
                    Map m = c.MapHeld;
                    if (m == null || !m.IsPlayerHome) return false;
                }
                return true;
            }
        }

        public override IEnumerable<GlobalTargetInfo> QuestLookTargets
        {
            get
            {
                foreach (GlobalTargetInfo t in base.QuestLookTargets) yield return t;
                if (site != null) yield return site;
            }
        }

        public override void QuestPartTick()
        {
            base.QuestPartTick();
            if (decided || Find.TickManager.TicksGame % 250 != 0) return;
            if (!home && AllCoresHome)
            {
                home = true;
                Find.SignalManager.SendSignal(new Signal(outSignalHome));
                OfferBroker();
                return;
            }
            if (home && brokerDeadlineTick >= 0 && Find.TickManager.TicksGame >= brokerDeadlineTick)
            {
                Deliver();
            }
        }

        private void OfferBroker()
        {
            if (!UnfinishedLineSettings.coreBrokerEnabled || Faction.OfEmpire == null)
            {
                Deliver();
                return;
            }
            brokerDeadlineTick = Find.TickManager.TicksGame + Mathf.Max(1, UnfinishedLineSettings.coreBrokerWaitDays) * 60000;
            ChoiceLetter letter = LetterMaker.MakeLetter(
                "A buyer for the cores",
                "Someone listened to your comms. A salvage broker working for " + Faction.OfEmpire.Name
                + " has made contact, polite and very well informed: three company pattern cores, sealed, "
                + "out of the old silicax foundry.\n\nThe broker offers " + UnfinishedLineSettings.coreSaleSilver
                + " silver for the three, collected by shuttle today, and the Empire's thanks.\n\n"
                + "The patterns are the Hive's, and the hope is the Enclaves'. Sell them, and neither will ever "
                + "forgive the Jawa. Refuse, and an Enclave courier takes the cores where they belong. The broker "
                + "will wait " + UnfinishedLineSettings.coreBrokerWaitDays + " days for an answer, then assume no.",
                UnfinishedLineDefOf.RUT_CoreBrokerOffer, new LookTargets(LiveCores), Faction.OfEmpire, quest);
            Find.LetterStack.ReceiveLetter(letter);
        }

        private Map CoreMap => LiveCores.Select(c => c.MapHeld).FirstOrDefault(m => m != null) ?? Find.AnyPlayerHomeMap;

        /// <summary>Removes the cores without firing cores.Destroyed (the fail branch): the quest tags go first.</summary>
        private void TakeCores()
        {
            foreach (Thing c in LiveCores.ToList())
            {
                c.questTags?.Clear();
                c.Destroy(DestroyMode.Vanish);
            }
        }

        /// <summary>The cores leave with an Enclave courier: the beat's success.</summary>
        public string Deliver()
        {
            if (decided) return "REFUSED: already decided";
            decided = true;
            RemoveBrokerLetters();
            TakeCores();
            Find.SignalManager.SendSignal(new Signal(outSignalDelivered));
            return "DELIVERED";
        }

        /// <summary>The sell-out (Q3=A): silver by drop pod, Empire goodwill, the cores leave, the parent is told.</summary>
        public string Sell()
        {
            if (decided) return "REFUSED: already decided";
            if (!home) return "REFUSED: the cores are not home";
            decided = true;
            RemoveBrokerLetters();
            Map map = CoreMap;
            TakeCores();
            if (map != null && UnfinishedLineSettings.coreSaleSilver > 0)
            {
                List<Thing> silver = new List<Thing>();
                int left = UnfinishedLineSettings.coreSaleSilver;
                while (left > 0)
                {
                    Thing s = ThingMaker.MakeThing(ThingDefOf.Silver);
                    s.stackCount = Mathf.Min(left, ThingDefOf.Silver.stackLimit);
                    left -= s.stackCount;
                    silver.Add(s);
                }
                DropPodUtility.DropThingsNear(DropCellFinder.TradeDropSpot(map), map, silver, canRoofPunch: false, forbid: false);
            }
            Faction empire = Faction.OfEmpire;
            if (empire != null && UnfinishedLineSettings.coreSaleEmpireGoodwill != 0)
            {
                empire.TryAffectGoodwillWith(Faction.OfPlayer, UnfinishedLineSettings.coreSaleEmpireGoodwill,
                    canSendMessage: true, canSendHostilityLetter: false, reason: UnfinishedLineDefOf.RUT_LineCoresSoldToEmpire);
            }
            Find.SignalManager.SendSignal(new Signal(outSignalSold));
            return "SOLD";
        }

        private void RemoveBrokerLetters()
        {
            foreach (Letter l in Find.LetterStack.LettersListForReading.ToList())
            {
                if (l is ChoiceLetter_RUT_CoreBroker && ((ChoiceLetter)l).quest == quest)
                {
                    Find.LetterStack.RemoveLetter(l);
                }
            }
        }

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag == inSignalMapGenerated)
            {
                TagPack(site?.Map);
            }
            else if (signal.tag == inSignalReleased && signal.args.TryGetArg("SUBJECT", out Pawn droid))
            {
                Freed(droid);
            }
        }

        /// <summary>Tags every wild-droid-pack pawn on the map with this quest's "wildDroids" tag. Returns the count.</summary>
        public int TagPack(Map map)
        {
            if (map == null) return 0;
            int n = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (p.Faction == null && p.MentalState is MentalState_RUT_WildDroidPack)
                {
                    QuestUtility.AddQuestTag(p, WildDroidTag);
                    n++;
                }
            }
            return n;
        }

        public string Freed(Pawn droid)
        {
            if (droid == null || droid.Dead) return "REFUSED: no droid";
            HediffDef bolt = DefDatabase<HediffDef>.GetNamedSilentFail("RSW_DW_RestrainingBolt");
            if (bolt != null && droid.health.hediffSet.HasHediff(bolt))
            {
                Messages.Message(droid.LabelShortCap + " walks out still bolted. The Enclaves will not count a droid in a bolt as freed.",
                    droid, MessageTypeDefOf.NeutralEvent, false);
                return "BOLTED";
            }
            freed++;
            int gw = UnfinishedLineSettings.freedWildDroidGoodwill;
            if (enclaves != null && gw != 0 && !enclaves.defeated)
            {
                enclaves.TryAffectGoodwillWith(Faction.OfPlayer, gw, canSendMessage: true, canSendHostilityLetter: false,
                    reason: UnfinishedLineDefOf.RUT_LineWildDroidFreed, lookTarget: droid);
            }
            return "FREED " + freed;
        }

        public string Describe()
        {
            return "cores " + LiveCores.Count() + "/" + cores.Count + " | home " + home + " | decided " + decided
                + " | broker deadline " + brokerDeadlineTick + " | freed " + freed + " | site " + (site?.HasMap == true ? "map" : site != null ? "no map" : "none");
        }

        public override void Cleanup()
        {
            base.Cleanup();
            RemoveBrokerLetters();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref cores, "cores", LookMode.Reference);
            Scribe_References.Look(ref site, "site");
            Scribe_References.Look(ref enclaves, "enclaves");
            Scribe_Values.Look(ref inSignalMapGenerated, "inSignalMapGenerated");
            Scribe_Values.Look(ref inSignalReleased, "inSignalReleased");
            Scribe_Values.Look(ref outSignalHome, "outSignalHome");
            Scribe_Values.Look(ref outSignalSold, "outSignalSold");
            Scribe_Values.Look(ref outSignalDelivered, "outSignalDelivered");
            Scribe_Values.Look(ref home, "home", false);
            Scribe_Values.Look(ref decided, "decided", false);
            Scribe_Values.Look(ref brokerDeadlineTick, "brokerDeadlineTick", -1);
            Scribe_Values.Look(ref freed, "freed", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (cores == null) cores = new List<Thing>();
                cores.RemoveAll(c => c == null);
            }
        }
    }

    /// <summary>XML verb for <see cref="QuestPart_RUT_PatternCores"/>. Reads $site, $cores and $enclaveFaction.</summary>
    public class QuestNode_RUT_PatternCores : QuestNode
    {
        [NoTranslate]
        public SlateRef<string> outSignalHome;

        [NoTranslate]
        public SlateRef<string> outSignalSold;

        [NoTranslate]
        public SlateRef<string> outSignalDelivered;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestPart_RUT_PatternCores part = new QuestPart_RUT_PatternCores
            {
                inSignalEnable = slate.Get<string>("inSignal"),
                site = slate.Get<Site>("site"),
                enclaves = slate.Get<Faction>("enclaveFaction"),
                inSignalMapGenerated = QuestGenUtility.HardcodedSignalWithQuestID("site.MapGenerated"),
                inSignalReleased = QuestGenUtility.HardcodedSignalWithQuestID("wildDroids.Released"),
                outSignalHome = QuestGenUtility.HardcodedSignalWithQuestID(outSignalHome.GetValue(slate)),
                outSignalSold = QuestGenUtility.HardcodedSignalWithQuestID(outSignalSold.GetValue(slate)),
                outSignalDelivered = QuestGenUtility.HardcodedSignalWithQuestID(outSignalDelivered.GetValue(slate))
            };
            List<Thing> cores = slate.Get<List<Thing>>("cores");
            if (cores != null) part.cores.AddRange(cores);
            QuestGen.quest.AddPart(part);
        }
    }

    /// <summary>The broker's offer. Sell / Refuse act on the beat's part; Postpone keeps the letter. The part
    /// treats silence past the deadline as a refusal.</summary>
    public class ChoiceLetter_RUT_CoreBroker : ChoiceLetter
    {
        private QuestPart_RUT_PatternCores Part => quest?.PartsListForReading.OfType<QuestPart_RUT_PatternCores>().FirstOrDefault();

        public override bool CanShowInLetterStack
        {
            get
            {
                QuestPart_RUT_PatternCores part = Part;
                return base.CanShowInLetterStack && part != null && !part.decided && quest.State == QuestState.Ongoing;
            }
        }

        public override IEnumerable<DiaOption> Choices
        {
            get
            {
                if (ArchivedOnly)
                {
                    yield return Option_Close;
                    yield break;
                }
                QuestPart_RUT_PatternCores part = Part;
                DiaOption sell = new DiaOption("Sell the cores (" + UnfinishedLineSettings.coreSaleSilver + " silver; the Hive and the Enclaves turn on you)")
                {
                    action = delegate
                    {
                        part?.Sell();
                        Find.LetterStack.RemoveLetter(this);
                    },
                    resolveTree = true
                };
                if (part == null || part.decided) sell.Disable("already decided");
                yield return sell;
                DiaOption refuse = new DiaOption("Refuse; send the cores to the Enclaves")
                {
                    action = delegate
                    {
                        part?.Deliver();
                        Find.LetterStack.RemoveLetter(this);
                    },
                    resolveTree = true
                };
                if (part == null || part.decided) refuse.Disable("already decided");
                yield return refuse;
                yield return Option_Postpone;
            }
        }
    }

    /// <summary>
    /// The general path from a beat to its parent chain. A child's own signals carry the child's quest id
    /// (QuestGen.GenerateNewSignal: "Quest{id}.{name}"), so the parent never hears them; this part, on the
    /// child's <see cref="inSignal"/>, sends "Quest{parentId}.{parentSignal}", which is exactly the string a
    /// parent node's &lt;inSignal&gt;parentSignal&lt;/inSignal&gt; resolves to. No parent: nothing happens.
    /// </summary>
    public class QuestPart_RUT_SignalParent : QuestPart
    {
        public string inSignal;

        public string parentSignal;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal) return;
            Quest parent = quest?.parent;
            if (parent == null || parentSignal.NullOrEmpty()) return;
            Find.SignalManager.SendSignal(new Signal("Quest" + parent.id + "." + parentSignal));
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref parentSignal, "parentSignal");
        }
    }

    public class QuestNode_RUT_SignalParent : QuestNode
    {
        [NoTranslate]
        public SlateRef<string> inSignal;

        [NoTranslate]
        public SlateRef<string> parentSignal;

        protected override bool TestRunInt(Slate slate) => !parentSignal.GetValue(slate).NullOrEmpty();

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            string sig = inSignal.GetValue(slate);
            QuestGen.quest.AddPart(new QuestPart_RUT_SignalParent
            {
                inSignal = sig.NullOrEmpty() ? slate.Get<string>("inSignal") : QuestGenUtility.HardcodedSignalWithQuestID(sig),
                parentSignal = parentSignal.GetValue(slate)
            });
        }
    }
}
