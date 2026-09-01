using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Pawn), "GetGizmos")]
public static class Pawn_GetGizmos_Patch
{
	public static string toggleCache;

	public static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> __result, Pawn __instance)
	{
		Pawn pawn = __instance;
		bool isDraftableAnimal = pawn.IsDraftableControllableAnimal();
		bool alreadyHasVanillaDraftButton = false;
		foreach (Gizmo item in __result)
		{
			Command_Toggle val = (Command_Toggle)(object)((item is Command_Toggle) ? item : null);
			if (val != null && ((Command)val).defaultDesc == toggleCache)
			{
				alreadyHasVanillaDraftButton = true;
			}
			yield return item;
		}
		if (pawn.abilities != null && !isDraftableAnimal && pawn.IsAbilityUserAnimal() && (!DebugSettings.godMode || (DebugSettings.godMode && !DebugSettings.ShowDevGizmos)))
		{
			foreach (Ability a in pawn.abilities.AllAbilitiesForReading)
			{
				bool visibleSecondary = (pawn.Drafted || a.def.displayGizmoWhileUndrafted) && a.GizmosVisible();
				foreach (Command gizmo in a.GetGizmos())
				{
					Command_Ability val2;
					if ((val2 = (Command_Ability)(object)((gizmo is Command_Ability) ? gizmo : null)) != null)
					{
						val2.devGizmo = !visibleSecondary && DebugSettings.ShowDevGizmos;
					}
					yield return (Gizmo)(object)gizmo;
				}
				foreach (Gizmo item2 in a.GetGizmosExtra())
				{
					yield return item2;
				}
			}
		}
		if (!alreadyHasVanillaDraftButton && isDraftableAnimal && pawn.drafter != null)
		{
			Command_Toggle val3 = new Command_Toggle();
			val3.toggleAction = delegate
			{
				pawn.drafter.Drafted = !pawn.drafter.Drafted;
			};
			val3.isActive = () => pawn.drafter.Drafted;
			((Command)val3).defaultLabel = TaggedString.op_Implicit(Translator.Translate(pawn.drafter.Drafted ? "CommandUndraftLabel" : "CommandDraftLabel"));
			((Command)val3).hotKey = KeyBindingDefOf.Command_ColonistDraft;
			((Command)val3).defaultDesc = TaggedString.op_Implicit(Translator.Translate("CommandToggleDraftDesc"));
			((Command)val3).icon = (Texture)(object)ContentFinder<Texture2D>.Get("ui/commands/Draft", true);
			val3.turnOnSound = SoundDefOf.DraftOn;
			((Command)val3).groupKey = 81729172;
			val3.turnOffSound = SoundDefOf.DraftOff;
			yield return (Gizmo)(object)val3;
		}
		foreach (ThingComp allComp in ((ThingWithComps)__instance).AllComps)
		{
			if (!(allComp is PawnGizmoProvider pawnGizmoProvider))
			{
				continue;
			}
			foreach (Gizmo gizmo2 in pawnGizmoProvider.GetGizmos())
			{
				yield return gizmo2;
			}
		}
	}

	static Pawn_GetGizmos_Patch()
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val = Translator.Translate("CommandToggleDraftDesc");
		toggleCache = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
	}
}
