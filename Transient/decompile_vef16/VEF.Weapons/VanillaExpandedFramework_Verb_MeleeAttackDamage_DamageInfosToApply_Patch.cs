using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_Verb_MeleeAttackDamage_DamageInfosToApply_Patch
{
	public static IEnumerable<CodeInstruction> ModifyMeleeDamage(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo meleeDamageDef = AccessTools.Field(typeof(VerbProperties), "meleeDamageDef");
		MethodInfo changeMeleeDamage = AccessTools.Method(typeof(VanillaExpandedFramework_Verb_MeleeAttackDamage_DamageInfosToApply_Patch), "ChangeMeleeDamage", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Ldfld && CodeInstructionExtensions.OperandIs(codes[i], (MemberInfo)meleeDamageDef))
			{
				yield return new CodeInstruction(OpCodes.Ldloc_2, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)changeMeleeDamage);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static DamageDef ChangeMeleeDamage(VerbProperties verbProps, Verb_MeleeAttackDamage verb)
	{
		if (((Verb)verb).EquipmentSource != null && StaticCollectionsClass.uniqueWeaponsInGame.Contains(((Thing)((Verb)verb).EquipmentSource).def))
		{
			ThingWithComps equipmentSource = ((Verb)verb).EquipmentSource;
			CompUniqueWeapon val = ((equipmentSource != null) ? equipmentSource.GetComp<CompUniqueWeapon>() : null);
			if (val != null)
			{
				foreach (WeaponTraitDef item in val.TraitsListForReading)
				{
					WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
					if (modExtension?.meleeDamageOverride != null)
					{
						return modExtension.meleeDamageOverride;
					}
				}
			}
		}
		return verbProps.meleeDamageDef;
	}
}
