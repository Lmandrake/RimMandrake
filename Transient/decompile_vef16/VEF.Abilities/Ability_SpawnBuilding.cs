using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Abilities;

public class Ability_SpawnBuilding : Ability
{
	public override bool CanAutoCast => false;

	public override void Cast(params GlobalTargetInfo[] targets)
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets);
		AbilityExtension_Building modExtension = ((Def)def).GetModExtension<AbilityExtension_Building>();
		if (modExtension.building == null)
		{
			return;
		}
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			Thing obj = GenSpawn.Spawn(modExtension.building, ((GlobalTargetInfo)(ref val)).Cell, ((Thing)pawn).Map, (WipeMode)0);
			obj.SetFactionDirect(((Thing)pawn).Faction);
			CompSpawnedBuilding compSpawnedBuilding = ThingCompUtility.TryGetComp<CompSpawnedBuilding>(obj);
			if (compSpawnedBuilding != null)
			{
				compSpawnedBuilding.lastDamageTick = Find.TickManager.TicksGame;
				compSpawnedBuilding.damagePerTick = Mathf.RoundToInt(GetPowerForPawn());
				int durationForPawn = GetDurationForPawn();
				if (durationForPawn > 0)
				{
					compSpawnedBuilding.finalTick = compSpawnedBuilding.lastDamageTick + durationForPawn;
				}
			}
		}
	}

	public override bool CanHitTarget(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		if (base.CanHitTarget(target))
		{
			return GridsUtility.GetFirstBuilding(((LocalTargetInfo)(ref target)).Cell, ((Thing)pawn).Map) == null;
		}
		return false;
	}
}
