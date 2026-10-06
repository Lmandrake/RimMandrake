using System;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // Found-tech study: a research project that stays hidden until colonists
    // have studied a thing found in the world. ONE mechanism, several users
    // (GREENTIDE_STELLOCK_LACE_BUILD_1 §2 asked for the Forge's spunstone
    // study to be generalised rather than copied):
    //   - TheForge: floatstone gardens -> RM_SpunstoneBonding
    //     (RM_CompSpunstoneStudy, now a thin subclass of this).
    //   - Greentide: the stellock branch -> RM_Research_StellockLace.
    //
    // Mechanism, unchanged from the Forge's RimSage-checked original
    // (src/RimMandrake/TheForge/Source/RM_ForgeSpunstone.cs history):
    //   - RM_CompFoundTechStudy is a knowledge-less CompStudiable, so core's
    //     WorkGiver_StudyInteract serves it (RimSage 1.6:
    //     WorkGiver_StudyInteract.HasJobOnThing returns false only when
    //     KnowledgeCategory != null; PotentialWorkThingsGlobal reads
    //     Find.StudyManager.GetStudiableThingsAndPlatforms).
    //   - Every study interaction adds its gained points to a colony-wide
    //     counter PER PROJECT (RM_FoundTechKnowledge), so two users never
    //     share a counter.
    //   - Until a project's counter reaches its threshold, the project answers
    //     IsHidden = true (postfix below): the research tab hides it and
    //     ResearchProjectDef.CanStartNow refuses it.
    //   - At the threshold a letter announces it and names who studied.
    //
    // Gating: each CompProperties carries a gateKey for RM_MechanicGates (the
    // owning mod registers its Mod Settings toggle under that key). Gate off:
    // the project is never hidden and the thing is not studiable. An
    // unregistered key reads ENABLED (RM_MechanicGates' own rule).
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_FoundTechStudy : CompProperties_Studiable
    {
        // The project this study reveals. Required.
        public ResearchProjectDef project;
        // RM_MechanicGates key for the owning mod's on/off toggle.
        public string gateKey;
        // Only read when the parent is a Plant: growth at which it counts as
        // studiable. 0 = always.
        public float minGrowth = 0f;
        // Colony study points needed to reveal the project.
        public float knowledgeToReveal = 12f;
        // Letter. letterText may use {STUDIER}; the "new project is open" and
        // "studied by" lines are appended by the mechanism.
        public string letterLabel;
        [MustTranslate]
        public string letterText;
        // Inspect line prefix, e.g. "Spunstone study (colony)".
        public string inspectLabel;

        public CompProperties_FoundTechStudy()
        {
            compClass = typeof(RM_CompFoundTechStudy);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (project == null)
            {
                yield return "CompProperties_FoundTechStudy has no project — nothing will ever be revealed.";
            }
            if (knowledgeToReveal <= 0f)
            {
                yield return "CompProperties_FoundTechStudy knowledgeToReveal must be > 0.";
            }
        }
    }

    public class RM_CompFoundTechStudy : CompStudiable
    {
        public new CompProperties_FoundTechStudy Props => (CompProperties_FoundTechStudy)props;

        protected bool GateOn => RM_MechanicGates.Enabled(Props.gateKey);

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

        // Which ticker runs depends on the parent: plants run only the Long
        // ticker (Plant overrides TickLong, never Tick), rotting items run
        // Rare. Refresh from whichever fires.
        public override void CompTick()
        {
            base.CompTick();
            if (parent.IsHashIntervalTick(250))
            {
                Refresh();
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            Refresh();
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            Refresh();
        }

        private void Refresh()
        {
            if (Props.project == null)
            {
                return;
            }
            SetStudyEnabled(GateOn && Mature && !RM_FoundTechKnowledge.IsRevealed(Props.project));
        }

        public override void Study(Pawn studier, float studyAmount, float anomalyKnowledgeAmount = 0f)
        {
            float before = studyPoints;
            base.Study(studier, studyAmount, anomalyKnowledgeAmount);
            float gained = studyPoints - before;
            if (gained > 0f && GateOn && Props.project != null)
            {
                RM_FoundTechKnowledge.Get()?.Add(Props.project, gained, studier, Props);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!GateOn || Props.project == null)
            {
                return null;
            }
            RM_FoundTechKnowledge k = RM_FoundTechKnowledge.Get();
            if (k == null || k.Revealed(Props.project))
            {
                return null;
            }
            string label = Props.inspectLabel.NullOrEmpty() ? Props.project.LabelCap + " study (colony)" : Props.inspectLabel;
            string line = label + ": " + k.Points(Props.project).ToString("0.#") + " / " + Props.knowledgeToReveal.ToString("0.#");
            if (!Mature)
            {
                line += ". Too young to study.";
            }
            return line;
        }
    }

    public class RM_FoundTechRecord : IExposable
    {
        public string project;
        public float points;
        public bool revealed;
        public List<string> studiers = new List<string>();

        public void ExposeData()
        {
            Scribe_Values.Look(ref project, "project");
            Scribe_Values.Look(ref points, "points", 0f);
            Scribe_Values.Look(ref revealed, "revealed", false);
            Scribe_Collections.Look(ref studiers, "studiers", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && studiers == null)
            {
                studiers = new List<string>();
            }
        }
    }

    public class RM_FoundTechKnowledge : GameComponent
    {
        private List<RM_FoundTechRecord> records = new List<RM_FoundTechRecord>();

        public RM_FoundTechKnowledge(Game game)
        {
        }

        public static RM_FoundTechKnowledge Get()
        {
            return Current.Game?.GetComponent<RM_FoundTechKnowledge>();
        }

        public static bool IsRevealed(ResearchProjectDef project)
        {
            RM_FoundTechKnowledge k = Get();
            return k != null && k.Revealed(project);
        }

        private RM_FoundTechRecord Find(ResearchProjectDef project, bool create)
        {
            if (project == null)
            {
                return null;
            }
            for (int i = 0; i < records.Count; i++)
            {
                if (records[i].project == project.defName)
                {
                    return records[i];
                }
            }
            if (!create)
            {
                return null;
            }
            RM_FoundTechRecord r = new RM_FoundTechRecord { project = project.defName };
            records.Add(r);
            return r;
        }

        public float Points(ResearchProjectDef project)
        {
            return Find(project, false)?.points ?? 0f;
        }

        public bool Revealed(ResearchProjectDef project)
        {
            return Find(project, false)?.revealed ?? false;
        }

        public IReadOnlyList<string> Studiers(ResearchProjectDef project)
        {
            return Find(project, false)?.studiers ?? new List<string>();
        }

        // Migration seam for a mod whose old per-project component predates
        // this one (TheForge's RM_SpunstoneKnowledge): fold its saved state in.
        public void Import(ResearchProjectDef project, float points, bool revealed, IEnumerable<string> studiers)
        {
            RM_FoundTechRecord r = Find(project, true);
            if (r == null)
            {
                return;
            }
            r.points += points;
            r.revealed |= revealed;
            if (studiers != null)
            {
                foreach (string s in studiers)
                {
                    if (!r.studiers.Contains(s))
                    {
                        r.studiers.Add(s);
                    }
                }
            }
        }

        public void Add(ResearchProjectDef project, float amount, Pawn studier, CompProperties_FoundTechStudy props)
        {
            RM_FoundTechRecord r = Find(project, true);
            if (r == null || r.revealed)
            {
                return;
            }
            r.points += amount;
            if (studier != null && !r.studiers.Contains(studier.LabelShort))
            {
                r.studiers.Add(studier.LabelShort);
            }
            if (r.points >= props.knowledgeToReveal)
            {
                Reveal(project, studier, props);
            }
        }

        public void Reveal(ResearchProjectDef project, Pawn studier, CompProperties_FoundTechStudy props)
        {
            RM_FoundTechRecord r = Find(project, true);
            if (r == null || r.revealed)
            {
                return;
            }
            r.revealed = true;
            string who = studier != null ? studier.LabelShort : "your researcher";
            StringBuilder sb = new StringBuilder();
            if (props != null && !props.letterText.NullOrEmpty())
            {
                sb.Append(props.letterText.Replace("{STUDIER}", who)).Append("\n\n");
            }
            sb.Append("A new research project is open: ").Append(project.LabelCap).Append('.');
            if (r.studiers.Count > 0)
            {
                sb.Append("\n\nThe samples were studied by: ").Append(string.Join(", ", r.studiers)).Append('.');
            }
            string label = props != null && !props.letterLabel.NullOrEmpty() ? props.letterLabel : project.LabelCap.ToString();
            Verse.Find.LetterStack.ReceiveLetter(label, sb.ToString(), LetterDefOf.PositiveEvent);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref records, "foundTechRecords", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && records == null)
            {
                records = new List<RM_FoundTechRecord>();
            }
        }
    }

    // Projects revealed by found-tech study, with the gate each answers to.
    // Built once from every ThingDef's comps (all defs are loaded before any
    // game can ask IsHidden).
    public static class RM_FoundTechRegistry
    {
        private static Dictionary<ResearchProjectDef, string> projects;

        public static bool TryGetGate(ResearchProjectDef project, out string gateKey)
        {
            if (projects == null)
            {
                Build();
            }
            return projects.TryGetValue(project, out gateKey);
        }

        private static void Build()
        {
            projects = new Dictionary<ResearchProjectDef, string>();
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def.comps == null)
                {
                    continue;
                }
                for (int i = 0; i < def.comps.Count; i++)
                {
                    if (def.comps[i] is CompProperties_FoundTechStudy p && p.project != null && !projects.ContainsKey(p.project))
                    {
                        projects.Add(p.project, p.gateKey);
                    }
                }
            }
        }
    }

    // The research tab hides a project, and CanStartNow refuses it, while
    // IsHidden is true (RimSage 1.6: MainTabWindow_Research, ResearchProjectDef.CanStartNow).
    [StaticConstructorOnStartup]
    public static class RM_Patch_FoundTechHidden
    {
        static RM_Patch_FoundTechHidden()
        {
            MethodBase target = AccessTools.PropertyGetter(typeof(ResearchProjectDef), nameof(ResearchProjectDef.IsHidden));
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] found-tech study: ResearchProjectDef.IsHidden getter not found; projects will NOT hide.");
                return;
            }
            try
            {
                new Harmony("mandrake.rm.environmentalhazards.foundtech").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_Patch_FoundTechHidden), nameof(Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] found-tech study: patch failed, projects will NOT hide. " + e);
            }
        }

        public static void Postfix(ResearchProjectDef __instance, ref bool __result)
        {
            if (__result || Current.Game == null)
            {
                return;
            }
            if (!RM_FoundTechRegistry.TryGetGate(__instance, out string gateKey))
            {
                return;
            }
            if (!RM_MechanicGates.Enabled(gateKey) || __instance.IsFinished)
            {
                return;
            }
            __result = !RM_FoundTechKnowledge.IsRevealed(__instance);
        }
    }
}
