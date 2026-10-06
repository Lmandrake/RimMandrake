using System.Reflection;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.TerminalBiomes
{
    // SCALD_FLOOR_PASS_1. The Scald kit piece whose engine class was
    // VANILLA (not mandrake.rm.environmentalhazards), so the only way to gate
    // it is a thin subclass here that reads this mod's own settings
    // directly. It does not need the shared assembly, so the vents keep
    // loading with or without it.

    // S4 — vent fields. RUT_ScaldVent's thingClass. Off: the vent stops
    // spraying (no steam puff, no sound) and any spray already sounding is
    // ended at once; the vent stays on the map, untouched. The steam-catch
    // condenser (S2) separately reads the vent as dormant through
    // RM_MechanicGateExtension on RUT_ScaldVent's def, so it stops drawing
    // from it too. On again: spraying resumes on the vent's own rhythm.
    public class RM_Building_ScaldVent : Building_SteamGeyser
    {
        // Building_SteamGeyser keeps its spray sound private (1.6 decompile:
        // `private Sustainer spraySustainer`). Read once; if a future engine
        // renames it the lookup is null and a switched-off vent simply lets
        // a mid-spray sound run out on its own, never an error.
        private static readonly FieldInfo SpraySustainerField =
            typeof(Building_SteamGeyser).GetField("spraySustainer", BindingFlags.Instance | BindingFlags.NonPublic);

        protected override void Tick()
        {
            if (RM_TerminalBiomesSettings.ScaldS4VentFieldsActive)
            {
                base.Tick();
                return;
            }

            if (SpraySustainerField != null && SpraySustainerField.GetValue(this) is Sustainer sustainer)
            {
                sustainer.End();
                SpraySustainerField.SetValue(this, null);
            }
        }

        public override string GetInspectString()
        {
            string text = base.GetInspectString();
            if (RM_TerminalBiomesSettings.ScaldS4VentFieldsActive)
            {
                return text;
            }
            string dormant = "RM_TerminalBiomes_VentDormant".Translate();
            return text.NullOrEmpty() ? dormant : text + "\n" + dormant;
        }
    }
}
