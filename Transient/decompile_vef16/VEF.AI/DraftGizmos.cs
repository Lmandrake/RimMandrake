using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AI;

[HarmonyPatch]
[StaticConstructorOnStartup]
public static class DraftGizmos
{
	public static readonly Texture2D AutoCastTex = ContentFinder<Texture2D>.Get("UI/CheckAuto", true);

	public static readonly Texture2D VEFHuntIcon = ContentFinder<Texture2D>.Get("UI/Commands/VEF_Hunt", true);

	public static bool IsPlayerDraftedInsectoid(Pawn pawn)
	{
		if (((pawn != null) ? ((Thing)pawn).Faction : null) == Faction.OfPlayerSilentFail && pawn.Drafted && pawn != null)
		{
			RaceProperties raceProps = pawn.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Animal) : ((bool?)null)) == true)
			{
				return pawn.RaceProps.FleshType == FleshTypeDefOf.Insectoid;
			}
		}
		return false;
	}

	[HarmonyPatch(typeof(Pawn_DraftController), "GetGizmos")]
	[HarmonyPostfix]
	public static IEnumerable<Gizmo> GetGizmosPostfix(IEnumerable<Gizmo> __result, Pawn_DraftController __instance)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = __instance.pawn;
		if (IsPlayerDraftedInsectoid(pawn))
		{
			Command_ToggleWithRClick draftHunt2 = new Command_ToggleWithRClick
			{
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VEF.DraftHuntLabel")),
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF.HuntDescription")),
				icon = (Texture)(object)VEFHuntIcon,
				isActive = () => DraftedActionHolder.GetData(pawn).hunt,
				toggleAction = delegate
				{
					DraftedActionHolder.GetData(pawn).ToggleHuntMode();
				},
				rightClickAction = delegate
				{
					DraftedActionHolder.GetData(pawn).ToggleAutoForAll();
				},
				activateSound = SoundDefOf.Click,
				groupKey = 6173612,
				hotKey = KeyBindingDefOf.Misc1
			};
			return UpdateEnumerable(__result, draftHunt2);
		}
		return __result;
		static IEnumerable<Gizmo> UpdateEnumerable(IEnumerable<Gizmo> gizmos, Command_ToggleWithRClick draftHunt)
		{
			foreach (Gizmo gizmo in gizmos)
			{
				Command_Toggle val = (Command_Toggle)(object)((gizmo is Command_Toggle) ? gizmo : null);
				if (val != null && (Object)(object)((Command)val).icon == (Object)(object)TexCommand.Draft)
				{
					yield return (Gizmo)(object)val;
					yield return (Gizmo)(object)draftHunt;
				}
				else
				{
					yield return gizmo;
				}
			}
		}
	}

	[HarmonyPatch(typeof(Command), "GizmoOnGUIInt")]
	[HarmonyPostfix]
	public static void GizmoOnGUIPostfix(Command __instance, GizmoResult __result, Rect butRect, GizmoRenderParms parms)
	{
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Invalid comparison between Unknown and I4
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		if (!(((object)__instance).GetType() == typeof(Command_Ability)))
		{
			return;
		}
		Command_Ability val = (Command_Ability)(object)((__instance is Command_Ability) ? __instance : null);
		Pawn pawn = val.Pawn;
		if (IsPlayerDraftedInsectoid(pawn))
		{
			DraftedActionData data = DraftedActionHolder.GetData(pawn);
			if (data.AutoCastFor(val.Ability.def))
			{
				float num = (parms.shrunk ? 12f : 24f);
				GUI.DrawTexture(new Rect(((Rect)(ref butRect)).x + ((Rect)(ref butRect)).width - num, ((Rect)(ref butRect)).y, num, num), (Texture)(object)AutoCastTex);
			}
			if ((int)((GizmoResult)(ref __result)).State == 3)
			{
				data.ToggleAutoCastFor(val.Ability.def);
			}
		}
	}
}
