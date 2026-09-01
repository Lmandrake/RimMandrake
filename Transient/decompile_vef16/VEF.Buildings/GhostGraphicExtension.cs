using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class GhostGraphicExtension : DefModExtension
{
	public enum CustomGhostMode
	{
		Vanilla,
		VanillaNoLinking,
		Blueprint,
		CustomGraphicPath,
		CustomGraphicMethodCached,
		CustomGraphicMethodNotCached
	}

	public class GraphicDataOverride
	{
		[NoTranslate]
		public string texPath;

		public Type graphicClass;

		public Vector2? drawSize;

		public bool? drawRotated;

		public bool? allowFlip;
	}

	public CustomGhostMode ghostMode;

	public CustomGhostMode extraGraphicGhostMode;

	public GraphicDataOverride customGraphicData;

	public GraphicDataOverride extraCustomGraphicData;

	public virtual Graphic GetCustomGraphic(Graphic baseGraphic, ThingDef thingDef, Color ghostCol, ThingDef stuff, bool main, int hash)
	{
		return null;
	}

	public override IEnumerable<string> ConfigErrors()
	{
		foreach (string item in _003C_003En__0())
		{
			yield return item;
		}
		if (!CustomGhostModeEnabled(ghostMode) && !CustomGhostModeEnabled(extraGraphicGhostMode))
		{
			yield return string.Format("both {0} and {1} are {2} and {3}, the extension won't work.", "ghostMode", "extraGraphicGhostMode", ghostMode, extraGraphicGhostMode);
		}
		if (ghostMode == CustomGhostMode.CustomGraphicPath)
		{
			if (customGraphicData == null)
			{
				yield return string.Format("{0} is {1}, but {2} is null.", "ghostMode", ghostMode, "customGraphicData");
			}
			else if (GenText.NullOrEmpty(customGraphicData.texPath))
			{
				yield return string.Format("{0} is {1}, but {2}.{3} is null or empty", "ghostMode", ghostMode, "customGraphicData", "texPath");
			}
		}
		if (extraGraphicGhostMode == CustomGhostMode.CustomGraphicPath)
		{
			if (extraCustomGraphicData == null)
			{
				yield return string.Format("{0} is {1}, but {2} is null.", "extraGraphicGhostMode", extraGraphicGhostMode, "extraCustomGraphicData");
			}
			else if (GenText.NullOrEmpty(extraCustomGraphicData.texPath))
			{
				yield return string.Format("{0} is {1}, but {2}.{3} is null or empty", "extraGraphicGhostMode", extraGraphicGhostMode, "extraCustomGraphicData", "texPath");
			}
		}
	}

	public static bool CustomGhostModeEnabled(CustomGhostMode ghostMode)
	{
		if (ghostMode > CustomGhostMode.Vanilla)
		{
			return (int)ghostMode < Enum.GetNames(typeof(CustomGhostMode)).Length;
		}
		return false;
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0()
	{
		return ((DefModExtension)this).ConfigErrors();
	}
}
