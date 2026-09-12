using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.RustCathedralHum
{
	// RUST_CATHEDRAL_MECHANICS_1 §3 -- the freeze half of the bolts'
	// dance/freeze display.
	//
	// Structured as a ThinkNode_Conditional subclass wrapping a plain vanilla
	// JobGiver (JobGiver_Idle), which is how vanilla structures every
	// conditional freeze it ships -- ThinkNode_ConditionalLowEnergy wrapping
	// JobGiver_SelfShutdown and ThinkNode_ConditionalDeactivated wrapping
	// JobGiver_Deactivated, both in Defs/Core/ThinkTreeDefs/Mechanoid.xml --
	// rather than a priority branch hidden inside the dance giver. The tree
	// file (Defs/ThinkTreeDefs/RUT_ThinkTree_LivingBolt.xml) is therefore
	// readable as the mechanism: whoever reads it can see that the freeze
	// outranks both the queued figure and the dance.
	//
	// Band direction: see the long note in that same XML file. In short, §1
	// shipped band 0 = calmest and band 4 = worst-and-silent, so the freeze
	// fires at the TOP of the range, not at 0 as the kit spec's pre-§1
	// wording says. The number lives in XML so re-ruling it costs no rebuild.
	//
	// Off a Rust Cathedral map GetBand returns -1 and this is never
	// satisfied, so the bolt falls through to the tree's vanilla wander --
	// the graceful-degradation floor.
	public class RM_ThinkNode_ConditionalAttitudeBand : ThinkNode_Conditional
	{
		// Satisfied when the map's current attitude band is at least this.
		public int freezeAtBandAtLeast = 4;

		// When true (the default) this node also respects the mod options, so
		// turning bolt mechanics off removes the freeze as well as the dance
		// and leaves an ordinary wandering critter.
		public bool respectModSettings = true;

		public override ThinkNode DeepCopy(bool resolve = true)
		{
			RM_ThinkNode_ConditionalAttitudeBand obj = (RM_ThinkNode_ConditionalAttitudeBand)base.DeepCopy(resolve);
			obj.freezeAtBandAtLeast = freezeAtBandAtLeast;
			obj.respectModSettings = respectModSettings;
			return obj;
		}

		protected override bool Satisfied(Pawn pawn)
		{
			if (respectModSettings && !RustCathedralHumSettings.BoltDisplayActive)
			{
				return false;
			}
			Map map = pawn?.Map;
			if (map == null)
			{
				return false;
			}
			int band = RM_MapComponent_BiomeAttitude.GetBand(map);
			if (band < 0)
			{
				// No attitude def governs this biome -- nothing to display.
				return false;
			}
			return band >= freezeAtBandAtLeast;
		}
	}
}
