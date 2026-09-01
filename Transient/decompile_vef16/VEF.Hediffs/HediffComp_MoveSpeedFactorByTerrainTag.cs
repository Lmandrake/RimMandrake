using System.Collections.Generic;
using VEF.Genes;
using Verse;

namespace VEF.Hediffs;

public class HediffComp_MoveSpeedFactorByTerrainTag : HediffComp
{
	public HediffCompProperties_MoveSpeedFactorByTerrainTag Props => (HediffCompProperties_MoveSpeedFactorByTerrainTag)(object)base.props;

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		AddThings();
	}

	public override void CompPostPostRemoved()
	{
		RemoveThings();
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		RemoveThings();
	}

	public override void Notify_PawnKilled()
	{
		RemoveThings();
	}

	public void AddThings()
	{
		if (((Hediff)base.parent).pawn != null && !GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(Props.moveSpeedFactorByTerrainTag))
		{
			StaticCollectionsClass.AddMoveSpeedFactorByTerrainTag((Thing)(object)((Hediff)base.parent).pawn, this, Props.moveSpeedFactorByTerrainTag);
		}
	}

	public void RemoveThings()
	{
		if (((Hediff)base.parent).pawn != null && !GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(Props.moveSpeedFactorByTerrainTag))
		{
			StaticCollectionsClass.RemoveMoveSpeedFactorByTerrainTag((Thing)(object)((Hediff)base.parent).pawn, this);
		}
	}
}
