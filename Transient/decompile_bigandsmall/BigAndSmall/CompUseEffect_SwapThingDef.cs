using System;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompUseEffect_SwapThingDef : CompTargetEffect
{
	public CompProperties_SwapThingDef Props => (CompProperties_SwapThingDef)(object)((ThingComp)this).props;

	public override void DoEffectOn(Pawn _, Thing target)
	{
		Pawn val = (Pawn)(object)((target is Pawn) ? target : null);
		if (val == null)
		{
			return;
		}
		if (Props.sapientVersion)
		{
			if (HumanlikeAnimalGenerator.reverseLookupHumanlikeAnimals.ContainsKey(target.def))
			{
				val.SwapAnimalToSapientVersion();
			}
			else
			{
				Log.Warning($"Tried to swap {val.Name} to a sapient version, but no sapient version found for {((Def)target.def).defName}.");
			}
			return;
		}
		if (target != null)
		{
			val.SwapThingDef(Props.target, state: true, 999999, force: true);
			return;
		}
		throw new ArgumentNullException("target", "No valid swap target specified.");
	}
}
