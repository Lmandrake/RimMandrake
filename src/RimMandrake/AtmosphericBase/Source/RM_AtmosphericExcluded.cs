// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1. A thing whose def carries this extension is never an emitter, whatever
// it is. It is how a hologram (L16: a god's body, never driven) or any glow that means something else opts out.
// Usage, on the def that should never be touched:
//   <modExtensions><li Class="RimMandrake.AtmosphericBase.RM_AtmosphericExcluded" /></modExtensions>
// (put MayRequire="mandrake.rm.atmosphericbase" on that <li> when this mod is optional for the def's mod).
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_AtmosphericExcluded : DefModExtension
    {
    }
}
