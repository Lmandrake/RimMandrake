using System;

namespace RimMandrake.ExplosiveKnockback
{
    // The pure kernel of the blast show (design/specs/2026-11-24-knockback-blast-show/design.md §2 to §5). Verse-free on
    // purpose: Source/SelfTestShow compiles THIS file with RM_KnockbackMath.cs, so the decision of how big each part of
    // the show is, and whether it shows at all, is tested as shipped. RM_KnockbackShow.cs only reads the game, calls
    // Plan() and draws what it returns. A `using Verse;` here breaks the selftest build.

    /// <summary>What kind of blast this is for the show (design §2). Bomb-like types get every part; Flame gets fire,
    /// smoke, scorch and soot with no thrown dirt and no crater; another mod's harmful type keeps its own cell flecks and
    /// gains shake, ripple, smoke, scar and soot; a type that harms nobody (Stun, EMP, Smoke, Extinguish) keeps its
    /// vanilla look in 0.2.0.</summary>
    public enum KbShowKind : byte { NoShow = 0, Bomb = 1, Flame = 2, OtherHarmful = 3 }

    /// <summary>The ground under the blast's centre (design §3.4 and §3.11).</summary>
    public enum KbShowGround : byte { Soil = 0, Stone = 1, Floor = 2, Water = 3 }

    /// <summary>The scar laid, by size class. None on water; a scorch (no pit) on stone, built floors and under a flame
    /// blast; a crater on soil and other loose ground.</summary>
    public enum KbScarKind : byte { None = 0, Crater = 1, Scorch = 2 }

    /// <summary>The player's switches for the show (design §5): one on/off per part, all on by default, and the screen
    /// shake strength slider (0 = none, 1 = as shipped, 2 = double).</summary>
    public struct KbShowSwitches
    {
        public bool fireAndFlash, screenShake, airRipple, craterScars, smoke, sootOnThings, sootOnPawns;
        public float shakeStrength;
        public bool powerFromDamage;     // the throw's own "Bigger blasts throw harder" switch: one measure for throw and show
        public float powerRefPercent;    // the throw's "Normal damage for a full push" percent

        public static KbShowSwitches AllOn()
        {
            return new KbShowSwitches
            {
                fireAndFlash = true, screenShake = true, airRipple = true, craterScars = true, smoke = true,
                sootOnThings = true, sootOnPawns = true, shakeStrength = 1f, powerFromDamage = true, powerRefPercent = 100f,
            };
        }

        public static KbShowSwitches AllOff()
        {
            KbShowSwitches s = AllOn();
            s.fireAndFlash = s.screenShake = s.airRipple = s.craterScars = s.smoke = s.sootOnThings = s.sootOnPawns = false;
            return s;
        }
    }

    /// <summary>One blast as the show sees it: everything the plan reads, and nothing from the game's types.</summary>
    public struct KbShowBlast
    {
        public KbShowKind kind;
        public KbShowGround ground;
        public float radius;             // Explosion.radius, cells
        public float damage;             // Explosion.damAmount
        public float refDamage;          // the type's reference damage (RM_Patch_DamageWorker_ExplosionKnockback.RefDamageOf)
        public float screenShakeFactor;  // Explosion.screenShakeFactor (1 for vanilla blasts)
        public float cameraDistance;     // cells from the blast to the centre of the player's view, on the ground plane
        public bool onCurrentMap;
        public bool inView;              // the blast's disc touches the player's view rect
    }

    /// <summary>What the show does for one blast. Every size is in cells; every count is a fleck count.</summary>
    public struct KbShowPlan
    {
        public float power;              // the one measure of the blast (§2)
        public bool show;                // false: the blast keeps its vanilla look in every part

        // what the hook does to the vanilla blast (the prefix's only writes)
        public bool suppressVanillaVisuals;     // doVisualEffects = false: vanilla flash, cell flecks, shake and splash stop
        public bool zeroVanillaShake;           // screenShakeFactor = 0: vanilla's own shake stops, our shake replaces it
        public bool suppressVanillaBlastMark;   // a Filth_BlastMark pre-spawn is dropped: our scar replaces it
        public bool replayVanillaShake;         // our fire part stopped vanilla's shake, our shake is off: give vanilla's back
        public bool replayWaterSplash;          // our fire part stopped vanilla's water splash, which 0.2.0 keeps (§3.15)

