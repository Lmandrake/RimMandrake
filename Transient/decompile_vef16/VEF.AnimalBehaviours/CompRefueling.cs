using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompRefueling : ThingComp
{
	public CompProperties_Refueling Props => (CompProperties_Refueling)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)base.parent).Map == null || !AnimalBehaviours_Settings.flagChargeBatteries || (Props.mustBeTamed && (((Thing)base.parent).Faction == null || !((Thing)base.parent).Faction.IsPlayer)) || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.fuelingRate, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		CellRect val2 = GenAdj.OccupiedRect(((Thing)val).Position, ((Thing)val).Rotation, IntVec2.One);
		val2 = ((CellRect)(ref val2)).ExpandedBy(Props.fuelingRadius);
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
			foreach (string item in Props.buildingsToAffect)
			{
				if (((Def)((Thing)edifice).def).defName == item)
				{
					list.Add(edifice);
				}
			}
		}
		if (list.Count > 0)
		{
			CompRefuelable val3 = ThingCompUtility.TryGetComp<CompRefuelable>((Thing)(object)GenCollection.RandomElement<Building>((IEnumerable<Building>)list));
			if (val3 != null)
			{
				val3.Refuel(1f);
			}
		}
	}
}
