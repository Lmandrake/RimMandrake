using System;
using System.Collections.Generic;

namespace RimMandrake.ExplosiveKnockback
{
    // The pure kernel of Explosive Knockback (design/RimMandrake/explosive_knockback_design_2026-10-06.md §3.3-3.4,
    // §4.4, §8.1). Verse-free on purpose: Source/SelfTest compiles THIS file, so every rule below is tested as
    // shipped. A `using Verse;` here breaks the selftest build, and that break is the guard rail working.

    public enum KbCell : byte
    {
        Open = 0,        // walkable, nothing in the way
        Wall = 1,        // impassable edifice / rock / Fillage.Full
        Door = 2,        // a closed door (incl. a FlowWorks sluice door)
        Partial = 3,     // sandbags, barricade: Fillage.Partial and passable
        Pawn = 4,        // another pawn stands here
        Pit = 5,         // an OPEN FlowWorks pit cell (D = 4, uncovered)
        CoveredPit = 6,  // a pit under an intact cover: a pit for the path (the throw ends IN it and breaks it)
        Water = 7,       // terrain this thing cannot stand on (deep water, lava)
        OutOfBounds = 8,
    }

    public enum KbKind : byte { Pawn = 0, Item = 1, Corpse = 2 }

    public enum KbStop : byte
    {
        None = 0,        // no move at all
        Distance = 1,    // flew its whole distance
        Wall = 2,
        Door = 3,
        Pawn = 4,
        Pit = 5,
        Water = 6,
        OutOfBounds = 7,
        PartialCover = 8, // only with "sandbags stop a throw" on
        // it crossed sandbags toward a pawn standing just past them, and comes back off them: it never reached that pawn
        // (bar no_impact_without_contact), so it hit nobody. With "sandbags stop a throw" off; it takes its own stop's hit.
        PawnBeyondCover = 9,
    }

    public interface IKbGrid
    {
        KbCell At(int x, int z);
    }

    public sealed class KbSettings
    {
        public float globalMultiplier = 1f;
        public float baseCells = 4f;
        public int maxCells = 6;
        // 70 kg = a clothed, armed human (body 60 kg + worn gear, which counts). The design's 60 kg calibrated a
        // NAKED human: with gear at ~8 kg a mortar beside a colonist threw 2, not the owner's 3 (Q7).
        public float refMass = 70f;
        // owner card 2026-11-13 ("Cutoff -> A mass limit"): a living pawn heavier than this (kg, the game's Mass stat less
        // carried inventory) is never thrown. 150 = 60 kg x body size 2.5, the old body-size cutoff's line.
        public float creatureMassLimit = 150f;
        public float lightMassLimit = 75f;
        public bool impactEnabled = true;
        public float impactPerCell = 4f;
        public bool sandbagsStop = false;
        public bool intoPits = true;
        // per-blast (design §2.1): scales wall / pawn / door impact for this blast (palm thumper 0 = an arrest tool)
        public float impactFactor = 1f;
    }

    /// <summary>One blast's knockback configuration (design §2.1). Supplied WHOLE by the first source that has one, in
    /// order projectile ThingDef -> weapon ThingDef -> DamageDef -> the "unpatched explosions" setting; no field-by-field
    /// merge, so an explicit force 0 on the projectile wins over a DamageDef that throws.</summary>
    public sealed class KbConfig
    {
        public float force = 1f;
        public int ownCap = 0;               // 0 = the global maximum
        public float impactFactor = 1f;
        public float massLimitOverride = 0f; // kg; 0 = unset: the global creature mass limit holds (grav-ram 216)
        // blast power (2026-11-13): force above is already typeForce x damageRatio once the game side has set these
        public float typeForce = 1f;
        public float damage = -1f;           // the explosion's own damage amount; -1 = not an explosion (gas burst)
        public float damageRatio = 1f;
        public string source = "none";       // projectile | weapon | damageDef | unpatched | none (journal)
        // false = ownCap is exact, never rescaled by the "weapons with their own maximum" scale: a gas burst's goods cap is
        // gasBurstGoodsCells, not a weapon's (blind cycle 1, RIMMANDRAKE_UNCOUPLE_GAS_GOODS_CAP_FROM_WEAPON_SCALE)
        public bool scaleOwnCap = true;
    }

    public static class KbLookup
    {
        /// <summary>First non-null wins whole. With none: a harmful blast throws at the unpatched fraction (default 1.0),
        /// a harmless one not at all.</summary>
        public static KbConfig Resolve(KbConfig projectile, KbConfig weapon, KbConfig damageDef, bool harmsHealth, float unpatchedFraction)
        {
            if (projectile != null)
            {
                projectile.source = "projectile";
                return projectile;
            }
            if (weapon != null)
            {
                weapon.source = "weapon";
                return weapon;
            }
            if (damageDef != null)
            {
                damageDef.source = "damageDef";
                return damageDef;
            }
            return new KbConfig { force = harmsHealth ? unpatchedFraction : 0f, source = harmsHealth ? "unpatched" : "none" };
        }

