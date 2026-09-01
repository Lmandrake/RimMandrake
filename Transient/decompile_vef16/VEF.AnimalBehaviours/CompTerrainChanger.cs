using System;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompTerrainChanger : ThingComp
{
	public int extraFertCounter = 5;

	public CompProperties_TerrainChanger Props => (CompProperties_TerrainChanger)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.checkingRate, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (!((Thing)val).Spawned || ((Thing)val).Faction == null || !((Thing)val).Faction.IsPlayer)
		{
			return;
		}
		IntVec3 val2 = ((!Props.inRadius) ? ((Thing)val).Position : CellFinder.RandomClosewalkCellNear(((Thing)val).Position, ((Thing)val).Map, Props.radius, (Predicate<IntVec3>)null));
		if (GridsUtility.GetTerrain(val2, ((Thing)val).Map) == TerrainDef.Named(Props.FirstStageTerrain))
		{
			((Thing)val).Map.terrainGrid.SetTerrain(val2, TerrainDef.Named(Props.SecondStageTerrain));
			if (ModLister.HasActiveModWithName("Alpha Animals"))
			{
				val.health.AddHediff(HediffDef.Named("AA_FertilizedTerrain"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
		if (!Props.doThirdStage)
		{
			return;
		}
		extraFertCounter--;
		if (extraFertCounter > 0)
		{
			return;
		}
		Pawn_TrainingTracker training = val.training;
		if (training != null && training.HasLearned(TrainableDefOf.Obedience) && GridsUtility.GetTerrain(val2, ((Thing)val).Map) == TerrainDef.Named(Props.SecondStageTerrain))
		{
			((Thing)val).Map.terrainGrid.SetTerrain(val2, TerrainDef.Named(Props.ThirdStageTerrain));
			if (ModLister.HasActiveModWithName("Alpha Animals"))
			{
				val.health.AddHediff(HediffDef.Named("AA_FertilizedTerrain"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
		extraFertCounter = 5;
	}
}
