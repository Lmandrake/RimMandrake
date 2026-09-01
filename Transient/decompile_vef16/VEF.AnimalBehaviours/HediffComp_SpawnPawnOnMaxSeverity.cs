using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_SpawnPawnOnMaxSeverity : HediffComp
{
	public HediffCompProperties_SpawnPawnOnMaxSeverity Props => base.props as HediffCompProperties_SpawnPawnOnMaxSeverity;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (((Hediff)base.parent).Severity >= 0.99f)
		{
			for (int i = 0; i < Props.pawnKindOptions.Count; i++)
			{
				PawnKindDef obj = Props.pawnKindOptions[i];
				Faction ofInsects = Faction.OfInsects;
				float? num = 0f;
				float? num2 = num;
				Pawn child = PawnGenerator.GeneratePawn(new PawnGenerationRequest(obj, ofInsects, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, num2, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
				SpawnPawn(child, ((HediffComp)this).Pawn, ((Thing)((HediffComp)this).Pawn).PositionHeld, ((Thing)((HediffComp)this).Pawn).MapHeld);
			}
			IntVec3 val = default(IntVec3);
			for (int j = 0; j < ((IntRange)(ref Props.filthCountRange)).RandomInRange; j++)
			{
				CellFinder.TryFindRandomReachableNearbyCell(((Thing)((HediffComp)this).Pawn).PositionHeld, ((Thing)((HediffComp)this).Pawn).MapHeld, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val, 999999);
				FilthMaker.TryMakeFilth(val, ((Thing)((HediffComp)this).Pawn).MapHeld, Props.filthCreated, 1, (FilthSourceFlags)0, true);
			}
			if (Props.sound != null)
			{
				SoundStarter.PlayOneShot(Props.sound, SoundInfo.op_Implicit(new TargetInfo(((Thing)((HediffComp)this).Pawn).PositionHeld, ((Thing)((HediffComp)this).Pawn).MapHeld, false)));
			}
			((Thing)((HediffComp)this).Pawn).TakeDamage(new DamageInfo(Props.damage, ((FloatRange)(ref Props.damageAmount)).RandomInRange, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
			((HediffComp)this).Pawn.health.RemoveHediff((Hediff)(object)base.parent);
		}
	}

	private void SpawnPawn(Pawn child, Pawn parent, IntVec3 position, Map map)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		GenSpawn.Spawn((Thing)(object)child, position, map, (WipeMode)2);
		FleshbeastUtility.SpawnPawnAsFlyer(child, map, position, 5, true);
	}
}