        /// <summary>A per-request copy of the global settings with this blast's cap, impact factor and mass-limit override
        /// applied. Never mutates the shared settings.</summary>
        public static KbSettings Apply(KbSettings global, KbConfig c, int globalCap, float ownCapScale)
        {
            return new KbSettings
            {
                globalMultiplier = global.globalMultiplier,
                baseCells = global.baseCells,
                maxCells = RM_KnockbackMath.CapFor(c?.ownCap ?? 0, globalCap, c == null || c.scaleOwnCap ? ownCapScale : 1f),
                refMass = global.refMass,
                creatureMassLimit = c != null && c.massLimitOverride > 0f ? c.massLimitOverride : global.creatureMassLimit,
                lightMassLimit = global.lightMassLimit,
                impactEnabled = global.impactEnabled,
                impactPerCell = global.impactPerCell,
                sandbagsStop = global.sandbagsStop,
                intoPits = global.intoPits,
                impactFactor = c != null ? Math.Max(0f, c.impactFactor) : 1f,
            };
        }
    }

    /// <summary>Stun-lock guard (design §4, GPT #4): no new launch until the landing stun has ended AND a recovery window
    /// has passed. window 0 = chain throws allowed.</summary>
    public static class KbImmunity
    {
        public static bool CanLaunch(int now, int landedAt, int stunEnd, int window)
        {
            if (window <= 0)
            {
                return true;
            }
            return now >= Math.Max(landedAt, stunEnd) + window;
        }
    }

    /// <summary>Shield counter (owner Q4): a shield that absorbed the blast absorbs the throw and pays
    /// force x perForce damage-equivalents (x the shield's energy loss per damage) on top. Returns the energy left; below
    /// zero the shield breaks.</summary>
    public static class KbShield
    {
        public static float EnergyAfter(float energy, float force, float perForce, float energyLossPerDamage)
        {
            return energy - Math.Max(0f, force) * Math.Max(0f, perForce) * Math.Max(0f, energyLossPerDamage);
        }
    }

    public struct KbResult
    {
        public int destX, destZ;
        public float pitEntryOffsetX, pitEntryOffsetZ; // from the landing cell's centre to the end of the flight
        public int cellsPlanned;
        public int cellsTravelled;
        public float impact;          // on the thrown pawn (already split when a pawn was hit)
        public float otherImpact;     // on the pawn it hit
        public bool hitOther;
        public int otherX, otherZ;
        public bool hitDoor;
        public int doorX, doorZ;
        public KbStop stop;
        // the solid cell (wall / door / map edge) the throw broke on, and the cell it was in when it did: what a
        // rebound reflects off (flying goods, RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD). hasBlock false = no solid hit.
        public bool hasBlock;
        public int blockX, blockZ, blockFromX, blockFromZ;

        public bool Moved => cellsTravelled > 0;
    }

    public struct KbCandidate
    {
        public int index;
        public KbKind kind;
        public float distance;
    }

    public static class RM_KnockbackMath
    {
        public static float Clamp01(float v) => v < 0f ? 0f : (v > 1f ? 1f : v);

        public static float Falloff(float dist, float radius)
        {
            if (radius <= 0f)
            {
                return 0f;
            }
            return 1f - Clamp01(dist / radius);
        }

        public static float MassScale(float mass, KbSettings s)
        {
            float m = Math.Max(mass, 1f);
            float v = (float)Math.Sqrt(s.refMass / m);
            return v < 0.25f ? 0.25f : (v > 2f ? 2f : v);
        }

        /// <summary>Cells to throw. 0 = no move. Calibration (owner Q7): mortar r 2.9, distance 1, 60 kg -> 3.</summary>
        public static int ThrowCells(float dist, float radius, float force, float mass, KbSettings s)
        {
            return Cells(ThrowRaw(dist, radius, force, mass, s), s);
        }

        /// <summary>Loose goods and corpses fly wild (owner card "C, wild"; sheet: about 1.6 times as far as a person): the
        /// kernel's unrounded throw times `wild`, rounded and capped like any throw. wild 1 = the plain kernel.</summary>
        public static int WildCells(float dist, float radius, float force, float mass, KbSettings s, float wild)
        {
            return Cells(ThrowRaw(dist, radius, force, mass, s) * Math.Max(0f, wild), s);
        }

