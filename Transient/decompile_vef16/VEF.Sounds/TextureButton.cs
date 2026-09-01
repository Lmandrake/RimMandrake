using UnityEngine;
using Verse;

namespace VEF.Sounds;

[StaticConstructorOnStartup]
public class TextureButton
{
	public static Texture2D VFELogo = ContentFinder<Texture2D>.Get("UI/Widgets/VFELogo", true);
}
