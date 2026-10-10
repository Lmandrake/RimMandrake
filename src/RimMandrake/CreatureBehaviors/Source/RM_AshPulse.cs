using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// LONGSHADE_BEDAZZLE_MECHANICS_1 (smoke calendar, ash act). A DefModExtension on a
	/// GameConditionDef: while the condition is active, plants grow faster (growthRateFactor) and
	/// the wild-plant spawner wants more plants (plantDensityFactor).
	/// MEASURED via RimSage 2026-10-10: GameCondition has NO plant-growth virtual (Plant.GrowthRate
	/// hard-codes NoxiousHaze/Drought by DefOf), so growth rides a postfix on Plant.get_GrowthRate;
	/// density rides the real GameCondition.PlantDensityFactor virtual (RM_GameCondition_GrowthPulse).
	/// PROVISIONAL numbers live on the def; gated by conditionGrowthEffectsEnabled.
	/// </summary>
	public class RM_GrowthPulseExtension : DefModExtension
	{
		/// <summary>Multiplies Plant.GrowthRate. PROVISIONAL.</summary>
		public float growthRateFactor = 1f;

		/// <summary>Multiplies the wild-plant spawner's desired density. PROVISIONAL.</summary>
		public float plantDensityFactor = 1f;

		/// <summary>Inspect-pane label for the growth multiplier line.</summary>
		public string growthLabel = "ash";

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string err in base.ConfigErrors())
			{
				yield return err;
			}
			if (growthRateFactor < 0.1f || growthRateFactor > 4f)
			{
				yield return "RM_GrowthPulseExtension growthRateFactor must be within 0.1..4.";
			}
			if (plantDensityFactor < 0.1f || plantDensityFactor > 4f)
			{
				yield return "RM_GrowthPulseExtension plantDensityFactor must be within 0.1..4.";
			}
		}
	}

	/// <summary>
	/// LONGSHADE_BEDAZZLE_MECHANICS_1 (smoke calendar, sand-lock act). A DefModExtension on a
	/// GameConditionDef: while active, the listed terrains (empty = the sand-swim default set
	/// Sand / SoftSand / RM_DeepSand) stop counting as swim or bury ground, so every sand swimmer
	/// breaches (its own breach logic, with its wake and stagger: a readable sign) and nothing
	/// can submerge or lie buried until the condition ends. Gated by sandLockEffectsEnabled.
	/// </summary>
	public class RM_SandLockExtension : DefModExtension
	{
		public List<TerrainDef> lockedTerrains;
	}

	/// <summary>A GameCondition whose PlantDensityFactor reads RM_GrowthPulseExtension.</summary>
	public class RM_GameCondition_GrowthPulse : GameCondition
	{
		public override float PlantDensityFactor(Map map)
		{
			if (!RM_CreatureBehaviorsSettings.conditionGrowthEffectsEnabled)
			{
				return 1f;
			}
			RM_GrowthPulseExtension ext = def.GetModExtension<RM_GrowthPulseExtension>();
			return ext == null ? 1f : ext.plantDensityFactor;
		}
	}

	public static class RM_ConditionGround
	{
		/// <summary>Product of growthRateFactor over active growth-pulse conditions (1 when none / off).</summary>
		public static float GrowthFactor(Map map)
		{
			if (map == null || !RM_CreatureBehaviorsSettings.conditionGrowthEffectsEnabled)
			{
				return 1f;
			}
			float f = 1f;
			List<GameCondition> conds = map.gameConditionManager.ActiveConditions;
			for (int i = 0; i < conds.Count; i++)
			{
				RM_GrowthPulseExtension ext = conds[i].def.GetModExtension<RM_GrowthPulseExtension>();
				if (ext != null)
				{
					f *= ext.growthRateFactor;
				}
			}
			return f;
		}

		/// <summary>The active growth-pulse label for the inspect line, or null.</summary>
		public static string GrowthLabel(Map map)
		{
			List<GameCondition> conds = map.gameConditionManager.ActiveConditions;
			for (int i = 0; i < conds.Count; i++)
			{
				if (conds[i].def.GetModExtension<RM_GrowthPulseExtension>() != null)
				{
					return conds[i].def.label;
				}
			}
			return null;
		}

		private static readonly HashSet<TerrainDef> DefaultSand = new HashSet<TerrainDef>();
		private static bool defaultsBuilt;

		/// <summary>True while an active sand-lock condition packs this cell's terrain hard.</summary>
		public static bool SandLocked(IntVec3 c, Map map)
		{
			if (map == null || !RM_CreatureBehaviorsSettings.sandLockEffectsEnabled || !c.InBounds(map))
			{
				return false;
			}
			List<GameCondition> conds = map.gameConditionManager.ActiveConditions;
			TerrainDef t = null;
			for (int i = 0; i < conds.Count; i++)
			{
				RM_SandLockExtension ext = conds[i].def.GetModExtension<RM_SandLockExtension>();
				if (ext == null)
				{
					continue;
				}
				if (t == null)
				{
					t = c.GetTerrain(map);
					if (t == null)
					{
						return false;
					}
				}
				if (ext.lockedTerrains != null && ext.lockedTerrains.Count > 0)
				{
					if (ext.lockedTerrains.Contains(t))
					{
						return true;
					}
				}
				else
				{
					EnsureDefaults();
					if (DefaultSand.Contains(t))
					{
						return true;
					}
				}
			}
			return false;
		}

		private static void EnsureDefaults()
		{
			if (defaultsBuilt)
			{
				return;
			}
			defaultsBuilt = true;
			foreach (string n in new[] { "Sand", "SoftSand", "RM_DeepSand" })
			{
				TerrainDef t = DefDatabase<TerrainDef>.GetNamedSilentFail(n);
				if (t != null)
				{
					DefaultSand.Add(t);
				}
			}
		}
	}

	/// <summary>Postfixes Plant.get_GrowthRate (and its inspect breakdown) with the growth-pulse factor.</summary>
	[StaticConstructorOnStartup]
	public static class RM_Patch_ConditionGrowth
	{
		public static bool patched;

		static RM_Patch_ConditionGrowth()
		{
			try
			{
				Harmony harmony = new Harmony("mandrake.rm.creaturebehaviors.conditiongrowth");
				var rate = AccessTools.PropertyGetter(typeof(Plant), nameof(Plant.GrowthRate));
				var desc = AccessTools.PropertyGetter(typeof(Plant), nameof(Plant.GrowthRateCalcDesc));
				if (rate == null)
				{
					Log.Warning("[RM CreatureBehaviors] condition growth: Plant.GrowthRate not found; ash-pulse growth stays off.");
					return;
				}
				harmony.Patch(rate, postfix: new HarmonyMethod(typeof(RM_Patch_ConditionGrowth), nameof(Postfix_GrowthRate)));
				if (desc != null)
				{
					harmony.Patch(desc, postfix: new HarmonyMethod(typeof(RM_Patch_ConditionGrowth), nameof(Postfix_CalcDesc)));
				}
				patched = true;
			}
			catch (Exception e)
			{
				Log.Error("[RM CreatureBehaviors] condition growth patch failed: " + e);
			}
		}

		public static void Postfix_GrowthRate(Plant __instance, ref float __result)
		{
			if (__result <= 0f || !__instance.Spawned)
			{
				return;
			}
			__result *= RM_ConditionGround.GrowthFactor(__instance.Map);
		}

		public static void Postfix_CalcDesc(Plant __instance, ref string __result)
		{
			if (!__instance.Spawned)
			{
				return;
			}
			float f = RM_ConditionGround.GrowthFactor(__instance.Map);
			if (f != 1f)
			{
				string label = RM_ConditionGround.GrowthLabel(__instance.Map) ?? "ash";
				__result = (__result ?? "") + "\n" + "StatsReport_MultiplierFor".Translate(label) + ": " + f.ToStringPercent();
			}
		}
	}
}
