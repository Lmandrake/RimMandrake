using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompThoughtEffecter : ThingComp
{
	public List<Pawn> pawnList = new List<Pawn>();

	public Pawn thisPawn;

	public CompProperties_ThoughtEffecter Props => (CompProperties_ThoughtEffecter)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01af: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!AnimalBehaviours_Settings.flagEffecters || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ref Pawn reference = ref thisPawn;
		ThingWithComps parent = base.parent;
		reference = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (thisPawn == null || ((Thing)thisPawn).Map == null || thisPawn.Dead || thisPawn.Downed || (Props.needsToBeTamed && (!Props.needsToBeTamed || ((Thing)thisPawn).Faction == null || !((Thing)thisPawn).Faction.IsPlayer)))
		{
			return;
		}
		foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)thisPawn).Position, ((Thing)thisPawn).Map, (float)Props.radius, true))
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val == null || val.needs?.mood?.thoughts == null || WildManUtility.AnimalOrWildMan(val) || !val.RaceProps.IsFlesh || val == base.parent || val.Dead || val.Downed || !(StatExtension.GetStatValue((Thing)(object)val, StatDefOf.PsychicSensitivity, true, -1) > 0f))
			{
				continue;
			}
			if (Props.showEffect)
			{
				Find.TickManager.slower.SignalForceNormalSpeedShort();
				SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
				FleckMaker.AttachedOverlay((Thing)(object)base.parent, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
			}
			if (!Props.conditionalOnWellBeing)
			{
				val.needs.mood.thoughts.memories.TryGainMemory(ThoughtDef.Named(Props.thoughtDef), (Pawn)null, (Precept)null);
				continue;
			}
			Pawn_NeedsTracker needs = thisPawn.needs;
			if (needs != null)
			{
				Need_Food food = needs.food;
				if (((food != null) ? new bool?(food.Starving) : ((bool?)null)) == true)
				{
					goto IL_02af;
				}
			}
			Pawn_HealthTracker health = thisPawn.health;
			if (health != null)
			{
				HediffSet hediffSet = health.hediffSet;
				if (((hediffSet != null) ? new float?(hediffSet.PainTotal) : ((float?)null)) > 0f)
				{
					goto IL_02af;
				}
			}
			Pawn_NeedsTracker needs2 = val.needs;
			if (needs2 == null)
			{
				continue;
			}
			Need_Mood mood = needs2.mood;
			if (mood == null)
			{
				continue;
			}
			ThoughtHandler thoughts = mood.thoughts;
			if (thoughts != null)
			{
				MemoryThoughtHandler memories = thoughts.memories;
				if (memories != null)
				{
					memories.TryGainMemory(ThoughtDef.Named(Props.thoughtDef), (Pawn)null, (Precept)null);
				}
			}
			continue;
			IL_02af:
			Pawn_NeedsTracker needs3 = val.needs;
			if (needs3 != null)
			{
				Need_Mood mood2 = needs3.mood;
				if (mood2 != null)
				{
					ThoughtHandler thoughts2 = mood2.thoughts;
					if (thoughts2 != null)
					{
						MemoryThoughtHandler memories2 = thoughts2.memories;
						if (memories2 != null)
						{
							memories2.RemoveMemoriesOfDef(ThoughtDef.Named(Props.thoughtDef));
						}
					}
				}
			}
			Pawn_NeedsTracker needs4 = val.needs;
			if (needs4 == null)
			{
				continue;
			}
			Need_Mood mood3 = needs4.mood;
			if (mood3 == null)
			{
				continue;
			}
			ThoughtHandler thoughts3 = mood3.thoughts;
			if (thoughts3 != null)
			{
				MemoryThoughtHandler memories3 = thoughts3.memories;
				if (memories3 != null)
				{
					memories3.TryGainMemory(ThoughtDef.Named(Props.thoughtDefWhenSuffering), (Pawn)null, (Precept)null);
				}
			}
		}
	}
}
