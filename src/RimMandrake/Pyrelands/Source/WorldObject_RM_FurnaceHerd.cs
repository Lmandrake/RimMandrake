using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>Which leg of the capacitor cycle a herd is currently on.</summary>
    public enum FurnaceHerdLeg
    {
        DeepDesert,
        Pyrelands,
        Terminator,
    }

    /// <summary>
    /// FURNACEBEAST_WORLD_MIGRATION_1 — the world leg. Split out of
    /// FURNACEBEAST_THERMAL_CYCLE_1: everything true of a furnace-beast herd
    /// while no Map holds it, cycling the planet the owner described
    /// (2026-09-14): "build up heat in the Deep Desert and intentionally
    /// coming into the Pyrelands to help it burn and absorb yet more heat …
    /// then they migrate all the way to the near terminator where they eat
    /// everything in sight while they slowly bleed out all that heat … Then
    /// they return to build up heat again."
    ///
    /// 🔑 A PLAIN WorldObject, NOT A MapParent. WorldObject_Inhabited (this
    /// mod's own sibling pattern) is a MapParent because a place a player
    /// visits needs a generated map; a herd never generates one of its own —
    /// it only ever DELIVERS onto a map that already exists at its tile
    /// (TryDeliverToSettledMap below). Modelled instead on
    /// RimWorld.Planet.TravellingTransporters — a plain WorldObject that
    /// exists purely between tiles, overriding TickInterval and setting Tile
    /// directly.
    ///
    /// ⚠️ THE MOVE IS A JUMP, NOT A GRADUAL TRAVEL ANIMATION.
    /// TravellingTransporters slerps its DrawPos between two tiles over many
    /// ticks (TraveledPctStepPerTick) for a caravan the player is watching.
    /// A furnace-beast herd's route spans weeks and is not something the
    /// player tracks tick-by-tick, so this deliberately sets
    /// <see cref="WorldObject.Tile"/> straight to the resolved destination —
    /// "route across WorldGrid tiles chosen by biome, not by pathing cost"
    /// (the item's own words), taken literally rather than building a second,
    /// harder-to-verify travel-animation system nothing asked for.
    ///
    /// 🔑 HOLDS REAL Pawns, deep-scribed — same shape as
    /// WorldObject_Inhabited.roster, and for the same reason: a custom holder
    /// cannot use LookMode.Reference safely (WorldPawnGC's critical-pawn test
    /// does not recognise it). UNLIKE Inhabited's frozen roster, this one is
    /// NOT ShouldTickContents=false — needs are meant to stay frozen (nobody
    /// wants a herd starving to death off-map over a 15-day desert dwell) but
    /// charge is meant to keep moving, so this class does not implement
    /// IThingHolderTickable at all (the default is "don't tick contents") and
    /// instead drives ONLY the charge field directly, once per its own
    /// TickInterval, via CompFurnaceThermalCharge.ApplyWorldTick — see that
    /// method's header for why this is the same number, not a second one.
    ///
    /// ⚠️ NO "NEAR FIRE" BONUS OFF-MAP. MapComponent_BurnLine (the standing
    /// burn the on-map job-giver seeks) only exists once a Map does. The
    /// Pyrelands leg's extra charging pull is therefore expressed purely
    /// through that biome's own hot ambient temperature — real, but gentler
    /// than standing in an actual fire. Left as an honest simplification
    /// rather than inventing a world-scale "burn intensity" concept nothing
    /// else in this codebase tracks.
    /// </summary>
    public class WorldObject_RM_FurnaceHerd : WorldObject, IThingHolder
    {
        /// <summary>The beasts. Real pawns, held off-map. See the class
        /// header for why LookMode.Deep and not Reference.</summary>
        public ThingOwner<Pawn> members;

        public FurnaceHerdLeg leg = FurnaceHerdLeg.DeepDesert;

        /// <summary>Ticks spent on the current leg since the last move,
        /// scribed so a save/load mid-dwell does not reset the clock.</summary>
        public int ticksAtCurrentLeg;

        public WorldObject_RM_FurnaceHerd()
        {
            members = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
        }

        protected override int UpdateRateTicks => PyrelandsTuning.WorldHerdUpdateIntervalTicks;

        public override string Label => "furnace-beast herd";

        public ThingOwner GetDirectlyHeldThings()
        {
            return members;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref members, "members", this);
            Scribe_Values.Look(ref leg, "leg", FurnaceHerdLeg.DeepDesert);
            Scribe_Values.Look(ref ticksAtCurrentLeg, "ticksAtCurrentLeg", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && members == null)
            {
                members = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
            }
        }

        protected override void TickInterval(int delta)
        {
            base.TickInterval(delta);

            if (!RM_PyrelandsSettings.pyrelandsEnabled
                || !RM_PyrelandsSettings.furnaceThermalEnabled
                || !RM_PyrelandsSettings.furnaceWorldMigrationEnabled)
            {
                return;
            }
            if (Destroyed || members == null)
            {
                return;
            }

            // Delivery is checked every interval regardless of leg: a player
            // can found a settlement on a tile the herd is already sitting on
            // mid-charge, and the herd must not wait for its next scheduled
            // move to notice.
            if (TryDeliverToSettledMap())
            {
                return;
            }

            AdvanceChargeAndLeg(delta);
        }

        // ------------------------------------------------------------------
        // Arrival: world -> map.
        // ------------------------------------------------------------------

        private bool TryDeliverToSettledMap()
        {
            if (members.Count == 0)
            {
                // An empty herd (every member already delivered or lost) has
                // nothing left to do on the world at all.
                Destroy();
                return true;
            }

            Map map = Current.Game?.FindMap(Tile);
            if (map == null)
            {
                return false;
            }

            DeliverMembersTo(map);
            Destroy();
            return true;
        }

        private void DeliverMembersTo(Map map)
        {
            List<Pawn> snapshot = members.InnerListForReading.ToList();
            int delivered = 0;
            for (int i = 0; i < snapshot.Count; i++)
            {
                Pawn beast = snapshot[i];
                if (beast == null || !members.Remove(beast))
                {
                    continue;
                }
                IntVec3 cell = DropCellFinder.RandomDropSpot(map);
                GenSpawn.Spawn(beast, cell, map, WipeMode.Vanish);
                delivered++;
            }
            if (delivered > 0)
            {
                Log.Message("[RimMandrake.Pyrelands] a furnace-beast herd (" + delivered + ") arrived on "
                    + map.Parent?.LabelCap + " (" + leg + " leg).");
            }
        }

        /// <summary>
        /// Defensive only: nothing in this build destroys a herd with members
        /// still aboard (DeliverMembersTo always empties first), but if
        /// something else ever does — a debug action, a future mod — this
        /// stops it from silently discarding living pawns the way an
        /// un-owned ThingOwner would.
        /// </summary>
        public override void Destroy()
        {
            if (members != null && members.Count > 0)
            {
                Map map = Current.Game?.FindMap(Tile);
                List<Pawn> leftover = members.InnerListForReading.ToList();
                for (int i = 0; i < leftover.Count; i++)
                {
                    Pawn p = leftover[i];
                    if (p == null || !members.Remove(p))
                    {
                        continue;
                    }
                    if (map != null)
                    {
                        GenSpawn.Spawn(p, DropCellFinder.RandomDropSpot(map), map, WipeMode.Vanish);
                    }
                    else if (!p.Destroyed)
                    {
                        Find.WorldPawns.PassToWorld(p);
                    }
                }
            }
            base.Destroy();
        }

        // ------------------------------------------------------------------
        // The cycle itself.
        // ------------------------------------------------------------------

        private void AdvanceChargeAndLeg(int delta)
        {
            if (members.Count == 0)
            {
                return;
            }

            float ambient = GenTemperature.GetTemperatureAtTile(Tile);
            List<Pawn> list = members.InnerListForReading;
            for (int i = 0; i < list.Count; i++)
            {
                list[i]?.TryGetComp<CompFurnaceThermalCharge>()?.ApplyWorldTick(ambient);
            }

            ticksAtCurrentLeg += delta;
            float avg = AverageCharge();

            switch (leg)
            {
                case FurnaceHerdLeg.DeepDesert:
                    // Time-driven, not charge-driven: this leg is the START of
                    // the charge, not its completion, so there is no
                    // threshold to wait on. "Basking for weeks."
                    if (ticksAtCurrentLeg >= PyrelandsTuning.WorldHerdDeepDesertDwellTicks)
                    {
                        AdvanceToLeg(FurnaceHerdLeg.Pyrelands, PyrelandsTuning.PyrelandsBiomeDefNames);
                    }
                    break;

                case FurnaceHerdLeg.Pyrelands:
                    if (avg >= PyrelandsTuning.FurnaceChargeAvoidAbove
                        || ticksAtCurrentLeg >= PyrelandsTuning.WorldHerdMaxLegDwellTicks)
                    {
                        AdvanceToLeg(FurnaceHerdLeg.Terminator, PyrelandsTuning.NearTerminatorBiomeDefNames);
                    }
                    break;

                case FurnaceHerdLeg.Terminator:
                    if (avg <= PyrelandsTuning.FurnaceChargeSeekBelow
                        || ticksAtCurrentLeg >= PyrelandsTuning.WorldHerdMaxLegDwellTicks)
                    {
                        AdvanceToLeg(FurnaceHerdLeg.DeepDesert, PyrelandsTuning.DeepDesertBiomeDefNames);
                    }
                    break;
            }
        }

        private void AdvanceToLeg(FurnaceHerdLeg next, IReadOnlyList<string> biomeNames)
        {
            leg = next;
            ticksAtCurrentLeg = 0;
            if (TryFindNearestBiomeTile(Tile, biomeNames, out PlanetTile dest))
            {
                Tile = dest;
            }
            else
            {
                // Stays put and simply re-evaluates next interval; the leg has
                // already advanced, so the max-dwell safety valve above still
                // applies rather than stalling this herd forever.
                Log.Warning("[RimMandrake.Pyrelands] a furnace-beast herd could not find a " + next
                    + " tile within " + PyrelandsTuning.WorldHerdTileSearchCap + " tiles of " + Tile
                    + "; staying put.");
            }
        }

        private float AverageCharge()
        {
            if (members.Count == 0)
            {
                return 0f;
            }
            float total = 0f;
            int n = 0;
            List<Pawn> list = members.InnerListForReading;
            for (int i = 0; i < list.Count; i++)
            {
                CompFurnaceThermalCharge comp = list[i]?.TryGetComp<CompFurnaceThermalCharge>();
                if (comp == null)
                {
                    continue;
                }
                total += comp.Charge;
                n++;
            }
            return n > 0 ? total / n : 0f;
        }

        // ------------------------------------------------------------------
        // Biome-routed tile finding, shared with Patch_FurnaceHerdMapRemoval.
        // ------------------------------------------------------------------

        /// <summary>Which leg a tile's own biome belongs to, for a herd being
        /// re-formed at that tile (Patch_FurnaceHerdMapRemoval) rather than
        /// advanced from elsewhere.</summary>
        public static FurnaceHerdLeg LegForBiome(BiomeDef biome)
        {
            if (biome == null)
            {
                return FurnaceHerdLeg.DeepDesert;
            }
            if (MatchesAny(biome.defName, PyrelandsTuning.PyrelandsBiomeDefNames))
            {
                return FurnaceHerdLeg.Pyrelands;
            }
            if (MatchesAny(biome.defName, PyrelandsTuning.NearTerminatorBiomeDefNames))
            {
                return FurnaceHerdLeg.Terminator;
            }
            return FurnaceHerdLeg.DeepDesert;
        }

        /// <summary>
        /// Breadth-first search outward from <paramref name="from"/> for the
        /// nearest tile whose PrimaryBiome matches one of
        /// <paramref name="biomeNames"/>. Checks <paramref name="from"/>
        /// itself first — a herd already standing in the target biome does
        /// not need to move at all, and Tile's own setter no-ops on an
        /// unchanged value.
        ///
        /// 🔴 THIS RUNS ON THE ALREADY-FIXED PLANET. It reads
        /// Find.WorldGrid's live tiles; it generates nothing and touches no
        /// terrain or biome assignment (CLAUDE.md: no worldgen, ever).
        /// </summary>
        internal static bool TryFindNearestBiomeTile(PlanetTile from, IReadOnlyList<string> biomeNames, out PlanetTile found)
        {
            found = PlanetTile.Invalid;
            if (!from.Valid || biomeNames == null || biomeNames.Count == 0)
            {
                return false;
            }

            WorldGrid grid = Find.WorldGrid;
            var visited = new HashSet<int>{ from.tileId };
            var queue = new Queue<PlanetTile>();
            queue.Enqueue(from);
            var neighbors = new List<PlanetTile>();
            int scanned = 0;

            while (queue.Count > 0 && scanned < PyrelandsTuning.WorldHerdTileSearchCap)
            {
                PlanetTile current = queue.Dequeue();
                scanned++;

                BiomeDef biome = grid[current]?.PrimaryBiome;
                if (biome != null && MatchesAny(biome.defName, biomeNames))
                {
                    found = current;
                    return true;
                }

                neighbors.Clear();
                grid.GetTileNeighbors(current, neighbors);
                for (int i = 0; i < neighbors.Count; i++)
                {
                    PlanetTile n = neighbors[i];
                    if (visited.Add(n.tileId))
                    {
                        queue.Enqueue(n);
                    }
                }
            }
            return false;
        }

        internal static bool MatchesAny(string defName, IReadOnlyList<string> names)
        {
            for (int i = 0; i < names.Count; i++)
            {
                if (string.Equals(defName, names[i], System.StringComparison.Ordinal))
                {
                    return true;
                }
            }
            return false;
        }

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder();
            string baseStr = base.GetInspectString();
            if (!baseStr.NullOrEmpty())
            {
                sb.AppendLine(baseStr);
            }
            sb.Append((members?.Count ?? 0) + " furnace-beasts . heading toward " + leg
                + " . charge " + AverageCharge().ToStringPercent("F0"));
            return sb.ToString().TrimEndNewlines();
        }
    }
}
