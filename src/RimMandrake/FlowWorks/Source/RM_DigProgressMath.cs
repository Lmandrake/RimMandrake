using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_KEEP_DIG_PROGRESS_ACROSS_MEALS_AND_NAPS (live 2026-11-13, live5_digreset.txt): vanilla's
	/// JobDriver_AffectFloor sets its private workLeft to the full BaseWorkAmount in the work toil's initAction, so a cut
	/// broken off for a meal, sleep, a draft or another pawn started again from zero (interrupted at 60%, a soil cut took
	/// 1.61x as long; a rock or deep-pit notch at labour x4 outlasts a colonist's work stretch and may never land). The work
	/// done is now parked per square when a job ends unfinished (<c>RM_MapComponent_DigProgress</c>) and taken back by the
	/// next job on the square, whoever does it. Vanilla's toil, tick and rate are untouched; this runs only when a job starts
	/// or ends. The arithmetic and the store live here, Verse-free, so the SelfTest proves the real code.</summary>
	public static class RM_DigProgressMath
	{
		/// <summary>vanilla's workLeft before the work toil began (JobDriver_AffectFloor's field initialiser).</summary>
		public const float VanillaNotStarted = -1000f;

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

		/// <summary>Work a new job takes from the store: what was parked, only while the square is still at the depth it was
		/// parked at (a cut or fill by anyone in between voids it), otherwise nothing.</summary>
		public static float Resume(bool has, float stored, int storedDepth, int depthNow)
		{
			return has && storedDepth == depthNow && Usable(stored) ? stored : 0f;
		}

		/// <summary>vanilla's workLeft for a job starting on a square with <paramref name="parked"/> work already done. Work
		/// above the total (the labour setting was lowered since, or a cut refused at a digger's cap) leaves 0, so the first
		/// work tick lands the cut.</summary>
		public static float WorkLeftAtStart(float total, float parked)
		{
			if (!Usable(total))
			{
				return total;
			}
			return total - (Usable(parked) ? Math.Min(parked, total) : 0f);
		}

		/// <summary>The work a job did on its square by the time it ended: none before the work toil began, the whole total
		/// once vanilla's countdown reached 0, else what the countdown says.</summary>
		public static float DoneAtEnd(float total, float workLeft, bool started)
		{
			if (!started || !Usable(total) || float.IsNaN(workLeft))
			{
				return 0f;
			}
			if (workLeft <= 0f)
			{
				return total;
			}
			return Math.Max(0f, Math.Min(total, total - workLeft));
		}

		/// <summary>A job saved before this fix carries vanilla's countdown and none of our fields: a positive workLeft means
		/// it was mid-work.</summary>
		public static bool WasMidWork(float workLeft)
		{
			return Usable(workLeft);
		}

		/// <summary>Whether a job that ended parks its work for the square: only work that did not land, on an order that
		/// still stands. A cancelled order takes its work with it.</summary>
		public static bool Keep(float done, bool landed, bool orderStands)
		{
			return !landed && orderStands && Usable(done);
		}

		/// <summary>vanilla AffectFloor's rate: 1.7 x the speed stat per tick (the SelfTest's job model works at it).</summary>
		public static float AfterTicks(float workLeft, float speed, int delta)
		{
			return workLeft - speed * RM_DigDepthMath.WorkPerTickAtSpeedOne * delta;
		}
	}

	/// <summary>Parked shovel work by cell index and direction, each tagged with the depth it was done at. The map component
	/// wraps it; saved as three parallel lists.</summary>
	public sealed class RM_DigProgressStore
	{
		private readonly Dictionary<int, float> done = new Dictionary<int, float>();

		private readonly Dictionary<int, int> depthAt = new Dictionary<int, int>();

		public int Count => done.Count;

		/// <summary>The work parked on the square, removed from the store (the job taking it now holds it).</summary>
		public float Take(int cellIndex, bool fill, int depthNow)
		{
			if (cellIndex < 0)
			{
				return 0f;
			}
			int key = RM_DigProgressMath.Key(cellIndex, fill);
			bool has = done.TryGetValue(key, out float stored);
			depthAt.TryGetValue(key, out int storedDepth);
			done.Remove(key);
			depthAt.Remove(key);
			return RM_DigProgressMath.Resume(has, stored, storedDepth, depthNow);
		}

		public float Peek(int cellIndex, bool fill, int depthNow)
		{
			if (cellIndex < 0)
			{
				return 0f;
			}
			int key = RM_DigProgressMath.Key(cellIndex, fill);
			bool has = done.TryGetValue(key, out float stored);
			depthAt.TryGetValue(key, out int storedDepth);
			return RM_DigProgressMath.Resume(has, stored, storedDepth, depthNow);
		}

		/// <summary>Park work on the square at its current depth (replaces what was there; nothing usable clears it).</summary>
		public void Put(int cellIndex, bool fill, float work, int depthNow)
		{
			if (cellIndex < 0)
			{
				return;
			}
			int key = RM_DigProgressMath.Key(cellIndex, fill);
			if (!RM_DigProgressMath.Usable(work))
			{
				done.Remove(key);
				depthAt.Remove(key);
				return;
			}
			done[key] = work;
			depthAt[key] = depthNow;
		}

		public void Clear(int cellIndex, bool fill)
		{
			if (cellIndex < 0 || done.Count == 0)
			{
				return;
			}
			int key = RM_DigProgressMath.Key(cellIndex, fill);
			done.Remove(key);
			depthAt.Remove(key);
		}

		public void ToLists(List<int> keys, List<float> work, List<int> depths)
		{
			keys.Clear();
			work.Clear();
			depths.Clear();
			foreach (KeyValuePair<int, float> kv in done)
			{
				keys.Add(kv.Key);
				work.Add(kv.Value);
				depths.Add(depthAt.TryGetValue(kv.Key, out int d) ? d : 0);
			}
		}

		/// <summary>Rebuilt from saved lists; a row that is short, unusable or off the map (<paramref name="numCells"/>) is
		/// dropped, never guessed. Null lists (a save from before this fix) give an empty store.</summary>
		public static RM_DigProgressStore FromLists(List<int> keys, List<float> work, List<int> depths, int numCells)
		{
			RM_DigProgressStore s = new RM_DigProgressStore();
			if (keys == null || work == null || depths == null)
			{
				return s;
			}
			int n = Math.Min(keys.Count, Math.Min(work.Count, depths.Count));
			for (int i = 0; i < n; i++)
			{
				int key = keys[i];
				int cell = RM_DigProgressMath.CellOf(key);
				if (key < 0 || cell >= numCells || !RM_DigProgressMath.Usable(work[i]))
				{
					continue;
				}
				s.done[key] = work[i];
				s.depthAt[key] = depths[i];
			}
			return s;
		}
	}
}
