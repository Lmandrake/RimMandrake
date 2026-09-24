using System.Collections.Generic;
using Verse;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3. The join between a live pool-fauna
	/// species and its carryable "breeding stock" item (spec §3 STOCK:
	/// "carry them home in a wet skin"). Convention-based rather than a
	/// DefModExtension — the breeding-stock ThingDef's defName is always
	/// the species PawnKindDef's defName plus the fixed suffix below, so
	/// there is nothing to keep in sync between two def files and no new
	/// DefModExtension class to maintain for a single string field.
	/// </summary>
	public static class RM_PoolBreederUtility
	{
		private const string BreedingStockSuffix = "BreedingStock";

		/// <summary>The seven species a player can NET and STOCK.
		/// RM_Vhorrin is deliberately absent — spec §2d: it is the
		/// mismanagement state made flesh, produced only by
		/// <see cref="RM_MapComponent_PoolStock"/> at cull/emergence time,
		/// never a breeder a colonist carries home.</summary>
		public static readonly HashSet<string> StockableSpeciesDefNames = new HashSet<string>
		{
			"RM_Murrin", "RM_Skarrin", "RM_Karrek", "RM_Vizhik",
			"RM_Loomu", "RM_Huldu", "RM_Ivvol",
		};

		public static string BreedingStockDefNameFor(string pawnKindDefName)
		{
			return pawnKindDefName + BreedingStockSuffix;
		}

		/// <summary>Reverse lookup used by the STOCK job: given a carried
		/// breeding-stock ThingDef, recover the species it releases.
		/// Returns false for anything that isn't one of ours (defName
		/// doesn't end in the suffix, or the recovered species isn't in
		/// the stockable set) rather than guessing.</summary>
		public static bool TryGetPawnKindDefName(ThingDef breedingStockDef, out string pawnKindDefName)
		{
			string defName = breedingStockDef?.defName;
			if (defName != null && defName.EndsWith(BreedingStockSuffix))
			{
				string candidate = defName.Substring(0, defName.Length - BreedingStockSuffix.Length);
				if (StockableSpeciesDefNames.Contains(candidate))
				{
					pawnKindDefName = candidate;
					return true;
				}
			}
			pawnKindDefName = null;
			return false;
		}
	}
}
