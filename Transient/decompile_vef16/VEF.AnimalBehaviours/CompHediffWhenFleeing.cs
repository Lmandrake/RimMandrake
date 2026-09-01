using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompHediffWhenFleeing : ThingComp
{
	public int cooldownCounter;

	public const int cooldown = 60000;

	public bool onCoolDown;

	public CompProperties_HediffWhenFleeing Props => (CompProperties_HediffWhenFleeing)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref cooldownCounter, "cooldownCounter", 0, false);
		Scribe_Values.Look<bool>(ref onCoolDown, "onCoolDown", false, false);
	}

	public override void CompTickInterval(int delta)
	{
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (onCoolDown)
		{
			cooldownCounter += delta;
			if (cooldownCounter >= 60000)
			{
				onCoolDown = false;
			}
		}
		else
		{
			if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta) || ((Thing)base.parent).Map == null)
			{
				return;
			}
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val.CurJob?.def != JobDefOf.Flee && val.CurJob?.def != JobDefOf.FleeAndCower)
			{
				return;
			}
			if (Props.graphicAndSoundEffect)
			{
				SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)val).Position, ((Thing)val).Map, false)));
				FleckMaker.AttachedOverlay((Thing)(object)val, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 6f, -1f);
			}
			val.health.AddHediff(Props.hediffToCause, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			if (Props.hediffOnRadius)
			{
				foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)val).Position, ((Thing)val).Map, Props.radius, true))
				{
					Pawn val2 = (Pawn)(object)((item is Pawn) ? item : null);
					if (val2 != null && ((Thing)val2).Faction == Faction.OfPlayerSilentFail && !val2.Dead && !val2.Downed && StatExtension.GetStatValue((Thing)(object)val2, StatDefOf.PsychicSensitivity, true, -1) > 0f)
					{
						val2.health.AddHediff(Props.hediffToCause, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
					}
				}
			}
			onCoolDown = true;
		}
	}
}
