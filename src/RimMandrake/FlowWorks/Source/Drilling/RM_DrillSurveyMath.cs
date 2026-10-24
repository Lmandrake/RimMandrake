namespace RimMandrake.FlowWorks.Drilling
{
	/// <summary>
	/// DRILL_PLACEMENT_ENFORCE_NO_DRY_HOLES (owner card 2026-10-22: "Should placement of a liquid drill or ground well be
	/// refused on a square the survey says holds no liquid? → Refuse on empty survey"). The survey is one per map
	/// (RM_MapComponent_SubsurfaceLiquid), so "the square holds no liquid" is the map's answer: surveyed and nothing found,
	/// or surveyed and the finite reserve already drawn to zero. Either refuses placement of a drill or bleed well. Ground
	/// nobody has surveyed yet is allowed (the placing hint still says "unsurveyed"). No Verse types: linked into the
	/// SelfTest project.
	/// </summary>
	public static class RM_DrillSurveyMath
	{
		public enum Verdict
		{
			Allowed,
			NoYield,
			Spent
		}

		/// <summary>surveyed: the map's survey has been rolled; hasYield: it found a drillable liquid; reserve: units left.</summary>
		public static Verdict Placement(bool surveyed, bool hasYield, float reserve)
		{
			if (!surveyed)
			{
				return Verdict.Allowed;
			}
			if (!hasYield)
			{
				return Verdict.NoYield;
			}
			return reserve <= 0f ? Verdict.Spent : Verdict.Allowed;
		}
		/// <summary>BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY: why a drill or bleed well is not pouring. One answer, the first
		/// failing condition, in the order Building_LiquidDrill.TickRare tests them, so the inspect line, the overhead icon
		/// and the tick can never disagree.</summary>
		public enum Block
		{
			None,
			DisabledInSettings,
			SwitchedOff,
			Unpowered,
			NoSubsurface,
			Unsurveyed,
			ReserveSpent,
			NoCanalForm,
			LiquidDisabledInSettings,
			OutletNotDug,
			OutletOtherLiquid,
			OutletBrimming
		}

		/// <summary>Plain facts about one drill at one moment (no Verse types).</summary>
		public struct State
		{
			public bool settingOn;
			public bool switchedOn;
			public bool needsPower;
			public bool powered;
			public bool surveyed;
			public bool hasYield;
			public float reserve;
			public bool hasCanalForm;
			public bool fluidAllowed;
			public bool outletDug;
			public bool outletOtherLiquid;
			public bool outletBrimming;
		}

		public static Block WhyNot(State s)
		{
			if (!s.settingOn) return Block.DisabledInSettings;
			if (!s.switchedOn) return Block.SwitchedOff;
			if (s.needsPower && !s.powered) return Block.Unpowered;
			if (!s.surveyed) return Block.Unsurveyed;
			if (!s.hasYield) return Block.NoSubsurface;
			if (!s.hasCanalForm) return Block.NoCanalForm;
			if (!s.outletDug) return Block.OutletNotDug;
			if (s.outletOtherLiquid) return Block.OutletOtherLiquid;
			if (!s.fluidAllowed) return Block.LiquidDisabledInSettings;
			if (s.outletBrimming) return Block.OutletBrimming;
			if (s.reserve <= 0f) return Block.ReserveSpent;
			return Block.None;
		}

		/// <summary>DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM: the pending units a drill write actually spent -- the decilitres that
		/// LANDED in the outlet (<paramref name="afterDl"/> - <paramref name="beforeDl"/>) in level units, never the levels it
		/// asked for. Filling a part-notch outlet to its brim lands less than a whole level (the brim write clears the part
		/// notch); charging the whole level burned the difference unlogged. Never negative.</summary>
		public static float SpentUnits(long beforeDl, long afterDl, long dlPerLevel, float unitPerLevel)
		{
			if (afterDl <= beforeDl || dlPerLevel <= 0)
			{
				return 0f;
			}
			return (float)((afterDl - beforeDl) / (double)dlPerLevel) * unitPerLevel;
		}
	}
}
