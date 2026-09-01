using Verse;

namespace VEF.Buildings;

public class ColorOption
{
	public float overlightRadius;

	public float glowRadius = 14f;

	public string texPath;

	public ColorInt glowColor = new ColorInt(255, 255, 255, 0) * 1.45f;

	public bool colorPickerEnabled;

	public bool darklightToggle;

	public string colorLabel = "";
}
