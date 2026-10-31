using System.Collections.Generic;
using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>Tuning for RM_DamageWorker_Bloodlust, on the DamageDef's modExtensions. Absent: the defaults below.</summary>
	public class RM_BloodlustExtension : DefModExtension
	{
		/// <summary>Share of the damage the stab actually dealt (after armour) that heals the attacker.</summary>
		public float healFraction = 0.5f;

		/// <summary>Most one hit may heal; 0 = no cap.</summary>
		public float maxHealPerHit = 0f;
	}

	/// <summary>
	/// ZRRIK_VAMPIRIC_STAB_REBUILD_OWN_BLOODLUST. RM_Zrrik's "vampiric stab": a vanilla stab that, once it draws blood from a
	/// living flesh pawn, heals the attacker's own fresh wounds (never scars) by a share of the damage dealt, worst wound first.
	/// Replaces Alpha Animals' DamageWorker_Vampiric (donor retired 2026-10-18). The rules are RM_RulesKernel.Bloodlust*
	/// (fuzzed in SelfTest/GreentideFuzz.cs, family "rules").
	/// </summary>
	public class RM_DamageWorker_Bloodlust : DamageWorker_Stab
	{
		public override DamageResult Apply(DamageInfo dinfo, Thing thing)
		{
			DamageResult result = base.Apply(dinfo, thing);
			Pawn attacker = dinfo.Instigator as Pawn;
			Pawn victim = thing as Pawn;
			if (attacker == null || result == null)
			{
				return result;
			}
			RM_BloodlustExtension ext = def?.GetModExtension<RM_BloodlustExtension>();
			float fraction = ext != null ? ext.healFraction : 0.5f;
			float cap = ext != null ? ext.maxHealPerHit : 0f;
			bool feeds = RM_RulesKernel.BloodlustFeeds(!attacker.Dead && attacker.health != null, attacker == victim,
				victim != null && victim.RaceProps != null && victim.RaceProps.IsFlesh, result.totalDamageDealt, fraction);
			if (!feeds)
			{
				return result;
			}
			var wounds = new List<Hediff_Injury>();
			List<Hediff> hediffs = attacker.health.hediffSet.hediffs;
			for (int i = 0; i < hediffs.Count; i++)
			{
				if (hediffs[i] is Hediff_Injury injury && !injury.IsPermanent() && injury.Severity > 0f)
				{
					wounds.Add(injury);
				}
			}
			if (wounds.Count == 0)
			{
				return result;
			}
			var severities = new float[wounds.Count];
			for (int i = 0; i < wounds.Count; i++)
			{
				severities[i] = wounds[i].Severity;
			}
			float[] heal = RM_RulesKernel.BloodlustHeals(result.totalDamageDealt, fraction, cap, severities);
			for (int i = 0; i < wounds.Count; i++)
			{
				// Heal() may remove a wound from hediffSet; the snapshot keeps the references valid.
				if (heal[i] > 0f && !attacker.Dead)
				{
					wounds[i].Heal(heal[i]);
				}
			}
			return result;
		}
	}
}
