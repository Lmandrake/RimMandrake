// BESKAR_ARMORER_QUEST_1 spec 2: the orbital covert, its cast, her forge. A SpaceMapParent because the gravship gate is the virtual
// WorldObject.GravShipCanLandOn and TileFinder reads it (decompiled 1.6): plain MapParent answers false.
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Utinni.BeskarArmorer
{
    public class RM_ArmorerCovert : SpaceMapParent
    {
        public bool lost;
        public int revealedTick;
        public int meltRemainder;
        public List<Pawn> cast = new List<Pawn>();

        public Pawn Armorer { get { return cast.FirstOrDefault(p => p.kindDef == ArmorerDefOf.RM_TheArmorer); } }

        public override bool GravShipCanLandOn { get { return !lost && base.GravShipCanLandOn; } }

        // Landing: MapGenerator hands a CanBeSettled parent to GravshipUtility.SettleTile, which destroys it for a player Settlement.
        public override AcceptanceReport CanBeSettled { get { return false; } }

        /// <summary>Departure: with no grav anchor the launch abandons the map, and the base Abandon destroys this object. Only the map
        /// goes; a lost covert goes whole.</summary>
        public override void Abandon(bool wasGravshipLaunch)
        {
            if (lost) { base.Abandon(wasGravshipLaunch); return; }
            if (HasMap) Current.Game.DeinitAndRemoveMap(Map, notifyPlayer: false);
        }

        public override bool ShouldRemoveMapNow(out bool alsoRemoveWorldObject)
        {
            bool remove = base.ShouldRemoveMapNow(out alsoRemoveWorldObject);
            alsoRemoveWorldObject = remove && lost;       // the object is permanent unless the Creed says otherwise
            return remove;
        }

        /// <summary>The map is thrown away on departure; the three pawns are not.</summary>
        public override void Notify_MyMapAboutToBeRemoved()
        {
            base.Notify_MyMapAboutToBeRemoved();
            foreach (Pawn p in cast)
            {
                if (p.Dead) continue;
                p.GetLord()?.RemovePawn(p);
                if (p.Spawned) p.DeSpawn();
                p.health.Reset();
                ArmorerCast.Mark(p);
                // the launch's AbandonMap may have passed them already, as ordinary world pawns the GC could take
                if (Find.WorldPawns.Contains(p)) Find.WorldPawns.ForcefullyKeptPawns.Add(p);
                else Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lost, "lost");
            Scribe_Values.Look(ref revealedTick, "revealedTick");
            Scribe_Values.Look(ref meltRemainder, "meltRemainder");
            Scribe_Collections.Look(ref cast, "cast", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit) { if (cast == null) cast = new List<Pawn>(); cast.RemoveAll(p => p == null); }
        }
    }

    public static class ArmorerCast
    {
        public static Faction TribeFaction()
        {
            Faction f = Find.FactionManager.FirstFactionOfDef(ArmorerDefOf.RM_TribeOfTheArmorer);
            if (f != null) return f;
            // the shipped world is frozen and a save predates this mod: the hidden faction is made here, never at world start
            f = FactionGenerator.NewGeneratedFaction(new FactionGeneratorParms(ArmorerDefOf.RM_TribeOfTheArmorer));
            Find.FactionManager.Add(f);
            f.SetRelationDirect(Faction.OfPlayer, FactionRelationKind.Neutral, false);
            return f;
        }

        public static void Mark(Pawn p)
        {
            HediffDef h = p.kindDef == ArmorerDefOf.RM_TheArmorer ? ArmorerDefOf.RM_ArmorerOfTheTribe : ArmorerDefOf.RM_CovertSwornMark;
            if (!p.health.hediffSet.HasHediff(h)) p.health.AddHediff(h);
            if (p.guest != null) p.guest.Recruitable = false;
        }

        private static Pawn Make(PawnKindDef kind, Faction f, string fixedName)
        {
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, f, PawnGenerationContext.NonPlayer, -1, forceGenerateNewPawn: true,
                canGeneratePawnRelations: false, mustBeCapableOfViolence: true));
            if (fixedName != null) p.Name = new NameTriple("The", fixedName, "Armorer");
            Mark(p);
            if (kind == ArmorerDefOf.RM_TheArmorer)
            {
                SkillRecord s = p.skills?.GetSkill(SkillDefOf.Crafting);
                if (s != null) { s.Level = 20; s.passion = Passion.Major; }
            }
            ThingDef ingot = ArmorerDefOf.KOTOR_IngotBeskar;
            foreach (Apparel a in p.apparel.WornApparel) if (a.Stuff == null && a.def.MadeFromStuff) a.SetStuffDirect(ingot);
            Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
            return p;
        }

        public static void Populate(RM_ArmorerCovert covert)
        {
            Faction f = TribeFaction();
            covert.SetFaction(f);
            covert.cast.Add(Make(ArmorerDefOf.RM_TheArmorer, f, "Armorer"));
            covert.cast.Add(Make(ArmorerDefOf.RM_CovertSworn, f, null));
            covert.cast.Add(Make(ArmorerDefOf.RM_CovertSworn, f, null));
        }
    }

    /// <summary>Puts the same three pawns on the regenerated map. Runs after the layout.</summary>
    public class RM_GenStep_ArmorerCast : GenStep
    {
        public override int SeedPart { get { return 771204913; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!(map.Parent is RM_ArmorerCovert covert)) return;
            Thing forge = map.listerThings.ThingsOfDef(ArmorerDefOf.RM_ArmorerForge).FirstOrDefault();
            if (forge == null) { Log.Error("[BeskarArmorer] RM_ArmorerCovertLayout placed no RM_ArmorerForge"); return; }
            forge.SetFaction(null);            // ITab_Bills and the player's bills: a neutral faction's table cannot be billed by him
            IntVec3 anchor = forge.InteractionCell;
            foreach (Pawn p in covert.cast)
            {
                if (p.Dead || p.Spawned) continue;
                IntVec3 c = CellFinder.StandableCellNear(anchor, map, 6f);
                GenSpawn.Spawn(p, c.IsValid ? c : anchor, map);
            }
            List<Pawn> alive = covert.cast.Where(p => p.Spawned).ToList();
            LordMaker.MakeNewLord(covert.Faction, new LordJob_DefendPoint(anchor, 6f, addFleeToil: false), map, alive);
            foreach (Pawn p in alive) { p.needs?.food?.SetInitialLevel(); if (p.needs?.rest != null) p.needs.rest.CurLevel = 1f; }
        }
    }

    public class CompProperties_ArmorerForge : CompProperties
    {
        public CompProperties_ArmorerForge() { compClass = typeof(CompArmorerForge); }
    }

    /// <summary>A non-player pawn never runs WorkGivers, so nothing would ever start her job: the forge hands her the DoBill job the
    /// vanilla WorkGiver_DoBill builds. Also keeps the cast fed: they live on a map with no kitchen and a player may stay for weeks.</summary>
    public class CompArmorerForge : ThingComp
    {
        public override void CompTickRare()
        {
            if (!(parent.Map?.Parent is RM_ArmorerCovert covert) || covert.lost) return;
            foreach (Pawn c in covert.cast)
            {
                if (c.needs?.food != null) c.needs.food.CurLevel = c.needs.food.MaxLevel;
                if (c.needs?.rest != null) c.needs.rest.CurLevel = 1f;
            }
            Pawn her = covert.Armorer;
            if (her == null || !her.Spawned || her.Dead || her.Downed || her.CurJobDef == JobDefOf.DoBill) return;
            if (!(ArmorerDefOf.RM_DoBillsArmorerForge.Worker is WorkGiver_DoBill giver)) return;
            Job job = giver.JobOnThing(her, parent, forced: true);
            if (job == null) return;
            job.playerForced = true;
            her.jobs.StartJob(job, JobCondition.InterruptForced);
        }
    }

    /// <summary>Spec 2.2 bill 1: the tribute is taken here, once.</summary>
    public class RM_RecipeWorker_ArmorerMelt : RecipeWorker
    {
        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            base.Notify_IterationCompleted(billDoer, ingredients);
            if (!(billDoer.Map?.Parent is RM_ArmorerCovert covert)) return;
            int mass = ingredients.Sum(BeskarUtil.Mass);
            int left = ArmorerKernel.MeltIngots(mass, BeskarArmorerSettings.tributeOneIn, ref covert.meltRemainder);
            while (left > 0)
            {
                Thing ingot = ThingMaker.MakeThing(ArmorerDefOf.KOTOR_IngotBeskar);
                ingot.stackCount = System.Math.Min(left, ingot.def.stackLimit);
                left -= ingot.stackCount;
                GenPlace.TryPlaceThing(ingot, billDoer.Position, billDoer.Map, ThingPlaceMode.Near);
            }
        }
    }
}
