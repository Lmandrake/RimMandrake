using Verse;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>Mod Settings section "Thirst" (THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY, design §6). Own static class, scribed
	/// into the FlowWorks settings file from RimMandrakeFlowWorksSettings.ExposeData and drawn by its window, the same shape
	/// as RM_QuarrySettings. Defaults = the ruled, shipped behaviour (animalsGetThirst ON: owner by card, OQ-5). All off
	/// leaves FlowWorks whole: bottles are plain items that fill, wash and trade. No toggle changes map generation.
	/// There is no provider switch: two thirst needs can never be forced on one pawn.</summary>
	public static class RM_ThirstSettings
	{
		public static bool thirstEnabled = true;
		public static float thirstRateMultiplier = 1f;
		public static bool thirstHeatScaling = true;
		public static bool animalsGetThirst = true;
		public static bool drinkFromTerrain = true;
		public static bool waterQualityEffects = true;
		/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU (Q5/Q8): a pawn desperate with thirst may drink slime or toxic water.</summary>
		public static bool lastResortDrinking = true;
		/// <summary>Read once, while patches apply (RM_PatchOperation_ThirstBridge): needs a restart.</summary>
		public static bool dbhBottleBridge = true;

		public static float RateMultiplier => thirstRateMultiplier < 0.25f ? 0.25f : (thirstRateMultiplier > 3f ? 3f : thirstRateMultiplier);

		public static void ExposeData()
		{
			Scribe_Values.Look(ref thirstEnabled, "thirstEnabled", true);
			Scribe_Values.Look(ref thirstRateMultiplier, "thirstRateMultiplier", 1f);
			Scribe_Values.Look(ref thirstHeatScaling, "thirstHeatScaling", true);
			Scribe_Values.Look(ref animalsGetThirst, "animalsGetThirst", true);
			Scribe_Values.Look(ref drinkFromTerrain, "drinkFromTerrain", true);
			Scribe_Values.Look(ref waterQualityEffects, "waterQualityEffects", true);
			Scribe_Values.Look(ref lastResortDrinking, "lastResortDrinking", true);
			Scribe_Values.Look(ref dbhBottleBridge, "dbhBottleBridge", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Thirst");
			list.Label("Thirst provider: " + RM_ThirstProvider.ModeLabel
				+ "  (read at startup; with Dubs Bad Hygiene's thirst running, ours steps aside and our bottles count for Dubs')");
			list.CheckboxLabeled("Pawns and animals get thirsty (FlowWorks thirst)", ref thirstEnabled,
				"A thirst bar that empties in about a day and a quarter, faster in heat. At empty, dehydration sets in and kills "
				+ "in about three days. Bottles, ponds, rivers and tanks quench it. Has no effect while Dubs Bad Hygiene's own "
				+ "thirst runs. Off: nobody gets FlowWorks thirst; bottles can still be drunk and their water quality still counts.");
			list.Label("Thirst rate: x" + RateMultiplier.ToString("F2") + "  (1x = empty in 1.25 days at a comfortable temperature)");
			thirstRateMultiplier = list.Slider(thirstRateMultiplier, 0.25f, 3f);
			list.CheckboxLabeled("Heat makes pawns thirstier", ref thirstHeatScaling,
				"Each degree above a pawn's comfortable maximum adds 5% to the rate, up to three times as fast. Off: a flat rate.");
			list.CheckboxLabeled("Animals get thirsty too", ref animalsGetThirst,
				"Every animal, wild and tame, gets the thirst bar and drinks from ponds and rivers (never from bottles or tanks). "
				+ "An animal far from water dehydrates, and its health tab says so. Off: no animal gets FlowWorks thirst.");
			list.CheckboxLabeled("Pawns can drink straight from ponds and rivers", ref drinkFromTerrain,
				"Slower than a bottle, at that water's quality. Off: pawns drink only from bottles and tanks (the hard scavenger "
				+ "mode). Animals always drink from terrain.");
			list.CheckboxLabeled("Water quality matters", ref waterQualityEffects,
				"Distilled water lifts the mood a little; fouled water (salt, brine) quenches less and can cause food poisoning; "
				+ "toxic water quenches half and adds toxic buildup. Off: every drink hydrates like plain water with no side effects. "
				+ "Either way, salt water and brine are never drunk outside the salt-water break, and slime and toxic water only "
				+ "by a desperate pawn.");
			list.CheckboxLabeled("Desperate pawns drink slime and toxic water", ref lastResortDrinking,
				"Like eating rotten food: only when the thirst bar is empty and no clean water is in reach, and it is always the "
				+ "last pick. Slime brings a massive mood hit, a day of purging and the slime's own harm; toxic water brings toxic "
				+ "buildup. Off: they are never drunk, and a pawn with nothing else dehydrates.");
			list.CheckboxLabeled("Our bottles count for Dubs Bad Hygiene's thirst (needs restart)", ref dbhBottleBridge,
				"With Dubs Bad Hygiene loaded, marks FlowWorks' drinkable bottles as Dubs drinkables. Off: Dubs' pawns ignore our "
				+ "bottles (an escape hatch if a Dubs update breaks the bridge). Takes effect at the next game start.");
		}
	}
}
