using Verse;

namespace RimMandrake.DivingInteraction
{
    // ELDER_TREASURE_TAG_TABLE_1 (design pass DI-1). Marker DefModExtension: "the Brine Elder may release
    // this def as a one-of-each singular treasure." Presence alone is the flag. RM_ tier treasures carry it
    // in TerminalBiomes/RM_ElderTreasures.xml; the three canon treasures (lightsaber, pre-Republic navcore,
    // droid brain) join the table by carrying it on their RUT_ defs in the Utinni patch layer. Replaces the
    // private string array that XML could not append to.
    public class RM_ElderTreasureExtension : DefModExtension
    {
    }
}
