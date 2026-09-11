using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Attach to a race ThingDef to make it gnaw data-listed
	/// buildings (by defName or by carrying a comp whose C# type name is
	/// listed — e.g. "CompGlower" covers every lamp without a denylist),
	/// and/or strip data-listed floor terrains, feeding on each bite. Both the
	/// bite damage and how often the JobGiver bothers looking for a target
	/// scale with RM_MapComponent_VerminPopulation's pressure value for this
	/// pawn's race — "nuisance unless there are many" (owner ruling,
	/// 2026-09-11) as an actual curve: seekChanceAtLowPressure/AtHighPressure
	/// and biteDamage*(1..meannessDamageMultiplier), not a flat number.
	/// </summary>
	public class RM_GnawTargetExtension : DefModExtension
	{
		public List<string> gnawBuildingDefNames;

		public List<string> gnawCompTypeNames;

		public List<string> gnawFloorTerrainDefNames;

		public float searchRadius = 30f;

		public float biteDamage = 6f;

		/// <summary>Bite damage at full population pressure = biteDamage * this.</summary>
		public float meannessDamageMultiplier = 2f;

		public float nutritionPerBite = 0.04f;

		public int ticksBetweenBites = 240;

		/// <summary>Chance per job-request check to seek a gnaw target when the race's population is at/below its soft cap.</summary>
		public float seekChanceAtLowPressure = 0.01f;

		/// <summary>Chance per job-request check to seek a gnaw target when the race's population is at/above its hard cap.</summary>
		public float seekChanceAtHighPressure = 0.2f;
	}
}
