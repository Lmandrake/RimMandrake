using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// A stack the dune swallowed — MOVING_DUNES_DESIGN.md §3 "Burial of items".
    ///
    /// Why a container at all, rather than leaving the item where it is and letting
    /// <c>hideAtSnowOrSandDepth</c> hide it: a hidden-but-present item stays selectable,
    /// haulable, reservable and deteriorating. That reads as a rendering bug, not as
    /// burial. Despawning the stack into a ThingOwner gets the pause on deterioration
    /// for free — <c>SteadyEnvironmentEffects</c> only walks things standing in cells —
    /// and makes the reveal a real event.
    ///
    /// The cache is an ITEM, not a building: a full-fillage edifice would zero its own
    /// cell's sand depth (<c>SandGrid.CanCoexistWithSand</c>), which would erode the very
    /// dune that made it and reveal it instantly.
    /// </summary>
    public class Thing_BuriedCache : ThingWithComps, IThingHolder
    {
        private ThingOwner innerContainer;

        /// <summary>Absolute tick this cache was created. Used only for the inspect
        /// string and for the oldest-first choice when a map is at its cache cap.</summary>
        public int buriedAtTick = -1;

        public Thing_BuriedCache()
        {
            innerContainer = new ThingOwner<Thing>(this, oneStackOnly: false);
        }

        public ThingOwner GetDirectlyHeldThings()
        {
            return innerContainer;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public int ContentsCount
        {
            get { return innerContainer.Count; }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref innerContainer, "innerContainer", this);
            Scribe_Values.Look(ref buriedAtTick, "buriedAtTick", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && innerContainer == null)
            {
                innerContainer = new ThingOwner<Thing>(this, oneStackOnly: false);
            }
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            if (buriedAtTick < 0)
            {
                buriedAtTick = Find.TickManager.TicksGame;
            }
        }

        /// <summary>Takes a thing into the cache. The thing may be spawned (it is
        /// despawned into the container) or already loose in another holder.</summary>
        public bool Accept(Thing thing)
        {
            if (thing == null || thing.Destroyed || thing == this)
            {
                return false;
            }
            // A spawned thing's holdingOwner is the MAP's ThingOwner, and ThingOwner
            // refuses to transfer to or from a map ("They must be spawned or despawned
            // manually", ThingOwner.cs:744) — so despawn first, always.
            if (thing.Spawned)
            {
                thing.DeSpawn();
            }
            if (thing.holdingOwner != null)
            {
                return thing.holdingOwner.TryTransferToContainer(thing, innerContainer, thing.stackCount) > 0;
            }
            return innerContainer.TryAdd(thing);
        }

        /// <summary>Absorbs another cache's contents, then destroys it. Caches merge per
        /// cell so a drifting front cannot leave a stack of containers on one tile.</summary>
        public void Absorb(Thing_BuriedCache other)
        {
            if (other == null || other == this || other.Destroyed)
            {
                return;
            }
            other.innerContainer.TryTransferAllToContainer(innerContainer);
            if (other.buriedAtTick >= 0 && (buriedAtTick < 0 || other.buriedAtTick < buriedAtTick))
            {
                buriedAtTick = other.buriedAtTick;
            }
            other.Destroy();
        }

        public override void TickRare()
        {
            base.TickRare();
            if (!Spawned)
            {
                return;
            }
            RM_DuneMaterialDef material = DuneFieldRegistry.MaterialOn(Map);
            // A cache on a map that is no longer a dune field (the mod's biome binding
            // was removed, or the thing was carried to an ordinary map) must not become
            // a permanent one-way hole: it reveals on the vanilla reveal depth instead.
            float revealAt = material != null ? material.revealDepth : 0.25f;
            if (Position.GetSandDepth(Map) <= revealAt)
            {
                Reveal();
            }
        }

        /// <summary>The erosion reveal: drop everything back onto the map and vanish.</summary>
        public void Reveal()
        {
            if (!Spawned)
            {
                return;
            }
            Map map = Map;
            IntVec3 pos = Position;
            if (innerContainer.Count > 0)
            {
                innerContainer.TryDropAll(pos, map, ThingPlaceMode.Near);
            }
            Destroy();
        }

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = Map;
            IntVec3 pos = Position;
            bool drop = innerContainer.Count > 0 && map != null && mode != DestroyMode.Vanish;
            base.Destroy(mode);
            if (drop)
            {
                innerContainer.TryDropAll(pos, map, ThingPlaceMode.Near);
            }
            innerContainer.ClearAndDestroyContentsOrPassToWorld();
        }

        public override string GetInspectString()
        {
            string text = base.GetInspectString();
            if (!text.NullOrEmpty())
            {
                text += "\n";
            }
            text += "RM_Dunes_CacheContents".Translate() + ": " + innerContainer.ContentsString.CapitalizeFirst();
            if (Spawned)
            {
                text += "\n" + "RM_Dunes_CacheDepth".Translate(
                    Position.GetSandDepth(Map).ToStringPercent());
            }
            return text;
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }
            if (DebugSettings.ShowDevGizmos)
            {
                yield return new Command_Action
                {
                    defaultLabel = "DEV: Reveal cache",
                    action = Reveal,
                };
            }
        }
    }
}
