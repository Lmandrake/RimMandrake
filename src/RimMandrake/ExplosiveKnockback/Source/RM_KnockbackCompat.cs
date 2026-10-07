using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>
    /// Soft dependencies, resolved by type NAME at startup — never a hard reference and never a
    /// MayRequire on a patch Operation (CLAUDE.md: that attribute is inert on an Operation node).
    /// With the mod absent every member reads "no pit here" / "no hose", and nothing is patched.
    /// </summary>
    public static class RM_KnockbackCompat
    {
        // ── FlowWorks (mandrake.rm.flowworks): superdeep pits and their covers ──
        private static Type excavationType;
        private static Func<object, IntVec3, bool> isSuperdeep;
        private static Func<object, IntVec3, byte> deepen;
        private static Func<Map, IntVec3, Thing> coverAt;
        private static Type coverType;

        // ── Gimme Some Slack (mandrake.rm.gimmesomeslack): a carried hose end ──
        private static Type hosesCompType;
        private static FieldInfo hosesReels;
        private static FieldInfo reelCarrier;
        private static MethodInfo reelDropCarry;

        public static bool FlowWorks => excavationType != null;
        public static bool GimmeSomeSlack => reelDropCarry != null;

        public static void Init()
        {
            try
            {
                excavationType = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_MapComponent_Excavation");
                if (excavationType != null)
                {
                    MethodInfo m = AccessTools.Method(excavationType, "IsSuperdeepExcavation", new[] { typeof(IntVec3) });
                    MethodInfo d = AccessTools.Method(excavationType, "Deepen", new[] { typeof(IntVec3) });
                    Type util = AccessTools.TypeByName("RimMandrake.FlowWorks.Pits.RM_PitCoverUtility");
                    MethodInfo ca = util == null ? null : AccessTools.Method(util, "CoverAt", new[] { typeof(Map), typeof(IntVec3) });
                    coverType = AccessTools.TypeByName("RimMandrake.FlowWorks.Pits.Building_PitCover");
                    if (m == null)
                    {
                        excavationType = null;
                    }
                    else
                    {
                        isSuperdeep = (o, c) => (bool)m.Invoke(o, new object[] { c });
                        deepen = d == null ? null : (Func<object, IntVec3, byte>)((o, c) => (byte)d.Invoke(o, new object[] { c }));
                        coverAt = ca == null ? null : (Func<Map, IntVec3, Thing>)((map, c) => ca.Invoke(null, new object[] { map, c }) as Thing);
                    }
                }
                Type trap = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_SuperdeepTrap");
                EventInfo ev = trap?.GetEvent("PitDescent", BindingFlags.Public | BindingFlags.Static);
                if (ev != null)
                {
                    ev.AddEventHandler(null, new Action<Pawn, IntVec3>((p, c) => RM_KnockbackJournal.Add("descent", 0, p, "at", c)));
                }
                hosesCompType = AccessTools.TypeByName("RimMandrake.GimmeSomeSlack.Hose.RM_MapComponent_Hoses");
                Type reel = AccessTools.TypeByName("RimMandrake.GimmeSomeSlack.Hose.CompHoseReel");
                if (hosesCompType != null && reel != null)
                {
                    hosesReels = AccessTools.Field(hosesCompType, "reels");
                    reelCarrier = AccessTools.Field(reel, "carrier");
                    reelDropCarry = AccessTools.Method(reel, "DropCarry", new[] { typeof(Pawn), typeof(bool) });
                    if (hosesReels == null || reelCarrier == null)
                    {
                        reelDropCarry = null;
                    }
                }
            }
            catch (Exception ex)
            {
                Log.Warning("[RM Explosive Knockback] compatibility probe failed, running without FlowWorks/GimmeSomeSlack hooks: " + ex.Message);
                excavationType = null;
                reelDropCarry = null;
            }
        }

        private static object Excavation(Map map)
        {
            if (excavationType == null || map == null)
            {
                return null;
            }
            List<MapComponent> comps = map.components;
            for (int i = 0; i < comps.Count; i++)
            {
                if (comps[i] != null && excavationType.IsInstanceOfType(comps[i]))
                {
                    return comps[i];
                }
            }
            return null;
        }

        /// <summary>Dug to D = 4 (covered or not).</summary>
        public static bool IsSuperdeep(Map map, IntVec3 c)
        {
            object ex = Excavation(map);
            return ex != null && isSuperdeep(ex, c);
        }

        public static Thing CoverAt(Map map, IntVec3 c)
        {
            return coverAt == null ? null : coverAt(map, c);
        }

        public static bool IsCover(Thing t) => coverType != null && t != null && coverType.IsInstanceOfType(t);

        /// <summary>Dig a cell to superdeep (runner scenes only). False if FlowWorks is absent.</summary>
        public static bool DigToSuperdeep(Map map, IntVec3 c)
        {
            object ex = Excavation(map);
            if (ex == null || deepen == null)
            {
                return false;
            }
            for (int i = 0; i < 4 && !isSuperdeep(ex, c); i++)
            {
                deepen(ex, c);
            }
            return isSuperdeep(ex, c);
        }

        /// <summary>Owner Q6: a carried hose end drops where the carrier stood. True if one was dropped.</summary>
        public static bool DropCarriedHose(Pawn p)
        {
            if (reelDropCarry == null || p?.Map == null)
            {
                return false;
            }
            MapComponent hoses = null;
            foreach (MapComponent mc in p.Map.components)
            {
                if (mc != null && hosesCompType.IsInstanceOfType(mc))
                {
                    hoses = mc;
                    break;
                }
            }
            if (hoses == null || !(hosesReels.GetValue(hoses) is IList reels))
            {
                return false;
            }
            bool dropped = false;
            for (int i = reels.Count - 1; i >= 0; i--)
            {
                object reel = reels[i];
                if (reel != null && reelCarrier.GetValue(reel) == p)
                {
                    dropped |= (bool)reelDropCarry.Invoke(reel, new object[] { p, true });
                }
            }
            return dropped;
        }
    }
}
