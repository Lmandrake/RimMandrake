using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
	// CAVERNS_PARITY_BUILD_1 — the "cave flora" Mod Settings toggle, made real,
	// and (same item, second pass) the Deep's own initial planting.
	//
	// Toggle ON (shipped default): PLANTS. The vanilla Plants GenStep (order 900)
	// never reads RUT_LanternDeeps.wildPlants on a Deep — under a natural roof it
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
	// and RUT_LanternDeepGenerator.xml already lists it after Plants.
	public class GenStep_DeepFloraGate : GenStep
	{
		public override int SeedPart => 1237834912;

		private static readonly string[] OwnedFloraDefNames =
		{
			"RUT_DeepMycelium",
			"RUT_Gleamtip",
			"RUT_Fungusfern",
			"RUT_CrystaltipBrambles",
			"RUT_YumBulbs",
			"RUT_DeepDulcisPlant",
			"RUT_Crystalcap",
			"RUT_DeepGreyLady",
			"RUT_DeepArpeau",
			"RUT_LuminousSpout",
			"RUT_DeepNuitae",
			"RUT_Lanternstone_Sowable",
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
