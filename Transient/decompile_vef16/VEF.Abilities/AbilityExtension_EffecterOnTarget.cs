using System.Collections.Generic;
using System.Linq;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_EffecterOnTarget : AbilityExtension_AbilityMod
{
	public bool onCaster;

	public EffecterDef effecterDef;

	public int maintainForTicks = -1;

	public float scale = 1f;

	public bool maintainForDuration;

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets, ability);
		Effecter val = null;
		IntVec3 val2;
		if (onCaster)
		{
			val2 = ((Thing)ability.pawn).Position;
			val = effecterDef.Spawn(val2, ((Thing)ability.pawn).Map, scale);
		}
		else
		{
			GlobalTargetInfo val3 = targets.First();
			val2 = ((GlobalTargetInfo)(ref val3)).Cell;
			val3 = targets.First();
			Effecter obj2;
			if (((GlobalTargetInfo)(ref val3)).HasThing)
			{
				EffecterDef obj = effecterDef;
				val3 = targets.First();
				obj2 = obj.Spawn(((GlobalTargetInfo)(ref val3)).Thing, ((Thing)ability.pawn).Map, scale);
			}
			else
			{
				obj2 = effecterDef.Spawn(val2, ((Thing)ability.pawn).Map, scale);
			}
			val = obj2;
		}
		if (maintainForDuration)
		{
			ability.AddEffecterToMaintain(val, val2, ability.GetDurationForPawn());
		}
		else if (maintainForTicks > 0)
		{
			ability.AddEffecterToMaintain(val, val2, maintainForTicks);
		}
		else
		{
			val.Cleanup();
		}
	}

	public override IEnumerable<string> ConfigErrors()
	{
		if (maintainForTicks > 0 && !abilityDef.needsTicking)
		{
			yield return ((Def)abilityDef).defName + " has AbilityExtension_EffecterOnTarget mod extension with maintainForTicks set to " + maintainForTicks + " but doesn't have needsTicking set to true. It will not work without ticking.";
		}
	}
}
