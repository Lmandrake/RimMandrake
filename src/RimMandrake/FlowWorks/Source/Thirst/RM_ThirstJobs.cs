using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>Design §3: drinking a filled bottle by ANY route (the vanilla Ingest job, an administered drink, a caravan
	/// tick, a bridge-ordered drink) raises RM_Thirst by litres / 3 at the bottle's water quality. Wired by the generator onto
	/// every drinkable bottle, beside IngestionOutcomeDoer_BottleResidue (which still leaves the dirty or empty bottle).
	/// In Dbh mode it hydrates nothing (DBH reads its WaterExt) but the quality effects still apply.</summary>
	public class IngestionOutcomeDoer_RM_Hydrate : IngestionOutcomeDoer
	{
		protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
		{
			try
			{
				RM_BottledLiquidExtension ext = ingested?.def.GetModExtension<RM_BottledLiquidExtension>();
				if (pawn == null || ext?.liquid == null)
				{
					return;
				}
				float litres = RM_Volume.Litres(RM_ContainerMaterials.UnitsIn(ingested, ext.liquid, ext.size)) * Math.Max(1, ingestedCount);
				RM_ThirstUtility.Drink(pawn, ext.liquid, litres, ingested);
			}
			catch (Exception e)
			{
				Log.WarningOnce("[RimMandrake.FlowWorks] hydrate outcome failed: " + e.Message, 0x7E1A57);
			}
		}
	}

	/// <summary>Humanlikes (inserted at Humanlike_PostDuty, the tag DBH's own ConditionalThirst uses): below 0.3, drink from
	/// the best reachable source by quality, then distance: Distilled > Potable > Fouled > Toxic, Toxic only when Parched.
	/// Sources: a drinkable bottle (inventory first, then the map) through the vanilla Ingest job; a tank of the pawn's own
	/// faction; a terrain edge (setting drinkFromTerrain).</summary>
	public class JobGiver_RM_Drink : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_ThirstUtility.IsThirsty(pawn) || pawn.Downed || pawn.Map == null)
			{
				return null;
			}
			float level = RM_ThirstUtility.Level(pawn);
			Thing bottle = RM_ThirstUtility.BestBottle(pawn, level, true, out RM_WaterQuality bq, out float bd);
			Building_LiquidTank tank = RM_ThirstUtility.BestTank(pawn, level, out RM_WaterQuality tq, out float td);
			IntVec3 cell = IntVec3.Invalid;
			RM_WaterQuality cq = RM_WaterQuality.Toxic;
			float cd = float.MaxValue;
			if (RM_ThirstSettings.drinkFromTerrain
				&& RM_ThirstUtility.TryFindDrinkCell(pawn, level, out cell, out LiquidDef _, out cq))
			{
				cd = (cell - pawn.Position).LengthHorizontalSquared;
			}
			int pick = -1;   // 0 bottle, 1 tank, 2 terrain
			RM_WaterQuality pq = RM_WaterQuality.Toxic;
			float pd = float.MaxValue;
			if (bottle != null) { pick = 0; pq = bq; pd = bd; }
			if (tank != null && (pick < 0 || RM_ThirstMath.Better(tq, td, pq, pd))) { pick = 1; pq = tq; pd = td; }
			if (cell.IsValid && (pick < 0 || RM_ThirstMath.Better(cq, cd, pq, pd))) { pick = 2; }
			switch (pick)
			{
				case 0:
					Job ingest = JobMaker.MakeJob(JobDefOf.Ingest, bottle);
					ingest.count = 1;
					return ingest;
				case 1:
					return JobMaker.MakeJob(RM_ThirstDefOf.RM_DrinkFromTank, tank);
				case 2:
					return RM_ThirstUtility.TerrainJob(cell);
			}
			return null;
		}
	}

	/// <summary>Animals (Animal_PreMain), wild and tame: below 0.3, walk to the nearest drinkable terrain edge and drink.
	/// Terrain only, never bottles or tanks (OQ-5). drinkFromTerrain does not gate animals.</summary>
	public class JobGiver_RM_AnimalDrink : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (pawn.RaceProps.Humanlike || !RM_ThirstUtility.IsThirsty(pawn) || pawn.Downed || pawn.Map == null)
			{
				return null;
			}
			if (RM_ThirstUtility.TryFindDrinkCell(pawn, RM_ThirstUtility.Level(pawn), out IntVec3 cell, out LiquidDef _, out RM_WaterQuality _))
			{
				return RM_ThirstUtility.TerrainJob(cell);
			}
			return null;
		}
	}

	/// <summary>Design §3 pack-bottles (the shape of DBH's PackWaterBottle): an idle colonist (Humanlike_PostMain) carrying
	/// fewer than 2 potable bottles takes up to 2 from the map, only while the map holds at least 4 more than that, so the
	/// stockpile is never stripped bare.</summary>
	public class JobGiver_RM_PackBottles : ThinkNode_JobGiver
	{
		public const int Want = 2;
		public const int LeaveOnMap = 4;

		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_ThirstProvider.OursLive || pawn.inventory == null || pawn.Map == null || !pawn.IsColonist
				|| RM_ThirstUtility.NeedOf(pawn) == null)
			{
				return null;
			}
			int have = 0;
			foreach (Thing t in pawn.inventory.innerContainer)
			{
				if (RM_ThirstUtility.IsDrinkableBottle(t) && (int)RM_ThirstUtility.Effective(RM_ThirstUtility.LiquidOf(t)) <= (int)RM_WaterQuality.Potable)
				{
					have += t.stackCount;
				}
			}
			if (have >= Want)
			{
				return null;
			}
			var pool = new List<Thing>();
			int onMap = 0;
			foreach (ThingDef def in RM_ThirstUtility.DrinkableBottles)
			{
				foreach (Thing t in pawn.Map.listerThings.ThingsOfDef(def))
				{
					if ((int)RM_ThirstUtility.Effective(RM_ThirstUtility.LiquidOf(t)) <= (int)RM_WaterQuality.Potable)
					{
						onMap += t.stackCount;
						pool.Add(t);
					}
				}
			}
			if (onMap < LeaveOnMap + (Want - have))
			{
				return null;
			}
			Thing take = GenClosest.ClosestThing_Global_Reachable(pawn.Position, pawn.Map, pool, PathEndMode.ClosestTouch,
				TraverseParms.For(pawn), 40f, t => !t.IsForbidden(pawn) && pawn.CanReserve(t));
			if (take == null)
			{
				return null;
			}
			Job job = JobMaker.MakeJob(JobDefOf.TakeInventory, take);
			job.count = Math.Min(Want - have, take.stackCount);
			return job;
		}
	}

	/// <summary>Stand at a drinkable terrain edge for 300 ticks, then +0.5 at the water's quality (OQ-2: slower than a bottle).
	/// The litres are debited from the pond body behind the cell like a bottle fill (a spent limited pond gives nothing).</summary>
	public class JobDriver_RM_DrinkFromTerrain : JobDriver
	{
		public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOn(() => RM_ThirstUtility.DrinkLiquidAt(Map.terrainGrid.TerrainAt(job.targetA.Cell)) == null);
			yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);
			Toil drink = Toils_General.Wait(RM_ThirstMath.TerrainDrinkTicks).WithProgressBarToilDelay(TargetIndex.A);
			drink.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			drink.initAction = () => pawn.rotationTracker.FaceCell(job.targetA.Cell);
			yield return drink;
			Toil finish = ToilMaker.MakeToil("RM_DrinkFromTerrain");
			finish.initAction = delegate
			{
				IntVec3 c = job.targetA.Cell;
				LiquidDef liquid = RM_ThirstUtility.DrinkLiquidAt(Map.terrainGrid.TerrainAt(c));
				if (liquid == null || !RM_LiquidBottleUtility.TryDebitTerrain(Map, c, RM_Volume.Units(RM_ThirstMath.TerrainDrinkLitres)))
				{
					return;
				}
				RM_ThirstUtility.Drink(pawn, liquid, RM_ThirstMath.TerrainDrinkLitres, null);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	/// <summary>Drink 1.5 L straight from a tank holding a drinkable liquid (design §3).</summary>
	public class JobDriver_RM_DrinkFromTank : JobDriver
	{
		private Building_LiquidTank Tank => job.targetA.Thing as Building_LiquidTank;

		public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
			this.FailOn(() => Tank == null || !RM_ThirstUtility.QualityOf(Tank.storedLiquid).HasValue);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			Toil drink = Toils_General.Wait(RM_ThirstMath.TankDrinkTicks).WithProgressBarToilDelay(TargetIndex.A);
			drink.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			yield return drink;
			Toil finish = ToilMaker.MakeToil("RM_DrinkFromTank");
			finish.initAction = delegate
			{
				Building_LiquidTank tank = Tank;
				LiquidDef liquid = tank?.storedLiquid;
				if (liquid == null || !tank.TryRemoveLiquid(RM_Volume.Units(RM_ThirstMath.TankDrinkLitres)))
				{
					return;
				}
				RM_ThirstUtility.Drink(pawn, liquid, RM_ThirstMath.TankDrinkLitres, null);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	/// <summary>Carry one bottle (A) to a patient or prisoner (B) and give it to them to drink: the bottle is ingested BY the
	/// patient, so every outcome doer (hydrate, quality, residue) runs exactly as for a pawn drinking it themselves.</summary>
	public class JobDriver_RM_AdministerWater : JobDriver
	{
		private const int GiveTicks = 120;

		private Pawn Patient => job.targetB.Pawn;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, 1, null, errorOnFailed)
				&& pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDestroyedNullOrForbidden(TargetIndex.A);
			this.FailOnDespawnedNullOrForbidden(TargetIndex.B);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return Toils_Haul.StartCarryThing(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch);
			Toil give = Toils_General.Wait(GiveTicks).WithProgressBarToilDelay(TargetIndex.B);
			give.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
			yield return give;
			Toil finish = ToilMaker.MakeToil("RM_AdministerWater");
			finish.initAction = delegate
			{
				Thing carried = pawn.carryTracker.CarriedThing;
				Pawn patient = Patient;
				if (carried == null || patient == null || patient.Dead || !RM_ThirstUtility.IsDrinkableBottle(carried))
				{
					return;
				}
				Thing one = carried.SplitOff(1);
				one.Ingested(patient, 0f);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}

	/// <summary>Doctor: give a bottle to a downed or bedridden humanlike (not a prisoner) below 0.3. Subclass for wardens.</summary>
	public class WorkGiver_RM_AdministerWater : WorkGiver_Scanner
	{
		protected virtual bool Prisoners => false;

		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.Pawn);

		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override bool ShouldSkip(Pawn pawn, bool forced = false) => !RM_ThirstProvider.OursLive;

		protected bool Wants(Pawn pawn, Pawn patient)
		{
			if (patient == null || patient == pawn || patient.Dead || !patient.RaceProps.Humanlike || !RM_ThirstUtility.IsThirsty(patient))
			{
				return false;
			}
			if (Prisoners)
			{
				return patient.IsPrisonerOfColony;
			}
			return !patient.IsPrisoner && (patient.Downed || patient.InBed())
				&& (patient.Faction == pawn.Faction || patient.HostFaction == pawn.Faction || patient.guest != null);
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			Pawn patient = t as Pawn;
			if (!Wants(pawn, patient) || !pawn.CanReserve(patient, 1, -1, null, forced))
			{
				return false;
			}
			return RM_ThirstUtility.BestBottle(pawn, RM_ThirstUtility.Level(patient), false, out _, out _) != null;
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			Pawn patient = t as Pawn;
			Thing bottle = RM_ThirstUtility.BestBottle(pawn, RM_ThirstUtility.Level(patient), false, out _, out _);
			if (bottle == null)
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RM_ThirstDefOf.RM_AdministerWater, bottle, patient);
			job.count = 1;
			return job;
		}
	}

	public class WorkGiver_RM_AdministerWaterPrisoner : WorkGiver_RM_AdministerWater
	{
		protected override bool Prisoners => true;
	}
}