        private static double ThrowRaw(float dist, float radius, float force, float mass, KbSettings s)
        {
            if (force <= 0f || s.globalMultiplier <= 0f)
            {
                return 0.0;
            }
            return s.baseCells * force * Falloff(dist, radius) * MassScale(mass, s) * s.globalMultiplier;
        }

        private static int Cells(double raw, KbSettings s)
        {
            int cells = (int)Math.Round(raw, MidpointRounding.AwayFromZero);
            if (cells > s.maxCells)
            {
                cells = s.maxCells;
            }
            return cells < 1 ? 0 : cells;
        }

        /// <summary>Blast power (owner card 2026-11-13, "Blast power -> Type x damage"): this explosion's damage over the
        /// reference damage (the damage type's own defaultDamage, or its extension's refDamage) times refPercent / 100.
        /// Multiplies the type's force. 1 when the switch is off or there is no usable reference, so a type at its own
        /// normal damage throws exactly what shipped before; a negative damage counts as 0.</summary>
        public static float DamageRatio(float damage, float refDamage, float refPercent, bool enabled)
        {
            float r = refDamage * refPercent / 100f;
            if (!enabled || !(r > 0f))
            {
                return 1f;
            }
            return Math.Max(0f, damage) / r;
        }

        /// <summary>The throw cap for one blast (owner, 2026-10-06, by question card: each weapon sets its own).
        /// ownCap > 0 = the blast's own maximum (its DamageDef's RM_KnockbackExtension.maxThrowCells) times the
        /// "weapons with their own maximum" scale, never below 1; ownCap <= 0 = the global maximum, as before.</summary>
        public static int CapFor(int ownCap, int globalCap, float ownCapScale)
        {
            if (ownCap <= 0)
            {
                return globalCap;
            }
            int c = (int)Math.Round(ownCap * ownCapScale, MidpointRounding.AwayFromZero);
            return c < 1 ? 1 : c;
        }

        /// <summary>Does this thing move at all, before geometry? A living pawn heavier than the creature mass limit stays;
        /// an item or corpse heavier than the goods limit stays (a corpse is goods: no body-size rule since 2026-11-13).</summary>
        public static bool Eligible(KbKind kind, float mass, KbSettings s)
        {
            if (kind == KbKind.Pawn && mass > s.creatureMassLimit)
            {
                return false;
            }
            if ((kind == KbKind.Item || kind == KbKind.Corpse) && mass > s.lightMassLimit)
            {
                return false;
            }
            return true;
        }

        /// <summary>Owner ruling 2026-11-10/11: does the storage under a loose good keep it from being thrown? Only a CLOSED
        /// container does (storage that hides its contents, or carries the opt-in tag); an open shelf only when the player
        /// turned the old rule back on.</summary>
        public static bool GoodsHeld(bool onStorage, bool closed, bool openStorageProtects)
        {
            return onStorage && (closed || openStorageProtects);
        }

        /// <summary>The fire-at-half switch (sheet: "fire at half ... off: fire throws nothing"): true when a resolved config's
        /// force is to be zeroed: the switch is off, the force is the damage type's own patch (source "damageDef"; a
        /// projectile's or weapon's own tuning is that weapon's and stays) and the type is fire (IsFireDamage).</summary>
        public static bool FireSwitchedOff(bool fireAtHalf, string source, string damageDefName, string hediffDefName)
        {
            return !fireAtHalf && source == "damageDef" && IsFireDamage(damageDefName, hediffDefName);
        }

        /// <summary>A fire damage type: Flame, or a type whose injury is a burn: Burn, or Anomaly's ElectricalBurn (its DamageDef
        /// has ParentName="Flame", so it inherits Flame's patched force 0.5, but its hediff is ElectricalBurn, not Burn).</summary>
        public static bool IsFireDamage(string damageDefName, string hediffDefName)
        {
            return damageDefName == "Flame" || hediffDefName == "Burn" || hediffDefName == "ElectricalBurn";
        }

        /// <summary>A closed container's planned throw (owner 2026-11-12, "the whole crate/chest would go flying a bit", by card
        /// 2026-11-14 thrown as built): a 1x1 container whose own mass plus its goods is at or under the container mass limit
        /// (closedContainerMassLimit, 250 kg, not the 75 kg goods limit) flies the kernel's item throw at that mass, so shorter
        /// than the same goods loose; anything else plans 0 cells and jolts in place. RM_MapComponent_Knockback.ThrowContainer
        /// walks the path (an open pit is a wall for it, it never rests on a person).</summary>
        public static int ContainerThrowCells(bool oneByOne, float mass, float containerMassLimit, float dist, float radius, float force, KbSettings s)
        {
            if (!oneByOne || mass > containerMassLimit)
            {
                return 0;
            }
            return ThrowCells(dist, radius, force, mass, s);
        }

