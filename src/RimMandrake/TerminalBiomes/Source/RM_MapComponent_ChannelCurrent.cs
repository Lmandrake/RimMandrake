using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // ════════════════════════════════════════════════════════════════════
    // TWILIGHT_CHANNEL_CURRENT_1. The one net-new C# system the ruled spec
    // names (design/Jawa/worldbuilding/biomes/the_twilight_deep_river_pass_
    // 2026-09-27.md §1.3, §6: "Net-new C# systems: ONE"). Everything else in
    // this item — the undersurge, the sink, the weir/silt/stake works, the
    // cargo float, the harness — is a branch, comp or parameter riding on
    // this one component.
    //
    // STORAGE. Two map-sized byte[] grids authored ONCE by
    // RM_GenStep_TwilightChannels at map-gen time and never recomputed live
    // (§1.5 — "the bed does not move"):
    //   flowDir[idx]  0 = no current here; 1-8 = a compass direction
    //                 (see RM_FlowDir) a thing at this cell drifts toward.
    //   lane[idx]     0 = None; 1 = Margin (recoverable — a pawn there may
    //                 still path against the push); 2 = Centre (inescapable).
    //   bankBand[idx] 0 = not part of the undersurge's widened strip; 1/2 =
    //                 how many rings out from the margin it sits. This is
    //                 GravTide's `BandAt` shape (§1.1/§2.2): a per-cell
    //                 answer derived ONCE from the flow grid at gen time,
    //                 never a second live-computed grid. A band cell needs
    //                 no flowDir of its own during calm weather — the
    //                 genstep still gives it one (pointing at the nearest
    //                 channel cell), so HasCurrent/LaneAt only need to ask
    //                 "is the surge on" to turn a band cell into a live
    //                 margin cell for the storm's duration, with no second
    //                 grid and no genstep re-run.
    //
    // CARRY. Every ProcessIntervalTicks this walks a small occupant
    // dictionary (registered by a cheaper, rarer ScanIntervalTicks pass —
    // same two-tier shape RM_MapComponent_MudSwallow uses for exactly the
    // same reason: a full-map Thing scan every tick is not needed when
    // "am I on hazardous ground" changes rarely for any one Thing) and
    // steps due occupants one cell along their flow direction. §1.3's own
    // production teleport idiom (GravTide's own placement API, confirmed by
    // this repo's RM_WanderingVortex already moving a spawned, non-pawn
    // ThingWithComps the same way — `base.Position = next;` — see that
    // file): a Pawn additionally gets `pather.StopDead()` +
    // `Notify_Teleported(false)` so the interrupted job re-evaluates
    // cleanly; anything else is a plain Position assignment.
    //
    // EXEMPTIONS (§1.3): a Building never drifts; a race carrying
    // RM_ChannelNativeExtension never registers; anything on or adjacent to
    // RM_FordStones terrain is skipped for that scan; anything on a cell an
    // arresting building claims (CompChannelArrester, §4's weir) is never
    // registered — it sits there, caught, until a colonist or the building
    // itself moves it.
    //
    // SAVE/LOAD (§1.5): the two authored grids are Scribed via
    // DataExposeUtility.LookByteArray, the compact idiom for map grids. A
    // save from before this mod (or a map-size mismatch) loads a null/wrong
    // array; PostLoadInit reallocates it to all-zero rather than
    // re-rolling the bed — "the current is simply off on that map," never a
    // null-ref, never a re-roll. The occupant dictionary is NOT Scribed —
    // rebuilt from the terrain/grid scan on the first interval after load,
    // MudSwallow's own posture ("a reload just restarts the dwell clock").
    // Per-thing drift state does not exist to lose: position IS the state.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_ChannelLane : byte
    {
        None = 0,
        Margin = 1,
        Centre = 2,
    }

    // 1-8, clockwise from North. 0 (default/unused) means "no direction" and
    // is never stored as a real flow value — HasCurrent gates on lane/band,
    // not on this being nonzero, so a stray 0 just means "does not move".
    public enum RM_FlowDir : byte
    {
        None = 0,
        North = 1,
        NorthEast = 2,
        East = 3,
        SouthEast = 4,
        South = 5,
        SouthWest = 6,
        West = 7,
        NorthWest = 8,
    }

    public enum RM_SinkOutcome
    {
        Recoverable,
        RecoverableInjured,
        Lost,
    }

    public enum RM_UndersurgeFrequency
    {
        Off,
        Rare,
        Common,
    }

    // §1.3 "Exempt: races carrying RM_ChannelNativeExtension (murrol,
    // waelune)". Neither race is built yet (both are owed content, not this
    // item's job — see report); this extension exists now so whichever pass
    // builds them only has to add one <li> to their <modExtensions>.
    public class RM_ChannelNativeExtension : DefModExtension
    {
    }

    // §4's arresting-building marker. Presence on a spawned ThingWithComps
    // stops the carry dead at that cell (Q2: "weirs catch people too").
    // `Active` lets RM_Building_BankWeir's breach state disable the catch
    // without removing/re-adding the comp.
    public class CompProperties_ChannelArrester : CompProperties
    {
        public CompProperties_ChannelArrester()
        {
            compClass = typeof(CompChannelArrester);
        }
    }

    public class CompChannelArrester : ThingComp
    {
        public bool Active = true;
    }

    public class RM_MapComponent_ChannelCurrent : MapComponent
    {
        // ── Authored grids ──────────────────────────────────────────────
        private byte[] flowDir;
        private byte[] lane;
        private byte[] bankBand;
        private List<IntVec3> sinkCells = new List<IntVec3>();

        // ── Live state ──────────────────────────────────────────────────
        private bool surgeActive;
        private List<Pawn> warnedPawns = new List<Pawn>();

        // Not Scribed — rebuilt from the grid/terrain scan (§1.5).
        private readonly Dictionary<Thing, int> nextMoveTick = new Dictionary<Thing, int>();

        private const int ScanIntervalTicks = 250; // MudSwallow's own registration cadence
        private const int ProcessIntervalTicks = 15; // fine enough to resolve a 45-tick CENTRE cadence
        private const int CentreCadenceTicks = 45; // §1.3 default: one cell per ~45 ticks in CENTRE
        private const int MarginCadenceTicks = 90; // §1.3 default: ~90 in MARGIN
        private const float SinkArrivalSearchRadius = 4f;

        private int scanCooldown;
        private int processCooldown;
        private int undersurgeRollCooldown;
        private const int UndersurgeRollIntervalTicks = GenTicks.TickRareInterval;

        // Cached terrain lookups — GetNamedSilentFail throughout, matching
        // GenStep_GreySeaFloorDressing's own established convention in this
        // mod, because the ford/bed/silt terrain defs are content drop §8.2's
        // job, not this item's (see engine summary table). Absence degrades
        // gracefully: the ford exemption simply never fires and the terrain
        // never paints, but the flow grid — the actual mechanism — is
        // unaffected either way.
        private TerrainDef fordDef;
        private bool fordLookupDone;

        public RM_MapComponent_ChannelCurrent(Map map)
            : base(map)
        {
            scanCooldown = Rand.Range(1, ScanIntervalTicks);
            processCooldown = Rand.Range(1, ProcessIntervalTicks);
            undersurgeRollCooldown = Rand.Range(1, UndersurgeRollIntervalTicks);
        }

        private void EnsureGrids()
        {
            int n = map.cellIndices.NumGridCells;
            if (flowDir == null || flowDir.Length != n)
            {
                flowDir = new byte[n];
            }
            if (lane == null || lane.Length != n)
            {
                lane = new byte[n];
            }
            if (bankBand == null || bankBand.Length != n)
            {
                bankBand = new byte[n];
            }
        }

        // ════════════════════════════════════════════════════════════════
        // Genstep authoring API — RM_GenStep_TwilightChannels calls these
        // once, at map gen, and never again.
        // ════════════════════════════════════════════════════════════════
        public void SetFlow(IntVec3 c, RM_FlowDir dir, RM_ChannelLane laneClass)
        {
            EnsureGrids();
            if (!c.InBounds(map))
            {
                return;
            }
            int idx = map.cellIndices.CellToIndex(c);
            flowDir[idx] = (byte)dir;
            lane[idx] = (byte)laneClass;
        }

        public void SetBankBand(IntVec3 c, RM_FlowDir towardChannel, int band)
        {
            EnsureGrids();
            if (!c.InBounds(map))
            {
                return;
            }
            int idx = map.cellIndices.CellToIndex(c);
            if (lane[idx] == 0)
            {
                // Never overwrite a real channel cell's own flow with the
                // band's "toward the channel" direction.
                flowDir[idx] = (byte)towardChannel;
            }
            bankBand[idx] = (byte)Mathf.Clamp(band, 0, 2);
        }

        public void SetSinkCells(List<IntVec3> cells)
        {
            sinkCells = new List<IntVec3>(cells);
        }

        // ════════════════════════════════════════════════════════════════
        // Queries
        // ════════════════════════════════════════════════════════════════
        public bool HasCurrent(IntVec3 c)
        {
            if (flowDir == null || !c.InBounds(map))
            {
                return false;
            }
            int idx = map.cellIndices.CellToIndex(c);
            if (lane[idx] != 0)
            {
                return true;
            }
            // §2.2 width-out: during the undersurge, the widened band reads
            // as live current with no second grid — see class header.
            return surgeActive && bankBand[idx] > 0 && flowDir[idx] != 0;
        }

        public RM_ChannelLane LaneAt(IntVec3 c)
        {
            if (lane == null || !c.InBounds(map))
            {
                return RM_ChannelLane.None;
            }
            int idx = map.cellIndices.CellToIndex(c);
            RM_ChannelLane l = (RM_ChannelLane)lane[idx];
            if (l != RM_ChannelLane.None)
            {
                return l;
            }
            if (surgeActive && bankBand[idx] > 0)
            {
                return RM_ChannelLane.Margin;
            }
            return RM_ChannelLane.None;
        }

        public RM_FlowDir FlowAt(IntVec3 c)
        {
            if (flowDir == null || !c.InBounds(map))
            {
                return RM_FlowDir.None;
            }
            return (RM_FlowDir)flowDir[map.cellIndices.CellToIndex(c)];
        }

        public int BankBandAt(IntVec3 c)
        {
            if (bankBand == null || !c.InBounds(map))
            {
                return 0;
            }
            return bankBand[map.cellIndices.CellToIndex(c)];
        }

        public bool SurgeActive => surgeActive;

        public static IntVec3 Offset(RM_FlowDir dir)
        {
            switch (dir)
            {
                case RM_FlowDir.North: return new IntVec3(0, 0, 1);
                case RM_FlowDir.NorthEast: return new IntVec3(1, 0, 1);
                case RM_FlowDir.East: return new IntVec3(1, 0, 0);
                case RM_FlowDir.SouthEast: return new IntVec3(1, 0, -1);
                case RM_FlowDir.South: return new IntVec3(0, 0, -1);
                case RM_FlowDir.SouthWest: return new IntVec3(-1, 0, -1);
                case RM_FlowDir.West: return new IntVec3(-1, 0, 0);
                case RM_FlowDir.NorthWest: return new IntVec3(-1, 0, 1);
                default: return IntVec3.Invalid;
            }
        }

        // ════════════════════════════════════════════════════════════════
        // Undersurge — called by RM_GameCondition_Undersurge's Init/End.
        // ════════════════════════════════════════════════════════════════
        public void BeginSurge()
        {
            surgeActive = true;
            GrabPawnsOnWidenedBand();
        }

        public void EndSurge()
        {
            surgeActive = false;
        }

        // §2 point 3, "the grab": a pawn standing on the widened strip when
        // its cell activates gets one PawnFlyer-shaped yank two cells toward
        // the bed. Done once, immediately, at surge start (rather than
        // waiting for the next 250-tick scan) so it reads as the violent
        // moment the spec describes rather than a quiet drift-in.
        private void GrabPawnsOnWidenedBand()
        {
            if (bankBand == null)
            {
                return;
            }
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || IsExempt(p))
                {
                    continue;
                }
                IntVec3 pos = p.Position;
                if (BankBandAt(pos) <= 0)
                {
                    continue;
                }
                RM_FlowDir dir = FlowAt(pos);
                IntVec3 step = Offset(dir);
                if (step == IntVec3.Invalid)
                {
                    continue;
                }
                IntVec3 target = pos + step + step; // "two cells toward the bed"
                if (!target.InBounds(map))
                {
                    target = pos + step;
                }
                if (target.InBounds(map))
                {
                    Move(p, target);
                    if (HasCurrent(target))
                    {
                        RegisterOccupant(p, target);
                    }
                }
            }
        }

        // ════════════════════════════════════════════════════════════════
        // Tick
        // ════════════════════════════════════════════════════════════════
        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_TerminalBiomesSettings.ChannelCurrentActive)
            {
                return; // MOD_OPTIONS_RETROFIT_1: all-off degrades to a no-op, §1.6
            }

            EnsureGrids();

            if (--scanCooldown <= 0)
            {
                scanCooldown = ScanIntervalTicks;
                ScanForOccupants();
            }

            if (--processCooldown <= 0)
            {
                processCooldown = ProcessIntervalTicks;
                ProcessOccupants();
            }

            if (--undersurgeRollCooldown <= 0)
            {
                undersurgeRollCooldown = UndersurgeRollIntervalTicks;
                TickUndersurgeRoll();
            }
        }

        // Cheap registration/deregistration pass — MudSwallow's own shape.
        // Snapshots both thing lists before touching anything so a Move()
        // inside ProcessOccupants (which runs on a different cadence)
        // cannot invalidate this loop; this method never moves anything.
        private void ScanForOccupants()
        {
            List<Thing> candidates = new List<Thing>(map.mapPawns.AllPawnsSpawned);
            candidates.AddRange(map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver));

            var stillPresent = new HashSet<Thing>();
            for (int i = 0; i < candidates.Count; i++)
            {
                Thing t = candidates[i];
                if (t == null || t.Destroyed || !t.Spawned)
                {
                    continue;
                }
                if (IsExempt(t))
                {
                    continue;
                }
                IntVec3 pos = t.Position;
                if (!HasCurrent(pos) || IsArrestedCell(pos))
                {
                    continue;
                }
                stillPresent.Add(t);
                if (!nextMoveTick.ContainsKey(t))
                {
                    RegisterOccupant(t, pos);
                }
            }

            if (nextMoveTick.Count == 0)
            {
                return;
            }
            List<Thing> stale = null;
            foreach (KeyValuePair<Thing, int> kv in nextMoveTick)
            {
                if (!stillPresent.Contains(kv.Key))
                {
                    (stale ?? (stale = new List<Thing>())).Add(kv.Key);
                }
            }
            if (stale != null)
            {
                for (int i = 0; i < stale.Count; i++)
                {
                    nextMoveTick.Remove(stale[i]);
                }
            }
        }

        private void RegisterOccupant(Thing t, IntVec3 pos)
        {
            nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, pos);
            if (t is Pawn p)
            {
                MaybeWarnFirstEntry(p);
            }
        }

        private void ProcessOccupants()
        {
            if (nextMoveTick.Count == 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            List<Thing> keys = new List<Thing>(nextMoveTick.Keys);
            for (int i = 0; i < keys.Count; i++)
            {
                Thing t = keys[i];
                if (t == null || t.Destroyed || !t.Spawned)
                {
                    nextMoveTick.Remove(t);
                    continue;
                }
                if (!nextMoveTick.TryGetValue(t, out int due) || now < due)
                {
                    continue;
                }
                StepOne(t);
            }
        }

        private void StepOne(Thing t)
        {
            IntVec3 pos = t.Position;
            if (!HasCurrent(pos))
            {
                nextMoveTick.Remove(t);
                return;
            }

            RM_FlowDir dir = FlowAt(pos);
            IntVec3 step = Offset(dir);
            if (step == IntVec3.Invalid)
            {
                nextMoveTick.Remove(t);
                return;
            }

            IntVec3 next = pos + step;
            if (!next.InBounds(map))
            {
                nextMoveTick.Remove(t);
                return;
            }

            if (IsSinkCell(next))
            {
                ArriveAtSink(t);
                nextMoveTick.Remove(t);
                return;
            }

            Move(t, next);

            if (IsArrestedCell(next))
            {
                nextMoveTick.Remove(t); // Q2 — the weir catches it; stop here
                return;
            }

            nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, next);
        }

        private void Move(Thing t, IntVec3 next)
        {
            // §1.1's confirmed production teleport idiom (GravTide's own
            // placement API; RM_WanderingVortex already moves a spawned,
            // non-pawn ThingWithComps the same way via a bare Position
            // assignment). Pawns additionally stop their pather and notify
            // so the interrupted job re-evaluates cleanly.
            if (t is Pawn pawn)
            {
                pawn.pather?.StopDead();
                pawn.Position = next;
                pawn.Notify_Teleported(false);
            }
            else
            {
                t.Position = next;
            }
        }

        // §1.3: MARGIN pushes at half cadence and a pawn there may still
        // path perpendicular to the flow; CENTRE is inescapable. Items
        // drift at half the pawn rate. The harness caps carried speed at
        // MARGIN cadence even in the centre. The undersurge doubles CENTRE
        // cadence and promotes MARGIN to CENTRE behaviour (handled by
        // LaneAt already reading Margin-as-current-Centre nowhere — see
        // note below: the promotion is cadence-only, lane classification
        // itself is untouched).
        private int CadenceFor(Thing t, IntVec3 cell)
        {
            RM_ChannelLane l = LaneAt(cell);
            bool harnessCapped = t is Pawn hp && RM_Apparel_FloatHarness.IsWorn(hp);
            bool centreBehaviour = l == RM_ChannelLane.Centre && !harnessCapped;
            // §2.1 "MARGIN cells promote to CENTRE behaviour" during a surge.
            if (surgeActive && l == RM_ChannelLane.Margin && !harnessCapped)
            {
                centreBehaviour = true;
            }

            int baseCadence = centreBehaviour ? CentreCadenceTicks : MarginCadenceTicks;
            if (surgeActive && centreBehaviour)
            {
                baseCadence = Mathf.Max(1, baseCadence / 2); // §2.1 "CENTRE cadence doubles"
            }
            if (!(t is Pawn))
            {
                baseCadence *= 2; // §1.3 "items drift at half the pawn rate"
            }

            float strength = Mathf.Max(0.05f, RM_TerminalBiomesSettings.channelCurrentStrength);
            return Mathf.Max(1, Mathf.RoundToInt(baseCadence / strength));
        }

        // ════════════════════════════════════════════════════════════════
        // Exemptions and arrest
        // ════════════════════════════════════════════════════════════════
        private bool IsExempt(Thing t)
        {
            if (t is Building)
            {
                return true; // §1.3 "buildings always — buildings never drift"
            }
            if (t is Pawn p && p.def.GetModExtension<RM_ChannelNativeExtension>() != null)
            {
                return true;
            }
            return NearFord(t.Position);
        }

        private bool NearFord(IntVec3 c)
        {
            if (!fordLookupDone)
            {
                fordDef = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FordStones");
                fordLookupDone = true;
            }
            if (fordDef == null)
            {
                return false;
            }
            if (c.GetTerrain(map) == fordDef)
            {
                return true;
            }
            for (int i = 0; i < GenAdj.AdjacentCells.Length; i++)
            {
                IntVec3 adj = c + GenAdj.AdjacentCells[i];
                if (adj.InBounds(map) && adj.GetTerrain(map) == fordDef)
                {
                    return true;
                }
            }
            return false;
        }

        // Public: RM_Thing_CargoFloat reads this directly to know when it
        // has been caught and should unload its contents in place.
        public bool IsArrestedCell(IntVec3 c)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                CompChannelArrester comp = (things[i] as ThingWithComps)?.GetComp<CompChannelArrester>();
                if (comp != null && comp.Active)
                {
                    return true;
                }
            }
            return false;
        }

        // Public for the same reason IsArrestedCell is: RM_Thing_CargoFloat
        // needs to notice unassisted sink arrival too.
        public bool IsSinkCell(IntVec3 c)
        {
            if (sinkCells == null)
            {
                return false;
            }
            for (int i = 0; i < sinkCells.Count; i++)
            {
                if (sinkCells[i] == c)
                {
                    return true;
                }
            }
            return false;
        }

        // ════════════════════════════════════════════════════════════════
        // The sink terminus — §3, ruled at the sitting (recoverable by
        // default, harsher ladder in Mod Settings).
        // ════════════════════════════════════════════════════════════════
        private void ArriveAtSink(Thing t)
        {
            IntVec3 dropCell = FreeSinkCell();

            if (t is Pawn pawn)
            {
                if (RM_TerminalBiomesSettings.SinkOutcome == RM_SinkOutcome.Lost)
                {
                    Find.LetterStack.ReceiveLetter(
                        "RM_ChannelSunkLostLabel".Translate(pawn.LabelShortCap),
                        "RM_ChannelSunkLostText".Translate(pawn.LabelShortCap),
                        LetterDefOf.NegativeEvent,
                        new TargetInfo(dropCell.IsValid ? dropCell : pawn.Position, map));
                    pawn.Destroy(DestroyMode.Vanish); // "the pawn is gone at basin arrival" — never a corpse to recover
                    return;
                }

                if (dropCell.IsValid)
                {
                    Move(pawn, dropCell);
                }
                Hediff sunk = HediffMaker.MakeHediff(RM_TerminalBiomesDefOf.RM_Hediff_Sunk, pawn);
                RM_HediffComp_Sunk comp = (sunk as HediffWithComps)?.TryGetComp<RM_HediffComp_Sunk>();
                if (comp != null)
                {
                    comp.ScarOnRescue = RM_TerminalBiomesSettings.SinkOutcome == RM_SinkOutcome.RecoverableInjured;
                }
                pawn.health.AddHediff(sunk);
                Messages.Message("RM_ChannelSunkMessage".Translate(pawn.LabelShortCap), pawn, MessageTypeDefOf.NegativeHealthEvent);
                return;
            }

            // Items: "the basin is also the map's lost-property office" —
            // they simply accumulate. A float in the sink is protected
            // unspoiled (§5 rung 2) because nothing here ever destroys or
            // scavenges anything sitting in the basin.
            if (dropCell.IsValid)
            {
                t.Position = dropCell;
            }
        }

        private IntVec3 FreeSinkCell()
        {
            if (sinkCells == null || sinkCells.Count == 0)
            {
                return IntVec3.Invalid;
            }
            IntVec3 centre = sinkCells[Rand.Range(0, sinkCells.Count)];
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, SinkArrivalSearchRadius, useCenter: true))
            {
                if (c.InBounds(map) && c.Standable(map) && !c.GetThingList(map).Exists(x => x is Pawn))
                {
                    return c;
                }
            }
            return centre;
        }

        // ════════════════════════════════════════════════════════════════
        // Undersurge MTB roll — Mod Settings' "undersurge frequency"
        // (off/rare/common). Kept here rather than on the GameCondition
        // itself for the same reason RM_MapComponent_GradientAxis's own
        // surge roll lives on the component: something that outlives any
        // one condition instance has to own the schedule.
        // ════════════════════════════════════════════════════════════════
        private void TickUndersurgeRoll()
        {
            if (surgeActive)
            {
                return; // one at a time
            }
            RM_UndersurgeFrequency freq = RM_TerminalBiomesSettings.undersurgeFrequency;
            if (freq == RM_UndersurgeFrequency.Off || !RM_TerminalBiomesSettings.ChannelCurrentActive)
            {
                return;
            }
            float mtbDays = freq == RM_UndersurgeFrequency.Common ? 4f : 12f; // INVENTED tuning, not a ruling
            if (!Rand.MTBEventOccurs(mtbDays, GenDate.TicksPerDay, UndersurgeRollIntervalTicks))
            {
                return;
            }
            GameCondition existing = map.gameConditionManager.GetActiveCondition(RM_TerminalBiomesDefOf.RM_GameCondition_Undersurge);
            if (existing != null)
            {
                return;
            }
            int duration = Rand.Range(30000, 60000); // "a day or so", §2 preamble
            GameCondition cond = GameConditionMaker.MakeCondition(RM_TerminalBiomesDefOf.RM_GameCondition_Undersurge, duration);
            map.gameConditionManager.RegisterCondition(cond);
        }

        private void MaybeWarnFirstEntry(Pawn p)
        {
            if (!RM_TerminalBiomesSettings.channelFirstEntryWarning)
            {
                return;
            }
            if (warnedPawns.Contains(p))
            {
                return;
            }
            warnedPawns.Add(p);
            Messages.Message("RM_ChannelFirstEntry".Translate(p.LabelShortCap), p, MessageTypeDefOf.NeutralEvent, historical: false);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            DataExposeUtility.LookByteArray(ref flowDir, "channelFlowDir");
            DataExposeUtility.LookByteArray(ref lane, "channelLane");
            DataExposeUtility.LookByteArray(ref bankBand, "channelBankBand");
            Scribe_Collections.Look(ref sinkCells, "channelSinkCells", LookMode.Value);
            Scribe_Values.Look(ref surgeActive, "channelSurgeActive", false);
            Scribe_Collections.Look(ref warnedPawns, "channelWarnedPawns", LookMode.Reference);

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                // §1.5: a save from before this mod (or a map-size mismatch)
                // regenerates nothing — the current is simply off on that
                // map, never a null-ref, never a re-roll of the bed.
                int n = map.cellIndices.NumGridCells;
                if (flowDir == null || flowDir.Length != n)
                {
                    flowDir = new byte[n];
                }
                if (lane == null || lane.Length != n)
                {
                    lane = new byte[n];
                }
                if (bankBand == null || bankBand.Length != n)
                {
                    bankBand = new byte[n];
                }
                if (sinkCells == null)
                {
                    sinkCells = new List<IntVec3>();
                }
                if (warnedPawns == null)
                {
                    warnedPawns = new List<Pawn>();
                }
            }
        }
    }
}
