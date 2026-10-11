// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- who has handed what to the framework, on this map.
//
// One record per taken fixture: the thing and the glow it had the moment it was handed over (RM_GlowSnapshot).
// Release writes that snapshot back and forgets the record. Everything else is a way of reaching Release:
//  * the player's "Take glow back" button;
//  * the light channel switched off in Mod Settings -> every fixture on every map released on the next frame;
//  * a fixture that leaves the map (uninstalled, minified, moved by gravship) -> restored, then forgotten, so the
//    colour it carries away is its own;
//  * a destroyed fixture -> forgotten (there is nothing left to restore).
// `scenarioDecides`: a scenario that decides for this map hides both buttons; it hands lights over through the API.
// MapComponentUpdate runs every frame, paused or not (Phase 0, Q1), which is where the reverse designators are kept
// registered (RM_AtmosphericDesignators) and the channel switch is honoured.
using System.Collections.Generic;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_TakenEmitter : IExposable
    {
        public Thing thing;
        public RM_GlowSnapshot prior = new RM_GlowSnapshot();

        public void ExposeData()
        {
            Scribe_References.Look(ref thing, "thing");
            Scribe_Deep.Look(ref prior, "prior");
        }
    }

    public class RM_MapComponent_AtmosphericBase : MapComponent
    {
        public bool scenarioDecides;
        private List<RM_TakenEmitter> taken = new List<RM_TakenEmitter>();
        // Phase 2: at most one mood per map (no rank exists to order two; territory is Phase 3). Saved.
        private RM_MoodClaim mood;
        // Groups a hooking mod registered (§2.2 source 1). NOT saved: the registering mod re-registers on load.
        private readonly Dictionary<string, HashSet<Thing>> registeredGroups = new Dictionary<string, HashSet<Thing>>();
        public readonly RM_Compositor compositor = new RM_Compositor();
        private int lastPruneFrame = -9999;
        private const int PruneEveryFrames = 60;

        public RM_MapComponent_AtmosphericBase(Map map) : base(map)
        {
        }

        public static RM_MapComponent_AtmosphericBase For(Map map)
        {
            return map?.GetComponent<RM_MapComponent_AtmosphericBase>();
        }

        public int TakenCount => taken.Count;

        public IEnumerable<Thing> TakenThings
        {
            get
            {
                for (int i = 0; i < taken.Count; i++)
                    yield return taken[i].thing;
            }
        }

        private int IndexOf(Thing t)
        {
            for (int i = 0; i < taken.Count; i++)
                if (taken[i].thing == t)
                    return i;
            return -1;
        }

        public bool IsTaken(Thing t)
        {
            return t != null && IndexOf(t) >= 0;
        }

        public RM_GlowSnapshot PriorOf(Thing t)
        {
            int i = IndexOf(t);
            return i < 0 ? null : taken[i].prior;
        }

        /// <summary>Why this thing may not be handed over now, or null when it may.</summary>
        public string TakeOverRefusal(Thing t)
        {
            if (!RM_AtmosphericBaseSettings.Cur.lightChannel) return "the light channel is off in Mod Settings";
            if (!RM_GlowAccess.Bound) return "this game's CompGlower no longer has the fields Atmospheric Base restores";
            if (t == null || t.MapHeld != map) return "not on this map";
            if (IsTaken(t)) return "already handed over";
            RM_EmitterVerdict v = RM_EmitterDiscovery.Classify(t);
            return v == RM_EmitterVerdict.Eligible ? null : v.ToString();
        }

        public bool TakeOver(Thing t)
        {
            if (TakeOverRefusal(t) != null) return false;
            taken.Add(new RM_TakenEmitter { thing = t, prior = RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(t)) });
            return true;
        }

        public bool Release(Thing t)
        {
            int i = IndexOf(t);
            if (i < 0) return false;
            RM_TakenEmitter rec = taken[i];
            taken.RemoveAt(i);
            compositor.Forget(rec.thing);
            CompGlower g = rec.thing != null && !rec.thing.Destroyed ? RM_EmitterDiscovery.GlowerOf(rec.thing) : null;
            if (g != null) RM_GlowAccess.Restore(g, rec.prior);
            return true;
        }

        public int ReleaseAll()
        {
            int n = 0;
            while (taken.Count > 0 && Release(taken[taken.Count - 1].thing)) n++;
            taken.Clear();
            return n;
        }

        /// <summary>The only driving verb: set a taken fixture's colour. The compositor is its caller; nothing that has
        /// not been handed over can be driven, and (L4) no colour outside a loaded scheme's palette is ever written.</summary>
        public bool Drive(Thing t, ColorInt color)
        {
            if (!RM_AtmosphericBaseSettings.Cur.lightChannel || !IsTaken(t)) return false;
            if (!RM_PaletteGuard.IsMember(color)) { RM_PaletteGuard.violations++; return false; }
            CompGlower g = RM_EmitterDiscovery.GlowerOf(t);
            if (g == null) return false;
            if (g.GlowColor != color || !g.HasGlowColorOverride) RM_GlowAccess.WriteColor(g, color);
            return true;
        }

        public void Prune()
        {
            for (int i = taken.Count - 1; i >= 0; i--)
            {
                Thing t = taken[i].thing;
                if (t == null || t.Destroyed) { taken.RemoveAt(i); continue; }
                if (!t.Spawned || t.Map != map) Release(t);
            }
        }

        public override void MapComponentUpdate()
        {
            if (Find.CurrentMap == map) RM_AtmosphericDesignators.EnsureRegistered();
            if (taken.Count == 0) return;
            if (!RM_AtmosphericBaseSettings.Cur.lightChannel) { ReleaseAll(); return; }
            int f = UnityEngine.Time.frameCount;
            if (f - lastPruneFrame >= PruneEveryFrames)
            {
                lastPruneFrame = f;
                Prune();
            }
            compositor.Update(this);
        }

        // ---------------------------------------------------------------- Phase 2: one mood, groups

        /// <summary>The mood showing now: the pushed one, else the framework's gentle default when switched on.</summary>
        public RM_MoodClaim EffectiveMood => mood ?? RM_Compositor.DefaultMood();
        public RM_MoodClaim PushedMood => mood;

        /// <summary>Phase 2 holds ONE mood: a push replaces whatever was pushed before and returns it. Refused (null
        /// returned, nothing changed) for an empty claimant or group, or a scheme that failed validation.</summary>
        public bool PushMood(string claimant, string group, RM_AtmosphericSchemeDef scheme, float rank, out RM_MoodClaim replaced)
        {
            replaced = null;
            if (string.IsNullOrEmpty(claimant) || string.IsNullOrEmpty(group) || scheme == null || !scheme.Valid) return false;
            replaced = mood;
            mood = new RM_MoodClaim { claimant = claimant, group = group, scheme = scheme, rank = rank };
            return true;
        }

        /// <summary>Release the pushed mood, only by the claimant that holds it. The next evaluation shows the default
        /// (or each fixture's own glow).</summary>
        public bool ReleaseMood(string claimant)
        {
            if (mood == null || mood.claimant != claimant) return false;
            mood = null;
            return true;
        }

        public void RegisterGroup(string name, IEnumerable<Thing> members)
        {
            if (string.IsNullOrEmpty(name)) return;
            registeredGroups[name] = members == null ? new HashSet<Thing>() : new HashSet<Thing>(members);
        }

        public bool UnregisterGroup(string name) => name != null && registeredGroups.Remove(name);

        public HashSet<Thing> RegisteredGroup(string name)
        {
            return name != null && registeredGroups.TryGetValue(name, out HashSet<Thing> g) ? g : null;
        }

        // ---------------------------------------------------------------- the map going away

        /// <summary>Game.DeinitAndRemoveMap -> MapComponentUtility.MapRemoved (RimSage 1.6): the map is gone, e.g. a
        /// gravship took off and abandoned it. A fixture that left on the ship is unspawned and would otherwise carry the
        /// driven colour away with no record left to restore it, so every surviving fixture gets its own glow back.
        /// Field-only: the map is already out of Find.Maps, so no glow grid may be touched (MapHeld would resolve
        /// against the wrong list), and an unspawned fixture registers nothing anyway -- CompGlower re-reads the field
        /// when it spawns again.</summary>
        public override void MapRemoved()
        {
            for (int i = taken.Count - 1; i >= 0; i--)
            {
                RM_TakenEmitter rec = taken[i];
                CompGlower g = rec.thing != null && !rec.thing.Destroyed ? RM_EmitterDiscovery.GlowerOf(rec.thing) : null;
                if (g != null && rec.prior != null) RM_GlowAccess.RestoreFieldOnly(g, rec.prior);
            }
            taken.Clear();
            mood = null;
            registeredGroups.Clear();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref scenarioDecides, "scenarioDecides", false);
            Scribe_Collections.Look(ref taken, "taken", LookMode.Deep);
            Scribe_Deep.Look(ref mood, "mood");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (taken == null) taken = new List<RM_TakenEmitter>();
                taken.RemoveAll(r => r == null || r.thing == null || r.prior == null);
                if (mood != null && (mood.scheme == null || string.IsNullOrEmpty(mood.claimant) || string.IsNullOrEmpty(mood.group))) mood = null;
            }
        }
    }
}
