using System.Runtime.CompilerServices;
using System.Text;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class RacialFeatureDef : Def, IRacialFeature
{
	[NoTranslate]
	public string iconPath = "BS_Traits/DisguisedDemon";

	public Color? iconColor = Color.white;

	private string cachedDescription;

	[CompilerGenerated]
	private Texture2D _003CIcon_003Ek__BackingField;

	public string Label => base.label;

	public Texture2D Icon
	{
		get
		{
			if ((Object)(object)_003CIcon_003Ek__BackingField == (Object)null)
			{
				if (GenText.NullOrEmpty(iconPath))
				{
					_003CIcon_003Ek__BackingField = BaseContent.BadTex;
				}
				else
				{
					_003CIcon_003Ek__BackingField = ContentFinder<Texture2D>.Get(iconPath, true) ?? BaseContent.BadTex;
				}
			}
			return _003CIcon_003Ek__BackingField;
		}
	}

	public Color IconColor => (Color)(((_003F?)iconColor) ?? Color.white);

	public string DescriptionFull => cachedDescription ?? (cachedDescription = GetDescriptionFull());

	protected string GetDescriptionFull()
	{
		StringBuilder stringBuilder = new StringBuilder();
		if (!GenText.NullOrEmpty(base.description))
		{
			stringBuilder.AppendLine(base.description);
		}
		return stringBuilder.ToString();
	}
}
