using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// ROT_HEALTH_SHARING_1. Attach to a race ThingDef to mark it as a "kin
	/// group" for two independent mechanisms that both read this one
	/// extension: RM_CompWoundLink (a fresh injury is partly mirrored onto
	/// nearby same-tag pawns) and RM_HediffComp_KinMending (nearby same-tag
	/// kin boost this pawn's own natural healing). One extension, one tag,
	/// one radius — a content mod wiring both mechanisms onto a race needs
	/// only this plus a `<comps>` entry for each, never two separate tag
	/// schemes to keep in sync.
	///
	/// Deliberately generic (no Rot/species name anywhere in this file):
	/// BIOME_FAUNA_ASSIGNMENT_SITTING_1 assigns this onto specific RotSporeKit
	/// variant defs by XML later — not this pass's job (item 3 of the spec).
	/// </summary>
	public class RM_WoundLinkExtension : DefModExtension
	{
		/// <summary>Kin-group identity. Pawns sharing the same tag (any
		/// string; races with different tags never interact) are "same-tag
		/// kin" for both RM_CompWoundLink and RM_HediffComp_KinMending.
		/// Left blank = this pawn never finds kin (both mechanisms need a
		/// matching non-empty tag on both sides), so a def author must set
		/// this for either mechanism to do anything.</summary>
		public string tag;

		/// <summary>Cells around a pawn searched for same-tag kin, both for
		/// mirroring a fresh wound (RM_CompWoundLink) and for counting kin
		/// toward RM_HediffComp_KinMending's healing boost. INVENTED: 12 —
		/// spec's own stated value ("tag, radius 12, share 60%, gate ≥8
		/// severity").</summary>
		public float radius = 12f;

		/// <summary>Fraction of a fresh injury's severity mirrored onto each
		/// same-tag kin in radius, and subtracted once from the original
		/// victim. INVENTED: 0.6 — spec's own stated value.</summary>
		public float shareFraction = 0.6f;

		/// <summary>Minimum fresh-injury severity before RM_CompWoundLink
		/// does anything — a scraped-knuckle graze never triggers a mirror,
		/// only a real wound does. INVENTED: 8 — spec's own stated value.</summary>
		public float severityGate = 8f;

		/// <summary>Same-tag kin required within radius before
		/// RM_HediffComp_KinMending's healing boost turns on. INVENTED: 2 —
		/// spec's own stated value ("≥2 same-tag kin").</summary>
		public int kinMendingMinKin = 2;
	}
}
