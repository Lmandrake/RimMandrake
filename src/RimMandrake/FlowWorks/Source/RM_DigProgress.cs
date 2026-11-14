using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_KEEP_DIG_PROGRESS_ACROSS_MEALS_AND_NAPS: shovel work done on a square whose dig or fill was broken
	/// off (a meal, sleep, a draft, a lost shovel) and is not finished; the next job on the square, by anyone, carries on
	/// from it (<see cref="RM_JobDriver_ShovelFloor"/>). A running job holds its own work (vanilla's workLeft, saved with the
	/// job); only parked work lives here. Dropped when the order is removed (cancelled, landed: the RemoveDesignation postfix
	/// below) or the square's depth moved since it was parked (read at Take). No tick: it costs nothing between jobs.</summary>
	public class RM_MapComponent_DigProgress : MapComponent
	{
		private RM_DigProgressStore store = new RM_DigProgressStore();

		private List<int> saveKeys;

		private List<float> saveWork;

		private List<int> saveDepths;

		public RM_MapComponent_DigProgress(Map map) : base(map)
		{
		}

		public int Count => store.Count;

		private int IndexOf(IntVec3 c)
		{
			return c.InBounds(map) ? map.cellIndices.CellToIndex(c) : -1;
		}

		private int DepthNow(IntVec3 c)
		{
			return map.GetComponent<RM_MapComponent_Excavation>()?.ExcavatedDepthAt(c) ?? 0;
		}

		public float Take(IntVec3 c, bool fill)
		{
			int i = IndexOf(c);
			return i < 0 ? 0f : store.Take(i, fill, DepthNow(c));
		}

		public float Peek(IntVec3 c, bool fill)
		{
			int i = IndexOf(c);
			return i < 0 ? 0f : store.Peek(i, fill, DepthNow(c));
		}

		public void Put(IntVec3 c, bool fill, float work)
		{
			int i = IndexOf(c);
			if (i >= 0)
			{
				store.Put(i, fill, work, DepthNow(c));
			}
		}

		public void Clear(IntVec3 c, bool fill)
		{
			store.Clear(IndexOf(c), fill);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				saveKeys = new List<int>();
				saveWork = new List<float>();
				saveDepths = new List<int>();
				store.ToLists(saveKeys, saveWork, saveDepths);
			}
			Scribe_Collections.Look(ref saveKeys, "rmDigProgressKeys", LookMode.Value);
			Scribe_Collections.Look(ref saveWork, "rmDigProgressWork", LookMode.Value);
			Scribe_Collections.Look(ref saveDepths, "rmDigProgressDepths", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				store = RM_DigProgressStore.FromLists(saveKeys, saveWork, saveDepths, map.cellIndices.NumGridCells);
			}
			if (Scribe.mode == LoadSaveMode.Saving || Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				saveKeys = null;
				saveWork = null;
				saveDepths = null;
			}
		}
	}

	/// <summary>A dig or fill order removed (cancelled by the player, landed by the work toil, dropped as stale) takes its
	/// parked work with it. Every removal path in vanilla funnels through RemoveDesignation (Delete, TryRemoveDesignation,
	/// RemoveAllDesignationsOn/OfDef). If this patch failed to apply, parked work still dies when the depth moves.</summary>
	[HarmonyPatch(typeof(DesignationManager), nameof(DesignationManager.RemoveDesignation))]
	[RimMandrake.Shared.PatchFeature("Dig and fill work kept per square")]
	public static class RM_Patch_DigProgressClearsWithItsOrder
	{
		[HarmonyPostfix]
		public static void Postfix(Designation des, Map ___map)
		{
			if (des?.def == null || ___map == null)
			{
				return;
			}
			bool fill;
			if (des.def == RimMandrakeFlowWorks_DefOf.RM_DigCanal)
			{
				fill = false;
			}
			else if (des.def == RimMandrakeFlowWorks_DefOf.RM_FillInCanal)
			{
				fill = true;
			}
			else
			{
				return;
			}
			___map.GetComponent<RM_MapComponent_DigProgress>()?.Clear(des.target.Cell, fill);
		}
	}
}