        // fire and flash (§3.1 to §3.4, §3.9)
        public float flashScale;
        public int fireballLobes;
        public float fireballScale;
        public int sparks;
        public int debris;               // dirt bits on soil, stone chips on stone and floor; 0 under flame and on water
        public bool debrisIsStone;

        // screen shake (§3.5)
        public float shakeMag;           // added to the camera shaker; the game caps the total at 0.2 x the player's own preference
        public int shakeHoldTicks;       // a bigger blast holds its shake longer (at half its kick)

        // air ripple (§3.6)
        public float rippleDiameter;     // the ring's final width
        public float rippleSeconds;      // how long the ring runs out (its life at the ripple fleck's fixed growth rate)
        public float rippleAlpha;        // its strength

        // crater scar (§3.11)
        public KbScarKind scarKind;
        public float scarSize;           // drawn width, cells
        public int scarSizeClass;        // index into ScarDrawSizes: which of the six scar defs of its kind

        // smoke and soot
        public int smokePuffs;
        public float smokeSeconds;
        public float sootThingsReach;    // cells from the centre that soot reaches on walls, doors, furniture and floors
        public float sootPawnsReach;     // cells from the centre that soot reaches on pawns (each soot part has its own field,
                                         // so one soot switch off leaves the other's look whole: S_OFF_OWN, S_SWITCH)
    }

    public static class RM_KnockbackShowPlan
    {
        // ---- anchors, each measured from RimWorld 1.6 (Core defs and DamageWorker.ExplosionStart, read 2026-11-24) ----

        /// <summary>The reference radius of power 1: the frag grenade's explosionRadius, 1.9 (RangedIndustrialGrenades.xml).
        /// A frag grenade at its type's normal damage (Bomb 50) has power 1.</summary>
        public const float RefRadius = 1.9f;

        /// <summary>Vanilla's flash is FleckDefOf.ExplosionFlash at scale radius x 6 (DamageWorker.ExplosionStart). Ours is
        /// the same size at power 1 for that radius, and grows with the square root of power.</summary>
        public const float VanillaFlashPerRadius = 6f;

        /// <summary>Vanilla's shake is 4 x radius x screenShakeFactor / distance to the camera (DamageWorker.ExplosionStart);
        /// the shaker caps the total at 0.2 x the player's preference (CameraShaker.MaxShakeMag) and decays it at 0.5 a
        /// second.</summary>
        public const float VanillaShakePerRadius = 4f;
        public const float VanillaShakeCap = 0.2f;

        /// <summary>Vanilla's mortar blast mark, Filth_BlastMark, is drawn 7 cells wide for a 2.9-cell blast
        /// (Filth_Various.xml, Items_Resource_Shell.xml): 7 / 2.9 = 2.41 cells of scar per cell of radius.</summary>
        public const float ScarPerRadius = 7f / 2.9f;

        // ---- design choices (design §3), each with its reason; the live scene sc_blast_show reads the look ----

        /// <summary>Our shake at power 1 directly under the view: half vanilla's cap, so a grenade is a kick and a mortar
        /// (power 2.3) or bigger nearly fills the cap. Below the cap, shake follows the square root of power.</summary>
        public const float ShakeAtPowerOne = 0.1f;

        /// <summary>A power-1 blast this many cells from the view's centre adds no shake (bar: "a far small blast does not
        /// shake it at all"). 30 cells is about half the width of the view at the default zoom [guess ~60%; sc_blast_show
        /// reads it]; reach grows with the square root of power, so a big blast shakes from farther.</summary>
        public const float ShakeReachAtPowerOne = 30f;

        /// <summary>A shake smaller than this is not added: it is below one pixel of camera travel at the default zoom
        /// [guess ~70%], and adding it would only keep the camera trembling in a far barrage.</summary>
        public const float ShakeFloor = 0.005f;

        /// <summary>The ripple runs at the RM_KnockbackBlastRipple def's growthRate (cells a second, fixed per def) from a
        /// zero start; its life sets its width. Keep this equal to the def's growthRate (the selftest reads both).</summary>
        public const float RippleGrowthPerSecond = 30f;

