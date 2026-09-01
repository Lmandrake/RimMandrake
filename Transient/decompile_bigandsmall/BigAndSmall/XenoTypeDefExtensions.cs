using System;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class XenoTypeDefExtensions
{
	public static XenotypeIconDef TryFindIconDef(Pawn parent)
	{
		string iconPath = parent.genes.Xenotype.iconPath;
		return GenCollection.FirstOrDefault<XenotypeIconDef>(DefDatabase<XenotypeIconDef>.AllDefsListForReading, (Predicate<XenotypeIconDef>)((XenotypeIconDef x) => string.Equals(x.texPath, iconPath, StringComparison.OrdinalIgnoreCase)));
	}

	public static float GetMorphWeight(this XenotypeDef def)
	{
		if (((Def)def).HasModExtension<XenotypeExtension>())
		{
			return ((Def)def).GetModExtension<XenotypeExtension>().morphWeight;
		}
		return 1f;
	}

	public static (ThingDef thing, bool force) GetForcedRace(this XenotypeDef def)
	{
		if (((Def)def).HasModExtension<XenotypeExtension>())
		{
			return (thing: ((Def)def).GetModExtension<XenotypeExtension>().setRace, force: ((Def)def).GetModExtension<XenotypeExtension>().forceRace);
		}
		return (thing: null, force: false);
	}

	public static bool TrySwapToXenotypeThingDef(this Pawn pawn)
	{
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.Xenotype : null);
		}
		XenotypeDef val = (XenotypeDef)obj;
		if (val != null)
		{
			(ThingDef, bool) forcedRace = val.GetForcedRace();
			var (val2, _) = forcedRace;
			if (val2 != null)
			{
				bool item = forcedRace.Item2;
				try
				{
					pawn.SwapThingDef(val2, state: true, 0, item);
					return true;
				}
				catch (Exception ex)
				{
					Log.Error($"Error while trying to swap {pawn.Name} to {((Def)val2).defName} during GenerateGenes step:\n{ex.Message}\n{ex.StackTrace}");
				}
			}
		}
		return false;
	}
}
