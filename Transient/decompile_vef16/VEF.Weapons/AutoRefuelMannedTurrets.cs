using RimWorld;
using Verse;

namespace VEF.Weapons;

public class AutoRefuelMannedTurrets : DefModExtension
{
	protected bool logMissingMannableComp = true;

	public bool reloadsMoreThanSingleItem;

	public virtual bool ShouldAutoReload(Building building, bool currentResult)
	{
		if (currentResult)
		{
			return true;
		}
		Building_TurretGun val = (Building_TurretGun)(object)((building is Building_TurretGun) ? building : null);
		if (val == null)
		{
			return false;
		}
		CompRefuelable comp = ((ThingWithComps)val).GetComp<CompRefuelable>();
		if (comp != null)
		{
			return !comp.HasFuel;
		}
		return false;
	}

	public virtual int ModifyRefuelCount(Building building, Thing fuel)
	{
		CompRefuelable obj = ThingCompUtility.TryGetComp<CompRefuelable>((Thing)(object)building);
		if (obj == null)
		{
			return 1;
		}
		return obj.GetFuelCountToFullyRefuel();
	}

	public override void ResolveReferences(Def parentDef)
	{
		if (Prefs.DevMode && !parentDef.ignoreConfigErrors && logMissingMannableComp)
		{
			ThingDef val = (ThingDef)(object)((parentDef is ThingDef) ? parentDef : null);
			if (val == null || val.GetCompProperties<CompProperties_Mannable>() == null)
			{
				Log.Error(string.Format("{0} doesn't have mannable comp, which is required by {1}.", parentDef, "AutoRefuelMannedTurrets"));
			}
		}
	}
}
