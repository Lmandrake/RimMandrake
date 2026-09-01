namespace BigAndSmall;

public class FlagStringStateData(EditPawnWindow.WindowTab? category, string customCategory, string label)
{
	public EditPawnWindow.WindowTab? displayTab = category;

	public string customCategory = customCategory;

	public string label = label;
}
