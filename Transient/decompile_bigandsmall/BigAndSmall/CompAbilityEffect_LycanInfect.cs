using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

/// <summary>
/// Just apply a bunch of Vampirism.
/// </summary>
public class CompAbilityEffect_LycanInfect : CompAbilityEffect
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		object obj = ((LocalTargetInfo)(ref target)).Pawn;
		if (obj == null)
		{
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			Thing obj2 = ((thing is Corpse) ? thing : null);
			obj = ((obj2 != null) ? ((Corpse)obj2).InnerPawn : null);
		}
		Pawn val = (Pawn)obj;
		if (val != null)
		{
			ApplyLycantropy(val);
			((CompAbilityEffect)this).Apply(target, dest);
		}
	}

	private void ApplyLycantropy(Pawn pawn)
	{
		IEnumerable<HediffDef> source = DefDatabase<HediffDef>.AllDefsListForReading.Where((HediffDef x) => ((Def)x).defName == "VU_Lycantropy");
		_ = ((AbilityComp)this).parent.pawn;
		if (source.Count() > 0)
		{
			HediffDef val = source.First();
			Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(val, false);
			if (firstHediffOfDef == null)
			{
				firstHediffOfDef = HediffMaker.MakeHediff(val, pawn, (BodyPartRecord)null);
				firstHediffOfDef.Severity = 0.45f;
				pawn.health.AddHediff(firstHediffOfDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
		else
		{
			Log.Warning($"Something went wrong, {pawn} hediff VU_Lycantropy could not be found. This is likely an mistake from the mod author.");
		}
	}
}
