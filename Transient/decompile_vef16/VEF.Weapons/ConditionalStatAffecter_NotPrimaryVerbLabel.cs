using Verse;

namespace VEF.Weapons;

public class ConditionalStatAffecter_NotPrimaryVerbLabel : ConditionalStatAffecter_PrimaryVerbLabel
{
	protected override bool IsApplicableVerbs(Verb verb)
	{
		return !base.IsApplicableVerbs(verb);
	}
}
