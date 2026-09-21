using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // VENOMVINE_CONTACT_VENOM_BUILD_1, the map-side half of the contact-venom
    // mechanism (design: desert_shade_plants_design.md §1b "detection").
    //
    // Shape copied, not reused, from vanilla's own Building_Trap.Tick
    // (MEASURED via the decompiled 1.6 source, 2026-09-20): scan the cells
    // that are armed, keep a per-pawn "already touching" record so one entry
    // is one trigger, and skip Pawn.Flying. A plant cannot BE a
    // Building_Trap (no growth, no wildPlants, no cutting job), and a plant
    // ticks Long, so the scan has to live somewhere that ticks every tick —
    // here, once per map, instead of once per vine.
    //
    // Cost: one dictionary probe per spawned pawn every 15 ticks. Independent
    // of stand size — a thousand-cell thicket costs exactly what a one-cell
    // vine costs.
    //
    // Auto-instantiated on every map by Map.FillComponents(), same as this
    // mod's other MapComponents. Harmless on a map with no contact-venom
    // plant on it: both collections stay empty and MapComponentTick returns
    // on its first line.
    public class MapComponent_ContactVenom : MapComponent
    {
        // How often the map is swept for pawns standing in a registered cell.
        // A pawn crossing one cell is there ~10-20 ticks at normal move
        // speed, so 15 catches essentially every crossing while costing a
        // fifteenth of a per-tick sweep. A crossing missed here is not a
        // silent failure of the mechanism — the pawn is simply not scratched
        // by that particular cell, exactly as if it had stepped around it.
        private const int SampleIntervalTicks = 15;

        // Pruning is a maintenance pass over what should always be a handful
        // of entries, so it does not need to run at sampling cadence.
        private const int PruneIntervalTicks = 2500;

        // NOT saved. Every plant re-registers its own cell from
        // CompContactVenom.PostSpawnSetup during load (respawningAfterLoad
        // runs the same registration path), so persisting this would only
        // create a second, staler source of truth for the same fact.
        private readonly Dictionary<IntVec3, CompContactVenom> armedCells =
            new Dictionary<IntVec3, CompContactVenom>();

        // Per-pawn contact clock — SAVED (design §5 step 8: "the per-pawn
        // clock survives save/load, no double scratch on load"). Parallel
        // lists rather than a Dictionary<Pawn, struct> because Scribe has a
        // first-class path for a list of references plus lists of values and
        // none for a dictionary keyed by a Thing reference. The list holds
        // only pawns currently in (or very recently in) contact, so a linear
        // scan is cheaper than the dictionary that would index it.
        private List<Pawn> contactPawns = new List<Pawn>();
        private List<int> lastContactTicks = new List<int>();
        private List<int> nextScratchTicks = new List<int>();
        private List<int> contactIntervals = new List<int>();

        public MapComponent_ContactVenom(Map map)
            : base(map)
        {
        }

        public void RegisterCell(IntVec3 cell, CompContactVenom comp)
        {
            if (!cell.IsValid || comp == null)
            {
                return;
            }

            // Last registrant wins. Two contact-venom plants on one cell is
            // not a case the plant defs can produce (one plant per cell), and
            // if some future thing does it, one of them arming the cell is
            // the right answer — the cell is dangerous either way.
            armedCells[cell] = comp;
        }

        public void DeregisterCell(IntVec3 cell, CompContactVenom comp)
        {
            if (!cell.IsValid)
            {
                return;
            }

            // Only clear the cell if this comp is the one that owns it —
            // otherwise a despawning vine would disarm a cell some other vine
            // has since taken over.
            if (armedCells.TryGetValue(cell, out CompContactVenom current) && current == comp)
            {
                armedCells.Remove(cell);
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (armedCells.Count == 0 && contactPawns.Count == 0)
            {
                return;
            }

            // Mod option: off means the plant stays where it is and does
            // nothing — inert, not removed. Every clock already running
            // FREEZES rather than resetting (no sampling, no pruning), so
            // turning the option back on resumes instead of forgiving; the
            // same posture every other timed mechanism in this kit takes.
            if (!RM_EnvironmentalHazardsSettings.contactVenomEnabled)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;

            if (now % SampleIntervalTicks == 0 && armedCells.Count > 0)
            {
                Sample(now);
            }

            if (now % PruneIntervalTicks == 0 && contactPawns.Count > 0)
            {
                Prune(now);
            }
        }

        private void Sample(int now)
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn == null || pawn.Dead)
                {
                    continue;
                }

                // Flyers are untouched, exactly as vanilla's own traps treat
                // them ("if it flies in the fiction, it flies in the game").
                if (pawn.Flying)
                {
                    continue;
                }

                if (!armedCells.TryGetValue(pawn.Position, out CompContactVenom vine)
                    || vine == null
                    || vine.parent == null
                    || !vine.parent.Spawned)
                {
                    continue;
                }

                if (IsImmune(pawn))
                {
                    continue;
                }

                int index = IndexOf(pawn);
                if (index < 0)
                {
                    // First contact with the stand — scratch now, then start
                    // this pawn's hourly clock.
                    Scratch(pawn, vine);
                    contactPawns.Add(pawn);
                    lastContactTicks.Add(now);
                    nextScratchTicks.Add(now + Mathf.Max(1, vine.Props.contactIntervalTicks));
                    contactIntervals.Add(Mathf.Max(1, vine.Props.contactIntervalTicks));
                    continue;
                }

                // Already in contact. Moving from one vine cell to another is
                // LINGERING, not re-entry (design §1b "trigger") — the clock
                // is not restarted, only kept alive — and so is leaving and
                // coming back inside the hour, because nothing prunes the
                // entry until a full interval of no contact has passed.
                lastContactTicks[index] = now;
                if (now >= nextScratchTicks[index])
                {
                    Scratch(pawn, vine);
                    int interval = Mathf.Max(1, vine.Props.contactIntervalTicks);
                    contactIntervals[index] = interval;
                    nextScratchTicks[index] = now + interval;
                }
            }
        }

        private void Prune(int now)
        {
            for (int i = contactPawns.Count - 1; i >= 0; i--)
            {
                Pawn pawn = contactPawns[i];
                bool gone = pawn == null || pawn.Dead || !pawn.Spawned || pawn.Map != map;
                if (gone || now - lastContactTicks[i] > contactIntervals[i])
                {
                    contactPawns.RemoveAt(i);
                    lastContactTicks.RemoveAt(i);
                    nextScratchTicks.RemoveAt(i);
                    contactIntervals.RemoveAt(i);
                }
            }
        }

        private int IndexOf(Pawn pawn)
        {
            for (int i = 0; i < contactPawns.Count; i++)
            {
                if (contactPawns[i] == pawn)
                {
                    return i;
                }
            }

            return -1;
        }

        // Race-level opt-out, plus vanilla's own per-kind trap immunity. The
        // second is beyond what the item's prose asked for and is recorded as
        // a build decision: PawnKindDef.immuneToTraps is the exact vanilla
        // flag for "a hazard sitting on the ground does not catch this kind",
        // Building_Trap.SpringChance honours it, and a contact-venom stand is
        // that same class of hazard. Without it a scripted or quest-critical
        // kind that vanilla is careful never to trap could be killed by a
        // plant.
        private static bool IsImmune(Pawn pawn)
        {
            if (pawn.def != null && pawn.def.HasModExtension<ContactVenomImmunity>())
            {
                return true;
            }

            if (pawn.kindDef != null && pawn.kindDef.immuneToTraps)
            {
                return true;
            }

            return false;
        }

        private static void Scratch(Pawn pawn, CompContactVenom vine)
        {
            CompProperties_ContactVenom props = vine.Props;
            DamageDef damage = props.damageDef ?? DamageDefOf.Scratch;

            float amount = props.damageAmount
                         * RM_EnvironmentalHazardsSettings.hazardDamageMultiplier
                         * RM_EnvironmentalHazardsSettings.contactVenomScratchMultiplier;
            if (amount <= 0f)
            {
                return;
            }

            // Instigator is the VINE THING, never a pawn (design §1b "who it
            // hurts"): a Thing instigator means no manhunter response and no
            // faction relation hit, while still naming the vine in the health
            // tab and the combat log.
            DamageInfo dinfo = new DamageInfo(
                damage,
                amount,
                props.armorPenetration,
                -1f,
                vine.parent,
                null,
                vine.parent.def,
                DamageInfo.SourceCategory.ThingOrUnknown,
                vine.parent);
            dinfo.SetBodyRegion(props.bodyHeight, BodyPartDepth.Outside);

            pawn.TakeDamage(dinfo);

            ApplyLethalityOption(pawn, damage);
        }

        // Mod option: venom lethality off. lethalSeverity is a HediffDef
        // field the engine reads directly, so the toggle cannot live in XML —
        // and severity on these hediffs only ever RISES from a scratch
        // (severityPerDay is negative), so clamping immediately after each
        // scratch is complete coverage of the only path to the lethal
        // threshold. 0.99x rather than the threshold itself because
        // Hediff.Severity's own setter clamps an assignment AT lethalSeverity
        // and Pawn_HealthTracker then reads >= as dead.
        //
        // Turning the option off never heals anyone: a carrier already past
        // the threshold is not rescued, it is simply no longer pushed further.
        private static void ApplyLethalityOption(Pawn pawn, DamageDef damage)
        {
            if (RM_EnvironmentalHazardsSettings.contactVenomLethal)
            {
                return;
            }

            if (damage.additionalHediffs == null || pawn.health == null)
            {
                return;
            }

            for (int i = 0; i < damage.additionalHediffs.Count; i++)
            {
                HediffDef hediffDef = damage.additionalHediffs[i].hediff;
                if (hediffDef == null || hediffDef.lethalSeverity <= 0f)
                {
                    continue;
                }

                Hediff hediff = pawn.health.hediffSet.GetFirstHediffOfDef(hediffDef);
                if (hediff == null)
                {
                    continue;
                }

                float ceiling = hediffDef.lethalSeverity * 0.99f;
                if (hediff.Severity > ceiling)
                {
                    hediff.Severity = ceiling;
                }
            }
        }

        private static void Truncate<T>(List<T> list, int count)
        {
            while (list.Count > count)
            {
                list.RemoveAt(list.Count - 1);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref contactPawns, "contactPawns", LookMode.Reference);
            Scribe_Collections.Look(ref lastContactTicks, "lastContactTicks", LookMode.Value);
            Scribe_Collections.Look(ref nextScratchTicks, "nextScratchTicks", LookMode.Value);
            Scribe_Collections.Look(ref contactIntervals, "contactIntervals", LookMode.Value);

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                contactPawns ??= new List<Pawn>();
                lastContactTicks ??= new List<int>();
                nextScratchTicks ??= new List<int>();
                contactIntervals ??= new List<int>();

                // A saved Pawn reference can come back null (the pawn was
                // removed by something else between save and load), and the
                // four lists must stay index-aligned or every clock after the
                // gap belongs to the wrong pawn. Drop any row that is not
                // fully intact rather than trying to repair it — the cost of
                // dropping one is one extra scratch, and the cost of a
                // misaligned row is a pawn carrying a stranger's clock.
                int rows = Mathf.Min(
                    Mathf.Min(contactPawns.Count, lastContactTicks.Count),
                    Mathf.Min(nextScratchTicks.Count, contactIntervals.Count));
                Truncate(contactPawns, rows);
                Truncate(lastContactTicks, rows);
                Truncate(nextScratchTicks, rows);
                Truncate(contactIntervals, rows);

                for (int i = rows - 1; i >= 0; i--)
                {
                    if (contactPawns[i] == null)
                    {
                        contactPawns.RemoveAt(i);
                        lastContactTicks.RemoveAt(i);
                        nextScratchTicks.RemoveAt(i);
                        contactIntervals.RemoveAt(i);
                    }
                }
            }
        }
    }
}
