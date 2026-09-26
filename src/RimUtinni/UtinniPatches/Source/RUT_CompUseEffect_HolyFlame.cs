using RimWorld;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
    // SUMP_UTINNI_LAYER_1 §2 — "the holy act": a colonist who Uses a flame
    // statue (CompUsable, vanilla; RUT_PerformHolyFlameAct/JobDriver_UseItem
    // does the walk-and-wait) performs the sun-rite. This CompUseEffect fires
    // a SCOPED HistoryEventDef so only this specific interaction — never
    // generic art admiration, never any other building's construction or use
    // — can grant the RUT_HolyFlame_Revered precept its memory thought.
    //
    // Investigated before writing, not guessed: HistoryEventDefOf.cs
    // (decompiled Assembly-CSharp) has no "admired art" event in this game
    // version at all, and PreceptComp_SelfTookMemoryThought.
    // Notify_MemberTookAction (read in full) filters only on `ev.def ==
    // eventDef` with no per-ThingDef check on the event's own args — so
    // reusing HistoryEventDefOf.BuildSpecificDef (fires on ANY construction,
    // GenConstruct.cs) would have granted the thought for building anything at
    // all. Hence a dedicated event, fired only from here.
    //
    // eventDefName is a plain string, resolved via GetNamedSilentFail rather
    // than a typed HistoryEventDef field or a [DefOf]: RUT_PerformedHolyFlameAct
    // is MayRequire="Ludeon.RimWorld.Ideology", so this comp (which lives in
    // UtinniPatches, an Ideology-agnostic mod) must degrade to a harmless no-op
    // rather than a hard XML cross-reference failure if Ideology is ever
    // absent from the active mod list.
    public class RUT_CompProperties_HolyFlameEffect : CompProperties_UseEffect
    {
        public string eventDefName;

        public RUT_CompProperties_HolyFlameEffect()
        {
            compClass = typeof(RUT_CompUseEffect_HolyFlame);
        }
    }

    public class RUT_CompUseEffect_HolyFlame : CompUseEffect
    {
        private RUT_CompProperties_HolyFlameEffect Props => (RUT_CompProperties_HolyFlameEffect)props;

        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);

            HistoryEventDef eventDef = DefDatabase<HistoryEventDef>.GetNamedSilentFail(Props.eventDefName);
            if (eventDef != null)
            {
                Find.HistoryEventsManager.RecordEvent(new HistoryEvent(eventDef, usedBy.Named(HistoryEventArgsNames.Doer)));
            }
        }
    }
}
