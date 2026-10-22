// WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED A1-A3 (runbook 2026-10-22 P2): the state read behind
// src/RimMandrake/FlowWorks/northstar/water_looks_proof.py. RM_WaterLookDraw's methods take a Map, so jawa/static_call cannot
// reach them; this wraps them for one square of the current map. Kept in its own file (RM_NorthstarProofs is shared).
using System.Globalization;
using System.Reflection;
using Verse;

namespace RimMandrake.FlowWorks
{
	public static class RM_WaterLookProofs
	{
		private static bool Cell(string s, out IntVec3 c)
		{
			c = IntVec3.Invalid;
			string[] p = (s ?? "").Split(',');
			if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
			{
				return false;
			}
			c = new IntVec3(x, 0, z);
			return true;
		}

		private static string B(bool b) => b ? "True" : "False";

		private static string F(double v) => v.ToString("0.####", CultureInfo.InvariantCulture);

		/// <summary>
		/// arg "x,z" (READ ONLY): one square's water look on the current map, from the same reads the two layers draw with →
		/// "WATERLOOK cell=x,z terrain=Def still=b dug=b hollow=n waterM=f dlPerMetre=n tint=f tn=f tw=f key=n watchKey=n|unread
		/// tintOn=b bandOn=b facesOn=b tintVisible=b|unread bandVisible=b|unread lookDirty=b|unread".
		/// tint = RM_WaterLookDraw.TintStrength (0/1/2), tn/tw = BandAt, key = KeyAt; watchKey = the key RM_WaterLookWatcher last
		/// noted for the square (the key its mesh was last dirtied for: watchKey != key after a 250-tick check = a stale picture);
		/// tintVisible / bandVisible = the section's own layers' Visible (what the settings hide); lookDirty = the section still
		/// owes a rebuild for the looks' mesh flag.
		/// arg "set:tint=0|1;band=0|1" (WRITES the two RM_WaterLookSettings, either part optional) → "WATERLOOKSET tintOn=b bandOn=b".
		/// arg "take:x;z;w;h;dl" (WRITES) takes up to dl decilitres off every dug square of the rect through the engine's own
		/// TryTakeDl (what a pump or levelling uses; no terrain is set by this call) → "WATERTAKE cells=n took=n".
		/// Else "REFUSED: ...".
		/// </summary>
		public static string ProofWaterLook(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "REFUSED: no current map";
			}
			arg = arg ?? "";
			if (arg.StartsWith("set:"))
			{
				foreach (string part in arg.Substring(4).Split(';'))
				{
					string[] kv = part.Split('=');
					if (kv.Length != 2 || (kv[1] != "0" && kv[1] != "1") || (kv[0] != "tint" && kv[0] != "band"))
					{
						return "REFUSED: set takes tint=0|1;band=0|1";
					}
					if (kv[0] == "tint")
					{
						RM_WaterLookSettings.deepWaterTintEnabled = kv[1] == "1";
					}
					else
					{
						RM_WaterLookSettings.wetWallBandEnabled = kv[1] == "1";
					}
				}
				return "WATERLOOKSET tintOn=" + B(RM_WaterLookSettings.deepWaterTintEnabled) + " bandOn=" + B(RM_WaterLookSettings.wetWallBandEnabled);
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null)
			{
				return "REFUSED: no excavation engine on the current map";
			}
			if (arg.StartsWith("take:"))
			{
				string[] a = arg.Substring(5).Split(';');
				if (a.Length != 5 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z) || !int.TryParse(a[2], out int w)
					|| !int.TryParse(a[3], out int h) || !long.TryParse(a[4], out long dl) || w <= 0 || h <= 0 || (long)w * h > 400 || dl <= 0)
				{
					return "REFUSED: take takes x;z;w;h;dl (w*h <= 400, dl > 0)";
				}
				int cells = 0;
				long took = 0;
				foreach (IntVec3 c in new CellRect(x, z, w, h).ClipInsideMap(map))
				{
					if (eng.IsExcavated(c))
					{
						cells++;
						took += eng.TryTakeDl(c, dl, out FluidDef _);
					}
				}
				return "WATERTAKE cells=" + cells + " took=" + took;
			}
			if (!Cell(arg, out IntVec3 q) || !q.InBounds(map))
			{
				return "REFUSED: arg must be x,z on the current map, set:..., or take:...";
			}
			RM_WaterLookDraw.BandAt(map, eng, q, out float tn, out float tw);
			bool dug = eng.IsExcavated(q);
			TerrainDef t = map.terrainGrid.TerrainAt(q);
			string line = "WATERLOOK cell=" + q.x + "," + q.z + " terrain=" + (t?.defName ?? "none") + " still=" + B(RM_WaterLookDraw.IsStillWater(map, q))
				+ " dug=" + B(dug) + " hollow=" + (dug ? eng.HollowDepthAt(q) : 0) + " waterM=" + F(RM_WaterLookDraw.WaterMetres(eng, q))
				+ " dlPerMetre=" + (long)System.Math.Round(RM_LevelSolve.U / RM_LevelSolve.Metres(RM_LevelSolve.U))
				+ " tint=" + F(RM_WaterLookDraw.TintStrength(map, eng, q)) + " tn=" + F(tn) + " tw=" + F(tw)
				+ " key=" + RM_WaterLookDraw.KeyAt(map, eng, q) + " watchKey=" + WatchKey(map, eng, q)
				+ " tintOn=" + B(RM_WaterLookSettings.deepWaterTintEnabled) + " bandOn=" + B(RM_WaterLookSettings.wetWallBandEnabled)
				+ " facesOn=" + B(RimMandrakeFlowWorksSettings.excavationWallFacesEnabled);
			Section s = map.mapDrawer?.SectionAt(q);
			SectionLayer tl = s?.GetLayer(typeof(SectionLayer_RMDeepWaterTint)), bl = s?.GetLayer(typeof(SectionLayer_RMWetWallBand));
			ulong flag = RM_WaterLookDraw.LookFlag;
			return line + " tintVisible=" + (tl == null ? "unread" : B(tl.Visible)) + " bandVisible=" + (bl == null ? "unread" : B(bl.Visible))
				+ " lookDirty=" + (s == null || flag == 0UL ? "unread" : B((s.dirtyFlags & flag) != 0UL));
		}

		private static readonly FieldInfo WatcherField = typeof(RM_MapComponent_Excavation).GetField("lookWatcher", BindingFlags.Instance | BindingFlags.NonPublic);
		private static readonly FieldInfo WatchField = typeof(RM_WaterLookWatcher).GetField("watch", BindingFlags.Instance | BindingFlags.NonPublic);
		private static readonly FieldInfo KeysField = typeof(RM_WaterLookMath.Watch).GetField("keys", BindingFlags.Instance | BindingFlags.NonPublic);

		/// <summary>The watcher's last noted key for the square, read by reflection (private state; "unread" if any link is gone
		/// or the watcher has not run on this map yet).</summary>
		private static string WatchKey(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			object watcher = WatcherField?.GetValue(eng);
			object watch = watcher == null ? null : WatchField?.GetValue(watcher);
			int[] keys = watch == null ? null : KeysField?.GetValue(watch) as int[];
			int i = map.cellIndices.CellToIndex(c);
			return keys == null || i < 0 || i >= keys.Length ? "unread" : keys[i].ToString(CultureInfo.InvariantCulture);
		}
	}
}
