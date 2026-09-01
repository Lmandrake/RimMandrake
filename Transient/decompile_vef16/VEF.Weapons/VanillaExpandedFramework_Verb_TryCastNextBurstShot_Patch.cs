using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_Verb_TryCastNextBurstShot_Patch
{
	public static IEnumerable<CodeInstruction> ChangeSoundProduced(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo verbProps = AccessTools.Field(typeof(Verb), "verbProps");
		FieldInfo soundCast = AccessTools.Field(typeof(VerbProperties), "soundCast");
		MethodInfo changeSound = AccessTools.Method(typeof(VanillaExpandedFramework_Verb_TryCastNextBurstShot_Patch), "ChangeSound", (Type[])null, (Type[])null);
		int position = 0;
		bool found = false;
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Ldarg_0 && codes[i + 1].opcode == OpCodes.Ldfld && CodeInstructionExtensions.OperandIs(codes[i + 1], (MemberInfo)verbProps) && codes[i + 2].opcode == OpCodes.Ldfld && CodeInstructionExtensions.OperandIs(codes[i + 2], (MemberInfo)soundCast) && codes[i + 3].opcode == OpCodes.Ldarg_0)
			{
				position = i;
				found = true;
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)changeSound);
			}
			else if (found && i > position && i < position + 3)
			{
				yield return new CodeInstruction(OpCodes.Nop, (object)null);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static SoundDef ChangeSound(Verb verb)
	{
		if (verb.EquipmentSource != null && StaticCollectionsClass.uniqueWeaponsInGame.Contains(((Thing)verb.EquipmentSource).def))
		{
			ThingWithComps equipmentSource = verb.EquipmentSource;
			CompUniqueWeapon val = ((equipmentSource != null) ? equipmentSource.GetComp<CompUniqueWeapon>() : null);
			if (val != null)
			{
				foreach (WeaponTraitDef item in val.TraitsListForReading)
				{
					WeaponTraitDefExtension modExtension = ((Def)item).GetModExtension<WeaponTraitDefExtension>();
					if (modExtension?.soundOverride != null)
					{
						return modExtension.soundOverride;
					}
				}
			}
		}
		return verb.verbProps.soundCast;
	}
}
