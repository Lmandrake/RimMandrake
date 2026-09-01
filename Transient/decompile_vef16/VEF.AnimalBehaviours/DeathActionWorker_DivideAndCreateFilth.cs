using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class DeathActionWorker_DivideAndCreateFilth : DeathActionWorker
{
	public DeathActionProperties_DivideAndCreateFilth Props => (DeathActionProperties_DivideAndCreateFilth)(object)base.props;

	public override void PawnDied(Corpse corpse, Lord prevLord)
	{
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_0118: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		Pawn innerPawn = corpse.InnerPawn;
		if (innerPawn != null)
		{
			for (int i = 0; i < Props.dividePawnKindOptions.Count; i++)
			{
				PawnKindDef obj = Props.dividePawnKindOptions[i];
				Faction faction = ((Thing)corpse.InnerPawn).Faction;
				float? num = 0f;
				float? num2 = num;
				Pawn child = PawnGenerator.GeneratePawn(new PawnGenerationRequest(obj, faction, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, num2, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
				SpawnPawn(child, innerPawn, ((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld, prevLord);
			}
			IntVec3 val = default(IntVec3);
			for (int j = 0; j < ((IntRange)(ref Props.filthCountRange)).RandomInRange; j++)
			{
				CellFinder.TryFindRandomReachableNearbyCell(((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val, 999999);
				FilthMaker.TryMakeFilth(val, ((Thing)corpse).MapHeld, Props.filthCreated, 1, (FilthSourceFlags)0, true);
			}
			if (Props.sound != null)
			{
				SoundStarter.PlayOneShot(Props.sound, SoundInfo.op_Implicit(new TargetInfo(((Thing)corpse).PositionHeld, ((Thing)corpse).MapHeld, false)));
			}
			((Thing)corpse).Destroy((DestroyMode)0);
		}
	}

	private void SpawnPawn(Pawn child, Pawn parent, IntVec3 position, Map map, Lord lord)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		GenSpawn.Spawn((Thing)(object)child, position, map, (WipeMode)2);
		if (lord != null)
		{
			lord.AddPawn(child);
		}
		FleshbeastUtility.SpawnPawnAsFlyer(child, map, position, 5, true);
	}
}
