using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheForge
{
    // ════════════════════════════════════════════════════════════════════
    // DHOGGUR_USE_DECIDE_SNUFFLING_FOR_A_JOB — the dhoggur's chemical swell. Owner, 2026-10-16: "improve the Dhoggur to
    // take advantage of some of the old Crescendo anole concept: if you mess with it, it swells with violent chemical
    // reactions that make it three times as big and spewing fire (firespit). Stays that way for 1/3 of a day, then it
    // can't do it again for another day. Super aggressive when angered, but otherwise totally docile and placid while
    // foraging." By card: trigger = ONLY taking damage; cooldown = one day from the moment the swell ENDS; size is REAL
    // (body size, health and melee damage all x3 while swollen, sprite drawn 3x). Owner: "Needs new angry art too... it
    // should be very scary." — the swollen texture (<body texPath>_Swollen) is drawn while swollen once installed.
    //
    // The crescendo anole (AA_CrescendoAnole) was a donor (Alpha Animals) creature; none of its mechanism was ever in
    // src/, so this is new code, not a port.
    //
    //   RM_CompDhoggurSwell             the state machine (RM_SwellKernel): damage -> swell, timed end, cooldown stamp,
    //                                   manhunter while swollen (wild only), fire spit via the hediff's <abilities>.
    //   RM_Hediff_DhoggurSwell          the visible condition; its stage's MeleeDamageFactor follows the scale setting.
    //   RM_Patch_DhoggurSwell_*         Pawn.BodySize / Pawn.HealthScale x scale for swollen pawns (a static set, so
    //                                   every other pawn pays one HashSet.Count read).
    //   RM_PawnRenderNode(Worker)_Swell the body node: the swollen texture as a graphic state (only when it exists) and
    //                                   the draw scale x scale while swollen.
    // All gated by RM_TheForgeSettings.dhoggurSwellEnabled (and the master switch).
    // ════════════════════════════════════════════════════════════════════

    public class CompProperties_DhoggurSwell : CompProperties
    {
        public HediffDef swellHediff;
        public int checkIntervalTicks = 250;

        public CompProperties_DhoggurSwell()
        {
            compClass = typeof(RM_CompDhoggurSwell);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
                yield return e;
            if (swellHediff == null)
                yield return "CompProperties_DhoggurSwell has no swellHediff";
            if (parentDef.race == null)
                yield return "CompProperties_DhoggurSwell is only for pawns";
        }
    }

    public class RM_CompDhoggurSwell : ThingComp
    {
        private SwellState state = new SwellState { swellEndTick = -1, cooldownUntilTick = 0 };

        public CompProperties_DhoggurSwell Props => (CompProperties_DhoggurSwell)props;
        private Pawn Pawn => parent as Pawn;
        public bool Swollen => RM_SwellKernel.Swollen(state);
        public static bool On => RM_TheForgeSettings.Active(RM_TheForgeSettings.dhoggurSwellEnabled);

        private static int Now => Find.TickManager.TicksGame;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            EnsureAbilityTracker();
            if (Swollen)
                RM_DhoggurSwellRegistry.Set(Pawn, true);
        }

        // Animals get no Pawn_AbilityTracker (RaceProperties.ShouldHaveAbilityTracker); the hediff's <abilities> need one.
        private void EnsureAbilityTracker()
        {
            Pawn p = Pawn;
            if (p != null && p.abilities == null)
                p.abilities = new Pawn_AbilityTracker(p);
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            Pawn p = Pawn;
            if (p == null || !p.Spawned)
                return;
            if (!RM_SwellKernel.CanSwell(state, On, p.Dead, totalDamageDealt, Now))
                return;
            BeginSwell(dinfo.Instigator);
        }

        public void BeginSwell(Thing instigator)
        {
            Pawn p = Pawn;
            EnsureAbilityTracker();
            RM_SwellKernel.Begin(ref state, Now, RM_SwellKernel.DurationTicks(RM_TheForgeSettings.dhoggurSwellHours));
            RM_DhoggurSwellRegistry.Set(p, true);
            if (!p.health.hediffSet.HasHediff(Props.swellHediff))
                p.health.AddHediff(Props.swellHediff);
            p.abilities?.Notify_TemporaryAbilitiesChanged();
            Enrage(p, instigator);
            Burst(p, 4f);
            p.Drawer?.renderer?.SetAllGraphicsDirty();
            if (p.Map == Find.CurrentMap && p.Faction == null)
                Messages.Message("The dhoggur swells with a violent chemical reaction!", p, MessageTypeDefOf.ThreatSmall, false);
        }

        public void EndSwell()
        {
            Pawn p = Pawn;
            RM_SwellKernel.End(ref state, Now, RM_SwellKernel.CooldownTicks(RM_TheForgeSettings.dhoggurCooldownDays));
            RM_DhoggurSwellRegistry.Set(p, false);
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Props.swellHediff);
            if (h != null)
                p.health.RemoveHediff(h);
            p.abilities?.Notify_TemporaryAbilitiesChanged();
            if (p.MentalStateDef == MentalStateDefOf.Manhunter)
                p.MentalState.RecoverFromState();
            if (p.Spawned)
            {
                Burst(p, 1.5f);
                p.Drawer?.renderer?.SetAllGraphicsDirty();
            }
        }

        // "Super aggressive when angered": a wild dhoggur goes manhunter for the swell (a tamed one keeps its owner).
        private static void Enrage(Pawn p, Thing instigator)
        {
            if (!RM_TheForgeSettings.dhoggurSwellManhunts || p.Faction != null || p.Dead || p.Downed)
                return;
            if (p.InAggroMentalState)
                return;
            p.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, "swelling with chemical fury",
                forced: true, forceWake: true, causedByDamage: true);
        }

        private static void Burst(Pawn p, float scale)
        {
            if (!p.Spawned)
                return;
            Vector3 at = p.DrawPos;
            FleckMaker.ThrowFireGlow(at, p.Map, scale);
            FleckMaker.ThrowSmoke(at, p.Map, scale);
            FleckMaker.ThrowMicroSparks(at, p.Map);
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!Swollen || !parent.Spawned || !parent.IsHashIntervalTick(Props.checkIntervalTicks))
                return;
            Pawn p = Pawn;
            if (p.Dead || RM_SwellKernel.ShouldEnd(state, On, Now))
            {
                EndSwell();
                return;
            }
            Enrage(p, null);
            if (Rand.Chance(0.5f))
            {
                FleckMaker.ThrowSmoke(p.DrawPos, p.Map, 1.2f);
                FleckMaker.ThrowMicroSparks(p.DrawPos, p.Map);
            }
        }

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);
            RM_DhoggurSwellRegistry.Set(Pawn, false);
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            RM_DhoggurSwellRegistry.Set(Pawn, false);
        }

        public override string CompInspectStringExtra()
        {
            if (!On)
                return null;
            int now = Now;
            if (Swollen)
                return "Swollen with chemical fury: " + RM_SwellKernel.TicksLeft(state, now).ToStringTicksToPeriod() + " left.";
            int cd = RM_SwellKernel.CooldownLeft(state, now);
            return cd > 0 ? "Spent: cannot swell again for " + cd.ToStringTicksToPeriod() + "." : null;
        }

        // [RMTheForgeDebug] line read by validation.py (dhoggur_swell chain).
        public string DebugStateReport()
        {
            Pawn p = Pawn;
            int now = Now;
            bool fire = false;
            if (p.abilities != null)
                foreach (Ability a in p.abilities.AllAbilitiesForReading)
                    if (a.def.defName == "RM_FireSpit") fire = true;
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Props.swellHediff);
            float dmg = p.GetStatValue(StatDefOf.MeleeDamageFactor);
            return "dhoggur id=" + p.ThingID + " swollen=" + Swollen + " hediff=" + (h != null) + " ticksLeft=" + RM_SwellKernel.TicksLeft(state, now)
                + " cooldownLeft=" + RM_SwellKernel.CooldownLeft(state, now) + " bodySize=" + p.BodySize.ToString("0.###")
                + " healthScale=" + p.HealthScale.ToString("0.###") + " meleeFactor=" + dmg.ToString("0.###")
                + " fireSpit=" + fire + " manhunter=" + (p.MentalStateDef == MentalStateDefOf.Manhunter)
                + " drawScale=" + RM_DhoggurSwellRegistry.ScaleOf(p).ToString("0.###") + " swollenArt=" + RM_PawnRenderNode_SwellBody.LastArtFound;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref state.swellEndTick, "rmSwellEndTick", -1);
            Scribe_Values.Look(ref state.cooldownUntilTick, "rmSwellCooldownUntil", 0);
        }
    }

    // Which pawns are swollen right now. Main thread only (ticks and the draw pre-pass never overlap).
    public static class RM_DhoggurSwellRegistry
    {
        private static readonly HashSet<Pawn> swollen = new HashSet<Pawn>();

        public static void Set(Pawn p, bool on)
        {
            if (p == null) return;
            if (on) swollen.Add(p); else swollen.Remove(p);
        }

        public static bool Has(Pawn p) { return swollen.Count > 0 && swollen.Contains(p); }

        public static float ScaleOf(Pawn p)
        {
            return RM_SwellKernel.Scale(Has(p) && RM_CompDhoggurSwell.On, RM_TheForgeSettings.dhoggurSwellScale);
        }
    }

    // The condition itself. Its one stage's MeleeDamageFactor is rebuilt from the scale setting (so tuning it works),
    // keeping every other field of the XML stage.
    public class RM_Hediff_DhoggurSwell : HediffWithComps
    {
        private static HediffStage cached;
        private static float cachedScale = -1f;
        private static HediffDef cachedFor;

        public override HediffStage CurStage
        {
            get
            {
                HediffStage xml = base.CurStage;
                if (xml == null)
                    return null;
                float s = RM_SwellKernel.Scale(true, RM_TheForgeSettings.dhoggurSwellScale);
                if (cached == null || cachedScale != s || cachedFor != def)
                {
                    HediffStage st = new HediffStage();
                    foreach (var f in typeof(HediffStage).GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance))
                        f.SetValue(st, f.GetValue(xml));
                    st.statFactors = new List<StatModifier>();
                    if (xml.statFactors != null)
                        foreach (StatModifier m in xml.statFactors)
                            if (m.stat != StatDefOf.MeleeDamageFactor) st.statFactors.Add(m);
                    st.statFactors.Add(new StatModifier { stat = StatDefOf.MeleeDamageFactor, value = s });
                    cached = st;
                    cachedScale = s;
                    cachedFor = def;
                }
                return cached;
            }
        }
    }

    [HarmonyPatch(typeof(Pawn), nameof(Pawn.BodySize), MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Dhoggur swell size", typeof(RM_TheForgeSettings), "dhoggurSwellEnabled")]
    public static class RM_Patch_DhoggurSwell_BodySize
    {
        public static void Postfix(Pawn __instance, ref float __result)
        {
            if (RM_DhoggurSwellRegistry.Has(__instance))
                __result *= RM_DhoggurSwellRegistry.ScaleOf(__instance);
        }
    }

    [HarmonyPatch(typeof(Pawn), nameof(Pawn.HealthScale), MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Dhoggur swell health", typeof(RM_TheForgeSettings), "dhoggurSwellEnabled")]
    public static class RM_Patch_DhoggurSwell_HealthScale
    {
        public static void Postfix(Pawn __instance, ref float __result)
        {
            if (RM_DhoggurSwellRegistry.Has(__instance))
                __result *= RM_DhoggurSwellRegistry.ScaleOf(__instance);
        }
    }

    // ── the look ─────────────────────────────────────────────────────────
    // Same pattern as the Miasma lastvine's rearing body (RM_LastvineRearing.cs): the vanilla animal body node plus one
    // extra graphic state built from the life stage's texPath + suffix, only when that texture exists.

    public class RM_PawnRenderNodeProperties_Swell : PawnRenderNodeProperties
    {
        public string swollenSuffix = "_Swollen";

        public RM_PawnRenderNodeProperties_Swell()
        {
            nodeClass = typeof(RM_PawnRenderNode_SwellBody);
            workerClass = typeof(RM_PawnRenderNodeWorker_SwellBody);
        }
    }

    [DefOf]
    public static class RM_ForgeGraphicStateDefOf
    {
        public static GraphicStateDef RM_DhoggurSwollen;

        static RM_ForgeGraphicStateDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ForgeGraphicStateDefOf));
        }
    }

    public class RM_PawnRenderNode_SwellBody : PawnRenderNode_AnimalPart_Body
    {
        private static readonly Dictionary<string, bool> textureExists = new Dictionary<string, bool>();
        public static bool LastArtFound;

        public RM_PawnRenderNode_SwellBody(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
            : base(pawn, props, tree)
        {
        }

        protected override IEnumerable<(GraphicStateDef state, Graphic graphic)> StateGraphicsFor(Pawn pawn)
        {
            foreach (var item in base.StateGraphicsFor(pawn))
                yield return item;
            Graphic g = SwollenGraphic(pawn);
            if (g != null)
                yield return (RM_ForgeGraphicStateDefOf.RM_DhoggurSwollen, g);
        }

        private Graphic SwollenGraphic(Pawn pawn)
        {
            GraphicData data = pawn.ageTracker?.CurKindLifeStage?.bodyGraphicData;
            var p = props as RM_PawnRenderNodeProperties_Swell;
            if (data == null || p == null || data.texPath.NullOrEmpty())
                return null;
            string path = data.texPath + p.swollenSuffix;
            if (!textureExists.TryGetValue(path, out bool exists))
            {
                exists = ContentFinder<Texture2D>.Get(path + "_south", false) != null;
                textureExists[path] = exists;
            }
            LastArtFound = exists;
            if (!exists)
                return null;
            Graphic calm = data.Graphic;
            Color c1 = pawn.health.hediffSet.GetSkinColor(calm.Color);
            Color c2 = pawn.health.hediffSet.GetSkinColor(calm.ColorTwo);
            return GraphicDatabase.Get<Graphic_Multi>(path, calm.Shader, calm.drawSize, c1, c2);
        }
    }

    public class RM_PawnRenderNodeWorker_SwellBody : PawnRenderNodeWorker_AnimalBody
    {
        protected override GraphicStateDef GetGraphicState(PawnRenderNode node, PawnDrawParms parms)
        {
            GraphicStateDef s = RM_ForgeGraphicStateDefOf.RM_DhoggurSwollen;
            if (node.tree.currentAnimation == null && parms.rotDrawMode == RotDrawMode.Fresh
                && RM_DhoggurSwellRegistry.Has(parms.pawn) && RM_CompDhoggurSwell.On && node.ContainsGraphicState(s))
                return s;
            return base.GetGraphicState(node, parms);
        }

        public override Vector3 ScaleFor(PawnRenderNode node, PawnDrawParms parms)
        {
            Vector3 v = base.ScaleFor(node, parms);
            float k = RM_DhoggurSwellRegistry.ScaleOf(parms.pawn);
            return k == 1f ? v : v * k;
        }
    }
}
