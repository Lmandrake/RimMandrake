using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_NearbyEffecter : HediffComp
{
	public HediffCompProperties_NearbyEffecter Props => (HediffCompProperties_NearbyEffecter)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.ticksConversionRate, delta))
		{
			return;
		}
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (pawn.Downed || ((Thing)pawn).Map == null)
		{
			return;
		}
		CellRect val = GenAdj.OccupiedRect(((Thing)pawn).Position, ((Thing)pawn).Rotation, IntVec2.One);
		val = ((CellRect)(ref val)).ExpandedBy(Props.radius);
		foreach (IntVec3 cell in ((CellRect)(ref val)).Cells)
		{
			if (!GenGrid.InBounds(cell, ((Thing)pawn).Map))
			{
				continue;
			}
			Thing val2 = GenCollection.FirstOrFallback<Thing>((IEnumerable<Thing>)new HashSet<Thing>(GridsUtility.GetThingList(cell, ((Thing)pawn).Map)), (Thing)null);
			if (val2 != null && Props.thingsToAffect.Contains(((Def)val2.def).defName))
			{
				Thing val3 = GenSpawn.Spawn(ThingDef.Named(Props.thingsToConvertTo[Props.thingsToAffect.IndexOf(((Def)val2.def).defName)]), cell, ((Thing)pawn).Map, (WipeMode)0);
				val3.stackCount = val2.stackCount;
				if (Props.isForbidden)
				{
					ForbidUtility.SetForbidden(val3, true, true);
				}
				if (Props.feedCauser && pawn?.needs?.food != null)
				{
					Need_Food food = pawn.needs.food;
					((Need)food).CurLevel = ((Need)food).CurLevel + Props.nutritionGained;
				}
				val2.Destroy((DestroyMode)0);
				break;
			}
		}
	}
}
