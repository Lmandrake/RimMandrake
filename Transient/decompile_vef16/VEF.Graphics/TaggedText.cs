namespace VEF.Graphics;

public class TaggedText : TaggedItem<string>
{
	public TaggedText()
	{
	}

	public TaggedText(string tag, string value)
		: base(tag, value)
	{
	}
}
