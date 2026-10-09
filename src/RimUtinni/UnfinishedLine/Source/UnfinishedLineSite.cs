using System.Collections.Generic;
using RimWorld;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_SITE_CHOICE_1 — where the line stands, offered when the Envoy succeeds (design 2.2).
    /// Owner ruling 2026-10-08 (question card): site B "your colony" is CUT; the Enclaves hold the line (Q1=A),
    /// so only A (the old foundry ruin), C (Enclave ground) and D (the Ore Seams) are offered. The transport is
    /// the ChoiceLetter fallback the design names: whether a QuestPart_Choice with no Reward renders is UNMEASURED
    /// and nothing here needs it. The site is stored on GameComponent_RUT_UnfinishedLine (a child quest cannot
    /// write the parent's slate), where beats 3-5 read it. Goodwill deltas are PROVISIONAL settings.
    /// </summary>
    public static class LineSites
    {
        public const string A = "A";
        public const string C = "C";
        public const string D = "D";

        public static readonly string[] All = { A, C, D };

        public static string Name(string site)
        {
            switch (site)
            {
                case A: return "the old silicax foundry ruin";
                case C: return "Enclave ground, on the Cathedral plateau";
                case D: return "the Ore Seams";
                default: return "nowhere yet";
            }
        }

        /// <summary>(Enclave delta, Hive delta) on top of the envoy beat's own +10 / +15.</summary>
        public static void Deltas(string site, out int enclave, out int hive)
        {
            switch (site)
            {
                case C: enclave = UnfinishedLineSettings.siteCEnclaveDelta; hive = UnfinishedLineSettings.siteCHiveDelta; break;
                case D: enclave = UnfinishedLineSettings.siteDEnclaveDelta; hive = UnfinishedLineSettings.siteDHiveDelta; break;
                default: enclave = UnfinishedLineSettings.siteAEnclaveDelta; hive = UnfinishedLineSettings.siteAHiveDelta; break;
            }
        }

        public static string Blurb(string site)
        {
            switch (site)
            {
                case C: return "Enclave ground (the Enclaves +++, the Hive unsatisfied: they cannot work it)";
                case D: return "the Ore Seams (the Hive +++, the Enclaves wary: 'Foundry product, again'; speeds the Hive's doom)";
                default: return "the old foundry ruin (neutral ground, joint stewardship; both pleased; recommended)";
            }
        }

        public static string GradeLine(string grade)
        {
            switch (grade)
            {
                case "Fine": return "The Enclaves still speak of the fine parts you fitted their fallen.";
                case "Honest": return "The Enclaves remember the honest work you did on their fallen.";
                case "Shoddy": return "The Enclaves remember the worn parts you fitted their fallen, and say nothing about it.";
                case "Neglected": return "The Enclaves remember that you left their fallen unmended.";
                default: return "";
            }
        }

        public static HistoryEventDef Reason => DefDatabase<HistoryEventDef>.GetNamedSilentFail("RUT_LineSiteChosen");

        /// <summary>Applies the choice: stores it, splits the goodwill, closes the letter. False if already chosen.</summary>
        public static bool Choose(string site)
        {
            GameComponent_RUT_UnfinishedLine comp = GameComponent_RUT_UnfinishedLine.Get;
            if (comp == null || !comp.lineSite.NullOrEmpty() || System.Array.IndexOf(All, site) < 0) return false;
            comp.lineSite = site;
            Deltas(site, out int enclave, out int hive);
            Nudge(LineFactions.Enclaves, enclave);
            Nudge(LineFactions.Hive, hive);
            Messages.Message("The line will stand at " + Name(site) + ".", MessageTypeDefOf.NeutralEvent, false);
            return true;
        }

        private static void Nudge(Faction f, int delta)
        {
            if (f == null || f.defeated || delta == 0) return;
            f.TryAffectGoodwillWith(Faction.OfPlayer, delta, canSendMessage: true, canSendHostilityLetter: false, reason: Reason);
        }

        public static void OfferLetter()
        {
            GameComponent_RUT_UnfinishedLine comp = GameComponent_RUT_UnfinishedLine.Get;
            if (comp == null || !comp.lineSite.NullOrEmpty()) return;
            if (!UnfinishedLineSettings.siteChoiceEnabled)
            {
                Choose(A);
                return;
            }
            string text = "The Hive's overseers have seen enough. Now everyone wants to know where the line will stand.\n\n"
                + "The old silicax foundry ruin is neutral ground, kept jointly with the Jawa as stewards. The Enclaves' plateau puts "
                + "the line in the Enclaves' hands, and the Hive cannot work it. The Ore Seams put it in the Hive's, and the "
                + "Enclaves will not forgive that. The line will not stand at your colony: the Enclaves hold it, and you get what it makes.\n\n"
                + GradeLine(comp.beat1Grade);
            ChoiceLetter letter = LetterMaker.MakeLetter("Where the line stands", text.Trim(), UnfinishedLineDefOf.RUT_LineSiteOffer);
            Find.LetterStack.ReceiveLetter(letter);
        }
    }

    /// <summary>The site offer: three options and Postpone. Silence is not a choice; beats 3-5 read the A default until it is made.</summary>
    public class ChoiceLetter_RUT_LineSite : ChoiceLetter
    {
        public override bool CanShowInLetterStack
        {
            get
            {
                GameComponent_RUT_UnfinishedLine comp = GameComponent_RUT_UnfinishedLine.Get;
                return base.CanShowInLetterStack && comp != null && comp.lineSite.NullOrEmpty();
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
                foreach (string site in LineSites.All)
                {
                    string s = site;
                    DiaOption opt = new DiaOption(LineSites.Blurb(s))
                    {
                        action = delegate
                        {
                            LineSites.Choose(s);
                            Find.LetterStack.RemoveLetter(this);
                        },
                        resolveTree = true
                    };
                    GameComponent_RUT_UnfinishedLine comp = GameComponent_RUT_UnfinishedLine.Get;
                    if (comp == null || !comp.lineSite.NullOrEmpty()) opt.Disable("already decided");
                    yield return opt;
                }
                yield return Option_Postpone;
            }
        }
    }

    /// <summary>On its signal: offers the site choice (the ChoiceLetter transport).</summary>
    public class QuestPart_RUT_SiteChoice : QuestPart
    {
        public string inSignal;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag == inSignal) LineSites.OfferLetter();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
        }
    }

    public class QuestNode_RUT_SiteChoice : QuestNode
    {
        [NoTranslate] public string inSignal;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new QuestPart_RUT_SiteChoice
            {
                inSignal = inSignal.NullOrEmpty() ? slate.Get<string>("inSignal") : QuestGenUtility.HardcodedSignalWithQuestID(inSignal)
            });
        }
    }

    // jawa/static_call proof (validation.py, site_choice). No bridge needed to read it offline in the selftest.
    public static class UnfinishedLineSiteProof
    {
        public static string ProofSite()
        {
            GameComponent_RUT_UnfinishedLine gc = GameComponent_RUT_UnfinishedLine.Get;
            LineSites.Deltas(LineSites.C, out int ce, out int ch);
            LineSites.Deltas(LineSites.D, out int de, out int dh);
            return "SITE " + (gc == null ? "no component" : (gc.lineSite.NullOrEmpty() ? "unchosen" : gc.lineSite))
                + " grade=" + (gc?.beat1Grade ?? "none") + " enabled=" + UnfinishedLineSettings.siteChoiceEnabled
                + " options=" + string.Join("", LineSites.All) + " C(" + ce + "," + ch + ") D(" + de + "," + dh + ")";
        }

        /// <summary>Offers the letter now (skips the quest); <paramref name="site"/> non-empty chooses straight away.</summary>
        public static string ProofChoose(string site)
        {
            if (!site.NullOrEmpty()) return LineSites.Choose(site) ? ProofSite() : "REFUSED: " + ProofSite();
            LineSites.OfferLetter();
            return ProofSite();
        }
    }
}
