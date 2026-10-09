using System;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_WORLD_LIGHT_1 (c), owner card 2026-10-08: a deepfire-lit colony is more visible at night. Once an hour,
    // on a player home map under a dark sky, every lit deepfire light this component owns raises the shared Colony
    // Visibility dial (the Visibility mod's GameComponent_ColonyVisibility.Adjust) a little. Visibility is optional:
    // found by name, never referenced, and absent it does nothing.
    // PROVISIONAL numbers: 0.05 per light per hour (LuminousPigmentSettings.deepfireVisibilityPerLight), at most
    // MaxPerPulse per hour, "dark sky" = sky glow below DarkSky.
    public partial class MapComponent_DeepfireLights
    {
        private const int VisibilityInterval = 2500;   // one in-game hour
        private const float DarkSky = 0.3f;            // PROVISIONAL
        private const float MaxPerPulse = 2f;          // PROVISIONAL

        private static bool visibilityLooked;
        private static Type visibilityType;
        private static MethodInfo visibilityAdjust;

        private void NightVisibilityPulse()
        {
            if (!LuminousPigmentSettings.deepfireNightVisibility || LuminousPigmentSettings.deepfireVisibilityPerLight <= 0f) return;
            if (!map.IsPlayerHome || map.skyManager.CurSkyGlow >= DarkSky) return;
            int lit = 0;
            foreach (LightEntry e in entries.Values)
            {
                if (e.Proxy == null || !e.Proxy.Spawned) continue;
                CompGlower g = e.Proxy.TryGetComp<CompGlower>();
                if (g != null && g.Glows && g.GlowRadius > 0f) lit++;
            }
            if (lit == 0) return;
            float delta = Math.Min(MaxPerPulse, lit * LuminousPigmentSettings.deepfireVisibilityPerLight);
            AdjustColonyVisibility(delta, lit + " deepfire lights at night");
        }

        private static void AdjustColonyVisibility(float delta, string reason)
        {
            if (!visibilityLooked)
            {
                visibilityLooked = true;
                visibilityType = GenTypes.GetTypeInAnyAssembly("RimMandrake.Visibility.GameComponent_ColonyVisibility");
                visibilityAdjust = visibilityType?.GetMethod("Adjust", new[] { typeof(float), typeof(string) });
            }
            if (visibilityAdjust == null || Current.Game == null) return;
            GameComponent comp = Current.Game.GetComponent(visibilityType);
            if (comp != null) visibilityAdjust.Invoke(comp, new object[] { delta, reason });
        }
    }
}
