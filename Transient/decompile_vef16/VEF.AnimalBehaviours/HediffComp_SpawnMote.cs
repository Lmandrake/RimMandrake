using RimWorld;
using VEF.Global;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_SpawnMote : HediffComp
{
	public Mote spawnedMote;

	public HediffCompProperties_SpawnMote Props => base.props as HediffCompProperties_SpawnMote;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		if (spawnedMote == null)
		{
			spawnedMote = MoteMaker.MakeAttachedOverlay((Thing)(object)((HediffComp)this).Pawn, Props.moteDef, Props.offset, 1f, -1f);
			if (spawnedMote is MoteAttachedScaled moteAttachedScaled)
			{
				moteAttachedScaled.maxScale = Props.maxScale;
			}
		}
		if (((Thing)spawnedMote).def.mote.needsMaintenance)
		{
			spawnedMote.Maintain();
		}
		((HediffComp)this).CompPostTick(ref severityAdjustment);
	}

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_References.Look<Mote>(ref spawnedMote, "spawnedMote", false);
	}
}
