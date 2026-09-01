using System.Collections.Generic;

namespace BigAndSmall;

public class PrerequisiteSet
{
	public enum PrerequisiteType
	{
		AnyOf,
		AllOf,
		NoneOf
	}

	public float allOfPerecntage = 1f;

	public float noneOfPercentage;

	public List<string> prerequisites;

	public PrerequisiteType type;
}
