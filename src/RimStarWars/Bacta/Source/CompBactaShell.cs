using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    public class CompProperties_BactaShell : CompProperties
    {
        /// <summary>The shell texture. Rotation-aware, like the tank body it sits on.</summary>
        public GraphicData graphicData;

        /// <summary>Which layer to draw it at. Default is over motes, so over the pawn.</summary>
        public AltitudeLayer altitudeLayer = AltitudeLayer.MoteOverhead;

        /// <summary>Offset from the building centre, in cells.</summary>
        public Vector3 offset = Vector3.zero;

        public CompProperties_BactaShell()
        {
            compClass = typeof(CompBactaShell);
        }

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string item in base.ConfigErrors(parentDef))
            {
                yield return item;
            }
            if (graphicData == null)
            {
                yield return "CompProperties_BactaShell has no graphicData";
            }
        }
    }

    /// <summary>
    /// The glass front of the tank, drawn OVER the occupant.
    ///
    /// Why a second layer at all: the tank body is printed into the map mesh below the pawn,
    /// and the pawn is drawn by the tank's DynamicDrawPhaseAt. Without a third pass the pawn
    /// floats in front of the cylinder rather than inside it. This is the same trick vanilla
    /// uses for the growth vat's top graphic and the BioReactor mod's shell layer — one
    /// rotation-aware graphic, drawn at a higher altitude, every frame.
    /// </summary>
    public class CompBactaShell : ThingComp
    {
        [Unsaved(false)]
        private Graphic cachedGraphic;

        public CompProperties_BactaShell Props => (CompProperties_BactaShell)props;

        public Graphic ShellGraphic
        {
            get
            {
                if (cachedGraphic == null && Props.graphicData != null)
                {
                    cachedGraphic = Props.graphicData.GraphicColoredFor(parent);
                }
                return cachedGraphic;
            }
        }

        public override void PostDraw()
        {
            base.PostDraw();

            if (!parent.Spawned)
            {
                return;
            }

            Graphic graphic = ShellGraphic;
            if (graphic == null)
            {
                return;
            }

            Vector3 loc = parent.DrawPos + Props.offset;
            loc.y = Props.altitudeLayer.AltitudeFor();
            graphic.Draw(loc, parent.Rotation, parent);
        }
    }
}
