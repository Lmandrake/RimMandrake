using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class AcidBuildUp : Hediff
{
	public static DamageDef acidDmgDef;

	private const float totalDamageAtMaxSeverity = 40f;

	private const float totalDurationAtOneSeverity = 2500f;

	private const int ticksBetweenDamage = 200;

	public static DamageDef AcidDmgDef
	{
		get
		{
			if (acidDmgDef == null)
			{
				acidDmgDef = DefDatabase<DamageDef>.GetNamed("BS_AcidDmgDirect", true);
				if (acidDmgDef == null)
				{
					acidDmgDef = DefDatabase<DamageDef>.GetNamed("AcidBurn", true);
				}
			}
			return acidDmgDef;
		}
	}

	public override string LabelInBrackets => GenText.ToStringPercent(((Hediff)this).Severity);

	public override void Tick()
	{
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		((Hediff)this).Tick();
		if (Find.TickManager.TicksGame % 200 == 0 && base.pawn != null && !base.pawn.Dead)
		{
			if (((Hediff)this).Severity > 3f)
			{
				((Hediff)this).Severity = 3f;
			}
			float num = 3.2f * Mathf.Lerp(base.pawn.BodySize, base.pawn.HealthScale, 0.5f);
			((Hediff)this).Severity = ((Hediff)this).Severity - 0.08f;
			((Thing)base.pawn).TakeDamage(new DamageInfo(AcidDmgDef, num, 300f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
	}
}
