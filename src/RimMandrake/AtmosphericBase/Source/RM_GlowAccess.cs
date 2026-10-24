// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- reading, driving and restoring a CompGlower's COLOUR exactly.
//
// "Exactly" means the comp's own override field, not the effective colour: CompGlower (Verse/CompGlower.cs, RimSage
// 1.6 decompile) holds `private ColorInt? glowColorOverride`, and GlowColor reads `override ?? Props.glowColor`.
// Writing the effective value back would leave an override where there was none, so a later def or colour-picker
// change would no longer show through. So the snapshot keeps HasValue too.
//
// Colour is written through `protected virtual SetGlowColorInternal(ColorInt?)` -- the path the vanilla colour picker
// and darklight toggle use: DeRegisterGlower / write / RegisterGlower only while ShouldBeLitNow, so an unlit or
// unspawned fixture is just written. It is the only way to restore a NULL override (the public setter takes a ColorInt).
//
// 🔴 RADIUS IS NOT OURS. Every radius write in this repo goes through src/RimMandrake/_Shared/LightLedger
// (LIGHT_LEDGER_ONE_1: ten direct writers in five mods kept undoing each other's dimming), and
// selftest_lightledger.py refuses a `GlowRadius =` anywhere else. Phase 1 never touches radius, so release returns
// the radius by construction and a ledger owner's dimming made while the lamp was held survives the release. When
// brightness is driven (Phase 2) it is ONE ledger modifier, `atmosphericbase.brightness`, cleared on release --
// never a snapshot of the radius written back, which would erase every other owner's effect.
// No Harmony: plain System.Reflection over two members, resolved once and checked by Bound.
using System;
using System.Reflection;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_GlowSnapshot : IExposable
    {
        public bool hadColor;
        public ColorInt color;

        public void ExposeData()
        {
            Scribe_Values.Look(ref hadColor, "hadColor", false);
            Scribe_Values.Look(ref color, "color", default(ColorInt));
        }

        public bool SameAs(RM_GlowSnapshot o)
        {
            return o != null && hadColor == o.hadColor && (!hadColor || color == o.color);
        }

        public override string ToString()
        {
            return "color=" + (hadColor ? color.ToString() : "none");
        }

        public static RM_GlowSnapshot Of(ColorInt? c) => new RM_GlowSnapshot { hadColor = c.HasValue, color = c ?? default(ColorInt) };

        public RM_GlowSnapshot Copy() => new RM_GlowSnapshot { hadColor = hadColor, color = color };
    }

    /// <summary>What can happen to a held lamp that is not the framework's own doing (owner decisions §9.6 and §9.9,
    /// 2026-10-23).</summary>
    public enum RM_HeldLampEvent
    {
        /// <summary>The player flicked it off (CompFlickable) -- L17: silent. It stays held, it is simply unlit (L9).</summary>
        SwitchedOffByHand,
        /// <summary>Another mod or the player changed its colour while it was held: "It is released. In Utinni this
        /// displeases gods." The lamp is released with THEIR colour kept (the saved colour is never written over it).</summary>
        ColourEditedExternally,
    }

    /// <summary>Pure policy for held lamps; compiled into the offline selftest.</summary>
    public static class RM_HeldLampPolicy
    {
        /// <summary>True when the override the fixture holds now is not what the framework last left there: someone
        /// else wrote it. `lastLeft` null means the framework does not yet know (a save from before this rule), never an
        /// edit.</summary>
        public static bool EditedExternally(RM_GlowSnapshot now, RM_GlowSnapshot lastLeft)
        {
            return now != null && lastLeft != null && !now.SameAs(lastLeft);
        }

        /// <summary>Does the framework release the lamp on this event?</summary>
        public static bool Releases(RM_HeldLampEvent e) => e == RM_HeldLampEvent.ColourEditedExternally;

        /// <summary>Does this event displease the gods? Only an external colour edit, and only aboard the Utinni (the
        /// map whose scenario decides, RM_AtmosphericBaseAPI.SetScenarioDecides). A hand switch-off never does (L17).
        /// AtmosphericBase only REPORTS it (RM_AtmosphericBaseAPI.LampEditedAboardUtinni); it never acts on anger (L2).</summary>
        public static bool DispleasesGods(RM_HeldLampEvent e, bool aboardUtinni)
        {
            return aboardUtinni && e == RM_HeldLampEvent.ColourEditedExternally;
        }
    }

    public static class RM_GlowAccess
    {
        private const BindingFlags Inst = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;

        private static readonly FieldInfo ColorField = typeof(CompGlower).GetField("glowColorOverride", Inst);
        private static readonly MethodInfo SetColorInternal = typeof(CompGlower).GetMethod(
            "SetGlowColorInternal", Inst, null, new[] { typeof(ColorInt?) }, null);

        /// <summary>Both members resolved with the expected types. False means the game's CompGlower changed shape
        /// and the take-over must refuse rather than guess.</summary>
        public static bool Bound =>
            ColorField != null && ColorField.FieldType == typeof(ColorInt?)
            && SetColorInternal != null;

        public static RM_GlowSnapshot Snapshot(CompGlower g)
        {
            var c = (ColorInt?)ColorField.GetValue(g);
            return new RM_GlowSnapshot
            {
                hadColor = c.HasValue,
                color = c ?? default(ColorInt),
            };
        }

        /// <summary>SELFTEST SEAM ONLY, null in game. CompGlower.ShouldBeLitNow names IThingGlower, an interface with a
        /// default method, which a plain .NET Framework console process refuses to load (TypeLoadException "Non-abstract,
        /// non-.cctor method in an interface"); Unity's Mono loads it. So the offline selftest swaps in a field-only
        /// writer and the regrid path (SetGlowColorInternal) is proven only by the live proof. validation.py refuses any
        /// assignment to this outside Source/SelfTest.</summary>
        internal static Action<CompGlower, ColorInt?> ColorWriterForSelfTest;

        internal static void WriteColorFieldOnly(CompGlower g, ColorInt? color)
        {
            ColorField.SetValue(g, color);
        }

        public static void WriteColor(CompGlower g, ColorInt? color)
        {
            if (ColorWriterForSelfTest != null) { ColorWriterForSelfTest(g, color); return; }
            SetColorInternal.Invoke(g, new object[] { color });
        }

        public static void Restore(CompGlower g, RM_GlowSnapshot s)
        {
            WriteColor(g, s.hadColor ? s.color : (ColorInt?)null);
        }

        /// <summary>Restore the override field WITHOUT the regrid, for a fixture whose map is being removed (Phase 2,
        /// MapRemoved): no glow grid may be touched then, and an unspawned fixture is registered nowhere.</summary>
        public static void RestoreFieldOnly(CompGlower g, RM_GlowSnapshot s)
        {
            WriteColorFieldOnly(g, s.hadColor ? s.color : (ColorInt?)null);
        }
    }
}
