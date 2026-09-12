using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// RUST_CATHEDRAL_MECHANICS_1 §6 (the roaches). Attach to a race ThingDef
	/// to make it forage data-listed "cleanable" items (by defName — e.g. a
	/// wastepack-style toxic-waste item) and/or filth, consuming the target on
	/// a timer. Generalizes the pattern measured in the donor mod
	/// LingLuo.Cockroach's ThinkNode_EatWastepack (dnfile metadata
	/// enumeration, RUST_CATHEDRAL_MECHANICS_1 kit spec §6) in two ways the
	/// donor did not: (a) no player-faction gate — this fires for ANY pawn
	/// whose race carries the extension, wild included, because
	/// RM_ThinkNode_EatCleanable is inserted on the shared
	/// Animal_PreMain insertTag alongside every other JobGiver in this
	/// assembly (see RM_ThinkTree_VerminBehaviors.xml); (b) filth is a
	/// first-class target alongside named items, not just wastepacks.
	///
	/// RM tier: nothing here knows what species, biome or campaign uses it —
	/// the target list and filth flag are entirely data-driven, same
	/// contract as RM_GnawTargetExtension in this same file group.
	/// </summary>
	public class RM_EatCleanableExtension : DefModExtension
	{
		/// <summary>defNames of items this pawn forages and consumes (e.g. "Wastepack").</summary>
		public List<string> cleanableThingDefNames;

		/// <summary>If true, ordinary map Filth is also a valid target.</summary>
		public bool eatsFilth = true;

		public float searchRadius = 25f;

		public float nutritionPerMeal = 0.2f;

		/// <summary>
		/// Ticks spent consuming a found target once reached. INVENTED
		/// parameter per the kit spec: "one filth/wastepack per 2h active" —
		/// 2 in-game hours (2 * 2500 ticks/hour) is the consumption toil
		/// itself, not an additional cooldown on top of it.
		/// </summary>
		public int eatDurationTicks = 5000;

		/// <summary>Chance per think-tree tick this JobGiver bothers looking for a target at all, keeping it from dominating a wild pawn's job selection.</summary>
		public float seekChance = 0.02f;
	}
}
