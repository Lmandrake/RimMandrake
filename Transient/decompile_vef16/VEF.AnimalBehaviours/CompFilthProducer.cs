using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

internal class CompFilthProducer : ThingComp
{
	public CompProperties_FilthProducer Props => (CompProperties_FilthProducer)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		if (!AnimalBehaviours_Settings.flagAnimalParticles || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.ticksToCreateFilth, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (((Thing)val).Map == null || !RestUtility.Awake(val) || val.Downed || val.Dead)
		{
			return;
		}
		CellRect val2 = GenAdj.OccupiedRect(((Thing)val).Position, ((Thing)val).Rotation, IntVec2.One);
		val2 = ((CellRect)(ref val2)).ExpandedBy(Props.radius);
		foreach (IntVec3 cell in ((CellRect)(ref val2)).Cells)
		{
			if (!GenGrid.InBounds(cell, ((Thing)val).Map) || !Rand.Chance(Props.rate))
			{
				continue;
			}
			int num = 0;
			List<Thing> list = ((Thing)base.parent).Map.thingGrid.ThingsListAt(cell);
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
				((Entity)obj).SpawnSetup(((Thing)val).Map, false);
			}
		}
	}
}
