// WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED (owner by card 2026-10-22, "Pick for me: shadow band + navy"): the approved deep-water
// look, drawn as a map section layer over the water, never as terrain (numbers and the mock it copies: RM_WaterLookMath).
//   - SectionLayer_RMDeepWaterTint: natural still water 5 m and deeper (any lake or pond; rivers excepted) under a navy overlay,
//     10 m and deeper a darker one. Every such square stays WaterDeep, so swimming, roads and other mods see no change. A DUG square
//     is not tinted here: the walls layer draws its water as one sheet (RM_ExcavationWalls.WaterSurface).
// RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE (owner walk 2026-11-25: "I suspect you're applying multiple layers
// over each other instead of calculating a single one"): the second look, the shadow band on the north and west walls above dug
// water, is gone. It was a separate layer of plain rectangles over the walls (the census counted it beside the sheet and the
// tint on one square), and the dry pit's own faces now show the bare wall above the water. The tint layer builds its mesh
// whatever the setting and hides through Visible. It rebuilds on a terrain change AND on its own mesh flag RM_WaterLooks
// (Defs/ManyWaters/MapMeshFlagDefs), which RM_WaterLookWatcher raises for a square whose deep step changed (FlowWorks GPT review
// 2026-10-22). Mod Settings: RM_WaterLookSettings (drawn and Scribed inside the water-body screen, RM_WaterMendSettings).
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	public static class RM_WaterLookSettings
	{
		public static bool deepWaterTintEnabled = true;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref deepWaterTintEnabled, "waterDeepTintEnabled", true);
		}

		// The shared helper's snapshot. MUST stay below the LAST public setting field (RM_SettingsReset).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_WaterLookSettings));

		public static void ResetToShipped() => RM_SettingsReset.ResetAll(typeof(RM_WaterLookSettings), shippedDefaults);

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("How water looks");
			list.CheckboxLabeled("Very deep water is darker", ref deepWaterTintEnabled,
				"On (shipped): water 5 m deep or more, in a lake or pond, is drawn a darker navy, and 10 m or more darker "
				+ "still, so you can see where the deep parts are. Only the picture changes. Rivers keep their own look. Off: all "
				+ "water 2 m deep or more looks the same, as in the base game. Takes effect at once.");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetToShipped);
		}
	}

	/// <summary>Shared mesh helpers of the water-look layer.</summary>
	internal static class RM_WaterLookDraw
	{
		private static MapMeshFlagDef lookFlag;
		private static bool lookFlagResolved;

		/// <summary>The looks' own mesh flag (the deep tint and the walls layer listen to it); 0 if the def is missing, which degrades to
		/// the old terrain-only redraw rather than throwing.</summary>
		public static ulong LookFlag
		{
			get
			{
				if (!lookFlagResolved)
				{
					lookFlag = DefDatabase<MapMeshFlagDef>.GetNamedSilentFail("RM_WaterLooks");
					lookFlagResolved = true;
				}
				return lookFlag;
			}
		}

		public static ulong Flags => (ulong)MapMeshFlagDefOf.Terrain | LookFlag;

		/// <summary>The square's tint strength (0, 1, 2: its deep step; rivers and dry ground 0).</summary>
		public static float TintStrength(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			if (!IsStillWater(map, c))
			{
				return 0f;
			}
			return RM_WaterLookMath.StepStrength(RM_WaterLadder.DeepStepForMetres(WaterMetres(eng, c)));
		}

		/// <summary>Water that is not a river (a river keeps its own look; the tint is for still water).</summary>
		public static bool IsStillWater(Map map, IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			TerrainDef t = map.terrainGrid.BaseTerrainAt(c);
			return t != null && t.IsWater && !t.IsRiver;
		}

		/// <summary>The square's picture key (RM_WaterLookMath.LookKey) from the same read the tint draws with.</summary>
		public static int KeyAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return RM_WaterLookMath.LookKey((int)TintStrength(map, eng, c));
		}

		/// <summary>Above the water terrain and the drowned wall faces, below the dry wall faces (RM_ExcavationWalls draws at
		/// TerrainScatter + 0.002 .. + 0.0039).</summary>
		public static float TintY => AltitudeLayer.TerrainScatter.AltitudeFor() + 0.0025f;

		public static Color32 C(RM_WaterLookMath.Rgba c, float alpha)
		{
			return new Color32(c.r, c.g, c.b, (byte)Mathf.Clamp(Mathf.RoundToInt(alpha * 255f), 0, 255));
		}

		public static Color32 C(RM_WaterLookMath.Rgba c)
		{
			return new Color32(c.r, c.g, c.b, c.a);
		}

		/// <summary>An axis-aligned quad with its own colour at each corner (bottom-left, top-left, top-right, bottom-right).</summary>
		public static void Quad(LayerSubMesh sm, float x0, float z0, float w, float h, float y, Color32 bl, Color32 tl, Color32 tr, Color32 br)
		{
			if (w <= 0f || h <= 0f)
			{
				return;
			}
			int n = sm.verts.Count;
			sm.verts.Add(new Vector3(x0, y, z0));
			sm.verts.Add(new Vector3(x0, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0 + h));
			sm.verts.Add(new Vector3(x0 + w, y, z0));
			for (int i = 0; i < 4; i++)
			{
				sm.uvs.Add(Vector3.zero);
			}
			sm.colors.Add(bl);
			sm.colors.Add(tl);
			sm.colors.Add(tr);
			sm.colors.Add(br);
			sm.tris.Add(n);
			sm.tris.Add(n + 1);
			sm.tris.Add(n + 2);
			sm.tris.Add(n);
			sm.tris.Add(n + 2);
			sm.tris.Add(n + 3);
		}

		/// <summary>True metres of water standing on <paramref name="c"/>: a dug square's own decilitres, an undug natural square's
		/// pond surface over its floor (RM_MapComponent_Excavation.NaturalWaterDlAt), 0 elsewhere.</summary>
		public static double WaterMetres(RM_MapComponent_Excavation eng, IntVec3 c)
		{
			if (eng.IsExcavated(c))
			{
				return eng.WaterMetresAt(c);
			}
			double dl = eng.NaturalWaterDlAt(c, out RM_LiquidBody _, out int _);
			return dl > 0.0 ? RM_LevelSolve.Metres((long)System.Math.Round(dl)) : 0.0;
		}
	}

	/// <summary>Water 5 m and deeper under a navy overlay, 10 m and deeper a darker one (RM_WaterLadder.DeepStep). Each corner's
	/// colour is the mean of the four squares round it, so the steps blend over one square instead of meeting in a hard line.</summary>
	public class SectionLayer_RMDeepWaterTint : SectionLayer
	{
		public SectionLayer_RMDeepWaterTint(Section section) : base(section)
		{
			relevantChangeTypes = RM_WaterLookDraw.Flags;
		}

		public override bool Visible => DebugViewSettings.drawTerrain && RM_WaterLookSettings.deepWaterTintEnabled;

		// strengths of the grown rect, reused: sections regenerate one at a time on the main thread (GPT review 2026-10-22:
		// a new float[] per section per regenerate)
		private static float[] strengthBuffer;

		public override void Regenerate()
		{
			ClearSubMeshes(MeshParts.All);
			Map map = Map;
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null)
			{
				FinalizeMesh(MeshParts.All);
				return;
			}
			CellRect rect = section.CellRect;
			// strengths of the rect grown by one square (corners need the squares beyond the section's edge)
			int x0 = rect.minX - 1, z0 = rect.minZ - 1, w = rect.Width + 2, h = rect.Height + 2;
			if (strengthBuffer == null || strengthBuffer.Length < w * h)
			{
				strengthBuffer = new float[w * h];
			}
			float[] s = strengthBuffer;
			bool any = false;
			for (int dz = 0; dz < h; dz++)
			{
				for (int dx = 0; dx < w; dx++)
				{
					float v = RM_WaterLookDraw.TintStrength(map, eng, new IntVec3(x0 + dx, 0, z0 + dz));
					s[dz * w + dx] = v;
					any |= v > 0f;
				}
			}
			if (any)
			{
				LayerSubMesh sm = GetSubMesh(RM_FaceMaterial.ShadeMat);
				float y = RM_WaterLookDraw.TintY;
				foreach (IntVec3 c in rect)
				{
					if (!RM_WaterLookDraw.IsStillWater(map, c) || eng.IsExcavated(c))
					{
						continue;   // a dug square's water is the walls layer's one sheet
					}
					int ix = c.x - x0, iz = c.z - z0;   // this square in the grown grid (1..w-2, 1..h-2)
					float bl = Corner(s, w, ix, iz), tl = Corner(s, w, ix, iz + 1), tr = Corner(s, w, ix + 1, iz + 1), br = Corner(s, w, ix + 1, iz);
					if (bl <= 0f && tl <= 0f && tr <= 0f && br <= 0f)
					{
						continue;
					}
					RM_WaterLookDraw.Quad(sm, c.x, c.z, 1f, 1f, y, Tint(bl), Tint(tl), Tint(tr), Tint(br));
				}
			}
			FinalizeMesh(MeshParts.All);
		}

		private static Color32 Tint(float strength)
		{
			return RM_WaterLookDraw.C(RM_WaterLookMath.TintAt(strength));
		}

		/// <summary>The corner at grown-grid point (<paramref name="px"/>, <paramref name="pz"/>): the mean of the four squares
		/// whose corner it is (squares (px−1..px, pz−1..pz)).</summary>
		private static float Corner(float[] s, int w, int px, int pz)
		{
			return 0.25f * (s[(pz - 1) * w + px - 1] + s[(pz - 1) * w + px] + s[pz * w + px - 1] + s[pz * w + px]);
		}

	}

	/// <summary>FlowWorks GPT review 2026-10-22: redraws the deep tint when a square's picture key changes (a deep step crossed)
	/// without a terrain write. Runs on its own 250-tick timer from the depth engine, the
	/// setting on or off (the meshes are kept current either way, so a toggle shows the right picture at once). Watches only
	/// squares that can carry a look: every dug square, and natural still water whose floor is 5 m or deeper (rebuilt every
	/// tenth check; shallower natural water can never reach the 5 m step). A changed key dirties only the looks' own mesh
	/// flag, on the square and its neighbours (the tint's corners blend over one square).</summary>
	public sealed class RM_WaterLookWatcher
	{
		public const int IntervalTicks = 250;
		private const int RescanEvery = 10;

		private readonly RM_WaterLookMath.Watch watch = new RM_WaterLookMath.Watch();
		private readonly System.Collections.Generic.List<IntVec3> naturalDeep = new System.Collections.Generic.List<IntVec3>();
		private int checks;

		public void Tick(Map map, RM_MapComponent_Excavation eng, System.Collections.Generic.IEnumerable<IntVec3> dug)
		{
			ulong flag = RM_WaterLookDraw.LookFlag;
			if (flag == 0UL)
			{
				return;   // no flag def: the layers redraw on terrain changes only, as before
			}
			if (checks++ % RescanEvery == 0)
			{
				Rescan(map, eng);
			}
			int cells = map.cellIndices.NumGridCells;
			foreach (IntVec3 c in dug)
			{
				Check(map, eng, c, cells, flag);
			}
			for (int i = 0; i < naturalDeep.Count; i++)
			{
				Check(map, eng, naturalDeep[i], cells, flag);
			}
		}

		private void Check(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int cells, ulong flag)
		{
			if (watch.Note(map.cellIndices.CellToIndex(c), cells, RM_WaterLookDraw.KeyAt(map, eng, c)))
			{
				map.mapDrawer.MapMeshDirty(c, flag, true, false);
			}
		}

		private void Rescan(Map map, RM_MapComponent_Excavation eng)
		{
			naturalDeep.Clear();
			int fiveMetreFloor = (int)System.Math.Ceiling(RM_WaterLadder.DeepStepFiveMetres / RM_Volume.MetresPerNotch);
			foreach (IntVec3 c in map.AllCells)
			{
				if (eng.IsSourceCell(c) && RM_WaterLookDraw.IsStillWater(map, c) && eng.BedLevelsAt(c) >= fiveMetreFloor)
				{
					naturalDeep.Add(c);
				}
			}
		}
	}
}
