using System.Collections.Generic;
using Verse;

namespace RimMandrake.LanternDeeps
{
	// CAVERNS_PARITY_BUILD_1 — the "cave flora" Mod Settings toggle, made real,
	// and (same item, second pass) the Deep's own initial planting.
	//
	// Toggle ON (shipped default): PLANTS. The vanilla Plants GenStep (order 900)
	// never reads RM_LanternDeeps.wildPlants on a Deep — under a natural roof it
	// draws only from the planet-wide cavePlant list (see DeepFloraPlanter's
	// header for the measured source) — so at order 950 this step walks the map
	// and seeds the biome's own flora at vanilla's desired density. Anything
	// vanilla already put down (Glowstool and friends, which ARE cavePlants) is
	// left in place and counts toward the cap.
	//
	// Toggle OFF: culls. There is no vanilla hook to suppress Plants per map, so
	// the off state removes plants whose def this mod owns — an owned-defs check
	// rather than "destroy every Plant", so a future mod that legitimately seeds
	// something else into a Deep is not quietly wiped by our settings toggle.
	//
	// Order 950 rather than a sibling step: it is the one place the toggle is
	// already consulted at gen time, both branches are "what grows in a Deep",
	// and RM_LanternDeepGenerator.xml already lists it after Plants.
	public class GenStep_DeepFloraGate : GenStep
	{
		// Distinct from GenStep_ScatterLanternstone (1237834911) and
		// GenStep_LanternstoneRock (1237834912) — a duplicate SeedPart here
		// meant this step and GenStep_LanternstoneRock shared the identical
		// RNG stream at Generate() time, defeating the per-GenStep
		// decorrelation SeedPart exists for (both steps derive their Rand
		// state from map seed + SeedPart, so an identical SeedPart gives them
		// an identical starting stream).
		public override int SeedPart => 1237834913;

		private static readonly string[] OwnedFloraDefNames =
		{
			"RM_DeepMycelium",
			"RM_ZivvitTaper",
			"RM_QuorrFern",
			"RM_OsskBramble",
			"RM_BrellikBulb",
			"RM_TwitchingPuffer",
			"RM_ThrakkCap",
			"RM_PrennaLace",
			"RM_VellokReed",
			"RM_KuvraSpout",
			"RM_NurrikGill",
			"RM_Lanternstone_Sowable",
		};

		private static HashSet<ThingDef> ownedFlora;

		private static HashSet<ThingDef> OwnedFlora
		{
			get
			{
				if (ownedFlora == null)
				{
					ownedFlora = new HashSet<ThingDef>();
					foreach (string name in OwnedFloraDefNames)
					{
						ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
						if (def != null)
						{
							ownedFlora.Add(def);
						}
					}
				}
				return ownedFlora;
			}
		}

		public override void Generate(Map map, GenStepParams parms)
		{
			if (LanternDeepsSettings.deepFloraEnabled)
			{
				if (DeepFloraPlanter.IsDeep(map))
				{
					DeepFloraPlanter.PlantInitial(map);
				}
				return;
			}

			List<Thing> doomed = new List<Thing>();
			foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
			{
				if (OwnedFlora.Contains(t.def))
				{
					doomed.Add(t);
				}
			}
			foreach (Thing t in doomed)
			{
				t.Destroy(DestroyMode.Vanish);
			}
		}
	}
}
