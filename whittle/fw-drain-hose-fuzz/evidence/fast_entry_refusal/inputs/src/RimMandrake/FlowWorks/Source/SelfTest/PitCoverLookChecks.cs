// PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT (owner 2026-10-24, a plank lid on the centre square of an open pit: "says it's a plank
// covered pit, but it sure doesn't look like it (empty pit appearance?)"): a lid beside an open pit square draws its own tier
// texture; a lid with none keeps the ground print (bar pit_covered_invisible). Offline checks on the production rules
// (RM_PitCoverLookMath) and on the production call sites that read them. Each case has a can-fail.
// NOT proven here: the live look (the owner's 3x3 pit with one centre lid; a wholly covered pit still invisible).
using System;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitCoverLookChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(System.IO.Path.Combine(rel));

        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PitCoverLook_lid_in_open_pit_shows_art", () =>
            {
                // the owner's shot: a 3x3 pit dug to 2 m (depth 4), one lid on the centre: all 8 neighbours show the hole
                Assert(RM_PitCoverLookMath.ShowsArt(new[] { 4, 4, 4, 4, 4, 4, 4, 4 }), "the centre lid of an open 3x3 pit shows its planks");
                // one open corner left (diagonal) still betrays the pit
                Assert(RM_PitCoverLookMath.ShowsArt(new[] { 0, 0, 0, 0, 0, 4, 0, 0 }), "one open neighbour, diagonal included, shows art");
                // a lid at the edge of a pit: ground on one side (0), off-map (-1), open pit on the other
                Assert(RM_PitCoverLookMath.ShowsArt(new[] { -1, -1, 0, 0, 6, 0, 0, -1 }), "a deeper open pit beside it shows art");
                Assert(!RM_PitCoverLookMath.ShowsArt(new[] { 0, 0, 0, 0, 0, 0, 0, 0 }), "can-fail: a wholly covered pit (lids and ground round it) prints ground");
                Assert(!RM_PitCoverLookMath.ShowsArt(new[] { -1, -1, -1, 0, 0, 0, 0, 0 }), "can-fail: the map edge betrays nothing");
                Assert(!RM_PitCoverLookMath.ShowsArt(null), "can-fail: no reading, no art");
            });

            Case("PitCoverLook_reprint_only_on_open_close", () =>
            {
                Assert(RM_PitCoverLookMath.FlipsNeighbourLids(0, 1), "the first cut beside a lid re-prints it");
                Assert(RM_PitCoverLookMath.FlipsNeighbourLids(4, 0), "a square filled back to ground re-prints the lids round it");
                Assert(!RM_PitCoverLookMath.FlipsNeighbourLids(4, 6), "can-fail: deepening an open pit changes no lid");
                Assert(!RM_PitCoverLookMath.FlipsNeighbourLids(0, 0), "can-fail: no change");
            });

            Case("PitCoverLook_occluder_piece_uv_matches_lid", () =>
            {
                int n = RM_PitCoverLookMath.UvSteps;
                Assert(RM_PitCoverLookMath.PieceUv(10, 20, 10f, 11f, 20f, 21f, out int u0, out int u1, out int v0, out int v1)
                    && u0 == 0 && u1 == n && v0 == 0 && v1 == n, "a whole-cell piece shows the whole texture");
                Assert(RM_PitCoverLookMath.PieceUv(10, 20, 10.25f, 10.75f, 20.5f, 21f, out u0, out u1, out v0, out v1)
                    && u0 == n / 4 && u1 == 3 * n / 4 && v0 == n / 2 && v1 == n, "a part piece shows its own window (north half, middle)");
                Assert(RM_PitCoverLookMath.PieceUv(10, 20, 9.5f, 10.5f, 19f, 22f, out u0, out u1, out v0, out v1)
                    && u0 == 0 && u1 == n / 2 && v0 == 0 && v1 == n, "a piece reaching past the cell clamps to it");
                Assert(RM_PitCoverLookMath.PieceUv(10, 20, 10.999f, 11f, 20f, 21f, out u0, out u1, out v0, out v1)
                    && u1 == n && u0 == n - 1, "a sliver at the east edge keeps one texel, inside the texture");
                Assert(!RM_PitCoverLookMath.PieceUv(10, 20, 11.5f, 12f, 20f, 21f, out _, out _, out _, out _),
                    "can-fail: a piece wholly outside the cell has no window");
                Assert(RM_PitCoverLookMath.PieceUv(10, 20, 10f, 11f, 20f, 21f, out u0, out u1, out v0, out v1)
                    && !(u0 == n / 4), "can-fail: a whole-cell piece is not a part window");
                Assert(RM_PitCoverLookMath.UvKey(0, n, 0, n) != RM_PitCoverLookMath.UvKey(0, n, 0, n - 1)
                    && RM_PitCoverLookMath.UvKey(1, 2, 3, 4) != RM_PitCoverLookMath.UvKey(3, 4, 1, 2), "windows key apart");
            });

            Case("PitCoverLook_production_wiring", () =>
            {
                string cover = Src("Pits", "Building_PitCover.cs");
                string print = Between(cover, "public override void Print(SectionLayer layer)", "public void Spring(");
                int artAt = print.IndexOf("RM_PitCoverUtility.LidShowsArt(map, Position)", StringComparison.Ordinal);
                int groundAt = print.IndexOf("RM_PitCoverUtility.SurfaceAround(map, Position)", StringComparison.Ordinal);
                Assert(artAt >= 0 && groundAt > artAt, "Print asks LidShowsArt before falling back to the ground print");
                Assert(print.Contains("Graphic.Print(layer, this, 0f)") && print.Contains("PrintedArt = art;"),
                    "the art branch prints the def's graphic and records it for the occluder");
                Assert(print.Contains("PrintedArt = null;"), "can-fail: the ground branch clears the recorded art");
                string shows = Between(cover, "public static bool LidShowsArt(", "public static void DirtyNeighbourLids(");
                Assert(shows.Contains("RM_SuspensionUnderpass.SeenDepthAt(map, eng, n)") && shows.Contains("RM_PitCoverLookMath.ShowsArt(seen)")
                    && shows.Contains("GenAdj.AdjacentCells[i]"), "LidShowsArt reads the shown depth of all 8 neighbours through the pure rule");

                string deck = Src("Pits", "Building_SpanDeck.cs");
                Assert(Between(deck, "public override void SpawnSetup(", "public override void DeSpawn(").Contains("RM_PitCoverUtility.DirtyNeighbourLids(map, Position)"),
                    "a lid or deck laid re-prints the lids round it");
                Assert(Between(deck, "public override void DeSpawn(", "/// <summary>").Contains("RM_PitCoverUtility.DirtyNeighbourLids(map, pos)"),
                    "a lid or deck lifted re-prints the lids round it");

                string exc = Src("RM_MapComponent_Excavation.cs");
                Assert(exc.Contains("Pits.RM_PitCoverLookMath.FlipsNeighbourLids(before, d)") && exc.Contains("Pits.RM_PitCoverLookMath.FlipsNeighbourLids(d, newD)"),
                    "digging and filling re-print the lids round the square");

                string lip = Src("Superdeep", "RM_PitLipOcclusion.cs");
                string band = Between(lip, "private void DrawBand(", "RecordPiece(p, sideOf >= 0 ? 'S' : 'N'");
                Assert(band.Contains("lid?.PrintedArt != null ? RM_FaceMaterial.OccluderMat(lid.PrintedArt)")
                    && band.Contains("ArtPieceMesh(cx, cz, pl, pr, a, b)"), "the occluder draws the matching window of a lid's art");
                Assert(band.Contains("t = map.terrainGrid.TerrainAt(g);"), "under the art it draws the pit floor the lattice gaps show");
                Assert(Between(lip, "private static Mesh ArtPieceMesh(", "private static Mesh Quad(").Contains("RM_PitCoverLookMath.PieceUv("),
                    "the art window comes from the pure PieceUv");
            });
        }
    }
}
