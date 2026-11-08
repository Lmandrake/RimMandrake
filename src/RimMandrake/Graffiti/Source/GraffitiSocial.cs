using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    /// <summary>A pawn means to do something about a mark.</summary>
    public class RM_Grudge : IExposable
    {
        public Pawn pawn;
        public Filth_Mark mark;
        public Pawn against;
        public RM_Answer answer;
        public int notBefore;
        public int until;
        /// <summary>It was about a mark still standing: when that mark goes, so does the grudge.</summary>
        public bool aboutMark;

        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "pawn");
            Scribe_References.Look(ref mark, "mark");
            Scribe_References.Look(ref against, "against");
            Scribe_Values.Look(ref answer, "answer");
            Scribe_Values.Look(ref notBefore, "notBefore");
            Scribe_Values.Look(ref until, "until");
            Scribe_Values.Look(ref aboutMark, "aboutMark");
        }
    }

    // Owner, 2026-11-07: "did you test the social implications of the mod? It's more than just art display." The map's walls as people read
    // them: who sees which mark (a walk past it, in sight, in the same room), what it does to them, and who means to do something about it.
    // The marks register themselves on spawn, so this needs no scan of the map's things; only the grudges and visits are saved, the marks keep
    // their own readers.
    public class MapComponent_GraffitiSocial : MapComponent
    {
        private const int SightInterval = 180;

        internal readonly List<Filth_Mark> marks = new List<Filth_Mark>();
        private List<RM_Grudge> grudges = new List<RM_Grudge>();
        private Dictionary<int, int> lastAnswered = new Dictionary<int, int>();
        private int lastRaidMessage = -99999;
        // A visiting faction's goodwill off the walls this visit: when it began, what it has lost and gained. Owner's pick: capped per visit.
        private Dictionary<int, int> visitStart = new Dictionary<int, int>();
        private Dictionary<int, int> visitLost = new Dictionary<int, int>();
        private Dictionary<int, int> visitGained = new Dictionary<int, int>();
        // Walls the player had scrubbed (Designator_ScrubGraffiti): the floor cells before them and two cells either way, with the tick.
        // Live 2026-11-08: the corridor ordered clean after Mo's spree took ten new marks in two days, and the order looked pointless.
        private Dictionary<IntVec3, int> scrubbedHold = new Dictionary<IntVec3, int>();
        internal const int ScrubHoldTicks = 10 * GenDate.TicksPerDay;
        private const float ScrubHoldRadius = 2.9f;
        private static bool forgotten;

        /// <summary>The player ordered this mark scrubbed: the wall around it is left clean by our own painters for a while.</summary>
        internal void HoldScrubbed(Filth_Mark m)
        {
            int now = Find.TickManager.TicksGame;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(m.Position, ScrubHoldRadius, useCenter: true))
            {
                if (c.InBounds(map)) scrubbedHold[c] = now;
            }
            if (scrubbedHold.Count > 4000) scrubbedHold.RemoveAll(kv => now - kv.Value >= ScrubHoldTicks);
        }

        /// <summary>Is this floor cell before a wall the player had scrubbed in the last ten days?</summary>
        internal bool HeldClean(IntVec3 c)
        {
            int now = Find.TickManager.TicksGame;
            if (scrubbedHold.TryGetValue(c, out int at) && now - at < ScrubHoldTicks) return true;
            for (int i = 0; i < heldStretches.Count; i++)
            {
                if (now - heldSince[i] < ScrubHoldTicks && heldStretches[i].Contains(c)) return true;
            }
            return false;
        }

        // The stretches the player dragged a scrub over, from the first mark to the last, three cells wider (a mark is wider than its cell:
        // live, with two, painters lined up a cell past each end and their paint reached back over the scrubbed wall). The ring round each scrubbed
        // mark alone left gaps: live 2026-11-08, a corridor wall dragged clean took a tag and a mockery in the next day, each three cells
        // from a scrubbed mark, right where the player had just ordered clean.
        private List<CellRect> heldStretches = new List<CellRect>();
        private List<int> heldSince = new List<int>();

        /// <summary>The player ordered every mark in this stretch scrubbed: our painters leave all of it alone for ten days.</summary>
        internal void HoldStretch(CellRect r)
        {
            int now = Find.TickManager.TicksGame;
            for (int i = heldStretches.Count - 1; i >= 0; i--)
            {
                if (now - heldSince[i] >= ScrubHoldTicks) { heldStretches.RemoveAt(i); heldSince.RemoveAt(i); }
            }
            heldStretches.Add(r.ExpandedBy(3).ClipInsideMap(map));
            heldSince.Add(now);
        }

        public MapComponent_GraffitiSocial(Map map) : base(map)
        {
        }

        public static MapComponent_GraffitiSocial For(Map map)
        {
            return map?.GetComponent<MapComponent_GraffitiSocial>();
        }

        public IEnumerable<RM_Grudge> Grudges => grudges;

        /// <summary>Paint weathers: each mark redrawn as it fades, and gone when it's worn through. Nobody takes this as an insult.</summary>
        private void Weather()
        {
            foreach (Filth_Mark m in marks.ToList())
            {
                if (!m.Spawned) continue;
                int step = m.WeatherStepNow(out float fade);
                if (fade >= 1f)
                {
                    GraffitiSocial.Trace(m.def.defName.Replace("RM_Graffiti_", "") + "@" + m.Position + " by " + (m.maker?.LabelShort ?? "-") + " weathered away");
                    m.SkipCleanNotice();
                    m.Destroy();
                    continue;
                }
                if (step != m.weatherStep)
                {
                    m.weatherStep = step;
                    map.mapDrawer.MapMeshDirty(m.Position, MapMeshFlagDefOf.Things);
                }
            }
        }

        public override void MapComponentTick()
        {
            if (map.IsHashIntervalTick(GenDate.TicksPerHour) && marks.Count > 0) Weather();
            if (!RM_GraffitiSettings.socialEnabled)
            {
                // Off means off: what the walls made people feel, and what they meant to do about it, goes the moment the switch does.
                if (!forgotten)
                {
                    foreach (Map m in Find.Maps)
                    {
                        GraffitiTemperament.ForgetAll(m);
                        For(m)?.grudges.Clear();
                    }
                    forgotten = true;
                }
                return;
            }
            forgotten = false;
            if (marks.Count == 0) return;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.IsHashIntervalTick(SightInterval) && p.RaceProps.Humanlike)
                {
                    GraffitiSocial.Look(p, this);
                }
            }
        }

        /// <summary>The enemy marks standing in this map's Home area, not crossed out: what the colony's territory thought counts. Owner's pick:
        /// a raider's tag out on far rock, where nobody can order it cleaned, isn't a claim on the colony's walls.</summary>
        public int EnemyMarks(Faction of)
        {
            int n = 0;
            for (int i = 0; i < marks.Count; i++)
            {
                Filth_Mark m = marks[i];
                if (!m.defaced && m.makerFaction != null && m.makerFaction != of && m.makerFaction.HostileTo(of) && m.Spawned && map.areaManager.Home[m.Position]) n++;
            }
            return n;
        }

        internal void AddGrudge(Pawn pawn, Filth_Mark mark, Pawn against, RM_Answer answer)
        {
            if (answer == RM_Answer.None || pawn == null || !GraffitiSocial.Answers(pawn)) return;
            int now = Find.TickManager.TicksGame;
            lastAnswered.TryGetValue(pawn.thingIDNumber, out int last);
            if (last > 0 && now - last < RM_GraffitiKernel.AnswerCooldownTicks) return;
            foreach (RM_Grudge g in grudges)
            {
                if (g.pawn == pawn) return;
            }
            grudges.Add(new RM_Grudge
            {
                pawn = pawn, mark = mark, against = against, answer = answer, aboutMark = mark != null,
                notBefore = now + Rand.Range(240, 1200), until = now + RM_GraffitiKernel.GrudgeExpiryTicks,
            });
        }

        /// <summary>The grudge this pawn could act on now, with the dead ones dropped: a mark gone, a painter gone, a grudge too old to bear.</summary>
        internal RM_Grudge GrudgeOf(Pawn pawn)
        {
            int now = Find.TickManager.TicksGame;
            for (int i = grudges.Count - 1; i >= 0; i--)
            {
                RM_Grudge g = grudges[i];
                bool markGone = g.aboutMark && (g.mark == null || g.mark.Destroyed || !g.mark.Spawned);
                bool dead = g.pawn == null || g.pawn.Dead || now > g.until || markGone
                    || ((g.answer == RM_Answer.Scrub || g.answer == RM_Answer.Deface) && (g.mark == null || g.mark.defaced))
                    || ((g.answer == RM_Answer.Reply || g.answer == RM_Answer.Confront) && (g.against == null || g.against.Dead || !g.against.Spawned || g.against.Map != map));
                if (dead)
                {
                    grudges.RemoveAt(i);
                    continue;
                }
                if (g.pawn == pawn && now >= g.notBefore) return g;
            }
            return null;
        }

        /// <summary>An answer was attempted and couldn't start: it stays open, and is tried again later.</summary>
        internal void Postpone(RM_Grudge g)
        {
            g.notBefore = Find.TickManager.TicksGame + RM_GraffitiKernel.AnswerRetryTicks;
        }

        /// <summary>A pawn finished answering this mark, or this painter: their grudge about it is settled, and they cool off.</summary>
        internal void Answered(Pawn pawn, Filth_Mark mark, Pawn against)
        {
            for (int i = grudges.Count - 1; i >= 0; i--)
            {
                RM_Grudge g = grudges[i];
                if (g.pawn == pawn && ((mark != null && g.mark == mark) || (against != null && g.against == against)))
                {
                    grudges.RemoveAt(i);
                    lastAnswered[pawn.thingIDNumber] = Find.TickManager.TicksGame;
                }
            }
        }

        internal bool RaidMessageDue()
        {
            int now = Find.TickManager.TicksGame;
            if (now - lastRaidMessage < 5000) return false;
            lastRaidMessage = now;
            return true;
        }

        /// <summary>What a visitor's read may still move this visit; records it.</summary>
        internal int ChargeVisit(Faction f, int delta)
        {
            int now = Find.TickManager.TicksGame;
            int id = f.loadID;
            if (!visitStart.TryGetValue(id, out int start) || now - start > RM_GraffitiKernel.VisitTicks)
            {
                visitStart[id] = now;
                visitLost[id] = 0;
                visitGained[id] = 0;
            }
            visitLost.TryGetValue(id, out int lost);
            visitGained.TryGetValue(id, out int gained);
            int charge = RM_GraffitiKernel.VisitCharge(delta, lost, gained);
            if (charge < 0) visitLost[id] = lost - charge;
            if (charge > 0) visitGained[id] = gained + charge;
            return charge;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref grudges, "rmGrudges", LookMode.Deep);
            Scribe_Collections.Look(ref lastAnswered, "rmLastAnswered", LookMode.Value, LookMode.Value);
            Scribe_Values.Look(ref lastRaidMessage, "rmLastRaidMessage", -99999);
            Scribe_Collections.Look(ref visitStart, "rmVisitStart", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref visitLost, "rmVisitLost", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref visitGained, "rmVisitGained", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.Saving) scrubbedHold.RemoveAll(kv => Find.TickManager.TicksGame - kv.Value >= ScrubHoldTicks);
            Scribe_Collections.Look(ref scrubbedHold, "rmScrubbedHold", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref heldStretches, "rmHeldStretches", LookMode.Value);
            Scribe_Collections.Look(ref heldSince, "rmHeldSince", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                scrubbedHold = scrubbedHold ?? new Dictionary<IntVec3, int>();
                heldStretches = heldStretches ?? new List<CellRect>();
                heldSince = heldSince ?? new List<int>();
                if (heldSince.Count != heldStretches.Count) { heldStretches.Clear(); heldSince.Clear(); }
                grudges = grudges ?? new List<RM_Grudge>();
                lastAnswered = lastAnswered ?? new Dictionary<int, int>();
                visitStart = visitStart ?? new Dictionary<int, int>();
                visitLost = visitLost ?? new Dictionary<int, int>();
                visitGained = visitGained ?? new Dictionary<int, int>();
                grudges.RemoveAll(g => g == null || g.pawn == null);
            }
        }
    }

    public static class GraffitiSocial
    {
        // ---------------------------------------------------------------- who counts

        /// <summary>Who does something about a mark: free adult colonists. Prisoners, slaves and children read and feel, and leave it at that.</summary>
        internal static bool Answers(Pawn p)
        {
            return p.IsColonist && !p.IsSlave && !p.IsPrisoner && p.DevelopmentalStage.Adult() && !GraffitiTemperament.IsNumb(p);
        }

        // ---------------------------------------------------------------- reading the walls

        internal static void Look(Pawn viewer, MapComponent_GraffitiSocial comp)
        {
            if (!viewer.Spawned || viewer.Downed || !viewer.Awake() || viewer.needs?.mood == null) return;
            if (viewer.DevelopmentalStage.Baby()) return;
            if (viewer.health.capacities.GetLevel(PawnCapacityDefOf.Sight) < 0.3f) return;
            Map map = viewer.Map;
            Room room = viewer.GetRoom();
            int now = Find.TickManager.TicksGame;
            bool ours = viewer.Faction == Faction.OfPlayer || viewer.IsPrisonerOfColony;
            bool visitor = !ours && viewer.Faction != null && !viewer.Faction.HostileTo(Faction.OfPlayer);
            if (!ours && !visitor) return;
            // A mark about you jumps out at you: on a wall full of tags, the one with your face on it is what you see first.
            for (int pass = 0; pass < 2; pass++)
            {
                for (int i = 0; i < comp.marks.Count; i++)
                {
                    Filth_Mark mark = comp.marks[i];
                    if ((mark.subject == viewer) != (pass == 0)) continue;
                    if (LooksAt(viewer, mark, comp, map, room, now, ours, visitor)) return;
                }
            }
        }

        /// <summary>One viewer, one mark: true if the look is used up (one thing at a time: the next look finds the next mark).</summary>
        private static bool LooksAt(Pawn viewer, Filth_Mark mark, MapComponent_GraffitiSocial comp, Map map, Room room, int now, bool ours, bool visitor)
        {
            if ((mark.Position - viewer.Position).LengthHorizontalSquared > RM_GraffitiKernel.SightRadiusSq) return false;
            if (mark.Position.Fogged(map) || mark.Position.GetRoom(map) != room) return false;
            if (ours && !mark.ReadyToBeRead(viewer, now)) return false;
            if (visitor && mark.FactionHasRead(viewer.Faction)) return false;
            if (!GenSight.LineOfSight(viewer.Position, mark.Position, map, skipFirstCell: true)) return false;
            if (visitor) return VisitorReads(viewer, mark, comp);
            bool first = mark.FirstReadBy(viewer);
            mark.NoteRead(viewer, now);
            return Reads(viewer, mark, comp, first);
        }

        internal static RM_Viewer StandingOf(Pawn v, Filth_Mark m)
        {
            Pawn maker = m.maker, subject = m.subject;
            TraitSet traits = v.story?.traits;
            return new RM_Viewer
            {
                isMaker = maker == v,
                isSubject = subject == v,
                ownFaction = m.makerFaction != null && m.makerFaction == (v.HostFaction ?? v.Faction),
                hostileMaker = m.makerFaction != null && v.Faction != null && m.makerFaction != v.Faction && m.makerFaction.HostileTo(v.Faction),
                loverOfSubject = subject != null && subject != v && LovePartnerRelationUtility.LovePartnerRelationExists(v, subject),
                loverOfMaker = maker != null && maker != v && LovePartnerRelationUtility.LovePartnerRelationExists(v, maker),
                opinionOfMaker = maker != null && maker != v && v.relations != null ? v.relations.OpinionOf(maker) : 0,
                opinionOfSubject = subject != null && subject != v && v.relations != null ? v.relations.OpinionOf(subject) : 0,
                kind = traits != null && traits.HasTrait(TraitDefOf.Kind),
                hot = GraffitiTemperament.IsHot(v),
                psychopath = traits != null && traits.HasTrait(TraitDefOf.Psychopath),
                hasIdeo = GraffitiJobUtility.IdeoOf(v) != null,
                makerHasIdeo = m.makerIdeo != null,
                sameIdeoAsMaker = GraffitiJobUtility.IdeoOf(v) != null && GraffitiJobUtility.IdeoOf(v) == m.makerIdeo,
            };
        }

        /// <summary>One colonist reads one mark. True if it did something to them. The first reading gives everything; a reading a day or
        /// more later gives the mood again, weaker, and nothing else (owner, card 2026-11-07).</summary>
        private static bool Reads(Pawn v, Filth_Mark m, MapComponent_GraffitiSocial comp, bool first)
        {
            RM_Temper temper = GraffitiTemperament.Of(v);
            if (temper.numb) return false;
            bool own = m.maker == v;
            float again = first ? 1f : RM_GraffitiKernel.RereadFactor;
            bool did = false;
            // The paint itself, before what it says: a plain tag is still a good or a bad piece of work (personality pass, section 9).
            if (m.hasCraft && !own && !m.defaced)
            {
                int stage = RM_GraffitiKernel.CraftStage(m.craft, out bool ugly);
                if (stage >= 0)
                {
                    did |= ugly ? GraffitiTemperament.Give(v, T.RM_Graffiti_UglyMark, null, again, 2, stage)
                        : GraffitiTemperament.Give(v, T.RM_Graffiti_FineArt, m.maker, again, 1, stage);
                }
            }
            // A clean freak minds the mess, whatever it says and however fine it is.
            if (temper.neat > 0 && !own && GameComponent_Graffiti.Get?.MessDue(v) == true)
            {
                did |= GraffitiTemperament.Give(v, T.RM_Graffiti_Mess, null, 1f, 2, temper.neat >= 2 ? 1 : 0);
                Trace(v.LabelShort + " minds the mess at " + m.Position + " (neat " + temper.neat + ")");
            }
            RM_Viewer standing = StandingOf(v, m);
            if (!RM_GraffitiKernel.StillSpeaks(m.defaced, standing.isMaker)) return did;
            RM_Reaction reaction = RM_GraffitiKernel.ReactionOf(m.Meaning, standing);
            Trace(v.LabelShort + (first ? " reads " : " rereads ") + m.def.defName.Replace("RM_Graffiti_", "") + "@" + m.Position + " by " + (m.maker?.LabelShort ?? "-")
                + " about " + (m.subject?.LabelShort ?? "-") + " -> " + reaction + " (maker " + standing.isMaker + ", subject " + standing.isSubject + ", of subject "
                + standing.opinionOfSubject + ", neat " + temper.neat + ")");
            if (reaction == RM_Reaction.None) return did;
            Apply(v, m, reaction, first, m.Reach * again);
            if (Treasures(reaction)) m.NoteValued(v);
            if (!first) return true;
            m.NoteReaction(reaction);
            Pawn other = reaction == RM_Reaction.Uneasy || reaction == RM_Reaction.Defiant ? null : m.maker;
            bool makerHere = other != null && other.Spawned && other.Map == v.Map && !other.Dead;
            RM_Answer answer = Answers(v)
                ? RM_GraffitiKernel.AnswerOf(reaction, standing.hot, !v.WorkTagIsDisabled(WorkTags.Violent), makerHere, CanReplyInPaint(v) && !m.lastWord && GameComponent_Graffiti.Get?.MockeryDue(v, m.maker) != false, Rand.Value, temper.lean)
                : RM_Answer.None;
            comp.AddGrudge(v, m, other, answer);
            if (answer != RM_Answer.None) Trace(v.LabelShort + " means to " + answer + (other != null ? " against " + other.LabelShort : ""));
            return true;
        }

        /// <summary>A reaction that makes a mark dear to its reader.</summary>
        private static bool Treasures(RM_Reaction r)
        {
            return r == RM_Reaction.Honored || r == RM_Reaction.Mourning || r == RM_Reaction.Moved || r == RM_Reaction.Uplifted || r == RM_Reaction.Warmed || r == RM_Reaction.FriendTag;
        }

        /// <summary>A hand that answers in paint: some skill, Artistic not beneath them, and allowed to paint a mockery at all (owner's pick: replies
        /// obey PainterMayPaint like any other mark, so a Kind artist doesn't paint cruelty and an Artistic-disabled pawn doesn't reply).</summary>
        internal static bool CanReplyInPaint(Pawn p)
        {
            return RM_GraffitiSettings.paintingEnabled && !p.WorkTagIsDisabled(WorkTags.Artistic) && (p.skills?.GetSkill(SkillDefOf.Artistic)?.Level ?? 0) >= 5
                && GraffitiPool.PainterMayPaint(RMGraffitiDefOf.RM_Graffiti_Mockery, p);
        }

        private static void Apply(Pawn v, Filth_Mark m, RM_Reaction reaction, bool first, float reach)
        {
            Pawn maker = m.maker, subject = m.subject;
            string makerName = maker?.LabelShort ?? "someone";
            string subjectName = m.SubjectName;
            string line = null;
            string log = null;
            Color tone = Tone.Neutral;
            // Mood comes with every reading; how they regard the people in it changes once, on the first.
            void Mood(ThoughtDef def, Pawn about, bool victim = false) { GraffitiTemperament.Give(v, def, about, reach, 0, 0, victim); }
            void Regard(ThoughtDef def, Pawn about, bool victim = false) { if (first) GraffitiTemperament.Give(v, def, about, reach, 0, 0, victim); }
            switch (reaction)
            {
                case RM_Reaction.Humiliated:
                    Mood(T.RM_Graffiti_Humiliated, maker, true); Regard(T.RM_Graffiti_PaintedMe, maker, true);
                    line = "Who painted that?!"; tone = Tone.Angry; log = "{0} found what {1} painted about them on the wall, and went white.";
                    break;
                case RM_Reaction.ShrugsOff:
                    Mood(T.RM_Graffiti_ShruggedOff, maker);
                    line = "Ha! Good likeness."; tone = Tone.Warm; log = "{0} laughed at the picture {1} painted of them.";
                    break;
                case RM_Reaction.FriendDefends:
                    Mood(T.RM_Graffiti_FriendMocked, subject); Regard(T.RM_Graffiti_MockedMyFriend, maker);
                    line = "That's " + subjectName + " up there."; tone = Tone.Angry; log = "{0} saw what {1} painted about " + subjectName + " and took it badly.";
                    break;
                case RM_Reaction.Gleeful:
                    if (subject != null) { Mood(T.RM_Graffiti_EnjoyedIt, subject); Regard(T.RM_Graffiti_SaidItForMe, maker); }
                    else Mood(T.RM_Graffiti_EnjoyedInsult, null);
                    line = "Ha. About time."; tone = Tone.Warm; log = "{0} grinned at what {1} put on the wall.";
                    break;
                case RM_Reaction.LostFace:
                    Regard(T.RM_Graffiti_WhatTheWallSays, subject);
                    line = "Is that true, about " + subjectName + "?"; tone = Tone.Neutral; log = "{0} read what {1} painted about " + subjectName + ", and it stuck.";
                    break;
                case RM_Reaction.Disapproves:
                    Regard(T.RM_Graffiti_Cruel, maker);
                    line = "That's cruel."; tone = Tone.Neutral; log = "{0} thought less of {1} after reading the wall.";
                    break;
                case RM_Reaction.Honored:
                    Mood(T.RM_Graffiti_Honored, maker); Regard(T.RM_Graffiti_HonoredMe, maker);
                    line = "That's... me."; tone = Tone.Warm; log = "{0} found the tribute {1} painted for them and stood looking at it.";
                    break;
                case RM_Reaction.Jealous:
                    Mood(T.RM_Graffiti_JealousOfWall, subject); Regard(T.RM_Graffiti_PaintedSomeoneElse, maker);
                    line = "Never painted ME."; tone = Tone.Angry; log = "{0} saw {1}'s tribute to " + subjectName + " and said nothing, loudly.";
                    break;
                case RM_Reaction.Scoffs:
                    Regard(T.RM_Graffiti_HonoredMyEnemy, maker);
                    line = "A tribute? To them?"; tone = Tone.Neutral; log = "{0} scoffed at {1}'s tribute to " + subjectName + ".";
                    break;
                case RM_Reaction.Warmed:
                    Mood(T.RM_Graffiti_Warmed, subject);
                    line = "Good for " + subjectName + "."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Mourning:
                    Mood(T.RM_Graffiti_Mourning, subject); Regard(T.RM_Graffiti_Remembered, maker);
                    line = "I miss " + subjectName + "."; tone = Tone.Warm; log = "{0} stopped at {1}'s memorial for " + subjectName + ".";
                    break;
                case RM_Reaction.Amused:
                    Mood(T.RM_Graffiti_Amused, null);
                    line = "Heh."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Moved:
                    Mood(T.RM_Graffiti_MovedByPiece, maker); Regard(T.RM_Graffiti_Artist, maker);
                    line = "Who made this?"; tone = Tone.Warm; log = "{0} stood looking at {1}'s piece on the wall.";
                    break;
                case RM_Reaction.Uplifted:
                    Mood(T.RM_Graffiti_Uplifted, null); Regard(T.RM_Graffiti_Faithful, maker);
                    line = "Our sign."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Offended:
                    GraffitiTemperament.Give(v, T.RM_Graffiti_Offended, null, reach, 3);
                    if (first && maker != null) GraffitiTemperament.Give(v, T.RM_Graffiti_Heretic, maker, reach, 3);
                    line = "Whose creed is that?"; tone = Tone.Angry; log = "{0} was offended by the creed {1} painted on the wall.";
                    break;
                case RM_Reaction.RivalTag:
                    Mood(T.RM_Graffiti_RivalHandMood, maker); Regard(T.RM_Graffiti_RivalHand, maker);
                    line = "Of course. " + makerName + " again."; tone = Tone.Angry; log = "{0} glared at {1}'s tag on the wall.";
                    break;
                case RM_Reaction.FriendTag:
                    Mood(T.RM_Graffiti_FriendHand, maker);
                    line = "That's " + makerName + "'s hand."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Uneasy:
                    // The mood is the situational "enemy graffiti nearby" (RM_Graffiti_ViewedHostileMark), there while they're near it.
                    line = "They were here."; tone = Tone.Neutral;
                    break;
                case RM_Reaction.Defiant:
                    Mood(T.RM_Graffiti_Defiant, null);
                    line = "Let them come back."; tone = Tone.Angry;
                    break;
            }
            if (!first) return;
            Say(v, line, tone);
            // A rival's tags, a friend's pieces, a creed: one walk down a corridor past five of them is one feeling, not five lines in the
            // log (live 2026-11-07: "Mo glared at BW's tag" three times in 360 ticks). Events (a mockery read, a tribute) always log.
            if (log != null && RM_GraffitiKernel.LogsOncePerDay(reaction) && LoggedToday(v, maker, reaction)) log = null;
            if (log != null) Log(v, maker, string.Format(log, v.LabelShort, makerName));
            if (log != null && RM_GraffitiKernel.Announces(reaction) && RM_GraffitiSettings.socialMessagesEnabled && PawnUtility.ShouldSendNotificationAbout(v))
            {
                Tell(string.Format(log, v.LabelShort, makerName), WallTarget(m), reaction == RM_Reaction.Humiliated ? MessageTypeDefOf.NegativeEvent : MessageTypeDefOf.SilentInput, historical: true);
            }
        }

        /// <summary>Every message the walls send, counted and kept (the game's own list forgets them in seconds), so a run of days can say how
        /// many reached the player: the owner's "never a stream of messages".</summary>
        internal static int messagesSent;
        internal static readonly List<string> messagesKept = new List<string>();

        internal static void Tell(string text, LookTargets at, MessageTypeDef type, bool historical = true)
        {
            messagesSent++;
            messagesKept.Add(Find.TickManager.TicksGame + " " + text);
            if (messagesKept.Count > 300) messagesKept.RemoveAt(0);
            Messages.Message(text, at, type, historical);
        }

        private static readonly Dictionary<long, int> lastLogged = new Dictionary<long, int>();

        /// <summary>Has this reader already had this kind of feeling about this painter's marks logged in the last day? Records it if not.</summary>
        private static bool LoggedToday(Pawn v, Pawn maker, RM_Reaction reaction)
        {
            long key = ((long)v.thingIDNumber << 32) ^ ((long)(maker?.thingIDNumber ?? 0) << 8) ^ (long)reaction;
            int now = Find.TickManager.TicksGame;
            if (lastLogged.TryGetValue(key, out int at) && at <= now && now - at < GenDate.TicksPerDay) return true;
            lastLogged[key] = now;
            return false;
        }

        /// <summary>A visitor's faction reads a mark on the host's wall, once per mark. Owner's pick: only marks your own people painted count,
        /// and one visit moves goodwill only so far. True if it moved anything.</summary>
        private static bool VisitorReads(Pawn v, Filth_Mark m, MapComponent_GraffitiSocial comp)
        {
            m.NoteFactionRead(v.Faction);
            if (m.defaced || m.makerFaction != Faction.OfPlayer) return false;
            ModExtension_Graffiti ext = m.def.GetModExtension<ModExtension_Graffiti>();
            bool taunt = ext != null && ext.category == GraffitiCategory.Taunt;
            int delta = RM_GraffitiKernel.GoodwillOf(m.Meaning, m.targetFaction == v.Faction, taunt, GraffitiJobUtility.IdeoOf(v) != null && GraffitiJobUtility.IdeoOf(v) == m.makerIdeo);
            if (delta == 0) return false;
            delta = comp.ChargeVisit(v.Faction, delta);
            if (delta == 0) return false;
            Trace(v.LabelShort + " of " + v.Faction.Name + " reads " + m.def.defName.Replace("RM_Graffiti_", "") + "@" + m.Position + ": goodwill " + delta);
            HistoryEventDef reason = delta > 0 ? RMGraffitiDefOf.RM_Graffiti_SharedSign : RMGraffitiDefOf.RM_Graffiti_WallInsult;
            v.Faction.TryAffectGoodwillWith(Faction.OfPlayer, delta, canSendMessage: true, canSendHostilityLetter: true, reason, new GlobalTargetInfo(v));
            Say(v, delta > 0 ? "A good sign, that." : "So that's what they think of us.", delta > 0 ? Tone.Warm : Tone.Angry);
            if (delta <= -5 && RM_GraffitiSettings.socialMessagesEnabled)
            {
                Tell(v.LabelShort + " of " + v.Faction.Name + " read the insult on your wall.", WallTarget(m), MessageTypeDefOf.NegativeEvent);
            }
            return true;
        }

        // ---------------------------------------------------------------- who paints what

        /// <summary>What this hand wants to say, if it wants to say anything about anyone: a mark def and who it's about. Null: it paints a plain mark from the pool.</summary>
        internal static ThingDef SocialMark(Pawn painter, bool spree, float room, out Pawn subject)
        {
            subject = null;
            if (!RM_GraffitiSettings.socialEnabled || painter.relations == null || painter.Map == null) return null;
            Pawn worst = null, beloved = null;
            int worstOpinion = 0, bestOpinion = 0;
            IReadOnlyList<Pawn> colonists = painter.Map.mapPawns.FreeColonistsSpawned.ToList();   // a copy: reading opinions can refill the game's cached list under us
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn c = colonists[i];
                if (c == painter) continue;
                int op = painter.relations.OpinionOf(c);
                // Nobody paints a mockery of a child; a child can still be loved.
                if (op < worstOpinion && c.DevelopmentalStage.Adult()) { worstOpinion = op; worst = c; }
                bool lover = LovePartnerRelationUtility.LovePartnerRelationExists(painter, c);
                if ((lover ? 100 : op) > bestOpinion) { bestOpinion = lover ? 100 : op; beloved = c; }
            }
            if (bestOpinion < RM_GraffitiKernel.CloseOpinion) beloved = null;
            Pawn mourned = Mourned(painter);
            bool kind = painter.story?.traits?.HasTrait(TraitDefOf.Kind) ?? false;
            RM_Meaning wants = RM_GraffitiKernel.WantsToPaint(spree, kind, worstOpinion, worst != null, beloved != null, mourned != null, Rand.Value);
            ThingDef def = null;
            switch (wants)
            {
                case RM_Meaning.Mockery: def = RMGraffitiDefOf.RM_Graffiti_Mockery; subject = worst; break;
                case RM_Meaning.Tribute: def = RMGraffitiDefOf.RM_Graffiti_Tribute; subject = beloved; break;
                case RM_Meaning.Memorial: def = RMGraffitiDefOf.RM_Graffiti_Memorial; subject = mourned; break;
            }
            if (def == null || GraffitiPool.WidthOf(def) > room || AlreadySaid(painter.Map, def, subject, painter) || !GraffitiPool.PainterMayPaint(def, painter))
            {
                subject = null;
                return null;
            }
            return def;
        }

        /// <summary>What a hand that set out to paint about this person paints when it gets to the wall, read off how it feels about them now:
        /// a memorial for the dead, a mockery for someone it dislikes, a tribute otherwise. Null if the moment has passed.</summary>
        internal static ThingDef MeaningFor(Pawn painter, Pawn subject)
        {
            if (!RM_GraffitiSettings.socialEnabled || subject == null || painter.relations == null) return null;
            ThingDef def = subject.Dead ? RMGraffitiDefOf.RM_Graffiti_Memorial
                : painter.relations.OpinionOf(subject) < 0 ? RMGraffitiDefOf.RM_Graffiti_Mockery : RMGraffitiDefOf.RM_Graffiti_Tribute;
            bool kind = painter.story?.traits?.HasTrait(TraitDefOf.Kind) ?? false;
            if (RM_GraffitiKernel.RefusesToPaint(def.GetModExtension<ModExtension_Graffiti>()?.meaning ?? RM_Meaning.None, kind)) return null;
            return AlreadySaid(painter.Map, def, subject, painter) ? null : def;
        }

        /// <summary>Grieving someone and not yet painted them a memorial that still stands.</summary>
        internal static bool OwesMemorial(Pawn p)
        {
            if (!RM_GraffitiSettings.socialEnabled || p?.Map == null) return false;
            Pawn dead = Mourned(p);
            return dead != null && !AlreadySaid(p.Map, RMGraffitiDefOf.RM_Graffiti_Memorial, dead, p);
        }

        /// <summary>A hand doesn't say the same thing about the same person twice while the first still stands.</summary>
        private static bool AlreadySaid(Map map, ThingDef def, Pawn subject, Pawn painter)
        {
            // Said lately, even if it's gone from the wall since.
            if (def == RMGraffitiDefOf.RM_Graffiti_Mockery && GameComponent_Graffiti.Get?.MockeryDue(painter, subject) == false) return true;
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(map);
            if (comp == null) return false;
            for (int i = 0; i < comp.marks.Count; i++)
            {
                Filth_Mark m = comp.marks[i];
                // A save from before pass 10 lost a dead subject's reference and kept only the name.
                bool about = m.subject == subject || (m.subject == null && subject != null && m.subjectName == subject.LabelShort);
                if (m.def == def && about && m.maker == painter && !m.defaced) return true;
            }
            return false;
        }

        /// <summary>Someone this pawn still grieves, off their own memories: a dead friend (the game's own "died" thought for someone they
        /// thought well of) or kin or a lover (the relation's own "died" thought). The "colonist died" every colonist gets is not grief: live
        /// 2026-11-07, Kinso, who had only that for Mo (-3), painted Mo a memorial and took +5.7 from it.</summary>
        internal static Pawn Mourned(Pawn p)
        {
            List<Thought_Memory> memories = p.needs?.mood?.thoughts?.memories?.Memories;
            if (memories == null) return null;
            for (int i = 0; i < memories.Count; i++)
            {
                Thought_Memory t = memories[i];
                if (t.otherPawn != null && t.otherPawn.Dead && t.otherPawn.RaceProps.Humanlike && !(t is Thought_MemorySocial) && t.MoodOffset() < 0f
                    && (t.def == ThoughtDefOf.PawnWithGoodOpinionDied || p.GetRelations(t.otherPawn).Any()))
                {
                    return t.otherPawn;
                }
            }
            return null;
        }

        /// <summary>Owner, card 2026-11-07: a memorial comes from someone "actually grieving". Does this pawn grieve that one?</summary>
        internal static bool Grieves(Pawn p, Pawn dead)
        {
            if (p == null || dead == null || !dead.Dead) return false;
            List<Thought_Memory> memories = p.needs?.mood?.thoughts?.memories?.Memories;
            if (memories == null) return false;
            for (int i = 0; i < memories.Count; i++)
            {
                Thought_Memory t = memories[i];
                if (t.otherPawn == dead && !(t is Thought_MemorySocial) && !GraffitiTemperament.IsOurs(t.def) && t.MoodOffset() < 0f) return true;
            }
            return false;
        }

        // ---------------------------------------------------------------- what happens next

        /// <summary>A mark is finished: the painter's own feeling, the player's notice. Owner, card 2026-11-07: "All mark makers get a small mood
        /// buff for having made it", and a memorial "helps them feel better".</summary>
        internal static void Notify_Painted(Filth_Mark mark, Pawn painter, string over = null)
        {
            if (painter == null || !RM_GraffitiSettings.socialEnabled) return;
            RM_Meaning meaning = mark.Meaning;
            Trace(painter.LabelShort + " painted " + mark.def.defName.Replace("RM_Graffiti_", "") + "@" + mark.Position + " (" + (mark.CraftLabel ?? "-") + ")"
                + (mark.subject != null ? " about " + mark.SubjectName : "") + (mark.targetFaction != null ? " insulting " + mark.targetFaction.Name : ""));
            if (painter.Faction == Faction.OfPlayer)
            {
                if (mark.subject != null && meaning == RM_Meaning.Mockery) GraffitiTemperament.Give(painter, T.RM_Graffiti_StuckItToThem, mark.subject);
                if (mark.subject != null && meaning == RM_Meaning.Mockery) GameComponent_Graffiti.Get?.NoteMocked(painter, mark.subject);
                else if (mark.subject != null && meaning == RM_Meaning.Memorial && Grieves(painter, mark.subject)) EaseGrief(painter, mark.subject);
                else GraffitiTemperament.Give(painter, T.RM_Graffiti_LeftMyMark, null);
                if (meaning == RM_Meaning.Tribute && mark.subject != null) mark.NoteValued(mark.subject);
            }
            if (mark.subject != null || meaning == RM_Meaning.Insult)
            {
                string what = meaning == RM_Meaning.Mockery ? " painted a mockery of " + mark.SubjectName
                    : meaning == RM_Meaning.Tribute ? " painted a tribute to " + mark.SubjectName
                    : meaning == RM_Meaning.Memorial ? " painted a memorial to " + mark.SubjectName
                    : " painted an insult to " + (mark.targetFaction?.Name ?? "a faction");
                what += " on the wall" + (over != null ? ", over " + over + "'s work." : ".");
                Log(painter, mark.subject, painter.LabelShort + what);
                if (RM_GraffitiSettings.socialMessagesEnabled && painter.Faction == Faction.OfPlayer)
                {
                    Tell(painter.LabelShort + what, WallTarget(mark), MessageTypeDefOf.SilentInput, historical: true);
                }
            }
            if (painter.Faction != null && painter.Faction.HostileTo(Faction.OfPlayer) && RM_GraffitiSettings.socialMessagesEnabled
                && MapComponent_GraffitiSocial.For(mark.Map)?.RaidMessageDue() == true)
            {
                Tell(painter.Faction.Name + " left their mark on your walls on the way out.", WallTarget(mark), MessageTypeDefOf.NegativeEvent);
            }
        }

        /// <summary>Painting the memorial helped: a lift of its own, and the grief itself wears off sooner.</summary>
        private static void EaseGrief(Pawn painter, Pawn dead)
        {
            GraffitiTemperament.Give(painter, T.RM_Graffiti_GriefEased, dead);
            List<Thought_Memory> memories = painter.needs?.mood?.thoughts?.memories?.Memories;
            if (memories == null) return;
            foreach (Thought_Memory t in memories)
            {
                if (t.otherPawn == dead && !(t is Thought_MemorySocial) && !GraffitiTemperament.IsOurs(t.def) && t.MoodOffset() < 0f && !t.permanent)
                {
                    t.age += (int)((t.DurationTicks - t.age) * GriefEasedShare);
                }
            }
        }

        private const float GriefEasedShare = 0.35f;

        /// <summary>How much this pawn still grieves that one (absolute): the game's own sad memories about the dead pawn, not ours.</summary>
        internal static float GriefFor(Pawn p, Pawn dead)
        {
            if (p == null || dead == null || !dead.Dead) return 0f;
            List<Thought_Memory> memories = p.needs?.mood?.thoughts?.memories?.Memories;
            if (memories == null) return 0f;
            float grief = 0f;
            for (int i = 0; i < memories.Count; i++)
            {
                Thought_Memory t = memories[i];
                if (t.otherPawn != dead || t is Thought_MemorySocial || GraffitiTemperament.IsOurs(t.def)) continue;
                float o = t.MoodOffset();
                if (o < 0f) grief -= o;
            }
            return grief;
        }

        /// <summary>Someone painted over this mark. Its maker takes it personally, and may do something about it, by the same table as anything else.</summary>
        internal static void Notify_WentOver(Filth_Mark under, Pawn by, bool quiet = false, bool lastWord = false)
        {
            Pawn maker = under.maker;
            if (!RM_GraffitiSettings.socialEnabled || maker == null || maker == by || maker.Dead || maker.needs?.mood == null || maker.Faction != Faction.OfPlayer) return;
            if (GraffitiTemperament.IsNumb(maker)) return;
            GraffitiTemperament.Give(maker, T.RM_Graffiti_WorkDestroyed, by);
            if (by != null) GraffitiTemperament.Give(maker, T.RM_Graffiti_DestroyedMyWork, by);
            Log(maker, by, (by?.LabelShort ?? "Someone") + " painted over " + maker.LabelShort + "'s work.");
            if (RM_GraffitiSettings.socialMessagesEnabled && maker.Spawned && !quiet)
            {
                Tell((by?.LabelShort ?? "Someone") + " painted over " + maker.LabelShort + "'s work.", WallTarget(under), MessageTypeDefOf.SilentInput);
            }
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(maker.Map);
            if (comp != null && by != null && maker.Spawned && Answers(maker))
            {
                bool here = by.Spawned && by.Map == maker.Map && !by.Dead;
                // Gone under a reply: that was the last word, and there's no painting back at it.
                RM_Answer answer = RM_GraffitiKernel.AnswerOf(RM_Reaction.WorkDestroyed, GraffitiTemperament.IsHot(maker), !maker.WorkTagIsDisabled(WorkTags.Violent), here,
                    CanReplyInPaint(maker) && !lastWord && GameComponent_Graffiti.Get?.MockeryDue(maker, by) != false, Rand.Value, GraffitiTemperament.Of(maker).lean);
                comp.AddGrudge(maker, null, by, answer);
            }
        }

        /// <summary>A mark was wiped or crossed out by this pawn: their satisfaction, its maker's anger if it was somebody's, the thanks of
        /// whoever it mocked (owner's pick: cleaning a mockery bonds subject and cleaner), and the hurt of anyone who held it dear, if it went
        /// in a cleaning fit.</summary>
        /// <param name="chore">Scrubbed as work, not as a statement: the player's scrub order or the cleaning rounds. A chore says nothing aloud
        /// and logs only the first of a cleaner's scrubs of one painter's work in a day (live 2026-11-08: one ordered cleanup of a spree
        /// stacked six "There. Gone." motes and wrote twenty log lines). An enemy mark, a rescue or a fit is still told in full.</param>
        internal static void Notify_Answered(Filth_Mark mark, Pawn by, bool crossedOut, bool fit = false, bool chore = false)
        {
            if (!RM_GraffitiSettings.socialEnabled || by == null) return;
            Pawn maker = mark.maker;
            bool enemy = mark.makerFaction != null && by.Faction != null && mark.makerFaction != by.Faction && mark.makerFaction.HostileTo(by.Faction);
            if (enemy) GraffitiTemperament.Give(by, T.RM_Graffiti_Reclaimed, null);
            else if (mark.Meaning == RM_Meaning.Mockery || mark.Meaning == RM_Meaning.Insult) GraffitiTemperament.Give(by, T.RM_Graffiti_Answered, null);
            if (maker != null && maker != by && !maker.Dead && maker.needs?.mood != null && maker.Faction == Faction.OfPlayer)
            {
                GraffitiTemperament.Give(maker, T.RM_Graffiti_Scrubbed, by);
                GraffitiTemperament.Give(maker, T.RM_Graffiti_ScrubbedMyWork, by);
            }
            Pawn subject = mark.subject;
            bool rescued = mark.Meaning == RM_Meaning.Mockery && subject != null && subject != by && subject != maker && !subject.Dead && !crossedOut;
            if (rescued)
            {
                GraffitiTemperament.Give(subject, T.RM_Graffiti_WipedItAway, by);
                GraffitiTemperament.Give(subject, T.RM_Graffiti_WipedItAwayMood, by);
            }
            if (fit && !crossedOut && by.Map != null)
            {
                foreach (Pawn p in by.Map.mapPawns.FreeColonistsSpawned.ToList())
                {
                    if (p != by && p != maker && p != (mark.Meaning == RM_Meaning.Mockery ? subject : null) && mark.ValuedBy(p))
                    {
                        GraffitiTemperament.Give(p, T.RM_Graffiti_ScrubbedWhatIDear, by);
                        GraffitiTemperament.Give(p, T.RM_Graffiti_ScrubbedWhatIDearMood, by);
                    }
                }
            }
            string verb = crossedOut ? " crossed out " : " scrubbed away ";
            string whose = enemy ? "the enemy's mark" : (maker != null && maker != by ? maker.LabelShort + "'s mark" : "a mark");
            string about = subject != null && subject != by ? " about " + mark.SubjectName : "";
            string text = by.LabelShort + verb + whose + about + "." + (rescued ? " " + mark.SubjectName + " won't forget that." : "");
            Trace(text + " @" + mark.Position + (fit ? " (in a cleaning fit)" : chore ? " (a chore)" : ""));
            bool story = !chore || enemy || rescued || fit;
            if (story || FirstChoreToday(by, maker)) Log(by, rescued ? subject : maker, text);
            if (story) Say(by, crossedOut ? "Not on my wall." : "There. Gone.", Tone.Neutral);
            // In a cleaning fit, only the first scrub is told; the fit's end sends the count (MentalState_GraffitiCompulsiveClean.PostEnd).
            bool tell = enemy || subject != null || fit;
            if (fit && by.MentalState is MentalState_GraffitiCompulsiveClean fitState)
            {
                tell = !fitState.told;
                fitState.told = true;
            }
            if (RM_GraffitiSettings.socialMessagesEnabled && by.Faction == Faction.OfPlayer && tell)
            {
                Tell(text, WallTarget(mark), MessageTypeDefOf.SilentInput);
            }
        }

        private static readonly Dictionary<long, int> lastChoreLog = new Dictionary<long, int>();

        /// <summary>The first chore scrub of this painter's work by this cleaner in a day, so a cleanup is one log line, not thirty.</summary>
        private static bool FirstChoreToday(Pawn by, Pawn maker)
        {
            long key = ((long)by.thingIDNumber << 32) | (uint)(maker?.thingIDNumber ?? 0);
            int now = Find.TickManager.TicksGame;
            if (lastChoreLog.TryGetValue(key, out int last) && now - last < GenDate.TicksPerDay && now >= last) return false;
            lastChoreLog[key] = now;
            return true;
        }

        /// <summary>A mockery is off the wall (scrubbed, crossed out, painted over, its wall gone): its subject's humiliation over it eases at
        /// once to its "gone now" stage, half as sharp, and lasts a day at most from here. Unless the same painter's other mockery of them still
        /// stands. GPT broaden, pass 12: a player who has it cleaned should see that help the person it hurt, not the same -13 for three days.</summary>
        internal static void Notify_MockeryGone(Filth_Mark mark)
        {
            Pawn subject = mark.subject, maker = mark.maker;
            if (mark.Meaning != RM_Meaning.Mockery || subject?.needs?.mood == null || subject.Dead || T.RM_Graffiti_Humiliated == null) return;
            MapComponent_GraffitiSocial comp = mark.Map != null ? MapComponent_GraffitiSocial.For(mark.Map) : null;
            if (comp != null && comp.marks.Any(o => o != mark && !o.defaced && o.Meaning == RM_Meaning.Mockery && o.subject == subject && o.maker == maker)) return;
            foreach (Thought_Memory m in subject.needs.mood.thoughts.memories.Memories)
            {
                if (m.def != T.RM_Graffiti_Humiliated || m.otherPawn != maker || m.CurStageIndex != 0) continue;
                m.SetForcedStage(1);
                m.age = System.Math.Max(m.age, m.DurationTicks - GenDate.TicksPerDay);
                Trace(subject.LabelShort + "'s humiliation over " + (maker?.LabelShort ?? "-") + "'s mockery eases: it's off the wall");
            }
        }

        /// <summary>A mark wiped by the cleaning job (the player's order, or the rounds): the same story, with whoever held the rag.</summary>
        internal static void Notify_Cleaned(Filth_Mark mark)
        {
            Map map = mark.Map;
            if (map == null) return;
            IReadOnlyList<Pawn> colonists = map.mapPawns.FreeColonistsSpawned.ToList();
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn p = colonists[i];
                if (p.CurJobDef == JobDefOf.Clean && p.CurJob != null && p.CurJob.targetA.Thing == mark)
                {
                    Notify_Answered(mark, p, crossedOut: false, chore: true);
                    return;
                }
            }
            Trace(mark.def.defName.Replace("RM_Graffiti_", "") + "@" + mark.Position + " by " + (mark.maker?.LabelShort ?? "-") + " is gone, and no cleaner held the rag");
        }

        /// <summary>Owner, card 2026-11-07: "if a person hates the subject, they will refuse to clean the insult". Null if they'd clean it.</summary>
        internal static string RefusesToClean(Pawn p, Filth_Mark mark)
        {
            if (mark == null || mark.Meaning != RM_Meaning.Mockery || mark.subject == null || mark.subject == p || p.relations == null) return null;
            if (GraffitiTemperament.IsNumb(p) || p.InMentalState) return null;
            return p.relations.OpinionOf(mark.subject) <= RM_GraffitiKernel.HatedOpinion ? p.LabelShort + " won't clean up an insult to " + mark.SubjectName + "." : null;
        }

        /// <summary>Had it out with the painter. Owner's pick, "Scale it with temper": whether it comes to blows is rolled on the confronter's own
        /// temper (the game's insult chance for him, times the table's column), at most once in 15 days for the whole game, and never past the
        /// game's own bars on who may fight. The message names both and the wall.</summary>
        internal static void Notify_Confronted(Pawn by, Pawn painter, Filth_Mark about)
        {
            if (!RM_GraffitiSettings.socialEnabled) return;
            GraffitiTemperament.Give(by, T.RM_Graffiti_Answered, null);
            float chance = FightChance(by, painter);
            GameComponent_Graffiti game = GameComponent_Graffiti.Get;
            bool fight = chance > 0f && game != null && game.FightDue && Rand.Value < chance;
            Trace(by.LabelShort + " confronts " + painter.LabelShort + ": fight chance " + chance.ToString("0.00") + (game != null && !game.FightDue ? " (a fight too recent)" : "") + " -> " + (fight ? "BLOWS" : "words"));
            // Live 2026-11-07: "about what Kinso painted about someone", over a plain tag that was about nobody.
            string where = about == null ? " what's on the wall"
                : about.subject != null || !about.subjectName.NullOrEmpty() ? " what " + painter.LabelShort + " painted about " + about.SubjectName
                : about.maker == painter ? " " + painter.LabelShort + "'s " + about.def.label + " on the wall"
                : " what's on the wall";
            if (fight)
            {
                game.lastFight = Find.TickManager.TicksGame;
                // StartSocialFight's own message points at the painter alone and says nothing of the wall (live pass 12: a fight the
                // player was never shown the cause of). Start the same fight here and send our own message, at both of them and the wall.
                painter.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.SocialFighting, null, forced: false, forceWake: false, causedByMood: false, otherPawn: by);
                by.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.SocialFighting, null, forced: false, forceWake: false, causedByMood: false, otherPawn: painter);
                TaleRecorder.RecordTale(TaleDefOf.SocialFight, painter, by);
                string blows = by.LabelShort + " confronted " + painter.LabelShort + " about" + where + ", and it came to blows.";
                Log(by, painter, blows);
                if (PawnUtility.ShouldSendNotificationAbout(by) || PawnUtility.ShouldSendNotificationAbout(painter))
                {
                    Tell(blows, about != null ? new LookTargets(new GlobalTargetInfo(by), new GlobalTargetInfo(painter), WallTarget(about).PrimaryTarget) : new LookTargets(by, painter), MessageTypeDefOf.ThreatSmall);
                }
                return;
            }
            Log(by, painter, by.LabelShort + " confronted " + painter.LabelShort + " about" + where + ".");
            if (RM_GraffitiSettings.socialMessagesEnabled)
            {
                Tell(by.LabelShort + " confronted " + painter.LabelShort + " about" + where + ".", about != null ? new LookTargets(new GlobalTargetInfo(by), new GlobalTargetInfo(painter), WallTarget(about).PrimaryTarget) : new LookTargets(by, painter), MessageTypeDefOf.NeutralEvent);
            }
        }

        /// <summary>The chance this confrontation comes to blows: 0 wherever the game itself wouldn't allow a fight.</summary>
        internal static float FightChance(Pawn by, Pawn painter)
        {
            if (!DebugSettings.enableRandomMentalStates || TutorSystem.TutorialMode || by.needs?.mood == null || painter.needs?.mood == null) return 0f;
            if (!by.interactions.SocialFightPossible(painter) || !painter.interactions.SocialFightPossible(by)) return 0f;
            // The game's own check lets a drafted pawn brawl; paint must never take a soldier out of the player's hands.
            if (by.Drafted || painter.Drafted) return 0f;
            float vanilla = by.interactions.SocialFightChance(InteractionDefOf.Insult, painter);
            return RM_GraffitiKernel.ConfrontFightChance(vanilla, GraffitiTemperament.Of(by).temper);
        }

        // ---------------------------------------------------------------- small hands

        /// <summary>Owner's pick: messages point at the wall. The wall cell the mark is drawn on, not the floor in front of it or the reader.</summary>
        internal static LookTargets WallTarget(Filth_Mark m)
        {
            if (m?.Map == null) return LookTargets.Invalid;
            IntVec3 at = m.wallSide >= 0 ? m.Position + new Rot4(m.wallSide).FacingCell : m.Position;
            return new LookTargets(at, m.Map);
        }

        /// <summary>The last readings and answers, for a live proof to print (RM_GraffitiSocialProof.Ledger). Costs a string per reading.</summary>
        internal static readonly List<string> trace = new List<string>();

        internal static void Trace(string line)
        {
            trace.Add(Find.TickManager.TicksGame + " " + line);
            if (trace.Count > 60) trace.RemoveAt(0);
        }

        private static void Say(Pawn p, string line, Color tone)
        {
            if (line == null || !p.Spawned || !RM_GraffitiSettings.socialMessagesEnabled) return;
            MoteMaker.ThrowText(p.DrawPos + new Vector3(0f, 0f, 0.6f), p.Map, line, tone, 4f);
        }

        private static void Log(Pawn a, Pawn b, string text)
        {
            if (a == null || Find.PlayLog == null) return;
            Find.PlayLog.Add(new PlayLogEntry_Graffiti(a, b, text));
        }

        private static class Tone
        {
            public static readonly Color Angry = new Color(0.95f, 0.45f, 0.35f), Warm = new Color(0.65f, 0.9f, 0.6f), Neutral = new Color(0.85f, 0.85f, 0.8f);
        }

        [DefOf]
        internal static class T
        {
            public static ThoughtDef RM_Graffiti_Humiliated, RM_Graffiti_PaintedMe, RM_Graffiti_ShruggedOff, RM_Graffiti_FriendMocked, RM_Graffiti_MockedMyFriend, RM_Graffiti_EnjoyedIt,
                RM_Graffiti_SaidItForMe, RM_Graffiti_EnjoyedInsult, RM_Graffiti_WhatTheWallSays, RM_Graffiti_Cruel, RM_Graffiti_Honored, RM_Graffiti_HonoredMe, RM_Graffiti_JealousOfWall,
                RM_Graffiti_PaintedSomeoneElse, RM_Graffiti_HonoredMyEnemy, RM_Graffiti_Warmed, RM_Graffiti_Mourning, RM_Graffiti_Remembered, RM_Graffiti_Amused, RM_Graffiti_MovedByPiece,
                RM_Graffiti_Artist, RM_Graffiti_Uplifted, RM_Graffiti_Faithful, RM_Graffiti_Offended, RM_Graffiti_Heretic, RM_Graffiti_RivalHandMood, RM_Graffiti_RivalHand, RM_Graffiti_FriendHand,
                RM_Graffiti_Defiant, RM_Graffiti_WorkDestroyed, RM_Graffiti_DestroyedMyWork, RM_Graffiti_Scrubbed, RM_Graffiti_ScrubbedMyWork, RM_Graffiti_LeftMyMark,
                RM_Graffiti_StuckItToThem, RM_Graffiti_Answered, RM_Graffiti_Reclaimed, RM_Graffiti_UglyMark, RM_Graffiti_FineArt, RM_Graffiti_Mess, RM_Graffiti_ScrubbedWhatIDear,
                RM_Graffiti_ScrubbedWhatIDearMood, RM_Graffiti_WipedItAway, RM_Graffiti_WipedItAwayMood, RM_Graffiti_GriefEased;

            static T()
            {
                DefOfHelper.EnsureInitializedInCtor(typeof(T));
            }
        }
    }

    /// <summary>A line in the pawns' social logs: what happened at the wall, naming whoever it named.</summary>
    public class PlayLogEntry_Graffiti : LogEntry
    {
        private Pawn a, b;
        private string text;

        public PlayLogEntry_Graffiti()
        {
        }

        public PlayLogEntry_Graffiti(Pawn a, Pawn b, string text)
        {
            this.a = a;
            this.b = b;
            this.text = text;
        }

        public override bool Concerns(Thing t) { return t == a || t == b; }

        public override IEnumerable<Thing> GetConcerns()
        {
            if (a != null) yield return a;
            if (b != null) yield return b;
        }

        public override Texture2D IconFromPOV(Thing pov) { return null; }

        protected override string ToGameStringFromPOV_Worker(Thing pov, bool forceLog) { return text; }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref a, "a", saveDestroyedThings: true);
            Scribe_References.Look(ref b, "b", saveDestroyedThings: true);
            Scribe_Values.Look(ref text, "text");
        }
    }

    /// <summary>The colony's unease at enemy marks left standing in its Home area, wherever a colonist happens to be.</summary>
    public class ThoughtWorker_EnemyClaim : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            // Numb (a psychopath, or any temperament row that feels nothing): no line at all. Live 2026-11-07 the multiplier alone left Toni
            // the psychopath a "+0 Enemy marks on our walls" in the needs tab, which reads as a bug.
            if (!RM_GraffitiSettings.socialEnabled || p.Map == null || !p.IsColonist || GraffitiTemperament.IsNumb(p)) return false;
            int stage = RM_GraffitiKernel.TerritoryStage(MapComponent_GraffitiSocial.For(p.Map)?.EnemyMarks(p.Faction) ?? 0);
            return stage < 0 ? ThoughtState.Inactive : ThoughtState.ActiveAtStage(stage);
        }

        public override float MoodMultiplier(Pawn p)
        {
            RM_Temper t = GraffitiTemperament.Of(p);
            return t.numb ? 0f : t.bad;
        }
    }

    /// <summary>A memorial's comfort: painting one (RM_Graffiti_GriefEased) or standing at one (RM_Graffiti_Mourning). Owner, card 2026-11-07:
    /// a memorial should soften grief, never turn it into a gain. So, read live: all of these about one dead pawn add up to at most half of
    /// the grief the pawn still feels for them (RM_GraffitiKernel.EaseShare), and when the grief is over, so is the comfort.</summary>
    public class Thought_GriefEase : Thought_Memory
    {
        internal static bool Eases(ThoughtDef def)
        {
            return def != null && (def == GraffitiSocial.T.RM_Graffiti_GriefEased || def == GraffitiSocial.T.RM_Graffiti_Mourning);
        }

        private float Raw => base.MoodOffset();

        public override float MoodOffset()
        {
            float raw = Raw;
            if (raw <= 0f || otherPawn == null) return raw;
            float grief = GraffitiSocial.GriefFor(pawn, otherPawn);
            float before = 0f;
            List<Thought_Memory> memories = pawn.needs?.mood?.thoughts?.memories?.Memories;
            if (memories == null) return 0f;
            for (int i = 0; i < memories.Count; i++)
            {
                Thought_Memory m = memories[i];
                if (m == this) break;
                if (m is Thought_GriefEase e && e.otherPawn == otherPawn) before += RM_GraffitiKernel.EaseShare(grief, e.Raw, before);
            }
            return RM_GraffitiKernel.EaseShare(grief, raw, before);
        }

        public override bool ShouldDiscard => base.ShouldDiscard || otherPawn == null || GraffitiSocial.GriefFor(pawn, otherPawn) <= 0f;
    }
}
