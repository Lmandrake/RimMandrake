using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TheSump
{
    // ════════════════════════════════════════════════════════════════════
    // SUMP_KETHREL_BUILD_1 - the kethrel's scrap shell.
    //
    // A boneless tar animal that picks up loose rigid things near tar and wears them. Load (kg of carried
    // stacks) maps to four stages: bare, light shell, heavy shell, full carapace. The stage drives the
    // RM_KethrelShell hediff (armour up, speed down) and the body sprite set (RM_PawnRenderNode_KethrelBody,
    // no Harmony). Every carried object is a real Thing in a ThingOwner on this comp, shown on the Shell
    // inspect tab, and dropped on molt, death or leaving the map. Nothing is destroyed.
    // Rare tick only (250 ticks): the comp never needs a per-tick hook.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_KethrelShell : CompProperties
    {
        // Cells around the animal in which it will pick a thing up.
        public int pickupRadius = 3;
        // Cells in which an idle animal will walk to a thing it wants.
        public int seekRadius = 14;
        // Cells around the animal that must hold tar for it to bind a shell.
        public int tarRadius = 2;
        // Carried kilograms at which the shell steps up to stages 1, 2 and 3.
        public List<float> stageLoadKg = new List<float> { 3f, 10f, 22f };
        // Besides any weapon: loose scrap it will wear.
        public List<ThingDef> pickupDefs = new List<ThingDef>();

        public RM_CompProperties_KethrelShell()
        {
            compClass = typeof(RM_CompKethrelShell);
        }
    }

    public class RM_CompKethrelShell : ThingComp, IThingHolder
    {
        private ThingOwner<Thing> carried;
        private int stage;

        public RM_CompProperties_KethrelShell Props => (RM_CompProperties_KethrelShell)props;
        public Pawn Pawn => (Pawn)parent;
        public int Stage => stage;
        public ThingOwner<Thing> Carried => carried;

        public override void Initialize(CompProperties properties)
        {
            base.Initialize(properties);
            if (carried == null)
            {
                carried = new ThingOwner<Thing>(this, false);
            }
        }

        public ThingOwner GetDirectlyHeldThings() => carried;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref carried, "kethrelShell", this);
            Scribe_Values.Look(ref stage, "kethrelStage", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && carried == null)
            {
                carried = new ThingOwner<Thing>(this, false);
            }
        }

        public float LoadKg
        {
            get
            {
                float kg = 0f;
                for (int i = 0; i < carried.Count; i++)
                {
                    kg += carried[i].GetStatValue(StatDefOf.Mass) * carried[i].stackCount;
                }
                return kg;
            }
        }

        public int StageForLoad(float kg)
        {
            return RM_KethrelKernel.StageForLoad(Props.stageLoadKg, kg);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            Pawn pawn = Pawn;
            Thing item = null, far = null;
            switch (RM_KethrelKernel.Decide(RM_TheSumpSettings.kethrelShellEnabled, pawn.Dead, pawn.Spawned, pawn.Downed, () => LoadKg,
                RM_TheSumpSettings.kethrelMoltLoadKg, TarNearby, () => (item = FindWantedItem(Props.pickupRadius)) != null, () => IsIdle(pawn),
                () => { far = FindWantedItem(Props.seekRadius); return far != null && pawn.CanReach(far, PathEndMode.Touch, Danger.Some); }))
            {
                case KethrelAction.Molt:
                    Molt(null);
                    break;
                case KethrelAction.PickUp:
                    PickUp(item);
                    break;
                case KethrelAction.Seek:
                    {
                        Job job = JobMaker.MakeJob(JobDefOf.Goto, far.Position);
                        job.expiryInterval = 900;
                        pawn.jobs.StartJob(job, JobCondition.InterruptForced);
                    }
                    break;
            }
        }

        private static bool IsIdle(Pawn pawn)
        {
            JobDef cur = pawn.CurJobDef;
            return cur == null || cur == JobDefOf.GotoWander || cur == JobDefOf.Wait_Wander || cur == JobDefOf.Wait;
        }

        private bool TarNearby()
        {
            Map map = parent.Map;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, Props.tarRadius, true))
            {
                if (c.InBounds(map) && IsTar(c, map))
                {
                    return true;
                }
            }
            return false;
        }

        // Tar is recognised by name: the Sump's own tar pockets, the poured moat and the built tar coating filth all carry "Tar".
        public static bool IsTar(IntVec3 c, Map map)
        {
            TerrainDef t = c.GetTerrain(map);
            if (t != null && RM_KethrelKernel.IsTarName(t.defName))
            {
                return true;
            }
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i].def.category == ThingCategory.Filth && RM_KethrelKernel.IsTarName(things[i].def.defName))
                {
                    return true;
                }
            }
            return false;
        }

        private bool Wanted(Thing t)
        {
            if (t == null || t.Destroyed || !t.Spawned)
            {
                return false;
            }
            return RM_KethrelKernel.Wanted(true, t.def.category == ThingCategory.Item, t.IsForbidden(Pawn), t.def.IsWeapon || Props.pickupDefs.Contains(t.def),
                t.MarketValue * t.stackCount, RM_TheSumpSettings.kethrelValueCeiling, RM_TheSumpSettings.kethrelTakeColonyProperty, parent.Map.areaManager.Home[t.Position]);
        }

        private Thing FindWantedItem(int radius)
        {
            Map map = parent.Map;
            Thing best = null;
            float bestDist = float.MaxValue;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, radius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (Wanted(things[i]))
                    {
                        float d = (things[i].Position - parent.Position).LengthHorizontalSquared;
                        if (d < bestDist)
                        {
                            bestDist = d;
                            best = things[i];
                        }
                    }
                }
            }
            return best;
        }

        public void PickUp(Thing item)
        {
            Thing piece = item.stackCount > 1 ? item.SplitOff(item.stackCount) : item;
            if (piece.Spawned)
            {
                piece.DeSpawn();
            }
            if (!carried.TryAdd(piece, true))
            {
                GenSpawn.Spawn(piece, parent.Position, parent.Map);
                return;
            }
            Refresh();
        }

        private void Refresh()
        {
            int s = StageForLoad(LoadKg);
            if (RM_KethrelKernel.StageChanged(stage, s))
            {
                stage = s;
                SetHediff(s);
                Pawn.Drawer?.renderer?.SetAllGraphicsDirty();
            }
        }

        private void SetHediff(int s)
        {
            HediffDef def = KethrelDefOf.RM_KethrelShell;
            Hediff h = Pawn.health.hediffSet.GetFirstHediffOfDef(def);
            if (s <= 0)
            {
                if (h != null)
                {
                    Pawn.health.RemoveHediff(h);
                }
                return;
            }
            if (h == null)
            {
                h = Pawn.health.AddHediff(def);
            }
            h.Severity = RM_KethrelKernel.HediffSeverity(s);
        }

        // Drops everything carried at the kethrel's feet. handler is the colonist who coaxed it, or null for a self molt.
        public int Molt(Pawn handler)
        {
            Map map = parent.MapHeld;
            int count = carried.Count;
            if (map != null && count > 0)
            {
                carried.TryDropAll(parent.PositionHeld, map, ThingPlaceMode.Near, null, null, false);
            }
            stage = 0;
            if (Pawn.health != null)
            {
                SetHediff(0);
                Pawn.Drawer?.renderer?.SetAllGraphicsDirty();
            }
            if (parent.Spawned && count > 0)
            {
                Messages.Message("RM_KethrelMoltDone".Translate(parent.LabelShort, count), parent, MessageTypeDefOf.NeutralEvent, false);
            }
            return count;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            // Death, leaving the map and any other despawn: nothing vanishes with the animal.
            if (map != null && carried != null && carried.Count > 0)
            {
                bool left = mode == DestroyMode.Vanish && !Pawn.Dead;
                carried.TryDropAll(parent.Position, map, ThingPlaceMode.Near, null, null, false);
                stage = 0;
                if (left)
                {
                    Messages.Message("RM_KethrelLeft".Translate(parent.LabelShort), new TargetInfo(parent.Position, map), MessageTypeDefOf.NeutralEvent, false);
                }
            }
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (parent.Faction == Faction.OfPlayer && carried.Count > 0)
            {
                yield return new Command_Action
                {
                    defaultLabel = "RM_KethrelMoltLabel".Translate(),
                    defaultDesc = "RM_KethrelMoltDesc".Translate(),
                    icon = TexCommand.Attack,
                    action = CoaxMolt
                };
            }
        }

        private void CoaxMolt()
        {
            var colonists = new List<Pawn>();
            var skills = new List<int>();
            var able = new List<bool>();
            foreach (Pawn p in parent.Map.mapPawns.FreeColonistsSpawned)
            {
                bool ok = !(p.Downed || p.WorkTagIsDisabled(WorkTags.Animals) || p.skills == null);
                colonists.Add(p);
                skills.Add(ok ? p.skills.GetSkill(SkillDefOf.Animals).Level : 0);
                able.Add(ok);
            }
            int pick = RM_KethrelKernel.BestHandler(skills, able);
            Pawn best = pick < 0 ? null : colonists[pick];
            int bestSkill = pick < 0 ? -1 : skills[pick];
            if (best == null)
            {
                Messages.Message("RM_KethrelMoltNoHandler".Translate(), parent, MessageTypeDefOf.RejectInput, false);
                return;
            }
            float fail = FailChance(bestSkill, RM_TheSumpSettings.kethrelHandlingDifficulty);
            Molt(best);
            if (Rand.Chance(fail))
            {
                Messages.Message("RM_KethrelMoltPanic".Translate(parent.LabelShort, best.LabelShort), parent, MessageTypeDefOf.NegativeEvent, false);
                Pawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, "kethrel panicked", true);
            }
        }

        // Chance a coaxed molt ends in a panicked charge. Pure, so the offline check can read it.
        public static float FailChance(int animalsSkill, float difficulty)
        {
            return RM_KethrelKernel.FailChance(animalsSkill, difficulty);
        }

        public override string CompInspectStringExtra()
        {
            if (carried == null || carried.Count == 0)
            {
                return null;
            }
            return "RM_KethrelShellInspect".Translate(StageLabel(stage), LoadKg.ToString("0.0"), carried.Count);
        }

        public static string StageLabel(int s)
        {
            return RM_KethrelKernel.StageLabel(s);
        }
    }

    [DefOf]
    public static class KethrelDefOf
    {
        public static HediffDef RM_KethrelShell;

        static KethrelDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(KethrelDefOf));
        }
    }

    /// <summary>Body node of the kethrel's render tree: the stage's whole-body sprite set in place of the stock one.</summary>
    public class RM_PawnRenderNode_KethrelBody : PawnRenderNode_AnimalPart_Body
    {
        public RM_PawnRenderNode_KethrelBody(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
            : base(pawn, props, tree)
        {
        }

        public override Graphic GraphicFor(Pawn pawn)
        {
            Graphic g = base.GraphicFor(pawn);
            if (g == null || pawn.Dead)
            {
                return g;
            }
            RM_CompKethrelShell comp = pawn.TryGetComp<RM_CompKethrelShell>();
            if (comp == null || comp.Stage <= 0 || pawn.Drawer.renderer.CurRotDrawMode != RotDrawMode.Fresh)
            {
                return g;
            }
            return GraphicDatabase.Get<Graphic_Multi>(StagePath(comp.Stage), g.Shader, g.drawSize, g.Color, g.ColorTwo);
        }

        public static string StagePath(int stage)
        {
            return "Things/Pawn/Animal/RM_Kethrel/RM_Kethrel_Stage" + stage;
        }
    }

    public class RM_ITab_KethrelShell : ITab_ContentsBase
    {
        public RM_ITab_KethrelShell()
        {
            labelKey = "RM_TabKethrelShell";
            containedItemsKey = "RM_KethrelShellContents";
            canRemoveThings = false;
        }

        public override IList<Thing> container
        {
            get
            {
                RM_CompKethrelShell comp = SelThing?.TryGetComp<RM_CompKethrelShell>();
                return comp != null ? (IList<Thing>)comp.Carried.InnerListForReading : new List<Thing>();
            }
        }

        public override bool IsVisible
        {
            get
            {
                RM_CompKethrelShell comp = SelThing?.TryGetComp<RM_CompKethrelShell>();
                return comp != null && comp.Carried.Count > 0;
            }
        }
    }
}
