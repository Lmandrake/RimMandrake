using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_BUILD_FLOWWORKS_TOSS_FLAME_JOBDEF_STILL_UNKNOWN (concept leaf toss_flame_from_rim, scene sc_toss_flame):
	/// the 'toss a flame' order. A colonist walks to the rim (dry standable ground outside the dug squares, within
	/// <see cref="RM_TossFlame.TossRange"/> and in sight of the target), takes aim a moment, and tosses a flame onto the
	/// square the player picked. Before this, RM_LiquidFire lit only from an existing fire, so a moat of fuel had no way
	/// to be lit by hand. The toss lights, in order: burnable liquid in a canal or pond (RM_LiquidFire.IgniteNow), a
	/// burnable spill on open ground (the sheet's TryLight), else whatever on the square burns (a vanilla fire). A square
	/// where nothing catches (water) stays dark. Setting: tossFlameOrderEnabled.
	/// </summary>
	public class JobDriver_TossFlame : JobDriver
	{
		public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOn(() => !RimMandrakeFlowWorksSettings.tossFlameOrderEnabled || !job.targetA.Cell.InBounds(Map));
			Toil walk = ToilMaker.MakeToil("RM_TossFlame_ToRim");
			walk.initAction = delegate
			{
				IntVec3 target = job.targetA.Cell;
				if (!RM_TossFlame.FindRim(pawn, target, out IntVec3 rim))
				{
					EndJobWith(JobCondition.Incompletable);
					return;
				}
				job.targetB = rim;
				if (pawn.Position == rim)
				{
					ReadyForNextToil();
					return;
				}
				pawn.pather.StartPath(rim, PathEndMode.OnCell);
			};
			walk.defaultCompleteMode = ToilCompleteMode.PatherArrival;
			yield return walk;
			Toil aim = ToilMaker.MakeToil("RM_TossFlame_Aim");
			aim.initAction = delegate
			{
				pawn.pather.StopDead();
				pawn.rotationTracker.FaceCell(job.targetA.Cell);
			};
			aim.handlingFacing = true;
			aim.defaultCompleteMode = ToilCompleteMode.Delay;
			aim.defaultDuration = RM_TossFlame.AimTicks;
			aim.WithProgressBarToilDelay(TargetIndex.A);
			yield return aim;
			Toil toss = ToilMaker.MakeToil("RM_TossFlame_Toss");
			toss.initAction = delegate
			{
				if (!RM_TossFlame.Toss(pawn, job.targetA.Cell))
				{
					Messages.Message("The flame went out: nothing on that square burns.", new TargetInfo(job.targetA.Cell, Map),
						MessageTypeDefOf.NeutralEvent, false);
				}
			};
			toss.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return toss;
		}
	}

	public static class RM_TossFlame
	{
		/// <summary>How far a colonist can toss a flame, in squares. PROVISIONAL (auto-decided 2026-11-15).</summary>
		public const float TossRange = 4.9f;
		public const int AimTicks = 60;
		private const float TossFireSize = 0.3f;

		/// <summary>Something on the square will catch: burnable canal or pond liquid, or a burnable spill, not yet alight.</summary>
		public static bool CanLight(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map) || !RimMandrakeFlowWorksSettings.canalFireEnabled)
			{
				return false;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex != null && RM_LiquidFire.BurnableFluidAt(map, ex, c) != null && !ex.LiquidFire.IsBurning(map, c))
			{
				return true;
			}
			Sheet.RM_MapComponent_Sheet sheet = Sheet.RM_MapComponent_Sheet.Of(map);
			return sheet != null && Sheet.RM_SheetSettings.fuelSpillsBurnEnabled && sheet.DlAt(c) > 0
				&& Sheet.RM_MapComponent_Sheet.Burnable(sheet.FluidAt(c)) && !sheet.IsBurning(c);
		}

		/// <summary>The rim: dry standable ground outside the dug squares (never thrown from in the liquid).</summary>
		private static bool IsRim(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			return c.InBounds(map) && c.Standable(map) && (ex == null || !ex.IsExcavated(c));
		}

		/// <summary>The rim square in reach and in sight of <paramref name="target"/> nearest the pawn that it can walk to.</summary>
		public static bool FindRim(Pawn pawn, IntVec3 target, out IntVec3 rim)
		{
			rim = IntVec3.Invalid;
			Map map = pawn.Map;
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			List<IntVec3> spots = new List<IntVec3>();
			int n = GenRadial.NumCellsInRadius(TossRange);
			for (int k = 1; k < n; k++)   // k = 0 is the target itself: nobody tosses a flame at their own feet
			{
				IntVec3 c = target + GenRadial.RadialPattern[k];
				if (IsRim(map, ex, c) && GenSight.LineOfSight(c, target, map))
				{
					spots.Add(c);
				}
			}
			spots.SortBy(c => c.DistanceToSquared(pawn.Position));
			foreach (IntVec3 c in spots)
			{
				if (pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
				{
					rim = c;
					return true;
				}
			}
			return false;
		}

		/// <summary>Give <paramref name="pawn"/> the toss order at <paramref name="c"/> (the float menu's and the button's act).</summary>
		public static bool Order(Pawn pawn, IntVec3 c)
		{
			return pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(RimMandrakeFlowWorks_DefOf.RM_TossFlame, c), JobTag.Misc);
		}

		/// <summary>Why <paramref name="pawn"/> cannot toss a flame at all now, or null. The button shows greyed with it.</summary>
		public static string Unable(Pawn pawn)
		{
			if (pawn.Downed) return "downed";
			if (pawn.health?.capacities != null && !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation)) return "cannot use hands";
			return null;
		}

		/// <summary>The "Toss a flame" button of a player colonist, or null (setting off, liquid fire off, not the player's).</summary>
		public static Gizmo Gizmo(Pawn pawn)
		{
			if (!RimMandrakeFlowWorksSettings.tossFlameOrderEnabled || !RimMandrakeFlowWorksSettings.canalFireEnabled || pawn == null
				|| !pawn.Spawned || !pawn.IsColonistPlayerControlled)
			{
				return null;
			}
			var cmd = new Command_Action
			{
				defaultLabel = "Toss a flame",
				defaultDesc = "Light a burnable liquid: tar, chemfuel or oil in a canal, pit, pond or spill. Choose the square; the colonist " +
							  "walks to dry ground within " + TossRange.ToString("0.#") + " squares of it and tosses a flame. Only a square where " +
							  "something will catch can be chosen. (Also on the right-click menu: \"Toss a flame here\".)",
				icon = ContentFinder<Texture2D>.Get("Things/Special/Fire/FireA", false) ?? TexCommand.Attack,
				action = () =>
				{
					Map map = pawn.Map;
					var tp = new TargetingParameters
					{
						canTargetLocations = true, canTargetPawns = false, canTargetBuildings = false, canTargetItems = false,
						validator = t => t.Cell.IsValid && CanLight(map, t.Cell)
					};
					Find.Targeter.BeginTargeting(tp, t =>
					{
						if (!FindRim(pawn, t.Cell, out _))
						{
							Messages.Message("No dry ground within " + TossRange.ToString("0.#") + " squares of that square that " + pawn.LabelShort +
											 " can reach and see it from.", MessageTypeDefOf.RejectInput, false);
							return;
						}
						Order(pawn, t.Cell);
					}, caster: pawn);
				}
			};
			string why = Unable(pawn);
			if (why != null) cmd.Disable(why);
			return cmd;
		}

		/// <summary>The flame lands on <paramref name="c"/>. False when nothing there caught.</summary>
		public static bool Toss(Pawn pawn, IntVec3 c)
		{
			Map map = pawn.Map;
			FleckMaker.ThrowMicroSparks(c.ToVector3Shifted(), map);
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex != null && ex.LiquidFire.IgniteNow(map, ex, c))
			{
				return true;
			}
			Sheet.RM_MapComponent_Sheet sheet = Sheet.RM_MapComponent_Sheet.Of(map);
			if (sheet != null && sheet.TryLight(c))
			{
				return true;
			}
			return FireUtility.TryStartFireIn(c, map, TossFireSize, pawn);
		}
	}

	/// <summary>Right-click a square with a colonist selected: "Toss a flame here", offered only where something will catch.</summary>
	public class FloatMenuOptionProvider_TossFlame : FloatMenuOptionProvider
	{
		protected override bool Drafted => true;
		protected override bool Undrafted => true;
		protected override bool Multiselect => false;
		protected override bool RequiresManipulation => true;

		protected override bool AppliesInt(FloatMenuContext context) => RimMandrakeFlowWorksSettings.tossFlameOrderEnabled;

		public override IEnumerable<FloatMenuOption> GetOptions(FloatMenuContext context)
		{
			Pawn p = context.FirstSelectedPawn;
			IntVec3 c = context.ClickedCell;
			if (p == null || !RM_TossFlame.CanLight(context.map, c)) yield break;
			if (!RM_TossFlame.FindRim(p, c, out _))
			{
				yield return new FloatMenuOption("Toss a flame here (no dry ground within reach)", null);
				yield break;
			}
			yield return new FloatMenuOption("Toss a flame here", () => RM_TossFlame.Order(p, c));
		}
	}

	/// <summary>RIMMANDRAKE_SHOW_TAR_LIGHT_ORDER_HE_FOUND_NONE (his walk, 2026-11-25: "How do you light Tar? I actually don't know
	/// how to do this in the game."): the order as a button on a selected colonist, so a player finds it without knowing the
	/// right-click. The button aims at a square; only a square where something will catch (RM_TossFlame.CanLight) is taken.</summary>
	[HarmonyPatch(typeof(Pawn), nameof(Pawn.GetGizmos))]
	[RimMandrake.Shared.PatchFeature("Toss a flame order", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "tossFlameOrderEnabled")]
	public static class RM_Patch_Pawn_TossFlameGizmo
	{
		public const string Label = "Toss a flame";

		[HarmonyPostfix]
		public static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> __result, Pawn __instance)
		{
			foreach (Gizmo g in __result)
			{
				yield return g;
			}
			Gizmo b = RM_TossFlame.Gizmo(__instance);
			if (b != null)
			{
				yield return b;
			}
		}
	}
}
