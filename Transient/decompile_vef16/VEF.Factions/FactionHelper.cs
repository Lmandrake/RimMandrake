using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Factions;

public static class FactionHelper
{
	public static Color? FactionOrIdeoColor(this Faction faction)
	{
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		if (ModsConfig.IdeologyActive)
		{
			Color? obj;
			if (faction == null)
			{
				obj = null;
			}
			else
			{
				FactionIdeosTracker ideos = faction.ideos;
				if (ideos == null)
				{
					obj = null;
				}
				else
				{
					Ideo primaryIdeo = ideos.PrimaryIdeo;
					obj = ((primaryIdeo != null) ? new Color?(primaryIdeo.Color) : ((Color?)null));
				}
			}
			Color? val = obj;
			if (val.HasValue)
			{
				return val.GetValueOrDefault();
			}
		}
		return (faction != null) ? new Color?(faction.Color) : ((Color?)null);
	}
}
