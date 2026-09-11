using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Attach to a race ThingDef to make RM_JobGiver_SeekMarkedTerrain
	/// draw it toward data-tagged terrain — the mynock's "drift to the hull"
	/// boarding behavior, but generic: any future creature that should be drawn
	/// toward a kind of ground (not a kind of building — RM_GnawTargetExtension
	/// covers buildings) reuses this by listing its own terrain defNames instead
	/// of setting seekSubstructure.
	///
	/// Once the pawn stands on a matching cell, nothing further is needed here —
	/// vanilla ThingDef.bringAlongOnGravship (defaults true) is what actually
	/// carries a pawn along at gravship launch (RimSage-verified,
	/// Gravship.ShouldBringOnGravship), so "boarding" costs zero additional C#
	/// once the seek behavior gets the pawn onto the ship.
	/// </summary>
	public class RM_SeekTargetExtension : DefModExtension
	{
		/// <summary>Seek any substructure-foundation cell (TerrainDef.IsSubstructure) — the gravship-hull case.</summary>
		public bool seekSubstructure;

		/// <summary>Seek any cell whose terrain defName is in this list, in addition to/instead of substructure.</summary>
		public List<string> seekTerrainDefNames;

		public float searchRadius = 40f;

		/// <summary>0..1 chance per job-request check that the pawn bothers to seek at all — keeps a lone vermin from beelining constantly.</summary>
		public float seekChancePerCheck = 0.05f;
	}
}
