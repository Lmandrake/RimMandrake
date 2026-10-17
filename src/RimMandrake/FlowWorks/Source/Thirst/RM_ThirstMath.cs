// THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (design/RimMandrake/thirst_bottles_design_2026-10-16.md, every OQ ruled by the
// owner by card 2026-10-16). The Verse-free arithmetic of FlowWorks' own thirst need, compiled into the mod AND into the
// SelfTest console app (Source/SelfTest/ThirstChecks.cs), so the numbers the selftest asserts are the numbers the game runs.
//
// Ruled numbers (OQ-3, "empty in about 1.25 days, up to 3x faster in heat, death about 3 days after empty"):
//   fall 0.8 / day at 1x (1.0 -> 0 in 1.25 days); a 1.5 L bottle restores 0.5 (litres / 3); heat x(1 + 0.05 per degree C
//   above the pawn's ComfyTemperatureMax), capped x3; hard labour x1.3; asleep x0.5.
//   RM_Dehydration +0.30 / day while the need is 0, -0.6 / day while it is above 0.3; lethal at 1.0 (~3.3 days at zero).
namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>Distilled > Potable > Fouled > Toxic. Mirrors LiquidTypes.LiquidThirstQuality value for value (kept apart so
	/// this file needs no Verse); RM_ThirstUtility converts.</summary>
	public enum RM_WaterQuality
	{
		Distilled = 0,
		Potable = 1,
		Fouled = 2,
		Toxic = 3,
		Slime = 4,
	}

	/// <summary>Mirrors LiquidTypes.LiquidUseClass value for value (THIRST_RULES_BUILD_SALT_OFF_THE_MENU, 04-merged.md §1/§8).</summary>
	public enum RM_DrinkUse
	{
		Potable = 0,
		LastResort = 1,
		BreakOnly = 2,
		Never = 3,
	}

	public enum RM_ThirstProviderMode
	{
		Own,
		Dbh,
	}

	public static class RM_ThirstMath
	{
		public const float TicksPerDay = 60000f;
		/// <summary>Vanilla Need.NeedInterval cadence (Pawn_NeedsTracker calls it every 150 ticks).</summary>
		public const float NeedIntervalTicks = 150f;

		public const float BaseFallPerDay = 0.8f;
		public const float InitialLevel = 0.8f;
		public const float LitresPerFullNeed = 3f;
		public const float HeatPerDegree = 0.05f;
		public const float HeatCap = 3f;
		public const float HardLabourFactor = 1.3f;
		public const float AsleepFactor = 0.5f;

		public const float ThirstyBelow = 0.3f;
		public const float ParchedBelow = 0.1f;

		public const float DehydrationGainPerDay = 0.30f;
		public const float DehydrationLossPerDay = 0.6f;
		public const float DehydrationLethal = 1f;

		/// <summary>A terrain drink (stand at the edge, 300 ticks) restores 0.5, the same as a 1.5 L bottle; it is slower.</summary>
		public const int TerrainDrinkTicks = 300;
		public const float TerrainDrinkLitres = 1.5f;
		public const int TankDrinkTicks = 120;
		public const float TankDrinkLitres = 1.5f;

		public const float FouledPoisonChance = 0.2f;
		public const float ToxicBuildupPerDrink = 0.12f;

		/// <summary>OQ-1: DBH's thirst runs and ours steps aside when DBH's NeedDef loaded AND a mod that turns it on is
		/// active (the Thirst add-on for Lite, or full DBH). Otherwise ours.</summary>
		public static RM_ThirstProviderMode ProviderMode(bool dbhNeedDefLoaded, bool thirstAddonActive, bool fullDbhActive,
			out string reason)
		{
			if (dbhNeedDefLoaded && (thirstAddonActive || fullDbhActive))
			{
				reason = "DBHThirst is loaded and " + (thirstAddonActive ? "Dubwise.DubsBadHygiene.Thirst" : "Dubwise.DubsBadHygiene")
					+ " is active: Dubs' thirst runs, RM_Thirst steps aside";
				return RM_ThirstProviderMode.Dbh;
			}
			reason = dbhNeedDefLoaded
				? "DBHThirst is loaded but neither the Thirst add-on nor full DBH is active"
				: "no DBHThirst NeedDef loaded";
			return RM_ThirstProviderMode.Own;
		}

		/// <summary>The heat factor: 1 + 0.05 per degree above the pawn's comfortable maximum, capped at 3.</summary>
		public static float HeatFactor(float ambientC, float comfyMaxC, bool heatScaling)
		{
			if (!heatScaling)
			{
				return 1f;
			}
			float over = ambientC - comfyMaxC;
			if (over <= 0f)
			{
				return 1f;
			}
			float f = 1f + HeatPerDegree * over;
			return f > HeatCap ? HeatCap : f;
		}

		public static float FallPerDay(float rateMultiplier, float heatFactor, bool hardLabour, bool asleep)
		{
			float f = BaseFallPerDay * rateMultiplier * heatFactor;
			if (hardLabour)
			{
				f *= HardLabourFactor;
			}
			if (asleep)
			{
				f *= AsleepFactor;
			}
			return f;
		}

		public static float FallPerInterval(float fallPerDay) => fallPerDay * NeedIntervalTicks / TicksPerDay;

		/// <summary>How much need one drink of <paramref name="litres"/> restores at a quality (before the 0..1 clamp).</summary>
		public static float Hydration(float litres, RM_WaterQuality quality, bool qualityEffects)
		{
			return litres / LitresPerFullNeed * HydrateFactor(quality, qualityEffects);
		}

		public static float HydrateFactor(RM_WaterQuality quality, bool qualityEffects)
		{
			if (!qualityEffects)
			{
				return 1f;
			}
			switch (quality)
			{
				case RM_WaterQuality.Fouled:
					return 0.7f;
				case RM_WaterQuality.Toxic:
					return 0.5f;
				case RM_WaterQuality.Slime:
					return SlimeHydrateFactor;
				default:
					return 1f;
			}
		}

		/// <summary>The quality the player actually gets: with quality effects off every drinkable is Potable.</summary>
		public static RM_WaterQuality Effective(RM_WaterQuality quality, bool qualityEffects)
		{
			return qualityEffects ? quality : RM_WaterQuality.Potable;
		}

		public const float SlimeHydrateFactor = 0.6f;

		/// <summary>Owner, Q5 2026-10-17: slime (and toxic water, Q8) "should follow the same rules for when people eat rotten
		/// food that makes them sick". Vanilla lets a pawn eat non-fresh food only when DESPERATE, which is hunger category
		/// Starving: the need at zero (FoodUtility.BestFoodSourceOnMap's desperate flag, JobGiver_GetFood). The mirror: a
		/// last-resort liquid only when the thirst need is empty.</summary>
		public static bool Desperate(float level) => level <= 0f;

		/// <summary>The one gate every drink search runs (04-merged.md §8). Humanlikes: Potable always; LastResort only when
		/// <see cref="Desperate"/> (and the setting allows it at all); BreakOnly (salt water, brine) only inside the salt-water
		/// break; Never never. Animals (Q12 part 2, "all animals can drink water and animals from biomes with terrible water can
		/// drink that terrible water"): Potable always; any other drinkable class only when native to the map's biome;
		/// Never never.</summary>
		public static bool MayDrink(RM_DrinkUse use, float level, bool humanlike, bool native, bool inSaltBreak,
			bool lastResortAllowed)
		{
			switch (use)
			{
				case RM_DrinkUse.Potable:
					return true;
				case RM_DrinkUse.Never:
					return false;
			}
			if (!humanlike)
			{
				return native;
			}
			if (use == RM_DrinkUse.LastResort)
			{
				return lastResortAllowed && Desperate(level);
			}
			return inSaltBreak;   // BreakOnly
		}

		/// <summary>True when source a is the better pick: use class first (any potable source beats any last resort, as a
		/// desperate pawn still ranks better food first), then quality, then nearer.</summary>
		public static bool Better(RM_DrinkUse useA, RM_WaterQuality a, float distA, RM_DrinkUse useB, RM_WaterQuality b, float distB)
		{
			if (useA != useB)
			{
				return (int)useA < (int)useB;
			}
			if (a != b)
			{
				return (int)a < (int)b;
			}
			return distA < distB;
		}

		/// <summary>Dehydration severity change over one need interval: up while empty, down while above 0.3, else none.</summary>
		public static float DehydrationDelta(float level, float intervalTicks)
		{
			if (level <= 0f)
			{
				return DehydrationGainPerDay * intervalTicks / TicksPerDay;
			}
			if (level > ThirstyBelow)
			{
				return -DehydrationLossPerDay * intervalTicks / TicksPerDay;
			}
			return 0f;
		}

		/// <summary>0 = fine, 1 = thirsty (&lt; 0.3), 2 = parched (&lt; 0.1), 3 = dehydrated (empty).</summary>
		public static int Category(float level)
		{
			if (level <= 0f)
			{
				return 3;
			}
			if (level < ParchedBelow)
			{
				return 2;
			}
			if (level < ThirstyBelow)
			{
				return 1;
			}
			return 0;
		}

		/// <summary>Days of thirst one container stock covers for <paramref name="drinkers"/> at the base rate (a readout).</summary>
		public static float DaysOfWater(float litres, int drinkers, float rateMultiplier)
		{
			if (drinkers <= 0 || rateMultiplier <= 0f)
			{
				return float.PositiveInfinity;
			}
			return litres / LitresPerFullNeed / (BaseFallPerDay * rateMultiplier * drinkers);
		}
	}
}
