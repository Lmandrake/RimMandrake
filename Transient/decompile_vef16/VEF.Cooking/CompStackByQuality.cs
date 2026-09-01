using RimWorld;
using Verse;

namespace VEF.Cooking;

public class CompStackByQuality : ThingComp
{
	public override bool AllowStackWith(Thing other)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		CompQuality val = ((ThingWithComps)(((other is ThingWithComps) ? other : null)?)).compQuality;
		if (val != null)
		{
			QualityCategory quality = val.Quality;
			QualityCategory quality2 = base.parent.compQuality.Quality;
			if (quality != quality2)
			{
				return false;
			}
		}
		return ((ThingComp)this).AllowStackWith(other);
	}
}
