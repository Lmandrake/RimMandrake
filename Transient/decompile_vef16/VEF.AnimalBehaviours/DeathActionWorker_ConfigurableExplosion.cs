using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace VEF.AnimalBehaviours;

public class DeathActionWorker_ConfigurableExplosion : DeathActionWorker
{
	public DeathActionProperties_ConfigurableExplosion Props => (DeathActionProperties_ConfigurableExplosion)(object)base.props;

	public override RulePackDef DeathRules => RulePackDefOf.Transition_DiedExplosive;

	public override bool DangerousInMelee => true;

	public override void PawnDied(Corpse corpse, Lord prevLord)
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		float num = ((corpse.InnerPawn.ageTracker.CurLifeStageIndex == 0) ? Props.babyExplosionRadius : ((corpse.InnerPawn.ageTracker.CurLifeStageIndex != 1) ? Props.adultExplosionRadius : Props.juvenileExplosionRadius));
		GenExplosion.DoExplosion(((Thing)corpse).Position, ((Thing)corpse).Map, num, Props.damageDef, (Thing)(object)corpse.InnerPawn, Props.damAmount, (float)Props.armorPenetration, Props.explosionSound, (ThingDef)null, (ThingDef)null, (Thing)null, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, (FloatRange?)null, true, 1f, 0f, true, (ThingDef)null, 1f, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}
}
