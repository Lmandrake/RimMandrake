using System.Xml;
using Verse;

namespace BigAndSmall;

public abstract class PatchOp_IfSettings : PatchOperation
{
	protected readonly PatchOperation match;

	protected readonly PatchOperation nomatch;

	protected abstract bool ShouldApply();

	protected override bool ApplyWorker(XmlDocument xml)
	{
		if (ShouldApply())
		{
			if (match != null)
			{
				return match.Apply(xml);
			}
		}
		else if (nomatch != null)
		{
			return nomatch.Apply(xml);
		}
		return true;
	}
}
