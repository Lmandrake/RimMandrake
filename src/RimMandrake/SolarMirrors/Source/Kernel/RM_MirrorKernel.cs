// Verse-free kernel of the solar mirrors (SOLAR_MIRRORS_MOD_DESIGN_1 §2.2-§2.7): the sun / mirror maths, the beam walk, the
// whole light pass (collectors -> shots -> relays, acyclic, depth-capped) over an abstract grid, change hashing, receiver
// hysteresis and the blinding gain. RM_MirrorMath (Vector3 facade) and RM_MapComponent_MirrorLight call this; the fuzz in
// SelfTest/ compiles this file alone: no Verse, RimWorld or UnityEngine. Axes: x east, y up, z north.
using System;
using System.Collections.Generic;

namespace RimMandrake.SolarMirrors
{
    /// <summary>A beam-walk visitor: true at the first cell that stops the beam. A struct passed by ref, so a walk allocates nothing.</summary>
    public interface IRM_LineVisitor
    {
        bool Blocked(int x, int z);
    }

    public struct RM_Vec
    {
        public float X, Y, Z;
        public RM_Vec(float x, float y, float z) { X = x; Y = y; Z = z; }
        public static RM_Vec Up { get { return new RM_Vec(0f, 1f, 0f); } }
        public static RM_Vec Zero { get { return new RM_Vec(0f, 0f, 0f); } }
        public bool IsZero { get { return X == 0f && Y == 0f && Z == 0f; } }
        public float SqrMagnitude { get { return X * X + Y * Y + Z * Z; } }
        public static float Dot(RM_Vec a, RM_Vec b) { return a.X * b.X + a.Y * b.Y + a.Z * b.Z; }
        public static RM_Vec operator +(RM_Vec a, RM_Vec b) { return new RM_Vec(a.X + b.X, a.Y + b.Y, a.Z + b.Z); }
        public static RM_Vec operator -(RM_Vec a, RM_Vec b) { return new RM_Vec(a.X - b.X, a.Y - b.Y, a.Z - b.Z); }
        public static RM_Vec operator *(float k, RM_Vec a) { return new RM_Vec(k * a.X, k * a.Y, k * a.Z); }
        // Unity's Vector3.normalized: a vector shorter than 1e-5 normalises to zero.
        public RM_Vec Normalized
        {
            get
            {
                float m = (float)Math.Sqrt(SqrMagnitude);
                return m > 1E-05f ? new RM_Vec(X / m, Y / m, Z / m) : Zero;
            }
        }
    }

    /// <summary>One mirror as the light pass sees it (built from the comp each pass).</summary>
    public struct RM_MirrorSpec
    {
        public float faceX, faceZ;                // the face centre, map space; its height is FaceHeight
        public int posX, posZ;                    // parent.Position: the beam walk starts here
        public int minX, minZ, maxX, maxZ;        // the OccupiedRect, inclusive
        public int footprintCells;                // def.size.x * def.size.z
        public float reflectivity;                // already multiplied and clamped (RM_MirrorKernel.Reflectivity)
        public int spotSize;
        public float maxRange;
        public bool spawned, hasAim, holdsTarget, targetValid, tracking;
        public int targetX, targetZ;
        public RM_Vec savedNormal;
        public float source;                      // mirror-free sun fraction at the footprint, 0..1 (daylight is applied here)
    }

    /// <summary>What a pass did to one mirror (written back to the comp's last* fields).</summary>
    public struct RM_MirrorResult
    {
        public bool fired, relayed;
        public float source, delivered, efficiency;
        public float input;                       // the light that arrived at the shot (sun share or relay share)
        public string blocker;
        public bool hasSpot;
        public int spotX, spotZ;
        public RM_Vec inDir;
        public bool commitNormal;                 // a tracking mirror re-aimed: write normal back
        public RM_Vec normal;
        public int depth;                         // 0 = fed by the sun, n = n relays deep
        public int litCount;
        public bool ranFire;                      // diagnostic: the mirror took a shot at all
    }

