using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class GeneUIDrawData
{
	private static Dictionary<string, CachedTexture> cacheTexDict = new Dictionary<string, CachedTexture>();

	public int architeCost;

	public string endoBackgroundPath;

	public string xenoBackgroundPath;

	public string architeBackgroundPath;

	public string endoBackgroundPath_Mech;

	public string xenoBackgroundPath_Mech;

	public string architeBackgroundPath_Mech;

	public CachedTexture GetCachedTexture(GeneType geneType, CachedTexture fallback = null, BSCache cache = null)
	{
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Expected O, but got Unknown
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Invalid comparison between Unknown and I4
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Invalid comparison between Unknown and I4
		string text = null;
		if (cache == null)
		{
			return fallback;
		}
		if (cache != null && cache.isMechanical)
		{
			text = ((architeCost <= 0) ? (((int)geneType == 1) ? xenoBackgroundPath_Mech : endoBackgroundPath_Mech) : architeBackgroundPath_Mech);
		}
		if (text == null)
		{
			text = ((architeCost <= 0) ? (((int)geneType == 1) ? xenoBackgroundPath : endoBackgroundPath) : architeBackgroundPath);
			if (text == null)
			{
				return fallback;
			}
		}
		if (cacheTexDict.TryGetValue(text, out var value))
		{
			return value;
		}
		CachedTexture val = new CachedTexture(text);
		cacheTexDict[text] = val;
		return val;
	}
}
