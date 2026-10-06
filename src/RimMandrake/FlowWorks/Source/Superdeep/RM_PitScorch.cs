using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_VISUAL_PRINCIPLES_1, principle 5 (owner, 2026-10-05): <i>"The burned pit must look like an empty pit
	/// that is scorched, not just a black surface or a normal pit."</i>
	///
	/// Cosmetic state only — which dug cells burned dry and how far their scorch has faded. The walls layer reads
	/// <see cref="StrengthAt"/> and draws an ash/char floor, soot on the faces and a scorch ring on the rim; the pit's
	/// depth, faces and every mechanic are untouched (RM_LiquidFire still drops its vanilla ash filth as before).
	///
	/// Rule (PROVISIONAL, recorded as assumption A5): a scorch PERSISTS until the cell is refilled (F &gt; 0) or filled
	/// in (D = 0), else fades over <c>pitScorchFadeDays</c> (Mod Setting, default 20; 0 = never), three times as fast
	/// while rain falls on it unroofed. Marked by a postfix on RM_LiquidFire.Extinguish(spent = true), so the fire code
	/// is not edited.
	/// </summary>
	public class RM_PitScorch : MapComponent
	{
		private const int Interval = 250;
		private const float RainFactor = 3f;

		private Dictionary<int, int> age = new Dictionary<int, int>();   // cell index -> weighted age in ticks
		private List<int> ageKeys;
		private List<int> ageValues;
		private readonly List<int> scratch = new List<int>();

		public RM_PitScorch(Map map) : base(map)
		{
		}

		public int Count => age.Count;

		public void Mark(IntVec3 c)
		{
			if (!RimMandrakeFlowWorksSettings.pitScorchEnabled || !c.InBounds(map))
			{
				return;
			}
			age[map.cellIndices.CellToIndex(c)] = 0;
			Dirty(c);
		}

		public float StrengthAt(IntVec3 c)
		{
			if (age.Count == 0 || !c.InBounds(map) || !age.TryGetValue(map.cellIndices.CellToIndex(c), out int a))
			{
				return 0f;
			}
			return RM_WallFaceMath.ScorchStrength(a, RimMandrakeFlowWorksSettings.pitScorchFadeDays);
		}

		public override void MapComponentTick()
		{
			if (age.Count == 0 || Find.TickManager.TicksGame % Interval != 0)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			bool raining = map.weatherManager.RainRate > 0.1f;
			float fade = RimMandrakeFlowWorksSettings.pitScorchFadeDays;
			scratch.Clear();
			scratch.AddRange(age.Keys);
			foreach (int i in scratch)
			{
				IntVec3 c = map.cellIndices.IndexToCell(i);
				if (eng == null || eng.ExcavatedDepthAt(c) == 0 || eng.FillAt(c) > 0)
				{
					age.Remove(i);      // refilled or filled in: the scorch is gone
					Dirty(c);
					continue;
				}
				int a = age[i];
				float before = RM_WallFaceMath.ScorchStrength(a, fade);
				a += (int)(Interval * (raining && !c.Roofed(map) ? RainFactor : 1f));
				float after = RM_WallFaceMath.ScorchStrength(a, fade);
				if (after <= 0f)
				{
					age.Remove(i);
					Dirty(c);
					continue;
				}
				age[i] = a;
				if (after != before)
				{
					Dirty(c);
				}
			}
		}

		private void Dirty(IntVec3 c)
		{
			if (map.mapDrawer == null)
			{
				return;
			}
			map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Terrain);
			for (int k = 0; k < 4; k++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[k];
				if (n.InBounds(map))
				{
					map.mapDrawer.MapMeshDirty(n, MapMeshFlagDefOf.Terrain);
				}
			}
		}

		public void ClearAll()
		{
			scratch.Clear();
			scratch.AddRange(age.Keys);
			age.Clear();
			foreach (int i in scratch)
			{
				Dirty(map.cellIndices.IndexToCell(i));
			}
		}

		public override void ExposeData()
		{
			Scribe_Collections.Look(ref age, "RM_pitScorch", LookMode.Value, LookMode.Value, ref ageKeys, ref ageValues);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && age == null)
			{
				age = new Dictionary<int, int>();
			}
		}
	}

	/// <summary>static_call hooks (one string arg) for the review map and state reads — no fire needed to stage a
	/// scorched pit, and a deterministic read instead of a screenshot hunt.</summary>
	public static class RM_PitScorchProof
	{
		/// <summary>"x0,z0,x1,z1" (inclusive rect, or "x,z" for one cell): mark every DUG cell in it scorched now.
		/// "SCORCH marked N".</summary>
		public static string ProofScorch(string arg)
		{
			Map map = Find.CurrentMap;
			RM_PitScorch s = map?.GetComponent<RM_PitScorch>();
			if (s == null || !Rect(arg, out CellRect r))
			{
				return "REFUSED: arg must be x,z or x0,z0,x1,z1 on the current map";
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			int n = 0;
			foreach (IntVec3 c in r)
			{
				if (c.InBounds(map) && eng != null && eng.ExcavatedDepthAt(c) > 0)
				{
					s.Mark(c);
					n++;
				}
			}
			return "SCORCH marked " + n;
		}

		/// <summary>"x,z": "SCORCH strength=s depth=d fill=f".</summary>
		public static string ProofScorchAt(string arg)
		{
			Map map = Find.CurrentMap;
			RM_PitScorch s = map?.GetComponent<RM_PitScorch>();
			if (s == null || !Rect(arg, out CellRect r))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			IntVec3 c = r.Min;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			return "SCORCH strength=" + s.StrengthAt(c).ToString("0.00") + " depth=" + (eng?.ExcavatedDepthAt(c) ?? 0)
				+ " fill=" + (eng?.FillAt(c) ?? 0);
		}

		private static bool Rect(string arg, out CellRect r)
		{
			r = default;
			string[] p = (arg ?? "").Split(',');
			int[] v = new int[p.Length];
			for (int i = 0; i < p.Length; i++)
			{
				if (!int.TryParse(p[i].Trim(), out v[i]))
				{
					return false;
				}
			}
			if (v.Length == 2)
			{
				r = CellRect.SingleCell(new IntVec3(v[0], 0, v[1]));
				return true;
			}
			if (v.Length == 4)
			{
				r = CellRect.FromLimits(v[0], v[1], v[2], v[3]);
				return true;
			}
			return false;
		}
	}

	/// <summary>Marks a cut scorched the moment RM_LiquidFire puts a cell out as SPENT (burned dry).</summary>
	[HarmonyPatch(typeof(RM_LiquidFire), "Extinguish")]
	public static class RM_Patch_ScorchOnSpent
	{
		[HarmonyPostfix]
		public static void Postfix(Map map, IntVec3 c, bool spent)
		{
			if (spent && map != null)
			{
				map.GetComponent<RM_PitScorch>()?.Mark(c);
			}
		}
	}
}
