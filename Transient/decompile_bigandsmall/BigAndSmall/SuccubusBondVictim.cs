using RimWorld;
using Verse;

namespace BigAndSmall;

public class SuccubusBondVictim : Hediff
{
	public override void Tick()
	{
		((Hediff)this).Tick();
		if (Gen.IsHashIntervalTick((Thing)(object)base.pawn, 1000))
		{
			float statValue = StatExtension.GetStatValue((Thing)(object)base.pawn, StatDefOf.PsychicSensitivity, true, -1);
			int psylinkLevel = PawnUtility.GetPsylinkLevel(base.pawn);
			if (statValue >= 1.5f && psylinkLevel >= 5)
			{
				((Hediff)this).Severity = 2f;
			}
			else
			{
				((Hediff)this).Severity = 1f;
			}
		}
	}
}
