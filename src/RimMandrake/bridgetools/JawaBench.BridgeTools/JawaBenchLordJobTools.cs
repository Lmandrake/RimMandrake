// JawaBenchLordJobTools.cs - rewrite what an AI group is DOING, mid-flight.
//
// LORD_JOB_SWAP_TOOL_1. There is no other route to raid scripting: every existing
// lord tool here either creates a Lord (lord_assault_spawn, lord_defend_spawn) or
// nudges one that already exists (lord_poke, lord_pawn_move). None can change what
// an existing group's state machine is FOR.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE, NOT GUESSED
// =============================================================
//   Verse/AI/Group/Lord.cs          SetJob(LordJob, bool loading = false)
//                                   GotoToil(LordToil)
//                                   Graph => graph  ·  CurLordToil => curLordToil
//                                   LordJob => curJob  ·  ownedPawns  ·  loadID  ·  faction
//   Verse/AI/Group/StateGraph.cs    StartingToil
//   Verse/AI/Group/LordManager.cs   List<Lord> lords
//   RimWorld/LordJob_AssaultColony.cs   the worked example of why a parameterless
//                                       ctor is NOT a safe default (below)
//
// 🔴 THE TWO CALLS ARE ONE OPERATION AND NEITHER IS SAFE ALONE.
// SetJob replaces curJob, nulls curLordToil and builds a NEW graph. It does not
// touch a single pawn's duty. GotoToil is what runs Init() and UpdateAllDuties()
// on the new starting toil. So a tool that called only SetJob would leave a group
// in the new graph with every pawn still obeying a duty issued by the old one -
// visibly following orders that no longer exist, with nothing in the log.
// ⇒ This tool always does both, and when GotoToil throws after SetJob succeeded it
// says PARTIALLY APPLIED rather than returning a failure that reads as "nothing
// happened". That halfway state is real and the caller has to know about it.
//
// 🔴 WHY A PARAMETERLESS CONSTRUCTOR IS NOT A SAFE DEFAULT, MEASURED IN THE SOURCE.
// LordJob_AssaultColony has one, and it exists for Scribe loading - it leaves
// assaulterFaction null. Read CreateGraph: every flee, kidnap and steal transition
// is inside `if (assaulterFaction != null && ...)`. So constructing it the easy way
// yields a graph that BUILDS, ERROR-CHECKS CLEAN and behaves like a different job.
// ⇒ This tool binds constructor arguments BY NAME and refuses a constructor it
// cannot satisfy, listing every signature it found. It never quietly picks the
// parameterless one.
//
// ⛔ AND IT NEVER DROPS AN ARGUMENT IT DID NOT UNDERSTAND. An arg naming no
// parameter is a REFUSAL here, by name, with the accepted names listed. That is
// deliberate: BRIDGE_DROPS_UNKNOWN_PARAMS_1 measured the host bridge silently
// discarding unknown keys across all its tools, and this file will not add another.
//
// GATED behind JAWA_GM_TOOLS, on the same test as lord_poke: what happens after
// this call is decided by the target StateGraph, not by the caller. Handing an
// existing group a fresh assault graph is the world acting on the player.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- shared shape readers ----------------------------------------------
        //
        // Every one of these is wrapped, because they are called to BUILD AN ERROR
        // REPORT as often as to build a success one, and a reader that throws while
        // describing a failure destroys the only evidence there was.

        private static string LordToilName(Lord l)
        {
            try { return l.CurLordToil != null ? l.CurLordToil.GetType().Name : "(none)"; }
            catch { return "(error)"; }
        }

        private static string LordJobName(Lord l)
        {
            try { return l.LordJob != null ? l.LordJob.GetType().Name : "(none)"; }
            catch { return "(error)"; }
        }

        /// <summary>
        /// The duty DEF NAME a pawn is currently carrying, which is the only thing
        /// that actually changes visible behaviour. 🔑 Read from mindState.duty and
        /// not from the Lord, because the whole failure this tool exists to prevent
        /// is the Lord and its pawns disagreeing.
        /// </summary>
        private static string PawnDutyName(Pawn p)
        {
            try
            {
                if (p == null || p.mindState == null || p.mindState.duty == null) return "(none)";
                return p.mindState.duty.def != null ? p.mindState.duty.def.defName : "(no def)";
            }
            catch { return "(error)"; }
        }

        private static List<string> LordCtorSignatures(Type t)
        {
            var outp = new List<string>();
            try
            {
                foreach (var c in t.GetConstructors(BindingFlags.Public | BindingFlags.Instance))
                    outp.Add(t.Name + "(" + string.Join(", ",
                        c.GetParameters().Select(p =>
                            p.ParameterType.Name + " " + p.Name +
                            (p.IsOptional ? " = " + (p.DefaultValue == null ? "null" : p.DefaultValue.ToString()) : "")
                        ).ToArray()) + ")");
            }
            catch (Exception e) { outp.Add("(could not read constructors: " + e.Message + ")"); }
            return outp;
        }

        /// <summary>
        /// Parse `name=value;name=value` into an ordinal-ignore-case dictionary.
        /// Returns false and sets err on a malformed pair rather than skipping it -
        /// a silently skipped argument is the defect this file is written against.
        /// </summary>
        private static bool TryParseNamedArgs(string s, out Dictionary<string, string> d, out string err)
        {
            d = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            err = null;
            if (string.IsNullOrWhiteSpace(s)) return true;
            foreach (var raw in s.Split(';'))
            {
                var pair = raw.Trim();
                if (pair.Length == 0) continue;
                int eq = pair.IndexOf('=');
                if (eq <= 0)
                {
                    err = "Malformed entry '" + pair + "'. Every entry must be name=value, separated by ';'.";
                    return false;
                }
                var k = pair.Substring(0, eq).Trim();
                var v = pair.Substring(eq + 1).Trim();
                if (k.Length == 0) { err = "Empty argument name in '" + pair + "'."; return false; }
                if (d.ContainsKey(k)) { err = "Argument '" + k + "' given twice."; return false; }
                d[k] = v;
            }
            return true;
        }

        /// <summary>
        /// Convert one string to one constructor parameter type. ⛔ The supported set
        /// is deliberately CLOSED: anything outside it is refused BY TYPE NAME rather
        /// than defaulted, because a LordJob field silently left null is exactly the
        /// LordJob_AssaultColony trap described in this file's header.
        /// </summary>
        private static bool TryConvertArg(string text, Type target, Map map, out object value, out string err)
        {
            value = null; err = null;
            try
            {
                if (target == typeof(string)) { value = text; return true; }

                if (target == typeof(bool))
                {
                    bool b;
                    if (!bool.TryParse(text, out b)) { err = "'" + text + "' is not true/false."; return false; }
                    value = b; return true;
                }
                if (target == typeof(int))
                {
                    int i;
                    if (!int.TryParse(text, NumberStyles.Integer, CultureInfo.InvariantCulture, out i))
                    { err = "'" + text + "' is not an integer."; return false; }
                    value = i; return true;
                }
                if (target == typeof(float))
                {
                    float f;
                    if (!float.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out f))
                    { err = "'" + text + "' is not a number."; return false; }
                    value = f; return true;
                }
                if (target.IsEnum)
                {
                    try { value = Enum.Parse(target, text, true); return true; }
                    catch
                    {
                        err = "'" + text + "' is not a " + target.Name + ". Accepted: " +
                              string.Join(", ", Enum.GetNames(target));
                        return false;
                    }
                }
                if (target == typeof(Faction))
                {
                    // by Faction.Name first (what a caller reads on screen), then by FactionDef.
                    var byName = Find.FactionManager.AllFactionsListForReading
                        .FirstOrDefault(f => string.Equals(f.Name, text, StringComparison.OrdinalIgnoreCase));
                    if (byName == null)
                        byName = Find.FactionManager.AllFactionsListForReading
                            .FirstOrDefault(f => f.def != null &&
                                                 string.Equals(f.def.defName, text, StringComparison.OrdinalIgnoreCase));
                    if (byName == null)
                    {
                        err = "No live Faction named or defNamed '" + text + "'. Live factions: " +
                              string.Join(", ", Find.FactionManager.AllFactionsListForReading
                                  .Select(f => f.Name + " [" + (f.def != null ? f.def.defName : "?") + "]").Take(40));
                        return false;
                    }
                    value = byName; return true;
                }
                if (target == typeof(IntVec3))
                {
                    var b = text.Split(',');
                    int x, y, z;
                    if (b.Length == 2 &&
                        int.TryParse(b[0].Trim(), out x) && int.TryParse(b[1].Trim(), out z))
                    { value = new IntVec3(x, 0, z); }
                    else if (b.Length == 3 &&
                             int.TryParse(b[0].Trim(), out x) && int.TryParse(b[1].Trim(), out y) &&
                             int.TryParse(b[2].Trim(), out z))
                    { value = new IntVec3(x, y, z); }
                    else { err = "'" + text + "' is not a cell. Give 'x,z' or 'x,y,z'."; return false; }

                    var c = (IntVec3)value;
                    if (map != null && !c.InBounds(map))
                    { err = "Cell " + c + " is outside the map (" + map.Size.x + "x" + map.Size.z + ")."; return false; }
                    return true;
                }
                if (target == typeof(Map)) { value = map; return true; }
                if (typeof(Def).IsAssignableFrom(target))
                {
                    var found = GenDefDatabase.GetDefSilentFail(target, text, false);
                    if (found == null) { err = "No " + target.Name + " named '" + text + "'."; return false; }
                    value = found; return true;
                }

                err = "This tool cannot build a " + target.Name +
                      " from a string. Supported: string, bool, int, float, enum, Faction, IntVec3, Map, any Def.";
                return false;
            }
            catch (Exception e)
            {
                err = "converting '" + text + "' to " + target.Name + " threw " + e.GetType().Name + ": " + e.Message;
                return false;
            }
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/lord_set_job",
            Description =
                "*** HANDS AN EXISTING AI GROUP A NEW STATE MACHINE *** Replace a Lord's " +
                "LordJob mid-flight and re-enter its graph, which is the only route to " +
                "re-scripting a raid that has already landed. Calls Lord.SetJob then " +
                "Lord.GotoToil(Graph.StartingToil) - BOTH, because SetJob alone swaps the " +
                "graph and leaves every pawn carrying a duty issued by the OLD one, which " +
                "looks like a working group obeying orders that no longer exist. " +
                "Constructor arguments are bound BY NAME from 'args' and an argument naming " +
                "no parameter is REFUSED, never dropped. A constructor that cannot be " +
                "satisfied is refused with every signature listed. It never falls back to a " +
                "parameterless constructor: LordJob_AssaultColony has one, it leaves " +
                "assaulterFaction null, and the resulting graph builds clean while silently " +
                "losing its flee, kidnap and steal transitions. Address the Lord by " +
                "lordIndex (from the lord_pawn_move 'list' action); pass loadID as well and " +
                "it is checked, because indices shift as groups form and die.",
            ResultDescription =
                "success, the Lord's index/loadID/faction/pawn count, jobBefore and jobAfter, " +
                "toilBefore and toilAfter, graphToilCount, and per-pawn dutyBefore/dutyAfter " +
                "with dutiesChanged. On a GotoToil failure: partiallyApplied true, and the " +
                "group is in the NEW graph carrying OLD duties - say so, do not retry blindly.")]
        public static async Task<object> LordSetJob(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Lord index from the lord_pawn_move 'list' action.", DefaultValue = -1)]
            int lordIndex = -1,
            [ToolParameter(Description =
                "The Lord's loadID. Optional, but if given it must match the Lord at lordIndex " +
                "or the call is refused - indices shift as groups form and die.", DefaultValue = -1)]
            int loadID = -1,
            [ToolParameter(Description =
                "LordJob type name, e.g. 'LordJob_AssaultColony', 'LordJob_ExitMapBest', " +
                "'LordJob_DefendPoint'. Namespace optional; searched in every loaded assembly, " +
                "so modded LordJobs work too.")]
            string lordJob = null,
            [ToolParameter(Description =
                "Constructor arguments, 'name=value;name=value', bound BY PARAMETER NAME. " +
                "e.g. 'assaulterFaction=Pirate;canKidnap=false'. A Faction takes its screen " +
                "name or its FactionDef defName; an IntVec3 takes 'x,z'.")]
            string args = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var lm = map.lordManager;

                // ---- 1. address the Lord, and assert its identity -------------------
                if (lordIndex < 0 || lordIndex >= lm.lords.Count)
                    return Fail("lordIndex " + lordIndex + " is out of range (0.." + (lm.lords.Count - 1) + ").",
                        new
                        {
                            lords = lm.lords.Select((l, i) => new
                            {
                                index = i,
                                loadID = l.loadID,
                                faction = l.faction != null ? l.faction.Name : null,
                                pawns = l.ownedPawns != null ? l.ownedPawns.Count : 0,
                                job = LordJobName(l),
                                toil = LordToilName(l)
                            }).ToList()
                        });

                var lord = lm.lords[lordIndex];

                if (loadID >= 0 && lord.loadID != loadID)
                    return Fail("Lord at index " + lordIndex + " has loadID " + lord.loadID +
                                ", not the " + loadID + " you asserted. Indices shift; re-read the list.");

                // Rule from the item: refuse a Lord with zero pawns. A jobless empty Lord
                // is removed by LordManager on its own tick, so acting on one is a race.
                int pawnCount = lord.ownedPawns != null ? lord.ownedPawns.Count : 0;
                if (pawnCount == 0)
                    return Fail("Lord " + lordIndex + " (loadID " + lord.loadID + ") owns no pawns. " +
                                "LordManager removes an empty Lord on its own tick, so a job set here " +
                                "would be discarded.");

                // ---- 2. resolve the LordJob type -----------------------------------
                if (string.IsNullOrWhiteSpace(lordJob)) return Fail("Give 'lordJob', e.g. 'LordJob_AssaultColony'.");
                var jobType = GenTypes.GetTypeInAnyAssembly(lordJob.Trim());
                if (jobType == null)
                    return Fail("No type '" + lordJob + "' in any loaded assembly.",
                        new
                        {
                            suggestions = GenTypes.AllTypes
                                .Where(t => typeof(LordJob).IsAssignableFrom(t) && !t.IsAbstract &&
                                            t.Name.IndexOf(lordJob.Trim(), StringComparison.OrdinalIgnoreCase) >= 0)
                                .Select(t => t.Name).Take(25).ToList()
                        });
                if (!typeof(LordJob).IsAssignableFrom(jobType))
                    return Fail("'" + jobType.FullName + "' is not a LordJob.");
                if (jobType.IsAbstract)
                    return Fail("'" + jobType.FullName + "' is abstract and cannot be constructed.");

                // ---- 3. bind constructor arguments BY NAME -------------------------
                Dictionary<string, string> supplied;
                if (!TryParseNamedArgs(args, out supplied, out err)) return Fail(err);

                var ctors = jobType.GetConstructors(BindingFlags.Public | BindingFlags.Instance);
                if (ctors.Length == 0)
                    return Fail("'" + jobType.Name + "' has no public constructor.");

                ConstructorInfo chosen = null;
                object[] chosenArgs = null;
                var rejections = new List<string>();

                // Prefer the constructor that CONSUMES THE MOST supplied arguments. A
                // constructor leaving a supplied argument unused is not a candidate at
                // all - that is the silent-drop defect, and it is refused below.
                foreach (var c in ctors.OrderByDescending(c => c.GetParameters().Length))
                {
                    var ps = c.GetParameters();
                    var names = new HashSet<string>(ps.Select(p => p.Name), StringComparer.OrdinalIgnoreCase);
                    var unknown = supplied.Keys.Where(k => !names.Contains(k)).ToList();
                    if (unknown.Count > 0)
                    {
                        rejections.Add(jobType.Name + "(" + ps.Length + " params): does not accept " +
                                       string.Join(", ", unknown.ToArray()));
                        continue;
                    }

                    var vals = new object[ps.Length];
                    string why = null;
                    for (int i = 0; i < ps.Length; i++)
                    {
                        string text;
                        if (supplied.TryGetValue(ps[i].Name, out text))
                        {
                            object v;
                            if (!TryConvertArg(text, ps[i].ParameterType, map, out v, out why))
                            { why = ps[i].Name + ": " + why; break; }
                            vals[i] = v;
                        }
                        else if (ps[i].IsOptional) { vals[i] = ps[i].DefaultValue; }
                        else if (ps[i].ParameterType == typeof(Map)) { vals[i] = map; }
                        else
                        { why = "required parameter '" + ps[i].Name + "' (" + ps[i].ParameterType.Name + ") was not given"; break; }
                    }
                    if (why != null) { rejections.Add(jobType.Name + "(" + ps.Length + " params): " + why); continue; }

                    chosen = c; chosenArgs = vals; break;
                }

                if (chosen == null)
                    return Fail("No constructor of '" + jobType.Name + "' could be satisfied from the arguments given.",
                        new { signatures = LordCtorSignatures(jobType), rejections, argumentsGiven = supplied.Keys.ToList() });

                // ⛔ The zero-argument construction guard. It is legal to ask for it
                // explicitly; it is never chosen because nothing else fitted.
                if (chosen.GetParameters().Length == 0 && ctors.Length > 1 && supplied.Count == 0)
                    return Fail("'" + jobType.Name + "' has a parameterless constructor AND richer ones, and you " +
                                "supplied no arguments. Refusing to guess: a Scribe-loading constructor leaves " +
                                "fields null and yields a graph that builds clean and behaves differently. " +
                                "Name the arguments you want, or pass args with the parameterless one's own " +
                                "(none) if that is genuinely what you mean.",
                        new { signatures = LordCtorSignatures(jobType) });

                LordJob newJob;
                try { newJob = (LordJob)chosen.Invoke(chosenArgs); }
                catch (Exception e)
                {
                    var inner = e.InnerException ?? e;
                    return Fail("Constructing " + jobType.Name + " threw " + inner.GetType().Name + ": " + inner.Message,
                        new { signatures = LordCtorSignatures(jobType) });
                }
                if (newJob == null) return Fail("Constructing " + jobType.Name + " returned null.");

                // ---- 4. snapshot BEFORE ---------------------------------------------
                var pawnsBefore = lord.ownedPawns
                    .Select(p => new { pawn = p, id = p != null ? p.ThingID : "(null)", duty = PawnDutyName(p) })
                    .ToList();
                string jobBefore = LordJobName(lord);
                string toilBefore = LordToilName(lord);

                // ---- 5. SetJob ------------------------------------------------------
                // This is where CreateGraph and graph.ErrorCheck run, so a LordJob whose
                // graph does not build fails HERE, before anything was disturbed.
                try { lord.SetJob(newJob); }
                catch (Exception e)
                {
                    return Fail("Lord.SetJob threw " + e.GetType().Name + ": " + e.Message +
                                " - the graph did not build. Nothing was applied; the Lord still holds '" +
                                jobBefore + "'.",
                        new { signatures = LordCtorSignatures(jobType), jobBefore, toilBefore });
                }

                int graphToilCount = -1;
                try { graphToilCount = lord.Graph != null && lord.Graph.lordToils != null ? lord.Graph.lordToils.Count : -1; }
                catch { graphToilCount = -1; }

                // ---- 6. GotoToil - the half that actually re-issues duties ----------
                LordToil starting = null;
                try { starting = lord.Graph != null ? lord.Graph.StartingToil : null; }
                catch (Exception e)
                {
                    return new
                    {
                        success = false,
                        partiallyApplied = true,
                        message = "SetJob SUCCEEDED and Graph.StartingToil threw " + e.GetType().Name + ": " + e.Message +
                                  ". The Lord is in the NEW graph with pawns still carrying duties from the OLD one. " +
                                  "This is a real halfway state - do not read it as 'nothing happened'.",
                        lordIndex,
                        lordLoadID = lord.loadID,
                        jobBefore,
                        jobAfter = LordJobName(lord),
                        toilBefore,
                        toilAfter = LordToilName(lord),
                        graphToilCount,
                        ticksGame = TicksGameSafe()
                    };
                }
                if (starting == null)
                    return new
                    {
                        success = false,
                        partiallyApplied = true,
                        message = "SetJob SUCCEEDED but the new graph has no starting toil, so duties were never " +
                                  "re-issued. The Lord is in the NEW graph with OLD duties.",
                        lordIndex,
                        lordLoadID = lord.loadID,
                        jobBefore,
                        jobAfter = LordJobName(lord),
                        toilBefore,
                        toilAfter = LordToilName(lord),
                        graphToilCount,
                        ticksGame = TicksGameSafe()
                    };

                try { lord.GotoToil(starting); }
                catch (Exception e)
                {
                    return new
                    {
                        success = false,
                        partiallyApplied = true,
                        message = "SetJob SUCCEEDED and Lord.GotoToil threw " + e.GetType().Name + ": " + e.Message +
                                  ". The Lord is in the NEW graph with pawns still carrying duties from the OLD one. " +
                                  "This is a real halfway state - do not read it as 'nothing happened'.",
                        lordIndex,
                        lordLoadID = lord.loadID,
                        jobBefore,
                        jobAfter = LordJobName(lord),
                        toilBefore,
                        toilAfter = LordToilName(lord),
                        graphToilCount,
                        pawns = pawnsBefore.Select(p => new { id = p.id, dutyBefore = p.duty, dutyAfter = PawnDutyName(p.pawn) }).ToList(),
                        ticksGame = TicksGameSafe()
                    };
                }

                // ---- 7. read back ----------------------------------------------------
                // 🔑 The duty per pawn is the evidence, not the toil name. GotoToil calls
                // UpdateAllDuties, and a toil that changed while no duty did is the exact
                // half-applied shape this tool exists to make visible.
                var pawns = pawnsBefore
                    .Select(p => new { id = p.id, dutyBefore = p.duty, dutyAfter = PawnDutyName(p.pawn) })
                    .ToList();
                int changed = pawns.Count(p => !string.Equals(p.dutyBefore, p.dutyAfter, StringComparison.Ordinal));

                return new
                {
                    success = true,
                    lordIndex,
                    lordLoadID = lord.loadID,
                    faction = lord.faction != null ? lord.faction.Name : null,
                    pawnCount,
                    constructorUsed = jobType.Name + "(" + string.Join(", ",
                        chosen.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name).ToArray()) + ")",
                    argumentsBound = supplied.Keys.ToList(),
                    jobBefore,
                    jobAfter = LordJobName(lord),
                    toilBefore,
                    toilAfter = LordToilName(lord),
                    graphToilCount,
                    pawns,
                    dutiesChanged = changed,
                    // ⚠️ Not an error. Some LordToils issue the SAME duty def the old one
                    // did, so a zero here means "re-issued identically", not "did nothing".
                    // The toil names and jobAfter are what settle it.
                    dutiesUnchangedNote = changed == 0
                        ? "No duty DEF changed. UpdateAllDuties did run; a toil may legitimately issue the same duty def. Read toilAfter and jobAfter."
                        : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
#endif
    }
}
