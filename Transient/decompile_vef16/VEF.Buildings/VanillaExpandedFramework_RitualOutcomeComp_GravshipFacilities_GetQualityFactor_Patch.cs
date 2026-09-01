using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(RitualOutcomeComp_GravshipFacilities), "GetQualityFactor")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_RitualOutcomeComp_GravshipFacilities_GetQualityFactor_Patch
{
	private static HashSet<ThingDef> tmpUsedFacilitiesForCount = new HashSet<ThingDef>();

	private static bool Prepare()
	{
		return VanillaExpandedFramework_CompAffectedByFacilities_CanPotentiallyLinkTo_Patch.isActive;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr, ILGenerator generator)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		//IL_0239: Unknown result type (might be due to invalid IL or missing references)
		//IL_023f: Expected O, but got Unknown
		//IL_02c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c8: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instr, generator);
		CodeInstruction[] array = (CodeInstruction[])(object)new CodeInstruction[2]
		{
			CodeInstruction.LoadField(typeof(VanillaExpandedFramework_RitualOutcomeComp_GravshipFacilities_GetQualityFactor_Patch), "tmpUsedFacilitiesForCount", false),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Action>>)(() => tmpUsedFacilitiesForCount.Clear))
		};
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[1] { CodeMatch.Calls(AccessToolsExtensions.DeclaredMethod(typeof(Dictionary<ThingDef, int>), "Clear", (Type[])null, (Type[])null)) });
		if (val.IsInvalid)
		{
			Log.Error("[VEF] Failed patching RitualOutcomeComp_GravshipFacilities - couldn't find `tmpFacilityCount:Clear` call.");
		}
		val.InsertAfter(array);
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[4]
		{
			CodeMatch.LoadsLocal(false, (string)null),
			CodeMatch.LoadsLocal(false, (string)null),
			CodeMatch.Calls(AccessToolsExtensions.DeclaredMethod(typeof(ThingDef), "GetCompProperties", (Type[])null, (Type[])null).MakeGenericMethod(typeof(CompProperties_GravshipFacility))),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(CompProperties_Facility), "maxSimultaneous"), false)
		});
		if (val.IsInvalid)
		{
			Log.Error("[VEF] Failed patching RitualOutcomeComp_GravshipFacilities - couldn't find location where max simultaneous connections are calculated.");
		}
		Label label = default(Label);
		val.DefineLabel(ref label);
		val.Insert((CodeInstruction[])(object)new CodeInstruction[3]
		{
			CodeInstruction.LoadLocal(CodeInstructionExtensions.LocalIndex(val.InstructionAt(1)), true),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<_003C_003EF_007B00000001_007D<ThingDef, bool>>>)(() => HandleEquivalentFacility)),
			new CodeInstruction(OpCodes.Brfalse_S, (object)label)
		});
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[2]
		{
			CodeMatch.LoadsLocal(true, (string)null),
			CodeMatch.Calls(AccessToolsExtensions.DeclaredMethod(typeof(Dictionary<ThingDef, float>.Enumerator), "MoveNext", (Type[])null, (Type[])null))
		});
		if (val.IsInvalid)
		{
			Log.Error("[VEF] Failed patching RitualOutcomeComp_GravshipFacilities - failed to find Dictionary+Enumerator:MoveNext.");
		}
		val.AddLabels((IEnumerable<Label>)new _003C_003Ez__ReadOnlySingleElementList<Label>(label));
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[1]
		{
			new CodeMatch((OpCode?)OpCodes.Newobj, (object)AccessToolsExtensions.Constructor(typeof(QualityFactor), Array.Empty<Type>(), false), (string)null)
		});
		if (val.IsInvalid)
		{
			Log.Error("[VEF] Failed patching RitualOutcomeComp_GravshipFacilities - couldn't find `new QualityFactor` call near final return statement.");
		}
		val.Insert(array);
		return val.Instructions();
	}

	public static bool HandleEquivalentFacility(ref ThingDef def)
	{
		def = ((Def)def).GetModExtension<FacilityExtension>()?.equivalentToFacility ?? def;
		return tmpUsedFacilitiesForCount.Add(def);
	}
}
