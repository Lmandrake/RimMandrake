using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // XML-deserialized entry: which item, consumed, unlocks which mode.
    // Plain data class -- RimWorld's XML loader fills the public fields by
    // reflection from a <li><moduleDef>..</moduleDef><mode>..</mode></li>.
    public class ShieldModuleMapping
    {
        public ThingDef moduleDef;
        public ShieldFieldMode mode;
    }
}
