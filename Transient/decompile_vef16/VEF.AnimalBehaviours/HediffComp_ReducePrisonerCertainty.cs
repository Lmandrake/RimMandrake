using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_ReducePrisonerCertainty : HediffComp
{
	public HediffCompProperties_ReducePrisonerCertainty Props => (HediffCompProperties_ReducePrisonerCertainty)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.checkingInterval, delta) || !((HediffComp)this).Pawn.RaceProps.Humanlike || ((HediffComp)this).Pawn.Ideo == null)
		{
			return;
		}
		Faction ofPlayer = Current.Game.World.factionManager.OfPlayer;
		object obj;
		if (ofPlayer == null)
		{
			obj = null;
		}
		else
		{
			FactionIdeosTracker ideos = ofPlayer.ideos;
			obj = ((ideos != null) ? ideos.PrimaryIdeo : null);
		}
		if (obj == null)
		{
			return;
		}
		if (((HediffComp)this).Pawn.Ideo != Current.Game.World.factionManager.OfPlayer.ideos.PrimaryIdeo)
		{
			((HediffComp)this).Pawn.ideo.Reassure((0f - Props.certaintyPerTick) * (float)Props.checkingInterval / 100f);
			if (((HediffComp)this).Pawn.ideo.Certainty <= 0f)
			{
				((HediffComp)this).Pawn.ideo.SetIdeo(Current.Game.World.factionManager.OfPlayer.ideos.PrimaryIdeo);
			}
		}
		else
		{
			((HediffComp)this).Pawn.ideo.Reassure(Props.certaintyPerTick * (float)Props.checkingInterval / 100f);
		}
	}
}
