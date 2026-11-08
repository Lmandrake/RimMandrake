// The smallest fake Verse/RimWorld that SouthDrawsFrontPawn.cs compiles against. Only the members it reads exist; a new
// one it starts reading breaks this build, which is the signal to extend the fake rather than to test around it.
// Pawn_DrawTracker.DrawPos below is vanilla 1.6's line (decomp Verse/Pawn_DrawTracker.cs:43) as the transpiler leaves
// it: SeededYOffset's read replaced by SouthDrawsFrontPawn.OrderedYOffset(this, pawn).
namespace UnityEngine
{
    public struct Vector3
    {
        public float x, y, z;
        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
    }
}

namespace RimMandrake.Patches
{
    public static class RM_PatchesSettings
    {
        public static bool southDrawsFront = true;
    }
}

namespace RimWorld
{
    public class Pawn_FlightTracker
    {
        public bool Flying;
        public float PositionOffsetFactor;
    }
}

namespace Verse
{
    using RimMandrake.Patches;
    using UnityEngine;

    public struct IntVec3
    {
        public int x, y, z;
        public IntVec3(int x, int y, int z) { this.x = x; this.y = y; this.z = z; }
    }

    public class Map
    {
        public IntVec3 Size;
        public Map(int sizeZ) { Size = new IntVec3(sizeZ, 1, sizeZ); }
    }

    public class PawnTweener
    {
        public Vector3 TweenedPos;
    }

    public class Pawn
    {
        public const float PawnLayerAltitude = 23 * 0.36585367f;   // AltitudeLayer.Pawn.AltitudeFor()
        public string label;
        public Map Map;
        public RimWorld.Pawn_FlightTracker flight;
        public Pawn_DrawTracker Drawer;

        public Pawn(string label, Map map, float x, float z, float seededYOffset)
        {
            this.label = label;
            Map = map;
            Drawer = new Pawn_DrawTracker(this, seededYOffset);
            Drawer.tweener.TweenedPos = new Vector3(x, 0f, z);
        }
    }

    public class Pawn_DrawTracker
    {
        private Pawn pawn;
        public PawnTweener tweener = new PawnTweener();
        public float SeededYOffset { get; }

        public Pawn_DrawTracker(Pawn pawn, float seeded) { this.pawn = pawn; SeededYOffset = seeded; }

        private float FlightYOffset() => pawn.flight == null ? 0f : 0.03658537f * pawn.flight.PositionOffsetFactor;

        public float DrawPosY => Pawn.PawnLayerAltitude + FlightYOffset() + SouthDrawsFrontPawn.OrderedYOffset(this, pawn);
    }
}
