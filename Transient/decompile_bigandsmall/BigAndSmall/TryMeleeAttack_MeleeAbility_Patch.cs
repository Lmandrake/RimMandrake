using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn_MeleeVerbs), "TryMeleeAttack")]
public static class TryMeleeAttack_MeleeAbility_Patch
{
	public static bool Prefix(Pawn_MeleeVerbs __instance, Thing target, Verb verbToUse = null, bool surpriseAttack = false)
	{
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = __instance.Pawn;
		try
		{
			if (pawn == null || pawn.Dead || pawn.Downed || (((Thing)pawn).Faction != null && ((Thing)pawn).Faction.IsPlayer) || pawn.stances.FullBodyBusy || pawn.WorkTagIsDisabled((WorkTags)8))
			{
				return true;
			}
		}
		catch
		{
			return true;
		}
		if (pawn?.abilities != null)
		{
			foreach (Ability item in from x in pawn.abilities.AllAbilitiesForReading.Where(delegate(Ability x)
				{
					//IL_0004: Unknown result type (might be due to invalid IL or missing references)
					if (x == null || !AcceptanceReport.op_Implicit(x.CanCast) || x.verb == null || !x.verb.IsMeleeAttack)
					{
						VerbProperties verbProps = x.verb.verbProps;
						if (verbProps != null && verbProps.range < 0f)
						{
							return x.def.aiCanUse;
						}
						return false;
					}
					return true;
				})
				where AcceptanceReport.op_Implicit(x.CanCast)
				select x)
			{
				LocalTargetInfo tgInfo = new LocalTargetInfo(target);
				if (item.CanApplyOn(tgInfo) && item.EffectComps.All((CompAbilityEffect x) => x.CanApplyOn(tgInfo, tgInfo)))
				{
					if (pawn.CurJob != null && ((Def)pawn.CurJob.def).defName == ((Def)item.def).defName)
					{
						return false;
					}
					pawn.jobs.StartJob(item.GetJob(tgInfo, tgInfo), (JobCondition)0, (ThinkNode)null, false, true, (ThinkTreeDef)null, (JobTag?)null, false, false, (bool?)null, false, true, false);
					item.StartCooldown(item.def.cooldownTicksRange.max);
					return false;
				}
			}
		}
		return true;
	}
}
