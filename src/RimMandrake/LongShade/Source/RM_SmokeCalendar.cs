using RimWorld;
using Verse;

namespace RimMandrake.LongShade
{
    /// <summary>
    /// LONGSHADE_BEDAZZLE_MECHANICS_1 smoke calendar (design long_shade_bedazzle_2026-09-27.md 4.2):
    /// "Then the ash settles". Carried on RM_SmokeHazeCondition: when the haze ends, the ash act
    /// starts on the same map, an ash-pulse growth surge and a sand-lock that outlasts it ("until
    /// the wind unpacks it"). All numbers live on the def and are PROVISIONAL.
    /// </summary>
    public class RM_SmokeCalendarExtension : DefModExtension
    {
        public GameConditionDef ashPulseCondition;
        public FloatRange ashPulseDays = new FloatRange(3f, 5f);
        public GameConditionDef sandLockCondition;
        public FloatRange sandLockDays = new FloatRange(4f, 7f);
    }

    /// <summary>The haze act's condition class: on End() it starts the ash act (each half behind its own toggle).</summary>
    public class RM_GameCondition_SmokeHaze : GameCondition
    {
        public override void End()
        {
            Map map = gameConditionManager?.ownerMap;
            base.End();
            RM_SmokeCalendar.StartAshAct(map, def.GetModExtension<RM_SmokeCalendarExtension>());
        }
    }

    public static class RM_SmokeCalendar
    {
        /// <summary>True if the ash act should start: mod on, Long Shade map, extension present, at least one half enabled.</summary>
        public static bool AshActAllowed(Map map, RM_SmokeCalendarExtension ext)
        {
            return map != null && ext != null && RM_LongShadeSettings.modEnabled
                && RM_ShadeExtrasTuning.OnLongShade(map)
                && (RM_LongShadeSettings.ashPulseEnabled || RM_LongShadeSettings.sandLockEnabled);
        }

        public static void StartAshAct(Map map, RM_SmokeCalendarExtension ext)
        {
            if (!AshActAllowed(map, ext))
            {
                return;
            }
            GameConditionManager mgr = map.gameConditionManager;
            GameConditionDef shown = null;
            if (RM_LongShadeSettings.ashPulseEnabled && ext.ashPulseCondition != null
                && !mgr.ConditionIsActive(ext.ashPulseCondition))
            {
                mgr.RegisterCondition(GameConditionMaker.MakeCondition(ext.ashPulseCondition,
                    (int)(ext.ashPulseDays.RandomInRange * GenDate.TicksPerDay)));
                shown = ext.ashPulseCondition;
            }
            if (RM_LongShadeSettings.sandLockEnabled && ext.sandLockCondition != null
                && !mgr.ConditionIsActive(ext.sandLockCondition))
            {
                mgr.RegisterCondition(GameConditionMaker.MakeCondition(ext.sandLockCondition,
                    (int)(ext.sandLockDays.RandomInRange * GenDate.TicksPerDay)));
                shown = shown ?? ext.sandLockCondition;
            }
            if (shown != null)
            {
                Find.LetterStack.ReceiveLetter("Ash settles", shown.letterText ?? shown.description,
                    LetterDefOf.NeutralEvent);
            }
        }
    }
}
