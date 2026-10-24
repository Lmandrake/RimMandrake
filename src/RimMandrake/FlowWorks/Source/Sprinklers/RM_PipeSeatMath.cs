// SPRINKLER_HEAD_FIX_FLOATS_OFF_CURVE (owner 2026-10-23: "Sprinkler on a curved pipe segment is no longer on pipe").
// Pure, Verse-free: compiled into the SelfTest console app as well as the mod.
using System;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>
	/// Where the universal pipe's DRAWN centreline crosses its own cell, per link mask and look, as an offset from the cell
	/// centre (x east, z north, in cells). A fitting set on the pipe (sprinkler head, pipe faucet) is printed at that point so
	/// it sits on the pipe and not beside a bend.
	///
	/// The pipe is vanilla Graphic_Linked over a 4x4 atlas (mask bits N=1 E=2 S=4 W=8). Ends, straights, tees and the cross
	/// run their axis through the cell centre, so their seat is (0,0). Only the four elbows (N+E, E+S,
	/// S+W, W+N) bend away: their centreline is a quarter arc of radius r about a corner point k*(sx,sz) on the elbow's
	/// outer side, and the seat is that arc's midpoint, on the diagonal through the cell centre:
	///   seat = (k - r/sqrt2) * (sx, sz),  sx = E ? +1 : -1,  sz = N ? +1 : -1.
	/// Measured on the shipped atlases (art_source/pipe; 704 px atlas, 176 px tile, 132 px shown cell) by
	/// Tools/selftest_pipe_seat.py, which fails if a redrawn atlas moves the arc by more than 1 px:
	///   Scrapper (compose_scrapper_v2): arc radius C/2 about the SHOWN cell's corner: k = r = 0.5   -> 0.2071 along the diagonal
	///   Industrial/Modern/Futuristic (build_pipe_atlas): radius 88 tile px about the TILE corner: k = r = 2/3 -> 0.2761
	/// The lone stub (mask 0, a pipe with no neighbour) is a round flange: centred in three looks, but drawn 4 px east and
	/// 4 px south of centre in the Scrapper atlas, so the seat follows it there.
	/// A look this table does not know gets (0,0): the old behaviour, never a guess.
	/// </summary>
	public static class RM_PipeSeatMath
	{
		public const int N = 1, E = 2, S = 4, W = 8;

		/// <summary>Pixels across the shown cell of a 704 px pipe atlas (176 px tile less 2 x 22 px padding).</summary>
		public const float ShownCellPx = 132f;

		/// <summary>How far east (and south) of centre the Scrapper lone-stub flange is drawn, in atlas pixels.</summary>
		public const float LoneStubScrapperPx = 4f;

		/// <summary>The elbow arc of a look: corner distance k and radius r, both in cells. False for an unknown look.</summary>
		public static bool ElbowArc(string look, out float k, out float r)
		{
			switch (look)
			{
				case "Scrapper":
					k = 0.5f; r = 0.5f; return true;
				case "Industrial":
				case "Modern":
				case "Futuristic":
					k = 2f / 3f; r = 2f / 3f; return true;
				default:
					k = 0f; r = 0f; return false;
			}
		}

		/// <summary>True for the four corner masks (exactly one of N/S and one of E/W).</summary>
		public static bool IsElbow(int mask)
		{
			mask &= 15;
			return mask == (N | E) || mask == (E | S) || mask == (S | W) || mask == (W | N);
		}

		/// <summary>The seat offset (x east, z north, cells) for a pipe of <paramref name="look"/> drawn with link
		/// <paramref name="mask"/>.</summary>
		public static void Seat(int mask, string look, out float x, out float z)
		{
			x = 0f; z = 0f;
			if ((mask & 15) == 0)
			{
				if (look == "Scrapper") { x = LoneStubScrapperPx / ShownCellPx; z = -LoneStubScrapperPx / ShownCellPx; }
				return;
			}
			if (!IsElbow(mask) || !ElbowArc(look, out float k, out float r)) return;
			float sx = (mask & E) != 0 ? 1f : -1f;
			float sz = (mask & N) != 0 ? 1f : -1f;
			float d = k - r / (float)Math.Sqrt(2.0);
			x = d * sx;
			z = d * sz;
		}

		/// <summary>The look named by a pipe atlas texPath ".../Pipe/&lt;Look&gt;/..."; null when the path names none.</summary>
		public static string LookOfTexPath(string texPath)
		{
			if (string.IsNullOrEmpty(texPath)) return null;
			string p = texPath.Replace('\\', '/');
			int i = p.IndexOf("/Pipe/", StringComparison.Ordinal);
			if (i < 0) return null;
			int s = i + 6;
			int e = p.IndexOf('/', s);
			return e > s ? p.Substring(s, e - s) : null;
		}
	}
}
