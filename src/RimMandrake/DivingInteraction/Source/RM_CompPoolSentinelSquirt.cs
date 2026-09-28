using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_RULED_CONTENT_1 §9 (Q13, question card 2026-09-27) — the
    // orruhmu's squirt. Full design:
    // design/Jawa/worldbuilding/biomes/grey_deep_pool_sentinel_2026-09-27.md
    //
    // Owner's original sentence (the_grey_deep.md §4d, verbatim): "Brine
    // pools and the creatures near them have a unique defence: they squirt
    // out a protein shower causing ultra-rapid crystallisation." RULED: ONE
    // new solitary species (RM_Orruhmu, RM_GreySeaFauna.xml), the third
    // trigger on the SAME consequence the pools and chimneys already use —
    // BrineEncasementUtility.TryEncase (lifted out of
    // MapComponent_BrineCrystallisation for exactly this reuse). This comp
    // is the only new C# the design doc owes.
    //
    // TRIGGER — crowded, deterministically, no rolls anywhere:
    //   0-1 humanlike/mech pawns within SquirtRadius: nothing, ever. A lone
    //     harvester can work beside an orruhmu all day.
    //   2+: the orruhmu SWELLS for one full rare tick — the visible tell
    //     (a pressurising hiss; no light, no glow — ban 4). Backing off
    //     below 2 before the next rare tick always cancels it, the same
    //     walk-out beat the chimney plume teaches. No ratchet.
    //   Still 2+ at the next rare tick: it squirts the NEAREST intruder in
    //     range — encased on the spot, standard RM_BrineEncasement jacket,
    //     mined out by friends, shipped wide-rescue smother rate. One pawn
    //     per squirt, never an area wipe.
    //
    // Cooldown: 15,000 ticks (6 in-game hours) — a spent orruhmu is just a
    // strange dome (CompInspectStringExtra says "spent") until it refills.
    //
    // Animals never count toward the crowd and are never sprayed — the same
    // deliberate scope as the shipped map component's pool/chimney triggers
    // (native chemistry; the orruhmu itself is also never encased).
    //
    // Attaches to an ANIMAL pawn (RM_Orruhmu), so CompTickRare is the
    // correct ticker — the Plant CompTickLong trap does not apply here.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompPoolSentinelSquirt : ThingComp
    {
        private const float SquirtRadius = 5f;
        private const int CooldownTicks = 15000; // 6 in-game hours, per the design doc

        private bool swelling;
        private int ticksSinceLastSquirt = CooldownTicks; // ready to fire the first time it is crowded

        private bool IsSpent => ticksSinceLastSquirt < CooldownTicks;

        public override void CompTickRare()
        {
            base.CompTickRare();
            ticksSinceLastSquirt += 250;

            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.greyPoolSentinelEnabled)
            {
                swelling = false;
                return;
            }
            if (parent?.Map == null || !parent.Spawned || IsSpent)
            {
                swelling = false;
                return;
            }

            int count = CountNearbyIntruders(out Pawn nearest);

            if (count <= 1)
            {
                swelling = false; // backing off during the swell always cancels — no ratchet
                return;
            }

            if (!swelling)
            {
                swelling = true;
                ThrowSwellTell();
                return; // one full rare tick of tell before it can fire
            }

            // Still crowded after the swell: it squirts.
            swelling = false;
            if (nearest != null && BrineEncasementUtility.TryEncase(nearest, parent.Map))
            {
                ticksSinceLastSquirt = 0;
            }
        }

        private int CountNearbyIntruders(out Pawn nearest)
        {
            nearest = null;
            float bestDist = float.MaxValue;
            int count = 0;
            IReadOnlyList<Pawn> pawns = parent.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || !p.Spawned)
                {
                    continue;
                }
                if (!p.RaceProps.Humanlike && !p.RaceProps.IsMechanoid)
                {
                    continue; // animals never count, never sprayed
                }
                float d = p.Position.DistanceTo(parent.Position);
                if (d > SquirtRadius)
                {
                    continue;
                }
                count++;
                if (d < bestDist)
                {
                    bestDist = d;
                    nearest = p;
                }
            }
            return count;
        }

        // Motion + sound only — NEVER light (ban 4). The bellows inflating /
        // crust plates lifting is art/animation work this pass does not
        // attempt; HissJet is the mechanical stand-in for "a wet
        // pressurising hiss" until real audio direction exists.
        private void ThrowSwellTell()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            SoundDef hiss = DefDatabase<SoundDef>.GetNamedSilentFail("HissJet");
            hiss?.PlayOneShot(SoundInfo.InMap(new TargetInfo(parent.Position, map)));
        }

        public override string CompInspectStringExtra()
        {
            if (IsSpent)
            {
                return "spent";
            }
            if (swelling)
            {
                return "swelling";
            }
            return null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref swelling, "swelling", false);
            Scribe_Values.Look(ref ticksSinceLastSquirt, "ticksSinceLastSquirt", CooldownTicks);
        }
    }

    public class CompProperties_PoolSentinelSquirt : CompProperties
    {
        public CompProperties_PoolSentinelSquirt()
        {
            compClass = typeof(RM_CompPoolSentinelSquirt);
        }
    }
}
