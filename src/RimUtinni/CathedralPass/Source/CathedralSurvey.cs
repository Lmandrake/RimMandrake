using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.CathedralPass
{
    // CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1 — the Imperial survey on the plates (arc spec §4, card A4).
    //
    // A survey team of the Empire hunting the clan (the pursuit spine's own faction: EmpirePursuit's pursuing faction
    // when that mod has one, else vanilla Empire; no faction is invented) hails the ship from Cathedral-adjacent
    // ground and asks what the clan's crews have seen. One dialog, three answers:
    //   (b) the guild's usual answer   -> quest ends Success  (GM blackboard: a large Regard gain, Imperial Heat untouched)
    //   (c) tell them about the plates -> quest ends Fail     (GM blackboard: an exposure-pressure input, §6.1)
    //   (a) leave the hail unanswered, or let it lapse        -> quest ends Unknown (nothing moves)
    // The quest is hidden (no Quests-tab row, so no "succeeded/failed" verdict is ever shown to the player) and
    // auto-accepted; WHEN it fires is the blackboard's call (gm_blackboard_shadow.py, advance_cathedral_survey),
    // through the baseChance-0 RUT_GiveQuest_CathedralSurveyMisdirection incident. Fallback text is the whole
    // text; no LLM is called. Nothing here touches Imperial Heat, the EmpirePursuit visibility dial or any goodwill.

    public enum SurveyAnswer { Dull, Pointed, Silent }

    /// <summary>The faction whose survey team it is: the pursuing faction of EmpirePursuit's ladder (soft-bound by
    /// reflection, as EmpirePursuit binds FlowWorks, so neither mod depends on the other), else vanilla Empire. Null when
    /// neither exists or it is defeated: then the quest cannot run.</summary>
    public static class SurveyFaction
    {
        private static bool bound;
        private static PropertyInfo partProp;
        private static FieldInfo factionField;

        public static Faction Resolve()
        {
            Faction f = PursuitFaction() ?? Faction.OfEmpire;
            if (f == null || f.defeated || f.IsPlayer) return null;
            return f;
        }

        private static Faction PursuitFaction()
        {
            if (!bound)
            {
                bound = true;
                Type search = AccessTools.TypeByName("RuthlessPursuingMechanoids.EmpireSearch");
                Type part = AccessTools.TypeByName("RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids");
                partProp = search == null ? null : AccessTools.Property(search, "Part");
                factionField = part == null ? null : AccessTools.Field(part, "PursuitFaction");
            }
            if (partProp == null || factionField == null || Current.Game == null) return null;
            try
            {
                object p = partProp.GetValue(null);
                return p == null ? null : factionField.GetValue(p) as Faction;
            }
            catch (Exception)
            {
                return null;
            }
        }
    }

    /// <summary>The GiveQuest incident for the survey, gated on the survey toggle.</summary>
    public class IncidentWorker_GiveQuest_CathedralSurvey : IncidentWorker_GiveQuest
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            return CathedralPassSettings.cathedralSurveyEnabled && base.CanFireNowSub(parms);
        }
    }

    /// <summary>Adds the survey hail: the dialog letter sent when the quest starts, its three answers and the signal
    /// each sends. {FACTION} in label/text is replaced by the survey faction's name.</summary>
    public class RUT_QuestNode_SurveyHail : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<string> letterLabel;
        public SlateRef<string> letterText;
        public SlateRef<string> answerDullLabel;
        public SlateRef<string> answerPointedLabel;
        public SlateRef<string> answerSilentLabel;
        [NoTranslate] public SlateRef<string> outSignalDull;
        [NoTranslate] public SlateRef<string> outSignalPointed;
        [NoTranslate] public SlateRef<string> outSignalSilent;
        public SlateRef<IntRange> finderFee;   // silver the surveyors drop by the ship for answer (c)

        protected override bool TestRunInt(Slate slate)
        {
            return slate.Exists("map") && SurveyFaction.Resolve() != null;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            Faction faction = SurveyFaction.Resolve();
            slate.Set("surveyFaction", faction);
            string Name(string s) => (s ?? "").Replace("{FACTION}", faction.Name);
            IntRange fee = finderFee.GetValue(slate);
            QuestGen.quest.AddPart(new RUT_QuestPart_SurveyHail
            {
                inSignal = QuestGenUtility.HardcodedSignalWithQuestID(inSignal.GetValue(slate)) ?? slate.Get<string>("inSignal"),
                faction = faction,
                mapParent = slate.Get<Map>("map").Parent,
                letterLabel = Name(letterLabel.GetValue(slate)),
                letterText = Name(letterText.GetValue(slate)),
                answerDullLabel = answerDullLabel.GetValue(slate),
                answerPointedLabel = answerPointedLabel.GetValue(slate),
                answerSilentLabel = answerSilentLabel.GetValue(slate),
                outSignalDull = QuestGenUtility.HardcodedSignalWithQuestID(outSignalDull.GetValue(slate)),
                outSignalPointed = QuestGenUtility.HardcodedSignalWithQuestID(outSignalPointed.GetValue(slate)),
                outSignalSilent = QuestGenUtility.HardcodedSignalWithQuestID(outSignalSilent.GetValue(slate)),
                finderFee = fee.max > 0 ? fee.RandomInRange : 0,
            });
        }
    }

    /// <summary>Sends the hail letter on its inSignal and carries the answer back as a quest signal. Answers once: a
    /// second answer (a reloaded letter, a double click) does nothing. When the quest ends any other way (the hail
    /// lapses, the map is lost) the letter is taken off the stack.</summary>
    public class RUT_QuestPart_SurveyHail : QuestPart
    {
        public string inSignal;
        public Faction faction;
        public MapParent mapParent;
        public string letterLabel, letterText;
        public string answerDullLabel, answerPointedLabel, answerSilentLabel;
        public string outSignalDull, outSignalPointed, outSignalSilent;
        public int finderFee;
        public bool hailSent;
        public bool answered;

        public override IEnumerable<Faction> InvolvedFactions
        {
            get
            {
                foreach (Faction f in base.InvolvedFactions) yield return f;
                if (faction != null) yield return faction;
            }
        }

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal || hailSent) return;
            hailSent = true;
            LetterDef def = DefDatabase<LetterDef>.GetNamed("RUT_CathedralSurveyHail");
            ChoiceLetter letter = LetterMaker.MakeLetter(letterLabel, letterText, def, faction, quest);
            letter.title = letterLabel;
            Find.LetterStack.ReceiveLetter(letter);
        }

        public void Answer(SurveyAnswer answer)
        {
            if (answered || quest == null || quest.State != QuestState.Ongoing) return;
            answered = true;
            if (answer == SurveyAnswer.Pointed && finderFee > 0 && mapParent?.Map is Map map)
            {
                Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
                silver.stackCount = finderFee;
                DropPodUtility.DropThingsNear(DropCellFinder.TradeDropSpot(map), map, new List<Thing> { silver }, forbid: false);
            }
            string signal = answer == SurveyAnswer.Dull ? outSignalDull : answer == SurveyAnswer.Pointed ? outSignalPointed : outSignalSilent;
            if (!signal.NullOrEmpty()) Find.SignalManager.SendSignal(new Signal(signal));
        }

        public override void Cleanup()
        {
            base.Cleanup();
            foreach (Letter l in Find.LetterStack.LettersListForReading.ToList())
                if (l is RUT_ChoiceLetter_SurveyHail hail && hail.quest == quest)
                    Find.LetterStack.RemoveLetter(hail);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_References.Look(ref faction, "faction");
            Scribe_References.Look(ref mapParent, "mapParent");
            Scribe_Values.Look(ref letterLabel, "letterLabel");
            Scribe_Values.Look(ref letterText, "letterText");
            Scribe_Values.Look(ref answerDullLabel, "answerDullLabel");
            Scribe_Values.Look(ref answerPointedLabel, "answerPointedLabel");
            Scribe_Values.Look(ref answerSilentLabel, "answerSilentLabel");
            Scribe_Values.Look(ref outSignalDull, "outSignalDull");
            Scribe_Values.Look(ref outSignalPointed, "outSignalPointed");
            Scribe_Values.Look(ref outSignalSilent, "outSignalSilent");
            Scribe_Values.Look(ref finderFee, "finderFee");
            Scribe_Values.Look(ref hailSent, "hailSent");
            Scribe_Values.Look(ref answered, "answered");
        }
    }

    /// <summary>The hail itself: the survey officer's question and the clan's three answers, plus Postpone. Its quest is
    /// hidden, so there is no Quests-tab link. Stays in the stack until answered or the quest ends.</summary>
    public class RUT_ChoiceLetter_SurveyHail : ChoiceLetter
    {
        public override bool CanDismissWithRightClick => false;

        public override bool CanShowInLetterStack =>
            base.CanShowInLetterStack && quest != null && quest.State == QuestState.Ongoing && !(Part?.answered ?? true);

        private RUT_QuestPart_SurveyHail Part => quest?.PartsListForReading.OfType<RUT_QuestPart_SurveyHail>().FirstOrDefault();

        public override IEnumerable<DiaOption> Choices
        {
            get
            {
                RUT_QuestPart_SurveyHail part = Part;
                if (ArchivedOnly || part == null || part.answered || quest.State != QuestState.Ongoing)
                {
                    yield return Option_Close;
                    yield break;
                }
                yield return AnswerOption(part.answerDullLabel, SurveyAnswer.Dull);
                yield return AnswerOption(part.answerPointedLabel, SurveyAnswer.Pointed);
                yield return AnswerOption(part.answerSilentLabel, SurveyAnswer.Silent);
                yield return Option_Postpone;
            }
        }

        private DiaOption AnswerOption(string label, SurveyAnswer answer)
        {
            return new DiaOption(label)
            {
                action = delegate
                {
                    Part?.Answer(answer);
                    Find.LetterStack.RemoveLetter(this);
                },
                resolveTree = true,
            };
        }
    }
}
