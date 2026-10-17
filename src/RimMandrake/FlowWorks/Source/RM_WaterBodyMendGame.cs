// FISH_ROLL_MEND_PONDS_BORN_BARREN (plan P13): the game side of RM_WaterBodyMath.cs. Patches the vanilla 1.6 (Odyssey) water-body
// tracker around its one live entry point, WaterBodyTracker.Notify_TerrainChanged (called from TerrainGrid.DoTerrainChangedEffects
// only while Playing and only when a square's waterBodyType changes), and the water-plant kill in DoTerrainChangedEffects.
//
// Map generation is untouched: ConstructBodies (map init and load) builds bodies without Notify_TerrainChanged, so no extra Rand
// call ever runs during mapgen.
//
// DUG WATER (P14 hook): today a dug canal's water is TEMP terrain over a channel floor, and GridsUtility.GetWaterBodyType reads
// under the temp layer, so dug water forms no vanilla body and none of this runs for it. P14 (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD,
// BENCH) moves wet dug squares to the BASE layer; from then every square it writes goes through Notify_TerrainChanged and gets all
// three mends with no further wiring. The plant grace already covers dug squares (RM_MapComponent_Excavation.IsExcavated).
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	public static class RM_WaterMendSettings
	{
		/// <summary>Master: the three water-body mends (fish roll as a body grows, fish and zone come back on refill, splits).</summary>
		public static bool waterBodyMendsEnabled = true;
		public static bool fishRollOnGrowth = true;
		/// <summary>Engine Q5a (defaulted, veto-able): the same fish return when a dried pond refills.</summary>
		public static bool fishReturnOnRefill = true;
		public static bool fishingZoneReturnOnRefill = true;
		public static bool waterBodySplitEnabled = true;
		/// <summary>Engine Q6a (defaulted, veto-able): water plants live through short changes of water depth.</summary>
		public static bool waterPlantGraceEnabled = true;
		public static float waterPlantDeepToleranceMetres = RM_WaterBodyMath.DefaultPlantDeepToleranceMetres;
		public static float waterPlantGraceHours = RM_WaterBodyMath.DefaultPlantGraceHours;

		public static RM_WaterMendFlags Flags => new RM_WaterMendFlags
		{
			rollOnGrowth = waterBodyMendsEnabled && fishRollOnGrowth,
			fishReturn = waterBodyMendsEnabled && fishReturnOnRefill,
			zoneReturn = waterBodyMendsEnabled && fishingZoneReturnOnRefill,
			split = waterBodyMendsEnabled && waterBodySplitEnabled,
		};

		public static void ExposeData()
		{
			Scribe_Values.Look(ref waterBodyMendsEnabled, "waterBodyMendsEnabled", true);
			Scribe_Values.Look(ref fishRollOnGrowth, "fishRollOnGrowth", true);
			Scribe_Values.Look(ref fishReturnOnRefill, "fishReturnOnRefill", true);
			Scribe_Values.Look(ref fishingZoneReturnOnRefill, "fishingZoneReturnOnRefill", true);
			Scribe_Values.Look(ref waterBodySplitEnabled, "waterBodySplitEnabled", true);
			Scribe_Values.Look(ref waterPlantGraceEnabled, "waterPlantGraceEnabled", true);
			Scribe_Values.Look(ref waterPlantDeepToleranceMetres, "waterPlantDeepToleranceMetres", RM_WaterBodyMath.DefaultPlantDeepToleranceMetres);
			Scribe_Values.Look(ref waterPlantGraceHours, "waterPlantGraceHours", RM_WaterBodyMath.DefaultPlantGraceHours);
		}

		public static void ResetToShipped()
		{
			waterBodyMendsEnabled = fishRollOnGrowth = fishReturnOnRefill = fishingZoneReturnOnRefill = waterBodySplitEnabled = true;
			waterPlantGraceEnabled = true;
			waterPlantDeepToleranceMetres = RM_WaterBodyMath.DefaultPlantDeepToleranceMetres;
			waterPlantGraceHours = RM_WaterBodyMath.DefaultPlantGraceHours;
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Fish, fishing zones and water plants in ponds that rise and fall");
			list.CheckboxLabeled("Fish and fishing zones keep up with ponds that grow, dry out or split", ref waterBodyMendsEnabled,
				"Fixes three base-game gaps in how it tracks bodies of water. Off: the base game's behaviour for all three below "
				+ "(a pond that starts small never gets fish, a pond that dries out never gets its fish or its fishing zone back, "
				+ "and a pond that dries in two stays one pond until the game is reloaded). Takes effect at once.");
			GUI.enabled = waterBodyMendsEnabled;
			list.CheckboxLabeled("  A pond that grows big enough gets fish", ref fishRollOnGrowth,
				"The game decides a pond's fish once, when it first appears. A pond that fills square by square starts at one "
				+ "square, too small for fish, and stays fishless forever. On: each time a fishless pond grows past 75, 100 and "
				+ "200 squares it gets the game's own chance of fish for its size (certain by 200), and a big one past 400, 1,600 "
				+ "and 6,000 squares its chance of an uncommon kind. Off: the base game's single roll.");
			list.CheckboxLabeled("  A pond that dries out gets the same fish back when it refills", ref fishReturnOnRefill,
				"On (shipped): a square that dries out remembers its pond's fish (and how many were left); when water returns "
				+ "there, the pond has the same kinds again. Off: a refilled pond is treated as new and, if the setting above is "
				+ "on, rolls fresh fish as it grows; with both off it never gets fish again (the base game).");
			list.CheckboxLabeled("  Fishing zone squares come back when the water does", ref fishingZoneReturnOnRefill,
				"The game deletes a fishing zone's square the moment it dries out, and deletes the zone when its last square "
				+ "dries. On: each square rejoins its zone when it is water again; a zone that drying emptied is made again with "
				+ "its name, colour and settings. A zone you deleted yourself is never brought back. Off: the base game.");
			list.CheckboxLabeled("  A pond that dries in two becomes two ponds", ref waterBodySplitEnabled,
				"On: when drying cuts a pond in two, each part is its own pond at once, with the same fish and a share of them "
				+ "by size (the base game keeps them as one until the next load, which skews fishing and freezing). Off: the "
				+ "base game.");
			GUI.enabled = true;
			list.CheckboxLabeled("Reeds, lilies and lotus live through water that rises and falls", ref waterPlantGraceEnabled,
				"In the base game a water plant dies the moment its square turns to deep water or dries out, so a pond a pump "
				+ "keeps raising and lowering loses its reeds every cycle. On: on squares this mod moves water on (ponds and dug "
				+ "cells), water up to the depth below never harms them, and dry ground or deeper water harms them only after "
				+ "the time below; then they wither as the base game has them. Elsewhere the base game rules. Off: the base game.");
			GUI.enabled = waterPlantGraceEnabled;
			list.Label("  Tolerated depth: up to " + (RM_WaterBodyMath.DeepWaterMetres + waterPlantDeepToleranceMetres).ToString("0.0#")
				+ " m of water (2 m + " + waterPlantDeepToleranceMetres.ToString("0.0#") + " m; shipped 3 m)");
			waterPlantDeepToleranceMetres = Mathf.Round(list.Slider(waterPlantDeepToleranceMetres, 0f, 5f) * 4f) / 4f;
			list.Label("  Survive dry ground or deeper water for " + waterPlantGraceHours.ToString("0") + " h (shipped 24)");
			waterPlantGraceHours = Mathf.Round(list.Slider(waterPlantGraceHours, 0f, 240f));
			GUI.enabled = true;
			if (list.ButtonText("Reset this section to shipped values"))
			{
				ResetToShipped();
			}
		}
	}

	/// <summary>Per map: the fish and fishing zones of squares that dried out, and how long each water plant has been on a square
	/// that no longer suits it. Saved with the map.</summary>
	public class RM_MapComponent_WaterMend : MapComponent
	{
		public RM_FishMemoryBook book = new RM_FishMemoryBook();
		public Dictionary<int, int> plantSince = new Dictionary<int, int>();

		public RM_MapComponent_WaterMend(Map map) : base(map)
		{
		}

		public static RM_MapComponent_WaterMend Of(Map map) => map?.GetComponent<RM_MapComponent_WaterMend>();

		public override void ExposeData()
		{
			base.ExposeData();
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				book.Prune();
			}
			List<int> fc = null, fr = null, rid = null, rtype = null, zc = null, zid = null;
			List<float> rpop = null;
			List<string> rcommon = null, runcommon = null;
			List<int> mid = null, mrepeatMode = null, mrepeatCount = null, mtargetCount = null, munpause = null, pc = null, ps = null;
			List<bool> mdied = null, mhidden = null, mallowed = null, mpause = null;
			List<string> mlabel = null;
			List<float> mpct = null, mr = null, mg = null, mb = null, ma = null;
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				fc = book.fishByCell.Keys.ToList();
				fr = fc.Select(k => book.fishByCell[k]).ToList();
				var recs = book.records.Values.ToList();
				rid = recs.Select(r => r.id).ToList();
				rtype = recs.Select(r => r.waterType).ToList();
				rpop = recs.Select(r => r.population).ToList();
				rcommon = recs.Select(r => string.Join(",", r.common)).ToList();
				runcommon = recs.Select(r => string.Join(",", r.uncommon)).ToList();
				zc = book.zoneByCell.Keys.ToList();
				zid = zc.Select(k => book.zoneByCell[k]).ToList();
				var ms = book.zones.Values.ToList();
				mid = ms.Select(m => m.zoneId).ToList();
				mdied = ms.Select(m => m.diedDry).ToList();
				mlabel = ms.Select(m => m.label ?? "").ToList();
				mr = ms.Select(m => m.r).ToList();
				mg = ms.Select(m => m.g).ToList();
				mb = ms.Select(m => m.b).ToList();
				ma = ms.Select(m => m.a).ToList();
				mhidden = ms.Select(m => m.hidden).ToList();
				mallowed = ms.Select(m => m.allowed).ToList();
				mrepeatMode = ms.Select(m => m.repeatMode).ToList();
				mrepeatCount = ms.Select(m => m.repeatCount).ToList();
				mtargetCount = ms.Select(m => m.targetCount).ToList();
				mpct = ms.Select(m => m.targetPopulationPct).ToList();
				mpause = ms.Select(m => m.pauseWhenSatisfied).ToList();
				munpause = ms.Select(m => m.unpauseAtCount).ToList();
				pc = plantSince.Keys.ToList();
				ps = pc.Select(k => plantSince[k]).ToList();
			}
			Scribe_Values.Look(ref book.nextId, "nextId", 1);
			Scribe_Collections.Look(ref fc, "fishCells", LookMode.Value);
			Scribe_Collections.Look(ref fr, "fishRecords", LookMode.Value);
			Scribe_Collections.Look(ref rid, "recordIds", LookMode.Value);
			Scribe_Collections.Look(ref rtype, "recordTypes", LookMode.Value);
			Scribe_Collections.Look(ref rpop, "recordPopulations", LookMode.Value);
			Scribe_Collections.Look(ref rcommon, "recordCommon", LookMode.Value);
			Scribe_Collections.Look(ref runcommon, "recordUncommon", LookMode.Value);
			Scribe_Collections.Look(ref zc, "zoneCells", LookMode.Value);
			Scribe_Collections.Look(ref zid, "zoneCellIds", LookMode.Value);
			Scribe_Collections.Look(ref mid, "zoneIds", LookMode.Value);
			Scribe_Collections.Look(ref mdied, "zoneDiedDry", LookMode.Value);
			Scribe_Collections.Look(ref mlabel, "zoneLabels", LookMode.Value);
			Scribe_Collections.Look(ref mr, "zoneR", LookMode.Value);
			Scribe_Collections.Look(ref mg, "zoneG", LookMode.Value);
			Scribe_Collections.Look(ref mb, "zoneB", LookMode.Value);
			Scribe_Collections.Look(ref ma, "zoneA", LookMode.Value);
			Scribe_Collections.Look(ref mhidden, "zoneHidden", LookMode.Value);
			Scribe_Collections.Look(ref mallowed, "zoneAllowed", LookMode.Value);
			Scribe_Collections.Look(ref mrepeatMode, "zoneRepeatMode", LookMode.Value);
			Scribe_Collections.Look(ref mrepeatCount, "zoneRepeatCount", LookMode.Value);
			Scribe_Collections.Look(ref mtargetCount, "zoneTargetCount", LookMode.Value);
			Scribe_Collections.Look(ref mpct, "zoneTargetPopulationPct", LookMode.Value);
			Scribe_Collections.Look(ref mpause, "zonePauseWhenSatisfied", LookMode.Value);
			Scribe_Collections.Look(ref munpause, "zoneUnpauseAtCount", LookMode.Value);
			Scribe_Collections.Look(ref pc, "plantCells", LookMode.Value);
			Scribe_Collections.Look(ref ps, "plantSince", LookMode.Value);
			if (Scribe.mode != LoadSaveMode.LoadingVars)
			{
				return;
			}
			book.fishByCell.Clear();
			book.records.Clear();
			book.zoneByCell.Clear();
			book.zones.Clear();
			plantSince.Clear();
			for (int i = 0; fc != null && fr != null && i < fc.Count && i < fr.Count; i++)
			{
				book.fishByCell[fc[i]] = fr[i];
			}
			for (int i = 0; rid != null && i < rid.Count; i++)
			{
				var r = new RM_FishMemoryBook.Record { id = rid[i], waterType = At(rtype, i), population = At(rpop, i) };
				r.common.AddRange(Split(At(rcommon, i)));
				r.uncommon.AddRange(Split(At(runcommon, i)));
				book.records[r.id] = r;
			}
			for (int i = 0; zc != null && zid != null && i < zc.Count && i < zid.Count; i++)
			{
				book.zoneByCell[zc[i]] = zid[i];
			}
			for (int i = 0; mid != null && i < mid.Count; i++)
			{
				book.zones[mid[i]] = new RM_FishMemoryBook.ZoneMemo
				{
					zoneId = mid[i], diedDry = At(mdied, i), label = At(mlabel, i), r = At(mr, i, 1f), g = At(mg, i, 1f), b = At(mb, i, 1f),
					a = At(ma, i, 1f), hidden = At(mhidden, i), allowed = At(mallowed, i, true), repeatMode = At(mrepeatMode, i),
					repeatCount = At(mrepeatCount, i, 1), targetCount = At(mtargetCount, i, 100), targetPopulationPct = At(mpct, i, 0.5f),
					pauseWhenSatisfied = At(mpause, i), unpauseAtCount = At(munpause, i, 50),
				};
			}
			for (int i = 0; pc != null && ps != null && i < pc.Count && i < ps.Count; i++)
			{
				plantSince[pc[i]] = ps[i];
			}
		}

		private static T At<T>(List<T> l, int i, T dflt = default) => l != null && i < l.Count ? l[i] : dflt;

		private static IEnumerable<string> Split(string s) => string.IsNullOrEmpty(s) ? Enumerable.Empty<string>() : s.Split(',');
	}

	/// <summary>RM_IWaterBodyView over a live map's tracker.</summary>
	internal sealed class RM_WaterBodyView : RM_IWaterBodyView
	{
		private static readonly AccessTools.FieldRef<WaterBodyTracker, List<WaterBody>> Bodies =
			AccessTools.FieldRefAccess<WaterBodyTracker, List<WaterBody>>("bodies");
		private static readonly AccessTools.FieldRef<WaterBodyTracker, Dictionary<IntVec3, WaterBody>> BodiesByCell =
			AccessTools.FieldRefAccess<WaterBodyTracker, Dictionary<IntVec3, WaterBody>>("bodiesByCell");
		private static readonly AccessTools.FieldRef<WaterBodyTracker, bool> AnyFish =
			AccessTools.FieldRefAccess<WaterBodyTracker, bool>("anyBodyContainsFish");
		private static readonly AccessTools.FieldRef<WaterBody, List<ThingDef>> Common =
			AccessTools.FieldRefAccess<WaterBody, List<ThingDef>>("commonFish");
		private static readonly AccessTools.FieldRef<WaterBody, List<ThingDef>> Uncommon =
			AccessTools.FieldRefAccess<WaterBody, List<ThingDef>>("uncommonFish");
		private static readonly AccessTools.FieldRef<WaterBody, bool> ShouldHaveFish =
			AccessTools.FieldRefAccess<WaterBody, bool>("shouldHaveFish");
		internal static readonly AccessTools.FieldRef<Zone_Fishing, bool> Allowed =
			AccessTools.FieldRefAccess<Zone_Fishing, bool>("allowed");

		private readonly Map map;
		private readonly WaterBodyTracker tracker;

		public RM_WaterBodyView(Map map)
		{
			this.map = map;
			tracker = map.waterBodyTracker;
		}

		public int Width => map.Size.x;
		public int Height => map.Size.z;
		private IntVec3 Cell(int i) => map.cellIndices.IndexToCell(i);
		private int Index(IntVec3 c) => map.cellIndices.CellToIndex(c);

		public object BodyAt(int cell) => tracker.TryGetWaterBodyAt(Cell(cell), out WaterBody b) ? b : null;
		public bool BodyAlive(object body) => body is WaterBody b && b.CellCount > 0 && Bodies(tracker).Contains(b);
		public int SizeOf(object body) => ((WaterBody)body).Size;
		public int RootOf(object body) => Index(((WaterBody)body).rootCell);
		public bool InBody(object body, int cell) => ((WaterBody)body).cells.Contains(Cell(cell));
		public bool HasCommonFish(object body) => Common((WaterBody)body)?.Count > 0;
		public bool HasUncommonFish(object body) => Uncommon((WaterBody)body)?.Count > 0;
		public int WaterTypeOf(object body) => (int)((WaterBody)body).waterBodyType;

		public RM_FishMemoryBook.Record Snapshot(object body) => SnapshotOf((WaterBody)body);

		internal static RM_FishMemoryBook.Record SnapshotOf(WaterBody b)
		{
			var r = new RM_FishMemoryBook.Record { waterType = (int)b.waterBodyType, population = b.Population };
			foreach (ThingDef d in Common(b) ?? new List<ThingDef>())
			{
				if (d != null) r.common.Add(d.defName);
			}
			foreach (ThingDef d in Uncommon(b) ?? new List<ThingDef>())
			{
				if (d != null) r.uncommon.Add(d.defName);
			}
			return r;
		}

		public void Restore(object body, RM_FishMemoryBook.Record r)
		{
			var b = (WaterBody)body;
			List<ThingDef> c = Common(b) ?? (Common(b) = new List<ThingDef>());
			List<ThingDef> u = Uncommon(b) ?? (Uncommon(b) = new List<ThingDef>());
			c.Clear();
			u.Clear();
			c.AddRange(r.common.Select(n => DefDatabase<ThingDef>.GetNamedSilentFail(n)).Where(d => d != null));
			u.AddRange(r.uncommon.Select(n => DefDatabase<ThingDef>.GetNamedSilentFail(n)).Where(d => d != null));
			ShouldHaveFish(b) = c.Count > 0;
			b.Population = r.population;
			if (c.Count + u.Count > 0)
			{
				AnyFish(tracker) = true;
			}
		}

		public void RollCommon(object body)
		{
			var b = (WaterBody)body;
			b.SetFishTypes();
			if (HasCommonFish(b) || HasUncommonFish(b))
			{
				b.InitializePopulation();
				AnyFish(tracker) = true;
			}
		}

		public void RollUncommon(object body)
		{
			var b = (WaterBody)body;
			BiomeFishTypes types = map.Biome?.fishTypes;
			if (types == null || !Rand.Chance(FishingUtility.ChanceForUncommonFishFromWaterBodySizeCurve.Evaluate(b.Size)))
			{
				return;
			}
			List<FishChance> pool = b.waterBodyType == WaterBodyType.Saltwater ? types.saltwater_Uncommon
				: b.waterBodyType == WaterBodyType.Freshwater ? types.freshwater_Uncommon : null;
			if (pool != null && pool.TryRandomElement(out FishChance pick) && pick.fishDef != null)
			{
				(Uncommon(b) ?? (Uncommon(b) = new List<ThingDef>())).Add(pick.fishDef);
			}
		}

		public void SplitOff(object from, List<int> piece, int totalBefore)
		{
			var fb = (WaterBody)from;
			var nb = new WaterBody(map, Cell(piece[0]));
			Dictionary<IntVec3, WaterBody> byCell = BodiesByCell(tracker);
			foreach (int i in piece)
			{
				IntVec3 c = Cell(i);
				fb.cells.Remove(c);
				nb.cells.Add(c);
				byCell[c] = nb;
			}
			nb.CellCount = piece.Count;
			fb.CellCount = fb.cells.Count;
			if (!fb.cells.Contains(fb.rootCell))
			{
				fb.rootCell = fb.cells.First();
			}
			nb.waterBodyType = fb.waterBodyType;
			Common(nb) = new List<ThingDef>(Common(fb) ?? new List<ThingDef>());
			Uncommon(nb) = new List<ThingDef>(Uncommon(fb) ?? new List<ThingDef>());
			ShouldHaveFish(nb) = ShouldHaveFish(fb);
			float share = totalBefore > 0 ? fb.Population * piece.Count / totalBefore : 0f;
			nb.Population = share;
			fb.Population -= share;
			Bodies(tracker).Add(nb);
			nb.RecacheState();
			fb.RecacheState();
		}

		public int RestoreZoneCell(int cell, RM_FishMemoryBook.ZoneMemo memo)
		{
			IntVec3 c = Cell(cell);
			if (map.zoneManager.ZoneAt(c) != null)
			{
				return -1;
			}
			foreach (Thing t in map.thingGrid.ThingsListAtFast(c))
			{
				if (!t.def.CanOverlapZones)
				{
					return -1;
				}
			}
			Zone_Fishing zone = map.zoneManager.AllZones.FirstOrDefault(z => z.ID == memo.zoneId) as Zone_Fishing;
			if (zone == null)
			{
				if (!memo.diedDry)
				{
					return -1;
				}
				zone = new Zone_Fishing(map.zoneManager);
				map.zoneManager.RegisterZone(zone);
				if (!string.IsNullOrEmpty(memo.label))
				{
					zone.label = memo.label;
				}
				zone.color = new Color(memo.r, memo.g, memo.b, memo.a);
				Allowed(zone) = memo.allowed;
				zone.repeatMode = (FishRepeatMode)memo.repeatMode;
				zone.repeatCount = memo.repeatCount;
				zone.targetCount = memo.targetCount;
				zone.targetPopulationPct = memo.targetPopulationPct;
				zone.pauseWhenSatisfied = memo.pauseWhenSatisfied;
				zone.unpauseAtCount = memo.unpauseAtCount;
			}
			zone.AddCell(c);
			if (memo.hidden && !zone.Hidden)
			{
				zone.Hidden = true;
			}
			return zone.ID;
		}

		internal static RM_FishMemoryBook.ZoneMemo MemoOf(Zone_Fishing z) => new RM_FishMemoryBook.ZoneMemo
		{
			zoneId = z.ID, label = z.label, r = z.color.r, g = z.color.g, b = z.color.b, a = z.color.a, hidden = z.Hidden,
			allowed = Allowed(z), repeatMode = (int)z.repeatMode, repeatCount = z.repeatCount, targetCount = z.targetCount,
			targetPopulationPct = z.targetPopulationPct, pauseWhenSatisfied = z.pauseWhenSatisfied, unpauseAtCount = z.unpauseAtCount,
		};
	}

	/// <summary>What the prefix saw before vanilla changed the tracker.</summary>
	public struct RM_WaterMendState
	{
		public bool active;
		public WaterBody body;
		public int bodySize;
		public RM_FishMemoryBook.Record fish;
		public Zone_Fishing zone;
		public RM_FishMemoryBook.ZoneMemo zoneMemo;
		public List<KeyValuePair<WaterBody, int>> neighbours;
	}

	[HarmonyPatch(typeof(WaterBodyTracker), nameof(WaterBodyTracker.Notify_TerrainChanged))]
	[RimMandrake.Shared.PatchFeature("Fish and fishing zones keep up with ponds that grow, dry out or split", typeof(RM_WaterMendSettings), "waterBodyMendsEnabled")]
	public static class RM_Patch_WaterBodyMend
	{
		private static readonly AccessTools.FieldRef<WaterBodyTracker, Map> MapOf =
			AccessTools.FieldRefAccess<WaterBodyTracker, Map>("map");

		[HarmonyPrefix]
		[HarmonyPriority(Priority.First)]
		public static void Prefix(WaterBodyTracker __instance, IntVec3 cell, TerrainDef oldTerr, TerrainDef newTerr, out RM_WaterMendState __state)
		{
			__state = default;
			if (!RM_WaterMendSettings.waterBodyMendsEnabled || Current.ProgramState != ProgramState.Playing
				|| newTerr?.waterBodyType == oldTerr?.waterBodyType || __instance.Bodies == null)
			{
				return;
			}
			Map map = MapOf(__instance);
			if (map == null || !cell.InBounds(map))
			{
				return;
			}
			__state.active = true;
			if (__instance.TryGetWaterBodyAt(cell, out WaterBody b) && b != null)
			{
				__state.body = b;
				__state.bodySize = b.Size;
				__state.fish = RM_WaterBodyView.SnapshotOf(b);
			}
			if (map.zoneManager.ZoneAt(cell) is Zone_Fishing z)
			{
				__state.zone = z;
				__state.zoneMemo = RM_WaterBodyView.MemoOf(z);
			}
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = cell + GenAdj.CardinalDirections[i];
				if (n.InBounds(map) && __instance.TryGetWaterBodyAt(n, out WaterBody nb) && nb != null)
				{
					(__state.neighbours ??= new List<KeyValuePair<WaterBody, int>>()).Add(new KeyValuePair<WaterBody, int>(nb, nb.Size));
				}
			}
		}

		[HarmonyPostfix]
		public static void Postfix(WaterBodyTracker __instance, IntVec3 cell, RM_WaterMendState __state)
		{
			if (!__state.active)
			{
				return;
			}
			Map map = MapOf(__instance);
			RM_MapComponent_WaterMend comp = RM_MapComponent_WaterMend.Of(map);
			if (comp == null)
			{
				return;
			}
			var view = new RM_WaterBodyView(map);
			RM_WaterMendFlags flags = RM_WaterMendSettings.Flags;
			int idx = map.cellIndices.CellToIndex(cell);
			if (cell.GetWaterBodyType(map) == WaterBodyType.None)
			{
				RM_FishMemoryBook.ZoneMemo memo = null;
				if (__state.zone != null && map.zoneManager.ZoneAt(cell) == null)
				{
					memo = __state.zoneMemo;
					memo.diedDry = __state.zone.cells.Count == 0;
				}
				RM_WaterBodyMend.AfterDried(view, comp.book, flags, idx, __state.body, __state.fish, memo);
				return;
			}
			int before = 0;
			if (__instance.TryGetWaterBodyAt(cell, out WaterBody now) && now != null)
			{
				if (now == __state.body)
				{
					before = __state.bodySize;
				}
				else if (__state.neighbours != null)
				{
					foreach (var kv in __state.neighbours)
					{
						if (kv.Key == now)
						{
							before = kv.Value;
						}
					}
				}
			}
			RM_WaterBodyMend.AfterWet(view, comp.book, flags, idx, before);
		}

		/// <summary>For RM_Patch_WaterBodyTypeFlip: a cell detached from its old-type body may have cut it in two.</summary>
		internal static void SplitAfterDetach(WaterBodyTracker tracker, IntVec3 cell, WaterBody body)
		{
			if (!RM_WaterMendSettings.Flags.split || body == null || body.CellCount <= 0)
			{
				return;
			}
			Map map = MapOf(tracker);
			if (map == null)
			{
				return;
			}
			var view = new RM_WaterBodyView(map);
			if (view.BodyAlive(body))
			{
				RM_WaterBodyMend.SplitIfApart(view, body, map.cellIndices.CellToIndex(cell));
			}
		}
	}

	/// <summary>Trap 4: water plants and a water level that moves.</summary>
	public static class RM_WaterPlantGrace
	{
		[System.ThreadStatic] private static Map ctxMap;
		[System.ThreadStatic] private static IntVec3 ctxCell;

		internal static void Enter(Map map, IntVec3 c)
		{
			ctxMap = map;
			ctxCell = c;
		}

		internal static void Exit()
		{
			ctxMap = null;
		}

		public static bool IsWaterPlant(ThingDef def) =>
			def?.plant != null && def.plant.WildTerrainTags.Overlaps(RM_WaterBodyMath.WaterPlantTags);

		/// <summary>Replaces HashSet.Overlaps at TerrainGrid.DoTerrainChangedEffects' water-plant kill: the vanilla answer, or
		/// "still suits" for a water plant in its grace.</summary>
		public static bool OverlapsOrGraced(HashSet<string> wild, IEnumerable<string> tags)
		{
			Map map = ctxMap;
			if (wild.Overlaps(tags))
			{
				// the square suits the plant again: its spell (if any) is over
				RM_MapComponent_WaterMend done = map != null ? RM_MapComponent_WaterMend.Of(map) : null;
				if (done != null && done.plantSince.Count > 0)
				{
					done.plantSince.Remove(map.cellIndices.CellToIndex(ctxCell));
				}
				return true;
			}
			if (map == null || !RM_WaterMendSettings.waterPlantGraceEnabled)
			{
				return false;
			}
			List<Thing> things = map.thingGrid.ThingsListAtFast(ctxCell);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Plant p && p.def.plant.WildTerrainTags == wild)
				{
					return Lives(p);
				}
			}
			return false;
		}

		/// <summary>A water plant whose square's terrain no longer carries its tags: does it live on?</summary>
		public static bool Lives(Plant p)
		{
			if (!RM_WaterMendSettings.waterPlantGraceEnabled || p?.Map == null || !IsWaterPlant(p.def))
			{
				return false;
			}
			Map map = p.Map;
			IntVec3 c = p.Position;
			if (map.terrainGrid.TerrainAt(c) == TerrainDefOf.ThinIce)
			{
				return false;   // ice is the base game's business
			}
			RM_MapComponent_WaterMend comp = RM_MapComponent_WaterMend.Of(map);
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (comp == null || ex == null)
			{
				return false;
			}
			bool managed = ex.IsExcavated(c) || ex.OriginalTerrainAt(c) != null;
			float metres = Swimming.RM_SwimWater.WaterMetresAt(map, ex, c);
			int i = map.cellIndices.CellToIndex(c);
			int since = comp.plantSince.TryGetValue(i, out int s) ? s : -1;
			bool lives = RM_WaterBodyMath.PlantLivesOn(false, managed, metres, RM_WaterMendSettings.waterPlantDeepToleranceMetres,
				Mathf.RoundToInt(RM_WaterMendSettings.waterPlantGraceHours * RM_WaterBodyMath.TicksPerHour), Find.TickManager.TicksGame, ref since);
			if (since < 0)
			{
				comp.plantSince.Remove(i);
			}
			else
			{
				comp.plantSince[i] = since;
			}
			return lives;
		}

	}

	[HarmonyPatch(typeof(TerrainGrid), "DoTerrainChangedEffects")]
	[RimMandrake.Shared.PatchFeature("Reeds, lilies and lotus live through water that rises and falls", typeof(RM_WaterMendSettings), "waterPlantGraceEnabled")]
	public static class RM_Patch_WaterPlantGraceOnChange
	{
		private static readonly MethodInfo Overlaps = AccessTools.Method(typeof(HashSet<string>), nameof(HashSet<string>.Overlaps));
		private static readonly MethodInfo Graced = AccessTools.Method(typeof(RM_WaterPlantGrace), nameof(RM_WaterPlantGrace.OverlapsOrGraced));

		[HarmonyPrefix]
		public static void Prefix(Map ___map, IntVec3 c)
		{
			RM_WaterPlantGrace.Enter(___map, c);
		}

		[HarmonyTranspiler]
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			int swapped = 0;
			foreach (CodeInstruction ins in instructions)
			{
				if ((ins.opcode == OpCodes.Callvirt || ins.opcode == OpCodes.Call) && ins.operand is MethodInfo m && m == Overlaps)
				{
					ins.opcode = OpCodes.Call;
					ins.operand = Graced;
					swapped++;
				}
				yield return ins;
			}
			if (swapped != 1)
			{
				throw new System.Exception("FlowWorks water-plant grace: expected one HashSet.Overlaps in TerrainGrid.DoTerrainChangedEffects, found " + swapped);
			}
		}

		[HarmonyPostfix]
		public static void Postfix()
		{
			RM_WaterPlantGrace.Exit();
		}
	}

	[HarmonyPatch(typeof(Plant), nameof(Plant.DyingBecauseOfTerrainTags), MethodType.Getter)]
	[RimMandrake.Shared.PatchFeature("Reeds, lilies and lotus live through water that rises and falls", typeof(RM_WaterMendSettings), "waterPlantGraceEnabled")]
	public static class RM_Patch_WaterPlantGraceDying
	{
		[HarmonyPostfix]
		public static void Postfix(Plant __instance, ref bool __result)
		{
			if (!RM_WaterMendSettings.waterPlantGraceEnabled)
			{
				return;
			}
			if (__result && RM_WaterPlantGrace.Lives(__instance))
			{
				__result = false;
			}
		}
	}
}
