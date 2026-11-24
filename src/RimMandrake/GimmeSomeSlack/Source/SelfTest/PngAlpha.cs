// A minimal PNG reader for the offline checks that judge where a picture's pixels stand (8-bit RGBA, not interlaced: every picture the mod ships here).
// Anything else throws by name: an unread picture is never read as an empty one.
using System;
using System.IO;
using System.IO.Compression;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal sealed class PngAlpha
    {
        public int W, H;
        private byte[] px;   // RGBA rows, top first
        public byte A(int x, int y) => px[(y * W + x) * 4 + 3];
        public int Lum(int x, int y) { int i = (y * W + x) * 4; return (px[i] + px[i + 1] + px[i + 2]) / 3; }

        public static PngAlpha Read(string path)
        {
            byte[] f = File.ReadAllBytes(path);
            if (f.Length < 33 || f[0] != 0x89 || f[1] != 'P') throw new InvalidDataException(path + ": not a PNG");
            int U32(int i) => f[i] << 24 | f[i + 1] << 16 | f[i + 2] << 8 | f[i + 3];
            var p = new PngAlpha();
            var idat = new MemoryStream();
            for (int i = 8; i + 8 <= f.Length;)
            {
                int len = U32(i);
                string t = System.Text.Encoding.ASCII.GetString(f, i + 4, 4);
                if (t == "IHDR")
                {
                    p.W = U32(i + 8); p.H = U32(i + 12);
                    if (f[i + 16] != 8 || f[i + 17] != 6 || f[i + 20] != 0) throw new InvalidDataException(path + ": not an 8-bit RGBA PNG without interlace (depth " + f[i + 16] + ", colour type " + f[i + 17] + ")");
                }
                else if (t == "IDAT") idat.Write(f, i + 8, len);
                i += 12 + len;
            }
            idat.Position = 0;
            var raw = new MemoryStream();
            using (var z = new ZLibStream(idat, CompressionMode.Decompress)) z.CopyTo(raw);
            byte[] r = raw.ToArray();
            int st = p.W * 4;
            p.px = new byte[st * p.H];
            for (int y = 0; y < p.H; y++)
            {
                int src = y * (st + 1), ft = r[src];
                for (int x = 0; x < st; x++)
                {
                    int a = x >= 4 ? p.px[y * st + x - 4] : 0, b = y > 0 ? p.px[(y - 1) * st + x] : 0, c = x >= 4 && y > 0 ? p.px[(y - 1) * st + x - 4] : 0, add;
                    switch (ft)
                    {
                        case 0: add = 0; break;
                        case 1: add = a; break;
                        case 2: add = b; break;
                        case 3: add = (a + b) / 2; break;
                        case 4:
                            int q = a + b - c, pa = Math.Abs(q - a), pb = Math.Abs(q - b), pc = Math.Abs(q - c);
                            add = pa <= pb && pa <= pc ? a : pb <= pc ? b : c; break;
                        default: throw new InvalidDataException(path + ": filter " + ft);
                    }
                    p.px[y * st + x] = (byte)(r[src + 1 + x] + add);
                }
            }
            return p;
        }
    }
}
