using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_FilthProducer : HediffComp
{
	public HediffCompProperties_FilthProducer Props => (HediffCompProperties_FilthProducer)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.ticksToCreateFilth, delta))
		{
			return;
		}
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (((Thing)pawn).Map == null || !RestUtility.Awake(pawn) || pawn.Downed || pawn.Dead)
		{
			return;
		}
		CellRect val = GenAdj.OccupiedRect(((Thing)pawn).Position, ((Thing)pawn).Rotation, IntVec2.One);
		val = ((CellRect)(ref val)).ExpandedBy(Props.radius);
		foreach (IntVec3 cell in ((CellRect)(ref val)).Cells)
		{
			if (!GenGrid.InBounds(cell, ((Thing)pawn).Map) || !Rand.Chance(Props.rate))
			{
				continue;
			}
			int num = 0;
			List<Thing> list = ((Thing)((Hediff)base.parent).pawn).Map.thingGrid.ThingsListAt(cell);
			for (int i = 0; i < list.Count; i++)
			{
				if (list[i] is Filth && ((Def)list[i].def).defName == Props.filthType)
				{
					num++;
				}
			}
			if (num < 3)
			{
				Thing obj = ThingMaker.MakeThing(ThingDef.Named(Props.filthType), (ThingDef)null);
				obj.Rotation = Rot4.North;
				obj.Position = cell;
				((Entity)obj).SpawnSetup(((Thing)pawn).Map, false);
			}
		}
	}
}
