// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- who has handed what to the framework, on this map.
//
// One record per taken fixture: the thing and the glow it had the moment it was handed over (RM_GlowSnapshot).
// Release writes that snapshot back and forgets the record. Everything else is a way of reaching Release:
//  * the player's "Take glow back" button;
//  * the light channel switched off in Mod Settings -> every fixture on every map released on the next frame;
//  * a fixture that leaves the map (uninstalled, minified, moved by gravship) -> restored, then forgotten, so the
//    colour it carries away is its own;
//  * a destroyed fixture -> forgotten (there is nothing left to restore);
//  * the "Hand over every lamp on this map" button has a reverse: "Take glow back from every lamp" (ReleaseAll).
// One way leaves WITHOUT a restore (owner decision §9.9, 2026-10-23): another mod or the player changes a held lamp's
// colour. `lastLeft` is what the framework last left in the override; when the fixture holds anything else, the lamp is
// released and THEIR colour is kept (ReleaseKeepingEdit). Aboard the Utinni (scenarioDecides) that release displeases
// the gods: it is reported through RM_AtmosphericBaseAPI.LampEditedAboardUtinni, never acted on here (L2). A lamp
// switched off by hand is silent (L17): it stays held and simply is not driven while unlit (L9).
// `scenarioDecides`: a scenario that decides for this map hides both buttons; it hands lights over through the API.
// MapComponentUpdate runs every frame, paused or not (Phase 0, Q1), which is where the reverse designators are kept
// registered (RM_AtmosphericDesignators) and the channel switch is honoured.
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_TakenEmitter : IExposable
    {
        public Thing thing;
        public RM_GlowSnapshot prior = new RM_GlowSnapshot();
        // What the framework last left in the override (prior at take-over, then each write). Saved, so an edit made
        // while the game was closed (a mod's own save data) still reads as an edit. Null on a save from before
        // §9.9: adopted from the fixture on the first look, never read as an edit.
        public RM_GlowSnapshot lastLeft;

        public void ExposeData()
        {
            Scribe_References.Look(ref thing, "thing");
            Scribe_Deep.Look(ref prior, "prior");
            Scribe_Deep.Look(ref lastLeft, "lastLeft");
        }
    }

    public class RM_MapComponent_AtmosphericBase : MapComponent
    {
        public bool scenarioDecides;
        // T3 (c): the Nine's intensity aboard the Utinni, set by the scenario through the API (RM_GodGate.Apply). Saved.
        // Gentle (the default) keeps a floor; Full is Full. Never a player setting: the settings name no god.
        public int godIntensity = (int)RM_Intensity.Gentle;
        private bool gravEngineCached;
        private int gravEngineFrame = -9999;
        private const int GravEngineEveryFrames = 250;
        private List<RM_TakenEmitter> taken = new List<RM_TakenEmitter>();
        // Phase 3: one mood per CLAIMANT (a push by the same claimant replaces its own). Saved. The compositor orders them
        // by the rank each consumer supplied: the top two hold territory, the next three at most are tremor.
        private List<RM_MoodClaim> moods = new List<RM_MoodClaim>();
        public const int MaxMoods = 16;
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
            RM_GlowSnapshot now = RM_GlowAccess.Snapshot(RM_EmitterDiscovery.GlowerOf(t));
            taken.Add(new RM_TakenEmitter { thing = t, prior = now, lastLeft = now.Copy() });
            return true;
        }

        /// <summary>The settings button "Hand over every lamp on this map" (owner decision §9.1): every eligible lamp not
        /// yet held. Refused as a whole (0) where the player may not choose (channel off, the button switched off, or a
        /// scenario decides for this map). Reversible: ReleaseAll gives every one its own glow back.</summary>
        public int TakeOverAll()
        {
            if (!RM_AtmosphericDesignators.PlayerMayChoose(map)) return 0;
            int n = 0;
            foreach (Building b in new List<Building>(RM_EmitterDiscovery.EligibleOn(map)))
                if (TakeOver(b)) n++;
            return n;
        }

        /// <summary>How many eligible lamps on this map are not held yet (the settings button's label).</summary>
        public int UnheldEligibleCount()
        {
            int n = 0;
            foreach (Building b in RM_EmitterDiscovery.EligibleOn(map))
                if (!IsTaken(b)) n++;
            return n;
        }

        // ---- §9.9: an external colour edit releases the lamp and keeps the edit
        public int externalEditReleases, externalEditOffences;

        /// <summary>Release every held lamp whose override is not what the framework last left there. Called at the top
        /// of every evaluation, before anything is written. Returns how many were released.</summary>
        public int ReleaseExternallyEdited()
        {
            List<Thing> edited = null;
            for (int i = 0; i < taken.Count; i++)
            {
                RM_TakenEmitter rec = taken[i];
                if (rec.thing == null || rec.thing.Destroyed) continue;
                CompGlower g = RM_EmitterDiscovery.GlowerOf(rec.thing);
                if (g == null) continue;
                RM_GlowSnapshot now = RM_GlowAccess.Snapshot(g);
                if (rec.lastLeft == null) { rec.lastLeft = now; continue; }
                if (RM_HeldLampPolicy.EditedExternally(now, rec.lastLeft)) (edited ?? (edited = new List<Thing>())).Add(rec.thing);
            }
            if (edited == null) return 0;
            foreach (Thing t in edited) ReleaseKeepingEdit(t);
            return edited.Count;
        }

        /// <summary>Forget a held lamp WITHOUT writing its saved colour back: someone else's colour is on it now and it is
        /// theirs to keep. Aboard the Utinni this displeases the gods (reported, never acted on here).</summary>
        public bool ReleaseKeepingEdit(Thing t)
        {
            int i = IndexOf(t);
            if (i < 0) return false;
            taken.RemoveAt(i);
            compositor.Forget(t);
            externalEditReleases++;
            if (RM_HeldLampPolicy.DispleasesGods(RM_HeldLampEvent.ColourEditedExternally, scenarioDecides))
            {
                externalEditOffences++;
                RM_AtmosphericBaseAPI.RaiseLampEditedAboardUtinni(map, t);
            }
            return true;
        }

        /// <summary>The compositor's substrate write: the fixture's own glow, as it was handed over.</summary>
        public bool ShowSubstrate(Thing t)
        {
            int i = IndexOf(t);
            CompGlower g = i < 0 ? null : RM_EmitterDiscovery.GlowerOf(t);
            if (g == null) return false;
            RM_GlowAccess.Restore(g, taken[i].prior);
            taken[i].lastLeft = taken[i].prior.Copy();
            return true;
        }

        public bool Release(Thing t)
        {
            int i = IndexOf(t);
            if (i < 0) return false;
            RM_TakenEmitter rec = taken[i];
            // §9.9 also holds between evaluations (take-all-back button, channel switched off, prune, a save edited while
            // closed): a colour someone else left on the lamp is never written over by the saved one.
            CompGlower now = rec.thing != null && !rec.thing.Destroyed ? RM_EmitterDiscovery.GlowerOf(rec.thing) : null;
            if (now != null && RM_HeldLampPolicy.EditedExternally(RM_GlowAccess.Snapshot(now), rec.lastLeft))
                return ReleaseKeepingEdit(rec.thing);
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
            int i = t == null ? -1 : IndexOf(t);
            if (!RM_AtmosphericBaseSettings.Cur.lightChannel || i < 0) return false;
            if (!RM_PaletteGuard.IsMember(color)) { RM_PaletteGuard.violations++; return false; }
            CompGlower g = RM_EmitterDiscovery.GlowerOf(t);
            if (g == null) return false;
            if (g.GlowColor != color || !g.HasGlowColorOverride) RM_GlowAccess.WriteColor(g, color);
            taken[i].lastLeft = RM_GlowSnapshot.Of(color);
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

        // ---------------------------------------------------------------- Phases 2-3: moods, groups

        /// <summary>The loudest mood showing now: the top-ranked pushed one, else the gentle default when switched on.</summary>
        public RM_MoodClaim EffectiveMood
        {
            get
            {
                List<RM_MoodClaim> r = RankedMoods();
                return r.Count > 0 ? r[0] : null;
            }
        }

        /// <summary>The loudest pushed mood, or null.</summary>
        public RM_MoodClaim PushedMood
        {
            get
            {
                RM_MoodClaim best = null;
                foreach (RM_MoodClaim m in moods)
                    if (m?.scheme != null && m.scheme.Valid && MayShow(m.scheme) && (best == null || RM_TerritoryKernel.CompareRank(m.rank, m.claimant, best.rank, best.claimant) < 0))
                        best = m;
                return best;
            }
        }

        public int PushedMoodCount => moods.Count;

        /// <summary>Does this map carry a player grav engine (a gravship)? Re-read every GravEngineEveryFrames frames.</summary>
        public bool HasGravEngine
        {
            get
            {
                int f = UnityEngine.Time.frameCount;
                if (f - gravEngineFrame >= GravEngineEveryFrames || f < gravEngineFrame)
                {
                    gravEngineFrame = f;
                    gravEngineCached = map?.listerBuildings != null
                        && map.listerBuildings.AllBuildingsColonistOfClass<RimWorld.Building_GravEngine>().Any();
                }
                return gravEngineCached;
            }
        }

        /// <summary>T3 (c), owner ruling §9.12: a god's reading shows only aboard a Utinni gravship; elsewhere it is inert.</summary>
        public bool MayShow(RM_AtmosphericSchemeDef scheme)
        {
            bool sig = RM_SignatureDef.ForScheme(scheme) != null;
            return !sig || RM_GodGate.MayShow(true, scenarioDecides, HasGravEngine);
        }

        /// <summary>Every live mood, loudest first (§2.6 step 1). Rank is the consumer's; it is only ORDERED here. With
        /// nothing pushed, the gentle default alone (or nothing when it is switched off).</summary>
        public List<RM_MoodClaim> RankedMoods()
        {
            var live = new List<RM_MoodClaim>();
            foreach (RM_MoodClaim m in moods)
                if (m?.scheme != null && m.scheme.Valid && !string.IsNullOrEmpty(m.group) && MayShow(m.scheme)) live.Add(m);
            if (live.Count == 0)
            {
                RM_MoodClaim d = RM_Compositor.DefaultMood();
                if (d != null) live.Add(d);
                return live;
            }
            live.Sort((x, y) => RM_TerritoryKernel.CompareRank(x.rank, x.claimant, y.rank, y.claimant));
            return live;
        }

        /// <summary>Push a mood. The same claimant pushing again replaces its own mood (returned in `replaced`); a new
        /// claimant joins the others. Refused (false, nothing changed) for an empty claimant or group, a scheme that failed
        /// validation, or a full map (MaxMoods).</summary>
        public bool PushMood(string claimant, string group, RM_AtmosphericSchemeDef scheme, float rank, out RM_MoodClaim replaced)
        {
            replaced = null;
            if (string.IsNullOrEmpty(claimant) || string.IsNullOrEmpty(group) || scheme == null || !scheme.Valid) return false;
            if (float.IsNaN(rank) || float.IsInfinity(rank)) return false;
            var claim = new RM_MoodClaim { claimant = claimant, group = group, scheme = scheme, rank = rank };
            int i = moods.FindIndex(m => m.claimant == claimant);
            if (i >= 0) { replaced = moods[i]; moods[i] = claim; return true; }
            if (moods.Count >= MaxMoods) return false;
            moods.Add(claim);
            return true;
        }

        /// <summary>Release a mood, only by the claimant that holds it. The next evaluation re-allocates what it held.</summary>
        public bool ReleaseMood(string claimant)
        {
            return claimant != null && moods.RemoveAll(m => m.claimant == claimant) > 0;
        }

        /// <summary>The proof's seam: lift every pushed mood off the map (to be put back with RestoreMoods).</summary>
        public List<RM_MoodClaim> TakeAllMoods()
        {
            var all = moods;
            moods = new List<RM_MoodClaim>();
            return all;
        }

        public void RestoreMoods(List<RM_MoodClaim> all)
        {
            moods = all ?? new List<RM_MoodClaim>();
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
                if (g != null && RM_HeldLampPolicy.EditedExternally(RM_GlowAccess.Snapshot(g), rec.lastLeft)) g = null;   // theirs to keep (§9.9)
                if (g != null && rec.prior != null) RM_GlowAccess.RestoreFieldOnly(g, rec.prior);
            }
            taken.Clear();
            moods.Clear();
            registeredGroups.Clear();
        }

        private RM_MoodClaim legacyMood;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref scenarioDecides, "scenarioDecides", false);
            Scribe_Values.Look(ref godIntensity, "godIntensity", (int)RM_Intensity.Gentle);
            Scribe_Collections.Look(ref taken, "taken", LookMode.Deep);
            Scribe_Collections.Look(ref moods, "moods", LookMode.Deep);
            // A Phase 2 save held ONE mood under "mood"; read it once and carry it into the list.
            if (Scribe.mode == LoadSaveMode.LoadingVars) Scribe_Deep.Look(ref legacyMood, "mood");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (taken == null) taken = new List<RM_TakenEmitter>();
                taken.RemoveAll(r => r == null || r.thing == null || r.prior == null);
                if (moods == null) moods = new List<RM_MoodClaim>();
                if (legacyMood != null && !moods.Exists(m => m?.claimant == legacyMood.claimant)) moods.Add(legacyMood);
                legacyMood = null;
                moods.RemoveAll(m => m == null || m.scheme == null || string.IsNullOrEmpty(m.claimant) || string.IsNullOrEmpty(m.group));
            }
        }
    }
}
