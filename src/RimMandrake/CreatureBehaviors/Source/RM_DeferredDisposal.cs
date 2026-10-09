using System;
using System.Collections.Generic;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// STILLSAND_NATIVE_CRASH_1. Holds retired path-grid customizers until enough GAME TICKS have
	/// passed that no vanilla path job can still be reading their NativeArray, then disposes them.
	///
	/// Why ticks and not rebuild count: vanilla 1.6 runs PathFinder.PathFinderTick in
	/// Map.MapPreTick — it completes last tick's jobs, then schedules this tick's PathGridJobs
	/// (Burst, worker threads) with job.custom = request.customizer.GetOffsetGrid(). Those jobs
	/// run while the main thread ticks things and then map components (MapPostTick). A request
	/// generated in tick T before a rebuild carries the old customizer and is only scheduled at
	/// T+1, and its job is only completed at the start of T+2. Disposing "one rebuild later"
	/// frees that array mid-job whenever two rebuilds land in the same or adjacent ticks (a
	/// direct Recompute() from Solar Mirrors / LongShade plus the grid's own requested one): the
	/// Burst job then reads freed memory and the game dies natively on a worker thread with no
	/// managed exception. RM_PitPathing (FlowWorks) already retires by tick for the same reason.
	///
	/// Pure (System only) so the offline selftest compiles this exact file.
	/// </summary>
	public sealed class RM_DeferredDisposal<T> where T : class, IDisposable
	{
		/// <summary>Minimum ticks between retirement and disposal. 2 is the proven floor
		/// (retired at T, last job using it completes at the start of T+2); 60 is margin for any
		/// request that sits in PathFinder's work queue with a later TickStart.</summary>
		public const int DefaultRetireAfterTicks = 60;

		private readonly List<KeyValuePair<T, int>> retired = new List<KeyValuePair<T, int>>();
		private readonly int retireAfterTicks;

		public RM_DeferredDisposal(int retireAfterTicks = DefaultRetireAfterTicks)
		{
			this.retireAfterTicks = Math.Max(2, retireAfterTicks);
		}

		public int Count => retired.Count;

		public int RetireAfterTicks => retireAfterTicks;

		/// <summary>Queue an object for disposal no earlier than now + RetireAfterTicks.
		/// Never disposes anything itself, so it is safe to call any number of times per tick.</summary>
		public void Retire(T item, int now)
		{
			if (item != null)
			{
				retired.Add(new KeyValuePair<T, int>(item, now));
			}
		}

		/// <summary>Dispose every item retired at least RetireAfterTicks ago. Returns how many.
		/// A clock that went backwards (a reload) leaves items queued rather than disposing early.</summary>
		public int DisposeDue(int now)
		{
			int n = 0;
			for (int i = retired.Count - 1; i >= 0; i--)
			{
				if (now - retired[i].Value >= retireAfterTicks)
				{
					retired[i].Key.Dispose();
					retired.RemoveAt(i);
					n++;
				}
			}
			return n;
		}

		/// <summary>Dispose everything now. Only for map removal, when the PathFinder and every
		/// job that could hold one of these arrays are going away with the map.</summary>
		public void DisposeAll()
		{
			for (int i = 0; i < retired.Count; i++)
			{
				retired[i].Key.Dispose();
			}
			retired.Clear();
		}
	}
}
