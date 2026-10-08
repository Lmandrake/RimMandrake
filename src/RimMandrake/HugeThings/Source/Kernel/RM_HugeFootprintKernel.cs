// Verse-free kernel of Huge Things' plant footprint: where the engine draws a huge plant, which cells its picture covers
// (the selection rect) and which cells its art touches the ground in at the current growth (the blocked cells).
// SelfTest/HugeThingsFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine. FootprintMath.cs adapts it to Verse
// types; selftest_hugethings_footprint.py mirrors it line for line against the real Rot masks.
//
// THE DRAW TRANSFORM, measured from decompiled 1.6 (RimSage, 2026-10-07), Plant.Print for maxMeshCount 1:
//   Rand.Seed = Position.GetHashCode();  centre = GenThing.TrueCenter = Position + (0.5, 0.5) for a 1x1 thing
//   centre += Gen.RandomHorizontalVector(0.05f)                                  (two Rand.Range draws)
//   visual = plant.visualSizeRange.LerpThroughRange(growth);  side = graphicData.drawSize.x * visual
//   if (centre.z - visual / 2 < Position.z) centre.z = Position.z + visual / 2   (bottom anchoring; uses visual, not side)
//   flipUv = Rand.Bool  (Printer_Plane.DefaultUvsFlipped: a mirror in x)
//   Graphic_Random: sub-graphic = SubGraphicAtIndex(Rand.Range(0, SubGraphicsCount))
//   Printer_Plane.PrintPlane(centre, (side, side)): a square, whatever the texture's aspect.
// Graphic_Random.MatSingleFor (called first in the loop) indexes by thingIDNumber and draws no Rand, so that is the whole
// sequence; CompHugeFootprint.Roll replays it. Graphic_Collection.Init orders sub-textures by name.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    /// <summary>The drawn quad: a square, world coordinates in cells.</summary>
    public struct HugeQuad
    {
        public float MinX, MinZ, Size;

        public float CentreX => MinX + Size * 0.5f;
    }

    /// <summary>An inclusive cell box.</summary>
    public struct CellBox
    {
        public int MinX, MinZ, MaxX, MaxZ;

        public CellBox(int minX, int minZ, int maxX, int maxZ)
        {
            MinX = minX;
            MinZ = minZ;
            MaxX = maxX;
            MaxZ = maxZ;
        }

        public bool Contains(int x, int z) => x >= MinX && x <= MaxX && z >= MinZ && z <= MaxZ;
    }

    /// <summary>A measured picture: its visible-pixel box (u left->right, v bottom->top, 0..1, unflipped) and its
    /// ground-contact cells at full growth (keys of (dx, dz) relative to the root cell, unflipped).</summary>
    public sealed class HugeMask
    {
        public float U0, V0, U1 = 1f, V1 = 1f;
        public float MeasuredSize;
        public readonly HashSet<long> Contact = new HashSet<long>();
    }

    public static class RM_HugeFootprintKernel
    {
        public static long Key(int dx, int dz) => ((long)dx << 32) | (uint)dz;

        public static int KeyX(long k) => (int)(k >> 32);

        public static int KeyZ(long k) => (int)(uint)k;

        /// <summary>Round half up (never Mathf.RoundToInt, which rounds half to even).</summary>
        public static int RoundHalfUp(float v) => (int)Math.Floor(v + 0.5f);

        /// <summary>The quad Plant.Print draws for a plant at (rootX, rootZ) with this visual size.</summary>
        public static HugeQuad Quad(int rootX, int rootZ, float drawSizeX, float visual, float jitterX, float jitterZ)
        {
            float cx = rootX + 0.5f + jitterX;
            float cz = rootZ + 0.5f + jitterZ;
            if (cz - visual / 2f < rootZ) cz = rootZ + visual / 2f;
            float side = drawSizeX * visual;
            return new HugeQuad { MinX = cx - side / 2f, MinZ = cz - side / 2f, Size = side };
        }

        /// <summary>The visible picture in world coordinates (float), mirrored when the engine flips it.</summary>
        public static void PictureBounds(HugeQuad q, HugeMask m, bool flip, out float x0, out float z0, out float x1, out float z1)
        {
            float u0 = flip ? 1f - m.U1 : m.U0;
            float u1 = flip ? 1f - m.U0 : m.U1;
            x0 = q.MinX + u0 * q.Size;
            x1 = q.MinX + u1 * q.Size;
            z0 = q.MinZ + m.V0 * q.Size;
            z1 = q.MinZ + m.V1 * q.Size;
        }

        /// <summary>Every cell the visible picture overlaps. Always at least one cell.</summary>
        public static CellBox PictureBox(HugeQuad q, HugeMask m, bool flip)
        {
            PictureBounds(q, m, flip, out float x0, out float z0, out float x1, out float z1);
            int minX = (int)Math.Floor(x0), minZ = (int)Math.Floor(z0);
            int maxX = Math.Max(minX, (int)Math.Ceiling(x1) - 1), maxZ = Math.Max(minZ, (int)Math.Ceiling(z1) - 1);
            return new CellBox(minX, minZ, maxX, maxZ);
        }

        /// <summary>
        /// The ground-contact cells now. The blocking quad is the drawn quad scaled by blockScale (Mod Settings) about
        /// its bottom-centre; each candidate cell's centre is mapped back to the full-growth, unflipped measurement frame
        /// (root-relative, quad side MeasuredSize, bottom on the root's south edge, centre column on the root's centre)
        /// and kept when it lands in a measured contact cell AND the centre lies inside the drawn picture (so a scaled
        /// footprint never leaves the art). Works for any scale without gaps. The root cell is never returned: an
        /// impassable edifice there would wipe the plant (GenSpawn.SpawningWipes, BlocksPlanting).
        /// </summary>
        public static List<long> ContactCells(int rootX, int rootZ, HugeQuad q, float blockScale, bool flip, HugeMask m)
        {
            List<long> outCells = new List<long>();
            if (m == null || m.Contact.Count == 0 || m.MeasuredSize <= 0f || q.Size <= 0f || blockScale <= 0f) return outCells;
            PictureBounds(q, m, flip, out float px0, out float pz0, out float px1, out float pz1);
            float bs = q.Size * blockScale;
            float left = q.CentreX - bs / 2f, bottom = q.MinZ;
            int x0 = (int)Math.Floor(left), x1 = (int)Math.Ceiling(left + bs);
            int z0 = (int)Math.Floor(bottom), z1 = (int)Math.Ceiling(bottom + bs);
            for (int z = z0; z < z1; z++)
            {
                for (int x = x0; x < x1; x++)
                {
                    if (x == rootX && z == rootZ) continue;
                    float cx = x + 0.5f, cz = z + 0.5f;
                    if (cx < px0 || cx > px1 || cz < pz0 || cz > pz1) continue;
                    float u = (cx - left) / bs, v = (cz - bottom) / bs;
                    if (u < 0f || u > 1f || v < 0f || v > 1f) continue;
                    if (flip) u = 1f - u;
                    int dx = (int)Math.Floor(0.5f + (u - 0.5f) * m.MeasuredSize);
                    int dz = (int)Math.Floor(v * m.MeasuredSize);
                    if (m.Contact.Contains(Key(dx, dz))) outCells.Add(Key(x, z));
                }
            }
            return outCells;
        }

        /// <summary>The selection rect: the picture, every blocked cell and the root cell.</summary>
        public static CellBox SelectBox(int rootX, int rootZ, CellBox picture, List<long> blocked)
        {
            int minX = Math.Min(picture.MinX, rootX), minZ = Math.Min(picture.MinZ, rootZ);
            int maxX = Math.Max(picture.MaxX, rootX), maxZ = Math.Max(picture.MaxZ, rootZ);
            if (blocked != null)
            {
                for (int i = 0; i < blocked.Count; i++)
                {
                    int x = KeyX(blocked[i]), z = KeyZ(blocked[i]);
                    if (x < minX) minX = x;
                    if (z < minZ) minZ = z;
                    if (x > maxX) maxX = x;
                    if (z > maxZ) maxZ = z;
                }
            }
            return new CellBox(minX, minZ, maxX, maxZ);
        }

        /// <summary>Box of w x h centred on a cell (even sizes lean east/north, as GenAdj.OccupiedRect does).</summary>
        public static CellBox CentredBox(int cx, int cz, int w, int h)
        {
            int minX = cx - (w - 1) / 2, minZ = cz - (h - 1) / 2;
            return new CellBox(minX, minZ, minX + w - 1, minZ + h - 1);
        }

        public static CellBox Union(CellBox a, CellBox b)
            => new CellBox(Math.Min(a.MinX, b.MinX), Math.Min(a.MinZ, b.MinZ), Math.Max(a.MaxX, b.MaxX), Math.Max(a.MaxZ, b.MaxZ));

        /// <summary>A huge pawn's click box: (drawn size x fraction x multiplier) centred on its draw cell, never smaller than
        /// its footprint. False = no bigger than vanilla (a one-cell footprint that the body does not exceed).</summary>
        public static bool PawnHitbox(float drawnX, float drawnY, float fraction, float multiplier, CellBox foot, int drawX, int drawZ,
                                      out CellBox box)
        {
            int w = HitboxSide(drawnX, fraction, multiplier), h = HitboxSide(drawnY, fraction, multiplier);
            int fw = foot.MaxX - foot.MinX + 1, fh = foot.MaxZ - foot.MinZ + 1;
            if (w <= fw && h <= fh)
            {
                box = foot;
                return fw * fh > 1;
            }
            box = Union(CentredBox(drawX, drawZ, w, h), foot);
            return true;
        }

        /// <summary>Pawn hitbox side from a drawn size; 1 means "no bigger than vanilla".</summary>
        public static int HitboxSide(float drawn, float fraction, float multiplier)
        {
            return Math.Max(1, RoundHalfUp(drawn * fraction * multiplier));
        }
    }
}
