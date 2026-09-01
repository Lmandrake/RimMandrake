using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Tornado), "CellImmuneToDamage")]
public static class CellImmuneToDamage
{
	public static void Postfix(Tornado __instance, IntVec3 c, ref bool __result)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		if (__result)
		{
			return;
		}
		List<CompShieldField> list = CompShieldField.ListerShieldGensActiveIn(((Thing)__instance).Map).ToList();
		for (int i = 0; i < list.Count; i++)
		{
			CompShieldField compShieldField = list[i];
			if (compShieldField.coveredCells.Contains(c))
			{
				if (compShieldField.affectedThings == null)
				{
					compShieldField.affectedThings = new Dictionary<Thing, int>();
				}
				if (!compShieldField.affectedThings.ContainsKey((Thing)(object)__instance))
				{
					compShieldField.AbsorbDamage(30f, DamageDefOf.TornadoScratch, (Thing)(object)__instance);
					compShieldField.affectedThings.Add((Thing)(object)__instance, 15);
				}
				__result = true;
				break;
			}
		}
	}
}
