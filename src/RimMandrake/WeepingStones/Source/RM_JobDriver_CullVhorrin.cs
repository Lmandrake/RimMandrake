using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 4. The CULL set-piece (spec §3/§2d): "It
	/// takes fingers. It has taken a wading child's arm, in the stories
	/// farmers tell to make the cull happen on time." Longer and riskier than
	/// an ordinary HARVEST toil, and drops an "enormous single harvest" of
	/// RM_VhorrinMeat sized to clear the Cull Feast recipe
	/// (RM_CookCullFeast, RM_StockedPoolRecipes.xml) from one cull alone.
	///
	/// SIMPLIFICATION FROM THE SPEC, noted honestly rather than silently:
	/// the spec calls this "the two-handler catch" and this wave ships it as
	/// one handler with a genuinely dangerous single-pawn toil (longer wait,
	/// a real injury chance well above HARVEST's) rather than building a
	/// true two-pawn cooperative job — RimWorld has no clean vanilla-idiom
	/// primitive for "two colonists on one AI toil" the way building a Frame
	/// does for construction, and inventing one is a build of its own. If the
	/// owner wants the literal two-handler mechanic later, that is follow-up
	/// work, not a defect in this wave.
	/// </summary>
	public class RM_JobDriver_CullVhorrin : JobDriver
	{
		private const int CullTicks = 420;

		private const float InjuryChance = 0.22f;

		private Pawn Vhorrin => job.targetA.Thing as Pawn;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			Pawn vhorrin = Vhorrin;
			return vhorrin != null && pawn.Reserve(vhorrin, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOn(() => Vhorrin == null || Vhorrin.Dead || !Vhorrin.Spawned);

			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

			Toil cull = Toils_General.Wait(CullTicks).WithProgressBarToilDelay(TargetIndex.A);
			cull.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			yield return cull;

			Toil finish = ToilMaker.MakeToil("MakeNewToils");
			finish.initAction = delegate
			{
				Pawn vhorrin = Vhorrin;
				if (vhorrin == null || !vhorrin.Spawned)
				{
					return;
				}
				IntVec3 spot = vhorrin.Position;
				Map map = vhorrin.Map;
				vhorrin.Destroy(DestroyMode.Vanish);

				if (Rand.Chance(InjuryChance))
				{
					pawn.TakeDamage(new DamageInfo(DamageDefOf.Bite, Rand.Range(6f, 14f), 0f, -1f, vhorrin));
					if (PawnUtility.ShouldSendNotificationAbout(pawn))
					{
						Messages.Message(
							"RM_VhorrinCullInjury".CanTranslate()
								? "RM_VhorrinCullInjury".Translate(pawn.LabelShort)
								: pawn.LabelShort + " was badly hurt culling a vhorrin.",
							pawn, MessageTypeDefOf.NegativeEvent);
					}
				}

				ThingDef meatDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_VhorrinMeat");
				if (meatDef == null)
				{
					return;
				}
				Thing meat = ThingMaker.MakeThing(meatDef);
				meat.stackCount = Rand.RangeInclusive(18, 24); // an enormous single harvest -- clears the Cull Feast alone
				GenPlace.TryPlaceThing(meat, spot, map, ThingPlaceMode.Near);

				if (PawnUtility.ShouldSendNotificationAbout(pawn))
				{
					Messages.Message(
						"RM_VhorrinCulled".CanTranslate()
							? "RM_VhorrinCulled".Translate(pawn.LabelShort)
							: "The pool is saved. " + pawn.LabelShort + " has culled the vhorrin.",
						pawn, MessageTypeDefOf.PositiveEvent);
				}
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