        /// <summary>The blast's power (design §2): the throw's own damage ratio (RM_KnockbackMath.DamageRatio, with the
        /// throw's switch and percent) times the blast's area against the reference radius. A blast that throws far looks
        /// big. Never negative; a zero radius is power 0.</summary>
        public static float Power(float damage, float refDamage, float radius, bool powerFromDamage, float refPercent)
        {
            float ratio = RM_KnockbackMath.DamageRatio(damage, refDamage, refPercent, powerFromDamage);
            float r = Math.Max(0f, radius) / RefRadius;
            return Math.Max(0f, ratio) * r * r;
        }

        /// <summary>The blast's effective radius: the radius a power-1 blast would need for this power. The size of every
        /// part with a width follows it.</summary>
        public static float EffectiveRadius(float power)
        {
            return RefRadius * (float)Math.Sqrt(Math.Max(0f, power));
        }

        /// <summary>The shake one blast adds (bar blast_show_screen_shake): harder for a bigger and a nearer blast, none
        /// beyond the reach, none at the slider's none, never negative. Inside the game's own cap.</summary>
        public static float ShakeMag(float power, float cameraDistance, float strength, float screenShakeFactor)
        {
            if (!(power > 0f) || !(strength > 0f) || !(screenShakeFactor > 0f))
            {
                return 0f;
            }
            float root = (float)Math.Sqrt(power);
            float reach = ShakeReachAtPowerOne * root;
            float d = Math.Max(0f, cameraDistance);
            if (d >= reach)
            {
                return 0f;
            }
            float fall = 1f - d / reach;
            float mag = strength * screenShakeFactor * ShakeAtPowerOne * root * fall * fall;
            return mag < ShakeFloor ? 0f : mag;
        }

        /// <summary>How much to add to the camera's current shake for a new blast's kick (§3.5, the trauma rule): shakes
        /// add as the root of the sum of their squares, never as a plain sum, so a barrage of small blasts does not sum
        /// into nausea, while one blast alone still shakes by its whole kick. Never negative.</summary>
        public static float ShakeToAdd(float current, float kick)
        {
            if (!(kick > 0f))
            {
                return 0f;
            }
            float c = Math.Max(0f, current);
            return Math.Max(0f, (float)Math.Sqrt(c * c + kick * kick) - c);
        }

        /// <summary>Vanilla's own shake (DamageWorker.ExplosionStart), given back when our fire part stopped it and our
        /// shake is off. cameraHeightDistance is vanilla's own: the straight line from the blast to the camera.</summary>
        public static float VanillaShakeMag(float radius, float screenShakeFactor, float cameraHeightDistance)
        {
            return cameraHeightDistance > 0f ? VanillaShakePerRadius * radius * screenShakeFactor / cameraHeightDistance : 0f;
        }

        /// <summary>The widths the scar is drawn at, one scar def per width and kind (filth draws at its def's drawSize):
        /// 3 cells up to 20, each about 1.45 times the last, with 7 (vanilla's mortar mark) among them.</summary>
        public static readonly float[] ScarDrawSizes = { 3f, 5f, 7f, 10f, 14f, 20f };

        /// <summary>The scar's size class: the drawn width nearest to the scar's size, measured by ratio (a geometric
        /// midpoint between two widths is the boundary).</summary>
        public static int ScarClass(float scarSize)
        {
            int best = 0;
            double bestD = double.MaxValue;
            double ls = Math.Log(Math.Max(1e-3f, scarSize));
            for (int i = 0; i < ScarDrawSizes.Length; i++)
            {
                double d = Math.Abs(Math.Log(ScarDrawSizes[i]) - ls);
                if (d < bestD)
                {
                    bestD = d;
                    best = i;
                }
            }
            return best;
        }

        /// <summary>How long a bigger blast holds its shake (CameraShaker.DoShake(mag, durationTicks) keeps the shake at
        /// least at mag for that long). The game caps how hard the camera shakes; a bigger blast still shakes LONGER, so
        /// above the cap it is still the bigger shake. 0 at power 1 and below; 15 ticks for each doubling above; at most
        /// 120 ticks (2 seconds: §3.5, the trauma model keeps a barrage from summing into nausea).</summary>
        public static int ShakeHoldTicks(float power, float mag)
        {
            if (!(mag > 0f) || !(power > 1f))
            {
                return 0;
            }
            return Clamp((int)Math.Round(15.0 * Math.Log(power, 2.0)), 0, 120);
        }

