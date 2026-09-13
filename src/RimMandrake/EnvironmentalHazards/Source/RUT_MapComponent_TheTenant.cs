using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F1/F2/F3 spike (fever_wood_kit_spec.md). The
    // Tenant is data, not a Thing (ban §6.1 enforced by architecture — it
    // never spawns, so no ambient IncidentDef/ThinkTree can ever reach it).
    // "The Tenant" is the internal working name only (water_taxonomy.csv
    // row fever_pool); this class name is code, never player-facing text.
    //
    // Card gate: this spec's own "Owner cards" section shows all three
    // ruled 2026-09-12 (commits 831201d4c, 744da3686) — the item file's
    // "3 owner cards open (await the next card sitting)" line is stale,
    // same pattern MIASMA_MECHANICS_1's spike found on its sibling kit.
    // Card 2 ("dragged under, rescue window", ruling B) is what this class
    // implements for downable pawns; wild animals still take the clean-
    // splash despawn the sheet's §4 "terribly lost" describes.
    //
    // SPIKE SCOPE: per-cell agitation storage (crib: RM_MapComponent_
    // GradientAxis's float[] pattern), the strike roll via the real
    // Rand.MTBEventOccurs(float mtb, float mtbUnit, float ticksSinceLastCheck)
    // signature (Verse/Rand.cs:509, confirmed against the live 1.6
    // decompile — vanilla itself calls it exactly this way at
    // Verse/Rand.cs:715), the rescue-window downed state (Verse/
    // HealthUtility.cs:246 DamageUntilDowned — non-lethal, confirmed real;
    // Verse/Pawn.cs:882 CarriedBy — confirmed real, used to detect a
    // successful rescue), the truce exemption (RM_TenantTruceExtension),
    // and the agitation setter F2's mirror-break event and F3's use-effect
    // both call. NOT done here, owed to the full build: discrete named-
    // pool bookkeeping for F3's "which pools moved lately" sell copy (this
    // spike tracks agitation per cell and offers a radius-local raise/read,
    // which is sufficient for the mechanism but not yet a pool-identity
    // list); the splash fleck/sound content; the "terribly lost" ambient
    // spawner (F2, separate small IncidentWorker, content not code); the
    // overlay draw call itself (MapComponentOnGUI, Verse/MapComponent.cs:20
    // — confirmed real, not yet wired to actual screen-space cell drawing).
    public class RUT_MapComponent_TheTenant : MapComponent
    {
        private const int ExposureCheckIntervalTicks = 250;
        private const float StrikeMtbExposureHours = 2.5f; // INVENTED, kit spec
        private const float MtbUnitTicks = 2500f; // 1 "exposure hour" = 2500 ticks (INVENTED tuning unit)
        private const float DrownRescueWindowTicks = 2500; // INVENTED: ~1 in-game hour to be rescued

        private float[] agitation;
        private int[] agitationExpiryTick;

        // Rescue-window state for downed (colonist/tamed) pawns pulled
        // under — card 2, ruling B. Cleared if CarriedBy becomes non-null
        // (a colonist reached and is hauling them) before the countdown
        // expires; if it expires first, the Tenant finishes the job.
        private readonly Dictionary<Pawn, int> drowningDeadline = new Dictionary<Pawn, int>();

        public RUT_MapComponent_TheTenant(Map map)
            : base(map)
        {
        }

        private void EnsureGrid()
        {
            int n = map.cellIndices.NumGridCells;
            if (agitation == null || agitation.Length != n)
            {
                agitation = new float[n];
                agitationExpiryTick = new int[n];
            }
        }

        private bool IsRegisteredWater(IntVec3 c)
        {
            TerrainDef t = c.GetTerrain(map);
            return t?.GetModExtension<RM_LurkingWaterExtension>() != null;
        }

        public float AgitationAt(IntVec3 c)
        {
            EnsureGrid();
            if (!c.InBounds(map))
            {
                return 0f;
            }
            int idx = map.cellIndices.CellToIndex(c);
            if (Find.TickManager.TicksGame > agitationExpiryTick[idx])
            {
                return 0f;
            }
            return agitation[idx];
        }

        /// <summary>F2 (mirror-break) and F3 (mirror-list use-effect) both
        /// call this — the shared write path for "this pool moved lately".
        /// Raises agitation in a radius around a seed cell (the local water
        /// blob touched), INVENTED default 3 days validity per the spec's
        /// mirror-break entry.</summary>
        public void RaiseAgitation(IntVec3 seed, float amount, int durationTicks, float radius = 6f)
        {
            EnsureGrid();
            int expiry = Find.TickManager.TicksGame + durationTicks;
            float radiusSq = radius * radius;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(seed, radius, useCenter: true))
            {
                if (!c.InBounds(map) || !IsRegisteredWater(c))
                {
                    continue;
                }
                if ((c - seed).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }
                int idx = map.cellIndices.CellToIndex(c);
                agitation[idx] = amount;
                agitationExpiryTick[idx] = expiry;
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (Find.TickManager.TicksGame % ExposureCheckIntervalTicks == 0)
            {
                ScanExposure();
            }

            TickDrowning();
        }

        private void ScanExposure()
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn.Dead || drowningDeadline.ContainsKey(pawn))
                {
                    continue;
                }
                if (pawn.kindDef?.GetModExtension<RM_TenantTruceExtension>() != null)
                {
                    continue; // nothing native drinks at the pools (§5)
                }
                if (!NearRegisteredWater(pawn.Position))
                {
                    continue;
                }

                float bodySizeFactor = pawn.BodySize > 0f ? pawn.BodySize : 1f;
                float mtb = StrikeMtbExposureHours / bodySizeFactor; // bigger drinkers die first, §4
                if (!Rand.MTBEventOccurs(mtb, MtbUnitTicks, ExposureCheckIntervalTicks))
                {
                    continue;
                }

                Strike(pawn);
            }
        }

        private bool NearRegisteredWater(IntVec3 pos)
        {
            TerrainDef here = pos.GetTerrain(map);
            RM_LurkingWaterExtension ext = here?.GetModExtension<RM_LurkingWaterExtension>();
            if (ext != null)
            {
                return true;
            }
            foreach (IntVec3 adj in GenAdjFast.AdjacentCells8Way(pos))
            {
                if (adj.InBounds(map) && IsRegisteredWater(adj))
                {
                    return true;
                }
            }
            return false;
        }

        private void Strike(Pawn pawn)
        {
            RaiseAgitation(pawn.Position, 1f, 60000 * 3); // this strike is itself evidence, F2

            bool colonistOrTamed = pawn.Faction != null && (pawn.IsColonist || pawn.Faction.IsPlayer);
            if (!colonistOrTamed)
            {
                // Wild animal: the clean splash — no corpse, no filth, the
                // sheet's "terribly lost" (§4). Despawn only; flecks/sound
                // are F2 content, not this spike's concern.
                if (pawn.Spawned)
                {
                    pawn.DeSpawn(DestroyMode.Vanish);
                }
                return;
            }

            // Card 2, ruling B: colonists/tamed go down with a drowning
            // clock in the shallows rather than being subtracted outright.
            // Non-lethal (DamageUntilDowned never kills, Verse/
            // HealthUtility.cs:246) — a real vanilla utility, not invented.
            HealthUtility.DamageUntilDowned(pawn, allowBleedingWounds: false);
            drowningDeadline[pawn] = Find.TickManager.TicksGame + (int)DrownRescueWindowTicks;
        }

        private void TickDrowning()
        {
            if (drowningDeadline.Count == 0)
            {
                return;
            }
            List<Pawn> toRemove = null;
            foreach (KeyValuePair<Pawn, int> kv in drowningDeadline)
            {
                Pawn pawn = kv.Key;
                if (pawn.Dead || !pawn.Spawned && pawn.CarriedBy == null)
                {
                    (toRemove ?? (toRemove = new List<Pawn>())).Add(pawn);
                    continue;
                }
                if (pawn.CarriedBy != null)
                {
                    // Rescued — a colonist reached them before the window
                    // closed. One story per victim (card 2).
                    (toRemove ?? (toRemove = new List<Pawn>())).Add(pawn);
                    continue;
                }
                if (Find.TickManager.TicksGame >= kv.Value)
                {
                    // Not rescued in time — the Tenant finishes it.
                    if (pawn.Spawned)
                    {
                        pawn.DeSpawn(DestroyMode.Vanish);
                    }
                    (toRemove ?? (toRemove = new List<Pawn>())).Add(pawn);
                }
            }
            if (toRemove != null)
            {
                for (int i = 0; i < toRemove.Count; i++)
                {
                    drowningDeadline.Remove(toRemove[i]);
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            // SPIKE SCOPE: the per-cell agitation grid itself is not yet
            // Scribed (TerrainGrid.ExposeTerrainGrid's per-cell array
            // pattern, Verse/TerrainGrid.cs:671, is the model to crib —
            // same owed item the Miasma spike named for its own grid; not
            // reproduced here since no per-cell save format decision has
            // been made yet). Drowning deadlines are transient-safe to
            // drop on load (the window is short; worst case a saved-mid-
            // drowning pawn is treated as rescued on load rather than
            // silently killed by a stale deadline).
        }
    }
}
