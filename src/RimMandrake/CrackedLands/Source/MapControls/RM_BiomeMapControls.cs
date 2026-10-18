using System.Collections.Generic;
using System.Text;
using LudeonTK;
using RimMandrake.FlowWorks.MapControls;
using RimWorld;
using Verse;

namespace RimMandrake.CrackedLands.MapControls
{
	/// <summary>FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: Baroque Biomes' map controls (flood trigger, soak zone) -- the
	/// lookups the canyon flood reads, the bridge surface (jawa/static_call, args '|'-separated; review_map.py and proofs place
	/// and fire them with it) and the debug actions. Answers are "OK ..." or "REFUSED: why".</summary>
	public static class RM_BiomeMapControls
	{
		public const string TriggerDef = "RM_FloodTrigger";
		public const string SoakZoneDef = "RM_SoakZone";

		private static ThingDef triggerDef, soakDef;

		private static ThingDef TDef => triggerDef ?? (triggerDef = DefDatabase<ThingDef>.GetNamedSilentFail(TriggerDef));
		private static ThingDef SDef => soakDef ?? (soakDef = DefDatabase<ThingDef>.GetNamedSilentFail(SoakZoneDef));

		/// <summary>Flood triggers work: their own switch AND FlowWorks' map controls master switch (they are FlowWorks map
		/// controls, whose inspect pane already reports that switch).</summary>
		public static bool FloodTriggersOn => RM_CrackedLandsSettings.floodTriggersEnabled && RM_MapControlSettings.mapControlsEnabled;

