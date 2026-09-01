namespace BigAndSmall;

public class PatchOp_RobotsEnabled : PatchOp_IfSettings
{
	protected override bool ShouldApply()
	{
		if (!BigSmallMod.settings.GetAndroidsEnabled())
		{
			return BigSmall.RobotsEnabled;
		}
		return true;
	}
}
