using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU, the salt-water break (design/RimMandrake/thirst_fluids_3x3_2026-10-17/
	/// 04-merged.md §8, owner Q8 2026-10-17: "break needs thirst plus low mood, like other breaks"; brine is salt).
	/// RM_Break_DrinkBrine is an ordinary mood-pool MentalBreakDef (Defs/Thirst/RM_Thirst_SaltBreak.xml): the mood pool
	/// supplies the low mood; this worker adds the thirst half (RM_ThirstMath.SaltBreakCan): parched on whichever thirst
	/// need runs (ours, or Dubs' DBHThirst under Q11), no potable water in reach, not still salt-poisoned (no re-entry), and
	/// salt water or brine to drink. Inside the state the pawn drinks salt until the bar reads full; each drink is brief
	/// relief (RM_Thought_SaltRelief) and salt poisoning (RM_SaltPoisoning), both data on the salt rows.</summary>
	public class MentalStateWorker_RM_DrinkBrine : MentalStateWorker
	{
		public override bool StateCanOccur(Pawn pawn)
		{
			if (!base.StateCanOccur(pawn) || !RM_ThirstSettings.saltBreakEnabled || !pawn.Spawned || pawn.Map == null
				|| !pawn.RaceProps.Humanlike || RM_ThirstUtility.ThirstNeedAny(pawn) == null)
			{
				return false;
			}
			float level = RM_ThirstUtility.LevelAny(pawn);
			if (level >= RM_ThirstMath.ParchedBelow)
			{
				return false;   // cheap exit first: almost every mood break is not thirst-driven
			}
			bool poisoned = RM_ThirstDefOf.RM_SaltPoisoning != null
				&& pawn.health.hediffSet.HasHediff(RM_ThirstDefOf.RM_SaltPoisoning);
			return RM_ThirstMath.SaltBreakCan(level, poisoned, RM_SaltBreakUtility.PotableReachable(pawn, level),
				RM_SaltBreakUtility.FindSalt(pawn) != null);
		}
	}

	/// <summary>The state: drink salt until the thirst bar reads RM_ThirstMath.SaltBreakQuenched, then it ends on its own
	/// (or vanilla's recovery timers end it first).</summary>
	public class MentalState_RM_DrinkBrine : MentalState
	{
		public override void MentalStateTick(int delta)
		{
			base.MentalStateTick(delta);
			if (pawn.MentalState == this && pawn.IsHashIntervalTick(120, delta)
				&& RM_ThirstUtility.LevelAny(pawn) >= RM_ThirstMath.SaltBreakQuenched)
			{
				RecoverFromState();
			}
		}
	}

	/// <summary>Inside RM_DrinkBrine (patched into vanilla's MentalStateNonCritical tree): walk to the nearest salt water
	/// or brine (a bottle, a tank, a shore) and drink it, again and again.</summary>
	public class JobGiver_RM_DrinkBrine : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (pawn.Downed || pawn.Map == null)
			{
				return null;
			}
			LocalTargetInfo salt = RM_SaltBreakUtility.FindSalt(pawn);
			if (!salt.IsValid)
			{
				return null;
			}
			if (salt.HasThing && salt.Thing is Building_LiquidTank tank)
			{
				return JobMaker.MakeJob(RM_ThirstDefOf.RM_DrinkFromTank, tank);
			}
			if (salt.HasThing)
			{
				Job ingest = JobMaker.MakeJob(JobDefOf.Ingest, salt.Thing);
				ingest.count = 1;
				return ingest;
			}
			return RM_ThirstUtility.TerrainJob(salt.Cell);
		}
	}

	public static class RM_SaltBreakUtility
	{
		/// <summary>Is any potable source in reach (a bottle, a tank, a pond)? The break needs "no fresh water in reach".</summary>
		public static bool PotableReachable(Pawn pawn, float level)
		{
			RM_DrinkUse potable = RM_DrinkUse.Potable;
			if (RM_ThirstUtility.BestBottle(pawn, level, true, out _, out _, out _, null, potable) != null)
			{
				return true;
			}
			if (RM_ThirstUtility.BestTank(pawn, level, out _, out _, out _, potable) != null)
			{
				return true;
			}
			return RM_ThirstSettings.drinkFromTerrain
				&& RM_ThirstUtility.TryFindDrinkCell(pawn, level, out _, out _, out _, out _, potable);
		}

		/// <summary>The nearest salt-water or brine source: a bottle (inventory first), else the nearer of a tank and a
		/// shore cell. Invalid when there is none.</summary>
		public static LocalTargetInfo FindSalt(Pawn pawn)
		{
			float level = RM_ThirstUtility.LevelAny(pawn);
			RM_DrinkUse salt = RM_DrinkUse.BreakOnly;
			Thing bottle = RM_ThirstUtility.BestBottle(pawn, level, true, out _, out _, out float bd, null, salt);
			Building_LiquidTank tank = RM_ThirstUtility.BestTank(pawn, level, out _, out _, out float td, salt);
			bool shore = RM_ThirstUtility.TryFindDrinkCell(pawn, level, out IntVec3 cell, out _, out _, out _, salt);
			float cd = shore ? (cell - pawn.Position).LengthHorizontalSquared : float.MaxValue;
			if (bottle != null && bd <= td && bd <= cd)
			{
				return bottle;
			}
			if (tank != null && td <= cd)
			{
				return tank;
			}
			return shore ? new LocalTargetInfo(cell) : LocalTargetInfo.Invalid;
		}
	}
}
