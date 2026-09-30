using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // WASTELAND_GPT_ENRICHMENT_1 §4 — the RITE OF TIPPING. A supervised waste
    // convoy offers silver and access (goodwill) if the colony licenses a marked
    // tipping pad (RM_WasteTippingPad + RM_CompTippingPad). Accepted casks are the
    // physical RM_WasteCask from §3: they can leak, feed processors through the
    // sealed cask bay, enter the bay, or be illegally reburied.
    //
    //   QuestScriptDef RM_Quest_RiteOfTipping (XML) -> QuestNode_RM_TippingContract
    //     -> QuestPart_RM_TippingContract, which runs the deliveries, the
    //     evidence ask (ChoiceLetter_RM_TippingEvidence) and the containment grant.
    //   IncidentDef RM_RiteOfTipping offers it (IncidentWorker_GiveQuest).
    //
    // Tier: this is RM_ (franchise-free), so the factions come from
    // RM_TippingQuestExtension on the QuestScriptDef. Unset, the contract picks
    // any non-hostile humanlike factions. The campaign's Junkers / Wildsteam /
    // Deepwater are set by the Utinni patch layer, never named here.
    // ════════════════════════════════════════════════════════════════════

    public class RM_TippingQuestExtension : DefModExtension
    {
        /// <summary>Who runs the convoy. Empty = any non-hostile humanlike faction.</summary>
        public List<FactionDef> convoyFactions = new List<FactionDef>();
        /// <summary>Who may ask for evidence. Empty = another non-hostile faction, if any.</summary>
        public List<FactionDef> evidenceFactions = new List<FactionDef>();
        /// <summary>Who may finance proper containment. Empty = another non-hostile faction, if any.</summary>
        public List<FactionDef> financeFactions = new List<FactionDef>();

        public IntRange casksPerDelivery = new IntRange(3, 5);
        public int deliveries = 3;
        public float deliveryIntervalDays = 4f;
        public int silverPerCask = 55;
        public int goodwillPerDelivery = 6;
        public int evidenceGoodwill = 15;
        public int evidenceRefusedGoodwill = -5;
        public int evidenceConvoyGoodwill = -10;
        public int financeGrantSilver = 450;
        public int financeGoodwill = 8;
        public float reburialDiscoveryChance = 0.5f;
        public int reburialGoodwill = -15;
        /// <summary>Missed deliveries (no licensed pad) before the contract fails.</summary>
        public int missedDeliveriesAllowed = 1;
    }

    /// <summary>The tipping pad: a marker post whose comp licenses the area around it.</summary>
    public class RM_CompProperties_TippingPad : CompProperties
    {
        public int radius = 3;

        public RM_CompProperties_TippingPad()
        {
            compClass = typeof(RM_CompTippingPad);
        }
    }

    public class RM_CompTippingPad : ThingComp
    {
        public RM_CompProperties_TippingPad Props => (RM_CompProperties_TippingPad)props;

        public CellRect Area => CellRect.CenteredOn(parent.Position, Props.radius).ClipInsideMap(parent.Map);

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            if (parent.Spawned)
            {
                GenDraw.DrawFieldEdges(Area.Cells.ToList(), new Color(0.75f, 0.85f, 0.35f));
            }
        }

        public override string CompInspectStringExtra()
        {
            QuestPart_RM_TippingContract c = RM_TippingUtility.ActiveContracts()
                .FirstOrDefault(p => p.map == parent.Map);
            if (c == null)
            {
                return "Tipping pad: unlicensed. A waste convoy may offer a licence.";
            }
            return "Licensed tipping pad (" + (c.convoyFaction?.Name ?? "convoy") + "): "
                 + c.deliveriesDone + " of " + c.deliveries + " deliveries tipped.";
        }

        public static RM_CompTippingPad FindPad(Map map)
        {
            if (map == null)
            {
                return null;
            }
            List<Building> list = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < list.Count; i++)
            {
                RM_CompTippingPad pad = list[i].GetComp<RM_CompTippingPad>();
                if (pad != null)
                {
                    return pad;
                }
            }
            return null;
        }
    }

    public static class RM_TippingUtility
    {
        public static IEnumerable<QuestPart_RM_TippingContract> ActiveContracts()
        {
            if (Find.QuestManager == null)
            {
                yield break;
            }
            List<Quest> quests = Find.QuestManager.QuestsListForReading;
            for (int i = 0; i < quests.Count; i++)
            {
                if (quests[i].State != QuestState.Ongoing)
                {
                    continue;
                }
                List<QuestPart> parts = quests[i].PartsListForReading;
                for (int j = 0; j < parts.Count; j++)
                {
                    if (parts[j] is QuestPart_RM_TippingContract c && c.State == QuestPartState.Enabled)
                    {
                        yield return c;
                    }
                }
            }
        }

        /// <summary>Called by RM_CompWasteCask.Rebury (§3).</summary>
        public static void Notify_IllegalReburial(Map map, IntVec3 cell)
        {
            foreach (QuestPart_RM_TippingContract c in ActiveContracts().ToList())
            {
                if (c.map == map)
                {
                    c.Notify_IllegalReburial(cell);
                }
            }
        }

        public static bool Usable(Faction f)
        {
            return f != null && !f.IsPlayer && !f.defeated && !f.Hidden && f.def.humanlikeFaction
                && !f.HostileTo(Faction.OfPlayer) && !f.temporary;
        }

        public static Faction Pick(List<FactionDef> defs, params Faction[] exclude)
        {
            IEnumerable<Faction> pool = Find.FactionManager.AllFactionsListForReading
                .Where(f => Usable(f) && !exclude.Contains(f));
            if (!defs.NullOrEmpty())
            {
                pool = pool.Where(f => defs.Contains(f.def));
            }
            return pool.TryRandomElement(out Faction pick) ? pick : null;
        }
    }

    /// <summary>
    /// Builds the contract. Writes slate vars <c>convoyFaction</c>, <c>convoyFactionName</c>,
    /// <c>evidenceFactionName</c>, <c>financeFactionName</c>, <c>casksPerDelivery</c>,
    /// <c>deliveries</c>, <c>silverPerDelivery</c> for the text packs.
    /// </summary>
    public class QuestNode_RM_TippingContract : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignalEnable;
        [NoTranslate] public SlateRef<string> outSignalSuccess;
        [NoTranslate] public SlateRef<string> outSignalFail;

        private static RM_TippingQuestExtension Ext =>
            QuestGen.Root?.GetModExtension<RM_TippingQuestExtension>() ?? new RM_TippingQuestExtension();

        protected override bool TestRunInt(Slate slate)
        {
            if (!RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.tippingEnabled)
            {
                return false;
            }
            return slate.Get<Map>("map") != null && RM_TippingUtility.Pick(Ext.convoyFactions) != null;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            RM_TippingQuestExtension ext = Ext;
            Map map = slate.Get<Map>("map");
            Faction convoy = RM_TippingUtility.Pick(ext.convoyFactions);
            Faction evidence = RM_TippingUtility.Pick(ext.evidenceFactions, convoy);
            Faction finance = RM_TippingUtility.Pick(ext.financeFactions, convoy, evidence);
            int casks = ext.casksPerDelivery.RandomInRange;

            QuestPart_RM_TippingContract part = new QuestPart_RM_TippingContract
            {
                inSignalEnable = QuestGenUtility.HardcodedSignalWithQuestID(inSignalEnable.GetValue(slate)) ?? slate.Get<string>("inSignal"),
                map = map,
                convoyFaction = convoy,
                evidenceFaction = evidence,
                financeFaction = finance,
                casksPerDelivery = casks,
                deliveries = ext.deliveries,
                silverPerDelivery = casks * ext.silverPerCask,
                outSignalSuccess = QuestGenUtility.HardcodedSignalWithQuestID(outSignalSuccess.GetValue(slate)),
                outSignalFail = QuestGenUtility.HardcodedSignalWithQuestID(outSignalFail.GetValue(slate)),
            };
            QuestGen.quest.AddPart(part);

            slate.Set("convoyFaction", convoy);
            slate.Set("convoyFactionName", convoy?.Name ?? "a waste convoy");
            slate.Set("evidenceFactionName", evidence?.Name ?? "nobody");
            slate.Set("financeFactionName", finance?.Name ?? "nobody");
            slate.Set("casksPerDelivery", casks);
            slate.Set("deliveries", ext.deliveries);
            slate.Set("silverPerDelivery", part.silverPerDelivery);
            slate.Set("hasEvidence", evidence != null);
            slate.Set("hasFinance", finance != null);
        }
    }

    public class QuestPart_RM_TippingContract : QuestPartActivable
    {
        public Map map;
        public Faction convoyFaction;
        public Faction evidenceFaction;
        public Faction financeFaction;
        public int casksPerDelivery = 4;
        public int deliveries = 3;
        public int silverPerDelivery = 200;
        public int deliveriesDone;
        private int missed;
        private int nextDeliveryTick = -1;
        private bool evidenceAsked;
        private bool financeGranted;
        private bool financeHinted;
        public string outSignalSuccess;
        public string outSignalFail;

        private RM_TippingQuestExtension Ext =>
            quest?.root?.GetModExtension<RM_TippingQuestExtension>() ?? new RM_TippingQuestExtension();

        public override IEnumerable<Faction> InvolvedFactions
        {
            get
            {
                if (convoyFaction != null) yield return convoyFaction;
                if (evidenceFaction != null) yield return evidenceFaction;
                if (financeFaction != null) yield return financeFaction;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref map, "map");
            Scribe_References.Look(ref convoyFaction, "convoyFaction");
            Scribe_References.Look(ref evidenceFaction, "evidenceFaction");
            Scribe_References.Look(ref financeFaction, "financeFaction");
            Scribe_Values.Look(ref casksPerDelivery, "casksPerDelivery", 4);
            Scribe_Values.Look(ref deliveries, "deliveries", 3);
            Scribe_Values.Look(ref silverPerDelivery, "silverPerDelivery", 200);
            Scribe_Values.Look(ref deliveriesDone, "deliveriesDone", 0);
            Scribe_Values.Look(ref missed, "missed", 0);
            Scribe_Values.Look(ref nextDeliveryTick, "nextDeliveryTick", -1);
            Scribe_Values.Look(ref evidenceAsked, "evidenceAsked", false);
            Scribe_Values.Look(ref financeGranted, "financeGranted", false);
            Scribe_Values.Look(ref financeHinted, "financeHinted", false);
            Scribe_Values.Look(ref outSignalSuccess, "outSignalSuccess");
            Scribe_Values.Look(ref outSignalFail, "outSignalFail");
        }

        protected override void Enable(SignalArgs receivedArgs)
        {
            base.Enable(receivedArgs);
            nextDeliveryTick = Find.TickManager.TicksGame + GenDate.TicksPerDay;
            string padLine = RM_CompTippingPad.FindPad(map) != null
                ? "Your tipping pad is marked; the first load comes in about a day."
                : "Build a waste tipping pad (Misc) before the first load arrives in about a day, or the convoy turns back.";
            Find.LetterStack.ReceiveLetter("Tipping licensed",
                (convoyFaction?.Name ?? "The convoy") + " will tip " + casksPerDelivery + " waste casks on your pad, "
              + deliveries + " times, and pay " + silverPerDelivery + " silver each time. " + padLine
              + "\n\nThe casks stay yours: they can leak if breached, they can feed tamed processor animals "
              + "through a sealed cask bay, and they can be reburied — illegally.",
                LetterDefOf.NeutralEvent, new LookTargets(RM_CompTippingPad.FindPad(map)?.parent), convoyFaction, quest);
        }

        public override void QuestPartTick()
        {
            base.QuestPartTick();
            if (Find.TickManager.TicksGame % GenTicks.TickRareInterval != 0)
            {
                return;
            }
            if (map == null || convoyFaction == null || convoyFaction.HostileTo(Faction.OfPlayer))
            {
                Fail("The tipping contract is void: " + (convoyFaction?.Name ?? "the convoy") + " is no longer dealing with you.");
                return;
            }
            if (Find.TickManager.TicksGame >= nextDeliveryTick)
            {
                TryDeliver();
                nextDeliveryTick = Find.TickManager.TicksGame + Mathf.RoundToInt(Ext.deliveryIntervalDays * GenDate.TicksPerDay);
            }
        }

        /// <summary>One convoy load. Public so a debug action / state read can drive it.</summary>
        public bool TryDeliver()
        {
            RM_CompTippingPad pad = RM_CompTippingPad.FindPad(map);
            if (pad == null)
            {
                missed++;
                convoyFaction.TryAffectGoodwillWith(Faction.OfPlayer, -5, true, true, HistoryEventDefOf.QuestGoodwillReward);
                if (missed > Ext.missedDeliveriesAllowed)
                {
                    Fail("The waste convoy found no licensed tipping pad again and has cancelled the contract.");
                }
                else
                {
                    Messages.Message("The waste convoy found no licensed tipping pad and turned back. Build one before the next load.",
                        MessageTypeDefOf.NegativeEvent);
                }
                return false;
            }
            List<Thing> load = new List<Thing>();
            ThingDef caskDef = RM_WastelandDefOf.RM_WasteCask;
            for (int i = 0; i < casksPerDelivery; i++)
            {
                load.Add(ThingMaker.MakeThing(caskDef));
            }
            Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
            silver.stackCount = silverPerDelivery;
            load.Add(silver);
            DropPodUtility.DropThingsNear(pad.parent.Position, map, load, 110, false, false, true, false, true, convoyFaction);
            convoyFaction.TryAffectGoodwillWith(Faction.OfPlayer, Ext.goodwillPerDelivery, true, true, HistoryEventDefOf.QuestGoodwillReward);
            deliveriesDone++;
            Messages.Message((convoyFaction.Name ?? "The convoy") + " has tipped " + casksPerDelivery + " waste casks on your pad and paid "
                           + silverPerDelivery + " silver (" + deliveriesDone + " of " + deliveries + ").",
                new LookTargets(pad.parent), MessageTypeDefOf.PositiveEvent);

            if (!evidenceAsked && evidenceFaction != null && RM_TippingUtility.Usable(evidenceFaction))
            {
                evidenceAsked = true;
                AskEvidence(pad);
            }
            CheckFinance();
            if (deliveriesDone >= deliveries)
            {
                Complete();
                if (!outSignalSuccess.NullOrEmpty())
                {
                    Find.SignalManager.SendSignal(new Signal(outSignalSuccess));
                }
            }
            return true;
        }

        private void AskEvidence(RM_CompTippingPad pad)
        {
            LetterDef def = DefDatabase<LetterDef>.GetNamedSilentFail("RM_TippingEvidence");
            if (def == null)
            {
                return;
            }
            ChoiceLetter_RM_TippingEvidence letter = (ChoiceLetter_RM_TippingEvidence)LetterMaker.MakeLetter(
                "Evidence wanted",
                evidenceFaction.Name + " have heard what " + convoyFaction.Name + " are tipping on your land, and want "
              + "proof: one of the casks, handed over for testing. They will remember the favour. "
              + convoyFaction.Name + " will remember it too.",
                def, new LookTargets(pad.parent), evidenceFaction, quest);
            letter.contractQuest = quest;
            letter.StartTimeout(GenDate.TicksPerDay * 2);
            Find.LetterStack.ReceiveLetter(letter);
        }

        /// <summary>Hand one cask over as evidence. Returns false if no cask is on the map.</summary>
        public bool GiveEvidence()
        {
            Thing cask = RM_CompWasteCask.AllCasks(map).FirstOrDefault(t => t.Spawned);
            if (cask == null)
            {
                Messages.Message("There is no waste cask on the map to hand over.", MessageTypeDefOf.RejectInput, historical: false);
                return false;
            }
            IntVec3 at = cask.Position;
            cask.Destroy(DestroyMode.Vanish);
            FleckMaker.ThrowDustPuff(at, map, 1f);
            evidenceFaction.TryAffectGoodwillWith(Faction.OfPlayer, Ext.evidenceGoodwill, true, true, HistoryEventDefOf.QuestGoodwillReward);
            convoyFaction.TryAffectGoodwillWith(Faction.OfPlayer, Ext.evidenceConvoyGoodwill, true, true, HistoryEventDefOf.QuestGoodwillReward);
            Messages.Message("A sample cask has gone to " + evidenceFaction.Name + " as evidence.", MessageTypeDefOf.NeutralEvent);
            return true;
        }

        public void RefuseEvidence()
        {
            evidenceFaction?.TryAffectGoodwillWith(Faction.OfPlayer, Ext.evidenceRefusedGoodwill, true, true, HistoryEventDefOf.QuestGoodwillReward);
        }

        private void CheckFinance()
        {
            if (financeGranted || financeFaction == null || !RM_TippingUtility.Usable(financeFaction))
            {
                return;
            }
            Building bay = map.listerBuildings.allBuildingsColonist.FirstOrDefault(b => b.GetComp<RM_CompWasteContainment>() != null);
            if (bay == null)
            {
                if (!financeHinted)
                {
                    financeHinted = true;
                    Find.LetterStack.ReceiveLetter("Containment offered",
                        financeFaction.Name + " will pay " + Ext.financeGrantSilver + " silver toward proper containment "
                      + "the first time a waste load arrives and you have a sealed cask bay standing.",
                        LetterDefOf.NeutralEvent, null, financeFaction, quest);
                }
                return;
            }
            financeGranted = true;
            Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
            silver.stackCount = Ext.financeGrantSilver;
            DropPodUtility.DropThingsNear(bay.Position, map, new List<Thing> { silver }, 110, false, false, true, false, true, financeFaction);
            financeFaction.TryAffectGoodwillWith(Faction.OfPlayer, Ext.financeGoodwill, true, true, HistoryEventDefOf.QuestGoodwillReward);
            Find.LetterStack.ReceiveLetter("Containment financed",
                financeFaction.Name + " have sent " + Ext.financeGrantSilver + " silver for your sealed cask bay.",
                LetterDefOf.PositiveEvent, new LookTargets(bay), financeFaction, quest);
        }

        public void Notify_IllegalReburial(IntVec3 cell)
        {
            RM_TippingQuestExtension ext = Ext;
            foreach (Faction f in new[] { evidenceFaction, financeFaction })
            {
                if (f != null && RM_TippingUtility.Usable(f) && Rand.Chance(ext.reburialDiscoveryChance))
                {
                    f.TryAffectGoodwillWith(Faction.OfPlayer, ext.reburialGoodwill, true, true, HistoryEventDefOf.QuestGoodwillReward,
                        new GlobalTargetInfo(cell, map));
                    Messages.Message(f.Name + " found out about the reburied waste cask.",
                        new LookTargets(new TargetInfo(cell, map)), MessageTypeDefOf.NegativeEvent);
                }
            }
        }

        private void Fail(string why)
        {
            if (State != QuestPartState.Enabled)
            {
                return;
            }
            Messages.Message(why, MessageTypeDefOf.NegativeEvent);
            Disable();
            if (!outSignalFail.NullOrEmpty())
            {
                Find.SignalManager.SendSignal(new Signal(outSignalFail));
            }
        }

        public override void Notify_FactionRemoved(Faction faction)
        {
            base.Notify_FactionRemoved(faction);
            if (faction == evidenceFaction) evidenceFaction = null;
            if (faction == financeFaction) financeFaction = null;
            if (faction == convoyFaction) convoyFaction = null;
        }
    }

    /// <summary>The evidence ask: hand over a cask, or refuse.</summary>
    public class ChoiceLetter_RM_TippingEvidence : ChoiceLetter
    {
        public Quest contractQuest;

        private QuestPart_RM_TippingContract Contract =>
            contractQuest?.PartsListForReading.OfType<QuestPart_RM_TippingContract>().FirstOrDefault();

        public override IEnumerable<DiaOption> Choices
        {
            get
            {
                if (ArchivedOnly)
                {
                    yield return Option_Close;
                    yield break;
                }
                QuestPart_RM_TippingContract c = Contract;
                DiaOption give = new DiaOption("Hand over a cask")
                {
                    action = () =>
                    {
                        if (c != null && c.GiveEvidence())
                        {
                            Find.LetterStack.RemoveLetter(this);
                        }
                    },
                    resolveTree = true
                };
                if (c == null)
                {
                    give.Disable("the contract has ended");
                }
                yield return give;
                yield return new DiaOption("Refuse")
                {
                    action = () =>
                    {
                        c?.RefuseEvidence();
                        Find.LetterStack.RemoveLetter(this);
                    },
                    resolveTree = true
                };
                yield return Option_Postpone;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref contractQuest, "contractQuest");
        }
    }
}
