using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHRUBLAND_GIANT_ENRAGE_1. The engine hook half of "giant with young" —
	/// a bare ticker that gives every pawn of the race a CompTickRare to hang
	/// the proximity check on. It carries NO tuning on purpose: all of that
	/// lives on RM_ParentalEnrageExtension, so a species author edits one data
	/// block (the extension) and adds one line (this comp), with no value
	/// declared in two places to drift apart.
	///
	/// See RM_ParentalEnrageExtension for the whole mechanism.
	/// </summary>
	public class RM_CompProperties_ParentalEnrage : CompProperties
	{
		public RM_CompProperties_ParentalEnrage()
		{
			compClass = typeof(RM_CompParentalEnrage);
		}

		public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
		{
			foreach (string err in base.ConfigErrors(parentDef))
			{
				yield return err;
			}

			// A carrier with no extension would tick forever and do nothing.
			// Say so at load rather than leaving a silently inert mechanic,
			// which is this kit's own recurring failure mode.
			if (parentDef != null && parentDef.GetModExtension<RM_ParentalEnrageExtension>() == null)
			{
				yield return "RM_CompProperties_ParentalEnrage on " + parentDef.defName
				             + " has no RM_ParentalEnrageExtension in modExtensions — the comp "
				             + "would never do anything. Add the extension or drop the comp.";
			}
		}
	}
}