    public struct RM_BeamOut
    {
        public float fromX, fromZ, toX, toZ, intensity;
    }

    /// <summary>The map as the pass needs it. Its cell queries are asked only for cells OUTSIDE the firing mirror's own footprint.</summary>
    public interface IRM_BeamWorld
    {
        int Width { get; }
        int Height { get; }
        /// <summary>A roof over (x,z). It stops a beam unless the beam already passed a glazed aperture (design §5 E2).</summary>
        bool Roofed(int x, int z);
        /// <summary>A glazed aperture on (x,z): it never stops a beam, and past it roofs no longer do (the beam is inside the room).</summary>
        bool IsAperture(int x, int z);
        /// <summary>Why a beam through (x,z) stops for anything but a roof (closed door, wall-like edifice), or null.</summary>
        string CellBlocks(int x, int z, int mirrorIndex);
        /// <summary>Index into the spec array of the mirror whose edifice stands on the cell, or -1.</summary>
        int MirrorAt(int x, int z);
        string BlockerEdge { get; }
        string BlockerSky { get; }
        string BlockerRoof { get; }
    }

    public static class RM_MirrorKernel
    {
        public const float FaceHeight = 1.5f;
        public const float MinUseful = 0.02f;
        public const float Deg2Rad = 0.0174532924f;

        public static float Clamp(float v, float lo, float hi) { return v < lo ? lo : v > hi ? hi : v; }

        // ── sun and mirror maths ────────────────────────────────────────

        public static RM_Vec SunVector(float shadowDirX, float shadowDirZ, float elevationDeg)
        {
            float e = Clamp(elevationDeg, 0f, 90f) * Deg2Rad;
            float ax = -shadowDirX;
            float az = -shadowDirZ;
            float len = (float)Math.Sqrt(ax * ax + az * az);
            if (len < 1e-5f)
            {
                return RM_Vec.Up;
            }
            float c = (float)Math.Cos(e);
            return new RM_Vec(ax / len * c, (float)Math.Sin(e), az / len * c).Normalized;
        }

        public static bool MovingSun(float dayPercent, float latitudeDeg, out RM_Vec sun)
        {
            sun = RM_Vec.Up;
            float h = (dayPercent - 0.5f) * 2f * (float)Math.PI;
            float ch = (float)Math.Cos(h);
            if (ch <= 0f)
            {
                return false;
            }
            float peak = 90f - Math.Min(89f, Math.Abs(latitudeDeg));
            float elev = peak * ch;
            float eq = latitudeDeg > 0f ? -1f : latitudeDeg < 0f ? 1f : 0f;
            float ax = -(float)Math.Sin(h);
            float az = eq * ch;
            float len = (float)Math.Sqrt(ax * ax + az * az);
            if (len < 1e-5f)
            {
                return true;
            }
            float e = elev * Deg2Rad;
            sun = new RM_Vec(ax / len * (float)Math.Cos(e), (float)Math.Sin(e), az / len * (float)Math.Cos(e)).Normalized;
            return true;
        }

        public static RM_Vec Normal(RM_Vec inDir, RM_Vec outDir)
        {
            RM_Vec n = inDir + outDir;
            return n.SqrMagnitude < 1e-8f ? inDir : n.Normalized;
        }

        public static float Efficiency(RM_Vec inDir, RM_Vec outDir)
        {
            return (float)Math.Sqrt(Math.Max(0f, (1f + RM_Vec.Dot(inDir, outDir)) * 0.5f));
        }

        public static float Cosine(RM_Vec normal, RM_Vec inDir) { return Math.Max(0f, RM_Vec.Dot(normal, inDir)); }

        public static RM_Vec Reflect(RM_Vec inDir, RM_Vec normal)
        {
            return (2f * RM_Vec.Dot(normal, inDir)) * normal - inDir;
        }

        public static bool GroundHit(float faceX, float faceY, float faceZ, RM_Vec dir, float maxRange, out float x, out float z)
        {
            x = faceX;
            z = faceZ;
            if (dir.Y > -0.01f)
            {
                return false;
            }
            float k = faceY / -dir.Y;
            float dx = dir.X * k;
            float dz = dir.Z * k;
            if (dx * dx + dz * dz > maxRange * maxRange)
            {
                return false;
            }
            x = faceX + dx;
            z = faceZ + dz;
            return true;
        }

