using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(VerbTracker), "GetVerbsCommands")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_VerbTracker_GetVerbsCommands_Patch
{
	private static bool Prepare()
	{
		return VanillaExpandedFramework_CompEquippable_PrimaryVerb_Patch.IsActive;
	}

	private static IEnumerable<Command> Postfix(IEnumerable<Command> commands, VerbTracker __instance)
	{
		IVerbOwner directOwner = __instance.directOwner;
		CompEquippable val = (CompEquippable)(object)((directOwner is CompEquippable) ? directOwner : null);
		if (val != null)
		{
			CompMultiVerbWeapon comp = ((ThingComp)val).parent.GetComp<CompMultiVerbWeapon>();
			if (comp != null)
			{
				foreach (Command command in commands)
				{
					Command_VerbTarget target = (Command_VerbTarget)(object)((command is Command_VerbTarget) ? command : null);
					if (target == null || target.verb.verbProps.untranslatedLabel == comp.ActiveVerbData.verbLabel || !GenCollection.Any<CompProperties_MultiVerbWeapon.VerbData>(comp.Props.verbs, (Predicate<CompProperties_MultiVerbWeapon.VerbData>)((CompProperties_MultiVerbWeapon.VerbData d) => d.verbLabel == target.verb.verbProps.untranslatedLabel)))
					{
						yield return command;
					}
				}
				foreach (Command item in comp.CompGetSwitchModeGizmo())
				{
					yield return item;
				}
				yield break;
			}
		}
		foreach (Command command2 in commands)
		{
			yield return command2;
		}
	}
}