        /// <summary>A blocked container's jolt, drawn (journal question 13): the drawn offset `ticksSince` ticks into a jolt of
        /// `durationTicks`, a decaying shake along the blast's direction (dx,dz), never more than `amplitude` cells, 0 before
        /// it starts and from its end on. Pure, so the selftest proves the bound the drawing uses.</summary>
        public static void JoltOffset(int ticksSince, int durationTicks, float amplitude, float dx, float dz, out float ox, out float oz)
        {
            ox = 0f;
            oz = 0f;
            if (durationTicks <= 0 || ticksSince < 0 || ticksSince >= durationTicks || !(amplitude > 0f))
            {
                return;
            }
            float m = (float)Math.Sqrt(dx * dx + dz * dz);
            if (m < 1e-6f)
            {
                dx = 1f;
                dz = 0f;
                m = 1f;
            }
            float left = 1f - ticksSince / (float)durationTicks;                 // decays to 0 at the end
            float wave = (float)Math.Sin((ticksSince + 1) * Math.PI / 3.0);     // a shake of about six ticks a cycle
            float a = amplitude * left * wave;
            ox = a * dx / m;
            oz = a * dz / m;
        }

        /// <summary>RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS (owner card d_c_heavy_knock): a flying good reaching a standing person's
        /// cell. A stack of at least minMass hits (Blunt dmgMin..max(dmgMin, dmgMax) by roll in [0,1), a staggerTicks stun) and
        /// its flight ends there; lighter goods, corpses and gas-thrown goods pass with no damage. True = hit.</summary>
        public static bool HeavyKnock(bool enabled, KbKind kind, bool personThere, float mass, float minMass, float dmgMin, float dmgMax,
            float roll, int staggerTicks, out float damage, out int stun, int explosionId = 0)
        {
            damage = 0f;
            stun = 0;
            if (explosionId < 0 || !enabled || kind != KbKind.Item || !personThere || mass < minMass)
            {
                return false;
            }
            float hi = dmgMax < dmgMin ? dmgMin : dmgMax;
            damage = dmgMin + (hi - dmgMin) * Clamp01(roll);
            stun = staggerTicks < 0 ? 0 : staggerTicks;
            return true;
        }

        /// <summary>RIMMANDRAKE_BREAK_COVER_UNDER_LANDING_STACK_STILL_WHOLE (certified leaf thrown_into_pit_falls): a thrown stack,
        /// corpse or pawn coming down on a covered pit cell breaks the cover and falls through, whatever its mass (scene sc_pit_fall:
        /// "on the covered cell the colonist and the stack fall through ... and the cover is broken";
        /// RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP: FlowWorks' own trap springs on a mass sum that spares the own
        /// faction, so a blast-thrown colonist stood on the cover). A gas burst's throw (negative explosion id) never breaks one
        /// (gas bursts never break pit covers); a closed container lands on free cells only. True = break the cover under the
        /// landing.</summary>
        public static bool LandingBreaksCover(KbKind kind, bool covered, bool container, int explosionId)
        {
            return covered && !container && explosionId >= 0;
        }

        /// <summary>What a superdeep cell is for the path (RM_MapKbGrid): another pawn there (on the cover's deck, or on an open
        /// pit's floor) blocks a thrown pawn as on any ground (bar pawn_hits_pawn_stops; blind cycle 5,
        /// RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER); else an intact cover is a covered pit and an open pit a pit (both
        /// end a throw in them: Resolve).</summary>
        public static KbCell PitCell(bool covered, bool forPawn, bool pawnThere)
        {
            if (forPawn && pawnThere)
            {
                return KbCell.Pawn;
            }
            return covered ? KbCell.CoveredPit : KbCell.Pit;
        }

        /// <summary>The cell a shove may enter: only open ground with nothing on it. Never a pit (open or covered), a wall,
        /// a door, sandbags, water, the map edge or a pawn.</summary>
        public static bool ShoveCellFree(KbCell c, bool hasThings)
        {
            return c == KbCell.Open && !hasThings;
        }

        /// <summary>A deterministic direction for a thing on the blast's own cell, keyed on (explosion, thing).</summary>
        public static void EpicentreDir(int explosionId, int thingId, out float dx, out float dz)
        {
            unchecked
            {
                uint h = 2166136261u;
                h = (h ^ (uint)explosionId) * 16777619u;
                h = (h ^ (uint)thingId) * 16777619u;
                h ^= h >> 13;
                h *= 0x5bd1e995u;
                h ^= h >> 15;
                double a = (h % 360u) * Math.PI / 180.0;
                dx = (float)Math.Cos(a);
                dz = (float)Math.Sin(a);
            }
        }

