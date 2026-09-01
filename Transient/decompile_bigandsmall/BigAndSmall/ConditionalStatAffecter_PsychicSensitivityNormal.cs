using Verse;

namespace BigAndSmall;

public class ConditionalStatAffecter_PsychicSensitivityNormal : ConditionalStatAffecter_PsychicSensitivityHigh
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("PsychicSensitivity_Normal"));

	public override float SensitivityThreshold => 0.9f;
}
