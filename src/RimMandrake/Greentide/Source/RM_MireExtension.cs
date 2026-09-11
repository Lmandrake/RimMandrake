using System.Collections.Generic;
using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1. Attach to any TerrainDef to make it a
	/// mire hazard: RM_MapComponent_TerrainMire escalates RM_Mired on any
	/// pawn standing there (unless immune), and RM_MapComponent_MudSwallow
	/// buries loose items left on it. Generic and reusable off any hazardous
	/// mud/quicksand terrain in any biome — nothing here names Greentide.
	///
	/// A terrain WITHOUT this extension (e.g. RM_ChurnmudSealed, the buildable
	/// sealant floor) is automatically safe: both map components gate purely
	/// on GetModExtension&lt;RM_MireExtension&gt;() != null. That is the whole
	/// sealant mechanism — no separate "is this cell sealed" registry needed.
	/// </summary>
	public class RM_MireExtension : DefModExtension
	{
		/// <summary>Hediff severity added per mire-check tick while standing on this terrain.</summary>
		public float mireSeverityPerTick = 0.008f;

		/// <summary>Hediff severity removed per mire-check tick once the pawn leaves the terrain.</summary>
		public float mireDecayPerTick = 0.02f;

		/// <summary>0..1 chance per check that a pawn below the "stuck" threshold shakes off some severity unaided.</summary>
		public float selfStruggleChancePerCheck = 0.15f;

		/// <summary>Severity at/above which self-struggle no longer works — a pull-free job is required (RM_WorkGiver_FreeMired).</summary>
		public float stuckThreshold = 0.85f;

		/// <summary>Race defNames immune to the mire (this biome's own native fauna, XML-listed by the content mod).</summary>
		public List<string> immuneThingDefNames;

		/// <summary>Ticks a loose item must sit on this terrain before RM_MapComponent_MudSwallow buries it. No exemption for stockpiled/hauled-to items — owner ruling 2026-09-11.</summary>
		public int swallowTicks = 2500;

		public bool IsImmune(Pawn pawn)
		{
			if (immuneThingDefNames.NullOrEmpty() || pawn?.def == null)
			{
				return false;
			}
			return immuneThingDefNames.Contains(pawn.def.defName);
		}
	}
}
