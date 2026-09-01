using System;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace VEF.Abilities;

public class AbilityExtension_WarmupEffecter : AbilityExtension_AbilityMod
{
	public bool onCaster;

	public EffecterDef effecterDef;

	public float scale = 1f;

	public override void WarmupToil(Toil toil)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		base.WarmupToil(toil);
		Effecter effecter = null;
		TargetInfo target = TargetInfo.Invalid;
		toil.AddPreInitAction((Action)InitEffecter);
		toil.AddPreTickAction((Action)delegate
		{
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			if (effecter == null || !((TargetInfo)(ref target)).IsValid)
			{
				InitEffecter();
			}
			Effecter obj = effecter;
			if (obj != null)
			{
				obj.EffectTick(target, target);
			}
		});
		toil.AddFinishAction((Action)delegate
		{
			Effecter obj2 = effecter;
			if (obj2 != null)
			{
				obj2.Cleanup();
			}
		});
		void InitEffecter()
		{
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
			//IL_00db: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
			//IL_0091: Unknown result type (might be due to invalid IL or missing references)
			//IL_0096: Unknown result type (might be due to invalid IL or missing references)
			CompAbilities comp = ((ThingWithComps)toil.actor).GetComp<CompAbilities>();
			Ability currentlyCasting = comp.currentlyCasting;
			if (onCaster)
			{
				target = TargetInfo.op_Implicit((Thing)(object)toil.actor);
				effecter = effecterDef.Spawn(((Thing)currentlyCasting.pawn).Position, ((Thing)currentlyCasting.pawn).Map, scale);
			}
			else
			{
				GlobalTargetInfo val = comp.currentlyCastingTargets[0];
				if (((GlobalTargetInfo)(ref val)).HasThing)
				{
					target = new TargetInfo(((GlobalTargetInfo)(ref val)).Thing);
					effecter = effecterDef.Spawn(((GlobalTargetInfo)(ref val)).Thing, ((GlobalTargetInfo)(ref val)).Map, scale);
				}
				else
				{
					target = new TargetInfo(((GlobalTargetInfo)(ref val)).Cell, ((GlobalTargetInfo)(ref val)).Map, false);
					effecter = effecterDef.Spawn(((GlobalTargetInfo)(ref val)).Cell, ((GlobalTargetInfo)(ref val)).Map, scale);
				}
			}
		}
	}
}
