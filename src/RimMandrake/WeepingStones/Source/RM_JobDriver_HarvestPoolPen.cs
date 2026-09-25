using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 4. The HARVEST verb's per-species catch job
	/// (spec §3: "net mid-air, basket-trap, whistle-call, night-lift — §2's
	/// catch methods are the job flavors"). One toil stands in for all four
	/// flavors — the flavor difference is the target species' own §2
	/// description text, not a different code path; the job's reportString
	/// already carries the generic "harvesting" verb. Drops the species'
	/// RM_&lt;Species&gt;Meat item (a plain suffix on the PawnKindDef's own
	/// defName, same convention <see cref="RM_PoolBreederUtility"/> uses for
	/// breeding stock) and carries skarrin/karrek's real handling risk
	/// (§2a/§2b: face-strikes, strips-to-the-bone) — same weights as netting
	/// them wild, since the catch itself is the dangerous part, not which
	/// side of the pen wall it happens on.
	/// </summary>
	public class RM_JobDriver_HarvestPoolPen : JobDriver
	{
		private const int HarvestTicks = 220;

		private const string MeatSuffix = "Meat";

		private Pawn Stock => job.targetA.Thing as Pawn;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			Pawn stock = Stock;
			return stock != null && pawn.Reserve(stock, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOn(() => Stock == null || Stock.Dead || !Stock.Spawned);

			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

			Toil harvest = Toils_General.Wait(HarvestTicks).WithProgressBarToilDelay(TargetIndex.A);
			harvest.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			yield return harvest;

			Toil finish = ToilMaker.MakeToil("MakeNewToils");
			finish.initAction = delegate
			{
				Pawn stock = Stock;
				if (stock == null || !stock.Spawned)
				{
					return;
				}
				string kindDefName = stock.kindDef?.defName;
				IntVec3 spot = stock.Position;
				Map map = stock.Map;
				stock.Destroy(DestroyMode.Vanish);

				if (kindDefName != null
					&& RM_WorkGiver_HarvestPoolPen.InjuryChancePerSpecies.TryGetValue(kindDefName, out float chance)
					&& Rand.Chance(chance))
				{
					pawn.TakeDamage(new DamageInfo(DamageDefOf.Scratch, Rand.Range(2f, 6f), 0f, -1f, stock));
					if (PawnUtility.ShouldSendNotificationAbout(pawn))
					{
						Messages.Message(
							"RM_PoolHandlerInjury".CanTranslate()
								? "RM_PoolHandlerInjury".Translate(pawn.LabelShort, stock.kindDef.label)
								: pawn.LabelShort + " was hurt harvesting a " + stock.kindDef.label + ".",
							pawn, MessageTypeDefOf.NegativeEvent);
					}
				}

				ThingDef meatDef = kindDefName == null
					? null
					: DefDatabase<ThingDef>.GetNamedSilentFail(kindDefName + MeatSuffix);
				if (meatDef == null)
				{
					return;
				}
				Thing meat = ThingMaker.MakeThing(meatDef);
				meat.stackCount = Rand.RangeInclusive(2, 4);
				GenPlace.TryPlaceThing(meat, spot, map, ThingPlaceMode.Near);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
