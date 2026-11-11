// DRAWN_EXTENT_UNIFY_ONE_RULER_TWO_MODS - the one ruler for a plant's DRAWN size: the square Plant.Print draws. Source-linked
// (<Compile Include … Link=…>) into Huge Things (hitboxes, blocked trunks) and Sun & Shade (crowns, shade), so a tree's hitbox
// and its crown can never disagree. Verse-free: the Huge Things fuzz (HugeThings/Source/SelfTest) compiles this file, and
// HugeThings/selftest_hugethings_footprint.py mirrors it. Types are internal, so two DLLs carrying it never share a public
// type name. Design: design/RimMandrake/sun_and_shade_modularity_2026-10-19.md §4 "One ruler for drawn size".
//
// THE DRAW TRANSFORM, measured from decompiled 1.6 (RimSage, 2026-10-07), Plant.Print for maxMeshCount 1:
//   centre = Position + (0.5, 0.5) + Gen.RandomHorizontalVector(0.05f)  (the jitter; the caller replays Rand)
//   visual = plant.visualSizeRange.LerpThroughRange(growth)              (the caller reads it from Verse)
//   if (centre.z - visual / 2 < Position.z) centre.z = Position.z + visual / 2   (bottom anchoring; uses visual, not side)
//   side = graphicData.drawSize.x * visual; Printer_Plane.PrintPlane(centre, (side, side)): a square, whatever the aspect.
namespace RimMandrake.Shared
{
    /// <summary>The drawn quad: a square, world coordinates in cells.</summary>
    internal struct DrawnQuad
    {
        public float MinX, MinZ, Size;
    }

    internal static class DrawnExtent
    {
        /// <summary>The drawn side: graphicData.drawSize.x × visual size.</summary>
        public static float Side(float drawSizeX, float visual) => drawSizeX * visual;

        /// <summary>The quad Plant.Print draws for a plant at (rootX, rootZ) with this visual size and position jitter.</summary>
        public static DrawnQuad Quad(int rootX, int rootZ, float drawSizeX, float visual, float jitterX, float jitterZ)
        {
            float cx = rootX + 0.5f + jitterX;
            float cz = rootZ + 0.5f + jitterZ;
            if (cz - visual / 2f < rootZ) cz = rootZ + visual / 2f;
            float side = Side(drawSizeX, visual);
            return new DrawnQuad { MinX = cx - side / 2f, MinZ = cz - side / 2f, Size = side };
        }
    }
}
