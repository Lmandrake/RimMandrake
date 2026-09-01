using RimWorld;
using Verse;

namespace VEF.Weapons;

public class PlaceWorker_ExpandedShowTurretRadius : PlaceWorker
{
	public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
	{
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		ExpandedShowTurretRadiusExtension extension = ((checkingDef != null) ? ((Def)checkingDef).GetModExtension<ExpandedShowTurretRadiusExtension>() : null);
		BuildableDef obj = ((checkingDef is ThingDef) ? checkingDef : null);
		object obj2;
		if (obj == null)
		{
			obj2 = null;
		}
		else
		{
			BuildingProperties building = ((ThingDef)obj).building;
			if (building == null)
			{
				obj2 = null;
			}
			else
			{
				ThingDef turretGunDef = building.turretGunDef;
				obj2 = ((turretGunDef != null) ? turretGunDef.Verbs.Find((VerbProperties v) => IsValidVerb(v, extension)) : null);
			}
		}
		VerbProperties val = (VerbProperties)obj2;
		if (val != null)
		{
			if (val.range > 0f && (extension == null || extension.drawMaxRange))
			{
				GenDraw.DrawRadiusRing(loc, val.range);
			}
			if (val.minRange > 0f && (extension == null || extension.drawMinRange))
			{
				GenDraw.DrawRadiusRing(loc, val.minRange);
			}
		}
		else
		{
			BuildableDef obj3 = ((checkingDef is ThingDef) ? checkingDef : null);
			object arg;
			if (obj3 == null)
			{
				arg = null;
			}
			else
			{
				BuildingProperties building2 = ((ThingDef)obj3).building;
				arg = ((building2 != null) ? Gen.ToStringSafe<ThingDef>(building2.turretGunDef) : null);
			}
			Log.ErrorOnce($"Trying to display turret range for {checkingDef} failed, since its turret ({arg}) " + "has no valid verbs to grab the range from. Either make sure the turret has a verb with a supported class, or use ExpandedShowTurretRadiusExtension def mod extension to specify supported verb classes.", Gen.HashCombineInt(((Def)(checkingDef?)).defNameHash ?? "null".GetHashCode(), 422220065));
		}
		return AcceptanceReport.op_Implicit(true);
	}

	private static bool IsValidVerb(VerbProperties v, ExpandedShowTurretRadiusExtension extension)
	{
		if (extension != null)
		{
			if (extension.allowedVerbClass != null)
			{
				if (extension.allowAnyVerb)
				{
					return extension.allowedVerbClass.IsAssignableFrom(v.verbClass);
				}
				return extension.allowedVerbClass == v.verbClass;
			}
			if (extension.allowAnyVerb)
			{
				return typeof(Verb).IsAssignableFrom(v.verbClass);
			}
		}
		if (!typeof(Verb_Shoot).IsAssignableFrom(v.verbClass) && !typeof(Verb_Spray).IsAssignableFrom(v.verbClass))
		{
			return typeof(Verb_ShootBeam).IsAssignableFrom(v.verbClass);
		}
		return true;
	}
}
