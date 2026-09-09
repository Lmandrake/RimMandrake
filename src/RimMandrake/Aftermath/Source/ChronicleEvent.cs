using System.Collections.Generic;
using Verse;

namespace RimMandrake.Aftermath
{
    // design/CHRONICLE_EVENT_SPINE.md's event row, verbatim on field names
    // and types. This engine (RimChronicle, still folder/namespace-named
    // Aftermath until the gated rename row lands) is the shared event spine
    // of the RM engine suite; a consumer reads THESE flat fields by
    // reflection, or downcasts Payload if it chose a compile-time reference.
    //
    // In-memory only, not IExposable -- the same documented limitation
    // BattleRecord carries: an event open at save time is not resumed.
    //
    // Field NAMES are a reflection contract. A consumer with no assembly
    // reference to this mod binds to them by string (see
    // src/RimMandrake/Ninefold/Source/ChronicleSubscriber.cs); renaming one
    // silently unbinds every such consumer with no compile error anywhere.
    public class ChronicleEvent
    {
        // Spine kind. v1 kinds are the constants on ChronicleEventKind.
        public readonly string Kind;

        public readonly int Tick;
        public readonly Map Map;

        // Pawns this event is about -- for a battle, the raid's original
        // pawns. Never null (empty list instead), so a consumer need not
        // null-guard before enumerating.
        public readonly List<Pawn> Actors;

        // The thing this event is about, when there is one (property
        // takings); null for battle-scoped kinds.
        public readonly Thing Thing;

        // Kind-specific outcome name -- for battle.closed, the BattleOutcome
        // enum's name. String rather than the enum so a consumer needs no
        // compile-time reference to read it.
        public readonly string Outcome;

        // The rich record behind the event (a BattleRecord, an
        // RM_AftermathRuleDef, ...). Typed as object precisely so a
        // reflection consumer can carry it without naming its type.
        public readonly object Payload;

        public ChronicleEvent(string kind, int tick, Map map, List<Pawn> actors,
                              Thing thing, string outcome, object payload)
        {
            Kind = kind;
            Tick = tick;
            Map = map;
            Actors = actors ?? new List<Pawn>();
            Thing = thing;
            Outcome = outcome;
            Payload = payload;
        }
    }

    // The kind strings, in one place so the producer side never spells one
    // by hand. Consumers bind to the literal value, not to this class.
    public static class ChronicleEventKind
    {
        // A raid the recorder was tracking has finished and been classified.
        // Payload: the BattleRecord. Outcome: the BattleOutcome name.
        public const string BattleClosed = "battle.closed";

        // An RM_AftermathRuleDef matched a closed battle and its payload
        // incident has just been queued. Payload: the RM_AftermathRuleDef
        // (carrying godTie/godDelta as plain data). Outcome: the triggering
        // battle's outcome name.
        public const string RuleQueued = "chronicle.rule.queued";
    }
}
