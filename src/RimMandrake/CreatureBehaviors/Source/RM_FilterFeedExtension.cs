using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_WHALE_FILTERFEED_1. Attach to a race ThingDef to let it FEED
	/// FROM TERRAIN — stand on one of feedTerrainDefNames and strain a meal out
	/// of the ground itself, with no food Thing involved at any point.
	///
	/// Why this exists at all: design/Jawa/worldbuilding/biomes/desert.md §10's
	/// own implementation table says "filter-feeding sand | C# — FoodTypeFlags
	/// is a closed enum with no terrain member." There is no terrain-grazing
	/// member to add and no vanilla comp that grazes ground rather than a
	/// Plant, so a race that eats sand cannot be expressed in XML at any tier.
	/// RM_JobGiver_FilterFeedTerrain + RM_JobDriver_FilterFeedTerrain are that
	/// route: an ordinary custom Job whose driver tops up Need_Food directly,
	/// which is FoodTypeFlags-independent by construction — the race keeps
	/// whatever foodType it declares for every OTHER purpose (taming, hauled
	/// feed, kibble, a player-built trough), and simply gains a second way to
	/// eat that the enum was never asked about.
	///
	/// RM tier: this names no terrain, no species and no biome. The desert's
	/// shade whale supplies "Sand"/"SoftSand" from its own def; a future ocean
	/// or marsh filter-feeder supplies its own list and reuses every line here.
	/// Any pawn whose race lacks this extension is rejected by the JobGiver on
	/// its first statement, so the shared Animal_PreMain insert stays free.
	/// </summary>
	public class RM_FilterFeedExtension : DefModExtension
	{
		/// <summary>
		/// TerrainDef defNames this race can strain a meal out of. Empty means
		/// the behaviour never fires — an unfilled extension is inert, never a
		/// race that feeds off every floor in the game.
		/// </summary>
		public List<string> feedTerrainDefNames = new List<string>();

		/// <summary>
		/// Start looking for feeding ground once the food need falls below this
		/// fraction of full. Deliberately well above vanilla's hungry threshold:
		/// a filter-feeder grazes continuously as it travels rather than making
		/// a trip once it is starving.
		/// </summary>
		public float beginBelowFoodPercent = 0.7f;

		/// <summary>
		/// Fraction of the pawn's FULL food need restored by one completed bout.
		/// A fraction rather than an absolute nutrition figure because Need_Food's
		/// MaxLevel scales with body size, and this kit has to read the same on a
		/// bodySize-16 megafauna and on anything smaller that reuses it later.
		/// </summary>
		public float foodPercentPerBout = 0.12f;

		/// <summary>Ticks spent straining one bout out of the ground.</summary>
		public int boutDurationTicks = 900;

		/// <summary>How far the pawn will walk to reach feeding ground.</summary>
		public float searchRadius = 18f;

		/// <summary>
		/// Optional filth left behind by a completed bout — the churned, sifted
		/// ground a filter-feeder leaves in its wake. Null leaves nothing.
		/// </summary>
		public ThingDef leavingsFilthDef;

		/// <summary>How many filth things a completed bout leaves, if any def is set.</summary>
		public int leavingsFilthCount = 1;
	}
}
