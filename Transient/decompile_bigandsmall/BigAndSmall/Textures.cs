using UnityEngine;
using Verse;

namespace BigAndSmall;

[StaticConstructorOnStartup]
public static class Textures
{
	public static Texture2D ColorPawn_Icon { get; } = ContentFinder<Texture2D>.Get("BS_UI/ColorPawn", true);

	public static Texture2D Mechanical_Icon { get; } = ContentFinder<Texture2D>.Get("BS_Traits/BS_Mechanical", true);

	public static Texture2D AlienIcon_Icon { get; } = ContentFinder<Texture2D>.Get("BS_UI/Race", true);

	public static Texture2D BrightnessTexture { get; } = ContentFinder<Texture2D>.Get("BS_UI/BrightnessGradient", true);

	public static Texture2D SliderHandle { get; } = ContentFinder<Texture2D>.Get("UI/Buttons/SliderHandle", true);
}
