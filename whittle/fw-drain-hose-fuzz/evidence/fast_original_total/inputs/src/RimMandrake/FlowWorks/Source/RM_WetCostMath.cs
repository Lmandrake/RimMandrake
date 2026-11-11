namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM (child of CANAL_COVER_DESIGN_WET_FOXHOLE; design
	/// design/RimMandrake/canal_cover_design_2026-10-17.md §5, §9, §10 step 4; owner rulings Q4, Q6, Q8 of 2026-10-18).
	/// The Verse-free arithmetic of what standing in water costs. Compiled into SelfTest; the Verse wiring is
	/// Swimming/RM_WetCosts.cs.
	///   - Aim (Q4): a shooter standing in water at chest depth or deeper has its own hit chance x0.85.
	///   - Cold (Q4): a pawn standing in water has its comfortable minimum temperature raised by +6 C (vanilla stat, so
	///     ordinary hypothermia comes sooner; no new hediff, no new kind of cold).
	///   - Swimmers cannot shoot (Q6): a pawn swimming (water over its head, standing) has no ranged verb.
	/// All three numbers PROVISIONAL defaults (FOUNDRY.md, owner 2026-10-03), each a Mod Setting.
	/// </summary>
	public static class RM_WetCostMath
	{
		/// <summary>Chest depth for a person: the water ladder's chest-deep stage (RM_WaterChestDeepStill) is 1.5 m.</summary>
		public const float PersonChestMetres = 1.5f;

		/// <summary>A person's height, RM_RelativeRulesMath.HeightByBand[2].</summary>
		public const float PersonHeightMetres = 1.75f;

		/// <summary>Chest depth as a share of the creature's own height ("relative to its height", item spec), so a person is
		/// at chest depth in exactly 1.5 m and a rat (0.5 m) in about 0.43 m.</summary>
		public const float ChestFraction = PersonChestMetres / PersonHeightMetres;

		/// <summary>PROVISIONAL: the shooter's own hit factor in chest-deep water (Q4: "about 15% worse").</summary>
		public const float DefaultAimFactor = 0.85f;

		/// <summary>PROVISIONAL: degrees C added to the comfortable minimum temperature while standing in water (Q4, §9).</summary>
		public const float DefaultColdOffset = 6f;

		/// <summary>Small slack so a body whose surface reads 1.4999 m (decilitre rounding) still counts as 1.5 m.</summary>
		public const float Slack = 0.005f;

		/// <summary>Water at or past this creature's chest.</summary>
		public static bool ChestDeep(float waterMetres, float heightMetres)
		{
			return heightMetres > 0f && waterMetres > 0f && waterMetres + Slack >= ChestFraction * heightMetres;
		}

		/// <summary>The shooter's factor: <paramref name="factor"/> when the setting is on and the shooter stands (not lying)
		/// in chest-deep water; 1 otherwise. A swimmer cannot shoot at all (<see cref="RangedAllowed"/>), so its factor is
		/// never read. The factor is clamped to [0, 1]: standing in water never helps aim.</summary>
		public static float AimFactor(bool on, float waterMetres, float heightMetres, bool lying, float factor)
		{
			if (!on || lying || !ChestDeep(waterMetres, heightMetres))
			{
				return 1f;
			}
			return factor < 0f ? 0f : (factor > 1f ? 1f : factor);
		}

		/// <summary>Degrees added to ComfyTemperatureMin: the offset while the setting is on and the pawn is in water.
		/// Never negative (being wet never makes the cold easier).</summary>
		public static float ColdOffset(bool on, bool inWater, float offset)
		{
			return on && inWater && offset > 0f ? offset : 0f;
		}

		/// <summary>Q6: may this verb fire? False only for a ranged verb of a swimmer while the setting is on.</summary>
		public static bool RangedAllowed(bool on, bool swimming, bool melee)
		{
			return melee || !on || !swimming;
		}
	}
}
