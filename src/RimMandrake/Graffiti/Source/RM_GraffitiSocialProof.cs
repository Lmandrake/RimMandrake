using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    /// <summary>Bridge hands for the live social proof (jawa/static_call). They set up relations through the game's own memories and orders; what follows is the mod's doing.</summary>
    public static class RM_GraffitiSocialProof
    {
        private static Pawn Named(string name)
        {
            return Find.CurrentMap?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.LabelShort == name);
        }

        /// <summary>a comes to hate b: the game's own Insulted memory, stacked. Returns a's opinion of b.</summary>
        public static string Feud(string args)
        {
            string[] w = args.Split('|');
            string a = w[0], b = w[1];
            Pawn pa = Named(a), pb = Named(b);
            if (pa == null || pb == null) return "error=no such pawn";
            for (int i = 0; i < 5; i++) pa.needs.mood.thoughts.memories.TryGainMemory(DefDatabase<ThoughtDef>.GetNamed("Insulted"), pb);
            return a + " of " + b + "=" + pa.relations.OpinionOf(pb);
        }

        /// <summary>Paint this mark about this pawn or faction, with the player's own order at the wall nearest the painter.</summary>
        public static string Order(string args)
        {
            string[] w = args.Split('|');
            string painter = w[0], defName = w[1], about = w.Length > 2 ? w[2] : "";
            Pawn p = Named(painter);
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (p == null || def == null) return "error=no such painter or mark";
            if (!GraffitiJobUtility.TryFindWallMarkCell(p, out IntVec3 cell)) return "error=no wall";
            p.Map.designationManager.AddDesignation(new Designation(cell, RMGraffitiDefOf.RM_PaintGraffitiHere));
            Faction f = Find.FactionManager.AllFactions.FirstOrDefault(x => x.Name == about);
            MapComponent_GraffitiOrders.For(p.Map).SetOrder(cell, def, Named(about), f);
            p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(RMGraffitiDefOf.RM_PaintGraffitiJob, cell));
            return "ordered at " + cell + ", job=" + p.CurJobDef?.defName;
        }

        /// <summary>Everything the social layer has done, as a player could read it: each pawn's job, thoughts and opinions off the walls; each mark's story; the open grudges.</summary>
        public static string Ledger(string args)
        {
            Map map = Find.CurrentMap;
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(map);
            if (comp == null) return "error=no map";
            var sb = new StringBuilder();
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                sb.AppendLine(p.LabelShort + " [" + string.Join(",", p.story.traits.allTraits.Select(t => t.def.defName)) + "] art " + (p.skills?.GetSkill(SkillDefOf.Artistic)?.Level ?? 0) + " mood " + p.needs.mood.CurLevelPercentage.ToString("0.00") + " : " + p.jobs.curDriver?.GetReport());
                var thoughts = new List<Thought>();
                p.needs.mood.thoughts.GetAllMoodThoughts(thoughts);
                foreach (Thought t in thoughts.Where(t => t.def.defName.StartsWith("RM_Graffiti")))
                {
                    sb.AppendLine("  mood " + t.MoodOffset().ToString("+0.#;-0.#") + " " + t.LabelCap);
                }
                foreach (Thought_Memory t in p.needs.mood.thoughts.memories.Memories.Where(t => t is Thought_MemorySocial && t.def.defName.StartsWith("RM_Graffiti")))
                {
                    sb.AppendLine("  opinion of " + t.otherPawn?.LabelShort + " " + ((Thought_MemorySocial)t).OpinionOffset().ToString("+0.#;-0.#") + " " + t.LabelCap);
                }
            }
            sb.AppendLine("marks " + comp.marks.Count);
            foreach (Filth_Mark m in comp.marks.Where(m => m.subject != null || m.defaced || m.targetFaction != null || m.Meaning != RM_Meaning.None))
            {
                sb.AppendLine("  " + m.Position + " " + m.StoryLines());
            }
            foreach (RM_Grudge g in comp.Grudges)
            {
                sb.AppendLine("grudge " + g.pawn?.LabelShort + " " + g.answer + " against " + g.against?.LabelShort);
            }
            return sb.ToString();
        }
    }
}
