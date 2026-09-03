// JawaBenchNeedsTools.cs - pawn state/health and needs/mood/mental-state tools.
//
// WHY THIS FILE EXISTS
// =====================
// `BRIDGE_TOOLS_EASY_BLOCK_1`, Group A: 9 EASY capabilities from the owner's cull -
// `design/Jawa/bridge/dll_capability_roster.html` - covering "Pawn state & health"
// and "Needs, mood & mental state". Every anchor below was read from 1.6 decompiled
// source (rimsage), not guessed:
//   Verse/Pawn_HealthTracker.cs      RestorePart(BodyPartRecord, Hediff, bool)
//   Verse/HealthUtility.cs           DamageUntilDowned / DamageUntilDead
//   Verse/Pawn.cs:3346                Kill(DamageInfo?, Hediff)
//   RimWorld/ResurrectionUtility.cs  TryResurrect(Pawn, ResurrectionParams)
//   RimWorld/ResurrectionParams.cs   the full field list (14 bools/floats)
//   RimWorld/Pawn_NeedsTracker.cs    AddOrRemoveNeedsAsAppropriate()
//   RimWorld/ThoughtHandler.cs       GetAllMoodThoughts(List<Thought>), TotalMoodOffset()
//   RimWorld/MemoryThoughtHandler.cs TryGainMemory(ThoughtDef, Pawn, Precept),
//                                    RemoveMemoriesOfDef, RemoveMemoriesOfDefWhereOtherPawnIs
//   Verse/AI/MentalBreaker.cs        TryDoMentalBreak(string, MentalBreakDef),
//                                    TryGetRandomMentalBreak(MentalBreakIntensity, out),
//                                    BreakThresholdMinor / Major / Extreme (floats, 0-1)
//   RimWorld/SituationalThoughtHandler.cs  Notify_SituationalThoughtsDirty()
//
// 🔴 OVERLAP, NOTED NOT HIDDEN: `jawa/pawn_health` (JawaBenchPawnTools.cs)
// already exposes a BLUNT restore (RestorePart(part) - the 1-arg overload, no
// diffException, no checkStateChange), and `jawa/pawn_need` already exposes a
// BLUNT add-memory (TryGainMemory(def, otherPawn), no remove, no Precept). This
// file's roster row asked for the FULL signatures, so `jawa/pawn_restore_part`
// and `jawa/pawn_memory` expose the extra parameters those blunt tools don't -
// they are not redundant, they are the fine-grained siblings.
//
// THE REFRESH TRAPS THIS FILE HANDLES:
//  * MentalBreaker.TryDoMentalBreak(reason, breakDef) calls breakDef.Worker
//    with NO NULL CHECK - a null breakDef is a NullReferenceException, not a
//    graceful refusal. When the caller omits breakDef this tool picks one with
//    TryGetRandomMentalBreak(intensity, out breakDef) FIRST and refuses if that
//    also comes up empty, so the crash never reaches the game.
//  * MemoryThoughtHandler.TryGainMemory silently NO-OPS a social
//    (Thought_MemorySocial) thought when both the def's own otherPawn and the
//    otherPawn argument are null - it never throws, never returns a bool, and
//    the memory list is simply unchanged. This tool checks ThoughtDef.IsSocial
//    BEFORE calling and refuses instead of eating the silent drop.
//  * Every mood poke (need write, memory add/remove, mental break) leaves
//    SituationalThoughtHandler's cache stale until something calls
//    Notify_SituationalThoughtsDirty() or 100 ticks pass - so pawn_thoughts,
//    pawn_memory and pawn_force_mental_break all call it themselves before
//    reading back, and it is also exposed standalone as pawn_dirty_situational
//    for a caller who pokes mood some other way (e.g. a raw hediff edit).
//  * HealthUtility.DamageUntilDowned/DamageUntilDead and Pawn.Kill all mutate
//    health directly with no return value - this tool reads back p.Downed /
//    p.Dead afterward so a silent no-op (e.g. an immune/incapable-of-death
//    race) cannot be mistaken for success.
//  * ResurrectionUtility.TryResurrect returns bool AND early-outs (still
//    returning false, not throwing) when the pawn isn't Dead, is Discarded, or
//    is an Anomaly UnnaturalCorpse - this tool surfaces that bool rather than
//    reporting success regardless.
//
// THREAD AFFINITY: same rule as every other file here. Everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  PAWN STATE & HEALTH
        // ================================================================

        [Tool(
            "jawa/pawn_restore_part",
            Description =
                "Regrow a destroyed limb or organ via the FULL " +
                "Pawn_HealthTracker.RestorePart(BodyPartRecord, Hediff, bool) signature - " +
                "the fine-grained sibling of jawa/pawn_health's action='restore', which only " +
                "calls the 1-arg overload. 🔴 RECURSIVE AND DESTRUCTIVE: it walks into every " +
                "child part too and wipes their hediffs, so it is gated behind " +
                "confirmDestructive=true. 'keepHediff' lets one hediff on the part survive the " +
                "wipe (the diffException argument); 'checkStateChange' controls whether " +
                "downed/dead state is re-evaluated immediately after (default true).",
            ResultDescription =
                "success, the part restored, whether it was actually missing beforehand, and " +
                "the pawn's hediff list read back afterward. A silent no-op is impossible to " +
                "mistake for success: missingBefore/missingAfter AND hediffCountBefore/hediffCount " +
                "are all reported, and 'changed' is true if either pair moved - a part that was " +
                "not missing shows its work only in the hediff count.")]
        public static async Task<object> PawnRestorePart(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "BodyPartDef name, e.g. Leg, Eye, Hand.")] string bodyPart = null,
            [ToolParameter(Description = "HediffDef to LEAVE ON the part instead of wiping it (the diffException argument). Omit to wipe everything on the part.")]
            string keepHediff = null,
            [ToolParameter(Description = "Re-evaluate downed/dead state immediately after. Default true.")]
            bool checkStateChange = true,
            [ToolParameter(Description = "Required - RestorePart is recursive and destructive into child parts.")]
            bool confirmDestructive = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.health == null) return Fail("Pawn has no health tracker.");
                if (!confirmDestructive)
                    return Fail("RestorePart is RECURSIVE into child parts, wipes their hediffs and does not drop what it removes. Pass confirmDestructive=true if that is what you want.");
                if (string.IsNullOrEmpty(bodyPart)) return Fail("Give a bodyPart.");
                string perr; var part = FindBodyPart(p, bodyPart, out perr);
                if (part == null) return Fail(perr);

                bool missingBefore = p.health.hediffSet.PartIsMissing(part);
                // RestorePart's main effect on a part that is NOT missing is wiping the hediffs on
                // it and every child part, which PartIsMissing cannot see - without a hediff count
                // taken BEFORE, that whole case reads identically to a no-op.
                int hediffCountBefore = p.health.hediffSet.hediffs.Count;

                Hediff exception = null;
                if (!string.IsNullOrEmpty(keepHediff))
                {
                    var hd = DefDatabase<HediffDef>.GetNamedSilentFail(keepHediff.Trim());
                    if (hd == null) return Fail("No HediffDef '" + keepHediff + "'.", DefSuggestions<HediffDef>(keepHediff));
                    exception = p.health.hediffSet.hediffs.FirstOrDefault(h => h.def == hd && h.Part == part);
                    if (exception == null)
                        return Fail("Pawn has no '" + hd.defName + "' hediff on " + part.def.defName + " to keep.");
                }

                p.health.RestorePart(part, exception, checkStateChange);

                bool missingAfter = p.health.hediffSet.PartIsMissing(part);
                var hediffs = p.health.hediffSet.hediffs
                    .Select(h => new { def = h.def.defName, part = h.Part != null ? h.Part.def.defName : null, severity = h.Severity })
                    .Take(40).ToList();

                return (object)new
                {
                    success = true,
                    part = part.def.defName,
                    keptHediff = exception != null ? exception.def.defName : null,
                    missingBefore,
                    missingAfter,
                    hediffCountBefore,
                    changed = missingBefore != missingAfter || hediffCountBefore != p.health.hediffSet.hediffs.Count,
                    downed = p.Downed,
                    dead = p.Dead,
                    hediffCount = p.health.hediffSet.hediffs.Count,
                    hediffs,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_force_incapacitate",
            Description =
                "Deterministic incapacitation with NO combat - action='downed' calls " +
                "HealthUtility.DamageUntilDowned, action='dead' calls " +
                "HealthUtility.DamageUntilDead, action='kill' calls Pawn.Kill(null) directly " +
                "(a clean death with no damage source, skipping HealthUtility's injury " +
                "simulation entirely). All three mutate health in place and return nothing, " +
                "so this reads p.Downed/p.Dead back afterward rather than assuming the call " +
                "worked.",
            ResultDescription = "success, action, downed/dead BEFORE and AFTER (so a no-op is visible), allowBleedingWoundsHonoured (false for 'dead' and 'kill' - see the parameter), and a health snapshot.")]
        public static async Task<object> PawnForceIncapacitate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'downed' | 'dead' | 'kill'.")] string action = "downed",
            [ToolParameter(Description = "Allow bleeding wounds. ⚠️ action='downed' ONLY - HealthUtility.DamageUntilDead(Pawn, DamageDef, ThingDef, BodyPartGroupDef) has no such parameter and Pawn.Kill deals no damage at all, so this is silently ignored for 'dead' and 'kill'. The result says which. Default true.")]
            bool allowBleedingWounds = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.health == null) return Fail("Pawn has no health tracker.");
                string A = (action ?? "downed").Trim().ToLowerInvariant();

                bool downedBefore = p.Downed, deadBefore = p.Dead;

                if (A == "downed") HealthUtility.DamageUntilDowned(p, allowBleedingWounds);
                else if (A == "dead") HealthUtility.DamageUntilDead(p);
                else if (A == "kill") p.Kill(null);
                else return Fail("action must be downed|dead|kill.");

                return (object)new
                {
                    success = true,
                    action = A,
                    allowBleedingWoundsHonoured = A == "downed" ? (bool?)allowBleedingWounds : null,
                    downedBefore, deadBefore,
                    downedAfter = p.Downed,
                    deadAfter = p.Dead,
                    changed = (downedBefore != p.Downed) || (deadBefore != p.Dead),
                    hediffCount = p.health.hediffSet.hediffs.Count,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_resurrect",
            Description =
                "Corpse back on its feet via ResurrectionUtility.TryResurrect(Pawn, " +
                "ResurrectionParams). ⛔ TryResurrect early-outs and returns FALSE, not an " +
                "exception, when the pawn is not Dead, is Discarded, or (Anomaly active) is an " +
                "UnnaturalCorpse - this tool surfaces that bool instead of reporting success " +
                "regardless. Side effects (restoreMissingParts, scars, spawning, the died-" +
                "thoughts removal, an invisible stun) are all exposed and default to what " +
                "ResurrectionParams itself defaults to.",
            ResultDescription = "success, resurrected (the real bool from TryResurrect), dead before/after, spawned, and a health/needs snapshot.")]
        public static async Task<object> PawnResurrect(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name of a DEAD pawn. Searched for among spawned pawns, world pawns alive or dead, and the inner pawn of every corpse on every map - including corpses held inside graves, caskets and containers.")] string pawn = null,
            [ToolParameter(Description = "RestorePart every missing/destroyed body part. Default true.")]
            bool restoreMissingParts = true,
            [ToolParameter(Description = "Chance [0-1] of a scar hediff per restored part. Default 0.")]
            float gettingScarsChance = 0f,
            [ToolParameter(Description = "Do not GenSpawn the pawn back onto the map even if its corpse was spawned. Default false.")]
            bool dontSpawn = false,
            [ToolParameter(Description = "Strip the DiedFrom/PawnDied memory thoughts colonists gained. Default true.")]
            bool removeDiedThoughts = true,
            [ToolParameter(Description = "Do not raise an assault Lord for a hostile faction's resurrected pawn. Default false.")]
            bool noLord = false,
            [ToolParameter(Description = "Stun the pawn for 5s, invisibly, right after resurrecting. Default false.")]
            bool invisibleStun = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                Pawn target = p;
                if (target == null && !string.IsNullOrEmpty(pawn))
                {
                    // 🔴 THE CORPSE IS A CONTAINER. FindPawn walks spawned map pawns and
                    // WorldPawns.AllPawnsAlive - a dead pawn is in NEITHER. Pawn.Kill despawns the
                    // pawn and hands it to a Corpse (Verse/Pawn.cs), and only a pawn separately
                    // passed to the world reaches WorldPawns, so the single commonest resurrect
                    // target - a fresh corpse lying on the map, or one in a grave, casket or
                    // container - used to read back as "no pawn matching". Search the dead world
                    // pawns AND every corpse's InnerPawn, recursively through thing holders.
                    string id = pawn.Trim();
                    if (id.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) && id.Length > 6)
                        id = id.Substring(6);
                    int n; bool numeric = int.TryParse(id, out n);
                    Func<Pawn, bool> matches = x =>
                        x != null && ((numeric && x.thingIDNumber == n)
                        || string.Equals(x.ThingID, id, StringComparison.OrdinalIgnoreCase)
                        || (x.Name != null && (string.Equals(x.Name.ToStringShort, id, StringComparison.OrdinalIgnoreCase) ||
                                               string.Equals(x.Name.ToStringFull, id, StringComparison.OrdinalIgnoreCase))));

                    var worldPawns = Find.WorldPawns != null ? Find.WorldPawns.AllPawnsAliveOrDead : null;
                    if (worldPawns != null) target = worldPawns.FirstOrDefault(x => matches(x));

                    if (target == null)
                    {
                        var corpses = new List<Corpse>();
                        foreach (var m in (Find.Maps ?? new List<Map>()))
                        {
                            ThingOwnerUtility.GetAllThingsRecursively(m, ThingRequest.ForGroup(ThingRequestGroup.Corpse), corpses, true);
                            var hit = corpses.FirstOrDefault(c => c != null && matches(c.InnerPawn));
                            if (hit != null) { target = hit.InnerPawn; break; }
                        }
                    }
                }
                if (target == null) return Fail("No pawn matching '" + pawn + "' among spawned pawns, world pawns (alive or dead), or the inner pawn of any corpse on any map (including corpses inside graves, caskets and other containers).");
                if (!target.Dead) return Fail("Pawn '" + target.LabelShortCap + "' is not Dead - TryResurrect logs an error and does nothing to a living pawn.");
                if (target.Discarded) return Fail("Pawn '" + target.LabelShortCap + "' is Discarded - TryResurrect refuses discarded pawns.");

                bool deadBefore = target.Dead;
                var parms = new ResurrectionParams
                {
                    restoreMissingParts = restoreMissingParts,
                    gettingScarsChance = gettingScarsChance,
                    dontSpawn = dontSpawn,
                    removeDiedThoughts = removeDiedThoughts,
                    noLord = noLord,
                    invisibleStun = invisibleStun,
                };

                bool resurrected;
                try { resurrected = ResurrectionUtility.TryResurrect(target, parms); }
                catch (Exception e) { return Fail("TryResurrect threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    resurrected,
                    deadBefore,
                    deadAfter = target.Dead,
                    spawned = target.Spawned,
                    thingId = target.ThingID,
                    label = target.LabelShortCap,
                    hediffCount = target.health != null ? target.health.hediffSet.hediffs.Count : 0,
                    needCount = target.needs != null ? target.needs.AllNeeds.Count : 0,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  NEEDS, MOOD & MENTAL STATE
        // ================================================================

        [Tool(
            "jawa/pawn_refresh_needs",
            Description =
                "Pawn_NeedsTracker.AddOrRemoveNeedsAsAppropriate() - walk every NeedDef and " +
                "add the ones ShouldHaveNeed now says yes to, remove the ones it says no to. " +
                "Call this AFTER a gene, trait or hediff edit changed which needs a pawn " +
                "should carry (e.g. a gene that removes the need for Rest, or a hediff that " +
                "adds a new addiction-style need) - none of the direct field edits refresh the " +
                "need LIST themselves, only need LEVELS.",
            ResultDescription = "success, the need list before and after (defName sets), added[], removed[].")]
        public static async Task<object> PawnRefreshNeeds(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.needs == null) return Fail("Pawn has no needs tracker.");

                var before = p.needs.AllNeeds.Select(n => n.def.defName).ToList();
                p.needs.AddOrRemoveNeedsAsAppropriate();
                var after = p.needs.AllNeeds.Select(n => n.def.defName).ToList();

                return (object)new
                {
                    success = true,
                    before,
                    after,
                    added = after.Except(before).ToList(),
                    removed = before.Except(after).ToList(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_thoughts",
            Description =
                "Every MOOD thought currently affecting a pawn, via " +
                "ThoughtHandler.GetAllMoodThoughts (memories with a non-zero mood offset, plus " +
                "the active situational thoughts) and ThoughtHandler.TotalMoodOffset() for the " +
                "grand total. ⚠️ GetAllMoodThoughts is NOT deduplicated - several thoughts of one " +
                "stack group are each listed, so the per-thought moodOffset values do NOT sum to " +
                "totalMoodOffset, which RimWorld builds from DISTINCT groups with each group's " +
                "stackedEffectMultiplier falloff applied. distinctGroupCount says how many groups " +
                "the total was actually assembled from. READ ONLY - it changes nothing, except that it calls " +
                "Notify_SituationalThoughtsDirty() FIRST so the situational half is not " +
                "reading a stale cache (situational thoughts otherwise only refresh every " +
                "100 ticks or on the next natural poke).",
            ResultDescription = "success, totalMoodOffset, thoughtCount (raw, undeduplicated), distinctGroupCount (the stack groups totalMoodOffset was built from), and per thought: def, label, moodOffset, isSocial, otherPawn (social only), stage.")]
        public static async Task<object> PawnThoughts(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.needs == null || p.needs.mood == null)
                    return Fail("Pawn has no mood need, so it cannot hold thoughts.");

                var handler = p.needs.mood.thoughts;
                handler.situational.Notify_SituationalThoughtsDirty();

                var raw = new List<Thought>();
                handler.GetAllMoodThoughts(raw);
                var distinct = new List<Thought>();
                handler.GetDistinctMoodThoughtGroups(distinct);

                var rows = raw.Select(t =>
                {
                    var social = t as ISocialThought;
                    return (object)new
                    {
                        def = t.def.defName,
                        label = t.LabelCap,
                        moodOffset = t.MoodOffset(),
                        isSocial = social != null,
                        otherPawn = social != null ? social.OtherPawn()?.LabelShortCap : null,
                        stage = t.CurStageIndex,
                    };
                }).ToList();

                return (object)new
                {
                    success = true,
                    totalMoodOffset = handler.TotalMoodOffset(),
                    curMoodLevel = p.needs.mood.CurLevel,
                    thoughtCount = rows.Count,
                    distinctGroupCount = distinct.Count,
                    thoughts = rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_memory",
            Description =
                "Inject or clear a memory thought via MemoryThoughtHandler - the FULL " +
                "signature (ThoughtDef, otherPawn, Precept) as fine control over " +
                "jawa/pawn_need's blunt action='thought' add-only path. action='add' calls " +
                "TryGainMemory; action='remove' calls RemoveMemoriesOfDef (or, with an " +
                "otherPawn given, the scoped RemoveMemoriesOfDefWhereOtherPawnIs so only that " +
                "relationship's copy is cleared). ⛔ A SOCIAL memory thought " +
                "(ThoughtDef.IsSocial) with NEITHER an otherPawn argument NOR one baked into " +
                "the def is DROPPED SILENTLY by RimWorld - TryGainMemory neither throws nor " +
                "returns a bool, the memory list is just unchanged. This tool checks IsSocial " +
                "BEFORE calling and REFUSES instead of eating that silent drop. Notifies " +
                "SituationalThoughtsDirty afterward so the mood change is visible immediately.",
            ResultDescription = "success, action, thought def, memoryCountBefore/After (so a silent drop is visible even though the underlying call never errors), and the memory list.")]
        public static async Task<object> PawnMemory(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'add' | 'remove'.")] string action = "add",
            [ToolParameter(Description = "ThoughtDef name.")] string thought = null,
            [ToolParameter(Description = "Other pawn id or name. Required for a social thought on add; scopes the removal on remove.")]
            string otherPawn = null,
            [ToolParameter(Description = "PreceptDef name (Ideology) sourcing this memory. Optional, add only.")]
            string precept = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.needs == null || p.needs.mood == null) return Fail("Pawn has no mood need, so it cannot hold thoughts.");
                if (string.IsNullOrEmpty(thought)) return Fail("Give a ThoughtDef.");
                var td = DefDatabase<ThoughtDef>.GetNamedSilentFail(thought.Trim());
                if (td == null) return Fail("No ThoughtDef '" + thought + "'.", DefSuggestions<ThoughtDef>(thought));
                if (!td.IsMemory) return Fail("'" + td.defName + "' is not a memory thought (ThoughtDef.IsMemory is false).");

                Pawn other = null;
                if (!string.IsNullOrEmpty(otherPawn))
                {
                    string e2; other = FindPawn(otherPawn, out e2);
                    if (other == null) return Fail("otherPawn: " + e2);
                }

                var memories = p.needs.mood.thoughts.memories;
                string A = (action ?? "add").Trim().ToLowerInvariant();
                int before = memories.Memories.Count;

                if (A == "add")
                {
                    if (td.IsSocial && other == null)
                        return Fail("'" + td.defName + "' is a SOCIAL thought and needs an otherPawn. Without one RimWorld drops it silently - refusing instead.");
                    Precept prec = null;
                    if (!string.IsNullOrEmpty(precept))
                    {
                        var pd = DefDatabase<PreceptDef>.GetNamedSilentFail(precept.Trim());
                        if (pd == null) return Fail("No PreceptDef '" + precept + "'.", DefSuggestions<PreceptDef>(precept));
                        prec = p.Ideo != null ? p.Ideo.PreceptsListForReading.FirstOrDefault(x => x.def == pd) : null;
                        if (prec == null) return Fail("Pawn's ideo has no precept of def '" + pd.defName + "'.");
                    }
                    memories.TryGainMemory(td, other, prec);
                }
                else if (A == "remove")
                {
                    if (other != null) memories.RemoveMemoriesOfDefWhereOtherPawnIs(td, other);
                    else memories.RemoveMemoriesOfDef(td);
                }
                else return Fail("action must be add|remove.");

                p.needs.mood.thoughts.situational.Notify_SituationalThoughtsDirty();
                int after = memories.Memories.Count;

                return (object)new
                {
                    success = true,
                    action = A,
                    thought = td.defName,
                    otherPawn = other != null ? other.LabelShortCap : null,
                    memoryCountBefore = before,
                    memoryCountAfter = after,
                    changed = before != after,
                    memories = memories.Memories.Select(m => new { def = m.def.defName, otherPawn = m.otherPawn != null ? m.otherPawn.LabelShortCap : null, age = m.age }).Take(40).ToList(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_force_mental_break",
            Description =
                "A specific or random mood-caused mental break via " +
                "MentalBreaker.TryDoMentalBreak(reason, MentalBreakDef). ⛔ TryDoMentalBreak " +
                "calls breakDef.Worker with NO NULL CHECK - passing a null def crashes rather " +
                "than refusing. When 'breakDef' is omitted this tool picks one itself with " +
                "TryGetRandomMentalBreak(intensity), and REFUSES if none is available at that " +
                "intensity rather than risking the crash. TryDoMentalBreak also returns FALSE " +
                "SILENTLY (CanHaveMentalBreak() gate: pawn downed, asleep, already in a " +
                "mental state, or blocked) - this tool surfaces that bool.",
            ResultDescription = "success, started (the real bool), breakDef actually used, current mental state before/after.")]
        public static async Task<object> PawnForceMentalBreak(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "MentalBreakDef name. Omit to pick one randomly for 'intensity'.")]
            string breakDef = null,
            [ToolParameter(Description = "'minor' | 'major' | 'extreme'. Used only when breakDef is omitted. Default minor.")]
            string intensity = "minor",
            [ToolParameter(Description = "Text shown as the break's cause. Default a bridge-authored reason.")]
            string reason = "Forced via bridge")
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.mindState == null || p.mindState.mentalBreaker == null)
                    return Fail("Pawn has no mental breaker (animals and mechs may not).");

                MentalBreakDef bd = null;
                if (!string.IsNullOrEmpty(breakDef))
                {
                    bd = DefDatabase<MentalBreakDef>.GetNamedSilentFail(breakDef.Trim());
                    if (bd == null) return Fail("No MentalBreakDef '" + breakDef + "'.", DefSuggestions<MentalBreakDef>(breakDef));
                }
                else
                {
                    MentalBreakIntensity mbi;
                    switch ((intensity ?? "minor").Trim().ToLowerInvariant())
                    {
                        case "major": mbi = MentalBreakIntensity.Major; break;
                        case "extreme": mbi = MentalBreakIntensity.Extreme; break;
                        case "minor": mbi = MentalBreakIntensity.Minor; break;
                        default: return Fail("intensity must be minor|major|extreme.");
                    }
                    if (!p.mindState.mentalBreaker.TryGetRandomMentalBreak(mbi, out bd) || bd == null)
                        return Fail("No MentalBreakDef available for intensity '" + intensity + "' on this pawn right now - refusing rather than calling TryDoMentalBreak with a null def, which crashes.");
                }

                string before = p.MentalState != null ? p.MentalState.def.defName : null;
                bool started;
                try { started = p.mindState.mentalBreaker.TryDoMentalBreak(reason ?? "Forced via bridge", bd); }
                catch (Exception e) { return Fail("TryDoMentalBreak threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    started,
                    breakDef = bd.defName,
                    reason = reason ?? "Forced via bridge",
                    mentalStateBefore = before,
                    mentalStateAfter = p.MentalState != null ? p.MentalState.def.defName : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_break_thresholds",
            Description =
                "MentalBreaker.BreakThresholdMinor / Major / Extreme - the mood levels " +
                "(0-1, same scale as needs.mood.CurLevel) below which a minor/major/extreme " +
                "mental break becomes possible, plus how close the pawn's ACTUAL current " +
                "mood is to each. READ ONLY. The thresholds derive from the pawn's " +
                "MentalBreakThreshold stat, so they differ pawn to pawn (traits, xenotype, " +
                "difficulty).",
            ResultDescription = "success, curMood, thresholdMinor/Major/Extreme, marginToMinor/Major/Extreme (curMood minus threshold - negative means already past it), and the BreakXIsImminent bools RimWorld itself uses.")]
        public static async Task<object> PawnBreakThresholds(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.mindState == null || p.mindState.mentalBreaker == null)
                    return Fail("Pawn has no mental breaker (animals and mechs may not).");
                if (p.needs == null || p.needs.mood == null)
                    return Fail("Pawn has no mood need, so break thresholds do not apply.");

                var mb = p.mindState.mentalBreaker;
                float curMood = p.needs.mood.CurLevel;

                return (object)new
                {
                    success = true,
                    curMood,
                    thresholdMinor = mb.BreakThresholdMinor,
                    thresholdMajor = mb.BreakThresholdMajor,
                    thresholdExtreme = mb.BreakThresholdExtreme,
                    marginToMinor = curMood - mb.BreakThresholdMinor,
                    marginToMajor = curMood - mb.BreakThresholdMajor,
                    marginToExtreme = curMood - mb.BreakThresholdExtreme,
                    minorIsImminent = mb.BreakMinorIsImminent,
                    majorIsImminent = mb.BreakMajorIsImminent,
                    extremeIsImminent = mb.BreakExtremeIsImminent,
                    blocked = mb.Blocked,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_dirty_situational",
            Description =
                "SituationalThoughtHandler.Notify_SituationalThoughtsDirty() - drop the " +
                "cached situational-thought list and force a full recompute on next read. " +
                "🔑 REQUIRED after most mood pokes (a hediff, a trait, a gene, an ideo precept " +
                "edit) or the change does not show for up to 100 ticks, because situational " +
                "thoughts otherwise only refresh on their own interval. jawa/pawn_thoughts, " +
                "jawa/pawn_memory and jawa/pawn_force_mental_break already call this " +
                "themselves - use this tool standalone after some OTHER edit (a raw hediff or " +
                "gene write) that those tools didn't make.",
            ResultDescription = "success, and totalMoodOffset read back immediately after the dirty (proof the recompute happened).")]
        public static async Task<object> PawnDirtySituational(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.needs == null || p.needs.mood == null)
                    return Fail("Pawn has no mood need, so it has no situational thought handler.");

                p.needs.mood.thoughts.situational.Notify_SituationalThoughtsDirty();
                float total = p.needs.mood.thoughts.TotalMoodOffset();

                return (object)new
                {
                    success = true,
                    totalMoodOffsetAfterDirty = total,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
