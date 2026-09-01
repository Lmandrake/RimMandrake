using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class IngredientValueGetter_Mass : IngredientValueGetter
{
	public override float ValuePerUnitOf(ThingDef t)
	{
		if (t.BaseMass != 0f)
		{
			return t.BaseMass;
		}
		return 1f;
	}

	public override string BillRequirementsDescription(RecipeDef r, IngredientCount ing)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF_BillRequiresMass", NamedArgument.op_Implicit(ing.GetBaseCount())));
	}
}
