using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>A map cell read for the kernel (design §3.4). Pawns block only a thrown pawn.</summary>
    public sealed class RM_MapKbGrid : IKbGrid
    {
        private readonly Map map;
        private readonly Thing self;
        private readonly bool forPawn;

        public RM_MapKbGrid(Map map, Thing self, bool forPawn)
        {
            this.map = map;
            this.self = self;
            this.forPawn = forPawn;
        }

        public KbCell At(int x, int z)
        {
            var c = new IntVec3(x, 0, z);
            if (!c.InBounds(map))
            {
                return KbCell.OutOfBounds;
            }
            Building ed = c.GetEdifice(map);
            if (ed is Building_Door door)
            {
                if (!door.Open)
                {
                    return KbCell.Door;
                }
            }
            else if (ed != null && !RM_KnockbackCompat.IsCover(ed) && (ed.def.passability == Traversability.Impassable || ed.def.Fillage == FillCategory.Full))
            {
                return KbCell.Wall;
            }
            if (RM_KnockbackCompat.IsSuperdeep(map, c))
            {
                // an occupied pit cell blocks a thrown pawn (GPT #15), a covered one too: a pawn on the deck is in the way
                // (blind cycle 5, RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER); one beneath the lid is not
                bool covered = RM_KnockbackCompat.CoverAt(map, c) != null;
                return RM_KnockbackMath.PitCell(covered, forPawn, forPawn && OtherPawnAt(c, covered));
            }
            if (ed != null && !(ed is Building_Door) && ed.def.Fillage == FillCategory.Partial)
            {
                return KbCell.Partial;
            }
            TerrainDef td = c.GetTerrain(map);
            if (td != null && td.passability == Traversability.Impassable)
            {
                return KbCell.Water;
            }
            if (!c.Walkable(map))
            {
                return KbCell.Wall;
            }
            if (forPawn && OtherPawnAt(c))
            {
                return KbCell.Pawn;
            }
            return KbCell.Open;
        }

        private bool OtherPawnAt(IntVec3 c, bool onDeckOnly = false)
        {
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Pawn p && p != self && !(onDeckOnly && RM_KnockbackCompat.IsBeneathCover(p)))
                {
                    return true;
                }
            }
            return false;
        }
    }

    /// <summary>The map as the plan reads it (KbPlanner.Decide): the path grid, and what a closed container's rest cell needs.
    /// `self` is the thing being decided; it never blocks itself.</summary>
    public sealed class RM_MapKbWorld : IKbWorld
    {
        private readonly Map map;
        private readonly Thing self;

        public RM_MapKbWorld(Map map, Thing self)
        {
            this.map = map;
            this.self = self;
        }

        public IKbGrid Grid(bool forPawn) => new RM_MapKbGrid(map, self, forPawn);

        public bool PawnAt(int x, int z)
        {
            var c = new IntVec3(x, 0, z);
            return c.InBounds(map) && c.GetFirstPawn(map) != null;
        }

        public bool Occupied(int x, int z) => RM_MapComponent_Knockback.Occupied(map, new IntVec3(x, 0, z));

        public bool Superdeep(int x, int z) => RM_KnockbackCompat.IsSuperdeep(map, new IntVec3(x, 0, z));
    }

    /// <summary>The knockback journal (design §8.2): one JSON line per request / launch / landing / skip, so a
    /// runner asserts records, never a correlate. In memory, capped; read through RM_KnockbackProof.</summary>
    public static class RM_KnockbackJournal
    {
        private static readonly List<string> lines = new List<string>();
        /// <summary>The same records, structured, for the in-game scene verdicts (RM_KnockbackProof).</summary>
        public static readonly List<Dictionary<string, object>> Recs = new List<Dictionary<string, object>>();
        public static int Launches;
        public static int ItemMoves;

        public static IReadOnlyList<string> Lines => lines;

        public static void Clear()
        {
            lines.Clear();
            Recs.Clear();
            Launches = 0;
            ItemMoves = 0;
        }

        public static void Add(string type, int explosionId, Thing t, params object[] kv)
        {
            var rec = new Dictionary<string, object> { ["type"] = type, ["tick"] = Find.TickManager?.TicksGame ?? 0, ["exp"] = explosionId };
            if (t != null)
            {
                rec["thing"] = t.ThingID;
                rec["thingId"] = t.thingIDNumber;
            }
            for (int i = 0; i + 1 < kv.Length; i += 2)
            {
                rec[(string)kv[i]] = kv[i + 1];
            }
            Recs.Add(rec);
            if (Recs.Count > 4000)
            {
                Recs.RemoveRange(0, 1000);
            }
            var sb = new StringBuilder(160);
            sb.Append("{\"type\":\"").Append(type).Append("\",\"tick\":").Append(Find.TickManager?.TicksGame ?? 0);
            sb.Append(",\"exp\":").Append(explosionId);
            if (t != null)
            {
                sb.Append(",\"thing\":\"").Append(t.ThingID).Append("\",\"def\":\"").Append(t.def.defName).Append('"');
            }
            for (int i = 0; i + 1 < kv.Length; i += 2)
            {
                sb.Append(",\"").Append(kv[i]).Append("\":");
                object v = kv[i + 1];
                if (v is IntVec3 c)
                {
                    sb.Append("[").Append(c.x).Append(',').Append(c.z).Append(']');
                }
                else if (v is float f)
                {
                    sb.Append(f.ToString("0.###", CultureInfo.InvariantCulture));
                }
                else if (v is int || v is long)
                {
                    sb.Append(v);
                }
                else if (v is bool b)
                {
                    sb.Append(b ? "true" : "false");
                }
                else
                {
                    sb.Append('"').Append(Convert.ToString(v, CultureInfo.InvariantCulture)?.Replace("\"", "'")).Append('"');
                }
            }
            sb.Append('}');
            lines.Add(sb.ToString());
            if (lines.Count > 4000)
            {
                lines.RemoveRange(0, 1000);
            }
        }
    }

    /// <summary>
    /// The per-map queue (design §4.1). Requests are flushed in MapComponentTick — the map's post-tick, after every
    /// Thing (the Explosion included) has ticked — from a snapshot, never reading the possibly destroyed Explosion.
    /// </summary>
    public class RM_MapComponent_Knockback : MapComponent
    {
        private readonly List<KnockbackRequest> queue = new List<KnockbackRequest>();
        private readonly KbExplosionLedger ledger = new KbExplosionLedger();
        // burning-gas shove guard (plan step 4): pawn thingIDNumber -> tick of its last gas shove. Not saved (a 2 s window).
        private readonly Dictionary<int, int> gasShovedAt = new Dictionary<int, int>();
        private int gasBursts;
        // stun-lock guard (design §4): pawn thingIDNumber -> landing tick / landing-stun end tick. Saved.
        private Dictionary<int, int> landedAt = new Dictionary<int, int>();
        private Dictionary<int, int> stunEnd = new Dictionary<int, int>();
        // the explosion id each pawn now in a knockback flight was thrown by (negative = a gas burst): set at every launch,
        // taken at its landing, where a blast-thrown pawn breaks the cover it comes down on. Saved (a flight outlives a save).
        private Dictionary<int, int> thrownBy = new Dictionary<int, int>();

        public void RememberThrow(Pawn p, int explosionId)
        {
            thrownBy[p.thingIDNumber] = explosionId;
        }

        // bar collision_bruise_by_size: the throwing blast's impact factor, for a landing on a pawn that walked onto the cell
        // mid-flight (a palm thumper's 0 bruises nobody there either). Not saved: after a load the landing reads 1.
        private readonly Dictionary<int, float> landingImpactFactor = new Dictionary<int, float>();

        public void RememberImpactFactor(Pawn p, float factor)
        {
            landingImpactFactor[p.thingIDNumber] = factor;
        }

        /// <summary>The impact factor of the blast that threw this pawn, forgotten once read; 1 when none is remembered.</summary>
        public float TakeImpactFactor(Pawn p)
        {
            if (!landingImpactFactor.TryGetValue(p.thingIDNumber, out float f))
            {
                return 1f;
            }
            landingImpactFactor.Remove(p.thingIDNumber);
            return f;
        }

        /// <summary>The mass a pawn is thrown and bruised by: the game's Mass stat less carried inventory, at least 1 kg.</summary>
        public static float PawnMass(Pawn p)
        {
            float m = Mathf.Max(1f, p.GetStatValue(StatDefOf.Mass) - MassUtility.InventoryMass(p));
#if RM_PROOFS
            if (RM_KnockbackProof.PinnedMass.TryGetValue(p.thingIDNumber, out float pinned))
            {
                m = pinned;   // test-only: sc_mass_and_power pins its colonist to 64-76 kg (judge gap g4)
            }
#endif
            return m;
        }

        /// <summary>The explosion that threw this pawn, forgotten once read. False when it was not thrown by us.</summary>
        public bool TakeThrow(Pawn p, out int explosionId)
        {
            if (!thrownBy.TryGetValue(p.thingIDNumber, out explosionId))
            {
                return false;
            }
            thrownBy.Remove(p.thingIDNumber);
            return true;
        }

        /// <summary>Called when one of our flyers sets a pawn down (RM_Patch_PawnFlyer_KnockbackLanding).</summary>
        public static void NotifyLanded(Pawn p)
        {
            if (p == null || !p.Spawned)
            {
                return;
            }
            RM_MapComponent_Knockback comp = p.Map.GetComponent<RM_MapComponent_Knockback>();
            if (comp == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            comp.landedAt[p.thingIDNumber] = now;
            comp.stunEnd[p.thingIDNumber] = now + (p.stances?.stunner?.StunTicksLeft ?? 0);
        }

        /// <summary>Proof/read: can this pawn be launched now under the recovery window?</summary>
        public bool CanLaunch(Pawn p, out int recoversAt)
        {
            int window = RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks;
            landedAt.TryGetValue(p.thingIDNumber, out int la);
            stunEnd.TryGetValue(p.thingIDNumber, out int se);
            bool known = landedAt.ContainsKey(p.thingIDNumber);
            recoversAt = known ? Math.Max(la, se) + window : 0;
            return !known || KbImmunity.CanLaunch(Find.TickManager.TicksGame, la, se, window);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                int now = Find.TickManager.TicksGame;
                var dead = new List<int>();
                foreach (var kv in landedAt)
                {
                    if (now - kv.Value > 60000)
                    {
                        dead.Add(kv.Key);
                    }
                }
                foreach (int k in dead)
                {
                    landedAt.Remove(k);
                    stunEnd.Remove(k);
                }
            }
            Scribe_Collections.Look(ref landedAt, "rmKbLandedAt", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref stunEnd, "rmKbStunEnd", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref thrownBy, "rmKbThrownBy", LookMode.Value, LookMode.Value);
            if (thrownBy == null)
            {
                thrownBy = new Dictionary<int, int>();
            }
            if (landedAt == null)
            {
                landedAt = new Dictionary<int, int>();
            }
            if (stunEnd == null)
            {
                stunEnd = new Dictionary<int, int>();
            }
        }

        public RM_MapComponent_Knockback(Map map) : base(map)
        {
        }

        public void Enqueue(KnockbackRequest r)
        {
            int now = Find.TickManager.TicksGame;
            // an explosion's wave lasts a few ticks; ids never repeat, so old keys are dead weight (dropped in generations, never mid-wave)
            if (!ledger.TryAdd(r.explosionId, r.thing.thingIDNumber, now))
            {
                return;
            }
            queue.Add(r);
            RM_KnockbackJournal.Add("request", r.explosionId, r.thing, "from", r.takeoff, "centre", r.centre,
                "radius", r.radius, "force", r.force, "damType", r.damType?.defName, "source", r.config?.source ?? "damageDef",
                "shieldAbsorbed", r.shield != null, "typeForce", r.config?.typeForce ?? r.force, "damage", r.config?.damage ?? -1f,
                "damageRatio", r.config?.damageRatio ?? 1f);
        }

#if RM_PROOFS
        /// <summary>Proof scenes only (RM_KnockbackProof): actions to run at a given game tick on this map, so a scene can
        /// fire a second blast mid-run. Empty in play; one Count check per tick.</summary>
        internal static readonly List<KeyValuePair<int, Action>> ProofSchedule = new List<KeyValuePair<int, Action>>();
        /// <summary>Proof planted breaks: re-impose the removed per-explosion cap (0 = none, as shipped), and land with the
        /// old Direct-first placement that shoves a resident stack.</summary>
        internal static int ProofThrowCap;
        internal static bool ProofDirectFirst;

#endif
        public override void MapComponentTick()
        {
#if RM_PROOFS
            if (ProofSchedule.Count > 0)
            {
                int now = Find.TickManager.TicksGame;
                for (int i = ProofSchedule.Count - 1; i >= 0; i--)
                {
                    if (ProofSchedule[i].Key <= now)
                    {
                        Action act = ProofSchedule[i].Value;
                        ProofSchedule.RemoveAt(i);
                        try
                        {
                            act();
                        }
                        catch (Exception ex)
                        {
                            Log.Warning("[RM Explosive Knockback] proof schedule: " + ex.Message);
                        }
                    }
                }
            }
#endif
            if (queue.Count == 0)
            {
                return;
            }
#if RM_PROOFS
            long flushT0 = System.Diagnostics.Stopwatch.GetTimestamp();
            try
            {
#endif
            var snapshot = new List<KnockbackRequest>(queue);
            queue.Clear();
            var groups = new Dictionary<int, List<KnockbackRequest>>();
            var order = new List<int>();
            foreach (KnockbackRequest r in snapshot)
            {
                if (!groups.TryGetValue(r.explosionId, out List<KnockbackRequest> g))
                {
                    g = new List<KnockbackRequest>();
                    groups[r.explosionId] = g;
                    order.Add(r.explosionId);
                }
                g.Add(r);
            }
            // RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE (owner 2026-11-12, "No caps please."): every request is
            // executed; frame time is a measured bar, not a limit. Pawns first, nearest first (Prioritise keeps all).
            foreach (int id in order)
            {
                List<KnockbackRequest> g = groups[id];
                var cands = new List<KbCandidate>(g.Count);
                for (int i = 0; i < g.Count; i++)
                {
                    Thing t = Resolve(g[i].thing);
                    KbKind k = t is Pawn ? KbKind.Pawn : (t is Corpse ? KbKind.Corpse : KbKind.Item);
                    cands.Add(new KbCandidate { index = i, kind = k, distance = (g[i].takeoff - g[i].centre).LengthHorizontal });
                }
                int cap = g.Count;
#if RM_PROOFS
                if (ProofThrowCap > 0)
                {
                    // the old cap counted the whole wave, across the ticks it spreads over
                    cap = Math.Min(cap, Math.Max(0, ProofThrowCap - ledger.Launched(id, Find.TickManager.TicksGame)));
                }
#endif
                List<KbCandidate> kept = RM_KnockbackMath.Prioritise(cands, cap);
                if (kept.Count < g.Count)
                {
                    var keptSet = new HashSet<int>();
                    foreach (KbCandidate c in kept)
                    {
                        keptSet.Add(c.index);
                    }
                    for (int i = 0; i < g.Count; i++)
                    {
                        if (!keptSet.Contains(i))
                        {
                            RM_KnockbackJournal.Add("skip", id, g[i].thing, "reason", "cap_per_explosion");
                        }
                    }
                }
                foreach (KbCandidate c in kept)
                {
                    try
                    {
                        if (Execute(g[c.index]))
                        {
                            ledger.AddLaunched(id, Find.TickManager.TicksGame); // read only by the proof cap; a count, no limit
                        }
                    }
                    catch (Exception ex)
                    {
                        Log.ErrorOnce("[RM Explosive Knockback] throw failed: " + ex, 0x4b4e4f43 ^ id);
                    }
                }
            }
#if RM_PROOFS
            }
            finally
            {
                RM_FrameProbe.FlushMs += RM_FrameProbe.MsSince(flushT0);
            }
#endif
        }

        private static Thing Resolve(Thing t)
        {
            if (t is Pawn p && p.Dead && p.Corpse != null)
            {
                return p.Corpse; // a pawn the blast killed is now a corpse, judged by the corpse rules
            }
            return t;
        }

        /// <summary>Owner ruling 2026-11-10/11 (RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED): goods on open storage (shelves,
        /// hoppers, tables: anything that draws its contents, owner 2026-11-12) fly like floor goods; only a CLOSED container (RM_KnockbackCompat.IsClosedContainer) keeps them. Goods
        /// on a shelf are ordinary spawned things on the shelf's cell, so this is decided by the edifice under them. The
        /// old every-storage rule returns only with openStorageProtectsGoods. Returns the journal reason, or null.</summary>
        private static string HeldReason(Thing t, Map map)
        {
            var f = new KbFacts();
            ReadStorage(f, t, map);
            return KbPlanner.HeldReason(f, RimMandrakeExplosiveKnockbackSettings.Rules());
        }

        /// <summary>What lies under a good: storage of any kind, and whether it is a closed container. The closed guard and
        /// the open-storage setting are applied by the plan (KbPlanner.HeldReason), not here.</summary>
        private static void ReadStorage(KbFacts f, Thing t, Map map)
        {
            Building ed = t.Position.GetEdifice(map);
            if (ed == null)
            {
                return;
            }
            f.onClosed = RM_KnockbackCompat.IsClosedContainer(ed);
            f.onStorage = f.onClosed || ed is Building_Storage || (ed.def.building != null && ed.def.building.fixedStorageSettings != null);
        }

        /// <summary>Called from the explosion prefix BEFORE the blast damages the item: will Execute throw it (same gates,
        /// same kernel, measured now)? Pit landing and path blocks are not predicted; a stack spared and then blocked is
        /// still spared.</summary>
        public static bool ItemWillBeThrown(Thing t, Explosion explosion, KbConfig cfg)
        {
            Map map = explosion.Map;
            if (map == null || !t.Spawned)
            {
                return false;
            }
            var f = new KbFacts { kind = KbKind.Item, spawned = true, thingId = t.thingIDNumber, x = t.Position.x, z = t.Position.z,
                mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount, onSuperdeep = RM_KnockbackCompat.IsSuperdeep(map, t.Position) };
            ReadStorage(f, t, map);
            var blast = new KbBlast { id = explosion.thingIDNumber, cx = explosion.Position.x, cz = explosion.Position.z, radius = explosion.radius, force = cfg.force };
            return KbPlanner.GoodWillBeThrown(f, blast, RimMandrakeExplosiveKnockbackSettings.Rules(), RimMandrakeExplosiveKnockbackSettings.Kernel(cfg));
        }

        /// <summary>Owner ruling 2026-11-12, "worse damage if they then hit a solid object": a stack stopped by a wall, door or
        /// the map edge takes Blunt damage per cell of throw it had left.</summary>
        private void GoodsWallImpact(KnockbackRequest r, Thing t, KbResult res, int cells)
        {
            GoodsImpact(t, r.explosionId, res.stop, cells - res.cellsTravelled, r.config?.impactFactor ?? 1f, r.instigator, "instant");
        }

        /// <summary>The goods wall impact itself, shared by the instant move and a flying stack (RM_ThingFlyer_Knockback),
        /// which takes it where its flight is cut short: on landing, or in flight at a rebound. `at` is journal only.</summary>
        internal static void GoodsImpact(Thing t, int explosionId, KbStop stop, int left, float impactFactor, Thing instigator, string at)
        {
            float per = RimMandrakeExplosiveKnockbackSettings.goodsWallImpactPerCell;
            if (per <= 0f || left <= 0 || t == null || t.Destroyed
                || !(stop == KbStop.Wall || stop == KbStop.Door || stop == KbStop.OutOfBounds))
            {
                return;
            }
            float dmg = per * left * impactFactor;
            if (dmg <= 0f)
            {
                return;
            }
            t.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg, 0f, -1f, instigator));
            RM_KnockbackJournal.Add("goods_impact", explosionId, t, "stop", stop.ToString(), "left", left, "damage", dmg,
                "destroyed", t.Destroyed, "at", at);
        }

        /// <summary>RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE: goods inside a closed container take no blast
        /// damage (read by the explosion prefix before the damage lands).</summary>
        public static bool InClosedContainer(Thing t, Map map)
        {
            return RimMandrakeExplosiveKnockbackSettings.closedContainerGuard && map != null && t.Spawned && t.def.category == ThingCategory.Item
                && RM_KnockbackCompat.IsClosedContainer(t.Position.GetEdifice(map));
        }

        /// <summary>Would a Direct placement of t at c shove a resident stack? GenPlace's TryPlaceDirect merges first, then
        /// spawns into a free item slot, but a stackLimit-1 thing (apparel, a weapon) is spawned even into a FULL cell, and
        /// GenSpawn then moves a resident out (or destroys it with no free cell): the bump the owner's frozen station-4 blast
        /// showed (RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS). True when what can merge does not hold it all and
        /// the cell's item slots are full.</summary>
        internal static bool WouldBump(Thing t, IntVec3 c, Map map)
        {
            if (t.def.category != ThingCategory.Item || !c.InBounds(map))
            {
                return false;
            }
            int items = 0, room = 0;
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++)
            {
                Thing h = l[i];
                if (h == t || h.def.category != ThingCategory.Item)
                {
                    continue;
                }
                items++;
                if (h.CanStackWith(t))
                {
                    room += Math.Max(0, h.def.stackLimit - h.stackCount);
                }
            }
            return room < t.stackCount && items >= c.GetMaxItemsAllowedInCell(map);
        }

        /// <summary>Lands a thrown stack (instant move and carrier alike) without ever moving a resident, in the order the plan
        /// gives (KbPlanner.LandingOrder): Direct at dest only when that bumps nothing, else GenPlace's Near (which never
        /// picks a full cell); a landing on a pit cell goes to the pit floor beside it, then to the rim on the side its leg
        /// came from (`from`), never past the pit; then Near the origin. Only when all fail is it spawned with
        /// VanishOrMoveAside (fallback), and then the residents it moved are counted. residentsMoved is measured, not
        /// assumed: every item on the fallback cell before, compared after. Gas bounds every placement by its cap from takeoff.</summary>
        internal static Thing PlaceLanding(Thing t, IntVec3 dest, IntVec3 origin, IntVec3 from, Map map, out bool fallback, out int residentsMoved,
            out KbPlanner.KbPlace via, int landingCap = 0)
        {
            fallback = false;
            via = KbPlanner.KbPlace.Fallback;
            bool WithinCap(IntVec3 c) => KbPlanner.LandingWithinCap(c.x, c.z, origin.x, origin.z, landingCap);
            bool destWithinCap = WithinCap(dest);
            IntVec3 fallbackCell = destWithinCap ? dest : origin;
            var residents = new List<KeyValuePair<Thing, IntVec3>>();
            foreach (Thing h in fallbackCell.GetThingList(map))
            {
                if (h != t && h.def.category == ThingCategory.Item)
                {
                    residents.Add(new KeyValuePair<Thing, IntVec3>(h, h.Position));
                }
            }
            bool bump = WouldBump(t, dest, map);
#if RM_PROOFS
            bump &= !ProofDirectFirst;
#endif
            Thing placed = null;
            var grid = new RM_MapKbGrid(map, t, false);
            foreach (KbPlanner.KbPlace place in KbPlanner.LandingOrder(bump, RM_KnockbackCompat.IsSuperdeep(map, dest)))
            {
                via = place;
                if (place == KbPlanner.KbPlace.Fallback)
                {
                    // never vanish: no free cell anywhere near either end
                    if (!t.Spawned && !t.Destroyed)
                    {
                        placed = GenSpawn.Spawn(t, fallbackCell, map, WipeMode.VanishOrMoveAside);
                        fallback = true;
                    }
                    break;
                }
                if (place == KbPlanner.KbPlace.Direct)
                {
                    if (destWithinCap && GenPlace.TryPlaceThing(t, dest, map, ThingPlaceMode.Direct, out placed))
                    {
                        break;
                    }
                    continue;
                }
                Predicate<IntVec3> allow = null;
                if (place == KbPlanner.KbPlace.PitFloor || place == KbPlanner.KbPlace.NearRim)
                {
                    KbPlanner.KbPlace pl = place;
                    HashSet<long> pit = place == KbPlanner.KbPlace.PitFloor ? KbPlanner.PitAround(grid, dest.x, dest.z) : null;
                    allow = c => c.InBounds(map) && WithinCap(c)
                        && KbPlanner.PlaceAllows(pl, c.x, c.z, dest.x, dest.z, from.x, from.z, grid.At(c.x, c.z), pit);
                }
                else if (landingCap > 0)
                {
                    allow = WithinCap;
                }
                if (GenPlace.TryPlaceThing(t, place == KbPlanner.KbPlace.NearOrigin ? origin : dest, map, ThingPlaceMode.Near, out placed, null, allow))
                {
                    break;
                }
            }
            residentsMoved = 0;
            foreach (KeyValuePair<Thing, IntVec3> kv in residents)
            {
                // a resident a stack merged INTO stays put; one moved aside or destroyed counts
                if (kv.Key.Destroyed ? kv.Key != placed : (!kv.Key.Spawned || kv.Key.Position != kv.Value))
                {
                    residentsMoved++;
                }
            }
            return placed ?? t;
        }

        /// <summary>One throw. True when something actually moved. The game side of the plan: read the facts (Facts), let
        /// KbPlanner.Decide rule, apply what it says and journal it. No rule lives here.</summary>
        private bool Execute(KnockbackRequest r)
        {
            Thing t = Resolve(r.thing);
            if (t == null || !t.Spawned || t.Map != map || t.Destroyed)
            {
                RM_KnockbackJournal.Add("skip", r.explosionId, r.thing, "reason", "not_spawned");
                return false;
            }
            if (t is Building container)
            {
                return ThrowContainer(r, container);
            }
            Pawn pawn = t as Pawn;
            if (pawn == null && !(t is Corpse) && t.def.category != ThingCategory.Item)
            {
                return false;
            }
            KbFacts f = Facts(t, r, out int recoversAt, out int lastGasShove);
            KbSettings s = r.config != null ? RimMandrakeExplosiveKnockbackSettings.Kernel(r.config) : RimMandrakeExplosiveKnockbackSettings.Kernel(r.ownCap);
            KbPlan p = KbPlanner.Decide(f, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules(), s, new RM_MapKbWorld(map, t));
            float mass = f.mass;
            IntVec3 start = t.Position;
            switch (p.act)
            {
                case KbAct.Skip:
                    JournalSkip(r, t, p, recoversAt, lastGasShove);
                    return false;
                case KbAct.Absorb:
                    AbsorbByShield(r, pawn);
                    return false;
                case KbAct.None:
                    return false;
            }
            var dest = new IntVec3(p.res.destX, 0, p.res.destZ);
            if (RimMandrakeExplosiveKnockbackSettings.debugDrawVectors && Prefs.DevMode)
            {
                map.debugDrawer.FlashLine(start, dest, 120, SimpleColor.Orange);
#if RM_PROOFS
                RM_KnockbackProof.VectorDraws++;
#endif
            }
            if (pawn != null)
            {
                // bar collision_bruise_by_size: a throw stopped by a pawn bruises both by size (KbPlanner.Collide)
                Pawn met = p.res.hitOther ? new IntVec3(p.res.otherX, 0, p.res.otherZ).GetFirstPawn(map) : null;
                float metMass = met != null && met != pawn ? PawnMass(met) : 0f;
                KbPlanner.Collide(ref p.res, mass, metMass, p.s);
                // LaunchPawn, or Blocked: ThrowPawn deals the impact either way and journals a throw of no cells as blocked
                bool thrown = ThrowPawn(r, pawn, start, dest, p.res, mass, f, p.s, met, metMass);
                if (thrown && r.gas)
                {
                    gasShovedAt[pawn.thingIDNumber] = Find.TickManager.TicksGame;
                }
                return thrown;
            }
            KbKind kind = f.kind;
            int cells = p.cells, kernelCells = p.kernelCells;
            float impactFactor = r.config?.impactFactor ?? 1f;
            if (p.act == KbAct.Blocked)
            {
                RM_KnockbackJournal.Add("blocked", r.explosionId, t, "from", start, "planned", cells, "stop", p.res.stop.ToString());
                GoodsWallImpact(r, t, p.res, cells);
                return false;
            }
            int count = t.stackCount;
            KbLeg leg = p.first;
            var legDest = new IntVec3(leg.res.destX, 0, leg.res.destZ);
            if (p.wallFirst)
            {
                // a wall, door or the map edge right behind it: it takes the hit where it lies, then flies the bounce
                GoodsImpact(t, r.explosionId, p.res.stop, cells, impactFactor, r.instigator, "rebound");
                if (t.Destroyed || !t.Spawned)
                {
                    RM_KnockbackJournal.Add("blocked", r.explosionId, t, "from", start, "planned", cells, "stop", p.res.stop.ToString(), "destroyedAtWall", true);
                    return false;
                }
            }
            // RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: the stack flies to the very cell the plan chose; the carrier lands it with
            // the plan's own placing order and takes the wall impact where the flight is cut short
            int landingCap = r.gas ? p.s.maxCells : 0;
            RM_ThingFlyer_Knockback fl = RM_ThingFlyer_Knockback.Launch(t, map, start, leg.res, leg.dx, leg.dz, kind, mass, r.explosionId,
                impactFactor, r.instigator, p.wallFirst ? 1 : 0, landingCap);
            if (fl != null)
            {
                RM_KnockbackJournal.ItemMoves++;
                RM_KnockbackJournal.Add("item_move", r.explosionId, t, "kind", kind.ToString(), "from", start, "to", legDest,
                    "planned", cells, "cells", leg.res.cellsTravelled, "stop", leg.res.stop.ToString(), "mass", mass, "count", count,
                    "kernelCells", kernelCells, "wildCells", cells, "flying", true, "flyer", fl.thingIDNumber, "flightTicks", fl.TicksLeft,
                    "wallFirst", p.wallFirst, "hopped", p.hopped, "tumbled", p.tumbled);
                if (p.wallFirst)
                {
                    FleckMaker.ThrowDustPuff(start, map, 0.8f);
                    RM_KnockbackJournal.Add("item_rebound", r.explosionId, t, "at", start, "hit", p.res.stop.ToString(), "left", cells,
                        "cells", leg.res.cellsPlanned, "to", legDest, "bounce", 1);
                }
                return true;
            }
            if (!t.Spawned || p.wallFirst)
            {
                return false;
            }
            // the carrier could not take it (never seen live): the old instant move, same placing
            t.DeSpawn();
            Thing placed = PlaceLanding(t, dest, start, start, map, out bool fallback, out int bumped, out KbPlanner.KbPlace via, landingCap);
            FleckMaker.ThrowDustPuff(dest, map, 1f);
            RM_KnockbackJournal.ItemMoves++;
            RM_KnockbackJournal.Add("item_move", r.explosionId, t, "kind", kind.ToString(), "from", start, "to", placed.Spawned ? placed.Position : dest,
                "planned", cells, "cells", p.res.cellsTravelled, "stop", p.res.stop.ToString(), "mass", mass, "count", count, "flying", false,
                "kernelCells", kernelCells, "wildCells", cells,
                "residentsMoved", bumped, "spawnFallback", fallback, "place", via.ToString());
            GoodsWallImpact(r, placed, p.res, cells);
            return true;
        }

        private static KbBlast BlastOf(KnockbackRequest r)
        {
            return new KbBlast { id = r.explosionId, cx = r.centre.x, cz = r.centre.z, radius = r.radius, force = r.force, gas = r.gas };
        }

        /// <summary>The facts of one pawn, corpse or loose good, read now (KbFacts). recoversAt and lastGasShove are journal
        /// detail for the immune and gas_cooldown skips.</summary>
        private KbFacts Facts(Thing t, KnockbackRequest r, out int recoversAt, out int lastGasShove)
        {
            recoversAt = 0;
            lastGasShove = 0;
            var f = new KbFacts { spawned = true, thingId = t.thingIDNumber, x = t.Position.x, z = t.Position.z,
                onSuperdeep = RM_KnockbackCompat.IsSuperdeep(map, t.Position) };
            // on an intact cover, not beneath it (bar gas_shoves_pawn_on_pit_cover)
            f.onCover = f.onSuperdeep && RM_KnockbackCompat.CoverAt(map, t.Position) != null && !(t is Pawn under && RM_KnockbackCompat.IsBeneathCover(under));
            if (t is Pawn p)
            {
                f.kind = KbKind.Pawn;
                f.mass = PawnMass(p);
                f.dead = p.Dead;
                f.flying = p.Flying;
                f.inBed = p.InBed();
                f.carryingPawn = p.carryTracker?.CarriedThing is Pawn;
                f.downed = p.Downed;
                f.animal = p.RaceProps.Animal;
                f.mechanoid = p.RaceProps.IsMechanoid;
                f.shieldAbsorbed = r.shield != null;
                f.recovering = !CanLaunch(p, out recoversAt);
                if (gasShovedAt.TryGetValue(p.thingIDNumber, out lastGasShove))
                {
                    f.gasShovedAgo = Find.TickManager.TicksGame - lastGasShove;
                }
            }
            else if (t is Corpse corpse)
            {
                f.kind = KbKind.Corpse;
                Pawn inner = corpse.InnerPawn;
                f.mass = inner != null ? inner.GetStatValue(StatDefOf.Mass) : corpse.GetStatValue(StatDefOf.Mass);
            }
            else
            {
                f.kind = KbKind.Item;
                f.mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
                ReadStorage(f, t, map);
            }
            return f;
        }

        /// <summary>One journal "skip" line, with the detail each reason has always carried.</summary>
        private static void JournalSkip(KnockbackRequest r, Thing t, KbPlan p, int recoversAt, int lastGasShove)
        {
            switch (p.reason)
            {
                case "gas_cooldown":
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason, "last", lastGasShove);
                    break;
                case "immune":
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason, "recoversAt", recoversAt);
                    break;
                case "too_heavy_creature":
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason, "mass", p.mass, "limit", p.s.creatureMassLimit);
                    break;
                case "too_heavy":
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason, "mass", p.mass, "limit", p.s.lightMassLimit);
                    break;
                case "too_weak":
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason, "dist", p.dist, "mass", p.mass);
                    break;
                case "corpses_off":
                case "items_off":
                case "in_pit":
                case "flying_off":
                    if (p.reason == "in_pit" && t is Pawn)
                    {
                        RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason, "at", t.Position);
                        break;
                    }
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason);
                    break;
                default:
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", p.reason, "at", t.Position);
                    break;
            }
        }

        /// <summary>Owner, 2026-11-12 (RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE): "the whole crate/chest would
        /// go flying a bit, but their contents would remain inside and protected". The plan rules (KbPlanner.Decide, a
        /// container): a 1x1 closed container at or under closedContainerMassLimit (its own mass, the goods on its cell and
        /// what it holds inside) flies as ONE carrier with its goods; never into a pit, it comes to rest on the farthest free
        /// open cell of its path short of a person; with no such cell it jolts in place. One journal "container" line each.</summary>
        private bool ThrowContainer(KnockbackRequest r, Building b)
        {
            if (!RM_KnockbackCompat.IsClosedContainer(b))
            {
                return false;
            }
            IntVec3 start = b.Position;
            var goods = new List<Thing>();
            float mass = b.GetStatValue(StatDefOf.Mass);
            foreach (Thing h in start.GetThingList(map))
            {
                if (h != b && h.def.category == ThingCategory.Item && RimMandrakeExplosiveKnockbackSettings.closedContainerGuard)
                {
                    goods.Add(h);
                    mass += h.GetStatValue(StatDefOf.Mass) * h.stackCount;
                }
            }
            int held = 0;
            if (b is IThingHolder holder && holder.GetDirectlyHeldThings() is ThingOwner inside)
            {
                for (int i = 0; i < inside.Count; i++)
                {
                    mass += inside[i].GetStatValue(StatDefOf.Mass) * inside[i].stackCount;
                    held++;
                }
            }
            bool one = b.def.size.x == 1 && b.def.size.z == 1;
            var f = new KbFacts { container = true, spawned = true, thingId = b.thingIDNumber, x = start.x, z = start.z, mass = mass, oneByOne = one };
            KbSettings s = r.config != null ? RimMandrakeExplosiveKnockbackSettings.Kernel(r.config) : RimMandrakeExplosiveKnockbackSettings.Kernel(r.ownCap);
            KbPlan p = KbPlanner.Decide(f, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules(), s, new RM_MapKbWorld(map, b));
            if (p.act == KbAct.None)
            {
                return false; // the container shove is off
            }
            var to = new IntVec3(p.toX, 0, p.toZ);
            bool flew = false;
            if (p.act == KbAct.ContainerThrown)
            {
                flew = RM_ThingFlyer_Knockback.LaunchContainer(b, goods, map, start, to, p.travelled, p.dx, p.dz, mass, r.explosionId,
                    r.config?.impactFactor ?? 1f, r.instigator) != null;
            }
            if (!flew)
            {
                FleckMaker.ThrowDustPuff(start, map, 1f);
                StartJolt(b, p.dx, p.dz);
            }
            RM_KnockbackJournal.Add("container", r.explosionId, b, "action", flew ? "thrown" : "jolt", "from", start, "to", flew ? to : start,
                "planned", p.planned, "cells", flew ? p.travelled : 0, "mass", mass, "goods", goods.Count, "held", held, "oneByOne", one,
                "overLimit", p.overLimit);
            return flew;
        }

        // ── the drawn jolt (journal question 13; steward's decision 6) ─────────────
        /// <summary>Ticks a jolt is drawn, its largest offset (cells), and the most jolts drawn at once (a barrage is bounded).</summary>
        public const int JoltTicks = 20;
        public const float JoltAmplitude = 0.15f;
        public const int MaxJolts = 64;
        private readonly List<KeyValuePair<Thing, Vector3>> joltThing = new List<KeyValuePair<Thing, Vector3>>();
        private readonly List<int> joltStart = new List<int>();
