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
		/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU (Q8): the salt-water mental break.</summary>
		public static bool saltBreakEnabled = true;
		/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU (Q1): the small mood penalty for an awkward drink.</summary>
		public static bool roughDrinkPenalty = true;
		/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU (Q10): litres of potable water every net keeps back for drinkers. 0 = off.</summary>
		public static float drinkingReserveLitres = 200f;
		/// <summary>Owner Q12 (2026-10-17): buckets fight fires; snow and ice gathered into water; blood quenches sanguophages.</summary>
		public static bool bucketFirefighting = true;
		public static bool snowGathering = true;
		public static bool sanguophageBloodQuenches = true;
		/// <summary>§8.2 step 8: the colony stock of filled potable bottles pawns keep on their own (0 = no limit).</summary>
		public static int filledBottlesPerColonist = 3;
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
			Scribe_Values.Look(ref saltBreakEnabled, "saltBreakEnabled", true);
			Scribe_Values.Look(ref roughDrinkPenalty, "roughDrinkPenalty", true);
			Scribe_Values.Look(ref drinkingReserveLitres, "drinkingReserveLitres", 200f);
			Scribe_Values.Look(ref bucketFirefighting, "bucketFirefighting", true);
			Scribe_Values.Look(ref snowGathering, "snowGathering", true);
			Scribe_Values.Look(ref sanguophageBloodQuenches, "sanguophageBloodQuenches", true);
			Scribe_Values.Look(ref filledBottlesPerColonist, "filledBottlesPerColonist", 3);
			Scribe_Values.Look(ref dbhBottleBridge, "dbhBottleBridge", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Thirst");
			list.Label("Whose thirst rules run: " + RM_ThirstProvider.ModeLabel
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
				"Distilled water lifts the mood a little; salt water and brine quench less; "
				+ "toxic water quenches half and adds toxic buildup. Off: every drink hydrates like plain water with no side effects. "
				+ "Either way, salt water and brine are never drunk outside the salt-water break, and slime and toxic water only "
				+ "by a desperate pawn.");
			list.CheckboxLabeled("Desperate pawns drink slime and toxic water", ref lastResortDrinking,
				"Like eating rotten food: only when the thirst bar is empty and no clean water is in reach, and it is always the "
				+ "last pick. Slime brings a massive mood hit, a day of purging and the slime's own harm; toxic water brings toxic "
				+ "buildup. Off: they are never drunk, and a pawn with nothing else dehydrates. Works under Dubs Bad Hygiene's "
				+ "thirst too (read off Dubs' bar).");
			list.CheckboxLabeled("Salt-water mental break", ref saltBreakEnabled,
				"A parched pawn in a low mood, with no fresh water in reach, can break and drink salt water or brine until the bar "
				+ "reads full. It feels better for an hour or two; then salt poisoning sets in (nausea, confusion, seizures, "
				+ "death if untreated), and thirst comes back three times as fast. Fresh water and a doctor cure it. Never twice "
				+ "while still poisoned. Off: salt water is simply never drunk.");
			list.CheckboxLabeled("Awkward drinking is a little unpleasant", ref roughDrinkPenalty,
				"Cups, bottles and taps at home are free, and so are ponds and rivers. Drinking on the road, out in the field away "
				+ "from home, or scooped out of a bucket or barrel gives a small mood penalty for a few hours. Ascetic, tough and "
				+ "undergrounder pawns, wild people and tribal folk never mind. Off: no drink ever costs mood.");
			list.Label("Drinking reserve on every pipe network: " + (drinkingReserveLitres < 1f ? "off" : drinkingReserveLitres.ToString("F0") + " L"),
				tooltip: "Sprinklers and machines stop drawing drinkable water when a network is down to this much, so crops and "
				+ "industry never drink the colony dry. Pawns drinking at a tank are never held back. Salt water, fuel and other "
				+ "undrinkable liquids keep no reserve. 0 = off.");
			drinkingReserveLitres = UnityEngine.Mathf.Round(list.Slider(drinkingReserveLitres, 0f, 2000f) / 50f) * 50f;
			list.CheckboxLabeled("Buckets fight fires", ref bucketFirefighting,
				"A firefighter with a filled bucket of water near at hand throws it on a fire in the home area: the fire and its "
				+ "neighbours go out at once, and the bucket comes back empty. With no bucket near, fires are beaten out as usual. "
				+ "Off: buckets are never thrown.");
			list.CheckboxLabeled("Snow and ice can be gathered into water", ref snowGathering,
				"Where no liquid fresh water is in reach, an empty bucket is filled with snow or ice chips. A bucket of snow melts "
				+ "into a bucket of water after a couple of hours above freezing, or at once over a fire. Ice blocks melt into "
				+ "buckets of water at a campfire or stove. Off: snow is never gathered (the melt bills stay).");
			list.Label("Filled water bottles kept per colonist: " + (filledBottlesPerColonist <= 0 ? "no limit" : filledBottlesPerColonist.ToString()),
				tooltip: "Pawns fill bottles on their own only until the colony holds this many filled bottles of drinkable water "
				+ "per colonist (packed ones count), up to ten per trip. Bottles are for the road; at home pawns drink at taps "
				+ "and ponds. Buckets and barrels are not limited. 0 = fill every empty bottle.");
			filledBottlesPerColonist = (int)list.Slider(filledBottlesPerColonist, 0f, 10f);
			list.CheckboxLabeled("Sanguophages quench thirst with blood", ref sanguophageBloodQuenches,
				"For a pawn with a hemogen gene, a hemogen pack is also a full drink of water. Off: packs only give hemogen.");
			list.CheckboxLabeled("Our bottles count for Dubs Bad Hygiene's thirst (needs restart)", ref dbhBottleBridge,
				"With Dubs Bad Hygiene loaded, marks FlowWorks' drinkable bottles as Dubs drinkables. Off: Dubs' pawns ignore our "
				+ "bottles (an escape hatch if a Dubs update breaks the bridge). Takes effect at the next game start.");
		}
	}
}
