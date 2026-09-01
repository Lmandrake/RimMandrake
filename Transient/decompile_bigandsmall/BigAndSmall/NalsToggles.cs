using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class NalsToggles
{
	private static bool? faLoaded;

	public static bool FALoaded
	{
		get
		{
			bool valueOrDefault = faLoaded == true;
			if (!faLoaded.HasValue)
			{
				valueOrDefault = ModsConfig.IsActive("Nals.FacialAnimation");
				faLoaded = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static void ApplyNLPatches(Harmony harmony)
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Expected O, but got Unknown
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Expected O, but got Unknown
		harmony.Patch((MethodBase)AccessTools.PropertyGetter(typeof(PawnRenderNode), "DebugEnabled"), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod((Delegate)new Func<IEnumerable<CodeInstruction>, IEnumerable<CodeInstruction>>(DebugEnabledTranspiler)), (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(PawnRenderTree), "InitializeAncestors", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod((Delegate)new Action<PawnRenderTree>(InitializeAncestorsPostfix)), (HarmonyMethod)null, (HarmonyMethod)null);
	}

	private static PawnRenderNode GetHead(Pawn pawn)
	{
		return ((pawn == null) ? null : pawn.Drawer?.renderer?.renderTree?.rootNode)?.children?.Where((PawnRenderNode x) => x.Props.tagDef == PawnRenderNodeTagDefOf.Head).FirstOrDefault();
	}

	public static void ToggleNalsStuff(Pawn pawn, FacialAnimDisabler options)
	{
		if (!FALoaded)
		{
			return;
		}
		PawnRenderNode head = GetHead(pawn);
		if (head == null || GenList.NullOrEmpty<PawnRenderNode>((IList<PawnRenderNode>)head.children))
		{
			return;
		}
		PawnRenderNode[] children = head.children;
		foreach (PawnRenderNode val in children)
		{
			if (((object)val.Worker).GetType().ToString().Contains("NLFacial"))
			{
				if (((object)val).ToString().Contains("HeadControllerComp"))
				{
					val.debugEnabled = !options.headName.Contains("NOT_");
					val.requestRecache = true;
				}
				else if (((object)val).ToString().Contains("SkinControllerComp"))
				{
					val.debugEnabled = !options.skinName.Contains("NOT_");
					val.requestRecache = true;
				}
				else if (((object)val).ToString().Contains("BrowControllerComp"))
				{
					val.debugEnabled = !options.browName.Contains("NOT_");
					val.requestRecache = true;
				}
				else if (((object)val).ToString().Contains("LidControllerComp"))
				{
					val.debugEnabled = !options.lidName.Contains("NOT_");
					val.requestRecache = true;
				}
				else if (((object)val).ToString().Contains("EyeballControllerComp"))
				{
					val.debugEnabled = !options.eyeballName.Contains("NOT_");
					val.requestRecache = true;
				}
				else if (((object)val).ToString().Contains("MouthControllerComp"))
				{
					val.debugEnabled = !options.mouthName.Contains("NOT_");
					val.requestRecache = true;
				}
			}
		}
	}

	public static IEnumerable<CodeInstruction> DebugEnabledTranspiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Expected O, but got Unknown
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Expected O, but got Unknown
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		list.InsertRange(0, new _003C_003Ez__ReadOnlyArray<CodeInstruction>((CodeInstruction[])(object)new CodeInstruction[3]
		{
			new CodeInstruction(OpCodes.Ldarg_0, (object)null),
			new CodeInstruction(OpCodes.Ldfld, (object)AccessTools.Field(typeof(PawnRenderNode), "debugEnabled")),
			new CodeInstruction(OpCodes.Ret, (object)null)
		}));
		return list.AsEnumerable();
	}

	public static void InitializeAncestorsPostfix(PawnRenderTree __instance)
	{
		BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(__instance.pawn);
		if (cacheUltraSpeed != null)
		{
			FacialAnimDisabler facialAnimDisabler = cacheUltraSpeed.facialAnimDisabler;
			if (facialAnimDisabler != null)
			{
				ToggleNalsStuff(__instance.pawn, facialAnimDisabler);
			}
		}
	}
}
