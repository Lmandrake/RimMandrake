using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_GASLIGHT_1 (item spec §2). The mechanism, sibling to
    // RM_CompProperties_WarblingGlow's own header. Reads the sibling
    // CompGlower's OWN Props.glowColor/glowRadius as the center it warbles
    // around (never a hardcoded color), so the same comp drives both the
    // lamp (piece 3) and the statue (piece 4, via qualityScalingEnabled)
    // with no duplicated animation code.
    //
    // Verified against Verse/CompGlower.cs and Verse/GlowGrid.cs (both read
    // in full this pass): GlowColor's setter (SetGlowColorInternal)
    // de-registers/re-registers the glower itself, so assigning it is
    // sufficient; GlowRadius's setter only stores the override and does
    // NOT re-register — the radius goes through the light ledger
    // (LIGHT_LEDGER_ONE_1), which re-registers a lit lamp on a real change.
    public class RM_Comp_WarblingGlow : ThingComp
    {
        // Per-instance tick offset so multiple lamps/statues on one map
        // don't all pulse in lockstep — re-rolled on every spawn/load
        // (cosmetic only; not worth a Scribe entry).
        private int phaseOffset;

        // WARBLING_GLOW_BASELINE_1: the colour the lamp had before we first touched it (a player-picked colour
        // survives), scribed as four ints so a save made mid-warble reloads around the same centre.
        private bool hasBaseline;
        private int baseR, baseG, baseB, baseA;

        private CompGlower glowerCache;
        private CompQuality qualityCache;
        private bool cachedSiblingComps;

        public RM_CompProperties_WarblingGlow Props => (RM_CompProperties_WarblingGlow)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            phaseOffset = Rand.Range(0, 100000);
            cachedSiblingComps = false;
        }

        private void EnsureSiblingComps()
        {
            if (cachedSiblingComps)
            {
                return;
            }

            glowerCache = parent.GetComp<CompGlower>();
            qualityCache = parent.GetComp<CompQuality>();
            cachedSiblingComps = true;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref hasBaseline, "warbleHasBaseline", false);
            Scribe_Values.Look(ref baseR, "warbleBaseR", 0);
            Scribe_Values.Look(ref baseG, "warbleBaseG", 0);
            Scribe_Values.Look(ref baseB, "warbleBaseB", 0);
            Scribe_Values.Look(ref baseA, "warbleBaseA", 255);
        }

        private const string WarbleOwner = "eh.warble";

        public override void CompTick()
        {
            if (!RM_EnvironmentalHazardsSettings.warblingGlowEnabled)
            {
                // mod option: warbling gaslight animation disabled — let go of the pulse once
                EnsureSiblingComps();
                if (glowerCache != null && parent.IsHashIntervalTick(250))
                {
                    LightLedger.ClearMul(glowerCache, WarbleOwner);
                    if (hasBaseline)
                    {
                        glowerCache.GlowColor = new ColorInt(baseR, baseG, baseB, baseA); // put the colour back where we found it
                        hasBaseline = false;
                    }
                }
                return;
            }

            EnsureSiblingComps();
            if (glowerCache == null || !parent.Spawned)
            {
                return;
            }

            RM_CompProperties_WarblingGlow p = Props;
            int interval = Mathf.Max(1, p.updateIntervalTicks);
            if (!parent.IsHashIntervalTick(interval))
            {
                return;
            }

            Apply(p);
        }

        private void Apply(RM_CompProperties_WarblingGlow p)
        {
            CompProperties_Glower glowProps = glowerCache.Props;
            if (glowProps == null)
            {
                return;
            }

            float speed = Mathf.Max(0.05f, RM_EnvironmentalHazardsSettings.warblingGlowSpeedMultiplier);
            float t = (Find.TickManager.TicksGame + phaseOffset) * speed;

            float wavePrimary = Mathf.Sin(2f * Mathf.PI * t / Mathf.Max(1, p.primaryPeriodTicks));
            float waveSecondary = Mathf.Sin(2f * Mathf.PI * t / Mathf.Max(1, p.secondaryPeriodTicks));

            float qualityScale = 1f;
            if (p.qualityScalingEnabled)
            {
                EnsureSiblingComps();
                if (qualityCache != null)
                {
                    qualityScale = QualityScaleFor(qualityCache.Quality);
                }
            }

            // Color: base hue wanders +/- hueRangeDegrees on wavePrimary,
            // brightness pulses +/- valuePulseFraction on the SAME wave so
            // the color and the "breathing" brightness read as one motion.
            if (!hasBaseline)
            {
                ColorInt now = glowerCache.GlowColor;
                baseR = now.r; baseG = now.g; baseB = now.b; baseA = now.a;
                hasBaseline = true;
            }
            Color baseColor = new ColorInt(baseR, baseG, baseB, baseA).ToColor;
            Color.RGBToHSV(baseColor, out float h, out float s, out float v);
            h = Mathf.Repeat(h + wavePrimary * (p.hueRangeDegrees / 360f), 1f);
            v = Mathf.Clamp01(v + wavePrimary * p.valuePulseFraction * qualityScale);
            Color newColor = Color.HSVToRGB(h, s, v);
            newColor.a = 1f;

            // Radius: driven by the SECOND wave (different period) so the
            // light doesn't just get brighter and bigger in lockstep — it
            // dances rather than simply breathing. LIGHT_LEDGER_ONE_1: a
            // multiplier in the light ledger around whatever else sizes this
            // lamp (the Dark, the aurora, a sipper), never a write over them.
            LightLedger.SetMul(glowerCache, WarbleOwner,
                Mathf.Max(0.05f, 1f + waveSecondary * p.radiusPulseFraction * qualityScale));

            // Radius first (the ledger re-registers only a LIT lamp), then
            // colour: CompGlower's GlowColor setter de/re-registers the glower
            // once, and only while it should be lit. A trailing ForceRegister
            // registered a second time per update and re-lit an unpowered or
            // flicked-off lamp.
            glowerCache.GlowColor = new ColorInt(newColor);
        }

        // Awful..Legendary -> 0.5x..2x, applied to both pulse fractions
        // (item spec §4, "flame display scales with art quality"). Deliberately
        // NOT applied to the mean radius/color (the sibling CompGlower's own
        // base values do that job) — this only scales how much the flame
        // DANCES, so a masterwork statue's flame is livelier, not merely bigger.
        private static float QualityScaleFor(QualityCategory q)
        {
            switch (q)
            {
                case QualityCategory.Awful:
                    return 0.5f;
                case QualityCategory.Poor:
                    return 0.7f;
                case QualityCategory.Normal:
                    return 1f;
                case QualityCategory.Good:
                    return 1.2f;
                case QualityCategory.Excellent:
                    return 1.4f;
                case QualityCategory.Masterwork:
                    return 1.7f;
                case QualityCategory.Legendary:
                    return 2f;
                default:
                    return 1f;
            }
        }
    }
}
