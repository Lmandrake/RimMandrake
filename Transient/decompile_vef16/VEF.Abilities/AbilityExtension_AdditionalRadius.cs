using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_AdditionalRadius : AbilityExtension_AbilityMod
{
	public float radius;

	public List<StatModifier> radiusStatFactors = new List<StatModifier>();

	public float GetRadiusFor(Pawn pawn)
	{
		return radiusStatFactors.Aggregate(radius, (float current, StatModifier statFactor) => current * (StatExtension.GetStatValue((Thing)(object)pawn, statFactor.stat, true, -1) * statFactor.value));
	}

	public override void GizmoUpdateOnMouseover(Ability ability)
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		base.GizmoUpdateOnMouseover(ability);
		float radiusFor = GetRadiusFor(ability.pawn);
		GenDraw.DrawRadiusRing(((Thing)ability.pawn).Position, radiusFor);
	}
}
