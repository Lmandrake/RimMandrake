using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.JawaIkee
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Ikee thought worker.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
    //
    // This assembly (Assemblies/JawaIkee.dll) ships inside the SWBestiary
    // mod folder but is a SEPARATE, unmerged DLL from the Livestock one
    // (RimMandrakeLivestockRSW.dll, its own RSW_LivestockSettings) — see
    // SWBestiary/About.xml's own "left in place, unmerged" notes for both.
    // Two settings entries under one packageId is the honest shape of that:
    // this one is titled distinctly so it reads as SWBestiary's Ikee slice,
    // not a whole second mod.
    //
    // One runtime mechanic here: ThoughtWorker_IkeeNearby. Its per-thought
    // radius and tolerant-xenotype list are already def-editable via
    // IkeeToleranceExtension in XML — that is the right place for a design
    // call, not a global settings duplicate — so the only thing worth a
    // player-facing toggle is turning the whole mood effect off.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_JawaIkeeSettings : ModSettings
    {
        public static bool ikeeThoughtEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ikeeThoughtEnabled, "ikeeThoughtEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("\"The ikee is watching me\" mood effect", ref ikeeThoughtEnabled,
                "Pawns near an ikee get a mood thought: comforted if their xenotype is one that "
              + "keeps creepy pets, unsettled otherwise. Off: the ikee has no mood effect on "
              + "anyone.");

            list.End();
        }
    }

    public class RSW_JawaIkeeMod : Mod
    {
        public static RSW_JawaIkeeSettings settings;

        public RSW_JawaIkeeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_JawaIkeeSettings>();
        }

        public override string SettingsCategory()
        {
            return "SW Bestiary: Ikee";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
