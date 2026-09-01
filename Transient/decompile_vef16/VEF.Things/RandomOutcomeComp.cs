using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Things;

public class RandomOutcomeComp : ThingComp
{
	public CompProperties_RandomOutcomeComp Props => (CompProperties_RandomOutcomeComp)(object)base.props;

	public Thing RandomWeapons()
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		ThingStuffPair val = GenCollection.RandomElement<ThingStuffPair>((IEnumerable<ThingStuffPair>)ThingStuffPair.AllWith((Predicate<ThingDef>)((ThingDef td) => (int)td.equipmentType == 1 && td.weaponTags != null && td.weaponTags.Contains(Props.canProvideTags[0]))));
		return ThingMaker.MakeThing(val.thing, val.stuff);
	}

	public override void CompTick()
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTick();
		if (((Thing)base.parent).Map != null)
		{
			Thing obj = RandomWeapons();
			CompQuality val = ((ThingWithComps)(((obj is ThingWithComps) ? obj : null)?)).compQuality;
			QualityCategory val2 = default(QualityCategory);
			if (val != null && QualityUtility.TryGetQuality((Thing)(object)base.parent, ref val2))
			{
				val.SetQuality(val2, (ArtGenerationContext?)(ArtGenerationContext)1);
			}
			GenPlace.TryPlaceThing(obj, ((Thing)base.parent).Position, ((Thing)base.parent).Map, (ThingPlaceMode)0, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
	}
}
