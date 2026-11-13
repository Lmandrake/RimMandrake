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
                if (RM_KnockbackCompat.CoverAt(map, c) != null)
                {
                    return KbCell.CoveredPit;
                }
                if (forPawn && OtherPawnAt(c))
                {
                    return KbCell.Pawn; // a pit cell that is occupied counts as blocked (GPT #15)
                }
                return KbCell.Pit;
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

        private bool OtherPawnAt(IntVec3 c)
        {
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Pawn p && p != self)
                {
                    return true;
                }
            }
            return false;
        }
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
                "shieldAbsorbed", r.shield != null);
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
            Building ed = t.Position.GetEdifice(map);
            if (ed == null)
            {
                return null;
            }
            bool closed = RM_KnockbackCompat.IsClosedContainer(ed);
            bool storage = closed || ed is Building_Storage || (ed.def.building != null && ed.def.building.fixedStorageSettings != null);
            if (!RM_KnockbackMath.GoodsHeld(storage, closed, RimMandrakeExplosiveKnockbackSettings.openStorageProtectsGoods))
            {
                return null;
            }
            return closed ? "closed_container" : "in_storage";
        }

        /// <summary>Called from the explosion prefix BEFORE the blast damages the item: will Execute throw it (same gates,
        /// same kernel, measured now)? Pit landing and path blocks are not predicted; a stack spared and then blocked is
        /// still spared.</summary>
        public static bool ItemWillBeThrown(Thing t, Explosion explosion, KbConfig cfg)
        {
            Map map = explosion.Map;
            if (map == null || !t.Spawned || !RimMandrakeExplosiveKnockbackSettings.throwItems || HeldReason(t, map) != null
                || RM_KnockbackCompat.IsSuperdeep(map, t.Position))
            {
                return false;
            }
            KbSettings s = RimMandrakeExplosiveKnockbackSettings.Kernel(cfg);
            float mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
            if (!RM_KnockbackMath.Eligible(KbKind.Item, mass, 0f, s))
            {
                return false;
            }
            float dist = (t.Position - explosion.Position).LengthHorizontal;
            return RM_KnockbackMath.ThrowCells(dist, explosion.radius, cfg.force, mass, s) > 0;
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
            return map != null && t.Spawned && t.def.category == ThingCategory.Item && RM_KnockbackCompat.IsClosedContainer(t.Position.GetEdifice(map));
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

        /// <summary>Lands a thrown stack (instant move and carrier alike) without ever moving a resident: Direct at dest only
        /// when that bumps nothing, else Near dest (GenPlace's Near never picks a full cell), else Near the origin. Only when
        /// all three fail is it spawned with VanishOrMoveAside (fallback), and then the residents it moved are counted.
        /// residentsMoved is measured, not assumed: every item on dest before, compared after.</summary>
        internal static Thing PlaceLanding(Thing t, IntVec3 dest, IntVec3 origin, Map map, out bool fallback, out int residentsMoved)
        {
            fallback = false;
            var residents = new List<KeyValuePair<Thing, IntVec3>>();
            foreach (Thing h in dest.GetThingList(map))
            {
                if (h != t && h.def.category == ThingCategory.Item)
                {
                    residents.Add(new KeyValuePair<Thing, IntVec3>(h, h.Position));
                }
            }
            bool direct = !WouldBump(t, dest, map);
#if RM_PROOFS
            direct |= ProofDirectFirst;
#endif
            Thing placed = null;
            if (!(direct && GenPlace.TryPlaceThing(t, dest, map, ThingPlaceMode.Direct, out placed))
                && !GenPlace.TryPlaceThing(t, dest, map, ThingPlaceMode.Near, out placed)
                && !GenPlace.TryPlaceThing(t, origin, map, ThingPlaceMode.Near, out placed))
            {
                // never vanish: no free cell anywhere near either end
                if (!t.Spawned && !t.Destroyed)
                {
                    placed = GenSpawn.Spawn(t, dest, map, WipeMode.VanishOrMoveAside);
                    fallback = true;
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

        /// <summary>One throw. True when something actually moved.</summary>
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
            KbKind kind;
            float mass, bodySize;
            Pawn pawn = t as Pawn;
            if (pawn != null)
            {
                string why = PawnSkipReason(pawn);
                if (why != null)
                {
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", why, "at", t.Position);
                    return false;
                }
                kind = KbKind.Pawn;
                mass = Mathf.Max(1f, pawn.GetStatValue(StatDefOf.Mass) - MassUtility.InventoryMass(pawn));
                bodySize = pawn.BodySize;
            }
            else if (t is Corpse corpse)
            {
                if (!RimMandrakeExplosiveKnockbackSettings.throwCorpses)
                {
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "corpses_off");
                    return false;
                }
                kind = KbKind.Corpse;
                Pawn inner = corpse.InnerPawn;
                mass = inner != null ? inner.GetStatValue(StatDefOf.Mass) : corpse.GetStatValue(StatDefOf.Mass);
                bodySize = inner?.BodySize ?? 1f;
            }
            else if (t.def.category == ThingCategory.Item)
            {
                if (!RimMandrakeExplosiveKnockbackSettings.throwItems)
                {
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "items_off");
                    return false;
                }
                string held = HeldReason(t, map);
                if (held != null)
                {
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", held, "at", t.Position);
                    return false;
                }
                kind = KbKind.Item;
                mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
                bodySize = 0f;
            }
            else
            {
                return false;
            }
            if (kind != KbKind.Pawn && RM_KnockbackCompat.IsSuperdeep(map, t.Position))
            {
                RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "in_pit");
                return false;
            }
            KbSettings s = r.config != null ? RimMandrakeExplosiveKnockbackSettings.Kernel(r.config) : RimMandrakeExplosiveKnockbackSettings.Kernel(r.ownCap);
            if (pawn != null && r.gas)
            {
                // burning gas shoves a person one cell, at most once per gasPawnCooldownTicks (plan step 4)
                int now = Find.TickManager.TicksGame;
                if (gasShovedAt.TryGetValue(pawn.thingIDNumber, out int last) && now - last < RimMandrakeExplosiveKnockbackSettings.gasPawnCooldownTicks)
                {
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "gas_cooldown", "last", last);
                    return false;
                }
                s.maxCells = Math.Min(s.maxCells, 1);
            }
            if (pawn != null && r.shield != null && RimMandrakeExplosiveKnockbackSettings.shieldsAbsorbThrow)
            {
                AbsorbByShield(r, pawn);
                return false;
            }
            if (pawn != null && !CanLaunch(pawn, out int recoversAt))
            {
                RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "immune", "recoversAt", recoversAt);
                return false;
            }
            if (!RM_KnockbackMath.Eligible(kind, mass, bodySize, s))
            {
                RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", bodySize >= s.immuneBodySize ? "too_big" : "too_heavy",
                    "mass", mass, "bodySize", bodySize);
                return false;
            }
            IntVec3 start = t.Position;
            float dist = (start - r.centre).LengthHorizontal;
            int cells = RM_KnockbackMath.ThrowCells(dist, r.radius, r.force, mass, s);
            if (cells <= 0)
            {
                RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "too_weak", "dist", dist, "mass", mass);
                return false;
            }
            float dx, dz;
            if (start == r.centre)
            {
                RM_KnockbackMath.EpicentreDir(r.explosionId, t.thingIDNumber, out dx, out dz);
            }
            else
            {
                dx = start.x - r.centre.x;
                dz = start.z - r.centre.z;
            }
            KbResult res = RM_KnockbackMath.Resolve(new RM_MapKbGrid(map, t, kind == KbKind.Pawn), start.x, start.z, dx, dz,
                cells, kind, mass, s);
            var dest = new IntVec3(res.destX, 0, res.destZ);
            if (RimMandrakeExplosiveKnockbackSettings.debugDrawVectors && Prefs.DevMode)
            {
                map.debugDrawer.FlashLine(start, dest, 120, SimpleColor.Orange);
            }
            if (pawn != null)
            {
                bool thrown = ThrowPawn(r, pawn, start, dest, res, mass);
                if (thrown && r.gas)
                {
                    gasShovedAt[pawn.thingIDNumber] = Find.TickManager.TicksGame;
                }
                return thrown;
            }
            if (!res.Moved)
            {
                RM_KnockbackJournal.Add("blocked", r.explosionId, t, "from", start, "planned", cells, "stop", res.stop.ToString());
                GoodsWallImpact(r, t, res, cells);
                return false;
            }
            int count = t.stackCount;
            if (RimMandrakeExplosiveKnockbackSettings.flyingGoods)
            {
                // RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: the stack flies to the very cell the instant move would choose; the
                // carrier lands it with the same GenPlace calls and takes the wall impact where the flight is cut short
                RM_ThingFlyer_Knockback f = RM_ThingFlyer_Knockback.Launch(t, map, start, res, dx, dz, kind, mass, r.explosionId,
                    r.config?.impactFactor ?? 1f, r.instigator);
                if (f != null)
                {
                    RM_KnockbackJournal.ItemMoves++;
                    RM_KnockbackJournal.Add("item_move", r.explosionId, t, "kind", kind.ToString(), "from", start, "to", dest,
                        "planned", cells, "cells", res.cellsTravelled, "stop", res.stop.ToString(), "mass", mass, "count", count,
                        "flying", true, "flyer", f.thingIDNumber, "flightTicks", f.TicksLeft);
                    return true;
                }
                if (!t.Spawned)
                {
                    return false;
                }
            }
            t.DeSpawn();
            Thing placed = PlaceLanding(t, dest, start, map, out bool fallback, out int bumped);
            FleckMaker.ThrowDustPuff(dest, map, 1f);
            RM_KnockbackJournal.ItemMoves++;
            RM_KnockbackJournal.Add("item_move", r.explosionId, t, "kind", kind.ToString(), "from", start, "to", placed.Spawned ? placed.Position : dest,
                "planned", cells, "cells", res.cellsTravelled, "stop", res.stop.ToString(), "mass", mass, "count", count, "flying", false,
                "residentsMoved", bumped, "spawnFallback", fallback);
            GoodsWallImpact(r, placed, res, cells);
            return true;
        }

        /// <summary>Owner, 2026-11-12 (RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE): "the whole crate/chest would
        /// go flying a bit, but their contents would remain inside and protected". A 1x1 closed container at or under
        /// closedContainerMassLimit (its own mass, the goods on its cell and what it holds inside) flies as ONE carrier
        /// with its goods: the kernel's item throw at that mass, so shorter than loose goods; never into a pit, it comes to
        /// rest on the farthest free open cell of its path short of a person; with no such cell it jolts in place. One
        /// journal "container" line each.</summary>
        private bool ThrowContainer(KnockbackRequest r, Building b)
        {
            if (!RimMandrakeExplosiveKnockbackSettings.shoveClosedContainers || !RM_KnockbackCompat.IsClosedContainer(b))
            {
                return false;
            }
            IntVec3 start = b.Position;
            float dx, dz;
            if (start == r.centre)
            {
                RM_KnockbackMath.EpicentreDir(r.explosionId, b.thingIDNumber, out dx, out dz);
            }
            else
            {
                dx = start.x - r.centre.x;
                dz = start.z - r.centre.z;
            }
            bool one = b.def.size.x == 1 && b.def.size.z == 1;
            var goods = new List<Thing>();
            float mass = b.GetStatValue(StatDefOf.Mass);
            foreach (Thing h in start.GetThingList(map))
            {
                if (h != b && h.def.category == ThingCategory.Item)
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
            KbSettings s = r.config != null ? RimMandrakeExplosiveKnockbackSettings.Kernel(r.config) : RimMandrakeExplosiveKnockbackSettings.Kernel(r.ownCap);
            s.intoPits = false; // an open pit is a wall for a container's path
            float dist = (start - r.centre).LengthHorizontal;
            float limit = RimMandrakeExplosiveKnockbackSettings.closedContainerMassLimit;
            int planned = one && mass <= limit ? RM_KnockbackMath.ThrowCells(dist, r.radius, r.force, mass, s) : 0;
            IntVec3 to = start;
            int travelled = 0;
            if (planned > 0)
            {
                var grid = new RM_MapKbGrid(map, b, true);
                KbResult res = RM_KnockbackMath.Resolve(grid, start.x, start.z, dx, dz, planned, KbKind.Item, mass, s);
                List<(int x, int z)> path = RM_KnockbackMath.Line(start.x, start.z, dx, dz, res.cellsTravelled);
                for (int i = 0; i < path.Count; i++)
                {
                    var c = new IntVec3(path[i].x, 0, path[i].z);
                    if (c.GetFirstPawn(map) != null)
                    {
                        break; // it does not fly through a person
                    }
                    if (ContainerCellFree(map, c, b))
                    {
                        to = c;
                        travelled = i + 1;
                    }
                }
            }
            bool flew = false;
            if (to != start)
            {
                flew = RM_ThingFlyer_Knockback.LaunchContainer(b, goods, map, start, to, travelled, dx, dz, mass, r.explosionId,
                    r.config?.impactFactor ?? 1f, r.instigator) != null;
            }
            if (!flew)
            {
                FleckMaker.ThrowDustPuff(start, map, 1f);
            }
            RM_KnockbackJournal.Add("container", r.explosionId, b, "action", flew ? "thrown" : "jolt", "from", start, "to", flew ? to : start,
                "planned", planned, "cells", flew ? travelled : 0, "mass", mass, "goods", goods.Count, "held", held, "oneByOne", one,
                "overLimit", mass > limit);
            return flew;
        }

        /// <summary>A cell a thrown container may come to rest on: open ground (no wall, door, sandbag, water, pit or edge),
        /// no pawn, nothing standing there but filth, grass and the like.</summary>
        internal static bool ContainerCellFree(Map map, IntVec3 c, Thing self)
        {
            return c.InBounds(map) && RM_KnockbackMath.ShoveCellFree(new RM_MapKbGrid(map, self, true).At(c.x, c.z), Occupied(map, c))
                && !RM_KnockbackCompat.IsSuperdeep(map, c);
        }

        /// <summary>A cell a thrown container may not land on: anything standing there but filth, grass and the like.</summary>
        private static bool Occupied(Map map, IntVec3 c)
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

        private static string PawnSkipReason(Pawn p)
        {
            if (p.Dead)
            {
                return "dead";
            }
            if (p.Flying)
            {
                return "flying";
            }
            if (p.InBed())
            {
                return "in_bed";
            }
            if (p.carryTracker?.CarriedThing is Pawn)
            {
                return "carrying_pawn";
            }
            if (p.Downed && !RimMandrakeExplosiveKnockbackSettings.throwDowned)
            {
                return "downed_off";
            }
            if (p.RaceProps.Animal && !RimMandrakeExplosiveKnockbackSettings.throwAnimals)
            {
                return "animals_off";
            }
            if (p.RaceProps.IsMechanoid && !RimMandrakeExplosiveKnockbackSettings.throwMechanoids)
            {
                return "mechanoids_off";
            }
            if (RM_KnockbackCompat.IsSuperdeep(p.Map, p.Position))
            {
                return "in_pit"; // GPT #1 + "you can't climb out. Period."
            }
            return null;
        }

        /// <summary>RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS (plan step 4): one clump of flammable gas burned at c. Not an
        /// explosion: nothing is damaged (so no pit cover breaks and no belt is drained), but every pawn, corpse and loose
        /// good within gasBurstRadius is queued like a blast's, at full force, goods capped at gasBurstGoodsCells and people
        /// at one cell, shield belts ignored. Each burst has its own negative id. A journal "gas_burst" line each.</summary>
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
            int id = -(++comp.gasBursts);
            float radius = Mathf.Max(0.9f, RimMandrakeExplosiveKnockbackSettings.gasBurstRadius);
            var cfg = new KbConfig { force = 1f, ownCap = Math.Max(1, RimMandrakeExplosiveKnockbackSettings.gasBurstGoodsCells), impactFactor = 0f, source = "gas" };
            int now = Find.TickManager.TicksGame;
            int n = 0;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, radius, true))
            {
                if (!cell.InBounds(map))
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

        private bool ThrowPawn(KnockbackRequest r, Pawn p, IntVec3 start, IntVec3 dest, KbResult res, float mass)
        {
            // impact at LAUNCH (GPT #7/#11), then re-check before the flyer
            if (res.impact > 0f)
            {
                p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, res.impact, 0f, -1f, r.instigator));
            }
            if (res.hitOther && res.otherImpact > 0f)
            {
                Pawn other = new IntVec3(res.otherX, 0, res.otherZ).GetFirstPawn(map);
                other?.TakeDamage(new DamageInfo(DamageDefOf.Blunt, res.otherImpact, 0f, -1f, r.instigator));
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
            ThingDef def = RM_KnockbackDefOf.RM_PawnFlyer_Knockback;
            int lo = Mathf.Max(0, RimMandrakeExplosiveKnockbackSettings.landingStunMin);
            def.pawnFlyer.stunDurationTicksRange = new IntRange(lo, Mathf.Max(lo, RimMandrakeExplosiveKnockbackSettings.landingStunMax));
            PawnFlyer flyer = PawnFlyer.MakeFlyer(def, p, dest, null, null, flyWithCarriedThing: true);
            if (flyer == null)
            {
                return false;
            }
            GenSpawn.Spawn(flyer, start, map);
            RM_KnockbackJournal.Launches++;
            RM_KnockbackJournal.Add("launch", r.explosionId, p, "from", start, "to", dest, "planned", res.cellsPlanned,
                "cells", res.cellsTravelled, "stop", res.stop.ToString(), "impact", res.impact, "otherImpact", res.otherImpact,
                "door", res.hitDoor, "mass", mass, "hoseDropped", hose, "faction", p.Faction?.def?.defName ?? "none");
            return true;
        }
    }
}