        /// <summary>The cells of the throw: grid steps along the line from (sx,sz) in direction (dx,dz), exactly
        /// `cells` steps long (cell count is grid steps, not Euclidean — GPT #15). Excludes the start.</summary>
        public static List<(int x, int z)> Line(int sx, int sz, float dx, float dz, int cells)
        {
            var path = new List<(int, int)>(Math.Max(cells, 0));
            float m = Math.Max(Math.Abs(dx), Math.Abs(dz));
            if (cells <= 0 || m < 1e-6f)
            {
                return path;
            }
            int tx = sx + (int)Math.Round(dx / m * cells, MidpointRounding.AwayFromZero);
            int tz = sz + (int)Math.Round(dz / m * cells, MidpointRounding.AwayFromZero);
            int ddx = Math.Abs(tx - sx), ddz = Math.Abs(tz - sz);
            int stepX = tx > sx ? 1 : -1, stepZ = tz > sz ? 1 : -1;
            int n = Math.Max(ddx, ddz);
            for (int i = 1; i <= n; i++)
            {
                // symmetric DDA: one step per i along the major axis
                int x = sx + (ddx == 0 ? 0 : stepX * (int)Math.Round((double)ddx * i / n, MidpointRounding.AwayFromZero));
                int z = sz + (ddz == 0 ? 0 : stepZ * (int)Math.Round((double)ddz * i / n, MidpointRounding.AwayFromZero));
                path.Add((x, z));
            }
            return path;
        }

        private static bool Solid(KbCell c) => c == KbCell.Wall || c == KbCell.Door || c == KbCell.OutOfBounds;

        public static float ImpactFor(int notTravelled, float mass, KbSettings s)
        {
            if (!s.impactEnabled || notTravelled <= 0)
            {
                return 0f;
            }
            return s.impactPerCell * s.impactFactor * notTravelled / (float)Math.Sqrt(MassScale(mass, s));
        }

        /// <summary>Bar collision_bruise_by_size (owner 2026-11-24: "the bruising should be proportional to the size of the thing
        /// that hit you"): the Blunt amount one pawn takes when it meets another, by landing on it or by being stopped by it.
        /// Size is the creature's mass, the measure this mod throws by. The amount is two cells of wall impact times the
        /// other's share of the pair's mass: it rises with the other's mass and falls with one's own, a like pair take one
        /// cell's wall hit each (the lightest hit the mod gives at a wall, leaf pawn_hits_pawn_stops "like at a wall"), and
        /// the heavier of an unequal pair takes next to nothing. Impact off, a blast with no impact, no other pawn, or a mass
        /// that is not a positive finite number: 0.</summary>
        public static float CollisionBruise(float ownMass, float otherMass, KbSettings s)
        {
            if (s == null || !s.impactEnabled || !(ownMass > 0f) || !(otherMass > 0f) || float.IsInfinity(ownMass) || float.IsInfinity(otherMass))
            {
                return 0f;
            }
            float amount = 2f * s.impactPerCell * s.impactFactor * otherMass / (ownMass + otherMass);
            return amount > 0f && !float.IsInfinity(amount) ? amount : 0f;
        }

