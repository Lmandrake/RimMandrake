using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_FIRSTLIGHT_BEAT_1 — beat 5 "First Light" and the epilogue "The Unbolting of the Line"
    /// (design droid_mass_production_quest_chain_2026-10-02.md §2.5-2.6).
    ///
    /// The beat is stock XML (QuestNode_Raid, QuestNode_Delay, letters, End) plus three small nodes here:
    ///   QuestNode_RUT_FirstLightSetup  the strike faction (the Empire when it is hostile to you, else the first
    ///                                  hostile raiding faction, so the beat still runs off-campaign) and the
    ///                                  run / strike / hold timings from Mod Settings, into the slate.
    ///   QuestNode_RUT_PassAll          vanilla QuestPart_PassAll has no QuestNode: "the run is done AND the strike
    ///                                  is broken" is two signals that must both arrive.
    ///   QuestNode_RUT_LineFlag         records a chain fact on GameComponent_RUT_UnfinishedLine for consumers that
    ///                                  do not exist yet: the construction branch opening (TECHPRINT_FACTION_GATING_1
    ///                                  reads constructionBranchOpen) and the Empire's first notice of the Hive
    ///                                  (Q4=A: the Geonosian Alliance arc is separate but linked; it reads
    ///                                  empireNoticedHive).
    ///
    /// Where the run happens: the strike comes to your colony, and the chosen site's faction sends defenders to hold beside
    /// you (UNFINISHED_LINE_SITE_BEATS_1, QuestNode_RUT_SiteAllies). A separate defence-site map is NOT built, so the
    /// failure is "the strike still holds your colony this long after the run ends" (holdDays) rather than the
    /// line core's destruction (the core building is P6, which Q1=A did not order).
    /// </summary>
    public class QuestNode_RUT_FirstLightSetup : QuestNode
    {
        [NoTranslate] public string storeFactionAs = "enemyFaction";
        [NoTranslate] public string storeRunTicksAs = "runTicks";
        [NoTranslate] public string storeStrikeDelayAs = "strikeDelayTicks";
        [NoTranslate] public string storeHoldTicksAs = "holdTicks";

        public static Faction StrikeFaction()
        {
            Faction empire = Faction.OfEmpire;
            if (empire != null && !empire.defeated && empire.HostileTo(Faction.OfPlayer))
            {
                return empire;
            }
            return Find.FactionManager.AllFactionsVisible
                .Where(f => !f.defeated && !f.IsPlayer && f.HostileTo(Faction.OfPlayer) && f.def.humanlikeFaction
                    && f.def.pawnGroupMakers != null && f.def.pawnGroupMakers.Any(g => g.kindDef == PawnGroupKindDefOf.Combat))
                .OrderBy(f => f.def.techLevel >= TechLevel.Industrial ? 0 : 1)
                .FirstOrDefault();
        }

        private void Store(Slate slate, Faction f)
        {
            slate.Set(storeFactionAs, f);
            slate.Set(storeRunTicksAs, (int)(UnfinishedLineSettings.firstLightRunDays * GenDate.TicksPerDay));
            slate.Set(storeStrikeDelayAs, (int)(UnfinishedLineSettings.firstLightStrikeDelayHours * GenDate.TicksPerHour));
            slate.Set(storeHoldTicksAs, (int)(UnfinishedLineSettings.firstLightHoldDays * GenDate.TicksPerDay));
        }

        protected override bool TestRunInt(Slate slate)
        {
            Faction f = StrikeFaction();
            if (f == null) return false;
            Store(slate, f);
            return true;
        }

        protected override void RunInt()
        {
            Store(QuestGen.slate, StrikeFaction());
        }
    }

    public class QuestNode_RUT_PassAll : QuestNode
    {
        [NoTranslate] public List<string> inSignals = new List<string>();
        [NoTranslate] public string outSignal;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            QuestPart_PassAll part = new QuestPart_PassAll
            {
                outSignal = QuestGenUtility.HardcodedSignalWithQuestID(outSignal)
            };
            foreach (string s in inSignals)
            {
                part.inSignals.Add(QuestGenUtility.HardcodedSignalWithQuestID(s));
            }
            QuestGen.quest.AddPart(part);
        }
    }

    public class QuestPart_RUT_LineFlag : QuestPart
    {
        public string inSignal;
        public string flag;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag == inSignal)
            {
                GameComponent_RUT_UnfinishedLine.Get?.SetFlag(flag);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref flag, "flag");
        }
    }

    public class QuestNode_RUT_LineFlag : QuestNode
    {
        [NoTranslate] public string inSignal;
        [NoTranslate] public string flag;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new QuestPart_RUT_LineFlag
            {
                inSignal = inSignal.NullOrEmpty() ? slate.Get<string>("inSignal") : QuestGenUtility.HardcodedSignalWithQuestID(inSignal),
                flag = flag
            });
        }
    }

    // jawa/static_call proof (validation.py, first_light).
    public static class UnfinishedLineFirstLightProof
    {
        public static string ProofFirstLightSetup()
        {
            Faction f = QuestNode_RUT_FirstLightSetup.StrikeFaction();
            GameComponent_RUT_UnfinishedLine gc = GameComponent_RUT_UnfinishedLine.Get;
            return "STRIKE " + (f == null ? "none" : f.def.defName + " hostile=" + f.HostileTo(Faction.OfPlayer))
                + " run=" + UnfinishedLineSettings.firstLightRunDays + "d flags branch=" + gc?.constructionBranchOpen
                + " noticed=" + gc?.empireNoticedHive + " done=" + gc?.lineCompleted;
        }
    }
}
