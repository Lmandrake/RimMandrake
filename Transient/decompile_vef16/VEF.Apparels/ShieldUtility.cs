using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Apparels;

public static class ShieldUtility
{
	private static bool initialized;

	public static int HandCount(this Pawn pawn)
	{
		int num = 0;
		HediffSet hediffSet = pawn.health.hediffSet;
		List<BodyPartRecord> list = pawn.RaceProps.body.GetPartsWithTag(BodyPartTagDefOf.ManipulationLimbCore).ToList();
		for (int i = 0; i < list.Count; i++)
		{
			BodyPartRecord val = list[i];
			num += val.GetChildParts(BodyPartTagDefOf.ManipulationLimbSegment).Count((BodyPartRecord p) => ((int)p.depth == 2 && !hediffSet.PartIsMissing(p)) || hediffSet.PartOrAnyAncestorHasDirectlyAddedParts(p));
		}
		return num;
	}

	public static bool CanUseShields(this Pawn p)
	{
		return p.HandCount() > 1;
	}

	public static bool IsShield(this Thing thing, out CompShield shieldComp)
	{
		if (thing is Apparel_Shield apparel_Shield)
		{
			shieldComp = apparel_Shield.CompShield;
			return shieldComp != null;
		}
		shieldComp = null;
		return false;
	}

	public static bool IsShield(this ThingDef tDef)
	{
		return tDef.HasComp(typeof(CompShield));
	}

	public static bool UsableWithShields(this ThingDef def)
	{
		if (!initialized)
		{
			VanillaShieldsExpandedStartup.SetValues();
			initialized = true;
		}
		ThingDefExtension modExtension = ((Def)def).GetModExtension<ThingDefExtension>();
		if (modExtension != null && modExtension.usableWithShields.HasValue)
		{
			return modExtension.usableWithShields.Value;
		}
		if (def.BaseMass >= 1.65f)
		{
			return false;
		}
		try
		{
			if (ModCompatibilityCheck.DualWield)
			{
				return !NonPublicMethods.DualWield.Ext_ThingDef_IsTwoHand(def) && NonPublicMethods.DualWield.Ext_ThingDef_CanBeOffHand(def);
			}
		}
		catch (Exception ex)
		{
			Log.Error("Dual Wield compatability is broken: " + ex.ToString());
		}
		return true;
	}

	public static ThingWithComps OffHandShield(this Pawn pawn)
	{
		Pawn_ApparelTracker apparel = pawn.apparel;
		if (apparel == null)
		{
			return null;
		}
		List<Apparel> wornApparel = apparel.WornApparel;
		if (wornApparel == null)
		{
			return null;
		}
		CompShield shieldComp;
		return (ThingWithComps)(object)GenCollection.FirstOrDefault<Apparel>(wornApparel, (Predicate<Apparel>)((Apparel t) => ((Thing)(object)t).IsShield(out shieldComp) && shieldComp.equippedOffHand));
	}

	public static void MakeRoomForShield(this Pawn pawn, ThingWithComps eq)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Expected O, but got Unknown
		if (pawn.OffHandShield() == null)
		{
			return;
		}
		Apparel val = default(Apparel);
		if (pawn.apparel.TryDrop((Apparel)pawn.OffHandShield(), ref val, ((Thing)pawn).Position, true))
		{
			if (val != null)
			{
				ForbidUtility.SetForbidden((Thing)(object)val, false, true);
			}
		}
		else
		{
			Log.Error(((object)pawn)?.ToString() + " couldn't make room for shield " + (object)eq);
		}
	}

	public static void AddShield(this Pawn pawn, Apparel newShield, bool dropReplacedApparel = false)
	{
		if (pawn.OffHandShield() != null)
		{
			Log.Error(string.Concat("Pawn ", ((Entity)pawn).LabelCap, " got shield ", newShield, " while already having shield "));
		}
		else
		{
			pawn.apparel.Wear(newShield, dropReplacedApparel, false);
		}
	}
}