		public static IEnumerable<Building_RM_FloodTrigger> Triggers(Map map)
		{
			if (map == null || TDef == null)
			{
				yield break;
			}
			List<Thing> things = map.listerThings.ThingsOfDef(TDef);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Building_RM_FloodTrigger t)
				{
					yield return t;
				}
			}
		}

		public static bool AnyClockTrigger(Map map)
		{
			if (map == null || TDef == null)
			{
				return false;
			}
			List<Thing> things = map.listerThings.ThingsOfDef(TDef);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Building_RM_FloodTrigger t && t.active && t.onClock)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>One active trigger on the clock, chosen at random; null when none.</summary>
		public static Thing PickClockTrigger(Map map)
		{
			List<Building_RM_FloodTrigger> on = new List<Building_RM_FloodTrigger>();
			foreach (Building_RM_FloodTrigger t in Triggers(map))
			{
				if (t.active && t.onClock)
				{
					on.Add(t);
				}
			}
			return on.Count == 0 ? null : on.RandomElement();
		}

		public static Building_RM_FloodTrigger TriggerAt(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return null;
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t is Building_RM_FloodTrigger ft)
				{
					return ft;
				}
			}
			return null;
		}

		// ── bridge surface ───────────────────────────────────────────────

		/// <summary>Place a flood trigger on the current map. onClock: the flood clock brings its floods in here; spill: an
		/// ordinary canyon flood from here instead of the channel only; maxCells 0 = the map's flood size.</summary>
		public static string PlaceFloodTrigger(IntVec3 cell, bool onClock, bool spill, int maxCells)
		{
			if (!Spawn(TDef, cell, out Thing t, out string why))
			{
				return why;
			}
			Building_RM_FloodTrigger ft = (Building_RM_FloodTrigger)t;
			ft.onClock = onClock;
			ft.spill = spill;
			ft.maxCells = maxCells < 0 ? 0 : maxCells;
			return "OK " + ft.StateLine();
		}

		/// <summary>Press the trigger at cell: warn=false floods now, warn=true runs the warning first.</summary>
		public static string FireFloodTrigger(IntVec3 cell, bool warn)
		{
			Building_RM_FloodTrigger ft = TriggerAt(Find.CurrentMap, cell);
			return ft == null ? "REFUSED: no flood trigger at " + cell : ft.Fire(warn);
		}

		/// <summary>Place a soak zone: radius r soaks a (2r+1)-square; hoursPerDay 1..24.</summary>
		public static string PlaceSoakZone(IntVec3 cell, int radius, float hoursPerDay)
		{
			if (radius < 0 || radius > 12)
			{
				return "REFUSED: radius " + radius + " (0..12)";
			}
			if (!Spawn(SDef, cell, out Thing t, out string why))
			{
				return why;
			}
			Building_RM_SoakZone z = (Building_RM_SoakZone)t;
			z.radius = radius;
			z.hoursPerDay = UnityEngine.Mathf.Clamp(hoursPerDay, 1f, 24f);
			z.TickRare();     // soak at once, not up to 250 ticks later
			return "OK " + z.StateLine();
		}

		/// <summary>Remove the flood trigger or soak zone at cell.</summary>
		public static string RemoveAt(IntVec3 cell)
		{
			Map map = Find.CurrentMap;
			if (map == null || !cell.InBounds(map))
			{
				return "REFUSED: no current map or " + cell + " off it";
			}
			foreach (Thing t in new List<Thing>(cell.GetThingList(map)))
			{
				if (t is Building_RM_FloodTrigger || t is Building_RM_SoakZone)
				{
					string id = t.ThingID;
					t.Destroy(DestroyMode.Vanish);
					return "OK removed " + id;
				}
			}
			return "REFUSED: no flood trigger or soak zone at " + cell;
		}

		/// <summary>Every flood trigger and soak zone on the current map, one line each, then the flood state.</summary>
		public static string Report()
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "REFUSED: no current map";
			}
			StringBuilder sb = new StringBuilder();
			int n = 0;
			foreach (Building_RM_FloodTrigger t in Triggers(map))
			{
				sb.Append(t.StateLine()).Append('\n');
				n++;
			}
			if (SDef != null)
			{
				foreach (Thing t in map.listerThings.ThingsOfDef(SDef))
				{
					if (t is Building_RM_SoakZone z)
					{
						sb.Append(z.StateLine()).Append('\n');
						n++;
					}
				}
			}
			sb.Append("controls=" + n + " floodTriggersOn=" + FloodTriggersOn + " soakZonesEnabled=" + RM_CrackedLandsSettings.soakZonesEnabled
				+ " flood: " + (map.GetComponent<RM_MapComponent_CanyonFlood>()?.DebugStateReport() ?? "ABSENT"));
			return sb.ToString();
		}

		private static bool Spawn(ThingDef def, IntVec3 cell, out Thing t, out string why)
		{
			t = null;
			why = null;
			Map map = Find.CurrentMap;
			if (map == null)
			{
				why = "REFUSED: no current map";
				return false;
			}
			if (def == null)
			{
				why = "REFUSED: map control def not loaded";
				return false;
			}
			if (!cell.InBounds(map))
			{
				why = "REFUSED: " + cell + " is off the map";
				return false;
			}
			foreach (Thing other in cell.GetThingList(map))
			{
				if (other is Building_RM_MapControl || other is Building_RM_SoakZone)
				{
					why = "REFUSED: a map control already stands at " + cell + " (" + other.ThingID + ")";
					return false;
				}
			}
			t = GenSpawn.Spawn(ThingMaker.MakeThing(def), cell, map);
			return true;
		}

		// ── debug actions (dev mode) ──────────────────────────────────────

		private const string CAT = "RMCrackedLands";
		private const string TAG = "[RMCrackedLandsDebug] ";

		[DebugAction(CAT, "Place flood trigger (aimed at a canal)", allowedGameStates = AllowedGameStates.PlayingOnMap,
			actionType = DebugActionType.ToolMap)]
		private static void DebugPlaceTrigger()
		{
			Log.Message(TAG + PlaceFloodTrigger(UI.MouseCell(), true, false, 0));
		}

		[DebugAction(CAT, "Place soak zone (5x5, always)", allowedGameStates = AllowedGameStates.PlayingOnMap,
			actionType = DebugActionType.ToolMap)]
		private static void DebugPlaceSoakZone()
		{
			Log.Message(TAG + PlaceSoakZone(UI.MouseCell(), 2, 24f));
		}

		[DebugAction(CAT, "Report flood triggers and soak zones (current map)", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void DebugReport()
		{
			Log.Message(TAG + Report());
		}
	}
}
