using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Ninefold
{
    // CHRONICLE_NINEFOLD_DECOUPLE_1 / design/CHRONICLE_EVENT_SPINE.md: this
    // engine's half of the battle wiring. The Chronicle engine (shipped today
    // as mandrake.rm.aftermath) publishes a closed battle on its static
    // ChronicleEvents spine; we subscribe and apply OUR god-deltas here. The
    // engine has no compile-time knowledge of Ninefold and Ninefold has no
    // compile-time knowledge of the engine -- soft-hook law 2 and 3 in the
    // spine spec forbid a <Reference> in EITHER direction between engines, so
    // the whole binding is AccessTools.TypeByName + null guards.
    //
    // Two kinds are consumed:
    //   "battle.closed"          -> the PER-BATTLE Sh'kaar delta that used to
    //                               live in the recorder's ApplyNinefoldDelta.
    //                               Reconciles with, does not duplicate,
    //                               Patch_BattleResolved's PER-DEATH hook.
    //   "chronicle.rule.queued"  -> an aftermath rule's godTie/godDelta, now
    //                               carried as a plain string + float on the
    //                               rule def instead of our God enum.
    //
    // If the Chronicle engine is not loaded, TypeByName returns null and this
    // whole file does nothing: Ninefold still ships standalone.
    [StaticConstructorOnStartup]
    public static class ChronicleSubscriber
    {
        // Post-rename name first, current name second. The Aftermath ->
        // RimChronicle rename is a separate gated row; probing both means the
        // rename does not have to land in the same commit as this file.
        private static readonly string[] EventsTypeNames =
        {
            "RimMandrake.Chronicle.ChronicleEvents",
            "RimMandrake.Aftermath.ChronicleEvents",
        };

        private const string KindBattleClosed = "battle.closed";
        private const string KindRuleQueued = "chronicle.rule.queued";

        // Cached reflection into the spine's event row and payloads. All are
        // resolved lazily off the first event actually received, so a field
        // rename shows up as one warning rather than a per-event storm.
        private static FieldInfo fKind, fOutcome, fPayload;
        private static bool rowFieldsResolved;
        private static bool warnedRowFields;
        private static readonly HashSet<string> WarnedBadGodNames = new HashSet<string>();

        static ChronicleSubscriber()
        {
            Type events = null;
            foreach (string name in EventsTypeNames)
            {
                events = AccessTools.TypeByName(name);
                if (events != null) break;
            }
            if (events == null) return; // Chronicle absent -- nothing to do.

            MethodInfo subscribe = AccessTools.Method(events, "Subscribe", new[] { typeof(Action<object>) });
            if (subscribe == null)
            {
                Log.Warning("[RimMandrake.Ninefold] found " + events.FullName +
                    " but no Subscribe(Action<object>) -- battle god-deltas are OFF. " +
                    "The chronicle spine's subscription API changed shape.");
                return;
            }

            subscribe.Invoke(null, new object[] { (Action<object>)OnChronicleEvent });

            if (Prefs.DevMode)
                Log.Message("[RimMandrake.Ninefold] subscribed to " + events.FullName + ".");
        }

        // The spine hands us a ChronicleEvent boxed as object -- we cannot
        // name its type, so every read is by field name (a documented
        // reflection contract on the engine side).
        private static void OnChronicleEvent(object e)
        {
            if (e == null) return;
            if (!ResolveRowFields(e.GetType())) return;

            string kind = fKind.GetValue(e) as string;
            if (kind == KindBattleClosed) ApplyBattleDelta(fOutcome.GetValue(e) as string);
            else if (kind == KindRuleQueued) ApplyRuleDelta(fPayload.GetValue(e));
        }

        private static bool ResolveRowFields(Type rowType)
        {
            if (rowFieldsResolved) return true;

            fKind = AccessTools.Field(rowType, "Kind");
            fOutcome = AccessTools.Field(rowType, "Outcome");
            fPayload = AccessTools.Field(rowType, "Payload");

            if (fKind == null || fOutcome == null || fPayload == null)
            {
                if (!warnedRowFields)
                {
                    warnedRowFields = true;
                    Log.Warning("[RimMandrake.Ninefold] " + rowType.FullName +
                        " is missing Kind/Outcome/Payload -- battle god-deltas are OFF. " +
                        "The chronicle event row was renamed out from under this consumer.");
                }
                return false;
            }

            rowFieldsResolved = true;
            return true;
        }

        // design/Jawa/proposals/plot_mechanisms_wave.md Part 2: "fires
        // Sh'kaar +D - the battle hook Ninefold currently lacks". Magnitude
        // scaled by outcome severity -- a first-pass ordering, same UNTUNED
        // status as EventMagnitude itself; real tuning is SATIATION_TUNING_RIG's
        // job. Outcome arrives as the BattleOutcome enum's NAME, since that
        // enum lives in the engine assembly we deliberately do not reference.
        private static void ApplyBattleDelta(string outcome)
        {
            GameComponent_Ninefold ninefold = GameComponent_Ninefold.Instance;
            if (ninefold == null) return;

            float delta;
            switch (outcome)
            {
                case "Repelled": delta = EventMagnitude.Large; break;
                case "Lost":
                case "Routed": delta = EventMagnitude.Medium; break;
                default: delta = EventMagnitude.Small; break;
            }

            ninefold.ApplyDelta(God.Shkaar, delta, "battle " + (outcome ?? "unknown"));
        }

        // Payload is an RM_AftermathRuleDef. We read three public fields off
        // it by name -- defName (from Verse.Def, which we DO share) plus the
        // rule's own godTie/godDelta.
        private static void ApplyRuleDelta(object ruleDef)
        {
            if (ruleDef == null) return;

            Type t = ruleDef.GetType();
            string godName = AccessTools.Field(t, "godTie")?.GetValue(ruleDef) as string;
            if (string.IsNullOrEmpty(godName)) return;

            object deltaBox = AccessTools.Field(t, "godDelta")?.GetValue(ruleDef);
            if (!(deltaBox is float delta)) return;

            string defName = (ruleDef as Def)?.defName ?? t.Name;

            if (!TryParseGod(godName, out God god))
            {
                // Once per bad name, not once per firing: this is a data
                // error in someone else's mod and it will recur every time
                // that rule queues.
                if (WarnedBadGodNames.Add(godName))
                    Log.Warning("[RimMandrake.Ninefold] aftermath rule " + defName +
                        " has godTie '" + godName + "', which is not one of the nine gods -- ignored.");
                return;
            }

            GameComponent_Ninefold.Instance?.ApplyDelta(god, delta, "aftermath queued: " + defName);
        }

        // Enum.TryParse<God> would also accept a bare ORDINAL ("7" parses as
        // Shkaar), which is exactly the silent-wrong-god failure the God
        // enum's own NINEFOLD_ENUM_ORDER_SAVE_TRAP_1 header warns about.
        // Match names only.
        private static bool TryParseGod(string name, out God god)
        {
            foreach (God g in GodExtensions.All)
            {
                if (string.Equals(g.ToString(), name, StringComparison.OrdinalIgnoreCase))
                {
                    god = g;
                    return true;
                }
            }
            god = default;
            return false;
        }
    }
}
