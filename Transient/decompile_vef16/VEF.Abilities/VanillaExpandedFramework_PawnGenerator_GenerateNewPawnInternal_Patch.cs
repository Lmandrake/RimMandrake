using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace VEF.Abilities;

[HarmonyPatch(typeof(PawnGenerator), "GenerateNewPawnInternal")]
public class VanillaExpandedFramework_PawnGenerator_GenerateNewPawnInternal_Patch
{
	[HarmonyPostfix]
	public static void Postfix(Pawn __result)
	{
		if (__result == null)
		{
			return;
		}
		PawnKindDef kindDef = __result.kindDef;
		PawnKindAbilityExtension pawnKindAbilityExtension = ((kindDef != null) ? ((Def)kindDef).GetModExtension<PawnKindAbilityExtension>() : null);
		if (pawnKindAbilityExtension == null)
		{
			return;
		}
		if (pawnKindAbilityExtension.implantDef != null)
		{
			Pawn_HealthTracker health = __result.health;
			object obj;
			if (health == null)
			{
				obj = null;
			}
			else
			{
				HediffSet hediffSet = health.hediffSet;
				obj = ((hediffSet != null) ? hediffSet.GetFirstHediffOfDef(pawnKindAbilityExtension.implantDef, false) : null);
			}
			object obj2 = obj as Hediff_Abilities;
			if (obj2 == null)
			{
				HediffDef implantDef = pawnKindAbilityExtension.implantDef;
				RaceProperties raceProps = __result.RaceProps;
				object obj3;
				if (raceProps == null)
				{
					obj3 = null;
				}
				else
				{
					BodyDef body = raceProps.body;
					obj3 = ((body != null) ? GenCollection.FirstOrFallback<BodyPartRecord>((IEnumerable<BodyPartRecord>)body.GetPartsWithDef(VEFDefOf.Brain), (BodyPartRecord)null) : null);
				}
				obj2 = HediffMaker.MakeHediff(implantDef, __result, (BodyPartRecord)obj3) as Hediff_Abilities;
			}
			Hediff_Abilities hediff_Abilities = (Hediff_Abilities)obj2;
			if (hediff_Abilities != null)
			{
				hediff_Abilities.giveRandomAbilities = pawnKindAbilityExtension.giveRandomAbilities;
				Pawn_HealthTracker health2 = __result.health;
				if (health2 != null)
				{
					health2.AddHediff((Hediff)(object)hediff_Abilities, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				((Hediff_Level)hediff_Abilities).SetLevelTo(pawnKindAbilityExtension.initialLevel);
			}
		}
		CompAbilities comp = ((ThingWithComps)__result).GetComp<CompAbilities>();
		if (comp == null)
		{
			return;
		}
		foreach (AbilityDef giveAbility in pawnKindAbilityExtension.giveAbilities)
		{
			comp.GiveAbility(giveAbility);
		}
	}
}
