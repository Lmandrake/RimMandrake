// JawaBenchAbilityTools.cs - drive a NON-COLONIST pawn from outside the game.
//
// BRIDGE_SELECT_NONCOLONIST_PAWN_1. MEASURED live 2026-09-20 (FOUNDRY): the
// external bridge's own rimworld/select_pawn and its ToolMapForPawns both
// REFUSE a pawn that is not a colonist, so no wild or hostile creature could be
// selected, and nothing could be made to fire an ability on command. Every
// creature mechanic this project rebuilds lives on a wild or hostile pawn, so
// that gap blocked live verification of all of them - the only alternative was
// waiting for the AI to volunteer the behaviour, which is not a test.
//
// WHERE THE COLONIST CHECK ACTUALLY LIVES, read from 1.6 source:
//   * Selector.SelectInternal (RimWorld/Selector.cs:300) has NO faction or
//     colonist gate at all. It refuses exactly four things: null, an object
//     that is not a Thing/Zone/Plan, a DESTROYED thing, and a WORLD PAWN - and
//     each refusal is a Log.Error, which pops the dev console. So the gate was
//     never the engine's; it belonged to the bridge's own pawn tools.
//   * VerbTracker.CreateVerbTargetCommand (Verse/VerbTracker.cs) DOES gate on
//     caster.Faction != Faction.OfPlayer, and Pawn_AbilityTracker.GetGizmos
//     gates on IsColonistPlayerControlled - but both of those build a GIZMO.
//     The verb and the ability underneath are unfaction-aware. Driving them
//     directly is not a bypass of a rule; it is skipping the button.
//
// GATING. Following the test stated in JawaBenchEventTools.cs and restated in
// JawaBenchGroupTools.cs: #if JAWA_GM_TOOLS is for tools that hand THE WORLD
// permission to act on the player (an incident, a raid, an AI that then decides
// for itself). Every tool in this file makes a NAMED pawn do a NAMED thing to a
// NAMED target, which is the same category jawa/damage, jawa/order_pawn and
// jawa/pawn_mental already occupy ungated. So: ungated.
//
// ALREADY COVERED, DO NOT REBUILD: forcing a mental state on an arbitrary pawn
// is jawa/pawn_mental, which resolves through FindPawn and has never had a
// faction check. Granting an AbilityDef is jawa/grant_ability. This file adds
// only what was genuinely missing: SELECT anything, and FIRE an ability or a
// verb on demand.
//
// THE SIX ENGINE FACTS THAT SHAPE THIS FILE, each read from 1.6 source:
//
//  1. Ability.Activate(target, dest) DOES NOT FIRE THE VERB. It calls
//     PreActivate, sets lastCombatantTick, and applies the EffectComps. That is
//     all (RimWorld/Ability.cs:543). An ability whose whole payload is a
//     projectile - RSW_VoltmawPlasmaVolley, Verb_AbilityShoot - produces NOTHING
//     from Activate, because the projectile is the verb's business. Anyone
//     testing a projectile ability with Activate would measure a silent success
//     and conclude the ability is broken. Hence mode='job' is the default.
//
//  2. Ability.QueueCastingJob routes through ShowCastingConfirmationIfNeeded,
//     which can push a Dialog_MessageBox onto the WindowStack and then never
//     cast (RimWorld/Ability.cs:611,664). A headless caller would get success
//     and a modal sitting on the owner's screen. So mode='job' builds the job
//     itself via Ability.GetJob and hands it to Pawn_JobTracker.TryTakeOrderedJob
//     - the identical job the confirmed path would have queued, minus the modal.
//
//  3. Ability.CanApplyOn reads the PRIVATE effectComps field, not the
//     EffectComps property that lazily fills it (RimWorld/Ability.cs:360). On a
//     freshly loaded ability that field is still null, so CanApplyOn skips every
//     comp veto and answers true. This file touches ability.EffectComps first,
//     which is what makes the subsequent CanApplyOn answer mean anything.
//
//  4. Verb.TryStartCastOn refuses on !caster.Spawned and on !CanHitTarget, and
//     both refusals are a bare false with no reason (Verse/Verb.cs:324). Both
//     are checked here first and named.
//
//  5. VerbTracker.InitVerb sets verb.caster = directOwner.ConstantCaster, and
//     Ability.ConstantCaster is the pawn - so an ability verb's caster is always
//     correct and never needs setting. Do not set it.
//
//  6. HediffSet.GetHediffsVerbs() hands back a SHARED static buffer that the
//     next call clears (Verse/HediffSet.cs:760). Copy it out before doing
//     anything else, the same trap MapPawns.AllPawnsUnspawned carries.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
// RimWorld.Planet, for Pawn.IsWorldPawn() - the extension lives on
// RimWorld.Planet.WorldPawnsUtility, and it is one of the four refusals
// Selector.SelectInternal Log.Errors on, so this file must be able to ask.
using RimWorld.Planet;
using RimBridgeServer.Sdk;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  shared helpers
        // ================================================================

        /// <summary>
        /// A target resolver for the three tools below: a pawn id/name first
        /// (FindPawn reaches held and world pawns too), then any live thing id.
        /// Deliberately NOT faction-aware.
        /// </summary>
        private static Thing AbilityToolsFindTarget(string id, out string err)
        {
            err = null;
            if (string.IsNullOrWhiteSpace(id)) { err = "Give a target id."; return null; }
            string perr;
            var p = FindPawn(id, out perr);
            if (p != null) return p;
            string terr;
            var t = SystemToolsFindThing(id, out terr);
            if (t != null) return t;
            err = terr ?? perr ?? ("Nothing matching '" + id + "'.");
            return null;
        }

        /// <summary>Every verb a pawn owns, with where each came from.</summary>
        private static List<KeyValuePair<string, Verb>> AbilityToolsAllVerbs(Pawn p)
        {
            var rows = new List<KeyValuePair<string, Verb>>();
            if (p == null) return rows;

            if (p.VerbTracker != null)
                foreach (var v in p.VerbTracker.AllVerbs)
                    rows.Add(new KeyValuePair<string, Verb>("race", v));

            if (p.equipment != null)
                foreach (var v in p.equipment.AllEquipmentVerbs)
                    rows.Add(new KeyValuePair<string, Verb>("equipment", v));

            if (p.apparel != null)
            {
                foreach (var ap in p.apparel.WornApparel)
                {
                    var comp = ap.GetComp<CompApparelVerbOwner>();
                    if (comp == null) continue;
                    foreach (var v in comp.AllVerbs)
                        rows.Add(new KeyValuePair<string, Verb>("apparel", v));
                }
            }

            if (p.health != null && p.health.hediffSet != null)
            {
                // 🔴 SHARED BUFFER. GetHediffsVerbs returns HediffSet's own static
                // tmpHediffVerbs, which the next call Clear()s. Copy it out now.
                var hv = new List<Verb>(p.health.hediffSet.GetHediffsVerbs());
                foreach (var v in hv)
                    rows.Add(new KeyValuePair<string, Verb>("hediff", v));
            }

            if (p.abilities != null)
            {
                foreach (var a in p.abilities.AllAbilitiesForReading)
                {
                    var v = a.verb;
                    if (v != null) rows.Add(new KeyValuePair<string, Verb>("ability:" + a.def.defName, v));
                }
            }

            return rows;
        }

        private static object AbilityToolsVerbRow(string source, Verb v, Pawn caster, LocalTargetInfo? target)
        {
            return new
            {
                source,
                id = v.GetUniqueLoadID(),
                label = v.verbProps != null ? v.verbProps.label : null,
                verbClass = v.GetType().Name,
                isMelee = v.IsMeleeAttack,
                range = v.verbProps != null ? v.verbProps.range : -1f,
                minRange = v.verbProps != null ? v.verbProps.minRange : -1f,
                warmupTime = v.verbProps != null ? v.verbProps.warmupTime : -1f,
                burstShotCount = v.verbProps != null ? v.verbProps.burstShotCount : 0,
                state = v.state.ToString(),
                warmingUp = v.WarmingUp,
                casterSpawned = v.caster != null && v.caster.Spawned,
                equipmentSource = v.EquipmentSource != null ? v.EquipmentSource.LabelCap.ToString() : null,
                hediffSource = v.HediffSource != null ? v.HediffSource.def.defName : null,
                usableByCaster = caster != null && v.IsStillUsableBy(caster),
                canHitTarget = target.HasValue ? (bool?)v.CanHitTarget(target.Value) : null,
            };
        }

        /// <summary>
        /// Turn targetId / x / z into a LocalTargetInfo. Returns null on success
        /// and a Fail object otherwise, so a caller can `if (bad != null) return bad;`.
        /// </summary>
        private static object AbilityToolsResolveTarget(
            Map map, string targetId, int x, int z,
            out LocalTargetInfo target, out string describedAs)
        {
            target = LocalTargetInfo.Invalid;
            describedAs = null;

            if (!string.IsNullOrWhiteSpace(targetId))
            {
                string terr;
                var t = AbilityToolsFindTarget(targetId, out terr);
                if (t == null) return Fail(terr);
                if (!t.Spawned)
                    return Fail(t.LabelCap + " (" + t.ThingID + ") is not spawned on a map, so it " +
                                "cannot be targeted. LocalTargetInfo needs a map position.");
                target = new LocalTargetInfo(t);
                describedAs = "thing " + t.ThingID;
                return null;
            }

            if (x < 0 || z < 0)
                return Fail("No target. Pass targetId for a thing or pawn, or x and z for a map cell.",
                    new { xGiven = x, zGiven = z });

            var cell = new IntVec3(x, 0, z);
            if (map == null) return Fail("No current map.");
            if (!cell.InBounds(map))
                return Fail("(" + x + "," + z + ") is outside the map.",
                    new { mapSize = new { x = map.Size.x, z = map.Size.z } });
            target = new LocalTargetInfo(cell);
            describedAs = "cell (" + x + "," + z + ")";
            return null;
        }

        private static object AbilityToolsPawnRow(Pawn p)
        {
            return new
            {
                id = p.ThingID,
                name = p.LabelShortCap.ToString(),
                kind = p.kindDef != null ? p.kindDef.defName : null,
                faction = p.Faction != null ? p.Faction.Name : null,
                isPlayer = p.Faction != null && p.Faction.IsPlayer,
                hostileToPlayer = p.HostileTo(Faction.OfPlayer),
                spawned = p.Spawned,
                downed = p.Downed,
                dead = p.Dead,
                drafted = p.drafter != null && p.drafter.Drafted,
                position = p.Spawned ? (object)new { x = p.Position.x, z = p.Position.z } : null,
                currentJob = p.CurJobDef != null ? p.CurJobDef.defName : null,
                stance = p.stances != null && p.stances.curStance != null
                    ? p.stances.curStance.GetType().Name : null,
            };
        }

        // ================================================================
        //  jawa/select_things
        // ================================================================
        [Tool(
            "jawa/select_things",
            Description =
                "Select ANY spawned thing - a wild animal, a hostile raider, a building, an " +
                "item - with no faction, colonist or player-control check of any kind. This is " +
                "the gap BRIDGE_SELECT_NONCOLONIST_PAWN_1 names: the external bridge's own " +
                "rimworld/select_pawn refuses a non-colonist, so nothing wild or hostile could " +
                "be put under the inspect pane at all. " +
                "🔑 Selector.SelectInternal was never the thing refusing - it has no faction " +
                "gate, only four refusals, and every one of them is a Log.Error that pops the " +
                "dev console. So all four are CHECKED HERE FIRST and returned as a reason " +
                "rather than being allowed to reach the engine: null, a destroyed thing, a " +
                "world pawn (a caravan member, a pawn in transit), and an unspawned thing (one " +
                "in a casket, pod or another pawn's inventory). " +
                "⚠️ Selecting a thing on a DIFFERENT map switches the current map and moves the " +
                "camera - the engine does that, not this tool, and the response says when it " +
                "happened. " +
                "⚠️ The engine caps selection at 200 objects; ids past that are reported as " +
                "refused rather than silently dropped. " +
                "Selection is a UI state, not a game state: it survives until something else " +
                "clears it and it does not persist into a save.",
            ResultDescription =
                "success (true only when every requested id ended up selected, READ BACK from " +
                "Selector.SelectedObjects rather than assumed), selectedCount, selected[] with " +
                "one row per object now selected, refused[] with a per-id reason, " +
                "mapSwitchedTo when the engine changed the current map, and ticksGame.")]
        public static async Task<object> SelectThings(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "One thing id, or a comma-separated list. A pawn may be named by its bare " +
                "ThingID ('Human45731'), the same with a 'Thing_' prefix, its numeric " +
                "thingIDNumber, or its name. Any other thing is matched by ThingID. " +
                "Not needed when action='clear' or action='get'.")]
            string ids = null,
            [ToolParameter(Description =
                "'select' replaces the current selection, 'add' appends to it, 'clear' " +
                "deselects everything, 'get' only reads back what is selected now.",
                DefaultValue = "select")]
            string action = "select",
            [ToolParameter(Description =
                "Move the camera to the first selected object. Off by default, because a " +
                "camera jump is a visible change to whatever the owner is looking at.",
                DefaultValue = false)]
            bool jumpCamera = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                var selector = Find.Selector;
                if (selector == null)
                    return Fail("Find.Selector is null - there is no UI layer yet. " +
                                "Selection needs a game that has finished loading into play.");

                var A = (action ?? "select").Trim().ToLowerInvariant();
                if (A != "select" && A != "add" && A != "clear" && A != "get")
                    return Fail("action '" + action + "' is not one of select, add, clear, get.");

                var mapBefore = Find.CurrentMap;
                var refused = new List<object>();
                var requested = new List<string>();

                if (A == "clear")
                {
                    selector.ClearSelection();
                }
                else if (A == "select" || A == "add")
                {
                    if (string.IsNullOrWhiteSpace(ids))
                        return Fail("action='" + A + "' needs ids. Pass action='clear' to deselect " +
                                    "everything or action='get' to read the selection back.");

                    var toks = ids.Split(',')
                                  .Select(s => s.Trim())
                                  .Where(s => s.Length > 0)
                                  .ToList();
                    if (toks.Count == 0) return Fail("ids parsed to nothing.");

                    var resolved = new List<Thing>();
                    foreach (var tok in toks)
                    {
                        requested.Add(tok);
                        string err;
                        var t = AbilityToolsFindTarget(tok, out err);
                        if (t == null) { refused.Add(new { id = tok, reason = err }); continue; }

                        // Every one of the four Selector refusals, pre-empted so the
                        // engine never gets to Log.Error about it.
                        if (t.Destroyed)
                        { refused.Add(new { id = tok, reason = t.LabelCap + " is DESTROYED; Selector refuses destroyed things." }); continue; }
                        var asPawn = t as Pawn;
                        if (asPawn != null && asPawn.IsWorldPawn())
                        { refused.Add(new { id = tok, reason = asPawn.LabelShortCap + " is a WORLD pawn (caravan, transit, off-map); Selector refuses world pawns outright." }); continue; }
                        if (!t.Spawned)
                        { refused.Add(new { id = tok, reason = t.LabelCap + " is not spawned (held in a casket, pod, container or inventory); there is nothing on a map to select." }); continue; }

                        resolved.Add(t);
                    }

                    if (A == "select") selector.ClearSelection();

                    foreach (var t in resolved)
                    {
                        if (selector.SelectedObjects.Count >= 200)
                        {
                            refused.Add(new { id = t.ThingID, reason = "Selector is at its 200-object cap; this one was not added." });
                            continue;
                        }
                        // playSound:false - a bridge call should not click at the owner.
                        selector.Select(t, false, true);
                    }

                    if (jumpCamera && resolved.Count > 0)
                        CameraJumper.TryJump(resolved[0]);
                }

                // READ BACK. Never the call's own say-so.
                var selectedRows = new List<object>();
                var selectedIds = new List<string>();
                foreach (var o in selector.SelectedObjects)
                {
                    var p = o as Pawn;
                    if (p != null)
                    {
                        selectedIds.Add(p.ThingID);
                        selectedRows.Add(AbilityToolsPawnRow(p));
                        continue;
                    }
                    var t = o as Thing;
                    if (t != null)
                    {
                        selectedIds.Add(t.ThingID);
                        selectedRows.Add(new
                        {
                            id = t.ThingID,
                            label = t.LabelCap.ToString(),
                            def = t.def != null ? t.def.defName : null,
                            position = t.Spawned ? (object)new { x = t.Position.x, z = t.Position.z } : null,
                        });
                        continue;
                    }
                    selectedRows.Add(new { id = (string)null, label = o != null ? o.GetType().Name : "null", def = (string)null, position = (object)null });
                }

                var mapAfter = Find.CurrentMap;
                var everyRequestedIsSelected =
                    (A == "select" || A == "add") &&
                    requested.Count > 0 &&
                    refused.Count == 0;

                return new
                {
                    success = A == "clear" || A == "get" ? true : everyRequestedIsSelected,
                    action = A,
                    requestedCount = requested.Count,
                    refusedCount = refused.Count,
                    refused,
                    selectedCount = selectedRows.Count,
                    selected = selectedRows,
                    selectedIds,
                    mapSwitchedTo = mapBefore != mapAfter && mapAfter != null
                        ? (object)new { index = mapAfter.Index, tile = mapAfter.Tile.ToString() }
                        : null,
                    cameraJumped = jumpCamera && (A == "select" || A == "add"),
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/pawn_use_ability
        // ================================================================
        [Tool(
            "jawa/pawn_use_ability",
            Description =
                "Make ANY pawn - wild, hostile, faction-less, undrafted - fire one of its " +
                "AbilityDefs at a target, with no faction or colonist check. action='list' " +
                "reads what the pawn has and why each one can or cannot fire right now; " +
                "action='cast' fires it. " +
                "🔴 THE THREE MODES ARE NOT INTERCHANGEABLE AND THE WRONG ONE MEASURES NOTHING. " +
                "mode='job' (default) is the REAL cast: it builds Ability.GetJob and hands it " +
                "to Pawn_JobTracker.TryTakeOrderedJob, so the pawn walks into range if it must, " +
                "warms up, and the verb fires - projectiles, burst counts, cooldown and all. " +
                "mode='verb' skips the job and calls Verb.TryStartCastOn directly from where " +
                "the pawn stands - immediate, no pathing, refuses if out of range. " +
                "mode='effect' calls Ability.Activate, which applies ONLY the ability's " +
                "CompAbilityEffects and DOES NOT FIRE THE VERB - an ability whose payload is a " +
                "projectile produces nothing at all from this mode, so do not use it to test " +
                "one and then conclude the ability is broken. " +
                "🔑 mode='job' deliberately does NOT go through Ability.QueueCastingJob, which " +
                "can push a confirmation Dialog_MessageBox onto the window stack and then never " +
                "cast, leaving a modal on the owner's screen and a headless caller reporting " +
                "success. It builds the identical job and queues it directly. " +
                "⚠️ A PAUSED GAME CANNOT CAST. The job is queued and nothing happens until the " +
                "game ticks. waitTicks>0 briefly sets Normal speed, waits, restores the previous " +
                "speed - including when the wait is cancelled - and that restore is reported as " +
                "speedRestored. With waitTicks=0 you must unpause yourself.",
            ResultDescription =
                "action='list': every AbilityDef the pawn holds with canCast (the AcceptanceReport " +
                "and its reason), cooldown ticks remaining, charges and the verb behind it. " +
                "action='cast': accepted (the real bool from the engine call, never assumed), the " +
                "gate that refused when it did, and a READ-BACK block taken after the wait - the " +
                "pawn's job, stance, verb state, lastCastTick and cooldown, which together are " +
                "the only evidence the cast actually started. ticksElapsed is at the top: if it " +
                "is 0 the game never ticked and nothing below it means anything.")]
        public static async Task<object> PawnUseAbility(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Caster pawn id, thingId or name. No faction check.")]
            string pawn = null,
            [ToolParameter(Description = "'list' or 'cast'.", DefaultValue = "list")]
            string action = "list",
            [ToolParameter(Description =
                "AbilityDef defName to fire, e.g. 'RSW_VoltmawPlasmaVolley'. Required for " +
                "action='cast'. Matched against the pawn's own abilities including temporary " +
                "ones from hediffs, equipment, apparel and roles.")]
            string ability = null,
            [ToolParameter(Description =
                "Target: a thing or pawn id. Overrides x/z when given.")]
            string targetId = null,
            [ToolParameter(Description = "Target cell X, when no targetId is given.", DefaultValue = -1)]
            int x = -1,
            [ToolParameter(Description = "Target cell Z, when no targetId is given.", DefaultValue = -1)]
            int z = -1,
            [ToolParameter(Description =
                "'job' (the real cast, default), 'verb' (cast in place, no pathing) or " +
                "'effect' (apply the effect comps only - NO PROJECTILE).",
                DefaultValue = "job")]
            string mode = "job",
            [ToolParameter(Description =
                "Call Ability.ResetCooldown() first, so a recently-used ability can be fired " +
                "again immediately for a test. Reports whether it was actually on cooldown.",
                DefaultValue = false)]
            bool resetCooldown = false,
            [ToolParameter(Description =
                "Skip the CanCast / CanApplyOn / CanHitTarget pre-checks and attempt the cast " +
                "anyway. The checks still RUN and are still reported - this only stops them " +
                "refusing. Use it to find out whether a gate is lying.",
                DefaultValue = false)]
            bool force = false,
            [ToolParameter(Description =
                "Draft the caster first, if it has a drafter. A drafted pawn holds position " +
                "instead of wandering off mid-warmup. Animals and non-player pawns have no " +
                "drafter and say so.",
                DefaultValue = false)]
            bool draft = false,
            [ToolParameter(Description =
                "GAME ticks to wait after the cast before reading back. A warmup of 7 seconds " +
                "is 420 ticks, so a volley needs several hundred to be visible. 0 reads back " +
                "immediately and measures only that the job was queued.",
                DefaultValue = 300)]
            int waitTicks = 300,
            [ToolParameter(Description = "Wall-clock ceiling on the wait, so a paused or hitching game cannot hang the call.", DefaultValue = 30)]
            int timeoutSeconds = 30,
            [ToolParameter(Description =
                "If the game is paused, run at Normal speed for the wait and restore the " +
                "previous speed afterwards. With this off, a paused game returns ticksElapsed=0.",
                DefaultValue = true)]
            bool unpause = true)
        {
            var A = (action ?? "list").Trim().ToLowerInvariant();
            var M = (mode ?? "job").Trim().ToLowerInvariant();
            if (A != "list" && A != "cast")
                return Fail("action '" + action + "' is not 'list' or 'cast'.");
            if (A == "cast" && M != "job" && M != "verb" && M != "effect")
                return Fail("mode '" + mode + "' is not 'job', 'verb' or 'effect'.");
            if (waitTicks < 0) return Fail("waitTicks must be >= 0, got " + waitTicks + ".");
            if (timeoutSeconds < 1 || timeoutSeconds > 300)
                return Fail("timeoutSeconds must be 1-300, got " + timeoutSeconds + ".");

            Pawn caster = null;
            Ability castAbility = null;
            var startTicks = -1;
            TimeSpeed speedBefore = TimeSpeed.Paused;
            var speedChanged = false;
            var speedRestored = false;
            var accepted = false;
            string refusedBy = null;
            var wasOnCooldown = false;
            var cooldownReset = false;
            var hadDrafter = false;
            object preCast = null;

            var setup = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                caster = FindPawn(pawn, out perr);
                if (caster == null) return Fail(perr ?? "No pawn.");
                if (caster.abilities == null)
                    return Fail(caster.LabelShortCap + " has no Pawn_AbilityTracker at all. " +
                                "An animal only gets one when something gives it one - " +
                                "jawa/grant_ability creates it. Nothing to cast.");

                var all = caster.abilities.AllAbilitiesForReading;

                if (A == "list")
                {
                    var rows = new List<object>();
                    foreach (var a in all)
                    {
                        // Touch EffectComps BEFORE CanApplyOn - see fact 3 in the header.
                        var comps = a.EffectComps;
                        var report = a.CanCast;
                        string gizmoReason;
                        var gizmoOff = a.GizmoDisabled(out gizmoReason);
                        rows.Add(new
                        {
                            def = a.def.defName,
                            label = a.def.label,
                            canCast = report.Accepted,
                            canCastReason = report.Accepted ? null : report.Reason,
                            onCooldown = a.OnCooldown,
                            cooldownTicksRemaining = a.CooldownTicksRemaining,
                            cooldownTicksTotal = a.CooldownTicksTotal,
                            usesCharges = a.UsesCharges,
                            remainingCharges = a.UsesCharges ? (int?)a.RemainingCharges : null,
                            casting = a.Casting,
                            canQueueCast = a.CanQueueCast,
                            // The gizmo's own verdict, reported because it is what a
                            // human clicking would see - NOT a gate this tool obeys.
                            gizmoDisabled = gizmoOff,
                            gizmoDisabledReason = gizmoOff ? gizmoReason : null,
                            effectCompCount = comps != null ? comps.Count : 0,
                            aiCanUse = a.def.aiCanUse,
                            jobDef = a.def.jobDef != null ? a.def.jobDef.defName : "CastAbilityOnThing (engine default)",
                            verb = a.verb != null
                                ? (object)new
                                {
                                    verbClass = a.verb.GetType().Name,
                                    range = a.verb.verbProps != null ? a.verb.verbProps.range : -1f,
                                    warmupTime = a.verb.verbProps != null ? a.verb.verbProps.warmupTime : -1f,
                                    burstShotCount = a.verb.verbProps != null ? a.verb.verbProps.burstShotCount : 0,
                                    defaultProjectile = a.verb.verbProps != null && a.verb.verbProps.defaultProjectile != null
                                        ? a.verb.verbProps.defaultProjectile.defName : null,
                                    state = a.verb.state.ToString(),
                                    casterIsPawn = a.verb.caster == caster,
                                }
                                : null,
                        });
                    }
                    preCast = new
                    {
                        pawn = AbilityToolsPawnRow(caster),
                        abilityCount = rows.Count,
                        permanentCount = caster.abilities.abilities.Count,
                        abilities = rows,
                    };
                    return null;
                }

                // ---- action == "cast"
                if (string.IsNullOrWhiteSpace(ability))
                    return Fail("action='cast' needs an ability (an AbilityDef defName).");

                var def = DefDatabase<AbilityDef>.GetNamedSilentFail(ability.Trim());
                if (def == null)
                    return Fail("No AbilityDef named '" + ability + "'.",
                        new { suggestions = DefSuggestions<AbilityDef>(ability) });

                castAbility = all.FirstOrDefault(a => a.def == def);
                if (castAbility == null)
                    return Fail(caster.LabelShortCap + " does not have " + def.defName + ". " +
                                "Grant it with jawa/grant_ability first.",
                        new { has = all.Select(a => a.def.defName).ToList() });

                if (!caster.Spawned)
                    return Fail(caster.LabelShortCap + " is not spawned on a map. " +
                                "Verb.TryStartCastOn refuses !caster.Spawned and a job cannot run.");

                var map = caster.Map;
                LocalTargetInfo target;
                string describedAs;
                var bad = AbilityToolsResolveTarget(map, targetId, x, z, out target, out describedAs);
                if (bad != null) return bad;

                if (target.Thing != null && target.Thing.Map != map)
                    return Fail("Target " + target.Thing.ThingID + " is on a different map from " +
                                caster.LabelShortCap + ". An ability cannot cross maps.");

                // Cooldown, before any gate reads it.
                wasOnCooldown = castAbility.OnCooldown;
                if (resetCooldown && wasOnCooldown)
                {
                    castAbility.ResetCooldown();
                    cooldownReset = true;
                }

                if (draft)
                {
                    hadDrafter = caster.drafter != null;
                    if (hadDrafter && !caster.drafter.Drafted) caster.drafter.Drafted = true;
                }

                // Touch EffectComps BEFORE CanApplyOn - fact 3.
                var effectComps = castAbility.EffectComps;
                var canCast = castAbility.CanCast;
                var canApply = castAbility.CanApplyOn(target);
                var verb = castAbility.verb;
                var canHit = verb != null && verb.CanHitTarget(target);

                if (!force)
                {
                    if (!canCast.Accepted)
                        refusedBy = "Ability.CanCast: " + (string.IsNullOrEmpty(canCast.Reason)
                            ? "refused with no reason given (usually cooldown or an AbilityComp veto)"
                            : canCast.Reason);
                    else if (!canApply)
                        refusedBy = "Ability.CanApplyOn returned false for " + describedAs +
                                    " - one of the " + (effectComps != null ? effectComps.Count : 0) +
                                    " effect comps vetoed this target, or the ability is self-only.";
                    else if (verb == null)
                        refusedBy = "The ability has no verb (VerbTracker.PrimaryVerb is null - " +
                                    "its verbProperties has no isPrimary entry).";
                    else if (M == "verb" && !canHit)
                        refusedBy = "Verb.CanHitTarget is false for " + describedAs +
                                    " - out of range, minRange, or no shootable line. mode='job' " +
                                    "would walk the pawn into range first; mode='verb' will not.";
                }

                preCast = new
                {
                    pawn = AbilityToolsPawnRow(caster),
                    ability = def.defName,
                    target = describedAs,
                    mode = M,
                    canCast = canCast.Accepted,
                    canCastReason = canCast.Accepted ? null : canCast.Reason,
                    canApplyOn = canApply,
                    canHitTarget = canHit,
                    canQueueCast = castAbility.CanQueueCast,
                    wasOnCooldown,
                    cooldownReset,
                    cooldownTicksRemaining = castAbility.CooldownTicksRemaining,
                    effectCompCount = effectComps != null ? effectComps.Count : 0,
                    lastCastTickBefore = castAbility.lastCastTick,
                    drafted = caster.drafter != null && caster.drafter.Drafted,
                    hasDrafter = caster.drafter != null,
                };

                if (refusedBy != null) return null;   // reported, nothing cast

                var tm = Find.TickManager;
                startTicks = tm != null ? tm.TicksGame : -1;
                if (tm != null)
                {
                    speedBefore = tm.CurTimeSpeed;
                    if (unpause && waitTicks > 0 && tm.CurTimeSpeed == TimeSpeed.Paused)
                    {
                        tm.CurTimeSpeed = TimeSpeed.Normal;
                        speedChanged = true;
                    }
                }

                if (M == "effect")
                {
                    // Activate applies EffectComps ONLY. No verb, no projectile.
                    accepted = castAbility.Activate(target, LocalTargetInfo.Invalid);
                }
                else if (M == "verb")
                {
                    if (verb == null) { refusedBy = "No verb to cast with."; return null; }
                    accepted = verb.TryStartCastOn(target);
                    if (!accepted)
                        refusedBy = "Verb.TryStartCastOn returned false. Its refusal paths are: " +
                                    "caster not spawned, the verb already Bursting (state=" +
                                    verb.state + "), or CanHitTarget false (computed here as " +
                                    canHit + "). It gives no reason of its own.";
                }
                else
                {
                    if (caster.jobs == null)
                    { refusedBy = caster.LabelShortCap + " has no Pawn_JobTracker; a job cannot be queued."; return null; }
                    // The identical job Ability.QueueCastingJob would have queued,
                    // minus ShowCastingConfirmationIfNeeded's possible modal.
                    var job = castAbility.GetJob(target, LocalTargetInfo.Invalid);
                    accepted = caster.jobs.TryTakeOrderedJob(job, JobTag.Misc, false);
                    if (!accepted)
                        refusedBy = "TryTakeOrderedJob REFUSED. Its refusal path is " +
                                    "TryMakePreToilReservations failing, or the current job being " +
                                    "non-interruptible (playerInterruptible=false, the driver " +
                                    "refusing, or the pawn being on fire).";
                }
                return null;
            }, cancellationToken).ConfigureAwait(false);

            if (setup != null) return setup;

            if (A == "list")
                return new { success = true, action = "list", result = preCast, ticksGame = await ctx.MainThread.InvokeAsync(() => TicksGameSafe(), cancellationToken).ConfigureAwait(false) };

            if (refusedBy != null && !accepted)
            {
                // Restore the speed even on the refusal path - nothing was cast,
                // so the game must not be left running because of this call.
                if (speedChanged)
                {
                    await ctx.MainThread.InvokeAsync(() =>
                    {
                        var tm = Find.TickManager;
                        if (tm != null) { tm.CurTimeSpeed = speedBefore; speedRestored = true; }
                        return 0;
                    }, cancellationToken).ConfigureAwait(false);
                }
                return new
                {
                    success = false,
                    action = "cast",
                    accepted = false,
                    refusedBy,
                    preCast,
                    speedRestored,
                    ticksElapsed = 0,
                    ticksGame = TicksGameSafe(),
                };
            }

            // 🔴 THE SPEED MUST COME BACK EVEN WHEN THE CALL DOES NOT. Everything
            // between here and the read-back can throw on cancellation, so the
            // restore lives in a finally as well as in the happy path.
            var ticksNow = startTicks;
            var timedOut = false;
            try
            {
                var elapsedMs = 0;
                while (waitTicks > 0)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (ticksNow - startTicks >= waitTicks) break;
                    if (elapsedMs >= timeoutSeconds * 1000) { timedOut = true; break; }
                    await Task.Delay(100, cancellationToken).ConfigureAwait(false);
                    elapsedMs += 100;
                    ticksNow = await ctx.MainThread.InvokeAsync(
                        () => TicksGameSafe(), cancellationToken).ConfigureAwait(false);
                }

                return await ctx.MainThread.InvokeAsync<object>(() =>
                {
                    var tm = Find.TickManager;
                    if (speedChanged && tm != null) { tm.CurTimeSpeed = speedBefore; speedRestored = true; }

                    var verb = castAbility != null ? castAbility.verb : null;
                    var elapsed = ticksNow - startTicks;
                    string note;
                    if (elapsed <= 0 && waitTicks > 0)
                        note = "The game did not tick. Nothing could happen - the cast is queued, not performed.";
                    else if (castAbility != null && castAbility.Casting)
                        note = "Still casting - warming up or mid-burst. Call again with waitTicks=0 to sample, or wait longer.";
                    else if (castAbility != null && castAbility.lastCastTick > startTicks)
                        note = "lastCastTick advanced past the start tick: the verb DID fire during this call.";
                    else if (castAbility != null && castAbility.OnCooldown && !wasOnCooldown)
                        note = "The ability went on cooldown during this call, which only happens after a cast.";
                    else
                        note = "No evidence the verb fired. Check the pawn's current job and the verb state below; " +
                               "for a projectile ability, mode='effect' never fires the verb at all.";

                    return new
                    {
                        success = accepted,
                        action = "cast",
                        mode = M,
                        accepted,
                        refusedBy,
                        ticksElapsed = elapsed,
                        timedOut,
                        speedChanged,
                        speedRestored,
                        preCast,
                        readBack = new
                        {
                            pawn = caster != null ? AbilityToolsPawnRow(caster) : null,
                            currentJob = caster != null && caster.CurJobDef != null ? caster.CurJobDef.defName : null,
                            jobIsThisAbility = caster != null && caster.CurJob != null && caster.CurJob.ability == castAbility,
                            stance = caster != null && caster.stances != null && caster.stances.curStance != null
                                ? caster.stances.curStance.GetType().Name : null,
                            verbState = verb != null ? verb.state.ToString() : null,
                            verbWarmingUp = verb != null && verb.WarmingUp,
                            lastCastTick = castAbility != null ? castAbility.lastCastTick : -1,
                            lastCastTickAdvanced = castAbility != null && castAbility.lastCastTick > startTicks,
                            casting = castAbility != null && castAbility.Casting,
                            onCooldown = castAbility != null && castAbility.OnCooldown,
                            cooldownTicksRemaining = castAbility != null ? castAbility.CooldownTicksRemaining : -1,
                            hadDrafter,
                        },
                        note,
                        ticksGame = TicksGameSafe(),
                    };
                }, cancellationToken).ConfigureAwait(false);
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
                            if (tm != null) tm.CurTimeSpeed = speedBefore;
                            return 0;
                        }, CancellationToken.None).ConfigureAwait(false);
                    }
                    catch (Exception) { /* the restore is best-effort on a dying call */ }
                }
            }
        }

        // ================================================================
        //  jawa/pawn_use_verb
        // ================================================================
        [Tool(
            "jawa/pawn_use_verb",
            Description =
                "Make ANY pawn fire one of its VERBS at a target, with no faction or colonist " +
                "check - the sibling of jawa/pawn_use_ability for creature mechanics built as a " +
                "verb rather than an AbilityDef. action='list' enumerates every verb the pawn " +
                "owns and where each came from; action='cast' calls Verb.TryStartCastOn. " +
                "🔑 FIVE SOURCES, all enumerated: 'race' (Pawn.VerbTracker - the animal's own " +
                "tools and any ThingDef verb, which is where a melee bite or an innate ranged " +
                "attack lives), 'equipment', 'apparel' (CompApparelVerbOwner), 'hediff' " +
                "(HediffComp_VerbGiver) and 'ability:<defName>' (the verb behind an AbilityDef). " +
                "An ability's verb appears here too, but firing it through this tool starts the " +
                "verb WITHOUT the ability's job, cooldown or effect comps - use " +
                "jawa/pawn_use_ability for an AbilityDef, and this one for everything else. " +
                "⚠️ Verb.TryStartCastOn refuses with a bare false on three conditions and names " +
                "none of them: the caster is not spawned, the verb is already Bursting, or " +
                "CanHitTarget is false. All three are checked and named here before the call. " +
                "⚠️ It casts FROM WHERE THE PAWN STANDS - there is no pathing. A target beyond " +
                "verbProps.range or inside minRange is simply refused.",
            ResultDescription =
                "action='list': one row per verb with source, id, verbClass, range, warmup, " +
                "burst count, current state, whether the caster can still use it and - when a " +
                "target was given - canHitTarget. action='cast': accepted (the engine's real " +
                "bool), the gate that refused when it did, and a read-back of the verb state, " +
                "the caster's stance and job after the wait.")]
        public static async Task<object> PawnUseVerb(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Caster pawn id, thingId or name. No faction check.")]
            string pawn = null,
            [ToolParameter(Description = "'list' or 'cast'.", DefaultValue = "list")]
            string action = "list",
            [ToolParameter(Description =
                "Which verb to fire, for action='cast'. Matched against the verb's " +
                "GetUniqueLoadID() first, then its verbProps.label, then its class name " +
                "(e.g. 'Verb_MeleeAttackDamage', 'Verb_AbilityShoot'). action='list' prints " +
                "all three for every verb. Ambiguity is reported, never resolved silently.")]
            string verb = null,
            [ToolParameter(Description = "Target: a thing or pawn id. Overrides x/z when given.")]
            string targetId = null,
            [ToolParameter(Description = "Target cell X, when no targetId is given.", DefaultValue = -1)]
            int x = -1,
            [ToolParameter(Description = "Target cell Z, when no targetId is given.", DefaultValue = -1)]
            int z = -1,
            [ToolParameter(Description =
                "Attempt the cast even when CanHitTarget or IsStillUsableBy says no. The checks " +
                "still run and are still reported; this only stops them refusing.",
                DefaultValue = false)]
            bool force = false,
            [ToolParameter(Description = "GAME ticks to wait before reading back. 0 measures only that the call was accepted.", DefaultValue = 120)]
            int waitTicks = 120,
            [ToolParameter(Description = "Wall-clock ceiling on the wait.", DefaultValue = 30)]
            int timeoutSeconds = 30,
            [ToolParameter(Description = "Unpause for the wait and restore the previous speed afterwards.", DefaultValue = true)]
            bool unpause = true)
        {
            var A = (action ?? "list").Trim().ToLowerInvariant();
            if (A != "list" && A != "cast")
                return Fail("action '" + action + "' is not 'list' or 'cast'.");
            if (waitTicks < 0) return Fail("waitTicks must be >= 0, got " + waitTicks + ".");
            if (timeoutSeconds < 1 || timeoutSeconds > 300)
                return Fail("timeoutSeconds must be 1-300, got " + timeoutSeconds + ".");

            Pawn caster = null;
            Verb chosen = null;
            string chosenSource = null;
            var startTicks = -1;
            TimeSpeed speedBefore = TimeSpeed.Paused;
            var speedChanged = false;
            var speedRestored = false;
            var accepted = false;
            string refusedBy = null;
            object preCast = null;

            var setup = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                caster = FindPawn(pawn, out perr);
                if (caster == null) return Fail(perr ?? "No pawn.");

                var verbs = AbilityToolsAllVerbs(caster);

                LocalTargetInfo target = LocalTargetInfo.Invalid;
                string describedAs = null;
                var haveTarget = !string.IsNullOrWhiteSpace(targetId) || (x >= 0 && z >= 0);
                if (haveTarget)
                {
                    var bad = AbilityToolsResolveTarget(caster.Map, targetId, x, z, out target, out describedAs);
                    if (bad != null) return bad;
                }

                if (A == "list")
                {
                    preCast = new
                    {
                        pawn = AbilityToolsPawnRow(caster),
                        target = describedAs,
                        verbCount = verbs.Count,
                        verbs = verbs.Select(kv => AbilityToolsVerbRow(
                            kv.Key, kv.Value, caster,
                            haveTarget ? (LocalTargetInfo?)target : null)).ToList(),
                    };
                    return null;
                }

                // ---- action == "cast"
                if (string.IsNullOrWhiteSpace(verb))
                    return Fail("action='cast' needs a verb. Call action='list' to see the ids.");
                if (!haveTarget)
                    return Fail("action='cast' needs a target: targetId, or x and z.");
                if (!caster.Spawned)
                    return Fail(caster.LabelShortCap + " is not spawned. Verb.TryStartCastOn " +
                                "refuses !caster.Spawned with a bare false.");

                var want = verb.Trim();
                Func<Func<KeyValuePair<string, Verb>, bool>, List<KeyValuePair<string, Verb>>> pick =
                    pred => verbs.Where(pred).ToList();

                var hits = pick(kv => string.Equals(kv.Value.GetUniqueLoadID(), want, StringComparison.OrdinalIgnoreCase));
                if (hits.Count == 0)
                    hits = pick(kv => kv.Value.verbProps != null &&
                                      string.Equals(kv.Value.verbProps.label, want, StringComparison.OrdinalIgnoreCase));
                if (hits.Count == 0)
                    hits = pick(kv => string.Equals(kv.Value.GetType().Name, want, StringComparison.OrdinalIgnoreCase));
                if (hits.Count == 0)
                    return Fail("No verb on " + caster.LabelShortCap + " matching '" + want + "'.",
                        new { verbs = verbs.Select(kv => new { source = kv.Key, id = kv.Value.GetUniqueLoadID(), verbClass = kv.Value.GetType().Name }).ToList() });
                if (hits.Count > 1)
                    return Fail("'" + want + "' matches " + hits.Count + " verbs on " +
                                caster.LabelShortCap + ". Name one by its unique id instead - " +
                                "an ambiguous cast is never resolved silently.",
                        new { matches = hits.Select(kv => new { source = kv.Key, id = kv.Value.GetUniqueLoadID(), verbClass = kv.Value.GetType().Name }).ToList() });

                chosen = hits[0].Value;
                chosenSource = hits[0].Key;

                var usable = chosen.IsStillUsableBy(caster);
                var canHit = chosen.CanHitTarget(target);
                var bursting = chosen.state == VerbState.Bursting;

                preCast = new
                {
                    pawn = AbilityToolsPawnRow(caster),
                    target = describedAs,
                    verb = AbilityToolsVerbRow(chosenSource, chosen, caster, target),
                };

                if (!force)
                {
                    if (bursting)
                        refusedBy = "The verb is already Bursting; TryStartCastOn refuses that outright.";
                    else if (!usable)
                        refusedBy = "Verb.IsStillUsableBy(" + caster.LabelShortCap + ") is false - " +
                                    "the verb is unavailable, its owner refuses it, or its damage " +
                                    "factor for this pawn is 0.";
                    else if (!canHit)
                        refusedBy = "Verb.CanHitTarget is false for " + describedAs + " - out of " +
                                    "range (" + (chosen.verbProps != null ? chosen.verbProps.range : -1f) +
                                    "), inside minRange, or no shootable line. This tool does not " +
                                    "path; the pawn casts from where it stands.";
                    if (refusedBy != null) return null;
                }

                var tm = Find.TickManager;
                startTicks = tm != null ? tm.TicksGame : -1;
                if (tm != null)
                {
                    speedBefore = tm.CurTimeSpeed;
                    if (unpause && waitTicks > 0 && tm.CurTimeSpeed == TimeSpeed.Paused)
                    {
                        tm.CurTimeSpeed = TimeSpeed.Normal;
                        speedChanged = true;
                    }
                }

                accepted = chosen.TryStartCastOn(target);
                if (!accepted)
                    refusedBy = "Verb.TryStartCastOn returned false and gives no reason. The three " +
                                "engine refusals, as computed here: casterSpawned=" + caster.Spawned +
                                ", bursting=" + bursting + ", canHitTarget=" + canHit + ".";
                return null;
            }, cancellationToken).ConfigureAwait(false);

            if (setup != null) return setup;

            if (A == "list")
                return new { success = true, action = "list", result = preCast, ticksGame = await ctx.MainThread.InvokeAsync(() => TicksGameSafe(), cancellationToken).ConfigureAwait(false) };

            if (!accepted)
            {
                if (speedChanged)
                {
                    await ctx.MainThread.InvokeAsync(() =>
                    {
                        var tm = Find.TickManager;
                        if (tm != null) { tm.CurTimeSpeed = speedBefore; speedRestored = true; }
                        return 0;
                    }, cancellationToken).ConfigureAwait(false);
                }
                return new
                {
                    success = false,
                    action = "cast",
                    accepted = false,
                    refusedBy,
                    preCast,
                    speedRestored,
                    ticksElapsed = 0,
                    ticksGame = TicksGameSafe(),
                };
            }

            var ticksNow = startTicks;
            var timedOut = false;
            try
            {
                var elapsedMs = 0;
                while (waitTicks > 0)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (ticksNow - startTicks >= waitTicks) break;
                    if (elapsedMs >= timeoutSeconds * 1000) { timedOut = true; break; }
                    await Task.Delay(100, cancellationToken).ConfigureAwait(false);
                    elapsedMs += 100;
                    ticksNow = await ctx.MainThread.InvokeAsync(
                        () => TicksGameSafe(), cancellationToken).ConfigureAwait(false);
                }

                return await ctx.MainThread.InvokeAsync<object>(() =>
                {
                    var tm = Find.TickManager;
                    if (speedChanged && tm != null) { tm.CurTimeSpeed = speedBefore; speedRestored = true; }
                    var elapsed = ticksNow - startTicks;
                    return new
                    {
                        success = true,
                        action = "cast",
                        accepted = true,
                        ticksElapsed = elapsed,
                        timedOut,
                        speedChanged,
                        speedRestored,
                        preCast,
                        readBack = new
                        {
                            pawn = caster != null ? AbilityToolsPawnRow(caster) : null,
                            verbState = chosen != null ? chosen.state.ToString() : null,
                            verbWarmingUp = chosen != null && chosen.WarmingUp,
                            stance = caster != null && caster.stances != null && caster.stances.curStance != null
                                ? caster.stances.curStance.GetType().Name : null,
                            currentJob = caster != null && caster.CurJobDef != null ? caster.CurJobDef.defName : null,
                        },
                        note = elapsed <= 0 && waitTicks > 0
                            ? "The game did not tick. TryStartCastOn was accepted but nothing has happened yet."
                            : "TryStartCastOn was accepted. A warmup verb shows Stance_Warmup while it winds up; " +
                              "a fired burst shows state=Bursting. Neither persists once the shot is away.",
                        ticksGame = TicksGameSafe(),
                    };
                }, cancellationToken).ConfigureAwait(false);
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
                            if (tm != null) tm.CurTimeSpeed = speedBefore;
                            return 0;
                        }, CancellationToken.None).ConfigureAwait(false);
                    }
                    catch (Exception) { /* best-effort on a dying call */ }
                }
            }
        }
    }
}
