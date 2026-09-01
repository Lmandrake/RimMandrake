namespace BigAndSmall;

public class PatchOp_FantasyEnabled : PatchOp_IfSettings
{
	protected override bool ShouldApply()
	{
		return BigSmallMod.settings.useFantasyNames;
	}
}
