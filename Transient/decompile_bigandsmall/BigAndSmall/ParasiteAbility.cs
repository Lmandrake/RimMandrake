using BigAndSmall.Abillities;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace BigAndSmall;

public class ParasiteAbility : CompAbilityEffect_JumpAndUseOn
{
	private CompProperties_ParasiteAbility Props => ((CompAbilityEffect)this).Props as CompProperties_ParasiteAbility;

	public override bool AICanTargetNow(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return ((CompAbilityEffect)this).Valid(target, false);
	}

	public override void ApplyEffect(IntVec3 origin, LocalTargetInfo target)
	{
		if (((LocalTargetInfo)(ref target)).Pawn != null)
		{
			Pawn pawn = ((AbilityComp)this).parent.pawn;
			Pawn pawn2 = ((LocalTargetInfo)(ref target)).Pawn;
			IThingHolder parentHolder = ((Thing)pawn).ParentHolder;
			PawnFlyer val = (PawnFlyer)(object)((parentHolder is PawnFlyer) ? parentHolder : null);
			if (val != null)
			{
				((Thing)pawn).holdingOwner = null;
				((Thing)val).Destroy((DestroyMode)0);
			}
			if (((Thing)pawn2).Faction != ((Thing)((AbilityComp)this).parent.pawn).Faction && !FactionUtility.HostileTo(((Thing)pawn2).Faction, ((Thing)((AbilityComp)this).parent.pawn).Faction) && ((Thing)pawn2).Faction != null && ((Thing)pawn).Faction != null)
			{
				((Thing)pawn2).Faction.TryAffectGoodwillWith(((Thing)pawn).Faction, -35, true, true, (HistoryEventDef)null, (GlobalTargetInfo?)null);
			}
			if (pawn2.health.hediffSet.GetFirstHediffOfDef(Props.pilotHediff, false) is Piloted piloted)
			{
				piloted.AddPilot((Thing)(object)pawn);
				return;
			}
			Piloted piloted2 = HediffMaker.MakeHediff(Props.pilotHediff, pawn2, (BodyPartRecord)null) as Piloted;
			pawn2.health.AddHediff((Hediff)(object)piloted2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			piloted2.AddPilot((Thing)(object)pawn);
		}
	}

	public override bool Valid(LocalTargetInfo target, bool throwMessages = false)
	{
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0213: Unknown result type (might be due to invalid IL or missing references)
		//IL_0228: Unknown result type (might be due to invalid IL or missing references)
		//IL_022d: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn == null)
		{
			return false;
		}
		if ((double)pawn.BodySize * 0.8 < (double)((AbilityComp)this).parent.pawn.BodySize)
		{
			BSCache cachePrepatched = pawn.GetCachePrepatched();
			if (cachePrepatched == null || !cachePrepatched.isAmorphous || !((double)pawn.BodySize * 0.99 < (double)((AbilityComp)this).parent.pawn.BodySize))
			{
				if (throwMessages)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ParasiteTargetTooSmall", NamedArgument.op_Implicit(((Entity)pawn).Label), NamedArgument.op_Implicit(((Entity)((AbilityComp)this).parent.pawn).Label))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
				}
				return false;
			}
		}
		if (!pawn.RaceProps.Humanlike || pawn.IsMutant)
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ParasiteTargetNotHumanlike", NamedArgument.op_Implicit(((Entity)pawn).Label), NamedArgument.op_Implicit(((Entity)((AbilityComp)this).parent.pawn).Label))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		if (!pawn.Downed)
		{
			Pawn_StanceTracker stances = pawn.stances;
			if (stances != null)
			{
				StunHandler stunner = stances.stunner;
				if (((stunner != null) ? new bool?(stunner.Stunned) : ((bool?)null)) == true)
				{
					goto IL_0203;
				}
			}
			if (pawn.health.capacities.CapableOf(PawnCapacityDefOf.Consciousness))
			{
				Pawn_HealthTracker health = pawn.health;
				if (health != null)
				{
					PawnCapacitiesHandler capacities = health.capacities;
					if (((capacities != null) ? new float?(capacities.GetLevel(PawnCapacityDefOf.Consciousness)) : ((float?)null)) <= 0.75f)
					{
						goto IL_0203;
					}
				}
			}
			Pawn_HealthTracker health2 = pawn.health;
			if (health2 != null)
			{
				HediffSet hediffSet = health2.hediffSet;
				if (((hediffSet != null) ? new float?(hediffSet.PainTotal) : ((float?)null)) > 0.35f)
				{
					goto IL_0203;
				}
			}
			if (RestUtility.Awake(pawn))
			{
				if (throwMessages)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ParasiteTargetNotImpaired", NamedArgument.op_Implicit(((Entity)pawn).Label), NamedArgument.op_Implicit(((Entity)((AbilityComp)this).parent.pawn).Label))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
				}
				return false;
			}
		}
		goto IL_0203;
		IL_0203:
		return true;
	}

	public override bool CanApplyOn(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return ((CompAbilityEffect)this).Valid(target, false);
	}
}
