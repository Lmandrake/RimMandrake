using Verse;

namespace VEF.Genes;

public class HediffComp_CustomBlood : HediffComp
{
	public HediffCompProperties_CustomBlood Props => (HediffCompProperties_CustomBlood)(object)base.props;

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		AddThings();
	}

	public override void CompPostPostRemoved()
	{
		RemoveThings();
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		RemoveThings();
	}

	public override void Notify_PawnKilled()
	{
		RemoveThings();
	}

	public void AddThings()
	{
		if (((Hediff)base.parent).pawn != null)
		{
			if (Props.customBloodThingDef != null)
			{
				StaticCollectionsClass.AddBloodtypeGenePawnToList((Thing)(object)((Hediff)base.parent).pawn, Props.customBloodThingDef);
			}
			if (Props.customBloodIcon != "")
			{
				StaticCollectionsClass.AddBloodIconGenePawnToList((Thing)(object)((Hediff)base.parent).pawn, Props.customBloodIcon);
			}
			if (Props.customBloodEffect != null)
			{
				StaticCollectionsClass.AddBloodEffectGenePawnToList((Thing)(object)((Hediff)base.parent).pawn, Props.customBloodEffect);
			}
			if (Props.customWoundsFromFleshtype != null)
			{
				StaticCollectionsClass.AddWoundsFromFleshtypeGenePawnToList((Thing)(object)((Hediff)base.parent).pawn, Props.customWoundsFromFleshtype);
			}
		}
	}

	public void RemoveThings()
	{
		if (((Hediff)base.parent).pawn != null)
		{
			if (Props.customBloodThingDef != null)
			{
				StaticCollectionsClass.RemoveBloodtypeGenePawnFromList((Thing)(object)((Hediff)base.parent).pawn);
			}
			if (Props.customBloodIcon != "")
			{
				StaticCollectionsClass.RemoveBloodIconGenePawnFromList((Thing)(object)((Hediff)base.parent).pawn);
			}
			if (Props.customBloodEffect != null)
			{
				StaticCollectionsClass.RemoveBloodEffectGenePawnFromList((Thing)(object)((Hediff)base.parent).pawn);
			}
			if (Props.customWoundsFromFleshtype != null)
			{
				StaticCollectionsClass.RemoveWoundsFromFleshtypeGenePawnFromList((Thing)(object)((Hediff)base.parent).pawn);
			}
		}
	}
}
