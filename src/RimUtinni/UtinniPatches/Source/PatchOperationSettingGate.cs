using System.Xml;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
    // MOD_OPTIONS_RETROFIT_1 — the only way an XML PatchOperation can respect a
    // Mod Settings toggle.
    //
    // WHY THIS IS SAFE: LoadedModManager.LoadAllActiveMods runs CreateModClasses()
    // — which constructs UtinniPatchesMod and so calls GetSettings<T>(), reading
    // the saved settings off disk — BEFORE LoadModXML()/ApplyPatches(). So by the
    // time ApplyWorker runs here, UtinniPatchesSettings' statics hold the player's
    // real choices. (Verse/LoadedModManager.cs, LoadAllActiveMods.)
    //
    // ⚠️ A settings change therefore takes effect on the NEXT game start, not
    // immediately — the def is already built. Every gated option's tooltip says so.
    //
    // Shape copied from Verse.PatchOperationConditional: a <match> branch and a
    // <nomatch> branch, each a full PatchOperation. Returns true when its chosen
    // branch is absent, because PatchOperation.Complete() logs a red error for any
    // operation that never succeeded and "the player turned this off" is not an
    // error.
    public class PatchOperationSettingGate : PatchOperation
    {
        public string setting;
        public PatchOperation match;
        public PatchOperation nomatch;

        protected override bool ApplyWorker(XmlDocument xml)
        {
            bool on;
            switch (setting)
            {
                case "utinniWorldIconEnabled":
                    on = UtinniPatchesSettings.utinniWorldIconEnabled;
                    break;
                default:
                    // Named-switch rather than reflection on purpose: a typo in the
                    // XML must be loud, not silently default to "on".
                    Log.Error("[UtinniPatches] PatchOperationSettingGate: unknown setting '"
                              + setting + "'. Leaving the vanilla def alone.");
                    return false;
            }

            PatchOperation branch = on ? match : nomatch;
            return branch == null || branch.Apply(xml);
        }
    }
}
