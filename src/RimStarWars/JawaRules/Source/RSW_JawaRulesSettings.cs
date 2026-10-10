using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.JawaRules
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Jawa Rules.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData, DoWindowContents
    // called from the Mod subclass).
    //
    // Named RSW_JawaRulesSettings/RSW_JawaRulesMod rather than
    // JawaRulesSettings/JawaRulesMod because JawaRulesMod is ALREADY the
    // name of this assembly's static Harmony-bootstrap class — colliding
    // with it is not an option — and this tier's naming grammar (owner,
    // 2026-08-30) prefixes new types RSW_ anyway.
    //
    // Five knobs, one per runtime mechanic this assembly's static
    // constructor arms:
    //   1. sowBanEnabled       — Patch_GrowerSow_ExtraRequirements
    //   2. droidRelationsEnabled — Patch_CreateInitialComponents
    //   3. petNamesEnabled     — Patch_GenerateNecessaryName
    //   4/5. worldLabel* — the two transpilers. A transpiler rewrites IL
    //      once, at patch-apply time, so there is no per-frame hook left to
    //      gate — instead each rewritten call site now CALLS
    //      CurrentWorldLabelAlpha()/CurrentWorldLabelLift() instead of
    //      pushing a baked-in literal, so the settings value (or the
    //      vanilla fallback, if the boost is switched off) is read live,
    //      every time WorldFeatures.UpdateAlpha / WrapAroundPlanetSurface
    //      runs — no restart needed to feel a slider move.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_JawaRulesSettings : ModSettings
    {
        public static bool sowBanEnabled = true;
        public static bool droidRelationsEnabled = true;
        public static bool petNamesEnabled = true;

        // KCSG_PAWNKIND_COLONIST_FALLBACK_1: PawnGenerator's world-pawn redress path
        // (GenerateOrRedressPawnInternal -> RedressPawn) is SUPPOSED to force the
        // redressed pawn onto the requested kind via pawn.ChangeKind(request.KindDef)
        // (Verse/Pawn.cs:6094), but AlienRace.HarmonyPatches.ChangeKindPrefix
        // (HumanoidAlienRaces) can skip that original call, leaving a recycled world
        // pawn (usually vanilla Colonist, xenotype Baseliner) standing in for one of
        // our useFactionXenotypes kinds. Reaches every caller of
        // PawnGenerator.GeneratePawn(kind, faction) with forceGenerateNewPawn left
        // false — raids, quests, faction rosters and KCSG dungeon layouts alike.
        public static bool pawnKindRedressFixEnabled = true;

        // JAWA_SWIM_HOOD_KEEP_1: keep the worn Jawa hood drawn while swimming
        // (Patch_ApparelHead_CanDrawNow_SwimHood). Read every frame; no restart.
        public static bool swimHoodEnabled = true;

        public static bool worldLabelAlphaBoostEnabled = true;
        public static float worldLabelAlpha = 0.6f;
        public static bool worldLabelLiftEnabled = true;
        public static float worldLabelLift = 1.5f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sowBanEnabled, "sowBanEnabled", true);
            Scribe_Values.Look(ref droidRelationsEnabled, "droidRelationsEnabled", true);
            Scribe_Values.Look(ref petNamesEnabled, "petNamesEnabled", true);
            Scribe_Values.Look(ref pawnKindRedressFixEnabled, "pawnKindRedressFixEnabled", true);
            Scribe_Values.Look(ref swimHoodEnabled, "swimHoodEnabled", true);
            Scribe_Values.Look(ref worldLabelAlphaBoostEnabled, "worldLabelAlphaBoostEnabled", true);
            Scribe_Values.Look(ref worldLabelAlpha, "worldLabelAlpha", 0.6f);
            Scribe_Values.Look(ref worldLabelLiftEnabled, "worldLabelLiftEnabled", true);
            Scribe_Values.Look(ref worldLabelLift, "worldLabelLift", 1.5f);
        }

        /// <summary>Called by the transpiled WorldFeatures.UpdateAlpha in place of its old 0.3 literal.</summary>
        public static float CurrentWorldLabelAlpha()
        {
            return RSW_RulesKernel.Current(worldLabelAlphaBoostEnabled, worldLabelAlpha, Patch_WorldFeatures_UpdateAlpha.VanillaAlpha);
        }

        /// <summary>Called by the transpiled WrapAroundPlanetSurface in place of its old 0.4 literal.</summary>
        public static float CurrentWorldLabelLift()
        {
            return RSW_RulesKernel.Current(worldLabelLiftEnabled, worldLabelLift, Patch_WorldFeatureText_Lift.VanillaLift);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_JawaRulesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_JawaRulesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or a save loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Colony rules", RimMandrake.Shared.SettingScope.Now, new[] { "sowBanEnabled", "swimHoodEnabled" }))
            {
                list.CheckboxLabeled("Jawa may not sow", ref sowBanEnabled,
                    "Jawa colonists skip planting in grow zones and hydroponics basins (they still "
                  + "harvest, cut plants and chop trees). Off: they sow like anyone else.");
                list.CheckboxLabeled("Jawa keep their hood while swimming", ref swimHoodEnabled,
                    "Vanilla hides all clothing and headgear on a swimming pawn. On: a worn Jawa "
                  + "hood stays drawn on the swimmer's head. Off: vanilla, and the smaller "
                  + "built-in fallback hood shows instead.");
                list.GapLine();
            }

            if (Group(list, "Pawn and animal generation fixes", RimMandrake.Shared.SettingScope.NextPulse, new[] { "droidRelationsEnabled", "petNamesEnabled", "pawnKindRedressFixEnabled" }))
            {
                list.CheckboxLabeled("Humanlike droids get a relations tracker", ref droidRelationsEnabled,
                    "Fixes a vanilla gap where humanlike droid races generate with no relations "
                  + "tracker and anything reaching for it throws. Off: droids generate exactly as "
                  + "they did before this mod.");
                list.CheckboxLabeled("Tamed/newborn animals draw names from their race", ref petNamesEnabled,
                    "Off: animals fall back to vanilla's numeric names (\"Dromedary 1\") instead of "
                  + "their race's name generator.");
                list.CheckboxLabeled("Fix recycled-pawn kind mismatches", ref pawnKindRedressFixEnabled,
                    "KCSG_PAWNKIND_COLONIST_FALLBACK_1: RimWorld can silently hand back a recycled "
                  + "world pawn (usually a vanilla Colonist/Baseliner) instead of the pawn kind a "
                  + "raid, quest, faction or dungeon layout asked for, when a Humanoid Alien Races "
                  + "compatibility patch blocks the engine's own kind correction. Off: vanilla "
                  + "behaviour, including the mismatch.");
                list.GapLine();
            }

            if (Group(list, "World map labels", RimMandrake.Shared.SettingScope.Now, new[] { "worldLabelAlphaBoostEnabled", "worldLabelAlpha", "worldLabelLiftEnabled", "worldLabelLift" }))
            {
                list.CheckboxLabeled("Boost world feature label opacity", ref worldLabelAlphaBoostEnabled,
                    "The italic region/sea/range names printed on the planet map. Off: vanilla's "
                  + "faint 0.30 opacity.");
                list.Label("  Label opacity: " + worldLabelAlpha.ToString("0.00"));
                worldLabelAlpha = list.Slider(worldLabelAlpha, 0.3f, 1f);
                list.CheckboxLabeled("Lift world feature labels off the surface", ref worldLabelLiftEnabled,
                    "Off: labels sit at vanilla's 0.4 height above the terrain, which can clip into it.");
                list.Label("  Label height: " + worldLabelLift.ToString("0.00"));
                worldLabelLift = list.Slider(worldLabelLift, 0.4f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_JawaRulesMod : Mod
    {
        public static RSW_JawaRulesSettings settings;

        public RSW_JawaRulesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_JawaRulesSettings>();

            // FULL_LOAD_ALPHAGENES_NRE_1 — MUST fire from this constructor, not from
            // JawaRulesMod's [StaticConstructorOnStartup] static ctor: Mod subclass
            // constructors run during LoadedModManager.CreateModClasses(), before
            // RimWorld.DefGenerator.GenerateImpliedDefs_PreResolve() — the earliest
            // point a Harmony patch can be armed and still be in place for it. See
            // JawaRulesMod.ArmEarlyGuards() and Patch_PawnKindDef_RaceProps_NullGuard
            // in JawaRules.cs for the full root-cause account.
            JawaRulesMod.ArmEarlyGuards();
        }

        public override string SettingsCategory()
        {
            return "Jawa Rules";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
