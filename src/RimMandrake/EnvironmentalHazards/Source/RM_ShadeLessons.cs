using System;
using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS. Design of record:
    // design/RimMandrake/shadecraft_lessons_design_2026-10-31.md.
    //
    //   - Two gear projects (RM_Research_Parasol, RM_Research_ShadeTent) are
    //     plain research and always visible: nothing here hides them.
    //   - Three idea projects (RM_ShadeIdea_*) are hidden found-tech projects
    //     (RM_FoundTechStudy). Dew off and deep cloth are revealed by studying
    //     a biome's own source (the comps come from Patches/
    //     RM_ShadeLessons_Sources.xml); portable shade is revealed by watching
    //     herd crossings, so it has no studiable thing and registers itself
    //     through RM_FoundTechProjectExtension on the project def.
    //   - When the second idea of a pair is finished, RM_ResearchMod_RaiseProject
    //     raises that piece's gear project to 75%. It RAISES, never adds:
    //     vanilla re-runs every finished project's mods on each FinishProject
    //     and on game load (decompiled 1.6: ResearchManager.FinishProject ->
    //     ReapplyAllMods; Game.LoadGame -> researchManager.ReapplyAllMods).
    //
    // Gate (Mod Settings "Shade gear is learned by study", key below): off,
    // sources are not studiable, crossings add nothing, and the idea projects
    // are ordinary visible research whose discount still works.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ShadeLessons
    {
        public const string GateKey = "EnvironmentalHazards.ShadeLessons";
        public const string PortableShadeProject = "RM_ShadeIdea_PortableShade";
    }

    // Pure arithmetic, no game state, so the selftest can read it as written.
    public static class RM_ShadeLessonMath
    {
        // Crossing watch radius in cells (design §3).
        public const float WatchRadius = 20f;

        // Progress to ADD so the project stands at fraction × cost, never less
        // than zero: a second Apply at the same progress adds nothing.
        public static float RaiseAmount(float current, float cost, float fraction)
        {
            if (cost <= 0f || fraction <= 0f)
            {
                return 0f;
            }
            float target = Math.Min(fraction, 1f) * cost;
            return Math.Max(0f, target - current);
        }

        // One point per crossing however many colonists watched; none unseen.
        public static float CrossingPoints(int watchers)
        {
            return watchers > 0 ? 1f : 0f;
        }
    }

    // A found-tech project with no studiable thing registers itself here, on
    // the ResearchProjectDef (RM_FoundTechRegistry reads it alongside ThingDef
    // comps). Its reveal threshold and letter live here too.
    public class RM_FoundTechProjectExtension : DefModExtension
    {
        public string gateKey;
        public float knowledgeToReveal = 12f;
        public string letterLabel;
        [MustTranslate]
        public string letterText;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (knowledgeToReveal <= 0f)
            {
                yield return "RM_FoundTechProjectExtension knowledgeToReveal must be > 0.";
            }
        }
    }

    // Raise `project` to `fraction` of its cost once every project in
    // `requires` is finished. Carried by each idea of a pair, listing both, so
    // whichever finishes second triggers it and one idea alone buys nothing.
    public class RM_ResearchMod_RaiseProject : ResearchMod
    {
        public ResearchProjectDef project;
        public List<ResearchProjectDef> requires = new List<ResearchProjectDef>();
        public float fraction = 0.75f;

        public override void Apply()
        {
            if (project == null || project.IsFinished || Find.ResearchManager == null)
            {
                return;
            }
            if (requires != null)
            {
                for (int i = 0; i < requires.Count; i++)
                {
                    if (requires[i] == null || !requires[i].IsFinished)
                    {
                        return;
                    }
                }
            }
            float add = RM_ShadeLessonMath.RaiseAmount(project.ProgressReal, project.Cost, fraction);
            if (add > 0f)
            {
                Find.ResearchManager.AddProgress(project, add);
            }
        }
    }

    // A herd crossing seen by a colonist teaches portable shade (design §3).
    [StaticConstructorOnStartup]
    public static class RM_ShadeCrossingWatch
    {
        private static ResearchProjectDef project;

        static RM_ShadeCrossingWatch()
        {
            project = DefDatabase<ResearchProjectDef>.GetNamedSilentFail(RM_ShadeLessons.PortableShadeProject);
            if (project == null)
            {
                Log.Warning("[RM EnvironmentalHazards] shade lessons: " + RM_ShadeLessons.PortableShadeProject
                    + " not found; herd crossings will teach nothing.");
                return;
            }
            RM_ShadeHop.CrossingLanded += OnCrossing;
        }

        public static bool CanWatch(Pawn p, IntVec3 landing, Map map)
        {
            if (p == null || !p.Spawned || p.Map != map || p.Downed || p.InMentalState || !p.Awake())
            {
                return false;
            }
            if (!p.Position.InHorDistOf(landing, RM_ShadeLessonMath.WatchRadius))
            {
                return false;
            }
            return GenSight.LineOfSight(p.Position, landing, map, skipFirstCell: true);
        }

        public static void OnCrossing(Pawn animal, IntVec3 landing)
        {
            if (project == null || animal == null || !animal.Spawned || animal.Faction != null
                || animal.RaceProps == null || !animal.RaceProps.Animal)
            {
                return;
            }
            if (!RM_MechanicGates.Enabled(RM_ShadeLessons.GateKey) || project.IsFinished)
            {
                return;
            }
            RM_FoundTechKnowledge k = RM_FoundTechKnowledge.Get();
            if (k == null || k.Revealed(project))
            {
                return;
            }
            Map map = animal.Map;
            int watchers = 0;
            Pawn nearest = null;
            float best = float.MaxValue;
            IReadOnlyList<Pawn> colonists = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn p = colonists[i];
                if (!CanWatch(p, landing, map))
                {
                    continue;
                }
                watchers++;
                float d = p.Position.DistanceToSquared(landing);
                if (d < best)
                {
                    best = d;
                    nearest = p;
                }
            }
            float points = RM_ShadeLessonMath.CrossingPoints(watchers);
            if (points <= 0f)
            {
                return;
            }
            RM_FoundTechProjectExtension ext = project.GetModExtension<RM_FoundTechProjectExtension>();
            k.Add(project, points, nearest, ext?.knowledgeToReveal ?? 12f, ext?.letterLabel, ext?.letterText);
        }
    }
}
