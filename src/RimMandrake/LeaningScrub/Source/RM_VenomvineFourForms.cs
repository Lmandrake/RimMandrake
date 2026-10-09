using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // Four further venomvine forms, admitted by the owner's card 2026-10-08
    // (LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1): Strangler, Weeper, Sleeper, Lure.
    // Each is its own build item (LEANINGSCRUB_STRANGLER_VINE_1, _WEEPER_VINE_1,
    // _SLEEPER_VINE_1, _LURE_VINE_1), its own Mod Setting, and with the setting
    // off is a plain venomvine stand. Defs: Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml.
    // Plants only tick TickLong, so strangler, weeper and lure work in CompTickLong
    // (no MapComponent). The sleeper must answer a footstep, so it registers with one
    // small MapComponent. Numbers PROVISIONAL. Logic in Kernel/RM_FourFormsKernel.cs.
    // ════════════════════════════════════════════════════════════════════

    // ── Strangler ──
    public class RM_CompProperties_Strangler : CompProperties
    {
        public float minGrowth = 0.5f;
        public float wrapStep = 0.1f;        // wrap progress per long tick
        public float fullDamage = 6f;        // per long tick at full wrap, blunt, to the wall or tree

        public RM_CompProperties_Strangler()
        {
            compClass = typeof(RM_CompStrangler);
        }
    }

    public class RM_CompStrangler : ThingComp
    {
        private Thing target;
        private float wrap;
        private bool trimCalled;

        public RM_CompProperties_Strangler Props => (RM_CompProperties_Strangler)props;

        public Thing Target => target;

        public float Wrap => wrap;

        private float Growth => parent is Plant plant ? plant.Growth : 1f;

        public static bool IsWrappable(Thing t)
        {
            if (t == null || t.Destroyed || !t.Spawned) return false;
            if (t is Plant p) return p.def.plant != null && p.def.plant.IsTree;
            return t is Building b && b.def.passability == Traversability.Impassable && b.def.useHitPoints;
        }

        private Thing FindTarget()
        {
            Thing best = null;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(parent))
            {
                if (!c.InBounds(parent.Map)) continue;
                List<Thing> things = c.GetThingList(parent.Map);
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t == parent || !IsWrappable(t)) continue;
                    // a wall of ours first: that is what a gardener minds
                    if (best == null || (t.Faction == Faction.OfPlayer && best.Faction != Faction.OfPlayer)) best = t;
                }
            }
            return best;
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            if (parent.Map == null || !RM_WindCalendar.On(RM_LeaningScrubSettings.stranglerEnabled)) return;
            if (!RM_FourFormsKernel.Wraps(true, Growth, Props.minGrowth)) return;
            if (!IsWrappable(target) || !parent.Position.AdjacentTo8WayOrInside(target))
            {
                Thing found = FindTarget();
                if (found != target) { wrap = 0f; trimCalled = false; }
                target = found;
                if (target == null) return;
            }
            wrap = RM_FourFormsKernel.WrapProgress(wrap, Props.wrapStep);
            float dmg = RM_FourFormsKernel.WrapDamage(wrap, Props.fullDamage * RM_LeaningScrubSettings.stranglerDamageFactor);
            if (dmg > 0f)
            {
                target.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg, 0f, -1f, parent));
            }
            // "Trimmed": a stand wrapped round something of ours calls for the cutters.
            if (RM_LeaningScrubSettings.stranglerAutoTrim && !trimCalled && target != null && target.Faction == Faction.OfPlayer
                && parent.Map.designationManager.DesignationOn(parent, DesignationDefOf.CutPlant) == null
                && parent.Map.designationManager.DesignationOn(parent, DesignationDefOf.HarvestPlant) == null)
            {
                parent.Map.designationManager.AddDesignation(new Designation(parent, DesignationDefOf.CutPlant));
                trimCalled = true;
                Messages.Message("A strangler venomvine is wrapped round your " + target.LabelNoCount + " and is marked to be cut back.",
                    new TargetInfo(parent.Position, parent.Map), MessageTypeDefOf.CautionInput, false);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref target, "rmStranglerTarget");
            Scribe_Values.Look(ref wrap, "rmStranglerWrap", 0f);
            Scribe_Values.Look(ref trimCalled, "rmStranglerTrimCalled", false);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.stranglerEnabled) || !IsWrappable(target)) return null;
            return "Wrapped round " + target.LabelNoCount + ": " + wrap.ToStringPercent() + " tight. Cut it back to stop it.";
        }
    }

    // ── Weeper ──
    public class RM_CompProperties_Weeper : CompProperties
    {
        public float minGrowth = 0.5f;
        public float poolChancePerLongTick = 0.1f;
        public int radius = 2;
        public int maxPollutedCells = 12;
        public ThingDef poolDef;

        public RM_CompProperties_Weeper()
        {
            compClass = typeof(RM_CompWeeper);
        }
    }

    public class RM_CompWeeper : ThingComp
    {
        private int polluted;

        public RM_CompProperties_Weeper Props => (RM_CompProperties_Weeper)props;

        private float Growth => parent is Plant plant ? plant.Growth : 1f;

        public override void CompTickLong()
        {
            base.CompTickLong();
            Map map = parent.Map;
            if (map == null) return;
            bool on = RM_WindCalendar.On(RM_LeaningScrubSettings.weeperEnabled);
            if (!RM_FourFormsKernel.WeepsNow(on, Growth, Props.minGrowth, Rand.Value, Props.poolChancePerLongTick)) return;
            IntVec3 cell = parent.Position + GenRadial.RadialPattern[Rand.RangeInclusive(1, GenRadial.NumCellsInRadius(Props.radius) - 1)];
            if (!cell.InBounds(map) || !cell.Walkable(map)) return;
            if (Props.poolDef != null) FilthMaker.TryMakeFilth(cell, map, Props.poolDef);
            // The pool poisons the soil: Biotech pollution, which stunts growth and kills plants (the DLCs are assumed).
            if (ModsConfig.BiotechActive && RM_LeaningScrubSettings.weeperPollutes
                && RM_FourFormsKernel.PollutionRoom(polluted, Props.maxPollutedCells) > 0 && !map.pollutionGrid.IsPolluted(cell))
            {
                map.pollutionGrid.SetPolluted(cell, true);
                polluted++;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref polluted, "rmWeeperPolluted", 0);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.weeperEnabled) || polluted == 0) return null;
            return "Weeping: " + polluted + " cells of soil poisoned round it.";
        }
    }

    // ── Sleeper ──
    public class RM_CompProperties_Sleeper : CompProperties
    {
        public float minBodySize = 0.5f;
        public float wakeRadius = 1.5f;
        public float wakeDamage = 6f;
        public ThingDef awakeDef;

        public RM_CompProperties_Sleeper()
        {
            compClass = typeof(RM_CompSleeper);
        }
    }

    public class RM_CompSleeper : ThingComp
    {
        public RM_CompProperties_Sleeper Props => (RM_CompProperties_Sleeper)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            parent.Map?.GetComponent<RM_MapComponent_SleeperWatch>()?.Register(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map?.GetComponent<RM_MapComponent_SleeperWatch>()?.Deregister(this);
        }

        public void Wake(Pawn disturber)
        {
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            if (map == null || Props.awakeDef == null) return;
            float growth = parent is Plant plant ? plant.Growth : 1f;
            parent.DeSpawn(DestroyMode.Vanish);
            Plant awake = (Plant)ThingMaker.MakeThing(Props.awakeDef);
            GenSpawn.Spawn(awake, pos, map);
            awake.Growth = Mathf.Max(growth, 0.5f);
            DamageDef venom = DefDatabase<DamageDef>.GetNamedSilentFail("RM_VenomvineScratch");
            List<Pawn> hit = new List<Pawn>();
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(pos, map, Props.wakeRadius, true))
            {
                if (t is Pawn hp) hit.Add(hp);
            }
            foreach (Pawn p in hit)
            {
                if (venom != null && !p.Dead && !p.Flying) p.TakeDamage(new DamageInfo(venom, Props.wakeDamage, 0.05f, -1f, awake));
            }
            Messages.Message(disturber != null ? disturber.LabelShort + " disturbed a dead-looking vine, and it was not dead."
                : "A dead-looking vine was not dead.", new TargetInfo(pos, map), MessageTypeDefOf.ThreatSmall, false);
            parent.Destroy();
        }
    }

    public class RM_MapComponent_SleeperWatch : MapComponent
    {
        private const int Interval = 15;
        private readonly HashSet<RM_CompSleeper> sleepers = new HashSet<RM_CompSleeper>();
        private readonly List<RM_CompSleeper> tmp = new List<RM_CompSleeper>();

        public RM_MapComponent_SleeperWatch(Map map) : base(map)
        {
        }

        public void Register(RM_CompSleeper c) { sleepers.Add(c); }

        public void Deregister(RM_CompSleeper c) { sleepers.Remove(c); }

        public int Count => sleepers.Count;

        public override void MapComponentTick()
        {
            if (sleepers.Count == 0 || Find.TickManager.TicksGame % Interval != 0) return;
            Sweep();
        }

        public void Sweep()
        {
            if (!RM_LeaningScrubSettings.modEnabled) return;
            bool on = RM_WindCalendar.On(RM_LeaningScrubSettings.sleeperEnabled);
            tmp.Clear();
            tmp.AddRange(sleepers);
            for (int i = 0; i < tmp.Count; i++)
            {
                RM_CompSleeper s = tmp[i];
                if (s.parent == null || !s.parent.Spawned) continue;
                foreach (Thing t in GenRadial.RadialDistinctThingsAround(s.parent.Position, map, s.Props.wakeRadius, true))
                {
                    Pawn p = t as Pawn;
                    if (p == null) continue;
                    if (RM_FourFormsKernel.Wakes(on, true, p.BodySize, s.Props.minBodySize, p.Flying, p.Dead))
                    {
                        s.Wake(p);
                        break;
                    }
                }
            }
        }
    }

    // ── Lure ──
    public class RM_CompProperties_Lure : CompProperties
    {
        public float minGrowth = 0.5f;
        public int fruitCap = 3;
        public int reach = 3;
        public ThingDef fruitDef;

        public RM_CompProperties_Lure()
        {
            compClass = typeof(RM_CompLure);
        }
    }

    public class RM_CompLure : ThingComp
    {
        public RM_CompProperties_Lure Props => (RM_CompProperties_Lure)props;

        private float Growth => parent is Plant plant ? plant.Growth : 1f;

        private int FruitNearby(Map map)
        {
            int n = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, Props.reach, true))
            {
                if (!c.InBounds(map)) continue;
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i].def == Props.fruitDef) n += things[i].stackCount;
                }
            }
            return n;
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            Map map = parent.Map;
            if (map == null || Props.fruitDef == null) return;
            bool on = RM_WindCalendar.On(RM_LeaningScrubSettings.lureEnabled);
            if (!RM_FourFormsKernel.DropsFruit(on, Growth, Props.minGrowth, FruitNearby(map), Props.fruitCap)) return;
            Thing fruit = ThingMaker.MakeThing(Props.fruitDef);
            fruit.stackCount = 1;
            GenPlace.TryPlaceThing(fruit, parent.Position, map, ThingPlaceMode.Near);
        }

        public override string CompInspectStringExtra()
        {
            return RM_WindCalendar.On(RM_LeaningScrubSettings.lureEnabled) && Growth >= Props.minGrowth
                ? "Sweet fruit hangs low in it; animals will come for it." : null;
        }
    }

    // jawa/static_call proof (validation.py, four_forms). Each fixture is built on the current map, driven through the
    // SHIPPED code with the setting on and then off, read back, and removed. Arg: "<form>|on" or "<form>|off".
    public static class RM_FourFormsProof
    {
        private static IntVec3 FindSpot(Map map)
        {
            foreach (IntVec3 c in map.AllCells)
            {
                if (c.x < 30 || c.z < 30 || c.x > map.Size.x - 30 || c.z > map.Size.z - 30 || c.x % 7 != 0 || c.z % 7 != 0) continue;
                bool ok = true;
                foreach (IntVec3 o in GenRadial.RadialCellsAround(c, 6f, true))
                {
                    if (!o.InBounds(map) || !o.Standable(map) || o.Roofed(map) || o.GetFirstPawn(map) != null || o.GetEdifice(map) != null) { ok = false; break; }
                }
                if (ok) return c;
            }
            return IntVec3.Invalid;
        }

        private static Plant Stand(Map map, string defName, IntVec3 c, List<Thing> made)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (def == null) return null;
            c.GetPlant(map)?.Destroy();
            Plant p = (Plant)ThingMaker.MakeThing(def);
            p.Growth = 1f;
            GenSpawn.Spawn(p, c, map);
            made.Add(p);
            return p;
        }

        public static string ProofForm(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            string[] parts = (args ?? "").Split('|');
            string form = parts[0];
            bool on = parts.Length < 2 || parts[1] != "off";
            var made = new List<Thing>();
            bool sMod = RM_LeaningScrubSettings.modEnabled, sStr = RM_LeaningScrubSettings.stranglerEnabled,
                sTrim = RM_LeaningScrubSettings.stranglerAutoTrim, sWee = RM_LeaningScrubSettings.weeperEnabled,
                sPol = RM_LeaningScrubSettings.weeperPollutes, sSle = RM_LeaningScrubSettings.sleeperEnabled,
                sLure = RM_LeaningScrubSettings.lureEnabled;
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                IntVec3 spot = FindSpot(map);
                if (!spot.IsValid) return "UNMEASURED: no open, unroofed 6-cell disc on this map";
                switch (form)
                {
                    case "strangler":
                    {
                        RM_LeaningScrubSettings.stranglerEnabled = on;
                        RM_LeaningScrubSettings.stranglerAutoTrim = false;
                        Plant st = Stand(map, "RM_StranglerVenomvine", spot, made);
                        if (st == null) return "FAIL: RM_StranglerVenomvine did not resolve";
                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.WoodLog);
                        GenSpawn.Spawn(wall, spot + IntVec3.East, map);
                        made.Add(wall);
                        int before = wall.HitPoints;
                        RM_CompStrangler c = st.GetComp<RM_CompStrangler>();
                        if (c == null) return "FAIL: no RM_CompStrangler";
                        for (int i = 0; i < 4; i++) c.CompTickLong();
                        bool hurt = !wall.Destroyed && wall.HitPoints < before;
                        return (on == hurt) ? "PASS strangler " + (on ? "wrapped (" + c.Wrap.ToStringPercent() + ", wall " + before + " -> " + wall.HitPoints + ")" : "toggle off left the wall alone")
                            : "FAIL strangler on=" + on + " wall " + before + " -> " + (wall.Destroyed ? 0 : wall.HitPoints);
                    }
                    case "weeper":
                    {
                        RM_LeaningScrubSettings.weeperEnabled = on;
                        RM_LeaningScrubSettings.weeperPollutes = false;
                        Plant st = Stand(map, "RM_WeeperVenomvine", spot, made);
                        if (st == null) return "FAIL: RM_WeeperVenomvine did not resolve";
                        RM_CompWeeper c = st.GetComp<RM_CompWeeper>();
                        if (c == null) return "FAIL: no RM_CompWeeper";
                        for (int i = 0; i < 200; i++) c.CompTickLong();
                        int pools = 0;
                        foreach (IntVec3 o in GenRadial.RadialCellsAround(spot, 3f, true))
                        {
                            Thing f = o.InBounds(map) ? map.thingGrid.ThingAt(o, c.Props.poolDef) : null;
                            if (f != null) { pools++; made.Add(f); }
                        }
                        return (on == (pools > 0)) ? "PASS weeper " + (on ? pools + " pools after 200 long ticks" : "toggle off shed nothing")
                            : "FAIL weeper on=" + on + " pools=" + pools;
                    }
                    case "sleeper":
                    {
                        RM_LeaningScrubSettings.sleeperEnabled = on;
                        Plant st = Stand(map, "RM_SleeperVenomvine", spot, made);
                        if (st == null) return "FAIL: RM_SleeperVenomvine did not resolve";
                        RM_MapComponent_SleeperWatch watch = map.GetComponent<RM_MapComponent_SleeperWatch>();
                        if (watch == null) return "FAIL: RM_MapComponent_SleeperWatch not on the map";
                        Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                        GenSpawn.Spawn(p, spot + IntVec3.East, map);
                        made.Add(p);
                        watch.Sweep();
                        Plant now = spot.GetPlant(map);
                        if (now != null) made.Add(now);
                        bool woke = now != null && now.def.defName == "RM_SleeperVenomvineAwake";
                        return (on == woke) ? "PASS sleeper " + (on ? "woke into a live stand" : "toggle off stayed asleep")
                            : "FAIL sleeper on=" + on + " plant now " + (now?.def.defName ?? "none");
                    }
                    case "lure":
                    {
                        RM_LeaningScrubSettings.lureEnabled = on;
                        Plant st = Stand(map, "RM_LureVenomvine", spot, made);
                        if (st == null) return "FAIL: RM_LureVenomvine did not resolve";
                        RM_CompLure c = st.GetComp<RM_CompLure>();
                        if (c == null) return "FAIL: no RM_CompLure";
                        for (int i = 0; i < 6; i++) c.CompTickLong();
                        int n = 0;
                        foreach (IntVec3 o in GenRadial.RadialCellsAround(spot, 4f, true))
                        {
                            if (!o.InBounds(map)) continue;
                            foreach (Thing t in o.GetThingList(map))
                            {
                                if (t.def == c.Props.fruitDef) { n += t.stackCount; made.Add(t); }
                            }
                        }
                        return (on == (n > 0)) ? "PASS lure " + (on ? n + " fruit (cap " + c.Props.fruitCap + ")" : "toggle off dropped none")
                            : "FAIL lure on=" + on + " fruit=" + n;
                    }
                    default:
                        return "UNMEASURED: unknown form " + form;
                }
            }
            finally
            {
                RM_LeaningScrubSettings.modEnabled = sMod;
                RM_LeaningScrubSettings.stranglerEnabled = sStr;
                RM_LeaningScrubSettings.stranglerAutoTrim = sTrim;
                RM_LeaningScrubSettings.weeperEnabled = sWee;
                RM_LeaningScrubSettings.weeperPollutes = sPol;
                RM_LeaningScrubSettings.sleeperEnabled = sSle;
                RM_LeaningScrubSettings.lureEnabled = sLure;
                foreach (Thing t in made)
                {
                    if (t != null && !t.Destroyed) t.Destroy();
                }
            }
        }
    }
}
