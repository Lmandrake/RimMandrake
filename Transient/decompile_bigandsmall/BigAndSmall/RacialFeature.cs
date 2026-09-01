using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Text;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class RacialFeature : IRacialFeature
{
	public string label = "Unnamed";

	public string description = "No description available.";

	public HediffDef hediffDescriptionSource;

	public string iconPath = "BS_Traits/Disguised";

	public Color? iconColor = Color.white;

	private string cachedDescription;

	[CompilerGenerated]
	private Texture2D _003CIcon_003Ek__BackingField;

	public string Label => label;

	public string DescriptionFull => cachedDescription ?? (cachedDescription = GetDescriptionFull());

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

	protected string GetDescriptionFull()
	{
		StringBuilder stringBuilder = new StringBuilder();
		if (hediffDescriptionSource != null)
		{
			stringBuilder.AppendLine(hediffDescriptionSource.Description);
		}
		stringBuilder.AppendLine(description);
		return stringBuilder.ToString();
	}

	public RacialFeature SetupFromThis(List<PawnExtension> extensions)
	{
		RacialFeature racialFeature = new RacialFeature
		{
			label = label,
			description = description,
			iconPath = iconPath,
			iconColor = iconColor,
			hediffDescriptionSource = hediffDescriptionSource
		};
		try
		{
			if (extensions.TryGetDescription(out var content))
			{
				racialFeature.cachedDescription = content + "\n\n" + racialFeature.cachedDescription;
			}
		}
		catch (Exception ex)
		{
			Log.ErrorOnce("Caught Exception in RacialFeatureDef.SetupFromThis: " + ex.Message + "\n" + ex.StackTrace, 423589);
		}
		return racialFeature;
	}
}
