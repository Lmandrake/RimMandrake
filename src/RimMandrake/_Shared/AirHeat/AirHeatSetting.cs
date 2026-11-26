// DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS: a hot-air biome's own Mod Settings row (on/off and a degrees slider) writes its
// air-heat GameConditionDef's temperatureOffset; Creature Behaviors' RM_MapComponent_AirHeat follows that field on every
// map of the biome within an in-game hour (0 ends the condition). Linked into each hot-air biome mod (the Forge, the
// Terminal Biomes' Scald, the Greentide) with <Compile Include>; internal, so each assembly has its own copy.
// Air heat is never Direct Sun and never switches off with Direct Sun.
using RimWorld;
using Verse;

namespace RimMandrake.Shared
{
    internal static class AirHeatSetting
    {
        /// <summary>The row's tooltip; every hot-air mod uses the same words.</summary>
        public const string Tip = "On: the air on this land is hotter by this many degrees, by day and by night. It shows on the "
            + "thermometer and in the conditions list. It changes the map's temperature, so plants feel it too, and rooms, "
            + "coolers and insulation answer it as they answer any hot weather. Shade does not cool it. It is not Direct Sun "
            + "and does not switch off with it. Off: the map has its plain climate.";

        /// <summary>Writes the condition's offset: degrees when on, 0 when off. A missing def does nothing.</summary>
        public static void Apply(string conditionDefName, bool on, float degreesC)
        {
            GameConditionDef def = DefDatabase<GameConditionDef>.GetNamedSilentFail(conditionDefName);
            if (def != null)
            {
                def.temperatureOffset = on ? degreesC : 0f;
            }
        }
    }
}
