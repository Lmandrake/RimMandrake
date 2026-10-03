using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_ENVOY_BEAT_1 — the brokered truce (design §2.2, §3.3; owner Q2 ruled 2026-10-03
    /// "both": the Enclaves broker a truce that holds the Hive while the chain runs, AND Hive goodwill
    /// rises beat by beat). The Hive starts hostile to the player; from the moment beat 2 is accepted
    /// until the chain ends, its goodwill is floored at 0 (Neutral), checked every 250 ticks, so the
    /// Hive does not raid while the two peoples are being brought together. The per-beat goodwill
    /// gains are ordinary QuestNode_ChangeFactionGoodwill nodes in each beat and accumulate on top.
    ///
    /// The truce ends three ways: the chain ends (any outcome; the spine's Cleanup), quietly, leaving
    /// goodwill where it stands; or the envoy is harmed / a betrayal, which ends it HOSTILE (the XML
    /// follows with ensureHostile) and fails the whole chain. No Harmony: a floor re-applied on a
    /// 250-tick check, so a large drop inside one window can flip the Hive hostile for a moment
    /// before the floor lifts it back to Neutral (relation hysteresis: Neutral again at goodwill 0).
    /// </summary>
    public class GameComponent_RUT_UnfinishedLine : GameComponent
    {
        public bool truceActive;

        public GameComponent_RUT_UnfinishedLine(Game game)
        {
        }

        public static GameComponent_RUT_UnfinishedLine Get => Current.Game?.GetComponent<GameComponent_RUT_UnfinishedLine>();

        public void StartTruce()
        {
            if (!UnfinishedLineSettings.brokeredTruceEnabled) return;
            truceActive = true;
            HoldFloor();
        }

        /// <summary>Ends the truce. <paramref name="hostile"/>: the Hive is turned hostile now.</summary>
        public void EndTruce(bool hostile)
        {
            truceActive = false;
            if (!hostile) return;
            Faction hive = LineFactions.Hive;
            if (hive != null && !hive.HostileTo(Faction.OfPlayer))
            {
                hive.SetRelationDirect(Faction.OfPlayer, FactionRelationKind.Hostile, true, "the brokered truce is broken");
            }
        }

        private void HoldFloor()
        {
            Faction hive = LineFactions.Hive;
            if (hive == null || hive.defeated) return;
            int gw = hive.GoodwillWith(Faction.OfPlayer);
            if (gw < 0)
            {
                hive.TryAffectGoodwillWith(Faction.OfPlayer, -gw, canSendMessage: false, canSendHostilityLetter: false);
            }
        }

        public override void GameComponentTick()
        {
            if (truceActive && Find.TickManager.TicksGame % 250 == 0)
            {
                HoldFloor();
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref truceActive, "truceActive", false);
        }
    }

    /// <summary>On its signal: starts the truce, or breaks it (Hive hostile) and fails the parent chain.</summary>
    public class QuestPart_RUT_Truce : QuestPart
    {
        public string inSignal;

        public bool breakIt;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal) return;
            GameComponent_RUT_UnfinishedLine comp = GameComponent_RUT_UnfinishedLine.Get;
            if (!breakIt)
            {
                comp?.StartTruce();
                return;
            }
            comp?.EndTruce(true);
            Quest chain = quest?.parent;
            if (chain != null && chain.State == QuestState.Ongoing)
            {
                chain.End(QuestEndOutcome.Fail);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref breakIt, "breakIt", false);
        }
    }

    /// <summary>XML verb for <see cref="QuestPart_RUT_Truce"/>. With no &lt;inSignal&gt; it uses the
    /// ambient one, i.e. fires when the beat is accepted (the shipped QuestNode_DroidRepairJob idiom).</summary>
    public class QuestNode_RUT_Truce : QuestNode
    {
        [NoTranslate]
        public SlateRef<string> inSignal;

        public bool breakIt;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            string sig = inSignal.GetValue(slate);
            QuestGen.quest.AddPart(new QuestPart_RUT_Truce
            {
                inSignal = sig.NullOrEmpty() ? slate.Get<string>("inSignal") : QuestGenUtility.HardcodedSignalWithQuestID(sig),
                breakIt = breakIt
            });
        }
    }
}
