using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>Shovel work already done on a square whose dig or fill was interrupted (hunger, thirst, sleep, a fire, a
	/// draft, a lost shovel) and is not finished: the next job on the square, by anyone, carries on from it. See
	/// <see cref="RM_DigProgressMath"/>. A running job holds its own work (<see cref="RM_JobDriver_ShovelFloor"/>, saved with
	/// the job); only paused work lives here, keyed by square and direction and tagged with the depth it was done at.
	/// Dropped when the order is cancelled (no designation) or the square's depth moves under it.</summary>
	public class RM_MapComponent_DigProgress : MapComponent
	{
		private Dictionary<int, float> done = new Dictionary<int, float>();

		private Dictionary<int, int> depthAt = new Dictionary<int, int>();

		private readonly List<int> pruneBuffer = new List<int>();

		public RM_MapComponent_DigProgress(Map map) : base(map)
		{
		}

		public int Count => done.Count;

		private bool KeyOf(IntVec3 c, bool fill, out int key)
		{
			key = 0;
			if (!c.InBounds(map))
			{
				return false;
			}
			key = RM_DigProgressMath.Key(map.cellIndices.CellToIndex(c), fill);
			return true;
		}

		private int DepthNow(IntVec3 c)
		{
			return map.GetComponent<RM_MapComponent_Excavation>()?.ExcavatedDepthAt(c) ?? 0;
		}

		/// <summary>The work paused on the square, removed from the store (the job taking it now holds it); 0 when there is
		/// none or the square's depth has moved since.</summary>
		public float Take(IntVec3 c, bool fill)
		{
			if (!KeyOf(c, fill, out int key))
			{
				return 0f;
			}
			bool has = done.TryGetValue(key, out float stored);
			depthAt.TryGetValue(key, out int storedDepth);
			done.Remove(key);
			depthAt.Remove(key);
			return RM_DigProgressMath.Resume(has, stored, storedDepth, DepthNow(c));
		}

		/// <summary>Pause work on the square at its current depth (replaces anything stored there).</summary>
		public void Put(IntVec3 c, bool fill, float work)
		{
			if (!KeyOf(c, fill, out int key))
			{
				return;
			}
			if (!RM_DigProgressMath.Usable(work))
			{
				done.Remove(key);
				depthAt.Remove(key);
				return;
			}
			done[key] = work;
			depthAt[key] = DepthNow(c);
		}

		public void Clear(IntVec3 c, bool fill)
		{
			if (KeyOf(c, fill, out int key))
			{
				done.Remove(key);
				depthAt.Remove(key);
			}
		}

		public float Peek(IntVec3 c, bool fill)
		{
			if (!KeyOf(c, fill, out int key))
			{
				return 0f;
			}
			bool has = done.TryGetValue(key, out float stored);
			depthAt.TryGetValue(key, out int storedDepth);
			return RM_DigProgressMath.Resume(has, stored, storedDepth, DepthNow(c));
		}

		public override void MapComponentTick()
		{
			if (done.Count == 0 || Find.TickManager.TicksGame % RM_DigProgressMath.PruneEveryTicks != 0)
			{
				return;
			}
			Prune();
		}

		/// <summary>Drops work whose order is gone (cancelled, or deleted as stale by the work giver) or whose square's depth
		/// moved (someone else cut or filled it).</summary>
		private void Prune()
		{
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			DesignationManager dm = map.designationManager;
			int cells = map.cellIndices.NumGridCells;
			pruneBuffer.Clear();
			foreach (KeyValuePair<int, float> kv in done)
			{
				int idx = RM_DigProgressMath.CellOf(kv.Key);
				if (idx < 0 || idx >= cells)
				{
					pruneBuffer.Add(kv.Key);
					continue;
				}
				IntVec3 c = map.cellIndices.IndexToCell(idx);
				DesignationDef des = RM_DigProgressMath.IsFill(kv.Key) ? RimMandrakeFlowWorks_DefOf.RM_FillInCanal : RimMandrakeFlowWorks_DefOf.RM_DigCanal;
				depthAt.TryGetValue(kv.Key, out int storedDepth);
				if (dm.DesignationAt(c, des) == null || (ex?.ExcavatedDepthAt(c) ?? 0) != storedDepth)
				{
					pruneBuffer.Add(kv.Key);
				}
			}
			for (int i = 0; i < pruneBuffer.Count; i++)
			{
				done.Remove(pruneBuffer[i]);
				depthAt.Remove(pruneBuffer[i]);
			}
			pruneBuffer.Clear();
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref done, "rmDigProgressDone", LookMode.Value, LookMode.Value);
			Scribe_Collections.Look(ref depthAt, "rmDigProgressDepth", LookMode.Value, LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (done == null)
				{
					done = new Dictionary<int, float>();
				}
				if (depthAt == null)
				{
					depthAt = new Dictionary<int, int>();
				}
				// a half-written pair is no record: keep only work that has its depth tag and is a usable amount
				pruneBuffer.Clear();
				foreach (KeyValuePair<int, float> kv in done)
				{
					if (!depthAt.ContainsKey(kv.Key) || !RM_DigProgressMath.Usable(kv.Value))
					{
						pruneBuffer.Add(kv.Key);
					}
				}
				for (int i = 0; i < pruneBuffer.Count; i++)
				{
					done.Remove(pruneBuffer[i]);
				}
				pruneBuffer.Clear();
				foreach (int key in depthAt.Keys)
				{
					if (!done.ContainsKey(key))
					{
						pruneBuffer.Add(key);
					}
				}
				for (int i = 0; i < pruneBuffer.Count; i++)
				{
					depthAt.Remove(pruneBuffer[i]);
				}
				pruneBuffer.Clear();
			}
		}
	}
}
