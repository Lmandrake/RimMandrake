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
            return Find.CurrentMap?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.LabelShort == name)
                ?? PawnsFinder.AllMapsWorldAndTemporary_AliveOrDead.FirstOrDefault(p => p.LabelShort == name);
        }

        /// <summary>a comes to hate b: the game's own Insulted memory, stacked. Returns a's opinion of b.</summary>
        public static string Feud(string args)
        {
            string[] w = args.Split('/');
            string a = w[0], b = w[1];
            Pawn pa = Named(a), pb = Named(b);
            if (pa == null || pb == null) return "error=no such pawn";
            for (int i = 0; i < 5; i++) pa.needs.mood.thoughts.memories.TryGainMemory(DefDatabase<ThoughtDef>.GetNamed("Insulted"), pb);
            return a + " of " + b + "=" + pa.relations.OpinionOf(pb);
        }

        /// <summary>a and b become close: the game's own kind-words memory, both ways. Returns both opinions.</summary>
        public static string Befriend(string args)
        {
            string[] w = args.Split('/');
            Pawn pa = Named(w[0]), pb = Named(w[1]);
            if (pa == null || pb == null) return "error=no such pawn";
            ThoughtDef kind = DefDatabase<ThoughtDef>.GetNamed("KindWords");
            for (int i = 0; i < 6; i++)
            {
                pa.needs.mood.thoughts.memories.TryGainMemory(kind, pb);
                pb.needs.mood.thoughts.memories.TryGainMemory(kind, pa);
            }
            return w[0] + " of " + w[1] + "=" + pa.relations.OpinionOf(pb) + ", back=" + pb.relations.OpinionOf(pa);
        }

        /// <summary>A new adult colonist, "Nick/Trait:degree,Trait/artistic level", spawned beside the first colonist. Test casting only:
        /// it picks who stands in the colony; everything that follows is the mod's doing.</summary>
        public static string Recruit(string args)
        {
            string[] w = args.Split('/');
            Map map = Find.CurrentMap;
            Pawn anchor = map?.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (anchor == null) return "error=no colonist to stand beside";
            var req = new PawnGenerationRequest(PawnKindDefOf.Colonist, Faction.OfPlayer, PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true,
                developmentalStages: DevelopmentalStage.Adult, allowDowned: false, canGeneratePawnRelations: false, mustBeCapableOfViolence: true);
            Pawn p = PawnGenerator.GeneratePawn(req);
            if (p.Name is NameTriple n) p.Name = new NameTriple(n.First, w[0], n.Last);
            GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(anchor.Position, map, 3), map);
            return Cast(w[0] + "/" + (w.Length > 1 ? w[1] : "") + "/" + (w.Length > 2 ? w[2] : ""));
        }

        /// <summary>"Nick/Trait:degree,Trait/artistic level": replace this colonist's traits and set their Artistic level. Empty keeps them.</summary>
        public static string Cast(string args)
        {
            string[] w = args.Split('/');
            Pawn p = Named(w[0]);
            if (p == null) return "error=no such pawn " + w[0];
            if (w.Length > 1 && w[1].Length > 0)
            {
                foreach (Trait t in p.story.traits.allTraits.ToList()) p.story.traits.RemoveTrait(t);
                foreach (string spec in w[1].Split(','))
                {
                    string[] d = spec.Split(':');
                    TraitDef def = DefDatabase<TraitDef>.GetNamedSilentFail(d[0]);
                    if (def == null) return "error=no trait " + d[0];
                    p.story.traits.GainTrait(new Trait(def, d.Length > 1 ? int.Parse(d[1]) : 0, forced: true));
                }
            }
            if (w.Length > 2 && w[2].Length > 0)
            {
                SkillRecord art = p.skills.GetSkill(SkillDefOf.Artistic);
                art.Level = int.Parse(w[2]);
                if (art.passion == Passion.None) art.passion = Passion.Minor;
            }
            p.Notify_DisabledWorkTypesChanged();
            GraffitiTemperament.Forget(p);
            return p.LabelShort + " [" + string.Join(",", p.story.traits.allTraits.Select(t => t.def.defName + (t.Degree != 0 ? ":" + t.Degree : ""))) + "] art "
                + p.skills.GetSkill(SkillDefOf.Artistic).Level + (p.WorkTagIsDisabled(WorkTags.Artistic) ? " (art disabled)" : "") + " at " + p.Position;
        }

        /// <summary>"Nick/x,z": the player sends this colonist to stand on that cell (an ordered goto, as a click would). What they see there is theirs.</summary>
        public static string Send(string args)
        {
            string[] w = args.Split('/');
            Pawn p = Named(w[0]);
            if (p == null) return "error=no such pawn";
            string[] xz = w[1].Split(',');
            IntVec3 c = new IntVec3(int.Parse(xz[0]), 0, int.Parse(xz[1]));
            bool ok = p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, c));
            return w[0] + " sent to " + c + " ok=" + ok;
        }

        /// <summary>This colonist's temperament as the table reads it, and their paint urge.</summary>
        public static string Temper(string args)
        {
            Pawn p = Named(args);
            if (p == null) return "error=no such pawn";
            RM_Temper t = GraffitiTemperament.Of(p);
            return args + " numb " + t.numb + " bad " + t.bad + " good " + t.good + " fine " + t.fine + " ugly " + t.ugly + " temper " + t.temper + " paint " + t.paint
                + " neat " + t.neat + " lean " + t.lean + " hot " + GraffitiTemperament.IsHot(p) + " urge " + GraffitiTemperament.Urge(p).ToString("0.00")
                + " mourns " + (GraffitiSocial.Mourned(p)?.LabelShort ?? "-") + " joy " + (p.needs?.joy?.CurLevelPercentage.ToString("0.00") ?? "-");
        }

        /// <summary>"a/b": if a confronted b over a mark, the chance it comes to blows (owner's pick: scaled with a's temper), beside the game's
        /// own chance of a fight over an insult.</summary>
        public static string Fight(string args)
        {
            string[] w = args.Split('/');
            Pawn a = Named(w[0]), b = Named(w[1]);
            if (a == null || b == null) return "error=no such pawn";
            return w[0] + " confronting " + w[1] + ": vanilla insult fight " + a.interactions.SocialFightChance(InteractionDefOf.Insult, b).ToString("0.000")
                + " temper " + GraffitiTemperament.Of(a).temper + " -> wall fight " + GraffitiSocial.FightChance(a, b).ToString("0.000") + " (opinion " + a.relations.OpinionOf(b) + ")";
        }

        /// <summary>"Nick/x,z": the player right-clicks the mark at that floor cell and picks Clean, as the float menu does: the cleaning work
        /// giver is asked, forced, and its refusal reason is what the menu would show.</summary>
        public static string CleanOrder(string args)
        {
            string[] w = args.Split('/');
            Pawn p = Named(w[0]);
            if (p == null) return "error=no such pawn";
            string[] xz = w[1].Split(',');
            IntVec3 c = new IntVec3(int.Parse(xz[0]), 0, int.Parse(xz[1]));
            Filth_Mark m = c.GetThingList(p.Map).OfType<Filth_Mark>().FirstOrDefault();
            if (m == null) return "error=no mark at " + c;
            var giver = (WorkGiver_CleanFilth)DefDatabase<WorkGiverDef>.GetNamed("CleanFilth").Worker;
            JobFailReason.Clear();
            if (!giver.HasJobOnThing(p, m, forced: true)) return w[0] + " REFUSES: " + (JobFailReason.Reason ?? "(no reason given)");
            Job job = giver.JobOnThing(p, m, forced: true);
            bool ok = job != null && p.jobs.TryTakeOrderedJob(job);
            return w[0] + " ordered to clean " + m.def.defName + " ok=" + ok;
        }

        /// <summary>This colonist dies (so those who loved them grieve, the game's own way).</summary>
        public static string Kill(string args)
        {
            Pawn p = Named(args);
            if (p == null) return "error=no such pawn";
            p.Kill(null);
            return args + " dead=" + p.Dead;
        }

        /// <summary>Every mark standing: def, craft, its Beauty as the game reads it, who made it about whom, and its room's beauty.</summary>
        public static string Marks(string args)
        {
            Map map = Find.CurrentMap;
            var sb = new StringBuilder();
            foreach (Filth_Mark m in map.listerThings.ThingsInGroup(ThingRequestGroup.Filth).OfType<Filth_Mark>())
            {
                Room r = m.Position.GetRoom(map);
                sb.AppendLine(m.Position + " " + m.def.defName.Replace("RM_Graffiti_", "") + " craft " + (m.CraftLabel ?? "-") + " beauty "
                    + m.GetStatValue(StatDefOf.Beauty).ToString("0.#") + " by " + (m.maker?.LabelShort ?? "-") + " about " + (m.subject?.LabelShort ?? "-")
                    + (m.defaced ? " DEFACED" : "") + " room beauty " + (r != null && !r.PsychologicallyOutdoors ? r.GetStat(RoomStatDefOf.Beauty).ToString("0.00") : "outdoors"));
            }
            return sb.ToString();
        }

        /// <summary>"painter/def/about[/x,z]": paint this mark about this pawn or faction, by the player's own order, at that floor cell or the wall nearest the painter.</summary>
        public static string Order(string args)
        {
            string[] w = args.Split('/');
            string painter = w[0], defName = w[1], about = w.Length > 2 ? w[2] : "";
            Pawn p = Named(painter);
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (p == null || def == null) return "error=no such painter or mark";
            IntVec3 cell;
            if (w.Length > 3 && w[3].Contains(","))
            {
                string[] xz = w[3].Split(',');
                cell = new IntVec3(int.Parse(xz[0]), 0, int.Parse(xz[1]));
            }
            else if (!GraffitiJobUtility.TryFindWallMarkCell(p, out cell)) return "error=no wall";
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
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.ToList())
            {
                sb.AppendLine(p.LabelShort + " [" + string.Join(",", p.story.traits.allTraits.Select(t => t.def.defName)) + "] art " + (p.skills?.GetSkill(SkillDefOf.Artistic)?.Level ?? 0) + " mood " + p.needs.mood.CurLevelPercentage.ToString("0.00") + " : " + p.jobs.curDriver?.GetReport());
                var thoughts = new List<Thought>();
                p.needs.mood.thoughts.GetAllMoodThoughts(thoughts);
                foreach (Thought t in thoughts.Where(t => t.def.defName.StartsWith("RM_Graffiti")))
                {
                    sb.AppendLine("  mood " + t.MoodOffset().ToString("+0.#;-0.#") + " " + t.LabelCap);
                }
                foreach (Thought_Memory t in p.needs.mood.thoughts.memories.Memories.Where(t => t is Thought_MemorySocial && t.def.defName.StartsWith("RM_Graffiti")).ToList())
                {
                    sb.AppendLine("  opinion of " + t.otherPawn?.LabelShort + " " + ((Thought_MemorySocial)t).OpinionOffset().ToString("+0.#;-0.#") + " " + t.LabelCap);
                }
            }
            sb.AppendLine("marks " + comp.marks.Count);
            foreach (Filth_Mark m in comp.marks.Where(m => m.subject != null || m.defaced || m.targetFaction != null || m.Meaning != RM_Meaning.None).ToList())
            {
                sb.AppendLine("  " + m.Position + " " + m.StoryLines());
            }
            if (args == "trace")
            {
                foreach (string line in GraffitiSocial.trace) sb.AppendLine("  . " + line);
                GraffitiSocial.trace.Clear();
            }
            foreach (RM_Grudge g in comp.Grudges.ToList())
            {
                sb.AppendLine("grudge " + g.pawn?.LabelShort + " " + g.answer + " against " + g.against?.LabelShort);
            }
            return sb.ToString();
        }
    }
}