        /// <summary>The 4-connected walk from (x0,z0) to (x1,z1): the visitor sees the cells strictly between. False at the first blocked one.</summary>
        public static bool LineClear<T>(int x0, int z0, int x1, int z1, ref T visitor) where T : struct, IRM_LineVisitor
        {
            int dx = Math.Abs(x1 - x0);
            int dz = Math.Abs(z1 - z0);
            int x = x0;
            int z = z0;
            int n = 1 + dx + dz;
            int xInc = x1 > x0 ? 1 : -1;
            int zInc = z1 > z0 ? 1 : -1;
            bool sideOnEqual = x0 != x1 ? x0 < x1 : z0 < z1;
            int error = dx - dz;
            dx *= 2;
            dz *= 2;
            bool first = true;
            while (n > 1)
            {
                if (!first && visitor.Blocked(x, z))
                {
                    return false;
                }
                first = false;
                if (error > 0 || (error == 0 && sideOnEqual))
                {
                    x += xInc;
                    error -= dz;
                }
                else
                {
                    z += zInc;
                    error += dx;
                }
                n--;
            }
            return true;
        }

        public static int Quantise(float v, float step = 0.05f) { return (int)Math.Round(v / step); }

        public static bool Hysteresis(bool wasLit, float light, float onAt, float offAt)
        {
            return wasLit ? light >= offAt : light >= onAt;
        }

        // ── settings-shaped helpers ─────────────────────────────────────

        public static float Reflectivity(float baseValue, bool stuffRowFound, float stuffValue, float multiplier)
        {
            float r = stuffRowFound ? stuffValue : baseValue;
            return Clamp(r * multiplier, 0f, 1f);
        }

        public static int PassInterval(int setting) { return setting < 125 ? 125 : setting > 1000 ? 1000 : setting; }
        public static int DepthCap(int setting) { return setting < 1 ? 1 : setting > 6 ? 6 : setting; }

        /// <summary>0 at night (glow &lt;= 0.1), full from 0.6.</summary>
        public static float Daylight(float celestialGlow) { return Clamp((celestialGlow - 0.1f) / 0.5f, 0f, 1f); }

        /// <summary>Severity a hostile standing in light l gains over one pass interval; 0 below the 0.5 threshold.</summary>
        public static float BlindGain(float l, float severityPerDay, int interval)
        {
            if (l < 0.5f) return 0f;
            return severityPerDay * Math.Min(1f, l) * interval / 60000f;
        }

        // ── dust, concentration, room heat, dazzle (SOLAR_MIRRORS_BUILD_1) ──

        /// <summary>Design §3.2: dust after `ticks` more ticks. A dust storm adds perDay per day; nothing else removes it
        /// (cleaning resets it to 0). Clamped to 0..1.</summary>
        public static float DustAfter(float dust, bool storm, float perDay, int ticks)
        {
            float d = Clamp(dust, 0f, 1f);
            if (!storm || perDay <= 0f || ticks <= 0)
            {
                return d;
            }
            return Clamp(d + perDay * ticks / 60000f, 0f, 1f);
        }

        /// <summary>The share of a mirror's reflectivity left under this much dust: 1 - dust x maxLoss, in 0..1.</summary>
        public static float DustFactor(float dust, float maxLoss)
        {
            return Clamp(1f - Clamp(dust, 0f, 1f) * Clamp(maxLoss, 0f, 1f), 0f, 1f);
        }

