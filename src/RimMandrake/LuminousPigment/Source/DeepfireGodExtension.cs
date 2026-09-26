using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §5.3: the hook the (not-yet-built) Utinni statue mod tags each
    // idol def with, under MayRequire="mandrake.rm.luminouspigment" --
    // "god" is the Ninefold God enum member name as a string (e.g. "Rekko"),
    // resolved by NinefoldDeltaBridge, never a hard enum reference (Ninefold
    // is a soft dependency). Nothing in THIS build reads the extension yet
    // -- the statue-coat delta (spec §5.2's "coat applied to a statue of a
    // god" row) needs CompDeepfire (piece 1, painting), deferred to
    // DEEPFIRE_PAINT_LIVE_VERIFY_1. Shipping the extension type now lets the
    // statue mod tag its idols today without waiting on that follow-on.
    public class DeepfireGodExtension : DefModExtension
    {
        public string god;
    }
}
