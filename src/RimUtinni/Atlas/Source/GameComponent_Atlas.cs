using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // One entry's state in this save. Keyed by the entry's defName STRING, so an
    // entry whose def later disappears (mod removed, def renamed) is kept as an
    // archived record rather than dropped, and comes back if the def returns.
    public class AtlasRecord : IExposable
    {
        public int discoveredTick = -1;   // -1: not yet found
        public bool backfilled;           // found by the first poll after the Atlas joined this save
        public bool loreRead;
        public bool rewarded;

        public bool Discovered => discoveredTick >= 0;

        public void ExposeData()
        {
            Scribe_Values.Look(ref discoveredTick, "discoveredTick", -1);
            Scribe_Values.Look(ref backfilled, "backfilled", false);
            Scribe_Values.Look(ref loreRead, "loreRead", false);
            Scribe_Values.Look(ref rewarded, "rewarded", false);
        }
    }

    // Tracks every Atlas entry for this save. Detection by kind (design §5.3):
    //  - durable facts are polled on two cadences (cheap every pollIntervalTicks,
    //    terrain scans every slowPollIntervalTicks);
    //  - transient acts arrive as signals through SignalManager, or as
    //    Atlas.Notify(tag) from any mod (no hard dependency needed: call it by
    //    reflection);
    //  - on load, and the first time the Atlas sees a save, one full poll backfills
    //    durable facts. A backfilled discovery never pays a reward (rewards are
    //    future-only, design §5.5).
    // Idempotent: discovering an already-found entry does nothing.
    public class GameComponent_Atlas : GameComponent, ISignalReceiver
    {
        private Dictionary<string, AtlasRecord> records = new Dictionary<string, AtlasRecord>();
        private bool seenThisSave;          // has the Atlas ever polled this save
        private int rewardsEnabledTick = -1; // rewards only for discoveries after this tick

        private bool registered;

        public static GameComponent_Atlas Instance => Current.Game?.GetComponent<GameComponent_Atlas>();

        public GameComponent_Atlas(Game game)
        {
        }

        public AtlasRecord RecordFor(AtlasEntryDef def, bool create = false)
        {
            if (def == null) return null;
            if (records.TryGetValue(def.defName, out AtlasRecord r)) return r;
            if (!create) return null;
            r = new AtlasRecord();
            records[def.defName] = r;
            return r;
        }

        public bool IsDiscovered(AtlasEntryDef def) => RecordFor(def)?.Discovered ?? false;

        public int ArchivedCount => records.Keys.Count(k => DefDatabase<AtlasEntryDef>.GetNamedSilentFail(k) == null);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref records, "records", LookMode.Value, LookMode.Deep);
            Scribe_Values.Look(ref seenThisSave, "seenThisSave", false);
            Scribe_Values.Look(ref rewardsEnabledTick, "rewardsEnabledTick", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && records == null)
                records = new Dictionary<string, AtlasRecord>();
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            // Signal receivers are not saved: register once per load.
            if (!registered)
            {
                Find.SignalManager.RegisterReceiver(this);
                registered = true;
            }
        }

        public override void GameComponentTick()
        {
            if (!AtlasSettings.detectionEnabled) return;
            int now = Find.TickManager.TicksGame;

            if (AtlasSettings.rewardsEnabled && rewardsEnabledTick < 0) rewardsEnabledTick = now;
            if (!AtlasSettings.rewardsEnabled) rewardsEnabledTick = -1;

            if (!seenThisSave)
            {
                // First poll in this save: everything already true is backfilled.
                PollAll(includeExpensive: true, backfill: true);
                seenThisSave = true;
                return;
            }

            int fast = System.Math.Max(60, AtlasSettings.pollIntervalTicks);
            int slow = fast * 10;
            if (now % fast != 0) return;
            PollAll(includeExpensive: now % slow == 0, backfill: false);
        }

        public override void LoadedGame()
        {
            base.LoadedGame();
            // A save from before an entry existed: backfill durable facts quietly.
            if (seenThisSave && AtlasSettings.detectionEnabled)
                PollAll(includeExpensive: true, backfill: true);
        }

        // Returns how many entries were newly discovered.
        public int PollAll(bool includeExpensive, bool backfill)
        {
            int n = 0;
            if (!AtlasSettings.detectionEnabled) return 0;
            foreach (AtlasEntryDef def in DefDatabase<AtlasEntryDef>.AllDefsListForReading)
            {
                if (IsDiscovered(def)) continue;
                if (!AtlasSettings.CategoryEnabled(def.category)) continue;
                if (!def.Available) continue;
                for (int i = 0; i < def.triggers.Count; i++)
                {
                    AtlasTrigger t = def.triggers[i];
                    if (t.Expensive && !includeExpensive) continue;
                    bool hit;
                    try { hit = t.Available && t.Check(); }
                    catch (System.Exception e)
                    {
                        Log.ErrorOnce("[Atlas] trigger " + t.GetType().Name + " on " + def.defName + " threw: " + e,
                            ("RUT_Atlas_" + def.defName).GetHashCode());
                        hit = false;
                    }
                    if (hit)
                    {
                        Discover(def, backfill);
                        n++;
                        break;
                    }
                }
            }
            return n;
        }

        public void Notify_SignalReceived(Signal signal)
        {
            if (!AtlasSettings.detectionEnabled) return;
            NotifyTag(signal.tag);
        }

        public int NotifyTag(string tag)
        {
            if (tag.NullOrEmpty()) return 0;
            int n = 0;
            foreach (AtlasEntryDef def in DefDatabase<AtlasEntryDef>.AllDefsListForReading)
            {
                if (IsDiscovered(def)) continue;
                if (!AtlasSettings.CategoryEnabled(def.category)) continue;
                foreach (AtlasTrigger t in def.triggers)
                {
                    if (t.Available && t.MatchesSignal(tag))
                    {
                        Discover(def, backfill: false);
                        n++;
                        break;
                    }
                }
            }
            return n;
        }

        public void Discover(AtlasEntryDef def, bool backfill)
        {
            AtlasRecord r = RecordFor(def, create: true);
            if (r.Discovered) return;
            r.discoveredTick = Find.TickManager.TicksGame;
            r.backfilled = backfill;

            if (!backfill && AtlasSettings.toastsEnabled)
            {
                string text = "RUT_Atlas_DiscoveredToast".Translate(def.LabelCap);
                if (!def.lore.NullOrEmpty()) text += " " + "RUT_Atlas_LoreKeptToast".Translate();
                Messages.Message(text, MessageTypeDefOf.PositiveEvent, historical: false);
            }

            if (!backfill) TryReward(def, r);
        }

        // Dev / reset path. Never called by gameplay.
        public void Forget(AtlasEntryDef def)
        {
            if (def != null) records.Remove(def.defName);
        }

        public void ForgetAll()
        {
            records.Clear();
        }

        private void TryReward(AtlasEntryDef def, AtlasRecord r)
        {
            if (!AtlasSettings.rewardsEnabled || r.rewarded) return;
            if (rewardsEnabledTick < 0 || r.discoveredTick < rewardsEnabledTick) return;
            if (def.rewardThing.NullOrEmpty() || def.rewardCount <= 0) return;
            ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(def.rewardThing);
            Map map = Find.AnyPlayerHomeMap;
            if (td == null || map == null) return;

            int count = UnityEngine.Mathf.Max(1, UnityEngine.Mathf.RoundToInt(def.rewardCount * AtlasSettings.rewardScale));
            var things = new List<Thing>();
            int left = count;
            while (left > 0)
            {
                Thing t = ThingMaker.MakeThing(td, td.MadeFromStuff ? GenStuff.DefaultStuffFor(td) : null);
                int stack = UnityEngine.Mathf.Min(left, td.stackLimit);
                t.stackCount = stack;
                left -= stack;
                things.Add(t);
            }
            DropPodUtility.DropThingsNear(DropCellFinder.TradeDropSpot(map), map, things);
            r.rewarded = true;
            Messages.Message("RUT_Atlas_RewardToast".Translate(def.LabelCap, count, td.label),
                MessageTypeDefOf.PositiveEvent, historical: false);
        }
    }

    // The public, dependency-free door for other mods. Call by reflection so the
    // caller needs no reference to this assembly:
    //   AccessTools.TypeByName("RimMandrake.Utinni.Atlas.Atlas")
    //     ?.GetMethod("Notify")?.Invoke(null, new object[] { "RM_Graffiti_FirstFinished" });
    // A SignalManager signal ending in the same tag works too, with no code at all.
    public static class Atlas
    {
        public static int Notify(string tag)
        {
            GameComponent_Atlas c = GameComponent_Atlas.Instance;
            if (c == null || !AtlasSettings.detectionEnabled) return 0;
            return c.NotifyTag(tag);
        }
    }
}
