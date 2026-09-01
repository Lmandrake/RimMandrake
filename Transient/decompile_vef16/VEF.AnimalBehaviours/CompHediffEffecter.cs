using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompHediffEffecter : ThingComp
{
	public List<Pawn> pawnList = new List<Pawn>();

	public Pawn thisPawn;

	public CompProperties_HediffEffecter Props => (CompProperties_HediffEffecter)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!AnimalBehaviours_Settings.flagEffecters || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ref Pawn reference = ref thisPawn;
		ThingWithComps parent = base.parent;
		reference = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (thisPawn == null || ((Thing)thisPawn).Map == null || thisPawn.Dead || thisPawn.Downed)
		{
			return;
		}
		foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)thisPawn).Position, ((Thing)thisPawn).Map, (float)Props.radius, true))
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val != null && (val.IsColonist || Props.notOnlyAffectColonists) && !val.Dead && !val.Downed && StatExtension.GetStatValue((Thing)(object)val, StatDefOf.PsychicSensitivity, true, -1) > 0f)
			{
				FleckMaker.AttachedOverlay((Thing)(object)base.parent, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
				val.health.AddHediff(HediffDef.Named(Props.hediff), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}
}
