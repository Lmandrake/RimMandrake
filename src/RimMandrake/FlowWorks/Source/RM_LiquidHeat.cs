using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LIQUID_HEAT_PUSH_1 (FL-1 / X-8; the heat push closed BOILING_WATER_BURNS_1 §3 specified and never landed).
	/// Hot and icy liquid move the air temperature of the ROOM they stand in, through vanilla heat (Room.Temperature,
	/// the same field a heater writes). So a roofed hut over boiling water is warm, a pit room flooded with a hot liquid
	/// is a heat cell for PIT_TEMPERATURE_SOFTENING_1 (vanilla Heatstroke does the harm), and icy water chills.
	///
	/// MEASURED (decompiled 1.6, Room.PushHeat): a room that uses the outdoor temperature takes no heat at all. So an
	/// OPEN shore stays at the map's outdoor temperature, exactly as it would beside a vanilla heater; that is the
	/// "one kind of heat" ruling, not a gap. Enclose the shore and it warms.
	///
	/// Sources, resolved once per def and cached: an excavated cell's fluid (FluidDef.hot/cold, else the LiquidDef
	/// that names it as canalFluid); a natural terrain's LiquidDef (terrainSuite) hot/cold, else its
	/// <see cref="RM_LiquidHeatExtension"/> (terrains no LiquidDef claims, e.g. the Scald's RUT_ScaldWater*).
	/// Arithmetic and bounds: <see cref="RM_LiquidHeatMath"/>.
	/// </summary>
	public class RM_LiquidHeat
	{
		/// <summary>The natural (terrain) hot/cold cells are rescanned this often; terrain rarely changes.</summary>
		public const int RescanTicks = 15000;

		private int nextTick;
		private int nextRescanTick;
		private int cursor;
		private readonly List<int> naturalCells = new List<int>();
		private readonly List<int> naturalKinds = new List<int>();
		private readonly List<IntVec3> cells = new List<IntVec3>();
		private readonly List<float> energies = new List<float>();
		private readonly Dictionary<Room, float> hotByRoom = new Dictionary<Room, float>();
		private readonly Dictionary<Room, float> coldByRoom = new Dictionary<Room, float>();
		private readonly List<Room> neigh = new List<Room>();

		// Last interval, for the proof surface (RM_LiquidHeatProof).
		public int lastSourceCells;
		public int lastVisited;
		public int lastRoomsWarmed;
		public int lastRoomsChilled;
		public float lastEnergy;

		public void Tick(Map map, RM_MapComponent_Excavation ex)
		{
			int now = Find.TickManager.TicksGame;
			if (now < nextTick)
			{
				return;
			}
			nextTick = now + RM_LiquidHeatMath.IntervalTicks;
			if (!RimMandrakeFlowWorksSettings.liquidHeatPushEnabled)
			{
				lastSourceCells = lastVisited = lastRoomsWarmed = lastRoomsChilled = 0;
				lastEnergy = 0f;
				return;
			}
			if (now >= nextRescanTick)
			{
				nextRescanTick = now + RescanTicks;
				RescanNatural(map, ex);
			}
			Push(map, ex, RimMandrakeFlowWorksSettings.liquidHeatStrength);
		}

		/// <summary>Forget the natural-cell list so the next interval rebuilds it (a proof painted terrain).</summary>
		public void Invalidate()
		{
			nextRescanTick = 0;
			nextTick = 0;
		}

		private void RescanNatural(Map map, RM_MapComponent_Excavation ex)
		{
			naturalCells.Clear();
			naturalKinds.Clear();
			TerrainGrid grid = map.terrainGrid;
			int n = map.cellIndices.NumGridCells;
			for (int i = 0; i < n; i++)
			{
				int k = KindOfTerrain(grid.TerrainAt(i));
				if (k != 0 && !ex.IsExcavated(map.cellIndices.IndexToCell(i)))
				{
					naturalCells.Add(i);
					naturalKinds.Add(k);
				}
			}
			cursor = 0;
		}

		private void Push(Map map, RM_MapComponent_Excavation ex, float strength)
		{
			// Gather this interval's sources: every wet hot/cold excavated cell, plus a budgeted slice of the natural list.
			cells.Clear();
			energies.Clear();
			foreach (IntVec3 c in ex.ExcavatedCells)
			{
				int f = ex.FillAt(c);
				if (f <= 0)
				{
					continue;
				}
				int k = KindOfFluid(ex.FluidAt(c) ?? ex.ActiveFluid);
				if (k != 0)
				{
					cells.Add(c);
					energies.Add(RM_LiquidHeatMath.CellEnergy(k, f, strength));
				}
			}
			int excavatedSources = cells.Count;
			int total = excavatedSources + naturalCells.Count;
			lastSourceCells = total;
			int visit = RM_LiquidHeatMath.Budget(total, out float scale);
			hotByRoom.Clear();
			coldByRoom.Clear();
			lastVisited = 0;
			// Excavated cells first (few, and the pit case matters), then the natural ring buffer.
			for (int j = 0; j < excavatedSources && lastVisited < visit; j++, lastVisited++)
			{
				Credit(map, cells[j], energies[j] * scale);
			}
			int natural = naturalCells.Count;
			for (int j = 0; j < natural && lastVisited < visit; j++, lastVisited++)
			{
				if (cursor >= natural)
				{
					cursor = 0;
				}
				int i = naturalCells[cursor];
				int k = naturalKinds[cursor];
				cursor++;
				Credit(map, map.cellIndices.IndexToCell(i),
					RM_LiquidHeatMath.CellEnergy(k, RM_LiquidHeatMath.NaturalCellLevels, strength) * scale);
			}
			lastEnergy = 0f;
			lastRoomsWarmed = Apply(hotByRoom, strength);
			lastRoomsChilled = Apply(coldByRoom, strength);
		}

		/// <summary>Vanilla GenTemperature.PushHeat's own routing: the cell's room, else split over its neighbours'
		/// rooms (deep water is impassable and has none). Outdoor rooms are dropped here, as Room.PushHeat drops them.</summary>
		private void Credit(Map map, IntVec3 c, float energy)
		{
			if (energy == 0f)
			{
				return;
			}
			Dictionary<Room, float> into = energy > 0f ? hotByRoom : coldByRoom;
			Room room = c.GetRoom(map);
			if (room != null)
			{
				Add(into, room, energy);
				return;
			}
			neigh.Clear();
			for (int i = 0; i < 8; i++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[i];
				if (n.InBounds(map))
				{
					Room r = n.GetRoom(map);
					if (r != null)
					{
						neigh.Add(r);
					}
				}
			}
			for (int i = 0; i < neigh.Count; i++)
			{
				Add(into, neigh[i], energy / neigh.Count);
			}
		}

		private static void Add(Dictionary<Room, float> into, Room room, float energy)
		{
			if (room.UsesOutdoorTemperature)
			{
				return;
			}
			into.TryGetValue(room, out float e);
			into[room] = e + energy;
		}

		private int Apply(Dictionary<Room, float> rooms, float strength)
		{
			int n = 0;
			foreach (KeyValuePair<Room, float> kv in rooms)
			{
				Room room = kv.Key;
				float e = RM_LiquidHeatMath.RoomEnergy(kv.Value, room.Temperature, room.CellCount, strength);
				if (e != 0f && room.PushHeat(e))
				{
					lastEnergy += e;
					n++;
				}
			}
			return n;
		}

		// ── identity: which defs are hot (+1) or cold (-1), cached once per def ──────────────────────────────────

		private static Dictionary<FluidDef, int> fluidKinds;
		private static Dictionary<TerrainDef, int> terrainKinds;

		public static int KindOfFluid(FluidDef f)
		{
			if (f == null)
			{
				return 0;
			}
			if (fluidKinds == null)
			{
				fluidKinds = new Dictionary<FluidDef, int>();
			}
			if (fluidKinds.TryGetValue(f, out int k))
			{
				return k;
			}
			k = RM_LiquidHeatMath.Kind(f.hot, f.cold);
			if (k == 0)
			{
				foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
				{
					if (l.canalFluid == f)
					{
						k = RM_LiquidHeatMath.Kind(l.hot, l.cold);
						break;
					}
				}
			}
			fluidKinds[f] = k;
			return k;
		}

		public static int KindOfTerrain(TerrainDef t)
		{
			if (t == null)
			{
				return 0;
			}
			if (terrainKinds == null)
			{
				var d = new Dictionary<TerrainDef, int>();
				foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
				{
					int lk = RM_LiquidHeatMath.Kind(l.hot, l.cold);
					if (lk == 0 || l.terrainSuite == null)
					{
						continue;
					}
					foreach (TerrainDef s in new[] { l.terrainSuite.shallow, l.terrainSuite.deep, l.terrainSuite.chestDeep })
					{
						if (s != null && !d.ContainsKey(s))
						{
							d[s] = lk;
						}
					}
				}
				terrainKinds = d;
			}
			if (terrainKinds.TryGetValue(t, out int k))
			{
				return k;
			}
			RM_LiquidHeatExtension ext = t.GetModExtension<RM_LiquidHeatExtension>();
			k = ext != null ? RM_LiquidHeatMath.Kind(ext.hot, ext.cold) : 0;
			terrainKinds[t] = k;
			return k;
		}
	}

	/// <summary>LIQUID_HEAT_PUSH_1: marks a liquid TERRAIN that no LiquidDef claims as hot or cold, so it warms or
	/// chills the room it lies in (RM_LiquidHeat). Add it by a FindMod-guarded patch from the mod that owns the terrain
	/// (a missing mod-extension class discards the whole def).</summary>
	public class RM_LiquidHeatExtension : DefModExtension
	{
		public bool hot;
		public bool cold;

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string e in base.ConfigErrors())
			{
				yield return e;
			}
			if (hot == cold)
			{
				yield return "RM_LiquidHeatExtension: set exactly one of hot or cold (both or neither pushes nothing).";
			}
		}
	}

	/// <summary>jawa/static_call read surface for the liquid_heat extension chain (northstar/extensions.py). Dev only.</summary>
	public static class RM_LiquidHeatProof
	{
		/// <summary>"x,z": "HEAT kind=K temp=T roomCells=N outdoor=B | sources=S visited=V warmed=W chilled=C energy=E".
		/// K is the heat kind of the cell's terrain (or of its fill, if it is a wet excavated cell).</summary>
		public static string ProofHeat(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return "REFUSED: no excavation component on the current map";
			}
			string[] p = (arg ?? "").Trim().Split(',');
			if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
			{
				return "REFUSED: arg must be x,z";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			if (!c.InBounds(map))
			{
				return "REFUSED: out of bounds";
			}
			int kind = ex.IsExcavated(c) && ex.FillAt(c) > 0
				? RM_LiquidHeat.KindOfFluid(ex.FluidAt(c) ?? ex.ActiveFluid)
				: RM_LiquidHeat.KindOfTerrain(c.GetTerrain(map));
			Room room = c.GetRoom(map);
			RM_LiquidHeat h = ex.LiquidHeat;
			return "HEAT kind=" + kind
				+ " temp=" + (room != null ? room.Temperature.ToString("F1") : "none")
				+ " roomCells=" + (room?.CellCount ?? 0)
				+ " outdoor=" + (room?.UsesOutdoorTemperature ?? true)
				+ " | sources=" + h.lastSourceCells + " visited=" + h.lastVisited
				+ " warmed=" + h.lastRoomsWarmed + " chilled=" + h.lastRoomsChilled
				+ " energy=" + h.lastEnergy.ToString("F0");
		}

		/// <summary>Rebuild the natural hot/cold cell list on the next interval (after a proof paints terrain).</summary>
		public static string ProofRescan(string arg)
		{
			RM_MapComponent_Excavation ex = Find.CurrentMap?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return "REFUSED: no excavation component on the current map";
			}
			ex.LiquidHeat.Invalidate();
			return "RESCAN queued";
		}
	}
}
