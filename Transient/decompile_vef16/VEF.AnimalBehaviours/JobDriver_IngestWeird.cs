using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobDriver_IngestWeird : JobDriver, IEatingDriver
{
	private Toil chewing;

	public const float EatCorpseBodyPartsUntilFoodLevelPct = 0.9f;

	public const TargetIndex IngestibleSourceInd = 1;

	private const TargetIndex TableCellInd = 2;

	private const TargetIndex ExtraIngestiblesToCollectInd = 3;

	private Thing IngestibleSource
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	private float ChewDurationMultiplier => 1f;

	public bool GainingNutritionNow
	{
		get
		{
			if (!ThingUtility.DestroyedOrNull(IngestibleSource))
			{
				return ((JobDriver)this).CurToil == chewing;
			}
			return false;
		}
	}

	public override void ExposeData()
	{
		((JobDriver)this).ExposeData();
	}

	public override string GetReport()
	{
		return ((JobDriver)this).GetReport();
	}

	public override void Notify_Starting()
	{
		((JobDriver)this).Notify_Starting();
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)base.pawn).Faction != null)
		{
			Thing ingestibleSource = IngestibleSource;
			if (!ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(ingestibleSource), base.job, 10, 1, (ReservationLayerDef)null, errorOnFailed, false))
			{
				return false;
			}
		}
		return true;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		CompEatWeirdFood comp = ThingCompUtility.TryGetComp<CompEatWeirdFood>((Thing)(object)base.pawn);
		if (comp == null)
		{
			yield break;
		}
		ToilFailConditions.FailOn<JobDriver_IngestWeird>(this, (Func<bool>)(() => IngestibleSource.Destroyed));
		chewing = ToilFailConditions.FailOnCannotTouch<Toil>(ToilFailConditions.FailOn(ChewAnything(base.pawn, 1f, (TargetIndex)1, (TargetIndex)2), (Func<Toil, bool>)((Toil x) => !IngestibleSource.Spawned && (base.pawn.carryTracker == null || base.pawn.carryTracker.CarriedThing != IngestibleSource))), (TargetIndex)1, (PathEndMode)2);
		foreach (Toil item in PrepareToIngestToils(chewing))
		{
			yield return item;
		}
		yield return chewing;
		yield return FinalizeIngestAnything(base.pawn, (TargetIndex)1, comp);
		yield return Toils_Jump.JumpIf(chewing, (Func<bool>)delegate
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			if (((LocalTargetInfo)(ref target)).Thing is Corpse)
			{
				Pawn_NeedsTracker needs = base.pawn.needs;
				if (needs == null)
				{
					return false;
				}
				Need_Food food = needs.food;
				return ((food != null) ? new float?(((Need)food).CurLevelPercentage) : ((float?)null)) < 0.9f;
			}
			return false;
		});
	}

	private IEnumerable<Toil> PrepareToIngestToils(Toil chewToil)
	{
		return PrepareToIngestToils_NonToolUser();
	}

	private IEnumerable<Toil> PrepareToIngestToils_NonToolUser()
	{
		yield return ReserveFood();
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
	}

	private Toil ReserveFood()
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		Toil obj = ToilMaker.MakeToil("ReserveFood");
		obj.initAction = delegate
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			if (!ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(thing), base.job, 10, 1, (ReservationLayerDef)null, true, false))
			{
				Log.Error(string.Concat("Pawn food reservation for ", base.pawn, " on job ", this, " failed, because it could not register food from ", thing, " - amount: ", 1));
				base.pawn.jobs.EndCurrentJob((JobCondition)64, true, true);
			}
			base.job.count = 1;
		};
		obj.defaultCompleteMode = (ToilCompleteMode)1;
		obj.atomicWithPrevious = true;
		return obj;
	}

	public static Toil ChewAnything(Pawn chewer, float durationMultiplier, TargetIndex ingestibleInd, TargetIndex eatSurfaceInd = 0)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		Toil toil = ToilMaker.MakeToil("ChewAnything");
		toil.initAction = delegate
		{
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			Pawn actor = toil.actor;
			LocalTargetInfo target = actor.CurJob.GetTarget(ingestibleInd);
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			actor.jobs.curDriver.ticksLeftThisToil = Mathf.RoundToInt(500f * durationMultiplier);
			if (thing.Spawned)
			{
				thing.Map.physicalInteractionReservationManager.Reserve(chewer, actor.CurJob, LocalTargetInfo.op_Implicit(thing));
			}
		};
		toil.tickIntervalAction = delegate(int delta)
		{
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Unknown result type (might be due to invalid IL or missing references)
			//IL_009d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_00df: Unknown result type (might be due to invalid IL or missing references)
			if (chewer != toil.actor)
			{
				toil.actor.rotationTracker.FaceCell(((Thing)chewer).Position);
			}
			else
			{
				LocalTargetInfo target2 = toil.actor.CurJob.GetTarget(ingestibleInd);
				Thing thing2 = ((LocalTargetInfo)(ref target2)).Thing;
				if (thing2 != null && thing2.Spawned)
				{
					toil.actor.rotationTracker.FaceCell(thing2.Position);
				}
				else if ((int)eatSurfaceInd != 0)
				{
					target2 = toil.actor.CurJob.GetTarget(eatSurfaceInd);
					if (((LocalTargetInfo)(ref target2)).IsValid)
					{
						Pawn_RotationTracker rotationTracker = toil.actor.rotationTracker;
						target2 = toil.actor.CurJob.GetTarget(eatSurfaceInd);
						rotationTracker.FaceCell(((LocalTargetInfo)(ref target2)).Cell);
					}
				}
			}
			PawnUtility.GainComfortFromCellIfPossible(toil.actor, delta, false);
		};
		ToilEffects.WithProgressBar(toil, ingestibleInd, (Func<float>)delegate
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target3 = toil.actor.CurJob.GetTarget(ingestibleInd);
			return (((LocalTargetInfo)(ref target3)).Thing == null) ? 1f : (1f - (float)toil.actor.jobs.curDriver.ticksLeftThisToil / Mathf.Round(500f * durationMultiplier));
		}, false, -0.5f, false);
		toil.defaultCompleteMode = (ToilCompleteMode)3;
		ToilFailConditions.FailOnDestroyedOrNull<Toil>(toil, ingestibleInd);
		toil.AddFinishAction((Action)delegate
		{
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			if (chewer != null && chewer.CurJob != null)
			{
				LocalTargetInfo target4 = chewer.CurJob.GetTarget(ingestibleInd);
				Thing thing3 = ((LocalTargetInfo)(ref target4)).Thing;
				if (thing3 != null && ((Thing)chewer).Map.physicalInteractionReservationManager.IsReservedBy(chewer, LocalTargetInfo.op_Implicit(thing3)))
				{
					((Thing)chewer).Map.physicalInteractionReservationManager.Release(chewer, toil.actor.CurJob, LocalTargetInfo.op_Implicit(thing3));
				}
			}
		});
		toil.handlingFacing = true;
		return toil;
	}

	public static Toil FinalizeIngestAnything(Pawn ingester, TargetIndex ingestibleInd, CompEatWeirdFood comp)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		Toil toil = ToilMaker.MakeToil("FinalizeIngestAnything");
		toil.initAction = delegate
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
			//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_01c3: Unknown result type (might be due to invalid IL or missing references)
			//IL_01c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_0428: Unknown result type (might be due to invalid IL or missing references)
			//IL_04af: Unknown result type (might be due to invalid IL or missing references)
			//IL_0317: Unknown result type (might be due to invalid IL or missing references)
			//IL_039e: Unknown result type (might be due to invalid IL or missing references)
			//IL_03d0: Unknown result type (might be due to invalid IL or missing references)
			//IL_0560: Unknown result type (might be due to invalid IL or missing references)
			Pawn actor = toil.actor;
			LocalTargetInfo target = actor.jobs.curJob.GetTarget(ingestibleInd);
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			float num = comp.Props.nutrition;
			if (comp.Props.areFoodSourcesPlants)
			{
				Plant val = (Plant)(object)((thing is Plant) ? thing : null);
				if (val != null)
				{
					num *= val.Growth;
				}
			}
			if (comp.Props.fullyDestroyThing)
			{
				if (comp.Props.drainBattery)
				{
					Building_Battery val2 = (Building_Battery)(object)((thing is Building_Battery) ? thing : null);
					if (val2 != null)
					{
						CompPowerBattery obj = ThingCompUtility.TryGetComp<CompPowerBattery>((Thing)(object)val2);
						obj.SetStoredEnergyPct(obj.StoredEnergyPct - comp.Props.percentageDrain);
					}
					else
					{
						thing.Destroy((DestroyMode)0);
					}
				}
				else
				{
					thing.Destroy((DestroyMode)0);
				}
			}
			else
			{
				if (thing.def.useHitPoints && !comp.Props.ignoreUseHitPoints)
				{
					thing.HitPoints -= (int)((float)thing.MaxHitPoints * comp.Props.percentageOfDestruction);
					if (thing.HitPoints <= 0)
					{
						thing.Destroy((DestroyMode)0);
					}
				}
				else
				{
					int num2 = (int)(comp.Props.percentageOfDestruction * (float)thing.def.stackLimit);
					thing.stackCount -= num2;
					if (thing.stackCount < 10)
					{
						thing.Destroy((DestroyMode)0);
					}
				}
				if (((Def)((Thing)actor).def).defName == "AA_AngelMoth" && ((Thing)actor).Faction == Faction.OfPlayer)
				{
					Thing obj2 = ((thing is ThingWithComps) ? thing : null);
					if (obj2 != null)
					{
						CompQuality compQuality = ((ThingWithComps)obj2).compQuality;
						if (((compQuality != null) ? new QualityCategory?(compQuality.Quality) : ((QualityCategory?)null)) == (QualityCategory?)6)
						{
							actor.health.AddHediff(HediffDef.Named("AA_AteFinestClothes"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
						}
					}
				}
			}
			if (comp.Props.hediffWhenEaten != "")
			{
				actor.health.AddHediff(HediffDef.Named(comp.Props.hediffWhenEaten), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			if (comp.Props.advanceLifeStage && ((Thing)actor).Map != null)
			{
				comp.currentFeedings++;
				if (comp.currentFeedings >= comp.Props.advanceAfterXFeedings && (!ModsConfig.OdysseyActive || !actor.training.HasLearned(InternalDefOf.VEF_CycleSeverance)))
				{
					if (comp.Props.fissionAfterXFeedings)
					{
						if (!comp.Props.fissionOnlyIfTamed || (((Thing)actor).Faction != null && ((Thing)actor).Faction.IsPlayer))
						{
							for (int i = 0; i < comp.Props.numberOfOffspring; i++)
							{
								Pawn obj3 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(comp.Props.defToFissionTo), ((Thing)actor).Faction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), true, true, false, false, true, 1f, false, false, true, true, false, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
								obj3.playerSettings.AreaRestrictionInPawnCurrentMap = actor.playerSettings.AreaRestrictionInPawnCurrentMap;
								obj3.relations.AddDirectRelation(PawnRelationDefOf.Parent, actor);
								GenSpawn.Spawn((Thing)(object)obj3, ((Thing)actor).Position, ((Thing)actor).Map, (WipeMode)0);
							}
							((Thing)actor).Destroy((DestroyMode)0);
						}
					}
					else
					{
						Pawn val3 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(comp.Props.defToAdvanceTo), ((Thing)actor).Faction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), true, true, false, false, true, 1f, false, false, true, true, false, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
						if (actor.Name != null && !GenText.UncapitalizeFirst(((object)actor.Name).ToString()).Contains(((Def)((Thing)actor).def).label))
						{
							val3.Name = actor.Name;
						}
						if (actor.training != null)
						{
							val3.training = actor.training;
						}
						if (actor.health != null)
						{
							val3.health = actor.health;
						}
						if (actor.foodRestriction != null)
						{
							val3.foodRestriction = actor.foodRestriction;
						}
						if (actor.playerSettings != null && actor.playerSettings.AreaRestrictionInPawnCurrentMap != null)
						{
							val3.playerSettings.AreaRestrictionInPawnCurrentMap = actor.playerSettings.AreaRestrictionInPawnCurrentMap;
						}
						GenSpawn.Spawn((Thing)(object)val3, ((Thing)actor).Position, ((Thing)actor).Map, (WipeMode)0);
						((Thing)actor).Destroy((DestroyMode)0);
					}
				}
			}
			if (!ingester.Dead)
			{
				Need_Food food = ingester.needs.food;
				((Need)food).CurLevel = ((Need)food).CurLevel + num;
			}
			ingester.records.AddTo(RecordDefOf.NutritionEaten, num);
		};
		toil.defaultCompleteMode = (ToilCompleteMode)1;
		return toil;
	}
}
