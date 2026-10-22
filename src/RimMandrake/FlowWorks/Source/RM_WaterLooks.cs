// WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED (owner by card 2026-10-22, "Pick for me: shadow band + navy"): the two approved water
// looks, drawn as map section layers over the water, never as terrain (numbers and the mock each copies: RM_WaterLookMath).
//   - SectionLayer_RMDeepWaterTint: water 5 m and deeper (any lake, pond, canal or pit; rivers excepted) under a navy overlay,
//     10 m and deeper a darker one. Every such square stays WaterDeep, so swimming, roads and other mods see no change.
//   - SectionLayer_RMWetWallBand: a wet dug square whose water stands below its lip shows a soft shadow band on its north and
//     west edges, as thick as the gap between the water and the lip.
// Both build their mesh whatever the setting and hide through Visible, so a toggle takes effect at once with no redraw. They
// rebuild on a terrain change AND on their own mesh flag RM_WaterLooks (Defs/ManyWaters/MapMeshFlagDefs), which
// RM_WaterLookWatcher raises for a square whose picture key changed (FlowWorks GPT review 2026-10-22: a level crossing
// 5 m / 10 m, or a band's gap changing, inside one terrain rung used to leave the picture stale until the next terrain
// write). Mod Settings: RM_WaterLookSettings (drawn and Scribed inside the water-body screen, RM_WaterMendSettings).
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	public static class RM_WaterLookSettings
	{
		public static bool deepWaterTintEnabled = true;
		public static bool wetWallBandEnabled = true;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref deepWaterTintEnabled, "waterDeepTintEnabled", true);
			Scribe_Values.Look(ref wetWallBandEnabled, "waterWallBandEnabled", true);
		}

		// The shared helper's snapshot. MUST stay below the LAST public setting field (RM_SettingsReset).
		private static readonly System.Collections.Generic.Dictionary<string, object> shippedDefaults = RM_SettingsReset.Snapshot(typeof(RM_WaterLookSettings));

		public static void ResetToShipped() => RM_SettingsReset.ResetAll(typeof(RM_WaterLookSettings), shippedDefaults);

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("How water looks");
			list.CheckboxLabeled("Very deep water is darker", ref deepWaterTintEnabled,
				"On (shipped): water 5 m deep or more, in a lake, pond, canal or pit, is drawn a darker navy, and 10 m or more darker "
				+ "still, so you can see where the deep parts are. Only the picture changes. Rivers keep their own look. Off: all "
				+ "water 2 m deep or more looks the same, as in the base game. Takes effect at once.");
			list.CheckboxLabeled("Shadow on the walls above dug water", ref wetWallBandEnabled,
				"On (shipped): when water in a dug canal or pit stands below the edge of the hole, a soft shadow on its north and west "
				+ "sides shows the bare wall between the water and the edge, wider the further down the water is. Off: the water "
				+ "is drawn right up to the edge. Takes effect at once.");
			RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, ResetToShipped);
		}
	}

	/// <summary>Shared mesh helpers of the two water-look layers.</summary>
	internal static class RM_WaterLookDraw
	{
		private static MapMeshFlagDef lookFlag;
		private static bool lookFlagResolved;

		/// <summary>The layers' own mesh flag (only these two layers listen to it); 0 if the def is missing, which degrades to
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

		/// <summary>The wall band's north and west thickness on a wet dug square (both 0 elsewhere).</summary>
		public static void BandAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c, out float tn, out float tw)
		{
			tn = tw = 0f;
			if (!eng.IsExcavated(c) || eng.WaterDlAt(c) <= 0)
			{
				return;
			}
			int d = eng.HollowDepthAt(c);
			double water = eng.WaterMetresAt(c);
			tn = RM_WaterLookMath.BandThickness(RM_WaterLookMath.GapMetres(d, Side(map, eng, c + IntVec3.North, d), water));
			tw = RM_WaterLookMath.BandThickness(RM_WaterLookMath.GapMetres(d, Side(map, eng, c + IntVec3.West, d), water));
		}

		/// <summary>The neighbour's floor in notches, for the gap, by the wall drawer's own rule (SectionLayer_RMExcavationWalls
		/// .NeighbourLevel): the map edge and natural liquid read as this square's own depth (no wall there), dry ground as 0, a
		/// dug or dried-bed neighbour as its hollow depth.</summary>
		private static int Side(Map map, RM_MapComponent_Excavation eng, IntVec3 n, int myDepth)
		{
			if (!n.InBounds(map) || eng.IsSourceCell(n))
			{
				return myDepth;
			}
			return eng.HollowDepthAt(n);
		}

		/// <summary>The square's picture key (RM_WaterLookMath.LookKey) from the same reads the layers draw with.</summary>
		public static int KeyAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			BandAt(map, eng, c, out float tn, out float tw);
			return RM_WaterLookMath.LookKey((int)TintStrength(map, eng, c), tn, tw);
		}

		/// <summary>Above the water terrain and the drowned wall faces, below the dry wall faces (RM_ExcavationWalls draws at
		/// TerrainScatter + 0.002 .. + 0.0039).</summary>
		public static float TintY => AltitudeLayer.TerrainScatter.AltitudeFor() + 0.0025f;

		/// <summary>Above every wall face and outline.</summary>
		public static float BandY => AltitudeLayer.TerrainScatter.AltitudeFor() + 0.0042f;

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
					if (!RM_WaterLookDraw.IsStillWater(map, c))
					{
						continue;
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

	/// <summary>A wet dug square whose water stands below the lip: a soft dark band on its north and west edges, as thick as the
	/// gap (RM_WaterLookMath.BandThickness), darkest at the lip and fading toward the water. The north side is the far wall the
	/// camera sees; the west the shaded side wall (RM_WallFaceMath's convention).</summary>
	public class SectionLayer_RMWetWallBand : SectionLayer
	{
		public SectionLayer_RMWetWallBand(Section section) : base(section)
		{
			relevantChangeTypes = RM_WaterLookDraw.Flags;
		}

		// the band shades a wall face, so it hides with the faces (excavationWallFacesEnabled) too
		public override bool Visible => DebugViewSettings.drawTerrain && RM_WaterLookSettings.wetWallBandEnabled
			&& RimMandrakeFlowWorksSettings.excavationWallFacesEnabled;

		public override void Regenerate()
		{
			ClearSubMeshes(MeshParts.All);
			Map map = Map;
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (eng != null)
			{
				LayerSubMesh sm = null;
				float y = RM_WaterLookDraw.BandY;
				foreach (IntVec3 c in section.CellRect)
				{
					RM_WaterLookDraw.BandAt(map, eng, c, out float tn, out float tw);
					if (tn <= 0f && tw <= 0f)
					{
						continue;
					}
					if (sm == null)
					{
						sm = GetSubMesh(RM_FaceMaterial.ShadeMat);
					}
					Color32 clear = RM_WaterLookDraw.C(RM_WaterLookMath.BandColour, 0f);
					if (tn > 0f)
					{
						Color32 lip = RM_WaterLookDraw.C(RM_WaterLookMath.BandColour, RM_WaterLookMath.BandAlpha(false));
						// hangs from the north edge: dark at the top, clear at its foot
						RM_WaterLookDraw.Quad(sm, c.x, c.z + 1f - tn, 1f, tn, y, clear, lip, lip, clear);
					}
					if (tw > 0f)
					{
						Color32 lip = RM_WaterLookDraw.C(RM_WaterLookMath.BandColour, RM_WaterLookMath.BandAlpha(true));
						// along the west edge: dark at the wall, clear toward the water
						RM_WaterLookDraw.Quad(sm, c.x, c.z, tw, 1f, y + 0.0001f, lip, lip, clear, clear);
					}
				}
			}
			FinalizeMesh(MeshParts.All);
		}
	}

	/// <summary>FlowWorks GPT review 2026-10-22: redraws the two water looks when a square's picture key changes (a deep step
	/// crossed, a band edge moved a rung) without a terrain write. Runs on its own 250-tick timer from the depth engine, the
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
