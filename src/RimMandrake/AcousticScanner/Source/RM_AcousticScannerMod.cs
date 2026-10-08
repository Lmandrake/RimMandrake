using UnityEngine;
using Verse;

namespace RimMandrake.AcousticScanner
{
    // GRAVSHIP_ACOUSTIC_SCANNER_1 — Mod Settings (MOD_OPTIONS_RETROFIT_1 doctrine:
    // defaults = shipped behaviour, every toggle wired to something real).
    public class RM_AcousticScannerSettings : ModSettings
    {
        public const int MinBandSize = RM_AcousticKernel.MinBandSize;   // hard floor: a reading is ALWAYS banded, never exact
        public const int MaxBandSize = RM_AcousticKernel.MaxBandSize;

        public bool enabled = true;
        public bool requireLandedShip = true;
        public float cooldownHours = 24f;
        public float overlayHours = 6f;
        public int bandSize = 11;
        public float rangeCells = 60f;
        public bool pulseEffects = true;

        public int BandSizeClamped => RM_AcousticKernel.ClampBandSetting(bandSize);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref requireLandedShip, "requireLandedShip", true);
            Scribe_Values.Look(ref cooldownHours, "cooldownHours", 24f);
            Scribe_Values.Look(ref overlayHours, "overlayHours", 6f);
            Scribe_Values.Look(ref bandSize, "bandSize", 11);
            Scribe_Values.Look(ref rangeCells, "rangeCells", 60f);
            Scribe_Values.Look(ref pulseEffects, "pulseEffects", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("RM_Acoustic_SettingEnabled".Translate(), ref enabled,
                "RM_Acoustic_SettingEnabledTip".Translate());
            list.CheckboxLabeled("RM_Acoustic_SettingRequireShip".Translate(), ref requireLandedShip,
                "RM_Acoustic_SettingRequireShipTip".Translate());
            list.CheckboxLabeled("RM_Acoustic_SettingEffects".Translate(), ref pulseEffects,
                "RM_Acoustic_SettingEffectsTip".Translate());
            list.Gap();

            list.Label("RM_Acoustic_SettingCooldown".Translate(cooldownHours.ToString("0")));
            cooldownHours = Mathf.Round(list.Slider(cooldownHours, 1f, 120f));
            list.Label("RM_Acoustic_SettingOverlay".Translate(overlayHours.ToString("0")));
            overlayHours = Mathf.Round(list.Slider(overlayHours, 1f, 48f));
            list.Label("RM_Acoustic_SettingRange".Translate(rangeCells.ToString("0")));
            rangeCells = Mathf.Round(list.Slider(rangeCells, 20f, 250f));
            list.Label("RM_Acoustic_SettingBand".Translate(BandSizeClamped, MinBandSize));
            bandSize = Mathf.RoundToInt(list.Slider(BandSizeClamped, MinBandSize, MaxBandSize));

            list.Gap();
            if (list.ButtonText("RM_Acoustic_SettingReset".Translate()))
            {
                enabled = true;
                requireLandedShip = true;
                pulseEffects = true;
                cooldownHours = 24f;
                overlayHours = 6f;
                bandSize = 11;
                rangeCells = 60f;
            }
            list.End();
        }
    }

    public class RM_AcousticScannerMod : Mod
    {
        public static RM_AcousticScannerSettings settings;

        public RM_AcousticScannerMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_AcousticScannerSettings>();
        }

        public override string SettingsCategory() => "RM_Acoustic_SettingsCategory".Translate();

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);
    }
}
