using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_GPT_ENRICHMENT_1 §3 — "heat you can hear".
    //
    // Lit ground and shade sound different, and the line between them is
    // what the player hears. Owner, typed on the 2026-09-30 card: "It's ok
    // for the heat sound to be where the camera is rather than your people."
    // So the bed keys off the CAMERA's cell, never a pawn's: the exposure the
    // sun-heat grid reports there (RM_MapComponent_ShadeGrid.ExposureAt,
    // which already folds in roofs, cast shade, gear and moving shade) picks
    // the lit bed or the shade bed.
    //
    // Three pieces, one setting family:
    //   • the camera bed (RM_MapComponent_HeatSoundscape), data on the biome
    //     (RM_HeatSoundscapeExtension);
    //   • a herd animal calls at the rim before it dashes (RM_ShadeHop's
    //     pause toil calls TryHerdCall) — the animal's own vanilla call;
    //   • a giant's footfalls carry further than it can be seen
    //     (RM_CompFootfalls on the gloomcast).
    // "Haze muffles everything" waits on the smoke calendar, which is not
    // built (LONGSHADE_BEDAZZLE_MECHANICS_1); it is a follow-up, not here.
    //
    // Sustainers are OnCamera / PerTick and MAINTAINED every tick here: an
    // unmaintained PerTick sustainer ends itself two ticks later (decompiled
    // 1.6 Sustainer.SustainerUpdate). There is no partial volume ramp on a
    // live sustainer, so a switch ends one bed and starts the other; the
    // minimum switch interval keeps a camera resting on a shadow's edge
    // from flickering.
    // ════════════════════════════════════════════════════════════════════
    public class RM_HeatSoundscapeExtension : DefModExtension
    {
        /// <summary>The bed while the camera looks at sunlit ground.</summary>
        public SoundDef litSound;

        /// <summary>The bed while the camera looks at shade.</summary>
        public SoundDef shadeSound;

        /// <summary>Exposure (0..1) at or above which the camera's cell
        /// counts as lit. TUNED: 0.5, the midpoint — no ruling sets it.</summary>
        public float litExposureAbove = 0.5f;

        /// <summary>Hysteresis: the bed may change at most this often.
        /// TUNED: 120 ticks (2 s).</summary>
        public int minSwitchTicks = 120;

        /// <summary>Chance a herd animal calls at the rim before a dash.
        /// TUNED: 0.5, so a herd's crossing is heard without every member
        /// calling at once.</summary>
        public float herdCallChance = 0.5f;

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (litSound == null && shadeSound == null)
            {
                yield return "RM_HeatSoundscapeExtension names neither litSound nor shadeSound.";
            }
            if (litSound != null && !litSound.sustain)
            {
                yield return "RM_HeatSoundscapeExtension litSound " + litSound.defName + " is not a sustainer.";
            }
            if (shadeSound != null && !shadeSound.sustain)
            {
                yield return "RM_HeatSoundscapeExtension shadeSound " + shadeSound.defName + " is not a sustainer.";
            }
        }
    }

    public class RM_MapComponent_HeatSoundscape : MapComponent
    {
        private const int CheckIntervalTicks = 30;

        private Sustainer sustainer;
        private SoundDef playing;
        private float playingVolume = -1f;
        private int lastSwitchTick = -999999;

        public RM_MapComponent_HeatSoundscape(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (sustainer != null && !sustainer.Ended)
            {
                sustainer.Maintain();
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            SoundDef want = Wanted(out RM_HeatSoundscapeExtension ext);
            float vol = RM_CreatureBehaviorsSettings.heatSoundscapeVolume * RM_ShadeHaze.SoundVolumeFactor(map);
            if (want == playing && sustainer != null && !sustainer.Ended && vol == playingVolume)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (want != null && playing != null && want != playing && ext != null
                && now - lastSwitchTick < ext.minSwitchTicks)
            {
                return;
            }
            End();
            if (want != null && vol > 0f)
            {
                SoundInfo info = SoundInfo.OnCamera(MaintenanceType.PerTick);
                info.volumeFactor = vol;
                sustainer = want.TrySpawnSustainer(info);
                playing = want;
                playingVolume = vol;
                lastSwitchTick = now;
            }
        }

        /// <summary>The bed the camera's cell calls for, or null.</summary>
        private SoundDef Wanted(out RM_HeatSoundscapeExtension ext)
        {
            ext = map.Biome?.GetModExtension<RM_HeatSoundscapeExtension>();
            if (ext == null || !RM_CreatureBehaviorsSettings.heatSoundscapeEnabled || Find.CurrentMap != map)
            {
                return null;
            }
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            CameraDriver cam = Find.CameraDriver;
            if (grid == null || !grid.SunHeatActive || cam == null)
            {
                return null;
            }
            IntVec3 cell = cam.MapPosition;
            if (!cell.IsValid || !cell.InBounds(map))
            {
                return null;
            }
            return grid.ExposureAt(cell) >= ext.litExposureAbove ? ext.litSound : ext.shadeSound;
        }

        private void End()
        {
            if (sustainer != null && !sustainer.Ended)
            {
                sustainer.End();
            }
            sustainer = null;
            playing = null;
            playingVolume = -1f;
        }

        public override void MapRemoved()
        {
            End();
            base.MapRemoved();
        }
    }

    public static class RM_HeatSoundscape
    {
        /// <summary>RM_ShadeHop's rim pause: a herd animal may call before
        /// it dashes. Its own vanilla life-stage call, nothing invented.</summary>
        public static void TryHerdCall(Pawn pawn)
        {
            if (!RM_CreatureBehaviorsSettings.creatureHeatSoundsEnabled || pawn?.Map == null
                || pawn.RaceProps == null || !pawn.RaceProps.herdAnimal)
            {
                return;
            }
            RM_HeatSoundscapeExtension ext = pawn.Map.Biome?.GetModExtension<RM_HeatSoundscapeExtension>();
            if (ext == null || !Rand.Chance(ext.herdCallChance))
            {
                return;
            }
            LifeStageUtility.PlayNearestLifestageSound(pawn, ls => ls.soundCall, null, null);
        }
    }

    /// <summary>A heavy creature's footfalls, played at its body while it
    /// walks. A map sound with a wide distRange is heard before the creature
    /// comes on screen — the gloomcast's "footfalls heard before it is seen".</summary>
    public class RM_CompProperties_Footfalls : CompProperties
    {
        public SoundDef sound;

        /// <summary>Ticks between footfalls while moving. TUNED per creature.</summary>
        public int intervalTicks = 90;

        public RM_CompProperties_Footfalls()
        {
            compClass = typeof(RM_CompFootfalls);
        }

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (sound == null)
            {
                yield return "RM_CompProperties_Footfalls has no sound.";
            }
            if (intervalTicks < 1)
            {
                yield return "RM_CompProperties_Footfalls intervalTicks must be >= 1.";
            }
        }
    }

    public class RM_CompFootfalls : ThingComp
    {
        public RM_CompProperties_Footfalls Props => (RM_CompProperties_Footfalls)props;

        public override void CompTick()
        {
            base.CompTick();
            if (!RM_CreatureBehaviorsSettings.creatureHeatSoundsEnabled || !parent.IsHashIntervalTick(Props.intervalTicks))
            {
                return;
            }
            if (parent is Pawn pawn && pawn.Spawned && !pawn.Dead && pawn.pather != null && pawn.pather.Moving)
            {
                Props.sound?.PlayOneShot(new TargetInfo(pawn.Position, pawn.Map));
            }
        }
    }
}
