using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class RecipeExtension : DefModExtension
{
	public bool? isSurgery;

	public PawnKindDef pawnKindDef;

	public GeneratedRecipeUser conditionalRecipe;

	public bool ShouldAddToRace(ThingDef thing, bool forceMechanical = false)
	{
		if (conditionalRecipe == null)
		{
			return false;
		}
		object obj;
		if (thing == null)
		{
			obj = null;
		}
		else
		{
			RaceProperties race = thing.race;
			obj = ((race != null) ? race.FleshType : null);
		}
		FleshTypeDef val = (FleshTypeDef)obj;
		if (val == null)
		{
			return false;
		}
		if (forceMechanical)
		{
			val = FleshTypeDefOf.Mechanoid;
		}
		GeneratedRecipeUser generatedRecipeUser = conditionalRecipe;
		if (thing.IsCorpse && !generatedRecipeUser.addToCorpses)
		{
			return false;
		}
		if (!thing.IsCorpse && !generatedRecipeUser.addToLivingThing)
		{
			return false;
		}
		if (generatedRecipeUser?.overrideRecipeUsers != null && !generatedRecipeUser.overrideRecipeUsers.Contains(thing))
		{
			return false;
		}
		if (GenList.NullOrEmpty<FleshTypeDef>((IList<FleshTypeDef>)generatedRecipeUser.validfleshTypes))
		{
			return true;
		}
		if (generatedRecipeUser.validfleshTypes.Contains(FleshTypeDefOf.Mechanoid))
		{
			object obj2;
			if (thing == null)
			{
				obj2 = null;
			}
			else
			{
				RaceProperties race2 = thing.race;
				obj2 = ((race2 != null) ? race2.BloodDef : null);
			}
			if (obj2 == BSDefs.Filth_MachineBits)
			{
				goto IL_00e6;
			}
			if (thing != null)
			{
				RaceProperties race3 = thing.race;
				if (((race3 != null) ? new bool?(race3.IsMechanoid) : ((bool?)null)) == true)
				{
					goto IL_00e6;
				}
			}
		}
		if (generatedRecipeUser.validfleshTypes.Contains(val))
		{
			return true;
		}
		return false;
		IL_00e6:
		return true;
	}
}
