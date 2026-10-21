using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3; capture rebuilt by WEEPINGSTONES_NET_TARGET_FLEES_1 (2026-10-21). Nets one wild
	/// pool-fauna pawn and turns it into a carryable breeding-stock item ("a wet skin", spec §3 STOCK) dropped where it
	/// was caught - the follow-up <see cref="RM_JobDriver_StockPoolPen"/> carries it home.
	///
	/// Capture is a THROW, not a channel (owner, 2026-10-07: "It's supposed to depend on how fast they are. Whether the
	/// net can hit the right place. How is this becoming our problem? Net mechanics are already in the game."). The
	/// old 200-tick touch-and-wait, and the stun that froze the target for the whole job so the wait could finish, are
	/// gone. Base game + all five DLC ship no net item or net class (searched Data/ XML and the decompiled source,
	/// 2026-10-21), so "the game's net mechanics" are built from the vanilla pieces a net throw is made of:
	///   - aim: vanilla <see cref="ShotReport.HitFactorFromShooter"/> (ShootingAccuracyPawn ^ distance x the pawn's
	///     range-band factors) decides whether the throw goes at the target's cell or 2-3 cells off;
	///   - flight: a vanilla <see cref="Projectile"/> (<see cref="RM_Projectile_PoolNet"/>) to that cell, destination
	///     fixed at launch, travel time = distance / speed;
	///   - landing: the net takes the target only if it is still under the net then - a fast or fleeing animal is not.
	/// A miss costs a re-throw; after <see cref="RM_WeepingStonesSettings.netMaxThrows"/> the job ends and the work
	/// giver may offer it again. A netted animal is entangled (vanilla stun) and the handler walks over and bags it.
	///
	/// Also the item's owed "handler injuries real-but-minor" (scope §4): bagging the more aggressive rows (skarrin/
	/// karrek/vizhik) has a small chance of a minor bite/scratch - never a maiming lottery.
	/// </summary>
	public class RM_JobDriver_NetPoolBreeder : JobDriver
	{
		public const string NetProjectileDefName = "RM_Projectile_PoolNet";

		/// <summary>Aim and release, like a grenade's warmup. INVENTED.</summary>
		private const int WindupTicks = 45;

		/// <summary>Securing an already-entangled animal in the skin. Short on purpose: the net did the catching.</summary>
		private const int BagTicks = 60;

		/// <summary>Safety cap on waiting for a thrown net to land (a 12-cell throw at speed 14 lands in ~86 ticks).</summary>
		private const int MaxFlightWaitTicks = 240;

		/// <summary>Species whose handling carries the "real-but-minor" injury risk the spec's bestiary rows call out by
		/// name (§2a/§2b/§2c). The gentle/doubt rows (murrin, loomu, huldu, ivvol) carry none.</summary>
		private static readonly Dictionary<string, float> InjuryChancePerSpecies = new Dictionary<string, float>
		{
			{ "RM_Skarrin", 0.12f },
			{ "RM_Karrek", 0.15f },
			{ "RM_Vizhik", 0.08f },
		};

		private int throwsMade;
		private Projectile thrownNet;

		private Pawn WildTarget => job.targetA.Thing as Pawn;

		public override void ExposeData()
		{
			base.ExposeData();
			if (Scribe.mode == LoadSaveMode.Saving && thrownNet != null && thrownNet.Destroyed)
			{
				thrownNet = null;
			}
			Scribe_Values.Look(ref throwsMade, "throwsMade", 0);
			Scribe_References.Look(ref thrownNet, "thrownNet");
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			Pawn wild = WildTarget;
			return wild != null && pawn.Reserve(wild, job, 1, -1, null, errorOnFailed);
		}

		private bool InThrowPosition()
		{
			Pawn wild = WildTarget;
			if (wild == null || !wild.Spawned || wild.Map != pawn.Map)
			{
				return false;
			}
			float dist = (wild.Position - pawn.Position).LengthHorizontal;
			return RM_NetKernel.InThrowRange(dist, RM_WeepingStonesSettings.netThrowRange)
				&& GenSight.LineOfSight(pawn.Position, wild.Position, pawn.Map);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOn(() => WildTarget == null || WildTarget.Dead || !WildTarget.Spawned);

			Toil bagApproach = Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

			// Already entangled (a net from an earlier job that just ended): go straight to bagging.
			yield return Toils_Jump.JumpIf(bagApproach, () => RM_PoolBreederUtility.IsNetted(WildTarget));

			// Close to throwing range with a clear line, then stop.
			Toil approach = Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			approach.AddPreTickIntervalAction(delegate
			{
				if (InThrowPosition())
				{
					pawn.pather.StopDead();
					ReadyForNextToil();
				}
			});
			yield return approach;

			yield return Toils_General.Wait(WindupTicks, TargetIndex.A);

			Toil throwNet = ToilMaker.MakeToil("MakeNewToils");
			throwNet.initAction = delegate
			{
				thrownNet = LaunchNet();
				throwsMade++;
			};
			throwNet.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return throwNet;

			Toil watch = ToilMaker.MakeToil("MakeNewToils");
			watch.handlingFacing = true;
			watch.tickIntervalAction = delegate
			{
				pawn.rotationTracker.FaceTarget(WildTarget);
				if (thrownNet == null || thrownNet.Destroyed || !thrownNet.Spawned)
				{
					ReadyForNextToil();
				}
			};
			watch.defaultCompleteMode = ToilCompleteMode.Delay;
			watch.defaultDuration = MaxFlightWaitTicks;
			yield return watch;

			Toil judge = ToilMaker.MakeToil("MakeNewToils");
			judge.initAction = delegate
			{
				thrownNet = null;
				if (RM_PoolBreederUtility.IsNetted(WildTarget))
				{
					return;
				}
				if (throwsMade < RM_WeepingStonesSettings.netMaxThrows)
				{
					JumpToToil(approach);
					return;
				}
				EndJobWith(JobCondition.Incompletable);
			};
			judge.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return judge;

			bagApproach.FailOn(() => !RM_PoolBreederUtility.IsNetted(WildTarget));
			yield return bagApproach;

			Toil bag = Toils_General.Wait(BagTicks, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
			bag.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			yield return bag;

			Toil finish = ToilMaker.MakeToil("MakeNewToils");
			finish.initAction = Bag;
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}

		/// <summary>Aim with vanilla's shooter factor; throw at the target's cell or, on a bad aim, 2-3 cells off it.</summary>
		private Projectile LaunchNet()
		{
			Pawn wild = WildTarget;
			ThingDef netDef = DefDatabase<ThingDef>.GetNamedSilentFail(NetProjectileDefName);
			if (wild == null || netDef == null)
			{
				EndJobWith(JobCondition.Errored);
				return null;
			}
			Map map = pawn.Map;
			float dist = (wild.Position - pawn.Position).LengthHorizontal;
			IntVec3 aim = wild.Position;
			if (!Rand.Chance(ShotReport.HitFactorFromShooter(pawn, dist)))
			{
				List<IntVec3> off = GenRadial.RadialCellsAround(wild.Position, RM_NetKernel.MissOffsetMin, RM_NetKernel.MissOffsetMax)
					.Where(c => c.InBounds(map) && !RM_NetKernel.NetCovers(wild.Position.x, wild.Position.z, c.x, c.z, RM_NetKernel.DefaultNetRadius))
					.ToList();
				if (off.Count > 0)
				{
					aim = off.RandomElement();
				}
			}
			Projectile net = (Projectile)GenSpawn.Spawn(netDef, pawn.Position, map);
			net.Launch(pawn, pawn.DrawPos, aim, wild, ProjectileHitFlags.None);
			return net;
		}

		private void Bag()
		{
			Pawn wild = WildTarget;
			if (wild == null || !wild.Spawned)
			{
				return;
			}
			string kindDefName = wild.kindDef?.defName;
			IntVec3 spot = wild.Position;
			Map map = wild.Map;
			RM_PoolBreederUtility.ClearNetted(wild);
			wild.Destroy(DestroyMode.Vanish);

			if (kindDefName != null && InjuryChancePerSpecies.TryGetValue(kindDefName, out float chance) && Rand.Chance(chance))
			{
				DamageDef dmg = kindDefName == "RM_Vizhik" ? DamageDefOf.Bite : DamageDefOf.Scratch;
				pawn.TakeDamage(new DamageInfo(dmg, Rand.Range(2f, 6f), 0f, -1f, wild));
				if (PawnUtility.ShouldSendNotificationAbout(pawn))
				{
					Messages.Message(
						"RM_PoolHandlerInjury".CanTranslate()
							? "RM_PoolHandlerInjury".Translate(pawn.LabelShort, wild.kindDef.label)
							: pawn.LabelShort + " was hurt netting a " + wild.kindDef.label + ".",
						pawn, MessageTypeDefOf.NegativeEvent);
				}
			}

			ThingDef stockDef = kindDefName == null
				? null
				: DefDatabase<ThingDef>.GetNamedSilentFail(RM_PoolBreederUtility.BreedingStockDefNameFor(kindDefName));
			if (stockDef == null)
			{
				return;
			}
			Thing stock = ThingMaker.MakeThing(stockDef);
			stock.stackCount = 1;
			GenPlace.TryPlaceThing(stock, spot, map, ThingPlaceMode.Near);
		}
	}
}
