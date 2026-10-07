using System.Collections.Generic;
using System.Text;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1 — the six further venomvine forms
    // (owner ruling 2026-10-03, "build all six"). Defs:
    // Defs/ThingDefs_Plants/RM_VenomvineSixForms.xml and
    // Defs/ThingDefs_Items/RM_VenomvineFormSupport.xml.
    //
    // Shape copied from RM_TwitcherLash.cs and RM_SmotherCraft.cs: plants only
    // TickLong (~33 s), so every comp here is DATA (tuning, Scribed state, the
    // inspect line) and registers itself with ONE MapComponent that does the
    // work. The registry is transient, rebuilt from PostSpawnSetup on load.
    //
    //   Rearing   pawn sweep: a body that has to push into the stand rears it;
    //             a light message (masked by the Gale), invisible pawns inside
    //             are revealed while it stands reared.
    //   Walking   on each Gale's onset: runners downwind of the leading edge,
    //             the fully grown tail dies back to dead venomvine. Map cap.
    //   Hoard     slow sweep: loose items (and the gear of corpses) in or next
    //             to the stand are grown in after a few hours; despawning the
    //             stand drops everything.
    //   Quench    fire sweep: a fire within reach bursts vanilla's firefoam
    //             explosion, then the stand is spent for days.
    //   Sworn     this mod's own venom scratch (RM_CompMarkedThorns), which
    //             spares pawns carrying the sap-mark hediff. Also used, with a
    //             growth gate and no sparing, by the walking stand's runners.
    //   Shedding  on each Gale's onset: a V of RM_ThornLitter downwind; the
    //             litter scratches weakly through the same pawn sweep.
    //
    // Downwind is RM_MapComponent_Lean's locked heading: on a map that does
    // not lean (or with the Lean off) walking and shedding stands stay put.
    // ════════════════════════════════════════════════════════════════════

    // ── Sworn (and walking runners): the scratch with a per-pawn exemption ──
    public class RM_CompProperties_MarkedThorns : CompProperties
    {
        public DamageDef damageDef;
        public float damageAmount = 3f;
        public float armorPenetration = 0.05f;
        public int contactIntervalTicks = 2500;
        public BodyPartHeight bodyHeight = BodyPartHeight.Bottom;
        // Below this growth the canes are soft: no scratch.
        public float minGrowth;
        // A pawn carrying this hediff is spared. Null spares nobody.
        public HediffDef sparingHediff;

        public RM_CompProperties_MarkedThorns()
        {
            compClass = typeof(RM_CompMarkedThorns);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (damageDef == null)
            {
                yield return "RM_CompProperties_MarkedThorns has no damageDef.";
            }
        }
    }

    public class RM_CompMarkedThorns : ThingComp
    {
        public RM_CompProperties_MarkedThorns Props => (RM_CompProperties_MarkedThorns)props;

        public float Growth => parent is Plant plant ? plant.Growth : 1f;

        public bool Armed => Growth >= Props.minGrowth;

        public bool Spares(Pawn p)
        {
            return Props.sparingHediff != null
                && RM_WindCalendar.On(RM_LeaningScrubSettings.swornSparesMarkedEnabled)
                && p.health?.hediffSet != null
                && p.health.hediffSet.HasHediff(Props.sparingHediff);
        }

        public override string CompInspectStringExtra()
        {
            if (!Armed)
            {
                return "Soft young cane: no thorns yet.";
            }
            if (Props.sparingHediff != null && RM_WindCalendar.On(RM_LeaningScrubSettings.swornSparesMarkedEnabled))
            {
                return "Spares anyone carrying " + Props.sparingHediff.label + ".";
            }
            return null;
        }
    }

    // On a filth def: the weak scratch of shed thorns.
    public class RM_ThornLitterExtension : DefModExtension
    {
        public DamageDef damageDef;
        public float damageAmount = 1f;
        public float armorPenetration = 0.02f;
        public int contactIntervalTicks = 2500;
    }

    // ── Rearing ──
    public class RM_CompProperties_Rearing : CompProperties
    {
        public float minBodySize = 0.8f;
        public float minGrowth = 0.5f;
        // Rear duration multiplier while the Stall holds ("doubly loud").
        public float stallFactor = 2f;

        public RM_CompProperties_Rearing()
        {
            compClass = typeof(RM_CompRearing);
        }
    }

    public class RM_CompRearing : RM_FormComp
    {
        private int rearedUntilTick = -1;

        public RM_CompProperties_Rearing Props => (RM_CompProperties_Rearing)props;

        public bool Reared => Find.TickManager.TicksGame < rearedUntilTick;

        public void Rear(int ticks)
        {
            rearedUntilTick = Mathf.Max(rearedUntilTick, Find.TickManager.TicksGame + ticks);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref rearedUntilTick, "rmRearedUntilTick", -1);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.rearingEnabled) || !Reared)
            {
                return null;
            }
            return "Reared upright against the lean: settles in "
                + (rearedUntilTick - Find.TickManager.TicksGame).ToStringTicksToPeriod() + ".";
        }
    }

    // ── Walking ──
    public class RM_CompProperties_Walking : CompProperties
    {
        public float runnerGrowth = 0.05f;
        public int maxStep = 2;
        public float tailDieChance = 0.5f;
        public int tailYield = 10;

        public RM_CompProperties_Walking()
        {
            compClass = typeof(RM_CompWalking);
        }
    }

    public class RM_CompWalking : RM_FormComp
    {
        public RM_CompProperties_Walking Props => (RM_CompProperties_Walking)props;
    }

    // ── Shedding ──
    public class RM_CompProperties_Shedding : CompProperties
    {
        public ThingDef litterDef;
        public float cellChance = 0.6f;
        public float minGrowth = 0.75f;

        public RM_CompProperties_Shedding()
        {
            compClass = typeof(RM_CompShedding);
        }
    }

    public class RM_CompShedding : RM_FormComp
    {
        public RM_CompProperties_Shedding Props => (RM_CompProperties_Shedding)props;
    }

    // ── Quench ──
    public class RM_CompProperties_Quench : CompProperties
    {
        public float triggerRadius = 1.5f;
        public float burstRadius = 4.9f;
        public float minGrowth = 0.5f;

        public RM_CompProperties_Quench()
        {
            compClass = typeof(RM_CompQuench);
        }
    }

    public class RM_CompQuench : RM_FormComp
    {
        private int readyTick = -1;

        public RM_CompProperties_Quench Props => (RM_CompProperties_Quench)props;

        public bool Ready => Find.TickManager.TicksGame >= readyTick;

        public float Growth => parent is Plant plant ? plant.Growth : 1f;

        public void Burst(Map map)
        {
            IntVec3 pos = parent.Position;
            readyTick = Find.TickManager.TicksGame
                + Mathf.RoundToInt(Mathf.Max(0.1f, RM_LeaningScrubSettings.quenchRecoveryDays) * GenDate.TicksPerDay);
            // Values read off vanilla FirefoamPopper's CompProperties_Explosive.
            GenExplosion.DoExplosion(pos, map, Props.burstRadius, DamageDefOf.Extinguish, parent,
                postExplosionSpawnThingDef: ThingDefOf.Filth_FireFoam, postExplosionSpawnChance: 1f,
                postExplosionSpawnThingCount: 1, applyDamageToExplosionCellsNeighbors: true);
            Messages.Message("A quench venomvine has burst and drenched the fire around it.",
                new TargetInfo(pos, map), MessageTypeDefOf.NeutralEvent, false);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref readyTick, "rmQuenchReadyTick", -1);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.quenchEnabled))
            {
                return null;
            }
            if (Ready)
            {
                return Growth >= Props.minGrowth ? "Knuckles swollen: will burst at fire." : null;
            }
            return "Spent, knuckles cracked: swells again in "
                + (readyTick - Find.TickManager.TicksGame).ToStringTicksToPeriod() + ".";
        }
    }

    // ── Hoard ──
    public class RM_CompProperties_Hoard : CompProperties
    {
        public int maxHeld = 40;
        public float minGrowth = 0.5f;

        public RM_CompProperties_Hoard()
        {
            compClass = typeof(RM_CompHoard);
        }
    }

    public class RM_CompHoard : RM_FormComp, IThingHolder
    {
        private ThingOwner<Thing> held;
        // Thing -> the tick it was first seen lying against the stand. Saved so a
        // reload does not restart every clock.
        private Dictionary<Thing, int> firstSeen = new Dictionary<Thing, int>();
        private List<Thing> tmpKeys;
        private List<int> tmpValues;
        private IntVec3 cachedPos = IntVec3.Invalid;

        public RM_CompProperties_Hoard Props => (RM_CompProperties_Hoard)props;

        public float Growth => parent is Plant plant ? plant.Growth : 1f;

        public int HeldCount => held?.Count ?? 0;

        public RM_CompHoard()
        {
            held = new ThingOwner<Thing>(this);
        }

        // IThingHolder.ParentHolder is ThingComp's own (parent.ParentHolder), the CompTransporter shape.
        public ThingOwner GetDirectlyHeldThings()
        {
            return held;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            cachedPos = parent.Position;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            // Cut, smothered, burned or killed: everything it kept falls out on the spot.
            if (map != null && held.Count > 0 && cachedPos.IsValid)
            {
                held.TryDropAll(cachedPos, map, ThingPlaceMode.Near);
                Messages.Message("A hoard venomvine has fallen and given back what it kept.",
                    new TargetInfo(cachedPos, map), MessageTypeDefOf.PositiveEvent, false);
            }
            firstSeen.Clear();
        }

        // Called by the MapComponent's slow sweep.
        public void Sweep(Map map, int now, int growInTicks, bool keepDeadGear)
        {
            if (Growth < Props.minGrowth)
            {
                return;
            }
            IntVec3 root = parent.Position;
            for (int i = 0; i < 9 && held.Count < Props.maxHeld; i++)
            {
                IntVec3 c = root + GenAdj.AdjacentCellsAndInside[i];
                if (!c.InBounds(map))
                {
                    continue;
                }
                List<Thing> list = c.GetThingList(map);
                for (int j = list.Count - 1; j >= 0 && held.Count < Props.maxHeld; j--)
                {
                    Thing t = list[j];
                    if (t.def.category != ThingCategory.Item || !t.def.EverHaulable)
                    {
                        continue;
                    }
                    if (t is Corpse && !keepDeadGear)
                    {
                        continue;
                    }
                    if (!firstSeen.TryGetValue(t, out int seen))
                    {
                        firstSeen[t] = now;
                        continue;
                    }
                    if (now - seen < growInTicks)
                    {
                        continue;
                    }
                    firstSeen.Remove(t);
                    if (t is Corpse corpse)
                    {
                        TakeGear(corpse);
                    }
                    else
                    {
                        t.DeSpawn();
                        if (!held.TryAdd(t))
                        {
                            GenPlace.TryPlaceThing(t, c, map, ThingPlaceMode.Near);
                        }
                    }
                }
            }
            Prune();
        }

        // The corpse stays where it fell; its clothes and weapons go into the cane.
        private void TakeGear(Corpse corpse)
        {
            Pawn dead = corpse.InnerPawn;
            if (dead == null)
            {
                return;
            }
            if (dead.equipment != null)
            {
                List<ThingWithComps> eq = new List<ThingWithComps>(dead.equipment.AllEquipmentListForReading);
                for (int i = 0; i < eq.Count && held.Count < Props.maxHeld; i++)
                {
                    dead.equipment.Remove(eq[i]);
                    held.TryAdd(eq[i]);
                }
            }
            if (dead.apparel != null)
            {
                List<Apparel> worn = new List<Apparel>(dead.apparel.WornApparel);
                for (int i = 0; i < worn.Count && held.Count < Props.maxHeld; i++)
                {
                    dead.apparel.Remove(worn[i]);
                    held.TryAdd(worn[i]);
                }
            }
        }

        private void Prune()
        {
            if (firstSeen.Count == 0)
            {
                return;
            }
            List<Thing> gone = null;
            foreach (KeyValuePair<Thing, int> kv in firstSeen)
            {
                Thing t = kv.Key;
                if (t == null || !t.Spawned || t.Map != parent.Map
                    || (t.Position - parent.Position).LengthHorizontalSquared > 2)
                {
                    (gone ??= new List<Thing>()).Add(t);
                }
            }
            if (gone != null)
            {
                for (int i = 0; i < gone.Count; i++)
                {
                    firstSeen.Remove(gone[i]);
                }
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref held, "rmHoardHeld", this);
            Scribe_Collections.Look(ref firstSeen, "rmHoardFirstSeen", LookMode.Reference, LookMode.Value,
                ref tmpKeys, ref tmpValues);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                held ??= new ThingOwner<Thing>(this);
                firstSeen ??= new Dictionary<Thing, int>();
                firstSeen.RemoveAll(kv => kv.Key == null);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.hoardEnabled) && held.Count == 0)
            {
                return null;
            }
            if (held.Count == 0)
            {
                return "Holds nothing yet.";
            }
            StringBuilder sb = new StringBuilder("Holds " + held.Count + ": ");
            int shown = Mathf.Min(held.Count, 6);
            for (int i = 0; i < shown; i++)
            {
                if (i > 0)
                {
                    sb.Append(", ");
                }
                sb.Append(held[i].LabelCap);
            }
            if (held.Count > shown)
            {
                sb.Append(" and " + (held.Count - shown) + " more");
            }
            sb.Append(".");
            return sb.ToString();
        }
    }

    // Base for the comps the MapComponent needs to find without a lister scan.
    public abstract class RM_FormComp : ThingComp
    {
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            parent.Map?.GetComponent<RM_MapComponent_VenomvineForms>()?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map?.GetComponent<RM_MapComponent_VenomvineForms>()?.Deregister(this);
        }
    }

    public class RM_MapComponent_VenomvineForms : MapComponent
    {
        private const int ThornInterval = 15;     // MapComponent_ContactVenom's own cadence
        private const int RearInterval = 30;      // the twitcher's
        private const int QuenchInterval = 60;
        private const int HoardInterval = 250;
        private const int RearMessageGap = 1200;

        private readonly HashSet<RM_CompRearing> rearing = new HashSet<RM_CompRearing>();
        private readonly HashSet<RM_CompWalking> walking = new HashSet<RM_CompWalking>();
        private readonly HashSet<RM_CompShedding> shedding = new HashSet<RM_CompShedding>();
        private readonly HashSet<RM_CompQuench> quench = new HashSet<RM_CompQuench>();
        private readonly HashSet<RM_CompHoard> hoard = new HashSet<RM_CompHoard>();

        // Per-pawn scratch clocks for the marked thorns and the litter. Not saved:
        // after a load a pawn already standing in a stand takes at most one early
        // scratch, the cost MapComponent_ContactVenom's comment weighs the other way.
        private readonly Dictionary<Pawn, int> nextThornTick = new Dictionary<Pawn, int>();
        private readonly Dictionary<Pawn, int> nextLitterTick = new Dictionary<Pawn, int>();
        private readonly List<Pawn> tmpPawns = new List<Pawn>();
        private readonly List<Pawn> tmpGone = new List<Pawn>();

        // Saved, so a save made mid-Gale does not re-fire the onset on load.
        private bool wasGale;
        private int lastRearMessageTick = -99999;

        public RM_MapComponent_VenomvineForms(Map map) : base(map)
        {
        }

        public void Register(RM_FormComp c)
        {
            switch (c)
            {
                case RM_CompRearing r: rearing.Add(r); break;
                case RM_CompWalking w: walking.Add(w); break;
                case RM_CompShedding s: shedding.Add(s); break;
                case RM_CompQuench q: quench.Add(q); break;
                case RM_CompHoard h: hoard.Add(h); break;
            }
        }

        public void Deregister(RM_FormComp c)
        {
            switch (c)
            {
                case RM_CompRearing r: rearing.Remove(r); break;
                case RM_CompWalking w: walking.Remove(w); break;
                case RM_CompShedding s: shedding.Remove(s); break;
                case RM_CompQuench q: quench.Remove(q); break;
                case RM_CompHoard h: hoard.Remove(h); break;
            }
        }

        public int WalkingCellCount => walking.Count;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wasGale, "rmFormsWasGale", false);
        }

        public override void MapComponentTick()
        {
            if (!RM_LeaningScrubSettings.modEnabled)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;

            if (now % ThornInterval == 0)
            {
                SweepThorns(now);
            }
            if (now % RearInterval == 0 && rearing.Count > 0)
            {
                SweepRearing(now);
            }
            if (now % QuenchInterval == 0 && quench.Count > 0)
            {
                SweepQuench();
            }
            if (now % HoardInterval == 0)
            {
                if (hoard.Count > 0)
                {
                    SweepHoard(now, -1);
                }
                bool gale = RM_WindCalendar.IsGale(map);
                if (gale && !wasGale)
                {
                    GaleOnset();
                }
                wasGale = gale;
            }
        }

        // ── marked thorns and thorn litter: one pawn pass ──
        public void SweepThorns(int now)
        {
            if (!RM_LeaningScrubSettings.modEnabled)
            {
                return;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            if (pawns.Count == 0)
            {
                return;
            }
            tmpPawns.Clear();
            tmpPawns.AddRange(pawns);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (p.Dead || !p.Spawned || p.Flying || IsImmune(p))
                {
                    continue;
                }
                IntVec3 c = p.Position;
                Plant plant = c.GetPlant(map);
                RM_CompMarkedThorns thorns = plant?.GetComp<RM_CompMarkedThorns>();
                if (thorns != null && thorns.Armed && !thorns.Spares(p) && Due(nextThornTick, p, now))
                {
                    RM_CompProperties_MarkedThorns pr = thorns.Props;
                    nextThornTick[p] = now + Mathf.Max(1, pr.contactIntervalTicks);
                    Scratch(p, pr.damageDef, pr.damageAmount, pr.armorPenetration, pr.bodyHeight, plant);
                    continue;
                }
                if (!RM_WindCalendar.On(RM_LeaningScrubSettings.sheddingEnabled))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(map);
                for (int j = 0; j < things.Count; j++)
                {
                    Thing t = things[j];
                    if (t.def.category != ThingCategory.Filth)
                    {
                        continue;
                    }
                    RM_ThornLitterExtension lit = t.def.GetModExtension<RM_ThornLitterExtension>();
                    if (lit == null)
                    {
                        continue;
                    }
                    if (Due(nextLitterTick, p, now))
                    {
                        nextLitterTick[p] = now + Mathf.Max(1, lit.contactIntervalTicks);
                        Scratch(p, lit.damageDef, lit.damageAmount, lit.armorPenetration, BodyPartHeight.Bottom, t);
                    }
                    break;
                }
            }
            tmpPawns.Clear();
            if (now % 2500 == 0)
            {
                PruneClocks(nextThornTick, now);
                PruneClocks(nextLitterTick, now);
            }
        }

        private static bool Due(Dictionary<Pawn, int> clocks, Pawn p, int now)
        {
            return !clocks.TryGetValue(p, out int next) || now >= next;
        }

        private void PruneClocks(Dictionary<Pawn, int> clocks, int now)
        {
            tmpGone.Clear();
            foreach (KeyValuePair<Pawn, int> kv in clocks)
            {
                if (kv.Key == null || kv.Key.Dead || !kv.Key.Spawned || kv.Key.Map != map || now - kv.Value > 2500)
                {
                    tmpGone.Add(kv.Key);
                }
            }
            for (int i = 0; i < tmpGone.Count; i++)
            {
                clocks.Remove(tmpGone[i]);
            }
            tmpGone.Clear();
        }

        // Same opt-outs as MapComponent_ContactVenom.IsImmune (race marker, trap-immune kinds).
        private static bool IsImmune(Pawn p)
        {
            return (p.def != null && p.def.HasModExtension<ContactVenomImmunity>())
                || (p.kindDef != null && p.kindDef.immuneToTraps);
        }

        // MapComponent_ContactVenom.Scratch's shape, honouring the kit's own venom settings.
        private static void Scratch(Pawn p, DamageDef damageDef, float baseAmount, float ap, BodyPartHeight height, Thing source)
        {
            if (!RM_EnvironmentalHazardsSettings.contactVenomEnabled)
            {
                return;
            }
            DamageDef damage = damageDef ?? DamageDefOf.Scratch;
            float amount = baseAmount * RM_EnvironmentalHazardsSettings.hazardDamageMultiplier
                * RM_EnvironmentalHazardsSettings.contactVenomScratchMultiplier;
            if (amount <= 0f)
            {
                return;
            }
            DamageInfo dinfo = new DamageInfo(damage, amount, ap, -1f, source, null, source.def,
                DamageInfo.SourceCategory.ThingOrUnknown, source);
            dinfo.SetBodyRegion(height, BodyPartDepth.Outside);
            p.TakeDamage(dinfo);
            if (RM_EnvironmentalHazardsSettings.contactVenomLethal || damage.additionalHediffs == null || p.health == null)
            {
                return;
            }
            for (int i = 0; i < damage.additionalHediffs.Count; i++)
            {
                HediffDef hd = damage.additionalHediffs[i].hediff;
                if (hd == null || hd.lethalSeverity <= 0f)
                {
                    continue;
                }
                Hediff h = p.health.hediffSet.GetFirstHediffOfDef(hd);
                if (h != null && h.Severity > hd.lethalSeverity * 0.99f)
                {
                    h.Severity = hd.lethalSeverity * 0.99f;
                }
            }
        }

        // ── rearing ──
        public void SweepRearing(int now)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.rearingEnabled))
            {
                return;
            }
            int ticks = Mathf.RoundToInt(Mathf.Max(0.05f, RM_LeaningScrubSettings.rearingHours) * GenDate.TicksPerHour);
            bool stall = RM_WindCalendar.IsStall(map);
            bool gale = RM_WindCalendar.IsGale(map);
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || !p.Spawned || p.Flying)
                {
                    continue;
                }
                Plant plant = p.Position.GetPlant(map);
                RM_CompRearing rear = plant?.GetComp<RM_CompRearing>();
                if (rear == null || plant.Growth < rear.Props.minGrowth)
                {
                    continue;
                }
                bool wasReared = rear.Reared;
                if (p.BodySize >= rear.Props.minBodySize)
                {
                    rear.Rear(stall ? Mathf.RoundToInt(ticks * rear.Props.stallFactor) : ticks);
                    if (!wasReared && !gale && ShouldAlert(p) && now - lastRearMessageTick >= RearMessageGap)
                    {
                        lastRearMessageTick = now;
                        Messages.Message("A rearing venomvine has stood up: " + p.LabelShort + " is pushing through it.",
                            new LookTargets(plant), MessageTypeDefOf.NeutralEvent, false);
                    }
                }
                // Anyone inside a reared stand cannot stay hidden.
                if (rear.Reared)
                {
                    p.GetInvisibilityComp()?.BecomeVisible();
                }
            }
        }

        // The player's own colonists and tame animals rear the stand (anything watching can see
        // it) but do not message the player about themselves.
        private static bool ShouldAlert(Pawn p)
        {
            return p.Faction != Faction.OfPlayer && (p.RaceProps.Humanlike || p.HostileTo(Faction.OfPlayer));
        }

        // ── quench ──
        private readonly List<RM_CompQuench> tmpQuench = new List<RM_CompQuench>();

        public int SweepQuench()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.quenchEnabled))
            {
                return 0;
            }
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            if (fires.NullOrEmpty())
            {
                return 0;
            }
            tmpQuench.Clear();
            foreach (RM_CompQuench q in quench)
            {
                if (!q.parent.Spawned || !q.Ready || q.Growth < q.Props.minGrowth)
                {
                    continue;
                }
                float r2 = q.Props.triggerRadius * q.Props.triggerRadius;
                for (int i = 0; i < fires.Count; i++)
                {
                    if ((fires[i].Position - q.parent.Position).LengthHorizontalSquared <= r2)
                    {
                        tmpQuench.Add(q);
                        break;
                    }
                }
            }
            int burst = 0;
            for (int i = 0; i < tmpQuench.Count; i++)
            {
                if (tmpQuench[i].parent.Spawned)
                {
                    tmpQuench[i].Burst(map);
                    burst++;
                }
            }
            tmpQuench.Clear();
            return burst;
        }

        // ── hoard ──
        private readonly List<RM_CompHoard> tmpHoard = new List<RM_CompHoard>();

        // growInOverride >= 0 replaces the Mod Setting (the proof hook only).
        public void SweepHoard(int now, int growInOverride)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.hoardEnabled))
            {
                return;
            }
            int growIn = growInOverride >= 0 ? growInOverride : Mathf.RoundToInt(Mathf.Max(0.05f, RM_LeaningScrubSettings.hoardGrowInHours) * GenDate.TicksPerHour);
            tmpHoard.Clear();
            tmpHoard.AddRange(hoard);
            for (int i = 0; i < tmpHoard.Count; i++)
            {
                if (tmpHoard[i].parent.Spawned)
                {
                    tmpHoard[i].Sweep(map, now, growIn, RM_LeaningScrubSettings.hoardKeepsDeadGear);
                }
            }
            tmpHoard.Clear();
        }

        // ── the Gale's onset: walking and shedding ──
        public void GaleOnset()
        {
            RM_MapComponent_Lean lean = RM_MapComponent_Lean.For(map);
            if (lean == null)
            {
                return;
            }
            Vector2 dir = lean.Downwind;
            Walk(dir);
            Shed(dir);
        }

        private static IntVec3 Step(IntVec3 from, Vector2 dir, float k)
        {
            return new IntVec3(from.x + Mathf.RoundToInt(dir.x * k), 0, from.z + Mathf.RoundToInt(dir.y * k));
        }

        private bool IsWalking(IntVec3 c)
        {
            return c.InBounds(map) && c.GetPlant(map)?.GetComp<RM_CompWalking>() != null;
        }

        public void Walk(Vector2 dir)
        {
            if (walking.Count == 0 || !RM_WindCalendar.On(RM_LeaningScrubSettings.walkingEnabled))
            {
                return;
            }
            int cap = Mathf.Max(0, RM_LeaningScrubSettings.walkingMaxCellsPerMap);
            List<RM_CompWalking> cells = new List<RM_CompWalking>(walking);
            // Group into stands (8-connected); a smothered cell anywhere stops its stand.
            HashSet<IntVec3> seen = new HashSet<IntVec3>();
            Dictionary<IntVec3, RM_CompWalking> byCell = new Dictionary<IntVec3, RM_CompWalking>();
            for (int i = 0; i < cells.Count; i++)
            {
                if (cells[i].parent.Spawned)
                {
                    byCell[cells[i].parent.Position] = cells[i];
                }
            }
            int total = byCell.Count;
            List<Thing> tailKills = new List<Thing>();
            foreach (IntVec3 start in byCell.Keys)
            {
                if (seen.Contains(start))
                {
                    continue;
                }
                List<RM_CompWalking> stand = new List<RM_CompWalking>();
                bool smothered = false;
                Queue<IntVec3> open = new Queue<IntVec3>();
                open.Enqueue(start);
                seen.Add(start);
                while (open.Count > 0)
                {
                    IntVec3 c = open.Dequeue();
                    RM_CompWalking w = byCell[c];
                    stand.Add(w);
                    RM_CompSmotherable sm = w.parent.TryGetComp<RM_CompSmotherable>();
                    if (sm != null && sm.Smothered)
                    {
                        smothered = true;
                    }
                    for (int k = 0; k < 8; k++)
                    {
                        IntVec3 n = c + GenAdj.AdjacentCells[k];
                        if (byCell.ContainsKey(n) && seen.Add(n))
                        {
                            open.Enqueue(n);
                        }
                    }
                }
                if (smothered)
                {
                    continue;
                }
                for (int s = 0; s < stand.Count; s++)
                {
                    RM_CompWalking w = stand[s];
                    Plant plant = w.parent as Plant;
                    if (plant == null || plant.Growth < 0.5f)
                    {
                        continue;
                    }
                    IntVec3 pos = plant.Position;
                    // Leading edge: nothing of the stand directly downwind.
                    if (total < cap && !IsWalking(Step(pos, dir, 1f)))
                    {
                        int k = Rand.RangeInclusive(1, Mathf.Max(1, w.Props.maxStep));
                        IntVec3 dest = Step(pos, dir, k);
                        if (dest.InBounds(map) && dest.GetPlant(map) == null && dest.GetEdifice(map) == null
                            && plant.def.CanEverPlantAt(dest, map))
                        {
                            Plant runner = (Plant)ThingMaker.MakeThing(plant.def);
                            runner.Growth = w.Props.runnerGrowth;
                            GenSpawn.Spawn(runner, dest, map);
                            total++;
                        }
                    }
                    // Tail: nothing of the stand directly upwind, fully grown.
                    if (plant.Growth >= 0.999f && stand.Count > 1 && !IsWalking(Step(pos, dir, -1f))
                        && Rand.Chance(w.Props.tailDieChance))
                    {
                        tailKills.Add(plant);
                    }
                }
            }
            for (int i = 0; i < tailKills.Count; i++)
            {
                Thing t = tailKills[i];
                if (!t.Spawned)
                {
                    continue;
                }
                IntVec3 pos = t.Position;
                int yield = t.TryGetComp<RM_CompWalking>()?.Props.tailYield ?? 0;
                t.Destroy(DestroyMode.Vanish);
                if (yield > 0 && RM_LeaningScrubDefOf.RM_DeadVenomvine != null)
                {
                    Thing wood = ThingMaker.MakeThing(RM_LeaningScrubDefOf.RM_DeadVenomvine);
                    wood.stackCount = Mathf.Min(yield, wood.def.stackLimit);
                    GenPlace.TryPlaceThing(wood, pos, map, ThingPlaceMode.Near);
                }
            }
        }

        public void Shed(Vector2 dir)
        {
            if (shedding.Count == 0 || !RM_WindCalendar.On(RM_LeaningScrubSettings.sheddingEnabled))
            {
                return;
            }
            int length = Mathf.Max(1, RM_LeaningScrubSettings.sheddingLength);
            Vector2 side = new Vector2(-dir.y, dir.x);
            List<RM_CompShedding> stands = new List<RM_CompShedding>(shedding);
            for (int i = 0; i < stands.Count; i++)
            {
                RM_CompShedding s = stands[i];
                Plant plant = s.parent as Plant;
                if (plant == null || !plant.Spawned || plant.Growth < s.Props.minGrowth || s.Props.litterDef == null)
                {
                    continue;
                }
                IntVec3 root = plant.Position;
                for (int d = 1; d <= length; d++)
                {
                    int half = d / 3;    // the V widens a cell either side every three cells out
                    for (int w = -half; w <= half; w++)
                    {
                        if (!Rand.Chance(s.Props.cellChance))
                        {
                            continue;
                        }
                        IntVec3 c = new IntVec3(root.x + Mathf.RoundToInt(dir.x * d + side.x * w), 0,
                            root.z + Mathf.RoundToInt(dir.y * d + side.y * w));
                        if (c.InBounds(map) && c.Walkable(map))
                        {
                            FilthMaker.TryMakeFilth(c, map, s.Props.litterDef);
                        }
                    }
                }
            }
        }
    }


    // The validation hook (validation.py chain "forms", via jawa/static_call), the
    // RM_FireStampProof shape: build a fixture on the current map, drive the SHIPPED
    // pass directly, read the state, clean up, restore every setting it touched.
    // args = "<form>|on" or "<form>|off". Answers PASS / FAIL / UNMEASURED text.
    public static class RM_VenomvineFormsProof
    {
        private static IntVec3 FindSpot(Map map)
        {
            foreach (IntVec3 c in map.AllCells)
            {
                if (c.x < 30 || c.z < 30 || c.x > map.Size.x - 30 || c.z > map.Size.z - 30) continue;
                if (c.x % 7 != 0 || c.z % 7 != 0) continue;
                bool ok = true;
                foreach (IntVec3 o in GenRadial.RadialCellsAround(c, 12f, true))
                {
                    if (!o.InBounds(map) || !o.Standable(map) || o.Roofed(map) || o.GetFirstPawn(map) != null
                        || o.GetEdifice(map) != null || map.fertilityGrid.FertilityAt(o) < 0.7f
                        || map.thingGrid.ThingAt(o, ThingDefOf.Fire) != null) { ok = false; break; }
                }
                if (ok) return c;
            }
            return IntVec3.Invalid;
        }

        private static Plant Stand(Map map, string defName, IntVec3 c, float growth, List<Thing> made)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (def == null) return null;
            c.GetPlant(map)?.Destroy();
            Plant p = (Plant)ThingMaker.MakeThing(def);
            p.Growth = growth;
            GenSpawn.Spawn(p, c, map);
            made.Add(p);
            return p;
        }

        private static Pawn Colonist(Map map, IntVec3 c, List<Thing> made)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            GenSpawn.Spawn(p, c, map);
            made.Add(p);
            return p;
        }

        private static int Injuries(Pawn p)
        {
            int n = 0;
            foreach (Hediff h in p.health.hediffSet.hediffs)
            {
                if (h is Hediff_Injury) n++;
            }
            return n;
        }

        private static int CountDefIn(Map map, ThingDef def, IntVec3 root, float radius)
        {
            int n = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(root, radius, true))
            {
                if (c.InBounds(map) && map.thingGrid.ThingAt(c, def) != null) n++;
            }
            return n;
        }

        public static string ProofForm(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            RM_MapComponent_VenomvineForms comp = map.GetComponent<RM_MapComponent_VenomvineForms>();
            if (comp == null) return "FAIL: RM_MapComponent_VenomvineForms not on the map";
            string[] parts = (args ?? "").Split('|');
            string form = parts[0];
            bool on = parts.Length < 2 || parts[1] != "off";
            var made = new List<Thing>();
            bool sMod = RM_LeaningScrubSettings.modEnabled, sRear = RM_LeaningScrubSettings.rearingEnabled,
                sWalk = RM_LeaningScrubSettings.walkingEnabled, sHoard = RM_LeaningScrubSettings.hoardEnabled,
                sQuench = RM_LeaningScrubSettings.quenchEnabled, sSworn = RM_LeaningScrubSettings.swornSparesMarkedEnabled,
                sShed = RM_LeaningScrubSettings.sheddingEnabled, sVenom = RM_EnvironmentalHazardsSettings.contactVenomEnabled;
            int sCap = RM_LeaningScrubSettings.walkingMaxCellsPerMap;
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                IntVec3 spot = FindSpot(map);
                if (!spot.IsValid) return "UNMEASURED: no open, unroofed, fertile 12-cell disc on this map";
                int now = Find.TickManager.TicksGame;
                switch (form)
                {
                    case "rearing":
                    {
                        RM_LeaningScrubSettings.rearingEnabled = on;
                        Plant st = Stand(map, "RM_RearingVenomvine", spot, 1f, made);
                        if (st == null) return "FAIL: RM_RearingVenomvine did not resolve";
                        RM_CompRearing r = st.GetComp<RM_CompRearing>();
                        if (r == null) return "FAIL: RM_RearingVenomvine carries no RM_CompRearing";
                        Colonist(map, spot, made);
                        comp.SweepRearing(now);
                        string st2 = "reared=" + r.Reared;
                        if (on) return r.Reared ? "PASS " + st2 : "FAIL: a colonist inside the stand did not rear it " + st2;
                        return r.Reared ? "FAIL: rearingEnabled off but the stand reared " + st2 : "PASS off " + st2;
                    }
                    case "sworn":
                    {
                        RM_LeaningScrubSettings.swornSparesMarkedEnabled = on;
                        RM_EnvironmentalHazardsSettings.contactVenomEnabled = true;
                        HediffDef mark = DefDatabase<HediffDef>.GetNamedSilentFail("RM_SwornSapMarked");
                        if (mark == null) return "FAIL: RM_SwornSapMarked did not resolve";
                        IntVec3 a = spot, b = spot + new IntVec3(3, 0, 0);
                        if (Stand(map, "RM_SwornVenomvine", a, 1f, made) == null) return "FAIL: RM_SwornVenomvine did not resolve";
                        Stand(map, "RM_SwornVenomvine", b, 1f, made);
                        Pawn marked = Colonist(map, a, made);
                        Pawn bare = Colonist(map, b, made);
                        marked.health.AddHediff(mark);
                        int m0 = Injuries(marked), b0 = Injuries(bare);
                        comp.SweepThorns(now);
                        int m1 = Injuries(marked), b1 = Injuries(bare);
                        string st = string.Format("marked {0}->{1} bare {2}->{3}", m0, m1, b0, b1);
                        if (b1 <= b0) return "UNMEASURED: the unmarked control took no scratch (thorns inert?) " + st;
                        if (on) return m1 == m0 ? "PASS " + st : "FAIL: the sap-marked colonist was scratched " + st;
                        return m1 > m0 ? "PASS off " + st : "FAIL: sparing off but the marked colonist was still spared " + st;
                    }
                    case "hoard":
                    {
                        RM_LeaningScrubSettings.hoardEnabled = on;
                        Plant st = Stand(map, "RM_HoardVenomvine", spot, 1f, made);
                        if (st == null) return "FAIL: RM_HoardVenomvine did not resolve";
                        RM_CompHoard h = st.GetComp<RM_CompHoard>();
                        if (h == null) return "FAIL: RM_HoardVenomvine carries no RM_CompHoard";
                        Thing steel = ThingMaker.MakeThing(ThingDefOf.Steel);
                        steel.stackCount = 7;
                        GenPlace.TryPlaceThing(steel, spot + new IntVec3(1, 0, 0), map, ThingPlaceMode.Direct);
                        made.Add(steel);
                        comp.SweepHoard(now, 0);
                        comp.SweepHoard(now + 1, 0);
                        int heldNow = h.HeldCount;
                        bool steelGone = !steel.Spawned;
                        IntVec3 pos = st.Position;
                        st.Destroy();
                        int back = 0;
                        foreach (Thing t in map.listerThings.ThingsOfDef(ThingDefOf.Steel))
                        {
                            if (t.Position.InHorDistOf(pos, 4f)) { back += t.stackCount; made.Add(t); }
                        }
                        string s2 = string.Format("held={0} steelGone={1} steelBackOnCut={2}", heldNow, steelGone, back);
                        if (on)
                        {
                            if (heldNow < 1 || !steelGone) return "FAIL: steel beside the stand was not grown in " + s2;
                            if (back < 7) return "FAIL: cutting the stand did not give the steel back " + s2;
                            return "PASS " + s2;
                        }
                        return heldNow > 0 || steelGone ? "FAIL: hoardEnabled off but it took the steel " + s2 : "PASS off " + s2;
                    }
                    case "quench":
                    {
                        RM_LeaningScrubSettings.quenchEnabled = on;
                        Plant st = Stand(map, "RM_QuenchVenomvine", spot, 1f, made);
                        if (st == null) return "FAIL: RM_QuenchVenomvine did not resolve";
                        RM_CompQuench q = st.GetComp<RM_CompQuench>();
                        if (q == null) return "FAIL: RM_QuenchVenomvine carries no RM_CompQuench";
                        Fire f = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
                        f.fireSize = 0.6f;
                        GenSpawn.Spawn(f, spot + new IntVec3(1, 0, 0), map);
                        made.Add(f);
                        int burst = comp.SweepQuench();
                        int foam = CountDefIn(map, ThingDefOf.Filth_FireFoam, spot, 5f);
                        string s2 = string.Format("burst={0} spent={1} foamCells={2}", burst, !q.Ready, foam);
                        if (on) return burst == 1 && !q.Ready ? "PASS " + s2 : "FAIL: fire beside a quench stand did not burst it " + s2;
                        return burst == 0 && q.Ready ? "PASS off " + s2 : "FAIL: quenchEnabled off but the stand burst " + s2;
                    }
                    case "walking":
                    {
                        RM_LeaningScrubSettings.walkingEnabled = on;
                        RM_LeaningScrubSettings.walkingMaxCellsPerMap = 100000;
                        ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WalkingVenomvine");
                        if (def == null) return "FAIL: RM_WalkingVenomvine did not resolve";
                        IntVec3 tail = spot + new IntVec3(-1, 0, 0);
                        Stand(map, "RM_WalkingVenomvine", tail, 1f, made);
                        Stand(map, "RM_WalkingVenomvine", spot, 1f, made);
                        IntVec3 d1 = spot + new IntVec3(1, 0, 0), d2 = spot + new IntVec3(2, 0, 0);
                        if (!def.CanEverPlantAt(d1, map) || !def.CanEverPlantAt(d2, map))
                            return "UNMEASURED: the cells downwind of the fixture cannot hold the plant (temperature?)";
                        int before = map.listerThings.ThingsOfDef(def).Count;
                        comp.Walk(new Vector2(1f, 0f));
                        bool runner = d1.GetPlant(map)?.def == def || d2.GetPlant(map)?.def == def;
                        int after = map.listerThings.ThingsOfDef(def).Count;
                        foreach (IntVec3 c in new[] { d1, d2 })
                        {
                            Plant pl = c.GetPlant(map);
                            if (pl != null && pl.def == def) made.Add(pl);
                        }
                        string s2 = string.Format("cells {0}->{1} runnerDownwind={2}", before, after, runner);
                        if (on) return runner ? "PASS " + s2 : "FAIL: a Gale laid no runner downwind of the leading edge " + s2;
                        return !runner && after == before ? "PASS off " + s2 : "FAIL: walkingEnabled off but the stand walked " + s2;
                    }
                    case "shedding":
                    {
                        RM_LeaningScrubSettings.sheddingEnabled = on;
                        ThingDef litter = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ThornLitter");
                        if (litter == null) return "FAIL: RM_ThornLitter did not resolve";
                        if (Stand(map, "RM_SheddingVenomvine", spot, 1f, made) == null) return "FAIL: RM_SheddingVenomvine did not resolve";
                        int before = CountDefIn(map, litter, spot, 11f);
                        comp.Shed(new Vector2(1f, 0f));
                        int after = CountDefIn(map, litter, spot, 11f);
                        int upwind = 0;
                        foreach (IntVec3 c in GenRadial.RadialCellsAround(spot, 11f, true))
                        {
                            Thing t = c.InBounds(map) ? map.thingGrid.ThingAt(c, litter) : null;
                            if (t == null) continue;
                            made.Add(t);
                            if (c.x < spot.x) upwind++;
                        }
                        string s2 = string.Format("litterCells {0}->{1} upwind={2}", before, after, upwind);
                        if (on)
                        {
                            if (after <= before) return "FAIL: a Gale shed no thorn litter downwind " + s2;
                            if (upwind > 0) return "FAIL: thorn litter landed upwind of the stand " + s2;
                            return "PASS " + s2;
                        }
                        return after == before ? "PASS off " + s2 : "FAIL: sheddingEnabled off but the stand shed " + s2;
                    }
                    default:
                        return "UNMEASURED: unknown form '" + form + "'";
                }
            }
            catch (System.Exception ex)
            {
                return "FAIL: proof threw " + ex.GetType().Name + ": " + ex.Message;
            }
            finally
            {
                RM_LeaningScrubSettings.modEnabled = sMod;
                RM_LeaningScrubSettings.rearingEnabled = sRear;
                RM_LeaningScrubSettings.walkingEnabled = sWalk;
                RM_LeaningScrubSettings.hoardEnabled = sHoard;
                RM_LeaningScrubSettings.quenchEnabled = sQuench;
                RM_LeaningScrubSettings.swornSparesMarkedEnabled = sSworn;
                RM_LeaningScrubSettings.sheddingEnabled = sShed;
                RM_LeaningScrubSettings.walkingMaxCellsPerMap = sCap;
                RM_EnvironmentalHazardsSettings.contactVenomEnabled = sVenom;
                for (int i = made.Count - 1; i >= 0; i--)
                {
                    if (made[i] != null && !made[i].Destroyed) made[i].Destroy();
                }
            }
        }
    }
}
