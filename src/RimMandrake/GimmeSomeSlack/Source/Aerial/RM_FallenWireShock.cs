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
    /// </summary>
    public static class RM_FallenWireShock
    {
        public const int CheckInterval = 20;
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
                        IntVec3 tip = CellOf(l.Tip);
                        if (tip.InBounds(map)) tips.Add(tip);
                        foreach (P2 p in l.Pts)
                        {
                            IntVec3 c = CellOf(p);
                            if (c == home || !c.InBounds(map)) continue;
                            contacts[map.cellIndices.CellToIndex(c)] = tip;
                        }
                        if (tip != home && tip.InBounds(map)) contacts[map.cellIndices.CellToIndex(tip)] = tip;
                    }
                }
            }
        }

        private static IntVec3 CellOf(P2 p) => new IntVec3((int)Math.Floor(p.X), 0, (int)Math.Floor(p.Z));

        /// <summary>Shock every flesh pawn standing on a contact cell.</summary>
        public static void CheckPawns(Map map, Dictionary<int, IntVec3> contacts)
        {
            if (contacts.Count == 0 || !AerialSettings.fallenWireShock) return;
            ResolveDefs();
            if (shockDef == null) return;
            List<Pawn> hit = null;
            foreach (KeyValuePair<int, IntVec3> kv in contacts)
            {
                IntVec3 c = map.cellIndices.IndexToCell(kv.Key);
                List<Thing> things = map.thingGrid.ThingsListAtFast(c);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i] is Pawn p && !p.Dead && p.RaceProps.IsFlesh && !AlreadyOut(p))
                        (hit ??= new List<Pawn>()).Add(p);
                }
            }
            if (hit == null) return;
            foreach (Pawn p in hit)
            {
                if (p.Spawned && !p.Dead) Shock(p, contacts);
            }
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

        /// <summary>"Throws them back a little": up to AerialSettings.fallenWireKnockback cells, straight away from the
        /// wire's live end (or any free direction when the pawn stands on the tip), stopping at the first cell that
        /// is not standable or is itself on a live wire.</summary>
        private static void Knockback(Pawn p, IntVec3 at, IntVec3 tip, Dictionary<int, IntVec3> contacts)
        {
            int cells = Mathf.Clamp(AerialSettings.fallenWireKnockback, 0, 3);
            if (cells == 0) return;
            Map map = p.Map;
            IntVec3 dir = at - tip;
            if (dir == IntVec3.Zero) dir = GenAdj.AdjacentCells[Rand.Range(0, 8)];
            dir = new IntVec3(Math.Sign(dir.x), 0, Math.Sign(dir.z));
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