#if RM_PROOFS
        /// <summary>Proof build: how many jolt frames were drawn and the largest offset drawn (cells), for the jolt's live check.</summary>
        internal static int JoltFrames;
        internal static float JoltMaxOffset;
        /// <summary>Per container (thingIDNumber): the largest offset its jolt was drawn at (RIMMANDRAKE_MEASURE_KNOCKBACK_JOLT_PER_CONTAINER_NOT_GHOST).</summary>
        internal static readonly Dictionary<int, float> JoltDrawn = new Dictionary<int, float>();
#endif

        /// <summary>A blocked closed container jolts in place: drawn shaking for JoltTicks, at most MaxJolts at once (the
        /// oldest gives way).</summary>
        private void StartJolt(Thing b, float dx, float dz)
        {
            if (joltThing.Count >= MaxJolts)
            {
                joltThing.RemoveAt(0);
                joltStart.RemoveAt(0);
            }
            joltThing.Add(new KeyValuePair<Thing, Vector3>(b, new Vector3(dx, 0f, dz)));
            joltStart.Add(Find.TickManager.TicksGame);
        }

        /// <summary>Draws each live jolt: the container's graphic again at its drawn position plus the bounded offset of
        /// RM_KnockbackMath.JoltOffset; a finished, despawned or destroyed one is dropped.</summary>
        public override void MapComponentUpdate()
        {
            if (joltThing.Count == 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            for (int i = joltThing.Count - 1; i >= 0; i--)
            {
                Thing b = joltThing[i].Key;
                int since = now - joltStart[i];
                if (b == null || b.Destroyed || !b.Spawned || b.Map != map || since >= JoltTicks || since < 0)
                {
                    joltThing.RemoveAt(i);
                    joltStart.RemoveAt(i);
                    continue;
                }
                Vector3 d = joltThing[i].Value;
                RM_KnockbackMath.JoltOffset(since, JoltTicks, JoltAmplitude, d.x, d.z, out float ox, out float oz);
                Vector3 at = b.DrawPos + new Vector3(ox, 0.01f, oz);
                b.Graphic?.Draw(at, b.Rotation, b);
#if RM_PROOFS
                JoltFrames++;
                JoltMaxOffset = Mathf.Max(JoltMaxOffset, Mathf.Sqrt(ox * ox + oz * oz));
                JoltDrawn.TryGetValue(b.thingIDNumber, out float drawn);
                JoltDrawn[b.thingIDNumber] = Mathf.Max(drawn, Mathf.Sqrt(ox * ox + oz * oz));
#endif
            }
        }

        /// <summary>A cell a thrown container may come to rest on: open ground (no wall, door, sandbag, water, pit or edge),
        /// no pawn, nothing standing there but filth, grass and the like.</summary>
        internal static bool ContainerCellFree(Map map, IntVec3 c, Thing self)
        {
            return c.InBounds(map) && KbPlanner.ContainerCellFree(new RM_MapKbWorld(map, self), c.x, c.z);
        }

        /// <summary>A cell a thrown container may not land on: anything standing there but filth, grass and the like.</summary>
        internal static bool Occupied(Map map, IntVec3 c)
        {
            if (!c.InBounds(map))
            {
                return true;
            }
            foreach (Thing th in c.GetThingList(map))
            {
                ThingCategory k = th.def.category;
                if (k == ThingCategory.Item || k == ThingCategory.Building || k == ThingCategory.Pawn
                    || (k == ThingCategory.Plant && th.def.passability != Traversability.Standable)
                    || th.def.IsBlueprint || th.def.IsFrame)
                {
                    return true;
                }
            }
            return false;
        }

        private static readonly AccessTools.FieldRef<CompShield, float> ShieldEnergy = AccessTools.FieldRefAccess<CompShield, float>("energy");
        private static readonly System.Reflection.MethodInfo ShieldBreak = AccessTools.Method(typeof(CompShield), "Break");

        /// <summary>Owner Q4: the shield that absorbed the blast absorbs the throw too, paying force x debit
        /// damage-equivalents; a strong throw can pop it (and a popped belt throws next time).</summary>
        private static void AbsorbByShield(KnockbackRequest r, Pawn p)
        {
            CompShield sh = r.shield;
            float before = ShieldEnergy(sh);
            float after = KbShield.EnergyAfter(before, r.force, RimMandrakeExplosiveKnockbackSettings.shieldDebitPerForce,
                sh.Props?.energyLossPerDamage ?? 0.033f);
            bool broke = false;
            if (sh.ShieldState == ShieldState.Active)
            {
                if (after < 0f)
                {
                    ShieldEnergy(sh) = 0f;
                    ShieldBreak?.Invoke(sh, null);
                    broke = true;
                }
                else
                {
                    ShieldEnergy(sh) = after;
                }
            }
            RM_KnockbackJournal.Add("skip", r.explosionId, p, "reason", "shield", "energyBefore", before, "energyAfter", Mathf.Max(0f, after),
                "broke", broke);
        }

        /// <summary>RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS (plan step 4): one clump of flammable gas burned at c. Not an
        /// explosion: nothing is damaged (so no pit cover breaks and no belt is drained), but every pawn, corpse and loose
        /// good within gasBurstRadius on a clear sight line is queued like a blast's, at full force, goods capped at gasBurstGoodsCells and people
        /// at one cell, shield belts ignored. Each burst has its own negative id. A journal "gas_burst" line each.</summary>
        /// <summary>A vent-gas cell bursts at most once in this many ticks (10 s), however often its fire relights drifted gas.</summary>
        private const int GasCellOnceTicks = 600;

        private readonly Dictionary<IntVec3, int> gasCellBurstTick = new Dictionary<IntVec3, int>();

        public static void GasBurst(Map map, IntVec3 c, Thing instigator, string source)
        {
            if (!RimMandrakeExplosiveKnockbackSettings.enabled || !RimMandrakeExplosiveKnockbackSettings.gasChain || map == null || !c.InBounds(map))
            {
                return;
            }
            RM_MapComponent_Knockback comp = map.GetComponent<RM_MapComponent_Knockback>();
            if (comp == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            // RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES (live 2026-11-16, the storeroom walk): gas drifting back
            // into a burned cell is relit by the Fire still burning there, and every Ignite was a burst, so a clump cell burst
            // twice 30-60 ticks apart. The bar is one burst per clump cell: the Cauldron's fire still burns, the cell does not
            // burst again inside GasCellOnceTicks. Not saved: a load mid-chain forgets it (one more burst at most).
            if (comp.gasCellBurstTick.TryGetValue(c, out int was) && now - was < GasCellOnceTicks)
            {
                RM_KnockbackJournal.Add("gas_reburst_skip", 0, null, "at", c, "after", now - was);
                return;
            }
            comp.gasCellBurstTick[c] = now;
            int id = -(++comp.gasBursts);
            float radius = Mathf.Max(0.9f, RimMandrakeExplosiveKnockbackSettings.gasBurstRadius);
            var cfg = new KbConfig { force = 1f, ownCap = Math.Max(1, RimMandrakeExplosiveKnockbackSettings.gasBurstGoodsCells), impactFactor = 0f, source = "gas",
                scaleOwnCap = false };
            int n = 0;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, radius, true))
            {
                // RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN: the sight line an explosion uses (DamageWorker.ExplosionCellsToHit)
                if (!cell.InBounds(map) || !GenSight.LineOfSight(c, cell, map, skipFirstCell: true))
                {
                    continue;
                }
                List<Thing> l = cell.GetThingList(map);
                for (int i = 0; i < l.Count; i++)
                {
                    Thing t = l[i];
                    if (t is Pawn || t is Corpse || t.def.category == ThingCategory.Item)
                    {
                        comp.Enqueue(new KnockbackRequest
                        {
                            explosionId = id, centre = c, radius = radius, damType = null, force = cfg.force, ownCap = cfg.ownCap,
                            config = cfg, shield = null, instigator = instigator, thing = t, takeoff = t.Position, tick = now, gas = true,
                        });
                        n++;
                    }
                }
            }
            RM_KnockbackJournal.Add("gas_burst", id, null, "at", c, "source", source, "radius", radius, "queued", n);
        }

        private bool ThrowPawn(KnockbackRequest r, Pawn p, IntVec3 start, IntVec3 dest, KbResult res, float mass, KbFacts f, KbSettings ks,
            Pawn met, float metMass)
        {
            // impact at LAUNCH (GPT #7/#11), then re-check before the flyer
            if (res.impact > 0f)
            {
                p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, res.impact, 0f, -1f, r.instigator));
            }
            if (res.hitOther && res.otherImpact > 0f && met != null && met != p)
            {
                met.TakeDamage(new DamageInfo(DamageDefOf.Blunt, res.otherImpact, 0f, -1f, r.instigator));
            }
            if (res.hitOther)
            {
                RM_KnockbackJournal.Add("bruise", r.explosionId, p, "how", "path", "other", met?.ThingID ?? "none", "otherId", met?.thingIDNumber ?? -1,
                    "mass", mass, "otherMass", metMass, "amount", res.impact, "otherAmount", res.otherImpact);
            }
            if (res.hitDoor && RimMandrakeExplosiveKnockbackSettings.doorsTakeDamage && res.impact > 0f)
            {
                Building door = new IntVec3(res.doorX, 0, res.doorZ).GetEdifice(map);
                door?.TakeDamage(new DamageInfo(DamageDefOf.Blunt, res.impact, 0f, -1f, r.instigator));
            }
            if (!res.Moved || p.Dead || !p.Spawned || p.Map != map)
            {
                RM_KnockbackJournal.Add("blocked", r.explosionId, p, "from", start, "planned", res.cellsPlanned, "stop", res.stop.ToString(),
                    "impact", res.impact, "otherImpact", res.otherImpact, "door", res.hitDoor);
                return false;
            }
            bool hose = RM_KnockbackCompat.DropCarriedHose(p);
            string carried = ThrowCarried(r, p, f, start, ks);
            ThingDef def = RM_KnockbackDefOf.RM_PawnFlyer_Knockback;
            int lo = Mathf.Max(0, RimMandrakeExplosiveKnockbackSettings.landingStunMin);
            def.pawnFlyer.stunDurationTicksRange = new IntRange(lo, Mathf.Max(lo, RimMandrakeExplosiveKnockbackSettings.landingStunMax));
            RM_Patch_PawnFlyer_KnockbackLanding.RememberHaul(p);    // back to its haul after landing (bar pawn_flight_arc)
            RM_Patch_PawnFlyer_KnockbackLanding.RememberThrow(p, r.explosionId); // a blast-thrown landing breaks a cover (sc_pit_fall)
            RememberImpactFactor(p, ks?.impactFactor ?? 1f);                      // a landing on a pawn bruises by this blast's factor
