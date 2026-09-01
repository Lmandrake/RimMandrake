using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using Verse;

namespace VEF.Abilities;

[HarmonyBefore(new string[] { "legodude17.mvcf" })]
[HarmonyPatch(typeof(Pawn), "TryGetAttackVerb")]
public static class VanillaExpandedFramework_Pawn_TryGetAttackVerb_Patch
{
	[HarmonyPostfix]
	public static void Postfix(Pawn __instance, ref Verb __result, Thing target)
	{
		CompAbilities compAbilities = ThingCompUtility.TryGetComp<CompAbilities>((Thing)(object)__instance);
		if (compAbilities == null)
		{
			return;
		}
		string reason;
		List<Verb_CastAbility> list = (from ab in compAbilities.LearnedAbilities
			where ab.AutoCast && ab.IsEnabledForPawn(out reason) && (target == null || ab.CanHitTarget(LocalTargetInfo.op_Implicit(target)))
			select ab.verb).ToList();
		if (GenList.NullOrEmpty<Verb_CastAbility>((IList<Verb_CastAbility>)list))
		{
			return;
		}
		if (target != null)
		{
			Tuple<Verb, float> tuple = default(Tuple<Verb, float>);
			if (GenCollection.TryRandomElementByWeight<Tuple<Verb, float>>(CollectionExtensions.AddItem<Tuple<Verb, float>>(from x in list
				where x.ability.AICanUseOn(target)
				select x into ve
				select new Tuple<Verb, float>((Verb)(object)ve, ve.ability.Chance), new Tuple<Verb, float>(__result, 1f)), (Func<Tuple<Verb, float>, float>)((Tuple<Verb, float> t) => t.Item2), ref tuple))
			{
				__result = tuple.Item1;
			}
		}
		else
		{
			Verb val = GenCollection.MaxBy<Verb, float>(CollectionExtensions.AddItem<Verb>((IEnumerable<Verb>)list, __result), (Func<Verb, float>)((Verb ve) => ve.verbProps.range));
			__result = val;
		}
	}
}
