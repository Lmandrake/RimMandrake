// JawaBenchGroupTools.cs - Lords/raids, Factions, Caravans/settlements and Ideology.
//
// BRIDGE_TOOLS_EASY_BLOCK_1, Group F, out of
// infrastructure/state/work/BRIDGE_TOOLS_EASY_REMAINING.md.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/AI/Group/Lord.cs, Verse/AI/Group/LordManager.cs,
//   Verse/AI/Group/LordUtility.cs, RimWorld/Signal.cs, RimWorld/SignalManager.cs,
//   RimWorld/IncidentParms.cs, RimWorld/Faction.cs,
//   RimWorld/Planet/SettleUtility.cs, RimWorld/Planet/CaravanMaker.cs,
//   RimWorld/Planet/Caravan.cs, RimWorld/Planet/Caravan_PathFollower.cs,
//   RimWorld/Planet/SettlementUtility.cs, RimWorld/Planet/PlanetTile.cs,
//   RimWorld/FactionIdeosTracker.cs, RimWorld/IdeoDevelopmentTracker.cs,
//   RimWorld/Precept_Role.cs, RimWorld/Precept_RoleSingle.cs,
//   RimWorld/Precept_RoleMulti.cs, RimWorld/Precept.cs, RimWorld/Ideo.cs.
//
// GATING follows the rule stated in JawaBenchEventTools.cs and JawaBenchSimTools.cs:
// #if JAWA_GM_TOOLS is for tools that make THE WORLD ACT on the player (an
// incident, a raid, hostile AI responding on its own) - not for tools that
// change only what the caller named. On that test:
//   GATED:   jawa/lord_poke (a memo/signal hands control to the Lord's own
//            StateGraph - what happens next is the AI's decision, not ours),
//            jawa/raid_shape_fire (fires a real raid), jawa/settlement_attack
//            (generates a hostile map and lets its defenders react).
//   UNGATED: everything else here sets a named field on a named object, the
//            same category jawa/faction_relations_set and jawa/set_pawn_ideo
//            already occupy ungated.
//
// A FEW THINGS THE SOURCE SAYS THAT SHAPE THIS FILE:
//   * Lord.CanAddPawn returns a bare bool - no reason string. A refusal here
//     is reported as exactly that: the engine does not explain itself further.
//   * Find.SignalManager.SendSignal is GLOBAL - it reaches every
//     ISignalReceiver process-wide, not just Lords on the current map.
//   * FactionIdeosTracker.SetPrimary is `primaryIdeo = ideo;` and nothing
//     else - no believer migration, no letter, no ideosMinor update.
//   * Precept_RoleMulti.Assign performs NO validation at all; Precept_RoleSingle
//     only Log.Errors on an invalid pawn and assigns anyway. Neither refuses,
//     so this file does not pretend the engine gates it - IsAssigned is read
//     back before and after instead.
//   * SettlementUtility.Attack calls AffectRelationsOnAttacked internally,
//     which is the ONLY goodwill hit applied - this file never applies a
//     second one.
//
// THREAD AFFINITY: same rule as every other file here - everything that
// touches game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  Lords, raids & AI groups
        // ================================================================

        [Tool(
            "jawa/lord_pawn_move",
            Description =
                "List every Lord on the current map, or move a NAMED pawn into or out of a " +
                "NAMED Lord. 'list' is read-only and shows the index each Lord answers to " +
                "(job type, faction, member count) - nothing else on this bridge can see a " +
                "Lord at all. 'attach' gates on Lord.CanAddPawn(p) first and refuses rather " +
                "than calling AddPawn blind; 'detach' finds the pawn's OWN current Lord via " +
                "LordUtility.GetLord and removes it from there, so 'lordIndex' is not needed " +
                "for detach. ⚠️ CanAddPawn returns a bare bool with no reason string - a " +
                "refusal here is reported exactly that plainly, because the engine does not " +
                "explain itself further.",
            ResultDescription =
                "success, action, lords[] (index, job, faction, pawnCount) for 'list'; for " +
                "attach/detach: pawn, lordIndexBefore, lordIndexAfter (-1 = none), and whether " +
                "the pawn's Lord after the call matches what was requested.")]
        public static async Task<object> LordPawnMove(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'list' (default), 'attach' or 'detach'.")]
            string action = "list",
            [ToolParameter(Description = "Pawn id, thingId or name, as accepted by every other pawn tool. Required for attach/detach.")]
            string pawn = null,
            [ToolParameter(Description = "Index into the 'list' rows - the Lord to attach into. Required for attach; ignored for detach.")]
            int lordIndex = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var lm = map.lordManager;

                Func<List<object>> rows = () => lm.lords.Select((l, i) => (object)new
                {
                    index = i,
                    job = l.LordJob != null ? l.LordJob.GetType().Name : "(null)",
                    faction = l.faction != null ? l.faction.def.defName : null,
                    pawnCount = l.ownedPawns != null ? l.ownedPawns.Count : 0
                }).ToList();

                if (string.Equals(action, "list", StringComparison.OrdinalIgnoreCase))
                    return new { success = true, action = "list", count = lm.lords.Count, lords = rows(), ticksGame = TicksGameSafe() };

                if (string.IsNullOrWhiteSpace(pawn)) return Fail("Give 'pawn' for attach/detach.");
                string perr; var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");

                if (string.Equals(action, "detach", StringComparison.OrdinalIgnoreCase))
                {
                    var priorLord = p.GetLord();
                    if (priorLord == null) return Fail(p.LabelShortCap + " has no Lord to detach from.", rows());
                    int priorIndex = lm.lords.IndexOf(priorLord);
                    try { priorLord.RemovePawn(p); }
                    catch (Exception e) { return Fail("RemovePawn threw: " + e.GetType().Name + ": " + e.Message); }
                    var nowLord = p.GetLord();
                    return new
                    {
                        success = nowLord == null,
                        action = "detach",
                        pawn = p.LabelShortCap,
                        lordIndexBefore = priorIndex,
                        lordIndexAfter = nowLord != null ? lm.lords.IndexOf(nowLord) : -1,
                        ticksGame = TicksGameSafe()
                    };
                }

                if (string.Equals(action, "attach", StringComparison.OrdinalIgnoreCase))
                {
                    if (lordIndex < 0 || lordIndex >= lm.lords.Count)
                        return Fail("lordIndex " + lordIndex + " is out of range (0.." + (lm.lords.Count - 1) + "). Call 'list' first.", rows());
                    var lord = lm.lords[lordIndex];
                    var priorLord = p.GetLord();
                    int priorIndex = priorLord != null ? lm.lords.IndexOf(priorLord) : -1;

                    if (priorLord == lord)
                        return new { success = true, action = "attach", pawn = p.LabelShortCap, lordIndexBefore = priorIndex, lordIndexAfter = lordIndex, note = "Already a member of this Lord; nothing to do.", ticksGame = TicksGameSafe() };

                    bool can;
                    try { can = lord.CanAddPawn(p); }
                    catch (Exception e) { return Fail("CanAddPawn threw: " + e.GetType().Name + ": " + e.Message); }
                    if (!can)
                        return Fail("Lord.CanAddPawn(" + p.LabelShortCap + ") returned false for lordIndex " + lordIndex +
                                    " (job " + (lord.LordJob != null ? lord.LordJob.GetType().Name : "(null)") + "). " +
                                    "The engine gives no reason string beyond this.", rows());

                    try { lord.AddPawn(p); }
                    catch (Exception e) { return Fail("AddPawn threw: " + e.GetType().Name + ": " + e.Message); }
                    var nowLord = p.GetLord();
                    return new
                    {
                        success = nowLord == lord,
                        action = "attach",
                        pawn = p.LabelShortCap,
                        lordIndexBefore = priorIndex,
                        lordIndexAfter = nowLord != null ? lm.lords.IndexOf(nowLord) : -1,
                        ticksGame = TicksGameSafe()
                    };
                }

                return Fail("action must be 'list', 'attach' or 'detach'.");
            }).ConfigureAwait(false);
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/lord_poke",
            Description =
                "*** HANDS CONTROL TO THE LORD'S OWN STATE MACHINE *** Advance a Lord the way " +
                "vanilla scripts do: 'memo' calls Lord.ReceiveMemo(string) on one Lord (by " +
                "index from jawa/lord_pawn_move 'list'); 'signal' calls " +
                "Find.SignalManager.SendSignal, which is GLOBAL - it reaches every " +
                "ISignalReceiver process-wide, not just Lords on this map. What happens next " +
                "is decided by the target StateGraph, not by this call, which is why it sits " +
                "behind the GM gate with jawa/fire_raid and jawa/weather_set.",
            ResultDescription =
                "success, action, and CurLordToil's TYPE NAME before/after for every Lord on " +
                "the map - the only generic evidence a memo or signal did anything, since " +
                "ReceiveMemo and SendSignal both return void.")]
        public static async Task<object> LordPoke(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'memo' or 'signal'.")] string action = "memo",
            [ToolParameter(Description = "Lord index from jawa/lord_pawn_move 'list'. Required for 'memo'.")] int lordIndex = -1,
            [ToolParameter(Description = "The memo string. Required for 'memo'.")] string memo = null,
            [ToolParameter(Description = "The signal tag. Required for 'signal'.")] string signalTag = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var lm = map.lordManager;

                Func<Lord, string> toil = l => { try { return l.CurLordToil != null ? l.CurLordToil.GetType().Name : "(none)"; } catch { return "(error)"; } };
                var before = lm.lords.Select((l, i) => new { index = i, toil = toil(l) }).ToList();

                if (string.Equals(action, "memo", StringComparison.OrdinalIgnoreCase))
                {
                    if (lordIndex < 0 || lordIndex >= lm.lords.Count)
                        return Fail("lordIndex " + lordIndex + " is out of range (0.." + (lm.lords.Count - 1) + ").");
                    if (string.IsNullOrWhiteSpace(memo)) return Fail("Give 'memo'.");
                    var lord = lm.lords[lordIndex];
                    var beforeToil = toil(lord);
                    try { lord.ReceiveMemo(memo); }
                    catch (Exception e) { return Fail("ReceiveMemo threw: " + e.GetType().Name + ": " + e.Message); }
                    var afterToil = toil(lord);
                    return new
                    {
                        success = true,
                        action = "memo",
                        lordIndex,
                        memo,
                        toilBefore = beforeToil,
                        toilAfter = afterToil,
                        moved = beforeToil != afterToil,
                        note = beforeToil == afterToil
                            ? "CurLordToil did not change. That may be correct (the memo may only set internal LordJob state, not the toil) - it is not proof of failure by itself."
                            : "CurLordToil changed - the state graph transitioned.",
                        ticksGame = TicksGameSafe()
                    };
                }

                if (string.Equals(action, "signal", StringComparison.OrdinalIgnoreCase))
                {
                    if (string.IsNullOrWhiteSpace(signalTag)) return Fail("Give 'signalTag'.");
                    int receiverCount = Find.SignalManager != null && Find.SignalManager.receivers != null ? Find.SignalManager.receivers.Count : -1;
                    try { Find.SignalManager.SendSignal(new Signal(signalTag)); }
                    catch (Exception e) { return Fail("SendSignal threw: " + e.GetType().Name + ": " + e.Message); }
                    var after = lm.lords.Select((l, i) => new { index = i, toil = toil(l) }).ToList();
                    var moved = new List<int>();
                    for (int i = 0; i < before.Count && i < after.Count; i++)
                        if (before[i].toil != after[i].toil) moved.Add(i);

                    return new
                    {
                        success = true,
                        action = "signal",
                        signalTag,
                        broadcastToReceivers = receiverCount,
                        lordsMoved = moved,
                        lordsBefore = before,
                        lordsAfter = after,
                        note = "SendSignal is GLOBAL - it went to every ISignalReceiver, not only Lords on THIS map. lordsMoved lists only which of this map's Lords changed toil.",
                        ticksGame = TicksGameSafe()
                    };
                }

                return Fail("action must be 'memo' or 'signal'.");
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/raid_shape_fire",
            Description =
                "*** ACTS ON THE LIVE COLONY - THIS SENDS A REAL RAID *** Fires a raid the same " +
                "way jawa/fire_raid does, but exposes the four IncidentParms fields neither " +
                "jawa/fire_raid nor jawa/raid_preview can set: raidNeverFleeIndividual, " +
                "raidForceOneDowned, pawnGroupMakerSeed (biocode weapon/apparel handled via " +
                "biocodeWeaponsChance/biocodeApparelChance too). Use jawa/fire_raid for a plain " +
                "raid; use this one only when the shape itself is the point. dryRun defaults " +
                "true. 🔴 READ blockedByDialog BEFORE executed - a Harmony prefix can replace the " +
                "raid with a modal and still set __result = true, so Find.WindowStack is diffed " +
                "across the firing. Clear any modal with jawa/window_list_close.",
            ResultDescription =
                "success (executed AND not blocked), dryRun, resolved (the parms as SENT, " +
                "including the shape flags), canFireNow (dry run), or executed + windowsOpened[] " +
                "+ blockedByDialog + arrived[] (faction, pawnsArrived, counted off the map " +
                "before/after - not echoed from the request).")]
        public static async Task<object> RaidShapeFire(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Threat points. -1 uses the storyteller's current default.")] float points = -1f,
            [ToolParameter(Description = "FactionDef of the attacker. Empty lets the worker choose a hostile faction.")] string faction = null,
            [ToolParameter(Description = "Never let individual raiders flee.")] bool raidNeverFleeIndividual = false,
            [ToolParameter(Description = "Force exactly one pawn to be generated downed.")] bool raidForceOneDowned = false,
            [ToolParameter(Description = "Fixed seed for the pawn group maker, for reproducible raid rosters. -1 leaves it random.")] int pawnGroupMakerSeed = -1,
            [ToolParameter(Description = "0..1 chance raiders' weapons are biocoded to them. -1 leaves the storyteller default.")] float biocodeWeaponsChance = -1f,
            [ToolParameter(Description = "0..1 chance raiders' apparel is biocoded to them. -1 leaves the storyteller default.")] float biocodeApparelChance = -1f,
            [ToolParameter(Description = "Resolve and REPORT without firing. Default true - you must opt in to the raid.")] bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                IncidentParms parms;
                try { parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, map); }
                catch (Exception e) { return Fail("DefaultParmsNow threw: " + e.Message); }

                if (points >= 0f) parms.points = points;
                if (parms.points <= 0f) return Fail("points must be > 0 - IncidentWorker_RaidEnemy logs an error otherwise.");

                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    var f = Find.FactionManager.FirstFactionOfDef(fd);
                    if (f == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                    parms.faction = f;
                }
                if (parms.faction == null)
                {
                    parms.faction = Find.FactionManager.AllFactionsVisible
                        .Where(f => f != Faction.OfPlayer && f.HostileTo(Faction.OfPlayer)
                                    && !f.def.pawnGroupMakers.NullOrEmpty() && f.def.canStageAttacks)
                        .RandomElementWithFallback(null);
                }

                parms.raidNeverFleeIndividual = raidNeverFleeIndividual;
                parms.raidForceOneDowned = raidForceOneDowned;
                if (pawnGroupMakerSeed >= 0) parms.pawnGroupMakerSeed = pawnGroupMakerSeed;
                if (biocodeWeaponsChance >= 0f) parms.biocodeWeaponsChance = biocodeWeaponsChance;
                if (biocodeApparelChance >= 0f) parms.biocodeApparelChance = biocodeApparelChance;

                var resolved = new
                {
                    points = parms.points,
                    faction = parms.faction != null ? parms.faction.def.defName : "(none available)",
                    raidNeverFleeIndividual = parms.raidNeverFleeIndividual,
                    raidForceOneDowned = parms.raidForceOneDowned,
                    pawnGroupMakerSeed = parms.pawnGroupMakerSeed,
                    biocodeWeaponsChance = parms.biocodeWeaponsChance,
                    biocodeApparelChance = parms.biocodeApparelChance
                };

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        resolved,
                        canFireNow = IncidentDefOf.RaidEnemy.Worker.CanFireNow(parms),
                        note = "DRY RUN - nothing was sent. Pass dryRun=false to actually raid the colony.",
                        ticksGame = TicksGameSafe()
                    };

                var before = new Dictionary<Faction, int>();
                foreach (var p in map.mapPawns.AllPawnsSpawned)
                    if (p.Faction != null) before[p.Faction] = (before.TryGetValue(p.Faction, out var bn) ? bn : 0) + 1;

                // FIRE_RAID_REPORTS_MODAL_1 - diff the window stack across TryExecute.
                var windowIdsBefore = SnapshotWindowIds();

                bool executed;
                try { executed = IncidentDefOf.RaidEnemy.Worker.TryExecute(parms); }
                catch (Exception e) { return Fail("TryExecute threw: " + e.GetType().Name + ": " + e.Message); }

                var windowsOpened = WindowsOpenedSince(windowIdsBefore);

                var after = new Dictionary<Faction, int>();
                foreach (var p in map.mapPawns.AllPawnsSpawned)
                    if (p.Faction != null) after[p.Faction] = (after.TryGetValue(p.Faction, out var an) ? an : 0) + 1;
                var arrivals = new List<object>();
                foreach (var kv in after)
                {
                    int was; before.TryGetValue(kv.Key, out was);
                    if (kv.Value > was)
                        arrivals.Add(new { faction = kv.Key.def.defName, name = kv.Key.Name, pawnsArrived = kv.Value - was });
                }

                int pawnsArrivedTotal = 0;
                foreach (var a in arrivals)
                    pawnsArrivedTotal += (int)a.GetType().GetProperty("pawnsArrived").GetValue(a, null);
                bool blockedByDialog = windowsOpened.Count > 0 && pawnsArrivedTotal == 0;
                string swallowNote = DialogSwallowNote(windowsOpened, pawnsArrivedTotal == 0);

                return new
                {
                    success = executed && !blockedByDialog,
                    dryRun = false,
                    resolved,
                    executed,
                    windowsOpened,
                    blockedByDialog,
                    actualFaction = parms.faction != null ? parms.faction.def.defName : null,
                    arrived = arrivals,
                    pawnsArrivedTotal,
                    note = blockedByDialog
                        ? swallowNote
                        : (executed
                            ? "Raid fired. arrived[] is counted off the map; a delayed arrival mode can legitimately show 0 pawns this instant."
                            : "TryExecute returned false - the worker refused these parms."),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
#endif // JAWA_GM_TOOLS

        // ================================================================
        //  Factions & relations
        // ================================================================

        [Tool(
            "jawa/faction_goodwill_check",
            Description =
                "PRE-FLIGHT Faction.CanChangeGoodwillFor(other, goodwillChange) in both " +
                "directions before writing anything, so a caller can report the refusal " +
                "instead of finding out jawa/faction_relations_set silently wrote a record the " +
                "engine will never move. Read-only. Also surfaces the individual flags " +
                "CanChangeGoodwillFor itself reads (HasGoodwill, permanentEnemy, defeated) so a " +
                "false answer is not a black box.",
            ResultDescription =
                "success, a, b, goodwillChange, canChangeAtoB, canChangeBtoA (independent " +
                "reads - the checks are not always symmetric), currentGoodwillAtoB/BtoA, and " +
                "diagnostics{aHasGoodwill,bHasGoodwill,aPermanentEnemy,bPermanentEnemy," +
                "aDefeated,bDefeated} - the flags CanChangeGoodwillFor consults, read " +
                "independently so a false answer can be explained even when the engine's own " +
                "method gives no reason string.")]
        public static async Task<object> FactionGoodwillCheck(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "First faction defName.")] string faction,
            [ToolParameter(Description = "Second faction defName.")] string other,
            [ToolParameter(Description = "The goodwill delta to test. Default 1 (matches jawa/faction_relations_get's canChangeGoodwill column).")] int goodwillChange = 1)
        {
            if (string.IsNullOrWhiteSpace(faction)) return Fail("faction is required.");
            if (string.IsNullOrWhiteSpace(other)) return Fail("other is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.FactionManager == null) return Fail("No FactionManager. This needs a GAME loaded.");

                var fdA = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                if (fdA == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                var a = Find.FactionManager.FirstFactionOfDef(fdA);
                if (a == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");

                var fdB = DefDatabase<FactionDef>.GetNamedSilentFail(other.Trim());
                if (fdB == null) return Fail("No FactionDef '" + other + "'.", DefSuggestions<FactionDef>(other));
                var b = Find.FactionManager.FirstFactionOfDef(fdB);
                if (b == null) return Fail("FactionDef '" + other + "' exists but no such faction is in this world.");

                if (a == b) return Fail("A faction has no goodwill relation with itself.");

                bool aOk, bOk;
                try { aOk = a.CanChangeGoodwillFor(b, goodwillChange); }
                catch (Exception e) { return Fail("CanChangeGoodwillFor(a->b) threw: " + e.GetType().Name + ": " + e.Message); }
                try { bOk = b.CanChangeGoodwillFor(a, goodwillChange); }
                catch (Exception e) { return Fail("CanChangeGoodwillFor(b->a) threw: " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    a = a.def.defName,
                    b = b.def.defName,
                    goodwillChange,
                    canChangeAtoB = aOk,
                    canChangeBtoA = bOk,
                    currentGoodwillAtoB = a.GoodwillWith(b),
                    currentGoodwillBtoA = b.GoodwillWith(a),
                    diagnostics = new
                    {
                        aHasGoodwill = a.HasGoodwill,
                        bHasGoodwill = b.HasGoodwill,
                        aPermanentEnemy = a.def.permanentEnemy,
                        bPermanentEnemy = b.def.permanentEnemy,
                        aDefeated = a.defeated,
                        bDefeated = b.defeated
                    },
                    note = "Use this before jawa/faction_relations_set to avoid a write that the engine's own goodwill events will refuse to sustain.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/faction_flags_set",
            Description =
                "Set Faction.hidden, .defeated and/or .temporary directly - plain fields in 1.6 " +
                "source with NO setter side effects and no Notify_ call anywhere that touches " +
                "them, so this write IS the whole operation, same as vanilla debug tools do " +
                "(DebugActionsMisc sets .temporary the same way). Use this to take a faction " +
                "off the board without deleting it. 'hidden' is nullable: the def already has " +
                "its own default (FactionDef.hidden) and the EFFECTIVE value the game reads is " +
                "Faction.Hidden = (hidden ?? def.hidden) - both are reported so writing " +
                "hidden=false is visibly different from never having set it.",
            ResultDescription = "success, dryRun, faction, was{hidden,hiddenEffective,defeated,temporary}, now{...}.")]
        public static async Task<object> FactionFlagsSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "FactionDef defName.")] string faction,
            [ToolParameter(Description = "Set the stored hidden flag. Omit to leave it alone.")] bool? hidden = null,
            [ToolParameter(Description = "Set defeated. Omit to leave it alone.")] bool? defeated = null,
            [ToolParameter(Description = "Set temporary. Omit to leave it alone.")] bool? temporary = null,
            [ToolParameter(Description = "Report the current flags and change nothing.")] bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(faction)) return Fail("faction is required.");
            if (!hidden.HasValue && !defeated.HasValue && !temporary.HasValue && !dryRun)
                return Fail("Nothing to do: pass hidden, defeated and/or temporary.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                var f = Find.FactionManager != null ? Find.FactionManager.FirstFactionOfDef(fd) : null;
                if (f == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");

                Func<object> snapshot = () => new { hidden = f.hidden, hiddenEffective = f.Hidden, defeated = f.defeated, temporary = f.temporary };
                var was = snapshot();

                if (!dryRun)
                {
                    if (hidden.HasValue) f.hidden = hidden.Value;
                    if (defeated.HasValue) f.defeated = defeated.Value;
                    if (temporary.HasValue) f.temporary = temporary.Value;
                }
                var now = snapshot();

                return new { success = true, dryRun, faction = f.def.defName, was, now, ticksGame = TicksGameSafe() };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Settlements, caravans & gravship
        // ================================================================

        [Tool(
            "jawa/colony_found",
            Description =
                "SettleUtility.AddNewHome - place a new home Settlement WorldObject on a named " +
                "tile for a named faction (default 'Player'). ⚠️ Does NOT generate a map - the " +
                "map is built lazily the first time the tile is entered, same as clicking " +
                "'Settle' in the UI. Refuses if the tile already carries a Settlement rather " +
                "than silently overwriting it.",
            ResultDescription =
                "success, tile, faction, settlementId, name, limitReached (informational - " +
                "Prefs.MaxNumberOfPlayerSettlements is a UI cap AddNewHome itself does not " +
                "enforce, so this can be true and the call still succeeds).")]
        public static async Task<object> ColonyFound(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "World tile id.")] int tile = -1,
            [ToolParameter(Description = "FactionDef defName, or 'Player'/'PlayerColony' for the player faction.")] string faction = "Player",
            [ToolParameter(Description = "Rename the settlement after creation. Empty keeps the generated name.")] string name = null,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            if (tile < 0) return Fail("Give 'tile', a valid world tile id.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var grid = Find.WorldGrid;
                if (grid == null) return Fail("No WorldGrid. This needs a world loaded.");
                if (tile >= grid.TilesCount) return Fail("Tile " + tile + " out of range (0.." + (grid.TilesCount - 1) + ").");

                Faction fac;
                if (string.Equals(faction, "Player", StringComparison.OrdinalIgnoreCase)
                    || string.Equals(faction, "PlayerColony", StringComparison.OrdinalIgnoreCase))
                {
                    fac = Faction.OfPlayer;
                }
                else
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail((faction ?? "").Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager != null ? Find.FactionManager.FirstFactionOfDef(fd) : null;
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                }
                if (fac == null) return Fail("No player faction exists yet (Faction.OfPlayer is null).");

                var pt = new PlanetTile(tile, grid.Surface);
                var already = Find.WorldObjects.ObjectsAt(pt).OfType<Settlement>().FirstOrDefault();
                if (already != null)
                    return Fail("Tile " + tile + " already has a Settlement ('" + already.Name + "', faction " +
                                (already.Faction != null ? already.Faction.def.defName : "none") +
                                "). Use jawa/world_objects_set to move or re-faction it instead.");

                bool limitReached = fac == Faction.OfPlayer && SettleUtility.PlayerSettlementsCountLimitReached;

                if (dryRun)
                    return new { success = true, dryRun = true, tile, faction = fac.def.defName, limitReached, ticksGame = TicksGameSafe() };

                Settlement s;
                try { s = SettleUtility.AddNewHome(pt, fac); }
                catch (Exception e) { return Fail("AddNewHome threw: " + e.GetType().Name + ": " + e.Message); }
                if (!string.IsNullOrEmpty(name)) s.Name = name;

                return new
                {
                    success = true,
                    tile,
                    faction = fac.def.defName,
                    settlementId = s.ID,
                    name = s.Name,
                    limitReached,
                    note = "AddNewHome does not generate a map. limitReached is informational only - it is a UI cap, not one AddNewHome enforces.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/caravan_create",
            Description =
                "CaravanMaker.MakeCaravan from NAMED spawned pawns (pulling them off their " +
                "current map), then optionally Caravan_PathFollower.StartPath toward a " +
                "destination tile with no arrival action (a plain move - use " +
                "jawa/settlement_attack afterwards for an attack). The whole caravan domain was " +
                "absent from this bridge before this tool.",
            ResultDescription =
                "success, caravanId, name, faction, pawnCount, tile (start), destTile, pathed " +
                "(StartPath's own bool - false means CanReach failed), refused[] for any pawn " +
                "token that did not resolve.")]
        public static async Task<object> CaravanCreate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ids/names/thingIds to put in the caravan.")] string pawns,
            [ToolParameter(Description = "FactionDef defName for the caravan. Empty uses the first resolved pawn's own faction.")] string faction = null,
            [ToolParameter(Description = "Starting world tile. -1 uses the first pawn's current map tile.")] int startTile = -1,
            [ToolParameter(Description = "Destination world tile to path toward immediately. -1 creates the caravan without moving it.")] int destTile = -1,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(pawns)) return Fail("Give 'pawns' - comma-separated ids/names.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var grid = Find.WorldGrid;
                if (grid == null) return Fail("No WorldGrid. This needs a world loaded.");

                var found = new List<Pawn>();
                var refused = new List<object>();
                foreach (var raw in pawns.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    var tok = raw.Trim();
                    if (tok.Length == 0) continue;
                    string perr; var p = FindPawn(tok, out perr);
                    if (p == null) refused.Add(new { pawn = tok, reason = perr });
                    else found.Add(p);
                }
                if (found.Count == 0) return Fail("No pawn resolved. Nothing to caravan.", new { refused });

                Faction fac;
                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager != null ? Find.FactionManager.FirstFactionOfDef(fd) : null;
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                }
                else fac = found[0].Faction ?? Faction.OfPlayer;
                if (fac == null) return Fail("Could not resolve a faction for the caravan - give 'faction' explicitly.");

                int stTileId = startTile;
                if (stTileId < 0)
                {
                    var m = found[0].Map;
                    if (m == null) return Fail(found[0].LabelShortCap + " is not on a spawned map and no 'startTile' was given. Give startTile explicitly.");
                    stTileId = m.Tile;
                }
                if (stTileId < 0 || stTileId >= grid.TilesCount) return Fail("Resolved start tile " + stTileId + " is out of range.");
                var startPt = new PlanetTile(stTileId, grid.Surface);

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        pawnCount = found.Count,
                        pawns = found.Select(p => p.LabelShort).ToList(),
                        faction = fac.def.defName,
                        startTile = stTileId,
                        destTile = destTile >= 0 ? (int?)destTile : null,
                        refused
                    };

                Caravan car;
                try { car = CaravanMaker.MakeCaravan(found, fac, startPt, true); }
                catch (Exception e) { return Fail("MakeCaravan threw: " + e.GetType().Name + ": " + e.Message); }

                bool pathed = false; string pathNote = null;
                if (destTile >= 0)
                {
                    if (destTile >= grid.TilesCount) pathNote = "destTile " + destTile + " out of range; caravan created but not sent.";
                    else
                    {
                        var destPt = new PlanetTile(destTile, grid.Surface);
                        try { pathed = car.pather.StartPath(destPt, null); }
                        catch (Exception e) { pathNote = "StartPath threw: " + e.GetType().Name + ": " + e.Message; }
                        if (!pathed && pathNote == null)
                            pathNote = "StartPath returned false - CanReach failed for this destination.";
                    }
                }

                return new
                {
                    success = true,
                    caravanId = car.ID,
                    name = car.Name,
                    faction = fac.def.defName,
                    pawnCount = car.PawnsListForReading.Count,
                    tile = car.Tile.tileId,
                    destTile = destTile >= 0 ? (int?)destTile : null,
                    pathed,
                    pathNote,
                    refused,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/settlement_attack",
            Description =
                "*** ACTS ON THE LIVE COLONY *** SettlementUtility.Attack(caravan, settlement) - " +
                "generates the settlement's map if it has none, and enters the caravan into " +
                "combat against its defenders. 🔴 Attack() itself calls " +
                "AffectRelationsOnAttacked -> Faction.TryAffectGoodwillWith INSIDE the engine " +
                "call - this tool does NOT apply a second goodwill hit; the delta reported here " +
                "IS that one. Refuses same-faction pairs.",
            ResultDescription =
                "success, caravan, settlement, settlementFaction, beforeKind/afterKind " +
                "(FactionRelationKind), beforeGoodwill/afterGoodwill, goodwillHitApplied.")]
        public static async Task<object> SettlementAttack(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Live Caravan WorldObject id, as returned by jawa/caravan_create.")] int caravanId = -1,
            [ToolParameter(Description = "Live Settlement WorldObject id.")] int settlementId = -1,
            [ToolParameter(Description = "Report what would happen and do not attack.")] bool dryRun = true)
        {
            if (caravanId < 0) return Fail("Give 'caravanId'.");
            if (settlementId < 0) return Fail("Give 'settlementId'.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var car = Find.WorldObjects.AllWorldObjects.OfType<Caravan>().FirstOrDefault(c => c.ID == caravanId);
                if (car == null) return Fail("No live Caravan with id " + caravanId + ".");
                var settlement = Find.WorldObjects.AllWorldObjects.OfType<Settlement>().FirstOrDefault(s => s.ID == settlementId);
                if (settlement == null) return Fail("No live Settlement with id " + settlementId + ".");
                if (settlement.Faction != null && settlement.Faction == car.Faction)
                    return Fail("Caravan and settlement share a faction (" + settlement.Faction.def.defName + "); Attack is for hostile encounters.");

                Faction sf = settlement.Faction;
                string beforeKind = sf != null ? sf.PlayerRelationKind.ToString() : null;
                int? beforeGoodwill = sf != null && Faction.OfPlayer != null ? (int?)Faction.OfPlayer.GoodwillWith(sf) : null;

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        caravan = car.Label,
                        settlement = settlement.Label,
                        settlementFaction = sf != null ? sf.def.defName : null,
                        beforeKind,
                        beforeGoodwill,
                        note = "Attack() applies its own goodwill hit via AffectRelationsOnAttacked - no second hit is applied by this tool. It also generates a map if the settlement has none, which can take a moment.",
                        ticksGame = TicksGameSafe()
                    };

                try { SettlementUtility.Attack(car, settlement); }
                catch (Exception e) { return Fail("Attack threw: " + e.GetType().Name + ": " + e.Message); }

                string afterKind = sf != null ? sf.PlayerRelationKind.ToString() : null;
                int? afterGoodwill = sf != null && Faction.OfPlayer != null ? (int?)Faction.OfPlayer.GoodwillWith(sf) : null;

                return new
                {
                    success = true,
                    dryRun = false,
                    caravan = car.Label,
                    settlement = settlement.Label,
                    settlementFaction = sf != null ? sf.def.defName : null,
                    beforeKind,
                    afterKind,
                    beforeGoodwill,
                    afterGoodwill,
                    goodwillHitApplied = beforeGoodwill != afterGoodwill,
                    note = "The goodwill delta above is the hit Attack() applied internally via AffectRelationsOnAttacked - not a separate write.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
#endif // JAWA_GM_TOOLS

        // ================================================================
        //  Ideology, precepts & rituals
        // ================================================================

        // Shared by ideo_set_primary and ideo_development: resolve an Ideo the
        // same way jawa/ideo_of does - numeric id, or a case-insensitive
        // substring of its generated `name`, since an Ideo has no defName.
        private static object ResolveIdeoArg(string ideo, out Ideo found)
        {
            found = null;
            var mgr = Find.IdeoManager;
            if (mgr == null) return Fail("No IdeoManager. Needs a GAME loaded.");
            var all = mgr.IdeosListForReading;
            if (all == null) return Fail("IdeoManager returned no ideo list.");

            var wanted = (ideo ?? "").Trim();
            int byId = 0; bool isId = wanted.Length > 0 && int.TryParse(wanted, out byId);
            var candidates = all.Where(q => q != null &&
                (isId ? q.id == byId : (q.name ?? "").IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)).ToList();

            if (candidates.Count == 0)
                return Fail("No ideo matches '" + ideo + "'. jawa/ideo_of lists what exists in this world.");
            if (candidates.Count > 1)
                return Fail("'" + ideo + "' matches " + candidates.Count + " ideos ambiguously.",
                    new { matches = candidates.Select(c => new { c.id, c.name }).ToList() });
            found = candidates[0];
            return null;
        }

        [Tool(
            "jawa/ideo_set_primary",
            Description =
                "FactionIdeosTracker.SetPrimary(Ideo) - set which Ideo a named faction treats as " +
                "primary. 🔴 SetPrimary is a BARE FIELD ASSIGNMENT in 1.6 source " +
                "(`primaryIdeo = ideo;`) and nothing else: no believer migration, no letter, no " +
                "change to ideosMinor. Existing pawns keep whatever Ideo they already carry " +
                "until something else (conversion, jawa/set_pawn_ideo) moves them. Requires " +
                "Ideology.",
            ResultDescription = "success, faction, was{id,name} (previous primary, may be null), now{id,name}.")]
        public static async Task<object> IdeoSetPrimary(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "FactionDef defName.")] string faction,
            [ToolParameter(Description = "Ideo id (numeric) or a substring of its name, per jawa/ideo_of.")] string ideo,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(faction)) return Fail("faction is required.");
            if (string.IsNullOrWhiteSpace(ideo)) return Fail("ideo is required - a numeric id or a substring of its name, per jawa/ideo_of.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive)
                    return Fail("Ideology is NOT active. There are no runtime Ideo objects to set as primary - this is a capability answer.");

                var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                var f = Find.FactionManager != null ? Find.FactionManager.FirstFactionOfDef(fd) : null;
                if (f == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                if (f.ideos == null) return Fail(f.def.defName + " has no FactionIdeosTracker at all.");

                Ideo target;
                var resolveFail = ResolveIdeoArg(ideo, out target);
                if (resolveFail != null) return resolveFail;

                var was = f.ideos.PrimaryIdeo;
                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        faction = f.def.defName,
                        was = was != null ? new { was.id, was.name } : null,
                        willBe = new { target.id, target.name }
                    };

                try { f.ideos.SetPrimary(target); }
                catch (Exception e) { return Fail("SetPrimary threw: " + e.GetType().Name + ": " + e.Message); }
                var now = f.ideos.PrimaryIdeo;

                return new
                {
                    success = now == target,
                    faction = f.def.defName,
                    was = was != null ? new { was.id, was.name } : null,
                    now = now != null ? new { now.id, now.name } : null,
                    note = "SetPrimary carried no side effects - existing believers were not migrated.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/ideo_role_assign",
            Description =
                "Precept_Role.Assign(pawn, addThoughts) / Unassign(pawn, generateThoughts) - make " +
                "a pawn hold (or stop holding) a role, e.g. Moral Guide, on the PAWN'S OWN Ideo " +
                "(Pawn.Ideo). 'role' matches a PreceptDef defName or label, case-insensitively, " +
                "against that ideo's RolesListForReading. ⚠️ The engine itself does NOT gate " +
                "this: Precept_RoleMulti.Assign performs no validation at all, and " +
                "Precept_RoleSingle only Log.Errors on an invalid pawn and assigns it anyway - " +
                "so this tool does not pretend to refuse on the engine's behalf. IsAssigned is " +
                "read back before and after as the ground truth. Requires Ideology.",
            ResultDescription = "success, pawn, role, roleDef, action, wasAssigned, nowAssigned.")]
        public static async Task<object> IdeoRoleAssign(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn,
            [ToolParameter(Description = "PreceptDef defName or label substring of the role, e.g. 'Moralist', 'IdeoRole_Moralist'.")] string role,
            [ToolParameter(Description = "'assign' or 'unassign'.")] string action = "assign",
            [ToolParameter(Description = "Generate the vanilla role-gained/lost thoughts.")] bool addThoughts = true,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(pawn)) return Fail("pawn is required.");
            if (string.IsNullOrWhiteSpace(role)) return Fail("role is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive) return Fail("Ideology is NOT active. There are no ideo roles to assign.");

                string perr; var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");

                var targetIdeo = p.Ideo;
                if (targetIdeo == null) return Fail(p.LabelShortCap + " has no Ideo - a role can only be assigned within the pawn's own ideoligion.");

                var roleWanted = role.Trim();
                var roles = targetIdeo.RolesListForReading ?? new List<Precept_Role>();
                var matches = roles.Where(r => r != null && (
                    string.Equals(r.def != null ? r.def.defName : null, roleWanted, StringComparison.OrdinalIgnoreCase)
                    || (r.def != null && r.def.defName != null && r.def.defName.IndexOf(roleWanted, StringComparison.OrdinalIgnoreCase) >= 0)
                    || (r.Label ?? "").IndexOf(roleWanted, StringComparison.OrdinalIgnoreCase) >= 0)).ToList();

                if (matches.Count == 0)
                    return Fail("'" + roleWanted + "' matches no role on " + p.LabelShortCap + "'s ideo (" + targetIdeo.name + ").",
                        new { roles = roles.Select(r => new { def = r.def != null ? r.def.defName : null, label = r.Label }).ToList() });
                if (matches.Count > 1)
                    return Fail("'" + roleWanted + "' matches " + matches.Count + " roles ambiguously.",
                        new { matches = matches.Select(r => new { def = r.def != null ? r.def.defName : null, label = r.Label }).ToList() });
                var precRole = matches[0];

                bool alreadyAssigned = precRole.IsAssigned(p);
                bool unassign = string.Equals(action, "unassign", StringComparison.OrdinalIgnoreCase);
                if (unassign && !alreadyAssigned)
                    return Fail(p.LabelShortCap + " does not currently hold role '" + precRole.Label + "'. Nothing to unassign.");

                if (dryRun)
                    return new { success = true, dryRun = true, pawn = p.LabelShortCap, role = precRole.Label, action = unassign ? "unassign" : "assign", alreadyAssigned };

                try
                {
                    if (unassign) precRole.Unassign(p, addThoughts);
                    else precRole.Assign(p, addThoughts);
                }
                catch (Exception e) { return Fail("Assign/Unassign threw: " + e.GetType().Name + ": " + e.Message); }

                bool nowAssigned = precRole.IsAssigned(p);
                bool ok = unassign ? !nowAssigned : nowAssigned;

                return new
                {
                    success = ok,
                    pawn = p.LabelShortCap,
                    role = precRole.Label,
                    roleDef = precRole.def != null ? precRole.def.defName : null,
                    action = unassign ? "unassign" : "assign",
                    wasAssigned = alreadyAssigned,
                    nowAssigned,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/ideo_development",
            Description =
                "IdeoDevelopmentTracker.TryAddDevelopmentPoints(int) and/or Notify_Reformed() - " +
                "push a named Ideo toward, or through, a reform. TryAddDevelopmentPoints " +
                "REFUSES (returns false) once CanReformNow is already true, matching the " +
                "engine's own cap; there is no subtract path in 1.6 source. Notify_Reformed " +
                "resets points to 0, increments reformCount, and fires every precept's " +
                "Notify_IdeoReformed - it is the real reform, not a preview. Requires Ideology.",
            ResultDescription =
                "success, ideo, addPointsRequested, pointsAdded (TryAddDevelopmentPoints' own " +
                "bool), reformed, was{points,reformCount,canReformNow,nextReform}, now{...}.")]
        public static async Task<object> IdeoDevelopment(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Ideo id (numeric) or a substring of its name, per jawa/ideo_of.")] string ideo,
            [ToolParameter(Description = "Development points to add. 0 to skip.")] int addPoints = 0,
            [ToolParameter(Description = "Also call Notify_Reformed() - the real reform, not a preview.")] bool reform = false,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(ideo)) return Fail("ideo is required - a numeric id or a substring of its name, per jawa/ideo_of.");
            if (addPoints < 0) return Fail("addPoints must be >= 0 - TryAddDevelopmentPoints itself refuses <= 0, and there is no subtract path in 1.6 source.");
            if (addPoints == 0 && !reform && !dryRun) return Fail("Nothing to do: pass addPoints and/or reform=true.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive) return Fail("Ideology is NOT active. There is no IdeoDevelopmentTracker to touch.");

                Ideo target;
                var resolveFail = ResolveIdeoArg(ideo, out target);
                if (resolveFail != null) return resolveFail;

                var dev = target.development;
                if (dev == null) return Fail("This ideo has no IdeoDevelopmentTracker (development is null).");

                Func<object> snapshot = () => new { points = dev.Points, reformCount = dev.reformCount, canReformNow = dev.CanReformNow, nextReform = dev.NextReformationDevelopmentPoints };
                var was = snapshot();

                if (dryRun) return new { success = true, dryRun = true, ideo = target.name, was };

                bool added = false;
                if (addPoints > 0)
                {
                    try { added = dev.TryAddDevelopmentPoints(addPoints); }
                    catch (Exception e) { return Fail("TryAddDevelopmentPoints threw: " + e.GetType().Name + ": " + e.Message); }
                }

                bool reformed = false;
                if (reform)
                {
                    try { dev.Notify_Reformed(); reformed = true; }
                    catch (Exception e) { return Fail("Notify_Reformed threw: " + e.GetType().Name + ": " + e.Message); }
                }

                var now = snapshot();

                return new
                {
                    success = true,
                    ideo = target.name,
                    addPointsRequested = addPoints,
                    pointsAdded = added,
                    reformed,
                    was,
                    now,
                    note = (addPoints > 0 && !added)
                        ? "TryAddDevelopmentPoints returned false - CanReformNow was already true before this call, so the engine refused to add more."
                        : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
