using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 4. The HARVEST verb (spec §3): "Sustainable
	/// netting below the replacement rate; per-species catch jobs." Targets
	/// any live, stockable pool-fauna pawn ALREADY STANDING IN a player's own
	/// <see cref="RM_Zone_PoolPen"/> — the opposite condition from
	/// <see cref="RM_WorkGiver_NetPoolBreeder"/>, which only wants pawns
	/// OUTSIDE a pen. RM_Vizhik is excluded (§2c: never caught in the pool,
	/// only traveling — RECAPTURE's job, which reuses NET); RM_Vhorrin is
	/// excluded (its own set-piece, <see cref="RM_WorkGiver_CullVhorrin"/>).
	///
	/// Deliberately unthrottled below what NeedsFeed/population already
	/// price in: the spec's OVERDRAW verb ("fish above replacement and the
	/// stock crashes") is a *player choice with a real consequence*, not a
	/// blocked action — <see cref="RM_MapComponent_PoolStock"/>'s own Pulse
	/// already reclassifies a stripped pen as Thin/Silent and, if crowded or
	/// crashed, can grow a vhorrin. Nothing here needs to re-enforce that.
	/// </summary>
	public class RM_WorkGiver_HarvestPoolPen : WorkGiver_Scanner
	{
		/// <summary>Species harvestable by a plain catch-and-butcher job.
		/// Murrin/loomu/huldu/ivvol carry no handling risk (§2's own table);
		/// skarrin/karrek do, same weights as netting them wild.</summary>
		public static readonly Dictionary<string, float> InjuryChancePerSpecies = new Dictionary<string, float>
		{
			{ "RM_Skarrin", 0.12f },
			{ "RM_Karrek", 0.15f },
		};

		private static readonly HashSet<string> HarvestableDefNames = new HashSet<string>
		{
			"RM_Murrin", "RM_Skarrin", "RM_Karrek", "RM_Loomu", "RM_Huldu", "RM_Ivvol",
		};

		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.Pawn);

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RM_WeepingStonesSettings.stockedPoolsEnabled;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			return IsHarvestable(pawn, t, forced);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!IsHarvestable(pawn, t, forced))
			{
				return null;
			}
			return JobMaker.MakeJob(RM_PoolStockDefOf.RM_HarvestPoolPen, t);
		}

		private static bool IsHarvestable(Pawn pawn, Thing t, bool forced)
		{
			Pawn stock = t as Pawn;
			if (stock == null || stock == pawn || stock.Dead || !stock.Spawned)
			{
				return false;
			}
			if (stock.def == null || !HarvestableDefNames.Contains(stock.def.defName))
			{
				return false;
			}
			if (!(stock.Map.zoneManager.ZoneAt(stock.Position) is RM_Zone_PoolPen))
			{
				return false; // only a designated pen's own stock -- a wild one is NET's job, not HARVEST's
			}
			if (!pawn.CanReserve(stock, 1, -1, null, forced))
			{
				return false;
			}
			return pawn.CanReach(stock, PathEndMode.Touch, Danger.Some);
		}
	}
}
