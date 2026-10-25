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
	}

	/// <summary>What one newly cut depth leaves on the lip.</summary>
	public enum RM_CutSpoil
	{
		None,
		Gravel,
		Chunk,
	}

	public static class RM_GroundClassMath
	{
		/// <summary>Card ruling 2026-10-25: salt crusts, packed snow and asphalt dig as RUBBLE (rock-speed digging, gravel
		/// only, never chunks). Gravel ground and cooled lava are broken rock already. An explicit list, never a name
		/// pattern: "contains Snow" would take loose snow too.</summary>
		public static readonly HashSet<string> RubbleTerrains = new HashSet<string>
		{
			"RUT_Jawa_SaltCrust", "RM_MiasmaSaltCrust", "VEE_Salt",
			"WastelandAsphalt", "RM_WastelandBrokenAsphalt", "BrokenAsphalt",
			"RM_PackedSnow", "VEE_DenseSnow_Rough",
			"Gravel", "CooledLava",
		};

		/// <summary>Owner 2026-10-25: "you can't dig in sand or mud (just slides back in)". Name words for modded mud,
		/// slime, quicksand and marsh that do not say so in their categoryType.</summary>
		private static readonly string[] SlumpWords = { "Mud", "Slime", "Quicksand", "Marsh" };

		/// <summary>Precedence: water, then the card's rubble list (it outranks a layerable flag and a Sand category: salt
		/// crusts are categoryType Sand), then player floors, then everything that slides back in, then rock, then soil.</summary>
		public static RM_GroundClass Classify(string defName, bool isWater, bool layerable, bool isRock, bool isSoil,
			bool diggable, string categoryType)
		{
			if (isWater)
			{
				return RM_GroundClass.Water;
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
