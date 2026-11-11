using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY / PIT_DIG_FIX_SAND_SLIDES_BACK_IN: what kind of ground a cut goes
	/// through, and what it gives and costs. Verse-free so the selftest pins it.</summary>
	public enum RM_GroundClass
	{
		NotDiggable,
		Soil,
		Rock,
		Rubble,
		Slumps,
		Floor,
		Water,
		/// <summary>ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN (owner card 2026-10-25): "Cutting into packed snow or ice should give
		/// crushed ice ... Ice is definitely diggable." Rock-speed digging; every cut leaves crushed ice.</summary>
		Ice,
	}

	/// <summary>What one newly cut depth leaves on the lip.</summary>
	public enum RM_CutSpoil
	{
		None,
		Gravel,
		Chunk,
		/// <summary>ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN: "acts like gravel on cold maps".</summary>
		CrushedIce,
	}

	public static class RM_GroundClassMath
	{
		/// <summary>Card ruling 2026-10-25: salt crusts and asphalt dig as RUBBLE (packed snow, on the first card, is ICE now:
		/// see <see cref="IceTerrains"/>) (rock-speed digging, gravel
		/// only, never chunks). Gravel ground and cooled lava are broken rock already. An explicit list, never a name
		/// pattern: "contains Snow" would take loose snow too.</summary>
		public static readonly HashSet<string> RubbleTerrains = new HashSet<string>
		{
			"RUT_Jawa_SaltCrust", "RM_MiasmaSaltCrust", "VEE_Salt",
			"WastelandAsphalt", "RM_WastelandBrokenAsphalt", "BrokenAsphalt",
			"Gravel", "CooledLava",
		};

		/// <summary>ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN (owner card 2026-10-25, superseding the rubble card for packed snow):
		/// packed snow and ice dig as ICE. An explicit list again: loose snow is not on it.</summary>
		public static readonly HashSet<string> IceTerrains = new HashSet<string>
		{
			"Ice", "RM_PackedIce", "RM_ChillIceBedrock",
			"RM_PackedSnow", "VEE_DenseSnow_Rough",
		};

		/// <summary>Owner 2026-10-25: "you can't dig in sand or mud (just slides back in)". Name words for modded mud,
		/// slime, quicksand and marsh that do not say so in their categoryType.</summary>
		private static readonly string[] SlumpWords = { "Mud", "Slime", "Quicksand", "Marsh" };

		/// <summary>Precedence: water, then the ice list, then the card's rubble list (it outranks a layerable flag and a Sand category: salt
		/// crusts are categoryType Sand), then player floors, then everything that slides back in, then rock, then soil.</summary>
		public static RM_GroundClass Classify(string defName, bool isWater, bool layerable, bool isRock, bool isSoil,
			bool diggable, string categoryType)
		{
			if (isWater)
			{
				return RM_GroundClass.Water;
			}
			if (defName != null && IceTerrains.Contains(defName))
			{
				return RM_GroundClass.Ice;
			}
			if (defName != null && RubbleTerrains.Contains(defName))
			{
				return RM_GroundClass.Rubble;
			}
			if (layerable)
			{
				return RM_GroundClass.Floor;
			}
			if (Slumps(defName, categoryType))
			{
				return RM_GroundClass.Slumps;
			}
			if (isRock || categoryType == "Stone")
			{
				return RM_GroundClass.Rock;
			}
			if (isSoil || diggable)
			{
				return RM_GroundClass.Soil;
			}
			return RM_GroundClass.NotDiggable;
		}

		public static bool Slumps(string defName, string categoryType)
		{
			if (categoryType == "Sand")
			{
				return true;
			}
			if (defName == null)
			{
				return false;
			}
			if (defName == "SoftSand" || defName == "MarshyTerrain")
			{
				return true;
			}
			foreach (string w in SlumpWords)
			{
				if (defName.IndexOf(w, System.StringComparison.Ordinal) >= 0)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Owner: rock ground "produces a chunk or gravel"; dirt "makes no chunks"; rubble is gravel only.</summary>
		public static RM_CutSpoil CutYield(RM_GroundClass cls, bool chunkRolled)
		{
			switch (cls)
			{
				case RM_GroundClass.Rock:
					return chunkRolled ? RM_CutSpoil.Chunk : RM_CutSpoil.Gravel;
				case RM_GroundClass.Rubble:
					return RM_CutSpoil.Gravel;
				case RM_GroundClass.Ice:
					return RM_CutSpoil.CrushedIce;
				default:
					return RM_CutSpoil.None;
			}
		}

		/// <summary>Owner: "it takes 1 gravel or 2 chunks to put it all back in again". Credit per notch filled.</summary>
		public const int CreditPerNotch = 2;

		public static int CreditOf(bool gravel)
		{
			return gravel ? 2 : 1;
		}

		/// <summary>Credit one unit of fill material pays, by kind (Codex review 2026-10-25: crushed ice must not fall through to
		/// the chunk rate). Gravel and crushed ice fund a notch each; a chunk half of one; anything else nothing.</summary>
		public static int CreditOf(RM_CutSpoil kind)
		{
			switch (kind)
			{
				case RM_CutSpoil.Gravel:
				case RM_CutSpoil.CrushedIce:
					return CreditPerNotch;
				case RM_CutSpoil.Chunk:
					return 1;
				default:
					return 0;
			}
		}

		/// <summary>ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES (owner by card 2026-10-25, "Match what was dug (1x)": crushed ice
		/// melts to the water the cut removed, not a 1x1 tank): the water one crushed ice melts to, in dL: one cut = one notch
		/// (0.5 m of one square, 1,000 L). The same number for melting where it lies and for the melter.</summary>
		public const int CrushedIceUnits = RM_Volume.UnitsPerLevel;

		/// <summary>The water a stack of <paramref name="count"/> crushed ice melts to (dL; never overflows).</summary>
		public static long MeltUnits(int count)
		{
			return count <= 0 ? 0L : (long)count * CrushedIceUnits;
		}

		/// <summary>ICE_MELT_TAME_STACK_FLOOD (owner by card 2026-10-25, "Melt one pile at a time"; owner: "it lowers the
		/// temperature of the room substantially"): the default cooling of one melting crushed ice, in vanilla heat per second
		/// (the unit of a cooler's CompTempControl energyPerSecond; a vanilla cooler is 21). One melting pile cools its room as
		/// hard as a vanilla cooler running flat out.</summary>
		public const float DefaultMeltCoolingPerSecond = 21f;

		public const float MinMeltCoolingPerSecond = 0f;

		public const float MaxMeltCoolingPerSecond = 100f;

		/// <summary>The setting as used: NaN or out of range is held to the range (NaN = the default).</summary>
		public static float ClampMeltCooling(float perSecond)
		{
			if (float.IsNaN(perSecond))
			{
				return DefaultMeltCoolingPerSecond;
			}
			return perSecond < MinMeltCoolingPerSecond ? MinMeltCoolingPerSecond : (perSecond > MaxMeltCoolingPerSecond ? MaxMeltCoolingPerSecond : perSecond);
		}

		/// <summary>The heat one melting pile pushes into its room per check of <paramref name="intervalTicks"/> ticks (a rare
		/// tick is 250): negative (it cools), zero when the setting is 0. 60 ticks are one second.</summary>
		public static float MeltHeatPerInterval(float perSecond, int intervalTicks)
		{
			return -ClampMeltCooling(perSecond) * System.Math.Max(0, intervalTicks) / 60f;
		}

		/// <summary>One pile at a time: after <paramref name="warmTicks"/> above 0 C (a pile melts after
		/// <paramref name="ticksPerPile"/>), how many crushed ice of a <paramref name="stackCount"/> stack melt now: at most one,
		/// never more than the stack.</summary>
		public static int PilesMeltingNow(int warmTicks, int ticksPerPile, int stackCount)
		{
			return stackCount > 0 && warmTicks >= System.Math.Max(1, ticksPerPile) ? 1 : 0;
		}

		/// <summary>Credit still owed before a notch can be filled.</summary>
		public static int CreditShort(int credit)
		{
			return credit >= CreditPerNotch ? 0 : CreditPerNotch - credit;
		}

		/// <summary>Credit left after a notch is filled; a fill that changed nothing spends nothing.</summary>
		public static int CreditAfterFill(int credit, bool depthChanged)
		{
			return depthChanged && credit >= CreditPerNotch ? credit - CreditPerNotch : credit;
		}

		/// <summary>Owner: mining rock "should now also produce the same material as the ground digging when it fails to
		/// produce a chunk". Counted as stack totals of the chunk def before and after the vanilla yield.</summary>
		public static bool MiningGivesGravel(int chunksBefore, int chunksAfter)
		{
			return chunksAfter <= chunksBefore;
		}
	}
}
