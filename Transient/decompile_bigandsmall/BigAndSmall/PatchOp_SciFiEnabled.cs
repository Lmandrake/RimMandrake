namespace BigAndSmall;

public class PatchOp_SciFiEnabled : PatchOp_IfSettings
{
	protected override bool ShouldApply()
	{
		return BigSmallMod.settings.useSciFiNames;
	}
}
