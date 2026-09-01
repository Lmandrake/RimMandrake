using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Factions;

public static class ExtendedFactionUtility
{
	public static Faction RandomFactionOfTechLevel(TechLevel level, bool allowHidden = false, bool allowDefeated = false, bool allowNonHumanlike = false)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		Faction result = default(Faction);
		if (GenCollection.TryRandomElement<Faction>(Find.FactionManager.AllFactions.Where((Faction f) => !f.def.isPlayer && f.def.techLevel == level && (allowHidden || !f.def.hidden) && (allowDefeated || !f.defeated) && (allowNonHumanlike || f.def.humanlikeFaction)), ref result))
		{
			return result;
		}
		return null;
	}
}
