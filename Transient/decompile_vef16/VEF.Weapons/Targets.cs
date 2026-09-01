using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public class Targets : IExposable
{
	public Dictionary<Projectile, LocalTargetInfo> targetInfos;

	private List<Projectile> thingKeys;

	private List<LocalTargetInfo> targetValues;

	public void ExposeData()
	{
		Scribe_Collections.Look<Projectile, LocalTargetInfo>(ref targetInfos, "targetInfos", (LookMode)3, (LookMode)5, ref thingKeys, ref targetValues, true, false, false);
	}
}
