using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    // The blast show (design/specs/2026-11-24-knockback-blast-show/design.md). This file reads the game and draws; every
    // decision of size, count and whether a part shows is RM_KnockbackShowPlan.Plan (Verse-free, tested offline as
    // shipped by selftest_explosiveknockback_blast_show.py). The show changes no damage, radius, cell or throw: the
    // prefix writes only doVisualEffects, screenShakeFactor and a Filth_BlastMark pre-spawn (the selftest's
    // B_VISUAL_ONLY line refuses any other write).

    [DefOf]
    public static class RM_KnockbackShowDefOf
    {
        public static FleckDef RM_KnockbackBlastFlash;
        public static FleckDef RM_KnockbackBlastFireball;
        public static FleckDef RM_KnockbackBlastSpark;
        public static FleckDef RM_KnockbackBlastDirt;
        public static FleckDef RM_KnockbackBlastStone;
        public static FleckDef RM_KnockbackBlastRipple;

        static RM_KnockbackShowDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_KnockbackShowDefOf));
        }
    }

    public static class RM_KnockbackShow
    {
        private static readonly AccessTools.FieldRef<Filth, int> DisappearAfterTicks =
            AccessTools.FieldRefAccess<Filth, int>("disappearAfterTicks");

        /// <summary>The last kick the show added to the camera shaker, and its tick: a public static a live scene reads with
        /// jawa/mod_settings_field get (sc_blast_show's V_SHAKE). Written only by Draw.</summary>
        public static float lastShakeKick;
        public static int lastShakeTick = -1;

        /// <summary>How long scars last, by the "How long scars and soot last" choice: short, normal, long.</summary>
        private static readonly float[] MarksLastFactor = { 0.5f, 1f, 2f };

        public static KbShowSwitches Switches()
        {
            return new KbShowSwitches
            {
                fireAndFlash = RimMandrakeExplosiveKnockbackSettings.showFireAndFlash,
                screenShake = RimMandrakeExplosiveKnockbackSettings.showScreenShake,
                airRipple = RimMandrakeExplosiveKnockbackSettings.showAirRipple,
                craterScars = RimMandrakeExplosiveKnockbackSettings.showCraterScars,
                // the parts of the later batches (smoke, soot) have no switch yet and draw nothing yet
                smoke = false,
                sootOnThings = false,
                sootOnPawns = false,
                shakeStrength = RimMandrakeExplosiveKnockbackSettings.showShakeStrength,
                powerFromDamage = RimMandrakeExplosiveKnockbackSettings.blastPowerFromDamage,
                powerRefPercent = RimMandrakeExplosiveKnockbackSettings.blastPowerRefPercent,
            };
        }

        public static KbShowKind KindOf(DamageDef def)
        {
            if (def == null || !def.harmsHealth)
            {
                return KbShowKind.NoShow;
            }
            if (RM_Patch_DamageWorker_ExplosionKnockback.IsFire(def))
            {
                return KbShowKind.Flame;
            }
            if (def == DamageDefOf.Bomb || def.defName == "BombSuper")
            {
                return KbShowKind.Bomb;
            }
            return KbShowKind.OtherHarmful;
        }

        public static KbShowGround GroundAt(IntVec3 c, Map map)
        {
            TerrainDef t = c.InBounds(map) ? c.GetTerrain(map) : null;
            if (t == null)
            {
                return KbShowGround.Soil;
            }
            if (t.IsWater)
            {
                return KbShowGround.Water;
            }
            if (t.layerable || t.IsFloor)
            {
                return KbShowGround.Floor;
            }
            if (t.IsSoil)
            {
                return KbShowGround.Soil;
            }
            // natural rock, rough or smoothed: a smoothed stone floor has no smoothedTerrain of its own and is not soil
            return t.natural && (t.smoothedTerrain != null || t.defName.IndexOf("Smooth", StringComparison.Ordinal) >= 0)
                ? KbShowGround.Stone : KbShowGround.Soil;
        }

        public static KbShowBlast BlastOf(Explosion e)
        {
            Map map = e.Map;
            bool onCurrent = map != null && map == Find.CurrentMap;
            KbShowBlast b = new KbShowBlast
            {
                // a caller that turned visual effects off (a quiet explosion) gets no show at all
                kind = e.doVisualEffects ? KindOf(e.damType) : KbShowKind.NoShow,
                ground = map != null ? GroundAt(e.Position, map) : KbShowGround.Soil,
                radius = e.radius,
                damage = e.damAmount,
                refDamage = RM_Patch_DamageWorker_ExplosionKnockback.RefDamageOf(e.damType),
                screenShakeFactor = e.screenShakeFactor,
                onCurrentMap = onCurrent,
            };
            if (onCurrent)
            {
                CameraDriver cam = Find.CameraDriver;
                IntVec3 centre = cam.MapPosition;
                b.cameraDistance = Mathf.Sqrt((centre.x - e.Position.x) * (centre.x - e.Position.x)
                                              + (centre.z - e.Position.z) * (centre.z - e.Position.z));
                b.inView = cam.CurrentViewRect.ExpandedBy(Mathf.CeilToInt(e.radius) + 1).Contains(e.Position);
            }
            return b;
        }

        public static void Draw(Explosion e, KbShowPlan p, float vanillaShakeFactor)
        {
            Map map = e.Map;
            if (map == null)
            {
                return;
            }
            Vector3 pos = e.Position.ToVector3Shifted();
            bool current = map == Find.CurrentMap;

            if (p.replayWaterSplash)
            {
                FleckMaker.WaterSplash(pos, map, e.radius * 6f, 20f);     // vanilla's own call (Explosion.StartExplosion)
            }
            if (current && p.replayVanillaShake)
            {
                float d = (pos - Find.Camera.transform.position).magnitude;
                Find.CameraDriver.shaker.DoShake(RM_KnockbackShowPlan.VanillaShakeMag(e.radius, vanillaShakeFactor, d));
            }
            if (current && p.shakeMag > 0f)
            {
                CameraShaker shaker = Find.CameraDriver.shaker;
                shaker.DoShake(RM_KnockbackShowPlan.ShakeToAdd(shaker.CurShakeMag, p.shakeMag));
                lastShakeKick = p.shakeMag;
                lastShakeTick = Find.TickManager.TicksGame;
                if (p.shakeHoldTicks > 0)
                {
                    shaker.DoShake(p.shakeMag * 0.5f, p.shakeHoldTicks);
                }
            }

            if (p.flashScale > 0f)
            {
                FleckMaker.Static(pos, map, RM_KnockbackShowDefOf.RM_KnockbackBlastFlash, p.flashScale);
            }
            for (int i = 0; i < p.fireballLobes; i++)
            {
                Vector3 off = Rand.InsideUnitCircleVec3 * (p.fireballScale * 0.35f);
                FleckCreationData d = FleckMaker.GetDataStatic(pos + off, map, RM_KnockbackShowDefOf.RM_KnockbackBlastFireball,
                    p.fireballScale * Rand.Range(0.75f, 1.15f));
                d.rotation = Rand.Range(0f, 360f);
                map.flecks.CreateFleck(d);
            }
            for (int i = 0; i < p.sparks; i++)
            {
                FleckCreationData d = FleckMaker.GetDataStatic(pos, map, RM_KnockbackShowDefOf.RM_KnockbackBlastSpark, Rand.Range(0.6f, 1f));
                d.velocityAngle = Rand.Range(0f, 360f);
                d.rotation = d.velocityAngle;           // a streak points the way it flies
                d.velocitySpeed = Rand.Range(5f, 12f);
                d.airTimeLeft = Rand.Range(0.3f, 0.8f);
                map.flecks.CreateFleck(d);
            }
            FleckDef bit = p.debrisIsStone ? RM_KnockbackShowDefOf.RM_KnockbackBlastStone : RM_KnockbackShowDefOf.RM_KnockbackBlastDirt;
            for (int i = 0; i < p.debris; i++)
            {
                FleckCreationData d = FleckMaker.GetDataStatic(pos, map, bit, Rand.Range(0.5f, 0.9f));
                d.velocityAngle = Rand.Range(0f, 360f);
                d.velocitySpeed = Rand.Range(2f, 7f);
                d.rotationRate = Rand.Range(-240f, 240f);
                d.airTimeLeft = Rand.Range(0.25f, 0.6f);
                map.flecks.CreateFleck(d);
            }

            if (p.rippleDiameter > 0f)
            {
                FleckDef rip = RM_KnockbackShowDefOf.RM_KnockbackBlastRipple;
                FleckCreationData d = FleckMaker.GetDataStatic(pos, map, rip, 0.1f);
                // the ring grows at the def's fixed rate: its life (solid + fade) sets its width (RM_KnockbackShowPlan)
                d.solidTimeOverride = Mathf.Max(0f, p.rippleSeconds - rip.fadeOutTime);
                d.instanceColor = new Color(1f, 1f, 1f, p.rippleAlpha);
                map.flecks.CreateFleck(d);
            }

            if (p.scarKind != KbScarKind.None)
            {
                LayScar(e.Position, map, p);
            }
        }

        public static string ScarDefName(KbScarKind kind, int sizeClass)
        {
            float w = RM_KnockbackShowPlan.ScarDrawSizes[Mathf.Clamp(sizeClass, 0, RM_KnockbackShowPlan.ScarDrawSizes.Length - 1)];
            return "RM_KnockbackBlast" + (kind == KbScarKind.Scorch ? "Scorch" : "Crater") + "_" + w.ToString("0");
        }

        private static void LayScar(IntVec3 c, Map map, KbShowPlan p)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(ScarDefName(p.scarKind, p.scarSizeClass));
            if (def == null || !c.InBounds(map))
            {
                return;
            }
            if (!FilthMaker.TryMakeFilth(c, map, def, 1, FilthSourceFlags.None, false))
            {
                return;
            }
            int choice = Mathf.Clamp(RimMandrakeExplosiveKnockbackSettings.showMarksLast, 0, MarksLastFactor.Length - 1);
            if (map.thingGrid.ThingAt(c, def) is Filth f && choice != 1)
            {
                DisappearAfterTicks(f) = (int)(DisappearAfterTicks(f) * MarksLastFactor[choice]);
            }
        }
    }

    /// <summary>The hook of the blast show (design §2): a prefix and a postfix on Explosion.StartExplosion, apart from the
    /// knockback hook on DamageWorker.ExplosionDamageThing. The prefix hands the vanilla visuals over before
    /// DamageWorker.ExplosionStart reads them; the postfix draws the show once the blast's cells are known.</summary>
    [HarmonyPatch(typeof(Explosion), nameof(Explosion.StartExplosion))]
    [RimMandrake.Shared.PatchFeature("Blast show")]
    public static class RM_Patch_Explosion_BlastShow
    {
        public struct State
        {
            public KbShowPlan plan;
            public float shakeFactor;
        }

        public static void Prefix(Explosion __instance, out State __state)
        {
            __state = default;
            try
            {
                KbShowPlan p = RM_KnockbackShowPlan.Plan(RM_KnockbackShow.BlastOf(__instance), RM_KnockbackShow.Switches());
                __state.plan = p;
                __state.shakeFactor = __instance.screenShakeFactor;
                if (!p.show)
                {
                    return;
                }
                if (p.suppressVanillaVisuals)
                {
                    __instance.doVisualEffects = false;
                }
                if (p.zeroVanillaShake)
                {
                    __instance.screenShakeFactor = 0f;
                }
                if (p.suppressVanillaBlastMark && __instance.preExplosionSpawnSingleThingDef == ThingDefOf.Filth_BlastMark)
                {
                    __instance.preExplosionSpawnSingleThingDef = null;
                }
            }
            catch (Exception ex)
            {
                __state = default;
                Log.ErrorOnce("[Explosive Knockback] blast show prefix failed; this blast keeps its vanilla look: " + ex, 0x4B5348);
            }
        }

        public static void Postfix(Explosion __instance, State __state)
        {
            if (!__state.plan.show)
            {
                return;
            }
            try
            {
                RM_KnockbackShow.Draw(__instance, __state.plan, __state.shakeFactor);
            }
            catch (Exception ex)
            {
                Log.ErrorOnce("[Explosive Knockback] blast show draw failed: " + ex, 0x4B5349);
            }
        }
    }
}
