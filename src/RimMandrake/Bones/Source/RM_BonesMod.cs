using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.Bones
{
    // BONES_LEAN_PORT_BUILD_TREELESS_WORLD Mod Settings. Defaults = shipped behaviour; all off = butchering
    // yields no bone (RM_Bones stays a Woody stuff and the rotting bed still yields it).
    public class RM_BonesSettings : ModSettings
    {
        public static bool butcherBones = true;
        public static float boneMultiplier = 1f;   // 0-5, RM_BonesKernel.MaxMultiplier

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref butcherBones, "butcherBones", true);
            Scribe_Values.Look(ref boneMultiplier, "boneMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard();
            list.Begin(inRect);
            list.CheckboxLabeled("RM_Bones_ButcherBones".Translate(), ref butcherBones, "RM_Bones_ButcherBones_Tip".Translate());
            list.Gap();
            list.Label("RM_Bones_Multiplier".Translate(boneMultiplier.ToString("0.00")), -1f, "RM_Bones_Multiplier_Tip".Translate());
            boneMultiplier = Mathf.Round(list.Slider(boneMultiplier, 0f, RM_BonesKernel.MaxMultiplier) * 20f) / 20f;
            list.Gap();
            if (list.ButtonText("RM_Bones_Reset".Translate()))
            {
                butcherBones = true;
                boneMultiplier = 1f;
            }
            list.End();
        }
    }

    public class RM_BonesMod : Mod
    {
        public static RM_BonesSettings settings;

        public RM_BonesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_BonesSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.bones"), typeof(RM_BonesMod).Assembly, "RimMandrake.Bones");
        }

        public override string SettingsCategory()
        {
            return "RM_Bones_SettingsCategory".Translate();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
