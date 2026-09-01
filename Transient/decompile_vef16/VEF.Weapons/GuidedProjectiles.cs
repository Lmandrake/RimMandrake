using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public class GuidedProjectiles : MapComponent
{
	public Dictionary<Thing, Targets> launcherTargets = new Dictionary<Thing, Targets>();

	private List<Thing> thingKeys;

	private List<Targets> targetValues;

	public GuidedProjectiles(Map map)
		: base(map)
	{
	}

	public void RegisterTarget(Pawn launcher, LocalTargetInfo target)
	{
	}

	public override void ExposeData()
	{
		((MapComponent)this).ExposeData();
		Scribe_Collections.Look<Thing, Targets>(ref launcherTargets, "launcherTargets", (LookMode)3, (LookMode)2, ref thingKeys, ref targetValues, true, false, false);
	}
}
