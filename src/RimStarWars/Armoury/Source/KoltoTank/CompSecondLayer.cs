using RimWorld;
using UnityEngine;
using Verse;

namespace KoltoTank;

internal class CompSecondLayer : ThingComp
{
    private Graphic graphicInt;

    public Vector3 offset;

    public virtual Graphic Graphic
    {
        get
        {
            if (graphicInt == null)
            {
                if (Props.graphicData == null)
                {
                    return BaseContent.BadGraphic;
                }
                graphicInt = Props.graphicData.GraphicColoredFor(parent);
                offset = Props.offset;
            }
            return graphicInt;
        }
    }

    public CompProperties_SecondLayer Props => (CompProperties_SecondLayer)props;

    public override void PostDraw()
    {
        if (parent.Rotation == Rot4.South)
        {
            Graphic.Draw(GenThing.TrueCenter(parent.Position, parent.Rotation, parent.def.size, Props.Altitude) + offset, parent.Rotation, parent, 0f);
        }
    }
}
