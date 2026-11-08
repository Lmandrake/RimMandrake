using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    /// <summary>One row of the temperament table: who it matches (a trait at a degree, a gene, a hediff or a precept, by name, so a row for a
    /// mod that isn't loaded is simply inert) and what it does to how they take a mark. Unset multipliers are 1.</summary>
    public class RM_TemperamentRow
    {
        public string trait;
        public int degree;
        public string gene;
        public string hediff;
        public string precept;

        public bool numb;
        public float bad = 1f, good = 1f, temper = 1f, paint = 1f, offended = 1f;
        /// <summary>Fills both craft columns unless fine or ugly says otherwise.</summary>
        public float craft = 1f;
        public float fine = -1f, ugly = -1f;
        public int neat;
        public RM_Lean lean = RM_Lean.None;

        [Unsaved] internal TraitDef traitDef;
        [Unsaved] internal GeneDef geneDef;
        [Unsaved] internal HediffDef hediffDef;
        [Unsaved] internal PreceptDef preceptDef;

        internal void Resolve()
        {
            traitDef = trait.NullOrEmpty() ? null : DefDatabase<TraitDef>.GetNamedSilentFail(trait);
            geneDef = gene.NullOrEmpty() ? null : DefDatabase<GeneDef>.GetNamedSilentFail(gene);
            hediffDef = hediff.NullOrEmpty() ? null : DefDatabase<HediffDef>.GetNamedSilentFail(hediff);
            preceptDef = precept.NullOrEmpty() ? null : DefDatabase<PreceptDef>.GetNamedSilentFail(precept);
        }

        internal bool Live => traitDef != null || geneDef != null || hediffDef != null || preceptDef != null;

        internal bool Matches(Pawn p)
        {
            if (traitDef != null)
            {
                Trait t = p.story?.traits?.GetTrait(traitDef);
                return t != null && !t.Suppressed && t.Degree == degree;
            }
            if (geneDef != null) return p.genes != null && p.genes.HasActiveGene(geneDef);
            if (hediffDef != null) return p.health?.hediffSet != null && p.health.hediffSet.HasHediff(hediffDef);
            if (preceptDef != null) return p.Ideo != null && p.Ideo.HasPrecept(preceptDef);
            return false;
        }

        internal RM_Temper AsTemper()
        {
            return new RM_Temper
            {
                numb = numb, bad = bad, good = good, temper = temper, paint = paint, offended = offended, neat = neat, lean = lean,
                fine = fine >= 0f ? fine : craft, ugly = ugly >= 0f ? ugly : craft,
            };
        }
    }

    /// <summary>The table (Defs/TemperamentDefs_Graffiti.xml). Several defs may add rows; every row of every one counts.</summary>
    public class RM_GraffitiTemperamentDef : Def
    {
        public List<RM_TemperamentRow> rows = new List<RM_TemperamentRow>();

        public override void ResolveReferences()
        {
            base.ResolveReferences();
            foreach (RM_TemperamentRow r in rows) r.Resolve();
        }
    }

    // Personality pass, owner by card 2026-11-07: "Sociopaths wouldn't feel any mood change or care, while sensitive types might get extra
    // mood debuffs or buffs as results. Clean freaks might get extra debuffs and have a mood break that makes them compulsively clean graffitti
    // marks." Each person takes a mark like themselves: one table, read here, and one route (Give) for every memory the walls hand out.
    public static class GraffitiTemperament
    {
        private static List<RM_TemperamentRow> live;
        private static readonly Dictionary<int, KeyValuePair<int, RM_Temper>> cache = new Dictionary<int, KeyValuePair<int, RM_Temper>>();
        private const int CacheTicks = 2500;

        private static List<RM_TemperamentRow> Rows
        {
            get
            {
                if (live != null) return live;
                live = new List<RM_TemperamentRow>();
                foreach (RM_GraffitiTemperamentDef d in DefDatabase<RM_GraffitiTemperamentDef>.AllDefsListForReading)
                {
                    foreach (RM_TemperamentRow r in d.rows)
                    {
                        if (r.Live) live.Add(r);
                    }
                }
                return live;
            }
        }

        /// <summary>This pawn's temperament toward marks, recomputed at most every 2500 ticks (a trait gained or a hediff healed shows by then).</summary>
        public static RM_Temper Of(Pawn p)
        {
            if (p == null) return RM_Temper.Plain;
            int now = Find.TickManager?.TicksGame ?? 0;
            if (cache.TryGetValue(p.thingIDNumber, out KeyValuePair<int, RM_Temper> hit) && now - hit.Key < CacheTicks && now >= hit.Key) return hit.Value;
            var matched = new List<RM_Temper>();
            foreach (RM_TemperamentRow r in Rows)
            {
                if (r.Matches(p)) matched.Add(r.AsTemper());
            }
            RM_Temper t = RM_GraffitiKernel.Combine(matched);
            cache[p.thingIDNumber] = new KeyValuePair<int, RM_Temper>(now, t);
            return t;
        }

        /// <summary>Drop this pawn's cached temperament: their traits just changed.</summary>
        internal static void Forget(Pawn p) { if (p != null) cache.Remove(p.thingIDNumber); }

        /// <summary>The game's own social-fight factors on this pawn (traits not suppressed, genes): what makes a hot head, with the table's temper.</summary>
        public static float VanillaFightFactors(Pawn p)
        {
            float f = 1f;
            if (p.story?.traits != null)
            {
                foreach (Trait t in p.story.traits.allTraits)
                {
                    if (!t.Suppressed) f *= t.CurrentData.socialFightChanceFactor;
                }
            }
            if (p.genes != null) f *= p.genes.SocialFightChanceFactor;
            return f;
        }

        public static bool IsHot(Pawn p) { return RM_GraffitiKernel.IsHot(Of(p).temper, VanillaFightFactors(p)); }

        public static bool IsNumb(Pawn p) { return Of(p).numb; }

        /// <summary>How strongly this hand reaches for the brush on its own: the table's paint column times the hand's own feel for art
        /// (RM_GraffitiKernel.HandUrge). A pawn the game says is incapable of art never paints by choice; a break can still drive one to it.</summary>
        public static float Urge(Pawn p)
        {
            if (p.WorkTagIsDisabled(WorkTags.Artistic)) return 0f;
            SkillRecord art = p.skills?.GetSkill(SkillDefOf.Artistic);
            float urge = Of(p).paint * RM_GraffitiKernel.HandUrge(art == null ? 0 : (int)art.passion, art?.Level ?? 0);
            return urge > 0f && GraffitiSocial.OwesMemorial(p) ? urge * RM_GraffitiKernel.GriefUrge : urge;
        }

        /// <summary>Every Graffiti memory goes through here: scaled by the mark's reach and the pawn's temperament for its sign, fitted to the pawn's
        /// budgets, and merged so that the stronger of two memories of one kind about one person stands (vanilla's merge renews the old one and
        /// throws away the new one's strength). Returns true if anything was given. `column` picks the multiplier: 0 meaning, 1 fine art, 2 ugly,
        /// 3 creed.</summary>
        internal static bool Give(Pawn p, ThoughtDef def, Pawn other, float reach = 1f, int column = 0, int stage = 0, bool victim = false)
        {
            if (def == null || p?.needs?.mood == null || !RM_GraffitiSettings.socialEnabled) return false;
            bool social = typeof(Thought_MemorySocial).IsAssignableFrom(def.ThoughtClass);
            if (social && other == null) return false;
            if (other != null && other == p) return false;
            if (!ThoughtUtility.CanGetThought(p, def, checkIfNullified: true)) return false;
            RM_Temper t = Of(p);
            if (t.numb) return false;
            stage = stage < 0 ? 0 : (stage >= def.stages.Count ? def.stages.Count - 1 : stage);
            ThoughtStage st = def.stages[stage];
            float baseValue = social ? st.baseOpinionOffset : st.baseMoodEffect;
            bool positive = baseValue > 0f;
            float factor = reach * (column == 1 ? t.fine : column == 2 ? t.ugly : column == 3 ? t.offended * t.bad : positive ? t.good : t.bad);
            if (factor <= 0.01f) return false;
            List<Thought_Memory> memories = p.needs.mood.thoughts.memories.Memories;
            Thought_Memory existing = null;
            float already = 0f;
            // A memorial's relief isn't wall pleasure and stands apart from its budget. Live 2026-11-07: Lark, whose lover had died (-16),
            // took +1.4 from painting the memorial, because funny doodles had already filled the budget, while a near-stranger had taken +5.7.
            bool apart = def == GraffitiSocial.T.RM_Graffiti_GriefEased;
            for (int i = 0; i < memories.Count; i++)
            {
                Thought_Memory m = memories[i];
                if (!IsOurs(m.def)) continue;
                if (m.def == GraffitiSocial.T.RM_Graffiti_GriefEased && !apart) continue;
                if (m.def == def && m.otherPawn == other) existing = m;
                if (social)
                {
                    if (m is Thought_MemorySocial s && m.otherPawn == other && (s.opinionOffset > 0f) == positive) already += System.Math.Abs(s.opinionOffset);
                }
                else if (!(m is Thought_MemorySocial))
                {
                    float o = m.MoodOffset();
                    if ((o > 0f) == positive && o != 0f) already += System.Math.Abs(o);
                }
            }
            if (existing != null && !social)
            {
                // Rereads: the stronger memory stands; one as strong renews it.
                float had = existing.moodPowerFactor;
                if (factor < had - 0.01f) return false;
                already -= System.Math.Abs(existing.MoodOffset());
                float fit = apart ? 1f : RM_GraffitiKernel.FitBudget(already, System.Math.Abs(baseValue) * factor, MoodBudget(t, positive, victim));
                if (fit <= 0f) return false;
                existing.moodPowerFactor = System.Math.Max(had, factor * fit);
                existing.Renew();
                return true;
            }
            float budget = social ? OpinionCap(positive, victim) : MoodBudget(t, positive, victim);
            float keep = apart ? 1f : RM_GraffitiKernel.FitBudget(already, System.Math.Abs(baseValue) * factor, budget);
            if (keep <= 0f) return false;
            Thought_Memory made = ThoughtMaker.MakeThought(def, stage);
            if (made is Thought_MemorySocial ms)
            {
                ms.opinionOffset = st.baseOpinionOffset * factor * keep;
            }
            else
            {
                made.moodPowerFactor = factor * keep;
            }
            p.needs.mood.thoughts.memories.TryGainMemory(made, other);
            return true;
        }

        private static float MoodBudget(RM_Temper t, bool positive, bool victim)
        {
            return positive ? RM_GraffitiKernel.GoodMoodBudget * System.Math.Max(t.good, 0.5f)
                : (victim ? RM_GraffitiKernel.VictimMoodBudget : RM_GraffitiKernel.BadMoodBudget) * System.Math.Max(t.bad, 0.5f);
        }

        private static float OpinionCap(bool positive, bool victim)
        {
            return positive ? RM_GraffitiKernel.GoodOpinionCap : (victim ? RM_GraffitiKernel.VictimOpinionCap : RM_GraffitiKernel.BadOpinionCap);
        }

        internal static bool IsOurs(ThoughtDef def) { return def != null && def.defName.StartsWith("RM_Graffiti_"); }

        /// <summary>Settings say the walls no longer matter between people: whatever they made people feel goes too.</summary>
        internal static int ForgetAll(Map map)
        {
            int n = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                List<Thought_Memory> memories = p.needs?.mood?.thoughts?.memories?.Memories;
                if (memories == null) continue;
                for (int i = memories.Count - 1; i >= 0; i--)
                {
                    if (IsOurs(memories[i].def))
                    {
                        p.needs.mood.thoughts.memories.RemoveMemory(memories[i]);
                        n++;
                    }
                }
            }
            return n;
        }
    }

    /// <summary>What the walls have done across the whole game, saved: the last fight they caused, the last break, and when each neat
    /// pawn last minded the mess. A fight or a break is rare by design (personality pass, section 10), whatever the number of maps.</summary>
    public class GameComponent_Graffiti : GameComponent
    {
        public int lastFight = -999999;
        public int lastBreak = -999999;
        private Dictionary<int, int> lastMess = new Dictionary<int, int>();

        public GameComponent_Graffiti(Game game)
        {
        }

        public static GameComponent_Graffiti Get => Current.Game?.GetComponent<GameComponent_Graffiti>();

        public bool FightDue => Find.TickManager.TicksGame - lastFight >= RM_GraffitiKernel.FightCooldownTicks;
        public bool BreakDue => Find.TickManager.TicksGame - lastBreak >= RM_GraffitiKernel.BreakCooldownTicks;

        /// <summary>A neat pawn minds the mess once in three days at most, however many marks there are.</summary>
        public bool MessDue(Pawn p)
        {
            int now = Find.TickManager.TicksGame;
            if (lastMess.TryGetValue(p.thingIDNumber, out int last) && now - last < 3 * 60000) return false;
            lastMess[p.thingIDNumber] = now;
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lastFight, "rmLastFight", -999999);
            Scribe_Values.Look(ref lastBreak, "rmLastBreak", -999999);
            Scribe_Collections.Look(ref lastMess, "rmLastMess", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) lastMess = lastMess ?? new Dictionary<int, int>();
        }
    }
}
