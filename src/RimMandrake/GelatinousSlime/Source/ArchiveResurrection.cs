using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_ARCHIVE_RESURRECTION_1 (Slime-side slice).
    //
    // Every time the body reads a colonist it files them: one SlimeSnapshot per person, overwritten by
    // each later touch. The archive vat grows a dead person back from their LAST entry. "Are they the
    // same?" is the design: the returned person has the snapshot's genes, skills, traits, age and
    // relations and NO memory of anything since. The old corpse/record stays; the colony holds both.
    // All numbers [INVENTED].

    public class SnapSkill : IExposable
    {
        public SkillDef def;
        public int level;
        public Passion passion;

        public void ExposeData()
        {
            Scribe_Defs.Look(ref def, "def");
            Scribe_Values.Look(ref level, "level");
            Scribe_Values.Look(ref passion, "passion");
        }
    }

    public class SnapTrait : IExposable
    {
        public TraitDef def;
        public int degree;

        public void ExposeData()
        {
            Scribe_Defs.Look(ref def, "def");
            Scribe_Values.Look(ref degree, "degree");
        }
    }

    public class SnapRelation : IExposable
    {
        public PawnRelationDef def;
        public Pawn other;

        public void ExposeData()
        {
            Scribe_Defs.Look(ref def, "def");
            Scribe_References.Look(ref other, "other");
        }
    }

    public class SlimeSnapshot : IExposable
    {
        public string key;
        public Pawn source;
        public Name name;
        public Gender gender;
        public PawnKindDef kind;
        public XenotypeDef xenotype;
        public List<GeneDef> endogenes = new List<GeneDef>();
        public List<GeneDef> xenogenes = new List<GeneDef>();
        public long ageBio;
        public long ageChrono;
        public List<SnapSkill> skills = new List<SnapSkill>();
        public List<SnapTrait> traits = new List<SnapTrait>();
        public BackstoryDef childhood;
        public BackstoryDef adulthood;
        public List<SnapRelation> relations = new List<SnapRelation>();
        public int lastTouchTick;
        public bool returned;

        public string Label
        {
            get { return name != null ? name.ToStringFull : "someone"; }
        }

        // The person is gone: no pawn reference left, or the pawn is dead, and they have not been grown back already.
        public bool IsDead
        {
            get { return !returned && (source == null || source.Dead); }
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref key, "key");
            Scribe_References.Look(ref source, "source");
            Scribe_Deep.Look(ref name, "name");
            Scribe_Values.Look(ref gender, "gender");
            Scribe_Defs.Look(ref kind, "kind");
            Scribe_Defs.Look(ref xenotype, "xenotype");
            Scribe_Collections.Look(ref endogenes, "endogenes", LookMode.Def);
            Scribe_Collections.Look(ref xenogenes, "xenogenes", LookMode.Def);
            Scribe_Values.Look(ref ageBio, "ageBio");
            Scribe_Values.Look(ref ageChrono, "ageChrono");
            Scribe_Collections.Look(ref skills, "skills", LookMode.Deep);
            Scribe_Collections.Look(ref traits, "traits", LookMode.Deep);
            Scribe_Defs.Look(ref childhood, "childhood");
            Scribe_Defs.Look(ref adulthood, "adulthood");
            Scribe_Collections.Look(ref relations, "relations", LookMode.Deep);
            Scribe_Values.Look(ref lastTouchTick, "lastTouchTick");
            Scribe_Values.Look(ref returned, "returned");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (endogenes == null) endogenes = new List<GeneDef>();
                if (xenogenes == null) xenogenes = new List<GeneDef>();
                if (skills == null) skills = new List<SnapSkill>();
                if (traits == null) traits = new List<SnapTrait>();
                if (relations == null) relations = new List<SnapRelation>();
                endogenes.RemoveAll(g => g == null);
                xenogenes.RemoveAll(g => g == null);
                skills.RemoveAll(s => s == null || s.def == null);
                traits.RemoveAll(t => t == null || t.def == null);
                relations.RemoveAll(r => r == null || r.def == null);
            }
        }
    }

    public class GameComponent_SlimeArchive : GameComponent
    {
        private List<SlimeSnapshot> snapshots = new List<SlimeSnapshot>();

        public GameComponent_SlimeArchive(Game game) { }

        public static GameComponent_SlimeArchive Instance
        {
            get { return Current.Game == null ? null : Current.Game.GetComponent<GameComponent_SlimeArchive>(); }
        }

        public List<SlimeSnapshot> All { get { return snapshots; } }

        public SlimeSnapshot Find(string key)
        {
            for (int i = 0; i < snapshots.Count; i++)
            {
                if (snapshots[i].key == key) return snapshots[i];
            }
            return null;
        }

        public List<SlimeSnapshot> DeadEntries()
        {
            List<SlimeSnapshot> res = new List<SlimeSnapshot>();
            for (int i = 0; i < snapshots.Count; i++)
            {
                if (snapshots[i].IsDead) res.Add(snapshots[i]);
            }
            return res;
        }

        // The body files this pawn as they are right now, overwriting the previous entry.
        public void Touch(Pawn p)
        {
            SlimeSnapshot s = Find(p.ThingID);
            if (s == null)
            {
                s = new SlimeSnapshot { key = p.ThingID };
                snapshots.Add(s);
            }
            s.source = p;
            s.name = p.Name;
            s.gender = p.gender;
            s.kind = p.kindDef;
            s.lastTouchTick = Find_TicksGame();
            s.ageBio = p.ageTracker.AgeBiologicalTicks;
            s.ageChrono = p.ageTracker.AgeChronologicalTicks;

            s.endogenes.Clear();
            s.xenogenes.Clear();
            s.xenotype = null;
            if (p.genes != null)
            {
                s.xenotype = p.genes.Xenotype;
                for (int i = 0; i < p.genes.Endogenes.Count; i++) s.endogenes.Add(p.genes.Endogenes[i].def);
                for (int i = 0; i < p.genes.Xenogenes.Count; i++) s.xenogenes.Add(p.genes.Xenogenes[i].def);
            }

            s.skills.Clear();
            if (p.skills != null)
            {
                for (int i = 0; i < p.skills.skills.Count; i++)
                {
                    SkillRecord r = p.skills.skills[i];
                    s.skills.Add(new SnapSkill { def = r.def, level = r.Level, passion = r.passion });
                }
            }

            s.traits.Clear();
            if (p.story != null)
            {
                List<Trait> tr = p.story.traits.allTraits;
                for (int i = 0; i < tr.Count; i++) s.traits.Add(new SnapTrait { def = tr[i].def, degree = tr[i].Degree });
                s.childhood = p.story.Childhood;
                s.adulthood = p.story.Adulthood;
            }

            s.relations.Clear();
            if (p.relations != null)
            {
                List<DirectPawnRelation> rel = p.relations.DirectRelations;
                for (int i = 0; i < rel.Count; i++)
                {
                    if (rel[i].otherPawn != null) s.relations.Add(new SnapRelation { def = rel[i].def, other = rel[i].otherPawn });
                }
            }
        }

        private static int Find_TicksGame()
        {
            return Verse.Find.TickManager.TicksGame;
        }

        public override void ExposeData()
        {
            Scribe_Collections.Look(ref snapshots, "snapshots", LookMode.Deep);
            if (snapshots == null) snapshots = new List<SlimeSnapshot>();
            if (Scribe.mode == LoadSaveMode.PostLoadInit) snapshots.RemoveAll(s => s == null || s.key == null);
        }
    }

    public static class SlimeArchiveUtility
    {
        // Humanlike people the colony holds. Visitors and raiders are not filed (bounded archive).
        public static bool Files(Pawn p)
        {
            return p != null && !p.Dead && p.RaceProps.Humanlike && p.Name != null
                && (p.IsColonist || p.IsPrisonerOfColony || p.IsSlaveOfColony);
        }

        // Called from the exposure tick and from an engulf. No-op with the toggle off.
        public static void Touch(Pawn p)
        {
            if (!SlimeSettings.archiveResurrection || !Files(p)) return;
            try
            {
                GameComponent_SlimeArchive a = GameComponent_SlimeArchive.Instance;
                if (a != null) a.Touch(p);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] archive touch: " + e.Message, 0x51A20);
            }
        }

        public static List<ThingDefCountClass> Cost
        {
            get
            {
                List<ThingDefCountClass> c = new List<ThingDefCountClass>();
                if (SlimeDefs.RawSlime != null) c.Add(new ThingDefCountClass(SlimeDefs.RawSlime, 150));
                ThingDef comp = ThingDefOf.ComponentSpacer;
                if (comp != null) c.Add(new ThingDefCountClass(comp, 4));
                return c;
            }
        }

        public static bool CanPay(Map map)
        {
            foreach (ThingDefCountClass c in Cost)
            {
                if (map.resourceCounter.GetCount(c.thingDef) < c.count) return false;
            }
            return true;
        }

        public static void Pay(Map map)
        {
            foreach (ThingDefCountClass c in Cost)
            {
                int left = c.count;
                List<Thing> things = new List<Thing>(map.listerThings.ThingsOfDef(c.thingDef));
                for (int i = 0; i < things.Count && left > 0; i++)
                {
                    Thing t = things[i];
                    if (t.IsForbidden(Faction.OfPlayer)) continue;
                    int take = Mathf.Min(left, t.stackCount);
                    t.SplitOff(take).Destroy(DestroyMode.Vanish);
                    left -= take;
                }
            }
        }

        // Grow the person back from the snapshot. Returns the new pawn or null.
        public static Pawn Grow(SlimeSnapshot s, IntVec3 cell, Map map)
        {
            PawnKindDef kind = s.kind ?? PawnKindDefOf.Colonist;
            PawnGenerationRequest req = new PawnGenerationRequest(
                kind, Faction.OfPlayer, PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true,
                canGeneratePawnRelations: false, fixedGender: s.gender,
                fixedBiologicalAge: s.ageBio / 3600000f, fixedChronologicalAge: s.ageChrono / 3600000f);
            Pawn pawn = PawnGenerator.GeneratePawn(req);

            if (s.name != null) pawn.Name = s.name;

            if (pawn.genes != null)
            {
                if (s.xenotype != null) pawn.genes.SetXenotypeDirect(s.xenotype);
                List<Gene> old = new List<Gene>(pawn.genes.GenesListForReading);
                for (int i = 0; i < old.Count; i++) pawn.genes.RemoveGene(old[i]);
                for (int i = 0; i < s.endogenes.Count; i++) pawn.genes.AddGene(s.endogenes[i], false);
                for (int i = 0; i < s.xenogenes.Count; i++) pawn.genes.AddGene(s.xenogenes[i], true);
            }

            if (pawn.story != null)
            {
                pawn.story.traits.allTraits.Clear();
                for (int i = 0; i < s.traits.Count; i++)
                {
                    pawn.story.traits.GainTrait(new Trait(s.traits[i].def, s.traits[i].degree, true), true);
                }
                if (s.childhood != null) pawn.story.Childhood = s.childhood;
                if (s.adulthood != null) pawn.story.Adulthood = s.adulthood;
            }

            if (pawn.skills != null)
            {
                for (int i = 0; i < s.skills.Count; i++)
                {
                    SkillRecord r = pawn.skills.GetSkill(s.skills[i].def);
                    if (r == null) continue;
                    r.Level = s.skills[i].level;
                    r.passion = s.skills[i].passion;
                    r.xpSinceLastLevel = 0f;
                }
            }

            // No stray generated relations; the snapshot's own come back.
            if (pawn.relations != null)
            {
                pawn.relations.ClearAllRelations();
                for (int i = 0; i < s.relations.Count; i++)
                {
                    Pawn o = s.relations[i].other;
                    if (o == null || o == s.source || o == pawn) continue;
                    if (pawn.relations.DirectRelationExists(s.relations[i].def, o)) continue;
                    pawn.relations.AddDirectRelation(s.relations[i].def, o);
                }
            }

            if (pawn.needs != null && pawn.needs.mood != null) pawn.needs.mood.thoughts.memories.Memories.Clear();

            HediffDef mark = DefDatabase<HediffDef>.GetNamedSilentFail("RM_ArchiveReturned");
            if (mark != null) pawn.health.AddHediff(mark);

            GenSpawn.Spawn(pawn, cell, map);
            s.returned = true;

            // Kin who knew both selves.
            ThoughtDef knew = DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_KnewBothSelves");
            if (knew != null)
            {
                foreach (Pawn other in map.mapPawns.FreeColonistsSpawned)
                {
                    if (other == pawn || other.needs == null || other.needs.mood == null) continue;
                    bool kin = false;
                    for (int i = 0; i < s.relations.Count; i++)
                    {
                        if (s.relations[i].other == other) { kin = true; break; }
                    }
                    if (kin) other.needs.mood.thoughts.memories.TryGainMemory(knew, pawn);
                }
            }
            return pawn;
        }
    }

    public class Building_SlimeArchiveVat : Building
    {
        public const int GrowTicks = 180000; // [INVENTED] 3 days powered
        private string growingKey;
        private int ticksLeft;

        public bool Growing { get { return growingKey != null; } }

        private bool Powered
        {
            get
            {
                CompPowerTrader p = GetComp<CompPowerTrader>();
                return p == null || p.PowerOn;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref growingKey, "growingKey");
            Scribe_Values.Look(ref ticksLeft, "ticksLeft");
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            if (Growing)
            {
                SlimeSnapshot snap = GameComponent_SlimeArchive.Instance != null ? GameComponent_SlimeArchive.Instance.Find(growingKey) : null;
                s += "\nGrowing " + (snap != null ? snap.Label : "someone") + " back: " + ticksLeft.ToStringTicksToPeriod()
                    + (Powered ? "" : " (no power)");
            }
            return s;
        }

        public override void TickRare()
        {
            base.TickRare();
            if (!Growing || !Spawned || !Powered) return;
            ticksLeft -= 250;
            if (ticksLeft > 0) return;
            SlimeSnapshot snap = GameComponent_SlimeArchive.Instance != null ? GameComponent_SlimeArchive.Instance.Find(growingKey) : null;
            growingKey = null;
            if (snap == null) return;
            IntVec3 cell = InteractionCell.IsValid ? InteractionCell : Position;
            Pawn p = SlimeArchiveUtility.Grow(snap, cell, Map);
            if (p != null)
            {
                Find.LetterStack.ReceiveLetter("grown back: " + snap.Label,
                    snap.Label + " has come out of the vat as they were the last time the body touched them. They remember nothing since. The old record stands beside the new.",
                    LetterDefOf.PositiveEvent, p);
            }
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;
            if (!SlimeSettings.archiveResurrection || Growing || !Spawned) yield break;
            Command_Action cmd = new Command_Action
            {
                defaultLabel = "Grow someone back",
                defaultDesc = "Grow a dead colonist back from the body's last entry for them. Costs raw slime and spacer components, and three days of power.",
                icon = BaseContent.BadTex,
                action = OpenMenu
            };
            yield return cmd;
        }

        private void OpenMenu()
        {
            GameComponent_SlimeArchive a = GameComponent_SlimeArchive.Instance;
            List<FloatMenuOption> opts = new List<FloatMenuOption>();
            if (a != null)
            {
                foreach (SlimeSnapshot s in a.DeadEntries())
                {
                    SlimeSnapshot snap = s;
                    opts.Add(new FloatMenuOption(snap.Label, () => Begin(snap)));
                }
            }
            if (opts.Count == 0)
            {
                opts.Add(new FloatMenuOption("no one the body has filed is dead", null));
            }
            Find.WindowStack.Add(new FloatMenu(opts));
        }

        private void Begin(SlimeSnapshot s)
        {
            if (!SlimeSettings.archiveResurrection || Growing) return;
            if (!SlimeArchiveUtility.CanPay(Map))
            {
                Messages.Message("Not enough raw slime and components on the map.", this, MessageTypeDefOf.RejectInput, false);
                return;
            }
            SlimeArchiveUtility.Pay(Map);
            growingKey = s.key;
            ticksLeft = GrowTicks;
        }
    }
}
