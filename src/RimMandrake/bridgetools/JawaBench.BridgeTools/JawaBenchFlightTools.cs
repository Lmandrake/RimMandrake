// JawaBenchFlightTools.cs - READ and DRIVE Pawn.Flying from outside the game.
//
// VENOMVINE_PATHCOST_AND_FLYER_1. MEASURED live 2026-09-21 (FOUNDRY): the whole
// existing bridge surface could neither READ nor WRITE a pawn's flight state -
// no companion tool touched it, the 766 enumerated debug-UI nodes held nothing
// flight-related, and the scripting tools are a lowered subset that only
// sequences existing capability calls. So MapComponent_ContactVenom.Sample's
// "if (pawn.Flying) continue" - the venomvine flyer exemption - was literally
// unobservable: a null result could not be told apart from "the birds never
// left the ground". This file closes that gap.
//
// THE ENGINE FACTS THAT SHAPE THIS FILE, each read from 1.6 source via RimSage:
//
//  1. Pawn.Flying (Verse/Pawn.cs:1515) is `flight?.Flying ?? false`, and
//     Pawn_FlightTracker.Flying (RimWorld/Pawn_FlightTracker.cs:47) is
//     `flightState != FlightState.Grounded`. So TakingOff and LANDING both read
//     as Flying. There is no "mostly landed" state - a pawn is airborne for
//     every consumer, including a trap and including the venomvine component,
//     right up to the tick the landing lerp completes.
//
//  2. Pawn_FlightTracker.StartFlying() is public but is gated on CanFlyNow,
//     which is `!Flying && CanEverFly && flightCooldownTicks <= 0`. CanEverFly
//     ends in `GetStatValue(StatDefOf.MaxFlightTime) > 0f`, so it is a STAT
//     switch, not a race flag (the same trap CLAUDE.md names for authoring
//     flyers). A species with MaxFlightTime 0 can never be made to fly through
//     the public API at all.
//
//  3. ...which is exactly why action='hold' exists and writes the private
//     flightState field directly. It makes Pawn.Flying answer true for ANY
//     pawn, flight-capable or not. That is not a cheat, it is the control arm:
//     it separates "the flyer exemption fires" from "geese happen to fly",
//     because a turkey held airborne must be skipped too if the skip is really
//     keyed on Flying.
//
//  4. 🔴 FLIGHT DOES NOT PERSIST BY ITSELF, AND THIS IS THE WHOLE REASON FOR
//     maintainTicks. Pawn_FlightTracker.Notify_JobStarted force-lands the pawn
//     on every job start whose JobDef lacks tryStartFlying, and FlightTick
//     lands it anyway once flyingTicks reaches MaxFlightTicks
//     (MaxFlightTime * 60). An animal changes job constantly. A caller that
//     sets Flying once, waits, and then reads a result has measured a pawn that
//     was airborne for an unknown fraction of the window - the precise
//     ambiguity this tool exists to remove. maintainTicks re-asserts the state
//     every poll for the whole window instead.
//
//  5. ForceLand() does NOT ground a pawn - it sets Landing, which still reads
//     Flying == true for another ~25 ticks, and then adds a
//     FlightCooldown-sized cooldown. So the grounded CONTROL arm cannot be
//     staged with ForceLand alone; action='land' writes Grounded directly and
//     zeroes the cooldown, which is the only way to get a definitely-grounded
//     pawn on a named tick.
//
// GATING. Following JawaBenchEventTools.cs's stated test and JawaBenchAbilityTools.cs's
// restatement of it: the GM gate is for tools that hand THE WORLD permission to
// act on the player. This one makes NAMED pawns do a NAMED thing, the same
// category as damage/order_pawn/pawn_mental. So: ungated.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    /// <summary>One maintain-poll's worth of state, so the poll loop does not
    /// have to reflect over an anonymous type to read its own numbers back.</summary>
    internal sealed class FlightPoll
    {
        public int Ticks;
        public int FlyingNow;
        public int Reasserts;
    }

    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  reflection handles onto Pawn_FlightTracker's private state
        // ================================================================
        // Every one of these is private with no accessor (read from 1.6
        // source). They are resolved once and each is null-checked at every
        // use, so a future engine version that renames one degrades to a
        // named refusal rather than a NullReferenceException in the caller.

        private static readonly FieldInfo FlightStateField =
            typeof(Pawn_FlightTracker).GetField("flightState", BindingFlags.Instance | BindingFlags.NonPublic);
        private static readonly FieldInfo FlightFlyingTicksField =
            typeof(Pawn_FlightTracker).GetField("flyingTicks", BindingFlags.Instance | BindingFlags.NonPublic);
        private static readonly FieldInfo FlightCooldownTicksField =
            typeof(Pawn_FlightTracker).GetField("flightCooldownTicks", BindingFlags.Instance | BindingFlags.NonPublic);
        private static readonly FieldInfo FlightLerpTickField =
            typeof(Pawn_FlightTracker).GetField("lerpTick", BindingFlags.Instance | BindingFlags.NonPublic);

        // 🔴 WHAT 'hold' WRITES INTO flyingTicks, AND WHY IT IS NOT 0.
        // FlightTick lands the pawn the moment flyingTicks >= MaxFlightTicks,
        // and MaxFlightTicks is MaxFlightTime * 60 - which is ZERO for every
        // species that cannot fly. So holding a turkey or a hare airborne with
        // flyingTicks = 0 lands it on the very next tick, and it then spends
        // ~50 ticks in Landing (still Flying) before hitting Grounded. That
        // produced a maintain window with flyingLowWater 0 and a measurement
        // that was only accidentally clean (MEASURED 2026-09-21). A large
        // negative value gives FlightTick ~100,000 ticks to count up through,
        // so a held pawn stays airborne whatever its stat says.
        private const int HoldFlyingTicks = -100000;

        // FlightState is a PRIVATE NESTED enum, so it cannot be named here.
        // Its members and values, read from source: Grounded=0, Flying=1,
        // TakingOff=2, Landing=3.
        private const int FlightStateGrounded = 0;
        private const int FlightStateFlying = 1;
        private const int FlightStateTakingOff = 2;
        private const int FlightStateLanding = 3;

        private static string FlightStateName(int v)
        {
            switch (v)
            {
                case FlightStateGrounded: return "Grounded";
                case FlightStateFlying: return "Flying";
                case FlightStateTakingOff: return "TakingOff";
                case FlightStateLanding: return "Landing";
                default: return "Unknown(" + v + ")";
            }
        }

        private static int FlightStateRaw(Pawn_FlightTracker t)
        {
            if (t == null || FlightStateField == null) return -1;
            try { return Convert.ToInt32(FlightStateField.GetValue(t)); }
            catch { return -1; }
        }

        private static bool FlightStateWrite(Pawn_FlightTracker t, int value, out string err)
        {
            err = null;
            if (t == null) { err = "No Pawn_FlightTracker."; return false; }
            if (FlightStateField == null)
            {
                err = "Pawn_FlightTracker has no private field 'flightState' in this build - " +
                      "the engine renamed it and this tool cannot write flight state.";
                return false;
            }
            try
            {
                FlightStateField.SetValue(t, Enum.ToObject(FlightStateField.FieldType, value));
                return true;
            }
            catch (Exception e) { err = "Writing flightState threw: " + e.Message; return false; }
        }

        private static int FlightIntField(Pawn_FlightTracker t, FieldInfo f, int fallback)
        {
            if (t == null || f == null) return fallback;
            try { return Convert.ToInt32(f.GetValue(t)); }
            catch { return fallback; }
        }

        private static void FlightIntWrite(Pawn_FlightTracker t, FieldInfo f, int value)
        {
            if (t == null || f == null) return;
            try { f.SetValue(t, value); }
            catch { /* reported by the read-back, never swallowed silently */ }
        }

        /// <summary>
        /// One pawn's complete flight picture. Every field is read from the raw
        /// tracker, never from a convenience getter that might be cached.
        /// </summary>
        private static object FlightRow(Pawn p)
        {
            var t = p.flight;
            var raw = FlightStateRaw(t);
            float maxFlightTime = -1f, flightCooldownStat = -1f;
            try { maxFlightTime = p.GetStatValue(StatDefOf.MaxFlightTime, true, 300); } catch { }
            try { flightCooldownStat = p.GetStatValue(StatDefOf.FlightCooldown); } catch { }
            var job = p.CurJob;
            return new
            {
                pawn = p.ThingID,
                thingIDNumber = p.thingIDNumber,
                label = p.LabelShortCap.ToString(),
                kindDef = p.kindDef != null ? p.kindDef.defName : null,
                thingDef = p.def != null ? p.def.defName : null,
                spawned = p.Spawned,
                dead = p.Dead,
                x = p.Spawned ? p.Position.x : -1,
                z = p.Spawned ? p.Position.z : -1,
                // THE ANSWER. Pawn.Flying itself, not a reconstruction of it.
                flying = p.Flying,
                hasTracker = t != null,
                flightState = FlightStateName(raw),
                flightStateRaw = raw,
                canEverFly = t != null && t.CanEverFly,
                canFlyNow = t != null && t.CanFlyNow,
                maxFlightTicks = t != null ? t.MaxFlightTicks : -1,
                maxFlightTimeStat = maxFlightTime,
                flightCooldownStat,
                flyingTicks = FlightIntField(t, FlightFlyingTicksField, -999),
                flightCooldownTicks = FlightIntField(t, FlightCooldownTicksField, -999),
                lerpTick = FlightIntField(t, FlightLerpTickField, -999),
                positionOffsetFactor = t != null ? t.PositionOffsetFactor : -1f,
                curJobDef = job != null && job.def != null ? job.def.defName : null,
                // JobDef.tryStartFlying is what decides whether the NEXT job start
                // keeps a pawn airborne or force-lands it. Report it, because it is
                // the single field that explains an unexpected landing.
                curJobTryStartFlying = job != null && job.def != null && job.def.tryStartFlying,
                curJobIfFlyingKeepFlying = job != null && job.def != null && job.def.ifFlyingKeepFlying,
                curJobFlying = job != null && job.flying,
                raceFlightStartChanceOnJobStart = p.RaceProps != null ? p.RaceProps.flightStartChanceOnJobStart : -1f,
                raceCanLeaveMapFlying = p.RaceProps != null && p.RaceProps.canLeaveMapFlying,
            };
        }

        /// <summary>
        /// Resolve the pawns this call acts on: an explicit id, or every spawned
        /// pawn whose kindDef or ThingDef defName matches 'kind'.
        /// </summary>
        private static List<Pawn> FlightSelect(string pawn, string kind, int maxPawns, out string err)
        {
            err = null;
            var outList = new List<Pawn>();
            if (!string.IsNullOrWhiteSpace(pawn))
            {
                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) { err = perr ?? ("No pawn matching '" + pawn + "'."); return outList; }
                outList.Add(p);
                return outList;
            }
            if (string.IsNullOrWhiteSpace(kind)) { err = "Give either a pawn id or a kind defName."; return outList; }

            var k = kind.Trim();
            var maps = Find.Maps ?? new List<Map>();
            foreach (var m in maps)
            {
                foreach (var p in m.mapPawns.AllPawnsSpawned)
                {
                    if (p == null || p.Dead) continue;
                    var kd = p.kindDef != null ? p.kindDef.defName : null;
                    var td = p.def != null ? p.def.defName : null;
                    if (string.Equals(kd, k, StringComparison.OrdinalIgnoreCase) ||
                        string.Equals(td, k, StringComparison.OrdinalIgnoreCase))
                    {
                        outList.Add(p);
                        if (outList.Count >= maxPawns) return outList;
                    }
                }
            }
            if (outList.Count == 0)
                err = "No spawned pawn has kindDef or ThingDef defName '" + k + "'. " +
                      "This is a defName match, not a label match - 'Goose' the label is " +
                      "kindDef 'Goose', but a modded bird may not be.";
            return outList;
        }

        [Tool(
            "jawa/pawn_flight",
            Description =
                "READ and DRIVE a pawn's flight state - Pawn.Flying and the whole " +
                "Pawn_FlightTracker behind it - for one pawn or for every spawned pawn of a " +
                "named kind. Nothing else on this bridge can read Flying at all, and no debug " +
                "action exposes it, so before this tool any claim about a flyer's behaviour " +
                "was an inference from species. " +
                "🔴 Flying IS NOT A RACE FLAG. Pawn_FlightTracker.CanEverFly ends in " +
                "GetStatValue(MaxFlightTime) > 0, so a species with that stat at 0 can never " +
                "be made to fly through the engine's own public API, whatever its race fields " +
                "say. canEverFly and maxFlightTimeStat are both reported so a null result can " +
                "be attributed. " +
                "🔴 TakingOff and LANDING BOTH READ AS FLYING. Pawn_FlightTracker.Flying is " +
                "flightState != Grounded, so a pawn counts as airborne for every consumer " +
                "(traps, the venomvine contact component) right up to the tick its landing " +
                "lerp finishes. Grounded is the only state that is not flying. " +
                "ACTIONS. 'report' (default) is read-only. 'start' is the engine's own " +
                "StartFlying(), which REFUSES unless CanFlyNow - already flying, cooldown " +
                "running, or MaxFlightTime 0 all block it, and the refusal is named per pawn. " +
                "'hold' writes the private flightState field directly and so works on ANY " +
                "pawn including one that can never fly - that is the control arm of a flight " +
                "experiment, not a cheat, because it separates 'the code path keyed on Flying " +
                "fires' from 'this species happens to fly'. 'land' writes Grounded directly " +
                "and zeroes the cooldown: ForceLand() alone is NOT enough, it only sets " +
                "Landing, which still reads as flying. " +
                "🔴 maintainTicks IS USUALLY MANDATORY, NOT OPTIONAL. Notify_JobStarted " +
                "force-lands a pawn on every job start whose JobDef lacks tryStartFlying, and " +
                "an animal changes job constantly; FlightTick also lands it once flyingTicks " +
                "reaches MaxFlightTicks. So a caller that sets Flying once and then waits has " +
                "measured a pawn that was airborne for an unknown fraction of the window. " +
                "maintainTicks re-asserts the state on every poll for that many GAME ticks and " +
                "reports reasserts plus the observed low-water mark, so the window's integrity " +
                "is part of the result rather than an assumption. " +
                "⚠️ A PAUSED GAME NEVER LANDS AND NEVER SAMPLES ANYTHING. With maintainTicks>0 " +
                "and unpause on, the call runs at Normal speed for the window and restores the " +
                "previous speed afterwards, including on cancellation.",
            ResultDescription =
                "pawns[]: one row each with flying (Pawn.Flying itself), flightState, " +
                "canEverFly, canFlyNow, maxFlightTicks, maxFlightTimeStat, the raw flyingTicks " +
                "/ flightCooldownTicks / lerpTick, and the current JobDef with its " +
                "tryStartFlying - which is the one field that explains an unexpected landing. " +
                "For an action, each row also carries changed, refusedReason (why the engine " +
                "declined, never a bare false) and the before/after flightState. " +
                "After a maintain window: ticksElapsed, reasserts, and flyingLowWater - the " +
                "smallest number of the selected pawns seen flying at any poll. If " +
                "flyingLowWater is less than the pawn count, the window was NOT clean and any " +
                "measurement taken across it is contaminated.")]
        public static async Task<object> PawnFlight(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'report' (read-only, default), 'start', 'hold' or 'land'.", DefaultValue = "report")]
            string action = "report",
            [ToolParameter(Description = "A single pawn id, thingId or name. No faction check.")]
            string pawn = null,
            [ToolParameter(Description =
                "Act on EVERY spawned pawn whose PawnKindDef or ThingDef defName matches this, " +
                "e.g. 'Goose'. A defName match, not a label match. Ignored when pawn is given.")]
            string kind = null,
            [ToolParameter(Description = "Ceiling on how many pawns a kind match may select.", DefaultValue = 200)]
            int maxPawns = 200,
            [ToolParameter(Description =
                "Re-assert the requested state every poll for this many GAME ticks, then read " +
                "back. Applies to 'start' and 'hold'. 0 acts once and returns immediately - " +
                "which for an animal means the state may not survive its next job start.",
                DefaultValue = 0)]
            int maintainTicks = 0,
            [ToolParameter(Description = "Wall-clock ceiling, so a paused or hitching game cannot hang the call.", DefaultValue = 60)]
            int timeoutSeconds = 60,
            [ToolParameter(Description =
                "If the game is paused, run at Normal speed for the maintain window and restore " +
                "the previous speed afterwards. With this off a paused game returns ticksElapsed=0.",
                DefaultValue = true)]
            bool unpause = true,
            [ToolParameter(Description =
                "For 'start': zero flightCooldownTicks first, so a pawn that only just landed " +
                "can be launched again for a test. Reported per pawn as cooldownCleared.",
                DefaultValue = true)]
            bool clearCooldown = true)
        {
            var A = (action ?? "report").Trim().ToLowerInvariant();
            if (A != "report" && A != "start" && A != "hold" && A != "land")
                return Fail("action '" + action + "' is not 'report', 'start', 'hold' or 'land'.");
            if (maxPawns < 1 || maxPawns > 2000) return Fail("maxPawns must be 1-2000, got " + maxPawns + ".");
            if (maintainTicks < 0 || maintainTicks > 60000)
                return Fail("maintainTicks must be 0-60000, got " + maintainTicks + ".");
            if (timeoutSeconds < 1 || timeoutSeconds > 300)
                return Fail("timeoutSeconds must be 1-300, got " + timeoutSeconds + ".");
            if (A == "land" && maintainTicks > 0)
                return Fail("maintainTicks does not apply to 'land' - a grounded pawn stays " +
                            "grounded until something launches it. Use it with 'hold' or 'start'.");

            var targets = new List<Pawn>();
            var rowsBefore = new List<object>();
            var actionRows = new List<object>();
            var startTicks = -1;
            TimeSpeed speedBefore = TimeSpeed.Paused;
            var speedChanged = false;
            var speedRestored = false;

            var setup = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string serr;
                targets = FlightSelect(pawn, kind, maxPawns, out serr);
                if (targets.Count == 0) return Fail(serr ?? "Nothing selected.");

                startTicks = TicksGameSafe();

                foreach (var p in targets) rowsBefore.Add(FlightRow(p));

                if (A == "report") return null;

                foreach (var p in targets)
                {
                    var t = p.flight;
                    var beforeRaw = FlightStateRaw(t);
                    var beforeFlying = p.Flying;
                    string refused = null;
                    var cooldownCleared = false;
                    var changed = false;

                    if (t == null)
                    {
                        // PawnComponentsUtility builds the tracker; a pawn without one
                        // is a real state, not an error, and Flying is false for it.
                        refused = "This pawn has no Pawn_FlightTracker at all, so it can " +
                                  "neither fly nor be made to. Pawn.Flying is permanently false for it.";
                    }
                    else if (A == "start")
                    {
                        if (clearCooldown && FlightIntField(t, FlightCooldownTicksField, 0) > 0)
                        {
                            FlightIntWrite(t, FlightCooldownTicksField, 0);
                            cooldownCleared = true;
                        }
                        if (!t.CanEverFly)
                            refused = "CanEverFly is false. It ends in GetStatValue(MaxFlightTime) > 0, " +
                                      "measured here at " + p.GetStatValue(StatDefOf.MaxFlightTime, true, 300) +
                                      "s - this species cannot be launched through the engine API. " +
                                      "Use action='hold' if you want it airborne as a control.";
                        else if (t.Flying)
                            refused = "Already flying (state " + FlightStateName(beforeRaw) + "). " +
                                      "CanFlyNow is false while airborne.";
                        else if (!t.CanFlyNow)
                            refused = "CanFlyNow is false with CanEverFly true and not flying, so the " +
                                      "flight cooldown is still running: flightCooldownTicks=" +
                                      FlightIntField(t, FlightCooldownTicksField, -999) + ".";
                        else
                        {
                            t.StartFlying();
                            changed = FlightStateRaw(t) != beforeRaw;
                            if (!changed)
                                refused = "StartFlying() returned without changing flightState, " +
                                          "although CanFlyNow was true. Nothing else in this call touched it.";
                        }
                    }
                    else if (A == "hold")
                    {
                        // Direct write - deliberately bypasses CanFlyNow (see header fact 3).
                        string werr;
                        if (!FlightStateWrite(t, FlightStateFlying, out werr)) refused = werr;
                        else
                        {
                            FlightIntWrite(t, FlightFlyingTicksField, HoldFlyingTicks);
                            FlightIntWrite(t, FlightLerpTickField, 0);
                            changed = beforeRaw != FlightStateFlying;
                        }
                    }
                    else // land
                    {
                        string werr;
                        if (!FlightStateWrite(t, FlightStateGrounded, out werr)) refused = werr;
                        else
                        {
                            FlightIntWrite(t, FlightFlyingTicksField, -1);
                            FlightIntWrite(t, FlightLerpTickField, 0);
                            FlightIntWrite(t, FlightCooldownTicksField, 0);
                            var job = p.CurJob;
                            if (job != null) job.flying = false;
                            changed = beforeRaw != FlightStateGrounded;
                        }
                    }

                    actionRows.Add(new
                    {
                        pawn = p.ThingID,
                        label = p.LabelShortCap.ToString(),
                        changed,
                        refusedReason = refused,
                        cooldownCleared,
                        flyingBefore = beforeFlying,
                        flyingAfter = p.Flying,
                        stateBefore = FlightStateName(beforeRaw),
                        stateAfter = FlightStateName(FlightStateRaw(t)),
                    });
                }

                if (maintainTicks > 0)
                {
                    var tm = Find.TickManager;
                    if (tm != null)
                    {
                        speedBefore = tm.CurTimeSpeed;
                        if (unpause && tm.CurTimeSpeed == TimeSpeed.Paused)
                        {
                            tm.CurTimeSpeed = TimeSpeed.Normal;
                            speedChanged = true;
                        }
                    }
                }
                return null;
            }, cancellationToken).ConfigureAwait(false);

            if (setup != null) return setup;

            if (A == "report")
                return new
                {
                    success = true,
                    action = "report",
                    count = rowsBefore.Count,
                    pawns = rowsBefore,
                    ticksGame = startTicks,
                };

            // ------------------------------------------------------------
            //  the maintain window
            // ------------------------------------------------------------
            // 🔴 THE SPEED MUST COME BACK EVEN WHEN THE CALL DOES NOT, so the
            // restore lives in a finally as well as on the happy path.
            var ticksNow = startTicks;
            var reasserts = 0;
            var polls = 0;
            var flyingLowWater = targets.Count;
            var timedOut = false;
            try
            {
                var elapsedMs = 0;
                while (maintainTicks > 0)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (ticksNow - startTicks >= maintainTicks) break;
                    if (elapsedMs >= timeoutSeconds * 1000) { timedOut = true; break; }
                    await Task.Delay(50, cancellationToken).ConfigureAwait(false);
                    elapsedMs += 50;

                    var poll = await ctx.MainThread.InvokeAsync<FlightPoll>(() =>
                    {
                        var flyingNow = 0;
                        var re = 0;
                        foreach (var p in targets)
                        {
                            if (p == null || p.Dead || !p.Spawned) continue;
                            var t = p.flight;
                            if (t == null) continue;
                            // Count BEFORE re-asserting: the low-water mark must
                            // record what the simulation actually saw, not what
                            // this tool put back afterwards.
                            if (p.Flying) flyingNow++;
                            else
                            {
                                string werr;
                                if (FlightStateWrite(t, FlightStateFlying, out werr))
                                {
                                    FlightIntWrite(t, FlightFlyingTicksField, HoldFlyingTicks);
                                    FlightIntWrite(t, FlightLerpTickField, 0);
                                    re++;
                                }
                            }
                            // Keep flyingTicks from reaching MaxFlightTicks even
                            // for a pawn that is still airborne, or FlightTick
                            // lands it mid-window.
                            if (FlightIntField(t, FlightFlyingTicksField, 0) > HoldFlyingTicks / 2)
                                FlightIntWrite(t, FlightFlyingTicksField, HoldFlyingTicks);
                        }
                        return new FlightPoll { Ticks = TicksGameSafe(), FlyingNow = flyingNow, Reasserts = re };
                    }, cancellationToken).ConfigureAwait(false);

                    ticksNow = poll.Ticks;
                    reasserts += poll.Reasserts;
                    if (poll.FlyingNow < flyingLowWater) flyingLowWater = poll.FlyingNow;
                    polls++;
                }
            }
            finally
            {
                if (speedChanged && !speedRestored)
                {
                    try
                    {
                        await ctx.MainThread.InvokeAsync(() =>
                        {
                            var tm = Find.TickManager;
                            if (tm != null) { tm.CurTimeSpeed = speedBefore; speedRestored = true; }
                            return 0;
                        }, CancellationToken.None).ConfigureAwait(false);
                    }
                    catch { /* the restore is best-effort; speedRestored reports the truth */ }
                }
            }

            var rowsAfter = await ctx.MainThread.InvokeAsync(() =>
            {
                var rows = new List<object>();
                foreach (var p in targets) rows.Add(FlightRow(p));
                return rows;
            }, cancellationToken).ConfigureAwait(false);

            var flyingAtEnd = 0;
            await ctx.MainThread.InvokeAsync(() =>
            {
                foreach (var p in targets) if (p != null && !p.Dead && p.Flying) flyingAtEnd++;
                return 0;
            }, cancellationToken).ConfigureAwait(false);

            return new
            {
                success = true,
                action = A,
                count = targets.Count,
                ticksElapsed = ticksNow - startTicks,
                maintainTicks,
                polls,
                reasserts,
                // 🔴 The integrity number. Less than count means the window was
                // NOT clean and anything measured across it is contaminated.
                flyingLowWater = maintainTicks > 0 ? flyingLowWater : -1,
                flyingAtEnd,
                timedOut,
                speedRestored,
                results = actionRows,
                pawns = rowsAfter,
                ticksGame = ticksNow,
            };
        }
    }
}
