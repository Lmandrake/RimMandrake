using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §5.3: the hook the (not-yet-built) Utinni statue mod tags each
    // idol def with, under MayRequire="mandrake.rm.luminouspigment" --
    // "god" is the Ninefold God enum member name as a string (e.g. "Rekko"),
    // resolved by NinefoldDeltaBridge, never a hard enum reference (Ninefold
    // is a soft dependency). Read by DeepfireGodDeltas.StatueGodOf when a
    // first coat lands on a thing whose def carries it (spec §5.2's "coat
    // applied to a statue of a god" row). A name that is not a God member
    // reads as untagged.
    public class DeepfireGodExtension : DefModExtension
    {
        public string god;
    }
}
