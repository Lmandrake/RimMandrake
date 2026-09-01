using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompExtremeXenophobia : ThingComp
{
	public List<Pawn> pawnList = new List<Pawn>();

	public Pawn thisPawn;

	public CompProperties_ExtremeXenophobia Props => (CompProperties_ExtremeXenophobia)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.berserkRate, delta) || ((Thing)base.parent).Map == null)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		foreach (Pawn freeColonist in ((Thing)base.parent).Map.mapPawns.FreeColonists)
		{
			if (freeColonist != null && freeColonist.IsColonist && !Props.AcceptedDefnames.Contains(((Def)((Thing)freeColonist).def).defName))
			{
				val.mindState.mentalStateHandler.TryStartMentalState(DefDatabase<MentalStateDef>.GetNamed("VEF_XenophobicRage", true), (string)null, true, false, false, (Pawn)null, false, false, false);
			}
		}
	}
}
