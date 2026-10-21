using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 6 (R12): the drawbridge pictures, read from the texPaths of the design doc's art
	/// contract (flowworks_drawbridge_design_2026-10-20.md §R12 "Art contract"). The commissioned art does not exist on disk
	/// until it passes review and `art install`, so every picture is looked up SILENTLY (ContentFinder, no error) and falls
	/// back to a stand-in that does exist: the suspension deck tile for the raised leaf and the planks, the anchor for the
	/// winch, the vanilla door for the gate, vanilla command icons. When an installed picture appears it is used with no code
	/// change. Nothing here generates or queues art.
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_DrawbridgeArt
	{
		public const string Dir = "Things/Building/FlowWorks/Drawbridge/";

		public enum LeafView
		{
			Face,
			Underside,
			Edge,
		}

		private static readonly Dictionary<string, Material> mats = new Dictionary<string, Material>();

		public static string Material(SuspensionTier t)
		{
			return t == SuspensionTier.Steel ? "Steel" : "Timber";
		}

		/// <summary>The contract path of the raised leaf in this view.</summary>
		public static string LeafUpPath(SuspensionTier t, LeafView v)
		{
			return Dir + "RM_DrawbridgeLeafUp_" + Material(t) + "_" + v;
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

		public static Material LeafUp(SuspensionTier t, LeafView v)
		{
			return MatOrNull(LeafUpPath(t, v), "Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_" + Material(t));
		}

		public static Material Planks(SuspensionTier t)
		{
			return MatOrNull(Dir + "RM_DrawbridgePlanks_" + Material(t), "Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_" + Material(t));
		}

		public static Texture2D Icon(string name, Texture2D fallback)
		{
			return ContentFinder<Texture2D>.Get("UI/Commands/FlowWorks/" + name, false) ?? fallback;
		}

		/// <summary>The winch house picture: the contract's Graphic_Multi when installed (its _south file exists), else the
		/// def's own stand-in. Swapped once at startup.</summary>
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

		/// <summary>Draw a raised leaf upright at its hinge: one copy per lane, standing on the hinge edge of the anchor square,
		/// its height the leaf length scaled by how far it has risen (the art is 1 lane × 4 cells; a longer steel leaf stretches).</summary>
		public static void DrawLeafUp(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			int full = RM_Drawbridges.FullTicks(r, l);
			if (l.progress <= 0 || full <= 0)
			{
				return;
			}
			IntVec3 step = l.hingeAtFirst ? r.dir.FacingCell : r.dir.Opposite.FacingCell;   // hinge toward the leaf
			Rot4 spanFromHinge = Rot4.FromIntVec3(step);
			Material mat = LeafUp(r.tier, ViewFor(spanFromHinge));
			if (mat == null)
			{
				return;
			}
			float rise = Mathf.Clamp01((float)l.progress / full);
			float h = l.Span.Length * rise;
			int hinge = RM_Drawbridges.HingeIndex(l);
			for (int lane = 0; lane < r.width; lane++)
			{
				Vector3 at = r.Cell(lane, hinge).ToVector3Shifted() + step.ToVector3() * 0.5f;   // the hinge edge
				at.z += h * 0.5f;
				at.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
				Matrix4x4 m = Matrix4x4.TRS(at, Quaternion.identity, new Vector3(1f, 1f, h));
				Graphics.DrawMesh(MeshPool.plane10, m, mat, 0);
			}
		}

		/// <summary>The art planks, stacked beside the hinge anchor (outside lane 0): art only, never an item (answer 1).</summary>
		public static void DrawPlanks(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			Material mat = Planks(r.tier);
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
	}
}
