using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class MechanicalColonistPatches
{
	[HarmonyPatch(typeof(GeneUtility), "AddedAndImplantedPartsWithXenogenesCount", new Type[] { typeof(Pawn) })]
	[HarmonyPriority(200)]
	public static class AddedAndImplantedPartsWithXenogenesCount_Patch
	{
		public static void Postfix(ref int __result, Pawn pawn)
		{
			BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(pawn);
			if (cacheUltraSpeed != null && cacheUltraSpeed.isMechanical)
			{
				__result += 2;
			}
		}
	}

	[CompilerGenerated]
	private sealed class _003C_003Ec__DisplayClass11_0
	{
		public Corpse __instance;

		public Pawn butcher;

		public float efficiency;
	}

	public static Dictionary<BodyDef, Dictionary<BodyPartDef, List<BodyPartRecord>>> cachedRecordsPerPartDefDefPerBodydef = new Dictionary<BodyDef, Dictionary<BodyPartDef, List<BodyPartRecord>>>();

	private static List<string> blackListMechanical = new List<string>(3) { "PsychophagyTarget", "ChronophagyTarget", "PhilophagyTarget" };

	private static List<string> blackListTrulyAgeless = new List<string>(1) { "ChronophagyTarget" };

	[HarmonyPatch(typeof(HealthUtility), "TryAnesthetize")]
	[HarmonyPrefix]
	[HarmonyPriority(200)]
	public static bool TryAnesthetizePatch(Pawn pawn)
	{
		BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(pawn);
		if (cacheUltraSpeed != null && cacheUltraSpeed.isMechanical)
		{
			return false;
		}
		return true;
	}

	[HarmonyPatch(typeof(FleshTypeDef), "ChooseWoundOverlay")]
	[HarmonyPrefix]
	[HarmonyPriority(200)]
	public static bool ChooseWoundOverlayPatch(ref ResolvedWound __result, FleshTypeDef __instance, Hediff hediff)
	{
		if (__instance != FleshTypeDefOf.Mechanoid)
		{
			BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(hediff.pawn);
			if (cacheUltraSpeed != null && cacheUltraSpeed.isMechanical)
			{
				__result = FleshTypeDefOf.Mechanoid.ChooseWoundOverlay(hediff);
				return false;
			}
		}
		return true;
	}

	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	[HarmonyPriority(int.MaxValue)]
	public static bool Deactivate_CompRottable(CompRottable __instance, ref bool __result)
	{
		ThingWithComps parent = ((ThingComp)__instance).parent;
		Corpse val = (Corpse)(object)((parent is Corpse) ? parent : null);
		if (val != null)
		{
			BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(val.InnerPawn);
			if (cacheUltraSpeed != null && cacheUltraSpeed.isMechanical)
			{
				__result = false;
				return false;
			}
		}
		return true;
	}

	[HarmonyPatch(typeof(Pawn_StyleTracker), "get_CanDesireLookChange")]
	[HarmonyPriority(int.MaxValue)]
	[HarmonyPrefix]
	public static bool CanDesireLookChangePrefix(Pawn_StyleTracker __instance, ref bool __result)
	{
		BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(__instance.pawn);
		if (cacheUltraSpeed != null && (cacheUltraSpeed.isMechanical || cacheUltraSpeed.disableLookChangeDesired))
		{
			return false;
		}
		return true;
	}

	[HarmonyPatch(typeof(BodyDef), "GetPartsWithDef")]
	[HarmonyPriority(200)]
	[HarmonyPostfix]
	public static void GetPartsWithDef_Postfix(ref IEnumerable<BodyPartRecord> __result, BodyDef __instance, BodyPartDef def)
	{
		if (!HumanPatcher.partImportsFromDictReverse.TryGetValue(def, out var value))
		{
			return;
		}
		if (!cachedRecordsPerPartDefDefPerBodydef.TryGetValue(__instance, out var value2))
		{
			value2 = new Dictionary<BodyPartDef, List<BodyPartRecord>>();
			cachedRecordsPerPartDefDefPerBodydef[__instance] = value2;
		}
		if (!value2.TryGetValue(def, out var value3))
		{
			value3 = new List<BodyPartRecord>();
			foreach (BodyPartDef item in value)
			{
				for (int i = 0; i < __instance.AllParts.Count; i++)
				{
					BodyPartRecord val = __instance.AllParts[i];
					if (val.def == item && !value3.Contains(val))
					{
						value3.Add(val);
					}
				}
			}
			cachedRecordsPerPartDefDefPerBodydef[__instance][def] = value3;
		}
		List<BodyPartRecord> list = __result.ToList();
		list.AddRange(value3);
		__result = list;
	}

	[HarmonyPatch(typeof(GenRecipe), "MakeRecipeProducts")]
	[HarmonyPrefix]
	[HarmonyPriority(800)]
	public static bool MakeRecipeProducts(ref IEnumerable<Thing> __result, RecipeDef recipeDef, Pawn worker, List<Thing> ingredients, Thing dominantIngredient, IBillGiver billGiver, Precept_ThingStyle precept = null, ThingStyleDef style = null, int? overrideGraphicIndex = null)
	{
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		RecipeExtension recipeExtension = recipeDef?.ExtensionsOnDef<RecipeExtension, RecipeDef>((List<Type>)null, (List<Type>)null, doSort: true)?.FirstOrDefault();
		if (recipeExtension != null)
		{
			PawnKindDef val = recipeExtension?.pawnKindDef;
			if (val != null)
			{
				__result = Array.Empty<Thing>();
				Faction val2 = Faction.OfPlayerSilentFail;
				if (val2 == null)
				{
					val2 = FactionUtility.DefaultFactionFrom(val.defaultFactionDef);
				}
				Pawn val3 = PawnGenerator.GeneratePawn(val, val2, (PlanetTile?)null);
				if (val3 != null)
				{
					GenSpawn.Spawn((Thing)(object)val3, ((Thing)worker).Position, ((Thing)worker).Map, (WipeMode)0);
					val3.relations.AddDirectRelation(BSDefs.BS_Creator, worker);
				}
				return false;
			}
		}
		return true;
	}

	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	[HarmonyPostfix]
	public static void PawnCanDo_Prefix(ref bool __result, PsychicRitualRoleDef __instance, Context context, Pawn pawn, TargetInfo target, ref AnyEnum reason)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(pawn);
		if (blackListMechanical.Contains(((Def)__instance).defName) && cacheUltraSpeed != null && cacheUltraSpeed.isMechanical)
		{
			__result = false;
			reason = AnyEnum.FromEnum<Condition>((Condition)33554432);
		}
		if (blackListTrulyAgeless.Contains(((Def)__instance).defName) && pawn.GetAllActiveGenes().Any((Gene x) => x is TrulyAgeless))
		{
			__result = false;
			reason = AnyEnum.FromEnum<Condition>((Condition)33554432);
		}
	}

	[HarmonyPatch(typeof(Corpse), "ButcherProducts", new Type[]
	{
		typeof(Pawn),
		typeof(float)
	})]
	[HarmonyPrefix]
	public static bool ButcherProducts_Prefix(ref IEnumerable<Thing> __result, Corpse __instance, Pawn butcher, float efficiency)
	{
		_003C_003Ec__DisplayClass11_0 CS_0024_003C_003E8__locals5 = new _003C_003Ec__DisplayClass11_0();
		CS_0024_003C_003E8__locals5.__instance = __instance;
		CS_0024_003C_003E8__locals5.butcher = butcher;
		CS_0024_003C_003E8__locals5.efficiency = efficiency;
		Corpse obj = CS_0024_003C_003E8__locals5.__instance;
		if (obj != null && ((Thing)(obj.InnerPawn?)).def?.IsMechanicalDef() == true)
		{
			__result = EnumerableFromLambda();
			return false;
		}
		return true;
		[IteratorStateMachine(typeof(_003C_003Ec__DisplayClass11_0._003C_003CButcherProducts_Prefix_003Eg__EnumerableFromLambda_007C0_003Ed))]
		IEnumerable<Thing> EnumerableFromLambda()
		{
			//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
			return new _003C_003Ec__DisplayClass11_0._003C_003CButcherProducts_Prefix_003Eg__EnumerableFromLambda_007C0_003Ed(-2)
			{
				_003C_003E4__this = CS_0024_003C_003E8__locals5
			};
		}
	}
}
