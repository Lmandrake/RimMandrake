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
        public static FleckDef RM_KnockbackBlastSmoke;

        static RM_KnockbackShowDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_KnockbackShowDefOf));
        }
    }

    public static class RM_KnockbackShow
    {
        private static readonly AccessTools.FieldRef<Filth, int> DisappearAfterTicks =
            AccessTools.FieldRefAccess<Filth, int>("disappearAfterTicks");
        // the cells the blast reaches (DamageWorker.ExplosionCellsToHit, filled by StartExplosion before our postfix): soot
        // lies only where the blast did reach, never behind a wall it stopped at (guiding principle 4)
        private static readonly AccessTools.FieldRef<Explosion, System.Collections.Generic.List<IntVec3>> CellsToAffect =
            AccessTools.FieldRefAccess<Explosion, System.Collections.Generic.List<IntVec3>>("cellsToAffect");

        /// <summary>Smoke puffs started in the last SmokeWindowTicks, and the window's start: a barrage's smoke is capped,
        /// so many blasts in a second cannot pile up hundreds of the costliest flecks (design §3.8, "capped per view";
        /// bar barrage_frame_budget). The cap is three blasts' worth of the plan's own per-blast maximum (30 puffs).</summary>
        private const int SmokeWindowTicks = 60;
        private const int SmokeCapPerWindow = 3 * 30;
        private static int smokeWindowStart = -1, smokeInWindow;

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
                smoke = RimMandrakeExplosiveKnockbackSettings.showSmoke,
                sootOnThings = RimMandrakeExplosiveKnockbackSettings.showSootOnThings,
                sootOnPawns = RimMandrakeExplosiveKnockbackSettings.showSootOnPawns,
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

            if (p.smokePuffs > 0)
            {
                DrawSmoke(e, map, p);
            }

            if (p.scarKind != KbScarKind.None)
            {
                LayScar(e.Position, map, p);
            }

            if (p.sootThingsReach > 0f || p.sootPawnsReach > 0f)
            {
                LaySoot(e, map, p);
            }
        }

        /// <summary>Smoke (design §3.8): non-rotating puffs that rise from the root, lean with the wind and thin over the
        /// plan's smokeSeconds; the first puffs are the darkest (the boiling base), later ones paler. The spread, speeds
        /// and tints are the look: the live scene sc_blast_show's and the art judge's to read.</summary>
        private static void DrawSmoke(Explosion e, Map map, KbShowPlan p)
        {
            FleckDef def = RM_KnockbackShowDefOf.RM_KnockbackBlastSmoke;
            int now = Find.TickManager.TicksGame;
            if (smokeWindowStart < 0 || now - smokeWindowStart >= SmokeWindowTicks || now < smokeWindowStart)
            {
                smokeWindowStart = now;
                smokeInWindow = 0;
            }
            int puffs = Mathf.Min(p.smokePuffs, SmokeCapPerWindow - smokeInWindow);
            if (puffs <= 0)
            {
                return;
            }
            smokeInWindow += puffs;
            Vector3 root = e.Position.ToVector3Shifted();
            float wind = Mathf.Clamp01(map.windManager.WindSpeed / 2f);       // WindSpeed runs about 0 to 2
            float life = Mathf.Max(0.5f, p.smokeSeconds - def.fadeInTime - def.fadeOutTime);
            float spread = Mathf.Max(0.6f, e.radius * 0.45f);
            float size = Mathf.Sqrt(Mathf.Max(1f, p.smokeSeconds / 12f));     // a longer-lived column is a bigger one
            for (int i = 0; i < puffs; i++)
            {
                float t = puffs > 1 ? i / (float)(puffs - 1) : 0f;           // 0: the base, 1: the last, palest puff
                FleckCreationData d = FleckMaker.GetDataStatic(root + Rand.InsideUnitCircleVec3 * spread, map, def,
                    Rand.Range(1.4f, 2.4f) * size);
                d.rotation = Rand.Range(0f, 360f);
                d.rotationRate = 0f;                                          // it never spins (his words)
                d.velocityAngle = Rand.Range(-12f, 12f) + 50f * wind;         // up the screen, leaning downwind
                d.velocitySpeed = Rand.Range(0.25f, 0.55f) + 0.5f * wind;
                d.solidTimeOverride = life * Rand.Range(0.75f, 1f);
                float g = Mathf.Lerp(0.08f, 0.42f, t) + Rand.Range(-0.03f, 0.03f);
                d.instanceColor = new Color(g, g, g, Rand.Range(0.75f, 0.95f));
                map.flecks.CreateFleck(d);
            }
        }

        /// <summary>Soot (design §3.12, §3.13): on the cells the blast reaches within the plan's reach of each part.</summary>
        private static void LaySoot(Explosion e, Map map, KbShowPlan p)
        {
            System.Collections.Generic.List<IntVec3> reached = CellsToAffect(e);
            if (reached == null || reached.Count == 0)
            {
                return;
            }
            IntVec3 c0 = e.Position;
            var things = new System.Collections.Generic.List<IntVec3>();
            var pawns = new System.Collections.Generic.List<IntVec3>();
            float rt = p.sootThingsReach * p.sootThingsReach, rp = p.sootPawnsReach * p.sootPawnsReach;
            foreach (IntVec3 c in reached)
            {
                float d2 = (c - c0).LengthHorizontalSquared;
                if (d2 <= rt)
                {
                    things.Add(c);
                }
                if (d2 <= rp)
                {
                    pawns.Add(c);
                }
            }
            if (things.Count > 0)
            {
                RM_KnockbackSoot.SootThings(map, things);
            }
            if (pawns.Count > 0)
            {
                RM_KnockbackSoot.SootPawns(map, pawns);
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
