using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_WHALE_FILTERFEED_1. Properties for RM_CompDungSeeder —
	/// desert.md §4c: "They leave massive dung at shade patches, and that dung
	/// immediately seeds young plants and young creatures around it. So the
	/// megafauna are the biome's circulatory system... fertilising every
	/// harbour they stop at."
	///
	/// RM tier: names no species, no plant and no biome. A def that carries this
	/// comp either supplies its own seedPlants/seedWildlife lists or leaves them
	/// empty, in which case the comp falls back to whatever the MAP'S OWN BIOME
	/// already spawns wild — which is the shape the fiction actually wants, since
	/// a vector carries what grows where it stops, not a fixed cargo.
	/// </summary>
	public class RM_CompProperties_DungSeeder : CompProperties
	{
		/// <summary>Ticks between dung events. 15000~30000 is roughly 6–12 in-game hours.</summary>
		public IntRange intervalTicksRange = new IntRange(15000, 30000);

		/// <summary>
		/// Minimum RM_MapComponent_ShadeGrid.ShadeAt score at the pawn's own cell
		/// for a dung event to seed anything. Below it the dung still drops (a
		/// body in the open still voids) but nothing takes — which IS the "at
		/// shade patches" half of the ruling, expressed as a mechanic rather than
		/// as flavour text over a flat chance.
		/// </summary>
		public float minShadeToSeed = 0.35f;

		/// <summary>Filth left by a dung event, in shade or out of it. Null leaves nothing.</summary>
		public ThingDef dungFilthDef;

		public int dungFilthCount = 3;

		/// <summary>Radius the dung fertilises and seeds within.</summary>
		public float seedRadius = 5.9f;

		/// <summary>Growth added to each existing plant in radius by one shaded dung event.</summary>
		public float growthBoost = 0.25f;

		/// <summary>Cap on plants boosted per event, so a big radius stays cheap.</summary>
		public int maxPlantsBoosted = 12;

		/// <summary>
		/// Plants this dung seeds. Empty falls back to the map biome's own wild
		/// plants, weighted by their biome commonality.
		/// </summary>
		public List<ThingDef> seedPlants = new List<ThingDef>();

		public IntRange seedPlantCount = new IntRange(1, 3);

		/// <summary>Growth a freshly seeded plant starts at — "young plants".</summary>
		public float seedPlantGrowth = 0.05f;

		/// <summary>Chance per shaded dung event that a young creature also arrives.</summary>
		public float wildlifeSpawnChance = 0.15f;

		/// <summary>
		/// Creatures this dung seeds. Empty falls back to the map biome's own
		/// wild animals under maxWildlifeBodySize — the passengers and parasites
		/// a vector picks up from wherever it has been.
		/// </summary>
		public List<PawnKindDef> seedWildlife = new List<PawnKindDef>();

		/// <summary>
		/// Body-size ceiling for the biome fallback. Keeps a dung pile seeding
		/// small life rather than delivering another megafauna.
		/// </summary>
		public float maxWildlifeBodySize = 0.6f;

		/// <summary>Biological age, in years, a seeded creature is generated at — "young creatures".</summary>
		public float seededWildlifeAgeYears = 0.4f;

		public RM_CompProperties_DungSeeder()
		{
			compClass = typeof(RM_CompDungSeeder);
		}
	}
}
