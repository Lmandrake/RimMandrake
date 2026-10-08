using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>Which leg of the capacitor cycle a herd is currently on.</summary>
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

            // The desert leg is time-driven ("basking for weeks"); the other two end on a charge threshold or the max dwell.
            if (RM_FurnaceKernel.ShouldAdvance(leg, ticksAtCurrentLeg, avg, PyrelandsTuning.WorldHerdDeepDesertDwellTicks,
                    PyrelandsTuning.WorldHerdMaxLegDwellTicks, PyrelandsTuning.FurnaceChargeSeekBelow, PyrelandsTuning.FurnaceChargeAvoidAbove))
            {
                FurnaceHerdLeg next = RM_FurnaceKernel.NextLeg(leg);
                AdvanceToLeg(next, next == FurnaceHerdLeg.Pyrelands ? PyrelandsTuning.PyrelandsBiomeDefNames
                    : next == FurnaceHerdLeg.Terminator ? PyrelandsTuning.NearTerminatorBiomeDefNames
                    : PyrelandsTuning.DeepDesertBiomeDefNames);
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
            return RM_FurnaceKernel.LegForBiome(biome?.defName, PyrelandsTuning.PyrelandsBiomeDefNames, PyrelandsTuning.NearTerminatorBiomeDefNames);
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
            bool hit = RM_FurnaceKernel.NearestMatching(from, t => t.tileId, (cur, into) => grid.GetTileNeighbors(cur, into),
                t =>
                {
                    BiomeDef biome = grid[t]?.PrimaryBiome;
                    return biome != null && MatchesAny(biome.defName, biomeNames);
                },
                PyrelandsTuning.WorldHerdTileSearchCap, out PlanetTile nearest);
            found = hit ? nearest : PlanetTile.Invalid;
            return hit;
        }

        internal static bool MatchesAny(string defName, IReadOnlyList<string> names)
        {
            return RM_FurnaceKernel.MatchesAny(defName, names);
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
