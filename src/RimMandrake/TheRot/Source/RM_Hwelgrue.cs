using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TheRot
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_HWELGRUE_GIANT_BUILD_1 — the hwelgrue, the gut that walks (spec in the item;
    // design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md §3).
    //
    //   graze    RM_JobGiver_GutGraze, spliced into the vanilla animal think tree at Animal_PreWander
    //            (the RM_ScratchOnSweetline idiom): an idle hwelgrue crawls to the nearest corpse, rotting
    //            food or haulable item on OPEN ground (not in a stockpile zone, not under a roof) and eats it.
    //   digest   RM_CompGutDigest: metal things (metallic stuff, components, plasteel, or a costList holding
    //            them) go WHOLE into its ThingOwner; everything else is destroyed. A corpse's gear and
    //            inventory are sorted the same way. Every N days (setting) a non-empty gut passes one
    //            RM_SheenCasting holding everything.
    //   casting  RM_CompSheenCasting + vanilla CompUsable: "Crack open" drops the contents at full HP.
    //   rest     standing still, it accelerates rot (×setting) on rottables within 6 cells (vanilla's own
    //            rate formula, the RM_MapComponent_AcceleratedRot idiom).
    //   temper   never starts a fight; when hurt it turns on whatever hurt it (melee, expiring job).
    //   cap      at most N (setting) living hwelgrue per map; a wild extra is removed on its first sweep.
    //   death    the gut's contents drop as one casting where it died (spec said at butchering: dropping at
    //            death cannot be lost to a corpse that is never butchered).
    //
    // NOT BUILT here: warm-ground marking (RM_MapComponent_WarmGround is terrain+room scoped and has no
    // cell-marking API, so "reuse, no new meter" has nothing to call), the swallow of downed pawns
    // (ROT_STILL_ALIVE_SWALLOW_1), the drive core (ROT_SWALLOWED_NAVIGATOR_1), the gut-mother sac
    // (ROT_GUT_MOTHER_VAT_1).
    // ════════════════════════════════════════════════════════════════════

    [DefOf]
    public static class RM_HwelgrueDefOf
    {
        public static ThingDef RM_Hwelgrue;
        public static ThingDef RM_SheenCasting;
        public static JobDef RM_GutGraze;

        static RM_HwelgrueDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_HwelgrueDefOf));
        }
    }

    public class CompProperties_RM_GutDigest : CompProperties
    {
        public float grazeRadius = 30f;
        public float restRadius = 6f;
        public int sweepInterval = 250;

        public CompProperties_RM_GutDigest()
        {
            compClass = typeof(RM_CompGutDigest);
        }
    }

    public class RM_CompGutDigest : ThingComp, IThingHolder
    {
        private ThingOwner<Thing> gut;
        private int ticksDigesting;
        private bool capChecked;

        public CompProperties_RM_GutDigest Props => (CompProperties_RM_GutDigest)props;

        private Pawn Pawn => parent as Pawn;

        public ThingOwner<Thing> Gut => gut;

        public RM_CompGutDigest()
        {
            gut = new ThingOwner<Thing>(this, oneStackOnly: false);
        }

        public IThingHolder ParentHolder => parent.ParentHolder;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public ThingOwner GetDirectlyHeldThings() => gut;

        public static int CastingIntervalTicks => Mathf.Max(2500, Mathf.RoundToInt(RM_TheRotSettings.hwelgrueCastingDays * 60000f));

        public override void CompTick()
        {
            base.CompTick();
            Pawn p = Pawn;
            if (p == null || !p.Spawned || p.Dead || !parent.IsHashIntervalTick(Props.sweepInterval)) return;
            if (!capChecked)
            {
                capChecked = true;
                if (OverCap(p))
                {
                    p.Destroy(DestroyMode.Vanish);
                    return;
                }
                RM_MapComponent_Hwelgrue.Get(p.Map)?.NotifySeen(p);
            }
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.hwelgrue) return;
            if (gut.Count > 0)
            {
                ticksDigesting += Props.sweepInterval;
                if (ticksDigesting >= CastingIntervalTicks)
                {
                    PassCasting();
                }
            }
            else
            {
                ticksDigesting = 0;
            }
            if (!p.Downed && !(p.pather?.Moving ?? false))
            {
                AccelerateRotAround(p);
            }
        }

        /// <summary>True when this is a WILD hwelgrue and the map already holds the setting's cap of
        /// other living ones (or the feature is off).</summary>
        public static bool OverCap(Pawn p)
        {
            if (p.Faction != null) return false;
            int cap = RM_TheRotSettings.theRotEnabled && RM_TheRotSettings.hwelgrue ? RM_TheRotSettings.hwelgrueMapCap : 0;
            int others = p.Map.mapPawns.AllPawnsSpawned.Count(o => o != p && o.def == p.def && !o.Dead);
            return others >= cap;
        }

        private void AccelerateRotAround(Pawn p)
        {
            float extra = RM_TheRotSettings.hwelgrueRotMultiplier - 1f;
            if (extra <= 0f) return;
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(p.Position, p.Map, Props.restRadius, true))
            {
                CompRottable rot = t.TryGetComp<CompRottable>();
                if (rot == null || !rot.Active) continue;
                float rate = GenTemperature.RotRateAtTemperature(t.AmbientTemperature);
                if (rate <= 0f) continue;
                rot.RotProgress += rate * extra * Props.sweepInterval;
            }
        }

        // ── eating ──────────────────────────────────────────────────────

        public static bool IsMetal(ThingDef def)
        {
            if (def == null) return false;
            if (def == ThingDefOf.ComponentIndustrial || def == ThingDefOf.ComponentSpacer || def == ThingDefOf.Plasteel) return true;
            if (def.stuffProps?.categories != null && def.stuffProps.categories.Contains(StuffCategoryDefOf.Metallic)) return true;
            return def.costList != null && def.costList.Any(c => c.thingDef != null && (c.thingDef == ThingDefOf.ComponentIndustrial
                || c.thingDef == ThingDefOf.ComponentSpacer || c.thingDef == ThingDefOf.Plasteel
                || (c.thingDef.stuffProps?.categories?.Contains(StuffCategoryDefOf.Metallic) ?? false)));
        }

        /// <summary>Metal content of a thing: the thing itself is metal, or made of a metallic stuff.</summary>
        public static bool HoldsMetal(Thing t)
        {
            if (t == null) return false;
            if (t is MinifiedThing m) return HoldsMetal(m.InnerThing);
            return IsMetal(t.def) || (t.Stuff != null && IsMetal(t.Stuff));
        }

        /// <summary>Eats <paramref name="food"/>: metal goes whole into the gut, the rest is destroyed.
        /// A corpse's equipment, apparel and inventory are sorted the same way. Returns how many things
        /// went into the gut.</summary>
        public int Digest(Thing food)
        {
            if (food == null || food.Destroyed) return 0;
            int kept = 0;
            if (food is Corpse corpse && corpse.InnerPawn != null)
            {
                Pawn inner = corpse.InnerPawn;
                List<Thing> carried = new List<Thing>();
                if (inner.equipment != null) carried.AddRange(inner.equipment.AllEquipmentListForReading);
                if (inner.apparel != null) carried.AddRange(inner.apparel.WornApparel);
                if (inner.inventory != null) carried.AddRange(inner.inventory.innerContainer);
                foreach (Thing c in carried)
                {
                    if (!HoldsMetal(c)) continue;
                    c.holdingOwner?.Remove(c);
                    if (gut.TryAdd(c, canMergeWithExistingStacks: false)) kept++;
                }
                food.Destroy(DestroyMode.Vanish);
                return kept;
            }
            if (HoldsMetal(food))
            {
                if (food.Spawned) food.DeSpawn();
                else food.holdingOwner?.Remove(food);
                if (gut.TryAdd(food, canMergeWithExistingStacks: false)) kept++;
                return kept;
            }
            food.Destroy(DestroyMode.Vanish);
            return 0;
        }

        // ── castings ────────────────────────────────────────────────────

        public Thing PassCasting()
        {
            Pawn p = Pawn;
            if (p == null || gut.Count == 0) return null;
            Map map = p.MapHeld;
            IntVec3 at = p.PositionHeld;
            Thing casting = MakeCasting();
            ticksDigesting = 0;
            if (casting == null || map == null) return null;
            GenPlace.TryPlaceThing(casting, at, map, ThingPlaceMode.Near);
            return casting;
        }

        private Thing MakeCasting()
        {
            Thing casting = ThingMaker.MakeThing(RM_HwelgrueDefOf.RM_SheenCasting);
            RM_CompSheenCasting held = casting.TryGetComp<RM_CompSheenCasting>();
            if (held == null) return null;
            gut.TryTransferAllToContainer(held.GetDirectlyHeldThings(), canMergeWithExistingStacks: false);
            return casting;
        }

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);
            if (gut.Count == 0 || prevMap == null) return;
            Thing casting = MakeCasting();
            if (casting != null) GenPlace.TryPlaceThing(casting, parent.PositionHeld, prevMap, ThingPlaceMode.Near);
        }

        // ── temper ──────────────────────────────────────────────────────

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            Pawn p = Pawn;
            if (p == null || p.Dead || p.Downed || !p.Spawned) return;
            if (!(dinfo.Instigator is Thing attacker) || attacker == p || attacker.Destroyed || !attacker.Spawned || attacker.Map != p.Map) return;
            if (p.CurJobDef == JobDefOf.AttackMelee && p.CurJob.targetA.Thing == attacker) return;
            Job job = JobMaker.MakeJob(JobDefOf.AttackMelee, attacker);
            job.expiryInterval = 2500;
            job.checkOverrideOnExpire = true;
            job.killIncappedTarget = false;
            p.jobs.StartJob(job, JobCondition.InterruptForced);
        }

        public override string CompInspectStringExtra()
        {
            if (gut.Count == 0) return "Gut empty. It crawls toward anything left lying in the open.";
            int left = Mathf.Max(0, CastingIntervalTicks - ticksDigesting);
            return "Digesting. Something metal rattles inside (" + gut.Count + "). Next casting in " + left.ToStringTicksToPeriod() + ".";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref gut, "gut", this);
            Scribe_Values.Look(ref ticksDigesting, "ticksDigesting", 0);
            Scribe_Values.Look(ref capChecked, "capChecked", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && gut == null)
            {
                gut = new ThingOwner<Thing>(this, oneStackOnly: false);
            }
        }
    }

    /// <summary>Picks the graze target: nearest reachable corpse, rotting food or other haulable on open
    /// ground within the comp's radius. Never a casting, a quest item, or anything in a stockpile zone or
    /// under a roof.</summary>
    public class RM_JobGiver_GutGraze : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (pawn.def != RM_HwelgrueDefOf.RM_Hwelgrue) return null;
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.hwelgrue) return null;
            RM_CompGutDigest comp = pawn.TryGetComp<RM_CompGutDigest>();
            if (comp == null || pawn.Downed || pawn.InMentalState) return null;
            Thing target = FindFood(pawn, comp.Props.grazeRadius);
            if (target == null) return null;
            Job job = JobMaker.MakeJob(RM_HwelgrueDefOf.RM_GutGraze, target);
            job.expiryInterval = 6000;
            return job;
        }

        public static bool Edible(Thing t, Pawn pawn)
        {
            if (t == null || !t.Spawned || t.Destroyed || t is Pawn) return false;
            if (t.def == RM_HwelgrueDefOf.RM_SheenCasting) return false;
            if (!t.questTags.NullOrEmpty()) return false;
            if (!t.def.EverHaulable && !(t is Corpse)) return false;
            if (t is Corpse c && c.InnerPawn?.def == RM_HwelgrueDefOf.RM_Hwelgrue) return false;
            Map map = t.Map;
            if (t.Position.Roofed(map)) return false;
            if (map.zoneManager.ZoneAt(t.Position) is Zone_Stockpile) return false;
            return pawn == null || pawn.CanReserve(t);
        }

        public static Thing FindFood(Pawn pawn, float radius)
        {
            return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
                PathEndMode.Touch, TraverseParms.For(pawn), radius, t => Edible(t, pawn));
        }
    }

    /// <summary>Crawl to it, work the dredge mouth over it, eat it.</summary>
    public class RM_JobDriver_GutGraze : JobDriver
    {
        private const int EatTicks = 300;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil chew = Toils_General.Wait(EatTicks, TargetIndex.A);
            chew.WithProgressBarToilDelay(TargetIndex.A);
            yield return chew;
            Toil eat = ToilMaker.MakeToil("RM_GutGraze_Eat");
            eat.initAction = delegate
            {
                Thing food = job.targetA.Thing;
                if (food != null && food.Spawned)
                {
                    pawn.TryGetComp<RM_CompGutDigest>()?.Digest(food);
                }
            };
            eat.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return eat;
        }
    }

    public class CompProperties_RM_SheenCasting : CompProperties
    {
        public CompProperties_RM_SheenCasting()
        {
            compClass = typeof(RM_CompSheenCasting);
        }
    }

    /// <summary>The casting's contents. Opening (vanilla CompUsable -> <see cref="RM_CompUseEffect_CrackCasting"/>)
    /// drops them polished: hit points to full, quality untouched.</summary>
    public class RM_CompSheenCasting : ThingComp, IThingHolder
    {
        private ThingOwner<Thing> contents;

        public RM_CompSheenCasting()
        {
            contents = new ThingOwner<Thing>(this, oneStackOnly: false);
        }

        public IThingHolder ParentHolder => parent.ParentHolder;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public ThingOwner GetDirectlyHeldThings() => contents;

        public List<Thing> Open(IntVec3 at, Map map)
        {
            List<Thing> dropped = new List<Thing>();
            foreach (Thing t in contents.ToList())
            {
                if (t.def.useHitPoints) t.HitPoints = t.MaxHitPoints;
                if (contents.TryDrop(t, at, map, ThingPlaceMode.Near, out Thing placed) && placed != null)
                {
                    dropped.Add(placed);
                }
            }
            return dropped;
        }

        public override string CompInspectStringExtra()
        {
            if (contents.Count == 0) return "Empty.";
            StringBuilder sb = new StringBuilder("Holds: ");
            sb.Append(string.Join(", ", contents.Take(4).Select(t => t.LabelShort)));
            if (contents.Count > 4) sb.Append(" and " + (contents.Count - 4) + " more");
            return sb.ToString();
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            // A casting smashed or burned, not opened: its metal is not lost, only unpolished.
            if (previousMap != null && contents.Count > 0)
            {
                contents.TryDropAll(parent.Position, previousMap, ThingPlaceMode.Near);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref contents, "contents", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && contents == null)
            {
                contents = new ThingOwner<Thing>(this, oneStackOnly: false);
            }
        }
    }

    public class RM_CompUseEffect_CrackCasting : CompUseEffect
    {
        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);
            RM_CompSheenCasting held = parent.TryGetComp<RM_CompSheenCasting>();
            Map map = parent.MapHeld;
            IntVec3 at = parent.PositionHeld;
            if (held != null && map != null)
            {
                List<Thing> dropped = held.Open(at, map);
                if (dropped.Count > 0)
                {
                    Messages.Message("The casting cracks open: " + string.Join(", ", dropped.Select(t => t.LabelShort)) + ", polished bright.",
                        new LookTargets(dropped), MessageTypeDefOf.PositiveEvent, false);
                }
            }
            parent.Destroy(DestroyMode.Vanish);
        }
    }

    /// <summary>Per-map memory: the first-sighting letter is sent once per map.</summary>
    public class RM_MapComponent_Hwelgrue : MapComponent
    {
        private bool lettered;

        public RM_MapComponent_Hwelgrue(Map map) : base(map)
        {
        }

        public static RM_MapComponent_Hwelgrue Get(Map map) => map?.GetComponent<RM_MapComponent_Hwelgrue>();

        public void NotifySeen(Pawn p)
        {
            if (lettered || !map.IsPlayerHome) return;
            lettered = true;
            Find.LetterStack.ReceiveLetter("A hwelgrue",
                "Something the size of a hauler is crawling across the Rot: a bone-white maggot, lilac underneath, every inch of it "
              + "wriggling with feeding tendrils and dotted with dark eye spots.\n\nIt eats whatever lies on open ground and keeps "
              + "only the metal, which it passes days later in glossy Sheen castings. It will not start a fight. It will finish one.",
                LetterDefOf.NeutralEvent, p);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lettered, "lettered", false);
        }
    }

    /// <summary>Deterministic reads/triggers for jawa/static_call (THE_ROT_FIRST_SCRIPT_1).</summary>
    public static class RM_HwelgrueProof
    {
        private static Pawn First(Map map) => map?.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.def == RM_HwelgrueDefOf.RM_Hwelgrue && !p.Dead);

        /// <summary>Spawns <paramref name="count"/> wild hwelgrue near the centre of the current map, runs
        /// each one's cap check, and reports how many remain. "HWELGRUE alive n".</summary>
        public static string ProofSpawn(int count)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no map";
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Hwelgrue");
            if (kind == null) return "REFUSED: no PawnKindDef RM_Hwelgrue";
            for (int i = 0; i < count; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(map.Center, map, 10), map);
                if (RM_CompGutDigest.OverCap(p)) p.Destroy(DestroyMode.Vanish);
            }
            return "HWELGRUE alive " + map.mapPawns.AllPawnsSpawned.Count(p => p.def == RM_HwelgrueDefOf.RM_Hwelgrue && !p.Dead);
        }

        /// <summary>Feeds the first hwelgrue on the current map a steel item made in place and a corpse-less
        /// non-metal (a wood log stack), then reports the gut. "GUT n | first DEF".</summary>
        public static string ProofDigest()
        {
            Pawn p = First(Find.CurrentMap);
            RM_CompGutDigest comp = p?.TryGetComp<RM_CompGutDigest>();
            if (comp == null) return "REFUSED: no hwelgrue on the current map";
            Thing knife = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamedSilentFail("MeleeWeapon_Knife") ?? ThingDefOf.Steel,
                DefDatabase<ThingDef>.GetNamedSilentFail("MeleeWeapon_Knife") != null ? ThingDefOf.Steel : null);
            Thing wood = ThingMaker.MakeThing(ThingDefOf.WoodLog);
            GenPlace.TryPlaceThing(knife, p.Position, p.Map, ThingPlaceMode.Near);
            GenPlace.TryPlaceThing(wood, p.Position, p.Map, ThingPlaceMode.Near);
            int kept = comp.Digest(knife) + comp.Digest(wood);
            return "GUT " + comp.Gut.Count + " | kept " + kept + " | wood destroyed " + wood.Destroyed + " | first " + (comp.Gut.Count > 0 ? comp.Gut[0].def.defName : "none");
        }

        /// <summary>Passes a casting now and cracks it open in place, damaging its contents first so the polish
        /// is visible. "CAST dropped n | all full hp B".</summary>
        public static string ProofCasting()
        {
            Pawn p = First(Find.CurrentMap);
            RM_CompGutDigest comp = p?.TryGetComp<RM_CompGutDigest>();
            if (comp == null) return "REFUSED: no hwelgrue on the current map";
            if (comp.Gut.Count == 0) return "REFUSED: gut empty (run ProofDigest first)";
            foreach (Thing t in comp.Gut) if (t.def.useHitPoints) t.HitPoints = Mathf.Max(1, t.MaxHitPoints / 3);
            Thing casting = comp.PassCasting();
            if (casting == null) return "REFUSED: no casting made";
            int castings = p.Map.listerThings.ThingsOfDef(RM_HwelgrueDefOf.RM_SheenCasting).Count;
            List<Thing> dropped = casting.TryGetComp<RM_CompSheenCasting>().Open(casting.Position, casting.Map);
            casting.Destroy(DestroyMode.Vanish);
            bool full = dropped.All(t => !t.def.useHitPoints || t.HitPoints == t.MaxHitPoints);
            return "CAST castings on map " + castings + " | dropped " + dropped.Count + " | all full hp " + full + " | gut now " + comp.Gut.Count;
        }

        /// <summary>The graze picker's verdict on a fresh item at an open cell vs a stockpile-zoned one is
        /// left to the live walk; this reads which thing the picker would choose now. "GRAZE def|none".</summary>
        public static string ProofGrazeTarget()
        {
            Pawn p = First(Find.CurrentMap);
            if (p == null) return "REFUSED: no hwelgrue on the current map";
            Thing t = RM_JobGiver_GutGraze.FindFood(p, 30f);
            return "GRAZE " + (t == null ? "none" : t.def.defName + " at " + t.Position);
        }
    }
}