        public static KbShowPlan Plan(KbShowBlast b, KbShowSwitches s)
        {
            KbShowPlan p = new KbShowPlan();
            p.power = Power(b.damage, b.refDamage, b.radius, s.powerFromDamage, s.powerRefPercent);
            if (b.kind == KbShowKind.NoShow || !(p.power > 0f))
            {
                return p;      // the vanilla look, untouched
            }
            p.show = true;
            float root = (float)Math.Sqrt(p.power);
            float er = EffectiveRadius(p.power);
            bool ownsFire = b.kind == KbShowKind.Bomb || b.kind == KbShowKind.Flame;

            // fire and flash: our fire replaces vanilla's flash and cell flecks; another mod's harmful type keeps its own
            if (s.fireAndFlash && ownsFire)
            {
                p.suppressVanillaVisuals = true;
                // vanilla's StartExplosion throws FleckMaker.WaterSplash on every blast with visual effects on, on any
                // ground (Explosion.StartExplosion, read 2026-11-24); 0.2.0 keeps it (§3.15), so the hook throws it back
                p.replayWaterSplash = true;
                if (b.inView && b.onCurrentMap)
                {
                    p.flashScale = VanillaFlashPerRadius * er;
                    // three to six lobes (§3.2): one more for each doubling of power from 1, three below it
                    p.fireballLobes = Clamp(3 + (int)Math.Floor(Math.Log(Math.Max(1f, p.power), 2.0)), 3, 6);
                    p.fireballScale = 1.2f * er;
                    // sparks: 6 at power 1, with the square root of power, at most 40 per blast (§3.3: capped per blast)
                    p.sparks = Clamp((int)Math.Round(6f * root), 2, 40);
                    if (b.kind == KbShowKind.Bomb && b.ground != KbShowGround.Water)
                    {
                        p.debris = Clamp((int)Math.Round(8f * root), 3, 48);
                        p.debrisIsStone = b.ground == KbShowGround.Stone || b.ground == KbShowGround.Floor;
                    }
                }
            }

            // screen shake: ours replaces vanilla's whenever our shake is on
            if (s.screenShake)
            {
                p.zeroVanillaShake = true;
                if (b.onCurrentMap)
                {
                    p.shakeMag = ShakeMag(p.power, b.cameraDistance, s.shakeStrength, b.screenShakeFactor);
                    p.shakeHoldTicks = ShakeHoldTicks(p.power, p.shakeMag);
                }
            }
            else if (p.suppressVanillaVisuals)
            {
                p.replayVanillaShake = true;   // our fire stopped vanilla's shake; the shake switch off means vanilla's shake
            }

            // air ripple: a ring to about the blast's edge, wider and stronger for a bigger blast
            if (s.airRipple && b.inView && b.onCurrentMap)
            {
                p.rippleDiameter = 2f * er;
                p.rippleSeconds = p.rippleDiameter / RippleGrowthPerSecond;
                p.rippleAlpha = Math.Min(1f, 0.35f * root);
            }

            // crater scar: laid on or off screen (a scar endures); none on water
            if (s.craterScars && b.ground != KbShowGround.Water)
            {
                p.suppressVanillaBlastMark = true;
                p.scarKind = b.kind == KbShowKind.Flame || b.ground == KbShowGround.Stone || b.ground == KbShowGround.Floor
                    ? KbScarKind.Scorch : KbScarKind.Crater;
                p.scarSize = ScarPerRadius * er;
                p.scarSizeClass = ScarClass(p.scarSize);
            }

            // smoke: drawn only in view on the current map (a fleck nobody sees costs frames)
            if (s.smoke && b.inView && b.onCurrentMap)
            {
                p.smokePuffs = Clamp((int)Math.Round(6f * root), 3, 30);
                p.smokeSeconds = 12f * root;
            }
            // soot: laid on or off screen (it endures, as a scar does)
            if (s.sootOnThings)
            {
                p.sootThingsReach = 0.8f * er;
            }
            if (s.sootOnPawns)
            {
                p.sootPawnsReach = 0.8f * er;
            }
            return p;
        }

        private static int Clamp(int v, int lo, int hi)
        {
            return v < lo ? lo : v > hi ? hi : v;
        }
    }
}
