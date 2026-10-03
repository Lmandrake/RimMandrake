using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.KeelHoist
{
    // HOIST_SHIP_PART_BUILD_1 — the keel hoist, ship form (design §2a-§2d).
    //
    // A MapPortal whose GetOtherMap()/GetDestinationLocation() (both virtual, RimSage-read) point where its cable
    // is: beside another MapPortal's exit below (a cave mouth, a dungeon entrance: target kind 1), or at a cell on
    // this map that nobody can walk to from the hoist (target kind 2). The whole vanilla load pipeline
    // (Dialog_EnterPortal, HaulToPortal, LoadAndEnterPortal) is reused; only arrival differs:
    //   * TRANSIT IS A HIDDEN TIMER. Hauled cargo lands in RM_HoistContainerProxy, which puts it in this hoist's
    //     transit owner instead of dropping it below. A rider who walks in is spawned below by JobDriver_EnterPortal
    //     and lifted back into transit on the next tick (despawning inside OnEntered would break the job's own
    //     post-spawn code). After cycleTicks (scaled by mass) each thing spawns at its destination.
    //   * DOWNED STRANGERS ARRIVE AS PRISONERS, DOWNED WILD BEASTS ARRIVE BOUND (RM_HoistRestraint, setting hours).
    //     They get into the dialog through a postfix scoped to RM_KeelHoist (Patch_DialogEnterPortal), never
    //     through the shared AllSendablePawns.
    //   * "Raise cradle" lifts what stands within 1.5 cells of the cradle below back up to the hoist.
    //   * Every arrival is written to the manifest (ITab_HoistManifest): nothing leaves without a record.
    // No pocket map is ever generated: GetOtherMap never calls the base.
    [StaticConstructorOnStartup]
    public class RM_KeelHoist : MapPortal, IThingHolder
    {
        private static readonly Texture2D LowerTex = ContentFinder<Texture2D>.Get("UI/Commands/LaunchShip");
        private static readonly Texture2D ReelTex = ContentFinder<Texture2D>.Get("UI/Designators/Cancel");
        private static readonly Texture2D RaiseTex = ContentFinder<Texture2D>.Get("UI/Commands/PodEject");

        public const int BaseCycleTicks = 625;   // a quarter hour for a weightless load
        public const float CradleRadius = 1.5f;

        public MapPortal targetPortal;
        public RM_SealedHolder targetHolder;   // HOIST_FIXED_SITE_FRAMES_1: target kind 3, a sealed holder feature
        public IntVec3 targetCell = IntVec3.Invalid;

        private readonly RM_HoistTransitHolder transitHolder;
        private ThingOwner<Thing> transit;
        private List<int> arriveAt = new List<int>();
        private List<bool> goingUp = new List<bool>();
        private List<string> fromLabel = new List<string>();
        private readonly List<Pawn> pendingRiders = new List<Pawn>();

        public List<RM_HoistManifestEntry> manifest = new List<RM_HoistManifestEntry>();

        public RM_KeelHoist()
        {
            transitHolder = new RM_HoistTransitHolder(this);
            transit = new ThingOwner<Thing>(transitHolder);
        }

        public ThingOwner<Thing> TransitOwner => transit;

        // MapPortal's GetChildHolders is empty and non-virtual; re-implementing the interface makes pawns on the
        // cable reachable through the holder tree (colonist counts, world-pawn GC), as a transporter's are.
        void IThingHolder.GetChildHolders(List<IThingHolder> outChildren)
        {
            outChildren.Add(transitHolder);
        }

        public CompPowerTrader Power => GetComp<CompPowerTrader>();
        public bool Powered => Power == null || Power.PowerOn;
        public bool CableDown => targetPortal != null || targetHolder != null || targetCell.IsValid;

        /// <summary>A site's fixed head-frame: its cable is set by the genstep and never moved or reeled.</summary>
        public virtual bool FixedCable => false;
        public int InTransitCount => transit.Count;
        public IEnumerable<Thing> InTransit => transit;

        public override string EnterString => "Lower by keel hoist";
        public override string EnteringString => "Riding the keel hoist";

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref targetPortal, "targetPortal");
            Scribe_References.Look(ref targetHolder, "targetHolder");
            Scribe_Values.Look(ref targetCell, "targetCell", IntVec3.Invalid);
            Scribe_Deep.Look(ref transit, "transit", transitHolder);
            Scribe_Collections.Look(ref arriveAt, "arriveAt", LookMode.Value);
            Scribe_Collections.Look(ref goingUp, "goingUp", LookMode.Value);
            Scribe_Collections.Look(ref fromLabel, "fromLabel", LookMode.Value);
            Scribe_Collections.Look(ref manifest, "manifest", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                transit = transit ?? new ThingOwner<Thing>(transitHolder);
                arriveAt = arriveAt ?? new List<int>();
                goingUp = goingUp ?? new List<bool>();
                fromLabel = fromLabel ?? new List<string>();
                manifest = manifest ?? new List<RM_HoistManifestEntry>();
                while (arriveAt.Count < transit.Count) arriveAt.Add(0);
                while (goingUp.Count < transit.Count) goingUp.Add(false);
                while (fromLabel.Count < transit.Count) fromLabel.Add("?");
            }
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            containerProxy = new RM_HoistContainerProxy { portal = this };
            if (!respawningAfterLoad && !FixedCable)
            {
                // Built, or carried here by the ship: a cable from another place cannot still be down.
                targetPortal = null;
                targetHolder = null;
                targetCell = IntVec3.Invalid;
            }
        }

        public override Map GetOtherMap()
        {
            return targetPortal != null && targetPortal.Spawned ? targetPortal.GetOtherMap() : Map;
        }

        public override IntVec3 GetDestinationLocation()
        {
            if (targetPortal != null && targetPortal.Spawned)
            {
                return targetPortal.GetDestinationLocation();
            }
            if (targetHolder != null && targetHolder.Spawned)
            {
                return targetHolder.Position;
            }
            return targetCell.IsValid ? targetCell : Position;
        }

        public override bool IsEnterable(out string reason)
        {
            if (!KeelHoistSettings.masterEnabled)
            {
                reason = "The keel hoist is switched off in Mod Settings.";
                return false;
            }
            if (!CableDown)
            {
                reason = "Lower the cable first.";
                return false;
            }
            if (!Powered)
            {
                reason = "No power.";
                return false;
            }
            return base.IsEnterable(out reason);
        }

        public override void OnEntered(Pawn pawn)
        {
            // The base would read def.portal letters and exit.Map; this portal has no exit of its own.
            Notify_ThingAdded(pawn);
            beenEntered = true;
            if (!KeelHoistSettings.colonistsMayRide && pawn.IsColonist && !pawn.Downed)
            {
                return;   // the rider already stands below; with riding off it is not held in transit
            }
            pendingRiders.Add(pawn);
        }

        public static int CycleTicksFor(Thing t)
        {
            float mass = t is Pawn p ? p.GetStatValue(StatDefOf.Mass) : t.GetStatValue(StatDefOf.Mass) * t.stackCount;
            return Mathf.Max(60, Mathf.RoundToInt(BaseCycleTicks * KeelHoistSettings.cycleTimeMultiplier * (1f + mass / 50f)));
        }

        public void BeginTransit(Thing t, bool up, string from)
        {
            if (t.Spawned)
            {
                if (t is Pawn p)
                {
                    p.DeSpawnOrDeselect();
                }
                else
                {
                    t.DeSpawn();
                }
            }
            t.holdingOwner?.Remove(t);
            if (!transit.TryAdd(t, canMergeWithExistingStacks: false))
            {
                // Could not hold it: put it straight back where the hoist stands rather than lose it.
                GenSpawn.Spawn(t, CellFinder.StandableCellNear(Position, Map, 3f), Map);
                return;
            }
            arriveAt.Add(Find.TickManager.TicksGame + CycleTicksFor(t));
            goingUp.Add(up);
            fromLabel.Add(from);
        }

        protected override void Tick()
        {
            base.Tick();
            if (pendingRiders.Count > 0)
            {
                foreach (Pawn rider in pendingRiders.ToList())
                {
                    if (rider.Spawned && !rider.Dead)
                    {
                        BeginTransit(rider, up: false, from: Map.Parent?.LabelCap ?? "the ship");
                    }
                }
                pendingRiders.Clear();
            }

            if (targetPortal != null && (!targetPortal.Spawned || targetPortal.Map != Map))
            {
                targetPortal = null;   // the mouth collapsed or the ship moved: the cable has nothing to hang on
            }
            if (targetHolder != null && (!targetHolder.Spawned || targetHolder.Map != Map))
            {
                targetHolder = null;
            }

            int now = Find.TickManager.TicksGame;
            for (int i = transit.Count - 1; i >= 0; i--)
            {
                if (i < arriveAt.Count && arriveAt[i] > now)
                {
                    continue;
                }
                Arrive(i);
            }
        }

        private void Arrive(int i)
        {
            Thing t = transit[i];
            bool up = i < goingUp.Count && goingUp[i];
            string from = i < fromLabel.Count ? fromLabel[i] : "?";
            Map map = up ? Map : GetOtherMap();
            IntVec3 cell = up ? (InteractionCell.IsValid && InteractionCell.InBounds(Map) ? InteractionCell : Position) : GetDestinationLocation();
            if (map == null || !cell.IsValid || !cell.InBounds(map))
            {
                map = Map;
                cell = Position;
            }

            if (t is Pawn pawn && !cell.Standable(map))
            {
                IntVec3 near = CellFinder.StandableCellNear(cell, map, 5f);
                if (near.IsValid)
                {
                    cell = near;
                }
            }

            Thing dropped = null;
            bool intoHolder = !up && targetHolder != null && targetHolder.Spawned && t is Pawn sunk
                              && !(sunk.IsColonist && !sunk.Downed);
            if (intoHolder)
            {
                transit.Remove(t);
                if (targetHolder.Accept((Pawn)t))
                {
                    dropped = t;
                }
                else
                {
                    GenSpawn.Spawn(t, CellFinder.StandableCellNear(cell, map, 5f), map);
                    dropped = t;
                    intoHolder = false;
                }
            }
            else
            {
                transit.TryDrop(t, cell, map, ThingPlaceMode.Near, out dropped);
            }
            arriveAt.RemoveAt(i);
            goingUp.RemoveAt(i);
            fromLabel.RemoveAt(i);
            if (dropped == null)
            {
                return;
            }

            bool captured = !intoHolder && dropped is Pawn p && TryCapture(p);
            manifest.Add(new RM_HoistManifestEntry
            {
                tick = Find.TickManager.TicksGame,
                label = dropped.LabelCap,
                up = up,
                from = from,
                to = intoHolder ? targetHolder.LabelCap.ToString() : (map.Parent?.LabelCap ?? map.ToString()),
                captured = captured,
            });
            if (manifest.Count > 200)
            {
                manifest.RemoveAt(0);
            }
        }

        public static bool TryCapture(Pawn p)
        {
            if (!KeelHoistSettings.downedStrangersAndBeasts || p.Dead || p.Faction == Faction.OfPlayer)
            {
                return false;
            }
            if (p.RaceProps.Humanlike)
            {
                if (p.IsPrisonerOfColony || p.IsSlaveOfColony || p.guest == null)
                {
                    return false;
                }
                p.guest.CapturedBy(Faction.OfPlayer);
                return true;
            }
            if (p.RaceProps.Animal && p.Faction == null)
            {
                Hediff h = HediffMaker.MakeHediff(KeelHoistDefOf.RM_HoistRestraint, p);
                HediffComp_Disappears gone = h.TryGetComp<HediffComp_Disappears>();
                if (gone != null)
                {
                    gone.ticksToDisappear = Mathf.RoundToInt(KeelHoistSettings.restraintHours * GenDate.TicksPerHour);
                }
                p.health.AddHediff(h);
                return true;
            }
            return false;
        }

        public bool IsValidCableTarget(LocalTargetInfo target, out string reason)
        {
            reason = null;
            float range = KeelHoistSettings.cableRange;
            if (target.Thing is MapPortal portal)
            {
                if (portal is RM_KeelHoist || portal.Map != Map)
                {
                    reason = "The cable cannot hang on another hoist.";
                    return false;
                }
                if (portal.Position.DistanceTo(Position) > range + portal.def.size.x)
                {
                    reason = "Out of the cable's reach.";
                    return false;
                }
                return true;
            }
            if (target.Thing is RM_SealedHolder holder)
            {
                if (holder.Map != Map || holder.Position.DistanceTo(Position) > range + holder.def.size.x)
                {
                    reason = "Out of the cable's reach.";
                    return false;
                }
                return true;   // lowering into it is allowed; lifting out waits for its gate (RaiseCradle)
            }
            IntVec3 c = target.Cell;
            if (!c.IsValid || !c.InBounds(Map) || c.DistanceTo(Position) > range)
            {
                reason = "Out of the cable's reach.";
                return false;
            }
            if (!c.Standable(Map))
            {
                reason = "Nothing could stand there.";
                return false;
            }
            IntVec3 from = InteractionCell.IsValid && InteractionCell.InBounds(Map) ? InteractionCell : Position;
            if (Map.reachability.CanReach(from, c, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)))
            {
                reason = "Pawns can walk there; the cable is for places walking does not reach.";
                return false;
            }
            return true;
        }

        public void LowerCableTo(LocalTargetInfo target)
        {
            targetPortal = null;
            targetHolder = null;
            targetCell = IntVec3.Invalid;
            if (target.Thing is MapPortal portal)
            {
                targetPortal = portal;
            }
            else if (target.Thing is RM_SealedHolder holder)
            {
                targetHolder = holder;
            }
            else
            {
                targetCell = target.Cell;
            }
        }

        public void ReelIn()
        {
            targetHolder = null;
            targetPortal = null;
            targetCell = IntVec3.Invalid;
        }

        public void RaiseCradle()
        {
            if (targetHolder != null && targetHolder.Spawned)
            {
                if (!targetHolder.GateOpen(out string why))
                {
                    Messages.Message(why, targetHolder, MessageTypeDefOf.RejectInput, historical: false);
                    return;
                }
                List<Pawn> held = targetHolder.TakeAll();
                foreach (Pawn p in held)
                {
                    BeginTransit(p, up: true, from: targetHolder.LabelCap);
                }
                Messages.Message(held.Count == 0 ? targetHolder.LabelCap + " is empty." : "The cradle rises out of " + targetHolder.Label + " with " + held.Count + ".",
                    this, MessageTypeDefOf.NeutralEvent, historical: false);
                return;
            }
            Map below = GetOtherMap();
            IntVec3 cradle = GetDestinationLocation();
            if (below == null || !cradle.IsValid)
            {
                return;
            }
            string from = below.Parent?.LabelCap ?? "below";
            var lift = new List<Thing>();
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(cradle, below, CradleRadius, true))
            {
                if (t == this || t is MapPortal || t.def.category == ThingCategory.Building)
                {
                    continue;
                }
                if (t is Pawn p)
                {
                    bool ours = p.Faction == Faction.OfPlayer || p.IsPrisonerOfColony || p.IsSlaveOfColony;
                    bool rider = ours && (KeelHoistSettings.colonistsMayRide || p.Downed || !p.IsColonist);
                    bool capturable = p.Downed && KeelHoistSettings.downedStrangersAndBeasts;
                    if (rider || capturable)
                    {
                        lift.Add(p);
                    }
                }
                else if (t.def.EverHaulable)
                {
                    lift.Add(t);
                }
            }
            foreach (Thing t in lift)
            {
                BeginTransit(t, up: true, from: from);
            }
            Messages.Message(lift.Count == 0 ? "Nothing on the cradle to raise." : "The cradle rises with " + lift.Count + " load(s).",
                this, MessageTypeDefOf.NeutralEvent, historical: false);
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }

            if (!CableDown && !FixedCable)
            {
                var lower = new Command_Action
                {
                    defaultLabel = "Lower cable...",
                    defaultDesc = "Drop the cable onto a cave mouth or dungeon entrance within reach, or onto a cell that "
                                + "nobody can walk to from here (the floor of a pit, a cliff shelf).",
                    icon = LowerTex,
                    action = () => Find.Targeter.BeginTargeting(new TargetingParameters
                    {
                        canTargetBuildings = true,
                        canTargetLocations = true,
                        canTargetPawns = false,
                        canTargetItems = false,
                        validator = t => IsValidCableTarget(t.HasThing ? new LocalTargetInfo(t.Thing) : new LocalTargetInfo(t.Cell), out _),
                    }, LowerCableTo, null, t => IsValidCableTarget(t, out _)),
                };
                if (!KeelHoistSettings.masterEnabled)
                {
                    lower.Disable("The keel hoist is switched off in Mod Settings.");
                }
                else if (!Powered)
                {
                    lower.Disable("No power.");
                }
                yield return lower;
            }
            if (CableDown)
            {
                if (!FixedCable)
                {
                var reel = new Command_Action
                {
                    defaultLabel = "Reel in cable",
                    defaultDesc = "Bring the cable up. The ship cannot launch while it is down.",
                    icon = ReelTex,
                    action = ReelIn,
                };
                if (transit.Count > 0)
                {
                    reel.Disable("Cargo is still on the cable.");
                }
                else if (LoadInProgress)
                {
                    reel.Disable("Loading is in progress; cancel it first.");
                }
                yield return reel;
                }

                var raise = new Command_Action
                {
                    defaultLabel = "Raise cradle",
                    defaultDesc = "Lift whatever stands on the cradle below (items, our people, the downed) up to the hoist.",
                    icon = RaiseTex,
                    action = RaiseCradle,
                };
                if (!KeelHoistSettings.masterEnabled)
                {
                    raise.Disable("The keel hoist is switched off in Mod Settings.");
                }
                else if (!Powered)
                {
                    raise.Disable("No power.");
                }
                yield return raise;
            }
        }

        public override void DrawExtraSelectionOverlays()
        {
            base.DrawExtraSelectionOverlays();
            if (targetPortal != null && targetPortal.Spawned)
            {
                GenDraw.DrawLineBetween(DrawPos, targetPortal.DrawPos, SimpleColor.White);
            }
            else if (targetHolder != null && targetHolder.Spawned)
            {
                GenDraw.DrawLineBetween(DrawPos, targetHolder.DrawPos, SimpleColor.White);
            }
            else if (targetCell.IsValid)
            {
                GenDraw.DrawLineBetween(DrawPos, targetCell.ToVector3Shifted(), SimpleColor.White);
            }
            else
            {
                GenDraw.DrawRadiusRing(Position, KeelHoistSettings.cableRange);
            }
        }

        public override string GetInspectString()
        {
            var lines = new List<string>();
            string baseText = base.GetInspectString();
            if (!baseText.NullOrEmpty())
            {
                lines.Add(baseText);
            }
            if (targetPortal != null)
            {
                lines.Add("Cable down: " + targetPortal.LabelCap);
            }
            else if (targetHolder != null)
            {
                lines.Add("Cable down: " + targetHolder.LabelCap);
            }
            else if (targetCell.IsValid)
            {
                lines.Add("Cable down: to the cell at " + targetCell.x + ", " + targetCell.z);
            }
            else
            {
                lines.Add("Cable reeled in");
            }
            if (transit.Count > 0)
            {
                int next = arriveAt.Count > 0 ? arriveAt.Min() - Find.TickManager.TicksGame : 0;
                lines.Add("On the cable: " + transit.Count + " (next arrives in " + Mathf.Max(0, next).ToStringTicksToPeriod() + ")");
            }
            if (KeelHoistSettings.openLineMeter && Map != null)
            {
                RM_MapComponent_OpenLine line = Map.GetComponent<RM_MapComponent_OpenLine>();
                if (line != null && line.level > 0f)
                {
                    lines.Add("Open line: " + line.level.ToString("0.0"));
                }
            }
            return string.Join("\n", lines);
        }

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            // Whatever is on the cable falls out where the hoist stood; nothing vanishes.
            if (Spawned && transit.Count > 0)
            {
                Map map = Map;
                IntVec3 at = Position;
                transit.TryDropAll(at, map, ThingPlaceMode.Near);
            }
            base.Destroy(mode);
        }
    }

    public class RM_HoistTransitHolder : IThingHolder
    {
        private readonly RM_KeelHoist hoist;

        public RM_HoistTransitHolder(RM_KeelHoist hoist)
        {
            this.hoist = hoist;
        }

        public IThingHolder ParentHolder => hoist;

        public ThingOwner GetDirectlyHeldThings() => hoist.TransitOwner;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }
    }

    public class RM_HoistContainerProxy : PortalContainerProxy
    {
        public override bool TryAdd(Thing item, bool canMergeWithExistingStacks = true)
        {
            var hoist = (RM_KeelHoist)portal;
            portal.Notify_ThingAdded(item);
            hoist.BeginTransit(item, up: false, from: hoist.Map?.Parent?.LabelCap ?? "the ship");
            return true;
        }
    }

    public class RM_HoistManifestEntry : IExposable
    {
        public int tick;
        public string label;
        public bool up;
        public string from;
        public string to;
        public bool captured;

        public void ExposeData()
        {
            Scribe_Values.Look(ref tick, "tick");
            Scribe_Values.Look(ref label, "label");
            Scribe_Values.Look(ref up, "up");
            Scribe_Values.Look(ref from, "from");
            Scribe_Values.Look(ref to, "to");
            Scribe_Values.Look(ref captured, "captured");
        }
    }
}