#if RM_PROOFS
            long takeoffT0 = System.Diagnostics.Stopwatch.GetTimestamp();
#endif
            // bar carried_thing_own_arc: the hands are empty here (ThrowCarried), so the pawn flies alone
            PawnFlyer flyer = PawnFlyer.MakeFlyer(def, p, dest, null, null, flyWithCarriedThing: false);
            if (flyer == null)
            {
                return false;
            }
            GenSpawn.Spawn(flyer, start, map);
#if RM_PROOFS
            RM_FrameProbe.PawnTakeoffMs += RM_FrameProbe.MsSince(takeoffT0);
            RM_FrameProbe.Takeoffs++;
#endif
            RM_KnockbackJournal.Launches++;
            RM_KnockbackJournal.Add("launch", r.explosionId, p, "from", start, "to", dest, "planned", res.cellsPlanned,
                "cells", res.cellsTravelled, "stop", res.stop.ToString(), "impact", res.impact, "otherImpact", res.otherImpact,
                "door", res.hitDoor, "mass", mass, "hoseDropped", hose, "carried", carried, "onCover", f != null && f.onCover, "gas", r.gas,
                "hitOther", res.hitOther, "faction", p.Faction?.def?.defName ?? "none");
            return true;
        }

        /// <summary>Bar carried_thing_own_arc: what a thrown pawn carries leaves its hands at the blast. Its own plan
        /// (KbPlanner.Carried) either flies it on a flight of its own, straight from the hands into a goods flyer, or leaves it
        /// on the start cell (too heavy, switched off, a pit). Returns the thing's id, or "none". A carried pawn never gets
        /// here (its carrier is skipped, carrying_pawn); a hose end was dropped just before (bar hose_drops_at_takeoff).</summary>
        private string ThrowCarried(KnockbackRequest r, Pawn p, KbFacts f, IntVec3 start, KbSettings ks)
        {
            Thing held = p.carryTracker?.CarriedThing;
            if (held == null || held is Pawn)
            {
                return "none";
            }
            string id = held.ThingID;
            int count = held.stackCount;
            KbKind kind = held is Corpse ? KbKind.Corpse : KbKind.Item;
            float cm = held is Corpse dead && dead.InnerPawn != null ? dead.InnerPawn.GetStatValue(StatDefOf.Mass) : held.GetStatValue(StatDefOf.Mass) * held.stackCount;
            KbSettings cs = r.config != null ? RimMandrakeExplosiveKnockbackSettings.Kernel(r.config) : RimMandrakeExplosiveKnockbackSettings.Kernel(r.ownCap);
            KbFacts carrier = f ?? new KbFacts { spawned = true, thingId = p.thingIDNumber, x = start.x, z = start.z };
            KbPlan cp = KbPlanner.Carried(carrier, held.thingIDNumber, kind, cm, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules(), cs,
                new RM_MapKbWorld(map, p));
            KbPlanner.CarriedRest(cp, carrier, out int rx, out int rz);
            RM_ThingFlyer_Knockback fl = null;
            if (cp.act == KbAct.ThrowGoods)
            {
                KbLeg leg = cp.first;
                fl = RM_ThingFlyer_Knockback.LaunchFromHands(p, held, map, start, leg.res, leg.dx, leg.dz, kind, cm, r.explosionId,
                    r.config?.impactFactor ?? 1f, r.instigator, cp.wallFirst ? 1 : 0, r.gas ? cp.s.maxCells : 0);
            }
            bool dropped = false;
            if (fl == null && p.carryTracker?.CarriedThing == held)
            {
                dropped = p.carryTracker.TryDropCarriedThing(start, ThingPlaceMode.Near, out Thing _);
            }
            RM_KnockbackJournal.Add("carried_throw", r.explosionId, p, "thing", id, "thingId", held.thingIDNumber, "count", count, "kind", kind.ToString(),
                "mass", cm, "act", fl != null ? "thrown" : dropped ? "dropped" : "held", "reason", cp.act == KbAct.Skip ? cp.reason : cp.act.ToString(),
                "from", start, "to", new IntVec3(rx, 0, rz), "planned", cp.cells, "flyer", fl?.thingIDNumber ?? -1, "flightTicks", fl?.TicksLeft ?? 0,
                "wallFirst", cp.wallFirst);
            if (fl != null)
            {
                RM_KnockbackJournal.ItemMoves++;
            }
            return id;
        }
    }
}
