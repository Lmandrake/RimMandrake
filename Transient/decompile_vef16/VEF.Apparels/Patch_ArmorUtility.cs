using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public static class Patch_ArmorUtility
{
	[HarmonyPatch(typeof(ArmorUtility), "GetPostArmorDamage")]
	public static class VanillaExpandedFramework_ArmorUtility_GetPostArmorDamage
	{
		public static bool Prefix(Pawn pawn, ref float amount, ref float armorPenetration, BodyPartRecord part, ref DamageDef damageDef, out bool deflectedByMetalArmor, out bool diminishedByMetalArmor, ref float __result)
		{
			deflectedByMetalArmor = false;
			diminishedByMetalArmor = false;
			if (damageDef.armorCategory != null)
			{
				StatDef armorRatingStat = damageDef.armorCategory.armorRatingStat;
				if (pawn.apparel != null)
				{
					List<Apparel> wornApparel = pawn.apparel.WornApparel;
					for (int i = 0; i < wornApparel.Count; i++)
					{
						Apparel val = wornApparel[i];
						if (((Thing)(object)val).IsShield(out var shieldComp) && shieldComp.UsableNow && shieldComp.CoversBodyPart(part))
						{
							float num = amount;
							NonPublicMethods.ArmorUtility_ApplyArmor(ref amount, armorPenetration, StatExtension.GetStatValue((Thing)(object)val, armorRatingStat, true, -1), (Thing)(object)val, ref damageDef, pawn, out var seventh);
							if (amount < 0.001f)
							{
								deflectedByMetalArmor = seventh;
								__result = 0f;
								return false;
							}
							if (amount < num)
							{
								diminishedByMetalArmor = seventh;
							}
						}
					}
				}
			}
			return true;
		}
	}

	[HarmonyPriority(800)]
	[HarmonyPatch(typeof(ArmorUtility), "ApplyArmor")]
	public static class VanillaExpandedFramework_ArmorUtility_ApplyArmor
	{
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator ilGen)
		{
			List<CodeInstruction> instructionList = instructions.ToList();
			Label firstLabel = ilGen.DefineLabel();
			instructionList[0].labels.Add(firstLabel);
			yield return new CodeInstruction(OpCodes.Ldarg_S, (object)3);
			yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_ArmorUtility_ApplyArmor), "IsShield", (Type[])null, (Type[])null));
			yield return new CodeInstruction(OpCodes.Brfalse, (object)firstLabel);
			yield return new CodeInstruction(OpCodes.Ldarg_S, (object)6);
			yield return new CodeInstruction(OpCodes.Ldarg_S, (object)3);
			yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_ArmorUtility_ApplyArmor), "ShieldUseDeflectMetalEffect", (Type[])null, (Type[])null));
			yield return instructionList.First((CodeInstruction i) => i.opcode == OpCodes.Br_S).Clone();
			for (int j = 0; j < instructionList.Count; j++)
			{
				yield return instructionList[j];
			}
		}

		private static bool IsShield(Thing armourThing)
		{
			return armourThing?.def.IsShield() ?? false;
		}

		private static bool ShieldUseDeflectMetalEffect(Thing armourThing)
		{
			return ThingCompUtility.TryGetComp<CompShield>(armourThing).Props.useDeflectMetalEffect;
		}
	}
}
