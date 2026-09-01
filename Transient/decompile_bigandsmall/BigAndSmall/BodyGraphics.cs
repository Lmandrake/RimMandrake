using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class BodyGraphics
{
	public static void CalculateBodyGraphicsForPawn(PawnRenderNode_Body __instance, Pawn pawn, ref Graphic __result, BSCache cache)
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Invalid comparison between Unknown and I4
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		if (cache.hideBody)
		{
			__result = GraphicsHelper.GetBlankMaterial();
			return;
		}
		if ((int)pawn.Drawer.renderer.CurRotDrawMode == 4)
		{
			if (cache.bodyDessicatedGraphicPath != null)
			{
				string bodyDessicatedGraphicPath = cache.bodyDessicatedGraphicPath;
				Graphic val = GraphicsHelper.TryGetCustomGraphics((PawnRenderNode)(object)__instance, bodyDessicatedGraphicPath, __result.color, __result.colorTwo, Color.white, __result.drawSize, cache.bodyMaterial);
				if (val != null)
				{
					__result = val;
				}
				else
				{
					Log.ErrorOnce($"Failed to get dessicated body graphic for {((pawn != null) ? pawn.Name : null)} at {bodyDessicatedGraphicPath}. Keeping previous graphic instead", 93484);
				}
				return;
			}
			CustomMaterial bodyMaterial = cache.bodyMaterial;
			if (bodyMaterial == null || !bodyMaterial.overrideDesiccated)
			{
				return;
			}
		}
		string bodyGraphicPath = cache.bodyGraphicPath;
		if (bodyGraphicPath != null)
		{
			Graphic val2 = GraphicsHelper.TryGetCustomGraphics((PawnRenderNode)(object)__instance, bodyGraphicPath, __result.color, __result.colorTwo, Color.white, __result.drawSize, cache.bodyMaterial);
			if (val2 != null)
			{
				__result = val2;
			}
			else
			{
				Log.ErrorOnce($"Failed to get body graphic for {((pawn != null) ? pawn.Name : null)} at {bodyGraphicPath}. Keeping previous graphic instead.", 99333);
			}
		}
		else if (ShowStandardBody(pawn, __result))
		{
			GenderMethods.TrySetGenderBody(__instance, pawn, ref __result);
		}
	}

	public static bool ShowStandardBody(Pawn pawn, Graphic __result)
	{
		if (__result.path == null)
		{
			return false;
		}
		int num;
		if (pawn == null || !pawn.IsMutant)
		{
			if (pawn == null)
			{
				num = 0;
			}
			else
			{
				Pawn_MutantTracker mutant = pawn.mutant;
				bool? obj;
				if (mutant == null)
				{
					obj = null;
				}
				else
				{
					MutantDef def = mutant.Def;
					obj = ((def != null) ? new bool?(GenList.NullOrEmpty<BodyTypeGraphicData>((IList<BodyTypeGraphicData>)def.bodyTypeGraphicPaths)) : ((bool?)null));
				}
				num = ((obj == false) ? 1 : 0);
			}
		}
		else
		{
			num = 0;
		}
		int num2;
		if (pawn != null && !pawn.IsCreepJoiner && pawn?.story?.bodyType != null)
		{
			if (pawn == null)
			{
				num2 = 0;
			}
			else
			{
				Pawn_CreepJoinerTracker creepjoiner = pawn.creepjoiner;
				bool? obj2;
				if (creepjoiner == null)
				{
					obj2 = null;
				}
				else
				{
					CreepJoinerFormKindDef form = creepjoiner.form;
					obj2 = ((form != null) ? new bool?(GenList.NullOrEmpty<BodyTypeGraphicData>((IList<BodyTypeGraphicData>)form.bodyTypeGraphicPaths)) : ((bool?)null));
				}
				num2 = ((obj2 == false) ? 1 : 0);
			}
		}
		else
		{
			num2 = 0;
		}
		bool flag = (byte)num2 != 0;
		if (num == 0 && !flag && pawn.story?.bodyType?.bodyNakedGraphicPath != null)
		{
			return !__result.path.Contains("EmptyImage");
		}
		return false;
	}
}
