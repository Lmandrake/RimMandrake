using UnityEngine;
using Verse;

namespace VEF.Buildings;

public static class GlowerUtility
{
	public static bool IsDarklight(Thing thing)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		CompGlower val = ThingCompUtility.TryGetComp<CompGlower>(thing);
		if (val != null)
		{
			ColorInt glowColor = val.GlowColor;
			return DarklightUtility.IsDarklight(Color32.op_Implicit(((ColorInt)(ref glowColor)).ProjectToColor32()));
		}
		return false;
	}
}
