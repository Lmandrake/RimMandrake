using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// LONGSHADE_BEDAZZLE_MECHANICS_1 (smoke calendar, haze act). A DefModExtension on a
	/// GameConditionDef: while the condition is active on a map, the shade grid's cast
	/// shadows run longer ("every shadow lengthens") and the camera heat bed is muffled
	/// ("haze muffles everything", LONGSHADE_GPT_ENRICHMENT_1 section 3). Mirrak false shade does
	/// not read the grid's cast length, so mirraks stay short by construction.
	/// PROVISIONAL numbers live on the def (comment there); gated by smokeHazeEffectsEnabled.
	/// </summary>
	public class RM_ShadeHazeExtension : DefModExtension
	{
		/// <summary>Multiplies the sun's shadow length per unit height. PROVISIONAL.</summary>
		public float shadowLengthFactor = 1f;

		/// <summary>Multiplies the camera heat-bed volume. PROVISIONAL.</summary>
		public float soundVolumeFactor = 1f;

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string err in base.ConfigErrors())
			{
				yield return err;
			}
			if (shadowLengthFactor < 0.1f || shadowLengthFactor > 4f)
			{
				yield return "RM_ShadeHazeExtension shadowLengthFactor must be within 0.1..4.";
			}
			if (soundVolumeFactor < 0f || soundVolumeFactor > 1f)
			{
				yield return "RM_ShadeHazeExtension soundVolumeFactor must be within 0..1.";
			}
		}
	}

	public static class RM_ShadeHaze
	{
		/// <summary>Combined factors, multiplicative.</summary>
		public static float Combine(IList<float> factors)
		{
			float f = 1f;
			if (factors != null)
			{
				for (int i = 0; i < factors.Count; i++)
				{
					f *= factors[i];
				}
			}
			return f;
		}

		private static readonly List<float> scratch = new List<float>();

		/// <summary>Shadow length factor in force on this map (1 when none or the setting is off).</summary>
		public static float ShadowLengthFactor(Map map)
		{
			return Read(map, true);
		}

		/// <summary>Camera heat-bed volume factor in force on this map (1 when none or off).</summary>
		public static float SoundVolumeFactor(Map map)
		{
			return Read(map, false);
		}

		private static float Read(Map map, bool length)
		{
			if (map == null || !RM_CreatureBehaviorsSettings.smokeHazeEffectsEnabled)
			{
				return 1f;
			}
			List<GameCondition> conds = map.gameConditionManager.ActiveConditions;
			scratch.Clear();
			for (int i = 0; i < conds.Count; i++)
			{
				RM_ShadeHazeExtension ext = conds[i].def.GetModExtension<RM_ShadeHazeExtension>();
				if (ext != null)
				{
					scratch.Add(length ? ext.shadowLengthFactor : ext.soundVolumeFactor);
				}
			}
			return Combine(scratch);
		}
	}
}
