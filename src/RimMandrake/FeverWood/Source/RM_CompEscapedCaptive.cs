using RimWorld;
using Verse;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_DIANOGA_PRISON_1. Per-pawn comp on RM_Sekkulaath_Juvenile
    // (and, once the Star Wars swap patch retargets the occupant, on
    // RSW_Dianoga too — this comp is added generically via <comps> on
    // whichever race is actually spawned, not hardcoded to one defName).
    //
    // §6m's escape ladder, read from the pawn's side:
    //   stage 1 — TOUGH, water-seeking, hostile: delivered on the RACE
    //             (Wildness/manhunterOnDamageChance/waterSeeker in the
    //             ThingDef), nothing to do here.
    //   stage 2 — "if it reaches a pool it establishes": THIS class's job.
    //             Only armed after an actual tank escape (Notify_JustEscaped)
    //             — a wild-born or successfully tamed Sekkulaath must not
    //             "install" just for standing in water it always lived near.
    //   stage 3 — "left alone in water it can mature into the real thing":
    //             explicitly UNSET duration/interruptibility (item's own
    //             `open` list) — NOT built. What ships instead: reaching a
    //             pool immediately calls Notify_SekkulaathInstalled(),
    //             which un-sets any prior "permanently killed on this map"
    //             flag on RM_MapComponent_TentacleWatch, i.e. the ambient
    //             elder-being system is guaranteed live on this map again.
    //             That is a real, honest reading of "you will have created
    //             the biome's worst threat yourself" without inventing a
    //             maturation timer the owner never gave. A true staged
    //             maturation (small horror -> full elder being, on a clock)
    //             is deferred to FEVERWOOD_DIANOGA_TANK_TUNING_1.
    public class RM_CompEscapedCaptive : ThingComp
    {
        private const int CheckIntervalTicks = 60; // frequent enough to catch a fast dash to water

        private bool armed;

        public void Notify_JustEscaped()
        {
            armed = true;
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!armed)
            {
                return;
            }

            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Map == null || pawn.Dead)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }

            RUT_MapComponent_TheTenant tenant = pawn.Map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null || !tenant.IsRegisteredWater(pawn.Position))
            {
                return;
            }

            Install(pawn);
        }

        private void Install(Pawn pawn)
        {
            armed = false;
            Map map = pawn.Map;
            IntVec3 pos = pawn.Position;

            map.GetComponent<RM_MapComponent_TentacleWatch>()?.Notify_SekkulaathInstalled();

            Messages.Message(
                "The escaped creature has reached the water and settled in — the pools have gained a new tenant.",
                new TargetInfo(pos, map), MessageTypeDefOf.ThreatBig);

            if (pawn.Spawned)
            {
                pawn.DeSpawn(DestroyMode.Vanish);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref armed, "armed", false);
        }
    }
}
