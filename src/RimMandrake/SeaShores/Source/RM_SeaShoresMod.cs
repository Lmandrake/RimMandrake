using UnityEngine;
using Verse;

namespace RimMandrake.SeaShores
{
    public class RM_SeaShoresMod : Mod
    {
        public static RM_SeaShoresSettings settings;

        public RM_SeaShoresMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_SeaShoresSettings>();
        }

        public override string SettingsCategory()
        {
            return "Sea Shores";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
