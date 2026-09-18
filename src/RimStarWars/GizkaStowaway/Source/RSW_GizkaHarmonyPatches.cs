using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.GizkaStowaway
{
    /// <summary>
    /// GIZKA_TRIBBLE_ADAPTATION_1 — every hook this feature attaches to the
    /// game, in one file so the whole surface area is readable at once.
    ///
    /// All five are postfixes or prefixes on public methods; nothing is
    /// transpiled, nothing is destructive, and each one does nothing at all
    /// unless its own Mod Setting is on.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RSW_GizkaHarmony
    {
        static RSW_GizkaHarmony()
        {
            new Harmony("mandrake.rsw.gizkastowaway").PatchAll();
        }
    }

    /// <summary>
    /// The flagship hook. GIZKA_HOLD_HOOK_SPIKE_1 read this out of decompiled
    /// source and then proved it live on a real landing of the campaign
    /// gravship: RimWorld.Scenario.PostGravshipLanded(Map) is public, is called
    /// by WorldComponent_GravshipController.LandingEnded() as its last act
    /// after the gravship, cargo and colonists are already placed, fires for
    /// EVERY landing route (new map and existing map alike), fires exactly once
    /// per landing, and is reached whether or not the player has gravship
    /// cutscenes switched on.
    /// </summary>
    [HarmonyPatch(typeof(Scenario), nameof(Scenario.PostGravshipLanded))]
    public static class Patch_Scenario_PostGravshipLanded
    {
        public static void Postfix(Map map)
        {
            GameComponent_GizkaStowaway.Instance?.Notify_GravshipLanded(map);
        }
    }

    /// <summary>
    /// Salvage. A wreck is not a concept the engine holds either, so this keys
    /// off the act rather than the object: a building being DECONSTRUCTED
    /// (never destroyed, never deconstructed by an enemy) whose def is one of
    /// the ship-wreckage things. The def list is resolved by silent lookup so
    /// that a missing Odyssey or a renamed def costs nothing.
    /// </summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.Destroy))]
    public static class Patch_Thing_Destroy_Salvage
    {
        private static bool resolved;
        private static HashSet<ThingDef> salvageDefs;

        private static HashSet<ThingDef> SalvageDefs
        {
            get
            {
                if (!resolved)
                {
                    resolved = true;
                    salvageDefs = new HashSet<ThingDef>();
                    // Each name below was checked to EXIST before it was
                    // written here; the two that the draft's prose implied
                    // ("CrashedShipPart", a generic wreck def) do not exist
                    // under those names and are not in this list. Silent
                    // lookup means a DLC-only def simply drops out.
                    string[] names =
                    {
                        "ShipChunk",
                        "ShipChunk_Mech",
                        "ShuttleCrashed",
                        "ShuttleCrashed_Exitable",
                        "ShuttleCrashed_Exitable_Mechanitor",
                        "MechRelay_Crashed",
                        "AncientShipBeacon",
                        "AncientCryptosleepCasket",
                        "AncientCryptosleepPod",
                        "Ship_CryptosleepCasket"
                    };
                    foreach (string n in names)
                    {
                        ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(n);
                        if (d != null) salvageDefs.Add(d);
                    }
                }
                return salvageDefs;
            }
        }

        public static void Prefix(Thing __instance, DestroyMode mode)
        {
            if (mode != DestroyMode.Deconstruct) return;
            if (__instance == null || !__instance.Spawned) return;
            if (!SalvageDefs.Contains(__instance.def)) return;
            GameComponent_GizkaStowaway.Instance?.Notify_SalvageDeconstructed(__instance);
        }
    }

    /// <summary>
    /// Purchased cargo. TradeDeal.TryExecute is the one place a deal actually
    /// moves goods; `actuallyTraded` false means the player closed the window
    /// having changed nothing, which must not count.
    /// </summary>
    [HarmonyPatch(typeof(TradeDeal), nameof(TradeDeal.TryExecute))]
    public static class Patch_TradeDeal_TryExecute
    {
        public static void Postfix(bool __result, ref bool actuallyTraded)
        {
            if (!__result || !actuallyTraded) return;
            Map map = Find.CurrentMap;
            if (map == null) return;
            GameComponent_GizkaStowaway.Instance?.Notify_TradeCompleted(map);
        }
    }

    /// <summary>
    /// Card 5, RULED 2026-09-12: the free-gift gag is IN for v1. This is the
    /// "one quest-system touch" the card budgets — a quest that ends in
    /// success can deliver a gizka nobody asked for, alongside whatever was
    /// actually agreed. No QuestScriptDef, no QuestNode, no reward-generation
    /// surgery: the gag is that it arrives WITH the payment, not that it is
    /// the payment.
    /// </summary>
    [HarmonyPatch(typeof(Quest), nameof(Quest.End))]
    public static class Patch_Quest_End
    {
        public static void Postfix(QuestEndOutcome outcome)
        {
            if (outcome != QuestEndOutcome.Success) return;
            Map map = Find.CurrentMap;
            if (map == null) return;
            GameComponent_GizkaStowaway.Instance?.Notify_QuestCompleted(map);
        }
    }

    /// <summary>
    /// Card 3, RULED 2026-09-12: "cull guilt: IN."
    ///
    /// Prefix rather than postfix because by the time Kill returns the pawn is
    /// despawned and the corpse has taken its place, so there is no longer a
    /// position to ask "who could see this?" about. Vanilla's own charges
    /// (bonded animal death, witnessed slaughter) still apply on top; this is
    /// the extra charge for the anonymous ones, which is exactly the set
    /// vanilla does not price and exactly the set a cull is made of.
    /// </summary>
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
    public static class Patch_Pawn_Kill_CullGuilt
    {
        private const float WitnessRadius = 12f;

        public static void Prefix(Pawn __instance)
        {
            RSW_GizkaSettings s = RSW_GizkaStowawayMod.Settings;
            if (s == null || !s.stowawayEventsEnabled || !s.cullGuiltEnabled) return;

            Pawn victim = __instance;
            if (victim == null || !victim.Spawned || victim.Map == null) return;
            if (!RSW_GizkaPopulation.IsStowawayGizka(victim)) return;

            ThoughtDef thought = DefDatabase<ThoughtDef>.GetNamedSilentFail("RSW_GizkaWatchedCull");
            if (thought == null) return;

            List<Pawn> colonists = victim.Map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn c = colonists[i];
                if (c == null || c.Dead || c.needs?.mood?.thoughts?.memories == null) continue;
                if (c.Position.DistanceTo(victim.Position) > WitnessRadius) continue;
                if (!GenSight.LineOfSight(c.Position, victim.Position, victim.Map)) continue;
                c.needs.mood.thoughts.memories.TryGainMemory(thought);
            }
        }
    }
}
