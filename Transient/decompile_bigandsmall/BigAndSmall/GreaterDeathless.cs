using RimWorld;
using Verse;

namespace BigAndSmall;

public class GreaterDeathless : TickdownGene
{
	public override void TickEvent()
	{
		HediffDef named = DefDatabase<HediffDef>.GetNamed("DeathRefusal", true);
		if (((Gene)this).pawn.health.hediffSet.GetFirstHediffOfDef(named, false) == null)
		{
			((Gene)this).pawn.health.AddHediff(named, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}

	public override void ResetCountdown()
	{
		tickDown = Rand.Range(10000, 120000);
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		((Gene)this).Notify_PawnDied(dinfo, culprit);
		HediffDef named = DefDatabase<HediffDef>.GetNamed("DeathRefusal", true);
		if ((((Gene)this).pawn.health.hediffSet.GetFirstHediffOfDef(named, false) != null && ((Gene)this).pawn.IsPrisoner) || ((Gene)this).pawn.IsSlave)
		{
			((Gene)this).pawn.guest.SetGuestStatus((Faction)null, (GuestStatus)0);
		}
	}

	public override void PostAdd()
	{
		((Gene)this).PostAdd();
		if (((Thing)((Gene)this).pawn).Faction != Faction.OfPlayerSilentFail && ((Gene)this).pawn.HostFaction != Faction.OfPlayerSilentFail && ModLister.CheckAnomaly("Death refusal") && !((Gene)this).pawn.Dead)
		{
			HediffDef named = DefDatabase<HediffDef>.GetNamed("DeathRefusal", true);
			if (((Gene)this).pawn.health.hediffSet.GetFirstHediffOfDef(named, false) == null)
			{
				((Gene)this).pawn.health.AddHediff(named, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}
}
