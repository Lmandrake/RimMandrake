// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Which picture a wall lamp look draws (owner's walk of 2026-11-24: "Lamps are shown to be pointed INTO the wall rather than OUT OF the wall ... This is
// true for every look shown"). RimWorld's facing of a wall attachment is the side its WALL is on (GenConstruct.GetWallAttachedTo: pos +
// CardinalDirections[rot]); the twelve lamp pictures are drawn and named for the side the lamp POINTS to (_north: base at the bottom, head up the
// picture). So at each facing the lamp draws the picture of the opposite one. T_WALL_LAMP_LOOKS_OFFLINE reads the pixels.
namespace RimMandrake.GimmeSomeSlack.Core
{
    public static class WallLampFacing
    {
        /// <summary>The facing (0 N, 1 E, 2 S, 3 W) whose picture a lamp with its wall at <paramref name="rot"/> draws: the way it points.</summary>
        public static int PictureRot(int rot) => (rot + 2) % 4;
    }
}
