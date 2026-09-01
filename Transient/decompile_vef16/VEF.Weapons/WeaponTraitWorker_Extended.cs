using RimWorld;
using Verse;

namespace VEF.Weapons;

public class WeaponTraitWorker_Extended : WeaponTraitWorker
{
	public void Notify_Added(Thing thing)
	{
		WeaponTraitDefExtension modExtension = ((Def)base.def).GetModExtension<WeaponTraitDefExtension>();
		if (modExtension != null && modExtension.refreshMaxHitPointsStat)
		{
			StatDefOf.MaxHitPoints.Worker.ClearCacheForThing(thing);
			thing.HitPoints = thing.MaxHitPoints;
		}
	}

	public void Notify_TraitRemoved()
	{
	}
}