        /// <summary>Design §2.6 / §3.3: the felt-temperature degrees concentrated light (above 1) adds on top of what
        /// plain sun already gave (`appliedC`). Vanilla heat only: the total never exceeds the biome's maxOffsetC, and
        /// light above `cap` adds nothing more. perUnitC = the biome's offset x the sun-heat strength x body-size factor.</summary>
        public static float ConcentrationExtraC(float light, float perUnitC, float maxOffsetC, float appliedC, float cap)
        {
            if (light <= 1f || perUnitC <= 0f || maxOffsetC <= 0f)
            {
                return 0f;
            }
            float total = Math.Min(light, Math.Max(1f, cap)) * perUnitC;
            if (total > maxOffsetC)
            {
                total = maxOffsetC;
            }
            float extra = total - Math.Max(0f, appliedC);
            return extra > 0f ? extra : 0f;
        }

        /// <summary>Design §2.6 / §5 E2: heat energy one lit, enclosed cell pushes into its room over one pass interval
        /// (GenTemperature.PushHeat units; vanilla pushers give heatPerSecond x seconds). 0 for no light.</summary>
        public static float RoomHeat(float light, float perLightPerSecond, int intervalTicks)
        {
            if (light <= 0f || perLightPerSecond <= 0f || intervalTicks <= 0)
            {
                return 0f;
            }
            return light * perLightPerSecond * intervalTicks / 60f;
        }

        /// <summary>Design §5 E4: the shooting-accuracy factor for a pawn standing in light l. 1 below 0.5; down to
        /// 1 - maxPenalty in full light; never below 0.</summary>
        public static float DazzleFactor(float l, float maxPenalty)
        {
            if (l < 0.5f || maxPenalty <= 0f)
            {
                return 1f;
            }
            return Clamp(1f - Clamp(maxPenalty, 0f, 1f) * Math.Min(1f, l), 0f, 1f);
        }

        /// <summary>Design §5 E3: the heliograph's reach in world tiles: the setting x daylight; 0 at night.</summary>
        public static float HeliographRange(float rangeTiles, float daylight)
        {
            return Math.Max(0f, rangeTiles) * Clamp(daylight, 0f, 1f);
        }

        public static RM_Vec DirTo(RM_MirrorSpec m, int cellX, int cellZ)
        {
            return (new RM_Vec(cellX + 0.5f, 0f, cellZ + 0.5f) - new RM_Vec(m.faceX, FaceHeight, m.faceZ)).Normalized;
        }

        /// <summary>The normal to use for light arriving from inDir: a mirror that holds its target re-aims (a tracking one commits it).</summary>
        public static RM_Vec NormalFor(RM_MirrorSpec m, RM_Vec inDir, out bool commit)
        {
            commit = false;
            if (m.holdsTarget && m.targetValid)
            {
                RM_Vec n = Normal(inDir, DirTo(m, m.targetX, m.targetZ));
                commit = m.tracking;
                return n;
            }
            return m.savedNormal;
        }

        public static void SpotRange(int spotSize, out int size, out int lo)
        {
            size = Math.Max(1, spotSize);
            lo = -(size - 1) / 2;
        }

        // ── beam blocking ───────────────────────────────────────────────

        /// <summary>One cell of the beam's way (design §2.2 + §5 E2): an aperture passes and lets the beam under roofs from
        /// then on; a roof stops it unless it is already inside; then the world's own blockers. Null when the cell is clear.</summary>
        public static string CellStops(IRM_BeamWorld w, int x, int z, int index, ref bool inside)
        {
            if (w.IsAperture(x, z))
            {
                inside = true;
                return null;
            }
            if (!inside && w.Roofed(x, z))
            {
                return w.BlockerRoof;
            }
            return w.CellBlocks(x, z, index);
        }

        private struct BeamWalk : IRM_LineVisitor
        {
            public IRM_BeamWorld world;
            public RM_MirrorSpec own;
            public int index;
            public string why;
            public bool inside;

            public bool Blocked(int x, int z)
            {
                if (x >= own.minX && x <= own.maxX && z >= own.minZ && z <= own.maxZ)
                {
                    return false;
                }
                why = CellStops(world, x, z, index, ref inside);
                return why != null;
            }
        }

