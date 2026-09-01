using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

internal class CompNearbyEffecter : ThingComp
{
	public CompProperties_NearbyEffecter Props => (CompProperties_NearbyEffecter)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.ticksConversionRate, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val.Downed || ((Thing)val).Map == null)
		{
			return;
		}
		CellRect val2 = GenAdj.OccupiedRect(((Thing)val).Position, ((Thing)val).Rotation, IntVec2.One);
		val2 = ((CellRect)(ref val2)).ExpandedBy(Props.radius);
		foreach (IntVec3 cell in ((CellRect)(ref val2)).Cells)
		{
			if (!GenGrid.InBounds(cell, ((Thing)val).Map))
			{
				continue;
			}
			Thing val3 = GenCollection.FirstOrFallback<Thing>((IEnumerable<Thing>)new HashSet<Thing>(GridsUtility.GetThingList(cell, ((Thing)val).Map)), (Thing)null);
			if (val3 != null && Props.thingsToAffect.Contains(((Def)val3.def).defName))
			{
				Thing val4 = GenSpawn.Spawn(ThingDef.Named(Props.thingsToConvertTo[Props.thingsToAffect.IndexOf(((Def)val3.def).defName)]), cell, ((Thing)val).Map, (WipeMode)0);
				val4.stackCount = val3.stackCount;
				if (Props.isForbidden)
				{
					ForbidUtility.SetForbidden(val4, true, true);
				}
				if (Props.feedCauser && val?.needs?.food != null)
				{
					Need_Food food = val.needs.food;
					((Need)food).CurLevel = ((Need)food).CurLevel + Props.nutritionGained;
				}
				val3.Destroy((DestroyMode)0);
				break;
			}
		}
	}
}
