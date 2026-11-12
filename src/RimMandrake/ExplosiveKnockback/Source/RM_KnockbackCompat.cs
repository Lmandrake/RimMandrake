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
        private static Func<object, IntVec3, byte> fillIn;
        private static Func<Map, IntVec3, Thing> coverAt;
        private static Type coverType;

        // ── Gimme Some Slack (mandrake.rm.gimmesomeslack): a carried hose end ──
        private static Type hosesCompType;
        private static FieldInfo hosesReels;
        private static FieldInfo reelCarrier;
        private static MethodInfo reelDropCarry;

        // ── The Cauldron (mandrake.rm.cauldron): its vent gas, a defless grid, burns cell by cell ──
        /// <summary>The gas chain's registration with the Cauldron's vent gas (RM_MapComponent_VentGas.Ignite is patched).
        /// A proof clears it to stand in for "the grid not registered" (its control).</summary>
        public static bool VentGasRegistered;
        /// <summary>The patch itself went on (the Cauldron is loaded); VentGasRegistered is only ever true with it.</summary>
        public static bool VentGasHooked;

        public static bool FlowWorks => excavationType != null;
        /// <summary>FlowWorks' hose reels (moved there from Gimme Some Slack at the hose port) are hooked: a thrown carrier drops the hose.</summary>
        public static bool Hoses => reelDropCarry != null;

        public static void Init()
        {
            try
            {
                excavationType = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_MapComponent_Excavation");
                if (excavationType != null)
                {
                    MethodInfo m = AccessTools.Method(excavationType, "IsSuperdeepExcavation", new[] { typeof(IntVec3) });
                    MethodInfo d = AccessTools.Method(excavationType, "Deepen", new[] { typeof(IntVec3) });
                    MethodInfo fi = AccessTools.Method(excavationType, "FillIn", new[] { typeof(IntVec3) });
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
                        fillIn = fi == null ? null : (Func<object, IntVec3, byte>)((o, c) => (byte)fi.Invoke(o, new object[] { c }));
                        coverAt = ca == null ? null : (Func<Map, IntVec3, Thing>)((map, c) => ca.Invoke(null, new object[] { map, c }) as Thing);
                    }
                }
                Type trap = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_SuperdeepTrap");
                EventInfo ev = trap?.GetEvent("PitDescent", BindingFlags.Public | BindingFlags.Static);
                if (ev != null)
                {
                    ev.AddEventHandler(null, new Action<Pawn, IntVec3>((p, c) => RM_KnockbackJournal.Add("descent", 0, p, "at", c)));
                }
                Type ventGas = AccessTools.TypeByName("RimMandrake.Cauldron.RM_MapComponent_VentGas");
                MethodInfo ignite = ventGas == null ? null : AccessTools.Method(ventGas, "Ignite", new[] { typeof(IntVec3), typeof(Thing) });
                if (ignite != null && ignite.ReturnType == typeof(bool))
                {
                    new Harmony("mandrake.rm.explosiveknockback.gaschain").Patch(ignite,
                        postfix: new HarmonyMethod(typeof(RM_KnockbackCompat), nameof(VentGasIgnitePostfix)));
                    VentGasHooked = true;
                    VentGasRegistered = true;
                }
                hosesCompType = AccessTools.TypeByName("RimMandrake.FlowWorks.Hose.RM_MapComponent_Hoses");   // the hose moved to FlowWorks (hose port, 2026-10-11)
                Type reel = AccessTools.TypeByName("RimMandrake.FlowWorks.Hose.CompHoseReel");
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
                Log.Warning("[RM Explosive Knockback] compatibility probe failed, running without FlowWorks hooks (pits, hoses): " + ex.Message);
                excavationType = null;
                reelDropCarry = null;
            }
        }

        /// <summary>RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS: one vent-gas cell burned (the Cauldron's own fire scan or any
        /// caller of Ignite) = one clump burst there. The Cauldron's chain itself spreads the fire cell by cell.</summary>
        public static void VentGasIgnitePostfix(MapComponent __instance, IntVec3 c, Thing instigator, bool __result)
        {
            if (__result && VentGasRegistered && __instance?.map != null)
            {
                RM_MapComponent_Knockback.GasBurst(__instance.map, c, instigator, "cauldron_vent_gas");
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

        // ── Closed containers (owner 2026-11-10/11; plan step 2, dl_closed_means_hidden; thrown whole, owner 2026-11-12) ──
        // Vanilla 1.6 has no player-built closed storage: shelves (Building_Storage) show their goods, and its sealed
        // crates (Building_Crate: ancient, hermetic, security) hold theirs in a ThingOwner, unspawned, where an explosion
        // never reaches them. A closed container is: storage whose def hides its contents (a comp or extension with a
        // bool field `showContents` set false: LWM's Deep Storage), our opt-in tag RM_KnockbackClosedStorage on any
        // building def (Patches/RM_Knockback_ClosedContainers.xml tags Cold Storage's lockers and crock), or, with
        // vanillaCratesClosed on, a Building_Crate. Decided per def (cached) plus the crate setting.
        private static readonly Dictionary<ThingDef, bool> closedByDef = new Dictionary<ThingDef, bool>();

        public static bool IsClosedContainer(Thing b)
        {
            if (b?.def == null || b.def.category != ThingCategory.Building)
            {
                return false;
            }
            if (!closedByDef.TryGetValue(b.def, out bool closed))
            {
                closed = b.def.HasModExtension<RM_KnockbackClosedStorage>() || AnyHides(b.def.comps) || AnyHides(b.def.modExtensions);
                closedByDef[b.def] = closed;
            }
            return closed || (b is Building_Crate && RimMandrakeExplosiveKnockbackSettings.vanillaCratesClosed);
        }

#if RM_PROOFS
        /// <summary>Forget the cached answers (a proof hook tagging a def at runtime).</summary>
        public static void ForgetClosed() => closedByDef.Clear();
#endif

        private static bool AnyHides(IList list)
        {
            if (list == null)
            {
                return false;
            }
            foreach (object o in list)
            {
                FieldInfo f = o?.GetType().GetField("showContents", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                if (f != null && f.FieldType == typeof(bool) && !(bool)f.GetValue(o))
                {
                    return true;
                }
            }
            return false;
        }

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

#if RM_PROOFS
        /// <summary>Fill a dug cell back to the surface (proof scenes only: a pit an earlier scene dug at a reused origin
        /// otherwise catches the next scene's throw — live 2026-10-07, thump cannon "2 cells" was a stop in a leftover pit).
        /// True when the cell ends at the surface or FlowWorks is absent.</summary>
        public static bool FillToSurface(Map map, IntVec3 c)
        {
            object ex = Excavation(map);
            if (ex == null || fillIn == null)
            {
                return ex == null;
            }
            for (int i = 0; i < 8; i++)
            {
                if (fillIn(ex, c) == 0)
                {
                    return true;
                }
            }
            return false;
        }

#endif
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