        /// <summary>Why a beam from this mirror to this cell is stopped, or null when it is clear.</summary>
        public static string FirstBlocker(IRM_BeamWorld w, RM_MirrorSpec m, int index, int x, int z)
        {
            if (x < 0 || z < 0 || x >= w.Width || z >= w.Height)
            {
                return w.BlockerEdge;
            }
            BeamWalk walk = new BeamWalk { world = w, own = m, index = index };
            if (!LineClear(m.posX, m.posZ, x, z, ref walk))
            {
                return walk.why;
            }
            bool inOwn = x >= m.minX && x <= m.maxX && z >= m.minZ && z <= m.maxZ;
            if (!inOwn)
            {
                bool inside = walk.inside;
                return CellStops(w, x, z, index, ref inside);
            }
            return null;
        }

        // ── the pass ────────────────────────────────────────────────────

        private struct Shot
        {
            public int mirror;
            public RM_Vec inDir;
            public float input;
            public bool relayed;
            public int depth;
        }

        public sealed class Pass
        {
            public float[] Light;
            public readonly List<int> LitCells = new List<int>();
            public readonly List<int> PrevLitCells = new List<int>();
            public readonly List<RM_BeamOut> Beams = new List<RM_BeamOut>();

            private readonly List<Shot> queue = new List<Shot>();
            private readonly List<Shot> next = new List<Shot>();
            private bool[] fired = new bool[0];
            private float[] relayIn = new float[0];
            private RM_Vec[] relayDir = new RM_Vec[0];
            private bool[] relaySeen = new bool[0];
            private readonly List<int> relayOrder = new List<int>();

            /// <summary>Run one pass. results is filled for every mirror (count entries). Returns nothing; read Light / LitCells / Beams.</summary>
            public void Run(IRM_BeamWorld w, RM_MirrorSpec[] mirrors, int count, RM_MirrorResult[] results, bool anyEffect, bool sunUp,
                RM_Vec sun, float daylight, int maxChain)
            {
                int n = w.Width * w.Height;
                if (Light == null || Light.Length != n)
                {
                    Light = new float[n];
                    LitCells.Clear();
                }
                PrevLitCells.Clear();
                PrevLitCells.AddRange(LitCells);
                for (int k = 0; k < LitCells.Count; k++)
                {
                    Light[LitCells[k]] = 0f;
                }
                LitCells.Clear();
                Beams.Clear();
                queue.Clear();
                if (fired.Length < count)
                {
                    fired = new bool[count];
                    relayIn = new float[count];
                    relayDir = new RM_Vec[count];
                    relaySeen = new bool[count];
                }
                for (int k = 0; k < count; k++) fired[k] = false;

                for (int k = 0; k < count; k++)
                {
                    RM_MirrorSpec m = mirrors[k];
                    results[k] = new RM_MirrorResult { inDir = RM_Vec.Zero, normal = RM_Vec.Zero };
                    if (!anyEffect || !sunUp || !m.spawned || !m.hasAim && !(m.holdsTarget && m.targetValid))
                    {
                        continue;
                    }
                    float src = m.source * daylight;
                    results[k].source = src;
                    if (src > MinUseful)
                    {
                        queue.Add(new Shot { mirror = k, inDir = sun, input = src, depth = 0 });
                    }
                }

                int depthCap = DepthCap(maxChain);
                for (int depth = 0; depth < depthCap && queue.Count > 0; depth++)
                {
                    next.Clear();
                    relayOrder.Clear();
                    for (int q = 0; q < queue.Count; q++)
                    {
                        Fire(w, mirrors, count, results, queue[q]);
                    }
                    for (int o = 0; o < relayOrder.Count; o++)
                    {
                        int mi = relayOrder[o];
                        if (!fired[mi] && relayIn[mi] > MinUseful)
                        {
                            next.Add(new Shot { mirror = mi, inDir = relayDir[mi], input = relayIn[mi], relayed = true, depth = depth + 1 });
                        }
                        relaySeen[mi] = false;
                        relayIn[mi] = 0f;
                    }
                    queue.Clear();
                    queue.AddRange(next);
                }
                queue.Clear();
                next.Clear();
            }

