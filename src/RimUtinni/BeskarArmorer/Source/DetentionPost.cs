// BESKAR_ARMORER_QUEST_1 spec 4.3: the site. Not a subclass of SitePartWorker_PrisonerWillingToJoin as the spec first said: its
// Notify_GeneratedByQuestGen makes its own prisoner, and C# cannot skip one level of base.
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;
using Verse.AI.Group;
using Verse.Grammar;

namespace RimMandrake.Utinni.BeskarArmorer
{
    public class RM_SitePartWorker_ImperialDetainee : SitePartWorker
    {
        public override void Notify_GeneratedByQuestGen(SitePart part, Slate slate, List<Rule> outExtraDescriptionRules, Dictionary<string, string> outExtraDescriptionConstants)
        {
            base.Notify_GeneratedByQuestGen(part, slate, outExtraDescriptionRules, outExtraDescriptionConstants);
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamed("RUT_Jawa_Blackstar_Heavy");
            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, Find.FactionManager.OfPirates, PawnGenerationContext.NonPlayer, -1, forceGenerateNewPawn: true));
            part.things = new ThingOwner<Pawn>(part, oneStackOnly: true);
            part.things.TryAdd(pawn);
            slate.Set("detainee", pawn);
        }

        public override string GetPostProcessedThreatLabel(Site site, SitePart sitePart)
        {
            string text = base.GetPostProcessedThreatLabel(site, sitePart);
            if (sitePart.things != null && sitePart.things.Any) text = text + ": " + sitePart.things[0].LabelShortCap;
            if (site.HasWorldObjectTimeout) text += " (" + "DurationLeft".Translate(site.WorldObjectTimeoutTicksLeft.ToStringTicksToPeriod()) + ")";
            return text;
        }
    }

    /// <summary>After the layout: the detainee in a cell, his plate in the evidence locker, the guards scaled by the site's points.</summary>
    public class RM_GenStep_DetentionPost : GenStep
    {
        public override int SeedPart { get { return 661204917; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            SitePart part = parms.sitePart;
            Faction empire = map.ParentFaction;
            Pawn detainee = part?.things?.OfType<Pawn>().FirstOrDefault();
            if (detainee != null)
            {
                part.things.Remove(detainee);
                Thing bed = map.listerThings.ThingsOfDef(ThingDefOf.Bed).FirstOrDefault();
                IntVec3 cell = bed?.Position ?? map.Center;
                Thing locker = map.listerThings.AllThings.FirstOrDefault(t => t.def.defName == "Shelf");
                IntVec3 lockerCell = locker?.Position ?? map.Center;
                detainee.equipment?.DestroyAllEquipment();
                foreach (Apparel a in detainee.apparel.WornApparel.ToList())
                {
                    if (!BeskarUtil.Carries(a)) continue;
                    detainee.apparel.Remove(a);
                    GenPlace.TryPlaceThing(a, lockerCell, map, ThingPlaceMode.Near);
                }
                GenSpawn.Spawn(detainee, cell, map);
                detainee.guest.SetGuestStatus(empire, GuestStatus.Prisoner);
            }
            if (empire == null) return;
            float points = System.Math.Max(part?.parms?.threatPoints ?? 0f, 400f);
            List<Pawn> guards = PawnGroupMakerUtility.GeneratePawns(new PawnGroupMakerParms
            {
                groupKind = PawnGroupKindDefOf.Combat, tile = map.Tile, faction = empire, points = points,
            }).ToList();
            if (guards.Count == 0) { Log.Warning("[BeskarArmorer] the Empire gave no guards at " + points + " points"); return; }
            foreach (Pawn g in guards) GenSpawn.Spawn(g, CellFinder.StandableCellNear(map.Center, map, 12f), map);
            LordMaker.MakeNewLord(empire, new LordJob_DefendBase(empire, map.Center, 25000), map, guards);
        }
    }
}
