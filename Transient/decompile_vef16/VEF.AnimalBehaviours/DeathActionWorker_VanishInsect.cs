using RimWorld;
using Verse;
using Verse.AI.Group;

namespace VEF.AnimalBehaviours;

public class DeathActionWorker_VanishInsect : DeathActionWorker
{
	public DeathActionProperties_VanishInsect Props => (DeathActionProperties_VanishInsect)(object)base.props;

	public override void PawnDied(Corpse corpse, Lord prevLord)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		if (Props.fleck != null)
		{
			FleckMaker.Static(((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld, Props.fleck, 1f);
		}
		if (Props.filth != null)
		{
			int randomInRange = ((IntRange)(ref Props.filthCountRange)).RandomInRange;
			for (int i = 0; i < randomInRange; i++)
			{
				FilthMaker.TryMakeFilth(((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld, Props.filth, 1, (FilthSourceFlags)0, true);
			}
		}
		CellRect val = new CellRect(((Thing)corpse).PositionHeld.x, ((Thing)corpse).PositionHeld.z, 3, 3);
		CellRect val2 = ((CellRect)(ref val)).ClipInsideMap(((Thing)corpse).MapHeld);
		IntVec3 randomCell = ((CellRect)(ref val2)).RandomCell;
		ThingDef filth_BloodInsect = ThingDefOf.Filth_BloodInsect;
		if (GenGrid.InBounds(randomCell, ((Thing)corpse).MapHeld) && GenSight.LineOfSight(randomCell, ((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld))
		{
			FilthMaker.TryMakeFilth(randomCell, ((Thing)corpse).MapHeld, filth_BloodInsect, 1, (FilthSourceFlags)0, true);
		}
		((Thing)corpse).Destroy((DestroyMode)0);
	}
}
