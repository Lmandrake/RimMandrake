using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.CathedralPass
{
    // CATHEDRAL_DESCENT_REVEAL_SITE_1 — the in-game half of the reveal (arc spec §5, card A7).
    //
    // WHEN the descent opens is the GM blackboard's (gm_blackboard_shadow.py, compute_reveal_beat_gate): VOUCHED conduct
    // posture plus the post-restore-choice story flag, never Regard alone, once. It fires RUT_CathedralDescent_Opening
    // through jawa/storyteller_fire; the def is baseChance 0, so the storyteller never rolls it. What lives here:
    //   - the one-time gate in the save (GameComponent_CathedralDescent): a second opening is refused, in game, even if
    //     the blackboard or a dev fires it again;
    //   - the quest node that sets the site down (the site's map is StructureInjectionsRUT's RUT_CathedralDescent_Site,
    //     looked up by name so this mod never hard-depends on it: absent, the opening is refused);
    //   - the escort: on the descent map every clan pawn is walked past by faction 13's machines, the pass's own
    //     exception scoped to this one map (Patch_CathedralPassHostility asks EscortApplies) and lost by any pawn that
    //     strikes one of them;
    //   - the beat at the bottom: the first clan pawn within reach of RUT_CathedralDescent_Terminus hears the address
    //     through its own speaker or comms set. The text is the prescribed fallback (the def's RUT_CathedralDescentText,
    //     linted by cathedral_arc_lint.py at stage 3); it is the whole beat with the Oracle absent. Then the reveal flag
    //     is set, once, and the quest ends in Success: the blackboard reads that ended quest (root
    //     RUT_CathedralDescent_Quest, EndedSuccess) as the reveal and moves to stage 3.
    // Nothing here writes faction, trader or codex text: the address is a dialog and a letter to the player alone.

    public static class CathedralDescentDefNames
    {
        public const string SitePart = "RUT_CathedralDescent_Site";
        public const string Terminus = "RUT_CathedralDescent_Terminus";
        public const string Quest = "RUT_CathedralDescent_Quest";
        public const string Opening = "RUT_CathedralDescent_Opening";
        public const string Address = "RUT_CathedralDescent_Address";
        public const string LogTag = "[RUT_CathedralDescent]";
    }

    /// <summary>Every player-facing string of the beat at the bottom, on its own def (RUT_CathedralDescent_Address, its own
    /// file) so cathedral_arc_lint.py --xml lints it at stage 3 apart from the stage-2 opening. Tags are the linter's text
    /// tags (label, lines, letterLabel/letterText, reportString).</summary>
    public class RUT_CathedralDescentText : Def
    {
        // label (Def's own): the address dialog's title
        public List<string> lines = new List<string>();   // the address, one dialog page each; [SPEAKER] is the channel
        public string letterLabel;                   // the letter the address leaves in the archive
        public string letterText;                    // ...and its text: the world describing behaviour (§P)
        public string reportString;                  // the one Message line when the descent's gear first hisses
    }

    /// <summary>The once-only state, in the save. opened: the way down has been set on the map. revealed: the address
    /// has been heard. Both are one-way.</summary>
    public class GameComponent_CathedralDescent : GameComponent
    {
        public bool opened;
        public int openedTick = -1;
        public bool revealed;
        public int revealedTick = -1;
        public int refusedOpenings;
        public HashSet<int> escortBroken = new HashSet<int>();   // pawn ids that struck a machine on the descent

        public GameComponent_CathedralDescent(Game game) { }

        public static GameComponent_CathedralDescent Get()
        {
            return Current.Game?.GetComponent<GameComponent_CathedralDescent>();
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref opened, "opened", false);
            Scribe_Values.Look(ref openedTick, "openedTick", -1);
            Scribe_Values.Look(ref revealed, "revealed", false);
            Scribe_Values.Look(ref revealedTick, "revealedTick", -1);
            Scribe_Values.Look(ref refusedOpenings, "refusedOpenings", 0);
            Scribe_Collections.Look(ref escortBroken, "escortBroken", LookMode.Value);
            if (escortBroken == null) escortBroken = new HashSet<int>();
        }
    }

    public static class CathedralDescent
    {
        private static SitePartDef sitePartDef;
        private static bool sitePartLooked;

        /// <summary>Looked up once (the hostility postfix asks on every mech-vs-clan check).</summary>
        public static SitePartDef SitePartDef
        {
            get
            {
                if (!sitePartLooked)
                {
                    sitePartDef = DefDatabase<SitePartDef>.GetNamedSilentFail(CathedralDescentDefNames.SitePart);
                    sitePartLooked = sitePartDef != null || DefDatabase<SitePartDef>.DefCount > 0;
                }
                return sitePartDef;
            }
        }
        public static ThingDef TerminusDef => DefDatabase<ThingDef>.GetNamedSilentFail(CathedralDescentDefNames.Terminus);
        public static QuestScriptDef QuestDef => DefDatabase<QuestScriptDef>.GetNamedSilentFail(CathedralDescentDefNames.Quest);
        public static RUT_CathedralDescentText Text => DefDatabase<RUT_CathedralDescentText>.GetNamedSilentFail(CathedralDescentDefNames.Address);

        /// <summary>Why an opening may not happen now, or null when it may. The pure gate in game: the blackboard owns
        /// the trigger set, the save owns "once".</summary>
        public static string OpeningRefusal()
        {
            if (!CathedralPassSettings.cathedralDescentEnabled) return "the descent is off in Mod Settings";
            GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
            if (st == null) return "no game";
            if (st.opened) return "the descent has already opened (tick " + st.openedTick + "); it opens once";
            if (st.revealed) return "the reveal has already been heard; it is heard once";
            if (SitePartDef == null) return CathedralDescentDefNames.SitePart + " is not loaded (StructureInjectionsRUT)";
            if (QuestDef == null) return CathedralDescentDefNames.Quest + " is not loaded";
            if (Text == null) return CathedralDescentDefNames.Address + " is not loaded";
            if (Find.AnyPlayerHomeMap == null) return "no player home map";
            if (DescentQuests().Any()) return "a " + CathedralDescentDefNames.Quest + " quest already exists; it opens once";
            return null;
        }

        /// <summary>Every descent quest in the save, ended or not (a dev "generate quest" bypasses the incident).</summary>
        public static IEnumerable<Quest> DescentQuests()
        {
            QuestScriptDef def = QuestDef;
            if (def == null || Find.QuestManager == null) yield break;
            foreach (Quest q in Find.QuestManager.QuestsListForReading)
                if (q.root == def) yield return q;
        }

        /// <summary>The descent quest whose site this map is, if any.</summary>
        public static Quest QuestOfSite(MapParent parent)
        {
            foreach (Quest q in DescentQuests())
                foreach (QuestPart part in q.PartsListForReading)
                    if (part is QuestPart_SpawnWorldObject sw && sw.worldObject == parent) return q;
            return null;
        }

        public static bool IsDescentMap(Map map)
        {
            if (!(map?.Parent is Site site) || site.parts == null) return false;
            SitePartDef def = SitePartDef;
            if (def == null) return false;
            for (int i = 0; i < site.parts.Count; i++)
                if (site.parts[i].def == def) return true;
            return false;
        }

        /// <summary>The escort (item 6's pass exception, scoped to this map and to the party): a clan pawn on the
        /// descent map, until it strikes one of the machines. Not gated on the setting: the setting decides whether the
        /// way down opens; a party already underground keeps its escort if the setting is switched off mid-walk.</summary>
        public static bool EscortApplies(Map map, Pawn holder)
        {
            if (holder == null || holder.Faction != Faction.OfPlayer || !IsDescentMap(map)) return false;
            GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
            return st == null || !st.escortBroken.Contains(holder.thingIDNumber);
        }

        public static void BreakEscort(Pawn p)
        {
            GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
            if (st != null && st.escortBroken.Add(p.thingIDNumber))
            {
                Messages.Message(EscortBrokenMessage(p.LabelShort), new LookTargets(p), MessageTypeDefOf.NegativeEvent);
            }
        }

        // the hardcoded player-facing strings, one place each, linted by selftest_cathedral_reveal_beat.py at stage 3
        public const string ListenOption = "Listen.";
        public const string CloseOption = "Go back up.";
        public static string EscortBrokenMessage(string name) => "The old sentinels no longer look away from " + name + ".";

        /// <summary>Who may hear the address: a clan colonist or one of the clan's droids/mechs, awake and on its feet.
        /// Never an animal.</summary>
        public static bool CanHear(Pawn p)
        {
            return p != null && !p.Dead && !p.Downed && p.Spawned && p.Faction == Faction.OfPlayer
                && (p.RaceProps.Humanlike || p.RaceProps.IsMechanoid) && !p.InMentalState;
        }

        /// <summary>The address fires only for a pawn that has come to the bottom: within reach of the terminus, with a
        /// clear line to it (not through rock from a side passage) and able to walk to it.</summary>
        public static bool AtTheBottom(Pawn p, Thing terminus, float radius)
        {
            if (p.Position.DistanceTo(terminus.Position) > radius) return false;
            if (!GenSight.LineOfSight(p.Position, terminus.Position, p.Map, skipFirstCell: true)) return false;
            return p.CanReach(terminus, Verse.AI.PathEndMode.Touch, Danger.Deadly);
        }

        /// <summary>Picks the tile: the Rust Cathedral tile nearest the colony; if none is painted yet (the world is
        /// painted once, at the end), the nearest open tile. The map underneath is the same either way.</summary>
        public static bool TryFindTile(out PlanetTile tile)
        {
            Map home = Find.AnyPlayerHomeMap;
            tile = PlanetTile.Invalid;
            if (home == null) return false;
            HashSet<BiomeDef> cathedral = CathedralPass.CathedralBiomes;
            bool Free(PlanetTile t) => !Find.WorldObjects.AnyWorldObjectAt(t);
            if (cathedral.Count > 0 && TileFinder.TryFindPassableTileWithTraversalDistance(home.Tile, 2, 40, out tile,
                    t => Free(t) && cathedral.Contains(Find.WorldGrid[t].PrimaryBiome), tileFinderMode: TileFinderMode.Near))
                return true;
            return TileFinder.TryFindPassableTileWithTraversalDistance(home.Tile, 2, 12, out tile, Free,
                tileFinderMode: TileFinderMode.Near);
        }

        /// <summary>Fires the beat at the bottom: dialog, letter, the flag, the quest's success. Once.</summary>
        public static bool SpeakAddress(Pawn listener, Thing terminus)
        {
            GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
            if (st == null || st.revealed) return false;
            RUT_CathedralDescentText txt = Text;
            if (txt == null || txt.lines.Count == 0)
            {
                Log.Error(CathedralDescentDefNames.LogTag + " no address text (" + CathedralDescentDefNames.Address + ")");
                return false;
            }
            Quest quest = QuestOfSite(listener.Map?.Parent);
            if (quest == null || quest.State != QuestState.Ongoing)
            {
                // the beat belongs to the quest that set this site down; without it the blackboard could never see the
                // reveal, so it is not spent here
                Log.Error(CathedralDescentDefNames.LogTag + " the address was reached but this site's quest is "
                    + (quest == null ? "missing" : quest.State.ToString()) + "; the reveal is not spent");
                return false;
            }

            string speaker = SpeakerPhrase(listener);
            List<string> pages = txt.lines.Select(l => Fill(l, speaker, listener)).ToList();
            DiaNode first = null, prev = null;
            for (int i = 0; i < pages.Count; i++)
            {
                var node = new DiaNode(pages[i]);
                if (first == null) first = node;
                if (prev != null)
                {
                    var next = new DiaOption(ListenOption) { link = node };
                    prev.options.Add(next);
                }
                prev = node;
            }
            prev.options.Add(new DiaOption(CloseOption) { resolveTree = true });
            Find.WindowStack.Add(new Dialog_NodeTree(first, delayInteractivity: true, radioMode: true, title: txt.label));

            // the archive keeps the whole address; the letter after it is the world describing behaviour only
            Find.LetterStack.ReceiveLetter(txt.letterLabel, Fill(txt.letterText, speaker, listener) + "\n\n"
                + string.Join("\n\n", pages), LetterDefOf.NeutralEvent, new LookTargets(listener));

            quest.End(QuestEndOutcome.Success, sendLetter: false);
            st.revealed = true;                      // last: every part of the beat above has happened
            st.revealedTick = Find.TickManager.TicksGame;
            Log.Message(CathedralDescentDefNames.LogTag + " the address was heard by " + listener.LabelShort + " at "
                + terminus.Position + "; reveal flag set at tick " + st.revealedTick);
            return true;
        }

        public static string SpeakerPhrase(Pawn p)
        {
            if (p.RaceProps.IsMechanoid || (p.def.defName ?? "").ToLowerInvariant().Contains("droid"))
                return p.LabelShort + "'s speaker grille";
            return "the comms set on " + p.LabelShort + "'s belt";
        }

        public static string Fill(string s, string speaker, Pawn p)
        {
            return (s ?? "").Replace("[SPEAKER]", speaker).Replace("[NAME]", p.LabelShort).Replace("\\n", "\n");
        }
    }

    /// <summary>The descent map's own watch: the escort's broken set, and the beat at the bottom.</summary>
    public class MapComponent_CathedralDescent : MapComponent
    {
        public const float AddressRadius = 6f;
        private bool hissed;
        private int isDescent = -1;   // -1 unknown, 0 no, 1 yes: a map's parent never changes

        public MapComponent_CathedralDescent(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (isDescent == 0 || Find.TickManager.TicksGame % 60 != 0) return;
            if (isDescent < 0) isDescent = CathedralDescent.IsDescentMap(map) ? 1 : 0;
            if (isDescent == 0) return;
            GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
            if (st == null || st.revealed) return;
            ThingDef tdef = CathedralDescent.TerminusDef;
            if (tdef == null) return;
            Thing terminus = map.listerThings.ThingsOfDef(tdef).FirstOrDefault();
            if (terminus == null) return;
            Pawn listener = null;
            float best = float.MaxValue;
            foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer))
            {
                if (!CathedralDescent.CanHear(p)) continue;
                float d = p.Position.DistanceTo(terminus.Position);
                if (d < best && CathedralDescent.AtTheBottom(p, terminus, AddressRadius)) { best = d; listener = p; }
                else if (!hissed && d <= AddressRadius * 4f)
                {
                    hissed = true;
                    string line = CathedralDescent.Text?.reportString;
                    if (!line.NullOrEmpty())
                        Messages.Message(CathedralDescent.Fill(line, CathedralDescent.SpeakerPhrase(p), p),
                            new LookTargets(p), MessageTypeDefOf.NeutralEvent);
                }
            }
            if (listener != null) CathedralDescent.SpeakAddress(listener, terminus);
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref hissed, "hissed", false);
        }
    }

    /// <summary>The opening: refused (with the reason logged) unless CathedralDescent.OpeningRefusal is null. A second
    /// fire, from the blackboard or a dev, is refused here.</summary>
    public class IncidentWorker_CathedralDescentOpening : IncidentWorker_GiveQuest
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            return CathedralDescent.OpeningRefusal() == null && base.CanFireNowSub(parms);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            string why = CathedralDescent.OpeningRefusal();
            if (why != null)
            {
                GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
                if (st != null) st.refusedOpenings++;
                Log.Message(CathedralDescentDefNames.LogTag + " opening refused: " + why);
                return false;
            }
            bool ok = base.TryExecuteWorker(parms);
            Quest made = CathedralDescent.DescentQuests().FirstOrDefault(q => q.State == QuestState.Ongoing);
            bool hasSite = made != null && made.PartsListForReading.Any(pt => pt is QuestPart_SpawnWorldObject);
            if (ok && hasSite)
            {
                GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
                st.opened = true;
                st.openedTick = Find.TickManager.TicksGame;
                Log.Message(CathedralDescentDefNames.LogTag + " opened at tick " + st.openedTick + " (quest " + made.id + ")");
                return true;
            }
            Log.Warning(CathedralDescentDefNames.LogTag + " opening did not produce a quest with a site (worker " + ok
                + ", quest " + (made?.id.ToString() ?? "none") + "); not marked opened");
            return false;
        }
    }

    /// <summary>Sets the descent site down on the tile CathedralDescent.TryFindTile picks; the quest's world object.</summary>
    public class RUT_QuestNode_CathedralDescentSite : QuestNode
    {
        [NoTranslate] public SlateRef<string> storeAs = "site";

        protected override bool TestRunInt(Slate slate)
        {
            return CathedralDescent.OpeningRefusal() == null && CathedralDescent.TryFindTile(out _);
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            if (!CathedralDescent.TryFindTile(out PlanetTile tile))
            {
                throw new System.InvalidOperationException("no tile for the descent site (test run found one)");
            }
            Site site = QuestGen_Sites.GenerateSite(
                new[] { new SitePartDefWithParams(CathedralDescent.SitePartDef, new SitePartParams()) }, tile, null);
            slate.Set(storeAs.GetValue(slate), site);
            QuestGen.quest.AddPart(new QuestPart_SpawnWorldObject
            {
                worldObject = site,
                inSignal = QuestGen.slate.Get<string>("inSignal"),
            });
        }
    }
}
