using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
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
        private readonly KbDedupe dedupe = new KbDedupe();
        private readonly KbTickBudget itemBudget = new KbTickBudget();
        private readonly Dictionary<int, int> launchedPerExplosion = new Dictionary<int, int>();
        private int dedupeTick = -1;

        public RM_MapComponent_Knockback(Map map) : base(map)
        {
        }

        public void Enqueue(KnockbackRequest r)
        {
            int now = Find.TickManager.TicksGame;
            if (now - dedupeTick > 600)
            {
                // an explosion's wave lasts a few ticks; ids never repeat, so old keys are dead weight
                dedupe.Clear();
                launchedPerExplosion.Clear();
                dedupeTick = now;
            }
            if (!dedupe.TryAdd(r.explosionId, r.thing.thingIDNumber))
            {
                return;
            }
            queue.Add(r);
            RM_KnockbackJournal.Add("request", r.explosionId, r.thing, "from", r.takeoff, "centre", r.centre,
                "radius", r.radius, "force", r.force, "damType", r.damType?.defName);
        }

        public override void MapComponentTick()
        {
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
                launchedPerExplosion.TryGetValue(id, out int used);
                int cap = Math.Max(0, RimMandrakeExplosiveKnockbackSettings.maxThrowsPerExplosion - used);
                List<KbCandidate> kept = RM_KnockbackMath.Prioritise(cands, cap);
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
                foreach (KbCandidate c in kept)
                {
                    try
                    {
                        if (Execute(g[c.index]))
                        {
                            launchedPerExplosion[id] = (launchedPerExplosion.TryGetValue(id, out int n) ? n : 0) + 1;
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

        /// <summary>One throw. True when something actually moved.</summary>
        private bool Execute(KnockbackRequest r)
        {
            Thing t = Resolve(r.thing);
            if (t == null || !t.Spawned || t.Map != map || t.Destroyed)
            {
                RM_KnockbackJournal.Add("skip", r.explosionId, r.thing, "reason", "not_spawned");
                return false;
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
                Building ed = t.Position.GetEdifice(map);
                if (ed is Building_Storage || (ed != null && ed.def.building != null && ed.def.building.fixedStorageSettings != null))
                {
                    RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "in_storage");
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
            KbSettings s = RimMandrakeExplosiveKnockbackSettings.Kernel(r.ownCap);
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
                return ThrowPawn(r, pawn, start, dest, res, mass);
            }
            if (!res.Moved)
            {
                RM_KnockbackJournal.Add("blocked", r.explosionId, t, "from", start, "planned", cells, "stop", res.stop.ToString());
                return false;
            }
            if (!itemBudget.TryTake(Find.TickManager.TicksGame, RimMandrakeExplosiveKnockbackSettings.maxItemThrowsPerMapTick))
            {
                RM_KnockbackJournal.Add("skip", r.explosionId, t, "reason", "cap_per_tick");
                return false;
            }
            int count = t.stackCount;
            t.DeSpawn();
            if (!GenPlace.TryPlaceThing(t, dest, map, ThingPlaceMode.Direct, out Thing placed)
                && !GenPlace.TryPlaceThing(t, dest, map, ThingPlaceMode.Near, out placed))
            {
                GenPlace.TryPlaceThing(t, start, map, ThingPlaceMode.Near, out placed);
            }
            FleckMaker.ThrowDustPuff(dest, map, 1f);
            RM_KnockbackJournal.ItemMoves++;
            RM_KnockbackJournal.Add("item_move", r.explosionId, t, "kind", kind.ToString(), "from", start, "to", placed?.Position ?? dest,
                "planned", cells, "cells", res.cellsTravelled, "stop", res.stop.ToString(), "mass", mass, "count", count);
            return true;
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
