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
    }
}
