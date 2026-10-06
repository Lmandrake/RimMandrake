using System.Collections.Generic;
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
    // adds to one colony-wide knowledge counter (the kit's RM_FoundTechKnowledge,
    // keyed by project).
    // Until the counter reaches the threshold, RM_SpunstoneBonding answers
    // IsHidden = true (the kit's RM_Patch_FoundTechHidden postfix), which is how the research
    // tab hides a project and how CanStartNow refuses it. At the threshold a
    // letter announces the breakthrough and names who studied the samples.
    //
    // FORGE_SPUNSTONE_SOURCES_1 (owner ruling 2026-10-03): the project also
    // unlocks RM_FloatstoneDoor and RM_SpunstoneHull (RM_SpunstoneParts.xml).
    // The ruled second source, foundry salvage caches, is campaign-only: the
    // comp that adds it to RUT_FoundrySalvageCache belongs in the Utinni
    // layer (owed there); this RM mod never names it.
    //
    // Toggle off: the project is never hidden and gardens are not studied.
    // ════════════════════════════════════════════════════════════════════
    // Since GREENTIDE_STELLOCK_LACE_BUILD_1 the mechanism lives once, in the
    // shared kit: RimMandrake.EnvironmentalHazards.RM_CompFoundTechStudy
    // (RM_FoundTechStudy.cs), which also serves the Greentide's stellock
    // branch. These names stay so the Flora XML, the debug actions and the
    // TheForge walk keep pointing at real classes; each project keeps its own
    // counter, so the two never cross-talk.
    public class CompProperties_SpunstoneStudy : RimMandrake.EnvironmentalHazards.CompProperties_FoundTechStudy
    {
        public const string GateKey = "TheForge.Spunstone";

        public CompProperties_SpunstoneStudy()
        {
            compClass = typeof(RM_CompSpunstoneStudy);
            gateKey = GateKey;
            // TUNED: one full study session (5 interactions x 0.87 base) is
            // ~4.35 points at research speed 1, so 12 is about three sessions:
            // a careful player reveals it within one growth phase.
            knowledgeToReveal = 12f;
            minGrowth = 0.9f;
            letterLabel = "Spunstone bonding";
            letterText = "Turning a floatstone garden in the light, {STUDIER} has seen it: the threads are not tangled at random. Each one carries strain to its neighbours, so the whole globe takes a load no single strand could. Lay it in the grain, and a beam of floatstone weighs almost nothing and bends almost not at all.";
            inspectLabel = "Spunstone study (colony)";
        }
    }

    public class RM_CompSpunstoneStudy : RimMandrake.EnvironmentalHazards.RM_CompFoundTechStudy
    {
    }

    // Kept as a facade over the shared counter, and as the loader for saves
    // written before the move: its old Scribe keys are read once and folded
    // into RM_FoundTechKnowledge.
    public class RM_SpunstoneKnowledge : GameComponent
    {
        private float legacyPoints;
        private bool legacyRevealed;
        private List<string> legacyStudiers;

        private static ResearchProjectDef Project => RM_TheForgeDefOf.RM_SpunstoneBonding;
        private static RimMandrake.EnvironmentalHazards.RM_FoundTechKnowledge Shared
            => RimMandrake.EnvironmentalHazards.RM_FoundTechKnowledge.Get();

        public float Points => Shared?.Points(Project) ?? 0f;
        public bool Revealed => Shared != null && Shared.Revealed(Project);

        public RM_SpunstoneKnowledge(Game game)
        {
        }

        public static RM_SpunstoneKnowledge Get()
        {
            return Current.Game?.GetComponent<RM_SpunstoneKnowledge>();
        }

        public void Reveal(Pawn studier)
        {
            CompProperties_SpunstoneStudy props = null;
            ThingDef garden = DefDatabase<ThingDef>.AllDefsListForReading.Find(d => d.GetCompProperties<CompProperties_SpunstoneStudy>() != null);
            if (garden != null)
            {
                props = garden.GetCompProperties<CompProperties_SpunstoneStudy>();
            }
            Shared?.Reveal(Project, studier, props ?? new CompProperties_SpunstoneStudy());
        }

        public override void LoadedGame()
        {
            base.LoadedGame();
            if ((legacyPoints > 0f || legacyRevealed) && Shared != null)
            {
                Shared.Import(Project, legacyPoints, legacyRevealed, legacyStudiers);
                legacyPoints = 0f;
                legacyRevealed = false;
                legacyStudiers = null;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                Scribe_Values.Look(ref legacyPoints, "spunstonePoints", 0f);
                Scribe_Values.Look(ref legacyRevealed, "spunstoneRevealed", false);
                Scribe_Collections.Look(ref legacyStudiers, "spunstoneStudiers", LookMode.Value);
            }
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
