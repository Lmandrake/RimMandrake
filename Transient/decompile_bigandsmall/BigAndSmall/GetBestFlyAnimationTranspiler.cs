using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class GetBestFlyAnimationTranspiler
{
	public static AnimationDef GetBestFlyAnimation_ForHumanlikeAnimal(Pawn pawn, Rot4? facingOverride = null)
	{
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Invalid comparison between Unknown and I4
		if (pawn.ageTracker == null)
		{
			return null;
		}
		if (!HumanlikeAnimalGenerator.humanlikeAnimals.TryGetValue(((Thing)pawn).def, out var value))
		{
			return null;
		}
		int lifeStageIndex = value.GetLifeStageIndex(pawn);
		List<PawnKindLifeStage> list = value.animalKind?.lifeStages;
		if (list == null)
		{
			return null;
		}
		Rot4 facing = (Rot4)(((_003F?)facingOverride) ?? ((Thing)pawn).Rotation);
		bool isFemale = (int)pawn.gender == 2;
		for (int num = lifeStageIndex; num >= 0; num--)
		{
			AnimationDef val = SelectAnimation(list[num]);
			if (val != null)
			{
				return val;
			}
		}
		return null;
		AnimationDef SelectAnimation(PawnKindLifeStage stage)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			if (stage == null)
			{
				return null;
			}
			if (facing == Rot4.South)
			{
				if (!isFemale)
				{
					return stage.flyingAnimationSouth;
				}
				return stage.flyingAnimationSouthFemale ?? stage.flyingAnimationSouth;
			}
			if (facing == Rot4.North)
			{
				if (!isFemale)
				{
					return stage.flyingAnimationNorth;
				}
				return stage.flyingAnimationNorthFemale ?? stage.flyingAnimationNorth;
			}
			if (!isFemale)
			{
				return stage.flyingAnimationEast;
			}
			return stage.flyingAnimationEastFemale ?? stage.flyingAnimationEast;
		}
	}

	[HarmonyPatch(typeof(Pawn_FlightTracker), "GetBestFlyAnimation")]
	[HarmonyPrefix]
	public static bool GetBestFlyAnimation_Prefix(ref AnimationDef __result, Pawn pawn, Rot4? facingOverride = null)
	{
		if (!HumanlikeAnimalGenerator.HasHumanlikeAnimals)
		{
			return true;
		}
		__result = GetBestFlyAnimation_ForHumanlikeAnimal(pawn, facingOverride);
		if (__result != null)
		{
			return false;
		}
		return true;
	}
}
