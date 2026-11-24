using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 6 (R12): the drawbridge pictures, read from the texPaths of the design doc's art
	/// contract (flowworks_drawbridge_design_2026-10-20.md §R12 "Art contract"). DRAWBRIDGE_LOOKS_WIRE_PICTURES_IN_WINGS: every
	/// picture is picked per material AND per look (Scrapper/Industrial/Modern/Futuristic, the bridge's own look as the suspension
	/// bridge keeps it), the candidates best first from <see cref="DrawbridgeArtPaths"/>: the material's picture, else the look's
	/// (DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK, owner by card 2026-10-22: "Material picks win").
	/// Every lookup is SILENT (ContentFinder, no error) and ends at a stand-in that exists: the suspension deck tile for the leaf
	/// and planks, the def's own picture for the winch, the vanilla door for the gate. Nothing here generates or queues art.
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_DrawbridgeArt
	{
		public const string Dir = DrawbridgeArtPaths.Dir;

		public enum LeafView
		{
			Face,
			Underside,
			Edge,
		}

		private static readonly Dictionary<string, Material> mats = new Dictionary<string, Material>();
		private static readonly Dictionary<string, Graphic> multis = new Dictionary<string, Graphic>();

		public static string Material(SuspensionTier t)
		{
			return DrawbridgeArtPaths.Material(t);
		}

		/// <summary>The look a drawbridge part draws in: its bridge's look (picked on the build button), else the default look
		/// once the suspension looks are loaded (a legacy unstyled bridge draws in the default look, as its decks do); null when
		/// no looks are loaded (the material pictures).</summary>
		public static string LookOf(SuspensionBridgeRecord r)
		{
			if (r != null && Machinery.PipeStyles.IsLook(r.look))
			{
				return r.look;
			}
			return LooksLoaded ? Machinery.PipeStyles.DefaultLook(Machinery.RM_MachinerySettings.pipeDefaultLook) : null;
		}

		private static bool? looksLoaded;

		public static bool LooksLoaded
		{
			get
			{
				if (looksLoaded == null)
				{
					looksLoaded = DefDatabase<ThingStyleDef>.GetNamedSilentFail(
						Machinery.PipeStyles.StyleDefName(RM_SuspensionLooks.StyledDefs[0], Machinery.PipeStyles.Scrapper)) != null;
				}
				return looksLoaded.Value;
			}
		}

		/// <summary>A cutout material for the first path that exists, or null.</summary>
		public static Material MatOrNull(params string[] paths)
		{
			foreach (string p in paths)
			{
				if (p == null)
				{
					continue;
				}
				if (mats.TryGetValue(p, out Material m))
				{
					if (m != null)
					{
						return m;
					}
					continue;
				}
				m = ContentFinder<Texture2D>.Get(p, false) != null ? MaterialPool.MatFrom(p, ShaderDatabase.Cutout) : null;
				mats[p] = m;
				if (m != null)
				{
					return m;
				}
			}
			return null;
		}

		/// <summary>The first candidate base path whose facing file exists (<paramref name="facing"/> e.g. "_south"), or null.</summary>
		public static string FirstWith(string[] bases, string facing)
		{
			foreach (string b in bases)
			{
				if (MatOrNull(b + facing) != null)
				{
					return b;
				}
			}
			return null;
		}

		public static Material LeafUp(SuspensionTier t, string look, LeafView v)
		{
			return LeafUp(t, look, v, out _);
		}

		/// <summary>The raised leaf's picture and the path it came from (DRAWBRIDGE_CABLES_FIX_STOP_SHORT: the edge pictures'
		/// painted rope stub is cropped by name).</summary>
		public static Material LeafUp(SuspensionTier t, string look, LeafView v, out string path)
		{
			List<string> c = new List<string>(DrawbridgeArtPaths.LeafUp(t, look, v.ToString()));
			c.Add("Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_" + Material(t));
			foreach (string p in c)
			{
				Material m = MatOrNull(p);
				if (m != null)
				{
					path = p;
					return m;
				}
			}
			path = null;
			return null;
		}

		/// <summary>The winch house picture for a material and look (Graphic_Multi, drawSize 1.5), or null (the def's own).</summary>
		public static Graphic Winch(SuspensionTier t, string look)
		{
			string path = FirstWith(DrawbridgeArtPaths.Winch(t, look), "_south");
			if (path == null)
			{
				return null;
			}
			if (!multis.TryGetValue(path, out Graphic g))
			{
				g = GraphicDatabase.Get<Graphic_Multi>(path, ShaderDatabase.Cutout, new Vector2(1.5f, 1.5f), Color.white);
				multis[path] = g;
			}
			return g;
		}

		/// <summary>The gate's picture for its state and door rotation, or null (the vanilla door draws).</summary>
		public static Material Gate(SuspensionTier t, string look, bool open, Rot4 rot)
		{
			string facing = DrawbridgeArtPaths.GateFacing(rot.IsHorizontal);
			string path = FirstWith(DrawbridgeArtPaths.Gate(t, look, open), facing);
			return path == null ? null : MatOrNull(path + facing);
		}

		public static Texture2D Icon(string name, Texture2D fallback)
		{
			return ContentFinder<Texture2D>.Get("UI/Commands/FlowWorks/" + name, false) ?? fallback;
		}

		/// <summary>The winch defs' own picture (blueprint, menu icon, an unlinked winch with no looks): the material's
		/// Graphic_Multi when installed. Swapped once at startup; a placed winch draws its bridge's look (Building_DrawbridgeWinch.Graphic).</summary>
		static RM_DrawbridgeArt()
		{
			SwapIfInstalled(RM_DrawbridgeDefOf.RM_DrawbridgeWinch_Timber, Dir + "RM_DrawbridgeWinch_Timber", new Vector2(1.5f, 1.5f));
			SwapIfInstalled(RM_DrawbridgeDefOf.RM_DrawbridgeWinch_Steel, Dir + "RM_DrawbridgeWinch_Steel", new Vector2(1.5f, 1.5f));
		}

		public static bool SwapIfInstalled(ThingDef def, string multiPath, Vector2 drawSize)
		{
			if (def == null || ContentFinder<Texture2D>.Get(multiPath + "_south", false) == null)
			{
				return false;
			}
			def.graphicData = new GraphicData
			{
				texPath = multiPath,
				graphicClass = typeof(Graphic_Multi),
				drawSize = drawSize,
			};
			def.graphic = def.graphicData.Graphic;
			return true;
		}

		/// <summary>TIMBER_LEAF_DIAGNOSE_UP_AND_INVISIBLE: every drawbridge leaf on the viewed map, each frame, from the bridges'
		/// map component: the raised leaf whether or not a winch house stands beside it (a staged or winchless raised leaf drew
		/// nothing when the winch's DrawAt drew it), and the art planks of a leaf that has its winch, as before.</summary>
		public static void DrawLeaves(Map map, IReadOnlyList<SuspensionBridgeRecord> bridges)
		{
			for (int i = 0; i < bridges.Count; i++)
			{
				SuspensionBridgeRecord r = bridges[i];
				if (r == null || !r.IsDrawbridge)
				{
					continue;
				}
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					DrawLeafUp(map, r, l);
					DrawLines(map, r, l);
					DrawOrderMark(map, r, l);
				}
			}
		}

		/// <summary>DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED: draw a raised leaf as a rigid leaf turned about its hinge
		/// (RM_DrawbridgeMath.DrawbridgeLeafPose): one strip per lane, each cell of the leaf one slice of the Face picture
		/// laid on the cell's projected parallelogram, so the leaf keeps its true length (no stretch), shortens on screen as it
		/// rises, and stops at the ruled hold (north-bank hinge 55, south-bank hinge 85, east/west 75). Before this, an upright
		/// picture was stretched to the full leaf length up the screen, so a north-running raised leaf covered its whole gap and
		/// read lowered. At angle 0 the strip covers exactly the flat deck footprint, so the first tick does not pop.</summary>
		public static void DrawLeafUp(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			int full = RM_Drawbridges.FullTicks(r, l);
			if (l.progress <= 0 || full <= 0)
			{
				return;
			}
			IntVec3 step = l.hingeAtFirst ? r.dir.FacingCell : r.dir.Opposite.FacingCell;   // hinge toward the leaf
			Material mat = LeafUp(r.tier, LookOf(r), LeafView.Face, out string path);
			if (mat == null)
			{
				return;
			}
			int length = l.Span.Length;
			double deg = DrawbridgeLeafPose.AngleDegrees(step.x, step.z, (double)l.progress / full);
			DrawbridgeLeafPose.CellVector(step.x, step.z, deg, out double vx, out double vz);
			Vector4 across = new Vector4(step.z, 0f, -step.x, 0f);   // a lane's width; keeps the picture's handedness (no back face)
			Vector4 along = new Vector4((float)vx, 0f, (float)vz, 0f);   // one cell of leaf on screen, hinge to tip
			float y = AltitudeLayer.BuildingOnTop.AltitudeFor();
			int hinge = RM_Drawbridges.HingeIndex(l);
			double rise = deg / DrawbridgeLeafPose.HoldDegrees(step.x, step.z);
			for (int lane = 0; lane < r.width; lane++)
			{
				Vector3 at = r.Cell(lane, hinge).ToVector3Shifted() + step.ToVector3() * 0.5f;   // the hinge edge
				for (int i = 0; i < length; i++)
				{
					float c = i + 0.5f;
					Matrix4x4 m = Matrix4x4.identity;
					m.SetColumn(0, across);
					m.SetColumn(1, new Vector4(0f, 1f, 0f, 0f));
					m.SetColumn(2, along);
					m.SetColumn(3, new Vector4(at.x + along.x * c, y, at.z + along.z * c, 1f));
					Graphics.DrawMesh(LeafSlice(DrawbridgeLeafPose.SliceFor(i, length)), m, Shaded(path, mat, rise * 0.42 * (1.0 - c / length)), 0);
				}
			}
			DrawLeafEdges(r, l, step, length, deg, y);
		}

		private static readonly Dictionary<string, Material> shadedMats = new Dictionary<string, Material>();

		/// <summary>The leaf's picture darkened by `dark` (0..1, in 12 steps): the hinge end in shade, the tip in the light, the only
		/// cue of lift a north or south leaf has (the accepted v3 sheet's shading).</summary>
		private static Material Shaded(string path, Material plain, double dark)
		{
			int step = Mathf.Clamp(Mathf.RoundToInt((float)dark * 24f), 0, 24);
			if (step == 0 || path == null)
			{
				return plain;
			}
			string key = path + "|" + step;
			if (!shadedMats.TryGetValue(key, out Material m))
			{
				float g = 1f - step / 24f;
				m = MaterialPool.MatFrom(path, ShaderDatabase.Cutout, new Color(g, g, g));
				shadedMats[key] = m;
			}
			return m;
		}

		/// <summary>The leaf's thickness: its tip end, and the long side an east or west leaf turns to the camera.</summary>
		private static void DrawLeafEdges(SuspensionBridgeRecord r, DrawbridgeLeaf l, IntVec3 step, int length, double deg, float y)
		{
			if (deg < 1.0)
			{
				return;
			}
			IntVec3 side = r.Side;
			Vector3 o = Lip(r, l, step);
			bool steel = RM_DrawbridgeMath.IsPowered(r.tier);
			double th = steel ? 0.10 : 0.16;
			Vector3 V(double along, double v, double below)
			{
				DrawbridgeFrameMath.P p = DrawbridgeFrameMath.Leaf(step.x, step.z, side.x, side.z, along, v, deg, below);
				return o + new Vector3((float)p.X, 0f, (float)p.Z);
			}
			double h = r.width / 2.0;
			y -= Altitudes.AltInc * 0.2f;
			if (step.x != 0)
			{
				double v = side.z > 0 ? -h : h;   // the southern long side
				Slab(V(0, v, 0), V(length, v, 0), V(0, v, th), steel ? new Color(0.27f, 0.29f, 0.31f) : new Color(0.36f, 0.235f, 0.133f), y);
			}
			Slab(V(length, -h, 0), V(length, h, 0), V(length, -h, th), steel ? new Color(0.5f, 0.51f, 0.53f) : new Color(0.52f, 0.36f, 0.22f), y - Altitudes.AltInc * 0.2f);
		}

		private static readonly Color Ink = new Color(0.06f, 0.05f, 0.04f);

		/// <summary>A solid parallelogram from corner a along a→b and a→c, inked round its edge.</summary>
		private static void Slab(Vector3 a, Vector3 b, Vector3 c, Color color, float y)
		{
			Vector3 ux = b - a, uz = c - a;
			Vector3 mid = a + (ux + uz) * 0.5f;
			Quad(mid, ux + ux.normalized * 0.08f, uz + uz.normalized * 0.08f, SolidColorMaterials.SimpleSolidColorMaterial(Ink), y - Altitudes.AltInc * 0.1f);
			Quad(mid, ux, uz, SolidColorMaterials.SimpleSolidColorMaterial(color), y);
		}

		private static void Quad(Vector3 mid, Vector3 ux, Vector3 uz, Material mat, float y)
		{
			if (ux.x * uz.z - ux.z * uz.x < 0f)
			{
				ux = -ux;   // never a back face
			}
			Matrix4x4 m = Matrix4x4.identity;
			m.SetColumn(0, new Vector4(ux.x, 0f, ux.z, 0f));
			m.SetColumn(2, new Vector4(uz.x, 0f, uz.z, 0f));
			m.SetColumn(3, new Vector4(mid.x, y, mid.z, 1f));
			Graphics.DrawMesh(MeshPool.plane10, m, mat, 0);
		}

		/// <summary>The middle of a leaf's hinge lip (the frame's origin).</summary>
		public static Vector3 Lip(SuspensionBridgeRecord r, DrawbridgeLeaf l, IntVec3 step)
		{
			Vector3 o = r.Cell(0, RM_Drawbridges.HingeIndex(l)).ToVector3Shifted() + r.Side.ToVector3() * ((r.width - 1) * 0.5f) + step.ToVector3() * 0.5f;
			o.y = 0f;
			return o;
		}

		/// <summary>The hauling lines (his ruling of 2026-11-03: the friendly side stays taut, "it's part of what the Winch is pulling
		/// on"): from the leaf's drawn tip edge over the lintel to the winch, in every state; on the far bank only the short
		/// mooring hitch of a lowered leaf. Rope on timber, cable on steel. Nothing crosses the open gap.</summary>
		public static void DrawLines(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			int full = RM_Drawbridges.FullTicks(r, l);
			Material mat = LineMat(r.tier, out Mesh mesh, out float tile);
			if (mat == null || full <= 0 || RM_MapComponent_SuspensionBridges.BuiltAt<Building_SuspensionAnchor>(map, r.Cell(0, RM_Drawbridges.HingeIndex(l))) == null
				|| RM_MapComponent_SuspensionBridges.StructuralDeckAt(map, r.Cell(0, l.hingeAtFirst ? l.last : l.first)) == null)
			{
				return;   // not built: nothing to hang a line on
			}
			IntVec3 step = l.hingeAtFirst ? r.dir.FacingCell : r.dir.Opposite.FacingCell;
			IntVec3 side = r.Side;
			Vector3 o = Lip(r, l, step);
			int length = l.Span.Length;
			double deg = DrawbridgeLeafPose.AngleDegrees(step.x, step.z, (double)l.progress / full);
			float y = AltitudeLayer.PawnUnused.AltitudeFor() + Altitudes.AltInc;
			Building_DrawbridgeWinch w = l.winch != null && l.winch.Spawned ? l.winch : null;
			bool farBank = l.hingeAtFirst ? l.last == r.length - 2 : l.first == 1;   // a tip that meets another leaf moors to nothing
			for (int sgn = -1; sgn <= 1; sgn += 2)
			{
				if (w != null)
				{
					Vector3 c = w.TrueCenter() - o;
					int winchSgn = c.x * side.x + c.z * side.z >= 0f ? 1 : -1;
					var drum = new DrawbridgeFrameMath.P { X = c.x, Z = c.z + DrawbridgeFrameMath.DrumZ };
					List<DrawbridgeFrameMath.P> pts = DrawbridgeFrameMath.NearLine(step.x, step.z, side.x, side.z, r.width, length, sgn, deg, winchSgn, drum);
					for (int i = 0; i + 1 < pts.Count; i++)
					{
						Line(o, pts[i], pts[i + 1], mat, mesh, tile, y);
					}
				}
				if (farBank && DrawbridgeFrameMath.Hitch(step.x, step.z, side.x, side.z, r.width, length, sgn, deg, out DrawbridgeFrameMath.P a, out DrawbridgeFrameMath.P b))
				{
					Line(o, a, b, mat, mesh, tile, y);
				}
			}
		}

		/// <summary>DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD: an order waiting for its colonist shows vanilla's flick mark on the winch house
		/// and over the leaf, as a switch waiting to be flicked does, until the colonist has worked it.</summary>
		private static void DrawOrderMark(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			Material mat = l.pendingOrder == RM_DrawbridgeMath.OrderNone ? null : DesignationDefOf.Flick.iconMat;
			if (mat == null)
			{
				return;
			}
			float y = AltitudeLayer.MetaOverlays.AltitudeFor();
			Vector3 mid = (r.Cell(0, l.first).ToVector3Shifted() + r.Cell(r.width - 1, l.last).ToVector3Shifted()) * 0.5f;
			mid.y = y;
			Graphics.DrawMesh(MeshPool.plane10, mid, Quaternion.identity, mat, 0);
			if (l.winch != null && l.winch.Spawned)
			{
				Vector3 at = l.winch.TrueCenter();
				at.y = y;
				Graphics.DrawMesh(MeshPool.plane10, at, Quaternion.identity, mat, 0);
			}
		}

		public const float LineThick = 0.075f;
		private static Mesh ropeMesh, cableMesh;

		/// <summary>The line's material and unit mesh (the line along z): the ferry's rope on timber (its painted rows), galvanised
		/// cable on steel. tile: how long one picture runs at the drawn thickness.</summary>
		private static Material LineMat(SuspensionTier t, out Mesh mesh, out float tile)
		{
			bool cable = RM_DrawbridgeMath.IsPowered(t);
			float v0 = cable ? 0f : 26f / 64f, v1 = cable ? 1f : 38f / 64f;
			if (cable)
			{
				mesh = cableMesh ?? (cableMesh = LineMesh("RM_DrawbridgeCable", v0, v1));
				tile = LineThick * 8f;
				return MatOrNull("RimMandrake/FlowWorks/SuspensionBridge/Cables/RM_Cable_Galv");
			}
			mesh = ropeMesh ?? (ropeMesh = LineMesh("RM_DrawbridgeRope", v0, v1));
			tile = LineThick * 256f / 12f;
			return MatOrNull("Things/Building/FlowWorks/Rivers/RM_FerryRope");
		}

		/// <summary>A unit plane whose z runs along the picture's u, its x across the rows v0..v1.</summary>
		private static Mesh LineMesh(string name, float v0, float v1)
		{
			var m = new Mesh
			{
				name = name,
				vertices = new[] { new Vector3(-0.5f, 0f, -0.5f), new Vector3(-0.5f, 0f, 0.5f), new Vector3(0.5f, 0f, 0.5f), new Vector3(0.5f, 0f, -0.5f) },
				uv = new[] { new Vector2(0f, v0), new Vector2(1f, v0), new Vector2(1f, v1), new Vector2(0f, v1) },
				triangles = new[] { 0, 1, 2, 0, 2, 3 },
			};
			m.RecalculateNormals();
			m.RecalculateBounds();
			return m;
		}

		private static void Line(Vector3 o, DrawbridgeFrameMath.P a, DrawbridgeFrameMath.P b, Material mat, Mesh mesh, float tile, float y)
		{
			Vector3 s = new Vector3(o.x + (float)a.X, y, o.z + (float)a.Z), e = new Vector3(o.x + (float)b.X, y, o.z + (float)b.Z);
			float len = (e - s).magnitude;
			if (len < 1e-3f)
			{
				return;
			}
			int n = Mathf.Max(1, Mathf.RoundToInt(len / tile));
			Quaternion q = Quaternion.LookRotation(e - s);
			for (int i = 0; i < n; i++)
			{
				Graphics.DrawMesh(mesh, Matrix4x4.TRS(Vector3.Lerp(s, e, (i + 0.5f) / n), q, new Vector3(LineThick, 1f, len / n + 0.01f)), mat, 0);
			}
		}

		private static readonly Dictionary<string, Material> leafDeckMats = new Dictionary<string, Material>();

		/// <summary>The lowered leaf's picture on one deck square and its turn: the raised leaf's own Face slice, so a raise starts
		/// from the picture on the ground (no pop at angle 0). Null when the square is not a drawbridge's, or no Face picture exists.</summary>
		public static Material LeafDeckMat(Building_SuspensionDeck deck, SuspensionBridgeRecord r, out float angle)
		{
			angle = 0f;
			if (r == null || !r.IsDrawbridge || r.raidPlank || !r.TryIndexOf(deck.Position, out _, out int i) || !(RM_Drawbridges.LeafOf(r, i) is DrawbridgeLeaf l))
			{
				return null;
			}
			Material mat = LeafUp(r.tier, LookOf(r), LeafView.Face, out string path);
			if (mat == null || path == null || !path.Contains("LeafUp"))
			{
				return null;
			}
			angle = (l.hingeAtFirst ? r.dir : r.dir.Opposite).AsAngle;
			int slice = DrawbridgeLeafPose.SliceFor(l.Span.FromHinge(i), l.Span.Length);
			string key = path + "|" + slice;
			if (!leafDeckMats.TryGetValue(key, out Material m) || m == null)
			{
				m = new Material(mat)
				{
					name = mat.name + "_slice" + slice,
					mainTextureOffset = new Vector2(LeafU0, (float)slice / DrawbridgeLeafPose.Slices),
					mainTextureScale = new Vector2(LeafU1 - LeafU0, 1f / DrawbridgeLeafPose.Slices),
				};
				leafDeckMats[key] = m;
			}
			return m;
		}

		public static bool PrintLeafDeck(SectionLayer layer, Building_SuspensionDeck deck, SuspensionBridgeRecord r)
		{
			Material m = LeafDeckMat(deck, r, out float angle);
			if (m == null)
			{
				return false;
			}
			Printer_Plane.PrintPlane(layer, deck.TrueCenter(), Vector2.one, m, angle);
			return true;
		}

		// ── the gate frame and the mooring (option B, his rulings of 2026-11-03) ───────────────────────────────

		/// <summary>A drawbridge's anchor: on the hinge bank its square of the threshold and (lane 0, for the whole width) the gate
		/// frame, two posts and one lintel cut from the picked open gate; on the far bank (lane 0) the footing and the two
		/// mooring posts. False when the anchor is not a drawbridge's (it prints as before).</summary>
		public static bool PrintDrawbridgeEnd(SectionLayer layer, Building_SuspensionAnchor anchor)
		{
			SuspensionBridgeRecord r = anchor.Map?.GetComponent<RM_MapComponent_SuspensionBridges>()?.RecordAt(anchor.Position);
			if (r == null || !r.IsDrawbridge || !r.TryIndexOf(anchor.Position, out int lane, out int i))
			{
				return false;
			}
			foreach (DrawbridgeLeaf l in r.leaves)
			{
				IntVec3 step = l.hingeAtFirst ? r.dir.FacingCell : r.dir.Opposite.FacingCell;
				if (RM_Drawbridges.HingeIndex(l) == i)
				{
					DrawbridgeArtPaths.FrameArt art = DrawbridgeArtPaths.Frame(r.tier);
					Vector3 c = anchor.TrueCenter();
					c.y = AltitudeLayer.FloorEmplacement.AltitudeFor();
					PrintRect(layer, art.Pad, c, 1f, 1f, (l.hingeAtFirst ? r.dir : r.dir.Opposite).AsAngle + art.PadTurn);
					if (lane == 0)
					{
						PrintFrame(layer, r, art, step, Lip(r, l, step));
					}
					return true;
				}
			}
			DrawbridgeLeaf end = r.leaves[i == 0 ? 0 : r.leaves.Count - 1];
			foreach (DrawbridgeLeaf l in r.leaves)
			{
				if (l.hingeAtFirst ? l.last == r.length - 2 && i == r.length - 1 : l.first == 1 && i == 0)
				{
					end = l;
				}
			}
			if (lane == 0)
			{
				PrintMooring(layer, r, end);
			}
			return true;
		}

		private static void PrintFrame(SectionLayer layer, SuspensionBridgeRecord r, DrawbridgeArtPaths.FrameArt art, IntVec3 step, Vector3 o)
		{
			IntVec3 side = r.Side;
			Vector3 At(DrawbridgeFrameMath.P p) => o + new Vector3((float)p.X, 0f, (float)p.Z);
			Vector3 a = At(DrawbridgeFrameMath.Post(step.x, step.z, side.x, side.z, r.width, -1));
			Vector3 b = At(DrawbridgeFrameMath.Post(step.x, step.z, side.x, side.z, r.width, 1));
			float postY = AltitudeLayer.BuildingOnTop.AltitudeFor() + Altitudes.AltInc;
			float topY = AltitudeLayer.PawnUnused.AltitudeFor();   // the lintel is overhead: over whoever walks through
			float w = (float)DrawbridgeFrameMath.PostW, h = (float)DrawbridgeFrameMath.PostH;
			if (step.x == 0)
			{
				Vector3 left = a.x < b.x ? a : b, right = a.x < b.x ? b : a;
				float x0 = left.x + w * 0.5f - 0.02f, x1 = right.x - w * 0.5f + 0.02f;
				float top = left.z + h - art.BeamDrop, beam = art.BeamDepth;
				int n = Mathf.Max(1, Mathf.RoundToInt((x1 - x0) / DrawbridgeArtPaths.BeamUnit));
				for (int k = 0; k < n; k++)
				{
					PrintRect(layer, art.Beam, new Vector3(x0 + (x1 - x0) * (k + 0.5f) / n, topY, top - beam * 0.5f), (x1 - x0) / n + 0.004f, beam, 0f);
				}
				PrintRect(layer, art.PostLeft, new Vector3(left.x, postY, left.z + h * 0.5f), w, h, 0f);
				PrintRect(layer, art.PostRight, new Vector3(right.x, postY, right.z + h * 0.5f), w, h, 0f);
				return;
			}
			Vector3 back = a.z > b.z ? a : b, front = a.z > b.z ? b : a;   // edge-on: the far post, the lintel end to end, the near post
			const float pw = 0.34f;
			PrintRect(layer, art.PostEdge, new Vector3(back.x, postY, back.z + h * 0.5f), pw, h, 0f);
			float z0 = front.z + h - 0.12f, z1 = back.z + h - 0.10f;
			Material ink = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Cutout, Ink);
			Printer_Plane.PrintPlane(layer, new Vector3(front.x, topY, (z0 + z1) * 0.5f), new Vector2(0.32f, z1 - z0), ink, 0f, false, null, null, 0f);
			int m = Mathf.Max(1, Mathf.RoundToInt((z1 - z0) / 0.5f));
			for (int k = 0; k < m; k++)
			{
				PrintRect(layer, art.BeamTop, new Vector3(front.x, topY + Altitudes.AltInc * 0.1f, z0 + (z1 - z0) * (k + 0.5f) / m), (z1 - z0) / m, 0.27f, 90f);
			}
			PrintRect(layer, art.PostEdge, new Vector3(front.x, topY + Altitudes.AltInc * 0.2f, front.z + h * 0.5f), pw, h, 0f);
		}

		/// <summary>The far bank: a footing and two mooring posts the width of the bridge, which carry nothing while the leaf is up.</summary>
		private static void PrintMooring(SectionLayer layer, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			IntVec3 step = l.hingeAtFirst ? r.dir.FacingCell : r.dir.Opposite.FacingCell;
			IntVec3 side = r.Side;
			Vector3 o = Lip(r, l, step);
			DrawbridgeArtPaths.FrameArt art = DrawbridgeArtPaths.Frame(r.tier);
			int length = l.Span.Length;
			Vector3 f = o + step.ToVector3() * (length + 0.26f);
			f.y = AltitudeLayer.FloorEmplacement.AltitudeFor();
			Vector2 size = step.x == 0 ? new Vector2(r.width, 0.36f) : new Vector2(0.36f, r.width);
			Printer_Plane.PrintPlane(layer, f, size + Vector2.one * 0.06f, MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Cutout, Ink), 0f, false, null, null, 0f);
			f.y += Altitudes.AltInc * 0.2f;
			PrintRect(layer, DrawbridgeArtPaths.Footing, f, size.x, size.y, 0f, 0.55f);
			float y = AltitudeLayer.Building.AltitudeFor();
			for (int k = 0; k < 2; k++)
			{
				int sgn = k == 0 ? -1 : 1;
				DrawbridgeFrameMath.P p = DrawbridgeFrameMath.Moor(step.x, step.z, side.x, side.z, r.width, length, sgn);
				Vector3 at = o + new Vector3((float)p.X, 0f, (float)p.Z + art.MoorH * 0.5f - 0.1f);
				at.y = y - at.z * 0.0005f;   // the southern post over the northern one
				PrintRect(layer, art.Moor, at, art.MoorW, art.MoorH, 0f);
			}
		}

		/// <summary>Print a pixel rectangle of a picture as a w × h plane turned by rot (grey &lt; 1 darkens it).</summary>
		private static void PrintRect(SectionLayer layer, DrawbridgeArtPaths.Cut cut, Vector3 at, float w, float h, float rot, float grey = 1f)
		{
			Material m = grey < 1f ? MaterialPool.MatFrom(cut.Path, ShaderDatabase.Cutout, new Color(grey, grey, grey)) : MatOrNull(cut.Path);
			if (m == null)
			{
				return;
			}
			Printer_Plane.PrintPlane(layer, at, new Vector2(w, h), m, rot, false, new[]
			{
				new Vector2(cut.U0, cut.V0), new Vector2(cut.U0, cut.V1), new Vector2(cut.U1, cut.V1), new Vector2(cut.U1, cut.V0),
			}, null, 0f);   // no tilt: with the default top-vertex lift a tall piece cuts through a short one on the same layer
		}

		private static readonly Mesh[] leafSlices = new Mesh[DrawbridgeLeafPose.Slices];

		/// <summary>The columns of the Face picture that hold the leaf's body (its hooks and margins dropped), so lanes abut and a
		/// lane fills its whole square: measured on RM_DrawbridgeLeafUp_Timber_Face and _Steel_Face (31..241 of 256).</summary>
		public const float LeafU0 = 31f / 256f, LeafU1 = 241f / 256f;

		/// <summary>A unit plane (x, z in -0.5..0.5, as MeshPool.plane10) showing one quarter of the 1 x 4 leaf picture, slice
		/// 0 the root (the hinge, the picture's bottom) to slice 3 the tip.</summary>
		public static Mesh LeafSlice(int slice)
		{
			Mesh m = leafSlices[slice];
			if (m != null)
			{
				return m;
			}
			float v0 = (float)slice / DrawbridgeLeafPose.Slices, v1 = (float)(slice + 1) / DrawbridgeLeafPose.Slices;
			m = new Mesh
			{
				name = "RM_LeafSlice" + slice,
				vertices = new[] { new Vector3(-0.5f, 0f, -0.5f), new Vector3(-0.5f, 0f, 0.5f), new Vector3(0.5f, 0f, 0.5f), new Vector3(0.5f, 0f, -0.5f) },
				uv = new[] { new Vector2(LeafU0, v0), new Vector2(LeafU0, v1), new Vector2(LeafU1, v1), new Vector2(LeafU1, v0) },
				triangles = new[] { 0, 1, 2, 0, 2, 3 },
			};
			m.RecalculateNormals();
			m.RecalculateBounds();
			leafSlices[slice] = m;
			return m;
		}

		/// <summary>How one anchor's picture is printed (as Graphic.Print prints it) and which ropes it paints.</summary>
		public sealed class AnchorPrint
		{
			public Material mat;
			public string facing;
			public bool flip;
			public float angle;
			public Vector3 center;
			public RM_DrawbridgeCableMath.RopeArt[] ropes;
			/// <summary>The deck square the ropes face is a raised leaf: the ropes lie slack on the bank, disconnected.</summary>
			public bool slack;
			/// <summary>Where a slack coil lies: the upright post's foot (a styled _north print), else -1 (ahead of the attachment).</summary>
			public double foot = -1;
			/// <summary>+1 when the rope frame's +lateral is the print's local +x (a mirrored print), else -1.</summary>
			public float hand;

			public Vector3 World(double a, double l)
			{
				(double x, double z) = RM_DrawbridgeCableMath.ToWorld(facing, flip, angle, a, l);
				return new Vector3(center.x + (float)x, center.y, center.z + (float)z);
			}
		}

		/// <summary>DRAWBRIDGE_CABLES_FIX_STOP_SHORT: the rope print of an anchor whose ropes face a deck square, or null (no deck
		/// ahead, a picture without a measured rope table, an unexpected print): then the anchor prints as before.</summary>
		public static AnchorPrint AnchorPrintFor(Thing a)
		{
			Map map = a?.Map;
			Graphic g = a?.Graphic;
			if (map == null || g == null || g.drawSize != Vector2.one)
			{
				return null;
			}
			Building_SuspensionDeck deck = RM_MapComponent_SuspensionBridges.StructuralDeckAt(map, a.Position + a.Rotation.FacingCell);
			if (deck == null)
			{
				return null;
			}
			Rot4 rot = a.Rotation;
			bool rotated = g.ShouldDrawRotated;
			string key = RM_DrawbridgeCableMath.KeyOf(g.path, g is Graphic_Multi && !rotated);
			if (key == null || (g is Graphic_Multi) == rotated)
			{
				return null;   // a styled picture prints unrotated per facing; the unstyled single prints rotated
			}
			var p = new AnchorPrint { slack = deck.leafRaised, mat = g.MatAt(rot, a) };
			if (rotated)
			{
				p.facing = "single";
				p.flip = false;
				p.angle = rot.AsAngle + g.DrawRotatedExtraAngleOffset;
			}
			else
			{
				if ((rot == Rot4.West && !g.WestFlipped) || (rot == Rot4.East && g.EastFlipped))
				{
					return null;   // a _west picture of its own: not measured
				}
				p.facing = rot == Rot4.North ? "north" : rot == Rot4.South ? "south" : "east";
				p.flip = rot == Rot4.West;
				p.angle = 0f;
			}
			p.ropes = RM_DrawbridgeCableMath.RopesFor(key, p.facing);   // upright bollards: per-facing attachment
			if (p.ropes == null)
			{
				return null;   // no measured rope table for this print (a rotated single): prints as before
			}
			p.foot = RM_DrawbridgeCableMath.SlackFoot(key, p.facing);
			p.center = a.TrueCenter() + g.DrawOffset(rot);
			Vector3 dir = p.World(1, 0) - p.World(0, 0);
			IntVec3 f = rot.FacingCell;
			if (Mathf.Abs(dir.x - f.x) > 0.01f || Mathf.Abs(dir.z - f.z) > 0.01f)
			{
				return null;   // the picture's ropes do not point at the deck
			}
			Vector3 lat = p.World(0, 1) - p.World(0, 0);
			p.hand = Vector3.Dot(lat, new Vector3(dir.z, 0f, -dir.x)) > 0f ? 1f : -1f;   // right of the rope direction
			return p;
		}

		/// <summary>A raised leaf's anchor: its picture up to the ropes' attachment points only (the bollards), the painted
		/// taut ropes cut away.</summary>
		public static void PrintBollards(SectionLayer layer, AnchorPrint p)
		{
			double cut = 1.0;
			foreach (RM_DrawbridgeCableMath.RopeArt r in p.ropes)
			{
				cut = System.Math.Min(cut, r.Attach);
			}
			PrintFrameRect(layer, p, 0.0, cut, 0.0, 1.0);
		}

		/// <summary>The rope-frame rectangle along [a0,a1] × lateral (lmid ± lspan/2) of the anchor picture, printed in place.</summary>
		private static void PrintFrameRect(SectionLayer layer, AnchorPrint p, double a0, double a1, double lmid, double lspan)
		{
			Vector3 c = p.World((a0 + a1) / 2, lmid);
			Vector3 along = p.World(a1, lmid) - p.World(a0, lmid);
			float rot = (float)RM_DrawbridgeCableMath.AngleOf(along.x, along.z);
			var uvs = new Vector2[4];
			int i = 0;
			foreach ((float sx, float sz) in Corners)
			{
				double a = (a0 + a1) / 2 + sz * (a1 - a0);
				double l = lmid + p.hand * sx * lspan;
				(double u, double v) = RM_DrawbridgeCableMath.ToUV(p.facing, a, l);
				uvs[i++] = new Vector2((float)u, (float)v);
			}
			Printer_Plane.PrintPlane(layer, c, new Vector2((float)lspan, (float)(a1 - a0)), p.mat, rot, false, uvs);
		}

		/// <summary>PrintPlane's corner order, as (local x, local z) in half units.</summary>
		private static readonly (float, float)[] Corners = { (-0.5f, -0.5f), (-0.5f, 0.5f), (0.5f, 0.5f), (0.5f, -0.5f) };

		/// <summary>The drawn ropes: lowered, each taut rope's run from its painted end to past the deck-facing edge under the
		/// deck; raised, each rope's slack loop on the bank. Every piece is cut from the picture's own painted rope.</summary>
		public static void PrintRopes(SectionLayer layer, AnchorPrint p)
		{
			Vector3 along = p.World(1, 0) - p.World(0, 0);
			bool vertical = Mathf.Abs(along.z) > Mathf.Abs(along.x);   // the rope runs up/down the screen (rotations N/S)
			foreach (RM_DrawbridgeCableMath.RopeArt r in p.ropes)
			{
				if (p.slack)
				{
					List<(double A, double L)> pts = RM_DrawbridgeCableMath.Slack(r, vertical, p.foot);   // a coil flat on the ground in every rotation; round an upright post's foot
					double src = r.Attach + 0.01;
					for (int i = 0; i + 1 < pts.Count; i++)
					{
						src = PrintRopeRun(layer, p, r, p.World(pts[i].A, pts[i].L), p.World(pts[i + 1].A, pts[i + 1].L), src);
					}
					continue;
				}
				foreach (RM_DrawbridgeCableMath.Piece pc in RM_DrawbridgeCableMath.Taut(r))
				{
					if (!pc.Painted)
					{
						PrintRopeRun(layer, p, r, p.World(pc.A0, pc.L0), p.World(pc.A1, pc.L1), r.End - (pc.A1 - pc.A0) - 0.01);
					}
				}
			}
		}

		/// <summary>One straight run of rope from world point s to e, tiled from the painted rope (along [Attach, End] of the
		/// picture) starting at src; returns where the next run's source starts, so a curve's pattern runs on.</summary>
		private static double PrintRopeRun(SectionLayer layer, AnchorPrint p, RM_DrawbridgeCableMath.RopeArt r, Vector3 s, Vector3 e, double src)
		{
			double lo = r.Attach + 0.01, hi = r.End - 0.005;
			Vector3 d = e - s;
			float len = new Vector2(d.x, d.z).magnitude;
			if (len < 1e-4f || hi - lo < 0.02)
			{
				return src;
			}
			float rot = (float)RM_DrawbridgeCableMath.AngleOf(d.x, d.z);
			float pad = (float)r.Thick * 0.5f;   // overlap at the joints of a bent rope
			double done = 0;
			while (done < len - 1e-4)
			{
				if (src < lo || src > hi - 0.02)
				{
					src = lo;
				}
				double piece = System.Math.Min(len - done, hi - src);
				Vector3 mid = s + d * (float)((done + piece / 2) / len);
				double geo = piece + (p.slack ? pad : 0f);
				var uvs = new Vector2[4];
				int i = 0;
				foreach ((float sx, float sz) in Corners)
				{
					double a = src + (sz + 0.5) * System.Math.Min(geo, hi - src);
					double l = r.Lateral + p.hand * sx * r.Thick;
					(double u, double v) = RM_DrawbridgeCableMath.ToUV(p.facing, a, l);
					uvs[i++] = new Vector2((float)u, (float)v);
				}
				Printer_Plane.PrintPlane(layer, mid, new Vector2((float)r.Thick, (float)geo), p.mat, rot, false, uvs, null, 0f);
				done += piece;
				src += piece;
			}
			return src;
		}

		private static readonly Dictionary<string, Mesh> gatePanels = new Dictionary<string, Mesh>();

		/// <summary>The gate's own square draws only its panel (the frame over all lanes is the hinge anchor's, PrintFrame): shut, the
		/// picked gate's planks; opening, the panel sinks into its slot until only the sill shows, so an open gate is a clear
		/// doorway. Edge-on (an east or west bridge) it is the panel's edge. False when no picture exists: the vanilla door draws.</summary>
		public static bool DrawGate(Building_Door gate, Vector3 drawLoc, SuspensionTier t, string look, bool sideways, float openPct)
		{
			DrawbridgeArtPaths.Cut cut = DrawbridgeArtPaths.GatePanel(t, sideways);
			Material mat = MatOrNull(cut.Path);
			if (mat == null)
			{
				return false;
			}
			float shut = Mathf.Lerp(1f, 0.14f, Mathf.Clamp01(openPct));
			int step = Mathf.RoundToInt(shut * 20f);
			shut = step / 20f;
			Vector3 at = drawLoc;
			at.y = AltitudeLayer.DoorMoveable.AltitudeFor();
			if (sideways)
			{
				Graphics.DrawMesh(CutMesh(cut, 1f, 20), Matrix4x4.TRS(at, Quaternion.identity, new Vector3(0.24f * (0.3f + 0.7f * shut), 1f, 1f)), mat, 0);
				return true;
			}
			at.z += -0.39f + 0.45f * shut;
			for (int k = -1; k <= 1; k += 2)
			{
				Graphics.DrawMesh(CutMesh(cut, shut, step), Matrix4x4.TRS(at + new Vector3(k * 0.25f, 0f, 0f), Quaternion.identity, new Vector3(0.5f, 1f, 0.9f * shut)), mat, 0);
			}
			return true;
		}

		/// <summary>A unit plane showing the top `part` of a cut.</summary>
		private static Mesh CutMesh(DrawbridgeArtPaths.Cut cut, float part, int step)
		{
			string key = cut.Path + "|" + cut.U0 + "|" + cut.V0 + "|" + step;
			if (!gatePanels.TryGetValue(key, out Mesh m) || m == null)
			{
				float v0 = cut.V1 - (cut.V1 - cut.V0) * part;
				m = new Mesh
				{
					name = "RM_GatePanel" + step,
					vertices = new[] { new Vector3(-0.5f, 0f, -0.5f), new Vector3(-0.5f, 0f, 0.5f), new Vector3(0.5f, 0f, 0.5f), new Vector3(0.5f, 0f, -0.5f) },
					uv = new[] { new Vector2(cut.U0, v0), new Vector2(cut.U0, cut.V1), new Vector2(cut.U1, cut.V1), new Vector2(cut.U1, v0) },
					triangles = new[] { 0, 1, 2, 0, 2, 3 },
				};
				m.RecalculateNormals();
				m.RecalculateBounds();
				gatePanels[key] = m;
			}
			return m;
		}

		/// <summary>A laid raid plank square: the mid piece, or at either end the end piece with its hooks toward that bank;
		/// the art runs top to bottom, turned to the span. False for a square that is not on a raid plank record.</summary>
		public static bool PrintRaidPlank(SectionLayer layer, Building_SuspensionDeck deck, SuspensionBridgeRecord r)
		{
			if (r == null || !r.raidPlank)
			{
				return false;
			}
			Material mat = RaidPlankMat(deck, r, out float angle);
			if (mat == null)
			{
				return false;
			}
			Printer_Plane.PrintPlane(layer, deck.TrueCenter(), Vector2.one, mat, angle);
			return true;
		}

		/// <summary>The piece a laid raid plank square prints, and its turn: the one chooser PrintRaidPlank and the fade over a
		/// pawn beneath (Building_SuspensionDeck.FadeMaterial) share. Null for a square that is not on a raid plank record.</summary>
		public static Material RaidPlankMat(Building_SuspensionDeck deck, SuspensionBridgeRecord r, out float angle)
		{
			angle = 0f;
			if (r == null || !r.raidPlank || !r.TryIndexOf(deck.Position, out _, out int i))
			{
				return null;
			}
			DrawbridgeArtPaths.RaidPlankPiece piece = DrawbridgeArtPaths.PieceAt(i, r.length);
			if (piece == DrawbridgeArtPaths.RaidPlankPiece.None)
			{
				return null;
			}
			Material mat = piece == DrawbridgeArtPaths.RaidPlankPiece.Mid
				? MatOrNull(DrawbridgeArtPaths.RaidPlankLaid)
				: MatOrNull(DrawbridgeArtPaths.RaidPlankLaidEnd, DrawbridgeArtPaths.RaidPlankLaid);
			Rot4 top = DrawbridgeArtPaths.TopTowardLip(piece) ? r.dir.Opposite : r.dir;
			angle = top.AsAngle;
			return mat;
		}
	}
}
