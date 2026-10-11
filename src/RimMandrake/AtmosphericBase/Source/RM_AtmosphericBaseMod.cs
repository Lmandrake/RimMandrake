using UnityEngine;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_AtmosphericBaseMod : Mod
    {
        public static RM_AtmosphericBaseSettings settings;

        public RM_AtmosphericBaseMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_AtmosphericBaseSettings>();
        }

        public override string SettingsCategory()
        {
            return "Atmospheric Base";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
