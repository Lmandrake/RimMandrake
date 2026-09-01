using System.Linq;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompEnrageOtherPawns : ThingComp
{
	public CompProperties_EnrageOtherPawns Props => (CompProperties_EnrageOtherPawns)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.checkingInterval, delta) || ((Thing)base.parent).Map == null)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val.mindState.mentalStateHandler.CurStateDef != MentalStateDefOf.Manhunter && val.mindState.mentalStateHandler.CurStateDef != MentalStateDefOf.ManhunterPermanent)
		{
			return;
		}
		foreach (Pawn item in ((Thing)base.parent).Map.mapPawns.AllPawnsSpawned.Where((Pawn x) => Props.pawnkinddefsToAffect.Contains(x.kindDef)).ToList())
		{
			item.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, (string)null, false, false, false, (Pawn)null, false, false, false);
		}
	}
}
