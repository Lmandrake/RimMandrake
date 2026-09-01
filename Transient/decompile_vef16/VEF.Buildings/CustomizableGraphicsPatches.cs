using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Buildings;

public static class CustomizableGraphicsPatches
{
	[HarmonyPatch]
	[HarmonyPatchCategory("LateHarmonyPatch")]
	private static class InjectImpliedDefComps
	{
		private static bool Prepare()
		{
			return AllowedToMakePatches;
		}

		private static IEnumerable<MethodBase> TargetMethods()
		{
			yield return AccessTools.DeclaredMethod(typeof(ThingDefGenerator_Buildings), "NewBlueprintDef_Thing", (Type[])null, (Type[])null);
			yield return AccessTools.DeclaredMethod(typeof(ThingDefGenerator_Buildings), "NewFrameDef_Thing", (Type[])null, (Type[])null);
		}

		private static void Postfix(ThingDef def, ThingDef __result)
		{
			CompProperties_CustomizableGraphic compProperties = def.GetCompProperties<CompProperties_CustomizableGraphic>();
			if (compProperties != null)
			{
				__result.comps.Add((CompProperties)(object)compProperties);
			}
		}
	}

	[HarmonyPatch(typeof(Blueprint_Build), "MakeSolidThing")]
	[HarmonyPatchCategory("LateHarmonyPatch")]
	private static class PreserveBlueprintOverride
	{
		private static bool Prepare()
		{
			return AllowedToMakePatches;
		}

		private static void Postfix(Blueprint_Build __instance, Thing __result)
		{
			if (ThingCompUtility.HasComp<CompCustomizableGraphic>((Thing)(object)__instance))
			{
				__result.overrideGraphicIndex = ((Thing)__instance).overrideGraphicIndex;
			}
		}
	}

	[HarmonyPatch(typeof(GhostUtility), "GhostGraphicFor")]
	[HarmonyPatchCategory("LateHarmonyPatch")]
	private static class UseUiIconForCustomizableGraphicGhosts
	{
		private static bool Prepare()
		{
			return AllowedToMakePatches;
		}

		private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			MethodInfo targetMethod = AccessTools.DeclaredPropertyGetter(typeof(GraphicData), "Linked");
			MethodInfo methodToInsert = AccessTools.DeclaredMethod(typeof(UseUiIconForCustomizableGraphicGhosts), "IsCustomizableGraphic", (Type[])null, (Type[])null);
			int totalPatched = 0;
			foreach (CodeInstruction instr in instructions)
			{
				yield return instr;
				if (CodeInstructionExtensions.Calls(instr, targetMethod))
				{
					yield return CodeInstruction.LoadArgument(1, false);
					yield return new CodeInstruction(OpCodes.Call, (object)methodToInsert);
					yield return new CodeInstruction(OpCodes.Or, (object)null);
					totalPatched++;
				}
			}
			if (totalPatched != 1)
			{
				Log.Error(string.Format("Patched incorrect amount of instructions for {0}.{1}. Expected: {2}, patched: {3}.", "GhostUtility", "GhostGraphicFor", 1, totalPatched));
			}
		}

		private static bool IsCustomizableGraphic(ThingDef def)
		{
			return def.GetCompProperties<CompProperties_CustomizableGraphic>() != null;
		}
	}

	[HarmonyPatch(typeof(GraphicUtility), "ExtractInnerGraphicFor")]
	[HarmonyPatchCategory("LateHarmonyPatch")]
	private static class UseCorrectGraphicForMinifiedThing
	{
		private static bool Prepare()
		{
			return AllowedToMakePatches;
		}

		private static bool Prefix(Graphic outerGraphic, Thing thing, ref int? indexOverride, ref Graphic __result)
		{
			Graphic_Indexed val = (Graphic_Indexed)(object)((outerGraphic is Graphic_Indexed) ? outerGraphic : null);
			if (val == null || !ThingCompUtility.HasComp<CompCustomizableGraphic>(thing))
			{
				return true;
			}
			if (indexOverride.HasValue)
			{
				__result = val.SubGraphicAtIndex(indexOverride.Value);
			}
			else
			{
				if (thing == null)
				{
					return true;
				}
				__result = val.SubGraphicFor(thing);
			}
			return false;
		}
	}

	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	[HarmonyPatchCategory("LateHarmonyPatch")]
	public static class Gravship_ThingPlacements_Patch
	{
		private static bool Prepare()
		{
			return AllowedToMakeGravshipRotationPatches;
		}

		private static void Prefix(Gravship __instance, Dictionary<Thing, PositionData> ___things, Rot4 ___tmpThingsRot)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			RotationDirection relativeRotation = Rot4.GetRelativeRotation(___tmpThingsRot, __instance.Rotation);
			if ((int)relativeRotation == 0)
			{
				return;
			}
			foreach (Thing key in ___things.Keys)
			{
				ThingCompUtility.TryGetComp<CompCustomizableGraphic>(key)?.Rotate(relativeRotation);
			}
		}
	}

	private static bool? allowedToMakePatches;

	private static bool allowedToMakeGravshipPatches;

	private static bool AllowedToMakePatches
	{
		get
		{
			if (!allowedToMakePatches.HasValue)
			{
				allowedToMakePatches = false;
				foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
				{
					CompProperties_CustomizableGraphic compProperties = allDef.GetCompProperties<CompProperties_CustomizableGraphic>();
					if (compProperties == null)
					{
						continue;
					}
					allowedToMakePatches = true;
					if (!ModsConfig.OdysseyActive || HasRotationData(compProperties.defaultGraphicData))
					{
						break;
					}
					if (compProperties.styledGraphicData == null)
					{
						continue;
					}
					using Dictionary<ThingStyleDef, List<CompProperties_CustomizableGraphic.CustomizableGraphicOptionData>>.ValueCollection.Enumerator enumerator2 = compProperties.styledGraphicData.Values.GetEnumerator();
					while (enumerator2.MoveNext() && !HasRotationData(enumerator2.Current))
					{
					}
				}
			}
			return allowedToMakePatches.Value;
			static bool HasRotationData(List<CompProperties_CustomizableGraphic.CustomizableGraphicOptionData> dataList)
			{
				foreach (CompProperties_CustomizableGraphic.CustomizableGraphicOptionData data in dataList)
				{
					if (data.clockwiseRotationIndex >= 0 && data.clockwiseRotationIndex < dataList.Count)
					{
						allowedToMakeGravshipPatches = true;
						return true;
					}
				}
				return false;
			}
		}
	}

	private static bool AllowedToMakeGravshipRotationPatches
	{
		get
		{
			if (AllowedToMakePatches)
			{
				return allowedToMakeGravshipPatches;
			}
			return false;
		}
	}
}
