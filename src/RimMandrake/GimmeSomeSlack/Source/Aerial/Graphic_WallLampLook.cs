using RimMandrake.GimmeSomeSlack.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>A wall lamp's look: a Graphic_Multi that draws, at each facing, the picture of the way the lamp points, away from its wall
    /// (<see cref="WallLampFacing"/>). Only which of its own four pictures is drawn changes.</summary>
    public class Graphic_WallLampLook : Graphic_Multi
    {
        private Material Pic(int rot)
        {
            switch (WallLampFacing.PictureRot(rot)) { case 0: return base.MatNorth; case 1: return base.MatEast; case 2: return base.MatSouth; default: return base.MatWest; }
        }
        private bool Flip(int rot) { int p = WallLampFacing.PictureRot(rot); return p == 1 ? base.EastFlipped : p == 3 && base.WestFlipped; }

        public override Material MatNorth => Pic(0);
        public override Material MatEast => Pic(1);
        public override Material MatSouth => Pic(2);
        public override Material MatWest => Pic(3);
        public override bool EastFlipped => Flip(1);
        public override bool WestFlipped => Flip(3);

        public override Graphic GetColoredVersion(Shader newShader, Color newColor, Color newColorTwo)
        {
            return GraphicDatabase.Get<Graphic_WallLampLook>(path, newShader, drawSize, newColor, newColorTwo, data, maskPath);
        }
    }
}
