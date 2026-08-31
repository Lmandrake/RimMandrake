using UnityEngine;
using Verse;

namespace KoltoTank;

internal class CompProperties_SecondLayer : CompProperties
{
    public GraphicData graphicData = null;

    public Vector3 offset = default(Vector3);

    // Kept as the literal numeric value from the decompiled source rather than
    // guessing which AltitudeLayer enum member it names in 1.6.
    public AltitudeLayer altitudeLayer = (AltitudeLayer)28;

    public float Altitude => Altitudes.AltitudeFor(altitudeLayer);

    public CompProperties_SecondLayer()
    {
        compClass = typeof(CompSecondLayer);
    }
}
