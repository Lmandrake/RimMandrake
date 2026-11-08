using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>Live bug (save NS_Pyrelands_play_q_col_d3dig, 2026-11-07): a colonist on RM_DigCanalJob stood on one
	/// canal square for over 10 game hours and fell to food 0.05 and thirst 0.0. Vanilla's AffectFloor work toil never
	/// lets the think tree look again until its work is done, and a first cut costs 3200 x 4 = 12,800 work, 16 to 31 hours
	/// for a weak miner. Two fixes, both in <c>RM_JobDriver_ShovelFloor</c>: the job re-reads the think tree every
	/// <see cref="OverrideCheckTicks"/> (food, drink, rest and fire win), and the work already done on a square is kept per
	/// square (<c>RM_MapComponent_DigProgress</c>), so whoever comes back carries on from it. The arithmetic of that
	/// store lives here, Verse-free, so the SelfTest can prove it.</summary>
	public static class RM_DigProgressMath
	{
		/// <summary>How often a running dig or fill re-reads the pawn's think tree (Job.expiryInterval with
		/// checkOverrideOnExpire). Under an hour: a notch at speed 1 is 12,800 / 1.7, about 7,500 ticks.</summary>
		public const int OverrideCheckTicks = 2000;

		/// <summary>How often the store drops work for squares whose order was cancelled or whose depth moved.</summary>
		public const int PruneEveryTicks = 250;

		/// <summary>One key per square and direction: a dig's work never counts toward a fill of the same square.</summary>
		public static int Key(int cellIndex, bool fill)
		{
			return cellIndex * 2 + (fill ? 1 : 0);
		}

		public static int CellOf(int key)
		{
			return key >> 1;
		}

		public static bool IsFill(int key)
		{
			return (key & 1) == 1;
		}

		public static bool Usable(float work)
		{
			return work > 0f && !float.IsNaN(work) && !float.IsInfinity(work);
		}

		/// <summary>Work a resumed job starts from: what was stored for the square, only while the square is still at the
		/// depth it was stored at (a cut or fill by anyone else in between voids it), otherwise nothing.</summary>
		public static float Resume(bool has, float stored, int storedDepth, int depthNow)
		{
			return has && storedDepth == depthNow && Usable(stored) ? stored : 0f;
		}

		/// <summary>One tick interval of shovel work: vanilla AffectFloor's own rate, 1.7 x the speed stat per tick.</summary>
		public static float AfterTicks(float done, float speed, int delta)
		{
			return done + speed * RM_DigDepthMath.WorkPerTickAtSpeedOne * delta;
		}

		public static bool Finished(float done, float total)
		{
			return total > 0f && done >= total;
		}

		/// <summary>The progress bar: the share of the work done, 0..1.</summary>
		public static float Fraction(float done, float total)
		{
			if (!(total > 0f) || !Usable(done))
			{
				return 0f;
			}
			return Math.Min(1f, done / total);
		}

		/// <summary>Whether a job that ended keeps its work for the square: only work that did not land, on an order that
		/// still stands. A cancelled order takes its work with it.</summary>
		public static bool Keep(float done, bool landed, bool orderStands)
		{
			return !landed && orderStands && Usable(done);
		}

		/// <summary>A save from before this fix holds vanilla's private workLeft (counting down from the total, -1000 before
		/// the work began). The work it stands for, 0..total; nothing when it says nothing.</summary>
		public static float FromWorkLeft(float workLeft, float total)
		{
			if (!Usable(workLeft) || !(total > 0f))
			{
				return 0f;
			}
			return Math.Max(0f, Math.Min(total, total - workLeft));
		}
	}
}
