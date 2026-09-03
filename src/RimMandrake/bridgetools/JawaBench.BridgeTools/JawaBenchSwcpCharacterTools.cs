// JawaBenchSwcpCharacterTools.cs - SWCP:Characters' own authored-character ROSTER,
// distinct from any generic PawnKindDef spawn.
//
// WHY THIS FILE EXISTS
// =====================
// SWCP_CHARACTERS_DECOMPILE_1, owner ruling "Yes, decompile it" - the character/
// pawnkind roster subsystem of "Star Wars KotOR Resources and Materials"
// (packageId guy762.MM.KotORCore), because character/pawnkind roster generation
// is what B45-B51 and the whole faction-slate effort is about.
//
// DECOMPILED, NOT GUESSED: ilspycmd 9.0.0.7889 (ICSharpCode.Decompiler 9.0.0.7889)
// against
//   C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3254370945\1.6\Assemblies\SWCP_Core.dll
// output tree: vendor/mod_sources/SWCP_Core_decompiled/ (gitignored, derived,
// regenerate with the command above against the live DLL - see
// research/RimMandrake/reference/rimworld_decompiled_source.md for the pattern).
// The mod's other four DLLs in the same folder (SWCPEnlist, SWCP_Currencies,
// SWCP_RimframeGrineerDoors, SWCP_Shuttles) were ALSO decompiled and searched -
// none of them contain a CharacterDef, a role registry, or any of the debug
// action names the owner recalled ("pool"/"displaced"/"roster"/"authored" match
// nowhere in any of the five). SWCP_Core.dll's actual debug category is
// "SWCP: Characters" (DebugActionsUniqueCharacters.cs) with exactly three
// actions: GenerateCharacter, LogCharacters, LogRoles - narrower than the
// item's paraphrased list, but the mechanism underneath is exactly what the
// item predicted: a named, AUTHORED-character roster distinct from a
// pawnKind-generic spawn.
//
// THE MECHANISM, READ FROM SOURCE (SWCP.Core/*.cs):
//   CharacterDef : Verse.Def                 pawnKind, faction, xenotype FIELDS;
//                                             definitions: List<CharacterBaseDefinition>
//                                             (appearance/story/title/unique-item,
//                                             applied pre- and post-generation);
//                                             roles: List<CharacterRole>
//   CharacterRole                             base; ApplyRole(Pawn) / PawnIsValid(Pawn)
//   CharacterRole_FactionLeader : CharacterRole
//                                             ApplyRole sets faction.leader = pawn,
//                                             syncs pawn.ideo to the faction's primary
//   CharacterRoleUtils                        [StaticConstructorOnStartup] builds
//                                             Dictionary<Type, IList> RoleRegistry
//                                             once at startup - the exact "role
//                                             registry" the owner's Player.log line
//                                             names ("Failed to retrieve a
//                                             CharacterDefWithRole<TRole> list...")
//   UniqueCharactersTracker : WorldComponent  THE roster. `characters`: private
//                                             List<UniqueCharacter>, one entry PER
//                                             CharacterDef that has EVER been drawn.
//                                             GetOrGenPawn(charDef, request=null,
//                                             faction=null): returns the SAME pawn
//                                             on every call after the first - a
//                                             SINGLETON per CharacterDef, generated
//                                             once, applies DEFINITIONS ONLY (never
//                                             roles - ApplyRole is called from one
//                                             place in the whole assembly, the
//                                             faction-leader Harmony patch in
//                                             Patches.cs), then PassToWorld. Its
//                                             `forcedFaction` argument is dead: the
//                                             body never reads it, always taking
//                                             FirstFactionOfDef(charDef.faction).
//                                             THIS is the capability
//                                             jawa/spawn_pawn cannot express: it
//                                             always rolls a fresh pawn.
//   UniqueCharacter : IExposable              def (CharacterDef), pawn (Pawn) - both
//                                             PUBLIC FIELDS.
//
// EVERYTHING HERE IS REFLECTION, ON PURPOSE, same rule as every other file in this
// folder: JawaBench.BridgeTools.csproj references only RimBridgeServer.Sdk,
// Assembly-CSharp and UnityEngine.CoreModule, so the companion loads fine on an
// install where SWCP is absent. A reflection miss returns null/refuses by name
// rather than throwing.
//
// 🔴 `characters` on UniqueCharactersTracker is a PRIVATE field with no public
// getter for "which pawn does this CharacterDef currently have" - the only public
// route is GetOrGenPawn, which GENERATES on a miss. A read-only roster listing
// therefore reads the RAW PRIVATE FIELD via reflection (BindingFlags.NonPublic) -
// the "read the raw field" rule from the companion skill, applied because here the
// convenient API has a SIDE EFFECT, not just a lossy getter.
//
// CharacterDef, UniqueCharacter, CharacterRole and CharacterBaseDefinition are all
// SWCP-only types and stay behind reflection throughout. Their `pawn`/`pawnKind`/
// `faction`/`xenotype` FIELD VALUES are ordinary Verse.Pawn / RimWorld.PawnKindDef /
// RimWorld.FactionDef / RimWorld.XenotypeDef instances (vanilla types shared with
// this project's own Assembly-CSharp reference), so once read out by reflection
// they are cast directly - no further reflection needed on them. CharacterDef
// itself derives from Verse.Def (confirmed in source), so it is cast straight to
// the vanilla `Def` base for defName/label, exactly like the KCSG def families in
// JawaBenchKcsgTools.cs.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags SwcpPrivInst = BindingFlags.NonPublic | BindingFlags.Instance;

        /// <summary>Read a private OR public instance field, or null when it is not there.</summary>
        private static object FieldOrNullAny(object obj, string name)
        {
            if (obj == null) return null;
            FieldInfo fi = obj.GetType().GetField(name, PubInst | SwcpPrivInst);
            if (fi == null) return null;
            try { return fi.GetValue(obj); }
            catch (Exception) { return null; }
        }

        /// <summary>SWCP.Core.UniqueCharactersTracker.Instance, or null (no World loaded, or SWCP absent).</summary>
        private static object SwcpTrackerInstance(out Type trackerType)
        {
            trackerType = GenTypes.GetTypeInAnyAssembly("SWCP.Core.UniqueCharactersTracker");
            if (trackerType == null) return null;
            PropertyInfo pi = trackerType.GetProperty("Instance", BindingFlags.Public | BindingFlags.Static);
            object inst = pi?.GetValue(null);
            if (inst == null) return null;
            // 🔴 `Instance` is a static assigned in the WorldComponent's constructor and in
            // FinalizeInit, and NEVER cleared. Quit a game to the main menu and it still
            // points at the DEAD world's tracker, so an ungated read reports a discarded
            // game's roster as live state. WorldComponent.world is the tell.
            if (Current.Game == null || Current.Game.World == null) return null;
            if (!ReferenceEquals(FieldOrNullAny(inst, "world"), Current.Game.World)) return null;
            return inst;
        }

        /// <summary>
        /// defName -> currently tracked Pawn (may be null for a tracked-but-unresolved
        /// entry), read straight from the tracker's private `characters` field. Never
        /// generates anything.
        /// </summary>
        private static Dictionary<string, Pawn> SwcpBuildTrackedPawnMap(out bool trackerAvailable)
        {
            trackerAvailable = false;
            var map = new Dictionary<string, Pawn>(StringComparer.OrdinalIgnoreCase);
            object tracker = SwcpTrackerInstance(out _);
            if (tracker == null) return map;
            trackerAvailable = true;
            IEnumerable list = FieldOrNullAny(tracker, "characters") as IEnumerable;
            if (list == null) return map;
            foreach (object entry in list)
            {
                if (entry == null) continue;
                Def d = FieldOrNull(entry, "def") as Def;
                if (d == null || string.IsNullOrEmpty(d.defName)) continue;
                map[d.defName] = FieldOrNull(entry, "pawn") as Pawn;
            }
            return map;
        }

        private static List<string> SwcpNameSuggestions(IEnumerable allDefs, string query)
        {
            var names = new List<string>();
            if (allDefs == null) return names;
            foreach (object o in allDefs)
            {
                Def d = o as Def;
                if (d != null && !string.IsNullOrEmpty(d.defName)) names.Add(d.defName);
            }
            string q = (query ?? "").Trim();
            return names
                .Where(n => n.IndexOf(q, StringComparison.OrdinalIgnoreCase) >= 0)
                .OrderBy(n => n, StringComparer.OrdinalIgnoreCase)
                .Take(8)
                .ToList();
        }

        [Tool(
            "jawa/swcp_character_roster",
            Description =
                "List every authored character from SWCP:Characters (SWCP_Core.dll, mod " +
                "'Star Wars KotOR Resources and Materials', guy762.MM.KotORCore) - the mod's " +
                "own named-character ROSTER, distinct from any generic PawnKindDef. Each " +
                "CharacterDef bundles a pawnKind, faction, optional xenotype, a list of " +
                "appearance/story/title/unique-item DEFINITIONS applied on generation, and " +
                "zero or more ROLES (e.g. CharacterRole_FactionLeader, whose ApplyRole would " +
                "make a pawn that faction's leader and sync its ideo - but SWCP only ever " +
                "calls ApplyRole from its own faction-leader patch, never from GetOrGenPawn, " +
                "so roleTypes[] is what the def DECLARES, not what any drawn pawn HAS). " +
                "READ ONLY - generates " +
                "nothing. When a World is loaded this also reports each character's LIVE " +
                "tracked state, read straight from UniqueCharactersTracker's own private " +
                "roster field: whether it has EVER been drawn (tracked), whether that pawn " +
                "still exists/is alive/is currently spawned, and where. Use " +
                "jawa/swcp_character_spawn to actually draw or place one. Refuses by name if " +
                "SWCP_Core.dll is not loaded.",
            ResultDescription =
                "success, characterCount, trackerAvailable (a World is loaded so live state " +
                "could be read), characters[]: defName, label, pawnKindDef, factionDef, " +
                "xenotypeDef, roleTypes[], definitionCount, tracked, pawnExists, alive, dead, " +
                "spawned, thingId, mapId, position.")]
        public static async Task<object> SwcpCharacterRoster(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Only include characters with at least one role type whose short name CONTAINS this, case-insensitive (e.g. 'FactionLeader'). Empty = all.")]
            string roleFilter = null,
            [ToolParameter(Description = "Only include characters that have been drawn/tracked at least once this game (a UniqueCharacter entry exists). Default false = list every authored CharacterDef.")]
            bool trackedOnly = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                Type charDefType = GenTypes.GetTypeInAnyAssembly("SWCP.Core.CharacterDef");
                if (charDefType == null)
                    return Fail("SWCP:Characters is not loaded - SWCP.Core.CharacterDef not found in any " +
                                "assembly. Expect SWCP_Core.dll (mod 'Star Wars KotOR Resources and " +
                                "Materials', guy762.MM.KotORCore).");

                IEnumerable allDefs = KcsgAllDefs(charDefType);
                if (allDefs == null)
                    return Fail("SWCP.Core.CharacterDef resolved but DefDatabase<CharacterDef>." +
                                "AllDefsListForReading could not be read.");

                bool trackerAvailable;
                Dictionary<string, Pawn> tracked = SwcpBuildTrackedPawnMap(out trackerAvailable);

                var rows = new List<object>();
                foreach (object cdObj in allDefs)
                {
                    Def d = cdObj as Def;
                    if (d == null || string.IsNullOrEmpty(d.defName)) continue;

                    var roleTypes = new List<string>();
                    IEnumerable roleList = FieldOrNull(cdObj, "roles") as IEnumerable;
                    if (roleList != null)
                        foreach (object r in roleList) if (r != null) roleTypes.Add(r.GetType().Name);

                    if (!string.IsNullOrEmpty(roleFilter) &&
                        !roleTypes.Any(rt => rt.IndexOf(roleFilter, StringComparison.OrdinalIgnoreCase) >= 0))
                        continue;

                    int definitionCount = 0;
                    IEnumerable defList = FieldOrNull(cdObj, "definitions") as IEnumerable;
                    if (defList != null) foreach (object x in defList) definitionCount++;

                    bool isTracked = tracked.TryGetValue(d.defName, out Pawn p);
                    if (trackedOnly && !isTracked) continue;

                    bool pawnExists = isTracked && p != null && !p.Discarded;
                    bool alive = pawnExists && !p.Dead;
                    bool spawned = pawnExists && p.Spawned;

                    var pawnKindDef = FieldOrNull(cdObj, "pawnKind") as PawnKindDef;
                    var factionDef = FieldOrNull(cdObj, "faction") as FactionDef;
                    var xenotypeDef = FieldOrNull(cdObj, "xenotype") as XenotypeDef;

                    rows.Add(new
                    {
                        defName = d.defName,
                        label = string.IsNullOrEmpty(d.label) ? d.defName : d.label,
                        pawnKindDef = pawnKindDef?.defName,
                        factionDef = factionDef?.defName,
                        xenotypeDef = xenotypeDef?.defName,
                        roleTypes,
                        definitionCount,
                        tracked = isTracked,
                        pawnExists,
                        alive,
                        dead = pawnExists && p.Dead,
                        spawned,
                        thingId = pawnExists ? p.ThingID : null,
                        mapId = spawned ? p.Map?.uniqueID : null,
                        position = spawned ? p.Position.ToString() : null,
                    });
                }

                return new
                {
                    success = true,
                    characterCount = rows.Count,
                    trackerAvailable,
                    characters = rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/swcp_character_spawn",
            Description =
                "Get-or-generate and place ON THE MAP one SWCP:Characters authored character " +
                "by defName - UniqueCharactersTracker.GetOrGenPawn, the mod's own SINGLETON " +
                "roster mechanic. NOT a duplicate of jawa/spawn_pawn: each CharacterDef maps " +
                "to AT MOST ONE persistent Pawn for the whole game - the first call GENERATES " +
                "it (applying its appearance/story/title/unique-item DEFINITIONS), and every " +
                "later call reuses the SAME pawn rather than rolling a fresh one. " +
                "🔴 ROLES ARE NOT APPLIED. GetOrGenPawn only runs " +
                "CharacterDefinitionUtils.ApplyRequestDefinitions/ApplyPawnDefinitions; " +
                "CharacterRole.ApplyRole is called from exactly one place in SWCP_Core - its " +
                "own faction-leader Harmony patch, which additionally gates on " +
                "PawnIsValid and on the pawn already belonging to that faction. So a " +
                "CharacterRole_FactionLeader character drawn through this tool is NOT made " +
                "faction leader and its ideo is NOT synced. " +
                "If that pawn is already spawned somewhere this REFUSES " +
                "to move it unless forceRespawn=true. Refuses by name if SWCP_Core.dll is not " +
                "loaded or if 'character' is not a real CharacterDef defName.",
            ResultDescription =
                "success, defName, thingId, label, factionDef, pawnKindDef, xenotypeDef, " +
                "mapId, position, wasNewlyGenerated, wasAlreadySpawned, moved, ticksGame.")]
        public static async Task<object> SwcpCharacterSpawn(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "CharacterDef defName. Required. jawa/swcp_character_roster lists them.")]
            string character = null,
            [ToolParameter(Description = "Cell X. Omit (with z) for map center.")]
            int? x = null,
            [ToolParameter(Description = "Cell Z. Omit (with x) for map center.")]
            int? z = null,
            [ToolParameter(Description = "If the pawn is already spawned elsewhere, despawn it there and respawn it at the given cell instead of refusing. Default false.")]
            bool forceRespawn = false)
        {
            if (string.IsNullOrWhiteSpace(character))
                return Fail("Give 'character' - a SWCP CharacterDef defName. jawa/swcp_character_roster lists them.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; Map map = MapOrNull(out err);
                if (map == null) return Fail(err);

                Type charDefType = GenTypes.GetTypeInAnyAssembly("SWCP.Core.CharacterDef");
                if (charDefType == null)
                    return Fail("SWCP:Characters is not loaded - SWCP.Core.CharacterDef not found in any assembly.");

                Def charDef = KcsgGetNamed(charDefType, character.Trim());
                if (charDef == null)
                    return Fail($"No SWCP CharacterDef '{character}'.",
                        new { suggestions = SwcpNameSuggestions(KcsgAllDefs(charDefType), character) });

                Type trackerType;
                object tracker = SwcpTrackerInstance(out trackerType);
                if (trackerType == null)
                    return Fail("SWCP.Core.UniqueCharactersTracker not found by reflection - is SWCP_Core.dll actually loaded?");
                if (tracker == null)
                    return Fail("UniqueCharactersTracker.Instance is null - no World loaded yet.");

                // Pre-check the RAW field before calling GetOrGenPawn (which has a side
                // effect on a miss), so the result can report generated-vs-reused honestly.
                Pawn existing = null;
                IEnumerable existingList = FieldOrNullAny(tracker, "characters") as IEnumerable;
                if (existingList != null)
                {
                    foreach (object entry in existingList)
                    {
                        if (!ReferenceEquals(FieldOrNull(entry, "def"), charDef)) continue;
                        existing = FieldOrNull(entry, "pawn") as Pawn;
                        break;
                    }
                }
                bool wasNewlyGenerated = existing == null || existing.Discarded;
                bool wasAlreadySpawned = existing != null && !existing.Discarded && existing.Spawned;

                if (wasAlreadySpawned && !forceRespawn)
                {
                    return new
                    {
                        success = true,
                        defName = ((Def)charDef).defName,
                        thingId = existing.ThingID,
                        label = existing.LabelShortCap,
                        factionDef = existing.Faction?.def?.defName,
                        pawnKindDef = existing.kindDef?.defName,
                        xenotypeDef = existing.genes?.Xenotype?.defName,
                        mapId = existing.Map?.uniqueID,
                        position = existing.Position.ToString(),
                        wasNewlyGenerated = false,
                        wasAlreadySpawned = true,
                        moved = false,
                        note = "Already alive and spawned - not moving it. Pass forceRespawn=true to relocate.",
                        ticksGame = TicksGameSafe(),
                    };
                }

                MethodInfo getOrGen = trackerType.GetMethod("GetOrGenPawn", BindingFlags.Public | BindingFlags.Instance);
                if (getOrGen == null) return Fail("SWCP.Core.UniqueCharactersTracker.GetOrGenPawn not found by reflection.");

                object result;
                try { result = getOrGen.Invoke(tracker, new object[] { charDef, null, null }); }
                catch (TargetInvocationException tie)
                {
                    return Fail("GetOrGenPawn threw: " + (tie.InnerException != null ? tie.InnerException.Message : tie.Message));
                }
                Pawn pawn = result as Pawn;
                if (pawn == null) return Fail("GetOrGenPawn returned no pawn.");

                IntVec3 cell = (x.HasValue && z.HasValue) ? new IntVec3(x.Value, 0, z.Value) : map.Center;
                if (!cell.InBounds(map))
                    return Fail("Cell " + cell + " is out of bounds for this map. GenSpawn.Spawn logs and " +
                        "returns null on an out-of-bounds cell rather than throwing, which for " +
                        "forceRespawn=true would leave this singleton character DESPAWNED with no way back.");

                bool moved = false;
                if (pawn.Spawned)
                {
                    if (forceRespawn)
                    {
                        pawn.DeSpawn(DestroyMode.Vanish);
                        Pawn respawned = GenSpawn.Spawn(pawn, cell, map, WipeMode.Vanish) as Pawn;
                        if (respawned == null || !pawn.Spawned)
                            return Fail("GenSpawn.Spawn failed after despawning " + pawn.LabelShortCap +
                                " for the move - the character is now UNSPAWNED. Cell was " + cell + ".");
                        moved = true;
                    }
                    // else: became spawned concurrently since the pre-check - report as-is, don't move it.
                }
                else
                {
                    Pawn spawned = GenSpawn.Spawn(pawn, cell, map, WipeMode.Vanish) as Pawn;
                    if (spawned == null || !pawn.Spawned)
                        return Fail("GenSpawn.Spawn failed for " + pawn.LabelShortCap + " at " + cell + ".");
                }

                return new
                {
                    success = true,
                    defName = ((Def)charDef).defName,
                    thingId = pawn.ThingID,
                    label = pawn.LabelShortCap,
                    factionDef = pawn.Faction?.def?.defName,
                    pawnKindDef = pawn.kindDef?.defName,
                    xenotypeDef = pawn.genes?.Xenotype?.defName,
                    mapId = pawn.Map?.uniqueID,
                    position = pawn.Position.ToString(),
                    wasNewlyGenerated,
                    wasAlreadySpawned,
                    moved,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
