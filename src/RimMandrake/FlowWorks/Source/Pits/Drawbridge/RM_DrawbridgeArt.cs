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

		public static Material Planks(SuspensionTier t, string look)
		{
			List<string> c = new List<string>(DrawbridgeArtPaths.Planks(t, look));
			c.Add("Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_" + Material(t));
			return MatOrNull(c.ToArray());
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
					if (l.winch != null && l.winch.Spawned)
					{
						DrawPlanks(map, r, l);
					}
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
					Graphics.DrawMesh(LeafSlice(DrawbridgeLeafPose.SliceFor(i, length)), m, mat, 0);
				}
			}
		}

		private static readonly Mesh[] leafSlices = new Mesh[DrawbridgeLeafPose.Slices];

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
				uv = new[] { new Vector2(0f, v0), new Vector2(0f, v1), new Vector2(1f, v1), new Vector2(1f, v0) },
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

		/// <summary>The art planks, stacked beside the hinge anchor (outside lane 0): art only, never an item (answer 1).</summary>
		public static void DrawPlanks(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			Material mat = Planks(r.tier, LookOf(r));
			if (mat == null)
			{
				return;
			}
			IntVec3 c = r.Cell(0, RM_Drawbridges.HingeIndex(l)) - r.Side;
			if (!c.InBounds(map))
			{
				return;
			}
			Vector3 at = c.ToVector3Shifted();
			at.y = AltitudeLayer.ItemImportant.AltitudeFor();
			Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(at, Quaternion.Euler(0f, r.dir.AsAngle, 0f), new Vector3(0.7f, 1f, 0.7f)), mat, 0);
		}

		/// <summary>A gate drawn in its picked art: 1 wide × 1.5 tall, standing on its own square (the top half-cell overlaps the
		/// square behind it, as a wall's top does). False when no picture exists for this state, and the vanilla door draws.</summary>
		public static bool DrawGate(Building_Door gate, Vector3 drawLoc, SuspensionTier t, string look, bool open)
		{
			Material mat = Gate(t, look, open, gate.Rotation);
			if (mat == null)
			{
				return false;
			}
			Vector3 at = drawLoc;
			at.y = AltitudeLayer.DoorMoveable.AltitudeFor();
			at.z += 0.25f;
			Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(at, Quaternion.identity, new Vector3(1f, 1f, 1.5f)), mat, 0);
			return true;
		}

		/// <summary>A laid raid plank square: the mid piece, or at either end the end piece with its hooks toward that bank;
		/// the art runs top to bottom, turned to the span. False for a square that is not on a raid plank record.</summary>
		public static bool PrintRaidPlank(SectionLayer layer, Building_SuspensionDeck deck, SuspensionBridgeRecord r)
		{
			if (r == null || !r.raidPlank || !r.TryIndexOf(deck.Position, out _, out int i))
			{
				return false;
			}
			DrawbridgeArtPaths.RaidPlankPiece piece = DrawbridgeArtPaths.PieceAt(i, r.length);
			if (piece == DrawbridgeArtPaths.RaidPlankPiece.None)
			{
				return false;
			}
			Material mat = piece == DrawbridgeArtPaths.RaidPlankPiece.Mid
				? MatOrNull(DrawbridgeArtPaths.RaidPlankLaid)
				: MatOrNull(DrawbridgeArtPaths.RaidPlankLaidEnd, DrawbridgeArtPaths.RaidPlankLaid);
			if (mat == null)
			{
				return false;
			}
			Rot4 top = DrawbridgeArtPaths.TopTowardLip(piece) ? r.dir.Opposite : r.dir;
			Printer_Plane.PrintPlane(layer, deck.TrueCenter(), Vector2.one, mat, top.AsAngle);
			return true;
		}
	}
}
