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

        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "pawn");
            Scribe_References.Look(ref mark, "mark");
            Scribe_References.Look(ref against, "against");
            Scribe_Values.Look(ref answer, "answer");
            Scribe_Values.Look(ref notBefore, "notBefore");
            Scribe_Values.Look(ref until, "until");
        }
    }

    // Owner, 2026-11-07: "did you test the social implications of the mod? It's more than just art display." The map's walls as people read
    // them: who sees which mark (a walk past it, in sight, in the same room), what it does to them, and who means to do something about it.
    // The marks register themselves on spawn, so this needs no scan of the map's things; only the grudges are saved, the marks keep their own readers.
    public class MapComponent_GraffitiSocial : MapComponent
    {
        private const int SightInterval = 180;

        internal readonly List<Filth_Mark> marks = new List<Filth_Mark>();
        private List<RM_Grudge> grudges = new List<RM_Grudge>();
        private Dictionary<int, int> lastAnswered = new Dictionary<int, int>();
        private int lastRaidMessage = -99999;

        public MapComponent_GraffitiSocial(Map map) : base(map)
        {
        }

        public static MapComponent_GraffitiSocial For(Map map)
        {
            return map?.GetComponent<MapComponent_GraffitiSocial>();
        }

        public IEnumerable<RM_Grudge> Grudges => grudges;

        public override void MapComponentTick()
        {
            if (!RM_GraffitiSettings.socialEnabled || marks.Count == 0)
            {
                return;
            }
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

        /// <summary>The enemy marks standing on this map's walls, not crossed out. What the colony's territory thought counts.</summary>
        public int EnemyMarks(Faction of)
        {
            int n = 0;
            for (int i = 0; i < marks.Count; i++)
            {
                Filth_Mark m = marks[i];
                if (!m.defaced && m.makerFaction != null && m.makerFaction != of && m.makerFaction.HostileTo(of)) n++;
            }
            return n;
        }

        internal void AddGrudge(Pawn pawn, Filth_Mark mark, Pawn against, RM_Answer answer)
        {
            if (answer == RM_Answer.None || pawn == null) return;
            int now = Find.TickManager.TicksGame;
            lastAnswered.TryGetValue(pawn.thingIDNumber, out int last);
            if (last > 0 && now - last < RM_GraffitiKernel.AnswerCooldownTicks) return;
            foreach (RM_Grudge g in grudges)
            {
                if (g.pawn == pawn) return;
            }
            grudges.Add(new RM_Grudge { pawn = pawn, mark = mark, against = against, answer = answer, notBefore = now + Rand.Range(240, 1200), until = now + RM_GraffitiKernel.GrudgeExpiryTicks });
        }

        /// <summary>The grudge this pawn could act on now, with the dead ones dropped.</summary>
        internal RM_Grudge GrudgeOf(Pawn pawn)
        {
            int now = Find.TickManager.TicksGame;
            for (int i = grudges.Count - 1; i >= 0; i--)
            {
                RM_Grudge g = grudges[i];
                bool dead = g.pawn == null || g.pawn.Dead || now > g.until
                    || ((g.answer == RM_Answer.Scrub || g.answer == RM_Answer.Deface) && (g.mark == null || g.mark.Destroyed || g.mark.defaced))
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

        internal void Settle(RM_Grudge g)
        {
            grudges.Remove(g);
            if (g.pawn != null) lastAnswered[g.pawn.thingIDNumber] = Find.TickManager.TicksGame;
        }

        internal bool RaidMessageDue()
        {
            int now = Find.TickManager.TicksGame;
            if (now - lastRaidMessage < 5000) return false;
            lastRaidMessage = now;
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref grudges, "rmGrudges", LookMode.Deep);
            Scribe_Collections.Look(ref lastAnswered, "rmLastAnswered", LookMode.Value, LookMode.Value);
            Scribe_Values.Look(ref lastRaidMessage, "rmLastRaidMessage", -99999);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                grudges = grudges ?? new List<RM_Grudge>();
                lastAnswered = lastAnswered ?? new Dictionary<int, int>();
                grudges.RemoveAll(g => g == null || g.pawn == null);
            }
        }
    }

    public static class GraffitiSocial
    {
        // ---------------------------------------------------------------- reading the walls

        internal static void Look(Pawn viewer, MapComponent_GraffitiSocial comp)
        {
            if (!viewer.Spawned || viewer.Downed || !viewer.Awake() || viewer.needs?.mood == null) return;
            if (viewer.health.capacities.GetLevel(PawnCapacityDefOf.Sight) < 0.3f) return;
            Map map = viewer.Map;
            Room room = viewer.GetRoom();
            int now = Find.TickManager.TicksGame;
            bool ours = viewer.Faction == Faction.OfPlayer || viewer.IsPrisonerOfColony;
            bool visitor = !ours && viewer.Faction != null && !viewer.Faction.HostileTo(Faction.OfPlayer);
            if (!ours && !visitor) return;
            for (int i = 0; i < comp.marks.Count; i++)
            {
                Filth_Mark mark = comp.marks[i];
                if ((mark.Position - viewer.Position).LengthHorizontalSquared > RM_GraffitiKernel.SightRadiusSq) continue;
                if (mark.Position.Fogged(map) || mark.Position.GetRoom(map) != room) continue;
                if (ours && !mark.ReadyToBeRead(viewer, now)) continue;
                if (visitor && mark.FactionHasRead(viewer.Faction)) continue;
                if (!GenSight.LineOfSight(viewer.Position, mark.Position, map, skipFirstCell: true)) continue;
                if (visitor)
                {
                    if (VisitorReads(viewer, mark)) return;
                    continue;
                }
                mark.NoteRead(viewer, now);
                if (Reads(viewer, mark, comp)) return;   // one thing at a time: the next look finds the next mark
            }
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
                hot = IsHot(traits),
                psychopath = traits != null && traits.HasTrait(TraitDefOf.Psychopath),
                hasIdeo = v.Ideo != null,
                makerHasIdeo = m.makerIdeo != null,
                sameIdeoAsMaker = v.Ideo != null && v.Ideo == m.makerIdeo,
            };
        }

        private static bool IsHot(TraitSet traits)
        {
            return traits != null && (traits.HasTrait(TraitDefOf.Abrasive) || traits.HasTrait(TraitDefOf.Bloodlust) || traits.HasTrait(TraitDefOf.Brawler));
        }

        /// <summary>One colonist reads one mark. True if it did something to them.</summary>
        private static bool Reads(Pawn v, Filth_Mark m, MapComponent_GraffitiSocial comp)
        {
            RM_Viewer standing = StandingOf(v, m);
            if (!RM_GraffitiKernel.StillSpeaks(m.defaced, standing.isMaker)) return false;
            RM_Reaction reaction = RM_GraffitiKernel.ReactionOf(m.Meaning, standing);
            if (reaction == RM_Reaction.None) return false;
            Apply(v, m, reaction);
            m.NoteReaction(reaction);
            Pawn other = reaction == RM_Reaction.Uneasy || reaction == RM_Reaction.Defiant ? null : m.maker;
            bool goodHand = (v.skills?.GetSkill(SkillDefOf.Artistic)?.Level ?? 0) >= 5 && !v.WorkTagIsDisabled(WorkTags.Artistic);
            bool canFight = !v.WorkTagIsDisabled(WorkTags.Violent);
            bool makerHere = other != null && other.Spawned && other.Map == v.Map && !other.Dead;
            RM_Answer answer = v.IsColonist ? RM_GraffitiKernel.AnswerOf(reaction, standing.hot, canFight, makerHere, goodHand, Rand.Value) : RM_Answer.None;
            comp.AddGrudge(v, m, other, answer);
            return true;
        }

        private static void Apply(Pawn v, Filth_Mark m, RM_Reaction reaction)
        {
            Pawn maker = m.maker, subject = m.subject;
            string makerName = maker?.LabelShort ?? "someone";
            string subjectName = m.SubjectName;
            string line = null;
            string log = null;
            Color tone = Tone.Neutral;
            switch (reaction)
            {
                case RM_Reaction.Humiliated:
                    Mem(v, T.RM_Graffiti_Humiliated, maker); Mem(v, T.RM_Graffiti_PaintedMe, maker);
                    line = "Who painted that?!"; tone = Tone.Angry; log = "{0} found what {1} painted about them on the wall, and went white.";
                    break;
                case RM_Reaction.ShrugsOff:
                    Mem(v, T.RM_Graffiti_ShruggedOff, maker);
                    line = "Ha! Good likeness."; tone = Tone.Warm; log = "{0} laughed at the picture {1} painted of them.";
                    break;
                case RM_Reaction.FriendDefends:
                    Mem(v, T.RM_Graffiti_FriendMocked, subject); Mem(v, T.RM_Graffiti_MockedMyFriend, maker);
                    line = "That's " + subjectName + " up there."; tone = Tone.Angry; log = "{0} saw what {1} painted about " + subjectName + " and took it badly.";
                    break;
                case RM_Reaction.Gleeful:
                    if (subject != null) { Mem(v, T.RM_Graffiti_EnjoyedIt, subject); Mem(v, T.RM_Graffiti_SaidItForMe, maker); }
                    else Mem(v, T.RM_Graffiti_EnjoyedInsult, null);
                    line = "Ha. About time."; tone = Tone.Warm; log = "{0} grinned at what {1} put on the wall.";
                    break;
                case RM_Reaction.LostFace:
                    Mem(v, T.RM_Graffiti_WhatTheWallSays, subject);
                    line = "Is that true, about " + subjectName + "?"; tone = Tone.Neutral; log = "{0} read what {1} painted about " + subjectName + ", and it stuck.";
                    break;
                case RM_Reaction.Disapproves:
                    Mem(v, T.RM_Graffiti_Cruel, maker);
                    line = "That's cruel."; tone = Tone.Neutral; log = "{0} thought less of {1} after reading the wall.";
                    break;
                case RM_Reaction.Honored:
                    Mem(v, T.RM_Graffiti_Honored, maker); Mem(v, T.RM_Graffiti_HonoredMe, maker);
                    line = "That's... me."; tone = Tone.Warm; log = "{0} found the tribute {1} painted for them and stood looking at it.";
                    break;
                case RM_Reaction.Jealous:
                    Mem(v, T.RM_Graffiti_JealousOfWall, subject); Mem(v, T.RM_Graffiti_PaintedSomeoneElse, maker);
                    line = "Never painted ME."; tone = Tone.Angry; log = "{0} saw {1}'s tribute to " + subjectName + " and said nothing, loudly.";
                    break;
                case RM_Reaction.Scoffs:
                    Mem(v, T.RM_Graffiti_HonoredMyEnemy, maker);
                    line = "A tribute? To them?"; tone = Tone.Neutral; log = "{0} scoffed at {1}'s tribute to " + subjectName + ".";
                    break;
                case RM_Reaction.Warmed:
                    Mem(v, T.RM_Graffiti_Warmed, subject);
                    line = "Good for " + subjectName + "."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Mourning:
                    Mem(v, T.RM_Graffiti_Mourning, subject); Mem(v, T.RM_Graffiti_Remembered, maker);
                    line = "I miss " + subjectName + "."; tone = Tone.Warm; log = "{0} stopped at {1}'s memorial for " + subjectName + ".";
                    break;
                case RM_Reaction.Amused:
                    Mem(v, T.RM_Graffiti_Amused, null);
                    line = "Heh."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Moved:
                    Mem(v, T.RM_Graffiti_MovedByPiece, maker); Mem(v, T.RM_Graffiti_Artist, maker);
                    line = "Who made this?"; tone = Tone.Warm; log = "{0} stood looking at {1}'s piece on the wall.";
                    break;
                case RM_Reaction.Uplifted:
                    Mem(v, T.RM_Graffiti_Uplifted, null); Mem(v, T.RM_Graffiti_Faithful, maker);
                    line = "Our sign."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Offended:
                    Mem(v, T.RM_Graffiti_Offended, null); Mem(v, T.RM_Graffiti_Heretic, maker);
                    line = "Whose creed is that?"; tone = Tone.Angry; log = "{0} was offended by the creed {1} painted on the wall.";
                    break;
                case RM_Reaction.RivalTag:
                    Mem(v, T.RM_Graffiti_RivalHandMood, maker); Mem(v, T.RM_Graffiti_RivalHand, maker);
                    line = "Of course. " + makerName + " again."; tone = Tone.Angry; log = "{0} glared at {1}'s tag on the wall.";
                    break;
                case RM_Reaction.FriendTag:
                    Mem(v, T.RM_Graffiti_FriendHand, maker);
                    line = "That's " + makerName + "'s hand."; tone = Tone.Warm;
                    break;
                case RM_Reaction.Uneasy:
                    line = "They were here."; tone = Tone.Neutral;
                    break;
                case RM_Reaction.Defiant:
                    Mem(v, T.RM_Graffiti_Defiant, null);
                    line = "Let them come back."; tone = Tone.Angry;
                    break;
            }
            Say(v, line, tone);
            if (log != null) Log(v, maker, string.Format(log, v.LabelShort, makerName));
            if (RM_GraffitiKernel.Announces(reaction) && RM_GraffitiSettings.socialMessagesEnabled && PawnUtility.ShouldSendNotificationAbout(v))
            {
                Messages.Message(string.Format(log, v.LabelShort, makerName), new LookTargets(v), reaction == RM_Reaction.Humiliated ? MessageTypeDefOf.NegativeEvent : MessageTypeDefOf.SilentInput, historical: true);
            }
        }

        /// <summary>A visitor's faction reads a mark on the host's wall, once per mark. True if it moved anything.</summary>
        private static bool VisitorReads(Pawn v, Filth_Mark m)
        {
            m.NoteFactionRead(v.Faction);
            ModExtension_Graffiti ext = m.def.GetModExtension<ModExtension_Graffiti>();
            bool taunt = ext != null && ext.category == GraffitiCategory.Taunt;
            int delta = RM_GraffitiKernel.GoodwillOf(m.Meaning, m.targetFaction == v.Faction, taunt, v.Ideo != null && v.Ideo == m.makerIdeo);
            if (delta == 0 || m.defaced) return false;
            HistoryEventDef reason = delta > 0 ? RMGraffitiDefOf.RM_Graffiti_SharedSign : RMGraffitiDefOf.RM_Graffiti_WallInsult;
            v.Faction.TryAffectGoodwillWith(Faction.OfPlayer, delta, canSendMessage: true, canSendHostilityLetter: true, reason, new GlobalTargetInfo(v));
            Say(v, delta > 0 ? "A good sign, that." : "So that's what they think of us.", delta > 0 ? Tone.Warm : Tone.Angry);
            if (delta <= -5 && RM_GraffitiSettings.socialMessagesEnabled)
            {
                Messages.Message(v.LabelShort + " of " + v.Faction.Name + " read the insult on your wall.", new LookTargets(v), MessageTypeDefOf.NegativeEvent);
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
            IReadOnlyList<Pawn> colonists = painter.Map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn c = colonists[i];
                if (c == painter) continue;
                int op = painter.relations.OpinionOf(c);
                if (op < worstOpinion) { worstOpinion = op; worst = c; }
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
            if (def == null || GraffitiPool.WidthOf(def) > room + 0.3f || AlreadySaid(painter.Map, def, subject, painter))
            {
                subject = null;
                return null;
            }
            return def;
        }

        /// <summary>A hand doesn't say the same thing about the same person twice while the first still stands.</summary>
        private static bool AlreadySaid(Map map, ThingDef def, Pawn subject, Pawn painter)
        {
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(map);
            if (comp == null) return false;
            for (int i = 0; i < comp.marks.Count; i++)
            {
                Filth_Mark m = comp.marks[i];
                if (m.def == def && m.subject == subject && m.maker == painter && !m.defaced) return true;
            }
            return false;
        }

        /// <summary>Someone this pawn still grieves, off their own memories: a dead person with a sad thought attached.</summary>
        private static Pawn Mourned(Pawn p)
        {
            List<Thought_Memory> memories = p.needs?.mood?.thoughts?.memories?.Memories;
            if (memories == null) return null;
            for (int i = 0; i < memories.Count; i++)
            {
                Thought_Memory t = memories[i];
                if (t.otherPawn != null && t.otherPawn.Dead && t.otherPawn.RaceProps.Humanlike && !(t is Thought_MemorySocial) && t.MoodOffset() < 0f)
                {
                    return t.otherPawn;
                }
            }
            return null;
        }

        // ---------------------------------------------------------------- what happens next

        /// <summary>A mark is finished: the painter's own feeling, the player's notice.</summary>
        internal static void Notify_Painted(Filth_Mark mark, Pawn painter)
        {
            if (painter == null || !RM_GraffitiSettings.socialEnabled) return;
            RM_Meaning meaning = mark.Meaning;
            if (mark.subject != null && meaning == RM_Meaning.Mockery) Mem(painter, T.RM_Graffiti_StuckItToThem, mark.subject);
            else Mem(painter, T.RM_Graffiti_LeftMyMark, null);
            if (mark.subject != null || meaning == RM_Meaning.Insult)
            {
                string what = meaning == RM_Meaning.Mockery ? " painted a mockery of " + mark.SubjectName
                    : meaning == RM_Meaning.Tribute ? " painted a tribute to " + mark.SubjectName
                    : meaning == RM_Meaning.Memorial ? " painted a memorial to " + mark.SubjectName
                    : " painted an insult to " + (mark.targetFaction?.Name ?? "a faction");
                Log(painter, mark.subject, painter.LabelShort + what + " on the wall.");
                if (RM_GraffitiSettings.socialMessagesEnabled && painter.Faction == Faction.OfPlayer)
                {
                    Messages.Message(painter.LabelShort + what + " on the wall.", new LookTargets(mark.Position, mark.Map), MessageTypeDefOf.SilentInput, historical: true);
                }
            }
            if (painter.Faction != null && painter.Faction.HostileTo(Faction.OfPlayer) && RM_GraffitiSettings.socialMessagesEnabled
                && MapComponent_GraffitiSocial.For(mark.Map)?.RaidMessageDue() == true)
            {
                Messages.Message(painter.Faction.Name + " left their mark on your walls on the way out.", new LookTargets(mark.Position, mark.Map), MessageTypeDefOf.NegativeEvent);
            }
        }

        /// <summary>Someone painted over this mark. Its maker takes it personally, and may do something about it.</summary>
        internal static void Notify_WentOver(Filth_Mark under, Pawn by)
        {
            Pawn maker = under.maker;
            if (!RM_GraffitiSettings.socialEnabled || maker == null || maker == by || maker.Dead || maker.needs?.mood == null || maker.Faction != Faction.OfPlayer) return;
            Mem(maker, T.RM_Graffiti_WorkDestroyed, by);
            if (by != null) Mem(maker, T.RM_Graffiti_DestroyedMyWork, by);
            Log(maker, by, (by?.LabelShort ?? "Someone") + " painted over " + maker.LabelShort + "'s work.");
            if (RM_GraffitiSettings.socialMessagesEnabled && maker.Spawned)
            {
                Messages.Message((by?.LabelShort ?? "Someone") + " painted over " + maker.LabelShort + "'s work.", new LookTargets(under.Position, maker.Map), MessageTypeDefOf.SilentInput);
            }
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(maker.Map);
            if (comp != null && by != null && maker.Spawned && maker.IsColonist)
            {
                bool here = by.Spawned && by.Map == maker.Map && !by.Dead;
                bool hot = IsHot(maker.story?.traits);
                bool goodHand = (maker.skills?.GetSkill(SkillDefOf.Artistic)?.Level ?? 0) >= 5;
                comp.AddGrudge(maker, null, by, RM_GraffitiKernel.AnswerOf(RM_Reaction.WorkDestroyed, hot, !maker.WorkTagIsDisabled(WorkTags.Violent), here, goodHand, Rand.Value) == RM_Answer.Confront
                    ? RM_Answer.Confront : (goodHand && here ? RM_Answer.Reply : RM_Answer.None));
            }
        }

        /// <summary>A mark was wiped or crossed out by this pawn: their satisfaction, and its maker's anger if it was somebody's.</summary>
        internal static void Notify_Answered(Filth_Mark mark, Pawn by, bool crossedOut)
        {
            if (!RM_GraffitiSettings.socialEnabled || by == null) return;
            Pawn maker = mark.maker;
            bool enemy = mark.makerFaction != null && by.Faction != null && mark.makerFaction != by.Faction && mark.makerFaction.HostileTo(by.Faction);
            if (enemy) Mem(by, T.RM_Graffiti_Reclaimed, null);
            else if (mark.Meaning == RM_Meaning.Mockery || mark.Meaning == RM_Meaning.Insult) Mem(by, T.RM_Graffiti_Answered, null);
            if (maker != null && maker != by && !maker.Dead && maker.needs?.mood != null && maker.Faction == Faction.OfPlayer)
            {
                Mem(maker, T.RM_Graffiti_Scrubbed, by);
                Mem(maker, T.RM_Graffiti_ScrubbedMyWork, by);
            }
            string verb = crossedOut ? " crossed out " : " scrubbed away ";
            string whose = enemy ? "the enemy's mark" : (maker != null && maker != by ? maker.LabelShort + "'s mark" : "a mark");
            string about = mark.subject != null && mark.subject != by ? " about " + mark.SubjectName : "";
            Log(by, maker, by.LabelShort + verb + whose + about + ".");
            Say(by, crossedOut ? "Not on my wall." : "There. Gone.", Tone.Neutral);
            if (RM_GraffitiSettings.socialMessagesEnabled && by.Faction == Faction.OfPlayer && (enemy || mark.subject != null))
            {
                Messages.Message(by.LabelShort + verb + whose + about + ".", new LookTargets(by), MessageTypeDefOf.SilentInput);
            }
        }

        /// <summary>A mark wiped by the cleaning job (the player's order, or the rounds): the same story, with whoever held the rag.</summary>
        internal static void Notify_Cleaned(Filth_Mark mark)
        {
            Map map = mark.Map;
            if (map == null) return;
            IReadOnlyList<Pawn> colonists = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn p = colonists[i];
                if (p.CurJobDef == JobDefOf.Clean && p.CurJob != null && p.CurJob.targetA.Thing == mark)
                {
                    Notify_Answered(mark, p, crossedOut: false);
                    return;
                }
            }
        }

        /// <summary>Had it out with the painter, whether or not it came to blows.</summary>
        internal static void Notify_Confronted(Pawn by, Pawn painter)
        {
            if (!RM_GraffitiSettings.socialEnabled) return;
            Mem(by, T.RM_Graffiti_Answered, null);
            if (RM_GraffitiSettings.socialMessagesEnabled)
            {
                Messages.Message(by.LabelShort + " confronted " + painter.LabelShort + " about what's on the wall.", new LookTargets(by, painter), MessageTypeDefOf.NeutralEvent);
            }
        }

        // ---------------------------------------------------------------- small hands

        private static void Mem(Pawn p, ThoughtDef def, Pawn other)
        {
            if (def == null || p?.needs?.mood == null) return;
            if (other == null && typeof(Thought_MemorySocial).IsAssignableFrom(def.ThoughtClass)) return;
            if (other != null && other == p) return;
            p.needs.mood.thoughts.memories.TryGainMemory(def, other);
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
        private static class T
        {
            public static ThoughtDef RM_Graffiti_Humiliated, RM_Graffiti_PaintedMe, RM_Graffiti_ShruggedOff, RM_Graffiti_FriendMocked, RM_Graffiti_MockedMyFriend, RM_Graffiti_EnjoyedIt,
                RM_Graffiti_SaidItForMe, RM_Graffiti_EnjoyedInsult, RM_Graffiti_WhatTheWallSays, RM_Graffiti_Cruel, RM_Graffiti_Honored, RM_Graffiti_HonoredMe, RM_Graffiti_JealousOfWall,
                RM_Graffiti_PaintedSomeoneElse, RM_Graffiti_HonoredMyEnemy, RM_Graffiti_Warmed, RM_Graffiti_Mourning, RM_Graffiti_Remembered, RM_Graffiti_Amused, RM_Graffiti_MovedByPiece,
                RM_Graffiti_Artist, RM_Graffiti_Uplifted, RM_Graffiti_Faithful, RM_Graffiti_Offended, RM_Graffiti_Heretic, RM_Graffiti_RivalHandMood, RM_Graffiti_RivalHand, RM_Graffiti_FriendHand,
                RM_Graffiti_Defiant, RM_Graffiti_WorkDestroyed, RM_Graffiti_DestroyedMyWork, RM_Graffiti_Scrubbed, RM_Graffiti_ScrubbedMyWork, RM_Graffiti_LeftMyMark, RM_Graffiti_StuckItToThem,
                RM_Graffiti_Answered, RM_Graffiti_Reclaimed;

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

    /// <summary>The colony's unease at enemy marks left standing on its walls, wherever a colonist happens to be.</summary>
    public class ThoughtWorker_EnemyClaim : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!RM_GraffitiSettings.socialEnabled || p.Map == null || !p.IsColonist) return false;
            int stage = RM_GraffitiKernel.TerritoryStage(MapComponent_GraffitiSocial.For(p.Map)?.EnemyMarks(p.Faction) ?? 0);
            return stage < 0 ? ThoughtState.Inactive : ThoughtState.ActiveAtStage(stage);
        }
    }
}
