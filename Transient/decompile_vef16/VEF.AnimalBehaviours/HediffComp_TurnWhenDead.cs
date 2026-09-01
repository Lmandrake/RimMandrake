using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_TurnWhenDead : HediffComp
{
	public HediffCompProperties_TurnWhenDead Props => (HediffCompProperties_TurnWhenDead)(object)base.props;

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_017d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0244: Unknown result type (might be due to invalid IL or missing references)
		//IL_024b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		float severityToTurn = Props.severityToTurn;
		Map map = ((Thing)((Hediff)base.parent).pawn.Corpse).Map;
		if (map == null || !(((Hediff)base.parent).Severity > severityToTurn))
		{
			return;
		}
		Gender gender = ((Hediff)base.parent).pawn.gender;
		Faction val = null;
		if (Props.isHostile)
		{
			val = Find.FactionManager.FirstFactionOfDef(FactionDef.Named(Props.factionToTurnTo));
		}
		int num = Rand.RangeInclusive(Props.numberOfSpawn[0], Props.numberOfSpawn[1]);
		for (int i = 0; i < num; i++)
		{
			Pawn val2 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(Props.thingToTurnTo), val, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, true, false, false, true, 1f, false, false, true, true, false, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
			PawnUtility.TrySpawnHatchedOrBornPawn(val2, (Thing)(object)((Hediff)base.parent).pawn.Corpse, (IntVec3?)null);
			if (Props.keepGender)
			{
				val2.gender = gender;
			}
			if (Props.isHostile)
			{
				val2.mindState.mentalStateHandler.TryStartMentalState(DefDatabase<MentalStateDef>.GetNamed("ManhunterPermanent", true), (string)null, true, false, false, (Pawn)null, false, false, false);
			}
		}
		IntVec3 val3 = default(IntVec3);
		for (int j = 0; j < 20; j++)
		{
			CellFinder.TryFindRandomReachableNearbyCell(((Thing)((Hediff)base.parent).pawn.Corpse).Position, map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val3, 999999);
			FilthMaker.TryMakeFilth(val3, ((Thing)((Hediff)base.parent).pawn.Corpse).Map, ThingDefOf.Filth_Blood, 1, (FilthSourceFlags)0, true);
		}
		SoundStarter.PlayOneShot(VEFDefOf.Hive_Spawn, SoundInfo.op_Implicit(new TargetInfo(((Thing)((Hediff)base.parent).pawn.Corpse).Position, map, false)));
		((Thing)((Hediff)base.parent).pawn.Corpse).Destroy((DestroyMode)0);
	}
}
