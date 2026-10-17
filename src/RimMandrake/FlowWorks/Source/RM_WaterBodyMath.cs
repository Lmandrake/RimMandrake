// FISH_ROLL_MEND_PONDS_BORN_BARREN (plan P13 of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG; engine doc
// design/RimMandrake/flowworks_natural_water_engine_2026-10-17.md §2.3). Verse-free: the arithmetic and the order of the
// three water-body mends and the water-plant grace, shared by the game adapter (RM_WaterBodyMend.cs) and the SelfTest port of
// the vanilla tracker (SelfTest/WaterBodyMendChecks.cs). Cells are grid indices (z * width + x).
//
// The vanilla 1.6 (Odyssey) traps, read from Verse/WaterBody.cs and RimWorld/WaterBodyTracker.cs:
//  (a) a body rolls its fish ONCE, in Initialize, at its size then; a body born at 1 cell rolls "no fish" (chance 0 under 75
//      cells) and growth never re-rolls. Mend: when a body with no fish grows past 75, 100 or 200 cells, roll again by the
//      game's own size curve (and uncommon fish at 400, 1600, 6000 for a body that has common fish only).
//  (b) a pond that dries out completely is removed at 0 cells; the refill is a new 1-cell body (trap a), and every dried
//      square left its fishing zone (RemoveCellFromExistingBody) and is never put back. Mend: a dried square remembers its
//      body's fish and its fishing zone; when it is water again its body gets the same fish back and the square rejoins the
//      zone (the zone is re-made, with its settings, if drying emptied it).
//  (c) the tracker never splits a body that dries in two. Mend: after a square leaves a body, if the body is no longer
//      4-connected, each piece but the largest becomes its own body with the same fish (population shared by size).
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	public static class RM_WaterBodyMath
	{
		/// <summary>The sizes at which vanilla's common-fish chance steps (FishingUtility.ChanceForCommonFishFromWaterBodySizeCurve:
		/// 0 under 75, 0.05 at 75, 0.5 at 100, 1.0 at 200).</summary>
		public static readonly int[] CommonRollSizes = { 75, 100, 200 };

		/// <summary>The sizes at which vanilla's uncommon-fish chance steps (ChanceForUncommonFishFromWaterBodySizeCurve: 0 under 400,
		/// 0.1 at 400, 0.25 at 1600, 0.7 at 6000).</summary>
		public static readonly int[] UncommonRollSizes = { 400, 1600, 6000 };

		/// <summary>Vanilla's common-fish chance by body size (the curve above, linear between its points).</summary>
		public static float CommonChance(int size)
		{
			if (size < 75) return 0f;
			if (size < 100) return 0.05f + (size - 75) * (0.45f / 25f);
			if (size < 200) return 0.5f + (size - 100) * (0.5f / 100f);
			return 1f;
		}

		/// <summary>True when growing from <paramref name="before"/> to <paramref name="after"/> cells passes one of
		/// <paramref name="sizes"/> (before &lt; s ≤ after).</summary>
		public static bool Crossed(int before, int after, int[] sizes)
		{
			foreach (int s in sizes)
			{
				if (before < s && after >= s)
				{
					return true;
				}
			}
			return false;
		}

		// ═══════════════════════════════════════════════ (c) splits ══

		/// <summary>After <paramref name="removed"/> left a body, the body's pieces if it is no longer 4-connected, else null.
		/// <paramref name="inBody"/> answers for the REMAINING cells. A cheap local test first: when the body cells around the
		/// removed square are joined through its 8-ring, no split is possible and nothing is walked.</summary>
		public static List<List<int>> SplitAfterRemoval(int removed, int width, int height, Func<int, bool> inBody)
		{
			int x = removed % width, z = removed / width;
			// ring, clockwise from north: N, NE, E, SE, S, SW, W, NW; even entries are the four cardinals
			int[] dx = { 0, 1, 1, 1, 0, -1, -1, -1 };
			int[] dz = { 1, 1, 0, -1, -1, -1, 0, 1 };
			var ring = new bool[8];
			int cardinals = 0;
			for (int k = 0; k < 8; k++)
			{
				int nx = x + dx[k], nz = z + dz[k];
				ring[k] = nx >= 0 && nz >= 0 && nx < width && nz < height && inBody(nz * width + nx);
				if (ring[k] && k % 2 == 0)
				{
					cardinals++;
				}
			}
			if (cardinals <= 1)
			{
				return null;
			}
			// arcs of consecutive body cells round the ring are connected (each ring step is a 4-neighbour step); count the arcs
			// that hold a cardinal
			int arcsWithCardinal = 0;
			int start = -1;
			for (int k = 0; k < 8; k++)
			{
				if (!ring[k])
				{
					start = k;
					break;
				}
			}
			if (start < 0)
			{
				return null;   // all eight in the body: one arc
			}
			bool inArc = false, arcHasCardinal = false;
			for (int i = 1; i <= 8; i++)
			{
				int k = (start + i) % 8;
				if (ring[k])
				{
					if (!inArc)
					{
						inArc = true;
						arcHasCardinal = false;
					}
					if (k % 2 == 0)
					{
						arcHasCardinal = true;
					}
				}
				else if (inArc)
				{
					inArc = false;
					if (arcHasCardinal)
					{
						arcsWithCardinal++;
					}
				}
			}
			if (arcsWithCardinal <= 1)
			{
				return null;
			}
			// the arcs may still meet further out (round an island): walk
			var seeds = new List<int>();
			for (int k = 0; k < 8; k += 2)
			{
				if (ring[k])
				{
					seeds.Add((z + dz[k]) * width + (x + dx[k]));
				}
			}
			var seen = new HashSet<int>();
			var pieces = new List<List<int>>();
			foreach (int s in seeds)
			{
				if (seen.Contains(s))
				{
					continue;
				}
				var piece = new List<int>();
				var queue = new Queue<int>();
				queue.Enqueue(s);
				seen.Add(s);
				while (queue.Count > 0)
				{
					int c = queue.Dequeue();
					piece.Add(c);
					int cx = c % width, cz = c / width;
					if (cx > 0) Visit(c - 1);
					if (cx < width - 1) Visit(c + 1);
					if (cz > 0) Visit(c - width);
					if (cz < height - 1) Visit(c + width);
				}
				pieces.Add(piece);

				void Visit(int n)
				{
					if (!seen.Contains(n) && inBody(n))
					{
						seen.Add(n);
						queue.Enqueue(n);
					}
				}
			}
			return pieces.Count > 1 ? pieces : null;
		}

		/// <summary>Which piece keeps the original body: the largest; a tie goes to the piece holding <paramref name="root"/>,
		/// then to the first.</summary>
		public static int KeeperPiece(List<List<int>> pieces, int root)
		{
			int best = 0;
			for (int i = 1; i < pieces.Count; i++)
			{
				if (pieces[i].Count > pieces[best].Count || (pieces[i].Count == pieces[best].Count && pieces[i].Contains(root) && !pieces[best].Contains(root)))
				{
					best = i;
				}
			}
			return best;
		}

		// ═══════════════════════════════════════════ water plants (trap 4) ══

		/// <summary>Vanilla's still-water ladder turns to WaterDeep (no shallow tags) at 2 m.</summary>
		public const float DeepWaterMetres = 2f;
		public const float DefaultPlantDeepToleranceMetres = 1f;
		public const float DefaultPlantGraceHours = 24f;
		public const int TicksPerHour = 2500;

		/// <summary>Does a water plant whose square no longer carries its terrain tags live on (true), or die the vanilla way
		/// (false)? <paramref name="tagsSuit"/>: the square's terrain still suits it (vanilla says live). <paramref name="managed"/>:
		/// the square is one FlowWorks moves water on (a dug cell or a pond square with a recorded original); elsewhere vanilla
		/// rules. Water deeper than it likes but no more than <paramref name="toleranceMetres"/> past 2 m never kills it; dry
		/// ground, or water past the tolerance, kills it only after <paramref name="graceTicks"/>. <paramref name="since"/> is the
		/// tick that spell began (-1 none), updated here.</summary>
		public static bool PlantLivesOn(bool tagsSuit, bool managed, float waterMetres, float toleranceMetres, int graceTicks, int now, ref int since)
		{
			if (tagsSuit)
			{
				since = -1;
				return true;
			}
			if (!managed)
			{
				return false;
			}
			if (waterMetres > 0f && waterMetres <= DeepWaterMetres + toleranceMetres)
			{
				since = -1;
				return true;
			}
			if (since < 0)
			{
				since = now;
			}
			return now - since < graceTicks;
		}

		/// <summary>The terrain tags vanilla's water plants live on (Odyssey Plants_Water.xml): a plant with any of these in its
		/// wildTerrainTags is a water plant.</summary>
		public static readonly HashSet<string> WaterPlantTags = new HashSet<string> { "WaterFreshShallow", "WaterFreshShallowStill", "WaterMarshy" };
	}

	/// <summary>Which mends are on (the Mod Settings, passed in so the order below is Verse-free).</summary>
	public struct RM_WaterMendFlags
	{
		public bool rollOnGrowth;
		public bool fishReturn;
		public bool zoneReturn;
		public bool split;
	}

	/// <summary>A dried square's memory: its body's fish, and its fishing zone. Saved with the map (the game adapter flattens
	/// it). Fish are defNames, water types ints, so the book needs no Verse.</summary>
	public sealed class RM_FishMemoryBook
	{
		public sealed class Record
		{
			public int id;
			public int waterType;
			public List<string> common = new List<string>();
			public List<string> uncommon = new List<string>();
			public float population;
		}

		/// <summary>A fishing zone's settings as they were when one of its squares dried, so a zone drying emptied can be
		/// re-made as it was.</summary>
		public sealed class ZoneMemo
		{
			public int zoneId;
			/// <summary>Drying took its last square (vanilla deregistered it). A zone the player deleted is never re-made.</summary>
			public bool diedDry;
			public string label;
			public float r = 1f, g = 1f, b = 1f, a = 1f;
			public bool hidden;
			public bool allowed = true;
			public int repeatMode;
			public int repeatCount = 1;
			public int targetCount = 100;
			public float targetPopulationPct = 0.5f;
			public bool pauseWhenSatisfied;
			public int unpauseAtCount = 50;
		}

		public readonly Dictionary<int, int> fishByCell = new Dictionary<int, int>();
		public readonly Dictionary<int, Record> records = new Dictionary<int, Record>();
		public readonly Dictionary<int, int> zoneByCell = new Dictionary<int, int>();
		public readonly Dictionary<int, ZoneMemo> zones = new Dictionary<int, ZoneMemo>();
		public int nextId = 1;

		// which record a LIVE body is writing into (unsaved: bodies are new objects after a load, and a new record then is fine)
		private readonly Dictionary<object, int> live = new Dictionary<object, int>(ReferenceComparer.Instance);

		private sealed class ReferenceComparer : IEqualityComparer<object>
		{
			public static readonly ReferenceComparer Instance = new ReferenceComparer();
			public new bool Equals(object x, object y) => ReferenceEquals(x, y);
			public int GetHashCode(object o) => System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(o);
		}

		/// <summary>The square <paramref name="cell"/> dried out of <paramref name="body"/>, whose fish are <paramref name="now"/>:
		/// remember them for that square (one record per live body, refreshed each time).</summary>
		public void RememberFish(int cell, object body, Record now)
		{
			if (!live.TryGetValue(body, out int id) || !records.ContainsKey(id))
			{
				id = nextId++;
				live[body] = id;
			}
			now.id = id;
			records[id] = now;
			fishByCell[cell] = id;
		}

		/// <summary>The fish a square remembered (and forget them for that square), or null.</summary>
		public Record RecallFish(int cell)
		{
			if (!fishByCell.TryGetValue(cell, out int id))
			{
				return null;
			}
			fishByCell.Remove(cell);
			return records.TryGetValue(id, out Record r) ? r : null;
		}

		public void RememberZone(int cell, ZoneMemo memo)
		{
			if (zones.TryGetValue(memo.zoneId, out ZoneMemo old) && old.diedDry)
			{
				memo.diedDry = true;
			}
			zones[memo.zoneId] = memo;
			zoneByCell[cell] = memo.zoneId;
		}

		public ZoneMemo RecallZone(int cell)
		{
			if (!zoneByCell.TryGetValue(cell, out int id))
			{
				return null;
			}
			zoneByCell.Remove(cell);
			return zones.TryGetValue(id, out ZoneMemo m) ? m : null;
		}

		/// <summary>A zone re-made under a new id: every square still waiting for the old one now waits for the new one.</summary>
		public void Rekey(int oldId, int newId)
		{
			if (oldId == newId || !zones.TryGetValue(oldId, out ZoneMemo m))
			{
				return;
			}
			zones.Remove(oldId);
			m.zoneId = newId;
			m.diedDry = false;
			zones[newId] = m;
			var keys = new List<int>();
			foreach (var kv in zoneByCell)
			{
				if (kv.Value == oldId)
				{
					keys.Add(kv.Key);
				}
			}
			foreach (int k in keys)
			{
				zoneByCell[k] = newId;
			}
		}

		/// <summary>Drop records and zone memos no square points at (before a save).</summary>
		public void Prune()
		{
			var usedR = new HashSet<int>(fishByCell.Values);
			var usedZ = new HashSet<int>(zoneByCell.Values);
			foreach (int id in new List<int>(records.Keys))
			{
				if (!usedR.Contains(id)) records.Remove(id);
			}
			foreach (int id in new List<int>(zones.Keys))
			{
				if (!usedZ.Contains(id)) zones.Remove(id);
			}
		}
	}

	/// <summary>The tracker as the mends see it. The game adapter implements it over Map.waterBodyTracker; the SelfTest over its
	/// port of the vanilla tracker.</summary>
	public interface RM_IWaterBodyView
	{
		int Width { get; }
		int Height { get; }
		/// <summary>The body holding <paramref name="cell"/> now, or null.</summary>
		object BodyAt(int cell);
		bool BodyAlive(object body);
		int SizeOf(object body);
		int RootOf(object body);
		bool InBody(object body, int cell);
		bool HasCommonFish(object body);
		bool HasUncommonFish(object body);
		int WaterTypeOf(object body);
		RM_FishMemoryBook.Record Snapshot(object body);
		void Restore(object body, RM_FishMemoryBook.Record r);
		/// <summary>Vanilla's own fish roll at the body's current size (WaterBody.SetFishTypes); fills the population when fish
		/// arrive.</summary>
		void RollCommon(object body);
		void RollUncommon(object body);
		/// <summary>Make <paramref name="piece"/> its own body, with <paramref name="from"/>'s fish and a share of its population.</summary>
		void SplitOff(object from, List<int> piece, int totalBefore);
		/// <summary>Put <paramref name="cell"/> back in zone <paramref name="memo"/> (re-made when it died dry); the zone's id after,
		/// or -1 when the square could not rejoin.</summary>
		int RestoreZoneCell(int cell, RM_FishMemoryBook.ZoneMemo memo);
	}

	/// <summary>The order of the mends around one vanilla Notify_TerrainChanged.</summary>
	public static class RM_WaterBodyMend
	{
		/// <summary>A square dried out of <paramref name="body"/> (captured before vanilla removed it; it may now be gone).
		/// <paramref name="hadFish"/>/<paramref name="fish"/> are its fish as they were then; <paramref name="zone"/> the fishing
		/// zone the square was in (null none).</summary>
		public static void AfterDried(RM_IWaterBodyView view, RM_FishMemoryBook book, RM_WaterMendFlags f, int cell, object body,
			RM_FishMemoryBook.Record fish, RM_FishMemoryBook.ZoneMemo zone)
		{
			if (f.fishReturn && body != null && fish != null && fish.common.Count + fish.uncommon.Count > 0)
			{
				book.RememberFish(cell, body, fish);
			}
			if (f.zoneReturn && zone != null)
			{
				book.RememberZone(cell, zone);
			}
			if (f.split && body != null && view.BodyAlive(body))
			{
				SplitIfApart(view, body, cell);
			}
		}

		public static void SplitIfApart(RM_IWaterBodyView view, object body, int removed)
		{
			List<List<int>> pieces = RM_WaterBodyMath.SplitAfterRemoval(removed, view.Width, view.Height, c => view.InBody(body, c));
			if (pieces == null)
			{
				return;
			}
			int total = view.SizeOf(body);
			int keep = RM_WaterBodyMath.KeeperPiece(pieces, view.RootOf(body));
			for (int i = 0; i < pieces.Count; i++)
			{
				if (i != keep)
				{
					view.SplitOff(body, pieces[i], total);
				}
			}
		}

		/// <summary>A square became water and vanilla has put it in a body. <paramref name="sizeBefore"/>: that body's size
		/// before (0 when vanilla just made it).</summary>
		public static void AfterWet(RM_IWaterBodyView view, RM_FishMemoryBook book, RM_WaterMendFlags f, int cell, int sizeBefore)
		{
			object body = view.BodyAt(cell);
			RM_FishMemoryBook.Record memory = book.RecallFish(cell);
			RM_FishMemoryBook.ZoneMemo zone = book.RecallZone(cell);
			if (body != null)
			{
				bool common = view.HasCommonFish(body), uncommon = view.HasUncommonFish(body);
				if (f.fishReturn && memory != null && !common && !uncommon && memory.waterType == view.WaterTypeOf(body))
				{
					view.Restore(body, memory);
				}
				else if (f.rollOnGrowth)
				{
					int size = view.SizeOf(body);
					if (!common && !uncommon && RM_WaterBodyMath.Crossed(sizeBefore, size, RM_WaterBodyMath.CommonRollSizes))
					{
						view.RollCommon(body);
					}
					else if (common && !uncommon && RM_WaterBodyMath.Crossed(sizeBefore, size, RM_WaterBodyMath.UncommonRollSizes))
					{
						view.RollUncommon(body);
					}
				}
			}
			if (f.zoneReturn && zone != null)
			{
				int now = view.RestoreZoneCell(cell, zone);
				if (now >= 0 && now != zone.zoneId)
				{
					book.Rekey(zone.zoneId, now);
				}
			}
		}
	}
}
