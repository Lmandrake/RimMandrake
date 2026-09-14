using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M12 build (greentide_kit_spec.md M12, "The
    // Greatbole — mineable living tower"). FEVER_WOOD_MECHANICS_1's own item
    // file names this exact class as one of the two it is blocked on (F7,
    // "bore-caves / Greatbole reuse") — kept generic on purpose, nothing
    // below names Greentide, a bole, or the Fever Wood: "any future
    // living-dungeon wants it" per the kit spec's own framing.
    //
    // Registration is push-based, same idiom as RM_MapComponent_DreadField
    // in this same assembly: a marker Thing's own comp
    // (RM_CompLivingBoleMarker) calls RegisterBole once on its FIRST ever
    // spawn and DeregisterBole once on despawn. UNLIKE DreadField, this
    // component's state is NOT fully re-derivable from what is currently
    // spawned — which cells are empty/enclosed/unsealed, which are
    // mid-regrow-timer, mid-creak-warning or mid-crush is genuine save
    // state (a mined-out chamber sitting empty carries no Thing of its own
    // to re-discover from, and re-flood-filling from the marker after some
    // chambers are already mined would silently shrink the footprint) — so
    // BoleRecord/CellTimer below ARE Scribed. A marker's own comp
    // (RM_CompLivingBoleMarker) scribes its own boleId and skips
    // re-registering on a load where that id is already set.
    //
    // Per-registered-bole state machine, one entry per footprint cell in
    // CellTimer.State:
    //   (untracked)  -> cell holds regrowthThing, or is sealed: never
    //                    tracked at all, cheapest state.
    //   Scheduled    -> cell is empty/enclosed/unsealed; a regrow lands at
    //                    DueTick. If the cell is still empty when that
    //                    tick arrives, the tree just regrows there quietly.
    //   Warning      -> the cell was occupied at Scheduled's DueTick — a
    //                    creak (message + sound) fires once, and a further
    //                    creakWarningTicks passes before the tree actually
    //                    starts pushing back, so a colonist gets a real
    //                    chance to clear the cell themselves.
    //   Crushing     -> DueTick lands with the cell still occupied — this,
    //                    and every following crushIntervalTicks, every
    //                    Thing on the cell takes one crush pulse (pawns
    //                    pushed to the nearest open cell, items destroyed
    //                    outright, buildings damaged and eventually
    //                    destroyed) until the cell is clear, then the tree
    //                    regrows there.
    public class RM_MapComponent_LivingRegrowth : MapComponent
    {
        // How often idle footprint cells are rescanned for new regrowth
        // candidates, and how often a pending timer is checked for its due
        // tick. Both INVENTED; cheap relative to a bole's footprint size
        // (a handful of cells per check), so one shared interval is fine.
        private const int TickInterval = 250;

        private List<BoleRecord> boles = new List<BoleRecord>();
        private int nextBoleId = 1;

        public RM_MapComponent_LivingRegrowth(Map map)
            : base(map)
        {
        }

        // M9's own anchor points when paired with M12 — the centers of
        // every currently-registered bole on this map. Empty on a map with
        // no bole (M9 running standalone) or before M12's own GenStep has
        // run yet this map-gen (ordering handles the paired case: M12's
        // GenStepDef order must be lower than M9's).
        public IReadOnlyList<IntVec3> BoleCenters
        {
            get
            {
                List<IntVec3> result = new List<IntVec3>(boles.Count);
                for (int i = 0; i < boles.Count; i++)
                {
                    result.Add(boles[i].center);
                }
                return result;
            }
        }

        // footprintCells: every cell this bole owns (its full blob, mined
        // out or not — fixed for the life of the registration).
        public int RegisterBole(
            IntVec3 center,
            IEnumerable<IntVec3> footprintCells,
            ThingDef regrowthThing,
            TerrainDef sealantTerrain,
            IntRange regrowDaysRange,
            int creakWarningTicks,
            int crushIntervalTicks,
            float crushDamagePerHit)
        {
            BoleRecord rec = new BoleRecord
            {
                id = nextBoleId++,
                center = center,
                regrowthThing = regrowthThing,
                sealantTerrain = sealantTerrain,
                regrowDaysMin = regrowDaysRange.min,
                regrowDaysMax = regrowDaysRange.max,
                creakWarningTicks = creakWarningTicks,
                crushIntervalTicks = crushIntervalTicks,
                crushDamagePerHit = crushDamagePerHit,
            };
            foreach (IntVec3 c in footprintCells)
            {
                rec.footprint.Add(c);
            }
            boles.Add(rec);
            return rec.id;
        }

        public void DeregisterBole(int boleId)
        {
            for (int i = boles.Count - 1; i >= 0; i--)
            {
                if (boles[i].id == boleId)
                {
                    boles.RemoveAt(i);
                    return;
                }
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_EnvironmentalHazardsSettings.livingRegrowthEnabled)
            {
                return; // MOD_OPTIONS_RETROFIT_1: master toggle — every registered bole freezes exactly where it is
            }

            if (boles.Count == 0)
            {
                return;
            }

            int tick = Find.TickManager.TicksGame;
            if (tick % TickInterval != 0)
            {
                return;
            }

            for (int i = 0; i < boles.Count; i++)
            {
                ScanForNewCandidates(boles[i], tick);
                ProcessTimers(boles[i], tick);
            }
        }

        private void ScanForNewCandidates(BoleRecord bole, int tick)
        {
            if (bole.regrowthThing == null)
            {
                return;
            }

            foreach (IntVec3 cell in bole.footprint)
            {
                if (!cell.InBounds(map) || bole.timers.ContainsKey(cell))
                {
                    continue;
                }

                if (bole.sealantTerrain != null && cell.GetTerrain(map) == bole.sealantTerrain)
                {
                    continue; // sealed — the whole sealant mechanism, no separate bookkeeping needed
                }

                Building edifice = cell.GetEdifice(map);
                if (edifice != null && edifice.def == bole.regrowthThing)
                {
                    continue; // still solid heartwood, nothing to regrow here
                }

                if (!map.roofGrid.Roofed(cell))
                {
                    continue; // not enclosed — the natural-roof patch is what "enclosed" means here
                }

                int days = Rand.RangeInclusive(bole.regrowDaysMin, bole.regrowDaysMax);
                bole.timers[cell] = new CellTimer
                {
                    State = CellTimer.TimerState.Scheduled,
                    DueTick = tick + days * GenDate.TicksPerDay,
                };
            }
        }

        private void ProcessTimers(BoleRecord bole, int tick)
        {
            if (bole.timers.Count == 0)
            {
                return;
            }

            List<IntVec3> toClear = null;
            List<IntVec3> keys = new List<IntVec3>(bole.timers.Keys);
            for (int i = 0; i < keys.Count; i++)
            {
                IntVec3 cell = keys[i];

                // Re-checked every pass, not just at scan time: sealing a
                // cell at ANY point — mid-Scheduled, mid-Warning, even
                // mid-Crushing — cancels the tree's claim on it outright,
                // same "no separate bookkeeping" contract the sealant
                // mechanism promises (RM_MireExtension's own header, M8).
                if (bole.sealantTerrain != null && cell.GetTerrain(map) == bole.sealantTerrain)
                {
                    (toClear ?? (toClear = new List<IntVec3>())).Add(cell);
                    continue;
                }

                CellTimer timer = bole.timers[cell];
                if (tick < timer.DueTick)
                {
                    continue;
                }

                switch (timer.State)
                {
                    case CellTimer.TimerState.Scheduled:
                        if (IsOccupied(cell))
                        {
                            CreakWarning(cell);
                            timer.State = CellTimer.TimerState.Warning;
                            timer.DueTick = tick + bole.creakWarningTicks;
                        }
                        else
                        {
                            RegrowCell(cell, bole);
                            (toClear ?? (toClear = new List<IntVec3>())).Add(cell);
                        }
                        break;

                    case CellTimer.TimerState.Warning:
                        if (!IsOccupied(cell))
                        {
                            // Vacated during the warning window — quiet regrow, no crushing needed.
                            RegrowCell(cell, bole);
                            (toClear ?? (toClear = new List<IntVec3>())).Add(cell);
                        }
                        else
                        {
                            timer.State = CellTimer.TimerState.Crushing;
                            timer.DueTick = tick + bole.crushIntervalTicks;
                        }
                        break;

                    case CellTimer.TimerState.Crushing:
                        bool stillOccupied = CrushPulse(cell, bole);
                        if (stillOccupied)
                        {
                            timer.DueTick = tick + bole.crushIntervalTicks;
                        }
                        else
                        {
                            RegrowCell(cell, bole);
                            (toClear ?? (toClear = new List<IntVec3>())).Add(cell);
                        }
                        break;
                }
            }

            if (toClear != null)
            {
                for (int i = 0; i < toClear.Count; i++)
                {
                    bole.timers.Remove(toClear[i]);
                }
            }
        }

        private void CreakWarning(IntVec3 cell)
        {
            Messages.Message(
                "RM_LivingRegrowthCreak".Translate(),
                new TargetInfo(cell, map),
                MessageTypeDefOf.ThreatBig);
            SoundDefOf.Building_Complete.PlayOneShot(SoundInfo.InMap(new TargetInfo(cell, map)));
        }

        // Returns true if the cell is STILL occupied after this pulse (the
        // caller keeps it in the Crushing state); false once it is clear.
        private bool CrushPulse(IntVec3 cell, BoleRecord bole)
        {
            List<Thing> things = new List<Thing>(cell.GetThingList(map));
            bool stillOccupied = false;
            float amount = bole.crushDamagePerHit * System.Math.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier);

            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t == null || t.Destroyed || t.def == bole.regrowthThing)
                {
                    continue;
                }

                if (t is Pawn pawn)
                {
                    pawn.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount, 0f, -1f, null));
                    if (pawn.Dead || !pawn.Spawned)
                    {
                        continue; // dead or already removed — no longer occupies the cell
                    }

                    IntVec3 dest = CellFinder.RandomClosewalkCellNear(cell, map, 6,
                        c => c.InBounds(map) && c.Standable(map) && !bole.footprint.Contains(c));
                    if (dest.IsValid && dest != cell)
                    {
                        pawn.Position = dest;
                        pawn.Notify_Teleported(false, true);
                    }
                    else
                    {
                        stillOccupied = true; // nowhere to push it — the pulse still landed, try again next interval
                    }
                    continue;
                }

                if (t.def.category == ThingCategory.Item)
                {
                    t.Destroy(); // "popped" — an item cannot be pushed clear like a pawn
                    continue;
                }

                if (t.def.category == ThingCategory.Building)
                {
                    t.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount, 0f, -1f, null));
                    if (!t.Destroyed)
                    {
                        stillOccupied = true;
                    }
                    continue;
                }

                // Anything else on the cell (filth, gas, an attachment): leave it, it does not block regrowth.
            }

            return stillOccupied;
        }

        private void RegrowCell(IntVec3 cell, BoleRecord bole)
        {
            if (!cell.InBounds(map) || bole.regrowthThing == null)
            {
                return;
            }
            GenSpawn.Spawn(bole.regrowthThing, cell, map);
        }

        private bool IsOccupied(IntVec3 cell)
        {
            List<Thing> things = cell.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t == null || t.Destroyed)
                {
                    continue;
                }
                ThingCategory cat = t.def.category;
                if (cat == ThingCategory.Pawn || cat == ThingCategory.Item || cat == ThingCategory.Building)
                {
                    return true;
                }
            }
            return false;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref nextBoleId, "nextBoleId", 1);
            Scribe_Collections.Look(ref boles, "boles", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.LoadingVars && boles == null)
            {
                boles = new List<BoleRecord>();
            }
        }
    }

    // One registered bole. Scribed in full (see the MapComponent's own
    // header for why re-deriving this from scratch on every load is not
    // safe once any chamber has been mined out).
    internal class BoleRecord : IExposable
    {
        public int id;
        public IntVec3 center;
        public HashSet<IntVec3> footprint = new HashSet<IntVec3>();
        public ThingDef regrowthThing;
        public TerrainDef sealantTerrain;
        public int regrowDaysMin;
        public int regrowDaysMax;
        public int creakWarningTicks;
        public int crushIntervalTicks;
        public float crushDamagePerHit;
        public Dictionary<IntVec3, CellTimer> timers = new Dictionary<IntVec3, CellTimer>();

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "id");
            Scribe_Values.Look(ref center, "center");
            Scribe_Collections.Look(ref footprint, "footprint", LookMode.Value);
            Scribe_Defs.Look(ref regrowthThing, "regrowthThing");
            Scribe_Defs.Look(ref sealantTerrain, "sealantTerrain");
            Scribe_Values.Look(ref regrowDaysMin, "regrowDaysMin");
            Scribe_Values.Look(ref regrowDaysMax, "regrowDaysMax");
            Scribe_Values.Look(ref creakWarningTicks, "creakWarningTicks");
            Scribe_Values.Look(ref crushIntervalTicks, "crushIntervalTicks");
            Scribe_Values.Look(ref crushDamagePerHit, "crushDamagePerHit");
            Scribe_Collections.Look(ref timers, "timers", LookMode.Value, LookMode.Deep);

            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                if (footprint == null)
                {
                    footprint = new HashSet<IntVec3>();
                }
                if (timers == null)
                {
                    timers = new Dictionary<IntVec3, CellTimer>();
                }
            }
        }
    }

    internal class CellTimer : IExposable
    {
        public enum TimerState { Scheduled, Warning, Crushing }

        public TimerState State;
        public int DueTick;

        public void ExposeData()
        {
            Scribe_Values.Look(ref State, "state");
            Scribe_Values.Look(ref DueTick, "dueTick");
        }
    }
}
