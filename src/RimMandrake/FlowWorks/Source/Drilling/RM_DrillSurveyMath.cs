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
	}
}
