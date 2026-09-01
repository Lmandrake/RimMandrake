using RimWorld;
using Verse;

namespace BigAndSmall;

public class ShrinkRayHediff : HediffWithComps
{
	public override float Severity
	{
		get
		{
			return ((Hediff)this).Severity;
		}
		set
		{
			((Hediff)this).Severity = value;
			HumanoidPawnScaler.GetCache(((Hediff)this).pawn, forceRefresh: true);
			((Hediff)this).pawn.Drawer.renderer.SetAllGraphicsDirty();
		}
	}

	public override void PostTick()
	{
		((HediffWithComps)this).PostTick();
		if (Find.TickManager.TicksGame % 250 == 0)
		{
			HumanoidPawnScaler.GetCache(((Hediff)this).pawn, forceRefresh: true);
			((Hediff)this).pawn.Drawer.renderer.SetAllGraphicsDirty();
		}
		if (((Hediff)this).pawn.BodySize <= 0.051f)
		{
			KillTarget();
		}
	}

	private void KillTarget()
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Expected O, but got Unknown
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		DamageInfo value = default(DamageInfo);
		((DamageInfo)(ref value))._002Ector(new DamageDef
		{
			deathMessage = "{0} popped out of existance"
		}, 0f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)(object)((Hediff)this).pawn, true, true, (QualityCategory)2, true, false);
		((Thing)((Hediff)this).pawn).Kill((DamageInfo?)value, (Hediff)null);
		if (MakeCorpse_Patch.corpse != null)
		{
			((Thing)MakeCorpse_Patch.corpse).Destroy((DestroyMode)0);
			MakeCorpse_Patch.corpse = null;
		}
	}

	public override bool CauseDeathNow()
	{
		return false;
	}
}
