using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[StaticConstructorOnStartup]
internal static class VerbUtility
{
	[HarmonyPatch(typeof(VerbProperties), "AdjustedRange")]
	public static class VerbProperties_AdjustedRange_Patch
	{
		public static void Prefix(VerbProperties __instance, Verb ownerVerb, Thing attacker, out float __state)
		{
			__state = float.NaN;
			if (__instance.Ranged)
			{
				Pawn val = (Pawn)(object)((attacker is Pawn) ? attacker : null);
				if (val != null)
				{
					__state = __instance.range;
					__instance.range *= val.GetVerbRangeMultiplier();
				}
			}
		}

		public static void Finalizer(VerbProperties __instance, float __state)
		{
			if (!float.IsNaN(__state))
			{
				__instance.range = __state;
			}
		}
	}

	public static Pawn GetPawnAsHolder(this Thing thing)
	{
		Pawn pawnAsHolderInt = GetPawnAsHolderInt(thing);
		_ = pawnAsHolderInt?.carryTracker;
		return pawnAsHolderInt;
	}

	private static Pawn GetPawnAsHolderInt(Thing thing)
	{
		IThingHolder parentHolder = thing.ParentHolder;
		Pawn_EquipmentTracker val = (Pawn_EquipmentTracker)(object)((parentHolder is Pawn_EquipmentTracker) ? parentHolder : null);
		if (val != null)
		{
			return val.pawn;
		}
		IThingHolder parentHolder2 = thing.ParentHolder;
		return ((Pawn_ApparelTracker)(((parentHolder2 is Pawn_ApparelTracker) ? parentHolder2 : null)?)).pawn;
	}

	public static float GetVerbRangeMultiplier(this Pawn pawn)
	{
		try
		{
			return StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_VerbRangeFactor, true, 60);
		}
		catch
		{
			return 1f;
		}
	}
}
