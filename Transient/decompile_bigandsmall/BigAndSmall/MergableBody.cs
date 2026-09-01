using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class MergableBody
{
	public BodyDef bodyDef;

	public ThingDef thingDef;

	[NoTranslate]
	public string overrideDefNamer;

	public string prefixLabel;

	public string suffixLabel;

	private bool fuse = true;

	public bool fuseAll;

	public bool fuseSet;

	public bool isMechanical;

	public bool defaultMechanical;

	public bool canBeFusionOne = true;

	public bool canMakeRobotVersion = true;

	public List<string> exclusionTags = new List<string>();

	public List<SimilarParts> removesParts = new List<SimilarParts>();

	/// <summary>
	/// Which order this will be merged in. Put weird stuff with a higher priority.
	///
	/// It is likely better that weird bodies are bodyOne so that a snake-hybrid starts with a snake body rather than trying to replace the legs.
	/// </summary>
	public float priority;

	public bool Fuse
	{
		get
		{
			if (fuse)
			{
				return !fuseSet;
			}
			return false;
		}
	}

	public bool ShouldRemovePart(BodyPartDef part)
	{
		foreach (SimilarParts removesPart in removesParts)
		{
			if (removesPart.Parts.Contains(part))
			{
				return true;
			}
		}
		return false;
	}
}
