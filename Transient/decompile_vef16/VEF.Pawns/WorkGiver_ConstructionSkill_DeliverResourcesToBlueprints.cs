using RimWorld;
using VEF.Things;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

public class WorkGiver_ConstructionSkill_DeliverResourcesToBlueprints : WorkGiver_ConstructDeliverResourcesToBlueprints
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
		return ((WorkGiver_ConstructDeliverResourcesToBlueprints)this).HasJobOnThing(pawn, t, forced);
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
		ThingDefExtension thingDefExtension = (ThingDefExtension)obj;
		if (thingDefExtension?.constructionSkillRequirement == null)
		{
			return null;
		}
		Job val = ((WorkGiver_ConstructDeliverResourcesToBlueprints)this).JobOnThing(pawn, t, forced);
		if (val != null && val.def == JobDefOf.PlaceNoCostFrame && !GenText.NullOrEmpty(thingDefExtension.constructionSkillRequirement.reportStringOverride))
		{
			val.reportStringOverride = thingDefExtension.constructionSkillRequirement.reportStringOverride;
		}
		return val;
	}
}
