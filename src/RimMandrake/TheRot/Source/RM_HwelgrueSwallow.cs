using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.TheRot
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_STILL_ALIVE_SWALLOW_1 — Still Alive In There. The hwelgrue swallows the DOWNED (any faction, humanlike
    // or animal) lying in the open, one at a time, and digests them slowly enough to rescue: hours per body size
    // (setting). Shape modelled on vanilla CompDevourer (Anomaly, decompiled 1.6): one-thing ThingOwner with
    // removeContentsIfDestroyed false, DeSpawn-then-TryAdd, drop near with a 60-tick stun, release on
    // Notify_Downed / Notify_Killed, the earned acid damage on release. CompDevourer itself is NOT attached (its
    // animation and leap-ability calls are devourer-specific).
    //
    //   cut out   released alive when the hwelgrue is downed or killed, or once it has taken the belly-cut
    //             threshold of damage (setting, 150) since the swallow. Released pawns are stunned, Sheen-coated
    //             (RM_SheenCoating) and take acid damage scaled by the time they spent inside.
    //   timeout   the swallowed pawn dies (acid), and its corpse goes to RM_CompGutDigest (metal gear comes
    //             back in a casting, the rest is gone).
    //   the mark  knocking from inside: one-shot sounds on the hwelgrue, LOUDER and FASTER early, fainter and
    //             slower as time runs out (three stage defs + scrabbling for an animal); silence when empty.
    //             Deviation: one-shots on a schedule, not a sustainer, so volume and rate are both ours to drive.
    //             PLACEHOLDER AUDIO: the stage defs use vanilla clip folders (wood punch, small scratch) pitched
    //             down until authored knocking lands.
    //   strangers a newly met wild hwelgrue may already hold someone (setting chance): a drifter or a pack
    //             animal, with a few hours left.
    // ════════════════════════════════════════════════════════════════════

    public class CompProperties_RM_GutSwallow : CompProperties
    {
        public float minHoursToDigest = 3f;

        public CompProperties_RM_GutSwallow()
        {
            compClass = typeof(RM_CompGutSwallow);
        }
    }

    public class RM_CompGutSwallow : ThingComp, IThingHolder
    {
        private ThingOwner<Thing> held;
        private int ticksInside;
        private int ticksToDigest;
        private float damageSinceSwallow;
        private int nextKnockTick = -1;
        private bool strangerRolled;
        private bool wasDrafted;

        public CompProperties_RM_GutSwallow Props => (CompProperties_RM_GutSwallow)props;

        private Pawn Self => parent as Pawn;

        public RM_CompGutSwallow()
        {
            held = new ThingOwner<Thing>(this, oneStackOnly: true, LookMode.Deep, removeContentsIfDestroyed: false);
        }

        public IThingHolder ParentHolder => parent.ParentHolder;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public ThingOwner GetDirectlyHeldThings() => held;

        public Pawn Inside => held.Count > 0 ? held[0] as Pawn : null;

        public bool Holding => held.Count > 0;

        /// <summary>Fraction of digestion time left, 1 = just swallowed, 0 = done.</summary>
        public float TimeLeftFraction => ticksToDigest <= 0 ? 0f : Mathf.Clamp01(1f - (float)ticksInside / ticksToDigest);

        public int TicksLeft => Mathf.Max(0, ticksToDigest - ticksInside);

        public static int DigestTicksFor(Pawn victim, CompProperties_RM_GutSwallow props)
        {
            float hours = Mathf.Max(props?.minHoursToDigest ?? 3f, RM_TheRotSettings.swallowHoursPerBodySize * (victim?.BodySize ?? 1f));
            return Mathf.RoundToInt(hours * 2500f);
        }

        // ── finding and swallowing ──────────────────────────────────────

        public static bool Swallowable(Pawn victim, Pawn eater)
        {
            if (victim == null || victim == eater || !victim.Spawned || victim.Dead || !victim.Downed) return false;
            if (victim.def == RM_HwelgrueDefOf.RM_Hwelgrue || victim.InBed() || victim.CarriedBy != null) return false;
            if (victim.Position.Roofed(victim.Map)) return false;
            return eater == null || eater.CanReserve(victim);
        }

        public static Pawn FindDowned(Pawn eater, float radius)
        {
            return (Pawn)GenClosest.ClosestThingReachable(eater.Position, eater.Map, ThingRequest.ForGroup(ThingRequestGroup.Pawn),
                PathEndMode.Touch, TraverseParms.For(eater), radius, t => Swallowable(t as Pawn, eater));
        }

        public bool Swallow(Pawn victim)
        {
            if (Holding || !Swallowable(victim, null)) return false;
            if (victim.drafter != null) wasDrafted = victim.drafter.Drafted;
            bool colony = victim.Faction == Faction.OfPlayer;
            victim.DeSpawn();
            if (!held.TryAdd(victim))
            {
                GenSpawn.Spawn(victim, parent.Position, parent.Map);
                return false;
            }
            ticksInside = 0;
            damageSinceSwallow = 0f;
            ticksToDigest = DigestTicksFor(victim, Props);
            nextKnockTick = Find.TickManager.TicksGame + 120;
            if (colony)
            {
                Find.LetterStack.ReceiveLetter("Swallowed: " + victim.LabelShortCap,
                    victim.LabelShortCap + " was swallowed by the hwelgrue.\n\nThey are still alive in there, for now: about "
                  + Mathf.RoundToInt(TicksLeft / 2500f) + " hours. Cut them out - down or kill it, or hurt it hard enough "
                  + "that its belly opens (" + Mathf.RoundToInt(RM_TheRotSettings.swallowBellyCutDamage) + " damage).",
                    LetterDefOf.ThreatBig, Self);
            }
            return true;
        }

        // ── ticking ─────────────────────────────────────────────────────

        public override void CompTick()
        {
            base.CompTick();
            Pawn self = Self;
            if (self == null || !self.Spawned || self.Dead) return;
            if (!strangerRolled && parent.IsHashIntervalTick(250))
            {
                strangerRolled = true;
                MaybeHoldStranger(self);
            }
            if (!Holding) return;
            ticksInside++;
            Pawn inside = Inside;
            if (inside == null || inside.Dead)
            {
                FinishDigestion();
                return;
            }
            if (ticksInside >= ticksToDigest)
            {
                FinishDigestion();
                return;
            }
            if (Find.TickManager.TicksGame >= nextKnockTick)
            {
                Knock(self, inside);
            }
        }

        private void Knock(Pawn self, Pawn inside)
        {
            float f = TimeLeftFraction;
            nextKnockTick = Find.TickManager.TicksGame + Mathf.RoundToInt(Mathf.Lerp(900f, 180f, f));
            float vol = KnockVolume(f);
            if (vol <= 0f) return;
            SoundDef def = KnockDef(inside, f);
            if (def == null) return;
            SoundInfo info = SoundInfo.InMap(new TargetInfo(self.Position, self.Map));
            info.volumeFactor = vol;
            def.PlayOneShot(info);
        }

        public static float KnockVolume(float timeLeftFraction) => Mathf.Lerp(0.25f, 1f, timeLeftFraction) * RM_TheRotSettings.swallowLoudness;

        public static SoundDef KnockDef(Pawn inside, float f)
        {
            if (inside != null && !inside.RaceProps.Humanlike) return RM_HwelgrueDefOf.RM_GutScrabbling;
            if (f > 0.66f) return RM_HwelgrueDefOf.RM_GutKnocking;
            if (f > 0.33f) return RM_HwelgrueDefOf.RM_GutKnocking_Weak;
            return RM_HwelgrueDefOf.RM_GutKnocking_Failing;
        }

        private void MaybeHoldStranger(Pawn self)
        {
            if (Holding || self.Faction != null || !RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.hwelgrue
                || !RM_TheRotSettings.hwelgrueSwallow || !Rand.Chance(RM_TheRotSettings.swallowStrangerChance)) return;
            if (self.Map.mapPawns.AllPawnsSpawned.Any(p => p.Downed && !p.Dead && p != self)) return;
            HoldStranger();
        }

        /// <summary>Puts a stranger inside with a few hours left: a drifter, or a pack animal.</summary>
        public Pawn HoldStranger()
        {
            if (Holding) return null;
            PawnKindDef kind = Rand.Chance(0.5f) ? DefDatabase<PawnKindDef>.GetNamedSilentFail("Muffalo") : null;
            kind = kind ?? DefDatabase<PawnKindDef>.GetNamedSilentFail("Drifter") ?? PawnKindDefOf.Villager;
            Pawn stranger = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer,
                forceGenerateNewPawn: true, canGeneratePawnRelations: false));
            if (!held.TryAdd(stranger)) return null;
            ticksToDigest = DigestTicksFor(stranger, Props);
            ticksInside = Mathf.Max(0, ticksToDigest - Mathf.RoundToInt(Rand.Range(2f, 6f) * 2500f));
            damageSinceSwallow = 0f;
            nextKnockTick = Find.TickManager.TicksGame + 120;
            return stranger;
        }

        // ── endings ─────────────────────────────────────────────────────

        private void FinishDigestion()
        {
            Pawn inside = Inside;
            Thing thing = held.Count > 0 ? held[0] : null;
            if (thing == null) return;
            if (inside != null && !inside.Dead)
            {
                DamageInfo acid = new DamageInfo(DamageDefOf.AcidBurn, 9999f, 0f, -1f, parent);
                inside.Kill(acid);
            }
            Thing remains = held.Count > 0 ? held[0] : null;
            if (remains != null)
            {
                held.Remove(remains);
                RM_CompGutDigest gut = parent.TryGetComp<RM_CompGutDigest>();
                if (gut != null) gut.Digest(remains);
                else if (!remains.Destroyed) remains.Destroy(DestroyMode.Vanish);
            }
            ticksInside = 0;
            ticksToDigest = 0;
            if (inside != null && Self?.Spawned == true)
            {
                Messages.Message("The knocking inside the hwelgrue has stopped.", Self, MessageTypeDefOf.NegativeEvent, false);
            }
        }

        /// <summary>Lets the swallowed pawn out alive (if it is). Returns it, or null.</summary>
        public Pawn Release(Map map, string why)
        {
            if (!Holding) return null;
            if (map == null) map = parent.MapHeld;
            if (map == null) return null;
            Thing thing = held[0];
            IntVec3 at = parent.PositionHeld;
            if (!held.TryDrop(thing, at, map, ThingPlaceMode.Near, out Thing dropped))
            {
                if (!RCellFinder.TryFindRandomCellNearWith(at, c => c.Standable(map), map, out IntVec3 cell, 1)) return null;
                dropped = GenSpawn.Spawn(held.Take(thing), cell, map);
            }
            float f = TimeLeftFraction;
            ticksInside = 0;
            ticksToDigest = 0;
            damageSinceSwallow = 0f;
            if (!(dropped is Pawn p)) return null;
            p.stances?.stunner?.StunFor(60, Self, addBattleLog: false, showMote: false);
            if (p.drafter != null) p.drafter.Drafted = wasDrafted;
            if (RM_HwelgrueDefOf.RM_SheenCoating != null) p.health.AddHediff(RM_HwelgrueDefOf.RM_SheenCoating);
            float earned = Mathf.Lerp(60f, 5f, f);
            DamageInfo acid = new DamageInfo(DamageDefOf.AcidBurn, earned, 0f, -1f, parent);
            acid.SetApplyAllDamage(true);
            p.TakeDamage(acid);
            Messages.Message(p.LabelShortCap + " " + why + ", slick with Sheen and acid-burned.", p,
                p.Faction == Faction.OfPlayer ? MessageTypeDefOf.PositiveEvent : MessageTypeDefOf.NeutralEvent, false);
            return p;
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (!Holding || Self == null || Self.Dead) return;
            damageSinceSwallow += totalDamageDealt;
            if (damageSinceSwallow >= RM_TheRotSettings.swallowBellyCutDamage)
            {
                Release(Self.MapHeld, "was cut out of the hwelgrue's belly");
            }
        }

        public override void Notify_Downed()
        {
            base.Notify_Downed();
            Release(Self?.MapHeld, "crawled out of the downed hwelgrue");
        }

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);
            Release(prevMap, "was cut out of the dead hwelgrue");
        }

        public override string CompInspectStringExtra()
        {
            Pawn inside = Inside;
            if (inside == null || inside.Dead) return null;
            float hours = TicksLeft / 2500f;
            return "Something is still alive in there: " + inside.LabelShort + ", about " + Mathf.Max(1, Mathf.RoundToInt(hours)) + " hours.";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref held, "held", this);
            Scribe_Values.Look(ref ticksInside, "ticksInside", 0);
            Scribe_Values.Look(ref ticksToDigest, "ticksToDigest", 0);
            Scribe_Values.Look(ref damageSinceSwallow, "damageSinceSwallow", 0f);
            Scribe_Values.Look(ref nextKnockTick, "nextKnockTick", -1);
            Scribe_Values.Look(ref strangerRolled, "strangerRolled", false);
            Scribe_Values.Look(ref wasDrafted, "wasDrafted", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (held == null) held = new ThingOwner<Thing>(this, oneStackOnly: true, LookMode.Deep, removeContentsIfDestroyed: false);
                held.removeContentsIfDestroyed = false;
            }
        }
    }

    /// <summary>Crawl to the downed pawn and take it in.</summary>
    public class RM_JobDriver_GutSwallow : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !(job.targetA.Thing is Pawn v) || !v.Downed);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(90, TargetIndex.A);
            Toil take = ToilMaker.MakeToil("RM_GutSwallow_Take");
            take.initAction = delegate
            {
                if (job.targetA.Thing is Pawn victim)
                {
                    pawn.TryGetComp<RM_CompGutSwallow>()?.Swallow(victim);
                }
            };
            take.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return take;
        }
    }

    /// <summary>Deterministic reads/triggers for jawa/static_call (THE_ROT_FIRST_SCRIPT_1).</summary>
    public static class RM_HwelgrueSwallowProof
    {
        private static Pawn Hwelgrue => Find.CurrentMap?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.def == RM_HwelgrueDefOf.RM_Hwelgrue && !p.Dead);

        /// <summary>Downs a fresh drifter beside the hwelgrue and swallows it directly. "SWALLOW held NAME | inspect ...".</summary>
        public static string ProofSwallow()
        {
            Pawn h = Hwelgrue;
            RM_CompGutSwallow comp = h?.TryGetComp<RM_CompGutSwallow>();
            if (comp == null) return "REFUSED: no hwelgrue on the current map";
            if (comp.Holding) return "REFUSED: already holding " + comp.Inside?.LabelShort;
            Pawn victim = PawnGenerator.GeneratePawn(DefDatabase<PawnKindDef>.GetNamedSilentFail("Drifter") ?? PawnKindDefOf.Villager, null);
            GenSpawn.Spawn(victim, CellFinder.RandomClosewalkCellNear(h.Position, h.Map, 3), h.Map);
            HealthUtility.DamageUntilDowned(victim, allowBleedingWounds: false);
            bool ok = victim.Downed && comp.Swallow(victim);
            return "SWALLOW " + (ok ? "held " + comp.Inside?.LabelShort : "failed (downed " + victim.Downed + ")")
                + " | spawned " + victim.Spawned + " | inspect " + (comp.CompInspectStringExtra() ?? "null");
        }

        /// <summary>Cuts the hwelgrue's belly (its body core part) for <paramref name="damage"/>.
        /// "CUT released B | spawned B | inside NAME|none | via belly|downed|dead | dealt N".
        /// The part is fixed, not random: an untargeted hit landing on a leg is capped at the leg's hit points,
        /// so the same 200 sometimes released and sometimes did not (run17 TheRot, 2026-10-03). A belly hit
        /// past the core part's hit points kills, which also releases; `via` says which ending fired.</summary>
        public static string ProofCut(float damage)
        {
            Pawn h = Hwelgrue;
            RM_CompGutSwallow comp = h?.TryGetComp<RM_CompGutSwallow>();
            if (comp == null) return "REFUSED: no hwelgrue on the current map";
            Pawn before = comp.Inside;
            BodyPartRecord belly = h.RaceProps.body.corePart;
            DamageInfo cut = new DamageInfo(DamageDefOf.Cut, damage, 0f, -1f, null, belly);
            cut.SetApplyAllDamage(true);
            float dealt = h.TakeDamage(cut).totalDamageDealt;
            string via = h.Dead ? "dead" : h.Downed ? "downed" : "belly";
            return "CUT released " + (before != null && !comp.Holding) + " | spawned " + (before?.Spawned ?? false)
                + " | inside " + (comp.Inside?.LabelShort ?? "none") + " | via " + via + " | dealt " + dealt.ToString("0");
        }

        /// <summary>The knock schedule at a given time-left fraction: "KNOCK def | volume v".</summary>
        public static string ProofKnock(float timeLeftFraction)
        {
            SoundDef d = RM_CompGutSwallow.KnockDef(null, timeLeftFraction);
            return "KNOCK " + (d?.defName ?? "none") + " | volume " + RM_CompGutSwallow.KnockVolume(timeLeftFraction).ToString("0.00");
        }
    }
}
