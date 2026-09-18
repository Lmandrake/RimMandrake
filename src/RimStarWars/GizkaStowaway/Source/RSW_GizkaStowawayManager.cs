using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.GizkaStowaway
{
    /// <summary>
    /// GIZKA_TRIBBLE_ADAPTATION_1, draft §1 — discovery.
    ///
    /// The shape the design REJECTS, in the owner's words and the item's:
    /// an IncidentDef in ThreatBig that a storyteller rolls at random. That is
    /// arrival with no story, indistinguishable from weather. There is no
    /// IncidentDef anywhere in this mod, deliberately.
    ///
    /// What ships instead: the gizka rides something the PLAYER did. Four
    /// hooks, each individually toggleable, each gated by a chance and a
    /// shared cooldown so the colony is never handed two in a week. Exactly
    /// ONE animal per discovery, tame, with a warm letter that is not a
    /// warning — the flavor line mentions that they breed, and that line is
    /// the only warning the Cute stage gets or needs.
    ///
    /// The gravship hook is the flagship (Card 4 gated the entire feature on
    /// confirming it): a Harmony postfix on RimWorld.Scenario.PostGravshipLanded,
    /// read from decompiled source and then LIVE-CONFIRMED on a real landing
    /// of the campaign gravship — GIZKA_HOLD_HOOK_SPIKE_1. Note that there is
    /// no "hold" concept in the engine at all; a gravship's hold is ordinary
    /// map, so "found in the hold" IS the landing moment and nothing further
    /// is hookable. Do not go looking for a first-entry trigger; it does not
    /// exist.
    /// </summary>
    public class GameComponent_GizkaStowaway : GameComponent
    {
        public static GameComponent_GizkaStowaway Instance;

        // Shared across all four triggers: one discovery per cooldown window,
        // whichever route delivers it.
        private const int DiscoveryCooldownTicks = 900000;   // 15 days
        private int lastDiscoveryTick = -999999;

        // Base per-trigger chances, before the Mod Settings frequency
        // multiplier. A gravship landing is the flagship moment and is by far
        // the likeliest; a completed trade is common enough that it has to be
        // rare per occurrence or it would be the only route anyone ever sees.
        private const float ChanceGravship = 0.35f;
        private const float ChanceSalvage = 0.12f;
        private const float ChanceTrade = 0.05f;
        private const float ChanceQuest = 0.10f;

        public GameComponent_GizkaStowaway(Game game)
        {
            Instance = this;
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Instance = this;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lastDiscoveryTick, "lastDiscoveryTick", -999999);
        }

        private bool Ready(bool triggerEnabled)
        {
            RSW_GizkaSettings s = RSW_GizkaStowawayMod.Settings;
            if (s == null || !s.stowawayEventsEnabled || !triggerEnabled) return false;
            if (RSW_GizkaPopulation.Kind == null) return false;   // donor absent
            if (Find.TickManager.TicksGame - lastDiscoveryTick < DiscoveryCooldownTicks) return false;
            return true;
        }

        private bool Roll(float baseChance)
        {
            float f = RSW_GizkaStowawayMod.Settings?.discoveryFrequency ?? 1f;
            return Rand.Chance(Mathf.Clamp01(baseChance * f));
        }

        // ---- the four hooks -------------------------------------------------

        public void Notify_GravshipLanded(Map map)
        {
            if (map == null) return;
            if (!Ready(RSW_GizkaStowawayMod.Settings.triggerGravship)) return;
            if (!Roll(ChanceGravship)) return;

            IntVec3 cell = FindAnchorCell(map);
            Discover(map, cell,
                "Gizka in the hold",
                "Something has been living in the hold.\n\nIt came out when the ramp did: a fist-sized thing on two legs, entirely unbothered, and by the time anyone thought to catch it, it had already been picked up and named.\n\nThe manifest says nothing about it. The crew of whatever ship this hull used to be might have known. Gizka breed, is the thing. They are known for it.");
        }

        public void Notify_SalvageDeconstructed(Thing salvage)
        {
            Map map = salvage?.Map;
            if (map == null) return;
            if (!Ready(RSW_GizkaStowawayMod.Settings.triggerSalvage)) return;
            if (!Roll(ChanceSalvage)) return;

            Discover(map, salvage.Position,
                "Gizka in the wreck",
                "It hopped out of the wreckage while the panels were coming off — thin, filthy, and apparently delighted.\n\nWhatever went down in that hull, this survived it. Gizka usually do. They breed faster than most things can eat them, which is most of the explanation for gizka.");
        }

        public void Notify_TradeCompleted(Map map)
        {
            if (map == null) return;
            if (!Ready(RSW_GizkaStowawayMod.Settings.triggerTrade)) return;
            if (!Roll(ChanceTrade)) return;

            Discover(map, FindAnchorCell(map),
                "Gizka in the cargo",
                "Crate three was not empty.\n\nThe trader is gone, the deal is closed, and the colony is now the owner of one gizka that was not on any invoice. This is not an accident that happens to traders. This is the oldest trick on the spacelanes: a gizka costs nothing to give away and does not stay one gizka.");
        }

        public void Notify_QuestCompleted(Map map)
        {
            if (map == null) return;
            if (!Ready(RSW_GizkaStowawayMod.Settings.triggerQuest)) return;
            if (!Roll(ChanceQuest)) return;

            Discover(map, FindAnchorCell(map),
                "Gizka: a free gift",
                "With the agreed payment came a small crate nobody had agreed to, and a note reading — with what the sender clearly believed was generosity — \"WITH THANKS. A GIFT.\"\n\nInside is a gizka. Somebody, somewhere, is now one gizka lighter and extremely pleased about it.");
        }

        // ---------------------------------------------------------------------

        private void Discover(Map map, IntVec3 near, string label, string text)
        {
            if (!CellFinder.TryFindRandomCellNear(near, map, 8,
                    c => c.Standable(map) && !c.Fogged(map), out IntVec3 cell))
            {
                cell = near;
            }

            Pawn p = RSW_GizkaPopulation.SpawnStowaway(map, cell, Faction.OfPlayer, newborn: false);
            if (p == null) return;

            lastDiscoveryTick = Find.TickManager.TicksGame;

            // Vanilla PositiveEvent letter, not a new LetterDef: the draft left
            // that to the build, and there is nothing a bespoke LetterDef would
            // do here that the vanilla one does not. The discovery is warm on
            // purpose — this is the cute half of the arc, and the game should
            // not be flagging it in threat colours.
            Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.PositiveEvent,
                new TargetInfo(p.Position, map));
        }

        private IntVec3 FindAnchorCell(Map map)
        {
            // Prefer somewhere the colony actually is, so the discovery is
            // found rather than merely spawned.
            if (map.mapPawns.FreeColonistsSpawnedCount > 0)
            {
                return map.mapPawns.FreeColonistsSpawned[0].Position;
            }
            return map.Center;
        }
    }
}
