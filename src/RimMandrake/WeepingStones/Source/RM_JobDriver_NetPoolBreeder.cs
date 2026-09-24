using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3. Nets one wild pool-fauna pawn and turns
	/// it into a carryable breeding-stock item ("a wet skin", spec §3 STOCK)
	/// dropped at the handler's feet — the follow-up
	/// <see cref="RM_JobDriver_StockPoolPen"/> carries it home. Also the
	/// item's owed "handler injuries real-but-minor" (scope §4): a handling
	/// accident on the more aggressive rows (skarrin/karrek/vizhik) has a
	/// small chance of a minor bite/scratch — never a maiming lottery, per
	/// the BENCH-settled smalls in the spec header.
	/// </summary>
	public class RM_JobDriver_NetPoolBreeder : JobDriver
	{
		private const int NetTicks = 200;

		/// <summary>Species whose handling carries the "real-but-minor"
		/// injury risk the spec's bestiary rows call out by name (§2a/§2b/
		/// §2c: face-strikes, strips-to-the-bone, septic bites). The gentle/
		/// doubt rows (murrin, loomu, huldu, ivvol) carry none — §2's own
		/// table says so ("None whatsoever" for huldu, no nastiness line for
		/// the others beyond "mild").</summary>
		private static readonly Dictionary<string, float> InjuryChancePerSpecies = new Dictionary<string, float>
		{
			{ "RM_Skarrin", 0.12f },
			{ "RM_Karrek", 0.15f },
			{ "RM_Vizhik", 0.08f },
		};

		private Pawn WildTarget => job.targetA.Thing as Pawn;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			Pawn wild = WildTarget;
			return wild != null && pawn.Reserve(wild, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOn(() => WildTarget == null || WildTarget.Dead || !WildTarget.Spawned);

			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

			Toil net = Toils_General.Wait(NetTicks).WithProgressBarToilDelay(TargetIndex.A);
			net.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			yield return net;

			Toil finish = ToilMaker.MakeToil("MakeNewToils");
			finish.initAction = delegate
			{
				Pawn wild = WildTarget;
				if (wild == null || !wild.Spawned)
				{
					return;
				}
				string kindDefName = wild.kindDef?.defName;
				IntVec3 spot = wild.Position;
				Map map = wild.Map;
				wild.Destroy(DestroyMode.Vanish);

				if (InjuryChancePerSpecies.TryGetValue(kindDefName, out float chance) && Rand.Chance(chance))
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
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
