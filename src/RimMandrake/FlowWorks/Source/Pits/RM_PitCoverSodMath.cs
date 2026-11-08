namespace RimMandrake.FlowWorks.Pits
{
    /// <summary>
    /// PIT_COVER_SOD (bar pit_covered_invisible: "the same patch of ground looks the same at play zoom in the BEFORE frame
    /// (undug) and the AFTER frame (a covered superdeep excavation)"). A lid that prints ground printed only the terrain, so in
    /// a grassy field it read as a bare square among the grass plants drawn over the terrain round it. The lid now also prints
    /// "sod": the low wild plant its surroundings carry, laid out the way vanilla Plant.Print lays a plant's meshes out.
    /// This is the pure part (which plant, how many meshes, where in the square); RM_PitCoverSod does the Verse reads and the
    /// printing. No Verse or Unity types: linked into the SelfTest project.
    /// </summary>
    public static class RM_PitCoverSodMath
    {
        /// <summary>A plant taller than this is a bush or a shrub, not sod: a lid does not grow one.</summary>
        public const float MaxVisualSize = 1.2f;

        /// <summary>Ground samples wanted before the census stops widening (one full ring of 8).</summary>
        public const int WantSamples = 8;

        /// <summary>The widest ring sampled (as RM_PitCoverUtility.SurfaceAround): a lid deep inside a wide deck still finds ground.</summary>
        public const int MaxRing = 4;

        /// <summary>Of 8 ground samples at least 3 must carry a low wild plant (scaled for other sample counts), else the lid
        /// stays bare: bare ground round it reads as bare, and a lone tuft beside it does not grow a lawn on the lid.</summary>
        public const int CarriersPerEight = 3;

        /// <summary>Offsets (dx, dz) of the square ring at Chebyshev distance <paramref name="r"/> round a cell, in a fixed order
        /// (south row west to east, then the sides south to north, then the north row), so ties break the same way every print.</summary>
        public static int[] RingOffsets(int r)
        {
            if (r <= 0)
            {
                return new int[0];
            }
            int[] o = new int[8 * r * 2];
            int k = 0;
            for (int x = -r; x <= r; x++)
            {
                o[k++] = x;
                o[k++] = -r;
            }
            for (int z = -r + 1; z <= r - 1; z++)
            {
                o[k++] = -r;
                o[k++] = z;
                o[k++] = r;
                o[k++] = z;
            }
            for (int x = -r; x <= r; x++)
            {
                o[k++] = x;
                o[k++] = r;
            }
            return o;
        }

        /// <summary>Do <paramref name="carriers"/> of <paramref name="samples"/> ground squares carry enough sod for the lid to
        /// carry it too? 3 of 8, the same share of any other count; no samples, no sod.</summary>
        public static bool Enough(int carriers, int samples)
        {
            return samples > 0 && carriers > 0 && carriers * WantSamples >= CarriersPerEight * samples;
        }

        /// <summary>The commonest key among <paramref name="keys"/> (a key per ground sample; -1 = carries no sod), ties to the
        /// one seen first; -1 when no sample carries one. <paramref name="count"/>: how many samples carry the winner.</summary>
        public static int Commonest(int[] keys, int n, out int count)
        {
            count = 0;
            int best = -1;
            if (keys == null)
            {
                return best;
            }
            n = n < keys.Length ? n : keys.Length;
            for (int i = 0; i < n; i++)
            {
                int key = keys[i];
                if (key < 0)
                {
                    continue;
                }
                bool seen = false;
                for (int j = 0; j < i && !seen; j++)
                {
                    seen = keys[j] == key;
                }
                if (seen)
                {
                    continue;
                }
                int c = 0;
                for (int j = i; j < n; j++)
                {
                    if (keys[j] == key)
                    {
                        c++;
                    }
                }
                if (c > count)
                {
                    best = key;
                    count = c;
                }
            }
            return best;
        }

        /// <summary>Vanilla Plant.Print's mesh count: ceil(growth x maxMeshCount), at least 1.</summary>
        public static int MeshCount(float growth, int maxMeshCount)
        {
            if (maxMeshCount < 1)
            {
                maxMeshCount = 1;
            }
            if (!(growth > 0f))
            {
                return 1;
            }
            if (growth > 1f)
            {
                growth = 1f;
            }
            int m = (int)System.Math.Ceiling(growth * maxMeshCount);
            return m < 1 ? 1 : (m > maxMeshCount ? maxMeshCount : m);
        }

        /// <summary>Vanilla Plant.Print's grid side for a maxMeshCount (1, 4, 9, 16, 25 give 1..5); anything else is 1, as
        /// vanilla falls back to after logging its "must be a perfect square" error.</summary>
        public static int GridSide(int maxMeshCount)
        {
            switch (maxMeshCount)
            {
                case 4: return 2;
                case 9: return 3;
                case 16: return 4;
                case 25: return 5;
                default: return 1;
            }
        }

        /// <summary>The centre (fractions of the square from its south-west corner) of sub-square <paramref name="index"/> on a
        /// side x side grid: index / side columns east, index % side rows north, as vanilla.</summary>
        public static void SubSquareCentre(int index, int side, out float dx, out float dz)
        {
            if (side < 1)
            {
                side = 1;
            }
            float step = 1f / side;
            dx = 0.5f * step + (index / side) * step;
            dz = 0.5f * step + (index % side) * step;
        }

        /// <summary>Vanilla's horizontal jitter of one sub-square mesh: 0.3 of a sub-square.</summary>
        public static float JitterMax(int side)
        {
            return (side < 1 ? 1f : 1f / side) * 0.3f;
        }

        /// <summary>The order the meshes fill the sub-squares in, as vanilla PlantPosIndices builds it: a list of
        /// <paramref name="maxMeshCount"/> slots holding 0..n-2 and a second 0 (vanilla fills k &lt; i of i + 1 slots, so the
        /// last sub-square is never drawn and the first may be drawn twice), shuffled. Vanilla shuffles 8 lists once at
        /// start-up with the live Rand and picks one by the plant's id; a lid has no plant id, so its list is shuffled here
        /// from <paramref name="seed"/> (the lid's position), deterministic across reloads. Kept quirk for quirk: the lid's
        /// tufts then sit the way every vanilla tuft round it sits.</summary>
        public static int[] PositionOrder(int maxMeshCount, int seed)
        {
            int n = maxMeshCount < 1 ? 1 : (maxMeshCount > 25 ? 25 : maxMeshCount);
            int[] a = new int[n];
            for (int k = 0; k < n - 1; k++)
            {
                a[k] = k;
            }
            uint s = (uint)seed ^ 0x9E3779B9u;
            for (int i = n - 1; i > 0; i--)
            {
                s = Mix(s + (uint)i);
                int j = (int)(s % (uint)(i + 1));
                int t = a[i];
                a[i] = a[j];
                a[j] = t;
            }
            return a;
        }

        /// <summary>Vanilla's single-mesh plant never hangs below its square: a centre whose foot (z - size / 2) falls south of
        /// the square's south edge is lifted to sit on it. <paramref name="lifted"/>: it was (the shadow then follows the square).</summary>
        public static float ClampSingleZ(float z, float squareSouthZ, float sizeFactor, out bool lifted)
        {
            lifted = z - sizeFactor / 2f < squareSouthZ;
            return lifted ? squareSouthZ + sizeFactor / 2f : z;
        }

        private static uint Mix(uint x)
        {
            x ^= x >> 16;
            x *= 0x7FEB352Du;
            x ^= x >> 15;
            x *= 0x846CA68Bu;
            x ^= x >> 16;
            return x;
        }
    }
}
