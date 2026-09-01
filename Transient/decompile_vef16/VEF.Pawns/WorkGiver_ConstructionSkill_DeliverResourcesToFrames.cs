using RimWorld;
using VEF.Things;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

public class WorkGiver_ConstructionSkill_DeliverResourcesToFrames : WorkGiver_ConstructDeliverResourcesToFrames
{
	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		ThingDef def = t.def;
		object obj;
		if (def == null)
		{
			obj = null;
		}
		else
		{
			BuildableDef entityDefToBuild = def.entityDefToBuild;
			obj = ((entityDefToBuild != null) ? ((Def)entityDefToBuild).GetModExtension<ThingDefExtension>() : null);
		}
		if (((ThingDefExtension)obj)?.constructionSkillRequirement == null)
		{
			return false;
		}
		return ((WorkGiver_ConstructDeliverResourcesToFrames)this).HasJobOnThing(pawn, t, forced);
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		ThingDef def = t.def;
		object obj;
		if (def == null)
		{
			obj = null;
		}
		else
		{
			BuildableDef entityDefToBuild = def.entityDefToBuild;
			obj = ((entityDefToBuild != null) ? ((Def)entityDefToBuild).GetModExtension<ThingDefExtension>() : null);
		}
		if (((ThingDefExtension)obj)?.constructionSkillRequirement == null)
		{
			return null;
		}
		return ((WorkGiver_ConstructDeliverResourcesToFrames)this).JobOnThing(pawn, t, forced);
	}
}
