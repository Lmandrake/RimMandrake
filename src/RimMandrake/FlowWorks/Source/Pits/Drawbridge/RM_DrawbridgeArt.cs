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

		/// <summary>The raised view of a leaf whose span runs this way from its hinge (contract: north shows the face, south the
		/// underside, east/west the edge).</summary>
		public static LeafView ViewFor(Rot4 spanFromHinge)
		{
			return spanFromHinge == Rot4.North ? LeafView.Face : spanFromHinge == Rot4.South ? LeafView.Underside : LeafView.Edge;
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
			List<string> c = new List<string>(DrawbridgeArtPaths.LeafUp(t, look, v.ToString()));
			c.Add("Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_" + Material(t));
			return MatOrNull(c.ToArray());
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

		/// <summary>Draw a raised leaf upright at its hinge: one copy per lane, standing on the hinge edge of the anchor square,
		/// its height the leaf length scaled by how far it has risen (the art is 1 lane × 4 cells; a longer steel leaf stretches).
		/// The edge view is drawn for a span running east and mirrored for west (contract).</summary>
		public static void DrawLeafUp(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			int full = RM_Drawbridges.FullTicks(r, l);
			if (l.progress <= 0 || full <= 0)
			{
				return;
			}
			IntVec3 step = l.hingeAtFirst ? r.dir.FacingCell : r.dir.Opposite.FacingCell;   // hinge toward the leaf
			Rot4 spanFromHinge = Rot4.FromIntVec3(step);
			Material mat = LeafUp(r.tier, LookOf(r), ViewFor(spanFromHinge));
			if (mat == null)
			{
				return;
			}
			Mesh mesh = spanFromHinge == Rot4.West ? MeshPool.plane10Flip : MeshPool.plane10;
			float rise = Mathf.Clamp01((float)l.progress / full);
			float h = l.Span.Length * rise;
			int hinge = RM_Drawbridges.HingeIndex(l);
			for (int lane = 0; lane < r.width; lane++)
			{
				Vector3 at = r.Cell(lane, hinge).ToVector3Shifted() + step.ToVector3() * 0.5f;   // the hinge edge
				at.z += h * 0.5f;
				at.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
				Matrix4x4 m = Matrix4x4.TRS(at, Quaternion.identity, new Vector3(1f, 1f, h));
				Graphics.DrawMesh(mesh, m, mat, 0);
			}
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