        /// <summary>Walk the throw (design §3.4). The start cell is never read.</summary>
        public static KbResult Resolve(IKbGrid grid, int sx, int sz, float dx, float dz, int cells, KbKind kind,
            float mass, KbSettings s)
        {
            var r = new KbResult { destX = sx, destZ = sz, cellsPlanned = cells, stop = KbStop.None };
            if (cells <= 0)
            {
                return r;
            }
            bool pawn = kind == KbKind.Pawn;
            List<(int x, int z)> path = Line(sx, sz, dx, dz, cells);
            int px = sx, pz = sz;
            int travelled = 0;
            KbStop stop = KbStop.Distance;
            int lastNonPartialX = sx, lastNonPartialZ = sz, lastNonPartialN = 0;
            foreach ((int x, int z) in path)
            {
                KbCell c = grid.At(x, z);
                // a diagonal step never cuts a wall corner: both orthogonal neighbours must be open
                if (x != px && z != pz && c != KbCell.OutOfBounds)
                {
                    if (Solid(grid.At(x, pz)) || Solid(grid.At(px, z)))
                    {
                        stop = KbStop.Wall;
                        SetBlock(ref r, x, z, px, pz);
                        break;
                    }
                }
                if (c == KbCell.OutOfBounds)
                {
                    stop = KbStop.OutOfBounds;
                    SetBlock(ref r, x, z, px, pz);
                    break;
                }
                if (c == KbCell.Wall)
                {
                    stop = KbStop.Wall;
                    SetBlock(ref r, x, z, px, pz);
                    break;
                }
                if (c == KbCell.Door)
                {
                    stop = KbStop.Door;
                    SetBlock(ref r, x, z, px, pz);
                    r.hitDoor = true;
                    r.doorX = x;
                    r.doorZ = z;
                    break;
                }
                if (c == KbCell.Water)
                {
                    stop = KbStop.Water;
                    break;
                }
                bool pit = c == KbCell.Pit || c == KbCell.CoveredPit;
                if (pit && !s.intoPits)
                {
                    stop = KbStop.Wall; // "throw into pits" off: a pit, open or covered, is a wall for the path
                    SetBlock(ref r, x, z, px, pz);
                    break;
                }
                if (c == KbCell.Partial && pawn && s.sandbagsStop)
                {
                    stop = KbStop.PartialCover;
                    break;
                }
                if (c == KbCell.Pawn && pawn)
                {
                    stop = KbStop.Pawn;
                    r.hitOther = true;
                    r.otherX = x;
                    r.otherZ = z;
                    break;
                }
                // enter the cell
                px = x;
                pz = z;
                travelled++;
                if (c != KbCell.Partial)
                {
                    lastNonPartialX = x;
                    lastNonPartialZ = z;
                    lastNonPartialN = travelled;
                }
                if (pit)
                {
                    // stops IN the first pit cell, open or covered: nothing is thrown across a pit (sheet thrown_into_pit_falls:
                    // "onto a covered cell falls through and breaks the cover; nothing is thrown across"); the landing breaks
                    // the cover (LandingBreaksCover)
                    stop = KbStop.Pit;
                    break;
                }
            }
            // nothing comes to rest on a sandbag cell (vanilla Sandbags are PassThroughOnly: walkable, not standable):
            // back to the last free cell along the line
            if (travelled > 0 && grid.At(px, pz) == KbCell.Partial)
            {
                px = lastNonPartialX;
                pz = lastNonPartialZ;
                travelled = lastNonPartialN;
                if (stop == KbStop.Pawn)
                {
                    // bar no_impact_without_contact: the sandbag stopped it before it reached the pawn beyond, so it hit
                    // nobody (0.1.0 reported the hit, a bruise on a pawn it never touched, lane 4 | sandbag 5 | pawn 6)
                    stop = KbStop.PawnBeyondCover;
                    r.hitOther = false;
                    r.otherX = 0;
                    r.otherZ = 0;
                }
            }
            r.destX = px;
            r.destZ = pz;
            r.cellsTravelled = travelled;
            r.stop = travelled == 0 && stop == KbStop.Distance ? KbStop.None : stop;
            if (pawn && (stop == KbStop.Wall || stop == KbStop.Door || stop == KbStop.Pawn || stop == KbStop.PartialCover || stop == KbStop.PawnBeyondCover))
            {
                float imp = ImpactFor(cells - travelled, mass, s);
                if (stop == KbStop.Pawn)
                {
                    r.impact = imp * 0.5f;
                    r.otherImpact = imp * 0.5f;
                }
                else
                {
                    r.impact = imp;
                }
            }
            return r;
        }

        private static void SetBlock(ref KbResult r, int bx, int bz, int fx, int fz)
        {
            r.hasBlock = true;
            r.blockX = bx;
            r.blockZ = bz;
            r.blockFromX = fx;
            r.blockFromZ = fz;
        }

        /// <summary>A rebound's new direction (flying goods): reflect (dx,dz) off the solid cell the throw broke on.
        /// A straight hit flips the axis it struck along; a diagonal hit flips the axis whose orthogonal neighbour is
        /// solid (both if both, or a bare corner). Returns false when there was no solid hit to reflect off.</summary>
        public static bool Reflect(IKbGrid grid, KbResult res, float dx, float dz, out float rx, out float rz)
        {
            rx = dx;
            rz = dz;
            if (!res.hasBlock)
            {
                return false;
            }
            int sx = res.blockX - res.blockFromX, sz = res.blockZ - res.blockFromZ;
            if (sx != 0 && sz != 0)
            {
                bool sideX = Solid(grid.At(res.blockX, res.blockFromZ));
                bool sideZ = Solid(grid.At(res.blockFromX, res.blockZ));
                bool flipX = sideX || !sideZ;
                bool flipZ = sideZ || !sideX;
                if (flipX)
                {
                    rx = -dx;
                }
                if (flipZ)
                {
                    rz = -dz;
                }
            }
            else if (sx != 0)
            {
                rx = -dx;
            }
            else if (sz != 0)
            {
                rz = -dz;
            }
            return true;
        }

