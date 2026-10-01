using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// STILLSAND_SAND_SWIM_KIT_1 — the worker behind RM_SandSwimExtension. Never authored in XML:
    /// RM_SandSwimStartup adds it to every race carrying the extension, so a consumer is one
    /// extension and nothing else.
    /// </summary>
    public class RM_CompProperties_SandSwim : CompProperties
    {
        public RM_CompProperties_SandSwim()
        {
            compClass = typeof(RM_CompSandSwim);
        }
    }

    /// <summary>
    /// State machine, evaluated every checkIntervalTicks (cosmetics and the rumble run per tick):
    ///   off swim terrain              -> surface (breach if it was under)
    ///   fighting / just hit / just breached (surfacedUntilTick) -> stay surfaced
    ///   hunting a target within strikeRangeCells -> breach for the strike
    ///   otherwise on swim terrain     -> submerged
    /// While submerged it will not press an attack on a pawn with no water in it (a race whose
    /// flesh is not organic: mechanoids, droids) — §4, droids are invisible to the food web.
    /// Same polling-comp shape as RM_CompAquaticAmbusher / RM_CompDrumLure in this assembly.
    /// </summary>
    public class RM_CompSandSwim : ThingComp
    {
        private int surfacedUntilTick = -1;
        private IntVec3 lastCell = IntVec3.Invalid;
        private Sustainer rumble;

        private RM_SandSwimExtension extCached;

        public RM_SandSwimExtension Ext => extCached ?? (extCached = parent.def.GetModExtension<RM_SandSwimExtension>());

        /// <summary>True while the pawn carries the submerged hediff (state-read friendly).</summary>
        public bool Submerged
        {
            get
            {
                Pawn pawn = parent as Pawn;
                return pawn?.health != null && Ext?.submergedHediff != null
                    && pawn.health.hediffSet.GetFirstHediffOfDef(Ext.submergedHediff) != null;
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            EnsureMarker(parent as Pawn);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            EndRumble();
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!(parent is Pawn pawn) || Ext == null)
            {
                return;
            }
            if (!pawn.Spawned || pawn.Dead || pawn.Map == null)
            {
                EndRumble();
                return;
            }

            if (pawn.Downed || !RM_CreatureBehaviorsSettings.sandSwimEnabled)
            {
                Surface(pawn, breach: false);
                return;
            }

            if (pawn.IsHashIntervalTick(Math.Max(1, Ext.checkIntervalTicks)))
            {
                Evaluate(pawn);
            }

            if (Submerged)
            {
                TickSubmerged(pawn);
            }
            else
            {
                EndRumble();
            }
        }

        private void Evaluate(Pawn pawn)
        {
            bool onSwim = RM_SandSwimUtility.IsSwimTerrain(pawn.Position, pawn.Map, Ext);
            bool submerged = Submerged;

            if (!onSwim)
            {
                Surface(pawn, breach: submerged); // reached hard ground: breaches out onto it
                return;
            }

            Pawn target = CurrentAttackTarget(pawn);
            if (submerged && target != null && RM_CreatureBehaviorsSettings.sandSwimDroidImmunity
                && !RM_SandSwimUtility.HasWaterInIt(target))
            {
                // §4: nothing under the sand senses a pawn with no water in it. Drop the attack
                // rather than surface for it; a surfaced (hit) swimmer can still fight back.
                pawn.jobs?.EndCurrentJob(JobCondition.Incompletable);
                target = null;
            }

            // STILLSAND_DUNE_GALE_1 §6: a storm is all vibration, so the swimmer cannot pick its
            // target out of it. It stays down and lets the strike go, like the droid case above.
            if (submerged && target != null)
            {
                RM_WeatherSenseExtension sense = RM_WeatherSenseExtension.On(pawn.Map);
                if (sense != null && sense.swimmerSenseChance < 1f && !Rand.Chance(sense.swimmerSenseChance))
                {
                    pawn.jobs?.EndCurrentJob(JobCondition.Incompletable);
                    target = null;
                }
            }

            if (target != null)
            {
                float range = Ext.strikeRangeCells;
                if ((target.Position - pawn.Position).LengthHorizontalSquared <= range * range)
                {
                    Surface(pawn, breach: submerged); // the strike
                    return;
                }
            }

            if (pawn.mindState?.meleeThreat != null)
            {
                Surface(pawn, breach: submerged); // in melee: never fights from under the sand
                return;
            }

            if (Find.TickManager.TicksGame < surfacedUntilTick)
            {
                return; // just breached — stays up
            }

            Submerge(pawn);
        }

        private void TickSubmerged(Pawn pawn)
        {
            // Wake puffs: a low dust line where it moves. Drawn for the player only (the pawn
            // itself is invisible) — the readable half of the wake until FOOTPRINT_TRACK_GRID_1
            // exists to hold the trough record.
            if (pawn.IsHashIntervalTick(Math.Max(1, Ext.wakeIntervalTicks)) && pawn.pather != null && pawn.pather.Moving)
            {
                FleckMaker.ThrowDustPuffThick(pawn.DrawPos, pawn.Map, 0.6f + 0.25f * pawn.BodySize,
                    new Color(0.78f, 0.69f, 0.52f, 0.7f));
            }

            // A drag: a submerged swimmer hauling a corpse scores the sand cell by cell.
            if (Ext.dragFilth != null && pawn.Position != lastCell
                && pawn.carryTracker?.CarriedThing is Corpse)
            {
                FilthMaker.TryMakeFilth(pawn.Position, pawn.Map, Ext.dragFilth, 1);
            }
            lastCell = pawn.Position;

            MaintainRumble(pawn);
        }

        private static Pawn CurrentAttackTarget(Pawn pawn)
        {
            Job job = pawn.CurJob;
            if (job == null)
            {
                return null;
            }
            if (job.def != JobDefOf.AttackMelee && job.def != JobDefOf.PredatorHunt)
            {
                return null;
            }
            return job.targetA.Thing as Pawn;
        }

        private void Submerge(Pawn pawn)
        {
            if (Submerged || pawn.health == null)
            {
                return;
            }
            pawn.health.AddHediff(HediffMaker.MakeHediff(Ext.submergedHediff, pawn)); // Invisibility comp's PostAdd hides it
        }

        private void Surface(Pawn pawn, bool breach)
        {
            EndRumble();
            if (pawn.health == null || Ext.submergedHediff == null)
            {
                return;
            }
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(Ext.submergedHediff);
            if (h == null)
            {
                return;
            }
            pawn.GetInvisibilityComp()?.BecomeVisible(instant: true);
            pawn.health.RemoveHediff(h);
            if (breach)
            {
                Breach(pawn);
            }
        }

        private void Breach(Pawn pawn)
        {
            surfacedUntilTick = Find.TickManager.TicksGame + Ext.surfacedTicks;
            if (!pawn.Spawned)
            {
                return;
            }
            Vector3 loc = pawn.DrawPos;
            for (int i = 0; i < 3; i++)
            {
                FleckMaker.ThrowDustPuffThick(loc + new Vector3(Rand.Range(-0.4f, 0.4f), 0f, Rand.Range(-0.4f, 0.4f)),
                    pawn.Map, 1.2f + 0.3f * pawn.BodySize, new Color(0.78f, 0.69f, 0.52f, 0.9f));
            }
            Ext.breachSound?.PlayOneShot(new TargetInfo(pawn.Position, pawn.Map));
            if (Ext.breachStaggerTicks > 0)
            {
                pawn.stances?.stagger?.StaggerFor(Ext.breachStaggerTicks);
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (parent is Pawn pawn && pawn.Spawned && !pawn.Dead && Ext != null && Submerged)
            {
                Surface(pawn, breach: true); // struck: driven up
            }
        }

        private void MaintainRumble(Pawn pawn)
        {
            if (Ext.rumbleSound == null || RM_CreatureBehaviorsSettings.sandSwimRumbleVolume <= 0f
                || (RM_WeatherSenseExtension.On(pawn.Map)?.drownsRumble ?? false))
            {
                EndRumble();
                return;
            }
            if (rumble == null || rumble.Ended)
            {
                SoundInfo info = SoundInfo.InMap(pawn, MaintenanceType.PerTick);
                info.volumeFactor = Mathf.Clamp(pawn.BodySize / 2f, 0.25f, 3f) * RM_CreatureBehaviorsSettings.sandSwimRumbleVolume;
                rumble = Ext.rumbleSound.TrySpawnSustainer(info);
            }
            rumble?.Maintain();
        }

        private void EndRumble()
        {
            if (rumble != null && !rumble.Ended)
            {
                rumble.End();
            }
            rumble = null;
        }

        private void EnsureMarker(Pawn pawn)
        {
            if (pawn?.health == null || Ext?.swimmerMarkerHediff == null)
            {
                return;
            }
            if (pawn.health.hediffSet.GetFirstHediffOfDef(Ext.swimmerMarkerHediff) == null)
            {
                pawn.health.AddHediff(HediffMaker.MakeHediff(Ext.swimmerMarkerHediff, pawn));
            }
        }

        /// <summary>§2 No vanishing. Called by the marker hediff for every pawn this swimmer kills.</summary>
        public void Notify_SwimmerKilled(Pawn victim)
        {
            Pawn pawn = parent as Pawn;
            Map map = victim?.MapHeld ?? pawn?.MapHeld;
            if (pawn == null || victim == null || map == null || Ext == null)
            {
                return;
            }
            IntVec3 at = victim.PositionHeld;
            if (!RM_SandSwimUtility.IsSwimTerrain(at, map, Ext))
            {
                return; // killed on hard ground, in plain view — an ordinary kill, no take
            }

            ThingDef funnel = Ext.takeFilth ?? DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Sand");
            if (funnel != null)
            {
                FilthMaker.TryMakeFilth(at, map, funnel, 1);
            }

            string text = "Something under the sand came up beneath " + victim.LabelShort
                + " and pulled the body down. A collapsed funnel of sand marks the place. It was a "
                + pawn.KindLabel + ".";
            bool playerConcern = victim.Faction == Faction.OfPlayer || victim.HostFaction == Faction.OfPlayer;
            if (playerConcern)
            {
                Find.LetterStack.ReceiveLetter("Taken under: " + victim.LabelShort, text,
                    LetterDefOf.NegativeEvent, new LookTargets(new TargetInfo(at, map)));
            }
            else if (map == Find.CurrentMap)
            {
                // Wild losses get a message, not a letter: the funnel is the sign, and a letter per
                // wild kill would bury the stack.
                Messages.Message(text, new LookTargets(new TargetInfo(at, map)), MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }

        public override string CompInspectStringExtra()
        {
            return Submerged ? "Under the sand." : null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref surfacedUntilTick, "rmSandSwimSurfacedUntil", -1);
        }
    }

    /// <summary>The marker hediff's comp: forwards the swimmer's kills to RM_CompSandSwim and
    /// keeps the marker out of the health tab.</summary>
    public class RM_HediffCompProperties_SandSwimmer : HediffCompProperties
    {
        public RM_HediffCompProperties_SandSwimmer()
        {
            compClass = typeof(RM_HediffComp_SandSwimmer);
        }
    }

    public class RM_HediffComp_SandSwimmer : HediffComp
    {
        public override bool CompDisallowVisible()
        {
            return true;
        }

        public override void Notify_KilledPawn(Pawn victim, DamageInfo? dinfo)
        {
            base.Notify_KilledPawn(victim, dinfo);
            Pawn.GetComp<RM_CompSandSwim>()?.Notify_SwimmerKilled(victim);
        }
    }

    public static class RM_SandSwimUtility
    {
        private static readonly HashSet<TerrainDef> DefaultSwimTerrains = new HashSet<TerrainDef>();
        private static bool defaultsBuilt;

        public static bool IsSwimTerrain(IntVec3 c, Map map, RM_SandSwimExtension ext)
        {
            if (map == null || !c.InBounds(map))
            {
                return false;
            }
            TerrainDef t = c.GetTerrain(map);
            if (t == null)
            {
                return false;
            }
            if (ext?.swimTerrains != null && ext.swimTerrains.Count > 0)
            {
                return ext.swimTerrains.Contains(t);
            }
            EnsureDefaults();
            return DefaultSwimTerrains.Contains(t);
        }

        private static void EnsureDefaults()
        {
            if (defaultsBuilt)
            {
                return;
            }
            defaultsBuilt = true;
            foreach (string n in new[] { "Sand", "SoftSand", "RM_DeepSand" })
            {
                TerrainDef t = DefDatabase<TerrainDef>.GetNamedSilentFail(n);
                if (t != null)
                {
                    DefaultSwimTerrains.Add(t);
                }
            }
        }

        /// <summary>§4: "a pawn with no water in it" — by race flag (organic flesh), never a
        /// defName list. Mechanoids and droids are not.</summary>
        public static bool HasWaterInIt(Pawn p)
        {
            return p?.RaceProps != null && p.RaceProps.IsFlesh;
        }

        /// <summary>§8, the piinnok hook (WATCHER_CREATURES_MOD_1): submerged swimmers with body
        /// size at least minBodySize within radius of cell. Returns the count; fills results
        /// when given.</summary>
        public static int SubmergedSwimmersNear(Map map, IntVec3 cell, float radius, float minBodySize, List<Pawn> results = null)
        {
            if (map == null)
            {
                return 0;
            }
            int count = 0;
            float r2 = radius * radius;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.BodySize < minBodySize || (p.Position - cell).LengthHorizontalSquared > r2)
                {
                    continue;
                }
                RM_CompSandSwim comp = p.GetComp<RM_CompSandSwim>();
                if (comp != null && comp.Submerged)
                {
                    count++;
                    results?.Add(p);
                }
            }
            return count;
        }
    }

    /// <summary>Gives every race carrying RM_SandSwimExtension its RM_CompSandSwim, so a consumer
    /// writes one extension and nothing else (§3).</summary>
    [StaticConstructorOnStartup]
    public static class RM_SandSwimStartup
    {
        static RM_SandSwimStartup()
        {
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def.race == null || !def.HasModExtension<RM_SandSwimExtension>())
                {
                    continue;
                }
                if (def.comps == null)
                {
                    def.comps = new List<CompProperties>();
                }
                if (!def.comps.Exists(c => c is RM_CompProperties_SandSwim))
                {
                    def.comps.Add(new RM_CompProperties_SandSwim());
                }
            }
        }
    }
}
