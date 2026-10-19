using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// SUSPENSION_DECK_LINKED_NO_SEAMS: a deck square draws from a Basic-linked 4x4 atlas (vanilla's MaterialAtlasPool format, the
	/// universal pipe's own), so a lane's neighbours carry the surface across and only a free side shows the side band. The atlas
	/// tile runs N-S; a deck square of an E-W bridge turns the tile a quarter clockwise and the mask is remapped to match.
	/// The neighbours that link are other deck squares and the bridge's anchors (the run continues into the post), checked here
	/// rather than through the def's linkFlags so no other linked thing in the game joins a deck.
	/// Mirrors art_source/SuspensionLooks/build_deck_atlas.py tile_mask (selftest_flowworks_suspension_linked.py keeps the pair honest).
	/// </summary>
	public static class RM_SuspensionDeckLink
	{
		/// <summary>The atlas index (tile frame: N=1, E=2, S=4, W=8) for the map-frame links n/e/s/w. A tile turned a quarter
		/// clockwise shows its N side toward map East, its E side toward South, its S side toward West and its W side toward North.</summary>
		public static int TileMask(bool n, bool e, bool s, bool w, bool horizontal)
		{
			bool[] map = { n, e, s, w };
			int shift = horizontal ? 1 : 0;
			int mask = 0;
			for (int k = 0; k < 4; k++)
			{
				if (map[(k + shift) % 4])
				{
					mask |= 1 << k;
				}
			}
			return mask;
		}

		public static bool LinksTo(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t is Building_SuspensionDeck || t is Building_SuspensionAnchor)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The deck square's tile (the picture to draw and the turn it needs): the linked atlas tile for its neighbours, or
		/// its plain material turned by the thing's rotation when its graphic is not linked.</summary>
		public static Material TileFor(Building_SuspensionDeck deck, out float angle)
		{
			if (deck.Graphic is Graphic_Linked graphic && graphic.SubGraphic != null)
			{
				Map map = deck.Map;
				IntVec3 p = deck.Position;
				bool horizontal = deck.Rotation.IsHorizontal;
				int mask = TileMask(LinksTo(map, p + IntVec3.North), LinksTo(map, p + IntVec3.East),
					LinksTo(map, p + IntVec3.South), LinksTo(map, p + IntVec3.West), horizontal);
				angle = horizontal ? 90f : 0f;
				return MaterialAtlasPool.SubMaterialFromAtlas(graphic.SubGraphic.MatSingleFor(deck), (LinkDirections)mask);
			}
			angle = deck.Rotation.AsAngle;
			return deck.Graphic?.MatSingle;
		}

		public static void Print(SectionLayer layer, Building_SuspensionDeck deck)
		{
			Material mat = TileFor(deck, out float angle);
			Printer_Plane.PrintPlane(layer, deck.TrueCenter(), Vector2.one, mat, angle);
		}
	}
}
