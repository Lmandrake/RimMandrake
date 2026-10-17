using System.Collections.Generic;
using RimMandrake.FlowWorks.Thirst;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
	/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU, owner Q12 2026-10-17 (approved, and again in his write-in: "buckets
	/// fight fires"). A firefighter with a filled bucket of a non-flammable water-family liquid near at hand carries it to a
	/// fire in the home area and throws it: every fire within the splash goes out at once, a little puddle is left, and the
	/// bucket comes back empty. It is a work giver ahead of vanilla's beating (priorityInType), so with no bucket near the
	/// pawn simply beats the fire as before. A part-drunk bucket only reaches the fire it is thrown at.</summary>
	public static class RM_BucketFirefighting
	{
		public const float FetchRadius = 25f;
		public const float FullSplashRadius = 1.5f;
		private const float ExtinguishAmount = 1000f;   // fireSize -= amount x 0.01: any fire goes out

		/// <summary>Water puts a fire out; fuel, tar and white slime would feed it, and only drinkable-family liquids qualify.</summary>
		public static bool Douses(LiquidDef liquid)
		{
			return liquid != null && liquid.thirstQuality.HasValue && !liquid.flammable;
		}

		public static bool IsDousingBucket(Thing t)
		{
			RM_BottledLiquidExtension ext = t?.def.GetModExtension<RM_BottledLiquidExtension>();
			return ext != null && ext.size == RM_ContainerSize.Bucket && !ext.IsEmpty && Douses(ext.liquid);
		}

		private static List<ThingDef> bucketDefs;

		private static List<ThingDef> BucketDefs
		{
			get
			{
				if (bucketDefs == null)
				{
					bucketDefs = new List<ThingDef>();
					foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
					{
						RM_BottledLiquidExtension ext = d.GetModExtension<RM_BottledLiquidExtension>();
						if (ext != null && ext.size == RM_ContainerSize.Bucket && !ext.IsEmpty && Douses(ext.liquid))
						{
							bucketDefs.Add(d);
						}
					}
				}
				return bucketDefs;
			}
		}

		/// <summary>The nearest reachable, unforbidden, reservable dousing bucket within FetchRadius of the pawn.</summary>
		public static Thing NearestBucket(Pawn pawn)
		{
			Map map = pawn.Map;
			Thing best = null;
			float bestSq = FetchRadius * FetchRadius;
			foreach (ThingDef def in BucketDefs)
			{
				List<Thing> things = map.listerThings.ThingsOfDef(def);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					float d = (t.Position - pawn.Position).LengthHorizontalSquared;
					if (d >= bestSq || t.IsForbidden(pawn) || !pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Deadly, 1, 1))
					{
						continue;
					}
					best = t;
					bestSq = d;
				}
			}
			return best;
		}

		/// <summary>Put out every fire (not one burning on a pawn) within the splash of <paramref name="at"/>.</summary>
		public static int Douse(Map map, IntVec3 at, float radius, Pawn by)
		{
			int put = 0;
			var fires = new List<Fire>();
			foreach (IntVec3 c in GenRadial.RadialCellsAround(at, radius, true))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				List<Thing> things = c.GetThingList(map);
				for (int i = 0; i < things.Count; i++)
				{
					if (things[i] is Fire f && !f.Destroyed && !(f.parent is Pawn))
					{
						fires.Add(f);
					}
				}
			}
			foreach (Fire f in fires)
			{
				if (f.Destroyed)
				{
					continue;
				}
				f.TakeDamage(new DamageInfo(DamageDefOf.Extinguish, ExtinguishAmount, 0f, -1f, by));
				put++;
				by?.records?.Increment(RecordDefOf.FiresExtinguished);
			}
			return put;
		}
	}

	public class WorkGiver_RM_DouseFireWithBucket : WorkGiver_Scanner
	{
		public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForDef(ThingDefOf.Fire);

		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override Danger MaxPathDanger(Pawn pawn) => Danger.Deadly;

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return !RM_ThirstSettings.bucketFirefighting || pawn.WorkTagIsDisabled(WorkTags.Firefighting)
				|| !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation);
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!(t is Fire fire) || fire.parent is Pawn || !pawn.Map.areaManager.Home[fire.Position])
			{
				return false;   // vanilla's own rule: buildings and ground in the home area (a burning pawn is beaten out)
			}
			if (!pawn.CanReserve(fire, 1, -1, null, forced))
			{
				return false;   // one bucket per fire: a second firefighter takes the next one
			}
			return RM_BucketFirefighting.NearestBucket(pawn) != null;
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			Thing bucket = RM_BucketFirefighting.NearestBucket(pawn);
			if (bucket == null)
			{
				return null;
			}
			Job job = JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_DouseFireWithBucket, bucket, t, t.Position);
			job.count = 1;
			return job;
		}
	}

	public class JobDriver_RM_DouseFireWithBucket : JobDriver
	{
		private const int ThrowTicks = 45;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, 1, null, errorOnFailed)
				&& pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDestroyedNullOrForbidden(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return Toils_Haul.StartCarryThing(TargetIndex.A);
			// target C is the fire's cell: the fire may burn out on the way, and the throw still lands there and catches its
			// neighbours
			yield return Toils_Goto.GotoCell(TargetIndex.C, PathEndMode.Touch);
			Toil aim = Toils_General.Wait(ThrowTicks);
			aim.initAction = () => pawn.rotationTracker.FaceCell(job.targetC.Cell);
			yield return aim;
			Toil throwIt = ToilMaker.MakeToil("RM_DouseThrow");
			throwIt.initAction = delegate
			{
				Thing carried = pawn.carryTracker.CarriedThing;
				RM_BottledLiquidExtension ext = carried?.def.GetModExtension<RM_BottledLiquidExtension>();
				if (ext == null || !RM_BucketFirefighting.Douses(ext.liquid))
				{
					return;
				}
				IntVec3 at = job.targetC.Cell;
				bool full = CompRM_DrawnLitres.DrawnUnits(carried) == 0;
				RM_BucketFirefighting.Douse(Map, at, full ? RM_BucketFirefighting.FullSplashRadius : 0.9f, pawn);
				ThingDef filth = ext.liquid.spillFilth ?? RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill;
				if (filth != null && at.InBounds(Map))
				{
					FilthMaker.TryMakeFilth(at, Map, filth, 1);
				}
				Thing empty = RM_LiquidBottleUtility.MakeContainer(RM_LiquidBottleUtility.EmptyDefFor(RM_ContainerSize.Bucket), carried);
				pawn.carryTracker.innerContainer.Remove(carried);
				carried.Destroy();
				RM_LiquidBottleUtility.PlacePaidFor(empty, pawn.Position, Map);
			};
			throwIt.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return throwIt;
		}
	}
}
