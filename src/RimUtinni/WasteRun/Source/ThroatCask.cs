using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.WasteRun
{
    // THROAT_CASK_ITEM_1. Owner, typed 2026-10-09: "constantly emitting terrible radiation. Extremely
    // dangerous to be near, even with a specially sealed chamber. Ship malfunctions while it's onboard
    // repeatedly. Feels like it's slowly causing armaggeddon just having it nearby."
    // EVERY NUMBER IS PROVISIONAL (mine, not ruled); the logic lives in WasteRunKernel.
    // Radiation rides vanilla ToxicUtility (the Warcasket dose-layer ruling), so a warcasket's own
    // toxic resistance still counts. A cask bay mutes the dose; it never silences it.
    public class RUT_CompProperties_ThroatCask : CompProperties
    {
        public float doseRadius = 14f;
        public float toxicFactor = 6f;
        public float shieldedDoseFactor = 0.35f;
        public int faultIntervalTicks = 60000;
        public float moodRadius = 15f;
        public float dieOffRadius = 15f;
        public float dieOffChancePerRare = 0.05f;
        public float burstRadius = 7f;

        public RUT_CompProperties_ThroatCask()
        {
            compClass = typeof(RUT_CompThroatCask);
        }
    }

    public class RUT_CompThroatCask : ThingComp
    {
        private int ticksPresent;
        private int ticksSinceFault;
        private float lastCarrierHealthLoss = -1f;

        private RUT_CompProperties_ThroatCask Props => (RUT_CompProperties_ThroatCask)props;

        private static bool Active => WasteRunKernel.ThroatCaskActive(WasteRunSettings.masterEnabled, WasteRunSettings.throatCaskEnabled);

        private static bool InBay(Thing t)
        {
            Map map = t.MapHeld;
            if (map == null || !t.Spawned) return false;
            List<Thing> here = t.Position.GetThingList(map);
            for (int i = 0; i < here.Count; i++)
            {
                if (here[i].def.defName == "RM_CaskBay") return true;
            }
            return false;
        }

        // Pawns carrying it (inventory or hands) are "the carrier".
        private Pawn Carrier()
        {
            return parent.ParentHolder is Pawn_InventoryTracker inv ? inv.pawn
                : parent.ParentHolder is Pawn_CarryTracker car ? car.pawn : null;
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!Active) return;
            Map map = parent.MapHeld;
            if (map == null) return;
            ticksPresent += GenTicks.TickRareInterval;
            ticksSinceFault += GenTicks.TickRareInterval;

            Pawn carrier = Carrier();
            if (WasteRunSettings.throatBurstEnabled && CheckBurst(carrier, map)) return;
            if (WasteRunSettings.throatRadiationEnabled) Irradiate(map, carrier);
            if (WasteRunSettings.throatShipFaultsEnabled) ShipFault(map);
            if (WasteRunSettings.throatDecayEnabled) Decay(map);
        }

        private bool CheckBurst(Pawn carrier, Map map)
        {
            bool harmed = false;
            if (carrier != null)
            {
                float loss = 0f;
                foreach (Hediff h in carrier.health.hediffSet.hediffs)
                {
                    if (h is Hediff_Injury inj) loss += inj.Severity;
                }
                harmed = lastCarrierHealthLoss >= 0f && loss > lastCarrierHealthLoss + 0.01f;
                lastCarrierHealthLoss = loss;
            }
            else
            {
                lastCarrierHealthLoss = -1f;
            }
            bool burning = parent.IsBurning() || (parent.Spawned && parent.Position.GetFirstThing<Fire>(map) != null);
            if (!WasteRunKernel.ShouldBurst(harmed, burning)) return false;
            Burst(map);
            return true;
        }

        private void Burst(Map map)
        {
            IntVec3 pos = parent.PositionHeld;
            Messages.Message("The Throat cask has burst.", new TargetInfo(pos, map), MessageTypeDefOf.NegativeEvent);
            GameCondition fallout = GameConditionMaker.MakeCondition(GameConditionDefOf.ToxicFallout, 3 * 60000);
            map.gameConditionManager.RegisterCondition(fallout);
            Thing source = parent;
            parent.Destroy(DestroyMode.Vanish);
            GenExplosion.DoExplosion(pos, map, Props.burstRadius, DamageDefOf.Bomb, null, 120);
        }

        private void Irradiate(Map map, Pawn carrier)
        {
            IntVec3 pos = parent.PositionHeld;
            bool shielded = InBay(parent);
            float rateScale = (float)GenTicks.TickRareInterval / ToxicUtility.CheckInterval;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead) continue;
                float dist = p.Position.DistanceTo(pos);
                // The carrier is never shielded by a bay it is not standing in.
                float dose = WasteRunKernel.ThroatDose(Props.toxicFactor, dist, Props.doseRadius, shielded && p != carrier, Props.shieldedDoseFactor);
                if (dose > 0f) ToxicUtility.DoPawnToxicDamage(p, dose * rateScale);
            }
        }

        private void ShipFault(Map map)
        {
            if (!WasteRunKernel.FaultDue(ticksSinceFault, Props.faultIntervalTicks)) return;
            if (!AboardShip(map)) return;
            ticksSinceFault = 0;
            List<Building> all = map.listerBuildings.allBuildingsColonist;
            List<CompBreakdownable> candidates = new List<CompBreakdownable>();
            for (int i = 0; i < all.Count; i++)
            {
                CompBreakdownable b = all[i].GetComp<CompBreakdownable>();
                if (b != null && !b.BrokenDown) candidates.Add(b);
            }
            if (candidates.Count == 0) return;
            CompBreakdownable pick = candidates.RandomElement();
            pick.DoBreakdown();
            Messages.Message("The Throat cask is wrecking the ship: " + pick.parent.LabelCap + " has failed.",
                pick.parent, MessageTypeDefOf.NegativeEvent);
        }

        // Aboard a gravship = the map holds a grav engine, or the cask sits in a cask bay (the bay needs ship substructure).
        private bool AboardShip(Map map)
        {
            ThingDef engine = DefDatabase<ThingDef>.GetNamedSilentFail("GravEngine");
            if (engine != null && map.listerBuildings.AllBuildingsColonistOfDef(engine).Count > 0) return true;
            return InBay(parent);
        }

        // Slow armageddon: plants and wild animals die off, pawns nearby sicken in the mind. Escalates with presence.
        private void Decay(Map map)
        {
            IntVec3 pos = parent.PositionHeld;
            float chance = WasteRunKernel.DieOffChance(Props.dieOffChancePerRare, ticksPresent);
            if (Rand.Chance(chance))
            {
                List<Thing> victims = new List<Thing>();
                foreach (IntVec3 c in GenRadial.RadialCellsAround(pos, Props.dieOffRadius, true))
                {
                    if (!c.InBounds(map)) continue;
                    List<Thing> here = c.GetThingList(map);
                    for (int i = 0; i < here.Count; i++)
                    {
                        if (here[i] is Plant || (here[i] is Pawn a && a.RaceProps.Animal && a.Faction == null)) victims.Add(here[i]);
                    }
                }
                if (victims.Count > 0) victims.RandomElement().Kill();
            }
            ThoughtDef def = DefDatabase<ThoughtDef>.GetNamedSilentFail("RUT_ThroatCaskNear");
            if (def == null) return;
            int stage = WasteRunKernel.NearStage(ticksPresent);
            IReadOnlyList<Pawn> pawns = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.needs?.mood == null || p.Position.DistanceTo(pos) > Props.moodRadius) continue;
                Thought_Memory m = (Thought_Memory)ThoughtMaker.MakeThought(def, stage);
                p.needs.mood.thoughts.memories.TryGainMemory(m);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!Active) return null;
            return "Radiating constantly" + (InBay(parent) ? " (muted by the cask bay, never silenced)." : ".");
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksPresent, "ticksPresent", 0);
            Scribe_Values.Look(ref ticksSinceFault, "ticksSinceFault", 0);
            Scribe_Values.Look(ref lastCarrierHealthLoss, "lastCarrierHealthLoss", -1f);
        }
    }
}
