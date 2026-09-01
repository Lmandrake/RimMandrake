using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompAbilityEffect_ControlledBlinking : CompAbilityEffect
{
	public CompProperties_ControlledBlinking Props => (CompProperties_ControlledBlinking)(object)((AbilityComp)this).props;

	public override bool Valid(LocalTargetInfo target, bool throwMessages = false)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		if (!GenGrid.InBounds(((LocalTargetInfo)(ref target)).Cell, ((Thing)((AbilityComp)this).parent.pawn).Map))
		{
			return false;
		}
		if (GenGrid.Impassable(((LocalTargetInfo)(ref target)).Cell, ((Thing)((AbilityComp)this).parent.pawn).Map))
		{
			return false;
		}
		return true;
	}

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		if (Props.warpEffect)
		{
			FleckMaker.Static(((Thing)((AbilityComp)this).parent.pawn).Position, ((Thing)((AbilityComp)this).parent.pawn).Map, FleckDefOf.PsycastAreaEffect, 10f);
		}
		((AbilityComp)this).parent.pawn.pather.StopDead();
		((Thing)((AbilityComp)this).parent.pawn).Position = ((LocalTargetInfo)(ref target)).Cell;
		((AbilityComp)this).parent.pawn.pather.ResetToCurrentPosition();
	}
}
