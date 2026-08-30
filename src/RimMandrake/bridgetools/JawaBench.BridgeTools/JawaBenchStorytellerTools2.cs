// JawaBenchStorytellerTools2.cs - eight more gaps: a mech cluster threat, the
// incident queue's clear half, an arbitrary persistent game speed, the
// letter-stack read (+ its gated delayed-send twin), one bundled
// audio/visual-feedback tool, retroactive props on an already-spawned thing,
// and guest/prisoner/slave status - the last unbuilt row in §0 of the roster.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   RimWorld/MechClusterGenerator.cs   GenerateClusterSketch(points, map, startDormant, forceNoConditionCauser)
//   RimWorld/MechClusterUtility.cs     SpawnCluster(center, map, sketch, dropInPods, canAssaultColony, questTag) -
//                                       the SAME utility Verb_MechCluster calls; does the
//                                       sketch spawn, the defend Lord, drop pods, everything.
//   RimWorld/IncidentQueue.cs          Clear() - the ONLY removal method; queuedIncidents
//                                       is private with no per-item Remove, so "clear" is
//                                       the whole capability, not a partial one.
//   Verse/TickManager.cs               CurTimeSpeed - a plain settable property (already
//                                       used, unexported, elsewhere in this codebase).
//   Verse/LetterStack.cs               LettersListForReading; ReceiveLetter(label, text,
//                                       textLetterDef, debugInfo, delayTicks, playSound) -
//                                       delayTicks IS the delayed-letter mechanism, not a
//                                       separate queue.
//   RimWorld/MusicManagerPlay.cs       ForcePlaySong(SongDef, bool ignorePrefsVolume)
//   Verse/CameraShaker.cs              DoShake(float mag) / DoShake(float mag, int durationTicks)
//   RimWorld/FleckMaker.cs             ThrowMetaIcon(IntVec3, Map, FleckDef, float velocitySpeed)
//   Verse/Thing.cs                     HitPoints - public virtual settable property
//   RimWorld/CompQuality.cs            SetQuality(QualityCategory, ArtGenerationContext?)
//   RimWorld/CompStyleable.cs          styleDef - public field
//   RimWorld/Pawn_GuestTracker.cs      SetGuestStatus(Faction newHost, GuestStatus) - a
//                                      self-contained method: it already calls every
//                                      notify/refresh (DisabledWorkTypesChanged,
//                                      AddAndRemoveDynamicComponents, ownership/ideo/
//                                      mechanitor notifies, reachability cache clear) -
//                                      none of the pawn-editing refresh traps apply here.
//
// GATING follows the rule stated in JawaBenchEventTools.cs/GroupTools.cs/
// IncidentTools.cs: #if JAWA_GM_TOOLS is for tools that make THE WORLD ACT on
// the player.
//   GATED:   jawa/spawn_mech_cluster (a live hostile threat, same tier as
//            jawa/fire_raid), jawa/incident_queue_clear (same family as the
//            already-gated jawa/incident_schedule - it manipulates what WILL
//            act on the player), jawa/letter_send_delayed (same tier as the
//            already-gated jawa/send_letter).
//   UNGATED: jawa/letter_list (pure read), jawa/set_game_speed (same tier as
//            the already-ungated jawa/time_set_ticks and
//            jawa/time_pin_normal_speed - time control is treated as a
//            diagnostic/utility lever here, not an incident), jawa/av_effect
//            (cosmetic audio/visual only - no mechanical effect on the
//            colony), jawa/set_thing_props (a field write, the same tier as
//            jawa/build_batch's own at-spawn quality/HP/faction/stuff params).
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  Mech cluster threat
        // ================================================================

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/spawn_mech_cluster",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Generate and spawn a mechanoid cluster threat " +
                "at a point value - MechClusterGenerator.GenerateClusterSketch(points, map, " +
                "startDormant, forceNoConditionCauser) then MechClusterUtility.SpawnCluster(...), " +
                "the exact utility Verb_MechCluster (the in-game 'drop mech cluster' ability) " +
                "calls: buildings + pawns + a defend Lord + drop pods, all wired. Points are " +
                "capped at MechClusterGenerator.MaxPoints (10000) internally by the generator - " +
                "not re-capped here.",
            ResultDescription =
                "success, center, points, startDormant, spawnedThingCount, spawnedThings[] " +
                "(thingId, def, label).")]
        public static async Task<object> SpawnMechCluster(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Centre cell 'x,z'. Required.")]
            string at = null,
            [ToolParameter(Description = "Threat points. Required.")]
            float points = 0f,
            [ToolParameter(Description = "Cluster starts dormant (must be woken/triggered) rather than immediately hostile. Default true.")]
            bool startDormant = true,
            [ToolParameter(Description = "Suppress the cluster's own activation condition-causer building. Default false.")]
            bool forceNoConditionCauser = false,
            [ToolParameter(Description = "Drop pawns/buildings in via drop pods rather than placing them directly. Default true.")]
            bool dropInPods = true,
            [ToolParameter(Description = "Let the cluster's defend Lord also assault the colony, not just defend itself. Default false.")]
            bool canAssaultColony = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (points <= 0f) return Fail("Give 'points', greater than 0.");
                if (!TryParseCellLocal(at, out var cell, out err)) return Fail(err);
                if (!cell.InBounds(map)) return Fail("Cell " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");

                MechClusterSketch sketch;
                try { sketch = MechClusterGenerator.GenerateClusterSketch(points, map, startDormant, forceNoConditionCauser); }
                catch (Exception e) { return Fail("GenerateClusterSketch threw " + e.GetType().Name + ": " + e.Message); }
                if (sketch == null) return Fail("GenerateClusterSketch returned null.");

                List<Thing> spawned;
                try { spawned = MechClusterUtility.SpawnCluster(cell, map, sketch, dropInPods, canAssaultColony); }
                catch (Exception e) { return Fail("SpawnCluster threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    center = new { x = cell.x, z = cell.z },
                    points,
                    startDormant,
                    spawnedThingCount = spawned.Count,
                    spawnedThings = spawned.Select(t => new { thingId = t.ThingID, def = t.def != null ? t.def.defName : null, label = t.LabelCap }).ToList(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Incident queue clear
        // ================================================================

        [Tool(
            "jawa/incident_queue_clear",
            Description =
                "Clear the WHOLE storyteller incident queue - IncidentQueue.Clear(). This is " +
                "the entire capability: the queue's backing list is private with no per-item " +
                "Remove, only Clear(), so a selective cancel does not exist to expose. Lists " +
                "what was cleared before clearing it, so a caller who only wanted to cancel " +
                "one entry can see what else it lost.",
            ResultDescription = "success, clearedCount, cleared[] (defName, fireTick, ticksUntilFireWas).")]
        public static async Task<object> IncidentQueueClear(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null || Find.Storyteller == null) return Fail("No active game/storyteller.");

                int now = TicksGameSafe();
                var cleared = new List<object>();
                foreach (QueuedIncident qi in Find.Storyteller.incidentQueue)
                {
                    cleared.Add(new
                    {
                        defName = qi.FiringIncident != null && qi.FiringIncident.def != null ? qi.FiringIncident.def.defName : null,
                        fireTick = qi.FireTick,
                        ticksUntilFireWas = qi.FireTick - now
                    });
                }

                try { Find.Storyteller.incidentQueue.Clear(); }
                catch (Exception e) { return Fail("IncidentQueue.Clear threw " + e.GetType().Name + ": " + e.Message, new { cleared }); }

                return new
                {
                    success = true,
                    clearedCount = cleared.Count,
                    cleared,
                    ticksGame = now
                };
            }).ConfigureAwait(false);
        }
#endif

        // ================================================================
        //  Game speed
        // ================================================================

        [Tool(
            "jawa/set_game_speed",
            Description =
                "Set TickManager.CurTimeSpeed persistently (Paused/Normal/Fast/Superfast/Ultrafast) - " +
                "unlike jawa/time_pin_normal_speed, this does not expire; it sits at the tier of " +
                "jawa/time_set_ticks, an ungated utility lever, not an incident.",
            ResultDescription = "success, speedBefore, speedAfter.")]
        public static async Task<object> SetGameSpeed(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'Paused', 'Normal', 'Fast', 'Superfast' or 'Ultrafast'. Required.")]
            string speed = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var tm = Find.TickManager;
                if (tm == null) return Fail("No active TickManager - is a game loaded?");

                TimeSpeed s;
                if (string.IsNullOrWhiteSpace(speed) || !Enum.TryParse(speed.Trim(), true, out s))
                    return Fail("'" + speed + "' is not a TimeSpeed. Accepted: " + string.Join(", ", Enum.GetNames(typeof(TimeSpeed))));

                TimeSpeed before = tm.CurTimeSpeed;
                try { tm.CurTimeSpeed = s; }
                catch (Exception e) { return Fail("Setting CurTimeSpeed threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    speedBefore = before.ToString(),
                    speedAfter = tm.CurTimeSpeed.ToString(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Letters
        // ================================================================

        [Tool(
            "jawa/letter_list",
            Description =
                "Read-only: list every letter currently on the stack - LetterStack." +
                "LettersListForReading. The read half of the gated jawa/send_letter and this " +
                "file's own jawa/letter_send_delayed.",
            ResultDescription = "success, count, letters[] (label, defName, arrivalTick, lookTargets summary).")]
        public static async Task<object> LetterList(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.LetterStack == null) return Fail("No active LetterStack - is a game loaded?");

                var rows = Find.LetterStack.LettersListForReading.Select(l => new
                {
                    label = l.Label,
                    defName = l.def != null ? l.def.defName : null,
                    arrivalTick = l.arrivalTick,
                    lookTargets = l.lookTargets != null && l.lookTargets.IsValid ? l.lookTargets.ToString() : null
                }).ToList();

                return new
                {
                    success = true,
                    count = rows.Count,
                    letters = rows,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/letter_send_delayed",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Queue a letter to arrive after 'delayTicks' - " +
                "LetterStack.ReceiveLetter(label, text, textLetterDef, debugInfo, delayTicks, " +
                "playSound). delayTicks IS the delay mechanism (an internal letterQueue " +
                "checked every LetterStackTick) - there is no separate 'schedule' API. Same " +
                "gate tier as jawa/send_letter.",
            ResultDescription = "success, label, textLetterDef, delayTicks, arriveAtTick.")]
        public static async Task<object> LetterSendDelayed(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Letter title. Required.")]
            string label = null,
            [ToolParameter(Description = "Letter body. Required.")]
            string text = null,
            [ToolParameter(Description = "LetterDef defName, e.g. NeutralEvent, PositiveEvent, ThreatBig. Default NeutralEvent.")]
            string textLetterDef = "NeutralEvent",
            [ToolParameter(Description = "Ticks from now before the letter appears on the stack. Required, must be > 0.")]
            int delayTicks = 0,
            [ToolParameter(Description = "Play the letter's arrival sound when it actually arrives. Default true.")]
            bool playSound = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.LetterStack == null) return Fail("No active LetterStack - is a game loaded?");
                if (string.IsNullOrWhiteSpace(label)) return Fail("Give 'label'.");
                if (string.IsNullOrWhiteSpace(text)) return Fail("Give 'text'.");
                if (delayTicks <= 0) return Fail("delayTicks must be > 0 - use jawa/send_letter for an immediate letter.");

                var ldef = DefDatabase<LetterDef>.GetNamedSilentFail((textLetterDef ?? "NeutralEvent").Trim());
                if (ldef == null) return Fail("No LetterDef '" + textLetterDef + "'.", DefSuggestions<LetterDef>(textLetterDef));

                int now = TicksGameSafe();
                try { Find.LetterStack.ReceiveLetter(label, text, ldef, "jawa/letter_send_delayed", delayTicks, playSound); }
                catch (Exception e) { return Fail("ReceiveLetter threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    label,
                    textLetterDef = ldef.defName,
                    delayTicks,
                    arriveAtTick = now + delayTicks,
                    ticksGame = now
                };
            }).ConfigureAwait(false);
        }
#endif

        // ================================================================
        //  Audio/visual feedback (cosmetic - no mechanical colony effect)
        // ================================================================

        [Tool(
            "jawa/av_effect",
            Description =
                "Cosmetic audio/visual feedback, no colony state changed: 'song' forces " +
                "MusicManagerPlay.ForcePlaySong(SongDef, ignorePrefsVolume); 'shake' calls " +
                "CameraDriver.shaker.DoShake(magnitude[, durationTicks]); 'fleck' throws " +
                "FleckMaker.ThrowMetaIcon(cell, map, FleckDef, velocitySpeed) at a cell.",
            ResultDescription = "success, mode, and the resolved def/params used.")]
        public static async Task<object> AvEffect(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'song', 'shake' or 'fleck'. Required.")]
            string mode = null,
            [ToolParameter(Description = "song: SongDef defName. fleck: FleckDef defName.")]
            string def = null,
            [ToolParameter(Description = "shake: magnitude (engine caps at 0.2 * Prefs.ScreenShakeIntensity). fleck: velocitySpeed, default 0.42.")]
            float magnitude = 0f,
            [ToolParameter(Description = "shake: optional duration in ticks - an extended shake request rather than an instant pulse. 0 = instant.")]
            int durationTicks = 0,
            [ToolParameter(Description = "song: ignore the user's music volume preference. Default false.")]
            bool ignorePrefsVolume = false,
            [ToolParameter(Description = "fleck: cell 'x,z'. Required for mode=fleck.")]
            string at = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string m = (mode ?? "").Trim().ToLowerInvariant();

                if (m == "song")
                {
                    if (string.IsNullOrWhiteSpace(def)) return Fail("Give 'def', a SongDef defName.");
                    var sdef = DefDatabase<SongDef>.GetNamedSilentFail(def.Trim());
                    if (sdef == null) return Fail("No SongDef '" + def + "'.", DefSuggestions<SongDef>(def));
                    if (Find.MusicManagerPlay == null) return Fail("No active MusicManagerPlay - is a game loaded?");
                    try { Find.MusicManagerPlay.ForcePlaySong(sdef, ignorePrefsVolume); }
                    catch (Exception e) { return Fail("ForcePlaySong threw " + e.GetType().Name + ": " + e.Message); }
                    return new { success = true, mode = "song", songDef = sdef.defName, ignorePrefsVolume, ticksGame = TicksGameSafe() };
                }

                if (m == "shake")
                {
                    if (magnitude <= 0f) return Fail("Give 'magnitude', greater than 0.");
                    if (Find.CameraDriver == null) return Fail("No active CameraDriver - is a game loaded?");
                    try
                    {
                        if (durationTicks > 0) Find.CameraDriver.shaker.DoShake(magnitude, durationTicks);
                        else Find.CameraDriver.shaker.DoShake(magnitude);
                    }
                    catch (Exception e) { return Fail("DoShake threw " + e.GetType().Name + ": " + e.Message); }
                    return new { success = true, mode = "shake", magnitude, durationTicks, curShakeMagAfter = Find.CameraDriver.shaker.CurShakeMag, ticksGame = TicksGameSafe() };
                }

                if (m == "fleck")
                {
                    string err; var map = MapOrNull(out err);
                    if (map == null) return Fail(err);
                    if (string.IsNullOrWhiteSpace(def)) return Fail("Give 'def', a FleckDef defName.");
                    var fdef = DefDatabase<FleckDef>.GetNamedSilentFail(def.Trim());
                    if (fdef == null) return Fail("No FleckDef '" + def + "'.", DefSuggestions<FleckDef>(def));
                    if (!TryParseCellLocal(at, out var cell, out err)) return Fail(err);
                    if (!cell.InBounds(map)) return Fail("Cell " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");
                    float speed = magnitude > 0f ? magnitude : 0.42f;
                    try { FleckMaker.ThrowMetaIcon(cell, map, fdef, speed); }
                    catch (Exception e) { return Fail("ThrowMetaIcon threw " + e.GetType().Name + ": " + e.Message); }
                    return new { success = true, mode = "fleck", fleckDef = fdef.defName, at = new { x = cell.x, z = cell.z }, velocitySpeed = speed, ticksGame = TicksGameSafe() };
                }

                return Fail("mode must be 'song', 'shake' or 'fleck'.");
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Retroactive thing props
        // ================================================================

        [Tool(
            "jawa/set_thing_props",
            Description =
                "Edit quality/HP/faction/style on a thing ALREADY on the map - jawa/build_batch " +
                "and jawa/spawn_batch only set these AT SPAWN TIME; nothing on this bridge " +
                "edited an existing thing's own properties before now. quality needs " +
                "CompQuality (silently skipped, reported, if absent - not every thing has " +
                "one); hitPoints is clamped to [1, MaxHitPoints] and only written if " +
                "def.useHitPoints; style needs CompStyleable (same silent-skip-and-report rule).",
            ResultDescription =
                "success, thing, changed[] (which of quality/hitPoints/faction/style were " +
                "actually written), skipped[] (which were asked for but the thing has no comp " +
                "for), qualityAfter, hitPointsAfter, maxHitPoints, factionAfter, styleDefAfter.")]
        public static async Task<object> SetThingProps(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id, thingId or name. Required.")]
            string thing = null,
            [ToolParameter(Description = "QualityCategory: Awful/Poor/Normal/Good/Excellent/Masterwork/Legendary. Omit to leave unchanged.")]
            string quality = null,
            [ToolParameter(Description = "New HitPoints. <=0 to leave unchanged.")]
            int hitPoints = 0,
            [ToolParameter(Description = "FactionDef defName, or 'null'/'none' to clear. Omit to leave unchanged.")]
            string faction = null,
            [ToolParameter(Description = "ThingStyleDef defName. Omit to leave unchanged.")]
            string style = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var t = FindLiveThingById(thing, out err);
                if (t == null) return Fail(err);

                var changed = new List<string>();
                var skipped = new List<string>();

                if (!string.IsNullOrWhiteSpace(quality))
                {
                    QualityCategory q;
                    if (!Enum.TryParse(quality.Trim(), true, out q))
                        return Fail("'" + quality + "' is not a QualityCategory. Accepted: " + string.Join(", ", Enum.GetNames(typeof(QualityCategory))));
                    var cq = t.TryGetComp<CompQuality>();
                    if (cq == null) skipped.Add("quality (no CompQuality)");
                    else { cq.SetQuality(q, ArtGenerationContext.Colony); changed.Add("quality"); }
                }

                if (hitPoints > 0)
                {
                    if (!t.def.useHitPoints) skipped.Add("hitPoints (def.useHitPoints is false)");
                    else { t.HitPoints = Math.Min(hitPoints, t.MaxHitPoints); changed.Add("hitPoints"); }
                }

                if (faction != null)
                {
                    if (string.Equals(faction.Trim(), "null", StringComparison.OrdinalIgnoreCase) ||
                        string.Equals(faction.Trim(), "none", StringComparison.OrdinalIgnoreCase))
                    {
                        try { t.SetFaction(null); changed.Add("faction"); }
                        catch (Exception e) { return Fail("SetFaction(null) threw " + e.GetType().Name + ": " + e.Message); }
                    }
                    else
                    {
                        var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                        if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                        var fac = Find.FactionManager.FirstFactionOfDef(fd);
                        if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                        try { t.SetFaction(fac); changed.Add("faction"); }
                        catch (Exception e) { return Fail("SetFaction threw " + e.GetType().Name + ": " + e.Message); }
                    }
                }

                if (!string.IsNullOrWhiteSpace(style))
                {
                    var sdef = DefDatabase<ThingStyleDef>.GetNamedSilentFail(style.Trim());
                    if (sdef == null) return Fail("No ThingStyleDef '" + style + "'.", DefSuggestions<ThingStyleDef>(style));
                    var cs = t.TryGetComp<CompStyleable>();
                    if (cs == null) skipped.Add("style (no CompStyleable)");
                    else { cs.styleDef = sdef; changed.Add("style"); }
                }

                if (changed.Count == 0 && skipped.Count == 0)
                    return Fail("Nothing to do - give at least one of quality, hitPoints, faction, style.");

                var qAfter = t.TryGetComp<CompQuality>();
                var sAfter = t.TryGetComp<CompStyleable>();
                return new
                {
                    success = true,
                    thing = t.LabelCap,
                    changed,
                    skipped,
                    qualityAfter = qAfter != null ? qAfter.Quality.ToString() : null,
                    hitPointsAfter = t.def.useHitPoints ? (int?)t.HitPoints : null,
                    maxHitPoints = t.def.useHitPoints ? (int?)t.MaxHitPoints : null,
                    factionAfter = t.Faction != null ? t.Faction.Name : null,
                    styleDefAfter = sAfter != null && sAfter.styleDef != null ? sAfter.styleDef.defName : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Guest / prisoner / slave status
        // ================================================================

        [Tool(
            "jawa/pawn_set_guest_status",
            Description =
                "Set a pawn's guest/prisoner/slave status - Pawn_GuestTracker.SetGuestStatus" +
                "(newHost, guestStatus). Self-contained: the engine method already runs every " +
                "notify/refresh this needs (disabled work types, dynamic components, " +
                "ownership/ideo/mechanitor notifies, reachability cache, attack-targets cache) " +
                "- none of the usual pawn-editing refresh traps apply here, unlike " +
                "jawa/set_pawn_backstory or jawa/set_pawn_appearance. Refuses (Log.Error inside " +
                "the engine call, surfaced here rather than swallowed) if guestStatus=Guest and " +
                "the pawn's own faction is hostile to newHost, or newHost equals the pawn's own " +
                "faction.",
            ResultDescription =
                "success, pawn, hostFactionBefore/After, guestStatusBefore/After, " +
                "resistanceAfter and willAfter (Prisoner only, freshly rolled by the engine call).")]
        public static async Task<object> PawnSetGuestStatus(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name. Required.")]
            string pawn = null,
            [ToolParameter(Description = "'Guest', 'Prisoner' or 'Slave'. Required.")]
            string guestStatus = null,
            [ToolParameter(Description = "Host FactionDef defName. Omit/'null'/'none' for no host (only valid for Guest).")]
            string hostFaction = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.guest == null) return Fail(p.LabelShortCap + " has no Pawn_GuestTracker (guest is null) - not a humanlike pawn?");

                GuestStatus gs;
                if (string.IsNullOrWhiteSpace(guestStatus) || !Enum.TryParse(guestStatus.Trim(), true, out gs))
                    return Fail("'" + guestStatus + "' is not a GuestStatus. Accepted: " + string.Join(", ", Enum.GetNames(typeof(GuestStatus))));

                Faction newHost = null;
                if (!string.IsNullOrWhiteSpace(hostFaction) &&
                    !string.Equals(hostFaction.Trim(), "null", StringComparison.OrdinalIgnoreCase) &&
                    !string.Equals(hostFaction.Trim(), "none", StringComparison.OrdinalIgnoreCase))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(hostFaction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + hostFaction + "'.", DefSuggestions<FactionDef>(hostFaction));
                    newHost = Find.FactionManager.FirstFactionOfDef(fd);
                    if (newHost == null) return Fail("FactionDef '" + hostFaction + "' exists but no such faction is in this world.");
                }

                var hostBefore = p.guest.HostFaction;
                var statusBefore = p.guest.GuestStatus;

                try { p.guest.SetGuestStatus(newHost, gs); }
                catch (Exception e) { return Fail("SetGuestStatus threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    pawn = p.LabelShortCap,
                    hostFactionBefore = hostBefore != null ? hostBefore.Name : null,
                    hostFactionAfter = p.guest.HostFaction != null ? p.guest.HostFaction.Name : null,
                    guestStatusBefore = statusBefore.ToString(),
                    guestStatusAfter = p.guest.GuestStatus.ToString(),
                    resistanceAfter = gs == GuestStatus.Prisoner ? (float?)p.guest.resistance : null,
                    willAfter = gs == GuestStatus.Prisoner ? (float?)p.guest.will : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
