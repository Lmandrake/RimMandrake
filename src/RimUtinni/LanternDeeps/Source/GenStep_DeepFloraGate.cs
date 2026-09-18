using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
	// CAVERNS_PARITY_BUILD_1 — the "cave flora" Mod Settings toggle, made real.
	//
	// The Deeps' flora is grown by the VANILLA Plants GenStep (GenStepDef
	// `Plants`, MEASURED order 900) off BiomeDef.wildPlants. There is no vanilla
	// hook to suppress that per-map and no field on the def that turns it off, so
	// the toggle is implemented as a cull that runs immediately after: order 950,
	// which is after Plants (900) and before Fog.
	//
	// It removes ONLY plants whose def this mod owns. A Deep is a pocket map, so
	// in practice that is everything growing there — but writing it as an
	// owned-defs check rather than "destroy every Plant" means a future mod that
	// legitimately seeds something else into a Deep is not quietly wiped by our
	// settings toggle.
	//
	// Cost when the toggle is ON (the shipped default): one early return.
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
