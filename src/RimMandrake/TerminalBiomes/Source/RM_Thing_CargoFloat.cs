using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1 §5 rung 2. "A buildable lattice-timber-
    // and-bladder raft, minified-container-shaped... load it on the bank,
    // push it in (a job), it rides the item drift whole and the weir
    // arrests it intact." Build-time simplification, flagged: "push it in
    // (a job)" ships here as a Gizmo on the float itself rather than a new
    // WorkGiver/JobDriver — loading is likewise automatic (nearby loose
    // haulables within one cell) rather than a separate load UI. Launching
    // pushes it onto an adjacent current cell (CARGO_FLOAT_LAUNCH_PUSH_1). Once
    // launched, this Thing is category Item, not Building, so
    // RM_MapComponent_ChannelCurrent's normal item-drift path (half the
    // pawn rate, per §1.3) picks it up with NO special-casing on the
    // component's side — the float rides the same mechanism as any other
    // dropped haulable. Its own Tick() only watches for the moment it gets
    // caught (a weir) or sinks, at which point it unloads intact — "a float
    // in the sink is recoverable unspoiled" because nothing in this mod
    // ever destroys or scavenges anything sitting in the basin (see
    // RM_MapComponent_ChannelCurrent.ArriveAtSink's own comment).
    public class RM_Thing_CargoFloat : ThingWithComps, IThingHolder
    {
        private ThingOwner<Thing> container;
        private bool loaded;

        public RM_Thing_CargoFloat()
        {
            container = new ThingOwner<Thing>(this);
        }

        public ThingOwner GetDirectlyHeldThings()
        {
            return container ?? (container = new ThingOwner<Thing>(this));
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            // Loading accepts any haulable, including minified things and other
            // floats, which are holders themselves: hand them to the traversal.
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        protected override void Tick()
        {
            base.Tick();
            if (!loaded || !Spawned || Map == null)
            {
                return;
            }
            if (!this.IsHashIntervalTick(30))
            {
                return; // cheap: only worth checking a few times a second
            }
            if (GetDirectlyHeldThings().Count == 0)
            {
                loaded = false;
                return;
            }
            RM_MapComponent_ChannelCurrent current = Map.GetComponent<RM_MapComponent_ChannelCurrent>();
            bool caught = (current != null && current.IsSinkCell(Position)) || IsOnArresterHere();
            if (caught)
            {
                Unload();
            }
        }

        private bool IsOnArresterHere()
        {
            List<Thing> here = Position.GetThingList(Map);
            for (int i = 0; i < here.Count; i++)
            {
                if (here[i] != this && (here[i] as ThingWithComps)?.GetComp<RimMandrake.FlowWorks.Rivers.RM_CompRiverArrester>()?.Active == true)
                {
                    return true;
                }
            }
            return false;
        }

        private void Unload()
        {
            GetDirectlyHeldThings().TryDropAll(Position, Map, ThingPlaceMode.Near);
            if (GetDirectlyHeldThings().Count > 0)
            {
                return; // no room for everything yet: stay loaded and retry on the next check
            }
            loaded = false;
            Messages.Message("RM_CargoFloatArrived".Translate(LabelShortCap), new TargetInfo(Position, Map), MessageTypeDefOf.PositiveEvent);
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }
            if (!loaded)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RM_CargoFloatLoadLaunch".Translate(),
                    defaultDesc = "RM_CargoFloatLoadLaunchDesc".Translate(),
                    action = LoadAndLaunch,
                };
            }
        }

        private void LoadAndLaunch()
        {
            if (Map == null)
            {
                return;
            }
            // CARGO_FLOAT_LAUNCH_PUSH_1: the float has to go INTO the current. On a current cell it rides from where it
            // is; on the bank it is pushed onto an adjacent current cell; with neither, it refuses before loading.
            RM_MapComponent_ChannelCurrent current = Map.GetComponent<RM_MapComponent_ChannelCurrent>();
            if (!TryFindLaunchCell(current, out IntVec3 launch))
            {
                Messages.Message("RM_CargoFloatNoCurrent".Translate(), new TargetInfo(Position, Map), MessageTypeDefOf.RejectInput, historical: false);
                return;
            }
            // "within one cell" (the header's promise): its own cell and the eight around it.
            List<Thing> near = new List<Thing>();
            foreach (IntVec3 c in GenAdj.CellsOccupiedBy(this))
            {
                near.AddRange(c.GetThingList(Map));
            }
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this))
            {
                if (c.InBounds(Map))
                {
                    near.AddRange(c.GetThingList(Map));
                }
            }
            for (int i = 0; i < near.Count; i++)
            {
                Thing t = near[i];
                if (t != this && t.Spawned && t.def.EverHaulable && !(t is Pawn) && !(t is RM_Thing_CargoFloat))
                {
                    IntVec3 from = t.Position;
                    t.DeSpawn(DestroyMode.Vanish);
                    if (!GetDirectlyHeldThings().TryAdd(t))
                    {
                        GenPlace.TryPlaceThing(t, from, Map, ThingPlaceMode.Near); // never orphan an unspawned thing
                    }
                }
            }
            loaded = GetDirectlyHeldThings().Count > 0;
            if (!loaded)
            {
                Messages.Message("RM_CargoFloatEmpty".Translate(), MessageTypeDefOf.RejectInput, historical: false);
                return;
            }
            if (launch != Position)
            {
                Position = launch; // the push: the item-drift scan registers it on its next pass
            }
        }

        /// <summary>Its own cell when that already carries current; else an adjacent standable current cell that is
        /// neither the sink nor held by a weir. False when there is none.</summary>
        private bool TryFindLaunchCell(RM_MapComponent_ChannelCurrent current, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            if (current == null || !RM_TerminalBiomesSettings.ChannelCurrentActive)
            {
                return false;
            }
            if (current.HasCurrent(Position) && !current.IsSinkCell(Position) && !current.IsArrestedCell(Position))
            {
                cell = Position;
                return true;
            }
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this).InRandomOrder())
            {
                if (c.InBounds(Map) && c.Standable(Map) && current.HasCurrent(c) && !current.IsSinkCell(c) && !current.IsArrestedCell(c))
                {
                    cell = c;
                    return true;
                }
            }
            return false;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref container, "container", this);
            Scribe_Values.Look(ref loaded, "loaded", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && container == null)
            {
                container = new ThingOwner<Thing>(this);
            }
        }
    }
}
