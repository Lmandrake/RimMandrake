using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.Greentide
{
    /// <summary>
    /// GREENTIDE_VURRAK_BUILD_1 — the Vurrak, the Greentide's false bank.
    /// Owner rulings (card, 2026-10-03, GREENTIDE_TERROR_REPLACEMENT_1):
    ///   body = the weighted crown: only something its size or bigger sets it
    ///     off; small animals just reveal it;
    ///   it bites anything that steps on it (no truce, ban 1);
    ///   warning = almost none: it bites the moment weight lands;
    ///   the game pauses on the first-ever reveal.
    /// Design: design/Jawa/worldbuilding/biomes/greentide_terror_replacement_design_2026-10-02.md
    /// (candidate 5's body under the Vurrak name; consult threshold 0.6 body size).
    ///
    ///   <li Class="RimMandrake.Greentide.CompProperties_BankAmbusher">
    ///     <disguiseHediff>RM_BankDisguise</disguiseHediff>
    ///   </li>
    /// </summary>
    public class CompProperties_BankAmbusher : CompProperties
    {
        /// <summary>Hediff carrying HediffCompProperties_Invisibility (visibleToPlayer false).</summary>
        public HediffDef disguiseHediff;

        /// <summary>Contact scan interval. A walking colonist crosses a cell in ~13 ticks, so keep this short;
        /// the scan is one thing-list read of the cell it lies on.</summary>
        public int checkIntervalTicks = 6;

        /// <summary>Default weight threshold (body size). The live value is the Greentide setting
        /// vurrakTriggerBodySize, which starts here.</summary>
        public float triggerMinBodySize = 0.6f;

        public FloatRange strikeDamageRange = new FloatRange(18f, 28f);

        /// <summary>After any reveal it stays an ordinary visible animal this long before it may lie down again.</summary>
        public int revealHoldTicks = 2500;

        /// <summary>One bout of lying flat before the think tree gets a turn (food, rest).</summary>
        public int lieStillTicks = 2500;

        /// <summary>How far it creeps to find bank to lie on.</summary>
        public float relocateRadius = 14f;

        /// <summary>A cell is "bank" when it is standable, not deep water, and a water cell lies within this radius.</summary>
        public float bankWaterRadius = 2.9f;

        public SoundDef revealSound;
        public ThingDef strikeFilth;
        public int strikeFilthCount = 2;

        public CompProperties_BankAmbusher()
        {
            compClass = typeof(RM_CompBankAmbusher);
        }
    }

    public class RM_CompBankAmbusher : ThingComp
    {
        private Pawn lastVictim;
        private int revealedUntilTick = -1;

        public CompProperties_BankAmbusher Props => (CompProperties_BankAmbusher)props;

        private Pawn Self => parent as Pawn;

        public bool Disguised
        {
            get
            {
                Pawn p = Self;
                return p != null && Props.disguiseHediff != null && p.health?.hediffSet?.GetFirstHediffOfDef(Props.disguiseHediff) != null;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref lastVictim, "rmVurrakLastVictim");
            Scribe_Values.Look(ref revealedUntilTick, "rmVurrakRevealedUntil", -1);
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (Disguised)
            {
                Reveal(null, struck: false); // shot or trodden by a fight: the bank was never ground
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(System.Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }
            Pawn pawn = Self;
            if (pawn == null || !pawn.Spawned || pawn.Map == null)
            {
                return;
            }
            bool wild = pawn.Faction == null;
            if (!RM_GreentideSettings.vurrakAmbushEnabled || !wild || pawn.Dead || pawn.Downed
                || pawn.InMentalState || pawn.jobs == null)
            {
                Unhide(pawn);
                return;
            }

            if (Disguised)
            {
                if (pawn.CurJobDef != JobDefOf.Wait || !IsBank(pawn.Position, pawn.Map))
                {
                    Unhide(pawn); // it got up on its own (hunger, rest): no reveal event
                    return;
                }
                CheckContact(pawn);
                return;
            }

            if (TryEatVictim(pawn))
            {
                return;
            }
            if (Find.TickManager.TicksGame < revealedUntilTick)
            {
                return;
            }
            JobDef cur = pawn.CurJobDef;
            if (cur == null || cur == JobDefOf.GotoWander || cur == JobDefOf.Wait_Wander || cur == JobDefOf.Wait)
            {
                LieDown(pawn);
            }
        }

        /// <summary>Returns "STRUCK id", "REVEALED id" or "QUIET". Public for RM_VurrakProof.</summary>
        public string CheckContact(Pawn pawn)
        {
            List<Thing> things = pawn.Map.thingGrid.ThingsListAtFast(pawn.Position);
            Pawn heavy = null;
            Pawn light = null;
            float threshold = RM_GreentideSettings.vurrakTriggerBodySize;
            for (int i = 0; i < things.Count; i++)
            {
                if (!(things[i] is Pawn c) || c == pawn || c.Dead || c.def == pawn.def || c.Flying)
                {
                    continue;
                }
                if (c.BodySize >= threshold)
                {
                    heavy = c;
                    break;
                }
                light = light ?? c;
            }
            if (heavy != null)
            {
                Reveal(heavy, struck: true);
                Strike(pawn, heavy);
                return "STRUCK " + heavy.ThingID;
            }
            if (light != null)
            {
                Reveal(light, struck: false);
                return "REVEALED " + light.ThingID;
            }
            return "QUIET";
        }

        private void Reveal(Pawn by, bool struck)
        {
            Pawn pawn = Self;
            Unhide(pawn);
            revealedUntilTick = Find.TickManager.TicksGame + Props.revealHoldTicks;
            if (pawn.Spawned && Props.revealSound != null)
            {
                Props.revealSound.PlayOneShot(new TargetInfo(pawn.Position, pawn.Map));
            }
            RM_GameComponent_Vurrak.NoteReveal(pawn, by, struck);
        }

        private void Strike(Pawn pawn, Pawn victim)
        {
            if (Props.strikeFilth != null && Props.strikeFilthCount > 0)
            {
                FilthMaker.TryMakeFilth(victim.Position, pawn.Map, Props.strikeFilth, Props.strikeFilthCount);
            }
            float angle = (victim.DrawPos - pawn.DrawPos).AngleFlat();
            victim.TakeDamage(new DamageInfo(DamageDefOf.Bite, Props.strikeDamageRange.RandomInRange, 0f, angle, pawn));
            lastVictim = victim;
            if (victim.Faction == Faction.OfPlayer && !victim.Dead)
            {
                Messages.Message("The bank under " + victim.LabelShort + " was a " + pawn.KindLabel + ". It has bitten "
                    + victim.Possessive() + " legs out from under " + victim.Possessive() + ".",
                    new LookTargets(pawn), MessageTypeDefOf.ThreatSmall);
            }
            if (!victim.Dead && victim.Spawned)
            {
                Job attack = JobMaker.MakeJob(JobDefOf.AttackMelee, victim);
                attack.killIncappedTarget = true;
                attack.expiryInterval = 900;
                attack.checkOverrideOnExpire = true;
                pawn.jobs.StartJob(attack, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
            }
        }

        private bool TryEatVictim(Pawn pawn)
        {
            if (lastVictim == null || !lastVictim.Dead)
            {
                return false;
            }
            Corpse corpse = lastVictim.Corpse;
            if (corpse == null || !corpse.Spawned || corpse.Map != pawn.Map
                || (corpse.Position - pawn.Position).LengthHorizontalSquared > 25f)
            {
                lastVictim = null;
                return false;
            }
            if (pawn.CurJobDef == JobDefOf.Ingest || pawn.needs?.food == null || pawn.needs.food.CurLevelPercentage > 0.9f)
            {
                return false;
            }
            if (!pawn.CanReserveAndReach(corpse, PathEndMode.Touch, Danger.Some))
            {
                return false;
            }
            Job eat = JobMaker.MakeJob(JobDefOf.Ingest, corpse);
            eat.count = 1;
            pawn.jobs.StartJob(eat, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
            return true;
        }

        public void LieDown(Pawn pawn)
        {
            Map map = pawn.Map;
            if (IsBank(pawn.Position, map))
            {
                Job wait = JobMaker.MakeJob(JobDefOf.Wait);
                wait.expiryInterval = Props.lieStillTicks;
                wait.checkOverrideOnExpire = true;
                pawn.jobs.StartJob(wait, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
                Hide(pawn);
                return;
            }
            if (CellFinder.TryFindRandomReachableNearbyCell(pawn.Position, map, Props.relocateRadius,
                    TraverseParms.For(pawn), c => IsBank(c, map), null, out IntVec3 bank))
            {
                Job go = JobMaker.MakeJob(JobDefOf.Goto, bank);
                go.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.jobs.StartJob(go, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
            }
        }

        public bool IsBank(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || !c.Standable(map))
            {
                return false;
            }
            TerrainDef here = c.GetTerrain(map);
            if (here == null || here.passability == Traversability.Impassable || IsDeep(here))
            {
                return false;
            }
            int n = GenRadial.NumCellsInRadius(Props.bankWaterRadius);
            for (int i = 0; i < n; i++)
            {
                IntVec3 o = c + GenRadial.RadialPattern[i];
                if (o.InBounds(map) && o.GetTerrain(map) is TerrainDef t && t.IsWater)
                {
                    return true;
                }
            }
            return false;
        }

        private static bool IsDeep(TerrainDef t)
        {
            return t == TerrainDefOf.WaterDeep || t == TerrainDefOf.WaterOceanDeep || t == TerrainDefOf.WaterMovingChestDeep;
        }

        private void Hide(Pawn pawn)
        {
            if (Props.disguiseHediff == null || pawn.health == null || Disguised)
            {
                return;
            }
            pawn.health.AddHediff(HediffMaker.MakeHediff(Props.disguiseHediff, pawn));
        }

        private void Unhide(Pawn pawn)
        {
            if (pawn?.health == null || Props.disguiseHediff == null)
            {
                return;
            }
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(Props.disguiseHediff);
            if (h == null)
            {
                return;
            }
            pawn.GetInvisibilityComp()?.BecomeVisible(instant: true);
            pawn.health.RemoveHediff(h);
        }
    }

    /// <summary>Remembers, per game, whether any Vurrak has ever been revealed in front of the player, so the
    /// very first reveal pauses the game and explains itself (owner ruling 2026-10-03).</summary>
    public class RM_GameComponent_Vurrak : GameComponent
    {
        public bool firstRevealSeen;

        public RM_GameComponent_Vurrak(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref firstRevealSeen, "rmVurrakFirstRevealSeen", false);
        }

        public static void NoteReveal(Pawn vurrak, Pawn by, bool struck)
        {
            RM_GameComponent_Vurrak gc = Current.Game?.GetComponent<RM_GameComponent_Vurrak>();
            if (gc == null || gc.firstRevealSeen || vurrak?.Map == null)
            {
                return;
            }
            if (vurrak.Map.mapPawns.FreeColonistsSpawnedCount == 0)
            {
                return; // nobody of ours there to see it: the first reveal is still to come
            }
            gc.firstRevealSeen = true;
            if (!RM_GreentideSettings.vurrakFirstRevealPause)
            {
                return;
            }
            string what = by == null
                ? "Something hit it, and it moved."
                : struck
                    ? by.LabelShort + " stepped onto it, and it bit."
                    : by.LabelShort + " was too light to set it off, but the ground flexed and showed what it was.";
            Find.LetterStack.ReceiveLetter("The bank moved",
                "A stretch of silted riverbank just stood up. It was a vurrak, lying flat and caked in silt, and nothing "
                + "about it looked like an animal until weight landed on it. " + what + "\n\n"
                + "Vurraks lie along the water's edge. Anything about a person's size or bigger that steps on one is bitten "
                + "at once. Smaller animals only make it flinch and show itself, so watching where wildlife walks can tell "
                + "you which banks are not banks.",
                LetterDefOf.ThreatBig, new LookTargets(vurrak));
            Find.TickManager.Pause();
        }
    }

    /// <summary>Bridge proof (jawa/static_call), GREENTIDE_VURRAK_BUILD_1 validation chain "vurrak".</summary>
    public static class RM_VurrakProof
    {
        /// <summary>Lays the wild Vurrak on <paramref name="cell"/> flat (disguised), spawns one
        /// <paramref name="stepper"/> on the same cell and runs the contact check once.
        /// Returns "DISGUISED=<bool> -> STRUCK id | REVEALED id | QUIET", or "REFUSED: why".</summary>
        public static string ProofStepOn(Map map, IntVec3 cell, PawnKindDef stepper)
        {
            if (map == null || stepper == null)
            {
                return "REFUSED: no map or stepper kind";
            }
            Pawn vurrak = null;
            foreach (Thing t in cell.GetThingList(map))
            {
                if (t is Pawn p && p.TryGetComp<RM_CompBankAmbusher>() != null)
                {
                    vurrak = p;
                    break;
                }
            }
            if (vurrak == null)
            {
                return "REFUSED: no vurrak at " + cell;
            }
            RM_CompBankAmbusher comp = vurrak.TryGetComp<RM_CompBankAmbusher>();
            if (!RM_GreentideSettings.vurrakAmbushEnabled)
            {
                return "REFUSED: vurrakAmbushEnabled is off";
            }
            if (!comp.IsBank(cell, map))
            {
                return "REFUSED: " + cell + " is not bank (needs water within " + comp.Props.bankWaterRadius + ")";
            }
            comp.LieDown(vurrak);
            bool disguised = comp.Disguised;
            Faction fac = stepper.RaceProps.Humanlike ? Faction.OfPlayer : null;
            Pawn s = PawnGenerator.GeneratePawn(stepper, fac);
            GenSpawn.Spawn(s, cell, map);
            return "DISGUISED=" + disguised + " -> " + comp.CheckContact(vurrak);
        }
    }
}