        /// <summary>Cells a rebound still flies: `keepPercent` of the cells left when the throw hit, rounded DOWN so below
        /// 100% a throw always runs out (1 cell left at 70% = 0, no rebound). At 100% nothing is lost and the chain does not
        /// end here: the carrier's MaxBounces ends it.</summary>
        public static int ReboundCells(int cellsLeft, float keepPercent)
        {
            if (cellsLeft <= 0 || keepPercent <= 0f)
            {
                return 0;
            }
            float k = keepPercent > 100f ? 100f : keepPercent;
            return Math.Min(cellsLeft, (int)Math.Floor(cellsLeft * k / 100f + 1e-4f));
        }

        /// <summary>Per-explosion cap (§4.4): pawns first, then corpses, then items nearest the centre.
        /// Returns the candidates kept, in throw order.</summary>
        public static List<KbCandidate> Prioritise(List<KbCandidate> all, int cap)
        {
            var sorted = new List<KbCandidate>(all);
            sorted.Sort((a, b) =>
            {
                int ka = KindRank(a.kind), kb = KindRank(b.kind);
                if (ka != kb)
                {
                    return ka.CompareTo(kb);
                }
                int d = a.distance.CompareTo(b.distance);
                return d != 0 ? d : a.index.CompareTo(b.index);
            });
            if (cap >= 0 && sorted.Count > cap)
            {
                sorted.RemoveRange(cap, sorted.Count - cap);
            }
            return sorted;
        }

        private static int KindRank(KbKind k) => k == KbKind.Pawn ? 0 : (k == KbKind.Corpse ? 1 : 2);
    }

    /// <summary>
    /// What one map remembers about recent explosions: which (explosion, thing) pairs were already queued (a repeat callback enqueues
    /// nothing, GPT #2) and how many throws each explosion has launched (the per-explosion cap spans several ticks). Ids never repeat, so
    /// old entries are dead weight; they are dropped in two generations a `window` apart instead of all at once, so an explosion whose
    /// wave straddles a rotation still has its pairs and its launch count: an entry lives at least `window` and at most 2 x `window` ticks.
    /// (The first version cleared everything every 600 ticks, which wiped a live explosion's cap and dedupe about 1% of the time.)
    /// </summary>
    public sealed class KbExplosionLedger
    {
        public const int DefaultWindow = 600;
        private HashSet<long> seenCur = new HashSet<long>(), seenPrev = new HashSet<long>();
        private Dictionary<int, int> launchedCur = new Dictionary<int, int>(), launchedPrev = new Dictionary<int, int>();
        private long curGen = long.MinValue;
        private readonly int window;

        public KbExplosionLedger(int window = DefaultWindow) { this.window = Math.Max(1, window); }

        // generations sit on a fixed grid of `window` ticks, so an entry made at tick t is certainly live until t + window and certainly
        // gone from t + 2 x window, however sparse the calls are
        private void Advance(int now)
        {
            long gen = now >= 0 ? now / window : -((-(long)now + window - 1) / window);
            if (curGen == long.MinValue) { curGen = gen; return; }
            if (gen == curGen) return;
            if (gen == curGen + 1)
            {
                seenPrev = seenCur; seenCur = new HashSet<long>();
                launchedPrev = launchedCur; launchedCur = new Dictionary<int, int>();
            }
            else    // two or more generations on, or the clock went backwards: nothing remembered is live
            {
                seenCur.Clear(); seenPrev.Clear(); launchedCur.Clear(); launchedPrev.Clear();
            }
            curGen = gen;
        }

        /// <summary>True the first time this (explosion, thing) pair is seen inside the memory window.</summary>
        public bool TryAdd(int explosionId, int thingId, int now)
        {
            Advance(now);
            long key = ((long)explosionId << 32) ^ (uint)thingId;
            if (seenPrev.Contains(key)) return false;
            return seenCur.Add(key);
        }

        /// <summary>Throws launched for this explosion within the memory window (both generations).</summary>
        public int Launched(int explosionId, int now)
        {
            Advance(now);
            int cur, prev;
            launchedCur.TryGetValue(explosionId, out cur);
            launchedPrev.TryGetValue(explosionId, out prev);
            return cur + prev;
        }

        public void AddLaunched(int explosionId, int now)
        {
            Advance(now);
            int n;
            launchedCur.TryGetValue(explosionId, out n);
            launchedCur[explosionId] = n + 1;
        }
    }

    /// <summary>The frame-time probe's reading (RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF; leaves frame_time_probe and
    /// barrage_frame_budget). Pure, so the selftest (K-22) proves the reading the proof scenes use.</summary>
    public struct KbFrameSummary
    {
        public int rows, pausedRows, framesElapsed, maxInAir;
        public float worstMs, meanMs, sumMs, wallSeconds;
        /// <summary>The bar's window in probe seconds (the running sum of ms), its unpaused rows and their nearest-rank
        /// 99th-percentile frame. With no window given the window is the whole run.</summary>
        public float windowLoS, windowHiS, windowP99Ms;
        public int windowRows;
    }

