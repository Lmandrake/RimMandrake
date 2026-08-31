using UnityEngine;
using Verse;

namespace KoltoTank;

public class CompProperties_KoltoTank : CompProperties
{
    public Vector3 innerDrawOffset;

    public Vector3 waterDrawCenter;

    public Vector2 waterDrawSize;

    public float bodySizeMin;

    public float bodySizeMax;

    public Color liquidColor;

    public float waterfillspeed = 0.01f;

    public string hediffOnExit;

    public string hediffOnEntry;

    public bool chronic;

    public float ticksBetweenHealing;

    public float multiplier;

    public CompProperties_KoltoTank()
    {
        compClass = typeof(CompKoltoTank);
    }
}
