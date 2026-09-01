using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.Apparels;
using Verse;

namespace VEF.Hediffs;

[StaticConstructorOnStartup]
public class HediffComp_Spreadable : HediffComp
{
	private static readonly Vector3 BreathOffset = new Vector3(0f, 0f, -0.04f);

	public int nextSpreadingTick;

	public int nextFleckSpawnTick;

	public HediffCompProperties_Spreadable Props => base.props as HediffCompProperties_Spreadable;

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		((HediffComp)this).CompPostPostAdd(dinfo);
		nextSpreadingTick = Find.TickManager.TicksGame + ((IntRange)(ref Props.spreadingTickInterval)).RandomInRange;
		nextFleckSpawnTick = Find.TickManager.TicksGame + ((IntRange)(ref Props.fleckSpawnInterval)).RandomInRange;
	}

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (Props.fleckDefOnPawn != null && Find.TickManager.TicksGame >= nextFleckSpawnTick && ((Thing)((HediffComp)this).Pawn).Map != null)
		{
			Pawn pawn = ((HediffComp)this).Pawn;
			Vector3 val = pawn.Drawer.DrawPos + pawn.Drawer.renderer.BaseHeadOffsetAt(((Thing)pawn).Rotation);
			Rot4 rotation = ((Thing)pawn).Rotation;
			IntVec3 facingCell = ((Rot4)(ref rotation)).FacingCell;
			Vector3 loc = val + ((IntVec3)(ref facingCell)).ToVector3() * 0.21f + BreathOffset;
			Map map = ((Thing)pawn).Map;
			rotation = ((Thing)pawn).Rotation;
			ThrowFleck(loc, map, ((Rot4)(ref rotation)).AsAngle, pawn.Drawer.tweener.LastTickTweenedVelocity);
			nextFleckSpawnTick = Find.TickManager.TicksGame + ((IntRange)(ref Props.fleckSpawnInterval)).RandomInRange;
		}
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Find.TickManager.TicksGame < nextSpreadingTick)
		{
			return;
		}
		if (((Thing)((HediffComp)this).Pawn).Map != null)
		{
			foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)((HediffComp)this).Pawn).Position, ((Thing)((HediffComp)this).Pawn).Map, Props.radiusToSpread, true))
			{
				Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
				if (val != null && val != ((HediffComp)this).Pawn && (!Props.requiresLineOfSightToSpread || GenSight.LineOfSight(((Thing)((HediffComp)this).Pawn).Position, ((Thing)val).Position, ((Thing)val).Map)))
				{
					TrySpreadDiseaseOn(val);
				}
			}
		}
		else
		{
			Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)((HediffComp)this).Pawn);
			if (caravan != null)
			{
				foreach (Pawn item2 in caravan.PawnsListForReading)
				{
					TrySpreadDiseaseOn(item2);
				}
			}
		}
		nextSpreadingTick = Find.TickManager.TicksGame + ((IntRange)(ref Props.spreadingTickInterval)).RandomInRange;
	}

	public void TrySpreadDiseaseOn(Pawn pawn)
	{
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		if (CanCatchDisease(pawn) && Rand.Chance(Props.baseDiseaseContractChance))
		{
			if (pawn.health.hediffSet.GetFirstHediffOfDef(((HediffComp)this).Def, false) == null && !GenText.NullOrEmpty(Props.spreadingMessageWarningKey))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.spreadingMessageWarningKey, NamedArgumentUtility.Named((object)pawn, "PAWN"))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.NegativeHealthEvent, true);
			}
			HealthUtility.AdjustSeverity(pawn, ((HediffComp)this).Def, Props.severityToInfect);
		}
	}

	private bool CanCatchDisease(Pawn pawn)
	{
		if ((Props.speciesCanCatch == null || RaceCanCatchDisease(pawn)) && pawn.health.immunity.DiseaseContractChanceFactor(((HediffComp)this).Def, (BodyPartRecord)null) > 0.001f && (Props.apparelsPreventingSpreading == null || !GenCollection.Any<ThingDef>(Props.apparelsPreventingSpreading, (Predicate<ThingDef>)((ThingDef x) => pawn.WearsApparel(x)))))
		{
			if (Props.statsPreventingSpreading != null)
			{
				return GenCollection.Any<StatModifier>(Props.statsPreventingSpreading, (Predicate<StatModifier>)((StatModifier x) => StatExtension.GetStatValue((Thing)(object)pawn, x.stat, true, -1) <= x.value));
			}
			return true;
		}
		return false;
	}

	private bool RaceCanCatchDisease(Pawn pawn)
	{
		using (List<RaceCategory>.Enumerator enumerator = Props.speciesCanCatch.GetEnumerator())
		{
			while (enumerator.MoveNext())
			{
				switch (enumerator.Current)
				{
				case RaceCategory.Humanlike:
					if (pawn.RaceProps.Humanlike)
					{
						return true;
					}
					break;
				case RaceCategory.Animal:
					if (pawn.RaceProps.Animal)
					{
						return true;
					}
					break;
				case RaceCategory.Mechanoid:
					if (pawn.RaceProps.IsMechanoid)
					{
						return true;
					}
					break;
				case RaceCategory.Insect:
					if (pawn.RaceProps.Insect)
					{
						return true;
					}
					break;
				}
			}
		}
		return false;
	}

	public void ThrowFleck(Vector3 loc, Map map, float throwAngle, Vector3 inheritVelocity)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		if (GenView.ShouldSpawnMotesAt(IntVec3Utility.ToIntVec3(loc), map, true))
		{
			FleckCreationData dataStatic = FleckMaker.GetDataStatic(loc + new Vector3(Rand.Range(-0.005f, 0.005f), 0f, Rand.Range(-0.005f, 0.005f)), map, Props.fleckDefOnPawn, Rand.Range(0.6f, 0.7f));
			dataStatic.rotationRate = Rand.RangeInclusive(-240, 240);
			dataStatic.velocityAngle = throwAngle + (float)Rand.Range(-10, 10);
			dataStatic.velocitySpeed = Rand.Range(0.1f, 0.8f);
			dataStatic.velocity = inheritVelocity * 0.5f;
			dataStatic.instanceColor = Props.fleckColor;
			dataStatic.scale = Props.fleckScale;
			map.flecks.CreateFleck(dataStatic);
		}
	}

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<int>(ref nextSpreadingTick, "nextSpreadingTick", 0, false);
		Scribe_Values.Look<int>(ref nextFleckSpawnTick, "nextFleckSpawnTick", 0, false);
	}
}
