using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

internal class CompSpawnPawnsOnMissingBodyPart : ThingComp
{
	public int existingMissingBodyParts;

	public CompProperties_SpawnPawnsOnMissingBodyPart Props => (CompProperties_SpawnPawnsOnMissingBodyPart)(object)base.props;

	public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
	{
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_0192: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_020c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0218: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val == null || val.Dead)
		{
			return;
		}
		List<BodyPartRecord> allParts = ((Thing)val).def.race.body.AllParts;
		List<Hediff> hediffs = val.health.hediffSet.hediffs;
		int num = 0;
		for (int i = 0; i < hediffs.Count; i++)
		{
			Hediff obj = hediffs[i];
			Hediff_MissingPart val2 = (Hediff_MissingPart)(object)((obj is Hediff_MissingPart) ? obj : null);
			if (val2 != null && allParts.Contains(((Hediff)val2).Part))
			{
				num++;
			}
		}
		if (num > existingMissingBodyParts)
		{
			existingMissingBodyParts = num;
			for (int j = 0; j < Props.pawnKindOptions.Count; j++)
			{
				PawnKindDef obj2 = Props.pawnKindOptions[j];
				Faction faction = ((Thing)val).Faction;
				float? num2 = 2f;
				float? num3 = num2;
				Pawn child = PawnGenerator.GeneratePawn(new PawnGenerationRequest(obj2, faction, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, num3, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
				SpawnPawn(child, val, ((Thing)val).PositionHeld, ((Thing)val).MapHeld, val.lord);
			}
			IntVec3 val3 = default(IntVec3);
			for (int k = 0; k < ((IntRange)(ref Props.filthCountRange)).RandomInRange; k++)
			{
				CellFinder.TryFindRandomReachableNearbyCell(((Thing)val).PositionHeld, ((Thing)val).MapHeld, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val3, 999999);
				FilthMaker.TryMakeFilth(val3, ((Thing)val).MapHeld, Props.filthCreated, 1, (FilthSourceFlags)0, true);
			}
			if (Props.sound != null)
			{
				SoundStarter.PlayOneShot(Props.sound, SoundInfo.op_Implicit(new TargetInfo(((Thing)val).PositionHeld, ((Thing)val).MapHeld, false)));
			}
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref existingMissingBodyParts, "existingMissingBodyParts", 0, false);
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
