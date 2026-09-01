using RimWorld;
using Verse;

namespace BigAndSmall;

public class LockedNeedClass
{
	public NeedDef need;

	public float value;

	public bool minValue;

	public string GetLabel()
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		if (need == null)
		{
			return "";
		}
		return TaggedString.op_Implicit(((Def)need).LabelCap + (minValue ? " Min" : ""));
	}
}
