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

    // Dead field: never set by the shipped KoltoTank def and never read by
    // CompKoltoTank (which checks hediff.def.chronic on the healed hediff
    // instead -- an unrelated value). Left in place for save/decompile
    // fidelity, not wired to anything.
    public bool chronic;

    // Dead field: floats at its 0f default in the shipped def and is
    // deliberately left unread by Building_KoltoTank -- reading it would
    // divide by that 0f. See the ticksBetweenHealing comment there.
    public float ticksBetweenHealing;

    // Read by Building_KoltoTank.SpawnSetup to scale ticksBetweenHealing
    // (2500 ticks/hour * multiplier). The shipped def sets 2.5, matching its
    // own description ("heal one random injury per 2.5 hours").
    public float multiplier;

    public CompProperties_KoltoTank()
    {
        compClass = typeof(CompKoltoTank);
    }
}
