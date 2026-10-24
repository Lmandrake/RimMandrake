// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 2 -- a scheme is DATA (spec §2.3): the four axes the owner named, as a Def,
// so an XML-only mod can add one (the def door, §2.8, is Phase 8; the data shape is fixed here). Validated by the pure
// kernel, so a malformed scheme is a red config error at load and never reaches a fixture.
// Palette entries parse through ParseHelper.ParseColorInt, the same "(r,g,b,a)" form CompProperties_Glower.glowColor uses.
using System.Collections.Generic;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_AtmosphericSchemeDef : Def
    {
        public List<ColorInt> palette = new List<ColorInt>();
        public RM_PatternKind pattern = RM_PatternKind.Steady;
        public float massPeriodSeconds = 120f;
        public float sparkSeconds = 2f;
        public int sparkOneIn = 2;
        public bool mayGoDark;
        public int flasherCount;
        public float flasherPeriodSeconds;
        // The pattern grammar (design atmospheric_base_god_patterns_2026-10-24.md §4): a stack of primitives, bottom first.
        // Absent = the old one-pattern form above, run as one layer. Present but empty is a config error.
        public List<RM_Layer> layers;
        public float scarLinger;        // M3 SCAR (RM_PatternModifiers.cs RM_Scar): 0 = off
        public bool scarKeeps;

        [Unsaved] private RM_SchemeData? data;

        public RM_SchemeData Data
        {
            get
            {
                if (data == null)
                {
                    int n = palette?.Count ?? 0;
                    var d = new RM_SchemeData
                    {
                        r = new int[n], g = new int[n], b = new int[n],
                        pattern = pattern, massPeriodSeconds = massPeriodSeconds, sparkSeconds = sparkSeconds,
                        sparkOneIn = sparkOneIn, mayGoDark = mayGoDark, flasherCount = flasherCount,
                        flasherPeriodSeconds = flasherPeriodSeconds,
                        layers = layers?.ToArray(), scarLinger = scarLinger, scarKeeps = scarKeeps,
                    };
                    for (int i = 0; i < n; i++) { d.r[i] = palette[i].r; d.g[i] = palette[i].g; d.b[i] = palette[i].b; }
                    if (d.layers == null) d.legacy = RM_PatternKernel.LegacyLayers(d);
                    data = d;
                }
                return data.Value;
            }
        }

        public bool Valid => RM_SchemeKernel.Errors(Data).Count == 0;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            foreach (string e in RM_SchemeKernel.Errors(Data)) yield return e;
        }
    }
}
