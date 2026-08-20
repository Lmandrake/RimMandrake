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
            err = "No spawned pawn matching '" + id + "'. " + all.Count + " pawns are spawned.";
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
                    apparel.Add(new { def = a.def.defName, stuff = a.Stuff != null ? a.Stuff.defName : null, hp = a.HitPoints });

            var equipment = new List<object>();
            if (p.equipment != null)
                foreach (var e in p.equipment.AllEquipmentListForReading)
                    equipment.Add(new { def = e.def.defName, stuff = e.Stuff != null ? e.Stuff.defName : null, isPrimary = e == p.equipment.Primary });

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
    }
}
