// JawaBenchPawnTools.cs - deep pawn editing.
//
// Owner, 2026-08-19: "Finely modify pawns especially their traits, backgrounds,
// names, backstories and notes, religions, faction, equipment... everything."
//
// 🔴 NOTES DO NOT EXIST. There is no free-text note field on Pawn or any
// Pawn_*Tracker in 1.6/Odyssey. Pawn is not IRenameable, there is no
// Dialog_Note, and Pawn_RecordsTracker is a numeric DefMap<RecordDef,float>.
// The ONLY writable free text is pawn.story.Title. Anything richer has to be
// storage we build ourselves. Do not fake it.
//
// 🔴 THE REFRESH TRAPS - every one of these is a silent failure:
//  * Setting a backstory refreshes NOTHING. The setters only null
//    backstoriesCache. The game's own debug tool does one of the four needed
//    calls; this file does all four.
//  * GainTrait does NOT check conflicts and TraitSet has NO trait cap.
//  * SkillRecord.Level's GETTER adds aptitudes, so read-back != what you wrote.
//    Verify against GetLevel(false).
//  * Appearance writes do not dirty the renderer.
//
// Every signature read from 1.6 source. Census:
//   design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md §3

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static Pawn FindPawn(string id, out string err)
        {
            err = null;
            if (string.IsNullOrEmpty(id)) { err = "Give a pawn id, name or thingId."; return null; }
            id = id.Trim();
            // 🔑 BOTH ID FORMS. jawa/list_pawns reports the bare 'Human45731' while some
            // bridge tools hand back the prefixed 'Thing_Human45731', and a caller passing
            // the wrong one used to get a clean zero-count success rather than an error
            // (BRIDGE_ARG_SHAPES_INCONSISTENT_1 row 1). They name the same pawn, so accept
            // either rather than making the caller know which tool produced the string.
            if (id.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) && id.Length > 6)
                id = id.Substring(6);
            var maps = Find.Maps ?? new List<Map>();
            var all = new List<Pawn>();
            foreach (var m in maps) all.AddRange(m.mapPawns.AllPawnsSpawned);
            int n;
            if (int.TryParse(id, out n))
            {
                var byId = all.FirstOrDefault(p => p.thingIDNumber == n);
                if (byId != null) return byId;
            }
            var exact = all.FirstOrDefault(p => string.Equals(p.ThingID, id, StringComparison.OrdinalIgnoreCase));
            if (exact != null) return exact;
            var byName = all.FirstOrDefault(p => p.Name != null &&
                (string.Equals(p.Name.ToStringShort, id, StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(p.Name.ToStringFull, id, StringComparison.OrdinalIgnoreCase) ||
                 string.Equals(p.LabelShort, id, StringComparison.OrdinalIgnoreCase)));
            if (byName != null) return byName;

            // 🔑 OFF-MAP FALLBACK (BRIDGE_PAWN_THOUGHTS_CARAVAN_GAP_1): a caravan member (or
            // any other pawn currently "passed to world" - a prisoner in transit, a pawn on
            // a map that isn't loaded) is never in mapPawns.AllPawnsSpawned above even though
            // it clearly exists. WorldPawns.AllPawnsAlive covers exactly this population
            // (caravans PassToWorld() every member) - try it before giving up. Same match
            // order/rules as the map pass; a pawn present on BOTH lists (unlikely, but not
            // impossible mid-transition) is already returned by the map pass above and never
            // reaches here, so there is no double-match ambiguity to resolve.
            var world = Find.WorldPawns != null ? Find.WorldPawns.AllPawnsAlive : null;
            if (world != null)
            {
                int nw;
                if (int.TryParse(id, out nw))
                {
                    var byIdW = world.FirstOrDefault(p => p.thingIDNumber == nw);
                    if (byIdW != null) return byIdW;
                }
                var exactW = world.FirstOrDefault(p => string.Equals(p.ThingID, id, StringComparison.OrdinalIgnoreCase));
                if (exactW != null) return exactW;
                var byNameW = world.FirstOrDefault(p => p.Name != null &&
                    (string.Equals(p.Name.ToStringShort, id, StringComparison.OrdinalIgnoreCase) ||
                     string.Equals(p.Name.ToStringFull, id, StringComparison.OrdinalIgnoreCase) ||
                     string.Equals(p.LabelShort, id, StringComparison.OrdinalIgnoreCase)));
                if (byNameW != null) return byNameW;
            }

            err = "No spawned or world pawn matching '" + id + "'. " + all.Count + " pawns are spawned, "
                  + (world != null ? world.Count.ToString() : "0") + " are world pawns (caravans, transit, etc.). "
                  + "Accepted: the bare thingID ('Human45731'), the same with a 'Thing_' prefix, "
                  + "the numeric thingIDNumber, or the pawn's name. jawa/list_pawns reports the bare form.";
            return null;
        }

        /// <summary>Everything a caller needs to see, read RAW where the getter lies.</summary>
        private static object PawnSnapshot(Pawn p)
        {
            var traits = new List<object>();
            if (p.story != null && p.story.traits != null)
                foreach (var t in p.story.traits.allTraits)
                    traits.Add(new { def = t.def.defName, degree = t.Degree, label = t.LabelCap, forced = t.ScenForced });

            var skills = new List<object>();
            if (p.skills != null)
                foreach (var sr in p.skills.skills)
                    skills.Add(new
                    {
                        skill = sr.def.defName,
                        // Level's getter ADDS APTITUDES. levelRaw is what was actually written.
                        levelRaw = sr.GetLevel(false),
                        levelEffective = sr.Level,
                        passion = sr.passion.ToString(),
                        xpSinceLastLevel = sr.xpSinceLastLevel,
                        disabled = sr.TotallyDisabled,
                    });

            var apparel = new List<object>();
            if (p.apparel != null)
                foreach (var a in p.apparel.WornApparel)
                    // `defName` is an ALIAS of `def`, and it is here because reading
                    // `.defName` off these rows returned null for twelve armed droids and
                    // was written up as "the Free Droid Enclaves field unarmed droids"
                    // (BRIDGE_ARG_SHAPES_INCONSISTENT_1 row 3). Both keys, same value.
                    apparel.Add(new { def = a.def.defName, defName = a.def.defName, stuff = a.Stuff != null ? a.Stuff.defName : null, hp = a.HitPoints });

            var equipment = new List<object>();
            if (p.equipment != null)
                foreach (var e in p.equipment.AllEquipmentListForReading)
                    equipment.Add(new { def = e.def.defName, defName = e.def.defName, stuff = e.Stuff != null ? e.Stuff.defName : null, isPrimary = e == p.equipment.Primary });

            var hediffs = new List<object>();
            if (p.health != null && p.health.hediffSet != null)
                foreach (var h in p.health.hediffSet.hediffs.Take(40))
                    hediffs.Add(new { def = h.def.defName, part = h.Part != null ? h.Part.def.defName : null, severity = h.Severity });

            var needs = new List<object>();
            if (p.needs != null && p.needs.AllNeeds != null)
                foreach (var nd in p.needs.AllNeeds)
                    needs.Add(new { need = nd.def.defName, level = nd.CurLevel, pct = nd.CurLevelPercentage });

            return new
            {
                thingId = p.ThingID,
                thingIdNumber = p.thingIDNumber,
                name = p.Name != null ? p.Name.ToStringFull : null,
                nameShort = p.LabelShort,
                title = p.story != null ? p.story.Title : null,
                kindDef = p.kindDef != null ? p.kindDef.defName : null,
                faction = p.Faction != null ? p.Faction.def.defName : null,
                factionName = p.Faction != null ? p.Faction.Name : null,
                gender = p.gender.ToString(),
                ageBiologicalYears = p.ageTracker != null ? p.ageTracker.AgeBiologicalYears : -1,
                ageChronologicalYears = p.ageTracker != null ? p.ageTracker.AgeChronologicalYears : -1,
                developmentalStage = p.DevelopmentalStage.ToString(),
                xenotype = p.genes != null && p.genes.Xenotype != null ? p.genes.Xenotype.defName : null,
                ideo = p.Ideo != null ? p.Ideo.name : null,
                childhood = p.story != null && p.story.Childhood != null ? p.story.Childhood.defName : null,
                adulthood = p.story != null && p.story.Adulthood != null ? p.story.Adulthood.defName : null,
                headType = p.story != null && p.story.headType != null ? p.story.headType.defName : null,
                bodyType = p.story != null && p.story.bodyType != null ? p.story.bodyType.defName : null,
                hair = p.story != null && p.story.hairDef != null ? p.story.hairDef.defName : null,
                beard = p.style != null && p.style.beardDef != null ? p.style.beardDef.defName : null,
                position = p.Spawned ? (object)new { x = p.Position.x, z = p.Position.z } : null,
                traits, skills, apparel, equipment, hediffs, needs,
            };
        }

        [Tool(
            "jawa/pawn_get",
            Description =
                "Deep read of one or more spawned pawns: identity, faction, ideoligion, " +
                "xenotype, age, backstories, traits, every skill, appearance, worn apparel, " +
                "equipment, hediffs and needs. " +
                "⭐ Skills report BOTH `levelRaw` (GetLevel(false), what was actually " +
                "written) and `levelEffective` (the getter, which ADDS APTITUDES). Validate " +
                "against levelRaw - the two differ and the difference has fooled people.",
            ResultDescription = "success, count, pawns[] with the full snapshot.")]
        public static async Task<object> PawnGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name. Empty lists all spawned pawns briefly.")] string pawn = null,
            [ToolParameter(Description = "Max pawns in a list. Default 20.")] int limit = 20)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.Maps == null || Find.Maps.Count == 0) return Fail("No map loaded.");

                if (string.IsNullOrEmpty(pawn))
                {
                    var rows = new List<object>();
                    foreach (var m in Find.Maps)
                        foreach (var p in m.mapPawns.AllPawnsSpawned)
                        {
                            if (rows.Count >= Math.Max(1, limit)) break;
                            rows.Add(new
                            {
                                thingId = p.ThingID, thingIdNumber = p.thingIDNumber,
                                name = p.LabelShort, kindDef = p.kindDef != null ? p.kindDef.defName : null,
                                faction = p.Faction != null ? p.Faction.def.defName : null,
                                x = p.Position.x, z = p.Position.z,
                            });
                        }
                    return (object)new { success = true, listing = true, count = rows.Count, pawns = rows, ticksGame = TicksGameSafe() };
                }

                string err; var pw = FindPawn(pawn, out err);
                if (pw == null) return Fail(err);
                return (object)new { success = true, count = 1, pawns = new List<object> { PawnSnapshot(pw) }, ticksGame = TicksGameSafe() };
            });
        }

        [Tool(
            "jawa/set_pawn_identity",
            Description =
                "Set a pawn's NAME and TITLE. Name parts are get-only properties, so a whole " +
                "new NameTriple is built - give first/nick/last, or `single` for a " +
                "single-name pawn. " +
                "⚠️ `title` is the ONLY free-text field a pawn has. There are no notes in " +
                "RimWorld 1.6 - no note field on Pawn or any tracker - so this is where a " +
                "one-line annotation must go if you want one to persist.",
            ResultDescription = "success, before/after name and title.")]
        public static async Task<object> SetPawnIdentity(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "First name.")] string first = null,
            [ToolParameter(Description = "Nickname.")] string nick = null,
            [ToolParameter(Description = "Last name.")] string last = null,
            [ToolParameter(Description = "Single name instead of a triple.")] string single = null,
            [ToolParameter(Description = "Custom title - the pawn's only free text.")] string title = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);

                var beforeName = p.Name != null ? p.Name.ToStringFull : null;
                var beforeTitle = p.story != null ? p.story.Title : null;
                var changed = new List<string>();

                if (!string.IsNullOrEmpty(single))
                {
                    p.Name = new NameSingle(single.Trim());
                    changed.Add("name(single)");
                }
                else if (first != null || nick != null || last != null)
                {
                    var cur = p.Name as NameTriple;
                    var f = first ?? (cur != null ? cur.First : "");
                    var n = nick ?? (cur != null ? cur.Nick : "");
                    var l = last ?? (cur != null ? cur.Last : "");
                    var nt = new NameTriple(f, string.IsNullOrEmpty(n) ? f : n, l);
                    if (!nt.IsValid)
                        return Fail("Resulting NameTriple is not valid (needs First and Last): '" + f + "' / '" + n + "' / '" + l + "'.");
                    p.Name = nt;
                    changed.Add("name");
                }

                if (title != null)
                {
                    if (p.story == null) return Fail("Pawn has no story tracker; cannot set a title.");
                    p.story.Title = title;
                    changed.Add("title");
                }

                if (changed.Count == 0) return Fail("Nothing to change - give first/nick/last, single, or title.");

                return (object)new
                {
                    success = true, changed,
                    before = new { name = beforeName, title = beforeTitle },
                    after = new { name = p.Name != null ? p.Name.ToStringFull : null, title = p.story != null ? p.story.Title : null },
                    note = "`title` is the only free text a pawn has - there are no notes in 1.6.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_pawn_backstory",
            Description =
                "Set a pawn's childhood and/or adulthood BackstoryDef. " +
                "🔴 The setters refresh NOTHING on their own - they only null a cache - so " +
                "this tool also runs Notify_DisabledWorkTypesChanged, " +
                "skills.Notify_SkillDisablesChanged, skills.DirtyAptitudes and " +
                "MeditationFocusTypeAvailabilityCache.ClearFor. The game's OWN debug tool " +
                "does only the last of those, which is why a hand-edited backstory leaves a " +
                "pawn with stale disabled work types.",
            ResultDescription = "success, before/after, refreshed[], and the resulting disabled work types.")]
        public static async Task<object> SetPawnBackstory(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "Childhood BackstoryDef.")] string childhood = null,
            [ToolParameter(Description = "Adulthood BackstoryDef. 'none' clears it.")] string adulthood = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.story == null) return Fail("Pawn has no story tracker.");

                var before = new
                {
                    childhood = p.story.Childhood != null ? p.story.Childhood.defName : null,
                    adulthood = p.story.Adulthood != null ? p.story.Adulthood.defName : null,
                };

                if (!string.IsNullOrEmpty(childhood))
                {
                    var bd = DefDatabase<BackstoryDef>.GetNamedSilentFail(childhood.Trim());
                    if (bd == null) return Fail("No BackstoryDef '" + childhood + "'.", DefSuggestions<BackstoryDef>(childhood));
                    p.story.Childhood = bd;
                }
                if (!string.IsNullOrEmpty(adulthood))
                {
                    if (adulthood.Trim().Equals("none", StringComparison.OrdinalIgnoreCase)) p.story.Adulthood = null;
                    else
                    {
                        var bd = DefDatabase<BackstoryDef>.GetNamedSilentFail(adulthood.Trim());
                        if (bd == null) return Fail("No BackstoryDef '" + adulthood + "'.", DefSuggestions<BackstoryDef>(adulthood));
                        p.story.Adulthood = bd;
                    }
                }

                // The four refreshes vanilla does NOT do for you.
                var refreshed = new List<string>();
                try { p.Notify_DisabledWorkTypesChanged(); refreshed.Add("Notify_DisabledWorkTypesChanged"); } catch (Exception e) { refreshed.Add("Notify_DisabledWorkTypesChanged FAILED: " + e.Message); }
                if (p.skills != null)
                {
                    try { p.skills.Notify_SkillDisablesChanged(); refreshed.Add("skills.Notify_SkillDisablesChanged"); } catch (Exception e) { refreshed.Add("Notify_SkillDisablesChanged FAILED: " + e.Message); }
                    try { p.skills.DirtyAptitudes(); refreshed.Add("skills.DirtyAptitudes"); } catch (Exception e) { refreshed.Add("DirtyAptitudes FAILED: " + e.Message); }
                }
                try { MeditationFocusTypeAvailabilityCache.ClearFor(p); refreshed.Add("MeditationFocusTypeAvailabilityCache.ClearFor"); } catch (Exception e) { refreshed.Add("MeditationCache FAILED: " + e.Message); }

                var disabled = new List<string>();
                try { foreach (var w in p.GetDisabledWorkTypes(true)) disabled.Add(w.defName); } catch { }

                return (object)new
                {
                    success = true,
                    before,
                    after = new
                    {
                        childhood = p.story.Childhood != null ? p.story.Childhood.defName : null,
                        adulthood = p.story.Adulthood != null ? p.story.Adulthood.defName : null,
                    },
                    refreshed,
                    disabledWorkTypes = disabled,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_traits",
            Description =
                "Add, remove or list a pawn's traits. " +
                "🔴 RimWorld's GainTrait does NOT check conflicts and TraitSet has NO trait " +
                "cap, so this tool checks TraitDef.ConflictsWith and " +
                "BackstoryDef.DisallowsTrait itself and REFUSES by default. Pass force=true " +
                "to stack a conflicting trait deliberately. " +
                "✅ Gain/RemoveTrait are self-refreshing - work types, skill disables, " +
                "aptitudes, situational thoughts, granted abilities and graphics all update.",
            ResultDescription = "success, added, removed, refused[], traits[] after.")]
        public static async Task<object> PawnTraits(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'add' | 'remove' | 'list'.")] string action = "list",
            [ToolParameter(Description = "TraitDef name.")] string trait = null,
            [ToolParameter(Description = "Trait degree. Default 0.")] int degree = 0,
            [ToolParameter(Description = "Add even if it conflicts.")] bool force = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.story == null || p.story.traits == null) return Fail("Pawn has no trait set.");
                var ts = p.story.traits;
                string A = (action ?? "list").Trim().ToLowerInvariant();
                var refused = new List<object>();
                int added = 0, removed = 0;

                if (A != "list")
                {
                    if (string.IsNullOrEmpty(trait)) return Fail("Give a TraitDef.");
                    var td = DefDatabase<TraitDef>.GetNamedSilentFail(trait.Trim());
                    if (td == null) return Fail("No TraitDef '" + trait + "'.", DefSuggestions<TraitDef>(trait));

                    if (A == "add")
                    {
                        if (td.degreeDatas != null && td.degreeDatas.Count > 0 && !td.degreeDatas.Any(d => d.degree == degree))
                            return Fail("Degree " + degree + " is not defined for '" + td.defName + "'. Valid: " +
                                        string.Join(", ", td.degreeDatas.Select(d => d.degree.ToString()).ToArray()));

                        if (ts.HasTrait(td)) refused.Add(new { trait = td.defName, why = "pawn already has this trait" });
                        else
                        {
                            var conflicts = ts.allTraits.Where(t => t.def.ConflictsWith(td)).Select(t => t.def.defName).ToList();
                            bool bsDisallows = false;
                            try
                            {
                                bsDisallows = (p.story.Childhood != null && p.story.Childhood.DisallowsTrait(td, degree))
                                           || (p.story.Adulthood != null && p.story.Adulthood.DisallowsTrait(td, degree));
                            }
                            catch { }

                            if ((conflicts.Count > 0 || bsDisallows) && !force)
                                refused.Add(new { trait = td.defName, why = "conflicts", conflictsWith = conflicts, backstoryDisallows = bsDisallows, hint = "pass force=true to add anyway" });
                            else
                            {
                                ts.GainTrait(new Trait(td, degree, false));
                                added++;
                            }
                        }
                    }
                    else if (A == "remove")
                    {
                        var have = ts.allTraits.FirstOrDefault(t => t.def == td);
                        if (have == null) refused.Add(new { trait = td.defName, why = "pawn does not have it" });
                        else { ts.RemoveTrait(have); removed++; }
                    }
                    else return Fail("action must be add|remove|list.");
                }

                var now = ts.allTraits.Select(t => new { def = t.def.defName, degree = t.Degree, label = t.LabelCap }).ToList();
                return (object)new
                {
                    success = true, action = A, added, removed, refused,
                    traitCount = now.Count,
                    note = "There is no trait cap in TraitSet and GainTrait checks nothing - the refusal above is ours.",
                    traits = now, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_pawn_skill",
            Description =
                "Set a pawn's skill level, passion and xp. " +
                "🔴 READ-BACK WARNING: SkillRecord.Level's GETTER adds aptitudes, so it can " +
                "differ from what you wrote. This tool reports BOTH `levelRaw` " +
                "(GetLevel(false), the written value) and `levelEffective`. Validate against " +
                "levelRaw. " +
                "⚠️ Setting Level does not reset xpSinceLastLevel, so a pawn can insta-level " +
                "afterwards - pass resetXp=true (the default) to zero it.",
            ResultDescription = "success, before/after per skill with levelRaw and levelEffective.")]
        public static async Task<object> SetPawnSkill(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "SkillDef name, e.g. Shooting, Melee, Construction.")] string skill = null,
            [ToolParameter(Description = "Level 0-20. -1 leaves it.")] int level = -1,
            [ToolParameter(Description = "None|Minor|Major. Empty leaves it.")] string passion = null,
            [ToolParameter(Description = "Zero xpSinceLastLevel after setting. Default true.")] bool resetXp = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.skills == null) return Fail("Pawn has no skill tracker (animals and mechs do not).");
                if (string.IsNullOrEmpty(skill)) return Fail("Give a SkillDef.");
                var sd = DefDatabase<SkillDef>.GetNamedSilentFail(skill.Trim());
                if (sd == null) return Fail("No SkillDef '" + skill + "'.", DefSuggestions<SkillDef>(skill));
                var sr = p.skills.GetSkill(sd);
                if (sr == null) return Fail("Pawn has no record for skill '" + sd.defName + "'.");

                var before = new { levelRaw = sr.GetLevel(false), levelEffective = sr.Level, passion = sr.passion.ToString(), xp = sr.xpSinceLastLevel, disabled = sr.TotallyDisabled };

                if (sr.TotallyDisabled)
                    return Fail("Skill '" + sd.defName + "' is TOTALLY DISABLED on this pawn by backstory, trait or gene. Writing a level would be silently meaningless. Change the backstory first.");

                if (level >= 0) sr.Level = Mathf.Clamp(level, 0, 20);
                if (!string.IsNullOrEmpty(passion))
                {
                    try { sr.passion = (Passion)Enum.Parse(typeof(Passion), passion.Trim(), true); }
                    catch { return Fail("Bad passion '" + passion + "'. None|Minor|Major."); }
                }
                if (resetXp) sr.xpSinceLastLevel = 0f;

                var after = new { levelRaw = sr.GetLevel(false), levelEffective = sr.Level, passion = sr.passion.ToString(), xp = sr.xpSinceLastLevel };
                return (object)new
                {
                    success = true, skill = sd.defName, before, after,
                    wroteLevel = level >= 0 ? (object)level : null,
                    readBackMatches = level < 0 || after.levelRaw == Mathf.Clamp(level, 0, 20),
                    note = "levelEffective includes aptitudes; levelRaw is what was written. Compare against levelRaw.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_pawn_appearance",
            Description =
                "Set head type, body type, hair, beard, hair colour and skin colour. " +
                "🔴 None of these dirty the renderer on their own, so this tool calls " +
                "Drawer.renderer.SetAllGraphicsDirty() afterwards - without it the pawn keeps " +
                "drawing its old face for the rest of the session. " +
                "⚠️ Nothing in RimWorld guards these: an off-gender head type, a " +
                "gene-requiring head, or an adult body on a child all 'work'. Child body is " +
                "forced only at load. skinColor uses skinColorOverride, which is SAVED - " +
                "SkinColorBase is [Unsaved] and would be lost.",
            ResultDescription = "success, before/after, and whether the renderer was dirtied.")]
        public static async Task<object> SetPawnAppearance(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "HeadTypeDef name.")] string headType = null,
            [ToolParameter(Description = "BodyTypeDef name.")] string bodyType = null,
            [ToolParameter(Description = "HairDef name.")] string hair = null,
            [ToolParameter(Description = "BeardDef name.")] string beard = null,
            [ToolParameter(Description = "Hair colour 'r,g,b' 0-1.")] string hairColor = null,
            [ToolParameter(Description = "Skin colour 'r,g,b' 0-1 (uses the SAVED override).")] string skinColor = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.story == null) return Fail("Pawn has no story tracker.");

                var before = new
                {
                    headType = p.story.headType != null ? p.story.headType.defName : null,
                    bodyType = p.story.bodyType != null ? p.story.bodyType.defName : null,
                    hair = p.story.hairDef != null ? p.story.hairDef.defName : null,
                    beard = p.style != null && p.style.beardDef != null ? p.style.beardDef.defName : null,
                };
                var changed = new List<string>();

                Func<string, Color?> parseCol = str =>
                {
                    var b = (str ?? "").Split(',');
                    float r0, g0, b0;
                    if (b.Length == 3 && float.TryParse(b[0], out r0) && float.TryParse(b[1], out g0) && float.TryParse(b[2], out b0))
                        return new Color(r0, g0, b0);
                    return null;
                };

                if (!string.IsNullOrEmpty(headType))
                {
                    var hd = DefDatabase<HeadTypeDef>.GetNamedSilentFail(headType.Trim());
                    if (hd == null) return Fail("No HeadTypeDef '" + headType + "'.", DefSuggestions<HeadTypeDef>(headType));
                    p.story.headType = hd; changed.Add("headType");
                }
                if (!string.IsNullOrEmpty(bodyType))
                {
                    var bd = DefDatabase<BodyTypeDef>.GetNamedSilentFail(bodyType.Trim());
                    if (bd == null) return Fail("No BodyTypeDef '" + bodyType + "'.", DefSuggestions<BodyTypeDef>(bodyType));
                    p.story.bodyType = bd; changed.Add("bodyType");
                }
                if (!string.IsNullOrEmpty(hair))
                {
                    var hd = DefDatabase<HairDef>.GetNamedSilentFail(hair.Trim());
                    if (hd == null) return Fail("No HairDef '" + hair + "'.", DefSuggestions<HairDef>(hair));
                    p.story.hairDef = hd; changed.Add("hair");
                }
                if (!string.IsNullOrEmpty(beard))
                {
                    if (p.style == null) return Fail("Pawn has no style tracker.");
                    var bd = DefDatabase<BeardDef>.GetNamedSilentFail(beard.Trim());
                    if (bd == null) return Fail("No BeardDef '" + beard + "'.", DefSuggestions<BeardDef>(beard));
                    p.style.beardDef = bd; changed.Add("beard");
                }
                if (!string.IsNullOrEmpty(hairColor))
                {
                    var c = parseCol(hairColor);
                    if (c == null) return Fail("hairColor must be 'r,g,b' with 0-1 floats.");
                    p.story.HairColor = c.Value; changed.Add("hairColor");
                }
                if (!string.IsNullOrEmpty(skinColor))
                {
                    var c = parseCol(skinColor);
                    if (c == null) return Fail("skinColor must be 'r,g,b' with 0-1 floats.");
                    p.story.skinColorOverride = c.Value; changed.Add("skinColorOverride");
                }

                if (changed.Count == 0) return Fail("Nothing to change.");

                bool dirtied = false;
                try { p.Drawer.renderer.SetAllGraphicsDirty(); dirtied = true; } catch (Exception e) { Log.Warning("[JawaBench] SetAllGraphicsDirty failed: " + e.Message); }

                return (object)new
                {
                    success = true, changed, rendererDirtied = dirtied,
                    before,
                    after = new
                    {
                        headType = p.story.headType != null ? p.story.headType.defName : null,
                        bodyType = p.story.bodyType != null ? p.story.bodyType.defName : null,
                        hair = p.story.hairDef != null ? p.story.hairDef.defName : null,
                        beard = p.style != null && p.style.beardDef != null ? p.style.beardDef.defName : null,
                    },
                    note = "Nothing here validates gender or life stage - an off-gender head works.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  P2 - LOADOUT AND BODY
        //  🔴 equipment.AddEquipment Log.Errors and does NOTHING if a Primary
        //     already exists. MakeRoomFor first, or the tool reports success
        //     having changed nothing.
        //  ✅ apparel.Wear DOES enforce CanWearTogether, drops conflicts and
        //     refreshes graphics itself.
        //  🔴 health.RestorePart is RECURSIVE into child parts, wipes their
        //     hediffs and does not drop what it removed.
        // ================================================================

        private static BodyPartRecord FindBodyPart(Pawn p, string partDefName, out string err)
        {
            err = null;
            if (string.IsNullOrEmpty(partDefName)) return null;
            var name = partDefName.Trim();
            var all = p.RaceProps != null && p.RaceProps.body != null ? p.RaceProps.body.AllParts : null;
            if (all == null) { err = "Pawn has no body definition."; return null; }
            var hit = all.FirstOrDefault(bp => bp.def != null && bp.def.defName.Equals(name, StringComparison.OrdinalIgnoreCase));
            if (hit == null)
            {
                var near = all.Where(bp => bp.def != null && bp.def.defName.IndexOf(name, StringComparison.OrdinalIgnoreCase) >= 0)
                              .Select(bp => bp.def.defName).Distinct().Take(8).ToList();
                err = "No body part '" + name + "' on this pawn. Nearby: " + (near.Count == 0 ? "(none)" : string.Join(", ", near.ToArray()));
            }
            return hit;
        }

        [Tool(
            "jawa/pawn_gear",
            Description =
                "🔴 THIS IS A WRITE TOOL. The READ is jawa/pawn_get, and jawa/thing_stats "
                + "for what a held item actually does. Reading `.equipment` off THIS tool's "
                + "refusal returns an empty list for every pawn, which reads exactly like "
                + "'they are all bare-handed' - that is how the opposite of the truth was "
                + "once written up (BRIDGE_ARG_SHAPES_INCONSISTENT_1 row 2). "
                + "Give, wear or clear a pawn's EQUIPMENT, APPAREL and INVENTORY. " +
                "action='equip' puts a weapon in the primary slot, 'wear' puts on apparel, " +
                "'inventory' stuffs an item into the pack, 'clear' empties one or all three. " +
                "🔴 EQUIP HANDLES THE PRIMARY-SLOT TRAP: RimWorld's AddEquipment logs an " +
                "error and silently does nothing when a primary already exists, so this " +
                "calls MakeRoomFor first and reports what it displaced. " +
                "✅ WEAR uses PawnApparelGenerator.GenerateApparelOfDefFor so the garment " +
                "arrives stuffed, coloured and quality-rolled, and apparel.Wear itself " +
                "enforces CanWearTogether and drops real conflicts.",
            ResultDescription = "success, action, displaced[], and the pawn's gear after.")]
        public static async Task<object> PawnGear(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'equip' | 'wear' | 'inventory' | 'clear'.")] string action = "equip",
            [ToolParameter(Description = "ThingDef of the weapon/apparel/item.")] string def = null,
            [ToolParameter(Description = "Stuff ThingDef.")] string stuff = null,
            [ToolParameter(Description = "Quality for the item.")] string quality = null,
            [ToolParameter(Description = "Stack count for inventory. Default 1.")] int count = 1,
            [ToolParameter(Description = "For clear: 'equipment' | 'apparel' | 'inventory' | 'all'.")] string clearWhat = "all")
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                string A = (action ?? "").Trim().ToLowerInvariant();
                var displaced = new List<object>();
                var notes = new List<string>();

                if (A == "clear")
                {
                    string W = (clearWhat ?? "all").Trim().ToLowerInvariant();
                    if (W == "all" || W == "equipment") { if (p.equipment != null) { p.equipment.DestroyAllEquipment(); notes.Add("equipment destroyed"); } }
                    if (W == "all" || W == "apparel") { if (p.apparel != null) { p.apparel.DestroyAll(); notes.Add("apparel destroyed"); } }
                    if (W == "all" || W == "inventory") { if (p.inventory != null) { p.inventory.DestroyAll(); notes.Add("inventory destroyed"); } }
                    if (notes.Count == 0) return Fail("clearWhat must be equipment|apparel|inventory|all.");
                }
                else
                {
                    if (string.IsNullOrEmpty(def))
                        return Fail("Give a ThingDef in 'def' - this is a WRITE tool and there "
                                    + "is nothing to " + A + ". If you wanted to READ this pawn's "
                                    + "gear, call jawa/pawn_get (identity, apparel, equipment, "
                                    + "hediffs, needs, skills, traits, xenotype) or jawa/thing_stats "
                                    + "for what the held item does. ⛔ Do not read a list off this "
                                    + "refusal: it has none, and an empty gear list reads exactly "
                                    + "like a bare-handed pawn.");
                    var td = DefDatabase<ThingDef>.GetNamedSilentFail(def.Trim());
                    if (td == null) return Fail("No ThingDef '" + def + "'.", DefSuggestions<ThingDef>(def));

                    ThingDef sd = null;
                    if (!string.IsNullOrEmpty(stuff)) sd = DefDatabase<ThingDef>.GetNamedSilentFail(stuff.Trim());
                    if (td.MadeFromStuff && sd == null) sd = GenStuff.DefaultStuffFor(td);
                    if (!td.MadeFromStuff) sd = null;

                    QualityCategory q = QualityCategory.Normal; bool setQ = false;
                    if (!string.IsNullOrEmpty(quality))
                    {
                        try { q = (QualityCategory)Enum.Parse(typeof(QualityCategory), quality.Trim(), true); setQ = true; }
                        catch { return Fail("Bad quality '" + quality + "'."); }
                    }

                    // equip/wear can drop a conflicting item via MakeRoomFor/Wear, and
                    // that drop targets pawn.Position on pawn.MapHeld - null for any
                    // off-map pawn (a caravan member, a world pawn). Both then fail
                    // silently (Log.Error, no exception) and leave the pawn unchanged
                    // while this tool still reported success. Refuse up front instead.
                    if ((A == "equip" || A == "wear" || A == "inventory") && p.MapHeld == null)
                        return Fail(p.LabelShortCap + " is off-map (no MapHeld) - equip/wear/inventory would silently no-op (MakeRoomFor/Wear/TryAdd all drop through a null map). Not supported for caravan/world pawns.");

                    if (A == "equip")
                    {
                        if (p.equipment == null) return Fail("Pawn has no equipment tracker.");
                        if (!td.IsWeapon) notes.Add("WARNING: '" + td.defName + "' is not flagged IsWeapon.");
                        var t = ThingMaker.MakeThing(td, sd) as ThingWithComps;
                        if (t == null) return Fail("'" + td.defName + "' did not make a ThingWithComps, so it cannot be equipment.");
                        if (setQ) { var cq = t.TryGetComp<CompQuality>(); if (cq != null) cq.SetQuality(q, ArtGenerationContext.Outsider); }

                        // 🔴 THE TRAP: AddEquipment Log.Errors and does nothing when a
                        // primary exists. MakeRoomFor first and say what was displaced -
                        // and verify it actually left, since MakeRoomFor(t) (no out param)
                        // itself fails silently (Log.Error only) if the drop cell/map is bad.
                        var prior = p.equipment.Primary;
                        if (prior != null)
                        {
                            p.equipment.MakeRoomFor(t);
                            if (p.equipment.Primary == prior)
                                return Fail("MakeRoomFor could not displace " + prior.def.defName + " (drop failed - see the game log) - " + td.defName + " was not equipped.");
                            displaced.Add(new { def = prior.def.defName, stuff = prior.Stuff != null ? prior.Stuff.defName : null });
                            notes.Add("displaced the existing primary via MakeRoomFor - without this AddEquipment would have silently no-opped");
                        }
                        p.equipment.AddEquipment(t);
                        if (p.equipment.Primary != t)
                            return Fail("AddEquipment did not make '" + td.defName + "' the pawn's primary (see the game log) - equip failed.");
                    }
                    else if (A == "wear")
                    {
                        if (p.apparel == null) return Fail("Pawn has no apparel tracker.");
                        if (!td.IsApparel) return Fail("'" + td.defName + "' is not apparel.");
                        Apparel ap = null;
                        try { ap = PawnApparelGenerator.GenerateApparelOfDefFor(p, td); } catch { }
                        if (ap == null) ap = (Apparel)ThingMaker.MakeThing(td, sd);
                        if (setQ) { var cq = ap.TryGetComp<CompQuality>(); if (cq != null) cq.SetQuality(q, ArtGenerationContext.Outsider); }
                        p.apparel.Wear(ap, true, false);
                        if (!p.apparel.WornApparel.Contains(ap))
                            return Fail("'" + td.defName + "' is not in the pawn's WornApparel after Wear() (see the game log for a dropped-conflict or drop failure) - wear failed.");
                    }
                    else if (A == "inventory")
                    {
                        if (p.inventory == null) return Fail("Pawn has no inventory tracker.");
                        var t = ThingMaker.MakeThing(td, sd);
                        t.stackCount = Math.Max(1, count);
                        if (setQ) { var cq = t.TryGetComp<CompQuality>(); if (cq != null) cq.SetQuality(q, ArtGenerationContext.Outsider); }
                        // TryAddOrTransfer returns the COUNT transferred, not a bool.
                        int moved = p.inventory.innerContainer.TryAddOrTransfer(t, Math.Max(1, count));
                        if (moved <= 0)
                            return Fail("inventory transferred 0 of " + Math.Max(1, count) + " - container refused it (full, or '" + td.defName + "' is unstorable).");
                        notes.Add("inventory transferred " + moved + " of " + Math.Max(1, count));
                    }
                    else return Fail("action must be equip|wear|inventory|clear.");
                }

                var snap = PawnSnapshot(p);
                return (object)new
                {
                    success = true, action = A, displaced, notes,
                    pawn = snap, ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_health",
            Description =
                "Add or remove a hediff, install a bionic, or restore a body part. " +
                "action='add' | 'remove' | 'bionic' | 'restore'. " +
                "⭐ 'bionic' needs NO RecipeDef and no surgeon: it does RestorePart(part) " +
                "then AddHediff(def, part), which is exactly what " +
                "Recipe_InstallArtificialBodyPart does with a null billDoer. " +
                "🔴 'restore' is DESTRUCTIVE AND RECURSIVE - RestorePart walks into child " +
                "parts, wipes their hediffs, and does not drop whatever it removed. It is " +
                "gated behind confirmDestructive=true.",
            ResultDescription = "success, action, hediffs after, and the affected part.")]
        public static async Task<object> PawnHealth(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'add' | 'remove' | 'bionic' | 'restore'.")] string action = "add",
            [ToolParameter(Description = "HediffDef (add/remove) or the bionic's HediffDef.")] string hediff = null,
            [ToolParameter(Description = "BodyPartDef name, e.g. Leg, Eye, Hand. Empty = whole body.")] string bodyPart = null,
            [ToolParameter(Description = "Severity for 'add'. -1 uses the def default.")] float severity = -1f,
            [ToolParameter(Description = "Required for 'restore' - it is recursive and destructive.")] bool confirmDestructive = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.health == null) return Fail("Pawn has no health tracker.");
                string A = (action ?? "").Trim().ToLowerInvariant();

                BodyPartRecord part = null;
                if (!string.IsNullOrEmpty(bodyPart))
                {
                    string perr;
                    part = FindBodyPart(p, bodyPart, out perr);
                    if (part == null) return Fail(perr);
                }

                string didWhat;
                if (A == "restore")
                {
                    if (!confirmDestructive)
                        return Fail("RestorePart is RECURSIVE into child parts, wipes their hediffs and does not drop what it removes. Pass confirmDestructive=true if that is what you want.");
                    if (part == null) return Fail("Give a bodyPart to restore.");
                    p.health.RestorePart(part);
                    didWhat = "restored " + part.def.defName + " (and its children)";
                }
                else
                {
                    if (string.IsNullOrEmpty(hediff)) return Fail("Give a HediffDef.");
                    var hd = DefDatabase<HediffDef>.GetNamedSilentFail(hediff.Trim());
                    if (hd == null) return Fail("No HediffDef '" + hediff + "'.", DefSuggestions<HediffDef>(hediff));

                    if (A == "add")
                    {
                        var h = p.health.AddHediff(hd, part);
                        if (h != null && severity >= 0f) h.Severity = severity;
                        didWhat = "added " + hd.defName + (part != null ? " to " + part.def.defName : " (whole body)");
                    }
                    else if (A == "remove")
                    {
                        var h = p.health.hediffSet.hediffs.FirstOrDefault(x => x.def == hd && (part == null || x.Part == part));
                        if (h == null) return Fail("Pawn has no hediff '" + hd.defName + "'" + (part != null ? " on " + part.def.defName : "") + ".");
                        p.health.RemoveHediff(h);
                        didWhat = "removed " + hd.defName;
                    }
                    else if (A == "bionic")
                    {
                        if (part == null) return Fail("Give a bodyPart for a bionic.");
                        p.health.RestorePart(part);
                        p.health.AddHediff(hd, part);
                        didWhat = "installed " + hd.defName + " on " + part.def.defName + " (RestorePart then AddHediff - no RecipeDef needed)";
                    }
                    else return Fail("action must be add|remove|bionic|restore.");
                }

                var hediffs = p.health.hediffSet.hediffs
                    .Select(h => new { def = h.def.defName, part = h.Part != null ? h.Part.def.defName : null, severity = h.Severity })
                    .Take(40).ToList();

                return (object)new
                {
                    success = true, action = A, didWhat,
                    partsAvailable = part == null && A != "restore"
                        ? p.RaceProps.body.AllParts.Select(bp => bp.def.defName).Distinct().Take(20).ToList()
                        : null,
                    hediffCount = p.health.hediffSet.hediffs.Count,
                    hediffs,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_need",
            Description =
                "Set a pawn's need level (food, rest, joy, comfort, beauty, outdoors...) or " +
                "give it a memory thought. action='need' writes CurLevel 0-1; " +
                "action='thought' calls TryGainMemory. " +
                "⚠️ Social thoughts REQUIRE an otherPawn - without one they are dropped " +
                "silently, so this refuses instead.",
            ResultDescription = "success, needs after, and the thought list.")]
        public static async Task<object> PawnNeed(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'need' | 'thought' | 'list'.")] string action = "list",
            [ToolParameter(Description = "NeedDef name for 'need'.")] string need = null,
            [ToolParameter(Description = "Level 0-1 for 'need'.")] float level = 0.5f,
            [ToolParameter(Description = "ThoughtDef name for 'thought'.")] string thought = null,
            [ToolParameter(Description = "Other pawn id for a social thought.")] string otherPawn = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.needs == null) return Fail("Pawn has no needs tracker.");
                string A = (action ?? "list").Trim().ToLowerInvariant();
                var notes = new List<string>();

                if (A == "need")
                {
                    if (string.IsNullOrEmpty(need)) return Fail("Give a NeedDef.");
                    var nd = DefDatabase<NeedDef>.GetNamedSilentFail(need.Trim());
                    if (nd == null) return Fail("No NeedDef '" + need + "'.", DefSuggestions<NeedDef>(need));
                    var n = p.needs.TryGetNeed(nd);
                    if (n == null) return Fail("This pawn has no '" + nd.defName + "' need. It has: " +
                        string.Join(", ", p.needs.AllNeeds.Select(z => z.def.defName).ToArray()));
                    n.CurLevelPercentage = Mathf.Clamp01(level);
                    notes.Add("set " + nd.defName + " to " + n.CurLevelPercentage);
                }
                else if (A == "thought")
                {
                    if (string.IsNullOrEmpty(thought)) return Fail("Give a ThoughtDef.");
                    var td = DefDatabase<ThoughtDef>.GetNamedSilentFail(thought.Trim());
                    if (td == null) return Fail("No ThoughtDef '" + thought + "'.", DefSuggestions<ThoughtDef>(thought));
                    if (p.needs.mood == null) return Fail("Pawn has no mood need, so it cannot hold thoughts.");
                    Pawn other = null;
                    if (!string.IsNullOrEmpty(otherPawn)) { string e2; other = FindPawn(otherPawn, out e2); }
                    if (td.IsSocial && other == null)
                        return Fail("'" + td.defName + "' is a SOCIAL thought and needs an otherPawn. Without one RimWorld drops it silently.");
                    p.needs.mood.thoughts.memories.TryGainMemory(td, other);
                    notes.Add("gained memory " + td.defName);
                }
                else if (A != "list") return Fail("action must be need|thought|list.");

                var needs = p.needs.AllNeeds.Select(n => new { need = n.def.defName, level = n.CurLevel, pct = n.CurLevelPercentage }).ToList();
                var memories = p.needs.mood != null
                    ? p.needs.mood.thoughts.memories.Memories.Select(m => new { def = m.def.defName, age = m.age }).Take(20).ToList()
                    : null;

                return (object)new { success = true, action = A, notes, needs, memories, ticksGame = TicksGameSafe() };
            });
        }


        // ================================================================
        //  P3 - ALLEGIANCE AND BODY PLAN
        // ================================================================
        [Tool(
            "jawa/set_pawn_faction",
            Description =
                "Change a pawn's faction, or recruit a prisoner/guest into the colony. " +
                "✅ Pawn.SetFaction is SELF-REFRESHING and does a great deal for you: lord " +
                "Notify_PawnLost, jobs.StopAll, drafter, guest status, mapPawns " +
                "re/de-registration, needs, relations, the colonist bar, surgery bills and " +
                "ChangeKind. " +
                "⭐ Use recruit=true for prisoner/guest -> player: RecruitUtility.Recruit " +
                "also unlocks apparel and replaces royal titles, which raw SetFaction does not. " +
                "⚠️ Changing faction on a pawn in an active raid removes it from its lord.",
            ResultDescription = "success, before/after faction, and the pawn snapshot.")]
        public static async Task<object> SetPawnFaction(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "FactionDef name. 'none' makes it factionless. 'player' is the colony.")] string faction = null,
            [ToolParameter(Description = "Use RecruitUtility.Recruit instead of raw SetFaction.")] bool recruit = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (string.IsNullOrEmpty(faction)) return Fail("Give a FactionDef, 'player' or 'none'.");

                var before = p.Faction != null ? p.Faction.def.defName : null;
                Faction target = null;
                var f = faction.Trim();

                if (f.Equals("none", StringComparison.OrdinalIgnoreCase)) target = null;
                else if (f.Equals("player", StringComparison.OrdinalIgnoreCase)) target = Faction.OfPlayer;
                else
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(f);
                    if (fd == null) return Fail("No FactionDef '" + f + "'.", DefSuggestions<FactionDef>(f));
                    target = Find.FactionManager.FirstFactionOfDef(fd);
                    if (target == null)
                        return Fail("FactionDef '" + f + "' exists but no such faction was GENERATED in this world. " +
                                    "Live factions: " + string.Join(", ", Find.FactionManager.AllFactionsVisible.Select(z => z.def.defName).Take(20).ToArray()));
                }

                if (p.Faction == target)
                    return Fail("Pawn is already in " + (target == null ? "no faction" : target.def.defName) + " - SetFaction warns and returns on a no-op.");

                var notes = new List<string>();
                try
                {
                    if (recruit && target != null) { RecruitUtility.Recruit(p, target); notes.Add("RecruitUtility.Recruit - apparel unlock + royal title replace"); }
                    else { p.SetFaction(target); notes.Add("Pawn.SetFaction - self-refreshing"); }
                }
                catch (Exception e) { return Fail("Faction change threw: " + e.GetType().Name + ": " + e.Message); }

                return (object)new
                {
                    success = true,
                    before, after = p.Faction != null ? p.Faction.def.defName : null,
                    isColonist = p.IsColonist, isPrisoner = p.IsPrisoner,
                    notes,
                    pawn = PawnSnapshot(p), ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_pawn_ideo",
            Description =
                "Set a pawn's ideoligion, adjust certainty, or assign an ideo role. " +
                "action='set' | 'certainty' | 'role' | 'list'. " +
                "⚠️ SetIdeo is NOT a quiet field write: it RANDOMISES certainty, unclaims " +
                "ideo-forbidden beds, may strip spouse and bond relations, and can send a " +
                "letter. It also no-ops on babies. " +
                "⚠️ Certainty's setter is PRIVATE - this uses OffsetCertainty.",
            ResultDescription = "success, before/after ideo and certainty, available ideos.")]
        public static async Task<object> SetPawnIdeo(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'set' | 'certainty' | 'role' | 'list'.")] string action = "list",
            [ToolParameter(Description = "Ideo NAME (they are runtime objects, not defs).")] string ideo = null,
            [ToolParameter(Description = "Certainty offset, e.g. 0.2 or -0.3.")] float certaintyOffset = 0f,
            [ToolParameter(Description = "Precept role label for action='role'. 'none' unassigns.")] string role = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.IdeologyActive)
                    return Fail("Ideology is not active. Ideoligions do not exist in this game - this is a loud failure, not a count of zero.");
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);

                var all = Find.IdeoManager != null ? Find.IdeoManager.IdeosListForReading : null;
                var available = all != null ? all.Select(i => new { name = i.name, memes = i.memes.Select(m => m.defName).Take(6).ToList(), believers = i.ColonistBelieverCountCached }).ToList() : null;
                string A = (action ?? "list").Trim().ToLowerInvariant();

                var beforeIdeo = p.Ideo != null ? p.Ideo.name : null;
                float beforeCert = p.ideo != null ? p.ideo.Certainty : -1f;
                var notes = new List<string>();

                if (A == "set")
                {
                    if (p.ideo == null) return Fail("Pawn has no ideo tracker.");
                    if (string.IsNullOrEmpty(ideo)) return Fail("Give an ideo NAME.");
                    var target = all != null ? all.FirstOrDefault(i => string.Equals(i.name, ideo.Trim(), StringComparison.OrdinalIgnoreCase)) : null;
                    if (target == null) return Fail("No ideoligion named '" + ideo + "'. Available: " +
                        (all == null ? "(none)" : string.Join(" | ", all.Select(i => i.name).ToArray())));
                    p.ideo.SetIdeo(target);
                    notes.Add("SetIdeo randomises certainty and may strip spouse/bond relations - that is vanilla, not us");
                }
                else if (A == "certainty")
                {
                    if (p.ideo == null) return Fail("Pawn has no ideo tracker.");
                    p.ideo.OffsetCertainty(certaintyOffset);
                    notes.Add("Certainty's setter is private; used OffsetCertainty");
                }
                else if (A == "role")
                {
                    if (p.Ideo == null) return Fail("Pawn has no ideoligion, so it cannot hold a role.");
                    if (string.IsNullOrEmpty(role)) return Fail("Give a role label or 'none'.");
                    var roles = p.Ideo.RolesListForReading;
                    if (role.Trim().Equals("none", StringComparison.OrdinalIgnoreCase))
                    {
                        var held = roles.FirstOrDefault(r => r.IsAssigned(p));
                        if (held == null) return Fail("Pawn holds no role to unassign.");
                        held.Unassign(p, false); notes.Add("unassigned " + held.LabelCap);
                    }
                    else
                    {
                        var r = roles.FirstOrDefault(z => string.Equals(z.LabelCap, role.Trim(), StringComparison.OrdinalIgnoreCase)
                                                       || string.Equals(z.def.defName, role.Trim(), StringComparison.OrdinalIgnoreCase));
                        if (r == null) return Fail("No role '" + role + "' in ideoligion '" + p.Ideo.name + "'. Roles: " +
                            string.Join(", ", roles.Select(z => (string)z.LabelCap).ToArray()));
                        r.Assign(p, true); notes.Add("assigned " + r.LabelCap + " (a single-occupant role replaces the previous holder and letters)");
                    }
                }
                else if (A != "list") return Fail("action must be set|certainty|role|list.");

                return (object)new
                {
                    success = true, action = A, notes,
                    before = new { ideo = beforeIdeo, certainty = beforeCert },
                    after = new { ideo = p.Ideo != null ? p.Ideo.name : null, certainty = p.ideo != null ? p.ideo.Certainty : -1f },
                    role = p.Ideo != null ? p.Ideo.RolesListForReading.Where(r => r.IsAssigned(p)).Select(r => (string)r.LabelCap).FirstOrDefault() : null,
                    availableIdeos = available,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_relations",
            Description =
                "Add, remove or list DIRECT relations between two pawns, and read opinion. " +
                "⚠️ RimWorld REFUSES `implied` relations - Kin, Cousin, Grand*, Great*, " +
                "Uncle/Nephew and friends are COMPUTED from the family graph, not stored - so " +
                "this reports that clearly instead of letting it look like a failed write. " +
                "✅ Reflexive relations auto-mirror onto the other pawn.",
            ResultDescription = "success, added/removed, opinion both ways, relations[].")]
        public static async Task<object> PawnRelations(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'add' | 'remove' | 'list'.")] string action = "list",
            [ToolParameter(Description = "PawnRelationDef, e.g. Spouse, Lover, Parent, Sibling.")] string relation = null,
            [ToolParameter(Description = "The other pawn's id or name.")] string otherPawn = null,
            [ToolParameter(Description = "Add a love relation even though the pawn already holds one. RimWorld does not enforce exclusivity; this tool does.")] bool force = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.relations == null) return Fail("Pawn has no relations tracker.");
                string A = (action ?? "list").Trim().ToLowerInvariant();
                var notes = new List<string>();
                int added = 0, removed = 0;
                Pawn other = null;

                if (A != "list")
                {
                    if (string.IsNullOrEmpty(relation)) return Fail("Give a PawnRelationDef.");
                    if (string.IsNullOrEmpty(otherPawn)) return Fail("Give otherPawn.");
                    string e2; other = FindPawn(otherPawn, out e2);
                    if (other == null) return Fail(e2);
                    if (other == p) return Fail("A pawn cannot hold a direct relation to itself.");
                    var rd = DefDatabase<PawnRelationDef>.GetNamedSilentFail(relation.Trim());
                    if (rd == null) return Fail("No PawnRelationDef '" + relation + "'.", DefSuggestions<PawnRelationDef>(relation));

                    if (rd.implied)
                        return Fail("'" + rd.defName + "' is an IMPLIED relation - RimWorld computes it from the family graph and refuses to store it directly. " +
                                    "Add the underlying blood relations instead (Parent, Sibling, Child) and this one will appear on its own.");

                    if (A == "add")
                    {
                        // 🔴 Measured 2026-08-19: nothing in RimWorld stops a pawn holding
                        // Fiance AND Spouse AND ExSpouse with the SAME person at once - the
                        // test produced exactly that. The love relations are meant to be
                        // mutually exclusive, so refuse by default the way pawn_traits does
                        // for conflicting traits.
                        var loveRels = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
                            { "Lover", "Fiance", "Spouse", "ExLover", "ExSpouse" };
                        if (loveRels.Contains(rd.defName) && !force)
                        {
                            var held = p.relations.DirectRelations
                                .Where(x => x.def != null && loveRels.Contains(x.def.defName))
                                .Select(x => x.def.defName + " (" + (x.otherPawn != null ? x.otherPawn.LabelShort : "?") + ")")
                                .ToList();
                            if (held.Count > 0)
                                return Fail("REFUSING: this pawn already holds a love relation - " + string.Join(", ", held.ToArray()) +
                                            ". Lover/Fiance/Spouse/ExLover/ExSpouse are meant to be mutually exclusive and RimWorld does NOT enforce it, " +
                                            "so adding '" + rd.defName + "' would leave the pawn holding several at once. " +
                                            "Remove the existing one first, or pass force=true if a deliberately incoherent state is what you want.",
                                            held);
                        }

                        if (p.relations.DirectRelationExists(rd, other)) notes.Add("relation already exists");
                        else { p.relations.AddDirectRelation(rd, other); added++; if (rd.reflexive) notes.Add("reflexive - mirrored onto the other pawn automatically"); }
                    }
                    else if (A == "remove")
                    {
                        if (!p.relations.DirectRelationExists(rd, other)) notes.Add("no such relation to remove");
                        else { p.relations.RemoveDirectRelation(rd, other); removed++; }
                    }
                    else return Fail("action must be add|remove|list.");
                }

                var rels = p.relations.DirectRelations.Select(r => new
                {
                    def = r.def.defName,
                    otherPawn = r.otherPawn != null ? r.otherPawn.LabelShort : null,
                    otherId = r.otherPawn != null ? r.otherPawn.thingIDNumber : -1,
                }).ToList();

                return (object)new
                {
                    success = true, action = A, added, removed, notes,
                    opinionOfOther = other != null ? (object)p.relations.OpinionOf(other) : null,
                    opinionOfMe = other != null ? (object)other.relations.OpinionOf(p) : null,
                    relationCount = rels.Count, relations = rels,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_genes",
            Description =
                "Add or remove genes, or set a whole xenotype. " +
                "🔴 THE ACTION VERBS ARE 'add' | 'remove' | 'xenotype' | 'list'. This text used " +
                "to say AddGene/RemoveGene, which are the ENGINE method names and are refused " +
                "by the binder (BRIDGE_ARG_SHAPES_INCONSISTENT_1 row 4). " +
                "✅ Adding or removing is FULLY SELF-REFRESHING via Notify_GenesChanged - " +
                "colours, body and head, needs, hediff cache, aptitudes, work types and " +
                "graphics all update. " +
                "🔴 ORDER MATTERS, AND IT IS GENE FIRST, APPEARANCE SECOND. That refresh " +
                "RE-ROLLS THE HEAD TYPE, so a head set before the gene is silently replaced " +
                "(row 5). This is Notify_GenesChanged doing its job, not a bug to suppress. " +
                "xenogene=true adds it as a xenogene rather than an " +
                "endogene, which is what determines inheritance.",
            ResultDescription = "success, xenotype, endogenes[], xenogenes[].")]
        public static async Task<object> PawnGenes(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'add' | 'remove' | 'xenotype' | 'list'.")] string action = "list",
            [ToolParameter(Description = "GeneDef name.")] string gene = null,
            [ToolParameter(Description = "XenotypeDef name for action='xenotype'.")] string xenotype = null,
            [ToolParameter(Description = "Add as a xenogene rather than an endogene. Default true.")] bool xenogene = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.BiotechActive)
                    return Fail("Biotech is not active. Genes and xenotypes do not exist in this game.");
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.genes == null) return Fail("Pawn has no gene tracker.");
                string A = (action ?? "list").Trim().ToLowerInvariant();
                var notes = new List<string>();

                if (A == "add" || A == "remove")
                {
                    if (string.IsNullOrEmpty(gene)) return Fail("Give a GeneDef.");
                    var gd = DefDatabase<GeneDef>.GetNamedSilentFail(gene.Trim());
                    if (gd == null) return Fail("No GeneDef '" + gene + "'.", DefSuggestions<GeneDef>(gene));
                    if (A == "add") { p.genes.AddGene(gd, xenogene); notes.Add("added as " + (xenogene ? "xenogene" : "endogene") + "; Notify_GenesChanged handles every refresh"); }
                    else
                    {
                        var g = p.genes.GenesListForReading.FirstOrDefault(z => z.def == gd);
                        if (g == null) return Fail("Pawn does not have gene '" + gd.defName + "'.");
                        p.genes.RemoveGene(g); notes.Add("removed");
                    }
                }
                else if (A == "xenotype")
                {
                    if (string.IsNullOrEmpty(xenotype)) return Fail("Give a XenotypeDef.");
                    var xd = DefDatabase<XenotypeDef>.GetNamedSilentFail(xenotype.Trim());
                    if (xd == null) return Fail("No XenotypeDef '" + xenotype + "'.", DefSuggestions<XenotypeDef>(xenotype));
                    p.genes.SetXenotype(xd);
                    notes.Add("SetXenotype clears existing xenogenes and re-adds the def's list");
                }
                else if (A != "list") return Fail("action must be add|remove|xenotype|list.");

                var endo = p.genes.Endogenes.Select(g => g.def.defName).ToList();
                var xeno = p.genes.Xenogenes.Select(g => g.def.defName).ToList();
                return (object)new
                {
                    success = true, action = A, notes,
                    xenotype = p.genes.Xenotype != null ? p.genes.Xenotype.defName : null,
                    xenotypeName = p.genes.xenotypeName,
                    endogeneCount = endo.Count, xenogeneCount = xeno.Count,
                    endogenes = endo, xenogenes = xeno,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/set_pawn_age",
            Description =
                "Set a pawn's biological and/or chronological age in YEARS. " +
                "🔴 Uses ageTracker.DebugSetAge, NOT the raw AgeBiologicalTicks setter - " +
                "DebugSetAge fires each BirthdayBiological along the way, which is what " +
                "applies life-stage hediffs and growth moments. The raw setter skips all of " +
                "that and leaves a pawn in a state nothing produced. " +
                "⚠️ BODY TYPE IS NOT AUTO-CORRECTED. The result reports whether the body " +
                "type now mismatches the life stage so you can fix it with " +
                "jawa/set_pawn_appearance.",
            ResultDescription = "success, before/after age, life stage, and a bodyTypeMismatch flag.")]
        public static async Task<object> SetPawnAge(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "Biological age in years. -1 leaves it.")] float biologicalYears = -1f,
            [ToolParameter(Description = "Chronological age in years. -1 leaves it.")] float chronologicalYears = -1f,
            [ToolParameter(Description = "Permit aging DOWN. DebugSetAge is forward-only, so this uses the raw setter and SKIPS every birthday.")] bool allowBackwards = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (p.ageTracker == null) return Fail("Pawn has no age tracker.");
                const long YEAR = 3600000L;

                var before = new
                {
                    biologicalYears = p.ageTracker.AgeBiologicalYears,
                    chronologicalYears = p.ageTracker.AgeChronologicalYears,
                    lifeStage = p.ageTracker.CurLifeStage != null ? p.ageTracker.CurLifeStage.defName : null,
                    bodyType = p.story != null && p.story.bodyType != null ? p.story.bodyType.defName : null,
                    developmental = p.DevelopmentalStage.ToString(),
                };

                var ageNotes = new List<string>();
                if (biologicalYears >= 0f)
                {
                    long wantTicks = (long)(biologicalYears * YEAR);
                    long haveTicks = p.ageTracker.AgeBiologicalTicks;

                    // 🔴 MEASURED 2026-08-19: DebugSetAge is FORWARD-ONLY. It walks
                    // birthdays forward and silently does NOTHING when asked to go down
                    // (54 -> 8 left the pawn at 54). Refuse loudly rather than report a
                    // success that changed nothing.
                    if (wantTicks < haveTicks && !allowBackwards)
                        return Fail("DebugSetAge is FORWARD-ONLY - it walks birthdays forward and silently does nothing when asked to age DOWN. " +
                                    "Pawn is " + p.ageTracker.AgeBiologicalYears + ", you asked for " + biologicalYears + ". " +
                                    "Pass allowBackwards=true to use the RAW setter instead, which works but SKIPS every BirthdayBiological - " +
                                    "so life-stage hediffs and growth moments never fire and the pawn ends in a state nothing produced.");

                    try
                    {
                        if (wantTicks < haveTicks)
                        {
                            p.ageTracker.AgeBiologicalTicks = wantTicks;
                            ageNotes.Add("aged DOWN via the raw setter - every BirthdayBiological was SKIPPED");
                        }
                        else
                        {
                            p.ageTracker.DebugSetAge(wantTicks);
                            ageNotes.Add("aged up via DebugSetAge - birthdays fired normally");
                        }
                    }
                    catch (Exception e) { return Fail("Age set threw: " + e.GetType().Name + ": " + e.Message); }
                }
                if (chronologicalYears >= 0f)
                {
                    try { p.ageTracker.AgeChronologicalTicks = (long)(chronologicalYears * YEAR); }
                    catch (Exception e) { return Fail("AgeChronologicalTicks threw: " + e.Message); }
                }
                if (biologicalYears < 0f && chronologicalYears < 0f) return Fail("Give a biological and/or chronological age.");

                try { p.Drawer.renderer.SetAllGraphicsDirty(); } catch { }

                var stage = p.ageTracker.CurLifeStage;
                var bt = p.story != null && p.story.bodyType != null ? p.story.bodyType.defName : null;
                bool mismatch = false;
                var dev = p.DevelopmentalStage;
                if (bt != null)
                {
                    bool bodyIsChild = bt == "Child" || bt == "Baby";
                    bool stageIsChild = dev == DevelopmentalStage.Child || dev == DevelopmentalStage.Baby || dev == DevelopmentalStage.Newborn;
                    mismatch = bodyIsChild != stageIsChild;
                }

                return (object)new
                {
                    success = true,
                    before,
                    after = new
                    {
                        biologicalYears = p.ageTracker.AgeBiologicalYears,
                        chronologicalYears = p.ageTracker.AgeChronologicalYears,
                        lifeStage = stage != null ? stage.defName : null,
                        bodyType = bt,
                        developmental = dev.ToString(),
                    },
                    ageNotes,
                    bodyTypeMismatch = mismatch,
                    warning = mismatch
                        ? "BODY TYPE NOW MISMATCHES THE LIFE STAGE. RimWorld does not correct this on an age change - fix it with jawa/set_pawn_appearance."
                        : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }


        // ================================================================
        //  P4 - PSYCHIC, PREGNANCY, MENTAL STATES, ROMANCE
        // ================================================================

        [Tool(
            "jawa/pawn_psychic",
            Description =
                "Set psylink level, grant or remove abilities/psycasts, and set psyfocus. " +
                "⚠ OVERLAPS jawa/grant_ability, which calls the same GainAbility for ANY AbilityDef. " +
                "This tool is the psycast-shaped one and owns psylink and psyfocus; that one is the " +
                "general grant. Neither is a superset of the other. " +
                "action='get' | 'psylink' | 'grant' | 'remove' | 'psyfocus'. " +
                "🔴 THE 0->N QUIRK IS HANDLED FOR YOU: PawnUtility.ChangePsylinkLevel " +
                "creates the PsychicAmplifier hediff on the FIRST call and returns without " +
                "ever reading the offset, so a single call can only ever reach level 1. " +
                "This tool ensures the hediff exists, then sets the exact level through " +
                "Hediff_Psylink.ChangeLevel. " +
                "📌 Granting a psycast WITHOUT a psylink works - nothing in GainAbility " +
                "checks. What gates CASTING is psyfocus band, so an ability granted to a " +
                "psylink-less pawn may be present and unusable.",
            ResultDescription = "success, psylinkLevel, psyfocus, entropy, abilities[].")]
        public static async Task<object> PawnPsychic(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'get' | 'psylink' | 'grant' | 'remove' | 'psyfocus'.")] string action = "get",
            [ToolParameter(Description = "Target psylink level 0-6 for action='psylink'.")] int level = -1,
            [ToolParameter(Description = "AbilityDef name for grant/remove.")] string ability = null,
            [ToolParameter(Description = "Psyfocus 0-1 for action='psyfocus'. -1 leaves it.")] float psyfocus = -1f,
            [ToolParameter(Description = "Clear all neural heat (entropy).")] bool clearEntropy = false,
            [ToolParameter(Description = "List only psycasts when reporting abilities.")] bool psycastsOnly = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                string A = (action ?? "get").Trim().ToLowerInvariant();
                var notes = new List<string>();

                if (A == "psylink")
                {
                    if (!ModsConfig.RoyaltyActive)
                        return Fail("Royalty is not active. Psylinks do not exist in this game.");
                    if (level < 0) return Fail("Give a target level 0-6.");
                    try
                    {
                        var src = p.GetMainPsylinkSource();
                        if (src == null)
                        {
                            // First call ONLY creates the hediff at level 1 - the offset is
                            // never read. This is the documented quirk, handled here.
                            p.ChangePsylinkLevel(1, false);
                            src = p.GetMainPsylinkSource();
                            notes.Add("created the PsychicAmplifier hediff (level 1) - the first ChangePsylinkLevel call never reads its offset");
                        }
                        if (src == null) return Fail("Could not create a psylink source on this pawn.");
                        int cur = src.level;
                        if (level != cur)
                        {
                            src.ChangeLevel(level - cur, false);
                            notes.Add("ChangeLevel(" + (level - cur) + ") -> " + src.level);
                        }
                        if (level == 0)
                        {
                            p.health.RemoveHediff(src);
                            notes.Add("level 0 requested - removed the psylink hediff entirely");
                        }
                    }
                    catch (Exception e) { return Fail("Psylink change threw: " + e.GetType().Name + ": " + e.Message); }
                }
                else if (A == "grant" || A == "remove")
                {
                    if (p.abilities == null) return Fail("Pawn has no ability tracker.");
                    if (string.IsNullOrEmpty(ability)) return Fail("Give an AbilityDef.");
                    var ad = DefDatabase<AbilityDef>.GetNamedSilentFail(ability.Trim());
                    if (ad == null) return Fail("No AbilityDef '" + ability + "'.", DefSuggestions<AbilityDef>(ability));
                    if (A == "grant")
                    {
                        p.abilities.GainAbility(ad);
                        notes.Add("granted " + ad.defName + (ad.IsPsycast ? " (a PSYCAST)" : ""));
                        if (ad.IsPsycast && p.GetPsylinkLevel() <= 0)
                            notes.Add("⚠️ this pawn has NO psylink - the psycast is present but casting is gated on psyfocus band, so it may be unusable");
                    }
                    else { p.abilities.RemoveAbility(ad); notes.Add("removed " + ad.defName); }
                }
                else if (A == "psyfocus")
                {
                    var pe = p.psychicEntropy;
                    if (pe == null) return Fail("Pawn has no psychic entropy tracker.");
                    if (psyfocus >= 0f)
                    {
                        try { pe.OffsetPsyfocusDirectly(Mathf.Clamp01(psyfocus) - pe.CurrentPsyfocus); notes.Add("psyfocus set"); }
                        catch (Exception e) { notes.Add("OffsetPsyfocusDirectly failed: " + e.Message); }
                    }
                    if (clearEntropy)
                    {
                        try { pe.RemoveAllEntropy(); notes.Add("entropy cleared"); }
                        catch (Exception e) { notes.Add("RemoveAllEntropy failed: " + e.Message); }
                    }
                }
                else if (A != "get") return Fail("action must be get|psylink|grant|remove|psyfocus.");

                var abil = new List<object>();
                if (p.abilities != null)
                    foreach (var a in p.abilities.AllAbilitiesForReading)
                    {
                        if (psycastsOnly && !a.def.IsPsycast) continue;
                        abil.Add(new { def = a.def.defName, label = a.def.label, isPsycast = a.def.IsPsycast });
                    }

                var pe2 = p.psychicEntropy;
                return (object)new
                {
                    success = true, action = A, notes,
                    royaltyActive = ModsConfig.RoyaltyActive,
                    psylinkLevel = p.GetPsylinkLevel(),
                    psyfocus = pe2 != null ? (object)pe2.CurrentPsyfocus : null,
                    entropy = pe2 != null ? (object)pe2.EntropyValue : null,
                    maxEntropy = pe2 != null ? (object)pe2.MaxEntropy : null,
                    abilityCount = abil.Count, abilities = abil,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_pregnancy",
            Description =
                "Start, advance or end a pregnancy. action='get' | 'start' | 'progress' | 'end'. " +
                "🔑 GESTATION PROGRESS *IS* THE HEDIFF SEVERITY - there is no separate field. " +
                "Setting it to 1 makes labour begin on the next tick. " +
                "'start' mirrors JobDriver_Lovin: MakeHediff(PregnantHuman) + SetParents with " +
                "an inherited gene set + AddHediff. " +
                "⚠️ PregnancyUtility.GetInheritedGeneSet can FAIL when the combined genes blow " +
                "the metabolism limit; vanilla aborts the pregnancy there and so does this, " +
                "rather than producing a child with no genes.",
            ResultDescription = "success, pregnancy state, gestation, mother and father.")]
        public static async Task<object> PawnPregnancy(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The MOTHER's pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'get' | 'start' | 'progress' | 'end'.")] string action = "get",
            [ToolParameter(Description = "The father's pawn id or name, for 'start'.")] string father = null,
            [ToolParameter(Description = "Gestation 0-1 for 'progress'. 1 begins labour.")] float progress = -1f,
            [ToolParameter(Description = "For 'end': true force-ends quietly, false terminates with the mood hit.")] bool quiet = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (!ModsConfig.BiotechActive)
                    return Fail("Biotech is not active. Pregnancy does not exist in this game.");
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                string A = (action ?? "get").Trim().ToLowerInvariant();
                var notes = new List<string>();

                Func<Hediff> getPreg = () =>
                {
                    try { return PregnancyUtility.GetPregnancyHediff(p); }
                    catch { return p.health.hediffSet.hediffs.FirstOrDefault(h => h is Hediff_Pregnant); }
                };

                if (A == "start")
                {
                    if (getPreg() != null) return Fail("This pawn is already pregnant.");
                    Pawn dad = null;
                    if (!string.IsNullOrEmpty(father)) { string e2; dad = FindPawn(father, out e2); if (dad == null) return Fail(e2); }

                    bool humanlike = p.RaceProps != null && p.RaceProps.Humanlike;
                    var def = humanlike ? HediffDefOf.PregnantHuman : HediffDefOf.Pregnant;
                    if (humanlike && dad != null)
                    {
                        try
                        {
                            if (!PregnancyUtility.CanEverProduceChild(dad, p))
                                return Fail("PregnancyUtility.CanEverProduceChild says these two can never produce a child - " +
                                            "check gender, life stage, sterility genes and Fertility stat.");
                        }
                        catch (Exception e) { notes.Add("CanEverProduceChild threw: " + e.Message); }
                    }

                    try
                    {
                        var h = (Hediff_Pregnant)HediffMaker.MakeHediff(def, p);
                        if (humanlike)
                        {
                            bool ok = true;
                            GeneSet gs = null;
                            try { gs = PregnancyUtility.GetInheritedGeneSet(dad, p, out ok); }
                            catch (Exception e) { notes.Add("GetInheritedGeneSet threw: " + e.Message); ok = false; }
                            if (!ok)
                                return Fail("The inherited gene set could not be produced - vanilla aborts a pregnancy here " +
                                            "(usually the combined genes exceed the metabolism limit). Refusing rather than " +
                                            "creating a child with no genes.");
                            h.SetParents(null, dad, gs);
                        }
                        p.health.AddHediff(h);
                        notes.Add("pregnancy started with " + def.defName + (dad != null ? ", father " + dad.LabelShort : ", no father"));
                    }
                    catch (Exception e) { return Fail("Starting the pregnancy threw: " + e.GetType().Name + ": " + e.Message); }
                }
                else if (A == "progress")
                {
                    var h = getPreg();
                    if (h == null) return Fail("This pawn is not pregnant.");
                    if (progress < 0f) return Fail("Give progress 0-1.");
                    h.Severity = Mathf.Clamp01(progress);
                    notes.Add("gestation (= hediff Severity) set to " + h.Severity +
                              (h.Severity >= 1f ? " - LABOUR WILL BEGIN ON THE NEXT TICK" : ""));
                }
                else if (A == "end")
                {
                    var h = getPreg();
                    if (h == null) return Fail("This pawn is not pregnant.");
                    try
                    {
                        if (quiet) { PregnancyUtility.ForceEndPregnancy(p, true); notes.Add("ForceEndPregnancy - no letter"); }
                        else { PregnancyUtility.TryTerminatePregnancy(p); notes.Add("TryTerminatePregnancy - adds the termination thought"); }
                    }
                    catch (Exception e)
                    {
                        p.health.RemoveHediff(h);
                        notes.Add("utility threw (" + e.Message + "); removed the hediff directly instead");
                    }
                }
                else if (A != "get") return Fail("action must be get|start|progress|end.");

                var cur = getPreg() as Hediff_Pregnant;
                return (object)new
                {
                    success = true, action = A, notes,
                    pregnant = cur != null,
                    hediff = cur != null ? cur.def.defName : null,
                    gestation = cur != null ? (object)cur.Severity : null,
                    mother = cur != null && cur.Mother != null ? cur.Mother.LabelShort : null,
                    father = cur != null && cur.Father != null ? cur.Father.LabelShort : null,
                    note = "Gestation IS the hediff severity - there is no separate progress field.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_mental",
            Description =
                "Force or end a mental state. action='list' | 'start' | 'end'. " +
                "⚠️ TryStartMentalState returns FALSE SILENTLY on about six conditions " +
                "(already in that state, asleep without forceWake, mutant that prevents " +
                "breaks, the worker refusing) - this tool surfaces that bool instead of " +
                "reporting success regardless. " +
                "🔴 SOME STATES NEVER RECOVER ON THEIR OWN: BerserkPermanent and " +
                "ManhunterPermanent set minTicksBeforeRecovery above the maximum. " +
                "action='list' flags them. RecoverFromState still works on all of them. " +
                "⚠️ Aggressive states let a colonist kill colonists.",
            ResultDescription = "success, started (the real bool), current state, and the def list.")]
        public static async Task<object> PawnMental(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'list' | 'start' | 'end'.")] string action = "list",
            [ToolParameter(Description = "MentalStateDef name.")] string state = null,
            [ToolParameter(Description = "Bypass the worker's own StateCanOccur check. Default true.")] bool forced = true,
            [ToolParameter(Description = "Start it even on a sleeping pawn. Default true.")] bool forceWake = true,
            [ToolParameter(Description = "Another pawn, for social states.")] string otherPawn = null,
            [ToolParameter(Description = "Max defs listed. Default 60.")] int limit = 60)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                string A = (action ?? "list").Trim().ToLowerInvariant();
                var notes = new List<string>();
                bool? started = null;

                if (A == "start")
                {
                    if (p.mindState == null || p.mindState.mentalStateHandler == null)
                        return Fail("Pawn has no mental state handler (animals and mechs may not).");
                    if (string.IsNullOrEmpty(state)) return Fail("Give a MentalStateDef.");
                    var sd = DefDatabase<MentalStateDef>.GetNamedSilentFail(state.Trim());
                    if (sd == null) return Fail("No MentalStateDef '" + state + "'.", DefSuggestions<MentalStateDef>(state));
                    Pawn other = null;
                    if (!string.IsNullOrEmpty(otherPawn)) { string e2; other = FindPawn(otherPawn, out e2); }
                    try
                    {
                        started = p.mindState.mentalStateHandler.TryStartMentalState(sd, "forced via bridge", forced, forceWake, false, other);
                        if (started != true)
                            notes.Add("TryStartMentalState returned FALSE - RimWorld refused. Common causes: already in this state, " +
                                      "asleep without forceWake, a mutant that prevents breaks, or the state's own worker saying no.");
                        if (sd.minTicksBeforeRecovery > sd.maxTicksBeforeRecovery)
                            notes.Add("⚠️ '" + sd.defName + "' NEVER RECOVERS on its own - use action='end'.");
                    }
                    catch (Exception e) { return Fail("TryStartMentalState threw: " + e.GetType().Name + ": " + e.Message); }
                }
                else if (A == "end")
                {
                    var ms = p.MentalState;
                    if (ms == null) return Fail("Pawn is not in a mental state.");
                    try { ms.RecoverFromState(); notes.Add("RecoverFromState - grants the recovery thought and notifies the breaker; the dirty alternative (Reset) does neither"); }
                    catch (Exception e) { return Fail("RecoverFromState threw: " + e.Message); }
                }
                else if (A != "list") return Fail("action must be list|start|end.");

                var defs = new List<object>();
                if (A == "list")
                    foreach (var d in DefDatabase<MentalStateDef>.AllDefsListForReading.Take(Math.Max(1, limit)))
                        defs.Add(new
                        {
                            def = d.defName,
                            label = d.label,
                            neverRecoversAlone = d.minTicksBeforeRecovery > d.maxTicksBeforeRecovery,
                            blockNormalThoughts = d.blockNormalThoughts,
                        });

                return (object)new
                {
                    success = true, action = A, started, notes,
                    currentState = p.MentalState != null ? p.MentalState.def.defName : null,
                    totalDefs = DefDatabase<MentalStateDef>.AllDefsListForReading.Count,
                    states = defs,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pawn_romance",
            Description =
                "Do the FULL social transaction, not just the relation flip. " +
                "action='romance' makes two pawns lovers and shares a bed; 'marry' runs " +
                "MarriageCeremonyUtility.Married - which ex-spouses everyone, removes Fiance, " +
                "adds the newly-married thoughts BOTH ways, renames after marriage and shares " +
                "a bed; 'breakup' mirrors InteractionWorker_Breakup so the BrokeUpWithMe " +
                "thought actually lands; 'memory' adds a ThoughtDef about another pawn. " +
                "🔑 OPINION IS PURELY COMPUTED - relation offsets plus thoughts. There is no " +
                "stored opinion field, so a MEMORY is the only lever on how two pawns feel.",
            ResultDescription = "success, what happened, opinion both ways, relations after.")]
        public static async Task<object> PawnRomance(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "First pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'romance' | 'marry' | 'breakup' | 'memory'.")] string action = "romance",
            [ToolParameter(Description = "The other pawn.")] string otherPawn = null,
            [ToolParameter(Description = "ThoughtDef for action='memory'.")] string thought = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var a = FindPawn(pawn, out err);
                if (a == null) return Fail(err);
                string e2; var b = FindPawn(otherPawn, out e2);
                if (b == null) return Fail(e2);
                if (a == b) return Fail("A pawn cannot romance itself.");
                string A = (action ?? "romance").Trim().ToLowerInvariant();
                var notes = new List<string>();

                try
                {
                    if (A == "romance")
                    {
                        foreach (var d in new[] { PawnRelationDefOf.ExLover, PawnRelationDefOf.ExSpouse })
                            if (a.relations.DirectRelationExists(d, b)) { a.relations.TryRemoveDirectRelation(d, b); notes.Add("cleared " + d.defName); }
                        if (!a.relations.DirectRelationExists(PawnRelationDefOf.Lover, b))
                        { a.relations.AddDirectRelation(PawnRelationDefOf.Lover, b); notes.Add("now lovers"); }
                        try { LovePartnerRelationUtility.TryToShareBed(a, b); notes.Add("shared a bed"); } catch (Exception ex) { notes.Add("TryToShareBed: " + ex.Message); }
                    }
                    else if (A == "marry")
                    {
                        MarriageCeremonyUtility.Married(a, b);
                        notes.Add("MarriageCeremonyUtility.Married - ex-spouses cleared, Fiance removed, newly-married thoughts both ways, name changed, bed shared. Setting Spouse alone would have skipped all of that.");
                    }
                    else if (A == "breakup")
                    {
                        bool wasSpouse = a.relations.DirectRelationExists(PawnRelationDefOf.Spouse, b);
                        foreach (var d in new[] { PawnRelationDefOf.Lover, PawnRelationDefOf.Fiance })
                            if (a.relations.DirectRelationExists(d, b)) { a.relations.TryRemoveDirectRelation(d, b); notes.Add("removed " + d.defName); }
                        if (wasSpouse)
                        {
                            a.relations.TryRemoveDirectRelation(PawnRelationDefOf.Spouse, b);
                            a.relations.AddDirectRelation(PawnRelationDefOf.ExSpouse, b);
                            notes.Add("Spouse -> ExSpouse");
                        }
                        else if (!a.relations.DirectRelationExists(PawnRelationDefOf.ExLover, b))
                        { a.relations.AddDirectRelation(PawnRelationDefOf.ExLover, b); notes.Add("added ExLover"); }
                        try
                        {
                            if (b.needs != null && b.needs.mood != null)
                            { b.needs.mood.thoughts.memories.TryGainMemory(ThoughtDefOf.BrokeUpWithMe, a); notes.Add("gave the other pawn the BrokeUpWithMe thought - a bare relation change produces NO thought"); }
                        }
                        catch (Exception ex) { notes.Add("BrokeUpWithMe: " + ex.Message); }
                    }
                    else if (A == "memory")
                    {
                        if (string.IsNullOrEmpty(thought)) return Fail("Give a ThoughtDef.");
                        var td = DefDatabase<ThoughtDef>.GetNamedSilentFail(thought.Trim());
                        if (td == null) return Fail("No ThoughtDef '" + thought + "'.", DefSuggestions<ThoughtDef>(thought));
                        if (a.needs == null || a.needs.mood == null) return Fail("Pawn has no mood need.");
                        a.needs.mood.thoughts.memories.TryGainMemory(td, b);
                        notes.Add("memory added - this is the ONLY lever on opinion, which is otherwise purely computed");
                    }
                    else return Fail("action must be romance|marry|breakup|memory.");
                }
                catch (Exception ex) { return Fail(A + " threw: " + ex.GetType().Name + ": " + ex.Message); }

                return (object)new
                {
                    success = true, action = A, notes,
                    opinionAtoB = a.relations.OpinionOf(b),
                    opinionBtoA = b.relations.OpinionOf(a),
                    relations = a.relations.DirectRelations
                        .Select(r => new { def = r.def.defName, with = r.otherPawn != null ? r.otherPawn.LabelShort : null }).ToList(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }

    }
}