using System.Linq;
using Verse;

namespace BigAndSmall;

public class HasCustomizableGraphics : DefModExtension
{
	private FlagString tag;

	public bool colorA;

	public bool colorB;

	public bool colorC;

	public FlagStringList customFlags = new FlagStringList();

	public FlagString Flag
	{
		get
		{
			return tag;
		}
		set
		{
			tag = value;
		}
	}

	public override string ToString()
	{
		return string.Format("[{0}] - Tag: {1}, ColorA: {2}, ColorB: {3}, ColorC: {4}", "HasCustomizableGraphics", Flag, colorA, colorB, colorC);
	}

	public HasCustomizableGraphics TryMerge(HasCustomizableGraphics other)
	{
		FlagString flagString = Flag.TryFuseIdentical(other.Flag);
		if ((object)flagString != null)
		{
			HasCustomizableGraphics hasCustomizableGraphics = new HasCustomizableGraphics();
			hasCustomizableGraphics.Flag = flagString;
			hasCustomizableGraphics.colorA = colorA || other.colorA;
			hasCustomizableGraphics.colorB = colorB || other.colorB;
			hasCustomizableGraphics.colorC = colorC || other.colorC;
			HasCustomizableGraphics hasCustomizableGraphics2 = hasCustomizableGraphics;
			FlagStringList flagStringList = new FlagStringList();
			foreach (FlagString item in customFlags.Union(other.customFlags))
			{
				flagStringList.Add(item);
			}
			hasCustomizableGraphics2.customFlags = flagStringList;
			return hasCustomizableGraphics;
		}
		return null;
	}
}
