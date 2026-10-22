using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// FALLEN_WIRE_SHOCK_1 (GS-2 + X-7). A live fallen wire is dangerous to everyone, colonists included.
    /// Owner ruling, typed on the card 2026-10-08: "doesn't have to be instantly lethal. Death should be rare,
    /// instead it knocks people out and throws them back a little (more realistic). Only people with weak heart
    /// conditions or existing heart damage get taken out."
    ///
    /// Shock: a flesh pawn on a cell a live fallen strand lies across is thrown back a cell or two away from the
    /// wire and knocked out (RM_FallenWireShock caps Consciousness, so vanilla downs it). A pawn with a weak
    /// heart (vanilla HeartArteryBlockage, an ongoing HeartAttack, or a damaged natural heart) instead gets
    /// vanilla HeartAttack at its lethal severity: the death reads as a heart attack.
    ///
    /// Fire: a live end lying in spilled fuel lights it. Vanilla Filth_Fuel on the tip cell, or FlowWorks'
    /// burnable liquid through a soft reflection lookup of RM_MapComponent_Excavation.LiquidFire.IgniteNow, so
    /// this mod needs nothing from FlowWorks and a missing or renamed member just turns that half off.
    ///
    /// Contact cells are rebuilt on the aerial component's 250-tick sweep (that is when liveness and lays are
    /// refreshed); pawns are checked every <see cref="CheckInterval"/> ticks so a pawn walking across a wire is
    /// caught. Numbers are PROVISIONAL.
    ///
    /// The colonist on the re-string job (design 2.6) is not shocked by the wires of the cut he is sent to splice: he walks to
    /// the cut, where the live half lies, and handles that wire as the job's own work (GSS_RESTRING_DIAGNOSE_FIXER_GETS_ZAPPED:
    /// L1 2026-10-15 downed him 2/2). Any other live wire, on his way there or anywhere else, shocks him (<see cref="OnOwnCut"/>).
    /// </summary>
    public static class RM_FallenWireShock
    {
        // GPT deep review 2026-10-22 #4: 20 let a pawn walking at normal speed (~13 ticks a cell) cross a contact between two
        // checks; 4 catches anything slower than 4 ticks a cell. The contact set is small, so the extra checks are cheap.
        public const int CheckInterval = 4;
        /// <summary>Chance per 250-tick sweep that a live end in fuel lights it. PROVISIONAL.</summary>
        public const float IgniteChancePerSweep = 0.35f;

        private static HediffDef shockDef, heartAttackDef, arteryBlockageDef;
        private static bool defsResolved;

        public static int shocks, kills, ignitions;

        private static void ResolveDefs()
        {
            if (defsResolved) return;
            defsResolved = true;
            shockDef = DefDatabase<HediffDef>.GetNamedSilentFail("RM_FallenWireShock");
            heartAttackDef = DefDatabase<HediffDef>.GetNamedSilentFail("HeartAttack");
            arteryBlockageDef = DefDatabase<HediffDef>.GetNamedSilentFail("HeartArteryBlockage");
        }

        /// <summary>Contact cells (cell index -> the live end's tip) of every live fallen strand on the map.</summary>
        public static void RebuildContacts(RM_MapComponent_Aerial aerial, Map map, Dictionary<int, IntVec3> contacts, List<IntVec3> tips)
        {
            contacts.Clear();
            tips.Clear();
            if (!AerialSettings.enabled || (!AerialSettings.fallenWireShock && !AerialSettings.fallenWireIgnites)) return;
            foreach (CompAerialAnchor a in aerial.Anchors)
            {
                if (a.fallen.Count == 0 || !(aerial.FallenLiveCached(a) ?? false)) continue;
                IntVec3 home = a.Position;
                foreach (FallenCord f in a.fallen)
                {
                    foreach (FallenLay l in aerial.Lays(a, f))
                    {
                        if (!l.TipGrounded) continue;           // the whole cable still hangs: nothing touches the ground
                        IntVec3 tip = CellOf(l.Tip);
                        if (tip.InBounds(map)) tips.Add(tip);
                        foreach (P2 p in AerialMath.GroundPts(l))  // GPT pre-release C3: never the hanging part (thin air)
                        {
                            IntVec3 c = CellOf(p);
                            if (c == home || !c.InBounds(map)) continue;
                            contacts[map.cellIndices.CellToIndex(c)] = tip;
                        }
                        if (tip != home && tip.InBounds(map)) contacts[map.cellIndices.CellToIndex(tip)] = tip;
                    }
                }
            }
            ExternalContacts(map, contacts, tips);
        }

        // ------------------------------------------------------------------ live wires another mod dropped
        /// <summary>PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 3: other mods' live fallen wires (FlowWorks: a powered power cord a
        /// collapsing bridge deck dropped into the hole). Each source answers, for a map, its live contact cells (cell -> that
        /// wire's live tip); they shock and ignite exactly like an aerial strand, under the same settings. The types are
        /// BCL + Verse only, so a caller needs no reference to this assembly: FlowWorks finds this by name (soft reflection),
        /// the mirror of how this file finds FlowWorks' liquid fire. The source owns liveness; this side never caches it beyond
        /// one contact rebuild.</summary>
        private static readonly List<Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>>> liveWireSources =
            new List<Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>>>();

        /// <summary>State read: contact cells the external sources gave at the last rebuild (all maps).</summary>
        public static int externalContacts;
        public static int LiveWireSourceCount => liveWireSources.Count;

        /// <summary>Public entry point for another mod's live fallen wires. Registering the same delegate twice is a no-op.</summary>
        public static void RegisterLiveWireSource(Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>> source)
        {
            if (source != null && !liveWireSources.Contains(source)) liveWireSources.Add(source);
        }

        /// <summary>Public entry point: a source's live wires on this map changed; rebuild the contacts on the next tick.</summary>
        public static void LiveWiresChanged(Map map)
        {
            map?.GetComponent<RM_MapComponent_Aerial>()?.MarkContactsDirty();
        }

        private static void ExternalContacts(Map map, Dictionary<int, IntVec3> contacts, List<IntVec3> tips)
        {
            externalContacts = 0;
            for (int s = 0; s < liveWireSources.Count; s++)
            {
                try
                {
                    IEnumerable<KeyValuePair<IntVec3, IntVec3>> got = liveWireSources[s](map);
                    if (got == null) continue;
                    foreach (KeyValuePair<IntVec3, IntVec3> kv in got)
                    {
                        if (!kv.Key.InBounds(map)) continue;
                        contacts[map.cellIndices.CellToIndex(kv.Key)] = kv.Value.InBounds(map) ? kv.Value : kv.Key;
                        externalContacts++;
                        if (kv.Value.InBounds(map) && !tips.Contains(kv.Value)) tips.Add(kv.Value);
                    }
                }
                catch (Exception e)
                {
                    Log.ErrorOnce("[GimmeSomeSlack] an external live-wire source threw; its wires are skipped: " + e, 0x6A5E8 + s);
                }
            }
        }

        private static IntVec3 CellOf(P2 p) => new IntVec3((int)Math.Floor(p.X), 0, (int)Math.Floor(p.Z));

        /// <summary>Shock every flesh pawn standing on a contact cell.</summary>
        public static void CheckPawns(Map map, Dictionary<int, IntVec3> contacts)
        {
            // GPT pre-release C2: the master switch counts too (contacts are also dropped at once on any lay change)
            if (contacts.Count == 0 || !AerialSettings.enabled || !AerialSettings.fallenWireShock) return;
            ResolveDefs();
            if (shockDef == null) return;
            List<Pawn> hit = null;
            foreach (KeyValuePair<int, IntVec3> kv in contacts)
            {
                IntVec3 c = map.cellIndices.IndexToCell(kv.Key);
                List<Thing> things = map.thingGrid.ThingsListAtFast(c);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i] is Pawn p && AerialMath.ShockTakes(p.RaceProps.IsFlesh, p.Dead, AlreadyOut(p), OnOwnCut(p, map, c)))
                        (hit ??= new List<Pawn>()).Add(p);
                }
            }
            if (hit == null) return;
            foreach (Pawn p in hit)
            {
                if (p.Spawned && !p.Dead) Shock(p, contacts);
            }
        }

        /// <summary>The re-string worker's exemption, scoped (review 2026-10-15): he is on RM_RestringSpan AND <paramref name="c"/>
        /// lies on a wire of the cut that job splices: either fallen half of any cut span of the anchor he was sent to
        /// (RestringAll splices every one of them). Walking across any other live wire, he is shocked like anyone else.</summary>
        public static bool OnOwnCut(Pawn p, Map map, IntVec3 c)
        {
            if (p.CurJobDef != Restringing.Job) return false;
            CompAerialAnchor a = CompAerialAnchor.Of(p.CurJob.targetA.Thing);
            RM_MapComponent_Aerial aerial = map.GetComponent<RM_MapComponent_Aerial>();
            if (a == null || aerial == null) return false;
            foreach (SpanLink l in a.links)
            {
                if (l.state != SpanState.Cut || l.other == null) continue;
                if (HalfTouches(aerial, map, a, l.other.thingIDNumber, c) || HalfTouches(aerial, map, l.other, a.thingIDNumber, c)) return true;
            }
            return false;
        }

        /// <summary>Does <paramref name="c"/> lie on the grounded part of <paramref name="x"/>'s fallen half of its cut span to
        /// <paramref name="partner"/>?</summary>
        private static bool HalfTouches(RM_MapComponent_Aerial aerial, Map map, CompAerialAnchor x, int partner, IntVec3 c)
        {
            if (!x.Spawned || x.Map != map) return false;
            foreach (FallenCord f in x.fallen)
            {
                if (f.cutPartner != partner) continue;
                foreach (FallenLay lay in aerial.Lays(x, f))
                    if (AerialMath.LayTouches(lay, c.x, c.z)) return true;
            }
            return false;
        }

        /// <summary>A pawn already knocked out by a shock is not re-shocked while it lies there (knock-out is a state,
        /// not damage; a pawn the knockback could not move would otherwise be hit every check).</summary>
        private static bool AlreadyOut(Pawn p)
        {
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(shockDef);
            return h != null && h.Severity >= 0.3f;
        }

        public static void Shock(Pawn p, Dictionary<int, IntVec3> contacts)
        {
            Map map = p.Map;
            IntVec3 at = p.Position;
            IntVec3 tip = contacts.TryGetValue(map.cellIndices.CellToIndex(at), out IntVec3 t) ? t : at;
            Vector3 v = at.ToVector3Shifted();
            FleckMaker.ThrowMicroSparks(v, map);
            FleckMaker.ThrowLightningGlow(v, map, 1.2f);
            SoundDefOf.Power_OffSmall?.PlayOneShot(new TargetInfo(at, map));
            shocks++;

            if (WeakHeart(p) && heartAttackDef != null)
            {
                kills++;
                BodyPartRecord heart = HeartOf(p);
                Hediff ha = HediffMaker.MakeHediff(heartAttackDef, p, heart);
                ha.Severity = 1f;
                p.health.AddHediff(ha, heart);
                if (!p.Dead) p.Kill(null, ha);
                if (p.Faction == Faction.OfPlayer)
                    Messages.Message(p.LabelShort + " touched a live fallen wire, and " + p.Possessive() + " weak heart gave out.",
                        new TargetInfo(at, map), MessageTypeDefOf.PawnDeath);
                return;
            }

            Knockback(p, at, tip, contacts);
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(shockDef);
            if (h != null) h.Severity = 1f;
            else p.health.AddHediff(shockDef);
            if (p.Faction == Faction.OfPlayer)
                Messages.Message(p.LabelShort + " was thrown back and knocked out by a live fallen wire.", p, MessageTypeDefOf.NegativeHealthEvent);
        }

        /// <summary>Weak heart: vanilla artery blockage, a heart attack already under way, or a natural heart that is
        /// damaged (below full part health). An artificial heart is not "heart damage".</summary>
        public static bool WeakHeart(Pawn p)
        {
            ResolveDefs();
            HediffSet hs = p.health.hediffSet;
            if (arteryBlockageDef != null && hs.HasHediff(arteryBlockageDef)) return true;
            if (heartAttackDef != null && hs.HasHediff(heartAttackDef)) return true;
            BodyPartRecord heart = HeartOf(p);
            if (heart == null || hs.PartIsMissing(heart) || hs.HasDirectlyAddedPartFor(heart)) return false;
            return hs.GetPartHealth(heart) < heart.def.GetMaxHealth(p) - 0.01f;
        }

        private static BodyPartRecord HeartOf(Pawn p)
        {
            List<BodyPartRecord> parts = p.RaceProps.body.AllParts;
            for (int i = 0; i < parts.Count; i++)
                if (parts[i].def == BodyPartDefOf.Heart) return parts[i];
            return null;
        }

        /// <summary>"Throws them back a little": up to AerialSettings.fallenWireKnockback cells, OFF the wire: away from its
        /// live end when that way is clear, otherwise the nearest turn from it whose first cell is standable and not on a live
        /// wire (GPT pre-release C6: mid-strand, "away from the tip" runs along the wire and used to stop at once), stopping
        /// at the first cell that is not standable or is itself on a live wire.</summary>
        private static void Knockback(Pawn p, IntVec3 at, IntVec3 tip, Dictionary<int, IntVec3> contacts)
        {
            int cells = Mathf.Clamp(AerialSettings.fallenWireKnockback, 0, 3);
            if (cells == 0) return;
            Map map = p.Map;
            IntVec3 away = at - tip;
            (int dx, int dz)? d = AerialMath.KnockbackDir(away.x, away.z, Rand.Range(0, 8), (dx, dz) =>
            {
                IntVec3 c = at + new IntVec3(dx, 0, dz);
                return c.InBounds(map) && c.Standable(map) && !contacts.ContainsKey(map.cellIndices.CellToIndex(c));
            });
            if (d == null) return;
            var dir = new IntVec3(d.Value.dx, 0, d.Value.dz);
            IntVec3 dest = at;
            for (int i = 1; i <= cells; i++)
            {
                IntVec3 c = at + new IntVec3(dir.x * i, 0, dir.z * i);
                if (!c.InBounds(map) || !c.Standable(map) || contacts.ContainsKey(map.cellIndices.CellToIndex(c))) break;
                dest = c;
            }
            if (dest == at) return;
            p.Position = dest;
            p.Notify_Teleported(true, true);
        }

        // ------------------------------------------------------------------ X-7: a live end lights spilled fuel
        private static Type excavationType;
        private static PropertyInfo liquidFireProp;
        private static MethodInfo igniteNow;
        private static bool flowWorksResolved;

        private static void ResolveFlowWorks()
        {
            if (flowWorksResolved) return;
            flowWorksResolved = true;
            try
            {
                excavationType = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.RM_MapComponent_Excavation");
                if (excavationType == null) return;
                liquidFireProp = excavationType.GetProperty("LiquidFire", BindingFlags.Public | BindingFlags.Instance);
                igniteNow = liquidFireProp?.PropertyType.GetMethod("IgniteNow", BindingFlags.Public | BindingFlags.Instance, null,
                    new[] { typeof(Map), excavationType, typeof(IntVec3) }, null);
                if (igniteNow == null)
                    Log.Warning("[GimmeSomeSlack] FlowWorks is loaded but RM_LiquidFire.IgniteNow(Map, RM_MapComponent_Excavation, IntVec3) " +
                                "was not found; live fallen wires will not light FlowWorks liquids.");
            }
            catch (Exception e)
            {
                igniteNow = null;
                Log.Warning("[GimmeSomeSlack] FlowWorks ignition lookup failed; live fallen wires will not light its liquids: " + e.Message);
            }
        }

        public static bool FlowWorksIgnitionAvailable { get { ResolveFlowWorks(); return igniteNow != null; } }

        /// <summary>Each live end lying in spilled fuel may light it this sweep.</summary>
        public static void TryIgnite(Map map, List<IntVec3> tips)
        {
            if (tips.Count == 0 || !AerialSettings.fallenWireIgnites) return;
            foreach (IntVec3 c in tips)
            {
                if (!Rand.Chance(IgniteChancePerSweep)) continue;
                if (IgniteAt(map, c)) ignitions++;
            }
        }

        public static bool IgniteAt(Map map, IntVec3 c)
        {
            if (c.GetFirstThing(map, ThingDefOf.Filth_Fuel) != null && FireUtility.TryStartFireIn(c, map, 0.4f, null))
                return true;
            ResolveFlowWorks();
            if (igniteNow == null) return false;
            try
            {
                MapComponent ex = map.GetComponent(excavationType);
                object fire = ex != null ? liquidFireProp.GetValue(ex) : null;
                return fire != null && (bool)igniteNow.Invoke(fire, new object[] { map, ex, c });
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[GimmeSomeSlack] live fallen wire: FlowWorks ignition threw; that half is off: " + e, 0x6A5E7);
                igniteNow = null;
                return false;
            }
        }
    }
}
