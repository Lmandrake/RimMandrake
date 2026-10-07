using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.Hose
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
    /// the reel (its free end cell and end piece), never per-cell things, so laying 40 cells is one click and a save
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
        /// <summary>Round 4: the hose a too-long route needed (cells) when it was retracted or refused, -1 = not measured.</summary>
        public float lastRetractNeed = -1f;
        private int portTick = int.MinValue;

        // ---------------------------------------------------------------- colonist-carried hose, stage S2 (saved)
        // hose_carry_design_2026-10-04.md sections 3 and 11. `laid` stays written and in step (= carry is Laid or
        // Dropped), so every older reader (flow tick, relays, probe, alert, reel art) is unchanged.
        /// <summary>Where the hose is: on the drum, being carried, lying out (set down or dropped), being wound in.</summary>
        public HoseCarryState carry = HoseCarryState.Stored;
        /// <summary>The cells the carrier WALKED (trail[0] = the reel cell the hose left from). EMPTY while Laid/Dropped =
        /// the planned route (a save from before this stage, the DEV instant lay and the probe's lay verb).</summary>
        public List<IntVec3> trail = new List<IntVec3>();
        /// <summary>The colonist holding the end (Carrying) or winding (Retracting); null otherwise.</summary>
        public Pawn carrier;
        /// <summary>Cells wound back in while Retracting.</summary>
        public float wound;
        /// <summary>The player's order (nothing in S2 executes it: S3's WorkGiver takes it) and its target cell.</summary>
        public HosePendingOrder pending = HosePendingOrder.None;
        public IntVec3 pendingAt = IntVec3.Invalid;
        /// <summary>S3 hook (design section 5 b): does this pawn's CURRENT job hold this reel? S3 replaces the default (the
        /// job targets the reel) with its driver-type test. Read by the 30-tick holder check.</summary>
        public static System.Func<Pawn, CompHoseReel, bool> HoldsReel = (p, r) => p.CurJob != null && p.CurJob.targetA.Thing == r.parent;

        /// <summary>The coupled neighbour (null = not connected), re-read at most every 60 ticks or when forced.</summary>
        public Thing Port(bool force = false)
        {
            int now = Find.TickManager?.TicksGame ?? 0;
            if (!force && HoseLive.CacheFresh(now, portTick, 60) && (port == null || port.Spawned)) return port;
            portTick = now;
            port = HosePorts.Find(this, out portSide, out portContact, out portKind);
            return port;
        }

        private static readonly Texture2D IconLay = ContentFinder<Texture2D>.Get("RimMandrake/GimmeSomeSlack/Hose/Nozzle", false);
        private static readonly Texture2D IconReel = ContentFinder<Texture2D>.Get("RimMandrake/GimmeSomeSlack/Hose/Reel_PumpHookup", false);
        private static readonly Texture2D IconEnd = ContentFinder<Texture2D>.Get("RimMandrake/GimmeSomeSlack/Hose/EndCap", false);

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
            // packed up (minified, destroyed): the hose comes back onto the reel (ReelGone); a carrier's job fails on its
            // despawned target A
            SetCarry(HoseCarryState.Stored);
            trail.Clear();
            carrier = null;
            wound = 0f;
            pending = HosePendingOrder.None;
            pendingAt = IntVec3.Invalid;
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
            Scribe_Values.Look(ref lastRetractNeed, "rmHoseRetractNeed", -1f);
            // S2 carry fields (design section 11); old keys above untouched
            if (Scribe.mode == LoadSaveMode.Saving) laid = HoseCarryLoad.IsLaid(carry);
            Scribe_Values.Look(ref carry, "rmHoseCarry", HoseCarryState.Stored);
            Scribe_Collections.Look(ref trail, "rmHoseTrail", LookMode.Value);
            Scribe_References.Look(ref carrier, "rmHoseCarrier");
            Scribe_Values.Look(ref wound, "rmHoseWound");
            Scribe_Values.Look(ref pending, "rmHosePending", HosePendingOrder.None);
            Scribe_Values.Look(ref pendingAt, "rmHosePendingAt", IntVec3.Invalid);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (trail == null) trail = new List<IntVec3>();
                // a save without rmHoseCarry: laid -> Laid on the planned route, exactly as before this stage
                carry = HoseCarryLoad.Resolve(laid, carry, trail.Count);
                laid = HoseCarryLoad.IsLaid(carry);
                if (laid && !far.IsValid && trail.Count > 0) far = trail[trail.Count - 1];
                if (laid && !far.IsValid) { carry = HoseCarryState.Stored; laid = false; trail.Clear(); }
                if (carry != HoseCarryState.Carrying && carry != HoseCarryState.Retracting) carrier = null;
            }
        }

        // ---------------------------------------------------------------- S2: carry state on the reel
        private void SetCarry(HoseCarryState s)
        {
            carry = s;
            bool was = laid;
            laid = HoseCarryLoad.IsLaid(s);
            if (was != laid) RefreshLook();
        }

        /// <summary>Is any hose off the drum and drawable (laid/dropped with a free end, or carried/wound with a trail)?</summary>
        public bool HoseOut =>
            laid ? far.IsValid : (carry == HoseCarryState.Carrying || carry == HoseCarryState.Retracting) && trail.Count > 0;

        /// <summary>The free end's cell: far while Laid/Dropped, the trail's last cell while carried or wound.</summary>
        public IntVec3 EndCell => laid ? far : trail.Count > 0 ? trail[trail.Count - 1] : IntVec3.Invalid;

        /// <summary>The walked trail as planner cells (empty = planned route).</summary>
        public List<Cell> TrailCells()
        {
            var l = new List<Cell>(trail.Count);
            foreach (IntVec3 c in trail) l.Add(new Cell(c.x, c.z));
            return l;
        }

        /// <summary>A short stable hash of the trail for the lay cache key ("" for an empty trail).</summary>
        public string TrailKey()
        {
            if (trail.Count == 0) return "";
            ulong h = 1469598103934665603UL;
            foreach (IntVec3 c in trail) h = (h ^ (ulong)(uint)(c.x * 73856093 ^ c.z * 19349663)) * 1099511628211UL;
            return "T" + trail.Count + ":" + h.ToString("x16");
        }

        private HoseTrail TrailOf(CordWorld w)
        {
            var t = new HoseTrail(Rect.Mouth, MaxLength);
            t.Cells.AddRange(TrailCells());
            return t;
        }

        private RM_MapComponent_Hoses Hoses => parent.Spawned ? parent.Map.GetComponent<RM_MapComponent_Hoses>() : null;

        /// <summary>The trail's pulled-taut length (cells), 0 with no trail. A planned (empty) trail reads the planned route.</summary>
        public float TrailLength()
        {
            RM_MapComponent_Hoses comp = Hoses;
            if (comp == null) return 0f;
            if (trail.Count == 0) return laid ? (float)System.Math.Max(0, HoseMath.RouteLength(comp.World(), Rect, new Cell(far.x, far.z), MaxLength, false)) : 0f;
            return (float)TrailOf(comp.World()).PulledLength(comp.World());
        }

        /// <summary>A planned (empty-trail) hose about to be picked up or wound: its route becomes explicit cells.</summary>
        private void MaterializeTrail()
        {
            if (trail.Count > 0 || !far.IsValid) return;
            RM_MapComponent_Hoses comp = Hoses;
            var f = new Cell(far.x, far.z);
            Cell s = Rect.StartCellToward(f);
            List<Cell> path = comp == null ? null : HoseMath.RouteCells(comp.World(), s, f, HoseMath.SearchLengthBound(MaxLength), false);   // B2: the route install judged
            if (path == null) path = new List<Cell> { s, f };
            foreach (Cell c in path) trail.Add(new IntVec3(c.X, 0, c.Z));
        }

        /// <summary>Does the walked trail still run over hose-walkable cells (the 250-tick corridor check)? A wall built on it
        /// sends the hose back to a planned route (design section 8: the obstacle moved it).</summary>
        public bool TrailWalkable(CordWorld w)
        {
            foreach (IntVec3 c in trail)
            {
                var k = new Cell(c.x, c.z);
                if (!Rect.Contains(k) && !w.IsWalkable(k)) return false;
            }
            return true;
        }

        private void HoseChanged()
        {
            lay = null;
            layKey = null;
        }

        /// <summary>A cell on or edge-adjacent to this reel: a Move order there means "bring the end back to the reel".</summary>
        public bool IsBringBack(IntVec3 c)
        {
            HoseReelRect r = Rect;
            return c.x >= r.X0 - 1 && c.x <= r.X0 + r.W && c.z >= r.Z0 - 1 && c.z <= r.Z0 + r.H;
        }

        // ---------------------------------------------------------------- S2: the five order methods (MP sync points, section 12)
        /// <summary>Relay redirection + loop refusal + the install check, shared by TryLay and the orders. Null = ok.</summary>
        private string ResolveTarget(ref IntVec3 target)
        {
            Map map = parent.Map;
            if (map == null) return "not spawned";
            RM_MapComponent_Hoses comp = map.GetComponent<RM_MapComponent_Hoses>();
            // CheckInstall answers null for a valid target: a `?? "no hose component"` here turned every valid lay
            // into a refusal (live lane F 2026-10-02: H2 "lay1: no hose component" while H1b's check read ok)
            if (comp == null) return "no hose component";
            // round 6, relays: aimed at another reel (its footprint or an intake cell), the hose ends on that reel's intake
            // nearest this reel's mouth; a chain may not loop back
            CompHoseReel relay = comp.ReelCovering(this, target);
            if (relay != null)
            {
                CordWorld w = comp.World();
                if (!HoseRelay.TryIntake(relay.Rect, Rect.Mouth, c => w.InBounds(c) && w.IsWalkable(c) && !Rect.Contains(c), out Cell intake))
                    return "the other reel has no free side to couple to";
                target = new IntVec3(intake.X, 0, intake.Z);
            }
            else relay = comp.RelayAt(this, new Cell(target.x, target.z));
            if (relay != null && comp.Loops(this, relay)) return "that reel already feeds this one (a chain may not loop back)";
            return comp.CheckInstall(this, target);
        }

        /// <summary>Player order: a colonist carries the end from the reel out to target. Null = placed, else why not.</summary>
        public string OrderDeploy(IntVec3 target)
        {
            if (carry != HoseCarryState.Stored) return "the hose is already out";
            string why = ResolveTarget(ref target);
            if (why != null) return why;
            pending = HosePendingOrder.Deploy;
            pendingAt = target;
            return null;
        }

        /// <summary>Player order: a colonist picks up the free end and carries it to target (on/next to the reel = bring it back).</summary>
        public string OrderMove(IntVec3 target)
        {
            if (carry != HoseCarryState.Laid && carry != HoseCarryState.Dropped && carry != HoseCarryState.Carrying) return "no hose end is out";
            if (!IsBringBack(target))
            {
                string why = ResolveTarget(ref target);
                if (why != null) return why;
            }
            pending = HosePendingOrder.Move;
            pendingAt = target;
            return null;
        }

        /// <summary>Player order: a colonist goes to the reel and winds the hose in.</summary>
        public string OrderRetract()
        {
            if (carry == HoseCarryState.Stored) return "the hose is already on the reel";
            pending = HosePendingOrder.Retract;
            pendingAt = IntVec3.Invalid;
            return null;
        }

        /// <summary>Clears the order; a carrier mid-walk drops the end where he stands, a winder stops winding.</summary>
        public void CancelOrder()
        {
            pending = HosePendingOrder.None;
            pendingAt = IntVec3.Invalid;
            if (carry == HoseCarryState.Carrying) DropCarry(carrier, false);
            else if (carry == HoseCarryState.Retracting && carrier != null) StopWind(carrier);
        }

        /// <summary>DEV / probe staging: today's instant lay. Null = laid.</summary>
        public string DevLayInstant(IntVec3 target) => TryLay(target);

        // ---------------------------------------------------------------- S2: what S3's job drivers call
        /// <summary>The pawn grabs the end: at the reel mouth (Stored -> Carrying) or where it lies (Laid/Dropped -> Carrying).
        /// Idempotent for the current carrier. False = refused (another carrier, being wound, or nothing to pick up).</summary>
        public bool BeginCarry(Pawn p)
        {
            if (p == null) return false;
            if (carry == HoseCarryState.Carrying) return carrier == p;
            HoseCarryEvent e = carry == HoseCarryState.Stored ? HoseCarryEvent.Grab : HoseCarryEvent.PickUp;
            HoseCarryState? n = HoseCarryTable.Next(carry, e);
            if (n == null) return false;
            if (carry == HoseCarryState.Stored)
            {
                trail.Clear();
                IntVec3 toward = pendingAt.IsValid ? pendingAt : p.Position;
                Cell s = Rect.StartCellToward(new Cell(toward.x, toward.z));
                trail.Add(new IntVec3(s.X, 0, s.Z));
                lastRetractReason = null;
                lastRetractNeed = -1f;
            }
            else MaterializeTrail();
            carrier = p;
            wound = 0f;
            sm.ResetFlat();
            SetCarry(n.Value);
            HoseChanged();
            return true;
        }

        /// <summary>The carrier entered <paramref name="cell"/> (call on every Position change). Appended/Truncated: carry on;
        /// Stowed: the end is back on the reel (Stored, a Move/Deploy order is done); Stretched: the hose is at full stretch,
        /// the end drops at the last cell that fitted and the order is cleared. The S3 driver ends its job on Stowed or
        /// Stretched. Unchanged when this pawn is not the carrier.</summary>
        public TrailStep CarrierStep(Pawn p, IntVec3 cell)
        {
            if (carry != HoseCarryState.Carrying || carrier != p || p == null || Hoses == null) return TrailStep.Unchanged;
            CordWorld w = Hoses.World();
            HoseTrail t = TrailOf(w);
            TrailStep r = t.Step(new Cell(cell.x, cell.z), w);
            if (r == TrailStep.Unchanged) return r;
            trail.Clear();
            foreach (Cell c in t.Cells) trail.Add(new IntVec3(c.X, 0, c.Z));
            if (r == TrailStep.Stowed)
            {
                trail.Clear();
                carrier = null;
                pending = HosePendingOrder.None;
                pendingAt = IntVec3.Invalid;
                SetCarry(HoseCarryState.Stored);
            }
            else if (r == TrailStep.Stretched)
            {
                far = trail[trail.Count - 1];
                carrier = null;
                pending = HosePendingOrder.None;
                pendingAt = IntVec3.Invalid;
                SetCarry(HoseCarryState.Dropped);
                if (parent.Faction == Faction.OfPlayer)
                    Messages.Message("Hose at full stretch at " + far + ": this reel holds " + MaxLength.ToString("0") + " cells of hose.",
                        new LookTargets(parent), MessageTypeDefOf.RejectInput, false);
            }
            HoseChanged();
            return r;
        }

        /// <summary>The carrier sets the end down at (or couples it to) target: Carrying -> Laid, order cleared. The target
        /// cell is stepped onto the trail first (a Touch arrival stands beside it; water, a tank side, a relay intake).</summary>
        public bool FinishCarry(Pawn p, IntVec3 target)
        {
            if (carry != HoseCarryState.Carrying || carrier != p || p == null) return false;
            if (target.IsValid) CarrierStep(p, target);
            if (carry != HoseCarryState.Carrying) return carry == HoseCarryState.Laid;
            far = trail[trail.Count - 1];
            carrier = null;
            pending = HosePendingOrder.None;
            pendingAt = IntVec3.Invalid;
            SetCarry(HoseCarryState.Laid);
            HoseChanged();
            return true;
        }

        /// <summary>Any interrupt: the end drops at the trail's last cell (Carrying -> Dropped). Idempotent: acts only when
        /// <paramref name="p"/> is the carrier (null = whoever holds it: the holder check, a cancel). keepPending: the
        /// order survives so an idle colonist resumes it (design section 2); false clears it (cancel, unreachable target).</summary>
        public bool DropCarry(Pawn p, bool keepPending = true)
        {
            if (carry != HoseCarryState.Carrying || (p != null && carrier != p)) return false;
            carrier = null;
            if (!keepPending) { pending = HosePendingOrder.None; pendingAt = IntVec3.Invalid; }
            if (trail.Count == 0) { SetCarry(HoseCarryState.Stored); HoseChanged(); return true; }
            far = trail[trail.Count - 1];
            SetCarry(HoseCarryState.Dropped);
            HoseChanged();
            return true;
        }

        /// <summary>The winder starts at the reel: Laid/Dropped -> Retracting. Idempotent for the current winder.</summary>
        public bool BeginWind(Pawn p)
        {
            if (p == null) return false;
            if (carry == HoseCarryState.Retracting) return carrier == p;
            HoseCarryState? n = HoseCarryTable.Next(carry, HoseCarryEvent.Wind);
            if (n == null) return false;
            MaterializeTrail();
            carrier = p;
            wound = 0f;
            SetCarry(n.Value);
            HoseChanged();
            return true;
        }

        /// <summary>Wind <paramref name="cells"/> in. True when the hose is fully on the reel (Stored, order cleared).</summary>
        public bool WindBy(Pawn p, float cells)
        {
            if (carry != HoseCarryState.Retracting || carrier != p) return carry == HoseCarryState.Stored;
            wound += System.Math.Max(0f, cells);
            if (wound + 1e-4f < TrailLength()) return false;
            ReelIn();
            return true;
        }

        /// <summary>The winder was interrupted: Retracting -> Dropped with the trail shortened by what was wound.</summary>
        public bool StopWind(Pawn p)
        {
            if (carry != HoseCarryState.Retracting || (p != null && carrier != p)) return false;
            RM_MapComponent_Hoses comp = Hoses;
            if (comp != null && trail.Count > 0)
            {
                CordWorld w = comp.World();
                HoseTrail t = TrailOf(w);
                t.ShortenBy(wound, w);
                trail.Clear();
                foreach (Cell c in t.Cells) trail.Add(new IntVec3(c.X, 0, c.Z));
            }
            carrier = null;
            wound = 0f;
            if (trail.Count == 0) { ReelIn(); return true; }
            far = trail[trail.Count - 1];
            SetCarry(HoseCarryState.Dropped);
            HoseChanged();
            return true;
        }

        /// <summary>Design section 5 b (the RopingTick pattern), run every 30 ticks by the map component: the holder of a carried
        /// or winding hose must still be holding it, else the end drops (or the winding stops) where it is.</summary>
        public void HolderCheck()
        {
            if (carry == HoseCarryState.Carrying)
            {
                if (!HolderValid(carrier)) DropCarry(null, true);
            }
            else if (carry == HoseCarryState.Retracting)
            {
                // S2 has no auto-wind: a winder-less Retracting reel (only a damaged save) reels in at once, as the
                // corridor auto-retract does today
                if (carrier == null) ReelIn();
                else if (!HolderValid(carrier)) StopWind(null);
            }
        }

        public bool HolderValid(Pawn p)
        {
            if (p == null || p.Dead || !p.Spawned || p.Map != parent.Map || p.Downed) return false;
            if (p.InMentalState && p.MentalStateDef != MentalStateDefOf.Roaming) return false;
            if (p.IsBurning() || !p.Awake()) return false;
            return HoldsReel == null || HoldsReel(p, this);
        }

        /// <summary>Null when laid, else why not (also the gizmo's reject message). Since the carry stage (S2) this is the DEV
        /// instant lay and the probe's staging path: the hose lies on the PLANNED route (empty trail), any order is cleared.</summary>
        public string TryLay(IntVec3 target)
        {
            if (carry == HoseCarryState.Carrying || carry == HoseCarryState.Retracting) return "a colonist is handling this hose";
            string why = ResolveTarget(ref target);
            if (why != null) return why;
            far = target;
            trail.Clear();
            carrier = null;
            wound = 0f;
            pending = HosePendingOrder.None;
            pendingAt = IntVec3.Invalid;
            SetCarry(HoseCarryState.Laid);
            lastRetractReason = null;
            lastRetractNeed = -1f;
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
            float need = why == "route too long" ? NeedFor(far) : -1f;
            ReelIn();
            lastRetractReason = why;
            lastRetractNeed = need;
            lastRetractTick = Find.TickManager?.TicksGame ?? 0;
            if (parent.Spawned && parent.Faction == Faction.OfPlayer)
                Messages.Message("Hose reeled in: " + Explain(why, need) + " (an obstacle cut its route and no other route fits the hose).",
                    new LookTargets(parent), MessageTypeDefOf.NegativeEvent, false);
        }

        /// <summary>Round 4 (owner, station 23: "the hose disappeared"): the hose a route to target needs, pulled taut,
        /// with the route margin (cells), or -1.</summary>
        public float NeedFor(IntVec3 target)
        {
            RM_MapComponent_Hoses comp = parent.Spawned ? parent.Map.GetComponent<RM_MapComponent_Hoses>() : null;
            if (comp == null || !target.IsValid) return -1f;
            double len = HoseMath.RouteLength(comp.World(), Rect, new Cell(target.x, target.z), -1, false);   // B2: as CheckInstall
            return len < 0 ? -1f : (float)(len * HoseMath.RouteMargin);
        }

        /// <summary>A reason with the numbers that make it readable: "route too long: the way there needs about 36 cells of
        /// hose, this reel holds 40".</summary>
        public string Explain(string why, float need) =>
            why == "route too long" && need > 0
                ? why + ": the way there needs about " + Mathf.CeilToInt(need) + " cells of hose, this reel holds " + MaxLength.ToString("0")
                : why;

        public void ReelIn()
        {
            SetCarry(HoseCarryState.Stored);
            trail.Clear();
            carrier = null;
            wound = 0f;
            pending = HosePendingOrder.None;
            pendingAt = IntVec3.Invalid;
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

        /// <summary>A cell targeter whose click runs <paramref name="order"/>; a refusal is told with the reason's numbers.</summary>
        private void TargetCell(string refusal, System.Func<IntVec3, string> order)
        {
            var tp = new TargetingParameters { canTargetLocations = true, canTargetPawns = false, canTargetBuildings = true, canTargetItems = false };
            Find.Targeter.BeginTargeting(tp, t =>
            {
                string why = order(t.Cell);
                if (why != null) Messages.Message(refusal + Explain(why, why == "route too long" ? NeedFor(t.Cell) : -1f) + ".", MessageTypeDefOf.RejectInput, false);
            }, caster: (Pawn)null);
        }

        /// <summary>Owner 2026-10-05 ("reels don't have a choose style option"): restyle this reel in place. The hose draws in the
        /// reel's look every frame (HoseStyles.HoseLook), so only the reel's own graphic needs refreshing.</summary>
        public void SetLook(string look)
        {
            ThingStyleDef sd = Aerial.StylePicker.StyleFor(parent.def, look);
            if (sd == null) return;
            parent.SetStyleDef(sd);
            parent.Notify_ColorChanged();
        }

        /// <summary>Owner ruling 2026-10-04: the player path is a colonist doing it (orders here, jobs in S3); the instant
        /// lay / reel-in are DEBUG actions under Prefs.DevMode only, with no setting that restores them.</summary>
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
            if (!HoseSettings.enabled || parent.Faction != Faction.OfPlayer) yield break;
            string relayNote = "\n\nTo go farther, build another hose reel out in the field and run this hose onto it: the hose couples to that reel's side, " +
                               "and that reel runs its own " + MaxLength.ToString("0") + "-cell hose onward. Whatever flows into a relay reel flows on through its hose.";
            if (carry == HoseCarryState.Stored)
                yield return new Command_Action
                {
                    defaultLabel = "Deploy hose",
                    defaultDesc = "Order a colonist to carry the hose's end out to a cell up to " + MaxLength.ToString("0") + " cells away. " +
                                  "The hose unrolls behind them along the way they walk." + relayNote,
                    icon = IconLay,
                    action = () => TargetCell("Cannot deploy the hose there: ", OrderDeploy)
                };
            if (laid)
            {
                yield return new Command_Action
                {
                    defaultLabel = "Move hose end",
                    defaultDesc = "Order a colonist to pick up the hose's free end and carry it to another cell. Choose a cell beside the reel to bring the end back.",
                    icon = IconLay,
                    action = () => TargetCell("Cannot move the hose end there: ", OrderMove)
                };
                yield return new Command_Action
                {
                    defaultLabel = "Retract hose",
                    defaultDesc = "Order a colonist to go to the reel and wind the hose back in.",
                    icon = IconReel,
                    action = () => OrderRetract()
                };
            }
            if (Aerial.StylePicker.IsStyled(parent.def))
                yield return new Command_Action
                {
                    defaultLabel = "Choose style",
                    defaultDesc = "Change how this reel and its hose look (scrapper, industrial, modern, futuristic). Free and instant; it changes art only, never cost or function.",
                    icon = parent.StyleDef?.UIIcon ?? IconLay,
                    action = () =>
                    {
                        string cur = Aerial.StylePicker.LookOfThing(parent);
                        var opts = new List<FloatMenuOption>();
                        foreach (string look in Aerial.AerialStyles.Looks)
                        {
                            ThingStyleDef sd = Aerial.StylePicker.StyleFor(parent.def, look);
                            if (sd == null) continue;
                            string l = look;
                            opts.Add(new FloatMenuOption(look + (look == cur ? " (current)" : ""), () => SetLook(l), sd.UIIcon ?? IconLay, Color.white));
                        }
                        Find.WindowStack.Add(new FloatMenu(opts));
                    }
                };
            if (pending != HosePendingOrder.None || carry == HoseCarryState.Carrying || (carry == HoseCarryState.Retracting && carrier != null))
                yield return new Command_Action
                {
                    defaultLabel = "Cancel hose order",
                    defaultDesc = "Forget the hose order. A colonist carrying the end drops it where they stand; one winding it in stops.",
                    icon = IconEnd,
                    action = CancelOrder
                };
            yield return new Command_Action
            {
                defaultLabel = end == HoseEnd.Nozzle ? "Free end: nozzle" : end == HoseEnd.EndCap ? "Free end: end cap" : "Free end: open",
                defaultDesc = "Switch what sits on the hose's free end: open (plain hose end), nozzle or end cap.",
                icon = end == HoseEnd.Nozzle ? IconLay : IconEnd,
                action = () => end = end == HoseEnd.Open ? HoseEnd.Nozzle : end == HoseEnd.Nozzle ? HoseEnd.EndCap : HoseEnd.Open
            };
            if (!Prefs.DevMode) yield break;
            if (HoseCarryTable.Next(carry, HoseCarryEvent.DevLay) != null)
                yield return new Command_Action
                {
                    defaultLabel = "DEV: lay hose instantly",
                    defaultDesc = "Debug action: lay the hose at once on its planned route, no colonist needed.",
                    icon = IconLay,
                    action = () => TargetCell("Cannot lay the hose there: ", DevLayInstant)
                };
            if (carry != HoseCarryState.Stored && HoseCarryTable.Next(carry, HoseCarryEvent.DevReelIn) != null)
                yield return new Command_Action
                {
                    defaultLabel = "DEV: reel in instantly",
                    defaultDesc = "Debug action: wind the hose back onto the reel at once.",
                    icon = IconReel,
                    action = ReelIn
                };
            if (laid)
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
            RM_MapComponent_Hoses comp = parent.Spawned ? parent.Map.GetComponent<RM_MapComponent_Hoses>() : null;
            List<CompHoseReel> feeders = comp?.FeedersOf(this) ?? new List<CompHoseReel>();
            string conn = p != null ? "Connected to " + p.LabelShort + " (" + portKind.ToString().ToLower() + ")."
                        : feeders.Count > 0 ? "Relay: fed by the hose from the reel at " + feeders[0].parent.Position + (feeders.Count > 1 ? " (+" + (feeders.Count - 1) + " more)" : "") + "."
                        : "Not connected: build it beside a pipe or tank, or lay another reel's hose onto it.";
            string order = pending == HosePendingOrder.Deploy ? "\nOrdered: deploy the hose to " + pendingAt + "."
                         : pending == HosePendingOrder.Move ? "\nOrdered: move the hose end to " + pendingAt + "."
                         : pending == HosePendingOrder.Retract ? "\nOrdered: retract the hose." : "";
            if (carry == HoseCarryState.Carrying)
                return conn + "\nHose being carried" + (carrier != null ? " by " + carrier.LabelShort : "") + ", " + TrailLength().ToString("0") + " of " + MaxLength.ToString("0") + " cells out." + order;
            if (carry == HoseCarryState.Retracting)
                return conn + "\nHose being wound in" + (carrier != null ? " by " + carrier.LabelShort : "") + "." + order;
            if (!laid) return conn + "\nHose reeled in." + (lastRetractReason != null ? " Retracted automatically: " + Explain(lastRetractReason, lastRetractNeed) + "." : "") + order;
            if (carry == HoseCarryState.Dropped)
                return conn + "\nHose end dropped at " + far + ", " + TrailLength().ToString("0") + " of " + MaxLength.ToString("0") + " cells out." + order;
            string len = lay != null ? ", " + lay.FlatLen.ToString("0") + " of " + MaxLength.ToString("0") + " cells" : "";
            CompHoseReel relay = comp?.RelayOf(this);
            string to = relay != null ? "the relay reel at " + relay.parent.Position : far.ToString();
            return conn + "\nHose laid to " + to + len + " (" + sm.State.ToString().ToLower() + ")." + order;
        }
    }
}
