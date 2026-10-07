using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_DIANOGA_PRISON_1. "A prison tank, not a pen: it teaches, it
    // produces, and it can get out" (design sheet §6j/§6m, owner rulings
    // 2026-09-23). Sits alongside a CompRefuelable on the same ThingDef —
    // CompRefuelable IS the feeding mechanism (its fuelFilter is set to
    // MeatRaw in XML, so vanilla's own WorkGiver_Refuel already hauls meat
    // to it with no new job/UI code) and this comp reads its fuel state
    // rather than re-implementing "does it have upkeep".
    //
    //   teaches  -> Notify_Taught() on RUT_MapComponent_TheTenant, once,
    //               the first time the tank produces successfully.
    //   produces -> Props.products, each on its own MTB-days roll, gated on
    //               CompRefuelable.HasFuel.
    //   escapes  -> two independent triggers: sustained neglect (unfed past
    //               neglectDaysBeforeEscapeRisk, then an MTB roll) and
    //               damage (past damageEscapeThresholdFraction lost, then a
    //               flat per-hit chance) — "a neglected OR damaged tank
    //               releases it" (§6j, emphasis the item's own).
    //
    // Escape spawns Props.occupantKindDefName (resolved live, not cached,
    // so the Star Wars swap patch — a PatchOperationReplace on this very
    // string — is picked up without any code change) as a wild, aggressive,
    // water-seeking animal: "it is TOUGH... makes for the nearest water and
    // hurts whatever is between" (§6m stage 1). RM_CompEscapedCaptive (a
    // per-pawn comp on the SPAWNED escapee, not this one) watches for it
    // reaching registered water and handles stage 2/3 from there.
    public class RM_CompCapturedSpecimen : ThingComp
    {
        private const int CheckIntervalTicks = RM_TankKernel.CheckIntervalTicks; // 1 in-game hour
        private const float TicksPerDay = RM_TankKernel.TicksPerDay;

        private int unfedSinceTick = -1;
        private bool taught;
        private bool occupied = true; // FEVERWOOD_BROOD_RANSOM_1: false once returned to the deep
        private Dictionary<ThingDef, int> lastProducedTick = new Dictionary<ThingDef, int>();

        public RM_CompProperties_CapturedSpecimen Props => (RM_CompProperties_CapturedSpecimen)props;

        private CompRefuelable Fuel => parent.GetComp<CompRefuelable>();

        /// <summary>FEVERWOOD_BROOD_RANSOM_1: counted in the world's tally of
        /// the deep's young while true.</summary>
        public bool Occupied => occupied;

        /// <summary>The occupant kind (resolved live so the Star Wars swap
        /// patch applies). With no tank to ask, reads the RM_SekkulaathTank
        /// def's own comp props.</summary>
        public static PawnKindDef YoungKind(RM_CompProperties_CapturedSpecimen props)
        {
            if (props == null)
            {
                ThingDef tank = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SekkulaathTank");
                props = tank?.GetCompProperties<RM_CompProperties_CapturedSpecimen>();
            }
            if (props != null && !props.occupantLikeTank.NullOrEmpty())
            {
                RM_CompProperties_CapturedSpecimen like = DefDatabase<ThingDef>.GetNamedSilentFail(props.occupantLikeTank)
                    ?.GetCompProperties<RM_CompProperties_CapturedSpecimen>();
                if (like != null && like != props && like.occupantLikeTank.NullOrEmpty())
                {
                    props = like;
                }
            }
            string name = props?.occupantKindDefName ?? "RM_Sekkulaath_Juvenile";
            return DefDatabase<PawnKindDef>.GetNamedSilentFail(name);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                foreach (RM_CapturedSpecimenProduct p in Props.products)
                {
                    if (p.thing != null)
                    {
                        lastProducedTick[p.thing] = Find.TickManager.TicksGame;
                    }
                }
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned || parent.Map == null)
            {
                return;
            }
            // Mod Settings master off = inert box, per that toggle's own tooltip; returned to the deep = an empty tank
            // neither produces nor escapes; a town's display tank is fed by the town and neither produces for nor escapes
            // on the player.
            if (!RM_TankKernel.RunsThisTick(RM_FeverWoodSettings.sekkulaathTankEnabled, occupied, IsForeignDisplay,
                    Find.TickManager.TicksGame))
            {
                return;
            }

            bool fed = Fuel == null || Fuel.HasFuel; // no CompRefuelable at all: treat as always-fed
            TickNeglect(fed);
            if (fed)
            {
                TickProduction();
            }
        }

        private void TickNeglect(bool fed)
        {
            if (!RM_TankKernel.NeglectStep(ref unfedSinceTick, fed, Find.TickManager.TicksGame, Props.neglectDaysBeforeEscapeRisk))
            {
                return;
            }

            float effectiveMtbDays = RM_TankKernel.NeglectMtbDays(Props.neglectEscapeMtbDays, RM_FeverWoodSettings.sekkulaathEscapeRiskMultiplier); // lower multiplier = shorter MTB = more escape-prone
            if (Rand.MTBEventOccurs(effectiveMtbDays, TicksPerDay, CheckIntervalTicks))
            {
                Escape("neglect");
            }
        }

        private void TickProduction()
        {
            for (int i = 0; i < Props.products.Count; i++)
            {
                RM_CapturedSpecimenProduct p = Props.products[i];
                if (p.thing == null)
                {
                    continue;
                }
                int last = lastProducedTick.TryGetValue(p.thing, out int t) ? t : Find.TickManager.TicksGame;
                if (!Rand.MTBEventOccurs(p.mtbDays, TicksPerDay, RM_TankKernel.ProductionWindow(Find.TickManager.TicksGame, last)))
                {
                    continue;
                }

                lastProducedTick[p.thing] = Find.TickManager.TicksGame;
                Thing produced = ThingMaker.MakeThing(p.thing);
                produced.stackCount = Mathf.Clamp(p.countRange.RandomInRange, 1, p.thing.stackLimit);
                GenPlace.TryPlaceThing(produced, parent.Position, parent.Map, ThingPlaceMode.Near);

                if (!taught && Props.teachesColonyWarning)
                {
                    taught = true;
                    parent.Map.GetComponent<RUT_MapComponent_TheTenant>()?.Notify_Taught();
                    Messages.Message("The tank's occupant has produced enough for the colony to finally learn its" +
                        " name — and the low hum that warns of the real thing beneath the pools.",
                        new TargetInfo(parent.Position, parent.Map), MessageTypeDefOf.PositiveEvent);
                }
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (totalDamageDealt <= 0f || parent.Destroyed || !parent.Spawned)
            {
                return;
            }
            if (!RM_TankKernel.DamageArmed(RM_FeverWoodSettings.sekkulaathTankEnabled, occupied, parent.HitPoints, parent.MaxHitPoints,
                    Props.damageEscapeThresholdFraction))
            {
                return;
            }

            float effectiveChance = RM_TankKernel.DamageEscapeChance(Props.damageEscapeChancePerHit, RM_FeverWoodSettings.sekkulaathEscapeRiskMultiplier); // lower multiplier = higher chance
            if (Rand.Chance(effectiveChance))
            {
                Escape("damage");
            }
        }

        /// <summary>"A neglected or damaged tank releases it — a disaster
        /// the player built" (§6j). Destroys the tank itself (it is a
        /// breach, not a door) and spawns the occupant kind as a wild,
        /// hostile, water-seeking escapee carrying the captivity marker
        /// (item's ruling 3: "it remembers the tank").</summary>
        private void Escape(string cause)
        {
            if (RM_TankKernel.EscapeFreesDisplayYoung(IsForeignDisplay, RM_FeverWoodSettings.broodRansomEnabled))
            {
                FreeDisplayYoung(parent.Map, parent.Position, breached: true);
                if (!parent.Destroyed)
                {
                    parent.Destroy(DestroyMode.Vanish);
                }
                return;
            }
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(Props.occupantKindDefName);

            if (!parent.Destroyed)
            {
                parent.Destroy(DestroyMode.Vanish);
            }

            if (kind == null || map == null)
            {
                return; // occupant kind not loaded (e.g. mid-swap misconfiguration) — tank still breaks, nothing to spawn
            }

            IntVec3 spawnCell = CellFinder.RandomClosewalkCellNear(pos, map, 3);
            Pawn escapee = PawnGenerator.GeneratePawn(kind, null);
            GenSpawn.Spawn(escapee, spawnCell, map);

            HediffDef memory = DefDatabase<HediffDef>.GetNamedSilentFail("RM_CaptivityMemory");
            if (memory != null)
            {
                escapee.health.AddHediff(memory);
            }

            // "it is TOUGH... hurts whatever is between it and there" —
            // manhunter while it beelines for water, same lever vanilla
            // manhunter-pack incidents use.
            escapee.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter,
                reason: "Escaped captivity", forceWake: true, causedByMood: false);

            escapee.GetComp<RM_CompEscapedCaptive>()?.Notify_JustEscaped();

            Messages.Message($"The tank has failed ({cause}) — its occupant has escaped and is heading for water!",
                new TargetInfo(spawnCell, map), MessageTypeDefOf.ThreatBig);
        }

        public override string CompInspectStringExtra()
        {
            string line;
            if (!occupied)
            {
                line = "Empty — its occupant was returned to the deep.";
            }
            else if (Fuel == null)
            {
                line = null;
            }
            else
            {
                line = Fuel.HasFuel
                    ? "Occupant fed — producing while stock lasts."
                    : "Occupant unfed — containment risk rising.";
            }
            string restless = RM_WorldComponent_DeepYoung.RestlessnessLine();
            if (restless != null)
            {
                line = line == null ? restless : line + "\n" + restless;
            }
            return line;
        }

        // FEVERWOOD_BROOD_RANSOM_1: "Return to the deep". A deliberate player
        // act: empties the tank and lets the young out NON-hostile, flagged
        // released, walking for the nearest pool. Only a Fever Wood pool
        // answers with a gift (RM_CompEscapedCaptive.ArriveReleased).
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!RM_FeverWoodSettings.broodRansomEnabled || !RM_FeverWoodSettings.sekkulaathTankEnabled)
            {
                yield break;
            }
            if (IsForeignDisplay)
            {
                yield return FreeYoungGizmo();
                yield break;
            }
            if (parent.Faction != Faction.OfPlayer)
            {
                yield break;
            }
            PawnKindDef kind = YoungKind(Props);
            Command_Action cmd = new Command_Action
            {
                defaultLabel = "Return to the deep",
                defaultDesc = "Open the tank and let its occupant go. It will make for the nearest water. If that "
                    + "water is a Fever Wood pool, the deep will know its young came home, and will pay for it.",
                icon = kind?.race?.uiIcon ?? BaseContent.BadTex,
                action = () => Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                    "Open the tank and let the young go? The tank will stand empty.", ReleaseToTheDeep, destructive: true))
            };
            if (!occupied)
            {
                cmd.Disable("The tank is empty.");
            }
            yield return cmd;
        }

        // ── FEVERWOOD_BROOD_RANSOM_1 §5: a town's display tank ──────────────

        /// <summary>A display tank another faction owns (campaign: Sporefall's).</summary>
        public bool IsForeignDisplay => RM_TankKernel.IsForeignDisplay(Props.displayTank, parent.Faction != null, parent.Faction == Faction.OfPlayer);

        /// <summary>A player colonist stands in or beside the tank's footprint.</summary>
        public Pawn AdjacentColonist()
        {
            if (!parent.Spawned)
            {
                return null;
            }
            CellRect near = parent.OccupiedRect().ExpandedBy(1);
            IReadOnlyList<Pawn> pawns = parent.Map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                if (near.Contains(pawns[i].Position) && !pawns[i].Downed && pawns[i].IsColonistPlayerControlled)
                {
                    return pawns[i];
                }
            }
            return null;
        }

        private Command_Action FreeYoungGizmo()
        {
            PawnKindDef kind = YoungKind(Props);
            Faction owner = parent.Faction;
            Command_Action cmd = new Command_Action
            {
                defaultLabel = "Free the young",
                defaultDesc = "Open " + owner.Name + "'s tank and let the young out. It will make for the nearest water; "
                    + "at a Fever Wood pool the deep pays " + (Props.giftRolls > 1 ? "twice over" : "for it")
                    + ". " + owner.Name + " will not forgive it (goodwill -" + RM_FeverWoodSettings.broodDisplayTankGoodwillLoss
                    + "). Needs a colonist standing beside the tank.",
                icon = kind?.race?.uiIcon ?? BaseContent.BadTex,
                action = () => Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                    "Free the young from " + owner.Name + "'s tank? They will see it done.",
                    () => FreeDisplayYoung(parent.Map, parent.Position, breached: false), destructive: true))
            };
            if (!occupied)
            {
                cmd.Disable("The tank is empty.");
            }
            else if (AdjacentColonist() == null)
            {
                cmd.Disable("A colonist must stand beside the tank.");
            }
            return cmd;
        }

        /// <summary>Frees a display tank's young: released (walks home, buys
        /// Props.giftRolls gifts at a Fever Wood pool), goodwill loss with the
        /// owner, one young fewer at the settlement, and the town's letter.
        /// Idempotent: an empty tank does nothing.</summary>
        public Pawn FreeDisplayYoung(Map map, IntVec3 pos, bool breached)
        {
            if (!RM_TankKernel.TryFreeDisplay(ref occupied, map != null))
            {
                return null;
            }
            Faction owner = parent.Faction;
            Pawn young = null;
            PawnKindDef kind = YoungKind(Props);
            if (kind != null)
            {
                young = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(young, CellFinder.RandomClosewalkCellNear(pos, map, 3), map);
                young.GetComp<RM_CompEscapedCaptive>()?.Notify_ReleasedToDeep(Props.giftRolls);
            }
            int loss = RM_FeverWoodSettings.broodDisplayTankGoodwillLoss;
            if (owner != null && owner != Faction.OfPlayer && loss > 0)
            {
                owner.TryAffectGoodwillWith(Faction.OfPlayer, -loss, canSendMessage: true, canSendHostilityLetter: true,
                    reason: null, lookTarget: young != null ? new GlobalTargetInfo(young) : (GlobalTargetInfo?)null);
            }
            if (map.Parent is Settlement settlement)
            {
                RM_WorldComponent_DeepYoung.Get?.Notify_DisplayTankFreed(settlement);
            }
            else
            {
                RM_WorldComponent_DeepYoung.Get?.Recompute();
            }
            string label = Props.freedLetterLabel ?? "The young is loose";
            string text = Props.freedLetterText
                ?? ((breached ? "The tank is broken open" : "The tank is opened") + " and its young slides out, making for the water. "
                    + (owner != null ? owner.Name + " saw it done." : ""));
            Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.NegativeEvent,
                young != null ? new LookTargets(young) : new LookTargets(new TargetInfo(pos, map)));
            return young;
        }

        public void ReleaseToTheDeep()
        {
            if (!RM_TankKernel.TryRelease(ref occupied, parent.Spawned))
            {
                return;
            }
            Map map = parent.Map;
            PawnKindDef kind = YoungKind(Props);
            if (Fuel != null)
            {
                Fuel.allowAutoRefuel = false; // nothing left to feed
            }
            if (kind != null)
            {
                Pawn young = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(young, CellFinder.RandomClosewalkCellNear(parent.Position, map, 3), map);
                young.GetComp<RM_CompEscapedCaptive>()?.Notify_ReleasedToDeep();
                Messages.Message("The tank is opened. The young slides out and makes for the water.",
                    young, MessageTypeDefOf.NeutralEvent);
            }
            RM_WorldComponent_DeepYoung.Get?.Recompute();
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            // Broken outright (no escape roll got there first): a display tank's young still gets out.
            if (RM_TankKernel.DestroyFreesDisplayYoung(mode == DestroyMode.KillFinalize, occupied, Props.displayTank, previousMap != null,
                    parent.Faction != null, parent.Faction == Faction.OfPlayer,
                    RM_FeverWoodSettings.broodRansomEnabled, RM_FeverWoodSettings.sekkulaathTankEnabled))
            {
                FreeDisplayYoung(previousMap, parent.Position, breached: true);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref unfedSinceTick, "unfedSinceTick", -1);
            Scribe_Values.Look(ref taught, "taught", false);
            Scribe_Values.Look(ref occupied, "occupied", true);
            Scribe_Collections.Look(ref lastProducedTick, "lastProducedTick", LookMode.Def, LookMode.Value);
            if (lastProducedTick == null)
            {
                lastProducedTick = new Dictionary<ThingDef, int>();
            }
        }
    }
}
