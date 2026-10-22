using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Sheet
{
	/// <summary>CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, Stage 3: Mod Settings for canal overflow (design
	/// canal_overflow_flooding_2026-10-21.md §4 Stage 3 / D7). Own static class, scribed into the FlowWorks settings file from
	/// RimMandrakeFlowWorksSettings.ExposeData, the same shape as RM_SprinklerSettings. Every default IS the shipped behaviour.
	///
	/// ⚠ The master switch is default OFF until the Stage 4 live acceptance validates it. D7 (owner card) says the shipped default
	/// is ON ONCE VALIDATED; flipping this default is the Stage 4 sign-off, not a tuning choice. For tonight's walk turn it on with
	/// the checkbox, the dev-mode debug action "RMFlowWorks / Canal overflow: switch on/off (test)", or the bridge
	/// (jawa/mod_settings_field typeName=RimMandrake.FlowWorks.Sheet.RM_SheetSettings field=sheetOverflowEnabled value=True).
	/// OFF: no new spill is accepted, so every inflow behaves exactly as before (refused at the brim, fill-in's homeless
	/// remainder and a release's leftover disclosed as lost). Water already standing keeps draining by its normal exits.
	///
	/// Loss rates: the owner card of 2026-10-22 keeps the placeholder rates as the defaults, to be tuned on the walk.</summary>
	public static class RM_SheetSettings
	{
		public static bool sheetOverflowEnabled = false;

		// per-inflow switches (D1, D2). Off: that inflow behaves as before (refused at the brim / disclosed).
		public static bool spillFromPumps = true;
		public static bool spillFromRain = true;
		public static bool spillFromFloods = true;
		public static bool spillFromFillIn = true;
		public static bool spillFromGravity = true;

		// effects (Stage 2)
		public static bool cropsDrownEnabled = true;       // D3: a crop under standing overflow for the delay dies
		public static bool irrigateEnabled = true;         // D3: soaked-in water irrigates (Explosive Growth soak, when loaded)
		public static bool pawnEffectsEnabled = true;      // path cost + SoakingWet at sheet depth; drowning in deep standing water
		public static bool putsOutFireEnabled = true;      // water sheets put out fire

		// all liquids (owner 2026-10-22: "Build for all flowworks liquids.")
		public static bool otherLiquidsSpillEnabled = true; // every FlowWorks liquid spills, not only water (each by its FluidDef)
		public static bool fuelSpillsBurnEnabled = true;    // D5: spilled fuel spreads and burns (its own setting)

		// tuning (defaults = shipped). Whole numbers where the bridge sets them (jawa/mod_settings_field).
		public static int sheetCapCm = 50;                 // the deepest a sheet stands (a walled yard); lowering it deletes nothing
		public static int maxWetSquares = 4000;            // the most squares spilled water may cover on one map
		public static float retentionCm = 1f;              // D9: held moisture below this never flows
		public static int sweepsPerPulse = 3;
		public static int doorLeakPercent = 5;             // D4: a door edge passes this share of the normal flow
		public static int cropDrownPulses = 1680;          // D3: one week at the 250-tick pulse
		public static float soakCmPerDaySand = 4f, soakCmPerDaySoil = 2f, soakCmPerDayGravel = 1f;
		public static float dryCmPerDayAt20C = 0.5f;
		public static float roofedDryPercent = 30f;
		public static int sheetPathCost = 30;              // vanilla shallow floodwater's cost; a pool (over 15 cm) costs twice

		// shipped value of every public static setting above (RM_SettingsReset); MUST stay below the last setting field
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_SheetSettings));

		/// <summary>Does a spill from <paramref name="from"/> enter the sheet now (master switch and that inflow's switch)?</summary>
		public static bool SpillsFrom(RM_SheetMath.Source from)
		{
			if (!sheetOverflowEnabled)
			{
				return false;
			}
			switch (from)
			{
				case RM_SheetMath.Source.Pump: return spillFromPumps;
				case RM_SheetMath.Source.Rain: return spillFromRain;
				case RM_SheetMath.Source.Flood: return spillFromFloods;
				case RM_SheetMath.Source.FillIn: return spillFromFillIn;
				case RM_SheetMath.Source.Gravity: return spillFromGravity;
				default: return false;
			}
		}

		public static void ResetAll()
		{
			RM_SettingsReset.ResetAll(typeof(RM_SheetSettings), shippedDefaults);
		}

		public static void ExposeData()
		{
			Scribe_Values.Look(ref sheetOverflowEnabled, "sheetOverflowEnabled", false);
			Scribe_Values.Look(ref spillFromPumps, "sheetSpillFromPumps", true);
			Scribe_Values.Look(ref spillFromRain, "sheetSpillFromRain", true);
			Scribe_Values.Look(ref spillFromFloods, "sheetSpillFromFloods", true);
			Scribe_Values.Look(ref spillFromFillIn, "sheetSpillFromFillIn", true);
			Scribe_Values.Look(ref spillFromGravity, "sheetSpillFromGravity", true);
			Scribe_Values.Look(ref cropsDrownEnabled, "sheetCropsDrown", true);
			Scribe_Values.Look(ref irrigateEnabled, "sheetIrrigates", true);
			Scribe_Values.Look(ref pawnEffectsEnabled, "sheetPawnEffects", true);
			Scribe_Values.Look(ref putsOutFireEnabled, "sheetPutsOutFire", true);
			Scribe_Values.Look(ref otherLiquidsSpillEnabled, "sheetOtherLiquidsSpill", true);
			Scribe_Values.Look(ref fuelSpillsBurnEnabled, "sheetFuelSpillsBurn", true);
			Scribe_Values.Look(ref sheetCapCm, "sheetCapCm", 50);
			Scribe_Values.Look(ref maxWetSquares, "sheetMaxWetSquares", 4000);
			Scribe_Values.Look(ref retentionCm, "sheetRetentionCm", 1f);
			Scribe_Values.Look(ref sweepsPerPulse, "sheetSweepsPerPulse", 3);
			Scribe_Values.Look(ref doorLeakPercent, "sheetDoorLeakPercent", 5);
			Scribe_Values.Look(ref cropDrownPulses, "sheetCropDrownPulses", 1680);
			Scribe_Values.Look(ref soakCmPerDaySand, "sheetSoakSand", 4f);
			Scribe_Values.Look(ref soakCmPerDaySoil, "sheetSoakSoil", 2f);
			Scribe_Values.Look(ref soakCmPerDayGravel, "sheetSoakGravel", 1f);
			Scribe_Values.Look(ref dryCmPerDayAt20C, "sheetDryCmPerDay", 0.5f);
			Scribe_Values.Look(ref roofedDryPercent, "sheetRoofedDryPercent", 30f);
			Scribe_Values.Look(ref sheetPathCost, "sheetPathCost", 30);
		}

		private static string Days(int pulses) =>
			(pulses * (float)RimMandrakeFlowWorksSettings.PulseIntervalTicks / GenDate.TicksPerDay).ToString("0.#");

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Canal overflow (being tested: off until the live walk signs it off)");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetAll);
			list.CheckboxLabeled("Overfilled channels spill water onto the ground", ref sheetOverflowEnabled,
				"On: water that a full channel cannot take runs over the edge as a thin sheet on the ground around it. The sheet "
				+ "spreads until it is about 1 cm deep, lies level, runs back into any channel, pit or pond with room, soaks in and "
				+ "dries. Every litre is counted. Off: a full channel refuses the water as before. Water already "
				+ "spilled keeps draining away; turning this off never deletes it.");
			list.CheckboxLabeled("  Every liquid spills, not only water (fuel, oil, tar, slime, blood...)", ref otherLiquidsSpillEnabled,
				"Each spills by its own nature: thick liquids soak in and dry slowly, propane boils off, poison poisons whoever "
				+ "stands in it, and different liquids never mix (a square holding one refuses another). Off: only water spills; "
				+ "a full channel of anything else refuses as before.");
			list.CheckboxLabeled("  Spilled fuel spreads and burns", ref fuelSpillsBurnEnabled,
				"A fire or a blast on or beside spilled fuel lights it; the fire runs across the spill at the fuel's own speed, into "
				+ "any channel of fuel it touches and back, and burns the spill away (chemfuel fast, oil and tar slowly, astrofuel "
				+ "explodes). Burned fuel is counted in the ledger below. Needs 'Burning liquid' on.");
			list.Label("Which water spills (each needs the switch above):");
			list.CheckboxLabeled("  Pumps pouring into a full channel", ref spillFromPumps,
				"Off: a pump backed up against a full channel stays backed up, as before.");
			list.CheckboxLabeled("  Rain on a full channel", ref spillFromRain, "Off: rain a full channel cannot take is not added, as before.");
			list.CheckboxLabeled("  Floods and released liquid (forge floods, hot-spring kits, tar belches)", ref spillFromFloods,
				"A released flood fills the channels it reaches; what is left spills here. Off: what is left is counted as lost "
				+ "(a message says how much).");
			list.CheckboxLabeled("  Water squeezed out by filling a channel in", ref spillFromFillIn,
				"Off: water with no channel to go to is counted as lost (a message says how much), as before.");
			list.CheckboxLabeled("  Tanks draining into a full channel (gravity feed)", ref spillFromGravity,
				"A tank set to Dump stands above the ground, so it keeps pushing into a full channel and the extra spills over the "
				+ "edge. Off: the tank waits, as before.");
			list.Label("What standing water does:");
			list.CheckboxLabeled("  Crops drown under standing water after the delay below; before that it waters them", ref cropsDrownEnabled,
				"Water at least 2 cm deep standing on a plant for the whole delay kills it (not trees). A thinner film never does.");
			list.CheckboxLabeled("  Water that soaks in waters the ground (Explosive Growth)", ref irrigateEnabled,
				"Only when the Explosive Growth mod is loaded.");
			list.CheckboxLabeled("  Pawns wade (slower, soaking wet) and can drown lying in deep water", ref pawnEffectsEnabled);
			list.CheckboxLabeled("  Spilled water puts out fire", ref putsOutFireEnabled,
				"Any spill that does not burn puts out a fire standing in it; spilled fuel never does.");
			list.Label("Tuning (the defaults are the shipped game; loss rates are first guesses, to be tuned):");
			sheetCapCm = Mathf.RoundToInt(list.SliderLabeled("Deepest a sheet can stand: " + sheetCapCm + " cm", sheetCapCm, 5f, 100f, 0.5f,
				"Only a walled yard gets this deep. Lowering it stops further filling; water already deeper stays and drains away."));
			maxWetSquares = Mathf.RoundToInt(list.SliderLabeled("Most squares spilled water may cover on a map: " + maxWetSquares,
				maxWetSquares, 500f, 20000f, 0.5f, "Past this, new spills are refused back to the channel (the pump stays backed up). "
				+ "Nothing is deleted.") / 100f) * 100;
			retentionCm = Mathf.Round(list.SliderLabeled("Water the ground holds before it flows: " + retentionCm.ToString("0.0") + " cm",
				retentionCm, 0.5f, 5f, 0.5f, "Below this a sheet is damp ground: it stops spreading and only soaks in or dries.") * 2f) / 2f;
			sweepsPerPulse = Mathf.RoundToInt(list.SliderLabeled("How fast it spreads (steps per flow pulse): " + sweepsPerPulse,
				sweepsPerPulse, 1f, 6f, 0.5f));
			doorLeakPercent = Mathf.RoundToInt(list.SliderLabeled("Water leaking under a door: " + doorLeakPercent + "% of open ground",
				doorLeakPercent, 0f, 50f, 0.5f));
			float days = cropDrownPulses * (float)RimMandrakeFlowWorksSettings.PulseIntervalTicks / GenDate.TicksPerDay;
			days = Mathf.Round(list.SliderLabeled("Crops drown after standing in water for: " + Days(cropDrownPulses) + " days", days,
				0.5f, 30f, 0.5f) * 2f) / 2f;
			cropDrownPulses = Mathf.Max(1, RM_SheetMath.PulsesFor(Mathf.RoundToInt(days * GenDate.TicksPerDay), RimMandrakeFlowWorksSettings.PulseIntervalTicks));
			soakCmPerDaySand = Mathf.Round(list.SliderLabeled("Soaks into sand: " + soakCmPerDaySand.ToString("0.0") + " cm a day",
				soakCmPerDaySand, 0f, 20f, 0.5f) * 2f) / 2f;
			soakCmPerDaySoil = Mathf.Round(list.SliderLabeled("Soaks into soil: " + soakCmPerDaySoil.ToString("0.0") + " cm a day",
				soakCmPerDaySoil, 0f, 20f, 0.5f) * 2f) / 2f;
			soakCmPerDayGravel = Mathf.Round(list.SliderLabeled("Soaks into gravel and poor ground: " + soakCmPerDayGravel.ToString("0.0")
				+ " cm a day", soakCmPerDayGravel, 0f, 20f, 0.5f) * 2f) / 2f;
			dryCmPerDayAt20C = Mathf.Round(list.SliderLabeled("Dries in the open at 20 °C: " + dryCmPerDayAt20C.ToString("0.0") + " cm a day",
				dryCmPerDayAt20C, 0f, 5f, 0.5f, "Hotter dries faster (up to 3x), at or below 0 °C nothing dries.") * 10f) / 10f;
			roofedDryPercent = Mathf.Round(list.SliderLabeled("Under a roof it dries at: " + roofedDryPercent.ToString("0") + "%",
				roofedDryPercent, 0f, 100f, 0.5f) / 5f) * 5f;
			sheetPathCost = Mathf.RoundToInt(list.SliderLabeled("Wading cost (path cost at 2 cm and deeper): " + sheetPathCost,
				sheetPathCost, 0f, 100f, 0.5f));
			if (Current.ProgramState == ProgramState.Playing && Find.CurrentMap != null)
			{
				RM_MapComponent_Sheet sheet = Find.CurrentMap.GetComponent<RM_MapComponent_Sheet>();
				if (sheet != null)
				{
					list.Label("This map: " + sheet.LedgerLine());
					if (sheet.WetCells > 0 && list.ButtonText("Dry all spilled water on this map now (counted as dried by hand)"))
					{
						sheet.DryAll();
					}
				}
			}
		}
	}
}
