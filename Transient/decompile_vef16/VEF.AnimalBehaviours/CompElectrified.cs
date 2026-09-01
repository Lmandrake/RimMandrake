using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompElectrified : ThingComp
{
	public CompProperties_Electrified Props => (CompProperties_Electrified)(object)base.props;

	protected int electroRate => Props.electroRate;

	protected int electroRadius => Props.electroRadius;

	protected int electroChargeAmount => Props.electroChargeAmount;

	public override void CompTickInterval(int delta)
	{
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)base.parent).Map == null || !AnimalBehaviours_Settings.flagChargeBatteries || !Gen.IsHashIntervalTick((Thing)(object)base.parent, electroRate, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		CellRect val2 = GenAdj.OccupiedRect(((Thing)val).Position, ((Thing)val).Rotation, IntVec2.One);
		val2 = ((CellRect)(ref val2)).ExpandedBy(electroRadius);
		List<Building> list = new List<Building>();
		foreach (IntVec3 cell in ((CellRect)(ref val2)).Cells)
		{
			if (!GenGrid.InBounds(cell, ((Thing)val).Map))
			{
				continue;
			}
			Building edifice = GridsUtility.GetEdifice(cell, ((Thing)val).Map);
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
		Building val3 = GenCollection.RandomElement<Building>((IEnumerable<Building>)list);
		IntVec3 position = ((Thing)val3).Position;
		FleckMaker.ThrowMicroSparks(((IntVec3)(ref position)).ToVector3(), ((Thing)val3).Map);
		using (IEnumerator<CompPowerBattery> enumerator3 = ((ThingWithComps)val3).GetComps<CompPowerBattery>().GetEnumerator())
		{
			if (enumerator3.MoveNext())
			{
				enumerator3.Current.AddEnergy((float)electroChargeAmount);
			}
		}
		if (ModLister.HasActiveModWithName("Alpha Animals") && ((Thing)val).Faction == Faction.OfPlayer)
		{
			val.health.AddHediff(HediffDef.Named("AA_RechargingBatteries"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}
}
