using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Hose
{
    [DefOf]
    public static class HoseDefOf
    {
        public static ThingDef RM_HoseReel;

        static HoseDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(HoseDefOf));
    }

    /// <summary>What sits on the free end. Open (the default since owner review 2026-10-04 B8): a plain open hose end the
    /// hose's own width, no nozzle-style fitting. Appended last so saved names keep their meaning.</summary>
    public enum HoseEnd { Nozzle, EndCap, Open }

    public class CompProperties_HoseReel : CompProperties
    {
        public CompProperties_HoseReel() => compClass = typeof(CompHoseReel);
    }

    /// <summary>
    /// A hose reel / pump hookup (design 3.6): a plain vanilla Building carrying this comp. The laid hose is DATA on
    /// the reel (its free end cell and end piece), never per-cell things, so laying 30 cells is one click and a save
    /// names only our def (walk M9: a mod-less load drops the reel with vanilla's missing-def error). The look is
    /// recomputed from (reel, end, seed) after a load. The flat/plump state machine is saved here, so a load keeps
    /// the state. A COMP, not a Building subclass, for the same save reason as the aerial anchors.
    /// </summary>
    [StaticConstructorOnStartup]
    public class CompHoseReel : ThingComp
    {
        public bool laid;
        public IntVec3 far = IntVec3.Invalid;
        public HoseEnd end = HoseEnd.Open;
        /// <summary>The debug/test flow provider's input (gizmo in dev mode, HoseProbe "flow:").</summary>
        public bool debugFlowing;
        public HoseStateMachine sm = new HoseStateMachine();
        /// <summary>Runtime only: the laid geometry and its cache keys, and the state history for the flicker check.</summary>
        public HoseLay lay;
        public string layKey;
        public ulong corridorHash;
        public string lastProvider = "none";
        public bool lastSignal;
        public readonly List<KeyValuePair<int, HoseVis>> history = new List<KeyValuePair<int, HoseVis>>();
        /// <summary>Runtime only: the coupled pipe/tank (owner review round 2), refreshed by Port() at most every 60 ticks.</summary>
        public Thing port;
        public Core.Cell portSide, portContact;
        public HosePortKind portKind = HosePortKind.None;
        /// <summary>Runtime: why the planner could not lay this hose (null when it could).</summary>
        public string lastLayReason;
        /// <summary>HOSE_BLOCKED_REROUTE_RETRACT_1: the last automatic reel-in (saved, so the inspect line survives a load).</summary>
        public string lastRetractReason;
        public int lastRetractTick = -1;
        private int portTick = int.MinValue;

        /// <summary>The coupled neighbour (null = not connected), re-read at most every 60 ticks or when forced.</summary>
        public Thing Port(bool force = false)
        {
            int now = Find.TickManager?.TicksGame ?? 0;
            if (!force && now - portTick < 60 && (port == null || port.Spawned)) return port;
            portTick = now;
            port = HosePorts.Find(this, out portSide, out portContact, out portKind);
            return port;
        }

        private static readonly Texture2D IconLay = ContentFinder<Texture2D>.Get("RimMandrake/MessyConduit/Hose/Nozzle", false);
        private static readonly Texture2D IconReel = ContentFinder<Texture2D>.Get("RimMandrake/MessyConduit/Hose/Reel_PumpHookup", false);
        private static readonly Texture2D IconEnd = ContentFinder<Texture2D>.Get("RimMandrake/MessyConduit/Hose/EndCap", false);

        public ulong Seed => (ulong)(parent.thingIDNumber * 7919L + 17);
        public float MaxLength => Mathf.Clamp(HoseSettings.maxLength, 4f, 80f);

        /// <summary>The reel's footprint (2x2 since round 3); the hose leaves it at the centre.</summary>
        public HoseReelRect Rect
        {
            get
            {
                CellRect rc = parent.OccupiedRect();
                return new HoseReelRect(rc.minX, rc.minZ, rc.Width, rc.Height);
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            parent.Map.GetComponent<RM_MapComponent_Hoses>()?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map.GetComponent<RM_MapComponent_Hoses>()?.Deregister(this);
            // packed up (minified, destroyed): the hose comes back onto the reel
            laid = false;
            lay = null;
            port = null;
            sm.ResetFlat();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref laid, "rmHoseLaid");
            Scribe_Values.Look(ref far, "rmHoseFar", IntVec3.Invalid);
            Scribe_Values.Look(ref end, "rmHoseEnd", HoseEnd.Open);
            Scribe_Values.Look(ref debugFlowing, "rmHoseDebugFlow");
            Scribe_Values.Look(ref sm.State, "rmHoseState", HoseVis.Flat);
            Scribe_Values.Look(ref sm.Since, "rmHoseSince");
            Scribe_Values.Look(ref sm.B0, "rmHoseB0");
            Scribe_Values.Look(ref sm.LastTrue, "rmHoseLastTrue", int.MinValue / 2);
            Scribe_Values.Look(ref sm.PlumpSince, "rmHosePlumpSince");
            Scribe_Values.Look(ref sm.Transitions, "rmHoseTransitions");
            Scribe_Values.Look(ref lastRetractReason, "rmHoseRetractWhy");
            Scribe_Values.Look(ref lastRetractTick, "rmHoseRetractTick", -1);
        }

        /// <summary>Null when laid, else why not (also the gizmo's reject message).</summary>
        public string TryLay(IntVec3 target)
        {
            Map map = parent.Map;
            if (map == null) return "not spawned";
            RM_MapComponent_Hoses comp = map.GetComponent<RM_MapComponent_Hoses>();
            // CheckInstall answers null for a valid target: a `?? "no hose component"` here turned every valid lay
            // into a refusal (live lane F 2026-10-02: H2 "lay1: no hose component" while H1b's check read ok)
            if (comp == null) return "no hose component";
            string why = comp.CheckInstall(this, target);
            if (why != null) return why;
            far = target;
            laid = true;
            lastRetractReason = null;
            lastLayReason = null;
            lay = null;
            layKey = null;
            sm.ResetFlat();
            history.Clear();
            RefreshLook();
            return null;
        }

        /// <summary>HOSE_BLOCKED_REROUTE_RETRACT_1: no route within the hose's length remains, so the hose winds back
        /// onto the reel (never left laid but invisible), with a message pointing at the reel and the Alert_HoseRetracted
        /// entry. The free-end target is forgotten; the player lays it again.</summary>
        public void Retract(string why)
        {
            ReelIn();
            lastRetractReason = why;
            lastRetractTick = Find.TickManager?.TicksGame ?? 0;
            if (parent.Spawned && parent.Faction == Faction.OfPlayer)
                Messages.Message("Hose reeled in: " + why + " (an obstacle cut its route and no other route fits the hose).",
                    new LookTargets(parent), MessageTypeDefOf.NegativeEvent, false);
        }

        public void ReelIn()
        {
            laid = false;
            lay = null;
            layKey = null;
            lastLayReason = null;
            sm.ResetFlat();
            history.Clear();
            RefreshLook();
        }

        /// <summary>Graphic_HoseReel picks stored vs deployed art at print time: reprint the reel's map mesh.</summary>
        private void RefreshLook()
        {
            if (parent.Spawned) parent.DirtyMapMesh(parent.Map);
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (!HoseSettings.enabled || parent.Faction != Faction.OfPlayer) yield break;
            if (!laid)
                yield return new Command_Action
                {
                    defaultLabel = "Lay hose",
                    defaultDesc = "Run the hose out to a cell up to " + MaxLength.ToString("0") + " cells away. Laid at once; reel it back in just as fast.",
                    icon = IconLay,
                    action = () =>
                    {
                        var tp = new TargetingParameters { canTargetLocations = true, canTargetPawns = false, canTargetBuildings = false, canTargetItems = false };
                        Find.Targeter.BeginTargeting(tp, t =>
                        {
                            string why = TryLay(t.Cell);
                            if (why != null) Messages.Message("Cannot lay the hose there: " + why + ".", MessageTypeDefOf.RejectInput, false);
                        }, caster: (Pawn)null);
                    }
                };
            else
                yield return new Command_Action
                {
                    defaultLabel = "Reel in hose",
                    defaultDesc = "Wind the hose back onto the reel.",
                    icon = IconReel,
                    action = ReelIn
                };
            yield return new Command_Action
            {
                defaultLabel = end == HoseEnd.Nozzle ? "Free end: nozzle" : end == HoseEnd.EndCap ? "Free end: end cap" : "Free end: open",
                defaultDesc = "Switch what sits on the hose's free end: open (plain hose end), nozzle or end cap.",
                icon = end == HoseEnd.Nozzle ? IconLay : IconEnd,
                action = () => end = end == HoseEnd.Open ? HoseEnd.Nozzle : end == HoseEnd.Nozzle ? HoseEnd.EndCap : HoseEnd.Open
            };
            if (Prefs.DevMode && laid)
                yield return new Command_Toggle
                {
                    defaultLabel = "DEV: flow through hose",
                    defaultDesc = "The debug flow provider: pretend liquid is moving through this hose (FlowWorks has no pump yet).",
                    isActive = () => debugFlowing,
                    toggleAction = () => debugFlowing = !debugFlowing
                };
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            if (!laid && HoseSettings.enabled)
                GenDraw.DrawCircleOutline(new Vector3((float)Rect.Centre.X, AltitudeLayer.MetaOverlays.AltitudeFor(), (float)Rect.Centre.Z), MaxLength);   // from the 2x2 reel's centre
        }

        public override string CompInspectStringExtra()
        {
            Thing p = parent.Spawned ? Port() : null;
            string conn = p != null ? "Connected to " + p.LabelShort + " (" + portKind.ToString().ToLower() + ")." : "Not connected: build it beside a pipe or tank.";
            if (!laid) return conn + "\nHose reeled in." + (lastRetractReason != null ? " Retracted automatically: " + lastRetractReason + "." : "");
            return conn + "\nHose laid to " + far + " (" + sm.State.ToString().ToLower() + ").";
        }
    }
}
