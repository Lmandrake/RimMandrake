using System.Collections.Generic;
using System.Linq;
using VEF.CacheClearing;
using Verse;

namespace VEF.Hediffs;

[StaticConstructorOnStartup]
public static class PhasingUtils
{
	public static HashSet<Pawn> PhasingPawns;

	static PhasingUtils()
	{
		PhasingPawns = new HashSet<Pawn>();
		ClearCaches.ClearCache();
	}

	public static bool IsPhasing(this Pawn p)
	{
		return PhasingPawns.Contains(p);
	}

	public static bool IsPhasingSlow(this Pawn p)
	{
		return p.health.hediffSet.GetAllComps().OfType<HediffComp_Phasing>().Any();
	}
}
