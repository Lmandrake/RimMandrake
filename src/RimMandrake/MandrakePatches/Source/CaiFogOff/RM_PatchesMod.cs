using UnityEngine;
using Verse;

namespace RimMandrake.Patches
{
    // The first Mod Settings page of RimMandrake Patches (CAI_FOG_SILENCE_FORCED_OFF_BY_US). One toggle; default = shipped
    // behaviour (CAI 5000's fog forced off, owner card 2026-10-20 "Keep CAI, force its fog off"); off = CAI's own checkbox
    // decides again (CAI's measured fresh-install default is also off).
    public class RM_PatchesSettings : ModSettings
    {
        public static bool caiFogForcedOff = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref caiFogForcedOff, "caiFogForcedOff", true);
        }
    }

    public class RM_PatchesMod : Mod
    {
        public RM_PatchesMod(ModContentPack content) : base(content)
        {
            GetSettings<RM_PatchesSettings>();
            CaiFogOff.Install();
        }

        public override string SettingsCategory() => "RimMandrake Patches";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            var l = new Listing_Standard();
            l.Begin(inRect);
            bool before = RM_PatchesSettings.caiFogForcedOff;
            l.CheckboxLabeled("Keep CAI 5000's fog of war off", ref RM_PatchesSettings.caiFogForcedOff,
                "CAI 5000 (Advanced AI + Fog Of War) ships its own fog layer. While this is on, that fog stays off at every " +
                "start and whenever CAI's settings are saved; CAI's combat AI is untouched. Turn it off to let CAI's own " +
                "'fog of war' checkbox decide (CAI's default is off). Only matters if CAI 5000 is installed.");
            l.Gap();
            l.Label(CaiFogOff.Status);
            l.End();
            if (RM_PatchesSettings.caiFogForcedOff && !before)
                CaiFogOff.Force("settings toggle");
        }
    }
}