    public static class KbFrameStats
    {
        /// <summary>ms[i], paused[i], inAir[i]: one row per probe sample. framesElapsed: the engine's frame count over the
        /// run; wallSeconds: real time over the run. The worst frame is the MAX of the unpaused rows, never a mean.</summary>
        public static KbFrameSummary Summarize(float[] ms, bool[] paused, int[] inAir, int framesElapsed, float wallSeconds)
        {
            return Summarize(ms, paused, inAir, framesElapsed, wallSeconds, 0f, float.PositiveInfinity);
        }

        /// <summary>As above, with the bar's window [windowLoS, windowHiS] in probe seconds: a row's probe time is the
        /// running sum of ms through it, paused rows included (they are real time); its unpaused rows give windowP99Ms.</summary>
        public static KbFrameSummary Summarize(float[] ms, bool[] paused, int[] inAir, int framesElapsed, float wallSeconds,
            float windowLoS, float windowHiS)
        {
            var g = new KbFrameSummary { rows = ms.Length, framesElapsed = framesElapsed, wallSeconds = wallSeconds, windowLoS = windowLoS, windowHiS = windowHiS };
            var window = new List<float>();
            double t = 0;
            for (int i = 0; i < ms.Length; i++)
            {
                g.sumMs += ms[i];
                t += ms[i];
                if (inAir[i] > g.maxInAir) g.maxInAir = inAir[i];
                if (paused[i]) { g.pausedRows++; continue; }
                if (ms[i] > g.worstMs) g.worstMs = ms[i];
                if (t >= windowLoS * 1000.0 && t <= windowHiS * 1000.0) window.Add(ms[i]);
            }
            g.meanMs = ms.Length > 0 ? g.sumMs / ms.Length : 0f;
            g.windowRows = window.Count;
            g.windowP99Ms = Percentile(window, 99f);
            return g;
        }

        /// <summary>Nearest-rank percentile: the smallest value with at least pct% of the values at or below it; 0 for none.</summary>
        public static float Percentile(List<float> values, float pct)
        {
            if (values.Count == 0) return 0f;
            var v = new List<float>(values);
            v.Sort();
            int k = (int)Math.Ceiling(pct / 100.0 * v.Count) - 1;
            return v[Math.Max(0, Math.Min(v.Count - 1, k))];
        }

        /// <summary>The probe's own check: one row per rendered frame (within 5%), its rows add up to the real time (within
        /// 10%), the run was not paused (at least 90% unpaused rows), and a deliberate sleep of sleptMs shows as a row.</summary>
        public static bool SelfCheck(KbFrameSummary g, float sleptMs, out string why)
        {
            why = null;
            if (g.rows == 0) why = "no rows";
            else if (g.rows - g.pausedRows < 0.9f * g.rows) why = "paused: " + g.pausedRows + " of " + g.rows + " rows";
            else if (Math.Abs(g.rows - g.framesElapsed) > 0.05f * Math.Max(1, g.framesElapsed)) why = "rows " + g.rows + " vs frames " + g.framesElapsed;
            else if (Math.Abs(g.sumMs / 1000f - g.wallSeconds) > 0.1f * Math.Max(0.001f, g.wallSeconds)) why = "rows sum " + g.sumMs / 1000f + " s vs wall " + g.wallSeconds + " s";
            else if (g.worstMs < sleptMs) why = "the slept frame is missing: worst " + g.worstMs + " ms";
            return why == null;
        }

        /// <summary>The barrage bar (owner 2026-11-15, "1 agree."): the 99th-percentile unpaused frame inside the window at
        /// most budgetMs, on a run that was not paused and whose probe ran to the window's end. A single random stall
        /// does not decide it (the mod-off control's worst frame broke 50 ms on them); a stretch of slow frames does.</summary>
        public static bool WithinBudget(KbFrameSummary g, float budgetMs, out string why)
        {
            why = null;
            if (g.rows == 0) why = "no rows";
            else if (g.rows - g.pausedRows < 0.9f * g.rows) why = "paused: " + g.pausedRows + " of " + g.rows + " rows";
            else if (!float.IsPositiveInfinity(g.windowHiS) && g.sumMs < g.windowHiS * 1000f) why = "the probe stopped at " + (g.sumMs / 1000f).ToString("0.00") + " s, before the window closed at " + g.windowHiS + " s";
            else if (g.windowRows == 0) why = "no unpaused rows in the window";
            else if (g.windowP99Ms > budgetMs) why = "p99 frame in the window " + g.windowP99Ms + " ms over " + budgetMs;
            return why == null;
        }
    }
}
