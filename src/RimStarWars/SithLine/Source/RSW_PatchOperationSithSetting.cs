using System.Xml;
using Verse;

namespace RimMandrake.StarWars.SithLine
{
    // An XML PatchOperation that respects a Sith Line Mod Setting. Same shape and reasoning as
    // RimMandrake.Utinni.UtinniPatches.PatchOperationSettingGate: LoadedModManager constructs RSW_SithLineMod (and so
    // reads the saved settings) BEFORE it applies patches, so the statics hold the player's choice here. A change
    // therefore applies at the next game start, which every gated option's label says.
    // Returns true when its chosen branch is absent: "the player turned this off" is not a patch error.
    public class RSW_PatchOperationSithSetting : PatchOperation
    {
        public string setting;
        public PatchOperation match;
        public PatchOperation nomatch;

        protected override bool ApplyWorker(XmlDocument xml)
        {
            bool on;
            switch (setting)
            {
                case "reskinText":
                    on = RSW_SithLineSettings.reskinText;
                    break;
                case "vanillaQuestsOff":
                    on = RSW_SithLineSettings.vanillaQuestsOff;
                    break;
                case "sithBuildingsUnbuildable":
                    on = RSW_SithLineSettings.sithBuildingsUnbuildable;
                    break;
                default:
                    // Named switch, not reflection: a typo in the XML must be loud, never a silent "on".
                    Log.Error("[SithLine] RSW_PatchOperationSithSetting: unknown setting '" + setting + "'.");
                    return false;
            }
            PatchOperation branch = on ? match : nomatch;
            return branch == null || branch.Apply(xml);
        }
    }
}
