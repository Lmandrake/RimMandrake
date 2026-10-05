// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Round 4 (owner 2026-10-04, typed: "Wall plates/rock holes STILL need more perspective bending and shifting into the wall.
// Check next time: do they extend OUT of the wall? If so, it's not right. They should look mounted ON the wall."):
// where a thing mounted on a wall face may be drawn, per face, from the 1.6 wall look as MEASURED in his screenshot
// 20261004162252_1.jpg (station 9, 133 px per cell): a wall cell draws its TOP over its north 0.62 and its visible SOUTH
// FACE as the light band over its south 0.38; its east and west faces are seen edge-on (a narrow bevel, ~0.18); its north
// face is hidden behind the top. The offline proof is src/RimMandrake/Utils/mockups/messy_conduit/wall_mount_check.py.
using System;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>Which face of a wall a mount sits on, named for the face (South = the face looking south, the visible one).</summary>
    public enum WallFaceKind { South, North, Side }

    public static class WallMount
    {
        /// <summary>The visible south face's height on screen, cells (the light band at the bottom of the wall cell).</summary>
        public const double SouthBand = 0.38;
        /// <summary>The east/west faces' edge-on bevel, cells: a side mount stays within it.</summary>
        public const double SideBevel = 0.18;
        /// <summary>The north face is hidden: a mount there shows no more than this sliver of the wall top.</summary>
        public const double NorthSliver = 0.08;

        /// <summary>into = unit vector from the open cell INTO the wall. A cord arriving from the south (+Z) meets the wall's
        /// SOUTH face; from the north (-Z) its hidden NORTH face; along X a side face.</summary>
        public static WallFaceKind FaceOf(V2 into) => into.Z > 0.5 ? WallFaceKind.South : into.Z < -0.5 ? WallFaceKind.North : WallFaceKind.Side;

        /// <summary>How deep into the wall (cells from its outer face, along into) a mount may reach and still read as ON the face.</summary>
        public static double MaxDepth(WallFaceKind f) => f == WallFaceKind.South ? SouthBand : f == WallFaceKind.Side ? SideBevel : NorthSliver;

        // ---------------------------------------------------------------- the cord's wall plate / rock hole decal
        // Plate (wall) and hole (rock) regions of the shipped Stub art, measured (u = art X, v = art Z, 0..1) over every look's
        // PNG; the region LEFT of U0 is the art's own cord curling in, which round 3 squashed into a hook (station 6). It is
        // never drawn now: the real cord meets the plate straight.
        public const double WallU0 = 0.25, WallU1 = 0.80, WallV0 = 0.24, WallV1 = 0.77;
        public const double RockU0 = 0.30, RockU1 = 0.84, RockV0 = 0.18, RockV1 = 0.82;
        /// <summary>An edge-on (side / hidden north) plate shows only the far strip of the plate: its edge seen side-on.</summary>
        public const double EdgeU0 = 0.56;
        /// <summary>The plate's size across the cord, cells.</summary>
        public const double PlateAcross = 0.36;
        /// <summary>Gap kept between the face line and the plate, cells, so no texel lands on the open floor.</summary>
        public const double FaceMargin = 0.01;

        /// <summary>Depth (along into) the plate is drawn at, per face: the south face shows the whole plate foreshortened
        /// into its band; a side or north face shows a thin strip of it.</summary>
        public static double PlateDepth(WallFaceKind f) => f == WallFaceKind.South ? SouthBand - 0.06 : f == WallFaceKind.Side ? 0.10 : 0.06;

        /// <summary>The decal for a cord's entry into a wall (rock = false) or rock (true) face: centred inside the wall,
        /// art +X along into, ScaleX = depth, Scale = across, cropped to the plate/hole.</summary>
        public static CordDecal EntryDecal(DecalKind kind, V2 face, V2 into)
        {
            WallFaceKind f = FaceOf(into);
            bool rock = kind == DecalKind.StubRock;
            double depth = PlateDepth(f);
            double u0 = rock ? RockU0 : WallU0, u1 = rock ? RockU1 : WallU1;
            if (f != WallFaceKind.South) u0 = Math.Max(u0, EdgeU0);
            var d = new CordDecal(kind, face + into * (FaceMargin + depth / 2), Math.Atan2(into.Z, into.X), PlateAcross)
            {
                Squash = depth / PlateAcross,
                U0 = u0, U1 = u1, V0 = rock ? RockV0 : WallV0, V1 = rock ? RockV1 : WallV1
            };
            return d;
        }

        /// <summary>The socket point on a plate (where the grommet / hole is): the plate's centre.</summary>
        public static V2 Socket(CordDecal d) => d.Pos;

        /// <summary>How far the decal's quad reaches along into from the face: (near, far) in cells. near &lt; 0 = it pokes out
        /// onto the open floor.</summary>
        public static void DepthSpan(CordDecal d, V2 face, V2 into, out double near, out double far)
        {
            double c = (d.Pos.X - face.X) * into.X + (d.Pos.Z - face.Z) * into.Z;
            double ca = Math.Abs(Math.Cos(d.Angle) * into.X + Math.Sin(d.Angle) * into.Z);   // 1 when art X is along into
            double half = (d.ScaleX * ca + d.Scale * (1 - ca)) / 2;
            near = c - half; far = c + half;
        }

        /// <summary>Is the decal mounted ON its face: nothing on the open floor (tolerance tol), nothing deeper than the face allows.</summary>
        public static bool OnFace(CordDecal d, V2 face, V2 into, double tol = 0.005)
        {
            DepthSpan(d, face, into, out double near, out double far);
            return near >= -tol && far <= MaxDepth(FaceOf(into)) + tol;
        }

        // ---------------------------------------------------------------- the wall terminal's loose wire
        /// <summary>Owner round 4 (station 6: "'hanging disconnected wire' doesn't look right hanging out of a perspective
        /// west-facing wall"): the loose wire leaves the socket STRAIGHT, continuing the line of the cord, then droops onto
        /// the floor. On the visible south face it hangs straight down the face (screen down is down that face) and curls on
        /// the floor at its foot; on a side or the hidden north face it comes straight out of the wall and lies on the floor.
        /// The first segment is straight along the exit direction (no hook at the socket).</summary>
        public static System.Collections.Generic.List<V2> LooseWire(V2 socket, V2 face, V2 into)
        {
            WallFaceKind f = FaceOf(into);
            var outv = -into;
            var side = new V2(-into.Z, into.X);
            var o = new System.Collections.Generic.List<V2>(18);
            if (f == WallFaceKind.South)
            {
                // straight down the band to its foot, then 0.16 onto the floor, the last bit curling sideways
                double toFoot = (socket.Z - face.Z);
                for (int i = 0; i <= 8; i++) o.Add(new V2(socket.X, socket.Z - toFoot * i / 8.0));
                V2 foot = o[o.Count - 1];
                for (int i = 1; i <= 8; i++)
                {
                    double t = i / 8.0;
                    o.Add(foot + new V2(0, -0.16 * t) + side * (0.10 * t * t));
                }
                return o;
            }
            // straight out of the face along the cord's own line, then sagging sideways (screen-down for a side face)
            V2 start = socket, exit = face + outv * 0.0;
            double inWall = (start - exit).Len;
            int k = Math.Max(2, (int)Math.Ceiling(inWall / 0.04));
            for (int i = 0; i <= k; i++) o.Add(start + (exit - start) * (i / (double)k));
            V2 sag = f == WallFaceKind.Side ? new V2(0, -1) : side;
            for (int i = 1; i <= 10; i++)
            {
                double t = i / 10.0;
                double droop = Math.Max(0, t - 0.35) / 0.65;          // the first third leaves dead straight, then it sags
                o.Add(exit + outv * (0.26 * t) + sag * (0.14 * droop * droop));
            }
            return o;
        }
    }
}
