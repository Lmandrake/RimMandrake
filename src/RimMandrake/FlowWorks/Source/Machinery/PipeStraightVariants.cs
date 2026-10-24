namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW (owner 2026-10-23: a long Scrapper run "repeats the same green spot every
    /// cell"): which straight-run tile a pipe cell draws. A look may ship, beside its linked atlas
    /// (<c>.../UniversalPipe_Atlas</c>), a sheet <c>.../UniversalPipe_Straights</c> of <see cref="Count"/> alternative straight
    /// tiles: column k-1 holds variant k, row 0 the east-west tile, row 1 the north-south tile, each laid out like an atlas tile
    /// (the shown 3/4 inside 1/8 of padding). Every variant's ends equal the atlas straight's, so any mix joins pixel-continuously
    /// (art_source/pipe/compose_scrapper_v3.py). The pick is a pure function of the cell, so it is the same every redraw, every
    /// load and on every machine, and needs nothing saved. Verse-free: the SelfTest console compiles this file.</summary>
    public static class PipeStraightVariants
    {
        /// <summary>Sheet columns (variants besides the atlas's own straight).</summary>
        public const int Count = 4;

        /// <summary>Hash bucket (low 3 bits) to tile: 0 = the atlas's own straight (3 of 8 cells), 1 and 2 = plain stretches
        /// (3 of 8), 3 and 4 = repair hardware (2 of 8: a wire wrap, a patch plate), so hardware stays occasional.</summary>
        private static readonly int[] Bucket = { 0, 0, 0, 1, 1, 2, 3, 4 };

        /// <summary>A stable 32-bit mix of a cell (two odd multipliers, then a murmur-style finaliser).</summary>
        public static uint CellHash(int x, int z)
        {
            unchecked
            {
                uint h = (uint)x * 0x8DA6B343u;
                h ^= (uint)z * 0xD8163841u;
                h ^= h >> 13;
                h *= 0x85EBCA6Bu;
                h ^= h >> 16;
                return h;
            }
        }

        /// <summary>0 = draw the atlas straight as vanilla does; 1..<see cref="Count"/> = sheet column k-1.</summary>
        public static int Pick(int x, int z) => Bucket[CellHash(x, z) & 7u];

        /// <summary>Graphic_Linked's link mask (N1 E2 S4 W8) is a straight run: north-south (5) or east-west (10).</summary>
        public static bool IsStraight(int mask) => mask == 5 || mask == 10;

        /// <summary>The straights sheet beside a look's linked atlas texPath, or null when the path is not a pipe atlas.</summary>
        public static string SheetPathFor(string atlasPath)
        {
            const string atlas = "UniversalPipe_Atlas";
            if (string.IsNullOrEmpty(atlasPath) || !atlasPath.EndsWith(atlas)) return null;
            return atlasPath.Substring(0, atlasPath.Length - atlas.Length) + "UniversalPipe_Straights";
        }

        /// <summary>UVs of variant k's shown cell in the sheet, in Printer_Plane corner order (bottom-left, top-left, top-right,
        /// bottom-right) as u0,v0,u1,v1,...; v = 0 is the image bottom. Independent of the sheet's pixel size.</summary>
        public static void Uvs(int k, bool eastWest, float[] uv)
        {
            float u0 = (k - 1 + 0.125f) / Count, u1 = u0 + 0.75f / Count;
            int row = eastWest ? 0 : 1;                       // row 0 is the top half of the image
            float vTop = 1f - (row + 0.125f) / 2f, vBot = vTop - 0.75f / 2f;
            uv[0] = u0; uv[1] = vBot;
            uv[2] = u0; uv[3] = vTop;
            uv[4] = u1; uv[5] = vTop;
            uv[6] = u1; uv[7] = vBot;
        }
    }
}
