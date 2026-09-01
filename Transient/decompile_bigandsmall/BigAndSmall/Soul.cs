using Verse;

namespace BigAndSmall;

public static class Soul
{
	public static SoulCollector GetOrAddSoulCollector(Pawn attacker)
	{
		if (BSDefs.BS_SoulCollector == null)
		{
			Log.Warning("Soul Collector Hediff is null. This is likely due to a missing mod or a missing def.");
			return null;
		}
		SoulCollector soulCollector = (SoulCollector)(object)attacker.health.hediffSet.GetFirstHediffOfDef(BSDefs.BS_SoulCollector, false);
		if (soulCollector == null)
		{
			attacker.health.AddHediff(BSDefs.BS_SoulCollector, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			soulCollector = (SoulCollector)(object)attacker.health.hediffSet.GetFirstHediffOfDef(BSDefs.BS_SoulCollector, false);
		}
		return soulCollector;
	}
}
