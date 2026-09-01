using RimWorld;
using Verse;

namespace VEF.Abilities;

public class TargetingParametersForAoE : TargetingParameters
{
	public bool mustBeSameFaction;

	public bool canTargetBlockedLocations = true;

	public bool ignoreRangeAndSight;

	public bool CanTarget(TargetInfo target, Ability ability)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		if (((TargetingParameters)this).CanTarget(target, (ITargetingSource)(object)ability) && (!mustBeSameFaction || (((TargetInfo)(ref target)).HasThing && ((TargetInfo)(ref target)).Thing.Faction == ((Thing)ability.pawn).Faction)))
		{
			if (!canTargetBlockedLocations)
			{
				return !GridsUtility.Filled(((TargetInfo)(ref target)).Cell, ((TargetInfo)(ref target)).Map);
			}
			return true;
		}
		return false;
	}
}
