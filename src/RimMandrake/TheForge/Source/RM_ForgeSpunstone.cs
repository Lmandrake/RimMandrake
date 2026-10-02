using System.Collections.Generic;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.TheForge
{
    // ════════════════════════════════════════════════════════════════════
    // FORGE_GPT_ENRICHMENT_1 §2 — spunstone bonding.
    //
    // Floatstone construction is learned in the Forge, not granted at a
    // bench. Mature floatstone gardens carry RM_CompSpunstoneStudy, a
    // CompStudiable: core's WorkGiver_StudyInteract sends researchers to
    // study any thing with a knowledge-less CompStudiable (RimSage 1.6,
    // WorkGiver_StudyInteract.HasJobOnThing), and every study interaction
    // adds to one colony-wide knowledge counter (RM_SpunstoneKnowledge).
    // Until the counter reaches the threshold, RM_SpunstoneBonding answers
    // IsHidden = true (Harmony postfix below), which is how the research
    // tab hides a project and how CanStartNow refuses it. At the threshold a
    // letter announces the breakthrough and names who studied the samples.
    //
    // NOT here, each its own open question (FORGE_SPUNSTONE_SOURCES_1): the
    // spec's "foundry salvage" caches are campaign-tier (RUT_) content this
    // RM mod cannot name, and the "high-speed doors and advanced structural
    // parts" the project unlocks are not defined anywhere yet.
    //
    // Toggle off: the project is never hidden and gardens are not studied.
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_SpunstoneStudy : CompProperties_Studiable
    {
        // Growth at which a garden counts as mature. Matches the garden's
        // own harvestMinGrowth (0.9) in RM_TheForge_Flora.xml.
        public float minGrowth = 0.9f;
        // TUNED: one full study session (5 interactions x 0.87 base) is
        // ~4.35 points at research speed 1, so 12 is about three sessions:
        // a careful player reveals it within one growth phase.
        public float knowledgeToReveal = 12f;

        public CompProperties_SpunstoneStudy()
        {
            compClass = typeof(RM_CompSpunstoneStudy);
        }
    }

    public class RM_CompSpunstoneStudy : CompStudiable
    {
        public new CompProperties_SpunstoneStudy Props => (CompProperties_SpunstoneStudy)props;

        private bool Mature
        {
            get
            {
                Plant plant = parent as Plant;
                return plant == null || plant.Growth >= Props.minGrowth;
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            Refresh();
        }

        // Plants run only the Long ticker (Plant overrides TickLong, never
        // Tick), so this is the comp hook that fires on a garden.
        public override void CompTickLong()
        {
            base.CompTickLong();
            Refresh();
        }

        private void Refresh()
        {
            RM_SpunstoneKnowledge k = RM_SpunstoneKnowledge.Get();
            SetStudyEnabled(RM_TheForgeSettings.Active(RM_TheForgeSettings.spunstoneStudyEnabled)
                && Mature && (k == null || !k.Revealed));
        }

        public override void Study(Pawn studier, float studyAmount, float anomalyKnowledgeAmount = 0f)
        {
            float before = studyPoints;
            base.Study(studier, studyAmount, anomalyKnowledgeAmount);
            float gained = studyPoints - before;
            if (gained > 0f && RM_TheForgeSettings.Active(RM_TheForgeSettings.spunstoneStudyEnabled))
            {
                RM_SpunstoneKnowledge.Get()?.Add(gained, studier, Props.knowledgeToReveal);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.spunstoneStudyEnabled))
            {
                return null;
            }
            RM_SpunstoneKnowledge k = RM_SpunstoneKnowledge.Get();
            if (k == null || k.Revealed)
            {
                return null;
            }
            string line = "Spunstone study (colony): " + k.Points.ToString("0.#") + " / " + Props.knowledgeToReveal.ToString("0.#");
            if (!Mature)
            {
                line += ". Too young to study.";
            }
            return line;
        }
    }

    public class RM_SpunstoneKnowledge : GameComponent
    {
        private float points;
        private bool revealed;
        private List<string> studiers = new List<string>();

        public float Points => points;
        public bool Revealed => revealed;

        public RM_SpunstoneKnowledge(Game game)
        {
        }

        public static RM_SpunstoneKnowledge Get()
        {
            return Current.Game?.GetComponent<RM_SpunstoneKnowledge>();
        }

        public void Add(float amount, Pawn studier, float threshold)
        {
            if (revealed)
            {
                return;
            }
            points += amount;
            if (studier != null && !studiers.Contains(studier.LabelShort))
            {
                studiers.Add(studier.LabelShort);
            }
            if (points >= threshold)
            {
                Reveal(studier);
            }
        }

        public void Reveal(Pawn studier)
        {
            revealed = true;
            ResearchProjectDef project = RM_TheForgeDefOf.RM_SpunstoneBonding;
            StringBuilder sb = new StringBuilder();
            sb.Append("Turning a floatstone garden in the light, ")
              .Append(studier != null ? studier.LabelShort : "your researcher")
              .Append(" has seen it: the threads are not tangled at random. Each one carries strain to its neighbours, so the whole globe takes a load no single strand could. Lay it in the grain, and a beam of floatstone weighs almost nothing and bends almost not at all.\n\n")
              .Append("A new research project is open: ").Append(project.LabelCap).Append('.');
            if (studiers.Count > 0)
            {
                sb.Append("\n\nThe samples were studied by: ").Append(string.Join(", ", studiers)).Append('.');
            }
            Find.LetterStack.ReceiveLetter("Spunstone bonding", sb.ToString(), LetterDefOf.PositiveEvent);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref points, "spunstonePoints", 0f);
            Scribe_Values.Look(ref revealed, "spunstoneRevealed", false);
            Scribe_Collections.Look(ref studiers, "spunstoneStudiers", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && studiers == null)
            {
                studiers = new List<string>();
            }
        }
    }

    // The research tab hides a project, and CanStartNow refuses it, while
    // IsHidden is true (RimSage 1.6: MainTabWindow_Research, ResearchProjectDef.CanStartNow).
    [HarmonyPatch(typeof(ResearchProjectDef), nameof(ResearchProjectDef.IsHidden), MethodType.Getter)]
    public static class RM_Patch_SpunstoneHidden
    {
        public static void Postfix(ResearchProjectDef __instance, ref bool __result)
        {
            if (__result || __instance != RM_TheForgeDefOf.RM_SpunstoneBonding)
            {
                return;
            }
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.spunstoneStudyEnabled) || Current.Game == null)
            {
                return;
            }
            if (__instance.IsFinished)
            {
                return;
            }
            RM_SpunstoneKnowledge k = RM_SpunstoneKnowledge.Get();
            __result = k == null || !k.Revealed;
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_TheForgeStartup
    {
        static RM_TheForgeStartup()
        {
            new Harmony("mandrake.rm.theforge").PatchAll(typeof(RM_TheForgeStartup).Assembly);
            RM_KeelworkUtility.ApplySetting();
        }
    }
}
