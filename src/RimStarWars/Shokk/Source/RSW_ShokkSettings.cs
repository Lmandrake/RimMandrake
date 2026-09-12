using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Shokk
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Shokk.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
    //
    // The only runtime C# mechanism this assembly ships is
    // RSW_CompEmergentSpawnOnDestroy (the rest of the mod — RSW_ShokkBound,
    // RSW_Damage_ShokkSpit, the turret-gun weapon, RSW_Webwork_SunScald —
    // is pure XML/def content, or lives in the shared
    // mandrake.rm.creaturebehaviors assembly and is out of this mod's
    // scope). Its one tunable is spawnChance, a per-def CompProperties
    // field (design-owned in whatever XML attaches the comp) — exposed
    // here as a global multiplier plus a master off switch, same shape as
    // Greentide's mireSeverityMultiplier.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_ShokkSettings : ModSettings
    {
        public static bool emergentSpawnEnabled = true;
        public static float emergentSpawnChanceMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref emergentSpawnEnabled, "emergentSpawnEnabled", true);
            Scribe_Values.Look(ref emergentSpawnChanceMultiplier, "emergentSpawnChanceMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Emergent Shokk spawn enabled", ref emergentSpawnEnabled,
                "Destroying a harvest-type Thing this is attached to (a creep-web node, a "
              + "gutter, …) has a chance to spawn a hostile, manhunter-forced Wyyyschokk on the "
              + "spot. Off: destroying those things never spawns anything.");
            if (emergentSpawnEnabled)
            {
                list.Label("  Spawn chance: " + emergentSpawnChanceMultiplier.ToString("0.00")
                    + "x (each def's own base chance, e.g. the shipped default of 3%)");
                emergentSpawnChanceMultiplier = list.Slider(emergentSpawnChanceMultiplier, 0f, 3f);
            }

            list.End();
        }
    }

    public class RSW_ShokkMod : Mod
    {
        public static RSW_ShokkSettings settings;

        public RSW_ShokkMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_ShokkSettings>();
        }

        public override string SettingsCategory()
        {
            return "Shokk";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
