using Verse;

namespace BigAndSmall;

public class ConditionalStatAffecter_PsychicSensitivityVeryHigh : ConditionalStatAffecter_PsychicSensitivityHigh
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("PsychicSensitivity_VeryHigh"));

	public override float SensitivityThreshold => 2.24f;
}
