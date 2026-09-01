using RimWorld;
using Verse;

namespace BigAndSmall;

public class ConditionalStatAffecter_PsychicSensitivityHigh : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("PsychicSensitivity_High"));

	public virtual float SensitivityThreshold => 1.59f;

	public override bool Applies(StatRequest req)
	{
		Thing thing = ((StatRequest)(ref req)).Thing;
		if (thing != null && thing.Spawned)
		{
			Thing thing2 = ((StatRequest)(ref req)).Thing;
			Pawn val = (Pawn)(object)((thing2 is Pawn) ? thing2 : null);
			if (val != null && StatExtension.GetStatValue((Thing)(object)val, StatDefOf.PsychicSensitivity, true, 10000) >= SensitivityThreshold)
			{
				return true;
			}
		}
		return false;
	}
}
