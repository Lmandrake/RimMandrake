using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompMetamorphosis : ThingComp
{
	public int metamorphosisTick;

	public int rareTicksInAYear = 14400;

	public CompProperties_Metamorphosis Props => (CompProperties_Metamorphosis)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref metamorphosisTick, "metamorphosisTick", 0, false);
	}

	public override void CompTickRare()
	{
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_0143: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_0189: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickRare();
		if (((Thing)base.parent).Map == null)
		{
			return;
		}
		metamorphosisTick++;
		if ((float)metamorphosisTick > (float)rareTicksInAYear * Props.timeInYears)
		{
			Faction faction = ((Thing)base.parent).Faction;
			GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(Props.pawnToTurnInto), faction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, true, false, false, true, 1f, false, false, true, true, false, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false)), CellFinder.RandomClosewalkCellNear(((Thing)base.parent).Position, ((Thing)base.parent).Map, 3, (Predicate<IntVec3>)null), ((Thing)base.parent).Map, (WipeMode)0);
			IntVec3 val = default(IntVec3);
			for (int i = 0; i < 20; i++)
			{
				CellFinder.TryFindRandomReachableNearbyCell(((Thing)base.parent).Position, ((Thing)base.parent).Map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val, 999999);
				FilthMaker.TryMakeFilth(val, ((Thing)base.parent).Map, ThingDefOf.Filth_AmnioticFluid, 1, (FilthSourceFlags)0, true);
			}
			SoundStarter.PlayOneShot(VEFDefOf.Hive_Spawn, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
	}

	public override string CompInspectStringExtra()
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		int num = (int)(((float)rareTicksInAYear * Props.timeInYears - (float)metamorphosisTick) * 250f);
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.reportString, NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(num, false, false, false, true, false))));
	}
}
