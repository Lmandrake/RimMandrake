using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>
	/// SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (design §4): the map's sprinkled cells (per cell: wet-until tick, the liquid key that
	/// wets it, the head that paid) and the pulse clock for every registered head. Heads register on spawn; the clock runs
	/// here, so a head needs no ticker of its own (VFE's sprinkler has none). Saved sparse: only cells still wet.
	///
	/// THE READ SEAM: <see cref="WetAt"/> and <see cref="Spend"/> are static and take only Verse types, so ExplosiveGrowth reads
	/// them reflection-soft (_Shared/FlowWorksSprinklerRead.cs); FlowWorks never references ExplosiveGrowth.
	/// </summary>
	public class RM_MapComponent_Sprinklers : MapComponent
	{
		private RM_SprinkledGrid grid;
		private readonly List<CompRM_SprinklerBase> heads = new List<CompRM_SprinklerBase>();

		/// <summary>State read (probe, selftests): paid pulses and units sprayed this session, map-wide.</summary>
		public static int Pulses, SprayedUnits;

		public RM_MapComponent_Sprinklers(Map map) : base(map)
		{
		}

		public IReadOnlyList<CompRM_SprinklerBase> Heads => heads;

		private static Map cachedMap;
		private static RM_MapComponent_Sprinklers cachedComp;

		/// <summary>One-slot cache: WetAt is read per plant tick by ExplosiveGrowth; GetComponent walks the component list.</summary>
		public static RM_MapComponent_Sprinklers Of(Map map)
		{
			if (map == null) return null;
			if (map == cachedMap && cachedComp != null && cachedComp.map == map) return cachedComp;
			RM_MapComponent_Sprinklers c = map.GetComponent<RM_MapComponent_Sprinklers>();
			if (c != null) { cachedMap = map; cachedComp = c; }
			return c;
		}

		private RM_SprinkledGrid Grid => grid ?? (grid = new RM_SprinkledGrid(map.cellIndices.NumGridCells));

		public void Register(CompRM_SprinklerBase h)
		{
			if (h != null && !heads.Contains(h)) heads.Add(h);
		}

		public void Deregister(CompRM_SprinklerBase h) => heads.Remove(h);

		public override void MapComponentTick()
		{
			int now = Find.TickManager.TicksGame;
			RM_SprinklerSprayFx.Tick(map, heads, now);   // visual only; returns at once off screen or with the setting off
			if (heads.Count == 0) return;
			for (int i = heads.Count - 1; i >= 0; i--)
			{
				CompRM_SprinklerBase h = heads[i];
				if (h?.parent == null || !h.parent.Spawned || h.parent.Map != map)
				{
					heads.RemoveAt(i);
					continue;
				}
				// a rare-tick cadence per head, staggered by its id
				if ((now + h.parent.thingIDNumber) % 250 != 0) continue;
				try
				{
					h.RareTick(now);
				}
				catch (System.Exception e)
				{
					Log.ErrorOnce("[FlowWorks] sprinkler " + h.parent + " failed its pulse: " + e, 0x5B71A1 ^ h.parent.thingIDNumber);
				}
			}
		}

		public void Wet(List<IntVec3> cells, string liquidKey, int until, int headId)
		{
			RM_SprinkledGrid g = Grid;
			CellIndices idx = map.cellIndices;
			foreach (IntVec3 c in cells) g.Wet(idx.CellToIndex(c), liquidKey, until, headId);
		}

		/// <summary>The liquid key wetting <paramref name="c"/> now (a FluidDef defName, e.g. RM_Fluid_Water), or null.</summary>
		public string WetKey(IntVec3 c, int now) => grid == null || !c.InBounds(map) ? null : grid.WetBy(map.cellIndices.CellToIndex(c), now);

		public bool WetByOther(IntVec3 c, int headId, int now) => grid != null && c.InBounds(map) && grid.WetByOther(map.cellIndices.CellToIndex(c), headId, now);

		public int LiveCells(int now) => grid?.LiveCells(now) ?? 0;

		// ---------------------------------------------------------------- the read seam (ExplosiveGrowth, reflection-soft)
		/// <summary>Is <paramref name="c"/> sprinkled now? <paramref name="liquidKey"/> = the FluidDef defName of what wets it.
		/// False while sprinklersEnabled is off.</summary>
		public static bool WetAt(Map map, IntVec3 c, out string liquidKey)
		{
			liquidKey = null;
			if (!RM_SprinklerSettings.sprinklersEnabled && !RM_SprinklerSettings.vfeSprinklerAdapterEnabled) return false;
			RM_MapComponent_Sprinklers comp = Of(map);
			if (comp == null) return false;
			liquidKey = comp.WetKey(c, Find.TickManager.TicksGame);
			return liquidKey != null;
		}

		/// <summary>EC3: a crop that fruited on a sprinkled cell spends it; dry until the next paid pulse. True if it was wet.</summary>
		public static bool Spend(Map map, IntVec3 c)
		{
			RM_MapComponent_Sprinklers comp = Of(map);
			if (comp?.grid == null || !c.InBounds(map)) return false;
			return comp.grid.Spend(map.cellIndices.CellToIndex(c), Find.TickManager.TicksGame);
		}

		// ---------------------------------------------------------------- save (sparse: wet cells only)
		public override void ExposeData()
		{
			base.ExposeData();
			List<int> cells = null, untils = null, owners = null;
			List<string> keys = null;
			if (Scribe.mode == LoadSaveMode.Saving && grid != null)
			{
				int now = Find.TickManager.TicksGame;
				cells = new List<int>(); untils = new List<int>(); owners = new List<int>(); keys = new List<string>();
				for (int i = 0; i < grid.wetUntil.Length; i++)
				{
					if (!RM_SprinklerKernel.IsWet(grid.wetUntil[i], now)) continue;
					cells.Add(i); untils.Add(grid.wetUntil[i]); owners.Add(grid.owner[i]); keys.Add(grid.palette[grid.liquid[i]] ?? "");
				}
			}
			Scribe_Collections.Look(ref cells, "sprinkledCells", LookMode.Value);
			Scribe_Collections.Look(ref untils, "sprinkledUntil", LookMode.Value);
			Scribe_Collections.Look(ref owners, "sprinkledOwner", LookMode.Value);
			Scribe_Collections.Look(ref keys, "sprinkledLiquid", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.LoadingVars && cells != null && untils != null && keys != null
			    && cells.Count == untils.Count && cells.Count == keys.Count)
			{
				RM_SprinkledGrid g = Grid;
				for (int i = 0; i < cells.Count; i++)
				{
					g.Wet(cells[i], keys[i] == "" ? null : keys[i], untils[i], owners != null && i < owners.Count ? owners[i] : 0);
				}
			}
		}
	}
}
