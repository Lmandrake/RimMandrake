using RimWorld;
using Verse;

namespace FactionLoadout;

public class PawnGenOptionEdit : IExposable
{
	public string KindDefName = "";

	public float SelectionWeight = 1f;

	public PawnKindDef KindDef => DefDatabase<PawnKindDef>.GetNamedSilentFail(KindDefName);

	public static PawnGenOptionEdit FromOption(PawnGenOption opt)
	{
		return new PawnGenOptionEdit
		{
			KindDefName = (((Def)(opt.kind?)).defName ?? ""),
			SelectionWeight = opt.selectionWeight
		};
	}

	public PawnGenOption ToPawnGenOption()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Expected O, but got Unknown
		return new PawnGenOption
		{
			kind = KindDef,
			selectionWeight = SelectionWeight
		};
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref KindDefName, "kind", "", false);
		Scribe_Values.Look<float>(ref SelectionWeight, "weight", 1f, false);
	}
}