            private void Fire(IRM_BeamWorld w, RM_MirrorSpec[] mirrors, int count, RM_MirrorResult[] results, Shot shot)
            {
                int mi = shot.mirror;
                if (fired[mi])
                {
                    return; // acyclic: a mirror fires once per pass
                }
                fired[mi] = true;
                RM_MirrorSpec m = mirrors[mi];
                results[mi].ranFire = true;
                results[mi].inDir = shot.inDir;
                results[mi].depth = shot.depth;
                results[mi].input = shot.input;
                bool commit;
                RM_Vec nrm = NormalFor(m, shot.inDir, out commit);
                results[mi].commitNormal = commit;
                results[mi].normal = nrm;
                if (nrm.IsZero)
                {
                    return;
                }
                float cos = Cosine(nrm, shot.inDir);
                float output = shot.input * m.reflectivity * cos;
                results[mi].efficiency = cos;
                if (output <= MinUseful)
                {
                    return;
                }
                int cx, cz;
                RM_Vec face = new RM_Vec(m.faceX, FaceHeight, m.faceZ);
                if (m.holdsTarget && m.targetValid)
                {
                    cx = m.targetX;
                    cz = m.targetZ;
                }
                else
                {
                    RM_Vec outDir = Reflect(shot.inDir, nrm);
                    float hx, hz;
                    if (!GroundHit(face.X, face.Y, face.Z, outDir, m.maxRange, out hx, out hz))
                    {
                        results[mi].blocker = w.BlockerSky;
                        return;
                    }
                    cx = (int)Math.Floor(hx);
                    cz = (int)Math.Floor(hz);
                }
                if (cx < 0 || cz < 0 || cx >= w.Width || cz >= w.Height)
                {
                    results[mi].blocker = w.BlockerEdge;
                    return;
                }
                int size, lo;
                SpotRange(m.spotSize, out size, out lo);
                int lit = 0;
                for (int dx = 0; dx < size; dx++)
                {
                    for (int dz = 0; dz < size; dz++)
                    {
                        int x = cx + lo + dx;
                        int z = cz + lo + dz;
                        if (x < 0 || z < 0 || x >= w.Width || z >= w.Height)
                        {
                            continue;
                        }
                        string why = FirstBlocker(w, m, mi, x, z);
                        if (why != null)
                        {
                            if (results[mi].blocker == null) results[mi].blocker = why;
                            continue;
                        }
                        AddLight(w, x, z, output);
                        lit++;
                        int oi = w.MirrorAt(x, z);
                        if (oi >= 0 && oi != mi && !fired[oi])
                        {
                            float share = output / Math.Max(1, mirrors[oi].footprintCells);
                            if (!relaySeen[oi])
                            {
                                relaySeen[oi] = true;
                                relayOrder.Add(oi);
                            }
                            relayIn[oi] += share;
                            relayDir[oi] = (face - new RM_Vec(mirrors[oi].faceX, FaceHeight, mirrors[oi].faceZ)).Normalized;
                        }
                    }
                }
                if (lit == 0)
                {
                    return;
                }
                results[mi].fired = true;
                results[mi].relayed = shot.relayed;
                results[mi].delivered = output;
                results[mi].hasSpot = true;
                results[mi].spotX = cx;
                results[mi].spotZ = cz;
                results[mi].litCount = lit;
                Beams.Add(new RM_BeamOut { fromX = face.X, fromZ = face.Z, toX = cx + 0.5f, toZ = cz + 0.5f, intensity = output });
            }

            private void AddLight(IRM_BeamWorld w, int x, int z, float v)
            {
                int i = z * w.Width + x;
                if (Light[i] <= 0f)
                {
                    LitCells.Add(i);
                }
                Light[i] += v;
            }

            /// <summary>Change detection on quantised light (design §2.7), never on raw floats.</summary>
            public int ChangeHash()
            {
                int hash = 17;
                for (int k = 0; k < LitCells.Count; k++)
                {
                    int i = LitCells[k];
                    hash = unchecked(hash * 31 + i * 7 + Quantise(Light[i]));
                }
                return unchecked(hash * 31 + LitCells.Count);
            }
        }
    }
}
