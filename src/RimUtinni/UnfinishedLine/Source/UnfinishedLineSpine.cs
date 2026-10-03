using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_SPINE_COUNT_1 — the chain's spine (design §3.3). Vanilla's subquest generators
    /// (Relic Hunt) pick the next child AT RANDOM; this one walks <see cref="beats"/> in order:
    /// the next beat is always beats[number of children that ended in success]. A child that fails
    /// or whose offer expires is simply offered again after the next interval, until that beat has
    /// failed more than <see cref="UnfinishedLineSettings.failuresAllowedPerBeat"/> times, which
    /// breaks the chain (<see cref="outSignalBroken"/>). Reaching <see cref="QuestPart_SubquestGenerator.maxSuccessfulSubquests"/>
    /// (the chain's full length, 5) completes the part and fires its outSignalsCompleted.
    ///
    /// <see cref="beats"/> holds only the beats that are BUILT. While the chain is longer than that
    /// list the part idles after the last built beat, silently, rather than completing early.
    /// </summary>
    public class QuestPart_RUT_SequentialSubquests : QuestPart_SubquestGenerator
    {
        public List<QuestScriptDef> beats = new List<QuestScriptDef>();

        public IntRange betweenBeats = new IntRange(300000, 600000);

        public string outSignalBroken;

        public bool broken;

        public int SuccessCount => SuccessfulSubquestCount;

        public QuestScriptDef CurrentBeat => SuccessCount < beats.Count ? beats[SuccessCount] : null;

        public int FailuresOf(QuestScriptDef beat)
        {
            return beat == null ? 0 : quest.GetSubquests(QuestState.EndedFailed).Count(q => q.root == beat);
        }

        public int PendingCount => quest.GetSubquests().Count(q => q.State == QuestState.Ongoing || q.State == QuestState.NotYetAccepted);

        protected override bool CanGenerateSubquest => !broken && CurrentBeat != null && base.CanGenerateSubquest;

        public override void QuestPartTick()
        {
            if (broken) return;
            if (Find.TickManager.TicksGame % 250 == 0)
            {
                QuestScriptDef beat = CurrentBeat;
                if (beat != null && PendingCount == 0 && FailuresOf(beat) > UnfinishedLineSettings.failuresAllowedPerBeat)
                {
                    Break();
                    return;
                }
            }
            base.QuestPartTick();
        }

        private void Break()
        {
            broken = true;
            if (!outSignalBroken.NullOrEmpty())
            {
                Find.SignalManager.SendSignal(new Signal(outSignalBroken));
            }
        }

        protected override Slate InitSlate()
        {
            Slate slate = new Slate();
            Map home = Find.AnyPlayerHomeMap;
            slate.Set("points", home != null ? StorytellerUtility.DefaultThreatPointsNow(home)
                                             : StorytellerUtility.DefaultThreatPointsNow(Find.World));
            return slate;
        }

        private IIncidentTarget Target => (IIncidentTarget)Find.AnyPlayerHomeMap ?? Find.World;

        protected override QuestScriptDef GetNextSubquestDef()
        {
            QuestScriptDef beat = CurrentBeat;
            if (beat == null || !beat.CanRun(InitSlate(), Target)) return null;
            return beat;
        }

        /// <summary>Generates the current beat. A beat that cannot run right now (its faction turned
        /// hostile, no settlement) is not an error: it is tried again after the next interval, so this
        /// returns true and logs nothing.</summary>
        protected override bool TryGenerateSubquest()
        {
            QuestScriptDef beat = GetNextSubquestDef();
            if (beat == null) return true;
            Quest child = QuestUtility.GenerateQuestAndMakeAvailable(beat, InitSlate());
            child.parent = quest;
            if (!child.hidden && child.root.sendAvailableLetter)
            {
                QuestUtility.SendLetterQuestAvailable(child);
            }
            interval = betweenBeats;
            return true;
        }

        /// <summary>Dev/bridge: offer the current beat now, skipping the wait. Returns the beat offered,
        /// or why none was.</summary>
        public string ForceNextBeat()
        {
            if (State != QuestPartState.Enabled) return "REFUSED: chain not accepted (part " + State + ")";
            if (broken) return "REFUSED: chain broken";
            QuestScriptDef beat = CurrentBeat;
            if (beat == null) return "REFUSED: no built beat after " + SuccessCount + " successes";
            if (PendingCount > 0) return "REFUSED: a beat is already offered or running";
            if (!beat.CanRun(InitSlate(), Target)) return "REFUSED: " + beat.defName + " cannot run now (TestRun false)";
            TryGenerateSubquest();
            return "OFFERED " + beat.defName;
        }

        public string Describe()
        {
            QuestScriptDef beat = CurrentBeat;
            return "part " + State + " | successes " + SuccessCount + "/" + maxSuccessfulSubquests
                + " | built beats " + beats.Count + " | current " + (beat?.defName ?? "none")
                + " | failures " + FailuresOf(beat) + " | pending " + PendingCount + " | broken " + broken;
        }

        /// <summary>The chain is over, whatever the outcome: a truce still running ends quietly
        /// (a hostile ending has already ended it).</summary>
        public override void Cleanup()
        {
            base.Cleanup();
            GameComponent_RUT_UnfinishedLine.Get?.EndTruce(false);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref beats, "beats", LookMode.Def);
            Scribe_Values.Look(ref betweenBeats, "betweenBeats");
            Scribe_Values.Look(ref outSignalBroken, "outSignalBroken");
            Scribe_Values.Look(ref broken, "broken", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && beats == null)
            {
                beats = new List<QuestScriptDef>();
            }
        }
    }

    /// <summary>The parent's one custom verb: emits <see cref="QuestPart_RUT_SequentialSubquests"/>,
    /// enabled when the parent is accepted. Its out-signals are named in XML so the parent's
    /// QuestNode_End branches stay editable without a rebuild (rimworld-quests §9).</summary>
    public class QuestNode_RUT_UnfinishedLineSpine : QuestNode
    {
        public List<QuestScriptDef> beats = new List<QuestScriptDef>();

        public int totalBeats = 5;

        [NoTranslate]
        public string outSignalComplete;

        [NoTranslate]
        public string outSignalBroken;

        protected override bool TestRunInt(Slate slate)
        {
            return beats.Count > 0 && LineFactions.Enclaves != null && LineFactions.Hive != null;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            int min = UnfinishedLineSettings.daysBetweenBeatsMin;
            int max = UnfinishedLineSettings.daysBetweenBeatsMax < min ? min : UnfinishedLineSettings.daysBetweenBeatsMax;
            QuestPart_RUT_SequentialSubquests part = new QuestPart_RUT_SequentialSubquests
            {
                inSignalEnable = slate.Get<string>("inSignal"),
                // The first beat follows acceptance within a day or two; later ones wait the setting.
                interval = new IntRange(60000, 120000),
                betweenBeats = new IntRange(min * 60000, max * 60000),
                maxActiveSubquests = 1,
                maxSuccessfulSubquests = totalBeats,
                outSignalBroken = outSignalBroken.NullOrEmpty() ? null : QuestGenUtility.HardcodedSignalWithQuestID(outSignalBroken)
            };
            part.beats.AddRange(beats.Where(b => b != null));
            part.subquestDefs.AddRange(part.beats);
            if (!outSignalComplete.NullOrEmpty())
            {
                part.outSignalsCompleted.Add(QuestGenUtility.HardcodedSignalWithQuestID(outSignalComplete));
            }
            QuestGen.quest.AddPart(part);
        }
    }

    /// <summary>Stores the Free Droid Enclaves, the Geonosian Foundry Hive, and the Enclave settlement
    /// nearest the colony, under the names given. TestRun fails (the quest is not offered) when the
    /// Enclaves are missing, hostile, or have no settlement, or the Hive is missing.</summary>
    public class QuestNode_RUT_GetLineFactions : QuestNode
    {
        [NoTranslate]
        public string storeEnclaveAs = "enclaveFaction";

        [NoTranslate]
        public string storeHiveAs = "hiveFaction";

        [NoTranslate]
        public string storeSettlementAs = "settlement";

        private static bool Resolve(Slate slate, out Faction enclaves, out Faction hive, out Settlement settlement)
        {
            enclaves = LineFactions.Enclaves;
            hive = LineFactions.Hive;
            Map map = slate.Get<Map>("map");
            settlement = LineFactions.NearestSettlement(enclaves, map != null ? map.Tile : PlanetTile.Invalid);
            return enclaves != null && hive != null && settlement != null && !enclaves.HostileTo(Faction.OfPlayer);
        }

        protected override bool TestRunInt(Slate slate)
        {
            if (!Resolve(slate, out Faction e, out Faction h, out Settlement s)) return false;
            Store(slate, e, h, s);
            return true;
        }

        protected override void RunInt()
        {
            Resolve(QuestGen.slate, out Faction e, out Faction h, out Settlement s);
            Store(QuestGen.slate, e, h, s);
        }

        private void Store(Slate slate, Faction e, Faction h, Settlement s)
        {
            if (!storeEnclaveAs.NullOrEmpty()) slate.Set(storeEnclaveAs, e);
            if (!storeHiveAs.NullOrEmpty()) slate.Set(storeHiveAs, h);
            if (!storeSettlementAs.NullOrEmpty()) slate.Set(storeSettlementAs, s);
        }
    }
}
