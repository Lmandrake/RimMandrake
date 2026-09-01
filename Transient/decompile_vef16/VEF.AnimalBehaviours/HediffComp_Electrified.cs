using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Electrified : HediffComp
{
	public HediffCompProperties_Electrified Props => (HediffCompProperties_Electrified)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)((Hediff)base.parent).pawn).Map == null || !Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.electroRate, delta))
		{
			return;
		}
		Pawn pawn = ((Hediff)base.parent).pawn;
		CellRect val = GenAdj.OccupiedRect(((Thing)pawn).Position, ((Thing)pawn).Rotation, IntVec2.One);
		val = ((CellRect)(ref val)).ExpandedBy(Props.electroRadius);
		List<Building> list = new List<Building>();
		foreach (IntVec3 cell in ((CellRect)(ref val)).Cells)
		{
			if (!GenGrid.InBounds(cell, ((Thing)pawn).Map))
			{
				continue;
			}
			Building edifice = GridsUtility.GetEdifice(cell, ((Thing)pawn).Map);
			if (edifice == null)
			{
				continue;
			}
			foreach (string item in Props.batteriesToAffect)
			{
				if (((Def)((Thing)edifice).def).defName == item)
				{
					list.Add(edifice);
				}
			}
		}
		if (list.Count <= 0)
		{
			return;
		}
		Building val2 = GenCollection.RandomElement<Building>((IEnumerable<Building>)list);
		IntVec3 position = ((Thing)val2).Position;
		FleckMaker.ThrowMicroSparks(((IntVec3)(ref position)).ToVector3(), ((Thing)val2).Map);
		using (IEnumerator<CompPowerBattery> enumerator3 = ((ThingWithComps)val2).GetComps<CompPowerBattery>().GetEnumerator())
		{
			if (enumerator3.MoveNext())
			{
				enumerator3.Current.AddEnergy((float)Props.electroChargeAmount);
			}
		}
		if (ModLister.HasActiveModWithName("Alpha Animals") && ((Thing)pawn).Faction == Faction.OfPlayer)
		{
			pawn.health.AddHediff(HediffDef.Named("AA_RechargingBatteries"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}
}
