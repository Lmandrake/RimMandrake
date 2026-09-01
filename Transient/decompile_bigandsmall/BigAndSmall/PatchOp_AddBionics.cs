namespace BigAndSmall;

public class PatchOp_AddBionics : PatchOp_IfSettings
{
	protected override bool ShouldApply()
	{
		return BigSmallMod.settings.surgeryAndBionics;
	}
}
