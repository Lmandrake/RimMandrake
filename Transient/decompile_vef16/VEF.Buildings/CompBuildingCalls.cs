using System.Collections.Generic;
using Verse;
using Verse.Sound;

namespace VEF.Buildings;

public class CompBuildingCalls : ThingComp
{
	public int tickCounter;

	public int nextTick;

	public CompProperties_BuildingCalls Props => (CompProperties_BuildingCalls)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
	}

	public override void Initialize(CompProperties props)
	{
		((ThingComp)this).Initialize(props);
		nextTick = ((IntRange)(ref Props.interval)).RandomInRange * 2000;
	}

	public override void CompTick()
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		if (tickCounter > nextTick)
		{
			SoundStarter.PlayOneShot(GenCollection.RandomElement<SoundDef>((IEnumerable<SoundDef>)Props.soundDefs), SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
			tickCounter = 0;
			nextTick = ((IntRange)(ref Props.interval)).RandomInRange * 2000;
		}
		tickCounter++;
	}
}
