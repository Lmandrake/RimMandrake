using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompSummonOnSpawn : ThingComp
{
	private bool summonOnce = true;

	public CompProperties_SummonOnSpawn Props => (CompProperties_SummonOnSpawn)(object)base.props;

	public void ExposeData()
	{
		Scribe_Values.Look<bool>(ref summonOnce, "summonOnce", true, false);
	}

	public override void CompTick()
	{
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_0177: Unknown result type (might be due to invalid IL or missing references)
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTick();
		if (!summonOnce || ((Thing)base.parent).Map == null)
		{
			return;
		}
		int num = Rand.RangeInclusive(Props.groupMinMax[0], Props.groupMinMax[1]);
		for (int i = 0; i < num; i++)
		{
			Pawn val = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(Props.pawnDef), Find.FactionManager.FirstFactionOfDef(FactionDefOf.AncientsHostile), (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, false, false, false, true, 1f, false, false, true, true, false, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
			GenSpawn.Spawn((Thing)(object)val, CellFinder.RandomClosewalkCellNear(((Thing)base.parent).Position, ((Thing)base.parent).Map, 3, (Predicate<IntVec3>)null), ((Thing)base.parent).Map, (WipeMode)0);
			if (Props.summonsAreManhunters)
			{
				val.mindState.mentalStateHandler.TryStartMentalState(DefDatabase<MentalStateDef>.GetNamed("ManhunterPermanent", true), (string)null, true, false, false, (Pawn)null, false, false, false);
			}
		}
		SoundStarter.PlayOneShot(VEFDefOf.Hive_Spawn, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
		summonOnce = false;
	}
}
