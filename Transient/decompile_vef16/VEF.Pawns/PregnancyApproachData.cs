using System.Collections.Generic;
using Verse;

namespace VEF.Pawns;

public class PregnancyApproachData : IExposable
{
	public Dictionary<Pawn, PregnancyApproachDef> partners = new Dictionary<Pawn, PregnancyApproachDef>();

	private List<Pawn> pawnKeys;

	private List<PregnancyApproachDef> defValues;

	public void ExposeData()
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Invalid comparison between Unknown and I4
		Scribe_Collections.Look<Pawn, PregnancyApproachDef>(ref partners, "partners", (LookMode)3, (LookMode)4, ref pawnKeys, ref defValues, true, false, false);
		if ((int)Scribe.mode == 4 && partners == null)
		{
			partners = new Dictionary<Pawn, PregnancyApproachDef>();
		}
	}
}
